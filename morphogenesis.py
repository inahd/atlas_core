"""
morphogenesis.py — derive a SceneGrammar from Atlas field_state.

Maps the live cosmological moment (panchanga, devi, graha, dasha, raga,
sound_state, wave field) to a complete, deterministic intent for the
morphogenesis playground:

    field_state  →  { elements, phase, sacred, intent }

The four derivation helpers compose:

    derive_morphogenesis_elements(field_state) → 6 element sliders 0..1
    derive_phase(field_state)                  → 1 of 7 phase strings
    derive_sacred(field_state)                 → vastu/yantra/mandala/phyllotaxy bundle
    derive_intent(field_state)                 → artistic SceneGrammar

A single entry point `derive_bundle(field_state)` returns the full
MorphogenesisBundle.  All functions are pure and deterministic — same
field_state in → same bundle out.  No `random.*` calls anywhere.
Randomness in the playground is the seed's job, not Atlas's.

Usage:

    from morphogenesis import derive_bundle
    bundle = derive_bundle(field_state)
    payload = bundle.as_dict()
    # → JSON-serializable for /field/morphogenesis or similar route
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import csv
import unicodedata
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────

def _norm(s: str) -> str:
    """Lower-case + strip diacritics, for matching panchanga values
    that may arrive as 'Bhagamālinī' or 'Bhagamalini'."""
    if not s:
        return ""
    nfkd = unicodedata.normalize("NFKD", str(s))
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower().strip()


def _safe_get(d: dict, *path, default=None):
    cur = d
    for k in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k)
        if cur is None:
            return default
    return cur


def _clamp01(v: float) -> float:
    if v < 0:
        return 0.0
    if v > 1:
        return 1.0
    return float(v)


# ─────────────────────────────────────────────────────────────────────
# Wave-field cues
# ─────────────────────────────────────────────────────────────────────
# Read drama / memory / revelation / void / structure from any of the
# wave-field data shapes Atlas might attach to field_state:
#   - field_state["chart"]["phase_pairs"]    (jyotisha_engine.compute_chart)
#   - field_state["phase_pairs"]              (alternate flat attach)
#   - field_state["chart"]["chladni_field"]
#   - field_state["chladni_field"]
#   - field_state["field_state_v1"]["field_signals"]   (always present)

def _wave_cues(field_state: dict) -> Dict[str, float]:
    """Extract five 0..1 axes describing the wave field's character.

    drama       — peak resonance amplitude (loudness)
    memory      — accumulated branch-memory tendency (persistence)
    revelation  — coherence / clarity (centred-strength)
    void        — peak cancellation amplitude (silence/destructive interference)
    structure   — how organised the active-vs-quiet nakshatra distribution is
    """
    # Try multiple locations for phase_pairs / wave field summary
    summary = (
        _safe_get(field_state, "chart", "phase_pairs", "field_summary")
        or _safe_get(field_state, "phase_pairs", "field_summary")
        or _safe_get(field_state, "wave_field", "field_summary")
        or {}
    )
    chladni = (
        _safe_get(field_state, "chart", "chladni_field")
        or _safe_get(field_state, "chladni_field")
        or {}
    )
    fsv1 = _safe_get(field_state, "field_state_v1") or {}
    signals = fsv1.get("field_signals") or {}

    # ── Drama: strongest single resonance amplitude ────────────────
    # Two-source amplitudes range up to ±2.0; we normalize.
    drama = 0.0
    res = summary.get("strongest_single_resonance") or {}
    amp = res.get("amplitude")
    if isinstance(amp, (int, float)):
        drama = abs(amp) / 2.0
    else:
        # Fallback: directional_bias variance (high variance ≈ dramatic field)
        bias = signals.get("directional_bias") or {}
        if bias:
            vals = list(bias.values())
            mean = sum(vals) / len(vals)
            var = sum((v - mean) ** 2 for v in vals) / len(vals)
            drama = _clamp01(var * 4)

    # ── Void: strongest cancellation amplitude ─────────────────────
    void = 0.0
    can = summary.get("strongest_single_cancellation") or {}
    cAmp = can.get("amplitude")
    if isinstance(cAmp, (int, float)):
        void = abs(cAmp) / 2.0

    # ── Revelation: coherence / centred-strength ───────────────────
    # field_state_v1.field_signals.center_strength is 0..1 already
    revelation = _clamp01(signals.get("center_strength", 0.3))

    # ── Memory: persistence proxy from active_nakshatras count.
    # Fewer "active" nakshatras with high amplitude → memory of long
    # accumulation in those positions; many active → fresh, low memory.
    memory = 0.0
    active = chladni.get("active_nakshatras")
    if isinstance(active, list) and len(active) > 0:
        # 27 total; concentration ratio
        memory = _clamp01(1 - (len(active) / 27))
    else:
        # Fallback: coherence_peaks count proportional to memory
        peaks = signals.get("coherence_peaks") or []
        if peaks:
            memory = _clamp01(0.3 + 0.05 * len(peaks))
        else:
            memory = 0.4

    # ── Structure: how organised the field is ──────────────────────
    # Use the field_vector from chladni_field if available; else fall
    # back to a flat 0.5.  High variance + small range = structured;
    # high variance + uniform spread = chaotic.
    structure = 0.5
    fv = chladni.get("field_vector")
    if isinstance(fv, list) and len(fv) > 0:
        mean = sum(fv) / len(fv)
        var = sum((v - mean) ** 2 for v in fv) / len(fv)
        # Pearson kurtosis approximation: peakedness → structure
        # Empirically, sigma in 0.0..0.4; map to 0..1.
        structure = _clamp01(var * 5)

    return {
        "drama": round(drama, 4),
        "memory": round(memory, 4),
        "revelation": round(revelation, 4),
        "void": round(void, 4),
        "structure": round(structure, 4),
    }


# ─────────────────────────────────────────────────────────────────────
# Element derivation
# ─────────────────────────────────────────────────────────────────────

# Graha → element bias (what a graha-coloured moment leans into)
_GRAHA_ELEMENT_BIAS = {
    # name (normalized) : (element_key, weight)
    "sun":     ("fire", 0.10),
    "surya":   ("fire", 0.10),
    "moon":    ("water", 0.12),
    "chandra": ("water", 0.12),
    "mars":    ("fire", 0.10),
    "mangala": ("fire", 0.10),
    "mercury": ("air", 0.10),
    "budha":   ("air", 0.10),
    "jupiter": ("ether", 0.12),
    "guru":    ("ether", 0.12),
    "venus":   ("water", 0.10),
    "shukra":  ("water", 0.10),
    "saturn":  ("earth", 0.15),
    "shani":   ("earth", 0.15),
    "rahu":    ("air", 0.10),
    "ketu":    ("ether", 0.10),
}


def derive_morphogenesis_elements(field_state: dict) -> Dict[str, float]:
    """Map panchanga + nakshatra-lord + devi + dasha into the six element
    sliders the playground consumes.  All values 0..1."""
    p = field_state.get("panchanga", {}) or {}
    elem = _norm(p.get("element"))
    guna = _norm(p.get("guna"))
    nak_lord = _norm(p.get("nak_lord"))
    devi_data = p.get("devi") or {}
    devi_elem = _norm(devi_data.get("element")) if isinstance(devi_data, dict) else ""

    # Mid-baseline so the playground doesn't sit at the panchanga floor
    elements = {
        "water": 0.30, "air": 0.30, "fire": 0.25,
        "earth": 0.25, "wood": 0.40, "ether": 0.30,
    }

    # Tithi element gets +0.20 toward its slider.  Wood is treated as
    # a structural slider (always present); earth/water boost moderately.
    elem_to_slider = {
        "water": "water", "air": "air", "fire": "fire",
        "earth": "earth", "ether": "ether",
    }
    if elem in elem_to_slider:
        elements[elem_to_slider[elem]] += 0.20

    # Devi element (often differs from tithi element) adds a smaller bias
    if devi_elem in elem_to_slider:
        elements[elem_to_slider[devi_elem]] += 0.10

    # Guna shifts
    if guna == "sattva":
        elements["ether"] += 0.15
        elements["water"] += 0.05
    elif guna == "rajas":
        elements["fire"] += 0.10
        elements["air"]  += 0.10
    elif guna == "tamas":
        elements["earth"] += 0.15
        elements["wood"]  += 0.05

    # Nakshatra lord shifts (graha colouring)
    bias = _GRAHA_ELEMENT_BIAS.get(nak_lord)
    if bias:
        key, w = bias
        elements[key] += w

    # Vara graha (weekday lord) — secondary
    vara = field_state.get("vara_graha") or {}
    vara_name = _norm(vara.get("name") or vara.get("name_key"))
    bias2 = _GRAHA_ELEMENT_BIAS.get(vara_name)
    if bias2:
        key, w = bias2
        elements[key] += w * 0.5

    # Dasha lord — yet another colouring (very subtle)
    dasha = field_state.get("dasha") or {}
    dasha_lord = _norm(dasha.get("lord"))
    bias3 = _GRAHA_ELEMENT_BIAS.get(dasha_lord)
    if bias3:
        key, w = bias3
        elements[key] += w * 0.3

    # Clamp
    return {k: round(_clamp01(v), 3) for k, v in elements.items()}


# ─────────────────────────────────────────────────────────────────────
# Phase derivation
# ─────────────────────────────────────────────────────────────────────

# Map tithi position within a paksha (0..14) to playground phase.
# Phase enum (must match atlas/grammar.js):
#   dormant · ignition · bloom · decay · collapse · memory · renewal

def derive_phase(field_state: dict) -> str:
    """Phase from tithi position in paksha.  Krishna paksha runs the
    second half of the cycle and emphasises decay/memory/renewal."""
    p = field_state.get("panchanga", {}) or {}
    tidx = p.get("tidx")
    if not isinstance(tidx, int):
        return "bloom"

    # tidx is 0..29 across the full lunar month; position in paksha is 0..14
    pos = tidx % 15
    paksha = _norm(p.get("paksha"))

    # Within a paksha:
    #   0–1   : dormant   (just past Amavasya/Purnima)
    #   2–6   : ignition+bloom (waxing/waning energy peak)
    #   7–10  : bloom (full)
    #   11–12 : decay
    #   13    : collapse
    #   14    : memory
    if pos <= 1:   base = "dormant"
    elif pos <= 4: base = "ignition"
    elif pos <= 9: base = "bloom"
    elif pos <= 11: base = "decay"
    elif pos <= 12: base = "collapse"
    elif pos == 13: base = "memory"
    else:          base = "renewal"

    # Krishna paksha: shift bloom-class to memory-class one notch
    # because the cosmological mood is dissolution-leaning
    if paksha in ("krsna", "krishna", "krishn"):
        if base == "bloom":     base = "decay"
        elif base == "ignition": base = "bloom"
        elif base == "decay":    base = "collapse"

    return base


# ─────────────────────────────────────────────────────────────────────
# Sacred-spatial derivation
# ─────────────────────────────────────────────────────────────────────
# The playground supports vastu / yantra / mandala / phyllotaxy as
# hidden field constraints.  The mappings here pick a canonical
# configuration from the current devi + nakshatra + coherence.

# Devi → yantra type (matches the geometries the 15 Nityas use in the
# Atlas geometry table; see static/morphogenesis/atlas/yantra.js for
# the available masks).
_DEVI_YANTRA = {
    "kameshvari":         "triangle_up",
    "bhagamalini":        "shatkona",
    "nityaklinna":        "triangle_down",
    "bherunda":           "triangle_up",
    "vahnivasini":        "lotus_8",
    "mahavajreshvari":    "shatkona",
    "sivaduti":           "circle",
    "shivaduti":          "circle",
    "tvarita":            "lotus_8",
    "kulasundari":        "lotus_8",
    "nitya":              "lotus_12",
    "nilapataka":         "circle",
    "vijaya":             "triangle_up",
    "sarvangasundari":    "lotus_12",
    "sarvamangala":       "lotus_12",
    "jvalamalini":        "lotus_12",
    "jwalamalini":        "lotus_12",
    "citra":              "sri_yantra_lite",
    "chitra":             "sri_yantra_lite",
}


def derive_sacred(field_state: dict) -> Dict[str, Any]:
    """Pick a sacred-spatial configuration from the live moment.

    Returns the bundle the playground frontend's `applyMode` function
    consumes (matches the `sacred:` block of static/morphogenesis/atlas/modes.js).
    """
    p = field_state.get("panchanga", {}) or {}
    devi_data = p.get("devi") or {}
    devi_name = _norm(devi_data.get("name") if isinstance(devi_data, dict) else "")
    paksha = _norm(p.get("paksha"))
    tidx = p.get("tidx") if isinstance(p.get("tidx"), int) else 14
    cues = _wave_cues(field_state)

    # Yantra type from the 15-Nitya mapping; fallback to a benign shape
    yantra_type = _DEVI_YANTRA.get(devi_name, "circle")

    # Mandala rings — proportional to coherence-peak count (a proxy for
    # how many concentric "shells" the current moment supports)
    fsv1 = _safe_get(field_state, "field_state_v1") or {}
    peaks = (fsv1.get("field_signals") or {}).get("coherence_peaks") or []
    n_peaks = len(peaks)
    if n_peaks == 0:
        mandala_rings = 0
    else:
        mandala_rings = max(0, min(7, 1 + n_peaks // 2))

    # Mandala gates — 0 in dormant/decay, 4 cardinal during bloom/renewal
    phase = derive_phase(field_state)
    if phase in ("bloom", "renewal"):
        mandala_gates = 4
    elif phase in ("ignition", "memory"):
        mandala_gates = 2
    else:
        mandala_gates = 0

    # Mandala invert — true when in krishna paksha + late-cycle
    # (root-direction descent matches the cosmological mood)
    mandala_invert = (paksha in ("krsna", "krishna", "krishn")) and (tidx % 15) >= 11

    # Strengths driven by clarity and dramatic axes
    master_strength  = round(0.45 + 0.30 * cues["revelation"], 3)
    vastu_strength   = round(0.40 + 0.30 * cues["structure"], 3)
    yantra_strength  = round(0.40 + 0.40 * cues["revelation"], 3)
    mandala_strength = round(0.30 + 0.40 * cues["structure"], 3) if mandala_rings else 0.0

    # Phyllotaxy — engage when air or wood is high enough that
    # golden-spiral dispersal makes structural sense
    elements = derive_morphogenesis_elements(field_state)
    enable_phyllo = (elements["air"] + elements["wood"]) > 1.0
    phyllo_count = max(16, min(80, int(24 + 80 * elements["wood"])))
    phyllo_scale = round(2.5 + 4 * elements["fire"], 2)

    return {
        "masterStrength":  master_strength,
        "vastuStrength":   vastu_strength,
        "yantraType":      yantra_type,
        "yantraStrength":  yantra_strength,
        "mandalaStrength": mandala_strength,
        "mandalaRings":    mandala_rings,
        "mandalaGates":    mandala_gates,
        "mandalaInvert":   bool(mandala_invert),
        "phyllotaxy": {
            "enabled": bool(enable_phyllo),
            "count":   phyllo_count,
            "scale":   phyllo_scale,
        },
    }


# ─────────────────────────────────────────────────────────────────────
# Intent — the artistic SceneGrammar
# ─────────────────────────────────────────────────────────────────────

# The 8 intentions, the 6 symmetries, the 7 hidden forms
INTENTIONS = [
    "bloom", "discharge", "gestation", "revelation",
    "dissolution", "inversion", "fossilization", "swarm",
]
SYMMETRIES = ["none", "bilateral", "radial", "spiral", "hexagonal", "quasicrystal"]
HIDDEN_FORMS = [
    "none", "cosmic_body", "flower", "twin_current",
    "inverted_tree", "gem_lattice", "insect_swarm",
]

# Per-intention transformation goal — short imperative phrase
# describing what the field is becoming.
_TRANSFORM_GOAL = {
    "bloom":         "water → vein → flower",
    "discharge":     "wood → branch → lightning",
    "gestation":     "moisture → density → membrane",
    "revelation":    "ether → coherence → eye",
    "dissolution":   "earth → ash → smoke",
    "inversion":     "tree → root → underworld",
    "fossilization": "tissue → mineral → memory",
    "swarm":         "wind → seed → swarm",
}

# Per-intention default hidden form
_INTENTION_FORM = {
    "bloom":         "flower",
    "discharge":     "twin_current",
    "gestation":     "cosmic_body",
    "revelation":    "cosmic_body",
    "dissolution":   "none",
    "inversion":     "inverted_tree",
    "fossilization": "gem_lattice",
    "swarm":         "insect_swarm",
}

# Yantra type → preferred symmetry mode
_YANTRA_SYMMETRY = {
    "none":            "none",
    "bindu":           "radial",
    "circle":          "radial",
    "triangle_up":     "bilateral",
    "triangle_down":   "bilateral",
    "shatkona":        "hexagonal",
    "square":          "bilateral",
    "lotus_8":         "radial",
    "lotus_12":        "radial",
    "sri_yantra_lite": "quasicrystal",
}

# Phase → tick within the playground's 3000-tick cycle where the
# scene is expected to be at peak expression
_PHASE_CLIMAX = {
    "dormant":  150,
    "ignition": 500,
    "bloom":    1000,
    "decay":    1800,
    "collapse": 2350,
    "memory":   2650,
    "renewal":  2900,
}


def derive_intent(field_state: dict) -> Dict[str, Any]:
    """Derive a complete artistic SceneGrammar for the morphogenesis
    playground.  Deterministic, pure function.

    Composes elements + phase + sacred + wave cues into a single
    intent describing what the scene is *trying* to express right now.
    """
    elements = derive_morphogenesis_elements(field_state)
    phase = derive_phase(field_state)
    sacred = derive_sacred(field_state)
    cues = _wave_cues(field_state)

    # ── Intention scoring ──────────────────────────────────────────
    # Each intention scored as a weighted sum of element values + phase
    # affinity + wave cues.  No tiebreak randomness — alphabetical
    # ordering of `INTENTIONS` resolves ties deterministically.
    e = elements
    scores: Dict[str, float] = {}

    scores["bloom"] = (
        e["water"] + e["wood"] + 0.5 * e["ether"]
        + (1.5 if phase == "bloom" else 0)
        + 0.6 * cues["revelation"]
        + 0.3 * cues["structure"]
    )
    scores["discharge"] = (
        e["fire"] + e["air"]
        + 1.4 * cues["drama"]
        + (1.0 if phase == "ignition" else 0)
    )
    scores["gestation"] = (
        e["water"] + e["earth"] + 0.4 * e["wood"]
        + (1.5 if phase == "dormant" else 0)
        + (0.8 if phase == "memory" else 0)
        + 0.5 * cues["memory"]
    )
    scores["revelation"] = (
        e["ether"] + 0.6 * e["air"]
        + 1.6 * cues["revelation"]
        + (1.0 if phase == "renewal" else 0)
    )
    scores["dissolution"] = (
        e["water"] + e["fire"]
        + (1.5 if phase == "collapse" else 0)
        + 1.4 * cues["void"]
    )
    scores["inversion"] = (
        e["earth"] + 0.7 * e["ether"]
        + (1.5 if phase == "memory" else 0)
        + 0.7 * cues["void"]
        + (0.6 if sacred.get("mandalaInvert") else 0)
    )
    scores["fossilization"] = (
        1.4 * e["earth"]
        + 1.4 * cues["structure"]
        + (1.0 if phase == "decay" else 0)
        + 0.5 * cues["memory"]
    )
    scores["swarm"] = (
        e["air"] + 0.7 * e["fire"] + e["wood"]
        + 0.8 * cues["drama"]
        + (0.4 if sacred.get("phyllotaxy", {}).get("enabled") else 0)
    )

    # Pick max — deterministic; INTENTIONS list order resolves ties
    intention = max(INTENTIONS, key=lambda k: (scores[k], -INTENTIONS.index(k)))

    # ── Symmetry derivation ────────────────────────────────────────
    # Anchor on yantra type, but lift to spiral / quasicrystal when
    # the cues call for it.
    yantra_type = sacred.get("yantraType", "none")
    symmetry = _YANTRA_SYMMETRY.get(yantra_type, "none")
    if cues["structure"] > 0.65 and intention in ("bloom", "revelation"):
        symmetry = "spiral"
    if intention == "swarm" and cues["drama"] > 0.5:
        symmetry = "none"
    if intention == "fossilization" and cues["structure"] > 0.7:
        symmetry = "quasicrystal"
    if symmetry not in SYMMETRIES:
        symmetry = "none"

    # ── Hidden form ────────────────────────────────────────────────
    hidden_form = _INTENTION_FORM.get(intention, "none")
    # cosmic_body upgrade when ether is very high regardless of intention
    if e["ether"] > 0.85 and intention not in ("dissolution",):
        hidden_form = "cosmic_body"

    # ── Transformation goal ────────────────────────────────────────
    transformation_goal = _TRANSFORM_GOAL.get(intention, "field → form → field")

    # ── Event density ──────────────────────────────────────────────
    # 0..1; how busy the scene should be
    event_density = _clamp01(
        0.35
        + 0.25 * e["fire"]
        + 0.25 * e["wood"]
        + 0.20 * cues["drama"]
        - 0.15 * cues["void"]
    )

    # ── Climax tick ────────────────────────────────────────────────
    climax_tick = _PHASE_CLIMAX.get(phase, 1000)

    return {
        "intention":          intention,
        "phase":              phase,
        "symmetry":           symmetry,
        "hiddenForm":         hidden_form,
        "transformationGoal": transformation_goal,
        "eventDensity":       round(event_density, 3),
        "drama":              cues["drama"],
        "memory":             cues["memory"],
        "revelation":         cues["revelation"],
        "void":               cues["void"],
        "structure":          cues["structure"],
        "climaxTick":         climax_tick,
        "_scores":            {k: round(v, 3) for k, v in scores.items()},
    }


# ─────────────────────────────────────────────────────────────────────
# Body archetype map — embodiment lookup
# ─────────────────────────────────────────────────────────────────────
# v0.6 layer: a body region is selected by panchanga.body_region +
# marma + intent + tithi phase, and yields the full embodiment context
# (asana, pranayama, marma point, render geometry, dhatu, animation
# pattern, color, cycle).  The frontend uses this to bend the field
# under hidden posture geometry — never to draw a yoga pose literally.

_BODY_ARCHETYPE_ROWS: Optional[List[Dict[str, str]]] = None


def _load_body_archetype_map() -> List[Dict[str, str]]:
    """Lazy-load datasets/morphogenesis/body_archetype_map.csv (cached)."""
    global _BODY_ARCHETYPE_ROWS
    if _BODY_ARCHETYPE_ROWS is None:
        path = Path(__file__).parent / "datasets" / "morphogenesis" / "body_archetype_map.csv"
        with path.open(encoding="utf-8") as f:
            _BODY_ARCHETYPE_ROWS = list(csv.DictReader(f))
    return _BODY_ARCHETYPE_ROWS


# Map nakshatra body_region word → CSV row name.
# panchanga returns "neck", "chest", etc.; CSV uses "cervical_spine", etc.
_BODY_REGION_KEYWORD_MAP = {
    "neck":    "cervical_spine", "throat":  "cervical_spine",
    "head":    "skull_vault",    "skull":   "skull_vault", "crown": "skull_vault",
    "chest":   "heart_muscle",   "heart":   "heart_muscle",
    "eye":     "eye_socket",     "eyes":    "eye_socket",
    "ear":     "cochlea",        "ears":    "cochlea",
    "nose":    "nasal_cavity",
    "jaw":     "jaw_masseter",
    "shoulder":"clavicle",       "shoulders":"clavicle",
    "arm":     "humerus",        "arms":    "humerus",
    "forearm": "radius_ulna",    "forearms":"radius_ulna",
    "wrist":   "carpals",
    "hand":    "phalanges",      "hands":   "phalanges", "finger": "phalanges",
    "fingers": "phalanges",
    "spine":   "thoracic_spine", "back":    "thoracic_spine",
    "rib":     "ribs",           "ribs":    "ribs",       "sternum":"sternum",
    "abdomen": "pelvis",         "navel":   "lumbar_spine", "stomach": "lumbar_spine",
    "pelvis":  "pelvis",         "hip":     "pelvis",     "hips":   "pelvis",
    "thigh":   "femur",          "thighs":  "femur",      "knee":   "femur",
    "calf":    "tibia_fibula",   "shin":    "tibia_fibula", "shins": "tibia_fibula",
    "foot":    "tarsals",        "feet":    "tarsals",
    "skin":    "skin_surface",   "fascia":  "fascia_network",
    "lung":    "lung_bronchial", "lungs":   "lung_bronchial",
}

# Per-intention preferred body region (used as fallback)
_INTENT_BODY_PREF = {
    "discharge":     "iris",
    "fossilization": "femur",
    "bloom":         "heart_muscle",
    "revelation":    "skull_vault",
    "swarm":         "phalanges",
    "dissolution":   "skin_surface",
    "gestation":     "pelvis",
    "inversion":     "tarsals",
}


def _match_marma(rows: List[Dict[str, str]], marma_name: str) -> Optional[Dict[str, str]]:
    """Try to find a CSV row whose marma_at_this_region matches marma_name.
    The CSV uses '/'-separated lists like 'Nila/Manya'; check both halves."""
    if not marma_name:
        return None
    marma_norm = marma_name.strip()
    candidates = [marma_norm] + [p.strip() for p in marma_norm.split("/")]
    for row in rows:
        cell = (row.get("marma_at_this_region") or "").strip()
        if not cell:
            continue
        cell_parts = [p.strip() for p in cell.split("/")]
        for c in candidates:
            if c and c in cell_parts:
                return row
    return None


def derive_embodiment(field_state: dict, intent: dict,
                      material_signature: Optional[dict] = None) -> Dict[str, Any]:
    """Pick an active body region by nakshatra body_region + marma +
    intent + tithi phase.  Returns the full embodiment context that the
    frontend uses to bend the field under hidden posture geometry.

    `material_signature` should be the bhasma_stage dict; when supplied,
    it modulates animation_cycle_ms (firing speeds up, dormancy slows).
    """
    rows = _load_body_archetype_map()
    by_region = {r["body_region"]: r for r in rows}
    selected: Optional[Dict[str, str]] = None

    p = field_state.get("panchanga", {}) or {}

    # Step 1 — match by today's marma (most specific)
    marma_today = field_state.get("marma_today") or {}
    marma_name = (marma_today.get("marma_name") or "").strip()
    selected = _match_marma(rows, marma_name)

    # Step 2 — panchanga.body_region keyword → CSV row
    if not selected:
        body_word = _norm(p.get("body_region"))
        target = _BODY_REGION_KEYWORD_MAP.get(body_word)
        if target and target in by_region:
            selected = by_region[target]

    # Step 3 — nak_data.body_region keyword (often duplicates panchanga
    # but provides a fallback shape)
    if not selected:
        nak = p.get("nak_data") or {}
        body_word = _norm(nak.get("body_region"))
        target = _BODY_REGION_KEYWORD_MAP.get(body_word)
        if target and target in by_region:
            selected = by_region[target]

    # Step 4 — intent-driven preference
    if not selected:
        intention = (intent or {}).get("intention", "bloom")
        target = _INTENT_BODY_PREF.get(intention, "heart_muscle")
        if target in by_region:
            selected = by_region[target]

    # Final fallback
    if not selected:
        selected = by_region.get("heart_muscle") or rows[0]

    color_primary = selected.get("color_primary") or "#FFB300"
    color_secondary = selected.get("color_secondary") or "#445566"
    animation_pattern = selected.get("animation_pattern") or "pulse_outward"
    try:
        cycle_ms = int(selected.get("animation_cycle_ms") or 5000)
    except (TypeError, ValueError):
        cycle_ms = 5000

    # Bhasma-stage modulation of cycle (puta_agni speeds, marana slows,
    # dormant_seed slows further).  Material colour stays the row's.
    if material_signature:
        stage = material_signature.get("stage", "")
        if stage == "puta_agni":
            cycle_ms = max(800, int(cycle_ms * 0.65))
        elif stage == "mardana":
            cycle_ms = max(800, int(cycle_ms * 0.85))
        elif stage == "marana":
            cycle_ms = int(cycle_ms * 1.30)
        elif stage == "dormant_seed":
            cycle_ms = int(cycle_ms * 1.60)

    return {
        "body_region":           selected.get("body_region"),
        "archetype":             selected.get("archetype"),
        "graha":                 selected.get("graha"),
        "dhatu":                 selected.get("dhatu"),
        "mathematical_equation": selected.get("mathematical_equation"),
        "render_geometry":       selected.get("render_geometry"),
        "asana_that_loads":      selected.get("asana_that_loads") or None,
        "pranayama_that_loads":  selected.get("pranayama_that_loads") or None,
        "marma_at_this_region":  selected.get("marma_at_this_region") or None,
        "color_primary":         color_primary,
        "color_secondary":       color_secondary,
        "animation_pattern":     animation_pattern,
        "animation_cycle_ms":    int(cycle_ms),
    }


# ─────────────────────────────────────────────────────────────────────
# Bhasma transformation stage
# ─────────────────────────────────────────────────────────────────────
# Map tithi position + paksha to one of nine rasaśāstra stages.  Each
# stage carries a material_action (string) and visual_operators (dict
# of pass-modulation parameters the frontend reads).
#
#   Shukla cycle  (building, purifying, firing, extracting)
#     0–2  shodhana       — purification rinse (5-media wash)
#     3–5  mardana        — turbulent grinding/kneading
#     6–8  bhavana        — moisture embedding (herb juice trituration)
#     9–11 puta_agni      — calcination by fire (the puta cycle)
#     12–13 sattva_extraction — essence drawing upward
#     14   stabilization  — full moon hold
#
#   Krishna cycle (settling, dissolving, returning)
#     0–2  marana         — mineralization, the death-pass
#     3–5  amritikarana   — nectar revival
#     6–8  dormant_seed   — bīja resting
#     9–14 (cycle re-begins) shodhana → mardana → ...

_BHASMA_VISUAL_OPS = {
    "shodhana": {
        "diffusion_boost": 1.40, "smoothing": 1.20,
        "moisture_rise": 1.20, "heat_drain": 0.85,
    },
    "mardana": {
        "advection_boost": 1.50, "shear_boost": 1.30, "structure_break": 1.20,
    },
    "bhavana": {
        "moisture_lock": 1.50, "diffusion_boost": 1.20, "branch_acc_boost": 1.30,
    },
    "puta_agni": {
        "heat_spike": 1.80, "charge_boost": 1.40, "discharge_boost": 1.30,
        "moisture_drain": 0.60,
    },
    "sattva_extraction": {
        "coherence_lift": 1.50, "life_lift": 1.30, "void_intensify": 1.20,
    },
    "stabilization": {
        "flow_dampen": 0.70, "tensegrity_lock": 1.0, "all_decay_slow": 1.0,
    },
    "marana": {
        "rigidity_boost": 1.60, "density_lock": 1.30, "life_drain": 0.70,
    },
    "amritikarana": {
        "life_lift": 1.50, "coherence_lift": 1.40, "moisture_lift": 1.30,
        "heat_balance": 1.0,
    },
    "dormant_seed": {
        "all_decay_strong": 0.92, "history_alpha_high": 1.0, "low_energy": 0.60,
    },
}

_BHASMA_ACTION = {
    "shodhana":      "shodhana — purification rinse",
    "mardana":       "mardana — turbulent grinding",
    "bhavana":       "bhavana — moisture embedding",
    "puta_agni":     "puta — calcination by fire",
    "sattva_extraction": "sattva-paatana — essence extraction",
    "stabilization": "stabilization — held coherence",
    "marana":        "marana — mineralization, the death-pass",
    "amritikarana":  "amritikarana — nectar revival",
    "dormant_seed":  "bīja — seed in dormancy",
}


def derive_bhasma_stage(field_state: dict) -> Dict[str, Any]:
    """Map tithi + paksha to bhasma transformation stage."""
    p = field_state.get("panchanga", {}) or {}
    tidx = p.get("tidx") if isinstance(p.get("tidx"), int) else 14
    paksha = _norm(p.get("paksha"))
    pos = tidx % 15
    is_krishna = paksha in ("krsna", "krishna", "krishn")

    if pos == 14:
        stage = "stabilization"
    elif not is_krishna:
        # Shukla — refining cycle
        if pos < 3:    stage = "shodhana"
        elif pos < 6:  stage = "mardana"
        elif pos < 9:  stage = "bhavana"
        elif pos < 12: stage = "puta_agni"
        else:          stage = "sattva_extraction"
    else:
        # Krishna — settling cycle
        if pos < 3:    stage = "marana"
        elif pos < 6:  stage = "amritikarana"
        elif pos < 9:  stage = "dormant_seed"
        elif pos < 12: stage = "shodhana"      # cycle restart
        else:          stage = "mardana"

    return {
        "stage":            stage,
        "material_action":  _BHASMA_ACTION[stage],
        "visual_operators": dict(_BHASMA_VISUAL_OPS[stage]),
        "tithi_pos":        pos,
        "paksha":           "Krishna" if is_krishna else "Shukla",
    }


# ─────────────────────────────────────────────────────────────────────
# Quasicrystal activation
# ─────────────────────────────────────────────────────────────────────
# A quasicrystal substrate becomes active when:
#   - intent.intention is "fossilization" or "revelation"
#   - OR pressure(structure) + coherence(revelation) + memory all elevated
#
# Active fold count is chosen to match the intention's natural symmetry:
#   revelation    → 11 (Nilapataka, Sri Yantra peak alignment)
#   fossilization →  7 (Sivaduti, mineral precision)
#   high memory   →  5 (Penrose)
#   high coherence→  8 (Ammann-Beenker)
#   else          → 11 (default to the highest planetary prime)

def derive_quasicrystal(field_state: dict, intent: dict) -> Dict[str, Any]:
    cues = _wave_cues(field_state)
    intention = (intent or {}).get("intention", "")

    pressure_proxy = cues["structure"]
    coherence = cues["revelation"]
    memory = cues["memory"]

    active = (
        intention in ("fossilization", "revelation") or
        (pressure_proxy > 0.55 and coherence > 0.50 and memory > 0.45)
    )

    if intention == "revelation":
        fold = 11
    elif intention == "fossilization":
        fold = 7
    elif memory > 0.7:
        fold = 5
    elif coherence > 0.65:
        fold = 8
    elif pressure_proxy > 0.6:
        fold = 9
    else:
        fold = 11

    if active:
        strength = 0.40 + 0.30 * (pressure_proxy + coherence + memory) / 3
        if intention == "revelation":
            strength = max(strength, 0.70)
        elif intention == "fossilization":
            strength = max(strength, 0.60)
    else:
        strength = 0.0

    if intention in ("fossilization", "revelation"):
        rationale = f"intention={intention}"
    elif active:
        rationale = "high pressure+coherence+memory"
    else:
        rationale = "off"

    return {
        "active":           bool(active),
        "fold":             int(fold),
        "strength":         round(strength, 3),
        "phason_amplitude": round(0.20 + 0.50 * memory, 3),
        "rationale":        rationale,
    }


# ─────────────────────────────────────────────────────────────────────
# MorphogenesisBundle
# ─────────────────────────────────────────────────────────────────────

@dataclass
class MorphogenesisBundle:
    """Complete morphogenesis configuration for the playground frontend.

    v0.6: now includes embodiment, bhasma_stage, and quasicrystal layers
    in addition to the v0.5 elements/phase/sacred/intent.  `as_dict()`
    returns a JSON-serializable bundle suitable for /field/morphogenesis.
    """
    elements: Dict[str, float]
    phase: str
    sacred: Dict[str, Any]
    intent: Dict[str, Any]
    embodiment: Dict[str, Any]
    bhasma_stage: Dict[str, Any]
    quasicrystal: Dict[str, Any]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "elements":     self.elements,
            "phase":        self.phase,
            "sacred":       self.sacred,
            "intent":       self.intent,
            "embodiment":   self.embodiment,
            "bhasma_stage": self.bhasma_stage,
            "quasicrystal": self.quasicrystal,
        }


def derive_bundle(field_state: dict) -> MorphogenesisBundle:
    """Single entry point — the full deterministic bundle from a
    field_state dict.  Pure, no side effects, no randomness.

    Composition order (each step may consume earlier results):
        elements ─┐
        phase    ─┤
        sacred   ─┤
        intent   ─┴→ bhasma_stage → embodiment ←─┘
                          ↓
                     quasicrystal (consults intent + cues)
    """
    elements = derive_morphogenesis_elements(field_state)
    phase = derive_phase(field_state)
    sacred = derive_sacred(field_state)
    intent = derive_intent(field_state)
    bhasma_stage = derive_bhasma_stage(field_state)
    embodiment = derive_embodiment(field_state, intent, bhasma_stage)
    quasicrystal = derive_quasicrystal(field_state, intent)

    return MorphogenesisBundle(
        elements=elements,
        phase=phase,
        sacred=sacred,
        intent=intent,
        embodiment=embodiment,
        bhasma_stage=bhasma_stage,
        quasicrystal=quasicrystal,
    )


# ─────────────────────────────────────────────────────────────────────
# CLI inspection
# ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) > 1 and sys.argv[1] not in ("--live", "-l"):
        # Read field_state JSON from a file path
        with open(sys.argv[1], encoding="utf-8") as f:
            field_state = json.load(f)
    else:
        # Pull live from localhost:5000/field
        import urllib.request
        with urllib.request.urlopen("http://localhost:5000/field", timeout=3) as r:
            field_state = json.loads(r.read().decode("utf-8"))

    bundle = derive_bundle(field_state)
    print(json.dumps(bundle.as_dict(), indent=2, ensure_ascii=False))
