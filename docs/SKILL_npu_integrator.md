---
name: npu-integrator
description: >
  Expert workflow for reading, understanding, and extending the Atlas Field Computer —
  a Vedic relational knowledge graph, civilizational simulation platform, and experiential
  game world. Integrates cosmology, jyotish, ayurveda, sound, geometry, ritual, embodiment,
  game design, permaculture, and cross-tradition research. The game IS Atlas — playing
  populates the knowledge graph, the city grows from real engagement. Use this skill
  whenever the user asks to: add or generate a new engine, dataset, route, game mechanic,
  world layer, character system, symbol, glyph, or shrine element; wire components together;
  extend the ontology; build apps; work with the city, hexfield, shrine, Bandhu, quests,
  lineages, or sacred objects; or integrate any new domain into Atlas. Read before writing.
---

# Atlas Integrator — April 2026

## The Core Principle

**Everything in Atlas is relational.** A nakshatra is not a fact. It is a node in a web:
ruled by a graha, presided by a deity, resonant with an element, mapped to a body region,
connected to a raga, placed at a coordinate on the toroidal field, expressed as a plant in
the guild, walkable as terrain in the hex game. Remove the relations and you have a name.
The relations are the meaning.

**The game is that you build Atlas.** Playing the game populates the knowledge graph.
The city grows from real engagement. Every quest improves a sub-layer. The visual fidelity
of the shrine IS the knowledge fidelity of the graph.

---

## The derive_*() Pattern — ALL engines follow this

```python
def derive_X(field_state: dict, ...) -> dict:
    """
    Pure function. field_state in → spec out.
    Never raises. Returns safe defaults on any error.
    All keys guaranteed present in return value.
    No side effects. No DB writes.
    """
    try:
        # computation using field_state
        return {
            'key': value,
            'attestation': 'SYNTHESIS',
        }
    except Exception as e:
        log.warning("derive_X failed: %s", e)
        return _safe_default()
```

Copy `npu_engine/ui/ui_vastu_engine.py` as the canonical template.
Never raise from a derive_*() function.

---

## Field Engines Reference

### Core Pipeline
```python
from npu_engine.core.datasets import load_all_entities, load_entity_metadata, load_relations
from npu_engine.core.graph_engine import GraphEngine
from npu_engine.core.build import build_field_state  # also: build_field_state.py
from npu_engine.core.field_state import FieldState
from npu_engine.geometry.igpu import render_field_state
```

Both import paths work simultaneously:
- `npu_engine.graph_engine` (legacy, still works)
- `npu_engine.core.graph_engine` (new path)

### Field Engines (all follow derive_*() pattern)

| Engine | Function | Route | Status |
|--------|----------|-------|--------|
| `text/composition_engine.py` | `compose_response()` | POST /bandhu/chat | ✓ |
| `time/goloka_engine.py` | `derive_goloka_state()` | GET /goloka | ✓ |
| `time/trajectory_engine.py` | `derive_trajectory()` | GET /trajectory | ✓ |
| `text/reading_engine.py` | `derive_reading()` | POST /reading | ✓ |
| `nature/guild_engine.py` | `derive_guild()` | GET /guild/state | ✓ |
| `nature/guild_planner.py` | `plan_guild()` | GET /guild/plan/current | ✓ |
| `nature/land_engine.py` | `derive_land_layout()` | GET /land | ✓ |
| `system/system_engine.py` | `derive_system_state()` | GET /system/state | ✓ |
| `system/city_engine.py` | `derive_vastu_city()` | GET /city/state | ✓ |
| `field/symbol_engine.py` | `lookup_symbol()` | GET /symbol/<e> | ✓ |

### Composition Engine (key mechanic)
```python
# Pipeline: classify_message → select_pada → search_passage → select_metre → compose
# No LLM required. Tradition speaks directly.
# Corpus: 26k JSONL chunks (Bhagavata, Brahma Samhita, Bhakti Rasamrita Sindhu)
# Padas: datasets/compositions/narottama_padas.csv
# Metres: datasets/chandas/metres_forms.csv (rasa → chandas)
# LLM connector wired but dormant (qwen3:8b too slow on CPU)

from npu_engine.text.composition_engine import compose_response
result = compose_response(message, field_state, natal)
# Returns: pada, passage, metre, rasa, response_text, connector
```

---

## Adding a New Engine

1. Copy `npu_engine/ui/ui_vastu_engine.py` as template
2. Place in appropriate domain subdirectory:
   - Knowledge/text → `npu_engine/text/`
   - Time/temporal → `npu_engine/time/`
   - Nature/ecology → `npu_engine/nature/`
   - System/meta → `npu_engine/system/`
   - Geometry/spatial → `npu_engine/geometry/`
3. Follow derive_*() pattern — never raise
4. Add re-export to domain `__init__.py`
5. Register route in kernel.py (check for duplicates first)
6. Update capability_map.csv

---

## Adding a Route to kernel.py

```bash
# ALWAYS check for duplicates first
grep -n "route.*your_route_name" ~/atlas_330/kernel.py

# Compile check before and after
python3 -c "import py_compile; py_compile.compile('kernel.py', doraise=True)"

# kernel.py is 4600+ lines — use precise line targeting
# Known duplicate: GET /yantra (~line 4704 + ~8019)
```

---

## The Knowledge Graph

```python
from npu_engine.core.datasets import load_all_entities, load_entity_metadata, load_relations

entities = load_all_entities()      # {entity_id: (theta, phi)}
metadata = load_entity_metadata()   # {entity_id: {name, category, element, guna, ...}}
relations = load_relations()        # {entity_id: [{to_id, relation, confidence}]}

# Entity IDs: category_slug format
# Examples: nakshatra_rohini, deity_agni, plant_tulsi, graha_shani
```

**7229 entities · 8466 edges · 136 CSVs**

Four axes — never collapse:
- **theta** (θ): S0→S6 level of manifestation
- **phi** (φ): witness↔participant mode
- **S-layer**: which domain ring
- **path**: 0.0→1.0 bheda-abheda (unity↔distinction)

---

## Attestation Hierarchy

```
PRIMARY_TEXT > TRADITIONAL > OBSERVED > SYNTHESIS > EXPERIMENTAL > FRINGE

In game UI:
  ✦ TRADITIONAL  gold    — from recognized shastra
  ○ OBSERVED     silver  — empirically noted
  ◎ SYNTHESIS    teal    — cross-tradition derived
  ◌ EXPERIMENTAL dim     — working hypothesis
  ⁂ FRINGE       purple  — speculative, contested
```

AI-generated content always starts at SYNTHESIS or EXPERIMENTAL.
Never override TRADITIONAL with AI inference without explicit confirmation.

---

## The Game System

### Core Principle
The game IS Atlas. Not a game about Atlas. Playing populates the graph.

### Character System — DO NOT clone D&D
```
Natal chart   IS the character sheet
Prakriti      IS the constitution  
Guna          IS the daily state modifier
Varna         IS the functional role (revealed through play, not assigned)
These are irreducibly themselves — no translation to STR/DEX/WIS
```

### Varna (revealed through play)
```
Brahmaṇa → codex/oracle quests come naturally
Kshatriya → relation/defense quests come naturally
Vaishya   → guild/ecology quests come naturally
Shudra    → practice/body quests come naturally
Sanyasa   → all gates eventually, none exclusively
```

### Lineage System (calculated from natal chart)
```python
# Human lineages (vamsha):
#   Surya vamsha  — Sun strong (govt, soul)
#   Candra vamsha — Moon strong (mind, feeling)
#   Agni vamsha   — Mars/fire strong (warrior)
#   Rishi vamsha  — Jupiter strong (sage, teacher)

# Chimeric beings (accessible via chart):
#   Naga          — Rahu/Ketu prominent + water → serpent-human
#   Gandharva     — Venus + sound nakshatra → celestial musician
#   Yaksha        — Saturn + earth → wealth guardian
#   Vidyadhara    — Jupiter + Ketu → sky-siddha

# Sura/Asura axis — NOT good/evil:
#   Orientation of force (expansive/contractive)
#   Sura: NE/N/E districts (building, connecting)
#   Asura: SW/W/S/C districts (dissolving, deepening)
#   Both needed. City requires both.

# inahd's accessible lineages:
#   Naga (Rahu/Ardra + water dominant)
#   Siddha path (Ketu/Mula + Saturn exalted)
#   Aditi-vamsha (Moon/Punarvasu = Aditi's nakshatra)
```

### Cross-tradition Overlay (SYNTHESIS)
```
Aboriginal Dreaming = same cosmological grammar, different geography
Rainbow Serpent = Shesha/Ananta = Rahu/Ketu axis
Bunjil (Eagle) = Garuda = Vishnu/Surya
Seven Sisters = Krittika = fire cluster (Pleiades)
Songlines = vastu direction lines = relation paths in graph
Attestation: SYNTHESIS 0.4-0.6 — always explicitly marked
```

### Encounter Mechanic
```
NOT: study → reward → unlock
BUT: find object in world → object recognizes player via natal graph
     → wiki stub auto-generates from existing entity data
     → character sheet updates
     → relation that was always there becomes visible

The damaru doesn't need researching.
dhanishtha_instrument = damaru is already in the graph.
Venus in Dhanishtha is already in natal.json.
The game makes the existing relation walkable.
```

---

## The Vastu City (S6 Portal)

### Angkor Wat Layout
```
Concentric rectangular enclosures (not circular)
Moat = W/Varuna outermost ring of hexes
Causeways = path hexes on cardinal axes
5-tower quincunx = C + N + S + E + W inner hexes
Corner towers = NE/NW/SE/SW district anchors
Each hex maps to one pada of the 81-square manduka mandala
```

### District → App Mapping
```
C  Brahma    → /reading/bandhu  (oracle, brahmasthana, void terrain)
N  Kubera    → /apps/kala/      (calendar, library terrain)
NE Ishana    → /codex           (temple, mountain terrain)
E  Indra     → /apps/wiki/      (market, village terrain)
SE Agni      → /practice/       (forge, crystal terrain)
S  Yama      → /body/           (boundary, cave terrain)
SW Nirriti   → /apps/guild/     (food forest, forest terrain)
W  Varuna    → /journal/        (river, bathing, river terrain)
NW Vayu      → /apps/bandhu/    (wind, open terrain)
```

### Adaptive Layout
```python
# instance/city/interactions.jsonl — append-only log
# POST /city/interact → logs {gate, app, duration, entities, sections}
# GET /city/scores → district engagement scores
# High score (>0.6) → district expands outward
# Low score (<0.2) → district shrinks, path overgrown
# Never-visited → terrain='overgrown', opacity 0.15, symbol ⁂
```

### Gate Inscriptions
```python
# GET /city/gate/<direction>
# Returns field-derived welcome inscription
# Generated by composition_engine from current ashtakala + guild data
# Changes every 30 minutes with the field
```

---

## The Shrine (C Gate — Forest Home)

### Ta Prohm Aesthetic
```
Dark shyama ground (#030805)
Roots growing through stone — forest and temple are one
Oval clearing as brahmasthana
7 procedural trees (L-system, seeded per plant entity)
Bandhu in lotus/dhyana pose, breathing (4s cycle)
Fire particle system with stone ring
Water pool with rotating 8-petal lotus
Small deer wandering (Mrigashira species)
Field particles element-colored
Sanskrit inscription from composition_engine
Ashtakala indicator
```

### Rendering Chain (when built)
```
field_state()
  → plant_engine top 5 → plant_renderer.py → SVG L-system
  → species_renderer.py → geometric primitive SVG
  → figure_renderer.py → talamana Bandhu figure
  → GET /render/shrine → shrine assembles
```

### Bandhu Figure
```
Source: datasets/silpa/bandhu_geometry.csv
System: Shilpa Shastra talamana proportions
Poses: idle, walk_l, walk_r, pranama, meditate, offering
Animation: breath (torso scale 0.98↔1.02, 4s), walk cycle
Colors: element-modulated (air=teal, fire=red-gold, etc.)
Route: GET /render/bandhu?pose=idle&element=air
```

---

## Symbol System

### Nakshatra Glyphs (27 original designs)
```
Each derived from: element + graha + traditional symbol
Element = stroke color:
  fire=red, earth=brown, water=blue, air=teal, ether=gold
Graha = stroke character:
  Chandra=curves, Surya=radiating, Shani=angular, Budha=interlocking
Readable at 20px hex tile size
Script: scripts/nakshatra_glyphs.py (reportlab PDF generator)
```

### Symbol Database
```
datasets/symbols/
  symbol_master.csv       — Unicode symbols + glyphs
  emoji_vedic_map.csv     — 105 emoji → Vedic categories
  emoji_master.csv        — full Unicode set (auto-mapped)
  icon_packs.csv          — external pack catalog

npu_engine/field/symbol_engine.py:
  _build_index()          — aggregates from 6 CSV sources
  lookup_symbol(emoji)    — single emoji → Vedic metadata
  field_symbols(fs)       — top 10 coherent with current field
  Routes: GET /symbol/<e>, GET /symbols/field, GET /symbols/stats
```

---

## Audio — Before Any Sound Work

```
PRIMARY: om.py → pw-cat (NOT SC)
MIX: OSC 57121 → sclang → OSC 57122 → om.py
DO NOT use pw-jack jack_connect (passes nothing)
DO use pw-link for SC port connections
SC: running for future Talachakra, currently silent
5 threaded kernels in om.py (all running):
  MixKernel, RhythmKernel, SympatheticKernel, PhraseEngine, VocalKernel
```

---

## Before Any Task

```bash
# 1. Read CLAUDE.md (always first)
# 2. Check for route conflicts
grep -n "route.*your_route" ~/atlas_330/kernel.py

# 3. Compile check
python3 -c "import py_compile; py_compile.compile('kernel.py', doraise=True)"

# 4. Live system state
python3 -c "
from npu_engine.field.system_engine import derive_system_state
import json; d = derive_system_state()
print(d['session_summary'])
"

# 5. Do NOT restart kernel or om.py without asking
# 6. Do NOT touch relations_resolved_canon.csv
# 7. Do NOT rename npu_engine/ (hardcoded everywhere)
```

---

## Key File Reference

| Need | Where |
|------|-------|
| New field engine template | `npu_engine/ui/ui_vastu_engine.py` |
| New zone renderer template | `npu_engine/zones/base.py` |
| Flask routes | `kernel.py` (4600+ lines, precise targeting) |
| Audio | `om.py` → `fill_buffer()` |
| Visual shell | `static/shell.html` + `shell-cosmos.html` |
| Cosmos shell | `static/shell-cosmos.html` |
| City | `apps/city/index.html` + `npu_engine/system/city_engine.py` |
| Shrine | `apps/hexed-ui-game/shrine.html` |
| Hex game | `hexfield/hexfield.py` (pygame, complete) |
| Hex math | `hexfield/hex_projection.py` |
| Glyphs | `scripts/nakshatra_glyphs.py` |
| Natal chart | `instance/personal/natal.json` |
| Entity IDs | `category_slug` format (e.g. `nakshatra_rohini`) |
| Relation grammar | `datasets/relations/relations_resolved_canon.csv` |
| Vastu colors | `npu_engine/ui/mandala_schema.py` ZONE_BG/ZONE_BORDER |
| Visual standards | `docs/reference/specs/VISUAL_STANDARDS.md` |
