# Atlas Field Computer — Architecture

Updated: 2026-04-05

---

## What Atlas Is

Atlas is a coherence computer — a system that reads the Vedic cosmological moment (panchanga) and expresses it simultaneously through sound, visual topology, text, and relational graph. It is not a tool you use; it is an environment you inhabit. The cosmos is the operating system. Every nakshatra transit, every tithi change, every graha movement shifts what Atlas shows, plays, and suggests. The system runs continuously on a van-mounted Intel NUC (kanjira), outputting through a MOTU M2 audio interface and serving a web interface over ngrok.

---

## Design Principles

### Everything derives from field state

The central object is `field_state` — a dict containing the current panchanga (tithi, nakshatra, vara, yoga, karana, hora, rahu kala), the current entities scored by coherence, and derived properties (trajectory, sound spec, vastu layout). Every engine reads this dict and returns its domain-specific output. No engine stores state independently.

### The `derive_*()` pattern

Every engine follows the same contract:

```python
def derive_something(field_state: dict, ...) -> dict:
    """
    Single function. Reads field_state + datasets.
    Returns validated dict — all keys guaranteed present.
    Never raises — returns safe defaults on any error.
    """
```

This pattern, established by `ui_vastu_engine.py`, ensures:
- **No exceptions propagate** — every function catches internally
- **All keys present** — callers never need to check for missing data
- **Validation at the boundary** — the `_validate()` helper fills defaults
- **Canonical mappings at top** — configuration is data, not scattered logic
- **Internal helpers are private** — only the public API is called externally

### Attestation hierarchy

Every piece of data carries an attestation marking its epistemic status:

| Level | Weight | Meaning |
|-------|--------|---------|
| `OBSERVED:PRIMARY_TEXT` | 1.0 | Directly from Gita, Bhagavata, Brahma Samhita |
| `OBSERVED:TRADITIONAL` | 0.8 | From living tradition (Narottama padas, jyotish tables) |
| `OBSERVED:PFAF` | 0.7 | From scientific/ethnobotanical databases |
| `SYNTHESIS` | 0.4 | Derived by Atlas from multiple sources |
| `INTERPRETATION` | 0.2 | Inferred, not directly attested |

Atlas never invents doctrine. When connecting two attested passages, the connection itself is marked `SYNTHESIS`. The passages retain their original attestation.

### The four axes

Every entity in Atlas has coordinates on four axes:

| Axis | Range | Meaning |
|------|-------|---------|
| **theta** (θ) | S0→S6 | Level of manifestation (Goloka → Lila) |
| **phi** (φ) | 0→2π | Witness ↔ participant (how you relate to it) |
| **S-layer** | S0-S6 | Which domain ring |
| **path** | 0.0→1.0 | Bheda-abheda (unity ↔ distinction) |

These are not metaphors. They are coordinate values stored per entity and used for spatial projection, coherence scoring, and sound mapping.

---

## The Field State

`field_state` is computed by `kernel.py:field_state()` (line ~2484). It calls:
1. `calc_panchanga(now)` — Swiss Ephemeris via `drik_panchanga.py` → tithi, nakshatra, vara, masa
2. `get_muhurta(now)` — current muhurta window → raga, bpm
3. `compute_yoga()`, `compute_karana()`, `compute_hora()`, `compute_rahu_kala()` — extended panchanga
4. `compute_swara()` — svara nadi from vara rules

The `/spine` endpoint builds a richer version via `build_field_state.py`:
```
panchanga + ToroidalField + GraphEngine + TempleGeometry + VectorStore
  → FieldState(entities, active_relations, formations, lifecycle, psi,
               vastu_grid, arc_phase, modulation, summary)
```

The spine response also includes:
- `sound_spec` from `derive_sound_spec()`
- `trajectory` from `derive_trajectory()`
- `system_audio` from `derive_audio_route()`
- `layers` from `generate_layer_mapping()`

---

## The S-Layer System

Seven concentric layers of manifestation, each driven by dedicated engines:

| Layer | Name | Domain | Key Engine |
|-------|------|--------|-----------|
| S0 | Bindu | Goloka · source · acintya | `goloka_engine.py` |
| S1 | Archetype | 15 Nitya Devis · 9 Grahas | `reading_engine.py` |
| S2 | Sound | Raga · tala · shruti · bija | `sound_engine.py`, `composition_engine.py` |
| S3 | Rhythm | Panchanga · muhurta · dasha | `trajectory_engine.py`, `intention_engine.py` |
| S4 | Geometry | Vastu · yantra · 108 pada | `land_engine.py`, `vastu_engine.py` |
| S5 | Nature | Ayurveda · plant · dosha · herb | `plant_engine.py`, `guild_engine.py` |
| S6 | Lila | Practice · altar · lila maps | `reading_engine.py` bandhu lens |

---

## The Vastu Mandala

The visual shell is organized as a 3x3 vastu mandala:

```
  NW Vayu      N Kubera     NE Ishana
  (Sound)      (Rhythm)     (Archetype)

  W Varuna     C Brahma     E Indra
  (Ecology)    (Cosmos)     (Codex)

  SW Nirriti   S Yama       SE Agni
  (Plants)     (Body)       (Action)
```

Each zone is resolved by `mandala_schema.py:resolve_mandala()`, which:
1. Reads the current field_state
2. Calls each `ZoneEngine.render_zone(field_state)`
3. Returns a dict of 9 zone specs (deity, title, rows, visual, apps)

The shell renders these zone specs. It never computes content — only displays what the engine provides. Three nesting levels: main mandala → sub-mandala (enter S-layer) → sub-zone (enter zone detail).

---

## NPU Engine Map

163 Python files across 15 subdirectories. Re-export layer at root — flat imports work.

Subdirectories: core/, engines/, field/, game/, geometry/, mix/, nature/, renderers/, rhythm/, sound/, sympathetic/, system/, text/, time/, ui/, vocal/, zones/

### Core

**`datasets.py`** — Loads 150+ CSV files from 37 dataset directories into entity/relation/metadata caches. 7208 entities, 8466 relational edges. Hub module with 4 importers.

**`graph_engine.py`** — Canonical relation graph. `GraphEngine.query()` finds entities, `.expand()` traverses edges, `.score()` ranks by coherence. Hub module with 7 importers.

**`build_field_state.py`** — Orchestrates FieldState construction from 10 engine modules: coherence_engine_v2, modulation_engine, vastu_engine, lifecycle_engine, ui_vastu_engine, toroidal_field, temple_geometry, graph_engine, vector_store.

**`field_to_sound.py`** — The descent chain: nakshatra → graha → raga (via graph traversal), element → Sa frequency, tithi → devi → bija.

**`igpu.py`** — iGPU render engine. 4 projections (plane, toroid, hex, 4d), entity rendering, role assignment, formation activation.

**`toroidal_field.py`** — Toroidal coordinate system (OpenVINO NPU). Theta/phi mapping for all entities.

**`mandala_schema.py`** — `resolve_mandala()` → 9 zone specs from field_state. Three nesting levels.

**`vector_store.py`** — Embedding store for passage search. 26k JSONL passage chunks.

**`vastu_engine.py`** — Vastu zone prescriptions and activation.

**`yantra_engine.py`** — Geometric yantra form generation.

**`card_engine.py`** — Card pack architecture for tarot/oracle draws.

**`s5_kernel.py`** — Nature layer kernel. Plant wheel (3 rings, 81 plants).

### Field Engines (`derive_*()` pattern)

**`ui_vastu_engine.py`** — `derive_ui_layout(field_state)` → center focus, layer ring, zone regions, entity nodes, navigation paths. The canonical pattern all other engines follow.

**`trajectory_engine.py`** — `derive_trajectory(field_state, natal)` → lunar arc (coming_from, now, moving_toward), dasha context (Mercury closes Oct 2027), musical implications (tempo_multiplier, tabla_active, phrase_character), session arc.

**`reading_engine.py`** — `derive_reading(lens, field_state, intention)` → 5 lenses (tarot/iching/jyotish/calendar/bandhu), each returning primary entity + passages + interpretation + musical response + Gaudiya pada.

**`composition_engine.py`** — `compose_response(message, field_state)` → classify intention → select pada from Narottama corpus → search passage from 26k JSONL chunks → select chandas metre by rasa → compose response. Optional LLM connector (Qwen3:8b, graceful fallback).

**`goloka_engine.py`** — `derive_goloka_state(field_state)` → maps current time to eternal ashtakala period (sakhi, raga, forest, seva, lila). Bridge_to_material coherence score.

**`intention_engine.py`** — `derive_windows(intention_id, field_state, days)` → scores muhurta windows by vara/nakshatra/tithi/hora match for 24 jyotish-sourced intentions.

**`land_engine.py`** — `derive_land_layout(field_state, plot)` → 9 vastu zone prescriptions with plants, structures, coherence scores. GeoJSON projection via `/land/layout`.

**`system_engine.py`** — `derive_system_state()` → hardware self-model, audio route derivation, connection checking.

**`helix_engine.py`** — `derive_helix_field()` → dual helix toroid, JDN ephemeris, 90-day projection, favorability scoring. 338 lines.

**`ring_engine.py`** — 10 ring types (muhurta/nakshatra/devi/graha/tala/herb_dosha/agricultural/zodiac/raga_time/ashtakala), data-driven.

**`city_engine.py`** — Hex city generation for Lila game.

**`symbol_engine.py`** — Emoji relational symbol system.

**`code_engine.py`** — Codebase dependency graph analysis (105 files).

### Renderers

**`figure_renderer.py`** — The Bandhu body rendering stack. 6 compositable layers:

| Layer | Function | Content |
|-------|----------|---------|
| skeleton | `render_skeleton_layer()` | 26 bones: skull dome, 24 vertebrae, 12 rib pairs (ida silver / pingala gold), clavicles, scapulae, pelvis with sacrum triangle, humeri, radii/ulnae, femurs, tibiae/fibulae, hands, feet |
| fluid | `render_fluid_layer()` | Rasa/D001: plasma field, CSF, lymph channels, axillary/inguinal pools, venous return (upward blue), arterial flow (downward warm), 8 synovial joints, CSS pulse animations |
| dhatu | `render_dhatu_layer()` | 7 dhatu geometric archetypes: radial, sinusoidal, branching, tensegrity, spiral, parabolic, vesica, concentric, tidal |
| signature | `render_signature_layer()` | 44 doctrine of signatures: plant-form glyphs at body regions (fig dome on skull, bamboo nodes on spine, lotus pod on heart). Zoom-gated: 1.0→structural, 2.0→morphological, 4.0→cellular |
| skin | `render_bandhu_svg()` | Volumetric SVG figure from Shilpa Shastra Uttama Dasatala measurements. Exact coordinates: head cy=-155, feet cy=+130. Sushumna axis, 7 chakra stations, toroidal breath animation (CSS @keyframes, 4s cycle, 3 torus phases at 120° offset) |

`render_bandhu_full()` composites layers: skeleton(0.18) + fluid(0.15) + dhatu(0.18) + signature(0.10) + skin(0.55). `dhatu=D005` highlights bone at 0.65. `dhatu=D001` highlights plasma at 0.40.

### Zone Engines (`ZoneEngine` pattern)

Each zone engine inherits from `base_engine.py:ZoneEngine` and provides:
- `get_entity(field_state)` — primary entity_id for this zone
- `render_icon(field_state)` — small contribution to center field
- `render_zone(field_state)` — full zone content (rows, visual, apps)

Nine engines: SoundEngine (NW), RhythmEngine (N), ArchetypeEngine (NE), EcologyEngine (W), CenterEngine (C), CodexEngine (E), PlantEngine (SW), BodyEngine (S), ActionEngine (SE).

**`plant_engine.py`** — 4D coherence scoring: nakshatra (0.35) + element (0.25) + dosha (0.20) + vara (0.10) + tithi (0.10). Returns top 5 plants.

**`guild_engine.py`** — 216 guild relations across 27 nakshatra plants. Moon phase → activity (observe/plant/harvest/prune/compost).

### Rendering

**`igpu.py`** — The iGPU render engine. Converts field_state into `RenderState`:
- 4 projections: `project_plane`, `project_toroid`, `project_hex`, `project_4d`
- `layout_nodes()` → position from theta/phi coordinates
- `assign_roles()` → center/orbit/bridge/free + motion (stable/orbit/oscillate/static)
- `activate_formations()` → pull members into spatial clusters
- `build_flow_vectors()` → 2-step relational chains via path_engine
- Routes: `GET /render?projection=toroid`, `GET /render/eternal`

### Sound Subsystems (threaded kernels in om.py)

| Kernel | Purpose |
|--------|---------|
| TanpuraEngine | 4 strings, additive synthesis, per-graha jivari |
| SarangiVoice | Bowed gut string at Sa, cached render_looped |
| bija_synth | Formant drone per devi bija |
| tabla_sampler | 7 percussion samples, tala-driven |
| MixKernel | 11-layer relational mix → OSC 57121 |
| RhythmKernel | Tala/theka/tihai/layakari → OSC |
| SympatheticKernel | 13 taraf strings → OSC |
| VocalKernel | 49 phonemes, 12 gamakas → OSC |

### The Goloka Layer (S0)

In Gaudiya Vaishnava cosmology, Goloka is the eternal realm where all activities occur simultaneously. The ashtakala divides these into 8 observable periods that correspond to times of day. `goloka_engine.py` maps material time to eternal lila: which forest is active (12 Vraja forests from `vraja_forests.csv`), which sakhi presides, which raga sounds, which seva is appropriate.

The two-sphere concept in `shell-cosmos.html` makes this visible: the live field sphere shows the current material state; the eternal sphere shows the corresponding Goloka state. Both rotate. Clicking swaps dominance.

---

## Audio Architecture

```
  TanpuraEngine (4 strings) ──┐
  SarangiVoice (bowed Sa)   ──┤
  bija_synth (formant drone) ──┼──→ fill_buffer() → pw-cat → PipeWire → MOTU M2
  tabla_sampler (7 samples)  ──┘
         ↑ _mix_amps[0..10]
         │
  MixKernel ──→ OSC 57121 ──→ sclang (atlas_mix.scd)
                                 ──→ OSC 57122 ──→ om.py _mix_amps
```

`fill_buffer()` multiplies each layer by its mix amp:
- `tanpura * mx[0]`, `bija * 0.06 * mx[10]`, `sarangi * 0.15 * mx[6]`, `tabla * 0.35 * mx[3]`

SC: scsynth running, JACK ports registered, but PipeWire 1.2.6 JACK shim doesn't bridge audio samples. Kept for future Talachakra work.

---

## The Composition Engine

When a user asks Bandhu a question, the field answers:

1. **Classify** — 50+ keywords map to 7 intentions (viraha/srishti/abhyasa/madhurya/dasya/jyotish/archetype)
2. **Select pada** — scores Narottama corpus by rasa match (0.3), time-of-day (0.25), composer preference (0.15), intention keywords (0.15)
3. **Search passage** — tries `vector_store.search()` over 26k JSONL chunks. Falls back to keyword search.
4. **Select metre** — maps rasa to chandas: shringara→Mandakranta, karuna→Anustubh, vira→Sardulvikridita
5. **Compose** — pada opening line + passage text + field moment + attribution

No LLM is required. Qwen3:8b is wired as an optional connector but currently too slow on CPU.

---

## The Shell

**`shell.html`** (`/shell`) — 3x3 vastu mandala grid. 9 zones as 80px border strips, center cosmos with iGPU-rendered toroid. Zone collapse (32px), zone-open (right-side drawer), observe panel (fullscreen overlay), entity wheel (radial selector), command line.

**`shell-cosmos.html`** (`/cosmos`) — Full-screen two-sphere instrument. Live field sphere (55vh) + eternal cosmology sphere (22vh). Click to swap. 8 floating vastu zone widgets. Glass-morphism aesthetic.

---

## Data Flow — Complete Example

What happens when you load `/shell`:

```
1. Browser fetches /shell/state
2. kernel.py calls field_state()
     → calc_panchanga(now) via Swiss Ephemeris
     → tithi=17 (Krishna Tritiya), nakshatra=Svati, element=air
3. mandala_schema.py resolves 9 zones
     → PlantEngine: Arjuna (Svati plant, air, score 0.50)
     → GuildEngine: Arjuna anchor + 4 companions
4. Response → shell.html applyState()
     → zone-nw: Vayu · Sound · current raga
     → zone-c: Svati (48px gold italic) + cosmos SVG
     → zone-sw: Nirriti · Arjuna (guild)
5. Browser fetches /render?projection=toroid
6. igpu.py render_field_state()
     → 64 entities projected via project_toroid(theta, phi)
     → assign_roles() + activate_formations()
7. Response → shell.html renderCosmos()
     → SVG circles, edges, flows, bindu
8. Repeats every 30 seconds
```

---

## Hardware — kanjira

| Component | Role | Status |
|-----------|------|--------|
| Intel Core Ultra (x86) | Python, Flask, panchanga, graph | active |
| Intel NPU (Meteor Lake) | OpenVINO coherence scoring | available — verified active for toroidal scoring |
| Intel Iris Xe iGPU | WebGL, yantra, toroid | active |
| 16GB DDR5 | RAM constraint | active |
| MOTU M2 USB | Analog stereo FL/FR | active |
| PipeWire 1.2.6 | pw-cat works, pw-jack broken for SC | active |

---

## What's Built (cumulative as of 2026-04-05)

- **27 engines** — all verified import OK, zero failures
- **163 Python files** in npu_engine/ across 15 subdirectories with re-export layer
- **Bandhu figure** — 6 rendering layers (skeleton→fluid→dhatu→signature→skin), toroidal breath
- **Ring engine** — 10 ring types, data-driven
- **Sacred geography** — 63 Shakti Pithas + 34 global sacred sites + 45 body relations
- **LeelaMaps** — 658 lines, 8 toggleable layers
- **Lila Streams** — land design tool, 28 mounds + 30 regional plants + vastu + permaculture
- **Live toroid** — Three.js dual helix, 4 view presets, entity nodes from /render
- **Helix engine** — 338 lines, JDN ephemeris, 90-day projection, favorability scoring
- **Domain reorganization** — 6 domains (kala/devi/deha/bhumi/vidya/lila), flat routes
- **Home page** — field-aware landing with app cards by domain
- **Dashboard** — static/index.html at /, live status per route
- **Hex game level 1** — Vayu↔Agni portal pair, Wesnoth terrain tiles
- **Journal routes** — GET/POST /journal (JSON storage in instance/journal/)
- **Kala app** — index + wheel.html, calendar + day routes working
- **Devi apps** — archana, tarot, mala, yantra (all 200)
- **Bhumi apps** — agriculture, ecology, guild, vastu, streams (all 200)
- **Vidya** — wiki browser at /vidya/wiki
- **219 wiki pages** — 3 empty stubs remaining
- **Research infrastructure** — anomalies, briefs, artifacts, queue
- **Wesnoth assets** — full game data for hex terrain tiles

## What's Not Built Yet

- **Vocal SynthDef** — 1154 lines waiting, no SC audio output path
- **SC→MOTU audio** — blocked on PipeWire 1.2.6 JACK shim
- **4D projection** — `project_4d()` exists in igpu.py, not exposed in any shell
- **Talachakra** — Pd visual tala, needs freeverb~ compilation
- **GIS land mapping** — Vishvakarma app exists but has no kernel route
- **Population layer** — multi-user natal charts
- **Systemd services** — scripts ready, not installed
- **Seeds pipeline** — 4 briefs exist in research/briefs/, not feeding into seeds yet
- **Wiki stubs** — 3 remaining: Today.md, index_tithi.md, index_ritual.md
- **Deha app** — body layer beyond Bandhu placeholder (marma, chakra, dinacharya)
- **Editor (Quill)** — journal/wiki editor, specced not built
- **Journal UI** — backend routes exist, no standalone app HTML

---

## App Domain Map

Six domains, flat routes. Each domain groups related apps under a single URL prefix.

| Domain | S-Layer | Route | Apps |
|--------|---------|-------|------|
| Kala | S3 | `/kala` | Time oracle, wheel, calendar, day |
| Devi | S1 | `/devi` | Archana, tarot, mala, yantra |
| Deha | S6 | `/deha` | Body, marma, chakra (Bandhu for now) |
| Bhumi | S5 | `/bhumi` | Agriculture, guild, ecology, vastu, streams |
| Vidya | S2 | `/vidya` | Library, wiki, journal, editor |
| Lila | S6 | `/lila` | Coherence game, hexed city |

Bandhu (`/bandhu`) is ambient S6 presence across all domains.
The shell mandala (`/shell`) maps zones to these six domains.

### Shell Zone → Domain Wiring

```
  NW Vayu (Sound)     → /kala
  N  Kubera (Rhythm)  → /vidya
  NE Ishana (Archetype)→ /devi
  W  Varuna (Ecology) → /bhumi
  C  Brahma (Cosmos)  → /live
  E  Indra (Codex)    → /lila
  SW Nirriti (Plants) → /bhumi/ecology
  S  Yama (Body)      → /deha
  SE Agni (Action)    → /lila/hexed
```

---

## Route Map (as of 2026-04-05)

217 route definitions in kernel.py. 46 routes verified 200 as of 2026-04-05. Zero 404s.

### Shells
| Route | File |
|-------|------|
| `GET /` | `static/home.html` |
| `GET /live` | `static/live.html` (toroid) |
| `GET /shell` | `static/shell.html` |
| `GET /cosmos` | `static/shell-cosmos.html` |
| `GET /atlas` | `static/atlas.html` |

### App Domains
| Route | File |
|-------|------|
| `GET /kala` | `apps/kala/index.html` |
| `GET /devi` | `apps/devi/archana/index.html` |
| `GET /devi/{archana,tarot,mala,yantra}` | `apps/devi/*/index.html` |
| `GET /deha` | `apps/bandhu/index.html` |
| `GET /bandhu` | `apps/bandhu/index.html` |
| `GET /bhumi` | `apps/bhumi/agriculture/index.html` |
| `GET /bhumi/{agriculture,guild,ecology,vastu,streams}` | `apps/bhumi/*/index.html` |
| `GET /vidya` | `apps/vidya/wiki/index.html` |
| `GET /lila` | `apps/lila/lila/index.html` |
| `GET /lila/hexed` | `apps/lila/hexed/city/index.html` |
| `GET /maps` | `apps/leela-maps/main.html` |

### Field Engines (JSON data)
| Route | Engine |
|-------|--------|
| `GET /spine` | `build_field_state.py` full FieldState |
| `GET /field` | `kernel.field_state()` panchanga only |
| `GET /helix` | `helix_engine.derive_helix_field()` |
| `GET /goloka` | `goloka_engine.derive_goloka_state()` |
| `GET /trajectory` | `trajectory_engine.derive_trajectory()` |
| `GET /guild/state` | `guild_engine.derive_guild()` |
| `GET /land` | `land_engine.derive_land_layout()` |
| `GET /land/layout` | GeoJSON vastu zones at lat/lon |
| `GET /render` | `igpu.py` projections |
| `GET /render/eternal` | `igpu.py` Goloka layer |
| `POST /observe` | entity deep dive |
| `POST /bandhu/chat` | `composition_engine.compose_response()` |
| `POST /reading` | `reading_engine.derive_reading()` |
| `GET /intention/classify` | intention classification |
| `GET /system/state` | hardware + audio snapshot |
| `GET /calendar/day` | muhurta breakdown |

---

## Datasets

37 directories: astro, astrobotany, ayurveda, canonical, carnatic, chandas, compositions, cosmology, entities, game, gandharva, geography, iching, jyotish, mappings, marma, morphogenesis, ontology, overlays, plants, ratna, relations, ritual, schema, semantics, silpa, sound, sources, species, svarodaya, symbols, system, tantra, tarot, vastu, views, yoga

## Wiki

219 total pages, 3 empty stubs (Today.md, index_tithi.md, index_ritual.md). Content pages are primarily deity entries. Subdirectory: wiki/cosmos/ (3 cosmological articles).

## Research

```
research/
  anomalies/  — system anomaly logs (1 file)
  briefs/     — 4 research briefs (aboriginal overlay, doctrine of signatures,
                shakti pitha, yoga instructions)
  artifacts/  — 1 HTML artifact (foot cosmology)
  offerings/  — empty, pipeline not active
  seeds/      — empty, pipeline not active
  queue.json  — research queue
```

---

## Geographic / GIS Applications

Three map-based apps, each a single HTML file with embedded data + Leaflet.js:

**LeelaMaps** (`apps/leela-maps/main.html`, route `/maps`) — Sacred geography browser. 8 toggle layers: Shakti Pithas (62 gold dots), world sacred sites (34 graha-colored), influence zones, great circle grid + phi spiral, ley lines, world body overlay, natal astrocartography, field checkin log. All data embedded — works offline.

**Land Design** (`apps/bhumi/streams/index.html`, route `/bhumi/streams`) — Interactive land design tool. 5 toggle layers: vastu overlay (9 GeoJSON zones from /land/layout), permaculture mandala (8 zone elements with Mollison principles), plant palette (30 regional plants + /guild/state), sacred sites & mounds (28 NA earthwork + sacred water sites), field state HUD. Offline fallback with client-side vastu computation.

**Vishvakarma** (`apps/vishvakarma/index.html`) — GIS vastu land design on satellite imagery. 9 pie-slice zones, natal plant placement, radius slider 5m→500m.

## Key File Reference

| Want to... | Look at |
|------------|---------|
| Add a field engine | Copy `ui_vastu_engine.py` pattern |
| Add a zone engine | Copy `plant_engine.py` (`ZoneEngine` subclass) |
| Add a kernel route | `kernel.py` — check for duplicate function names |
| Add a dataset | Engine-specific CSV loader (not centralized) |
| Change sound | `om.py` `fill_buffer()` |
| Change the grid shell | `static/shell.html` |
| Change the cosmos shell | `static/shell-cosmos.html` |
| Add an app | `apps/<domain>/<name>/index.html` + flat route in `kernel.py` |
| Add a body render layer | `figure_renderer.py` — add function + wire in `render_bandhu_full()` |
| Add a map layer | `apps/leela-maps/main.html` — add to loaders dict + toggle button |
| Add sacred geography | `datasets/geography/` — CSV with lat/lon + embed in JS |
| Check code topology | `datasets/system/code_topology.csv` |
| Check system state | `python3 -c "from npu_engine.field.system_engine import derive_system_state; ..."` |
