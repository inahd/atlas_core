# CLAUDE.md — Atlas Core

## What this is
Clean computation layer. Engine + corpus + kernel.
Returns JSON only. No apps. No HTML. No presentation.

engine computes → corpus holds → apps present elsewhere

## Read first
1. `docs/ARCHITECTURE.md` — design principles
2. `SYSTEM_MAP.md` — current engine state
3. `CORE_SCOPE.md` — boundary definition

## Before any task
```python
from npu_engine.field.code_engine import derive_code_context
ctx = derive_code_context('your task description')
# ctx['files_to_read']      — read these first
# ctx['fragile_points']     — handle with care
# ctx['related_routes']     — Flask routes affected
# ctx['known_issues']       — current bugs in this area
```

## Core entry points
| Function | Module | Returns |
|----------|--------|---------|
| `field_state()` | kernel.py | Complete field state dict |
| `calc_panchanga()` | kernel.py | Vedic panchanga |
| `derive_site_state()` | npu_engine/field/site_engine.py | Terrain + hydrology + solar |
| `derive_regional_plants()` | npu_engine/field/region_engine.py | iNat + PFAF + USDA plants |
| `derive_permaculture_mandala()` | npu_engine/field/land_engine.py | Ecosystem design |
| `derive_guild_state()` | npu_engine/engines/guild_engine.py | Plant guild from field |
| `build_field_state()` | npu_engine/build_field_state.py | Full FieldState object |

## Key JSON endpoints
| Route | Returns |
|-------|---------|
| `/field` | Panchanga + field state |
| `/spine` | Unified field + entities + layers + sound |
| `/observe` | Entity deep dive: graph + passages + relations |
| `/site/state` | Terrain + hydrology + solar + suitability |
| `/plants/region` | iNat + PFAF + USDA regional plants |
| `/land/mandala` | Permaculture mandala design |
| `/guild/state` | Plant guild from field state |
| `/corpus/search` | Full text search across 80+ texts |
| `/coherence` | Top-N entities by coherence score |
| `/trajectory` | Temporal arc: lunar + dasha + musical |
| `/goloka` | Eternal Goloka: ashtakala + sakhi + forest |
| `/calendar/day` | Full muhurta breakdown |
| `/intention/classify` | Intention → favorable windows |
| `/system/state` | Hardware + audio + capabilities snapshot |

## S0–S6 Layer System
| Layer | Name | Domain |
|-------|------|--------|
| S0 | Bindu | Goloka · acintya · source · ashtakala |
| S1 | Archetype | 15 Nitya Devis · 9 Grahas · deity governance |
| S2 | Sound | Raga · tala · shruti · bija · vocal |
| S3 | Rhythm | Panchanga · tithi · nakshatra · muhurta · dasha |
| S4 | Geometry | Vastu · yantra · 108 pada topology · torus knot |
| S5 | Nature | Ayurveda · plant wheel · dosha · marma · herb |
| S6 | Lila | Practice · codex · altar · lila maps |

## Four Axes — Never Collapse
| Axis | Range | Meaning |
|------|-------|---------|
| **theta** (θ) | S0→S6 | Level of manifestation |
| **phi** (φ) | witness↔participant | Mode of engagement |
| **S-layer** | S0-S6 | Which domain ring |
| **path** | 0.0→1.0 | Bheda-abheda (unity↔distinction) |

## Boundary rule
Returns JSON → belongs here.
Returns HTML/SVG/audio/redirect → belongs in app layer.

## Do Not Touch
- `datasets/relations/relations_resolved_canon.csv` — canonical edges
- `npu_engine/` — do not rename (package name hardcoded everywhere)
- `instance/personal/` — personal data (natal.json, altar.json)
- Running kernel — don't restart without asking

## NPU Core API
```python
from npu_engine import datasets as DS
DS.load_all_entities()      # {entity_id: (theta, phi)}
DS.load_entity_metadata()   # {entity_id: {name, category, element, guna, ...}}
DS.load_relations()         # {entity_id: [{to_id, relation, confidence}]}
```
Entity IDs: `category_slug` (e.g. `nakshatra_rohini`, `deity_agni`, `plant_tulsi`)

## Known fragile points
- `kernel.py` is ~9800 lines — edits need precise line targeting
- `npu_engine/tanpura_engine.py` — circular import fixed via render_fn injection
- `figure_renderer.py` — body coordinates hardcoded, changing breaks all layers

## Session Protocol
1. Read this CLAUDE.md
2. Work — commit with ✦ prefix

## What not to do
- Do not assume kala_engine.py or bot_engine.py exist — they don't
- Do not add routes without checking `grep -n "def <name>" kernel.py` for duplicates
- Do not write to canonical graph without user confirmation
- Do not flatten the four axes
- Do not rebuild what already exists — audit first

## User
**inahd** · Gainesville FL · van life
Natal: Jan 27 1983 · 11:57am · Montreal · Lagna: Vṛṣabha · Rohiṇī pada 1
Mercury dasa closes Oct 2027. Chart at `instance/personal/natal.json`.
