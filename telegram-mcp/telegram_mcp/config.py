from dataclasses import dataclass, field
from pathlib import Path
import yaml


@dataclass
class Channel:
    name: str
    category: str = "General"


@dataclass
class Defaults:
    days: int = 7


@dataclass
class TelegramConfig:
    channels: list[Channel]
    defaults: Defaults = field(default_factory=Defaults)


def load_telegram_config(path: str | Path) -> TelegramConfig:
    config_path = Path(path).expanduser()
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {path}")

    with open(config_path) as f:
        raw = yaml.safe_load(f)

    channels = [
        Channel(name=ch["name"], category=ch.get("category", "General"))
        for ch in raw.get("channels", [])
    ]

    defaults_raw = raw.get("defaults", {})
    defaults = Defaults(days=defaults_raw.get("days", 7))

    return TelegramConfig(channels=channels, defaults=defaults)
