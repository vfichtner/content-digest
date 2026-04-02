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

1. **Telegram API credentials** from https://my.telegram.org -- set `TELEGRAM_API_ID` and `TELEGRAM_API_HASH` as environment variables
2. **First-time Telegram auth** -- run the auth command printed by the installer
3. **YouTube MCP server** -- install separately (e.g. [dannySubsense/youtube-mcp-server](https://github.com/dannySubsense/youtube-mcp-server))
4. **Edit channel configs** in `~/.claude/config/telegram-channels.yaml` and `youtube-channels.yaml`
5. **Restart Claude Code** to load the MCP server

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
