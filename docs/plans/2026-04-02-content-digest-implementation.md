# Content Digest - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Claude Skill that monitors Telegram and YouTube channels, summarizes content weighted by engagement, and outputs German-language digests.

**Architecture:** Three components: (1) Telegram MCP Server (Python/FastMCP/Telethon), (2) YouTube MCP Server (existing `dannySubsense/youtube-mcp-server`), (3) Content Digest Skill that orchestrates both. Config files in `~/.claude/config/`.

**Tech Stack:** Python 3.10+, FastMCP, Telethon, PyYAML, pytest. YouTube via existing MCP server with `google-api-python-client` + `youtube-transcript-api`.

**Design Doc:** `docs/plans/2026-04-02-content-digest-design.md`

---

## Task 1: Project Scaffolding - Telegram MCP Server

**Files:**
- Create: `telegram-mcp/pyproject.toml`
- Create: `telegram-mcp/src/__init__.py`
- Create: `telegram-mcp/src/server.py`
- Create: `telegram-mcp/tests/__init__.py`
- Create: `telegram-mcp/.env.example`
- Create: `telegram-mcp/.gitignore`

**Step 1: Initialize git repo and project structure**

```bash
cd /Users/vfichtner/Development/claude-code
mkdir -p telegram-mcp/src telegram-mcp/tests
cd telegram-mcp
git init
```

**Step 2: Create `pyproject.toml`**

```toml
[project]
name = "telegram-mcp"
version = "0.1.0"
description = "MCP server for Telegram channel monitoring"
requires-python = ">=3.10"
dependencies = [
    "fastmcp>=2.0.0",
    "telethon>=1.34.0",
    "pyyaml>=6.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23.0",
]

[project.scripts]
telegram-mcp = "src.server:main"

[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.backends._legacy:_Backend"
```

**Step 3: Create `.env.example`**

```
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+49xxxxxxxxxx
```

**Step 4: Create `.gitignore`**

```
.env
*.session
*.session-journal
__pycache__/
*.pyc
.venv/
dist/
*.egg-info/
```

**Step 5: Create empty `__init__.py` files**

```bash
touch src/__init__.py tests/__init__.py
```

**Step 6: Create minimal `src/server.py`**

```python
from fastmcp import FastMCP

mcp = FastMCP("telegram-mcp")


def main():
    mcp.run()


if __name__ == "__main__":
    main()
```

**Step 7: Install dependencies**

```bash
cd /Users/vfichtner/Development/claude-code/telegram-mcp
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

**Step 8: Verify server starts**

```bash
python -c "from src.server import mcp; print('Server module loads OK')"
```
Expected: `Server module loads OK`

**Step 9: Commit**

```bash
git add -A
git commit -m "feat: scaffold telegram-mcp project with FastMCP"
```

---

## Task 2: Config Loader

**Files:**
- Create: `telegram-mcp/src/config.py`
- Create: `telegram-mcp/tests/test_config.py`
- Create: `~/.claude/config/telegram-channels.yaml` (sample)

**Step 1: Write the failing test**

```python
# tests/test_config.py
import tempfile
import os
import yaml
import pytest
from src.config import load_telegram_config


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
    assert config.defaults.days == 7  # default
```

**Step 2: Run test to verify it fails**

```bash
cd /Users/vfichtner/Development/claude-code/telegram-mcp
source .venv/bin/activate
pytest tests/test_config.py -v
```
Expected: FAIL - `cannot import name 'load_telegram_config'`

**Step 3: Write implementation**

```python
# src/config.py
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


def load_telegram_config(path: str) -> TelegramConfig:
    config_path = Path(path)
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
```

**Step 4: Run tests**

```bash
pytest tests/test_config.py -v
```
Expected: 3 passed

**Step 5: Create sample config**

```bash
mkdir -p ~/.claude/config
```

```yaml
# ~/.claude/config/telegram-channels.yaml
channels:
  - name: "@durov"
    category: "Tech"
  - name: "@python_digest"
    category: "Dev"

defaults:
  days: 7
```

**Step 6: Commit**

```bash
git add src/config.py tests/test_config.py
git commit -m "feat: add YAML config loader for telegram channels"
```

---

## Task 3: Telegram Client Wrapper

**Files:**
- Create: `telegram-mcp/src/telegram_client.py`
- Create: `telegram-mcp/tests/test_telegram_client.py`

**Step 1: Write the failing test**

```python
# tests/test_telegram_client.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone, timedelta
from src.telegram_client import TelegramWrapper


@pytest.fixture
def mock_client():
    client = AsyncMock()
    return client


@pytest.mark.asyncio
async def test_get_posts_returns_formatted_data(mock_client):
    """Test that get_posts returns correctly structured post data."""
    mock_message = MagicMock()
    mock_message.id = 123
    mock_message.text = "Hello World"
    mock_message.date = datetime(2026, 4, 1, 12, 0, tzinfo=timezone.utc)
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


@pytest.mark.asyncio
async def test_get_posts_filters_by_date(mock_client):
    """Test that posts older than `days` are excluded."""
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
    """Test fetching comments for a post."""
    mock_reply = MagicMock()
    mock_reply.id = 456
    mock_reply.text = "Great post!"
    mock_reply.date = datetime(2026, 4, 1, 14, 0, tzinfo=timezone.utc)
    mock_reply.reactions = None

    mock_client.get_messages = AsyncMock(return_value=[mock_reply])

    wrapper = TelegramWrapper(mock_client)
    comments = await wrapper.get_comments("@test_channel", post_id=123)

    assert len(comments) == 1
    assert comments[0]["text"] == "Great post!"
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_telegram_client.py -v
```
Expected: FAIL - `cannot import name 'TelegramWrapper'`

**Step 3: Write implementation**

```python
# src/telegram_client.py
from datetime import datetime, timezone, timedelta
from telethon import TelegramClient


class TelegramWrapper:
    def __init__(self, client: TelegramClient):
        self.client = client

    async def get_posts(self, channel: str, days: int = 7) -> list[dict]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        messages = await self.client.get_messages(channel, limit=100)

        posts = []
        for msg in messages:
            if msg.date < cutoff:
                continue
            if not msg.text:
                continue

            reactions_count = 0
            if msg.reactions and msg.reactions.results:
                reactions_count = sum(r.count for r in msg.reactions.results)

            replies_count = 0
            if msg.replies:
                replies_count = msg.replies.replies or 0

            posts.append({
                "id": msg.id,
                "text": msg.text,
                "date": msg.date.isoformat(),
                "views": msg.views or 0,
                "forwards": msg.forwards or 0,
                "reactions_count": reactions_count,
                "replies_count": replies_count,
                "engagement_score": (msg.views or 0) + (msg.forwards or 0) * 10 + reactions_count * 5 + replies_count * 3,
            })

        return sorted(posts, key=lambda p: p["engagement_score"], reverse=True)

    async def get_comments(self, channel: str, post_id: int) -> list[dict]:
        replies = await self.client.get_messages(channel, reply_to=post_id, limit=50)

        comments = []
        for reply in replies:
            if not reply.text:
                continue

            reactions_count = 0
            if reply.reactions and reply.reactions.results:
                reactions_count = sum(r.count for r in reply.reactions.results)

            comments.append({
                "id": reply.id,
                "text": reply.text,
                "date": reply.date.isoformat(),
                "reactions_count": reactions_count,
            })

        return comments
```

**Step 4: Run tests**

```bash
pytest tests/test_telegram_client.py -v
```
Expected: 3 passed

**Step 5: Commit**

```bash
git add src/telegram_client.py tests/test_telegram_client.py
git commit -m "feat: add Telegram client wrapper with engagement scoring"
```

---

## Task 4: MCP Server Tools

**Files:**
- Modify: `telegram-mcp/src/server.py`
- Create: `telegram-mcp/tests/test_server.py`

**Step 1: Write the failing test**

```python
# tests/test_server.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.server import mcp


@pytest.mark.asyncio
async def test_list_tools():
    """Verify all expected tools are registered."""
    tools = mcp._tool_manager._tools
    tool_names = set(tools.keys())
    assert "telegram_get_posts" in tool_names
    assert "telegram_get_comments" in tool_names
    assert "telegram_list_channels" in tool_names
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_server.py -v
```
Expected: FAIL - tools not registered

**Step 3: Write implementation**

```python
# src/server.py
import os
import json
from dotenv import load_dotenv
from fastmcp import FastMCP
from telethon import TelegramClient
from src.config import load_telegram_config
from src.telegram_client import TelegramWrapper

load_dotenv()

mcp = FastMCP("telegram-mcp")

CONFIG_PATH = os.path.expanduser("~/.claude/config/telegram-channels.yaml")
SESSION_PATH = os.path.expanduser("~/.claude/config/telegram.session")

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
    return json.dumps(channels, indent=2)


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
```

**Step 4: Run tests**

```bash
pytest tests/test_server.py -v
```
Expected: PASS

**Step 5: Commit**

```bash
git add src/server.py tests/test_server.py
git commit -m "feat: register MCP tools for telegram channel access"
```

---

## Task 5: Register Telegram MCP Server in Claude Code

**Files:**
- Modify: `~/.claude/.mcp.json`

**Step 1: Read current MCP config**

```bash
cat ~/.claude/.mcp.json
```

**Step 2: Add telegram-mcp entry**

Add to the `mcpServers` object in `~/.claude/.mcp.json`:

```json
{
  "mcpServers": {
    "telegram": {
      "command": "/Users/vfichtner/Development/claude-code/telegram-mcp/.venv/bin/python",
      "args": ["-m", "src.server"],
      "cwd": "/Users/vfichtner/Development/claude-code/telegram-mcp",
      "env": {
        "TELEGRAM_API_ID": "YOUR_API_ID",
        "TELEGRAM_API_HASH": "YOUR_API_HASH",
        "TELEGRAM_PHONE": "+49XXXXXXXXXX"
      }
    }
  }
}
```

**Step 3: First-time Telegram authentication**

Run manually in terminal to complete phone verification:

```bash
cd /Users/vfichtner/Development/claude-code/telegram-mcp
source .venv/bin/activate
python -c "
import asyncio, os
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()
client = TelegramClient(
    os.path.expanduser('~/.claude/config/telegram.session'),
    int(os.environ['TELEGRAM_API_ID']),
    os.environ['TELEGRAM_API_HASH']
)

async def auth():
    await client.start(phone=os.environ['TELEGRAM_PHONE'])
    print('Authenticated! Session saved.')
    await client.disconnect()

asyncio.run(auth())
"
```

**Step 4: Verify MCP server works**

Restart Claude Code and verify:
```
/mcp
```
Expected: `telegram` server listed as connected

**Step 5: Commit**

```bash
cd /Users/vfichtner/Development/claude-code/telegram-mcp
git add -A
git commit -m "docs: add MCP registration instructions"
```

---

## Task 6: Install & Configure YouTube MCP Server

**Step 1: Clone and install `dannySubsense/youtube-mcp-server`**

```bash
cd /Users/vfichtner/Development/claude-code
git clone https://github.com/dannySubsense/youtube-mcp-server.git youtube-mcp
cd youtube-mcp
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Step 2: Get YouTube Data API key**

1. Go to Google Cloud Console
2. Enable YouTube Data API v3
3. Create API key

**Step 3: Register in Claude Code MCP config**

Add to `~/.claude/.mcp.json`:

```json
{
  "youtube": {
    "command": "/Users/vfichtner/Development/claude-code/youtube-mcp/.venv/bin/python",
    "args": ["server.py"],
    "cwd": "/Users/vfichtner/Development/claude-code/youtube-mcp",
    "env": {
      "YOUTUBE_API_KEY": "YOUR_API_KEY"
    }
  }
}
```

Note: Check the actual entry point file name after cloning - may differ.

**Step 4: Create YouTube config**

```yaml
# ~/.claude/config/youtube-channels.yaml
channels:
  - id: "UCsBjURrPoezykLs9EqgamOA"
    name: "Fireship"
    category: "Dev"

defaults:
  days: 7
```

**Step 5: Verify**

Restart Claude Code, run `/mcp`, confirm `youtube` is connected.

**Step 6: Test YouTube tools manually**

In Claude Code:
```
List recent videos from Fireship using the youtube MCP
```

Expected: Video list with titles, dates, view counts.

---

## Task 7: Content Digest Skill

**Files:**
- Create: `~/.claude/skills/content-digest.md`

**Step 1: Write the skill file**

```markdown
---
name: content-digest
description: Monitors Telegram and YouTube channels, creates engagement-weighted German summaries of the last N days
---

## Parameters

Parse these from the user's invocation:
- `days` — Number of days to look back. Default: 7
- `source` — `all`, `telegram`, or `youtube`. Default: `all`
- `category` — Filter by category from config. Default: all categories

## Instructions

You are a content analyst creating a German-language digest of Telegram and YouTube channels.

### Step 1: Load Configs

Read both config files:
- `~/.claude/config/telegram-channels.yaml`
- `~/.claude/config/youtube-channels.yaml`

If `source` parameter limits to one, skip the other. If `category` is set, filter channels.

### Step 2: Gather Telegram Data

For each Telegram channel in config:
1. Call `telegram_get_posts(channel=<name>, days=<days>)`
2. Note the top 3 posts by engagement_score
3. For the top 3 posts, call `telegram_get_comments(channel=<name>, post_id=<id>)`

### Step 3: Gather YouTube Data

For each YouTube channel in config:
1. Call `get_channel_videos(channel_id=<id>)` — filter to last N days
2. For the top 3 videos by views, call `get_video_transcript(video_id=<id>)`
3. For the top 3 videos, call `get_video_comments(video_id=<id>)`

### Step 4: Analyze & Rank

Rank all content by engagement:
- Telegram: engagement_score from the API
- YouTube: views + likes*5 + comments*3

Identify cross-source themes — topics that appear in both Telegram AND YouTube get boosted.

### Step 5: Write Conversation Summary

Output in German, following this format:

```
# Content Digest — KW {week}/{year}

## Top-Themen dieser Woche
1. **{Thema}** — {Kurzbeschreibung} (Quellen: {channels})
2. ...

## Telegram Highlights
### {Channel} ({Category})
- **Top Post** ({views} Views, {reactions} Reactions): {Zusammenfassung}
  - Diskussion: {Kommentar-Zusammenfassung}

## YouTube Highlights
### {Channel} ({Category})
- **"{Titel}"** ({views} Views) — Key Points:
  - {Punkt 1}
  - {Punkt 2}
  - Kommentare: {Zusammenfassung}

## Stimmungsbild
{Zusammenfassung der dominanten Narrative, Trends und Stimmungen}
```

### Step 6: Write Detail File

Save the full digest (all posts/videos, not just highlights) to:
`docs/digests/{YYYY-MM-DD}-content-digest.md`

Use the same format but include ALL posts and videos, not just top ones.
```

**Step 2: Verify skill loads**

In Claude Code:
```
/content-digest
```

Expected: Skill triggers and starts executing steps.

**Step 3: Commit**

```bash
cd /Users/vfichtner/Development/claude-code/telegram-mcp
git add -A
git commit -m "feat: add content-digest skill"
```

---

## Task 8: End-to-End Test

**Step 1: Run full digest**

```
/content-digest days=3
```

**Step 2: Verify output**

- [ ] German language summary appears in conversation
- [ ] Top-Themen section identifies cross-source themes
- [ ] Telegram Highlights shows engagement-ranked posts
- [ ] YouTube Highlights shows video summaries with key points
- [ ] Detail file created in `docs/digests/`

**Step 3: Test filters**

```
/content-digest source=telegram days=1
/content-digest source=youtube category=Dev
```

**Step 4: Fix any issues found during testing**

Iterate on skill prompt, config, or MCP tools as needed.

**Step 5: Final commit**

```bash
git add -A
git commit -m "feat: content-digest skill complete and tested"
```
