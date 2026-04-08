"""
relational_synth.py — Entity graph → synthesis parameters

The graph IS the instrument.
No hardcoded music knowledge.
No synthesis here — only relational mapping.
Output goes to om.py (tanpura), bridge.py (SC), or future renderers.
"""

# Shruti ratios — physics, not music knowledge
_SHRUTI = {
    "Sa": 1.0, "re": 256/243, "Re": 9/8, "ga": 32/27, "Ga": 5/4,
    "ma": 4/3, "Ma": 45/32, "Pa": 3/2, "dha": 128/81, "Dha": 5/3,
    "ni": 16/9, "Ni": 15/8,
    "Re♭": 256/243, "Ga♭": 32/27, "Ma#": 45/32, "Dha♭": 128/81, "Ni♭": 16/9,
}

_ELEMENT_TIMBRE = {
    "water": "round",
    "fire":  "bright",
    "earth": "warm",
    "air":   "airy",
    "ether": "pure",
}

_ELEMENT_JAWARI = {
    "earth": 0.4,
    "air":   0.5,
    "water": 0.6,
    "fire":  0.7,
    "ether": 0.3,
}

# Prahar register — time of day determines the base Sa
# Prahar 1-8 maps 3-hour windows starting from 6pm
# Real tanpuras play C3-D3 range. Never below B2 (123Hz).
_PRAHAR_REGISTER = {
    1: 146.83,  # evening — D3
    2: 130.81,  # night — C3
    3: 130.81,  # late night — C3
    4: 130.81,  # pre-dawn — C3
    5: 123.47,  # dawn — B2 (lowest acceptable)
    6: 130.81,  # morning — C3
    7: 138.59,  # late morning — C#3
    8: 130.81,  # conclusion — C3
}

# Element adds color as semitone offset — not octave transposition
_ELEMENT_OFFSET = {
    "fire":  +4,   # bright
    "earth":  0,   # grounded at base
    "water": -2,   # slightly lower — fluid
    "air":   +2,   # slightly higher — light
    "ether":  0,   # neutral
}


def _derive_sa_hz(field_state: dict) -> float:
    """Sa from prahar register + element color. Always 110-185Hz."""
    p = field_state.get("panchanga", {})
    drd = field_state.get("devi_raga_def") or {}

    # Prahar from raga def, fallback to clock
    prahar = drd.get("prahar", 0)
    if not prahar or prahar == 0:
        from datetime import datetime
        h = datetime.now().hour
        prahar = max(1, min(8, (h % 24) // 3 + 1))

    base = _PRAHAR_REGISTER.get(prahar, 130.81)
    element = (p.get("element") or "ether").lower()
    offset = _ELEMENT_OFFSET.get(element, 0)
    sa_hz = base * (2.0 ** (offset / 12.0))

    # Hard clamp — no real tanpura plays outside this range
    return max(110.0, min(185.0, sa_hz))


# Rāgas that omit Pa — use Ma tuning instead
_MA_RAGAS = {"Mārvā", "Marva", "Hindol", "Mālkauns", "Malkauns"}
# Rāgas that use Dha tuning
_DHA_RAGAS = {"Mārvā", "Marva"}


def compute_tanpura_params(field_state: dict) -> dict:
    """Tanpura tuning and timbre from field state."""
    ss = field_state.get("sound_state", field_state)
    p = field_state.get("panchanga", {})

    element = (p.get("element") or ss.get("element") or "ether").lower()
    sa_hz = _derive_sa_hz(field_state)
    raga = ss.get("raga") or ""
    aroha = ss.get("raga_aroha") or ss.get("raga_notes") or []

    # Tuning: check if rāga omits Pa
    has_pa = any(s in ("Pa",) for s in aroha) if aroha else True

    if raga in _DHA_RAGAS:
        tuning = "Dha-sa-sa-Sa"
        string_ratios = [5/3, 2.0, 2.0, 1.0]
    elif not has_pa or raga in _MA_RAGAS:
        tuning = "Ma-sa-sa-Sa"
        string_ratios = [4/3, 2.0, 2.0, 1.0]
    else:
        tuning = "Pa-sa-sa-Sa"
        string_ratios = [3/2, 2.0, 2.0, 1.0]

    jawari = _ELEMENT_JAWARI.get(element, 0.3)

    # Observance modifies gap
    obs = field_state.get("observance")
    obs_type = ""
    if isinstance(obs, dict):
        obs_type = obs.get("type", "")
    elif isinstance(obs, list) and obs:
        obs_type = obs[0].get("type", "")
    loop_gap_ms = 200 if obs_type == "ekadashi" else 150

    return {
        "sa_hz": float(sa_hz),
        "tuning": tuning,
        "string_ratios": string_ratios,
        "jawari": jawari,
        "element": element,
        "loop_gap_ms": loop_gap_ms,
    }


def compute_melody_voices(field_state: dict) -> list:
    """Generate melodic phrase via rāga graph traversal, modulated by field coherence.

    Uses raga_graph.py for rāga-compliant phrase generation.
    NPU svara_weights modulate edge weights so high-coherence swaras appear more.
    """
    from .raga_graph import generate_phrase, phrase_to_freqs, JI_RATIOS

    ss = field_state.get("sound_state", field_state)
    svara_weights = ss.get("svara_weights") or field_state.get("svara_weights") or {}
    raga_name = ss.get("raga") or field_state.get("raga") or "Yaman"
    vadi = ss.get("raga_vadi") or ""
    samvadi = ss.get("raga_samvadi") or ""
    element = (field_state.get("panchanga", {}).get("element") or "ether").lower()
    sa_hz = _derive_sa_hz(field_state)

    # Average entity coherence as field-strength proxy
    entities = field_state.get("entities", [])
    if entities:
        avg_score = sum(e.get("score", 0) for e in entities[:10]) / min(10, len(entities))
        field_strength = min(1.0, avg_score / 1.5)
    else:
        field_strength = 0.5

    # Generate phrase via graph walk, modulated by svara_weights
    phrase = generate_phrase(raga_name, length=6, svara_weights=svara_weights)
    freq_pairs = phrase_to_freqs(phrase, float(sa_hz), JI_RATIOS)

    voices = []
    for freq, swara_name in freq_pairs:
        # Base amplitude from field strength
        amplitude = 0.5 * field_strength

        # Boost vādī / samvādī
        base_swara = swara_name.rstrip('~').rstrip('+').rstrip('-')
        if base_swara == vadi:
            amplitude *= 1.4
        elif base_swara == samvadi:
            amplitude *= 1.2

        # Andolana marker
        is_andolana = swara_name.endswith('~')

        amplitude = min(1.0, amplitude)

        voices.append({
            "swara": swara_name,
            "freq_hz": freq,
            "amplitude": round(amplitude, 4),
            "timbre": _ELEMENT_TIMBRE.get(element, "pure"),
            "duration_beats": 1.5 if is_andolana else 1.0,
            "andolana": is_andolana,
        })

    return voices


def compute_rhythm_pattern(field_state: dict) -> dict:
    """Rhythmic parameters from tāla and entity coherence."""
    ss = field_state.get("sound_state", field_state)
    entities = field_state.get("entities", [])

    tala_bols = ss.get("tala_bols") or []
    bpm = ss.get("bpm") or 72
    beat_ms = round(60000 / max(bpm, 30), 1)

    # Tradition: carnatic if any deity entity has coherence > 0.6
    tradition = "hindustani"
    for e in entities:
        eid = e.get("entity_id", "")
        if eid.startswith("deity_") and e.get("score", 0) > 0.6:
            tradition = "carnatic"
            break

    percussion_type = "mridangam" if tradition == "carnatic" else "tabla"

    # Observance check
    obs = field_state.get("observance")
    obs_type = ""
    if isinstance(obs, dict):
        obs_type = obs.get("type", "")
    elif isinstance(obs, list) and obs:
        obs_type = obs[0].get("type", "")

    active = obs_type != "ekadashi"

    return {
        "tradition": tradition,
        "tala_bols": tala_bols,
        "bpm": bpm,
        "beat_ms": beat_ms,
        "sam_amplitude": 1.0,
        "accent_amplitude": 0.7,
        "other_amplitude": 0.4,
        "percussion_type": percussion_type,
        "active": active,
    }


def compute_master_params(field_state: dict) -> dict:
    """Master output parameters from field coherence."""
    breath_rate = float(field_state.get("breath_rate", 1.0))
    master_gain = round(breath_rate * 0.7, 3)
    entities = field_state.get("entities", [])

    # Observance
    obs = field_state.get("observance")
    obs_type = ""
    if isinstance(obs, dict):
        obs_type = obs.get("type", "")
    elif isinstance(obs, list) and obs:
        obs_type = obs[0].get("type", "")

    # Richness: proportion of entities with score > 0.7
    high_coh = sum(1 for e in entities if e.get("score", 0) > 0.7)
    richness = round(min(1.0, high_coh / max(len(entities), 1)), 3)

    yuga_alpha = float(field_state.get("yuga_alpha", 1.0))

    return {
        "breath_rate": breath_rate,
        "master_gain": master_gain,
        "observance_type": obs_type,
        "yuga_alpha": yuga_alpha,
        "richness": richness,
    }


def compute_synth_params(field_state: dict) -> dict:
    """
    Given /field response, return complete synthesis parameters.
    Called every 10s when field changes.
    """
    from .mudra_graph import get_mudra_for_field

    return {
        "tanpura": compute_tanpura_params(field_state),
        "voices": compute_melody_voices(field_state),
        "rhythm": compute_rhythm_pattern(field_state),
        "master": compute_master_params(field_state),
        "mudra": get_mudra_for_field(field_state),
    }
