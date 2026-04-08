---
name: atlas-state
description: >
  Instant orientation skill for the Coherence Atlas project. Use this skill at
  the start of ANY session involving Atlas development, research, scripting,
  graph work, wiki population, visualization, or philosophical/doctrinal writing.
  Also trigger when the user mentions: seeds, nakshatras, grahas, offering cycle,
  cycle runner, mandala, graph merge, canon, cosmology, jyotish, wiki pages,
  atlas pipeline, shrine, hexfield, city, bandhu, game, or any Atlas script by name.
  This skill prevents lost context, wrong assumptions about what's working, and
  repeated re-explanation. Read it before touching anything.
---

# Atlas State — April 2026

## What Atlas Is

Atlas Field Computer is a **local-first cosmological knowledge graph engine** running
as a Flask application on kanjira (Intel NPU, 30GB RAM, Gainesville FL, van life).
It is a coherence engine, research backend, and experiential game world simultaneously.

**The game is that you build Atlas.** Playing the game populates the knowledge graph.
The city grows from real engagement. Every quest improves a sub-layer.

---

## Hardware — kanjira

- Intel NPU (OpenVINO coherence scoring)
- Intel Iris Xe iGPU (WebGL/yantra/torus rendering)
- 30GB RAM
- PipeWire 1.2.6 — audio (pw-cat works, pw-jack broken for SC)
- MOTU M2 — USB audio interface
- Network: ngrok tunnel active

---

## Live System Check

```bash
./start.sh status

python3 -c "
from npu_engine.field.system_engine import derive_system_state
import json; d = derive_system_state()
print(d['session_summary'])
print('audio:', d['audio']['path'])
print('stable:', d['audio']['stable'])
"
```

---

## Repository: ~/atlas_330

```
kernel.py              Flask spine, 173 routes, port 5000
om.py                  Audio engine → pw-cat → MOTU M2
sc/atlas_mix.scd       OSC relay (sclang, no SC audio)
start.sh               System boot + control
drik_panchanga.py      Vedic panchanga calculator

npu_engine/            Computation layer (9 domain subdirectories)
  core/                datasets, graph_engine, build_field_state, vector_store
  geometry/            vastu_engine, igpu, yantra_engine, temple_geometry
  sound/               field_to_sound, tanpura_engine, sarangi_voice, bija_synth
  text/                codex_engine, reading_engine, composition_engine
  time/                trajectory_engine, goloka_engine, intention_engine
  nature/              s5_kernel, guild_engine, guild_planner, land_engine
  ui/                  mandala_schema, ui_vastu_engine
  game/                card_engine, generator
  system/              system_engine, code_engine, city_engine
  zones/               zone renderers (NE/N/NW/E/SE/S/SW/W/C)
  field/               (legacy path, re-exports still work)
  engines/             (legacy path, re-exports still work)

datasets/              136 CSVs, 7229 entities, 8466 edges
  astro/               nakshatra, tithi, graha tables
  vastu/               vastu geometry (from cosmology/ cleanup)
  ayurveda/            herbs, dosha, marma
  gandharva/           bija, sound theory
  plants/              guild relations (216), PFAF, nakshatra plants
  sound/               raga_master.csv (master for ALL traditions)
  symbols/             251 symbols from 6 sources
  cosmology/           goloka/, deity, festival (cleaned to 15 files)
  svarodaya/           Shiva Svarodaya breath science (NOT musical svaras)
  sources/             828 text files (Bhagavata, Brahma Samhita, etc.)
  system/              system_topology, code_topology, capability_map

static/
  shell.html           /shell — vastu grid mandala interface
  shell-cosmos.html    /cosmos — two-sphere instrument interface

apps/
  city/index.html      /apps/city/ — vastu city S6 portal
  hexed-ui-game/
    shrine.html        /shrine — Ta Prohm forest home (Bandhu's clearing)
  codex/               /codex — manuscript study
  guild/               /apps/guild/ — permaculture guild planner
  agriculture/         /apps/agriculture/ — nakshatra planting calendar
  vastu/               /apps/vastu/ — vastu analyzer
  bandhu/              /apps/bandhu/ — companion chat

hexfield/
  hexfield.py          pygame hex field game (1345 lines, complete)
  hex_projection.py    theta/phi → hex grid math

scripts/
  nakshatra_glyphs.py  27 nakshatra glyph generator (PDF)
  pfaf_lookup.py       PFAF plant database lookup
  session_open.py      Session start protocol
  session_close.py     Session end snapshot

instance/
  personal/
    natal.json         Birth chart (Jan 27 1983, 11:57am, Montreal)
    altar.json         Consecrated entities
  city/
    interactions.jsonl  Adaptive city interaction log
```

---

## What's Working (April 2026)

| System | Status |
|--------|--------|
| Sound: tanpura + sarangi + tabla + bija | ✓ pw-cat → MOTU |
| Mix: MixKernel → sclang → om.py | ✓ |
| Field: panchanga, nakshatra, tithi, hora | ✓ |
| Composition engine: /bandhu/chat → Narottama padas | ✓ no LLM |
| Goloka engine: ashtakala lila | ✓ populated |
| Reading engine: 5 lenses | ✓ |
| Trajectory engine: lunar arc + dasha | ✓ |
| Guild engine: 216 companion relations | ✓ |
| Land engine: vastu spatial planning | ✓ |
| Symbol engine: 251 symbols indexed | ✓ |
| City engine: vastu city S6 portal | ✓ |
| Shrine: Ta Prohm forest home | ✓ |
| Nakshatra glyphs: 27 designed | ✓ PDF generated |
| igpu.py: /render + /render/eternal | ✓ |
| Hexfield pygame: complete | ✓ |

---

## Audio Architecture

```
PRIMARY PATH (working):
  TanpuraEngine ──┐
  SarangiVoice  ──┤
  bija_synth    ──┼──→ om.py fill_buffer() → pw-cat → PipeWire → MOTU M2
  tabla_sampler ──┘

MIX CONTROL (working):
  MixKernel → OSC 57121 → sclang atlas_mix.scd → OSC 57122 → om.py

SC AUDIO: SILENT — pw-jack/PW 1.2.6 incompatibility
  sclang runs as OSC relay only (no scsynth needed)
  DO NOT use pw-jack jack_connect
  DO use pw-link for SC port connections

OLLAMA: port 11434, qwen3:8b, CPU only (~130s/prompt)
  /bandhu/chat defaults to use_llm=False
  Graceful fallback — tradition speaks directly
```

---

## Key Endpoints

| Route | Returns |
|-------|---------|
| GET /field | Full panchanga + field state |
| GET /spine | Unified: panchanga + entities + layers + sound |
| GET /render | 64 iGPU nodes with x,y for SVG cosmos |
| GET /render/eternal | Eternal cosmology sphere |
| GET /goloka | Ashtakala lila state |
| GET /trajectory | Lunar arc + dasha context |
| GET /guild/state | Permaculture guild companions |
| GET /guild/plan/current | Full guild plan from PFAF data |
| GET /land | Vastu spatial planning |
| GET /city/state | Vastu city hex grid |
| GET /city/gate/<dir> | Gate inscription |
| POST /city/interact | Log district interaction |
| POST /bandhu/chat | Composition engine response |
| POST /reading | Oracle reading (5 lenses) |
| GET /symbol/<emoji> | Symbol Vedic metadata |
| GET /symbols/field | Field-coherent symbols |
| GET /system/state | Hardware + audio snapshot |
| GET /shell | shell.html |
| GET /cosmos | shell-cosmos.html |
| GET /shrine | shrine.html |
| GET /apps/city/ | City hex grid |

---

## Datasets Wired (April 2026)

```
goloka/ashtakala_lila.csv      → goloka_engine ✓
goloka/sakhi_seva.csv          → goloka_engine ✓
marma/body_region_marma.csv    → body_engine ✓
carnatic/*.csv                 → rhythm/graph_seed_data ✓
compositions/narottama_padas.csv → composition_engine ✓
chandas/metres_forms.csv       → composition_engine ✓
plants/guild_relations.csv     → guild_engine ✓ (216 rows)
symbols/emoji_vedic_map.csv    → symbol_engine ✓ (105 emoji)
symbols/symbol_master.csv      → symbol_engine ✓
```

---

## Pending / Not Yet Built

```
figure_renderer.py     Bandhu SVG from talamana proportions
plant_renderer.py      L-system trees (field-scored)
Ring engine            Not built
4D projection          Designed, not built
Vocal SynthDef         1154 lines waiting, SC audio silent
Systemd services       Scripts ready at scripts/install_services.sh
Qwen3 NPU inference    Too slow on CPU
Whisper NPU            ~4h install
datasets/game/         lineages, chimera, sacred objects (designed)
npu_engine/game/       lineage_engine, character_engine (designed)
```

---

## S-Layer System

| Layer | Name | Domain | Terrain |
|-------|------|--------|---------|
| S0 | Bindu | Goloka · ashtakala · eternal cosmology | void |
| S1 | Archetype | 15 Nitya Devis · 9 Grahas · deity governance | mountain |
| S2 | Sound | Raga · tala · shruti · bija · vocal | library |
| S3 | Rhythm | Panchanga · tithi · nakshatra · muhurta | river |
| S4 | Geometry | Vastu · yantra · 108 pada · torus knot | crystal |
| S5 | Nature | Ayurveda · plant wheel · dosha · marma | forest |
| S6 | Lila | Practice · codex · altar · city · game | village |

---

## Vastu City — S6 Portal

```
Angkor Wat layout — concentric rectangular enclosures
Moat = W/Varuna ring of hexes
5-tower quincunx = brahmasthana + 4 cardinals
9 districts = 9 vastu zones

C  Brahma    → /reading/bandhu  (oracle, brahmasthana)
N  Kubera    → /apps/kala/      (calendar, treasury)
NE Ishana    → /codex           (temple, learning)
E  Indra     → /apps/wiki/      (market, knowledge)
SE Agni      → /practice/       (forge, action)
S  Yama      → /body/           (boundary, marma)
SW Nirriti   → /apps/guild/     (forest, plants)
W  Varuna    → /journal/        (river, reflection)
NW Vayu      → /apps/bandhu/    (wind, conversation)

Adaptive: high engagement → district expands
          low engagement  → overgrown (opacity 0.15)
Interaction log: instance/city/interactions.jsonl
```

---

## Natal Chart (inahd)

```
Jan 27 1983 · 11:57am · Montreal QC
Lagna: Vrshabha (Taurus) · Rohini pada 1
Sun:   Capricorn / Shravana
Moon:  Gemini / Punarvasu
Mars:  Aquarius / Shatabhisha
Mercury: Sagittarius / Purvashadha
Jupiter: Scorpio / Anuradha
Venus: Aquarius / Dhanishtha
Saturn: Libra / Svati (EXALTED)
Rahu:  Gemini / Ardra (R)
Ketu:  Sagittarius / Mula (R)
Dasha: Mercury · closes Oct 2027
Chart: instance/personal/natal.json
```

---

## Session Protocol

```bash
1. Read CLAUDE.md
2. ./start.sh status
3. python3 -c "
   from npu_engine.field.system_engine import derive_system_state
   import json; d = derive_system_state()
   print(d['session_summary'])
   "
4. Work — commit with ✦ prefix
5. python3 scripts/session_close.py
```

---

## Do Not Touch

- `datasets/relations/relations_resolved_canon.csv` — canonical edges
- `npu_engine/` — do not rename (package name hardcoded everywhere)
- Running kernel.py — don't restart without asking
- Running om.py / pw-cat — don't kill without asking
- `instance/personal/` — personal data

---

## Known Fragile Points

- `kernel.py` GET /yantra defined twice (~line 4704 + ~8019)
- `kernel.py` create_app() is 4600+ lines — precise line targeting
- SC→MOTU via pw-jack — connections appear but audio silent
- Both import paths work: `npu_engine.graph_engine` AND
  `npu_engine.core.graph_engine` — re-export layer, not file moves

---

## Supabase

Project: `oxskujpofiipoeifcfnm` · us-east-1
URL: `https://oxskujpofiipoeifcfnm.supabase.co`
