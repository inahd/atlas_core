---
name: npu-integrator
description: >
  Expert workflow for reading, understanding, and extending the Atlas cosmological knowledge
  system — a Vedic relational knowledge graph and civilizational simulation platform integrating
  cosmology, jyotish, ayurveda, sound, geometry, ritual, embodiment, speculative fiction, and
  game design. Atlas is the technical substrate for the Coherence Spectrum game, the Emergent
  Satya Yuga worldbuilding framework, and The Devi Field novel. The npu_engine package provides
  the computational layer. Use this skill whenever the user asks to: add or generate a new module,
  dataset, script, wiki page, game mechanic, world layer, story element, or character system; wire
  components together; extend the ontology; generate cards, infographics, or visualizations; write
  docs; run or explain a pipeline step; work with seeds, offerings, research cycles, or narrative
  structure; or integrate any new domain into Atlas or Coherence Spectrum. Read before writing — always.
---

# Atlas Integrator Skill

## The Core Principle

**Everything in Atlas is relational.** A nakshatra is not a fact — it is a node
in a web. Remove the relations and you have a name. The relations are the meaning.

Your job when extending Atlas: **find where the new thing connects into the
existing web.** An island node with no relations adds nothing. A node with three
strong relations to existing entities adds coherence.

This applies equally to code, datasets, wiki pages, game mechanics, and UI.
A shell panel that doesn't read from `/spine` is hardcoded where it should be
relational. A wiki page with no relations is a name without meaning.

---

## Canonical Folder Map (April 2026)

```
atlas_330/
  kernel.py             Flask spine — port 5000
  om.py                 Tanpura drone (root canonical — not npu_engine/om.py)
  drik_panchanga.py     Vedic panchanga
  start.sh              Boot/control script
  CLAUDE.md             Live session map — read first

  npu_engine/           Reasoning layer — DO NOT RENAME
    datasets.py         136 CSVs → 3400-node graph
    graph_engine.py     Canonical relation graph
    build_field_state.py  FieldState construction
    field_to_sound.py   Nakshatra → raga descent chain
    mandala_schema.py   Vastu mandala zone resolver
    ui_vastu_engine.py  UI layout from field state (derive_ui_layout())
    phrase_engine.py    Live raga graph traversal
    bija_synth.py       Formant synthesis
    mix/                11-layer mix graph → OSC
    rhythm/             Tala → OSC
    sympathetic/        13 taraf strings → OSC

  datasets/             Canonical — DO NOT MODIFY
    relations/relations_resolved_canon.csv  ← SACRED
    sources/            Sanskrit/English texts + JSONL chunks
    cosmology/          Grahas, nakshatras, devis, rashis
    carnatic/           Talas, ragas
    ayurveda/           704 herbs

  apps/                 12 web apps (all served by kernel)
  static/               shell.html (THE surface) + css/js
    js/shell.js         Main shell renderer
    js/ui.js            Camera, keyboard, observe overlay
  sc/                   SuperCollider (atlas_synth.scd, start_sc.sh)
  scripts/              Pipeline
  instance/             Personal (altar.json, natal.json, vector_store/)
  wiki/                 nakshatras/ grahas/ devis/ music/ kalas/ cosmos/
  docs/reference/specs/ VISUAL_STANDARDS.md, atlas_axes.md — read before UI work
  purana/               Archive
```

**Gone (April 2026):** kosha/, karma/, kshetra/, mandala/, nada/ — removed.
Use real paths above.

---

## System Architecture

**Knowledge graph** — entities + relations, three-axis metadata.
Every relation: `subject | predicate | object | source | confidence | stability | authority`

**Computational substrate** — `npu_engine/` processes the graph into field state.
The chain: `datasets.py → graph_engine.py → build_field_state.py → field_state`

**UI layout engine** — `npu_engine/ui_vastu_engine.py` → `derive_ui_layout(field_state)`.
Produces: center_focus, layer_ring (S0–S6), zone_regions (8 vastu directions),
entity_nodes, navigation_paths, style_hints. All coords in [0,1]. Validated.
**Renderers consume this — they never recompute layout.**

**Shell** — `static/shell.html` reads `/spine` → calls `derive_ui_layout()` result.
The ideal shell knows nothing: ~400 lines reading field data and rendering it.
Zone panels should be a thin border ring; center cosmos fills the window.

**Sound** — `om.py` (tanpura drone) + SC (`sc/atlas_synth.scd`) via OSC.
Sound is first-class — runs independent of browser. SC is the audio path.

**Pipeline** — `scripts/` implements: ingest → relate → score → gap-detect → promote.

**Creative layer** — Coherence Spectrum (sim), Emergent Satya Yuga (worldbuilding),
The Devi Field (novel). Same ontology at different resolutions.

---

## Three Authority Axes (always independent)

- **Stability**: `stable` → `working` → `experimental`
- **Authority**: `shastra` (textual) | `sadhu` (practitioner) | `guru` (AI)
- **Visualization**: `relation` → `analytic` → `symbolic` → `canonical`

AI content always starts `experimental / guru`. Canon is the anchor.
Never skip `guard_canon.py` for relation promotion.

## Media generation law
`graph → template → artifact` — never `prompt → guess → artifact`

---

## Step 1 — Orient (always first)

Read in order:
1. `CLAUDE.md` — live session map, endpoints, user context
2. `SYSTEM_MAP.md` — what's running, wired, broken
3. `docs/reference/specs/VISUAL_STANDARDS.md` — before any CSS/SVG/HTML
4. `docs/reference/specs/atlas_axes.md` — four axes before any data work
5. The specific module/dataset/app the task touches

**Ask before writing:**
- What existing entities/modules does this connect to?
- What relation predicates already exist for this? (`docs/reference/specs/ATLAS_ONTOLOGY_SCHEMA.md`)
- What stability/authority level is appropriate?
- Does this already exist somewhere? Would it duplicate or add coherence?

---

## Step 2 — Clarify (only if genuinely ambiguous)

One focused question. Confirm which existing entities/modules the new component
connects to, and at what stability layer.

---

## Step 3 — Generate

### New dataset (CSV)
```csv
entity_id,name,element,guna,domain,stability,authority,source
nakshatra_rohini,Rohiṇī,water,tamas,jyotish,stable,shastra,Brihat Samhita
```

### New relation
```csv
subject,predicate,object,confidence,stability,authority,source
nakshatra_rohini,ruled_by,graha_chandra,1.0,stable,shastra,Brihat Samhita 24.1
```
Never write to `relations_resolved_canon.csv`. Add to `datasets/relations/`
and let the promotion pipeline handle it.

### New npu_engine module
```python
# npu_engine/new_engine.py
"""Brief — what it computes and what graph nodes it connects."""
from npu_engine.graph_engine import GraphEngine

class NewEngine:
    def __init__(self):
        self.graph = GraphEngine()

    def compute(self, field_state: dict) -> dict:
        # derive from field — never hardcode cosmological knowledge
        ...
```
Add lazy import to `npu_engine/__init__.py`.
Register Flask route in `kernel.py` if it needs an endpoint.

### New wiki page
Location: `wiki/<type>/<name>.md` — subdirectory structure is canonical.
- Nakshatras → `wiki/nakshatras/rohini.md`
- Grahas → `wiki/grahas/chandra.md` (Sanskrit names)
- Devis → `wiki/devis/kameshvari.md`
- Ragas → `wiki/music/ragas/yaman.md`

```markdown
# Rohiṇī

**id:** nakshatra_rohini
**type:** nakshatra
**number:** 4
**element:** water
**guna:** tamas
**lord:** Chandra
**deity:** Prajāpati

## Relations
- ruled_by: graha_chandra
- presided_by: deity_brahma
- element: water

## Passages
> Source: Brihat Samhita 24.x — attested quote here

## Notes
```

### New app
Location: `apps/<name>/index.html`
- Connect to `localhost:5000/field` or `/spine` for live data
- Degrade gracefully offline
- Dark palette: `--bg:#0a0800 --gold:#e0c27b`
- Register route in `kernel.py`
- All cosmological parameters from field_state — never hardcoded

### UI / shell work
- Read `docs/reference/specs/VISUAL_STANDARDS.md` first — always
- Layout computed by `ui_vastu_engine.py → derive_ui_layout()` — never recompute in JS
- Shell reads `/spine` → feeds layout object to `renderer.js`
- Zone panels = thin border ring; center cosmos = 70%+ of window
- `torus.js` renders 3D field on center canvas
- Clicking a zone expands it in place; ESC collapses

---

## Current Wiring State (April 2026)

### Fully working
- `kernel.py` — Flask spine, port 5000
- `npu_engine/datasets.py` — 3400-node graph
- `npu_engine/build_field_state.py` — FieldState
- `npu_engine/ui_vastu_engine.py` — derive_ui_layout()
- `apps/agriculture/` — PWA, /field live, offline
- `/field`, `/spine`, `/shell/state`, `/observe`, `/render`, `/s5`

### Working but needs fixes
- `om.py` — stuck on ALSA device 9 (spdif). Fix: `run_sounddevice` must
  return `False` on failure to fall through to `run_pwcat`. Device should
  be discovered by name not hardcoded index.
- `static/shell.html` — renders zones as equal 3×3 grid. Needs border-ring
  layout with cosmos center. Layout data from `derive_ui_layout()` is correct.
- `/` serves legacy `atlas.html` — should redirect to `/shell`

### Stub / incomplete
- `apps/devi_tarot/` — no route, only via iframe
- `apps/bandhu/` — not seeding wiki_engine or vector_memory
- Vocal engine (kokoro ONNX in `models/`) — not wired into om_engines
- `wiki/grahas/` — EN + SA duplicate pages (surya+sun, guru+jupiter etc.)
- `wiki/deity__*.md` flat files — not consolidated into subfolder
- `wiki/ragas/` and `wiki/talas/` — empty directories

---

## Key File Reference

| What | Where |
|------|-------|
| Entity types + relation grammar | `docs/reference/specs/ATLAS_ONTOLOGY_SCHEMA.md` |
| Four axes | `docs/reference/specs/atlas_axes.md` |
| Visual law | `docs/reference/specs/VISUAL_STANDARDS.md` |
| Live session map | `CLAUDE.md` |
| System status | `SYSTEM_MAP.md` |
| UI layout engine | `npu_engine/ui_vastu_engine.py` |
| Shell renderer | `static/js/shell.js`, `static/shell.html` |
| Flask API | `kernel.py` — port 5000 |
| Canonical graph | `datasets/relations/relations_resolved_canon.csv` |
| Sound spec | `docs/SOUND.md` |
| Personal data | `instance/personal/` (altar.json, natal.json) |

---

## What Claude Must Never Do

- Write to `datasets/relations/relations_resolved_canon.csv`
- Flatten the three authority axes
- Hardcode cosmological knowledge in JS/HTML (it comes from the field)
- Rename `npu_engine/`
- Add nodes without stability + authority metadata
- Assume a script or endpoint works without verifying
- Recompute layout in a renderer — `derive_ui_layout()` is the single source
- Use `npu_engine/om.py` — the canonical om is at root `om.py`
