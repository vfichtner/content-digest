---
name: content-digest
description: Monitors Telegram and YouTube channels via MCP servers, creates engagement-weighted German summaries of the last N days
---

## Parameters

Parse from the user's invocation:
- `days` — Number of days to look back. Default: 7
- `source` — `all`, `telegram`, or `youtube`. Default: `all`
- `category` — Filter by category from config. Default: all categories

## Prerequisites

This skill requires two MCP servers registered in `~/.claude/.mcp.json`:
- **telegram** — provides `telegram_list_channels`, `telegram_get_posts`, `telegram_get_comments`
- **youtube** — provides `get_channel_videos`, `get_video_transcript`, `get_video_comments` and other tools

IMPORTANT: Use ONLY the MCP tools from the registered servers. NEVER use WebFetch, web scraping, or RSS feeds as a fallback. If an MCP server is not connected, report the issue to the user and skip that source.

## Instructions

You are a content analyst producing a German-language digest of Telegram and YouTube channels.

### Step 1: Load configs

Read both config files using the Read tool:
- `~/.claude/config/telegram-channels.yaml`
- `~/.claude/config/youtube-channels.yaml`

If `source` limits to one source, skip the other. If `category` is set, filter channels accordingly.

### Step 2: Gather Telegram data

IMPORTANT: Use the MCP tools from the `telegram` server. These are available as regular tool calls.

For each Telegram channel in the config:
1. Call the MCP tool `telegram_get_posts` with parameters `channel` and `days`
2. Identify the top 3 posts by `engagement_score`
3. For the top 3 posts, call the MCP tool `telegram_get_comments` with `channel` and `post_id`

### Step 3: Gather YouTube data

IMPORTANT: Use the MCP tools from the `youtube` server. These are available as regular tool calls.

For each YouTube channel in the config:
1. Call the MCP tool `get_channel_videos` with `channel_id` — filter to the last N days
2. For the top 3 videos by views, call the MCP tool `get_video_transcript` with `video_id`
3. For the top 3 videos, call the MCP tool `get_video_comments` with `video_id`

If a YouTube MCP tool has a different name, use ToolSearch to discover the available tools.

### Step 4: Analyze & rank

Rank all content by engagement:
- Telegram: `engagement_score` from the API
- YouTube: views + likes*5 + comments*3

Identify cross-source themes — topics appearing in BOTH Telegram AND YouTube are boosted.

### Step 5: Output summary in conversation

Output in German, using this format:

```
# Content Digest — KW {week}/{year}

## Top-Themen dieser Woche
1. **{Topic}** — {Short description} (Sources: {channels})
2. ...

## Telegram Highlights
### {Channel} ({Category})
- **Top Post** ({views} Views, {reactions} Reactions): {Summary}
  - Diskussion: {Comment summary}

## YouTube Highlights
### {Channel} ({Category})
- **"{Title}"** ({views} Views) — Key Points:
  - {Point 1}
  - {Point 2}
  - Kommentare: {Comment summary}

## Stimmungsbild
{Summary of dominant narratives, trends, and sentiment}
```

### Step 6: Write detail file

Save the full digest (all posts/videos, not just highlights) to:
`docs/digests/{YYYY-MM-DD}-content-digest.md`

Use the same format but include ALL posts and videos.
