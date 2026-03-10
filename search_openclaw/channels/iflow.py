"""iFlow route that reuses the current OpenClaw key."""

from __future__ import annotations

from .base import Channel


class IFlowChannel(Channel):
    name = "iflow_search"
    description = "iFlow（复用当前 OpenClaw Key）"
    backends = ["iFlow OpenAI-compatible API"]
    tier = 2

    def can_handle(self, target: str) -> bool:
        return True

    def check(self, config=None) -> tuple[str, str]:
        if not config:
            return "off", "未提供配置"
        api_key = config.get("iflow_api_key")
        base_url = config.get("iflow_base_url")
        model = config.get("iflow_model")
        if api_key and base_url:
            return "ok", f"已复用 OpenClaw 的 iFlow 配置（{model} @ {base_url}）"
        return "off", "未检测到 OpenClaw 的 iFlow 配置；请确认 ~/.openclaw/openclaw.json 中已配置 iflow"
