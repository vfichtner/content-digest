---
name: content-digest
description: Monitors Telegram and YouTube channels, creates engagement-weighted German summaries of the last N days
---

## Parameter

Parse diese aus dem Aufruf des Users:
- `days` — Anzahl Tage zurückblicken. Default: 7
- `source` — `all`, `telegram`, oder `youtube`. Default: `all`
- `category` — Filter nach Kategorie aus der Config. Default: alle Kategorien

## Anweisungen

Du bist ein Content-Analyst und erstellst einen deutschsprachigen Digest von Telegram- und YouTube-Kanälen.

### Schritt 1: Configs laden

Lies beide Config-Dateien:
- `~/.claude/config/telegram-channels.yaml`
- `~/.claude/config/youtube-channels.yaml`

Falls `source` auf eine Quelle beschränkt ist, überspringe die andere. Falls `category` gesetzt ist, filtere die Kanäle.

### Schritt 2: Telegram-Daten sammeln

Für jeden Telegram-Kanal in der Config:
1. Rufe `telegram_get_posts(channel=<name>, days=<days>)` auf
2. Identifiziere die Top 3 Posts nach engagement_score
3. Für die Top 3 Posts, rufe `telegram_get_comments(channel=<name>, post_id=<id>)` auf

### Schritt 3: YouTube-Daten sammeln

Für jeden YouTube-Kanal in der Config:
1. Rufe `get_channel_videos(channel_id=<id>)` auf — filtere auf die letzten N Tage
2. Für die Top 3 Videos nach Views, rufe `get_video_transcript(video_id=<id>)` auf
3. Für die Top 3 Videos, rufe `get_video_comments(video_id=<id>)` auf

### Schritt 4: Analysieren & Ranken

Ranke allen Content nach Engagement:
- Telegram: engagement_score aus der API
- YouTube: views + likes*5 + comments*3

Identifiziere quellenübergreifende Themen — Themen die sowohl in Telegram ALS AUCH YouTube auftauchen werden höher gewichtet.

### Schritt 5: Zusammenfassung in der Konversation

Ausgabe auf Deutsch, folgendes Format:

```
# Content Digest — KW {woche}/{jahr}

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

### Schritt 6: Detail-Datei schreiben

Speichere den vollständigen Digest (alle Posts/Videos, nicht nur Highlights) unter:
`docs/digests/{YYYY-MM-DD}-content-digest.md`

Verwende das gleiche Format, aber mit ALLEN Posts und Videos.
