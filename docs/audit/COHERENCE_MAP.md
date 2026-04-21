# Atlas Coherence Map — April 21, 2026

## Coherent Subsystems

These are vertical slices where dataset → engine → route → UI all align.

### 1. Panchanga → Sound (FULLY COHERENT)
```
calc_panchanga() → field_state → derive_sound_spec → OSC → SuperCollider
    ↓ datasets: astro/*.csv, cosmology/*.csv
    ↓ engines: sound_engine, field_to_sound, tanpura, bija, tabla
    ↓ routes: /field, /spine, sound_bp (26 routes)
    ↓ output: MOTU M2 analog audio
```
Live, running, producing sound 24/7. The most complete subsystem.

### 2. Jyotisha Chart Engine (FULLY COHERENT)
```
Swiss Ephemeris → compute_chart → jyotish_bp → jyotish_chart.html
    ↓ datasets: jyotish/*.csv (5 reference CSVs)
    ↓ engines: jyotisha_engine, jyotish_utils
    ↓ routes: /jyotish/* (10 routes)
    ↓ UI: nakshatra mandala, wave field overlay
```
Built April 16-18. Complete from ephemeris to visualization.

### 3. Graph + Observe (MOSTLY COHERENT)
```
datasets.py → graph_engine → /observe → observe panel (in oracle.html)
    ↓ datasets: relations/ (27 CSVs), entities/ (8 CSVs + reference JSONs)
    ↓ engines: graph_engine, codex_engine, vector_store
    ↓ routes: /observe, /entity, /codex, /graph
```
Works but the UI surface is scattered — observe panel exists in oracle.html
and shell.html but there's no dedicated observation UI.

### 4. S-Layer Pages (COHERENT, RECENT)
```
layer_composer → LAYER_DATASETS → /layers/<N> → s0-s6.html
    ↓ datasets: pulls from ALL 42 domains via manifest
    ↓ engine: layer_composer._assemble_s0 through _assemble_s6
    ↓ routes: /layers, /layers/<layer>, /layer-data
    ↓ UI: 7 HTML pages (s0.html through s6.html)
```
Built April 10-11. Self-assembling pages from dataset manifests.

### 5. Corpus Search (COHERENT)
```
80+ texts → JSONL chunks → vector_store → /corpus/search
    ↓ datasets: sources/ (14 text traditions, 26k chunks)
    ↓ engines: vector_store, passage_resolver
    ↓ routes: corpus_bp (8 routes)
```

### 6. Oracle (COHERENT)
```
iching_augury_engine + pasaka_engine → /lila/augury/* → oracle.html
    ↓ datasets: iching/*.csv (9 CSVs), pasaka.csv
    ↓ engines: iching_augury_engine, pasaka_engine
    ↓ routes: 6 augury routes + pasaka
    ↓ UI: oracle.html (two-panel with hexagram + pasaka)
```

### 7. Plant/Guild/Agriculture (COHERENT)
```
plant_engine + guild_engine → plants_bp → bhumi apps (atlas_330)
    ↓ datasets: plants/ (12 files), astrobotany/ (4)
    ↓ engines: plant_engine, guild_engine, s5_kernel, land_engine
    ↓ routes: plants_bp (17), /guild/*, /agriculture/*
    ↓ UI: in atlas_330/apps/bhumi/
```

## Orphaned Components

### Datasets Without Active Engines
- `datasets/karma/` (1 csv) — no karma engine exists
- `datasets/permaculture/` (1 csv) — no dedicated engine (land_engine is closest)
- `datasets/temples/` (2 csv) — temple_geometry reads different data
- `datasets/sanskrit/` (1 csv) — no engine
- `datasets/silpa/` (1 csv) — no shilpa shastra engine
- `datasets/semantics/` (1 csv) — semantic_engine may use it, unclear

### Engines Without Routes
- `npu_engine/vocal/` (11 files) — vocal synthesis built but no route
  exposes it. Waiting for SC vocal SynthDef (noted in ARCHITECTURE as "not built").
- `npu_engine/rhythm/` (13 files) — rhythm kernel exists but only the
  rhythm_engine zone engine is routed. The full layakari/tihai/cross-rhythm
  pipeline is unrouted.
- `npu_engine/sympathetic/` (4 files) — sympathetic string model, no route.
- `npu_engine/game/` (6 files) — character, lineage, orientation engines.
  /character route exists but the full game pipeline is partial.
- `npu_engine/text/` (11 files) — many are re-exports or duplicates of
  files that also exist at the top level.

### HTML Without Working Backend
- `static/s4-bloom.html` — variant S4 page, unclear if live
- `static/hexd-portal.html` — hexfield game portal, partially wired

### Research Not Consolidated
- 8 deep-research-report files (Mar 27) — bulk research downloads, not
  integrated into papers or datasets
- 4 .docx research files — not in markdown, not in the analysis pipeline
- `research/queue.json` — research queue, may be stale

## Redundancy

### Duplicate Engine Locations
Many engines exist in BOTH a subdirectory AND the top level of npu_engine/:
- `npu_engine/codex_engine.py` AND `npu_engine/text/codex_engine.py`
- `npu_engine/field_to_sound.py` AND `npu_engine/sound/field_to_sound.py`
- `npu_engine/s5_kernel.py` AND `npu_engine/nature/s5_kernel.py`
- `npu_engine/vastu_engine.py` AND `npu_engine/geometry/vastu_engine.py`
- `npu_engine/yantra_engine.py` AND `npu_engine/geometry/yantra_engine.py`

The subdirectory versions appear to be re-imports (`from ..yantra_engine import *`)
not independent copies. But this creates confusion about which is canonical.

### pasaka_engine.py × 2
- `npu_engine/pasaka_engine.py` — simple cast() + get() (the one kernel uses)
- `npu_engine/field/pasaka_engine.py` — full field-derived cast with Lo Shu,
  score_cast, derive_field_cast (the one with wave field integration)
Both exist, kernel imports from the root one.

### Multiple Orientation Documents
- `CLAUDE.md` — primary orientation (checked in, maintained)
- `SYSTEM_MAP.md` — engine/route map (dated April 8)
- `CORE_SCOPE.md` — boundary definition
- `docs/ARCHITECTURE.md` — detailed architecture (dated April 5)
- `docs/ATLAS_STATE_OF_THE_UNION.md` — state document (undated)
- `docs/SESSION_HANDOFF.md` — session handoff notes
- Multiple skill files in docs/ — competing versions

## Gaps

### Domains with Data but No Computation
- **Tantra**: 2 CSVs (chakra_cross_domain, another), no tantra engine
- **Marma**: 4 CSVs (marma_points, etc.), no marma engine (figure_renderer
  knows body coords but doesn't compute marma)
- **Ratna**: 1 CSV (gems), no gemology engine
- **Morphogenesis**: 3 CSVs (body archetypes, signatures), used by
  figure_renderer but no standalone engine

### UI Surfaces Missing
- No dedicated jyotish chart page in atlas_330 apps (only in atlas_core static)
- No dedicated wave field visualization beyond the mandala
- No Devi-cycle visualization (the S1 page shows current Devi but doesn't
  show the cycle or allow navigation)
- No journal UI (backend routes exist, no frontend)
- No editor (Quill specced but not built)

### atlas_330 ↔ atlas_core Gap
- atlas_330 has 27 HTML apps that call atlas_core JSON routes
- atlas_core has static HTML pages that duplicate some atlas_330 functionality
- The boundary is blurred — CORE_SCOPE says "no HTML in core" but core has 17 HTML files
- The kala app in atlas_330 was updated (April 16) to call /jyotish/calendar
  — this cross-repo dependency works but isn't documented
