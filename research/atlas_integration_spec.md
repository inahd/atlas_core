# Atlas Integration Spec: Jyotish Metallurgical Framework

*Handoff document for Claude Code on kanjira. Specifies how to integrate the materials-cosmology framework developed externally into atlas_core as a permanent, queryable capability.*

---

## What's being integrated

The framework that produced 91.7% structural recovery of classical ashtadhatu nakshatra prescriptions. Currently exists as standalone Python modules. Needs to become:

- Queryable datasets in `datasets/`
- Integration with existing `panchanga_engine` and `jyotisha_engine`
- Flask routes exposing the capability
- Persistent across kernel restarts
- Generalized beyond panchaloha — any alloy operation should be queryable

Source files (in user-data/uploads or wherever the packet was extracted):
- `jyotish_metallurgy.py` (graha-metal correspondences, friendship matrix)
- `panchaloha_alloy.py` (alloy recipes, scoring functions, nakshatras)
- `run_panchaloha_analysis.py` (reference for analysis logic)

---

## Phase 1: Datasets

Convert hardcoded Python data to CSV datasets. Place in `datasets/jyotish/metallurgy/` (create directory if needed).

### `datasets/jyotish/metallurgy/graha_metal_correspondences.csv`

```
graha,sanskrit,primary_metal,primary_metal_sanskrit,secondary_metals,dhatu_class,cosmological_signature
surya,सूर्य,gold,suvarna,"copper",jeeva,"solar charge, central authority, tejas"
chandra,चन्द्र,silver,rajata,"pearl",dhatu,"lunar coolness, fluidity, manas"
mangala,मङ्गल,copper,tamra,"red coral",dhatu,"tapas, fire-transformation, blood"
budha,बुध,brass,kamsya,"mercury, emerald",jeeva,"intelligence, transformation"
guru,गुरु,gold,suvarna,"yellow sapphire",jeeva,"wisdom, expansion, sattva"
shukra,शुक्र,silver,rajata,"diamond, platinum",moola,"rasa, beauty, refinement"
shani,शनि,iron,lauha,"steel, blue sapphire, lead",dhatu,"structure, time, density, hardness"
rahu,राहु,lead,sisa,"hessonite, mixed metals",dhatu,"amplification, distortion, smoke"
ketu,केतु,lead-tin,---,"cat's eye, mixed",jeeva,"dissolution, ash"
```

### `datasets/jyotish/metallurgy/naisargika_friendship.csv`

Two-column format: graha_a, graha_b, friendship_value. Encode the BPHS friendship matrix. Reference: `jyotish_metallurgy.py` `NAISARGIKA_FRIENDSHIPS` dict.

```
graha_a,graha_b,friendship
surya,chandra,1
surya,mangala,1
surya,budha,0
surya,guru,1
surya,shukra,-1
surya,shani,-1
chandra,mangala,0
... [continue for all pairs from NAISARGIKA_FRIENDSHIPS]
```

### `datasets/jyotish/metallurgy/nakshatra_lordship.csv`

```
nakshatra_index,nakshatra,sanskrit,vimshottari_lord,dhruva,sattvic,inauspicious,pratishtha_auspicious
1,ashwini,अश्विनी,ketu,false,false,false,false
2,bharani,भरणी,shukra,false,false,true,false
3,krittika,कृत्तिका,surya,false,false,true,false
4,rohini,रोहिणी,chandra,true,true,false,true
... [continue for all 27 nakshatras from Nakshatra enum]
```

### `datasets/jyotish/metallurgy/alloy_recipes.csv`

```
alloy_name,sanskrit_name,source_text,component_metal,component_graha,weight_pct
panchaloha,पञ्चलोह,Shilpa Shastra,gold,surya,1.0
panchaloha,पञ्चलोह,Shilpa Shastra,silver,chandra,1.0
panchaloha,पञ्चलोह,Shilpa Shastra,copper,mangala,80.0
panchaloha,पञ्चलोह,Shilpa Shastra,iron,shani,3.0
panchaloha,पञ्चलोह,Shilpa Shastra,zinc,guru,15.0
ashtadhatu,अष्टधातु,Shilpa Shastra,gold,surya,12.5
ashtadhatu,अष्टधातु,Shilpa Shastra,silver,chandra,12.5
ashtadhatu,अष्टधातु,Shilpa Shastra,copper,mangala,12.5
ashtadhatu,अष्टधातु,Shilpa Shastra,lead,shani,12.5
ashtadhatu,अष्टधातु,Shilpa Shastra,zinc,guru,12.5
ashtadhatu,अष्टधातु,Shilpa Shastra,tin,guru,12.5
ashtadhatu,अष्टधातु,Shilpa Shastra,iron,shani,12.5
ashtadhatu,अष्टधातु,Shilpa Shastra,mercury,budha,12.5
```

### `datasets/jyotish/metallurgy/tithi_favorability.csv`

Reference: `TITHI_FAVORABILITY` dict in `jyotish_metallurgy.py`. 30 rows, columns: tithi, name, score, paksha, note.

### `datasets/jyotish/metallurgy/yoga_classification.csv`

Inauspicious yogas listed; all others assumed neutral/auspicious. Reference: `INAUSPICIOUS_YOGAS` list.

---

## Phase 2: Engine module

Create `engines/metallurgy_engine.py` (or wherever Atlas's other engines live — match existing convention).

### Core functions

```python
def assess_alloy_operation(alloy_name, panchanga_state, practitioner_grahas=None):
    """
    Given an alloy name and current panchanga state, return composite
    favorability score plus per-component breakdown.
    
    panchanga_state: dict with keys (vaara, hora_index, tithi, yoga, nakshatra)
    practitioner_grahas: optional list of practitioner's natal grahas
    
    Returns: dict with combined_score, per_component_breakdown, assessment_text
    """

def find_optimal_windows(alloy_name, days_ahead=30, panchanga_engine_fn=None):
    """
    Scan upcoming N days using Atlas's panchanga_engine to compute live state.
    Return ranked list of favorable windows.
    """

def predict_alloy_optimal_nakshatras(alloy_name, baseline_panchanga=None):
    """
    For a given alloy and baseline conditions, rank all 27 nakshatras
    by predicted favorability. (The function used in the structural
    validation.)
    """

def compare_to_tradition(alloy_name, prescribed_nakshatras=None):
    """
    Run the structural validation - framework predictions vs tradition's
    prescribed list. Returns precision/recall metrics.
    """
```

### Integration with existing engines

```python
# In assess_alloy_operation, panchanga_state should ideally be obtained from:
from engines.panchanga_engine import current_panchanga
state = current_panchanga(timestamp, location)

# For practitioner_grahas:
from instance.personal.natal import natal_chart
practitioner_grahas = natal_chart['major_grahas']
```

### Caching

These computations are cheap; no caching needed unless you find performance issues. Don't over-engineer.

---

## Phase 3: Flask routes

Add to `jyotish_bp.py` (or create `metallurgy_bp.py` if you prefer separate blueprint):

```
GET  /jyotish/metallurgy/alloys
     → list available alloy recipes from dataset

GET  /jyotish/metallurgy/correspondences
     → return graha-metal correspondences

GET  /jyotish/metallurgy/assess
     ?alloy=ashtadhatu
     ?date=2026-05-03 (optional, defaults to now)
     ?include_practitioner=true (optional)
     → return assessment for given alloy at given moment

GET  /jyotish/metallurgy/optimal-windows
     ?alloy=ashtadhatu
     ?days=30
     → scan upcoming N days, return ranked favorable windows

GET  /jyotish/metallurgy/structural-validation
     ?alloy=ashtadhatu
     → run the panchaloha-style comparison; return precision/recall vs
       tradition's prescribed nakshatras

GET  /jyotish/metallurgy/component-breakdown
     ?alloy=ashtadhatu
     ?nakshatra=rohini (optional, defaults to all 27)
     → return per-component graha compatibility breakdown
```

---

## Phase 4: Validation

After integration, run the structural validation as a kernel-side test:

```bash
curl http://localhost:5000/jyotish/metallurgy/structural-validation?alloy=ashtadhatu
```

Expected response includes `precision: 0.917` and `recall: 0.917`. *If it does not, the integration has drifted from the source modules — debug.* This is the canary that confirms the framework still works after integration.

---

## Phase 5: UI (optional, lower priority)

If you want a portal view of this:

`templates/jyotish_metallurgy.html` — page showing:
- Current panchanga state
- Per-alloy favorability scores for "right now"
- Upcoming optimal windows (next 30 days)
- Structural validation results (the 91.7% finding)

This is portal/cartographer aesthetic register (S3/S4 cartographer per your established style: navy/orange, JetBrains Mono).

---

## Phase 6: Generalization

Once integrated for panchaloha and ashtadhatu, the same machinery extends to:

- **Bhasma protocols**: each bhasma is a "single-metal alloy" in the framework. Add to `alloy_recipes.csv` with weight_pct=100 for the single metal.
  - lauha bhasma → shani
  - tamra bhasma → mangala
  - swarna bhasma → surya
  - rajata bhasma → chandra
  - naga bhasma → shani (or rahu — variant)
  - yashada bhasma → guru
- **Bell-bronze tuning**: copper-tin alloy, two-graha (mangala + guru). 
- **Specific deity-murti recipes**: extend dataset with deity-specific weighting variants.

The framework handles all of these without code changes — only dataset additions.

---

## What this gives Atlas

After integration:
- Atlas can answer "is this a favorable moment for X operation" for any alloy in the dataset, queryable through standard kernel routes
- The structural validation finding (91.7% for ashtadhatu) becomes a permanent verifiable claim within Atlas's own system
- Predictions made by Atlas can be logged for future empirical comparison if practitioners track outcomes
- The framework lives where the rest of Atlas's intelligence lives, queryable alongside panchanga, jyotisha, sound, and other engines
- Future work (deity-specific recipes, cross-tradition comparisons) is dataset extension, not code rewriting

---

## What this doesn't give Atlas

This integration handles the *structural validation* layer — Atlas can compute the framework's predictions live. It does NOT yet:

- Connect to physical experiment data for empirical validation (that requires lab partnership)
- Run the wootz physics simulation (separate module, separate integration spec if wanted)
- Handle tatkalika (temporal) friendship — only naisargika encoded
- Distinguish between deity-specific recipe variants

These are future extensions, not blockers.

---

## Source files reference

The Python modules that produced the framework are in the research_packet (or wherever you've stored them on kanjira):

- `jyotish_metallurgy.py` — primary reference for friendship matrix, tithi favorability, hora system, optimal-window scanning
- `panchaloha_alloy.py` — primary reference for nakshatra system, alloy recipes, multi-metal scoring formula
- `run_panchaloha_analysis.py` — primary reference for the structural validation logic

Treat these as canonical specifications. The CSVs and engine module should produce identical results when given identical inputs. The structural validation (91.7%) is the regression test.

---

## Estimated effort

- Phase 1 (datasets): 1-2 hours of focused Claude Code work
- Phase 2 (engine module): 2-3 hours
- Phase 3 (routes): 1-2 hours
- Phase 4 (validation): 30 minutes
- Phase 5 (UI): 2-4 hours if wanted
- Phase 6 (extensions): incremental, dataset-only

Total core integration (Phases 1-4): half a focused day on kanjira.

---

## Notes on scope

This integrates the *structural framework* into Atlas. It is not the entire Atlas materials-cosmology research program — that's broader and continues across multiple workstreams. This specific spec covers the metallurgical-timing capability, which is the part that's currently mature enough to integrate.

When the wootz physics simulation matures further or when bhasma data is added, those become separate integration specs following the same pattern.
