import subprocess

from search_openclaw.config import Config
from search_openclaw.social_scrape import _extract_run_dir, scrape_social


def test_extract_run_dir():
    assert _extract_run_dir("运行目录: /tmp/demo\n") == "/tmp/demo"
    assert _extract_run_dir("Run directory: /tmp/demo2\n") == "/tmp/demo2"


def test_scrape_social_x(monkeypatch, tmp_path):
    config = Config(config_path=tmp_path / "config.yaml")
    config.set("x_auth_state_path", "/tmp/auth_state.json")

    def fake_run(cmd, **kwargs):
        return subprocess.CompletedProcess(cmd, 0, "运行目录: /tmp/run-x\n", "")

    monkeypatch.setattr("subprocess.run", fake_run)
    result = scrape_social(config, "x", "AI Agent", headless=True)
    assert result["x"]["run_dir"] == "/tmp/run-x"
    assert "search_openclaw.social.x_keyword_search" in result["x"]["command"]
