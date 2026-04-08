"""
sound_engine.py — Sound specification derived from field state.

Audio analogue of ui_vastu_engine.py: single public function, validated output,
all keys guaranteed present, safe to send to SC without checks.

Hierarchy:
    kernel / build_field_state
        → field_state
        → field_to_sound  (graph traversal: nak→graha→raga, element→Sa)
        → sound_spec      (this module: mode-weighted layers + OSC messages)
        → osc_bridge      (fires to SC)

Modes:
    field   — minimal, always-on: tanpura + light melody
    daw     — full arrangement: all layers active
    ritual  — observance-aware: Ekadashi=drone only, festival=full
    compose — phrase engine active, generative, higher melody
    silence — drone only, no percussion
"""

from typing import Any, Dict, List


# ══════════════════════════════════════════════════════════
# CANONICAL LAYER WEIGHTS PER MODE
# ══════════════════════════════════════════════════════════

_LAYER_NAMES = ("tanpura", "melody", "tabla", "bija", "drone", "sympathetic")

_MODE_WEIGHTS = {
    "field": {
        "tanpura": 1.0, "melody": 0.2, "tabla": 0.0,
        "bija": 0.15, "drone": 0.0, "sympathetic": 0.1,
    },
    "daw": {
        "tanpura": 0.9, "melody": 0.6, "tabla": 0.5,
        "bija": 0.3, "drone": 0.2, "sympathetic": 0.4,
    },
    "ritual": {
        "tanpura": 1.0, "melody": 0.3, "tabla": 0.1,
        "bija": 0.4, "drone": 0.3, "sympathetic": 0.2,
    },
    "compose": {
        "tanpura": 0.8, "melody": 0.8, "tabla": 0.3,
        "bija": 0.2, "drone": 0.1, "sympathetic": 0.5,
    },
    "silence": {
        "tanpura": 0.6, "melody": 0.0, "tabla": 0.0,
        "bija": 0.0, "drone": 0.0, "sympathetic": 0.0,
    },
}

# Ekadashi overrides everything to drone-only
_EKADASHI_WEIGHTS = {
    "tanpura": 0.7, "melody": 0.0, "tabla": 0.0,
    "bija": 0.2, "drone": 0.4, "sympathetic": 0.0,
}

# Guna → master reverb/character
_GUNA_MASTER = {
    "sattva": {"reverb": 0.08, "decay": 0.8, "amp": 0.55},
    "rajas":  {"reverb": 0.15, "decay": 1.2, "amp": 0.65},
    "tamas":  {"reverb": 0.25, "decay": 2.0, "amp": 0.45},
}

# Element index for /atlas/field OSC message
_ELEM_IDX = {"earth": 0, "water": 1, "fire": 2, "air": 3, "ether": 4}
_GUNA_IDX = {"tamas": 0, "rajas": 1, "sattva": 2}

VALID_MODES = frozenset(_MODE_WEIGHTS.keys())


# ══════════════════════════════════════════════════════════
# INTERNAL HELPERS
# ══════════════════════════════════════════════════════════

def _resolve_sound_params(field_state: dict) -> dict:
    """Extract sa_hz, raga, tala, bpm, element, guna from field_state.

    Uses field_to_sound for graph traversal when possible,
    falls back to panchanga direct fields.
    """
    p = field_state.get("panchanga", {})
    ss = field_state.get("sound_state", {})

    # Try graph traversal
    try:
        from ..field_to_sound import field_to_sound, element_to_sa
        fts = field_to_sound(field_state)
        sa_hz = fts.get("sa_hz", 130.81)
        raga = fts.get("raga", "")
        element = fts.get("element", "ether")
        guna = fts.get("guna", "sattva")
        bija = fts.get("bija", "om")
        bija_path = fts.get("bija_path", [])
    except Exception:
        element = p.get("element", "ether").lower()
        guna = p.get("guna", "sattva").lower()
        from ..field_to_sound import element_to_sa
        sa_hz = element_to_sa(element)
        raga = ss.get("raga", p.get("devi_raga", ""))
        bija = "om"
        bija_path = []

    tala = ss.get("tala", "Adi")
    bpm = float(ss.get("bpm", p.get("tala_bpm", 72)))
    tradition = ss.get("tradition", "hindustani")

    return {
        "sa_hz": sa_hz,
        "raga": raga,
        "tala": tala,
        "bpm": bpm,
        "tradition": tradition,
        "element": element,
        "guna": guna,
        "bija": bija,
        "bija_path": bija_path,
    }


def _resolve_observance(field_state: dict) -> tuple:
    """Return (observance_name: str, is_ekadashi: bool)."""
    p = field_state.get("panchanga", {})
    obs_list = p.get("observances", [])
    if not obs_list:
        obs_list = field_state.get("observances", [])

    obs_name = ""
    obs_type = ""
    if obs_list and isinstance(obs_list, list) and obs_list[0]:
        obs_name = obs_list[0].get("name", obs_list[0].get("observance_name", ""))
        obs_type = obs_list[0].get("type", obs_list[0].get("observance_type", ""))

    ekadashi = obs_type == "ekadashi" or "ekadashi" in (p.get("tithi", "")).lower()
    return obs_name, ekadashi


def _compute_layers(mode: str, ekadashi: bool, coherence: float) -> dict:
    """Compute layer weights from mode, observance, and coherence score."""
    if ekadashi:
        base = dict(_EKADASHI_WEIGHTS)
    else:
        base = dict(_MODE_WEIGHTS.get(mode, _MODE_WEIGHTS["field"]))

    # Coherence modulates active layers (higher coherence → more melody/tabla)
    if mode in ("field", "ritual") and not ekadashi:
        base["melody"] = _clamp(base["melody"] * (0.5 + coherence))
        base["tabla"] = _clamp(base["tabla"] * coherence)
        base["sympathetic"] = _clamp(base["sympathetic"] * (0.3 + 0.7 * coherence))

    return {k: round(_clamp(v), 3) for k, v in base.items()}


def _compute_master(guna: str, mode: str) -> dict:
    """Master bus parameters from guna + mode."""
    master = dict(_GUNA_MASTER.get(guna, _GUNA_MASTER["rajas"]))

    if mode == "silence":
        master["amp"] = round(master["amp"] * 0.6, 3)
    elif mode == "daw":
        master["amp"] = round(min(0.85, master["amp"] * 1.2), 3)

    return {k: round(_clamp(v, 0.0, 1.0 if k != "decay" else 4.0), 3)
            for k, v in master.items()}


def _build_osc_messages(spec: dict) -> list:
    """Build ready-to-send OSC message list from resolved spec.

    Each entry: [osc_address, [arg1, arg2, ...]]
    Maps to atlas_synth.scd routes on port 57120.
    """
    msgs = []
    sa = spec["sa_hz"]
    layers = spec["layers"]
    master = spec["master"]
    element = spec.get("_element", "ether")
    guna = spec.get("_guna", "sattva")

    # /atlas/tanpura/sa — set Sa frequency
    msgs.append(["/atlas/tanpura/sa", [sa]])

    # /atlas/tanpura/amp — scale from tanpura layer weight
    msgs.append(["/atlas/tanpura/amp", [layers["tanpura"]]])

    # /atlas/bija — formant drone (freq, f1, f2, f3, amp)
    bija_path = spec.get("_bija_path", [])
    bija_amp = layers["bija"]
    if bija_path and bija_amp > 0.01:
        # Use first vowel's formants
        v = bija_path[0]
        msgs.append(["/atlas/bija", [
            sa, float(v.get("f1_hz", 800)), float(v.get("f2_hz", 1200)),
            float(v.get("f3_hz", 2500)), bija_amp,
        ]])
    else:
        msgs.append(["/atlas/bija", [sa, 800.0, 1200.0, 2500.0, bija_amp]])

    # /atlas/master — reverb, decay, amp
    msgs.append(["/atlas/master", [
        master["reverb"], master["decay"], master["amp"],
    ]])

    # /atlas/field — composite field update (sa, jivari, guna_idx, elem_idx)
    jivari = 0.4 if guna == "rajas" else 0.2 if guna == "sattva" else 0.55
    msgs.append(["/atlas/field", [
        sa, jivari,
        float(_GUNA_IDX.get(guna, 1)),
        float(_ELEM_IDX.get(element, 4)),
    ]])

    return msgs


# ══════════════════════════════════════════════════════════
# HARDENING HELPERS
# ══════════════════════════════════════════════════════════

def _clamp(v, lo: float = 0.0, hi: float = 1.0) -> float:
    try:
        return max(lo, min(hi, float(v)))
    except (TypeError, ValueError):
        return lo


def _validate_spec(spec: dict) -> dict:
    """Ensure all required keys exist with correct types.
    Never returns partial data. Mirrors ui_vastu_engine._validate_layout."""
    defaults = {
        "mode": "field",
        "sa_hz": 130.81,
        "raga": "",
        "tala": "Adi",
        "bpm": 72.0,
        "tradition": "hindustani",
        "layers": {k: 0.0 for k in _LAYER_NAMES},
        "observance": "",
        "ekadashi": False,
        "master": {"reverb": 0.15, "decay": 1.2, "amp": 0.55},
        "osc_messages": [],
        "attestation": "SYNTHESIS",
    }

    for key, default in defaults.items():
        if key not in spec or spec[key] is None:
            spec[key] = default
        elif isinstance(default, dict) and isinstance(spec[key], dict):
            for dk, dv in default.items():
                if dk not in spec[key]:
                    spec[key][dk] = dv

    # Clamp all numeric layer weights
    layers = spec["layers"]
    for k in _LAYER_NAMES:
        layers[k] = round(_clamp(layers.get(k, 0.0)), 3)

    # Clamp master
    m = spec["master"]
    m["reverb"] = round(_clamp(m.get("reverb", 0.15)), 3)
    m["decay"] = round(_clamp(m.get("decay", 1.2), 0.1, 4.0), 3)
    m["amp"] = round(_clamp(m.get("amp", 0.55)), 3)

    # Clamp sa_hz
    spec["sa_hz"] = round(_clamp(spec["sa_hz"], 32.0, 1000.0), 2)
    spec["bpm"] = round(_clamp(spec["bpm"], 20.0, 300.0), 1)

    # Mode must be valid
    if spec["mode"] not in VALID_MODES:
        spec["mode"] = "field"

    # Attestation always present
    spec["attestation"] = "SYNTHESIS"

    return spec


# ══════════════════════════════════════════════════════════
# PUBLIC API
# ══════════════════════════════════════════════════════════

def derive_sound_spec(field_state: dict, mode: str = "field") -> dict:
    """Derive complete sound specification from field state.

    Single function for sound computation. osc_bridge consumes the result;
    it never recomputes. Mirrors ui_vastu_engine.derive_ui_layout exactly.

    Args:
        field_state: dict with panchanga, sound_state, entities, observances.
        mode: one of 'field', 'daw', 'ritual', 'compose', 'silence'.

    Returns:
        Validated, SC-consumable sound spec. All keys guaranteed present.
        osc_messages list is ready to send without further processing.

    Layer weights are mode + coherence driven, not truth.
    attestation: SYNTHESIS — these are design decisions, not shastra.
    """
    if mode not in VALID_MODES:
        mode = "field"

    # Resolve sound params from graph traversal
    params = _resolve_sound_params(field_state)

    # Observance
    obs_name, ekadashi = _resolve_observance(field_state)

    # Ritual mode: Ekadashi forces drone-only regardless
    if mode == "ritual" and ekadashi:
        pass  # ekadashi flag handles it in _compute_layers

    # Coherence score — from psi or lifecycle
    psi = field_state.get("psi", {})
    coherence = _clamp(psi.get("intensity", psi.get("stability", 0.5)))

    # Trajectory — tempo and tabla modulation from temporal arc
    try:
        from ..field.trajectory_engine import derive_trajectory
        traj = derive_trajectory(field_state)
        traj_music = traj.get("musical_implication", {})
    except Exception:
        traj_music = {}

    tempo_mult = float(traj_music.get("tempo_multiplier", 1.0))
    params["bpm"] = round(params["bpm"] * tempo_mult, 1)

    # Trajectory overrides: Ekadashi proximity silences tabla
    if not traj_music.get("tabla_active", True):
        ekadashi = True  # forces drone-only layers

    # Compute layers
    layers = _compute_layers(mode, ekadashi, coherence)

    # Master bus
    master = _compute_master(params["guna"], mode)

    # Volume trend from trajectory
    vol_trend = traj_music.get("volume_trend", "stable")
    if vol_trend == "softening":
        master["amp"] = round(master["amp"] * 0.85, 3)
    elif vol_trend == "silence":
        master["amp"] = round(master["amp"] * 0.5, 3)

    # Assemble spec
    spec = {
        "mode": mode,
        "sa_hz": params["sa_hz"],
        "raga": params["raga"],
        "tala": params["tala"],
        "bpm": params["bpm"],
        "tradition": params["tradition"],
        "layers": layers,
        "observance": obs_name,
        "ekadashi": ekadashi,
        "master": master,
        "osc_messages": [],
        "attestation": "SYNTHESIS",
        # Internal fields for OSC builder (stripped after)
        "_element": params["element"],
        "_guna": params["guna"],
        "_bija_path": params.get("bija_path", []),
    }

    # Build OSC messages
    spec["osc_messages"] = _build_osc_messages(spec)

    # Strip internal fields
    spec.pop("_element", None)
    spec.pop("_guna", None)
    spec.pop("_bija_path", None)

    return _validate_spec(spec)
