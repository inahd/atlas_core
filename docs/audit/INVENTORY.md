# Atlas Inventory — April 21, 2026

## Engines by Subdirectory

### npu_engine/ (top level) — 40 files
Core computation modules. Most are imported by kernel.py or other engines.

| File | Purpose | Used by |
|------|---------|---------|
| datasets.py | Loads 240+ CSVs into entity/relation caches | Everything |
| graph_engine.py | Canonical relation graph (7208 nodes, 8466 edges) | /observe, /entity, spine |
| build_field_state.py | Orchestrates FieldState from 10 engines | /spine |
| field_state.py | FieldState dataclass | build_field_state |
| field_layers.py | S0-S6 layer mapping | /layers |
| field_to_sound.py | Nakshatra→graha→raga descent chain | sound_engine |
| igpu.py | iGPU render: 4 projections | /render |
| toroidal_field.py | Toroidal coordinates (OpenVINO NPU) | build_field_state |
| torus_queries.py | 108-pada torus knot queries | /observe |
| mandala_schema.py | Vastu mandala zone resolver (3-level) | /shell/state |
| vastu_engine.py | Vastu zone activation | /vastu |
| yantra_engine.py | Basic yantra generation | /yantra |
| yantra_generator.py | SVG yantra rendering | /yantra |
| vector_store.py | Embedding store (26k chunks) | /corpus/search |
| card_engine.py | Tarot/oracle card draws | /tarot |
| s5_kernel.py | Plant wheel (81 plants) | /s5 |
| jyotisha_engine.py | Swiss Ephemeris chart computation | /jyotish/* |
| jyotish_utils.py | Rashi/graha normalization, CSV loaders | jyotisha_engine |
| pasaka_engine.py | Pasaka dice oracle (3d4) | /lila/augury/pasaka |
| orientation.py | Philosophical orientation from chart | /orientation |
| coherence_engine_v2.py | Coherence scoring | build_field_state |
| modulation_engine.py | Field modulation | build_field_state |
| lifecycle_engine.py | Lifecycle phase | build_field_state |
| temple_geometry.py | Temple geometric layout | build_field_state |
| ui_vastu_engine.py | UI layout derivation (canonical pattern) | /mandala/layout |
| natal_musician.py | Natal→musician reading | /musician |
| relational_engine.py | Relational distance | graph queries |
| path_engine.py | Entity path traversal | codex |

### npu_engine/field/ — 34 files
Field-derived engines following the `derive_*()` pattern.

| File | Purpose | Route |
|------|---------|-------|
| composition_engine.py | Compose response from field | /compose |
| goloka_engine.py | Eternal Goloka state | /goloka |
| trajectory_engine.py | Temporal arc + dasha | /trajectory |
| reading_engine.py | 5-lens oracle reading | /reading |
| land_engine.py | Vastu land planning | /land |
| helix_engine.py | Dual helix, 90-day projection | /helix |
| intention_engine.py | Intention→favorable windows | /intention |
| system_engine.py | Hardware self-model | /system/state |
| site_engine.py | Terrain + hydrology + solar | /site |
| region_engine.py | iNat + PFAF regional plants | /plants/region |
| code_engine.py | Codebase dependency graph | Internal |
| layer_composer.py | Self-assembling S-layer pages | /layers |
| ring_engine.py | 10 ring types | /ring |
| symbol_engine.py | Emoji relational symbol | /symbol |
| city_engine.py | Hex city generation | /hexfield |
| iching_augury_engine.py | I Ching augury (Lo Shu weighted) | /lila/augury/* |
| pasaka_engine.py | Pasaka field-derived cast | /lila/augury/pasaka/field |
| transit_engine.py | Tarabala transit analysis | /transit/analysis |
| briefing_engine.py | Daily briefing (LLM) | /briefing |
| geosolar_engine.py | Solar/wind/barometric logger | /geosolar |
| svarodaya_engine.py | Breath/svara rules | /svarodaya |
| dinacharya_engine.py | Daily routine | /dinacharya |
| chandas_engine.py | Vedic metre scoring | /chandas |
| astrobotany_engine.py | Plant lunar phase | /astrobotany |
| yantra_extension_engine.py | Kronecker tensor yantra (81x81) | Research |
| yantra_navagraha_engine.py | Navagraha eigendecomposition | Research |
| yantra_router.py | Lo Shu matrix routing | /yantra |
| resonance_engine.py | Field resonance | S-layer pages |
| semantic_engine.py | Semantic field queries | Internal |
| interpret_engine.py | Field interpretation | /interpret |
| llm_composition_engine.py | LLM composition | /compose |
| guild_planner.py | Guild planning | /guild/plan |

### npu_engine/engines/ — 12 files (Zone engines)
9 ZoneEngine subclasses + base + guild + sound.

### npu_engine/sound/ — 22 files
Full audio pipeline: tanpura, sarangi, bija, tabla, santoor, phrase, raga graph.

### npu_engine/vocal/ — 11 files
Vocal synthesis: bhava, breath, gamaka, phoneme, svara, syllable.

### npu_engine/rhythm/ — 13 files
Rhythm engine: tala, theka, tihai, layakari, cross-rhythm, tabla intelligence.

### npu_engine/mix/ — 11 files
Audio mix: per-nakshatra, per-guna, per-deity, authority-weighted.

### npu_engine/routes/ — 9 blueprints (112 routes total)

| Blueprint | Routes | Domain |
|-----------|--------|--------|
| system_bp | 25 | Health, audio, capabilities |
| sound_bp | 26 | Sound modes, OSC, raga |
| plants_bp | 17 | Regional plants, PFAF, USDA |
| render_bp | 10 | iGPU projections, bandhu figure |
| jyotish_bp | 10 | Chart, natal, transits, wave field, calendar |
| corpus_bp | 8 | Text search, registry |
| reading_bp | 8 | Oracle readings (5 lenses) |
| symbols_bp | 8 | Emoji symbol system |

## Datasets — 42 Domains, 240 CSVs, 677 JSONs

Top domains by file count:
relations (27 csv), cosmology (20 csv), ayurveda (18 csv),
astro (16 csv), sound (11 csv), vastu (11 csv), plants (12 total),
iching (9 csv), entities (8 csv), gandharva (7 csv), geography (7 csv),
species (7 csv), symbols (7 csv), carnatic (7 csv), sources (8 total)

## Static HTML — 17 pages

S-layer pages: s0.html through s6.html (7)
Tools: oracle.html, shalaka.html, jyotish_chart.html, glyphs.html (4)
Portals: home.html, index.html, dashboard.html, hexd-portal.html (4)
Assets: atlas.js, atlas-theme.css, interaction_engine.js

## Research Papers

| File | Date | Subject | Status |
|------|------|---------|--------|
| yantra_eigenvalue_exploration.md | Apr 12 | Lo Shu eigenvalues, 7 findings | Complete |
| two-source-interference-v3.md | Apr 17 | Aspect theory as wave interference, 8 findings | Draft v3 |
| planetary-primes-v1.md | Apr 17 | Retrograde symmetries + vertebral | Draft v1 |
| vertebral-primes-v1.md | Apr 17 | Cross-species skeletal analysis | Draft v1 |
| 8 deep-research-reports | Mar 27 | Various deep research topics | Reference |
| 11 domain research notes | Mar 27 | Carnatic tala, chandas, gandharva, etc. | Reference |
