# Content Digest Skill - Design

## Überblick

Ein Claude Skill `/content-digest`, der on-demand Telegram-Kanäle und YouTube-Kanäle der letzten Woche analysiert, nach Engagement gewichtet und eine deutsche Zusammenfassung liefert.

## Architektur

```
┌─────────────────┐     ┌──────────────────────┐     ┌─────────────────────┐
│  Telegram MCP   │     │   Content Digest      │     │  YouTube MCP        │
│  Server (neu)   │◄────│   Skill (neu)         │────►│  Server (bestehend/ │
│  Python/Telethon│     │  Orchestriert beides   │     │   oder neu)         │
└─────────────────┘     └──────────────────────┘     └─────────────────────┘
                               │
                        ┌──────┴───────┐
                        │ Config Files │
                        │ telegram.yaml│
                        │ youtube.yaml │
                        └──────────────┘
```

**Output:**
- Konversation: Kompakte Zusammenfassung mit Top-Themen und Highlights
- Datei: `docs/digests/YYYY-MM-DD-content-digest.md` mit allen Details

**Sprache:** Alles Deutsch, unabhängig von Quellsprache.

## Komponente 1: Telegram MCP Server

**Technologie:** Python mit Telethon, lokaler MCP Server via `stdio`.

**Tools:**
- `telegram_list_channels` - Listet abonnierte Kanäle auf
- `telegram_get_posts(channel, days=7)` - Posts eines Kanals der letzten X Tage, inkl. Views, Reactions, Forwards
- `telegram_get_comments(channel, post_id)` - Kommentare zu einem bestimmten Post
- `telegram_get_post_stats(channel, post_id)` - Detaillierte Engagement-Metriken

**Authentifizierung:** Telethon Session-Datei. Einmalige Anmeldung mit Phone-Number + Code, danach persistent.

**Config `~/.claude/config/telegram-channels.yaml`:**
```yaml
channels:
  - name: "@dulorov"
    category: "Tech"
  - name: "@python_digest"
    category: "Dev"
  - name: "@ai_news_feed"
    category: "AI"

defaults:
  days: 7
```

**Projektstruktur:**
```
telegram-mcp/
  pyproject.toml
  src/
    server.py       # MCP Server Einstiegspunkt
    telegram.py     # Telethon Client Wrapper
    config.py       # YAML Config Loader
```

## Komponente 2: YouTube MCP Server

**Ansatz:** Bestehenden Community YouTube MCP Server nutzen. Falls keiner alle Features abdeckt (besonders Transkripte), schlanken eigenen bauen.

**Benötigte Funktionen:**
- Kanal-Videos der letzten X Tage auflisten
- Video-Transkripte abrufen (Untertitel/Captions)
- Kommentare zu Videos laden
- Basis-Metriken (Views, Likes, Comments Count)

**Libraries (falls eigener Server):** `google-api-python-client` + `youtube-transcript-api`

**Config `~/.claude/config/youtube-channels.yaml`:**
```yaml
channels:
  - id: "UCxxxxxx"
    name: "Fireship"
    category: "Dev"
  - id: "UCyyyyyy"
    name: "Theo"
    category: "Tech"

defaults:
  days: 7
```

## Komponente 3: Content Digest Skill

**Aufruf:** `/content-digest` mit optionalen Parametern.

**Parameter:**
- `days=7` - Zeitraum (Default: 7)
- `source=all|telegram|youtube` - Nur eine Quelle oder beide (Default: all)
- `category=Tech` - Nur bestimmte Kategorie filtern

**Beispielaufrufe:**
- `/content-digest` - Alles, letzte 7 Tage
- `/content-digest days=3` - Nur letzte 3 Tage
- `/content-digest source=telegram` - Nur Telegram
- `/content-digest category=AI days=14` - Nur AI-Kategorie, 2 Wochen

**Ablauf:**
1. Config laden - Beide YAML-Dateien lesen
2. Daten sammeln - Parallel Telegram-Posts und YouTube-Videos abrufen
3. Engagement bewerten - Posts/Videos nach Reactions, Views, Kommentaren ranken
4. Deep Dive - Für Top-Posts Kommentare nachladen, für Top-Videos Transkripte ziehen
5. Synthese - Alles auf Deutsch zusammenfassen, gewichtet nach Engagement

**Output-Format Konversation:**
```markdown
# Content Digest - KW 14/2026

## Top-Themen diese Woche
1. **Thema X** - Kurzbeschreibung (Quellen: @channel1, Fireship)
2. **Thema Y** - Kurzbeschreibung (Quelle: @channel2)

## Telegram Highlights
### @channel1 (Tech)
- Post mit meisten Reactions: ...
- Wichtigste Diskussion: ...

## YouTube Highlights
### Fireship (Dev)
- "Video Titel" (120k Views) - Key Points: ...

## Stimmungsbild
Zusammenfassung der dominanten Narrative und Trends
```

**Detail-Datei:** `docs/digests/YYYY-MM-DD-content-digest.md` - gleiche Struktur, aber mit allen Posts/Videos, nicht nur Highlights.

## Relevanz-Gewichtung

Engagement-basiert:
- **Telegram:** Reactions, Kommentaranzahl, Views, Forwards
- **YouTube:** Views, Likes, Kommentaranzahl

Posts/Videos mit höherem Engagement werden prominenter in der Zusammenfassung platziert und erhalten einen Deep Dive (Kommentare, Transkripte).

## Config-Speicherort

Global unter `~/.claude/config/` - nicht projektgebunden, da die Kanäle projektübergreifend relevant sind.

## Entscheidungen

- **Telegram Client API** (nicht Bot API) - voller Zugriff auf alles was der Account sieht
- **MCP Server Architektur** - ermöglicht dem Skill intelligentes, interaktives Nachladen
- **Bestehender YouTube MCP** - kein Rad neu erfinden, Fallback: eigener schlanker Server
- **Getrennte Config-Dateien** - unabhängig wartbar
- **Engagement-basierte Gewichtung** - objektiv, kein manuelles Tagging nötig
