"""
phoneme_graph.py — Queries matrika/bija phoneme nodes.

Every sound has cosmological meaning. This module maps syllables to
their element, chakra, deity, rasa, and SC-ready formant profile.
"""

from typing import Dict, List, Optional
from .graph_seed_data import MATRIKA_PHONEMES


# Build lookup indices at import time
_BY_SYLLABLE = {p["syllable"]: p for p in MATRIKA_PHONEMES}
_BY_ELEMENT = {}
_BY_DEITY = {}
_BY_CHAKRA = {}

for p in MATRIKA_PHONEMES:
    _BY_ELEMENT.setdefault(p["element"], []).append(p)
    _BY_DEITY.setdefault(p["deity"], []).append(p)
    _BY_CHAKRA.setdefault(p["chakra"], []).append(p)


def get_formant_profile(syllable: str) -> Dict:
    """Return SC-ready formant parameters for a syllable.

    Returns: {f1, f2, f3, bw} or defaults if unknown.
    """
    p = _BY_SYLLABLE.get(syllable)
    if p:
        return {"f1": p["f1"], "f2": p["f2"], "f3": p["f3"], "bw": p["bw"]}
    # Fallback: neutral open vowel
    return {"f1": 600, "f2": 1200, "f3": 2500, "bw": 80}


def get_phonemes_for_deity(deity_id: str) -> List[Dict]:
    """Return matrika phonemes associated with a deity.

    deity_id: bare name like 'agni', 'vishnu', 'shiva'
    """
    key = deity_id.lower().split(":")[-1]
    return _BY_DEITY.get(key, [])


def get_phonemes_for_element(element: str) -> List[Dict]:
    """Return phonemes by element affinity."""
    return _BY_ELEMENT.get(element.lower(), [])


def get_phonemes_for_chakra(chakra: str) -> List[Dict]:
    """Return phonemes by chakra."""
    return _BY_CHAKRA.get(chakra.lower(), [])


def get_syllable_sequence(nakshatra_entry: dict) -> List[Dict]:
    """Build a singable syllable sequence for a nakshatra.

    Combines pada syllables + bija in singing order.
    Each element tagged with formant profile.

    Args:
        nakshatra_entry: dict from nakshatra_ragas.NAKSHATRA_MAP

    Returns: list of {syllable, f1, f2, f3, bw, role}
    """
    sequence = []

    # Bija syllables first (invocation)
    for syl in nakshatra_entry.get("bija", []):
        profile = get_formant_profile(syl)
        sequence.append({**profile, "syllable": syl, "role": "bija"})

    # Pada syllables (structural)
    for syl in nakshatra_entry.get("pada", []):
        profile = get_formant_profile(syl)
        sequence.append({**profile, "syllable": syl, "role": "pada"})

    # Deity bija if present
    deity_bija = nakshatra_entry.get("deity_bija", "")
    if deity_bija:
        profile = get_formant_profile(deity_bija[:2])  # first 2 chars as approx
        sequence.append({**profile, "syllable": deity_bija, "role": "deity_bija"})

    return sequence


def get_rasa_for_syllable(syllable: str) -> str:
    """Return the rasa associated with a syllable, or 'shanta' default."""
    p = _BY_SYLLABLE.get(syllable)
    return p["rasa"] if p else "shanta"
