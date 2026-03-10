import json
import subprocess

from search_openclaw.search import (
    SearchResult,
    auto_provider,
    dump_results_json,
    format_results,
    search,
)
from search_openclaw.config import Config


def test_auto_provider_prefers_brave(tmp_path):
    config = Config(config_path=tmp_path / "config.yaml")
    config.set("tavily_api_key", "tvly")
    config.set("brave_api_key", "brv")
    assert auto_provider(config) == "brave"


def test_dump_results_json():
    payload = dump_results_json("brave", [SearchResult("t", "u", "s", "brave")])
    parsed = json.loads(payload)
    assert parsed["provider"] == "brave"
    assert parsed["results"][0]["title"] == "t"


def test_format_results():
    text = format_results("tavily", [SearchResult("Title", "https://x", "Snippet", "tavily")])
    assert "Provider: tavily" in text
    assert "Title" in text


def test_search_github(monkeypatch, tmp_path):
    config = Config(config_path=tmp_path / "config.yaml")
    monkeypatch.setattr("shutil.which", lambda cmd: "/usr/bin/gh" if cmd == "gh" else None)

    def fake_run(cmd, **kwargs):
        data = [
            {
                "name": "search-openclaw",
                "owner": {"login": "demo"},
                "description": "desc",
                "url": "https://github.com/demo/search-openclaw",
                "stargazerCount": 10,
                "updatedAt": "2026-03-10T00:00:00Z",
            }
        ]
        return subprocess.CompletedProcess(cmd, 0, json.dumps(data), "")

    monkeypatch.setattr("subprocess.run", fake_run)
    provider, results = search("openclaw", "github", 5, config)
    assert provider == "github"
    assert results[0].title == "demo/search-openclaw"


def test_iflow_settings_inherited_from_openclaw(monkeypatch, tmp_path):
    home = tmp_path / "home"
    openclaw_dir = home / ".openclaw"
    openclaw_dir.mkdir(parents=True)
    (openclaw_dir / "openclaw.json").write_text(
        json.dumps(
            {
                "models": {
                    "providers": {
                        "iflow": {
                            "apiKey": "iflow-secret-123",
                            "baseUrl": "https://apis.iflow.cn/v1",
                            "models": [{"id": "qwen3-max"}],
                        }
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("HOME", str(home))
    config = Config()
    assert config.get("iflow_api_key") == "iflow-secret-123"
    assert config.get("iflow_model") == "qwen3-max"
