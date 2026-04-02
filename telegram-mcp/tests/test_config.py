import tempfile
import os
import yaml
import pytest
from telegram_mcp.config import load_telegram_config


def test_load_config_returns_channels():
    config_data = {
        "channels": [
            {"name": "@test_channel", "category": "Tech"},
            {"name": "@other_channel", "category": "Dev"},
        ],
        "defaults": {"days": 7},
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(config_data, f)
        f.flush()
        config = load_telegram_config(f.name)

    os.unlink(f.name)
    assert len(config.channels) == 2
    assert config.channels[0].name == "@test_channel"
    assert config.channels[0].category == "Tech"
    assert config.defaults.days == 7


def test_load_config_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        load_telegram_config("/nonexistent/path.yaml")


def test_load_config_default_days():
    config_data = {
        "channels": [{"name": "@ch", "category": "General"}],
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(config_data, f)
        f.flush()
        config = load_telegram_config(f.name)

    os.unlink(f.name)
    assert config.defaults.days == 7
