# Atlas Core — System Map
# Ground truth for the computation layer.
# Updated: 2026-04-08

---

## What this is

Clean computation layer extracted from atlas_330.
JSON-only kernel + engines + datasets + corpus.
No apps, no HTML, no audio output, no presentation.

---

## ESSENTIAL — must run for system to work

### Kernel
| File | Role | Depends on |
|------|------|------------|
| `kernel.py` | Flask spine, ~182 JSON routes, port 5000 | npu_engine/, datasets/, drik_panchanga.py |
| `drik_panchanga.py` | Vedic panchanga calculator (Swiss Ephemeris, Lahiri) | swisseph (pip) |

### NPU Engine — core reasoning
| File | Role | Status |
|------|------|--------|
| `npu_engine/datasets.py` | Loads 150+ CSVs → entity graph | stable |
| `npu_engine/graph_engine.py` | Canonical relation graph (7208 nodes, 8466 edges) | stable |
| `npu_engine/build_field_state.py` | FieldState construction from panchanga + graph | stable |
| `npu_engine/field_state.py` | FieldState dataclass | stable |
| `npu_engine/field_layers.py` | S0-S6 layer mapping from spine | stable |
| `npu_engine/field_to_sound.py` | Nakshatra → graha → raga descent chain | stable |
| `npu_engine/mandala_schema.py` | Vastu mandala zone resolver (3-level nesting) | working |
| `npu_engine/igpu.py` | iGPU render engine — 3 projections + 4D + motion | stable |
| `npu_engine/toroidal_field.py` | Toroidal coordinate system (OpenVINO NPU) | stable |
| `npu_engine/torus_queries.py` | 108-pada torus knot queries | stable |

---

## Key JSON Endpoints
| Route | Method | Returns |
|-------|--------|---------|
| `/field` | GET | Full panchanga + field state |
| `/spine` | GET | Unified field + entities + layers + sound_spec + trajectory |
| `/observe` | POST | Deep entity dive: graph + torus + deity + plant + passages |
| `/render` | GET | iGPU render: ?projection=plane\|toroid\|hex\|4d |
| `/render/eternal` | GET | Canonical entity positions (eternal cosmology) |
| `/render/bandhu` | GET | SVG figure (?layers=all&dhatu=D005&zoom=2.0) |
| `/trajectory` | GET | Temporal arc: lunar phase, dasha context, musical implications |
| `/goloka` | GET | Eternal Goloka state: ashtakala, forest, sakhi, devi |
| `/bandhu/chat` | POST | Composition engine: pada + passage + metre |
| `/reading` | POST | Oracle reading: tarot/iching/jyotish/calendar/bandhu |
| `/guild/state` | GET | Plant guild: anchor + companions + moon phase |
| `/land` | GET | Vastu land planning: 9 zones + recommendations |
| `/land/mandala` | GET | Permaculture mandala design |
| `/land/layout` | GET | GeoJSON vastu zones (?lat=X&lon=Y&radius_m=50) |
| `/site/state` | GET | Terrain + hydrology + solar + suitability |
| `/plants/region` | GET | iNat + PFAF + USDA regional plants |
| `/plants/field` | GET | Plants scored by 4D field coherence |
| `/corpus/search` | GET | Full text search across 80+ texts |
| `/corpus/registry` | GET | Available text corpora |
| `/system/state` | GET | Hardware + audio + capabilities self-model |
| `/intention/classify` | POST | Intention → favorable field windows |
| `/calendar/day` | GET | Full muhurta breakdown |
| `/coherence` | GET | Top-N entities by coherence score |
| `/research/files` | GET | File browser (?dir=geography) |
| `/research/file` | GET | Raw file content |

---

## Engines (verified 2026-04-08)

### field/ engines
| Engine | Route |
|--------|-------|
| `npu_engine/field/composition_engine.py` | `/bandhu/chat` |
| `npu_engine/field/goloka_engine.py` | `/goloka` |
| `npu_engine/field/trajectory_engine.py` | `/trajectory` |
| `npu_engine/field/reading_engine.py` | `/reading/bandhu` |
| `npu_engine/field/land_engine.py` | `/land`, `/land/layout`, `/land/mandala` |
| `npu_engine/field/symbol_engine.py` | `/symbol/*` |
| `npu_engine/field/helix_engine.py` | `/helix` |
| `npu_engine/field/intention_engine.py` | `/intention/*` |
| `npu_engine/field/system_engine.py` | `/system/state`, `/system/audio` |
| `npu_engine/field/code_engine.py` | (internal) |
| `npu_engine/field/site_engine.py` | `/site/state`, `/site/swales`, `/site/suitability` |
| `npu_engine/field/region_engine.py` | `/plants/region` |

### Other engines
| Engine | Route |
|--------|-------|
| `npu_engine/engines/guild_engine.py` | `/guild/state` |
| `npu_engine/renderers/figure_renderer.py` | `/render/bandhu` |
| `npu_engine/igpu.py` | `/render` |
| `npu_engine/toroidal_field.py` | (core) |
| `npu_engine/graph_engine.py` | (core) |
| `npu_engine/datasets.py` | (core) |
| `npu_engine/mandala_schema.py` | `/shell/state` |
| `npu_engine/field_layers.py` | (core) |
| `npu_engine/field_to_sound.py` | `/sound/*` |
| `npu_engine/build_field_state.py` | `/spine` |
| `npu_engine/s5_kernel.py` | `/plants/*` |
| `npu_engine/card_engine.py` | `/card/*` |
| `npu_engine/vector_store.py` | (core) |
| `npu_engine/vastu_engine.py` | `/vastu` |
| `npu_engine/yantra_engine.py` | `/yantra` |

### Engines that do NOT exist
- `kala_engine.py` — NOT BUILT
- `bot_engine.py` — NOT BUILT

---

## Datasets
| Path | Count | Role |
|------|-------|------|
| `datasets/` | 150+ CSVs | The knowledge base |
| `datasets/relations/` | ~1442 edges | Graph edges (text-entity links) |
| `datasets/relations/relations_resolved_canon.csv` | canonical | DO NOT MODIFY |
| `datasets/sources/` | 14 text domains, 26k JSONL chunks | Fetched texts |
| `datasets/cosmology/` | deity, festival, nakshatra, goloka | Cosmological reference data |
| `datasets/compositions/` | Narottama padas, navagraha kritis | Gaudiya composition corpus |
| `datasets/chandas/` | metres_forms, correspondence_matrix | Chandas metre data by rasa |
| `datasets/plants/` | 27 nakshatra plants, 216 guild relations | Agriculture + permaculture |
| `datasets/ayurveda/` | 704 herbs + 7 dhatu render params | Dosha matrix, herb spine |
| `datasets/morphogenesis/` | body_archetype_map(26), doctrine_of_signatures(44) | Body-plant-geometry |
| `datasets/geography/` | pithas(63), sacred_sites(34), body_relations(45) | Sacred geography |
| `datasets/system/` | system_topology, code_topology, capabilities | Self-model |

---

## NPU Engine — supporting modules

| File | Role | Status |
|------|------|--------|
| `npu_engine/tanpura_engine.py` | 4-string engine, CSV-driven, render_fn injection | stable |
| `npu_engine/sarangi_voice.py` | Bowed gut string, cached render_looped | stable |
| `npu_engine/bija_synth.py` | Formant bija mantra synthesis | stable |
| `npu_engine/relational_params.py` | Field → instrument physics (NamedTuples) | stable |
| `npu_engine/tanpura_field.py` | Field → tanpura tuning (22-shruti) | stable |
| `npu_engine/phrase_engine.py` | Live raga graph traversal → note events | stable |
| `npu_engine/natal_musician.py` | Natal chart → musician reading | stable |
| `npu_engine/sound/sound_engine.py` | Sound spec derivation (trajectory-aware) | stable |
| `npu_engine/sound/osc_bridge.py` | OSC → SuperCollider (port 57120) | stable |
| `npu_engine/engines/` | 9 ZoneEngine subclasses (vastu zones) | stable |
| `npu_engine/s5_kernel.py` | Plant wheel (3 rings, 81 plants) | stable |
| `npu_engine/card_engine.py` | Devi tarot card draw/spread | stable |
| `npu_engine/codex_engine.py` | Codex text retrieval | stable |
| `npu_engine/codex_interaction.py` | Entity → codex passages | stable |
| `npu_engine/vector_store.py` | Embedding store for passage search | stable |
| `npu_engine/vastu_engine.py` | Vastu zone activation | stable |
| `npu_engine/yantra_engine.py` | Yantra geometry computation | stable |
| `npu_engine/field/code_engine.py` | Codebase dependency graph | stable |

---

## Scripts

| File | Role |
|------|------|
| `scripts/porter.py` | Audio connection watchdog |
| `scripts/session_open.py` | Session start |
| `scripts/session_close.py` | Session end |
| `scripts/fetch_texts.py` | GRETIL text downloader |
| `scripts/fetch_archive.py` | Literature harvester (57 texts) |
| `scripts/text_entity_linker.py` | Graph-coherence text linking |

---

## Not in this repo (lives in atlas_330 app layer)

| Component | Why excluded |
|-----------|-------------|
| `om.py` | Audio output — presentation |
| `sc/` | SuperCollider — presentation |
| `static/` | HTML/CSS/JS — presentation |
| `apps/` | HTML apps — presentation |
| `hexfield.py` | pygame TUI — presentation |
| `start.sh` | Boots audio + apps — orchestration |

---

## Known issues

- `kernel.py` is ~9800 lines — edits need precise line targeting
- Tanpura engine: circular import fixed via render_fn injection
- Figure renderer: body coordinates hardcoded
- Some sound routes send OSC to om.py which isn't in this repo — they return JSON specs but the actual playback needs the app layer
