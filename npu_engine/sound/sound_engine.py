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
        "tanpura": 1.0, "melody": 0.2, "tabla": 0.25,
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

    # Enrich with wave field data (non-blocking — failures are silent)
    try:
        _enrich_with_wave_field(spec)
    except Exception:
        pass  # wave data is optional; sound continues without it

    # Strip internal fields
    spec.pop("_element", None)
    spec.pop("_guna", None)
    spec.pop("_bija_path", None)

    return _validate_spec(spec)


# ══════════════════════════════════════════════════════════
# WAVE FIELD ENRICHMENT
# ══════════════════════════════════════════════════════════

# Nakshatra → suggested raga mapping
_NAK_RAGA = {
    'Ashwini': 'Bilawal', 'Bharani': 'Kalyani', 'Krittika': 'Todi',
    'Rohini': 'Bhairavi', 'Mrigashira': 'Hindol', 'Ardra': 'Darbari',
    'Punarvasu': 'Yaman', 'Pushya': 'Kafi', 'Ashlesha': 'Bhairav',
    'Magha': 'Marwa', 'Purva Phalguni': 'Puriya', 'Uttara Phalguni': 'Bihag',
    'Hasta': 'Miyan ki Todi', 'Chitra': 'Ahir Bhairav', 'Swati': 'Desh',
    'Vishakha': 'Jaunpuri', 'Anuradha': 'Malkauns', 'Jyeshtha': 'Bageshri',
    'Mula': 'Shree', 'Purva Ashadha': 'Kedar', 'Uttara Ashadha': 'Hamir',
    'Shravana': 'Durga', 'Dhanishta': 'Sarang', 'Shatabhisha': 'Lalit',
    'Purva Bhadrapada': 'Basant', 'Uttara Bhadrapada': 'Jayjaywanti',
    'Revati': 'Hansadhwani',
}

# Dominant harmonic → tanpura partial emphasis
_K_TO_PARTIAL = {
    1: 'sa', 3: 'ga', 4: 'ma', 6: 'dha', 7: 'ni', 12: 'pa',
}

_K_LABELS = {1: 'conjunction', 2: 'opposition', 3: 'trine', 4: 'square',
             6: 'sextile', 7: 'septile', 12: 'rashi'}

_WAVE_K_VALUES = [1, 3, 4, 6, 7, 12]


def _enrich_with_wave_field(spec: dict):
    """Add wave field data to the sound spec. Non-destructive — only adds keys."""
    import math
    from itertools import combinations
    from datetime import datetime, timezone

    try:
        from npu_engine.jyotisha_engine import compute_chart, compute_pair_interference
    except ImportError:
        return  # jyotish engine not available

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    try:
        chart = compute_chart(now, 29.65, -82.32)
    except Exception:
        return

    grahas = chart.get('grahas', {})
    if not grahas or 'Moon' not in grahas:
        return

    moon = grahas['Moon']
    moon_long = moon['deg_absolute']
    moon_nak = moon.get('nakshatra', '')
    nak_size = 360.0 / 27.0
    moon_nak_mid = (int(moon_long / nak_size)) * nak_size + nak_size / 2

    # 1. Raga from Moon nakshatra (suggestion only)
    wave_raga = _NAK_RAGA.get(moon_nak, '')
    if wave_raga and not spec.get('raga'):
        spec['raga'] = wave_raga
    spec['wave_raga'] = wave_raga
    spec['wave_moon_nak'] = moon_nak

    # 2. Gamak intensity from wave activation at Moon's nak midpoint
    graha_names = [g for g in grahas if g != 'Moon']
    pairs = list(combinations(graha_names, 2))

    activation = 0.0
    k_scores = {k: 0.0 for k in _WAVE_K_VALUES}
    peak_amp = 0.0
    peak_pair = ''
    peak_k = 0

    for a, b in pairs:
        lon_a = grahas[a]['deg_absolute']
        lon_b = grahas[b]['deg_absolute']
        for k in _WAVE_K_VALUES:
            amp = compute_pair_interference(lon_a, lon_b, moon_nak_mid, k)
            abs_amp = abs(amp)
            activation += abs_amp
            k_scores[k] += abs_amp
            if abs_amp > peak_amp:
                peak_amp = abs_amp
                peak_pair = f"{a}-{b}"
                peak_k = k

    # Normalize (28 pairs × 6 k-values × max amp 2 = 336 theoretical max)
    max_possible = len(pairs) * len(_WAVE_K_VALUES) * 2.0
    gamak_intensity = min(activation / max_possible, 1.0) if max_possible > 0 else 0.5

    spec['wave_gamak_intensity'] = round(gamak_intensity, 3)
    spec['wave_peak_pair'] = peak_pair
    spec['wave_peak_k'] = peak_k

    # 3. Tempo from tithi phase
    tithi = chart.get('tithi', {})
    phase = tithi.get('sun_moon_phase_deg', 180)
    wave_bpm = 81 + 27 * math.sin(math.radians(phase))
    spec['wave_bpm'] = round(wave_bpm, 1)

    # Blend into existing bpm
    existing_bpm = spec.get('bpm', 72)
    spec['bpm'] = round(0.7 * existing_bpm + 0.3 * wave_bpm, 1)

    # 4. Dominant harmonic → partial emphasis
    dominant_k = max(k_scores, key=k_scores.get) if k_scores else 12
    spec['wave_partial'] = _K_TO_PARTIAL.get(dominant_k, 'pa')
    spec['wave_dominant_k'] = dominant_k
    spec['wave_dominant_k_name'] = _K_LABELS.get(dominant_k, f'k={dominant_k}')

    # 5. Pair interference → interval mix (partial ratios + amplitudes)
    interval_mix = _compute_interval_mix(grahas, moon_nak_mid, k_scores)
    spec['wave_interval_mix'] = interval_mix

    # 6. Planetary prime rhythm mode
    rhythm = _compute_rhythm_mode(k_scores)
    spec['wave_rhythm_mode'] = rhythm

    # 7. Natal tonal filter
    natal_filter = _compute_natal_filter(gamak_intensity)
    spec['wave_natal_filter'] = natal_filter

    # 8. Breath cycle micro-variation
    breath = _compute_breath(gamak_intensity, phase)
    spec['wave_breath'] = breath

    # 9. Tempo: wider range (60-120 bpm, sinusoidal)
    wave_bpm = 90 + 30 * math.sin(math.radians(phase))
    spec['wave_bpm'] = round(wave_bpm, 1)
    existing_bpm = spec.get('bpm', 72)
    spec['bpm'] = round(0.7 * existing_bpm + 0.3 * wave_bpm, 1)

    # 10. Hora weight (slow timescale)
    hora = chart.get('meta', {})
    hora_data = _compute_hora_weight(chart)
    spec['wave_hora'] = hora_data

    # 11. Append ALL wave OSC messages
    osc = spec.get('osc_messages', [])
    osc.append(['/atlas/wave/gamak', [gamak_intensity]])
    osc.append(['/atlas/wave/bpm', [wave_bpm]])
    osc.append(['/atlas/wave/partial', [_K_TO_PARTIAL.get(dominant_k, 'pa')]])
    osc.append(['/atlas/wave/k', [float(dominant_k)]])

    # Interval mix: flatten to [ratio1, amp1, ratio2, amp2, ...]
    partials_flat = []
    for ratio, amp in sorted(interval_mix.items()):
        partials_flat.extend([ratio, round(amp, 3)])
    if partials_flat:
        osc.append(['/atlas/wave/partials', partials_flat])

    # Rhythm mode
    osc.append(['/atlas/wave/rhythm_mode', [
        float(rhythm['dominant_prime']),
        float(rhythm['secondary_prime']),
        round(rhythm['blend_ratio'], 2),
    ]])

    # Breath (fast cycle params — sent at medium rate, SC interpolates)
    osc.append(['/atlas/wave/breath', [
        round(breath['gamak_probability'], 3),
        round(breath['pitch_drift_cents'], 1),
        round(breath['energy'], 3),
    ]])

    # Hora weight (slow timescale)
    osc.append(['/atlas/wave/hora', [hora_data['graha'], hora_data['weight']]])

    # Natal filter
    if natal_filter.get('home_raga'):
        osc.append(['/atlas/natal/raga', [natal_filter['home_raga']]])
        osc.append(['/atlas/natal/partial_emphasis', [
            natal_filter.get('partial_ratio', 1.5),
            natal_filter.get('weight', 0.3),
        ]])


# ══════════════════════════════════════════════════════════
# INTERVAL MIX, RHYTHM, NATAL FILTER, BREATH
# ══════════════════════════════════════════════════════════

# Harmonic k → just-intonation partial ratio
_K_TO_RATIO = {
    1: 1.0,      # Sa (unison)
    2: 2.0,      # Sa' (octave)
    3: 1.5,      # Pa (3:2 perfect fifth)
    4: 4/3,      # Ma (4:3 perfect fourth)
    5: 5/4,      # Ga (5:4 major third)
    6: 6/5,      # ga (6:5 minor third)
    7: 7/4,      # Ni (7:4 natural seventh)
    9: 9/8,      # Re (9:8 major second)
    11: 11/8,    # Ma tivra (11:8 tritone)
    12: 1.0,     # rashi → Sa (complete cycle returns to fundamental)
}

# Planetary prime → phrase grouping
_PRIME_BOL = {
    3: 'ta-ki-ta',
    5: 'ta-ka-ta-ki-ta',
    7: 'ta-ki-ta-ta-ka-ta-ki',
    11: 'dha-ti-dha-ge-na-ti-na-ke-dha-ti-na',
}


def _compute_interval_mix(grahas, moon_nak_mid, k_scores):
    """Map wave field k-scores to drone partial ratios + amplitudes."""
    if not k_scores:
        return {1.5: 0.5}  # default Pa emphasis

    # Normalize k_scores to 0-1
    total = sum(k_scores.values())
    if total <= 0:
        return {1.5: 0.5}

    mix = {}
    for k, score in k_scores.items():
        ratio = _K_TO_RATIO.get(k, 1.0)
        amp = score / total  # proportional weight
        if ratio in mix:
            mix[ratio] = max(mix[ratio], amp)
        else:
            mix[ratio] = amp

    # Keep top 4 partials, normalize to sum=1
    top = dict(sorted(mix.items(), key=lambda x: x[1], reverse=True)[:4])
    top_total = sum(top.values())
    if top_total > 0:
        top = {k: v / top_total for k, v in top.items()}
    return top


def _compute_rhythm_mode(k_scores):
    """Determine dominant and secondary planetary prime from wave field."""
    # Map k-scores to planetary primes
    prime_scores = {}
    for k, score in k_scores.items():
        # k=3 → Mercury(3), k=4 → relates to Mars(7) via 4th aspect
        # k=6 → Venus(5) via sextile, k=7 → Mars(7), k=12 → full cycle
        # Direct mapping: use the k value if it's a prime, else nearest
        if k in (3, 5, 7, 11):
            prime_scores[k] = prime_scores.get(k, 0) + score
        elif k == 4:
            prime_scores[7] = prime_scores.get(7, 0) + score * 0.5
        elif k == 6:
            prime_scores[5] = prime_scores.get(5, 0) + score * 0.5
            prime_scores[3] = prime_scores.get(3, 0) + score * 0.5
        elif k == 12:
            prime_scores[3] = prime_scores.get(3, 0) + score * 0.3

    if not prime_scores:
        return {'dominant_prime': 7, 'secondary_prime': 3, 'blend_ratio': 0.8,
                'dominant_bol': _PRIME_BOL[7], 'secondary_bol': _PRIME_BOL[3]}

    sorted_primes = sorted(prime_scores.items(), key=lambda x: x[1], reverse=True)
    dom = sorted_primes[0]
    sec = sorted_primes[1] if len(sorted_primes) > 1 else (3, 0)

    # Blend ratio: how dominant is the primary (0.5 = equal, 1.0 = total dominance)
    total = dom[1] + sec[1]
    blend = dom[1] / total if total > 0 else 0.8

    return {
        'dominant_prime': dom[0],
        'secondary_prime': sec[0],
        'blend_ratio': round(blend, 2),
        'dominant_bol': _PRIME_BOL.get(dom[0], 'ta-ki-ta'),
        'secondary_bol': _PRIME_BOL.get(sec[0], 'ta-ki-ta'),
    }


def _compute_natal_filter(transit_activation):
    """Natal tonal personality — blends with transit state."""
    try:
        from npu_engine.jyotisha_engine import load_natal_json, compute_chart
        natal = load_natal_json()
        natal_chart = compute_chart(natal['dt_utc'], natal['lat'], natal['lon'])
    except Exception:
        return {'home_raga': '', 'weight': 0.0, 'partial_ratio': 1.5}

    natal_moon_nak = natal_chart['grahas']['Moon'].get('nakshatra', '')
    home_raga = _NAK_RAGA.get(natal_moon_nak, '')

    # Find strongest dignity graha for partial emphasis
    best_dignity = ''
    best_graha = 'Moon'
    dignity_rank = {'deeply_exalted': 6, 'exalted': 5, 'mooltrikona': 4,
                    'own': 3, 'friend': 2, 'neutral': 1, 'enemy': 0,
                    'debilitated': -1, 'deeply_debilitated': -2}
    best_score = -3
    for name, g in natal_chart['grahas'].items():
        d = g.get('dignity', 'neutral')
        if dignity_rank.get(d, 0) > best_score:
            best_score = dignity_rank.get(d, 0)
            best_graha = name
            best_dignity = d

    # Partial ratio from strongest graha's nak lord chain
    partial_ratio = 1.5  # default Pa

    # Natal weight: inverse of transit activation
    # High transit → sky speaks (natal weight low)
    # Low transit → self speaks (natal weight high)
    import math
    natal_weight = 1.0 - math.tanh(2.0 * (transit_activation - 0.5))
    natal_weight = max(0.1, min(0.9, natal_weight * 0.5))

    return {
        'home_raga': home_raga,
        'weight': round(natal_weight, 3),
        'partial_ratio': partial_ratio,
        'strongest_graha': best_graha,
        'strongest_dignity': best_dignity,
    }


def _compute_breath(activation, tithi_phase):
    """Micro-variation params for the 5s fast cycle."""
    import math
    # Breath depth scales with activation
    # High activation → wider breath (±5 bpm), more gamak
    # Low activation → shallow breath (±1 bpm), less gamak
    breath_depth = 1.0 + 4.0 * activation  # 1-5 bpm amplitude

    # Gamak probability: chance of ornament on each note
    gamak_prob = 0.2 + 0.6 * activation  # 0.2-0.8

    # Pitch drift: slow sruti wavering (±cents)
    drift = 2.0 + 3.0 * (1.0 - activation)  # quieter = more drift (meditative)

    # Energy: overall intensity for the fast cycle
    energy = 0.3 + 0.5 * math.sin(math.radians(tithi_phase)) * activation

    return {
        'gamak_probability': round(gamak_prob, 3),
        'pitch_drift_cents': round(drift, 1),
        'breath_depth_bpm': round(breath_depth, 1),
        'energy': round(max(0, min(1, energy)), 3),
    }


def _compute_hora_weight(chart):
    """Hora graha → tonal center weight (slow timescale)."""
    grahas = chart.get('grahas', {})
    # Find hora from Sun's position (approximate: hora = 1/24 of day)
    # The actual hora is in field_state, not in chart. Use Sun position as proxy.
    sun = grahas.get('Sun', {})
    sun_nak_lord = sun.get('nakshatra_lord', 'Sun')

    # Map hora graha to tonal weight
    _HORA_WEIGHT = {
        'Sun': 0.9, 'Moon': 0.6, 'Mars': 0.8,
        'Mercury': 0.7, 'Jupiter': 0.75, 'Venus': 0.65,
        'Saturn': 0.5, 'Rahu': 0.4, 'Ketu': 0.35,
    }
    weight = _HORA_WEIGHT.get(sun_nak_lord, 0.7)

    return {'graha': sun_nak_lord, 'weight': round(weight, 2)}
