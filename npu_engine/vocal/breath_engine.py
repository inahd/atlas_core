"""
breath_engine.py — Places breath/silence by querying tala graph.

Silence is structural, not absence. Breath is placed at khali beats,
phrase boundaries, and rasa-appropriate pauses.
"""

from typing import Dict, List, NamedTuple
from .graph_seed_data import TALA_BREATH


class BreathMap(NamedTuple):
    positions: List[int]     # beat indices where breath occurs
    durations: List[float]   # seconds per breath


def get_breath_positions(tala_name: str, mode: str = "gat",
                         arc: float = 0.5,
                         rasa: str = "shanta") -> BreathMap:
    """Return breath placement map for current tala/mode/arc.

    Args:
        tala_name: e.g. "Teentaal", "Rupak"
        mode: "alap" (spacious), "gat" (moderate), "taan" (minimal)
        arc: 0.0-1.0 compositional arc position
        rasa: current rasa for breath character

    Returns: BreathMap with beat positions and durations.
    """
    tala = TALA_BREATH.get(tala_name, TALA_BREATH.get("Adi"))
    if tala is None:
        tala = {"beats": 8, "khali": [4], "sam": [0], "phrase_ends": [3, 7]}

    beats = tala["beats"]
    khali = tala["khali"]
    phrase_ends = tala["phrase_ends"]

    positions = []
    durations = []

    if mode == "alap":
        # Alap: breath is long, frequent, structural
        # Breathe at khali AND phrase ends, plus extra pauses
        for b in khali:
            positions.append(b)
            durations.append(_breath_duration(rasa, "long"))
        for b in phrase_ends:
            if b not in positions:
                positions.append(b)
                durations.append(_breath_duration(rasa, "medium"))
        # Extra pauses in alap — every 3-4 beats
        for b in range(0, beats, 3):
            if b not in positions and b not in tala["sam"]:
                positions.append(b)
                durations.append(_breath_duration(rasa, "very_long"))

    elif mode == "taan":
        # Taan: breath is minimal, only at cycle boundaries
        # One breath at khali, that's it
        for b in khali:
            positions.append(b)
            durations.append(_breath_duration(rasa, "short"))

    else:  # gat (default)
        # Gat: breath at khali + phrase ends
        for b in khali:
            positions.append(b)
            durations.append(_breath_duration(rasa, "medium"))
        for b in phrase_ends:
            if b not in positions:
                positions.append(b)
                durations.append(_breath_duration(rasa, "short"))

    # Sort by position
    paired = sorted(zip(positions, durations))
    if paired:
        positions, durations = zip(*paired)
        return BreathMap(list(positions), list(durations))
    return BreathMap([], [])


# Rasa → breath character
_RASA_BREATH = {
    "shanta":    {"short": 0.3, "medium": 0.8, "long": 1.5, "very_long": 3.0},
    "shringara": {"short": 0.2, "medium": 0.6, "long": 1.2, "very_long": 2.0},
    "karuna":    {"short": 0.4, "medium": 1.0, "long": 2.0, "very_long": 4.0},
    "vira":      {"short": 0.15, "medium": 0.4, "long": 0.8, "very_long": 1.2},
    "raudra":    {"short": 0.1, "medium": 0.3, "long": 0.6, "very_long": 1.0},
    "hasya":     {"short": 0.15, "medium": 0.5, "long": 1.0, "very_long": 1.5},
    "bhayanaka": {"short": 0.3, "medium": 0.8, "long": 1.5, "very_long": 2.5},
    "bibhatsa":  {"short": 0.3, "medium": 0.7, "long": 1.3, "very_long": 2.5},
    "adbhuta":   {"short": 0.2, "medium": 0.6, "long": 1.2, "very_long": 2.0},
}


def _breath_duration(rasa: str, length: str) -> float:
    table = _RASA_BREATH.get(rasa, _RASA_BREATH["shanta"])
    return table.get(length, 0.5)
