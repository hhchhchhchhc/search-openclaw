"""Configuration management for Search OpenClaw."""

from __future__ import annotations

import os
import json
from pathlib import Path
from typing import Any

import yaml


class Config:
    """Manage Search OpenClaw configuration stored in YAML."""

    CONFIG_DIR = Path.home() / ".search-openclaw"
    CONFIG_FILE = CONFIG_DIR / "config.yaml"

    FEATURE_REQUIREMENTS = {
        "brave_search": ["brave_api_key"],
        "tavily_search": ["tavily_api_key"],
        "exa_search": ["exa_api_key"],
        "perplexity_search": ["perplexity_api_key"],
        "iflow_search": ["iflow_api_key"],
        "github_search": ["github_token"],
    }

    def __init__(self, config_path: Path | None = None):
        self.config_path = Path(config_path) if config_path else self.CONFIG_FILE
        self.config_dir = self.config_path.parent
        self.data: dict[str, Any] = {}
        self._ensure_dir()
        self.load()

    def _ensure_dir(self) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def load(self) -> None:
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.data = yaml.safe_load(f) or {}
        else:
            self.data = {}

    def save(self) -> None:
        self._ensure_dir()
        try:
            import stat

            fd = os.open(
                str(self.config_path),
                os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                stat.S_IRUSR | stat.S_IWUSR,
            )
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                yaml.dump(self.data, f, default_flow_style=False, allow_unicode=True, sort_keys=True)
        except OSError:
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(self.data, f, default_flow_style=False, allow_unicode=True, sort_keys=True)

    def get(self, key: str, default: Any = None) -> Any:
        if key in self.data:
            return self.data[key]
        if key.startswith("iflow_"):
            iflow = self.get_iflow_settings()
            mapped = {
                "iflow_api_key": "api_key",
                "iflow_base_url": "base_url",
                "iflow_model": "model",
            }
            if mapped.get(key) in iflow:
                return iflow[mapped[key]]
        env_val = os.environ.get(key.upper())
        if env_val:
            return env_val
        return default

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value
        self.save()

    def delete(self, key: str) -> None:
        self.data.pop(key, None)
        self.save()

    def is_configured(self, feature: str) -> bool:
        return all(self.get(k) for k in self.FEATURE_REQUIREMENTS.get(feature, []))

    def configured_provider_count(self) -> int:
        return sum(
            1
            for feature in (
                "brave_search",
                "tavily_search",
                "exa_search",
                "perplexity_search",
                "iflow_search",
            )
            if self.is_configured(feature)
        )

    def to_dict(self) -> dict[str, Any]:
        masked: dict[str, Any] = {}
        for key, value in self.data.items():
            if any(token in key.lower() for token in ("key", "token", "password", "cookie")):
                masked[key] = f"{str(value)[:8]}..." if value else None
            else:
                masked[key] = value
        iflow = self.get_iflow_settings()
        if iflow:
            masked["iflow_inherited_from_openclaw"] = {
                "base_url": iflow.get("base_url"),
                "model": iflow.get("model"),
                "api_key": f"{iflow['api_key'][:8]}..." if iflow.get("api_key") else None,
            }
        return masked

    def detect_x_aggregator_settings(self) -> dict[str, Any]:
        repo = Path("/home/user/图片/x_search_aggregator")
        if not repo.exists():
            return {}

        candidates = [
            repo / ".venv" / "bin" / "python",
            repo / "venv" / "bin" / "python",
        ]
        python_bin = next((str(path) for path in candidates if path.exists()), None) or "python3"

        state_candidates = [
            repo / "auth_state_cookie.json",
            repo / "auth_state.json",
        ]
        state_path = next((str(path) for path in state_candidates if path.exists()), None)

        return {
            "repo_path": str(repo),
            "python_bin": python_bin,
            "x_auth_state_path": state_path,
        }

    def get_iflow_settings(self) -> dict[str, Any]:
        candidates = [
            Path.home() / ".openclaw" / "openclaw.json",
            Path.home() / ".openclaw" / "agents" / "clawbot2-code" / "agent" / "models.json",
        ]
        for path in candidates:
            if not path.exists():
                continue
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue

            models_root = raw.get("models", raw)
            providers = models_root.get("providers", {})
            iflow = providers.get("iflow")
            if not iflow:
                continue

            models = iflow.get("models") or []
            model_id = None
            if models and isinstance(models, list):
                first = models[0]
                if isinstance(first, dict):
                    model_id = first.get("id")

            settings = {
                "api_key": iflow.get("apiKey") or iflow.get("api_key"),
                "base_url": iflow.get("baseUrl") or iflow.get("base_url") or "https://apis.iflow.cn/v1",
                "model": model_id or "qwen3-max",
                "api": iflow.get("api"),
                "source_path": str(path),
            }
            if settings["api_key"]:
                return settings
        return {}
