from search_openclaw.config import Config
from search_openclaw.doctor import check_all, format_report


def test_check_all(tmp_path):
    config = Config(config_path=tmp_path / "config.yaml")
    results = check_all(config)
    assert "web" in results
    assert "brave_search" in results


def test_format_report(tmp_path):
    config = Config(config_path=tmp_path / "config.yaml")
    config.set("tavily_api_key", "key")
    report = format_report(check_all(config))
    assert "Search OpenClaw" in report
    assert "Tavily" in report
