# Atlas Core Scope

This directory marks the boundary of the core computation and corpus layer.
Everything here computes, holds, or documents. Nothing here presents.

## What is core

### Engine (`npu_engine/`)
The computation substrate. 163 Python files, 30k lines.
Computes field state, graph relations, coherence scores, sound specs,
trajectories, guild assignments, land analysis, site terrain.
All engines follow the `derive_*()` contract: never raises, all keys guaranteed.

### Corpus (`datasets/sources/`)
The textual inheritance. 80+ texts across 9 traditions.
JSONL chunks + raw text files. `corpus_registry.json` is the index.
Domains: Gaudiya, Vedic, Yoga, Jyotish, Ayurveda, Dharma, Cosmology, Vastu, Epics.

### Datasets (`datasets/`)
The knowledge base. 37 directories, 150+ CSVs.
Entities, relations, plants, geography, cosmology, morphogenesis, sound.
`datasets.py` loads everything. `graph_engine.py` indexes it.

### Research (`research/`)
Active research artifacts. Anomalies, briefs, seeds, artifacts, queue.

### Docs (`docs/`)
Architecture, schemas, audit reports, session handoffs.

## What is NOT core

### Apps (`apps/`, `static/`)
Presentation layer. HTML/CSS/JS. Reads from core via HTTP.
Includes: /study, /hexd, /kala, /lila-streams, /toroid_yantra, etc.
Apps are consumers of core, not part of it.

### Kernel (`kernel.py`)
The HTTP spine. Routes core computation to apps.
Minimal server — just wires `derive_*()` functions to JSON endpoints.
Core-adjacent but not core itself.

### Audio (`om.py`, `sc/`)
Sound synthesis output. Reads from core field state.
Independent process that consumes `field_to_sound` output.

## Separation principle

```
  engine computes → corpus holds → apps present later
```

The engine layer produces validated dicts from datasets and field state.
The corpus layer holds canonical and acquired text.
The app layer (not here) presents those dicts and texts to humans.

This separation means:
- Engine changes don't require app changes
- Corpus additions don't require engine changes
- App redesigns don't touch computation or data
- Any new app can read from the same core

## Core entry points

| Entry | Function | Returns |
|-------|----------|---------|
| `npu_engine.build_field_state` | `build_field_state(panchanga)` | Complete FieldState dict |
| `npu_engine.datasets` | `load_all_entities()` | 7208 entities with θ,φ |
| `npu_engine.graph_engine` | `GraphEngine().query()` | Relation graph traversal |
| `npu_engine.field.region_engine` | `derive_regional_plants(lat,lon)` | iNat + PFAF + USDA plants |
| `npu_engine.field.site_engine` | `derive_site_state(lat,lon)` | Terrain + hydrology + solar |
| `npu_engine.field.land_engine` | `derive_permaculture_mandala(fs,lat,lon)` | Ring-based ecosystem design |
| `npu_engine.engines.guild_engine` | `derive_guild(fs)` | Plant guild from field state |

## Corpus entry points

| Path | Content |
|------|---------|
| `datasets/sources/corpus_registry.json` | 81-entry text index |
| `datasets/sources/manifest.json` | 19-entry acquisition manifest |
| `datasets/sources/{domain}/{text}_chunks.jsonl` | Text chunks |
| `datasets/sources/{domain}/{text}.txt` | Raw text files |

## What this directory is for

This `core/` directory is a scope marker, not a code container.
The actual code lives in `npu_engine/`, `datasets/`, `research/`, `docs/`.
This file exists to make the boundary explicit and prevent apps from
creeping into the computation layer.
