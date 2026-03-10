import subprocess

from search_openclaw.channels import get_all_channels, get_channel
from search_openclaw.channels.exa_search import ExaSearchChannel
from search_openclaw.config import Config


def test_channel_registry():
    channels = get_all_channels()
    names = [channel.name for channel in channels]
    assert "web" in names
    assert "brave_search" in names
    assert "multi_search" in names
    assert len(names) == len(set(names))


def test_get_channel():
    channel = get_channel("tavily_search")
    assert channel is not None
    assert channel.name == "tavily_search"


def test_exa_channel_ok_with_mcporter(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda cmd: "/usr/bin/mcporter" if cmd == "mcporter" else None)

    def fake_run(cmd, **kwargs):
        assert cmd[:3] == ["/usr/bin/mcporter", "config", "list"]
        return subprocess.CompletedProcess(cmd, 0, "exa https://mcp.exa.ai/mcp", "")

    monkeypatch.setattr("subprocess.run", fake_run)
    status, message = ExaSearchChannel().check()
    assert status == "ok"
    assert "Exa" in message


def test_multi_search_warns_with_single_provider(tmp_path):
    import os

    os.environ["HOME"] = str(tmp_path / "isolated-home")
    config = Config(config_path=tmp_path / "config.yaml")
    config.set("brave_api_key", "x")
    status, message = get_channel("multi_search").check(config)
    assert status == "warn"
    assert "1 个搜索源" in message


def test_iflow_channel_ok_when_openclaw_has_key(monkeypatch, tmp_path):
    home = tmp_path / "home"
    openclaw_dir = home / ".openclaw"
    openclaw_dir.mkdir(parents=True)
    (openclaw_dir / "openclaw.json").write_text(
        '{"models":{"providers":{"iflow":{"apiKey":"secret-12345","baseUrl":"https://apis.iflow.cn/v1","models":[{"id":"qwen3-max"}]}}}}',
        encoding="utf-8",
    )
    monkeypatch.setenv("HOME", str(home))
    config = Config()
    status, message = get_channel("iflow_search").check(config)
    assert status == "ok"
    assert "iFlow" in message
