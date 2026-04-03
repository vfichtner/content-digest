# content-digest

Claude Skill that monitors Telegram and YouTube channels, analyzes content by engagement, and produces German-language summaries.

## Components

- **`skill/content-digest.md`** -- Claude Skill that orchestrates data collection and summarization
- **`telegram-mcp/`** -- MCP Server (Python/FastMCP/Telethon) for Telegram channel access
- **`config/`** -- Example config files for channel lists
- **`install.sh`** -- Installation script

## Installation

```bash
git clone https://github.com/vfichtner/content-digest.git
cd content-digest
./install.sh
```

The install script will:
1. Set up a Python virtual environment and install `telegram-mcp`
2. Copy config templates to `~/.claude/config/`
3. Register the Telegram MCP server in `~/.claude/.mcp.json`

### Manual steps after install

**1. Telegram API credentials**

Get your API ID and Hash from https://my.telegram.org and add them to `~/.claude/.mcp.json`:

```json
{
  "mcpServers": {
    "telegram": {
      "env": {
        "TELEGRAM_API_ID": "your_id",
        "TELEGRAM_API_HASH": "your_hash"
      }
    }
  }
}
```

**2. Telegram authentication**

Run the auth script in a terminal (interactive -- asks for phone number and verification code):

```bash
cd content-digest/telegram-mcp
.venv/bin/python scripts/auth.py
```

The script reads credentials from `~/.claude/.mcp.json` and saves the session to `~/.claude/config/telegram.session`.

**3. YouTube MCP server**

Install a YouTube MCP server separately, e.g. [dannySubsense/youtube-mcp-server](https://github.com/dannySubsense/youtube-mcp-server).

**4. Channel configs**

Edit the channel lists:
- `~/.claude/config/telegram-channels.yaml`
- `~/.claude/config/youtube-channels.yaml`

**5. Restart Claude Code** to load the MCP servers.

## Usage

```
/content-digest              # All sources, last 7 days
/content-digest days=3       # Last 3 days
/content-digest source=telegram  # Telegram only
/content-digest category=Dev     # Filter by category
```

## Output

- Conversation: compact German summary with top themes, highlights, and sentiment
- File: `docs/digests/YYYY-MM-DD-content-digest.md` with full details

## Development

```bash
cd telegram-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/ -v
```
