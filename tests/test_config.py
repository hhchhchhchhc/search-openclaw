from search_openclaw.config import Config


def test_set_and_get(tmp_path):
    config = Config(config_path=tmp_path / "config.yaml")
    config.set("brave_api_key", "abc")
    assert config.get("brave_api_key") == "abc"


def test_is_configured(tmp_path):
    config = Config(config_path=tmp_path / "config.yaml")
    assert not config.is_configured("tavily_search")
    config.set("tavily_api_key", "test")
    assert config.is_configured("tavily_search")


def test_to_dict_masks_sensitive(tmp_path):
    config = Config(config_path=tmp_path / "config.yaml")
    config.set("iflow_api_key", "super-secret")
    masked = config.to_dict()
    assert masked["iflow_api_key"].startswith("super-se")
