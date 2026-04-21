# Nitya Devi Layer — Framework Analysis

**Design document** | April 21, 2026 | Analysis only, not implementation

---

## Current State

### What's Already Built

The Nitya Devi layer is **substantially implemented** across the Atlas codebase.
This was not expected going into this analysis. The infrastructure is distributed
across datasets, kernel, layer composer, yantra engines, and the S1 rendering
page. What follows documents the current state and identifies what remains to
wire it into the jyotisha engine and wave field framework.

### Datasets (atlas_core)

| File | Rows | Status | Content |
|------|------|--------|---------|
| `datasets/cosmology/nitya_devi_master.csv` | 15 | Untracked | Full Devi attributes: IAST, Devanagari, bija, mantra, element, guna, rasa, color, graha, shakti, weapons, mudras, ornaments, capability_signature. Attestation: attested_classical (all 15). |
| `datasets/cosmology/nitya_devi_mapping.csv` | 15 | Untracked | Tithi→Devi→color mapping. Simple lookup table. |
| `datasets/cosmology/nitya_yantra_geometry.csv` | 15 | Untracked | 81 columns per Devi: triangle count/orientation/scale/rotation, inner circle, bindu form, petal count, bhupura, colors, line weight, projection angle, interference radius, **wave_function**, **frequency_multiplier**, **angular_position_degrees**, avarana correspondence, Sri Yantra triangle mapping. Attestation: OBSERVED:TRADITIONAL (rows 2-9, 14 from Daksinamurti Samhita), SPECULATIVE (rows 1, 10-13, 15). |
| `datasets/astro/tithi_master.csv` | 30 | Tracked | Both pakshas: tithi_num, deity, element, guna, quality, good_for, avoid, **nitya_devi** column links to Devi. |
| `datasets/astro/tithi_data.csv` | 30 | Untracked | Duplicate/refresh of tithi_master. |

### Kernel (atlas_core/kernel.py)

- **Lines 276-292:** `NITYA_DEVIS` — hardcoded list of 15 tuples (name, emoji, process_description, raga).
- **Lines 295-312:** `_devi_dict(didx)` — converts 0-14 index to dict with name, symbol, description, raga, entity_id, tithi_position.
- **Lines 1725+:** `DEVI_DATA` — processed records with extended fields (slug, type, element, guna, body_parts, mantra).
- **`calc_panchanga()`** — returns `field_state["panchanga"]["devi"]` as the active Nitya Devi dict.
- **`field_state["devi_raga"]`** — current Devi's raga, used by the sound engine.

### Layer Composer (npu_engine/field/layer_composer.py)

- `LAYER_DATASETS` manifests include `nitya_devi_master.csv` and `nitya_devi_mapping.csv` for S1, S2, and S4 layers.
- `_assemble_s1()` builds a "NITYA DEVI" section from the mapping CSV.
- The S1 HTML page renders: SVG Devi yantra (outer square, 4 gates, circle, triangle, bindu), colored from master CSV, with full bija mantra, description, weapons, graha, capability signature.

### Yantra Engines

- `npu_engine/yantra_engine.py` — basic generation: euclidean rhythm, polygon, lotus petals.
- `npu_engine/yantra_generator.py` — SVG/field rendering: triangles, petals, generate_yantra.
- `npu_engine/field/yantra_router.py` — Navagraha yantra matrices (Lo Shu 3x3, eigendecomposition).
- `npu_engine/field/yantra_navagraha_engine.py` — base eigenvalue computation.
- `npu_engine/field/yantra_extension_engine.py` — Kronecker tensor products: 3x3 → 9x9 → 27x27 → 81x81 (108-pada resolution). NPU/iGPU acceleration via OpenVINO.

### Research Outputs

- `research/snapshots/` — 45 PNG renders of all 15 Nitya Devis as yantras across 3 layouts (aligned, merkaba, bloom). Generated April 8, 2026.
- Commit `b4cf116` (Apr 2): "s4: Chladni nodal interference — yantra geometry + tithi slider"
- Commit `9390925` (Apr 6): "resonance: fix vara matching, arati naming, 15 Nitya Devi images"
- Commit `ea38ac8` (Apr 11): "S1 page — devi yantra, mantra, raga details, corpus passage"

### atlas_330 Archive

- `atlas_330/wiki/devis/nitya.md`, `nityaklinna.md` — wiki pages for Nitya Devis.
- `atlas_330/wiki/index_tithi.md` — tithi index page.
- `atlas_330/apps/devi/yantra/` — yantra demo app.
- Individual tithi wiki pages: `tithi__Dvadashi.md`, `tithi__Ekadashi.md`, etc.

### Entity References

- `datasets/entities/reference/devi_nityaklinna.json` — example detailed entity with identity (IAST, Devanagari, synonyms), field_coordinates (theta/phi/psi on toroidal field), domains (tantric source, gandharva raga), nakshatra_correspondence, field_activation conditions, use_ratings.

---

## Nakshatra Layer Pattern (Reference)

The nakshatra layer is the most complete vertical slice in Atlas. It provides
the template for what a fully-wired layer looks like.

### Dataset Schema Pattern

```
nakshatra_master.csv:    27 rows, canonical attributes (name, lord, deity, symbol, shakti, guna, element, body_region, dosha, yoni, qualities)
nakshatra_deities.csv:   27 rows, deity-level attributes (icon, vahana, mudra, colors, gemstone, mantra_bija, shakti_name, tattva, rasa)
nakshatra_padas.csv:     108 rows (27 × 4), pada subdivisions
nakshatra_syllables.csv: 108 rows, pada sound syllables

Relations:
  relations_nakshatra_deity.csv   — nakshatra → deity edges
  relations_nakshatra_plants.csv  — nakshatra → plant edges
  relations_nakshatra_graha.csv   — nakshatra → graha lord edges

Cross-domain:
  nakshatra_agriculture.csv       — agricultural calendar
  nakshatra_species.csv           — yoni animal vertebral data
  nakshatra_body_map.csv          — body region mapping
  nakshatra_cards.json            — tarot correspondence
  dosha_nakshatra_matrix.csv      — ayurvedic cross-reference
  hexagram_nakshatra_resonance.csv — I Ching cross-reference
```

**Attestation pattern:** Every CSV row carries an `attestation_status` column. Values: `attested_classical` (from named primary text), `OBSERVED:TRADITIONAL` (from living tradition), `SYNTHESIS` (derived by Atlas), `SPECULATIVE` (inference without attestation).

### Engine Function Pattern

```python
# jyotish_utils.py — data loading
NAKSHATRAS = [...]                    # 27 names
NAK_LORDS = [...]                     # 27 lords (Vimsottari dasha)
def nak_from_longitude(lon) -> str    # longitude → name
def nak_index_from_longitude(lon)     # longitude → 0-26
def pada_from_longitude(lon) -> int   # longitude → 1-4
def nak_lord_from_longitude(lon)      # longitude → lord name
def load_rashi_lords() -> dict        # CSV loader, cached

# jyotisha_engine.py — computation
def compute_chart(...) -> dict        # full chart with nakshatra per graha
def compute_tara_bala(transit, birth) # nakshatra-to-nakshatra relationship
def compute_nakshatra_field(grahas)   # 27-element wave density vector
def compute_wave_field(grahas)        # pair interference at all targets
```

### Route Pattern

```
GET /jyotish/natal          → full chart (nakshatra in every graha entry)
GET /jyotish/transits       → current sky
GET /jyotish/tara/<nak>     → Tara Bala for one nakshatra
GET /jyotish/wave_field     → 27-element nakshatra density + pair analysis
GET /jyotish/chart          → mandala visualization (HTML)
```

### Attestation Flow

```
CSV (attestation_status column)
  → engine function loads CSV, passes attestation through
  → route returns JSON with attestation field
  → UI displays attestation as badge/indicator
  → layer_composer checks attestation for S-layer composition rules
```

---

## Devi Layer Requirements — What's Missing

Given the survey, the Devi layer is **80% built**. The datasets exist, the
kernel integration exists, the S1 rendering exists. What's missing is the
**jyotisha engine integration** — the same wave field framework that the
nakshatra layer has.

### 1. Engine Functions Needed

The `compute_tithi()` function in `jyotisha_engine.py` currently returns:

```python
{
    "index": 0-29,
    "name": "Shukla Pratipada",
    "paksha": "Shukla",
    "deity": "Agni",
    "sun_moon_phase_deg": 6.0,
    "nitya": None,              # ← NEEDS FILLING
    "chladni_k": None,          # ← NEEDS FILLING
    "sri_yantra_alignment": None, # ← NEEDS FILLING
    "avarana": None,            # ← NEEDS FILLING
}
```

**Functions to add to `jyotisha_engine.py`:**

```python
def resolve_nitya_devi(tithi_index: int) -> dict:
    """Given tithi 0-29, return active Nitya Devi with all attributes.
    Loads from nitya_devi_master.csv. Tithi 0-14 maps to Devi 1-15.
    Tithi 15-29 maps to Devi 15-1 (reverse in Krishna paksha).
    Returns: name_iast, name_devanagari, bija, mantra, element, guna,
    rasa, color, graha, shakti, weapons, mudras, capability_signature,
    angular_position (from yantra_geometry.csv), wave_function,
    frequency_multiplier, avarana, sri_yantra_triangle."""

def compute_devi_chladni_field(devi_id: int, resolution: int = 360) -> dict:
    """Compute Chladni interference pattern for one Devi's yantra.
    Uses yantra_geometry.csv: wave_function, frequency_multiplier,
    interference_radius_fraction, projection_angle.
    Returns: field array (1D angular or 2D disk), nodal_count,
    symmetry_order, peak_positions."""

def compute_devi_wave_interaction(
    devi_id: int, graha_longitudes: dict
) -> dict:
    """How the current graha positions interact with this Devi's
    wave field. Which grahas sit on her nodal lines? Which are
    at her maxima? Returns activation scores per graha."""
```

### 2. Data Loading Functions Needed in `jyotish_utils.py`

```python
def load_nitya_devi_master() -> Dict[int, dict]:
    """Load nitya_devi_master.csv keyed by tithi_num (1-15)."""

def load_nitya_yantra_geometry() -> Dict[int, dict]:
    """Load nitya_yantra_geometry.csv keyed by devi_id (1-15)."""

def devi_from_tithi(tithi_index: int) -> dict:
    """Quick lookup: tithi 0-29 → Devi dict.
    Handles Krishna paksha reversal."""
```

### 3. Routes Needed

```
GET /nitya/today             → active Devi + attributes + wave field
GET /nitya/devi/<id>         → specific Devi by ID (1-15)
GET /nitya/field/<tithi>     → Chladni field for a tithi position
GET /nitya/calendar          → 30-day Devi cycle projection
GET /nitya/yantra/<id>       → SVG yantra geometry data
```

These could be a new `nitya_bp` blueprint or added to `jyotish_bp`.
Recommendation: add to `jyotish_bp` since the Devi layer is part of
the panchanga (not a separate system).

### 4. Fill the Null Fields in compute_tithi()

The existing `compute_tithi()` return schema has 4 null fields ready for
the Devi layer. These should be populated:

```python
"nitya": resolve_nitya_devi(tidx),
"chladni_k": yantra_geometry[devi_id]["frequency_multiplier"],
"sri_yantra_alignment": yantra_geometry[devi_id]["triangle_in_sri_yantra"],
"avarana": yantra_geometry[devi_id]["avarana_correspondence"],
```

### 5. Sound Engine Integration

The sound engine already uses `_NAK_RAGA` to map Moon nakshatra → raga.
The Devi layer adds a parallel mapping: Devi → raga (already in
`NITYA_DEVIS` tuples and `nitya_devi_master.csv`). The sound engine
should blend both:

- Moon nakshatra raga (from transit sky)
- Active Devi raga (from tithi)
- Natal home raga (from birth Moon)

Weighted blend: Devi raga dominates during observances (Ekadashi, Purnima),
nakshatra raga dominates otherwise.

---

## Data Availability

### Fully Present (use as-is)

| Attribute | Source | Attestation |
|-----------|--------|-------------|
| 15 Devi names (IAST + Devanagari) | nitya_devi_master.csv | attested_classical |
| Bija mantras | nitya_devi_master.csv | attested_classical |
| Short mantras | nitya_devi_master.csv | attested_classical |
| Element, guna, rasa | nitya_devi_master.csv | attested_classical |
| Graha correspondence | nitya_devi_master.csv | attested_classical |
| Shakti (power) | nitya_devi_master.csv | attested_classical |
| Weapons + mudras | nitya_devi_master.csv | attested_classical |
| Color | nitya_devi_master.csv | attested_classical |
| Capability signature | nitya_devi_master.csv | attested_classical |
| Tithi → Devi mapping | tithi_master.csv | attested_classical |
| Tithi qualities | tithi_master.csv | attested_classical |
| Raga per Devi | kernel.py NITYA_DEVIS | SYNTHESIS |

### Present with Mixed Attestation

| Attribute | Source | Notes |
|-----------|--------|-------|
| Yantra geometry (rows 2-9, 14) | nitya_yantra_geometry.csv | OBSERVED:TRADITIONAL from Daksinamurti Samhita |
| Yantra geometry (rows 1, 10-13, 15) | nitya_yantra_geometry.csv | SPECULATIVE — no explicit geometry described in source texts for these Devis |
| Angular positions | nitya_yantra_geometry.csv | Equal-spacing assumed (24° apart). No canonical angular positions found in corpus. |
| Wave function parameters | nitya_yantra_geometry.csv | SPECULATIVE — sine/cosine assignments are analytical, not traditional |

### Not Present — Needs Sourcing

| Attribute | Primary Sources to Check |
|-----------|------------------------|
| Dhyana verses (full meditation descriptions) | Tantraraja Tantra, Nityasodasikarnava |
| Specific avarana rituals per Devi | Varivasya Rahasya, Parasurama Kalpa Sutra |
| Confirmed angular positions (if non-equal) | Nityasodasikarnava (if it specifies ordering) |
| Individual Devi-to-nakshatra mappings beyond what's in entity files | Needs systematic sourcing |
| Devi-specific tala/rhythm associations | Not attested; would be SYNTHESIS |

---

## Open Questions

### Need Inahd's Decision

1. **Route location:** Add Devi routes to existing `jyotish_bp.py` or create a new `nitya_bp.py` blueprint? The Devi layer is panchanga-integral, not separate. Recommend: `jyotish_bp`.

2. **Krishna paksha mapping:** In Krishna paksha, do the 15 Devis map in reverse order (Citra→Kameshvari) or repeat forward? The `tithi_master.csv` currently maps tithis 16-30 to the same Devi names as 1-15 (forward repeat). The Tantraraja tradition uses reverse mapping. Which convention?

3. **Angular positions:** The `nitya_yantra_geometry.csv` uses equal 24° spacing. Should the engine use this, or should it be configurable for future non-equal-spacing if a source is found?

4. **Wave function assignment:** Rows 1, 10-13, 15 have wave functions marked SPECULATIVE. Should the engine use them with a reduced confidence weight, or omit them until attested?

5. **Sound integration:** Should the Devi raga override the nakshatra raga, blend with it, or only activate during specific conditions (observances, Devi-specific puja times)?

### Need Primary Source Access

6. The Daksinamurti Samhita is cited for yantra geometry of Devis 2-9 and 14. The actual text should be verified — current data is from shivashakti.com secondary source.

7. Devis 10-13 (Nitya, Nilapataka, Vijaya, Sarvamangala) have SPECULATIVE yantra geometry. The Nityasodasikarnava may describe these — it's the primary tantra for the Nitya cycle.

### Places Where Tradition Is Unclear

8. The `frequency_multiplier` column in yantra_geometry.csv assigns harmonic orders (1-5) to each Devi. These are analytical assignments, not traditional. Whether the Devis have canonical harmonic associations (beyond the self-evident tithi number) is an open question.

9. The relationship between the 15 Nitya Devis and the 15 singular vectors of the wave fine structure matrix (Finding 10 in the two-source paper) is a computational observation, not a traditional correspondence. Whether to surface this in the engine output is a design choice about how much speculation the system should carry.

---

## Recommended Build Sequence

### Phase 1: Data Loading (1 session)

Add to `jyotish_utils.py`:
- `load_nitya_devi_master()`
- `load_nitya_yantra_geometry()`
- `devi_from_tithi()`

Fill the null fields in `compute_tithi()`:
- `nitya` → full Devi dict from master CSV
- `chladni_k` → frequency_multiplier from yantra geometry
- `sri_yantra_alignment` → triangle_in_sri_yantra
- `avarana` → avarana_correspondence

**Checkpoint:** `curl /jyotish/natal` should show Devi data in tithi field. Review before proceeding.

### Phase 2: Devi Routes (1 session)

Add to `jyotish_bp.py`:
- `GET /jyotish/devi/today`
- `GET /jyotish/devi/<id>`
- `GET /jyotish/devi/calendar` (30-day cycle)

**Checkpoint:** Routes return correct Devi for current tithi. Review attestation display.

### Phase 3: Chladni Field (1 session)

Add to `jyotisha_engine.py`:
- `compute_devi_chladni_field()` — uses yantra geometry CSV wave params
- `compute_devi_wave_interaction()` — how grahas interact with Devi field

Wire into `compute_chart()` alongside existing `compute_wave_field()`.

**Checkpoint:** Wave field data includes Devi Chladni field. Review whether SPECULATIVE geometry rows should be included or marked.

### Phase 4: Visualization (1 session)

Either extend `jyotish_chart.html` or create a new Devi mandala page:
- 15-segment Devi wheel (tithi cycle)
- Yantra SVG rendering per Devi from geometry CSV
- Current Devi highlighted with wave activation

**Checkpoint:** Visual review in browser. Compare with existing S1 yantra renders.

### Phase 5: Sound Integration (1 session)

Update `sound_engine.py`:
- Blend Devi raga with nakshatra raga
- Devi-specific Chladni frequency modulates tanpura partials
- Devi capability_signature influences musical character

**Checkpoint:** Listen for Devi raga appearing during specific tithis.

### What Can Be Stubbed vs Must Be Attested

| Component | Stub OK? | Reason |
|-----------|----------|--------|
| Data loading + compute_tithi fill | No — use existing attested CSVs | Data is present and attested |
| Chladni field for attested Devis (2-9, 14) | No — compute from attested geometry | Source cited (Daksinamurti Samhita) |
| Chladni field for speculative Devis (1, 10-13, 15) | Yes — mark as SPECULATIVE in output | No canonical geometry in corpus |
| Angular positions | Yes — use equal spacing with note | No canonical non-equal source found |
| Wave function assignments | Yes — mark as SYNTHESIS | Analytical, not traditional |
| Devi-to-nakshatra correspondence | Partial — use entity file data where present | Only devi_nityaklinna.json exists as reference entity |
| Sound integration | Yes — SYNTHESIS throughout | Design decisions, not shastra |

---

*This document is analysis only. No datasets, engines, routes, or code
were created. The build sequence above is a recommendation for future
sessions, with review checkpoints at each phase.*
