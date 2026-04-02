import os
import json
from pathlib import Path
from dotenv import load_dotenv
from fastmcp import FastMCP
from telethon import TelegramClient
from telegram_mcp.config import load_telegram_config
from telegram_mcp.client import TelegramWrapper

load_dotenv()

mcp = FastMCP("telegram-mcp")

CONFIG_PATH = os.environ.get(
    "TELEGRAM_CONFIG_PATH",
    str(Path("~/.claude/config/telegram-channels.yaml").expanduser()),
)
SESSION_PATH = os.environ.get(
    "TELEGRAM_SESSION_PATH",
    str(Path("~/.claude/config/telegram.session").expanduser()),
)

_client = None
_wrapper = None


async def get_wrapper() -> TelegramWrapper:
    global _client, _wrapper
    if _wrapper is None:
        api_id = int(os.environ["TELEGRAM_API_ID"])
        api_hash = os.environ["TELEGRAM_API_HASH"]
        _client = TelegramClient(SESSION_PATH, api_id, api_hash)
        await _client.start(phone=os.environ.get("TELEGRAM_PHONE"))
        _wrapper = TelegramWrapper(_client)
    return _wrapper


@mcp.tool()
async def telegram_list_channels() -> str:
    """List configured Telegram channels from the config file."""
    config = load_telegram_config(CONFIG_PATH)
    channels = [{"name": ch.name, "category": ch.category} for ch in config.channels]
    return json.dumps(channels, indent=2, ensure_ascii=False)


@mcp.tool()
async def telegram_get_posts(channel: str, days: int = 7) -> str:
    """Get posts from a Telegram channel for the last N days, sorted by engagement.

    Args:
        channel: Channel username (e.g. @durov)
        days: Number of days to look back (default: 7)
    """
    wrapper = await get_wrapper()
    posts = await wrapper.get_posts(channel, days=days)
    return json.dumps(posts, indent=2, ensure_ascii=False)


@mcp.tool()
async def telegram_get_comments(channel: str, post_id: int) -> str:
    """Get comments/replies for a specific post.

    Args:
        channel: Channel username (e.g. @durov)
        post_id: The message ID to get comments for
    """
    wrapper = await get_wrapper()
    comments = await wrapper.get_comments(channel, post_id=post_id)
    return json.dumps(comments, indent=2, ensure_ascii=False)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
