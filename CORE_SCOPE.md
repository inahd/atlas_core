# Core Scope — Atlas Boundary Definition

## The Rule

**Core = returns JSON. Period.**

Not core = returns HTML, SVG, audio, files, redirects to apps.

```
engine computes → corpus holds → apps present elsewhere
```

## What belongs in atlas_core

| Component | Why |
|-----------|-----|
| `kernel.py` | JSON-only Flask routes (~182 endpoints) |
| `npu_engine/` | All computation engines (163 files) |
| `datasets/` | Knowledge base (150+ CSVs, 7208 entities, 8466 edges) |
| `datasets/sources/` | Text corpus (80+ texts, 26k JSONL chunks, 9 traditions) |
| `drik_panchanga.py` | Vedic panchanga calculator |
| `core/` | Coherence engine |
| `docs/` | Architecture documentation |
| `scripts/` | Utility scripts |
| `research/` | Research artifacts |
| `instance/personal/` | Natal chart, altar state |

## What does NOT belong in atlas_core

| Component | Why | Where it lives |
|-----------|-----|----------------|
| `apps/` | HTML presentation | atlas_330 (future: atlas_apps) |
| `static/` | HTML/CSS/JS | atlas_330 (future: atlas_apps) |
| `om.py` | Audio output | atlas_330 |
| `sc/` | SuperCollider | atlas_330 |
| `hexfield.py` | pygame TUI | atlas_330 |
| `start.sh` | Orchestration | atlas_330 |
| `brahmanda4.html` | HTML page | atlas_330 |

## Boundary test

When adding a new route or feature, ask:

1. Does it `return jsonify(...)` or `return app.response_class(..., mimetype="application/json")`?
   → **Yes** → belongs in atlas_core
2. Does it `return send_from_directory(...)` or `return redirect(...)`?
   → **No** → belongs in app layer
3. Does it generate audio, HTML, or serve static files?
   → **No** → belongs in app layer

## The three pillars

```
┌─────────────────────────────────────┐
│           atlas_core                │
│                                     │
│  ┌──────────┐  ┌──────────────┐    │
│  │  Engine   │  │   Corpus     │    │
│  │npu_engine/│  │datasets/     │    │
│  │163 files  │  │sources/      │    │
│  │30k lines  │  │80+ texts     │    │
│  └─────┬─────┘  └──────┬───────┘    │
│        │               │            │
│        ▼               ▼            │
│  ┌──────────────────────────────┐   │
│  │       kernel.py              │   │
│  │    ~182 JSON routes          │   │
│  │    port 5000                 │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
         │
         │ JSON API
         ▼
┌─────────────────────────────────────┐
│     App Layer (separate repo)       │
│  apps/ · static/ · om.py · sc/     │
│  HTML · SVG · Audio · Presentation  │
└─────────────────────────────────────┘
```
