---
name: atlas-state
description: >
  Instant orientation skill for the Atlas 330 / atlas_core project. Use this skill at
  the start of ANY session involving Atlas development, research, scripting, graph work,
  dataset work, visualization, or philosophical/doctrinal writing. Also trigger when the
  user mentions: kernel.py, npu_engine, field_state, nakshatra, tithi, graha, devi,
  raga, corpus, relations, datasets, routes, S-layers, hexfield, toroidal field,
  Bandhu, sound, or any Atlas engine by name. Read before touching anything.
---

# Atlas State Skill

## What Atlas Is

**Atlas 330** is a Vedic cosmological field computer running as a Flask kernel (`kernel.py`)
on a van-mounted Intel NUC called `kanjira` at `~/atlas_core/`. It integrates jyotish,
biodynamic agriculture, sacred geometry, Ayurveda, Gaudiya Vaishnava knowledge systems,
and NPU-powered relational graph computation into a unified living platform.

The guiding principle: **everything is a projection of the cosmological field state.**
Every API endpoint, every display, every sound event derives from `kernel.field_state()`.
Nothing cosmological is hardcoded.

---

## Repository Structure (as of April 2026 audit)

```
atlas_core/
  kernel.py               Flask entry point — 203 routes, ~9,800 lines
  npu_engine/             204 Python engine files across 15 subdirectories
    datasets.py           1,365 lines — shared CSV/JSON loader, all data access
    build_field_state.py  field state construction pipeline
    graph_engine.py       GraphEngine — loads and traverses the relation graph
    toroidal_field.py     ToroidalField — θ/φ coordinate system
    field/                Core live engines (goloka, helix, intention, trajectory, etc.)
    engines/              Zone engines (guild, plant, body, sound, etc.)
    renderers/            figure_renderer, species_renderer
    sound/                OSC bridge + sound engine (most other files are 1-line stubs)
    rhythm/               Carnatic rhythm engines (cross_rhythm, tala_graph, etc.)
    vocal/                Vocal synthesis engines
    sympathetic/          Sympathetic string model
    mix/                  Mix kernel, authority/guna/nakshatra bias
    game/                 character, lineage, orientation engines
    geometry/             STUB directory (planned refactor)
    core/                 STUB directory (planned refactor)
    zones/                STUB directory (planned refactor)
    time/                 STUB directory (planned refactor)
    text/                 STUB directory (planned refactor)
    system/               STUB directory (planned refactor)
  datasets/               ~1,043 files — 188 CSV, 677 JSON, 82 JSONL
    astro/                nakshatra, tithi, graha, rashi
    ayurveda/             herbs, dosha, dhatu, rasa
    carnatic/             raga, tala, kriti
    cosmology/            devi, deity, goloka, ashtakala
    gandharva/            therapeutic raga, bija, instruments
    geography/            sacred sites, ecoregions
    marma/                body-region-marma
    plants/               nakshatra plants, guild, ethnobotany, pfaf
    ratna/                gems, metals
    relations/            26 CSV files — 5,547 canonical graph edges
    sources/              82 JSONL files — 139,071 corpus chunks
    symbols/              glyphs, emoji vedic map
    vastu/                pada grid, deities
    iching/               hexagrams, trigrams, resonance tables
    species/              animal yoni, vahana
    svarodaya/            nadi, element, tithi rules
    game/                 lineages, sura_asura_map
    system/               topology, capability_map
  static/                 20 HTML files — the frontend
    home.html             root dashboard (S0–S6 domain entry)
    live.html             Three.js r128 dual-helix toroid (kala view)
    hexd.html             HEXD research workspace/IDE (5 modes)
    portal.html           404 portal
    s0.html–s6.html       S-layer domain pages
    widgets/              coherence, dasha, field, goloka, guild, natal, sound, system, transits
  sc/                     atlas_mix.scd, atlas_synth.scd — SuperCollider SynthDefs
  docs/audit/             Full system audit outputs (April 2026)
```

---

## Known State as of April 10, 2026

**Source**: `docs/audit/AUDIT_SUMMARY.md` and full audit documents.

### Scale
- 203 routes in kernel.py
- 204 engine files in npu_engine/
- 55 routes FULL (engine wired), 148 PARTIAL (inline code or missing engine import)
- 188 CSV datasets, 82 JSONL files, 139,071 corpus chunks
- 5,547 relation rows across 26 CSV files
- ~7,200+ graph entities, ~8,500+ edges

### System Health
| Domain | Score | Key issue |
|--------|-------|-----------|
| Datasets | 80% | 6 missing files; 924 orphaned files not yet wired |
| Relations | 75% | Entity ID format inconsistent; 1,682 of 1,687 subjects unresolved |
| Engines | 90% | 204 files; S0–S5 all covered; S6 gap |
| Routes | 85% | 55 FULL; corpus/research group 0/8 FULL |
| Corpus | 85% | 139k chunks; bg_chunks.jsonl = 0; tradition metadata blank |
| Frontend | 90% | 20 pages; API routes generally exist |
| Sound | 70% | Engines written; SC present; no PipeWire/JACK/MOTU playback |
| Environment | 75% | NPU not detected; requirements.txt has only 4 entries |

### 6 Missing Dataset Files (blockers)
These are referenced in code but don't exist — likely causing 500 errors:
- `datasets/layer_mapping.csv` — used by `layer_engine.py` → /layers routes
- `datasets/marma/marma_coordinates.csv`
- `datasets/sanskrit/matrika_50.csv`
- `datasets/geography/sacred_sites_india.csv`
- `datasets/geography/vraja_parikrama.csv`
- `datasets/karma/dasha_meanings.csv`

### Corpus State
- Strong Gaudiya coverage: Bhagavatam 15k, BRS 2k, HBV 2.6k, BBM 3.1k, Vedanta Sutra 3.7k
- `gaudiya/bg_chunks.jsonl` = 0 chunks (BG corpus missing — only index file present)
- Tradition/language fields blank in corpus registry — /corpus/search can't filter by tradition
- 1 registered-but-missing JSONL; 2 present-but-unregistered

### Entity ID Problem
The `entities/` directory (57 rows total) is a stub, not the live entity source. Live entities
are loaded from domain CSVs via `npu_engine/datasets.py`. Relation subjects use mixed formats:
`nakshatra:rohini`, `nakshatra:1`, and `nakshatra_rohini` coexist. No canonical ID registry exists.
This is the most impactful data integrity issue.

### Sound Architecture
Fully designed, not outputting:
- `tanpura_engine.py` (558 lines), `field_to_sound.py` (428 lines), `sound_engine.py` (373 lines)
- `phrase_engine.py` (392 lines), `osc_bridge.py` (57 lines, WORKING)
- `sc/atlas_synth.scd` + `sc/atlas_mix.scd` present
- Blocker: PipeWire JACK shim to MOTU M2 not configured
- Most `npu_engine/sound/` files are 1-line stubs pointing to top-level implementations

### S-Layer Engine Coverage
- S0: goloka_engine ✓
- S1: build_field_state, field_state, toroidal_field, field_layers ✓
- S2: sound_engine, field_to_sound ✓
- S3: rhythm_engine, trajectory_engine, cross_rhythm_engine ✓
- S4: yantra_engine, yantra_generator ✓
- S5: s5_kernel, plant_engine ✓
- **S6: 0 engines — gap**

### Stub Directories (not broken, planned refactors)
`npu_engine/core/`, `/geometry/`, `/zones/`, `/time/`, `/text/`, `/system/` —
all contain 1-line stub files. The working implementations live at npu_engine/ top level
and in `npu_engine/field/`. Do not count these as failures.

---

## Three System Axes (always independent)

1. **Stability**: `stable` / `working` / `experimental`
2. **Authority**: `shastra` (textual) | `sadhu` (practitioner) | `guru` (synthesis/AI)
3. **Visualization**: `relation` / `analytic` / `symbolic` / `canonical`

AI-generated content always starts at `experimental / guru`. Never override canonical data.

---

## Key APIs

```
GET  /field              → current field state (tithi, nakshatra, devi, raga, muhurta, etc.)
GET  /spine              → full panchanga spine
GET  /trajectory         → nakshatra/tithi arc projection
GET  /goloka             → ashtakala + Vraja forest + Nitya Devi
GET  /helix              → dual-helix toroidal field state
GET  /intention/now      → current muhurta intention
GET  /sound/spec         → live sound specification for SuperCollider
GET  /yantra             → yantra SVG + parameters
GET  /rings              → ring engine output
GET  /corpus/search      → JSONL passage search
GET  /layers             → S-layer summary (requires layer_mapping.csv — currently missing)
GET  /guild/state        → nakshatra plant guild state
GET  /land               → land/site design engine
```

---

## Session Startup Protocol

1. **Identify session type**: engine work / dataset / route / frontend / corpus / sound / relations
2. **Check audit state**: what's the current status of the domain being touched?
3. **Check for missing files**: if touching layers, marma, geography, karma, or sanskrit domains — those files are missing
4. **Confirm entity ID format**: before writing relations, check which format the target domain uses
5. **Sound sessions**: assume no audio output until PipeWire/JACK/MOTU is confirmed working
6. **NPU sessions**: `lspci` shows NPU undetected — all compute is CPU until resolved

## What Claude Should Never Do

- Assume any PARTIAL route is broken — most are working with inline code, not a named engine import
- Count stub directories (core/, geometry/, zones/, etc.) as missing engines
- Hardcode cosmological values — always derive from /field
- Add relation rows without checking entity ID format consistency
- Assume npu_engine/sound/ stubs are the implementations — real code is at npu_engine/ top level
- Modify canonical relation CSVs (relations_resolved_canon.csv) without explicit confirmation
- Assume the BG corpus exists — bg_chunks.jsonl is currently empty
