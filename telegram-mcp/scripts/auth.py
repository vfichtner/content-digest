#!/usr/bin/env python3
"""First-time Telegram authentication. Reads credentials from ~/.claude/.mcp.json."""

import asyncio
import json
import os
from pathlib import Path

from telethon import TelegramClient


def get_credentials():
    mcp_path = Path("~/.claude/.mcp.json").expanduser()
    if not mcp_path.exists():
        raise FileNotFoundError(f"{mcp_path} not found. Register the telegram MCP server first.")

    config = json.loads(mcp_path.read_text())
    telegram_env = config.get("mcpServers", {}).get("telegram", {}).get("env", {})

    api_id = telegram_env.get("TELEGRAM_API_ID")
    api_hash = telegram_env.get("TELEGRAM_API_HASH")

    if not api_id or not api_hash:
        raise ValueError("TELEGRAM_API_ID and TELEGRAM_API_HASH must be set in ~/.claude/.mcp.json")

    return int(api_id), api_hash


async def main():
    api_id, api_hash = get_credentials()
    session_path = str(Path("~/.claude/config/telegram.session").expanduser())

    os.makedirs(Path(session_path).parent, exist_ok=True)

    print(f"Session will be saved to: {session_path}")
    print("You will be asked for your phone number and a verification code.\n")

    client = TelegramClient(session_path, api_id, api_hash)
    await client.start()
    print("\nAuthenticated! Session saved.")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
