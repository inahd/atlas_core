# Coherence Atlas

A living Vedic field computer. Computes panchanga, generates sound
and visual states from 110 CSV datasets across 33 knowledge domains.

## Start

```bash
./start.sh
```

Opens http://localhost:5000

## Stack

| Component | File | Purpose |
|-----------|------|---------|
| Kernel | `kernel.py` | Flask API — field computation, 60 HTTP endpoints |
| Sound | `atlas_synth.scd` | SuperCollider — 19 synths, 41 OSC handlers |
| Bridge | `bridge.py` | Polls kernel, renders events, sends OSC to SC |
| Frontend | `atlas.html` | Browser environment — Canvas2D field + codex terminal |
| NPU | `npu_engine/` | 24 modules — graph, codex, query, renderers |
| Data | `datasets/` | 110 CSVs — nakshatras, ragas, plants, deities, yoga |
| Apps | `apps/` | 15 standalone HTML apps served via iframe overlay |
| Wiki | `wiki/` | 105 entity markdown pages |

## Requirements

- Python 3.11+ (Flask, pythonosc)
- SuperCollider 3.14+ with Jack audio
- Browser (Canvas2D, WebAudio)

## Key Endpoints

```
GET  /field          — full panchanga + field state
GET  /spine          — enriched field with entities + sound
GET  /coherence?n=N  — top N coherent entities
GET  /mandala/layout — 5-ring relational mandala data
GET  /sound/state    — current raga, tala, bpm
POST /observe        — entity observation (7-domain reading)
```

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md), [SOUND.md](SOUND.md),
[DATASETS.md](DATASETS.md), [APPS.md](APPS.md), [NPU.md](NPU.md).
