#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="${HOME}/.claude/config"
VENV_DIR="${SCRIPT_DIR}/telegram-mcp/.venv"

echo "=== Content Digest Skill - Installation ==="
echo

# 1. Install skill as global slash command
echo "[1/5] Installing /content-digest slash command..."
COMMANDS_DIR="${HOME}/.claude/commands"
mkdir -p "${COMMANDS_DIR}"
cp "${SCRIPT_DIR}/skill/content-digest.md" "${COMMANDS_DIR}/content-digest.md"
echo "  ✓ /content-digest command installed"

# 2. Install telegram-mcp
echo "[2/5] Installing telegram-mcp..."
cd "${SCRIPT_DIR}/telegram-mcp"
python3 -m venv "${VENV_DIR}"
"${VENV_DIR}/bin/pip" install -e ".[dev]" --quiet
echo "  ✓ telegram-mcp installed"

# 2. Copy config templates
echo "[3/5] Setting up config files..."
mkdir -p "${CONFIG_DIR}"

if [ ! -f "${CONFIG_DIR}/telegram-channels.yaml" ]; then
    cp "${SCRIPT_DIR}/config/telegram-channels.example.yaml" "${CONFIG_DIR}/telegram-channels.yaml"
    echo "  ✓ Created ${CONFIG_DIR}/telegram-channels.yaml (edit with your channels)"
else
    echo "  → ${CONFIG_DIR}/telegram-channels.yaml already exists, skipping"
fi

if [ ! -f "${CONFIG_DIR}/youtube-channels.yaml" ]; then
    cp "${SCRIPT_DIR}/config/youtube-channels.example.yaml" "${CONFIG_DIR}/youtube-channels.yaml"
    echo "  ✓ Created ${CONFIG_DIR}/youtube-channels.yaml (edit with your channels)"
else
    echo "  → ${CONFIG_DIR}/youtube-channels.yaml already exists, skipping"
fi

# 3. Register MCP server
echo "[4/5] Registering MCP server..."
MCP_CONFIG="${HOME}/.claude/.mcp.json"

if [ -f "${MCP_CONFIG}" ]; then
    # Check if telegram entry already exists
    if python3 -c "import json; d=json.load(open('${MCP_CONFIG}')); exit(0 if 'telegram' in d.get('mcpServers',{}) else 1)" 2>/dev/null; then
        echo "  → telegram MCP server already registered, skipping"
    else
        python3 -c "
import json
with open('${MCP_CONFIG}') as f:
    config = json.load(f)
config.setdefault('mcpServers', {})['telegram'] = {
    'command': '${VENV_DIR}/bin/python',
    'args': ['-m', 'telegram_mcp.server'],
    'cwd': '${SCRIPT_DIR}/telegram-mcp',
    'env': {
        'TELEGRAM_API_ID': '\${TELEGRAM_API_ID}',
        'TELEGRAM_API_HASH': '\${TELEGRAM_API_HASH}'
    }
}
with open('${MCP_CONFIG}', 'w') as f:
    json.dump(config, f, indent=2)
"
        echo "  ✓ telegram MCP server registered in ${MCP_CONFIG}"
    fi
else
    python3 -c "
import json
config = {'mcpServers': {'telegram': {
    'command': '${VENV_DIR}/bin/python',
    'args': ['-m', 'telegram_mcp.server'],
    'cwd': '${SCRIPT_DIR}/telegram-mcp',
    'env': {
        'TELEGRAM_API_ID': '\${TELEGRAM_API_ID}',
        'TELEGRAM_API_HASH': '\${TELEGRAM_API_HASH}'
    }
}}}
with open('${MCP_CONFIG}', 'w') as f:
    json.dump(config, f, indent=2)
"
    echo "  ✓ Created ${MCP_CONFIG} with telegram MCP server"
fi

# 4. Setup instructions
echo "[5/5] Remaining manual steps:"
echo
echo "  a) Get Telegram API credentials from https://my.telegram.org"
echo "     Add them to ~/.claude/.mcp.json under mcpServers.telegram.env:"
echo "       \"TELEGRAM_API_ID\": \"your_id\","
echo "       \"TELEGRAM_API_HASH\": \"your_hash\""
echo
echo "  b) Run first-time Telegram auth:"
echo "       cd ${SCRIPT_DIR}/telegram-mcp"
echo "       ${VENV_DIR}/bin/python scripts/auth.py"
echo
echo "  c) Edit your channel configs:"
echo "       ${CONFIG_DIR}/telegram-channels.yaml"
echo "       ${CONFIG_DIR}/youtube-channels.yaml"
echo
echo "  d) Install a YouTube MCP server (e.g. dannySubsense/youtube-mcp-server)"
echo
echo "  e) Restart Claude Code to load the MCP server"
echo
echo "=== Installation complete ==="
