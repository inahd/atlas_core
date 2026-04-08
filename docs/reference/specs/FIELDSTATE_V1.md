# FieldState v1 — Shared Field Contract
# Bead 009 · coherence-atlas-009-npu
# Date: 2026-03-22
# Status: SPEC · defines the shared spine for all surfaces

---

## Purpose

Four surfaces read the same field:

- **Brahmāṇḍa** — toroidal rendering (3D spatial)
- **Vāstu** — planar field rendering (2D directional)
- **Talachakra** — sound derivation (temporal/rhythmic)
- **Vyāsāsana** — text interpretation (domain-separated)

They must not duplicate logic.
They must read from one shared representation.

This document defines that representation: **FieldState v1**.

---

## 1. JSON Schema

FieldState is a JSON object with six top-level keys.
All values are derived by `kernel.py field_state()`.
No surface computes these — they only read and interpret.

```json
{
  "version": 1,

  "theta": {
    "panchanga": {
      "tithi":      "Pañcamī",
      "tithi_num":  5,
      "paksha":     "Kṛṣṇa",
      "nakshatra":  "Dhaniṣṭhā",
      "nak_lord":   "Maṅgala",
      "vara":       "Śukravāra ♀",
      "yoga":       { "name": "Prīti", "quality": "auspicious" },
      "karana":     { "name": "Bālava", "quality": "auspicious" }
    },
    "s_layer": 3,
    "theta_rad": 5.131,
    "attestation": "OBSERVED"
  },

  "phi": {
    "position": 3.927,
    "label": "center-right",
    "companion": "Bandhu",
    "element": "air",
    "guna": "tamas",
    "attestation": "OBSERVED"
  },

  "psi": "jijnasu",

  "field_signals": {
    "center_strength": 0.72,
    "directional_bias": {
      "N": 0.6, "E": 0.85, "S": 0.3, "W": 0.45
    },
    "coherence_peaks": [
      { "entity_id": "pranayama_bhramari", "score": 0.91, "element": "air" },
      { "entity_id": "raga_bhairavi",      "score": 0.84, "element": "water" },
      { "entity_id": "nakshatra_sravana",  "score": 0.78, "element": "ether" }
    ],
    "attestation": "SYNTHESIS"
  },

  "sound": {
    "raga":      "Mārvā",
    "tala":      "Ādi",
    "tala_beats": 8,
    "gati":      "chatusra",
    "bpm":       72,
    "arc_phase": 0.65,
    "attestation": {
      "raga": "OBSERVED",
      "tala": "TRADITIONAL",
      "gati": "SYNTHESIS",
      "bpm":  "OBSERVED"
    }
  },

  "muhurta": {
    "name": "Sāyaṃ Sandhyā",
    "quality": "auspicious",
    "rahu_kala_active": false
  }
}
```

### Key-by-key explanation

#### `theta` — the vertical axis (TIME / LEVEL)

Encodes **what level of reality is active now**.

| Field | Source | Notes |
|-------|--------|-------|
| `panchanga.*` | `calc_panchanga()` in kernel.py | Already computed. Restructured for clarity. |
| `s_layer` | Derived from muhūrta + prahar mapping | 0–6 integer. Optional — omit if not yet computed. |
| `theta_rad` | `panchanga_to_coords()` θ output | The actual toroid major-axis coordinate in radians (0–2π). Computed by NPU. |
| `attestation` | Static | Panchanga is OBSERVED (astronomical calculation). |

**Where θ comes from today:**
`panchanga_to_coords()` in `npu_engine/toroidal_field.py` already computes θ as a weighted circular mean of nakshatra (0.5), tithi (0.35), vara (0.15). No new computation needed — just expose the result.

#### `phi` — the horizontal axis (WITNESS ↔ PARTICIPANT)

Encodes **what mode of engagement is resonant now**.

| Field | Source | Notes |
|-------|--------|-------|
| `position` | `panchanga_to_coords()` φ output | Radians, 0–2π. |
| `label` | Derived from position | `"far-left"`, `"left"`, `"center-left"`, `"center"`, `"center-right"`, `"right"`, `"far-right"` |
| `companion` | Derived from position | `"Shilpi"` (φ < π), `"Bheruṇḍā"` (φ ≈ π), `"Bandhu"` (φ > π), `null` (θ ≈ 0, S0) |
| `element` | `nak_data.element` | The element proxy for φ (per TWO_AXIS_FIELD_SPEC.md). |
| `guna` | `nak_data.guna` | The guna proxy for φ. |

**Where φ comes from today:**
Same `panchanga_to_coords()` — element (0.6 weight) + guna (0.4 weight) circular mean. Already computed. The `label` and `companion` are trivial derivations from the radian value.

#### `psi` — the engagement mode

One of four values from Bhagavad Gītā 7.16:

| Value | Meaning | When |
|-------|---------|------|
| `"arta"` | Distressed seeker | User-set or inferred from low coherence |
| `"jijnasu"` | Curious inquirer | Default |
| `"artharthi"` | Goal-seeking | User-set |
| `"jnani"` | Knowledge-established | User-set or inferred from high coherence + witness position |

**Not computed by the field.** This is user input or companion inference. Default: `"jijnasu"`. Surfaces should accept it if present, ignore if absent.

#### `field_signals` — derived spatial/coherence data

| Field | Source | Notes |
|-------|--------|-------|
| `center_strength` | Coherence score at (θ, φ) center point | 0.0–1.0. How "alive" the field center is. |
| `directional_bias` | Derived from element + vastu_zone | N/E/S/W scores, 0.0–1.0. Which spatial direction is energized. |
| `coherence_peaks` | `ToroidalField.field_query()` top results | Already computed by `/coherence`. Top N entities closest to current moment. |

**Where this comes from today:**
- `center_strength`: the top coherence score from `get_coherence_score()`.
- `directional_bias`: already computed in Vāstu app from element/guna/vara. Should be computed once in kernel, not per-app.
- `coherence_peaks`: already returned by `/coherence` endpoint. Just include top 5 in FieldState.

#### `sound` — rhythmic/melodic field

| Field | Source | Notes |
|-------|--------|-------|
| `raga` | `devi_raga` or `muhurta_raga` from field_state() | Already computed. |
| `tala` | `generate_composition()` → `nakshatra_tala[nak]` | Already computed. Nakshatra → tāla mapping. |
| `tala_beats` | Same source | Beat count. |
| `gati` | Guna → gati mapping | `sattva→tisra`, `rajas→chatusra`, `tamas→khanda` (already in Talachakra). |
| `bpm` | `muhurta.bpm` | Already computed. |
| `arc_phase` | Tithi cycle position (tidx / 30) | 0.0–1.0. Where in the lunar arc we are. |

#### `muhurta` — timing window

| Field | Source | Notes |
|-------|--------|-------|
| `name` | `get_muhurta()` | Already computed. |
| `quality` | From hora/yoga quality | Summary quality signal. |
| `rahu_kala_active` | `compute_rahu_kala()` | Boolean. |

---

## 2. `/field` Route Output

### Principle: additive, not breaking

The existing `/field` response stays exactly as-is. We add one new top-level key: `"field_state_v1"`.

Apps that understand v1 read from `field_state_v1`.
Apps that don't continue reading from the flat structure.
No breaking change.

### Proposed addition to `field_state()` in kernel.py

```python
# At the end of field_state(), before return:
# Derive FieldState v1 contract (additive — does not replace existing keys)
_theta_rad = None
_phi_rad = None
try:
    toroid = get_toroid()
    _theta_rad, _phi_rad = toroid.moment_to_coords(_toroid_panchanga(fs))
except Exception:
    pass

_phi_label = _phi_to_label(_phi_rad) if _phi_rad is not None else "center"
_companion = _phi_to_companion(_phi_rad) if _phi_rad is not None else None

# Sound derivation
_nak_itrans = nak_to_itrans(p5.get("nakshatra", ""))
_tala_info = NAKSHATRA_TALA.get(_nak_itrans, {"tala": "Ādi", "beats": 8})
_guna_gati = {"sattva": "tisra", "rajas": "chatusra", "tamas": "khanda"}
_gati = _guna_gati.get(p5.get("guna", "").lower(), "chatusra")

# Center strength from coherence
_center = 0.0
try:
    coh = get_coherence_score(now)
    _center = coh.get("coherence_top", 0.0)
except Exception:
    pass

# Coherence peaks
_peaks = []
try:
    toroid = get_toroid()
    results = toroid.field_query(_toroid_panchanga(fs), top_n=5)
    _peaks = [
        {"entity_id": r["entity_id"], "score": round(r["score"], 3),
         "element": r.get("element", "")}
        for r in results
    ]
except Exception:
    pass

# Directional bias from element
_elem = p5.get("element", "ether").lower()
_dir_map = {
    "fire":  {"N": 0.3, "E": 0.5, "S": 0.9, "W": 0.3},
    "water": {"N": 0.5, "E": 0.3, "S": 0.3, "W": 0.9},
    "earth": {"N": 0.9, "E": 0.5, "S": 0.5, "W": 0.5},
    "air":   {"N": 0.5, "E": 0.9, "S": 0.3, "W": 0.5},
    "ether": {"N": 0.6, "E": 0.6, "S": 0.6, "W": 0.6},
}
_dir_bias = _dir_map.get(_elem, _dir_map["ether"])

fs["field_state_v1"] = {
    "version": 1,
    "theta": {
        "panchanga": {
            "tithi": p5["tithi"],
            "tithi_num": p5["tidx"] + 1,
            "paksha": p5["paksha"],
            "nakshatra": p5["nakshatra"],
            "nak_lord": p5["nak_lord"],
            "vara": p5["vara"],
            "yoga": yoga,
            "karana": karana,
        },
        "s_layer": None,  # not yet computed
        "theta_rad": round(_theta_rad, 4) if _theta_rad is not None else None,
        "attestation": "OBSERVED",
    },
    "phi": {
        "position": round(_phi_rad, 4) if _phi_rad is not None else None,
        "label": _phi_label,
        "companion": _companion,
        "element": _elem,
        "guna": p5.get("guna", ""),
        "attestation": "OBSERVED",
    },
    "psi": "jijnasu",  # default; user-set in future
    "field_signals": {
        "center_strength": round(_center, 3),
        "directional_bias": _dir_bias,
        "coherence_peaks": _peaks,
        "attestation": "SYNTHESIS",
    },
    "sound": {
        "raga": devi_raga_name,
        "tala": _tala_info["tala"],
        "tala_beats": _tala_info["beats"],
        "gati": _gati,
        "bpm": mu.get("bpm", 72),
        "arc_phase": round(p5["tidx"] / 30.0, 3),
        "attestation": {
            "raga": "OBSERVED",
            "tala": "TRADITIONAL",
            "gati": "SYNTHESIS",
            "bpm": "OBSERVED",
        },
    },
    "muhurta": {
        "name": mu.get("name", ""),
        "quality": hora.get("hora_quality", "neutral"),
        "rahu_kala_active": rahu_kala.get("rahu_kala_active", False),
    },
}
```

### Example response (abbreviated)

```
GET /field

{
  "panchanga": { ... },        ← existing, unchanged
  "muhurta": { ... },          ← existing, unchanged
  "devi_raga": "Mārvā",       ← existing, unchanged
  ... all existing keys ...

  "field_state_v1": {          ← NEW: the shared contract
    "version": 1,
    "theta": {
      "panchanga": {
        "tithi": "Pañcamī",
        "tithi_num": 5,
        "paksha": "Kṛṣṇa",
        "nakshatra": "Dhaniṣṭhā",
        "nak_lord": "Maṅgala",
        "vara": "Śukravāra ♀",
        "yoga": { "yoga_name": "Prīti", "yoga_quality": "auspicious" },
        "karana": { "karana_name": "Bālava", "karana_quality": "auspicious" }
      },
      "s_layer": null,
      "theta_rad": 5.131,
      "attestation": "OBSERVED"
    },
    "phi": {
      "position": 3.927,
      "label": "center-right",
      "companion": "Bandhu",
      "element": "air",
      "guna": "tamas",
      "attestation": "OBSERVED"
    },
    "psi": "jijnasu",
    "field_signals": {
      "center_strength": 0.72,
      "directional_bias": { "N": 0.5, "E": 0.9, "S": 0.3, "W": 0.5 },
      "coherence_peaks": [
        { "entity_id": "pranayama_bhramari", "score": 0.91, "element": "air" }
      ],
      "attestation": "SYNTHESIS"
    },
    "sound": {
      "raga": "Mārvā",
      "tala": "Ādi",
      "tala_beats": 8,
      "gati": "khanda",
      "bpm": 72,
      "arc_phase": 0.167,
      "attestation": {
        "raga": "OBSERVED",
        "tala": "TRADITIONAL",
        "gati": "SYNTHESIS",
        "bpm": "OBSERVED"
      }
    },
    "muhurta": {
      "name": "Sāyaṃ Sandhyā",
      "quality": "auspicious",
      "rahu_kala_active": false
    }
  }
}
```

---

## 3. Surface Mapping Guidance

### Brahmāṇḍa (toroidal rendering)

**Reads:** `theta.theta_rad`, `phi.position`, `field_signals.coherence_peaks`

| FieldState key | Brahmāṇḍa use |
|----------------|----------------|
| `theta.theta_rad` | Major axis position of the "current moment" point on the torus. Drives the golden dot. |
| `phi.position` | Minor axis position. Together with θ, places the moment on the torus surface. |
| `field_signals.coherence_peaks` | Entity points to render near the moment. Score → brightness/size. `element` → color. |
| `field_signals.center_strength` | Intensity of the central glow. Higher = brighter pulse at moment point. |
| `sound.bpm` | Animation speed. Torus rotation rate scales with bpm. |
| `sound.raga` | Scale selection for audio output (already used). |

**Does NOT use:** `directional_bias` (that's planar, not toroidal), `psi` (no behavioral mode in spatial view).

### Vāstu (planar field rendering)

**Reads:** `field_signals.directional_bias`, `phi.element`, `phi.guna`, `theta.panchanga.vara`

| FieldState key | Vāstu use |
|----------------|-----------|
| `field_signals.directional_bias` | **Primary input.** N/E/S/W scores become the radial gradient weights. Replaces the per-app element→direction computation. |
| `field_signals.center_strength` | Brahma-sthāna (center zone) intensity. |
| `phi.element` | Element coloring of the field. Fire=warm, Water=cool, etc. |
| `phi.guna` | Modifies zone scoring (sattva→NE boost, rajas→SE, tamas→SW — already in Vāstu app). |
| `theta.panchanga.vara` | Vara planet → deity zone correspondence. |
| `muhurta.rahu_kala_active` | If true, SW zone (Nirṛti) intensifies as warning. |

**Does NOT use:** `theta_rad`, `phi.position` (those are toroidal coordinates, not spatial), `sound.*`.

### Talachakra (sound derivation)

**Reads:** `sound.*`, `theta.panchanga.nakshatra`, `phi.guna`

| FieldState key | Talachakra use |
|----------------|----------------|
| `sound.tala` | Tāla family selection. Direct. |
| `sound.tala_beats` | Beat count for pattern generation. |
| `sound.gati` | Gati (subdivision pattern). Drives jati selection. |
| `sound.bpm` | Tempo. Direct. |
| `sound.raga` | Rāga scale selection. Direct (already used). |
| `sound.arc_phase` | Tithi cycle position. Drives intensity arc — beginning of lunar cycle = sparse patterns, middle = dense, end = dissolving. |
| `field_signals.center_strength` | Coherence → density. Higher coherence = more layered patterns. Lower = minimal. |
| `sound.attestation.*` | Display per-field attestation badges in the Talachakra field panel. |

**Does NOT use:** `directional_bias`, `theta_rad` / `phi.position` (sound is temporal, not spatial).

### Vyāsāsana (text interpretation)

**Reads:** everything, but **does not collapse domains**

| FieldState key | Vyāsāsana use |
|----------------|----------------|
| `theta.panchanga.*` | Left panel: full pañcāṅga display. |
| `phi.label` | Shows "witness ← center-right → participant" indicator. |
| `phi.companion` | Shows which companion is active in the field. |
| `psi` | Adjusts interpretation tone. Arta = urgent guidance. Jñāni = contemplative. |
| `field_signals.coherence_peaks` | "Coherence top 5" in the left panel. |
| `sound.raga`, `sound.tala` | Display in field panel (informational, not generative). |
| `muhurta.*` | Timing display. |
| All `attestation` fields | Attestation badges on every displayed value. **This is the one surface where attestation is always visible.** |

**Critical rule:** Vyāsāsana never synthesizes across domains. It displays each domain's content and source separately. The `field_state_v1` provides shared coordinates; the `/observe` endpoint provides domain-separated readings. They serve different purposes.

---

## 4. Constraints

### What this does NOT do

- **Does not create a new endpoint.** `field_state_v1` is a key inside the existing `/field` response.
- **Does not move existing computation.** θ/φ already computed in `panchanga_to_coords()`. Tāla already computed in `generate_composition()`. We expose what exists.
- **Does not duplicate NPU logic.** Coherence peaks come from `ToroidalField.field_query()`. Directional bias is a simple element→direction map (6 lines), not NPU.
- **Does not change any surface.** This is a contract. Surfaces migrate to it at their own pace.
- **Does not break `/field`.** All existing keys remain. `field_state_v1` is additive.

### What surfaces must NOT do

- Compute θ or φ themselves (read from `field_state_v1.theta.theta_rad` / `phi.position`)
- Duplicate the nakshatra→tāla map (read from `sound.tala`)
- Re-derive coherence scores (read from `field_signals.coherence_peaks`)
- Hardcode directional weights (read from `field_signals.directional_bias`)

### What kernel.py must guarantee

- `field_state_v1` is present on every `/field` response
- θ and φ are computed once, here, not per-surface
- `attestation` is present on every derived signal
- `coherence_peaks` are from NPU, not fabricated
- `sound.gati` mapping is documented and stable

---

## 5. Migration Path

### Phase 1 (this spec): Define

- Write FIELDSTATE_V1.md ← you are here
- No code changes yet

### Phase 2: Emit

- Add `field_state_v1` key to `field_state()` output
- Add two helper functions: `_phi_to_label()`, `_phi_to_companion()`
- ~40 lines of additive Python in kernel.py

### Phase 3: Consume (per-surface, independent)

- Brahmāṇḍa: read `theta_rad` / `phi.position` instead of re-deriving
- Vāstu: read `directional_bias` instead of computing locally
- Talachakra: read `sound.tala` / `sound.gati` instead of deriving
- Vyāsāsana: read `field_signals` for left panel

Each surface migrates independently. No coordination required.
The old flat keys stay forever (or until all surfaces have migrated).

---

## Appendix: φ Label and Companion Derivation

```python
import math

def _phi_to_label(phi_rad):
    """Convert φ radians to human-readable position label."""
    if phi_rad is None:
        return "center"
    # Normalize to 0–2π
    phi = phi_rad % (2 * math.pi)
    if phi < math.pi / 8:
        return "far-left"
    elif phi < 3 * math.pi / 8:
        return "left"
    elif phi < 5 * math.pi / 8:
        return "center-left"
    elif phi < 7 * math.pi / 8:
        return "center"
    elif phi < 9 * math.pi / 8:
        return "center"
    elif phi < 11 * math.pi / 8:
        return "center-right"
    elif phi < 13 * math.pi / 8:
        return "right"
    elif phi < 15 * math.pi / 8:
        return "far-right"
    else:
        return "far-left"  # wraps


def _phi_to_companion(phi_rad):
    """Derive active companion from φ position."""
    if phi_rad is None:
        return None
    phi = phi_rad % (2 * math.pi)
    margin = math.pi / 6  # ~30° zone around center
    if abs(phi - math.pi) < margin:
        return "Bheruṇḍā"
    elif phi < math.pi:
        return "Shilpi"
    else:
        return "Bandhu"
```

---

✦ FieldState v1 · the shared spine · one field, four instruments
✦ The field tends itself. That IS Satya Yuga.
