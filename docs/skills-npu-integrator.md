---
name: npu-integrator
description: >
  Expert workflow for reading, understanding, and extending the Atlas 330 cosmological
  knowledge system — a Vedic relational knowledge graph and civilizational simulation
  platform integrating cosmology, jyotish, ayurveda, sound, geometry, ritual, embodiment,
  speculative fiction, and game design. Atlas is the technical substrate for the Coherence
  Spectrum game, the Emergent Satya Yuga worldbuilding framework, and The Devi Field novel.
  The npu_engine package provides the computational layer. Use this skill whenever the user
  asks to: add or generate a new module, dataset, script, wiki page, game mechanic, world
  layer, story element, or character system; wire components together; extend the ontology;
  generate cards, infographics, or visualizations; write docs; run or explain a pipeline
  step; work with seeds, offerings, research cycles, or narrative structure; or integrate
  any new domain into Atlas. Read before writing — always.
---

# Atlas Integrator Skill

## The Core Principle

**Everything in Atlas is relational.** This is not a metaphor — it is the operative rule
for every task.

A nakshatra is not a fact. It is a node in a web: ruled by a graha, presided by a deity,
resonant with an element and guna, mapped to a body region, connected to a raga, placed
at a coordinate on the toroidal field. Remove the relations and you have a name. The
relations are the meaning.

**Your job when extending Atlas is always the same: find where the new thing connects
into the existing web. An island node with no relations adds nothing. A node with three
strong relations to existing entities adds coherence.**

---

## System Architecture

Atlas has six interconnected layers:

**Knowledge graph** — entities and relations with three-axis metadata.
Every relation carries: `from_id | relation | to_id | source | confidence | stability | authority`
Graph data loaded from `datasets/` via `npu_engine/datasets.py`. The `entities/` directory
is a stub (57 rows); live entity space is in the domain CSV files.

**Computational substrate** — `npu_engine/` (204 files) processes the graph:
`build_field_state.py`, `graph_engine.py`, `toroidal_field.py`, `field/` engines,
sound/rhythm/vocal/sympathetic subsystems.

**Flask kernel** — `kernel.py` at `localhost:5000`. 203 routes. All cosmological
computation flows through `/field` (field state endpoint). Frontend and engines both
read from here.

**Frontend** — `static/` (20 HTML files). S-layer domain pages (s0–s6), widgets,
toroidal field visualizer (`live.html`), HEXD workspace (`hexd.html`).

**Corpus** — `datasets/sources/` (82 JSONL, 139,071 chunks). Searchable via `/corpus/search`.
Gaudiya corpus is the priority tradition. Passage resolver links chunks to entities.

**Creative/civilizational layer** — Atlas is the technical substrate for:
- **Coherence Spectrum** — persistent procedural civilization simulator
- **Emergent Satya Yuga** — worldbuilding/story framework
- **The Devi Field** — speculative eco-mythic sci-fi novel

---

## Three Axes (always independent)

- **Stability**: `stable` → `working` → `experimental`
- **Authority**: `shastra` (textual) | `sadhu` (practitioner) | `guru` (synthesis/AI)
- **Visualization**: `relation` → `analytic` → `symbolic` → `canonical`

AI-generated content always starts at `experimental / guru`. Never skips the canon guard.
Canon is the anchor. Relations grow outward from it.

---

## Media generation principle
`graph → template → artifact` (never `prompt → guess → artifact`)

---

## Step 1 — Orient: find the relations (always do this first)

Before writing anything, read these:

1. The relevant engine file(s) in `npu_engine/` — check what datasets they load
2. `npu_engine/datasets.py` — how data is loaded and what types are returned
3. The relevant CSV(s) in `datasets/` — check column names and entity ID format
4. Any sibling engine in the same subdirectory — match its patterns exactly
5. The route in `kernel.py` that calls this engine — understand the response contract

**What to extract — always ask: what does this connect to?**
- Which existing entities, modules, or datasets does the new thing relate to?
- What entity ID format does this domain use? (`nakshatra:rohini` or `nakshatra_rohini`?)
- What stability/authority level do those existing relations carry?
- Where would this node sit on the θ/φ toroidal coordinate system?
- Which S-layer does it belong to?
- Does similar work already exist — would this increase relational density or duplicate?

**Known entity ID fragmentation** (April 2026): The relation CSVs use mixed formats.
Before adding any relation rows, check which format the target domain uses in its existing
relation files. The canonical preference is `category:slug` (e.g. `nakshatra:rohini`,
`graha:chandra`, `devi:lalita`).

---

## Step 2 — Clarify (only if genuinely ambiguous)

Ask one focused question. For integration tasks, confirm which existing
entities/modules/datasets the new component connects to, and at what stability layer.

---

## Step 3 — Generate

Match the task type to the right output pattern:

### New npu_engine module

- Match file and class naming of sibling engines — `*_engine.py` pattern
- Include module-level docstring: purpose, cosmological domain, datasets used
- Add `# Atlas Relations:` comment listing which entities/engines it connects to
- Follow same `__init__` signature style as existing working engines (not stubs)
- Register in `npu_engine/__init__.py` in same style as existing exports
- Place in the right subdirectory: `field/` for live field engines, `engines/` for
  zone engines, top-level for core engines
- **Do not place in stub directories** (core/, geometry/, zones/, time/, text/, system/)
  unless explicitly migrating existing code there

### New dataset (CSV)

- Match column naming of closest existing dataset in same domain directory
- Always include: `id` or entity-id field, name fields, `attestation_status` or `confidence`
- Preferred relation CSV schema: `from_id, relation, to_id, source_title, source_locator,
  excerpt, tradition, confidence, notes`
- Preferred entity CSV schema: `id, name, name_iast, element, guna, [domain fields]`
- Place in the correct subdirectory — check `datasets/` structure
- If dataset is referenced in any engine, add the file immediately (even a stub CSV
  with correct headers stops 500 errors)

### New kernel route

- Match the pattern of the nearest functional route — FULL routes are the models
- Always call an engine rather than implementing logic inline
- Return JSON with consistent structure; include `field_state` context where relevant
- Add to the correct group in kernel.py (field, sound, plants, reading, render, etc.)

### New relation file

- Match column structure of `datasets/relations/bija_relations.csv` (most complete schema):
  `from_id, relation, to_id, source_title, source_locator, excerpt, tradition, confidence, notes`
- Use `category:slug` entity ID format
- Confidence: `0.99` (textual canon) → `0.9` (strong inference) → `0.7` (resonance) →
  `seed_unverified` (proposed, not yet checked)
- New predicates must be justified; prefer existing predicates from the relations corpus

### New frontend page

- Match pattern of nearest S-layer page (s0–s6)
- Connect to `/field` for panchanga on load; degrade gracefully if offline
- Derive all cosmological params from field state — never hardcode
- Dark palette: background transparent, connect to CSS variables
- Add fetch() calls only to routes that exist in kernel.py (check route audit)

### Corpus ingestion

- JSONL format: one chunk per line, each with `text`, `source`, `chunk_id`, `tradition`,
  `language` fields
- Register in corpus registry with tradition + language populated
- Run chunk count check after ingestion
- Priority gaps: BG corpus (bg_chunks.jsonl = 0), Rasashastra, Grihya Sutra

### Game layer component

- New terrain type: map to an S-layer and a cosmological domain
- New field event: must derive from a `field_state()` transition, not a timer
- New mechanic: must express a relational principle
- Progression states: `unknown → observed → documented → attested → mastered`

### Coherence Spectrum element

- Herd mechanics: fluid density fields, not individual control
- Coherence level affects: herd viscosity, predator behavior, tech reliability, rendering
- Dosha morphogenesis: sustained environmental pressure → physiological drift
- Planetary alignment events: derive coefficients from `kernel.field_state()`

### Emergent Satya Yuga element

- Five phases: Collapse → Discovery → Resistance → Breakthrough → Stabilization
- NPUs: meaning-based computation via Sanskrit grammar logic
- Secret societies as relational factions (Axiom Directorate, Custodians of the Broken Axis,
  Solar Ascendancy, Mycelial Covenant)

### The Devi Field narrative element

- Characters carry the framework experientially: Anika (soil/earth), Eli (mind/NPU), Maya (forest/body)
- "The Devi Field did not impose. It entrained." — core narrative principle
- Tone: grounded, scientific, mythic without being mystical

---

## Step 4 — Present

For each generated output:
1. State which existing patterns you matched and why
2. Show the content
3. Flag any assumptions made due to missing context
4. Note the stability layer and authority level of the generated content
5. Note which of the 6 missing dataset files (if any) the work depends on

---

## Guardrails

- **Relations over nodes.** Always identify at least three existing entities the new
  thing connects to before generating it.
- **Canon is sacred.** Never modify `relations_resolved_canon.csv` or canonical entity
  counts (27 nakshatras, 9 grahas, 12 rashis, 5 elements, 3 gunas) without explicit confirmation.
- **Layer discipline.** All AI-generated content starts at `experimental / guru`.
- **Field state is the source of truth.** Never hardcode cosmological values into visual
  components — always derive from `kernel.field_state()` at `localhost:5000/field`.
- **Sanskrit integrity.** Preserve devanagari, IAST transliteration, and English gloss
  as separate fields. Don't flatten to English-only.
- **Frame awareness.** If a term varies by sampradaya, note the frame.
- **Never guess at the codebase.** Read the file before assuming its interface.
- **No islands.** Output must connect into the existing relational web.
- **Check missing files first.** If the task touches layer_mapping, marma_coordinates,
  matrika_50, sacred_sites_india, vraja_parikrama, or dasha_meanings — those files are
  missing and need creating before the engine will work.

---

## S0–S6 Layer System

```
S0  ✦  Bindu · Metaphysical Source
       Goloka Vṛndāvana · acintya · the axis everything points toward
       Engine: goloka_engine.py
       Routes: /goloka

S1  🔱  Archetype & Deity
       15 Nitya Devīs · Navagraha · 64 Śaktis
       Engine: build_field_state.py, field_state.py, toroidal_field.py
       Routes: /field, /spine, /trajectory, /helix

S2  🎵  Sound & Mantra
       Raga, tala, bija, tanpura, svara
       Engine: sound_engine.py, field_to_sound.py, osc_bridge.py
       Routes: /sound/spec, /sound/state (mostly PARTIAL)
       Status: engines written, no audio output (PipeWire/JACK blocker)

S3  ⏳  Time & Rhythm
       Kala, panchanga, tithi, vara, nakshatra arc
       Engine: trajectory_engine.py, intention_engine.py, rhythm/
       Routes: /trajectory, /intention/now, /calendar/day

S4  🔷  Geometry & Symbol
       Yantra, mandala, vastu, hexfield
       Engine: yantra_engine.py, yantra_generator.py, vastu_engine.py, igpu.py
       Routes: /yantra, /yantra/svg, /render/*

S5  🌿  Ecology & Embodiment
       Plants, body, marma, ayurveda, biodynamics
       Engine: s5_kernel.py, plant_engine.py, guild_engine.py, body_engine.py
       Routes: /plants/*, /guild/*, /land

S6  👁  Lived Experience & Oracle
       Reading, game, character, codex, journal
       Engine: reading_engine.py, character_engine.py, card_engine.py
       Routes: /reading/*, /card/*, /codex/*
       Note: S6 has 0 dedicated field engines — gap in coverage
```

---

## Current Route Health (April 2026)

| Group | Full | Partial | Total | Priority |
|-------|------|---------|-------|----------|
| Symbols/rings | 6 | 0 | 6 | ✓ done |
| Reading/oracle | 11 | 4 | 15 | mostly done |
| Plants/land | 11 | 11 | 22 | half done |
| Render/geometry | 7 | 7 | 14 | half done |
| System | 4 | 2 | 6 | mostly done |
| Sound | 1 | 15 | 16 | needs work |
| Corpus/research | 0 | 8 | 8 | needs work |
| Field/spine | 4 | 5 | 9 | core is ok |

Sound routes and corpus/research routes are the biggest functional gaps.

---

## Key Datasets by Domain

| Domain | Primary files |
|--------|--------------|
| Nakshatra | `astro/nakshatra_master.csv` (27r), `astro/nakshatra_full.csv` |
| Tithi | `astro/tithi_master.csv` (30r), `cosmology/nitya_devi_master.csv` |
| Graha | `astro/grahas.csv` (9r), `cosmology/graha_master.csv` |
| Devi | `cosmology/nitya_devi_master.csv` (15r) |
| Raga | `sound/raga_master.csv` (20r), `gandharva/raga_therapeutic.csv` |
| Tala | `carnatic/tala_master.csv` (50r), `carnatic/35_talas.csv` |
| Plants | `plants/nakshatra_plants.csv`, `plants/pfaf_structured.csv` (2,514r) |
| Marma | `marma/marma_field.csv` (37r), `marma/body_region_marma.csv` |
| Vastu | `vastu/vastu_directions.csv`, `vastu/perimeter_deities.csv` |
| Sound params | `sound/tanpura_strings.csv` (7r) |
| Goloka | `cosmology/ashtakala.csv`, `cosmology/vraja_forests.csv` |
| Game | `game/lineages.csv`, `game/sura_asura_map.csv` |

---

## Orphaned Datasets (rich but dark — next expansion targets)

These datasets exist but are not referenced by any engine. Priority wiring targets:

- `astrobotany/` — astrobotanical classes, biodynamic-vedic mapping, herbs by class
- `carnatic/` — tala graph in `rhythm/tala_graph.py` reads hardcoded data; these CSVs should feed it
- `svarodaya/` — activity_matrix (210r), tithi/vara rules; svarodaya engine not yet built
- `chandas/` — metre correspondence matrix, metres forms; no engine
- `iching/` — hexagram tables mostly wired via reading_engine; check coverage
- `geography/` — ecoregions, sacred sites; partially used in site_engine and region_engine

---

## Sound Architecture

The sound layer is fully designed but not outputting. When working on sound:

```
field_state()
    ↓
field_to_sound.py       → derives raga, element, guna character, treatment vector
    ↓
sound_engine.py         → builds OSC message set (_resolve_sound_params, _compute_layers)
    ↓
osc_bridge.py           → send_sound_spec() → SuperCollider via OSC
    ↓
sc/atlas_synth.scd      → SynthDefs: tanpura, raga melody, tabla bols, bija drone
```

Active blockers:
1. PipeWire JACK shim to MOTU M2 not configured
2. SuperCollider not started as service
3. No systemd service files installed

The tanpura and bija synth engines are fully written. The OSC bridge is working.
The gap is the audio plumbing, not the computation.

---

## Corpus Architecture

```
datasets/sources/
  <tradition>/<text>_chunks.jsonl    one chunk per line
  entity_index.json                  chunk_id → entity refs
  passages.csv                       tagged passage index
datasets/relations/
  text_entity_relations.csv          chunk → entity links (1,442 rows)
```

Search path: `/corpus/search` → `passage_resolver.py` → entity_index.json + JSONL chunks.

Tradition coverage: ayurveda, cosmology, dharma, epics, gaudiya (priority), jyotish,
vastu, vedic, yoga. All 82 files present except BG (0 chunks).

---

## Local Inference Stack

Atlas runs local LLM via Ollama — entirely offline, no cloud dependency.

```
kernel.field_state()  →  field_scheduler scoring
                     →  ollama (local LLM: Bandhu chat, embeddings, research synthesis)
                     →  vector_store.py (semantic search over graph nodes)
```

**Role separation:**
- **Claude** (external, this session) — architect, code generator, skill builder
- **Ollama** (local, on kanjira) — runtime intelligence: Bandhu companion, embeddings, AI pipeline
