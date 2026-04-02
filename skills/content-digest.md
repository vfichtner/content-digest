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
