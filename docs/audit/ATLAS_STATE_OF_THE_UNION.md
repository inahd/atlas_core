# Atlas 330 — State of the Union

**Date**: April 10, 2026  
**Source**: Full 14-section system audit  
**Repository**: `~/atlas_core/` on `kanjira` (Intel NUC, Meteor Lake, van-mounted)  
**Kernel**: `python kernel.py` → `localhost:5000`

---

## Purpose of This Document

This is the living reference for the current state of Atlas 330 — what exists, what works,
what is broken, what is dark, and what the pathway forward looks like. It is written for
both human collaborators and AI assistants (Claude, Ollama) working on this system.

**How to use it:**
- Read the System Health section before starting any session
- Read the relevant domain section before touching any engine, dataset, or route
- Append to the Task Queue sections as work completes or new needs are discovered
- Do not replace completed tasks — strike them through and date them
- Update the health scores when significant work lands

**How AI should use it:**
- Read this document at the start of any Atlas session in place of re-running an audit
- Do not invent system state — if something is not described here, ask or check the file
- When generating new code or data, check the relevant task queue for existing plans
- When completing a task, note it here with a date and one-line summary

---

## System Philosophy Reminder

Everything in Atlas is relational. `kernel.field_state()` is the spine — every display,
sound event, and agent action derives from it. The corpus provides textual grounding.
The relation graph provides semantic structure. The engines compute projections.
The frontend renders them.

The authority hierarchy is always: Shastra → Sadhu → Guru. AI-generated content
always starts at `experimental / guru`. Canon is never silently overridden.

**The three axes are always independent:**
- Stability: `stable` / `working` / `experimental`
- Authority: `shastra` / `sadhu` / `guru`
- Visualization: `relation` / `analytic` / `symbolic` / `canonical`

---

## System Health Snapshot (April 2026)

| Domain | Score | Trend | Primary Blocker |
|--------|-------|-------|----------------|
| Datasets | 80% | → | 6 missing files; 924 orphaned |
| Relations | 75% | → | Entity ID format fragmented |
| Engines | 90% | ↑ | S6 gap; stub dirs incomplete |
| Routes | 85% | ↑ | Sound 1/16 full; corpus 0/8 full |
| Corpus | 85% | ↑ | BG empty; tradition metadata blank |
| Frontend | 90% | ↑ | Fetch targets mostly live |
| Sound | 70% | → | PipeWire/JACK/MOTU not connected |
| Environment | 75% | → | NPU undetected; deps not pinned |

**Overall system readiness: ~82%**

The computational layer (engines, routes, graph) is substantially complete. The primary
debt is in data infrastructure (missing files, ID normalization, orphaned datasets) and
audio plumbing (the sound layer is fully designed but silent).

---

## Scale Reference

```
203   routes in kernel.py
204   engine files in npu_engine/
55    routes FULL (engine explicitly wired)
148   routes PARTIAL (inline or stub — not necessarily broken)
188   CSV datasets across 33 knowledge domains
677   JSON files
82    JSONL corpus files
139,071  corpus text chunks
5,547  relation rows across 26 CSV files
21,157  total CSV rows
772   unique column names across all CSVs
~7,200  graph entities
~8,500  graph edges
2     SuperCollider files (atlas_synth.scd, atlas_mix.scd)
20    frontend HTML files
```

---

## Domain 1: Datasets

### Current State

953 files total (188 CSV, 677 JSON, 82 JSONL). 21,157 CSV rows across 33 knowledge domains.
The dataset layer is broad but uneven: core cosmological entities (nakshatra, graha, tithi,
devi, element) are richly covered by multiple overlapping files. Many specialist domains
(carnatic, svarodaya, chandas, astrobotany) are complete but not yet wired to any engine.

**Entity coverage depth:**
- nakshatra: 40 files
- graha: 44 files
- element: 64 files
- deity: 40 files
- plant: 26 files
- dosha: 29 files
- vastu: 27 files

**The overlap problem**: 197 column names appear in multiple files. The top conflicts
are `notes` (71 files), `element` (43 files), `name` (33 files), `source` (32 files).
Most are CONFLICT-class (values differ), not REDUNDANT. This is a column naming problem,
not a data duplication problem — the fields mean different things in different contexts.

**The orphan problem**: 924 files exist but are referenced by no engine. This is not
waste — it is the unexplored territory. Priority expansion targets:
- `astrobotany/` — 4 files, fully formed, no engine
- `carnatic/` — 7 files, rhythm engines partially use hardcoded data instead
- `svarodaya/` — 6 files including activity_matrix (210 rows), no engine
- `chandas/` — 2 files (metre forms, correspondence matrix), no engine
- `geography/` — 4 files, partially used by site_engine and region_engine

### Critical Issues

**6 missing files** — these are referenced in code and their absence likely causes
startup errors or 500 responses on affected routes:

| File | Engine that needs it | Impact |
|------|---------------------|--------|
| `datasets/layer_mapping.csv` | `layer_engine.py` | /layers routes → 500 |
| `datasets/marma/marma_coordinates.csv` | `library_kernel.py` | /library routes |
| `datasets/sanskrit/matrika_50.csv` | `library_kernel.py` | /library routes |
| `datasets/geography/sacred_sites_india.csv` | `library_kernel.py` | /library routes |
| `datasets/geography/vraja_parikrama.csv` | `library_kernel.py` | /library routes |
| `datasets/karma/dasha_meanings.csv` | `library_kernel.py` | /library routes |

### Task Queue — Datasets

- [ ] **DS-001** Create `datasets/layer_mapping.csv` with correct schema for `layer_engine.py`
  — check `npu_engine/layer_engine.py` for expected columns before creating
  — *Priority: CRITICAL — blocks /layers routes*

- [ ] **DS-002** Create stub CSVs for the 5 other missing files
  — correct headers only; content can be populated later
  — `marma_coordinates.csv`, `matrika_50.csv`, `sacred_sites_india.csv`,
    `vraja_parikrama.csv`, `dasha_meanings.csv`
  — *Priority: HIGH — stops 500 errors on startup*

- [ ] **DS-003** Add `attestation_status` and `confidence` columns to CSVs that lack them
  — run `grep -rL "attestation" datasets/*.csv` to find candidates
  — *Priority: MEDIUM — improves relation promotion pipeline*

- [ ] **DS-004** Wire `carnatic/` datasets to `npu_engine/rhythm/tala_graph.py`
  — tala_graph.py currently uses hardcoded data; should read from
    `carnatic/tala_master.csv`, `carnatic/35_talas.csv`, `carnatic/tala_families.csv`
  — *Priority: MEDIUM — enriches S3 terrain*

- [ ] **DS-005** Wire `astrobotany/` datasets — build `astrobotany_engine.py`
  — inputs: `astrobotany/astrobotanical_classes.csv`, `herbs_by_class.csv`,
    `biodynamic_vedic_mapping.csv`
  — connects to: nakshatra plants layer, biodynamic calendar, s5_kernel
  — *Priority: MEDIUM*

- [ ] **DS-006** Wire `svarodaya/` datasets — build `svarodaya_engine.py`
  — inputs: `svarodaya/activity_matrix.csv` (210 rows), `tithi_rules.csv`,
    `vara_rules.csv`, `nadis.csv`
  — connects to: intention_engine, field_state, nadi field
  — *Priority: MEDIUM*

- [ ] **DS-007** Merge duplicate nakshatra files
  — `astro/nakshatra_core.csv`, `nakshatra_deities.csv`, `nakshatra_extended.csv`,
    `nakshatra_full.csv`, `nakshatra_master.csv` cover overlapping ground
  — propose canonical merge with all columns; keep master as source of truth
  — *Priority: LOW — cosmetic but reduces confusion*

- [ ] **DS-008** Wire `chandas/` to composition and sound engines
  — `chandas/metres_forms.csv` connects metre to syllable count and cadence
  — `chandas/metre_correspondence_matrix.csv` connects metre to graha/nakshatra
  — *Priority: LOW*

---

## Domain 2: Relations

### Current State

26 relation CSV files, 5,547 total rows. The relation layer has good breadth but uneven
quality. Key relation files:

| File | Rows | Attestation quality |
|------|------|-------------------|
| `iching_relations.csv` | 1,946 | Mixed (0.45–1.00) |
| `text_entity_relations.csv` | 1,442 | 0.7 (auto-generated) |
| `relational_repair.csv` | 209 | 0.85–0.95 |
| `relations_resolved_overlays.csv` | 323 | seed_unverified |
| `vastu_relations.csv` | 145 | 0.8–0.9 |
| `deity_relations.csv` | 159 | 0.8 |
| `relations_nakshatra_plants.csv` | 135 | verified |
| `species_relations.csv` | 163 | 0.85–0.95 |

**The entity ID crisis**: 1,682 of 1,687 relation subjects are unresolved against the
entity registry. This is not because the entities don't exist — it is because the
`entities/` directory (57 total rows) is a stub, not the live entity space. The live
entities are loaded from domain CSVs. The real problem is that relation subjects use
mixed ID formats with no canonical registry to resolve against.

Known formats in use:
- `nakshatra:rohini` — preferred category:slug
- `nakshatra:1` — numeric index (relations_nakshatra_deity.csv)
- `art_agriculture` — underscore-joined, no category prefix
- `chunk:brihat` — text chunk reference
- `plant:Ashvagandha` — capitalized name
- `species:ashva` — lowercase slug

**Zero-row files**: `relations_raga_ritual.csv` and `relations_resolved_proto_canon.csv`
are empty. These are planned but not yet populated.

### Task Queue — Relations

- [ ] **REL-001** Normalize entity IDs to `category:slug` format
  — define the canonical slug for each entity type
  — write a repair script: reads all relation CSVs, normalizes IDs, writes in-place
  — cross-reference against all domain CSV `id` columns to build a lookup table
  — *Priority: HIGH — largest data integrity issue in the system*

- [ ] **REL-002** Build entity ID registry
  — scan all domain CSVs for `id` columns
  — output `datasets/entities/entity_registry.csv` with: `entity_id, entity_type, name, source_file`
  — this becomes the canonical lookup for relation subject/object resolution
  — *Priority: HIGH — prerequisite for REL-001*

- [ ] **REL-003** Populate `relations_raga_ritual.csv`
  — connect raga to festival, tithi, observance context
  — sources: `cosmology/gaudiya_festivals.csv`, `cosmology/ashtakala.csv`,
    `cosmology/daily_program.csv`
  — *Priority: MEDIUM*

- [ ] **REL-004** Promote `relations_resolved_overlays.csv` rows
  — 323 rows currently `seed_unverified`
  — run each through corpus search to find textual grounding
  — move verified rows to `relations_resolved_canon.csv`
  — *Priority: MEDIUM*

- [ ] **REL-005** Deduplicate inverse relations
  — check for `(A, rel, B)` and `(B, inverse_rel, A)` pairs in the graph
  — decide policy: keep both, keep one, or collapse
  — *Priority: LOW*

- [ ] **REL-006** Add Gaudiya-priority relations
  — Narottama das Thakura padas → raga/ashtakala/lila connections
  — Sources: `compositions/narottama_padas.csv` already exists (8 rows)
  — connect to goloka topology, vraja forests, sakhi seva datasets
  — *Priority: MEDIUM — Gaudiya community presentation readiness*

---

## Domain 3: NPU Engines

### Current State

204 Python files across 15 subdirectories. The engine layer is healthy — S0 through S5
all have active engines. The architecture has matured through a refactor cycle that left
several shadow stub directories.

**What is working** (key WORKING + route-wired engines):
- `build_field_state.py` — the spine
- `graph_engine.py` — graph traversal
- `toroidal_field.py` — θ/φ coordinate system
- `field/goloka_engine.py` — ashtakala, vraja forests, nitya devi
- `field/helix_engine.py` — dual-helix toroidal field
- `field/trajectory_engine.py` — nakshatra/tithi arc
- `field/intention_engine.py` — muhurta intention scoring
- `field/reading_engine.py` — tarot, I Ching, jyotish, Bandhu reading
- `field/ring_engine.py` — ring projections
- `field/symbol_engine.py` — glyph/emoji lookup
- `field/system_engine.py` — hardware/capability map
- `field/land_engine.py` — site/land design
- `field/guild_planner.py` — nakshatra plant guild planning
- `renderers/figure_renderer.py` — Bandhu SVG renderer
- `renderers/species_renderer.py` — species SVG renderer
- `sound/sound_engine.py` — OSC message builder
- `sound/osc_bridge.py` — OSC send to SuperCollider
- `tanpura_engine.py` (top-level) — tanpura physics
- `field_to_sound.py` — field → raga/element/guna mapping
- `phrase_engine.py` — melodic phrase generation
- `bija_synth.py` — bija phoneme synthesis
- `card_engine.py` — oracle card draw/spread
- `yantra_engine.py` + `yantra_generator.py` — yantra SVG
- `datasets.py` — all data access (1,365 lines, central)
- `mandala_schema.py` (2,309 lines) — mandala layout

**S-layer coverage:**
- S0: goloka_engine ✓
- S1: build_field_state, field_state, toroidal_field, field_layers ✓
- S2: sound_engine, field_to_sound ✓
- S3: trajectory_engine, intention_engine, rhythm/ ✓
- S4: yantra_engine, yantra_generator, vastu_engine, igpu ✓
- S5: s5_kernel, plant_engine, guild_engine, body_engine ✓
- **S6: 0 dedicated engines — gap**

**Stub directories** (planned refactor targets, not failures):
`npu_engine/core/`, `/geometry/`, `/zones/`, `/time/`, `/text/`, `/system/`
All contain 1-line placeholder files. Working implementations live at top level
and in `npu_engine/field/`.

**The `npu_engine/sound/` confusion**: Most files there (bija_synth.py, phrase_engine.py,
tanpura_engine.py, etc.) are 1-line stubs pointing to the real implementations at
`npu_engine/bija_synth.py`, `npu_engine/phrase_engine.py`, etc. Do not edit the stubs —
edit the top-level files.

### Task Queue — Engines

- [ ] **ENG-001** Build `svarodaya_engine.py`
  — reads `datasets/svarodaya/activity_matrix.csv`, `tithi_rules.csv`, `vara_rules.csv`
  — outputs: recommended activities, nadi for current field state, coherence score
  — connects to: intention_engine, field_state, body_engine
  — register route: GET /svarodaya
  — *Priority: MEDIUM*

- [ ] **ENG-002** Build S6 engine — ritual/lived experience layer
  — no dedicated S6 engine exists; journal, bandhu_chat, readings are PARTIAL
  — candidates: a `ritual_engine.py` that synthesizes muhurta + observance + devi context
  — or: a `dinacharya_engine.py` reading `ayurveda/dinacharya_panchanga.csv`
  — *Priority: MEDIUM*

- [ ] **ENG-003** Migrate stub directories progressively
  — `npu_engine/time/trajectory_engine.py` → move `field/trajectory_engine.py` there
  — do one subdirectory at a time; update imports in kernel.py before removing old path
  — *Priority: LOW — architectural cleanup*

- [ ] **ENG-004** Wire `rhythm/tala_graph.py` to carnatic CSVs
  — currently uses hardcoded tala data
  — load from `carnatic/tala_master.csv`, `carnatic/35_talas.csv`
  — *Priority: MEDIUM*

- [ ] **ENG-005** Add astrobotany engine
  — see DS-005 above
  — *Priority: MEDIUM*

---

## Domain 4: Kernel Routes

### Current State

203 routes in kernel.py (~9,800 lines). Route health:
- **55 FULL** — engine explicitly imported and called
- **148 PARTIAL** — inline logic, missing engine import, or data load without engine wrapper
- **0 STUB/DEAD** — no completely broken routes detected

The PARTIAL classification does not mean broken. Many PARTIAL routes work fine with
inline code. The concern is maintainability: a 9,800-line kernel.py is difficult to
navigate and will become more so.

**Route groups by health:**

| Group | Full | Partial | Total | Notes |
|-------|------|---------|-------|-------|
| Symbols/rings | 6 | 0 | 6 | Complete |
| Reading/oracle | 11 | 4 | 15 | Mostly complete |
| System | 4 | 2 | 6 | Mostly complete |
| Plants/land | 11 | 11 | 22 | Half done |
| Render/geometry | 7 | 7 | 14 | Half done |
| Field/spine | 4 | 5 | 9 | Core works |
| Sound | **1** | 15 | 16 | **Critical gap** |
| Corpus/research | **0** | 8 | 8 | **Critical gap** |

**Sound routes**: Only `/sound/spec` is FULL. The 15 PARTIAL sound routes
(`/sound/voice`, `/sound/mantra`, `/sound/raga`, `/sound/bols`, etc.) are not wired
to the working sound engines.

**Corpus routes**: `/corpus/registry`, `/corpus/read`, `/corpus/search` are PARTIAL
— they exist but the underlying passage_resolver / corpus indexing is not fully wired.

**Frontend-referenced routes that exist** (verified from frontend audit):
`/field`, `/intention/now`, `/coherence-score`, `/glyphs/all`, `/sound/spec`,
`/trajectory`, `/goloka`, `/guild/state`, `/rings`, `/reading/bandhu`,
`/plants/region`, `/system/audio`, `/system/state`, `/natal`, `/transits`

### Task Queue — Routes

- [ ] **RTE-001** Wire `/corpus/search` fully
  — `passage_resolver.py` is WORKING; the route calls it but filtering/tradition
    metadata is blank — fix corpus registry metadata first (COR-002)
  — *Priority: HIGH — corpus search is a core research tool*

- [ ] **RTE-002** Wire sound routes to engines
  — `/sound/raga`, `/sound/mantra`, `/sound/voice` should call `sound_engine.py`
  — `/sound/bols` should call `tabla_sampler.py`
  — `/sound/state` should reflect actual SuperCollider state
  — *Priority: HIGH — prerequisite for audio output*

- [ ] **RTE-003** Wire `/layers` route
  — requires DS-001 (layer_mapping.csv) first
  — `layer_engine.py` is WORKING once the CSV exists
  — *Priority: HIGH — depends on DS-001*

- [ ] **RTE-004** Split kernel.py into Flask blueprints
  — group by domain: sound_bp, plants_bp, reading_bp, render_bp, corpus_bp, system_bp
  — no functional change; maintainability gain
  — one blueprint at a time; test each before moving on
  — *Priority: LOW — architectural; do after other work stabilizes*

- [ ] **RTE-005** Add 501 responses for stub routes
  — routes that call missing engines should return 501 (Not Implemented)
    rather than 500 (Server Error)
  — *Priority: LOW*

---

## Domain 5: Corpus

### Current State

82 JSONL files, 139,071 text chunks across 9 traditions. The corpus is substantial and
well-organized. Gaudiya coverage is the deepest:

**Gaudiya corpus** (priority tradition):
- Bhagavatam: 15,034 chunks
- Brihad Bhagavatamrita: 3,130 chunks
- Bhakti Rasamrita Sindhu: 2,053 chunks (+154 in part 1 file)
- Hari Bhakti Vilasa: 2,649 chunks
- Vedanta Sutra: 3,757 chunks
- Brahma Samhita: 54 chunks
- Sikshashtakam: 52 chunks
- **Bhagavad Gita: 0 chunks** ← critical gap

**Other traditions**:
- Mahabharata: 27,686 en + 19,506 sa chunks = 47,192 total
- Ayurveda (Charaka, Sushruta, Bhavaprakasha): ~7,000 chunks
- Yoga (Mahanirvana, Shiva Samhita each: 5,737 chunks)
- Jyotish (Surya Siddhanta, Brihat Parashara, Brihat Jataka): ~5,500 chunks
- Vastu (Brihat Samhita, Manasara): ~2,900 chunks

**Registry state**: 81 entries. 1 registered-but-missing file. 2 present-but-unregistered.
Tradition and language fields are blank (`'?'`) across all 81 entries — this means
`/corpus/search` cannot filter by tradition, and the passage_resolver cannot weight
by authority.

### Task Queue — Corpus

- [ ] **COR-001** Add Bhagavad Gita corpus
  — `gaudiya/bg_chunks.jsonl` exists but has 0 chunks
  — use existing chunking pattern from other gaudiya texts
  — prioritize: Prabhupada translation + purports, Vishvanatha Chakravarti commentary
  — register in corpus registry with tradition=gaudiya, language=en
  — *Priority: CRITICAL — Gaudiya community presentation readiness*

- [ ] **COR-002** Populate corpus registry metadata
  — add `tradition` and `language` fields to all 81 registry entries
  — this unlocks tradition-filtered search in `/corpus/search`
  — *Priority: HIGH — unlocks corpus research workflows*

- [ ] **COR-003** Register 2 unregistered JSONL files
  — identify which 2 files are present but missing from registry
  — add with correct metadata
  — *Priority: MEDIUM*

- [ ] **COR-004** Add Grihya Sutra corpus
  — known gap identified in audit context
  — connects to: ritual calendar, festival engine, svarodaya layer
  — *Priority: MEDIUM*

- [ ] **COR-005** Add Rasashastra corpus
  — known gap: Ayurveda mineral/alchemical tradition
  — connects to: herb_exemplars, dhatu layer, ratna layer
  — *Priority: MEDIUM*

- [ ] **COR-006** Build tradition-weight index
  — passage_resolver uses text chunks but doesn't weight by tradition authority
  — build a tradition confidence table: gaudiya=0.99, jyotish_classical=0.95, etc.
  — inject into passage scoring
  — *Priority: LOW*

---

## Domain 6: Frontend

### Current State

20 HTML files in `static/`. The frontend is well-structured and largely functional.
All primary API targets (`/field`, `/goloka`, `/trajectory`, `/sound/spec`, etc.)
have corresponding routes that exist in kernel.py.

**Pages and their primary API connections:**
- `home.html` — `/field`, `/coherence-score`, `/goloka`, `/rings`, `/sound/spec`, `/intention/now`
- `live.html` — Three.js r128 toroid (kala view)
- `hexd.html` — HEXD workspace (5 modes: Field, Calendar, Journal, Research, Editor)
- `s0.html–s6.html` — S-layer domain pages
- `widgets/` — 10 focused widget pages (coherence, dasha, field, goloka, guild, natal, sound, system, transits)

**Key design notes:**
- Bandhu is an ambient floating presence across all domains — not an oracle or chat interface
- `live.html` toroid: torus tube = solar year, toroidal angle φ = solar position, poloidal angle θ = lunar/tithi
- `hexd.html` hex terrain directly represents live system state: 404 routes = dark forest, 200 = passable, working apps = lit villages

**Frontend gaps identified:**
- `widgets/sound.html` calls `/sound/spec` and `/system/audio` — both exist but sound output is silent
- `home.html` calls `/reading/bandhu` — this route is FULL; Bandhu reading works
- `/plants/region` is called with hardcoded `lat=29.65&lon=-82.32` (Gainesville) — should be dynamic

### Task Queue — Frontend

- [ ] **FE-001** Add dynamic geolocation to `/plants/region` call
  — replace hardcoded lat/lon with browser `navigator.geolocation`
  — fallback to current hardcoded values
  — *Priority: LOW*

- [ ] **FE-002** Add error handling for offline API calls
  — all fetch() calls should degrade gracefully when kernel is not running
  — show a "standalone mode" indicator, not a blank page
  — *Priority: MEDIUM*

- [ ] **FE-003** Unify CSS variables across all pages
  — each page currently defines its own color variables; extract to a shared `atlas.css`
  — *Priority: LOW*

- [ ] **FE-004** Surface all working routes in home.html
  — `home.html` is the root dashboard; it should show status of all 55 FULL routes
  — connect to `/health` and `/api` index routes
  — *Priority: MEDIUM*

---

## Domain 7: Sound

### Current State

The sound layer is the most completely designed unworking system in Atlas. Every
computational component exists and is substantive:

**Computational pipeline (all WORKING):**
```
field_state()
    ↓
field_to_sound.py     (428 lines) — derives raga, element, guna, treatment vector
    ↓
sound_engine.py       (373 lines) — builds OSC message set
    ↓
osc_bridge.py         (57 lines)  — send_sound_spec() → SuperCollider via OSC
    ↓
sc/atlas_synth.scd               — SynthDefs: tanpura, raga melody, tabla bols, bija drone
sc/atlas_mix.scd                 — mix layer
```

**Additional working sound engines:**
- `tanpura_engine.py` (558 lines) — full tanpura physics with graha jivari model
- `tanpura_field.py` (242 lines) — tithi → string weights
- `phrase_engine.py` (392 lines) — melodic phrase generation with gamaka types
- `bija_synth.py` (247 lines) — bija phoneme synthesis
- `sarangi_voice.py` (377 lines) — sarangi voice model
- `rhythm/` — cross_rhythm, tala_graph, tihai, theka, layakari (all WORKING)
- `vocal/` — bhava, breath, gamaka, phoneme_graph, syllable_sequencer, vocal_kernel (all WORKING)
- `sympathetic/` — string model, excitation, sympathetic kernel (all WORKING)
- `mix/` — mix_kernel, mix_osc, nakshatra_mix, deity_mix (all WORKING)

**The only gap is audio plumbing:**
1. PipeWire JACK shim not configured → SuperCollider can't see MOTU M2
2. SuperCollider not running as a service
3. No systemd service files exist for any Atlas component

### Task Queue — Sound

- [ ] **SND-001** Configure PipeWire JACK bridge
  — install `pipewire-jack` if not present
  — set `PIPEWIRE_ALSA_HACK=1` or configure `/etc/pipewire/jack.conf`
  — verify: `pw-jack jackd -d dummy` then `pw-jack scsynth -u 57110`
  — test: `sclang -e "s.boot; s.ping;"`
  — *Priority: CRITICAL — prerequisite for all audio output*

- [ ] **SND-002** Write SuperCollider startup script
  — `sc/start_atlas.sh`: starts scsynth, loads atlas_synth.scd, loads atlas_mix.scd
  — verify all SynthDefs loaded before sending OSC
  — *Priority: HIGH — depends on SND-001*

- [ ] **SND-003** Install systemd service for kernel.py
  — `atlas-kernel.service` → `python ~/atlas_core/kernel.py`
  — enable on boot
  — *Priority: HIGH — reliability*

- [ ] **SND-004** Install systemd service for SuperCollider
  — `atlas-sound.service` → runs `sc/start_atlas.sh`
  — start after `atlas-kernel.service`
  — *Priority: HIGH — depends on SND-001, SND-002*

- [ ] **SND-005** Wire sound routes to engines
  — see RTE-002 above
  — `/sound/raga` → `sound_engine.py` → `phrase_engine.py` → OSC
  — `/sound/bols` → `tabla_sampler.py` → OSC
  — *Priority: HIGH — depends on SND-001*

- [ ] **SND-006** Test tanpura end-to-end
  — `tanpura_engine.py` is the most complete instrument model
  — verify: field_state → tanpura_field.py → tanpura_engine.py → osc_bridge.py → SC
  — this is the single instrument that should work first
  — *Priority: HIGH — minimum viable audio milestone*

- [ ] **SND-007** Port critical SynthDefs to WebAudio
  — bija drone and tanpura drone could run in the browser
  — enables sound on `home.html` without SuperCollider
  — *Priority: LOW — fallback path; SC path is preferred*

---

## Domain 8: Environment

### Current State

**Requirements**: `requirements.txt` has only 4 entries. The npu_engine package uses
`numpy`, `scipy`, `concurrent.futures`, and likely `flask`, `ephem`/`skyfield`, `python-osc`,
`requests`, and others. The requirements file is significantly incomplete.

**NPU**: Intel Meteor Lake NPU not detected in `lspci`. The NUC has NPU capability;
this likely needs an OpenVINO driver or kernel module. `toroidal_field.py` has `_init_npu()`
already written — it just needs the hardware available.

**No systemd services installed**: Atlas has no auto-start. Kernel must be started manually
after each boot. No watchdog, no restart-on-crash.

### Task Queue — Environment

- [ ] **ENV-001** Audit and complete `requirements.txt`
  — run `pipreqs ~/atlas_core/ --force` to generate from imports
  — review and pin versions
  — add: `flask`, `numpy`, `scipy`, `python-osc`, `requests`, `ephem` or `skyfield`,
    `playwright` (called in code), `pillow` (likely)
  — *Priority: HIGH*

- [ ] **ENV-002** Investigate NPU detection
  — check: `ls /dev/accel*` and `dmesg | grep -i npu`
  — install `openvino-dev` if not present: `pip install openvino-dev`
  — verify: `python -c "from openvino.runtime import Core; c=Core(); print(c.available_devices)"`
  — *Priority: HIGH — NPU inference is a core system capability*

- [ ] **ENV-003** Install systemd services
  — `atlas-kernel.service` (see SND-003)
  — `atlas-sound.service` (see SND-004)
  — `atlas-ngrok.service` (if remote access needed)
  — *Priority: HIGH*

- [ ] **ENV-004** Add health monitoring
  — `scripts/health_check.sh` — pings /health, checks SC, checks NPU
  — run via cron every 5 minutes; log to `logs/health.log`
  — *Priority: MEDIUM*

---

## Priority Remediation Pathway

This is the ordered path toward a presentable, stable, audio-producing Atlas 330.

### Phase 1: Stop the bleeding (< 1 day total)

These unblock downstream work and stop 500 errors:

1. **DS-001/DS-002** — Create 6 missing dataset stubs (30 min)
2. **ENV-001** — Complete requirements.txt (1 hr)
3. **COR-002** — Populate corpus registry tradition/language fields (1 hr)
4. **COR-001** — Add BG corpus (2–4 hrs)

### Phase 2: First audio (2–4 days)

The milestone: tanpura plays from field state.

5. **SND-001** — Configure PipeWire JACK bridge (2–4 hrs, may need iteration)
6. **SND-002** — Write SuperCollider startup script (1 hr)
7. **SND-003/SND-004** — Install systemd services (1 hr)
8. **SND-006** — Test tanpura end-to-end (1–2 hrs)
9. **ENV-002** — Enable NPU detection (2–4 hrs)

### Phase 3: Data integrity (3–5 days)

The milestone: relation graph is coherent and queryable.

10. **REL-002** — Build entity ID registry (1 day)
11. **REL-001** — Normalize entity IDs (1–2 days)
12. **RTE-001** — Wire /corpus/search fully (2–3 hrs)
13. **RTE-003** — Wire /layers route (1 hr, after DS-001)

### Phase 4: Expand the dark territory (ongoing)

Wire orphaned datasets to engines:

14. **DS-004** — Wire carnatic/ to tala_graph (1 day)
15. **DS-005** — Build astrobotany engine (1–2 days)
16. **DS-006** — Build svarodaya engine (1–2 days)
17. **ENG-002** — Build S6 ritual/dinacharya engine (1–2 days)
18. **REL-003/REL-006** — Populate raga-ritual and Gaudiya relations (2–3 days)

### Phase 5: Architecture (ongoing)

19. **RTE-004** — Split kernel.py into blueprints (3–5 days)
20. **ENG-003** — Migrate stub directories (progressive, low urgency)

---

## Session Log

*Append entries here as work completes. Format: `YYYY-MM-DD — [TASK-ID] description (who)`*

- 2026-04-10 — Full 14-section system audit completed via Claude Code on kanjira
- 2026-04-10 — atlas-state and npu-integrator skills rewritten to reflect current state
- 2026-04-10 — This document created

---

## Appendix A: How to Run an Atlas Session

### Starting Atlas

```bash
cd ~/atlas_core
python kernel.py
# → Flask running on http://localhost:5000

# In another terminal, start SuperCollider (once SND-001/002 are done):
bash sc/start_atlas.sh
```

### Checking system health

```bash
curl localhost:5000/health
curl localhost:5000/field    # current field state
curl localhost:5000/goloka   # ashtakala + vraja
curl localhost:5000/sound/spec  # sound specification
```

### Running a targeted audit

```bash
# Check which routes return 200:
for route in /field /goloka /helix /trajectory /rings /yantra /corpus/search; do
  echo "$route: $(curl -s -o /dev/null -w '%{http_code}' localhost:5000$route)"
done
```

### Adding a dataset and wiring it

1. Create `datasets/<domain>/<name>.csv` with correct headers
2. Check `npu_engine/datasets.py` for the existing loader pattern
3. Add a loader function in the relevant engine or in `datasets.py`
4. Add or update the kernel.py route to call the engine
5. Test: `curl localhost:5000/<route>`
6. Update the task queue in this document

---

## Appendix B: Coding Task Queue Format

Tasks in this document follow this format for AI-readable execution:

```
- [ ] **DOMAIN-NNN** Short imperative title
  — detail line 1: what files to read/write
  — detail line 2: what engines/datasets connect
  — detail line 3: test criterion or success condition
  — *Priority: CRITICAL / HIGH / MEDIUM / LOW — optional blocker note*
```

When starting a task as an AI assistant:
1. Read the task description fully
2. Read the files mentioned in the detail lines before writing anything
3. Check this document's session log for any partial work already done
4. Complete the task, then append a session log entry
5. Mark the task `- [x]` with a date

When a task is completed:
```
- [x] **DS-001** Create `datasets/layer_mapping.csv` *(2026-04-11 — created with 7-column schema)*
```

---

## Appendix C: Known Good Patterns

### Engine file structure
```python
"""
engine_name.py

Purpose: one sentence.
Domain: S3 / Kala / time cycles
Relations: connects nakshatra → raga → muhurta via trajectory

Datasets:
    datasets/astro/nakshatra_master.csv  — nakshatra attributes
    datasets/cosmology/ashtakala.csv     — 8 daily periods
"""

from npu_engine.datasets import load_csv

_NAKSHATRAS = None

def _load():
    global _NAKSHATRAS
    if _NAKSHATRAS is None:
        _NAKSHATRAS = load_csv("datasets/astro/nakshatra_master.csv")

def derive_result(field_state: dict) -> dict:
    _load()
    # ... computation
    return {"result": ..., "source": "engine_name"}
```

### Relation row format (canonical)
```
from_id,relation,to_id,source_title,source_locator,excerpt,tradition,confidence,notes
nakshatra:rohini,nakshatra_ruling_graha,graha:chandra,Brihat Parashara Hora,,,,0.99,classical attribution
```

### Dataset CSV header convention
```
id,name,name_iast,name_devanagari,element,guna,tradition,attestation_status,source,notes
```

### Kernel route pattern (minimal FULL route)
```python
@app.route("/domain/endpoint")
def _endpoint():
    from npu_engine.domain_engine import derive_result
    fs = build_field_state()
    result = derive_result(fs)
    return jsonify(result)
```
