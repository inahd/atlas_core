# S-Layer Pages — Current State

April 21, 2026 | Analysis from code reading + live API testing

---

## Overview

7 pages (s0.html through s6.html) served at `/s0` through `/s6`. All share:
- atlas-theme.css (CSS vars)
- atlas.js (atlasGet helper)
- interaction_engine.js (click-to-detail system)
- Footer bar with panchanga strip (nakshatra, tithi, vara, devi)
- Right-side nav dots linking between layers
- 60-second auto-refresh interval

Each page fetches `/field` for panchanga data and `/layer/sN/compose` for
layer-specific content assembled by the layer_composer engine.

---

## S0 · Goloka (7.6K, 175 lines)

**Layout:** Single centered card. Minimalist, meditative.

**Data sources:** `/goloka`, `/field`, `/resonance`, `/layer/s0/compose`

**Sections present (from API + code):**
1. Ashtakala period name + approximate time
2. Active forest name + lila description
3. Presiding sakhi name (colored by devi)
4. Devi block: bija mantra, name (IAST + Devanagari), description
5. Narottama pada (devotional verse from compositions corpus)
6. Pratibimba coherence bar (bridge_to_material score)
7. Vaishnava tattva line (top 3 from layer compose)
8. Temple stream link (if live)

**What shows data:** All 8 sections populate from live endpoints. The devi
block pulls from both `/goloka` (nitya_devi) and layer_composer raw_data
(nitya_devi_master.csv) for richer detail.

**What's clickable:** Passages have `data-passage` and `data-source` attributes
for the interaction_engine click-to-detail system. Temple stream is a link.

**Rendering quality:** Background gradient uses devi color. Clean, focused.
No images/SVG — text only.

**Issues:**
- `/layer/s0/compose` returns 0 sections (the layer_composer doesn't have
  an S0 assembler; data comes directly from `/goloka`). The `lc` fetch is
  wasted but doesn't break anything.
- `/resonance` endpoint may return empty if no temple streams are configured.

---

## S1 · Archetype (13K, 243 lines)

**Layout:** Three-column. Left: panchanga + sound. Center: devi + deity +
yantra + scripture. Right: raga + graha deity + domains + devi metadata.

**Data sources:** `/field`, `/layer/s1/compose`, `/sound/state`,
`/corpus/search?q=Nitya+Devi+eternal`

**Sections present (from API: 3 sections from layer_composer):**
1. NITYA DEVI — name, color, color_meaning
2. NAKSHATRA DEITY — deity name, nakshatra, rasa, tattva, weapons (array),
   vahana, mudra, body/garment colors, direction, gemstone, metal, time, bija,
   shakti
3. GRAHA BIJA — graha-specific bija mantras

**What shows data (verified from code):**

- **Left column:** Nakshatra + deity + shakti, tithi + paksha, vara, element +
  guna, raga name + tala + bpm, Sa frequency, graha bija list, hora lord,
  rahu kala window. All populate from `/field` and `/sound/state`.

- **Center column:**
  - Devi name (IAST) — from NITYA DEVI section or raw nitya_devi_master
  - Devi name (Devanagari) — from raw_data.nitya_devi_master.name_devanagari
  - Devi description — from raw_data or section
  - Bija mantra (large teal text) — from raw_data.bija
  - Short mantra — from raw_data.mantra_short
  - Nakshatra deity name + nakshatra + rasa + tattva
  - **Weapons list** — YES, displayed. Pulled from deitySec.weapons array.
    Each weapon is a clickable `<span>` with `data-entity-id` for the
    interaction engine.
  - Deity attributes grid: vahana, mudra, body color, garment color, direction,
    gemstone, metal, day, time, bija, shakti
  - **Yantra SVG** — YES, rendered. `buildDeviYantra(color, 140)` draws:
    outer square bhupura, 4 gate T-shapes, inner circle, upward triangle,
    central bindu (double circle). Colored by devi color_hex.
  - **Devi weapons_full** — YES, displayed below yantra. Full weapon text
    from raw_data.weapons_full (e.g., "sugarcane bow, flowery arrows,
    ankusha, pasha").
  - Corpus passage — from `/corpus/search`, shows first result text + source.

- **Right column:** Raga name + vadi/samvadi + rasa + time + Sa Hz. Graha
  deity name + domain + element + weapon + vahana. Deity domains list. Vahana
  symbolism. Devi metadata: element, guna, rasa, graha, shakti,
  capability_signature.

**What's clickable:** Weapons (data-entity-id), passages (data-passage +
data-source). Both wire to interaction_engine.js modal system.

**Rendering quality:** This is the richest S-layer page. Three-column layout
with full devi + deity data. The yantra is a simple geometric SVG (bhupura +
circle + triangle + bindu), not the elaborate Chladni form from s4-bloom.
Devi color pervades the design.

**Issues:**
- The yantra SVG is generic (same for all 15 devis — outer square, circle,
  triangle, bindu). It doesn't use the per-devi geometry from
  nitya_yantra_geometry.csv (triangle count, orientation, petal count vary).
- Capability_signature (CUT, BIND, BURN/PURIFY, etc.) shows as raw text.
  Could be rendered as badges.
- No devi iconography images (only the geometric yantra SVG).

---

## S2 · Sound (14.5K, 292 lines)

**Layout:** Three-column. Left: raga details. Center: tala/rhythm. Right:
chandas/metre.

**Data sources:** `/field`, `/layer/s2/compose`, `/sound/state`,
`/rhythm/theka`, `/chandas`

**Sections present (from API: 0 sections from layer_composer):**
The S2 layer_composer returns 0 sections. All data comes from the direct
endpoint fetches.

**What shows data:**
- Raga name, time, rasa, aroha/avaroha (ascending/descending scales)
- Tala name, matra count, theka pattern
- Chandas (metre): name, pattern, rasa match
- Sound state: mode, Sa Hz, bpm, layers active

**What's clickable:** Limited — no interaction_engine integration visible.

**Issues:**
- Layer composer returns 0 sections for S2. The page works because it fetches
  data directly from /sound/state, /rhythm/theka, /chandas. But it doesn't
  benefit from the layer_composer's dataset cross-referencing.
- No SVG or visual elements. Text-only.

---

## S3 · Kala (12K, 316 lines)

**Layout:** Two-column + top bar. Top: tithi arc + approach events.
Left: panchanga details + trajectory. Right: svarodaya + dinacharya.

**Data sources:** `/field`, `/layer/s3/compose`, `/trajectory`, `/svarodaya`,
`/dinacharya`, `/chandas`

**Sections present (from API: 4 sections):**
1. NAKSHATRA — nakshatra details
2. TITHI — tithi details
3. NAKSHATRA DEITY PROFILE — deity extended attributes
4. NITYA DEVI — devi mapping

**What shows data:**
- Tithi phase arc (visual position in lunar cycle)
- Approaching events (Ekadashi, Purnima, Amavasya)
- Trajectory: coming from / moving toward / dasha context
- Svarodaya: active nostril, breath rhythm
- Dinacharya: daily routine recommendations
- Nakshatra + tithi details from layer_composer

**What's clickable:** Minimal click interaction.

**Issues:**
- The tithi arc is computed client-side from tidx/30 — correct but simple.
- No integration with the jyotisha engine's compute_tithi (which has the
  null devi fields). Still uses the kernel's calc_panchanga data.

---

## S4 · Geometry (10K, 187 lines)

**Layout:** Vastu-inspired grid. Center: compass rose. Grid: 9 vastu
zone cells. Info panel.

**Data sources:** `/field`, `/yantra/navagraha`

**Sections present (from API: 3 sections):**
1. ELEMENT GEOMETRY — element-based geometric forms
2. GEOMETRY ARCHETYPES — morphological archetypes
3. GRAHA AVATAR BPHS — avatar correspondences

**What shows data:**
- 3x3 vastu grid with zone names and direction labels
- Lo Shu compass rose (N/S/E/W with zone names)
- Navagraha yantra matrix data (from /yantra/navagraha)
- Layer composer sections rendered as text blocks

**What's clickable:** No click handlers (0 detected).

**Rendering quality:** Has SVG elements (compass directions, zone grid).
Most structurally visual of the S-layers after S1.

**Issues:**
- This is the simple S4 (10K). The elaborate s4-bloom.html (54K) with
  Chladni interference + tithi slider is unrouted.
- No integration with the wave field engine (compute_wave_field,
  compute_nakshatra_field). These were built later and haven't been
  wired back into S4.
- The layer_composer provides geometric data but the page renders it
  as text, not visual geometry.

---

## S5 · Bhumi (14K, 368 lines)

**Layout:** Single column, card-based sections.

**Data sources:** `/field`, `/layer/s5/compose`, `/astrobotany`

**Sections present (from API: 6 sections — the richest layer):**
1. DHATU HERB MATRIX — 7 dhatu × herb mappings
2. NAKSHATRA PLANTS — current nakshatra's associated plants
3. NAKSHATRA SPECIES — yoni animal species data
4. ABORIGINAL ANIMALS — indigenous species correspondences
5. ASANA CORE — yoga asana recommendations
6. NAKSHATRA BODY MAP — body region mapping

**What shows data:**
- Current nakshatra plant + properties
- Astrobotany: moon phase → agricultural activity
- Dhatu-herb correspondences
- Species/yoni data
- Body region from nakshatra
- Asana recommendations

**What's clickable:** Passages and entities via interaction_engine attributes.

**Issues:**
- 6 sections is the most content-rich layer. But the rendering is flat
  (card stack), not spatially organized like S1's three-column layout.
- No plant images or species illustrations.
- The guild engine data isn't pulled (no /guild/state fetch).

---

## S6 · Lila (10K, 203 lines)

**Layout:** Sectioned single column with `class="section"` blocks (9 found).

**Data sources:** `/field`, `/layer/s6/compose`, `/goloka`, `/sound/state`,
`/svarodaya`, `/dinacharya`, `/chandas`

**Sections present (from API: 0 sections from layer_composer):**
Layer_composer returns 0 sections for S6. Like S2, the page fetches directly
from multiple endpoints.

**What shows data:**
- Goloka state (ashtakala period, forest, sakhi)
- Practice recommendations
- Sound state
- Svarodaya (breath)
- Dinacharya (daily routine)
- Chandas (metre)

**What's clickable:** Section blocks have class="section" but no explicit
onclick handlers.

**Issues:**
- Returns 0 layer_composer sections. All data from direct endpoint fetches.
- No game/lila integration (the hex game, tarot, character engines are
  in atlas_330 apps).
- This is the thinnest S-layer in terms of unique content — it aggregates
  from other layers rather than having its own domain.

---

## Summary Table

| Page | Size | Layout | Compose sections | Direct fetches | SVG/Visual | Click handlers | Quality |
|------|------|--------|-----------------|---------------|------------|----------------|---------|
| S0 | 7.6K | Centered card | 0 | /goloka, /resonance | None | Passages | Clean |
| S1 | 13K | Three-column | 3 (devi, deity, bija) | /sound/state, /corpus | Yantra SVG | Weapons, passages | **Best** |
| S2 | 14.5K | Three-column | 0 | /sound, /rhythm, /chandas | None | None | Functional |
| S3 | 12K | Two-col + top | 4 (nak, tithi, deity, devi) | /trajectory, /svaro, /dina | None | Minimal | Functional |
| S4 | 10K | Vastu grid | 3 (geo, arch, avatar) | /yantra/navagraha | Compass SVG | None | **Underbuilt** |
| S5 | 14K | Card stack | 6 (herbs, plants, species, asana, body) | /astrobotany | None | Passages | Data-rich |
| S6 | 10K | Sections | 0 | /goloka, /sound, /svaro, /dina, /chandas | None | None | Thin |

## Specific Questions Answered

### S1 Weapons: YES
Weapons are displayed. The nakshatra deity's weapons come from the NAKSHATRA
DEITY section (layer_composer pulls from nakshatra_deities.csv). Each weapon
is a clickable span with data-entity-id. Additionally, the Devi weapons_full
text (from nitya_devi_master.csv raw_data) renders below the yantra as
descriptive text.

### S1 Yantra SVG: YES, but generic
`buildDeviYantra(color, size)` renders: outer square (bhupura), 4 T-shaped
gates, inner circle, upward triangle, central bindu. Colored by the active
devi's color_hex. The form is the SAME for all 15 devis — it does not use
the per-devi geometry from nitya_yantra_geometry.csv (which specifies
different triangle counts, orientations, petal counts, and wave functions
per devi).

### S1 Devi Iconography: NO
No devi images or elaborate iconographic representations. The page shows:
name (IAST + Devanagari), description text, bija mantra, weapons text, and
the generic geometric yantra SVG. The 45 yantra PNG renders in
research/snapshots/ are not displayed.

---

## Layer Composer Coverage

| Layer | Sections returned | Assessment |
|-------|-------------------|------------|
| S0 | 0 | No _assemble_s0 in layer_composer; data from /goloka directly |
| S1 | 3 | Rich: devi + deity + bija. Could add more (weapons as section, raga) |
| S2 | 0 | No _assemble_s2; data from direct sound/rhythm/chandas fetches |
| S3 | 4 | Good: nakshatra + tithi + deity + devi |
| S4 | 3 | Present but underused: page renders as text, not visual geometry |
| S5 | 6 | Best coverage: 6 cross-domain sections |
| S6 | 0 | No _assemble_s6; aggregates from other layer endpoints |

Three layers (S0, S2, S6) have no layer_composer content. They work because
they fetch from dedicated endpoints, but they don't benefit from the
dataset cross-referencing that the layer_composer provides.

---

## What Would Improve Each Layer

| Layer | Priority improvement |
|-------|---------------------|
| S0 | Add layer_composer S0 assembler (tattva + goloka datasets) |
| S1 | Use per-devi yantra geometry from nitya_yantra_geometry.csv instead of generic |
| S2 | Add layer_composer S2 assembler (raga + tala + gandharva datasets) |
| S3 | Wire to jyotisha engine's compute_tithi for devi null-field data |
| S4 | Wire to wave field engine. Render geometry visually, not as text. Consider merging s4-bloom Chladni content. |
| S5 | Add guild_state data. Plant images if available. |
| S6 | Add layer_composer S6 assembler. Wire to game/lila engines. |
