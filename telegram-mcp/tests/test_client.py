import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone, timedelta
from telegram_mcp.client import TelegramWrapper


@pytest.fixture
def mock_client():
    return AsyncMock()


@pytest.mark.asyncio
async def test_get_posts_returns_formatted_data(mock_client):
    mock_message = MagicMock()
    mock_message.id = 123
    mock_message.text = "Hello World"
    mock_message.date = datetime.now(timezone.utc) - timedelta(hours=1)
    mock_message.views = 5000
    mock_message.forwards = 100
    mock_message.reactions = None
    mock_message.replies = MagicMock()
    mock_message.replies.replies = 42

    mock_client.get_messages = AsyncMock(return_value=[mock_message])

    wrapper = TelegramWrapper(mock_client)
    posts = await wrapper.get_posts("@test_channel", days=7)

    assert len(posts) == 1
    assert posts[0]["id"] == 123
    assert posts[0]["text"] == "Hello World"
    assert posts[0]["views"] == 5000
    assert posts[0]["forwards"] == 100
    assert posts[0]["replies_count"] == 42
    assert posts[0]["engagement_score"] == 5000 + 100 * 10 + 0 * 5 + 42 * 3


@pytest.mark.asyncio
async def test_get_posts_filters_by_date(mock_client):
    old_msg = MagicMock()
    old_msg.id = 1
    old_msg.text = "Old"
    old_msg.date = datetime(2025, 1, 1, tzinfo=timezone.utc)
    old_msg.views = 100
    old_msg.forwards = 0
    old_msg.reactions = None
    old_msg.replies = None

    mock_client.get_messages = AsyncMock(return_value=[old_msg])

    wrapper = TelegramWrapper(mock_client)
    posts = await wrapper.get_posts("@test_channel", days=7)

    assert len(posts) == 0


@pytest.mark.asyncio
async def test_get_comments(mock_client):
    mock_reply = MagicMock()
    mock_reply.id = 456
    mock_reply.text = "Great post!"
    mock_reply.date = datetime.now(timezone.utc) - timedelta(hours=1)
    mock_reply.reactions = None

    mock_client.get_messages = AsyncMock(return_value=[mock_reply])

    wrapper = TelegramWrapper(mock_client)
    comments = await wrapper.get_comments("@test_channel", post_id=123)

    assert len(comments) == 1
    assert comments[0]["text"] == "Great post!"
