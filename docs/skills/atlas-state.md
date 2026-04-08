---
name: atlas-state
description: >
  Instant orientation skill for the Coherence Atlas project. Use this skill at
  the start of ANY session involving Atlas development, research, scripting,
  graph work, wiki population, visualization, or philosophical/doctrinal writing.
  Also trigger when the user mentions: seeds, nakshatras, grahas, offering cycle,
  cycle runner, mandala, graph merge, canon, cosmology, jyotish, wiki pages,
  atlas pipeline, or any Atlas script by name. This skill prevents lost context,
  wrong assumptions about what's working, and repeated re-explanation. Read it
  before touching anything.
---

# Atlas State Skill

## What Atlas Is

Coherence Atlas is a **local-first cosmological knowledge graph engine** for
organizing Vedic and related traditional knowledge into a structured relational
system. It runs on **kanjira** — an Intel NPU machine in a van in Gainesville FL.

The system mirrors the Guru–Sadhu–Shastra epistemic model:
- **Shastra** = canonical datasets and textual passages (the kernel)
- **Sadhu** = overlays, annotations, practitioner interpretation
- **Guru** = AI-assisted synthesis and inference (never overrides canon)

The guiding principle: **resonance over accumulation**.

---

## Repository Structure (canonical — updated April 2026)

```
atlas_330/
  kernel.py             Flask spine — port 5000
  om.py                 Tanpura drone — always running
  drik_panchanga.py     Vedic panchanga (Swiss Ephemeris)
  start.sh              System boot/control script
  CLAUDE.md             Session map — read first every session

  npu_engine/           Reasoning layer — DO NOT RENAME
    datasets.py         Loads all CSVs → 3400-node graph
    graph_engine.py     Canonical relation graph
    build_field_state.py  FieldState construction
    field_state.py      FieldState namedtuple
    field_layers.py     S0–S6 layer mapping
    field_to_sound.py   Nakshatra → graha → raga descent chain
    mandala_schema.py   Vastu mandala zone resolver
    tanpura_field.py    Field → tanpura tuning
    phrase_engine.py    Live raga graph traversal → note events
    bija_synth.py       Formant bija mantra synthesis
    s5_kernel.py        Plant wheel (3 rings)
    toroidal_field.py   Torus coordinates
    torus_queries.py    108-pada torus knot queries
    mix/                11-layer mix graph → OSC
    rhythm/             Tala/theka/tihai/layakari → OSC
    sympathetic/        13 taraf strings → OSC

  datasets/             Canonical data — DO NOT MODIFY contents
    relations/          Graph edges
      relations_resolved_canon.csv   ← SACRED — never overwrite
    sources/            Sanskrit/English texts + JSONL chunks
    cosmology/          27 nakshatras, 9 grahas, 15 devis, 12 rashis
    ayurveda/           704 herbs, dosha matrix
    plants/             Nakshatra plants, agriculture calendar
    carnatic/           Talas, ragas, kritis
    astro/              Tithi, nakshatra tables

  apps/                 12 web apps (served by kernel)
    agriculture/        Nakshatra planting calendar (PWA)
    archana/            Devi worship
    bandhu/             Companion chat
    codex/              Sacred manuscript study
    devi_tarot/         Card spread
    ecology/            Plant ecology dashboard
    guild/              Companion planting
    lila/               Coherence game
    research/           Query + synthesis
    vastu/              Vastu analyzer
    wiki/               Entity browser
    yantra/             Sri Yantra topology

  static/               Visual surface
    shell.html          THE interface — served at /shell
    atlas.html          Legacy — served at / (should redirect to /shell)
    css/shell.css       Canonical styles
    js/                 shell.js, ui.js, s1_layer.js, cosmos_nav.js, etc.
    audio/tabla/        Tabla WAV samples

  sc/                   SuperCollider
    atlas_synth.scd     SynthDefs — loaded by start_sc.sh
    atlas_mix.scd       Mix engine
    start_sc.sh         SC boot (pw-jack + MOTU M2)

  scripts/              Pipeline scripts
  instance/             Personal data (altar.json, natal.json, vector_store/)
  wiki/                 Entity wiki pages (subdirectory structure)
    nakshatras/         27 nakshatra pages (clean — use these)
    grahas/             Graha pages (has EN+SA duplicates — needs cleanup)
    devis/              15 Nitya Devi pages
    music/ragas/        14 raga pages
    kalas/              64 kala entries
    cosmos/             Cosmological docs
    gaudiya/            Gaudiya lineage docs
    sakhis/             8 sakhi pages
    deity__*.md         Flat deity pages (not yet consolidated into subdir)
    tithi__*.md         4 tithi pages (flat)
  docs/                 Architecture, specs, research
    reference/specs/    VISUAL_STANDARDS.md, atlas_axes.md, etc.
  models/               kokoro-v1.0.onnx (TTS — not yet wired)
  systemd/              Service files
  purana/               Archive — relics and experiments
  tests/                Test suite
  vyakti/               Symlinks → instance/personal/
```

**What is NOT here anymore (cleaned April 2026):**
- `kosha/`, `karma/`, `kshetra/`, `mandala/`, `nada/` — Sanskrit symlink trees removed
- Root `atlas_synth.scd`, `atlas_mix.scd` — duplicates archived, canonical in `sc/`
- `npu_engine/om.py` — archived (root `om.py` is canonical)
- Garbage files (`=12,`, `for`, `import`, `datasets.zip`, `kernel.py.bak`)

---

## Four Axes (never collapse these)

| Axis | Range | Meaning |
|------|-------|---------|
| **theta** (θ) | S0→S6 | Level of manifestation |
| **phi** (φ) | witness↔participant | Mode of engagement |
| **S-layer** | S0–S6 | Which domain ring |
| **path** | 0.0→1.0 | Bheda-abheda (unity↔distinction) |

---

## S0–S6 Layer System

| Layer | Name | Domain |
|-------|------|--------|
| S0 | Bindu | Goloka · acintya · source · ashtakala |
| S1 | Archetype | 15 Nitya Devis · 9 Grahas · deity governance |
| S2 | Sound | Raga · tala · shruti · bija · vocal |
| S3 | Rhythm | Panchanga · tithi · nakshatra · muhurta |
| S4 | Geometry | Vastu · yantra · 108 pada · torus knot |
| S5 | Nature | Ayurveda · plant wheel · dosha · marma |
| S6 | Lila | Practice · codex · altar · lila maps |

---

## Three Authority Axes (always preserve independently)

1. **Stability**: `stable` / `working` / `experimental`
2. **Authority**: `shastra` / `sadhu` / `guru`
3. **Visualization permission**: `relation` / `analytic` / `symbolic` / `canonical`

AI inference always starts at `experimental / guru`. Never skips `guard_canon.py`.

---

## Live Endpoints

| Route | Method | Returns |
|-------|--------|---------|
| `/field` | GET | Full panchanga + field state |
| `/spine` | GET | Unified field: panchanga + entities + layers |
| `/shell/state` | GET | Resolved mandala zones |
| `/observe` | POST | Deep entity dive |
| `/attend` | POST | Subtle mix nudge |
| `/render` | GET | 64 iGPU nodes for SVG cosmos |
| `/s5` | GET | Plant wheel state |
| `/shell` | GET | Serves static/shell.html |

---

## Known State (April 2026)

**Graph**: ~3400 nodes, ~4000+ edges across 19 entity types

**Wiki pages**: Subdirectory structure is canonical:
- `wiki/nakshatras/` — 27 pages ✓
- `wiki/grahas/` — has EN+SA duplicates (surya+sun, guru+jupiter etc.) — needs dedup
- `wiki/devis/` — 15 pages ✓
- `wiki/deity__*.md` flat files — not yet consolidated into subfolder
- `wiki/ragas/` and `wiki/talas/` — empty directories (gap)

**Sound**: om.py stuck on ALSA device 9 (spdif) — PipeWire won't open it.
SC is the audio path. om.py needs `run_sounddevice` to return `False` on
failure so it falls through to `run_pwcat`. Fix pending.

**Known open issues**:
- `/` serves legacy `atlas.html` — should redirect to `/shell`
- `apps/devi_tarot/` has no route
- Vocal engine (kokoro ONNX) not wired
- `wiki/grahas/` has EN/SA duplicates

---

## Session Startup Protocol

1. Read `CLAUDE.md` (it's the live session map)
2. Read `docs/reference/specs/VISUAL_STANDARDS.md` before any CSS/SVG
3. Identify session type: scripting / graph / wiki / sound / visual / philosophy
4. Check what's running: `./start.sh status`
5. Flag canonical safety: new relations need stability + authority metadata
6. Commit with `✦` prefix

## What Claude Should Never Do

- Override `datasets/relations/relations_resolved_canon.csv`
- Flatten the four axes
- Add nodes without entity type and stability metadata
- Rename `npu_engine/`
- Assume scripts work without verifying
- Treat wiki page shells as populated content
