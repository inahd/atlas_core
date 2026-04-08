# Atlas Restructure Plan — 2026-04-05

Full audit of npu_engine/ (202 files, 30,164 lines) and kernel.py (9,267 lines, 219 routes).

---

## 1. CURRENT STATE

### 1.1 npu_engine/ Module Inventory

**Foundation (root level — implementations)**

| Module | Lines | Role |
|--------|-------|------|
| field_state.py | 102 | FieldState dataclass — the universal spine |
| toroidal_field.py | 665 | 2-axis coordinate system (θ, φ) |
| datasets.py | 1,366 | Universal CSV/JSON loader, 7208 entities |
| graph_engine.py | 277 | Canonical relation graph, 8466 edges |
| coherence_engine_v2.py | 209 | Relation-aware reranking |
| build_field_state.py | 318 | THE pipeline orchestrator |
| vector_store.py | 699 | SentenceTransformer passage search |
| igpu.py | 787 | iGPU render: 4 projections, entity layout |
| mandala_schema.py | 2,310 | Vastu mandala zone resolver (9 zones, 3 nesting levels) |

**Sound synthesis (root level)**

| Module | Lines | Role |
|--------|-------|------|
| tanpura_engine.py | 559 | 4-string additive synthesis |
| sarangi_voice.py | 378 | Bowed gut string at Sa |
| bija_synth.py | 248 | Formant mantra synthesis |
| tabla_sampler.py | 241 | 7 percussion WAV samples |
| field_to_sound.py | 429 | Descent chain: nakshatra→graha→raga |
| tanpura_field.py | 243 | Tanpura tuning from field |
| raga_graph.py | 442 | Melodic phrase graph, JI ratios |
| phrase_engine.py | 393 | Live raga traversal → note events |
| swara_engine.py | 336 | Planetary gaze → musical expression |
| natal_musician.py | 656 | Natal chart → musician reading |
| relational_params.py | 182 | Field → instrument physics params |
| relational_synth.py | 271 | Entity graph → synthesis params |
| mudra_graph.py | 423 | Rasa → mudra mappings |
| composition_db.py | 242 | Playlist and mantra selection |
| aspect_repair.py | 228 | Planetary aspect edges |

**Text/knowledge (root level)**

| Module | Lines | Role |
|--------|-------|------|
| codex_engine.py | 535 | Graph-derived codex generation |
| codex_interaction.py | 140 | Entity → codex passages |
| codex_modes.py | 17 | 5 canonical codex modes |
| library_kernel.py | 285 | Library state builder |
| passage_resolver.py | 177 | Passage search and ranking |
| path_engine.py | 388 | Relational path traversal |
| query_engine.py | 212 | Structured field query |
| treasury.py | 201 | Content treasury resolver |
| generator.py | 393 | NPU content generator |

**Geometry/spatial (root level)**

| Module | Lines | Role |
|--------|-------|------|
| vastu_engine.py | 406 | S4 spatial geometry from S3 time |
| ui_vastu_engine.py | 496 | Interface layout from field state |
| yantra_engine.py | 296 | Sacred geometry from field |
| yantra_generator.py | 247 | Sri Yantra SVG generation |
| temple_geometry.py | 219 | Formation detection |
| torus_queries.py | 176 | 108-pada torus spatial queries |
| orientation.py | 192 | Philosophical orientation |

**Ecology/nature (root level)**

| Module | Lines | Role |
|--------|-------|------|
| s5_kernel.py | 307 | Plant wheel (3 rings, 81 plants) |
| card_engine.py | 462 | Oracle card engine |

**Layer/lifecycle (root level)**

| Module | Lines | Role |
|--------|-------|------|
| field_layers.py | 253 | S0-S6 generative layer mapping |
| layer_engine.py | 160 | Dataset → layer assignment |
| lifecycle_engine.py | 69 | Arc phase + formation lifecycle |
| modulation_engine.py | 102 | Bounded embedding modulation |
| relational_engine.py | 178 | NPU cluster component |

**Compatibility**

| Module | Lines | Role |
|--------|-------|------|
| _compat.py | 21 | Documents old→new import mapping (no actual re-exports) |
| __init__.py | 6 | Exports FieldState, build_field_state, apply_modulation, query_field_state |

### 1.2 Subdirectory Inventory

**field/ — 13 field computation engines**

| Module | Lines | Role |
|--------|-------|------|
| composition_engine.py | 617 | Narottama corpus, pada selection |
| reading_engine.py | 667 | 5 oracle lenses |
| intention_engine.py | 651 | Muhurta window scoring |
| trajectory_engine.py | 531 | Temporal arc, dasha context |
| system_engine.py | 501 | Hardware self-model |
| ring_engine.py | 493 | 10 ring types |
| guild_planner.py | 412 | Permaculture guild hex layout |
| code_engine.py | 396 | Codebase topology analysis |
| goloka_engine.py | 354 | Eternal ashtakala periods |
| city_engine.py | 344 | Hex city generation |
| helix_engine.py | 339 | Dual helix toroid |
| land_engine.py | 245 | Vastu spatial prescriptions |
| symbol_engine.py | 242 | Vedic symbol mapping |

**engines/ — 11 vastu zone engines**

| Module | Lines | Role |
|--------|-------|------|
| base_engine.py | 70 | ZoneEngine base class |
| center_engine.py | 85 | C · Brahma assembler |
| plant_engine.py | 214 | SW · Nirriti · 4D plant scoring |
| body_engine.py | 105 | S · Yama · marma/anatomy |
| guild_engine.py | 336 | Plant guilds from field |
| rhythm_engine.py | 37 | N · Kubera · tala/calendar |
| archetype_engine.py | 36 | NE · Ishana · deity/devi |
| sound_engine.py | 33 | NW · Vayu · raga/svara |
| ecology_engine.py | 33 | W · Varuna · plant/herb |
| codex_engine.py | 31 | E · Indra · text/study |
| action_engine.py | 31 | SE · Agni · ritual/craft |

**renderers/ — 2 visualization engines**

| Module | Lines | Role |
|--------|-------|------|
| figure_renderer.py | 1,177 | Bandhu body: 6 compositable layers |
| species_renderer.py | 205 | Species SVG rendering |

**sound/ — 17 files (15 re-exports + 2 implementations)**

| Module | Lines | Role |
|--------|-------|------|
| sound_engine.py | 374 | Sound spec from field state |
| osc_bridge.py | 58 | OSC to SuperCollider |
| (15 others) | 2 each | Re-exports from root-level modules |

**mix/ — 10 relational mixing files**

| Module | Lines | Role |
|--------|-------|------|
| mix_kernel.py | 152 | Top coordinator (runs every 4 beats) |
| graph_seed_data.py | 146 | Mix relational seeds |
| mix_history.py | 66 | Smoothing/change detection |
| mix_osc.py | 63 | OSC to SuperCollider |
| layer_graph.py | 43 | Layer-rasa-arc queries |
| sam_mix.py | 39 | Sam/khali mix events |
| authority_mix.py | 31 | Authority → mix character |
| deity_mix.py | 19 | Deity → mix bias |
| nakshatra_mix.py | 15 | Nakshatra → element bias |
| guna_mix.py | 15 | Guna → timbral character |

**rhythm/ — 10 tala/beat files**

| Module | Lines | Role |
|--------|-------|------|
| graph_seed_data.py | 275 | Tala/bol relational seeds |
| rhythm_kernel.py | 184 | Top coordinator |
| theka_engine.py | 94 | Theka variation |
| sam_field.py | 86 | Sam-gravity computation |
| tala_graph.py | 76 | Tala/vibhag/beat queries |
| rhythm_osc.py | 72 | OSC to SuperCollider |
| tihai_engine.py | 67 | Tihai calculation |
| cross_rhythm_engine.py | 54 | Polyrhythm generation |
| layakari_engine.py | 50 | Density multiplication |
| fill_engine.py | 48 | Fills approaching sam |

**sympathetic/ — 4 taraf string files**

| Module | Lines | Role |
|--------|-------|------|
| string_model.py | 118 | 13-string tuning model |
| sympathetic_kernel.py | 115 | Top coordinator |
| excitation.py | 71 | Excitation event detection |
| sympathetic_osc.py | 69 | OSC to SuperCollider |

**vocal/ — 9 voice synthesis files**

| Module | Lines | Role |
|--------|-------|------|
| graph_seed_data.py | 235 | Vocal relational seeds |
| vocal_kernel.py | 202 | Top coordinator |
| syllable_sequencer.py | 150 | Phoneme assembly |
| gamaka_engine.py | 106 | Ornament selection |
| breath_engine.py | 99 | Breath/silence placement |
| phoneme_graph.py | 91 | Matrika/bija phonemes |
| bhava_engine.py | 82 | Rasa → bhava state |
| svara_voice.py | 71 | Swara → vocal quality |
| vocal_osc.py | 111 | OSC to SuperCollider |

**game/ — 3 implementations + 3 re-exports**

| Module | Lines | Role |
|--------|-------|------|
| character_engine.py | 199 | Natal + field → character |
| lineage_engine.py | 163 | Accessible lineages |
| orientation_engine.py | 83 | Sura/asura orientation |
| card_engine.py | 2 | Re-export |
| generator.py | 2 | Re-export |
| relational_engine.py | 2 | Re-export |

**Re-export directories (pure forwarding)**

| Directory | Files | Purpose |
|-----------|-------|---------|
| core/ | 8 | Re-exports 7 foundational modules |
| geometry/ | 8 | Re-exports 7 spatial modules |
| text/ | 11 | Re-exports 10 text modules |
| time/ | 8 | Re-exports 7 temporal modules |
| ui/ | 3 | Re-exports 2 UI modules |
| system/ | 3 | Re-exports 1 system module |
| nature/ | 6 | Re-exports 5 ecology modules |
| zones/ | 13 | Re-exports all zone engines |

### 1.3 kernel.py Route Groups (219 routes)

| Group | Count | Lines | Primary npu_engine imports |
|-------|-------|-------|--------------------------|
| Health/OSC | 2 | 3615-3633 | — |
| Field/State | 10 | 3634-3960 | graph_engine, datasets, torus_queries |
| Orientation/Interact | 5 | 3966-4050 | orientation, datasets |
| Claims/Playlist/Observe | 4 | 4019-4220 | datasets, composition_db |
| Navigate | 1 | 4217 | graph_engine |
| Transits/Dasha/Mode | 4 | 4313-4355 | — |
| Spine | 1 | 4353 | build_field_state, field_layers, sound_engine, system_engine, trajectory_engine |
| Render | 6 | 4455-4643 | igpu, datasets |
| Sound | 16 | 4643-5260 | sound_engine, osc_bridge, bija_synth, natal_musician, swara_engine, mix |
| Mandala | 1 | 5261 | mandala_schema, graph_engine, field_layers, s5_kernel, engines.CENTER |
| Knowledge/S5 | 2 | 5366-5391 | graph_engine, s5_kernel |
| Cards | 3 | 5391-5428 | card_engine |
| Altar/Library | 3 | 5428-5478 | library_kernel |
| Plants | 14 | 5478-5968 | s5_kernel, guild_engine, plant_engine, graph_engine, pfaf.sqlite |
| Coherence | 4 | 5901-6030 | coherence_engine_v2 |
| Codex | 6 | 6040-6400 | codex_interaction, path_engine, query_engine, vector_store |
| Hexfield/Layer | 3 | 6327-6400 | layer_engine, codex_interaction |
| Vastu | 1 | 6403 | vastu_engine, ui_vastu_engine, sound_engine, osc_bridge |
| S3/Practice | 1 | 6518 | — |
| Bandhu/Compose | 3 | 6571-6660 | composition_engine |
| Graph/Entities | 1 | 6660 | graph_engine |
| Tarot/Archana | 3 | 6717-6867 | card_engine |
| Layers | 3 | 6937-6972 | — |
| Ollama | 1 | 6972 | — |
| Shells (shell/cosmos/live/helix) | 4 | 6992-7027 | static files |
| Shell/State | 1 | 7069 | mandala_schema, shell state |
| Yantra/Passages | 4 | 7027-7069 | yantra_generator, passage_resolver |
| Beat/Stream | 3 | 7193-7260 | — |
| Brahmanda | 1 | 7257 | yantra_engine |
| Domain Portals (kala/devi/deha/bhumi/vidya/lila) | 25 | 7407-7535 | static files |
| Game (city/ring/lila) | 15 | 7535-7800 | city_engine, ring_engine |
| Render/Bandhu | 4 | 8824-8870 | figure_renderer, species_renderer |
| Symbol | 3 | 8883-8901 | symbol_engine |
| Character | 4 | 8903-8925 | game.character_engine, game.lineage_engine, game.orientation_engine |
| Guild/Land | 7 | 8928-8975 | guild_engine, guild_planner, land_engine |
| Plants/Field | 3 | 8960-8984 | plant_engine, land_engine |
| System | 4 | 8989-9003 | system_engine |
| Research | 5 | 9071-9184 | — (file I/O) |
| Intention/Calendar | 4 | 8498-8605 | intention_engine |
| Journal | 3 | 8607-8660 | — (file I/O) |
| Trajectory/Reading/Goloka | 8 | 8707-8749 | trajectory_engine, reading_engine, goloka_engine |
| Static/Portal | 8 | 8119-8216 | — |
| Generated | 6 | 8222-8290 | generator |
| Docs | 2 | 8290-8316 | — |
| Treasury/Wheel | 3 | 8403-8498 | treasury, datasets |

### 1.4 Import Architecture

**Top-level imports (before create_app, lines 37-56):**
```
npu_engine.toroidal_field.ToroidalField
npu_engine.datasets.load_all_entities
npu_engine.relational_engine.RelationalEngine
npu_engine.temple_geometry.TempleGeometry
```

**Late top-level imports (inside create_app but before routes):**
```
npu_engine.field_to_sound.field_to_sound        (line 2443)
npu_engine.vector_store.get_vector_store         (line 3483)
```

**Inline imports: ~120 import statements across ~52 unique modules.**

Most-imported modules from kernel.py:
1. graph_engine — 12 uses
2. datasets — 7 uses
3. reading_engine — 5 uses
4. city_engine — 5 uses
5. igpu — 4 uses
6. system_engine — 4 uses
7. sound_engine — 4 uses
8. field_to_sound — 3 uses
9. intention_engine — 3 uses
10. card_engine — 3 uses

### 1.5 Circular Import Risks

**None detected.** The architecture is clean:
- Foundation modules (field_state, toroidal_field, datasets) import nothing from npu_engine
- build_field_state imports only field_state
- All field/ engines import from root-level modules, never from each other
- Re-export directories only re-export (no new logic)
- sound/ subdirectory is almost pure re-export (15 of 17 files)

**One known historical risk:** `tanpura_engine.py` had a circular import with om.py, fixed via render_fn injection. Not a npu_engine-internal issue.

### 1.6 Broken/Commented-Out Imports

None found. All 219 routes are active. _compat.py documents mapping but has no actual re-export code — it's a documentation-only file.

---

## 2. ZONE ASSIGNMENT

### Vastu Direction → Module Mapping

**C · Brahma — Center/Orchestration**
| Module | Why |
|--------|-----|
| build_field_state.py | THE pipeline orchestrator |
| field_state.py | Universal spine all modules consume |
| __init__.py | Package entry point |
| kernel.py | Flask spine |
| mandala_schema.py | Assembles all 9 zones |
| engines/center_engine.py | Already assigned C |
| coherence_engine_v2.py | Central scoring function |
| modulation_engine.py | Central modulation |
| lifecycle_engine.py | Central lifecycle |

**NE · Ishana — Archetype/Sacred Knowledge**
| Module | Why |
|--------|-----|
| goloka_engine.py | Eternal realm — highest manifestation |
| reading_engine.py | Oracle/divination — sacred knowledge |
| card_engine.py | Card oracle — sacred randomness |
| engines/archetype_engine.py | Already assigned NE |
| orientation.py | Philosophical orientation |
| game/orientation_engine.py | Sura/asura — sacred duality |

**E · Indra — Perception/Text/Knowledge**
| Module | Why |
|--------|-----|
| codex_engine.py | Text generation |
| codex_interaction.py | Entity → text |
| codex_modes.py | 5 codex modes |
| library_kernel.py | Library system |
| passage_resolver.py | Text passage search |
| path_engine.py | Graph traversal → text output |
| query_engine.py | Structured query |
| vector_store.py | Semantic search |
| treasury.py | Content treasury |
| engines/codex_engine.py | Already assigned E |
| composition_engine.py | Text composition (pada selection) |

**SE · Agni — Action/Transformation/Fire**
| Module | Why |
|--------|-----|
| city_engine.py | City generation — active world building |
| engines/action_engine.py | Already assigned SE |
| generator.py | Content generation — creative fire |
| game/character_engine.py | Character — active participation |
| game/lineage_engine.py | Lineage — active inheritance |
| symbol_engine.py | Symbol mapping — active signification |

**S · Yama — Body/Boundary/Structure**
| Module | Why |
|--------|-----|
| figure_renderer.py | Body rendering |
| species_renderer.py | Species rendering |
| engines/body_engine.py | Already assigned S |
| temple_geometry.py | Geometric structure |
| torus_queries.py | Spatial structure |

**SW · Nirriti — Plants/Decomposition/Ecology**
| Module | Why |
|--------|-----|
| s5_kernel.py | Plant wheel |
| engines/plant_engine.py | Already assigned SW |
| engines/guild_engine.py | Guild ecology |
| guild_planner.py | Permaculture planning |
| land_engine.py | Vastu land prescriptions |
| engines/ecology_engine.py | Already assigned W (ambiguous — ecology spans W and SW) |

**W · Varuna — Water/Depth/Nature**
| Module | Why |
|--------|-----|
| datasets.py | Deep data reservoir |
| graph_engine.py | Deep relational structure |
| engines/ecology_engine.py | Already assigned W |
| relational_engine.py | Deep relational processing |

**NW · Vayu — Sound/Wind/Transmission**
| Module | Why |
|--------|-----|
| tanpura_engine.py | Drone sound |
| sarangi_voice.py | Bowed sound |
| bija_synth.py | Mantra sound |
| tabla_sampler.py | Percussion sound |
| field_to_sound.py | Field → sound descent |
| tanpura_field.py | Tanpura tuning |
| raga_graph.py | Melodic graph |
| phrase_engine.py | Live melody |
| swara_engine.py | Planetary music |
| natal_musician.py | Natal music |
| relational_params.py | Sound params |
| relational_synth.py | Graph → synthesis |
| mudra_graph.py | Gesture/sound |
| composition_db.py | Compositions |
| aspect_repair.py | Aspect edges |
| sound/ (all) | Sound subsystem |
| mix/ (all) | Mixing subsystem |
| rhythm/ (all) | Rhythm subsystem |
| sympathetic/ (all) | Taraf resonance |
| vocal/ (all) | Voice synthesis |
| engines/sound_engine.py | Already assigned NW |

**N · Kubera — Time/Rhythm/Calendar**
| Module | Why |
|--------|-----|
| trajectory_engine.py | Temporal arc |
| intention_engine.py | Calendar scoring |
| helix_engine.py | Time helix |
| field_layers.py | Layer mapping (S0-S6 temporal ordering) |
| layer_engine.py | Layer assignment |
| engines/rhythm_engine.py | Already assigned N |
| ring_engine.py | Ring specifications (temporal rings) |

### Ambiguous Assignments

| Module | Candidates | Resolution |
|--------|-----------|------------|
| igpu.py | C (central render) or S (geometry) | **C** — it serves all domains |
| vastu_engine.py | S (geometry) or C (central layout) | **C** — vastu IS the mandala |
| ui_vastu_engine.py | C (central UI) | **C** — drives shell layout |
| code_engine.py | E (knowledge) or C (self-model) | **C** — system self-awareness |
| system_engine.py | C (system) or independent | **C** — hardware self-model |
| yantra_engine.py | S (geometry) or NE (sacred) | **NE** — sacred geometry |
| yantra_generator.py | S (geometry) or NE (sacred) | **NE** — Sri Yantra is Ishana |

---

## 3. DEPENDENCY ORDER

### Zero External Dependencies (move first)
These import nothing from npu_engine:
1. field_state.py
2. toroidal_field.py
3. datasets.py (imports only stdlib + optional yaml)
4. codex_modes.py
5. _compat.py

### Single Dependency
6. graph_engine.py → datasets
7. coherence_engine_v2.py → graph_engine
8. vector_store.py → nothing from npu_engine (optional transformers)

### Core Pipeline (move together)
9. build_field_state.py → field_state (+ lazy imports of coherence, modulation, vastu, lifecycle, toroidal_field, temple_geometry, graph_engine, vector_store)

### Independent Leaf Engines (move in any order after core)
These read field_state and/or datasets but nothing else in npu_engine:
10. All field/ engines (13 files) — each imports from root level only
11. All engines/ zone engines (11 files) — each imports from root level only
12. renderers/ (2 files) — imports from datasets only
13. game/ implementations (3 files) — imports from root level only

### Sound Subsystem (move as unit)
14. Root-level sound modules (15 files)
15. sound/ directory (17 files including re-exports)
16. mix/ directory (10 files)
17. rhythm/ directory (10 files)
18. sympathetic/ directory (4 files)
19. vocal/ directory (9 files)

### Heavy Hub Modules (move last — most importers)
20. graph_engine.py — imported by 12 kernel routes
21. datasets.py — imported by 7 kernel routes
22. mandala_schema.py — imports from engines/ CENTER + many modules
23. igpu.py — imported by 4 kernel routes

### Safe Move Sequence

```
Session 1: Foundation
  Step 1: field_state.py, codex_modes.py, _compat.py (zero deps)
  Step 2: toroidal_field.py (zero deps)
  Step 3: datasets.py (zero deps)
  Step 4: graph_engine.py (depends on datasets)
  Step 5: vector_store.py (zero npu deps)
  Step 6: coherence_engine_v2.py (depends on graph_engine)
  Step 7: build_field_state.py (depends on field_state)

Session 2: Independent Engines
  Step 8: All field/ engines (13 files, no cross-deps)
  Step 9: All engines/ zone engines (11 files, no cross-deps)
  Step 10: renderers/ (2 files)
  Step 11: game/ implementations (3 files)

Session 3: Sound (move as unit)
  Step 12: Root-level sound modules (15 files)
  Step 13: sound/ + mix/ + rhythm/ + sympathetic/ + vocal/ (50 files)

Session 4: Geometry/Text/Layout
  Step 14: temple_geometry, torus_queries, orientation
  Step 15: vastu_engine, ui_vastu_engine
  Step 16: codex_engine, codex_interaction, passage_resolver, path_engine, etc.
  Step 17: yantra_engine, yantra_generator

Session 5: Hub Modules + Cleanup
  Step 18: mandala_schema.py (depends on engines/)
  Step 19: igpu.py
  Step 20: Update all re-export directories
  Step 21: Remove stale re-export files
  Step 22: Final import audit
```

---

## 4. FRAGILE POINTS

### 4.1 Inline Imports in kernel.py

~120 inline imports inside route functions. This is intentional — it avoids loading all of npu_engine at startup and allows routes to fail independently. **Do not convert to top-level imports.** During restructure, each inline import path must be updated.

Critical inline imports (used most frequently):
```
from npu_engine.graph_engine import GraphEngine           # 12 locations
from npu_engine.datasets import load_entity_metadata      # 7 locations
from npu_engine.field.reading_engine import derive_reading # 5 locations
from npu_engine.field.city_engine import ...               # 5 locations
from npu_engine.igpu import render_field_state             # 4 locations
from npu_engine.field.system_engine import ...             # 4 locations
from npu_engine.sound.sound_engine import ...              # 4 locations
```

### 4.2 Circular Import Risks

Currently none. The architecture is clean. Risks would emerge if:
- Any field/ engine imports from another field/ engine
- mandala_schema imports from engines/ which imports from mandala_schema
- sound_engine imports from field_to_sound which imports from sound_engine

**tanpura_engine.py ↔ om.py** is the one historical circular import, fixed via render_fn injection. This is NOT an npu_engine-internal issue — it's at the om.py boundary.

### 4.3 Hardcoded Paths

**In kernel.py:**
```python
_here = os.path.dirname(os.path.abspath(__file__))       # safe
os.path.join(_here, "static", ...)                         # safe
os.path.join(_here, "apps", ...)                           # safe
os.path.join(_here, "datasets", "plants", "pfaf.sqlite")  # safe
os.path.join(_here, "instance", ...)                       # safe
os.path.join(_here, "wiki", ...)                           # safe
```

**In npu_engine/:**
```python
datasets.py: DATASETS_ROOT = Path(__file__).parent.parent / "datasets"  # safe
code_engine.py: similar relative path                                    # safe
system_engine.py: reads /proc, /sys, runs pw-link                       # system-dependent
```

**Temp files in kernel.py:**
```python
/tmp/om_attend.json
/tmp/atlas_field.json
/tmp/atlas_render.png
/tmp/om_volume.json
/tmp/s5_state.json
/tmp/library_state.json
```
These will not break on restructure but are not configurable.

### 4.4 Package Name

`npu_engine` is hardcoded in:
- Every `from npu_engine.X import Y` in kernel.py (~120 locations)
- Every re-export in 8 subdirectories (~60 files)
- om.py imports
- scripts/ imports
- CLAUDE.md documentation

**The package name MUST NOT change.** All restructuring happens within npu_engine/.

### 4.5 Re-export Chain Complexity

The current re-export architecture has 3 layers:
```
kernel.py → from npu_engine.bija_synth import synthesize_bija
                    ↓ (root-level implementation)
           npu_engine/bija_synth.py

kernel.py → from npu_engine.sound.bija_synth import synthesize_bija
                    ↓ (re-export)
           npu_engine/sound/bija_synth.py
                    ↓ (imports from)
           npu_engine/bija_synth.py (actual implementation)
```

Both paths work today. During restructure, if implementations move, re-exports must update or new re-exports must be added at old locations.

---

## 5. WHAT DOES NOT MOVE

| File | Why |
|------|-----|
| om.py | Audio synthesis entry point, runs independently, circular import boundary |
| drik_panchanga.py | Swiss Ephemeris calculator, standalone |
| kernel.py | Flask spine — import paths updated, file stays |
| start.sh | System boot script |
| scripts/*.py | Utility scripts, independent |
| npu_engine/__init__.py | Package root, always stays |
| npu_engine/field_state.py | Zero deps, imported by everything — safer to leave at root |
| npu_engine/datasets.py | Zero deps, hub module (7 kernel imports) — moving would break 60+ import paths |
| npu_engine/graph_engine.py | Hub module (12 kernel imports) — moving would break most routes |
| npu_engine/build_field_state.py | Orchestrator — tight coupling to root-level modules |
| datasets/ | Data files, not code |
| static/, apps/ | Frontend files |
| instance/ | Personal data |

**Recommendation: Do not move root-level hub modules.** The current root-level + subdirectory re-export architecture already works. Moving hub modules (datasets, graph_engine, build_field_state) would require updating 120+ import paths in kernel.py for marginal organizational benefit.

---

## 6. ESTIMATED SESSION COUNT

### Assessment

The current architecture is **already restructured**. The April 2026 restructure (commits cb8cae7, 125c9a8) created:
- 15 domain subdirectories with implementations
- 8 re-export directories for backward compatibility
- Clean dependency graph with no circular imports

**What remains is not restructuring but cleanup:**

### Recommended Sessions

**Session A: Re-export Audit (1 session, ~2 hours)**
- Verify every re-export file actually re-exports correctly
- Remove _compat.py (it's documentation-only, not functional)
- Ensure every `npu_engine/X/__init__.py` exports what kernel.py expects
- Test: `python3 -c "from npu_engine.sound.bija_synth import synthesize_bija"` for every re-export

**Session B: kernel.py Route Extraction (2-3 sessions)**
- Extract route groups into Flask Blueprints (optional, not required)
- Or: just organize routes with clear section headers and consistent import patterns
- This is the biggest win but also the riskiest — 9,267 lines, 219 routes
- Safest approach: add section comment headers, do NOT split file yet

**Session C: Stale Code Removal (1 session)**
- Identify root-level modules that are ONLY accessed via re-exports (never directly)
- If module X is only imported as `from npu_engine.sound.X`, the root-level X.py can eventually be moved into sound/ and the re-export reversed
- This is optional polish, not structural

**Session D: Test Coverage (1 session)**
- npu_engine/tests/ has only 1 file (test_toroid.py, nearly empty)
- Add import smoke tests for every module
- Add route response tests for critical endpoints

### Total: 4-6 sessions

### What NOT to do:
- Do not split kernel.py into multiple files without extensive testing
- Do not rename npu_engine/
- Do not move datasets.py or graph_engine.py out of root
- Do not remove re-export files until all import paths are verified
- Do not restructure during a session that also builds features

---

## SUMMARY

The Atlas npu_engine is already well-structured after the April 2026 restructure. The main remaining work is:

1. **Cleanup** — verify re-exports, remove dead _compat.py
2. **Documentation** — kernel.py route sections need clear headers
3. **Testing** — import smoke tests and route response tests
4. **Optional** — Flask Blueprints for kernel.py (high risk, moderate reward)

The dependency graph is clean. No circular imports exist. The re-export layer provides backward compatibility. The `derive_*()` pattern is consistent across all field engines. The vastu zone engines follow a uniform base class pattern.

**Recommendation: Do not restructure further. The system works. Build features instead.**
