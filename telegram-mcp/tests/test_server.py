import asyncio
from telegram_mcp.server import mcp


def test_tools_registered():
    tools = asyncio.run(mcp.list_tools())
    tool_names = {t.name for t in tools}
    assert "telegram_get_posts" in tool_names
    assert "telegram_get_comments" in tool_names
    assert "telegram_list_channels" in tool_names
