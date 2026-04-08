"""
mudra_graph.py — Mudrā relational graph for Atlas performance synthesis.

Maps rasa → mudrā sequences → abhinaya (expressive gesture).
Driven by the same field state that drives raga_graph.py.
No rendering here — outputs mudrā names + durations for downstream use.

Sources: Nāṭyaśāstra (Bharata Muni), Abhinaya Darpaṇa (Nandikeshvara)
"""

import random
from typing import Any, Dict, List, Optional

# ══════════════════════════════════════════════════════════
# MUDRĀ VOCABULARY
# ══════════════════════════════════════════════════════════

# Asamyuta (single-hand) hastas — 28 canonical
ASAMYUTA = [
    'Pataka', 'Tripataka', 'Ardhapataka', 'Kartarimukha',
    'Mayura', 'Ardhachandra', 'Arala', 'Shukatunda',
    'Mushti', 'Shikhara', 'Kapittha', 'Katakamukha',
    'Suchi', 'Chandrakala', 'Padmakosha', 'Sarpashirsha',
    'Mrigashirsha', 'Simhamukha', 'Kangula', 'Alapadma',
    'Chatura', 'Bhramara', 'Hamsasya', 'Hamsapaksha',
    'Sandamsha', 'Mukula', 'Tamrachuda', 'Trishula',
]

# Samyuta (two-hand) hastas — 24 canonical
SAMYUTA = [
    'Anjali', 'Kapota', 'Karkata', 'Swastika',
    'Dola', 'Pushpaputa', 'Utsanga', 'Shivalinga',
    'Katakavardhana', 'Kartariswastika', 'Shakata', 'Shankha',
    'Chakra', 'Samputa', 'Pasha', 'Kilaka',
    'Matsya', 'Kurma', 'Varaha', 'Garuda',
    'Nagabandha', 'Khatwa', 'Bherunda', 'Avahitta',
]

# Display names for UI/atlas events
_DISPLAY_NAMES = {
    'Pataka':       'Flag · Open Palm',
    'Tripataka':    'Three-Part Flag',
    'Ardhapataka':  'Half Flag',
    'Kartarimukha': 'Scissors Face',
    'Mayura':       'Peacock',
    'Ardhachandra': 'Half Moon',
    'Arala':        'Bent · Curved',
    'Shukatunda':   'Parrot Beak',
    'Mushti':       'Fist',
    'Shikhara':     'Peak · Pinnacle',
    'Kapittha':     'Wood Apple',
    'Katakamukha':  'Bracelet Opening',
    'Suchi':        'Needle · Pointing',
    'Chandrakala':  'Moon Digit',
    'Padmakosha':   'Lotus Bud',
    'Sarpashirsha': 'Serpent Head',
    'Mrigashirsha': 'Deer Head',
    'Simhamukha':   'Lion Face',
    'Kangula':      'Ringing Bell',
    'Alapadma':     'Lotus in Full Bloom',
    'Chatura':      'Square · Clever',
    'Bhramara':     'Bee',
    'Hamsasya':     'Swan Face',
    'Hamsapaksha':  'Swan Wing',
    'Sandamsha':    'Pincers',
    'Mukula':       'Bud · Offering',
    'Tamrachuda':   'Rooster Crest',
    'Trishula':     'Trident',
    'Anjali':       'Salutation · Prayer',
    'Kapota':       'Dove',
    'Pushpaputa':   'Flower Offering',
    'Garuda':       'Eagle · Divine Vehicle',
    'Shivalinga':   'Śiva Emblem',
    'Swastika':     'Auspicious Cross',
}

# ══════════════════════════════════════════════════════════
# RASA → MUDRĀ MAPPING (Nāṭyaśāstra)
# ══════════════════════════════════════════════════════════

RASA_MUDRAS = {
    'shringara': {
        'primary': ['Hamsasya', 'Katakamukha', 'Alapadma', 'Kapittha'],
        'sequence_bias': 'flowing',
        'tempo': 'madhya',
    },
    'bhakti': {
        'primary': ['Anjali', 'Pataka', 'Shikhara', 'Chandrakala'],
        'sequence_bias': 'sustained',
        'tempo': 'vilamba',
    },
    'karuna': {
        'primary': ['Mrigashirsha', 'Ardhachandra', 'Mukula', 'Kapittha'],
        'sequence_bias': 'slow_descent',
        'tempo': 'vilamba',
    },
    'vira': {
        'primary': ['Tripataka', 'Mushti', 'Shikhara', 'Suchi'],
        'sequence_bias': 'strong_accented',
        'tempo': 'druta',
    },
    'shanta': {
        'primary': ['Pataka', 'Anjali', 'Hamsapaksha', 'Padmakosha'],
        'sequence_bias': 'still',
        'tempo': 'vilamba',
    },
    'adbhuta': {
        'primary': ['Alapadma', 'Sarpashirsha', 'Simhamukha', 'Chandrakala'],
        'sequence_bias': 'expansive',
        'tempo': 'madhya',
    },
    'raudra': {
        'primary': ['Tripataka', 'Suchi', 'Trishula', 'Mushti'],
        'sequence_bias': 'sharp_percussive',
        'tempo': 'druta',
    },
    'hasya': {
        'primary': ['Hamsasya', 'Bhramara', 'Kangula', 'Chatura'],
        'sequence_bias': 'light_quick',
        'tempo': 'druta',
    },
    'bibhatsa': {
        'primary': ['Kartarimukha', 'Shukatunda', 'Arala', 'Mushti'],
        'sequence_bias': 'contracting',
        'tempo': 'madhya',
    },
}

# ══════════════════════════════════════════════════════════
# ELEMENT → MUDRĀ CHARACTER
# ══════════════════════════════════════════════════════════

ELEMENT_MUDRAS = {
    'earth':  {'quality': 'grounded',  'preferred': ['Pataka', 'Mushti', 'Kapittha', 'Anjali']},
    'water':  {'quality': 'flowing',   'preferred': ['Alapadma', 'Hamsasya', 'Padmakosha', 'Sarpashirsha']},
    'fire':   {'quality': 'sharp',     'preferred': ['Tripataka', 'Suchi', 'Trishula', 'Shikhara']},
    'air':    {'quality': 'light',     'preferred': ['Hamsapaksha', 'Bhramara', 'Chandrakala', 'Mayura']},
    'ether':  {'quality': 'expansive', 'preferred': ['Anjali', 'Pataka', 'Pushpaputa', 'Garuda']},
}

# ══════════════════════════════════════════════════════════
# NAKṢATRA → MUDRĀ (from Nāṭyaśāstra nakṣatra deities)
# ══════════════════════════════════════════════════════════

NAKSHATRA_MUDRAS = {
    'Ashvini':          'Hamsasya',
    'Bharani':          'Trishula',
    'Krittika':         'Tripataka',
    'Rohini':           'Padmakosha',
    'Mrigashira':       'Mrigashirsha',
    'Ardra':            'Arala',
    'Punarvasu':        'Anjali',
    'Pushya':           'Pushpaputa',
    'Ashlesha':         'Sarpashirsha',
    'Magha':            'Shikhara',
    'Purva Phalguni':   'Kapittha',
    'Uttara Phalguni':  'Pataka',
    'Hasta':            'Hamsasya',
    'Chitra':           'Alapadma',
    'Swati':            'Hamsapaksha',
    'Vishakha':         'Trishula',
    'Anuradha':         'Anjali',
    'Jyeshtha':         'Mushti',
    'Mula':             'Suchi',
    'Purva Ashadha':    'Padmakosha',
    'Uttara Ashadha':   'Shikhara',
    'Shravana':         'Hamsapaksha',
    'Dhanishta':        'Tripataka',
    'Shatabhisha':      'Chandrakala',
    'Purva Bhadra':     'Trishula',
    'Uttara Bhadra':    'Sarpashirsha',
    'Revati':           'Pushpaputa',
}

# Nakṣatra name normalization for matching kernel IAST names
_NAK_NORMALIZE = {
    'aśvinī': 'Ashvini', 'ashwini': 'Ashvini',
    'bharaṇī': 'Bharani', 'bharani': 'Bharani',
    'kṛttikā': 'Krittika', 'krittika': 'Krittika',
    'rohiṇī': 'Rohini', 'rohini': 'Rohini',
    'mṛgaśīrā': 'Mrigashira', 'mrigashira': 'Mrigashira',
    'ārdrā': 'Ardra', 'ardra': 'Ardra',
    'punarvasu': 'Punarvasu',
    'puṣya': 'Pushya', 'pushya': 'Pushya',
    'āśleṣā': 'Ashlesha', 'ashlesha': 'Ashlesha',
    'maghā': 'Magha', 'magha': 'Magha',
    'pūrva phālgunī': 'Purva Phalguni', 'purva phalguni': 'Purva Phalguni',
    'uttara phālgunī': 'Uttara Phalguni', 'uttara phalguni': 'Uttara Phalguni',
    'hasta': 'Hasta',
    'citrā': 'Chitra', 'chitra': 'Chitra',
    'svātī': 'Swati', 'swati': 'Swati',
    'viśākhā': 'Vishakha', 'vishakha': 'Vishakha',
    'anurādhā': 'Anuradha', 'anuradha': 'Anuradha',
    'jyeṣṭhā': 'Jyeshtha', 'jyeshtha': 'Jyeshtha',
    'mūla': 'Mula', 'mula': 'Mula',
    'pūrvāṣāḍhā': 'Purva Ashadha', 'purva ashadha': 'Purva Ashadha',
    'uttarāṣāḍhā': 'Uttara Ashadha', 'uttara ashadha': 'Uttara Ashadha',
    'śravaṇa': 'Shravana', 'shravana': 'Shravana',
    'dhaniṣṭhā': 'Dhanishta', 'dhanishta': 'Dhanishta',
    'śatabhiṣā': 'Shatabhisha', 'shatabhisha': 'Shatabhisha',
    'pūrva bhādrapadā': 'Purva Bhadra', 'purva bhadrapada': 'Purva Bhadra',
    'uttara bhādrapadā': 'Uttara Bhadra', 'uttara bhadrapada': 'Uttara Bhadra',
    'revatī': 'Revati', 'revati': 'Revati',
}

# ══════════════════════════════════════════════════════════
# DIRECTED TRANSITION GRAPH
# ══════════════════════════════════════════════════════════

# Each mudrā → list of natural successor mudrās (ordered by affinity).
# Transitions follow physical hand-shape proximity and aesthetic flow.
MUDRA_TRANSITIONS = {
    'Pataka':       ['Tripataka', 'Anjali', 'Hamsapaksha', 'Alapadma', 'Ardhachandra'],
    'Tripataka':    ['Pataka', 'Suchi', 'Shikhara', 'Mushti', 'Kartarimukha'],
    'Ardhapataka':  ['Pataka', 'Tripataka', 'Kartarimukha', 'Ardhachandra'],
    'Kartarimukha': ['Tripataka', 'Shukatunda', 'Arala', 'Ardhapataka'],
    'Mayura':       ['Hamsapaksha', 'Chandrakala', 'Alapadma', 'Bhramara'],
    'Ardhachandra': ['Pataka', 'Mrigashirsha', 'Chandrakala', 'Arala'],
    'Arala':        ['Shukatunda', 'Kartarimukha', 'Ardhachandra', 'Sarpashirsha'],
    'Shukatunda':   ['Arala', 'Kartarimukha', 'Sarpashirsha', 'Mushti'],
    'Mushti':       ['Shikhara', 'Tripataka', 'Suchi', 'Pataka'],
    'Shikhara':     ['Mushti', 'Suchi', 'Tripataka', 'Kapittha'],
    'Kapittha':     ['Katakamukha', 'Shikhara', 'Hamsasya', 'Mukula'],
    'Katakamukha':  ['Hamsasya', 'Kapittha', 'Alapadma', 'Chatura'],
    'Suchi':        ['Tripataka', 'Shikhara', 'Pataka', 'Trishula'],
    'Chandrakala':  ['Ardhachandra', 'Alapadma', 'Mrigashirsha', 'Mayura'],
    'Padmakosha':   ['Alapadma', 'Pushpaputa', 'Mukula', 'Hamsasya'],
    'Sarpashirsha': ['Arala', 'Chandrakala', 'Mrigashirsha', 'Shukatunda'],
    'Mrigashirsha': ['Hamsasya', 'Chandrakala', 'Ardhachandra', 'Alapadma'],
    'Simhamukha':   ['Tripataka', 'Mushti', 'Alapadma', 'Trishula'],
    'Kangula':      ['Bhramara', 'Chatura', 'Hamsasya', 'Kapittha'],
    'Alapadma':     ['Hamsasya', 'Padmakosha', 'Katakamukha', 'Chandrakala'],
    'Chatura':      ['Katakamukha', 'Kangula', 'Hamsasya', 'Bhramara'],
    'Bhramara':     ['Kangula', 'Mayura', 'Hamsapaksha', 'Chatura'],
    'Hamsasya':     ['Katakamukha', 'Alapadma', 'Mukula', 'Kapittha'],
    'Hamsapaksha':  ['Pataka', 'Mayura', 'Bhramara', 'Chandrakala'],
    'Sandamsha':    ['Mukula', 'Katakamukha', 'Kapittha', 'Hamsasya'],
    'Mukula':       ['Padmakosha', 'Hamsasya', 'Kapittha', 'Sandamsha'],
    'Tamrachuda':   ['Tripataka', 'Shikhara', 'Kangula', 'Mushti'],
    'Trishula':     ['Suchi', 'Tripataka', 'Shikhara', 'Simhamukha'],
    # Samyuta (two-hand)
    'Anjali':       ['Pataka', 'Pushpaputa', 'Kapota', 'Hamsasya'],
    'Kapota':       ['Anjali', 'Pushpaputa', 'Pataka', 'Padmakosha'],
    'Pushpaputa':   ['Anjali', 'Padmakosha', 'Kapota', 'Mukula'],
    'Garuda':       ['Hamsapaksha', 'Pataka', 'Anjali', 'Tripataka'],
    'Shivalinga':   ['Anjali', 'Shikhara', 'Mushti', 'Pataka'],
    'Swastika':     ['Pataka', 'Anjali', 'Tripataka', 'Hamsapaksha'],
}

# Tempo → duration in beats
_TEMPO_BEATS = {
    'vilamba': 2.0,
    'madhya':  1.0,
    'druta':   0.5,
}


# ══════════════════════════════════════════════════════════
# INTERNAL HELPERS
# ══════════════════════════════════════════════════════════

def _normalize_nakshatra(name: str) -> str:
    """Normalize kernel nakṣatra name to lookup key."""
    if not name:
        return ""
    low = name.lower().strip()
    # Direct match in NAKSHATRA_MUDRAS keys
    for k in NAKSHATRA_MUDRAS:
        if k.lower() == low:
            return k
    # Normalized alias
    canonical = _NAK_NORMALIZE.get(low)
    if canonical:
        return canonical
    # Partial match
    for k in NAKSHATRA_MUDRAS:
        if k.lower().startswith(low.split()[0]) if low else False:
            return k
    return ""


def _get_rasa_from_raga(raga_name: str) -> str:
    """Map rāga to primary rasa. Rough heuristic from rāga character."""
    if not raga_name:
        return 'shanta'
    low = raga_name.lower()
    _RAGA_RASA = {
        'yaman': 'shringara', 'bhairava': 'bhakti', 'bhimpalasi': 'karuna',
        'darbari': 'karuna', 'bageshri': 'shringara', 'marva': 'adbhuta',
        'kafi': 'hasya', 'multani': 'karuna', 'todi': 'karuna',
        'malkauns': 'shanta', 'hindol': 'shringara', 'puriya': 'shanta',
        'bihag': 'shringara', 'khamaj': 'shringara',
    }
    for key, rasa in _RAGA_RASA.items():
        if key in low:
            return rasa
    return 'shanta'


def _pick_weighted(candidates: list, preferred: set, weight: float = 2.0) -> str:
    """Pick from candidates, preferring items in the preferred set."""
    if not candidates:
        return 'Pataka'
    weights = []
    for c in candidates:
        weights.append(weight if c in preferred else 1.0)
    total = sum(weights)
    r = random.random() * total
    cumulative = 0.0
    for c, w in zip(candidates, weights):
        cumulative += w
        if r <= cumulative:
            return c
    return candidates[0]


# ══════════════════════════════════════════════════════════
# PUBLIC API
# ══════════════════════════════════════════════════════════

def get_mudra_for_field(field_state: dict) -> dict:
    """Determine primary and secondary mudrā from current field state.

    Returns:
        {primary, secondary, quality, tempo, nakshatra_mudra, rasa, element}
    """
    p = field_state.get("panchanga", {})
    nak_raw = p.get("nakshatra", "")
    element = (p.get("element") or "ether").lower()
    raga = field_state.get("raga") or field_state.get("sound_state", {}).get("raga", "")

    # Nakṣatra → primary mudrā
    nak_key = _normalize_nakshatra(nak_raw)
    primary = NAKSHATRA_MUDRAS.get(nak_key, "Pataka")

    # Rasa → secondary mudrā
    rasa = _get_rasa_from_raga(raga)
    rasa_info = RASA_MUDRAS.get(rasa, RASA_MUDRAS['shanta'])
    secondary_candidates = [m for m in rasa_info['primary'] if m != primary]
    secondary = secondary_candidates[0] if secondary_candidates else primary

    # Element quality
    elem_info = ELEMENT_MUDRAS.get(element, ELEMENT_MUDRAS['ether'])
    quality = elem_info['quality']
    tempo = rasa_info['tempo']

    return {
        "primary": primary,
        "secondary": secondary,
        "quality": quality,
        "tempo": tempo,
        "rasa": rasa,
        "element": element,
        "nakshatra_mudra": f"{nak_key} → {primary}" if nak_key else f"default → {primary}",
        "attestation": "TRADITIONAL",
    }


def generate_mudra_sequence(field_state: dict, length: int = 6) -> list:
    """Walk the transition graph to generate a mudrā sequence.

    Weights transitions by rasa preference and element quality.
    Each step: {mudra, hand, duration_beats, quality}
    """
    context = get_mudra_for_field(field_state)
    current = context["primary"]
    rasa = context["rasa"]
    element = context["element"]
    tempo = context["tempo"]

    # Build preferred set from rasa + element
    rasa_info = RASA_MUDRAS.get(rasa, RASA_MUDRAS['shanta'])
    elem_info = ELEMENT_MUDRAS.get(element, ELEMENT_MUDRAS['ether'])
    preferred = set(rasa_info['primary']) | set(elem_info['preferred'])

    beat_dur = _TEMPO_BEATS.get(tempo, 1.0)

    sequence = []
    all_mudras = set(ASAMYUTA) | set(SAMYUTA)

    for i in range(length):
        # Determine hand: samyuta mudras use both
        hand = "both" if current in SAMYUTA else ("left" if i % 2 == 0 else "right")

        sequence.append({
            "mudra": current,
            "hand": hand,
            "duration_beats": beat_dur,
            "quality": context["quality"],
        })

        # Transition
        successors = MUDRA_TRANSITIONS.get(current, [])
        if successors:
            current = _pick_weighted(successors, preferred)
        else:
            # No explicit transitions — pick from rasa/element preferred
            fallback = list(preferred - {current})
            current = random.choice(fallback) if fallback else 'Pataka'

    return sequence


def mudra_to_atlas_event(mudra_dict: dict, element: str = "ether",
                         rasa: str = "shanta") -> dict:
    """Convert mudrā dict to an atlas display event."""
    name = mudra_dict.get("mudra", "Pataka")
    beat_dur = mudra_dict.get("duration_beats", 1.0)

    # Rough ms conversion (assume 72 bpm default)
    duration_ms = int(beat_dur * (60000 / 72))

    return {
        "type": "mudra",
        "name": name,
        "display_name": _DISPLAY_NAMES.get(name, name),
        "duration_ms": duration_ms,
        "element": element,
        "rasa": rasa,
        "hand": mudra_dict.get("hand", "right"),
        "quality": mudra_dict.get("quality", "flowing"),
    }
