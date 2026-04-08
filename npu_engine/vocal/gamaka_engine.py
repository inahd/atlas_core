"""
gamaka_engine.py — Selects ornaments by querying graph relations.

No random selection — gamakas are chosen by which are characteristic
of the current raga, swara, and rasa context.
"""

from typing import Dict, Optional, Tuple
from .graph_seed_data import GAMAKA_TYPES, GAMAKA_INDEX, SVARA_RAGA_RASA

# Pre-index svara-raga-rasa triangles
_SRR_INDEX = {}
for tri in SVARA_RAGA_RASA:
    key = (tri["swara"], tri["raga"])
    _SRR_INDEX[key] = tri


class GamakaInstruction:
    """OSC-ready gamaka parameters."""
    __slots__ = ("type_name", "type_index", "depth", "rate", "duration")

    def __init__(self, type_name: str, type_index: int,
                 depth: float, rate: float, duration: float):
        self.type_name = type_name
        self.type_index = type_index
        self.depth = depth      # cents
        self.rate = rate        # Hz (0 for glide types)
        self.duration = duration  # seconds

    def as_osc(self, note_freq: float) -> list:
        """Return OSC-ready list: [type_index, depth, rate, note_freq]"""
        return [self.type_index, self.depth, self.rate, note_freq]


def get_gamaka(swara: str, raga_name: str, arc_position: float,
               intensity_mult: float = 1.0) -> Optional[GamakaInstruction]:
    """Find the characteristic gamaka for this swara in this raga.

    Queries the svara-raga-rasa triangle first, then falls back
    to raga-level characteristic gamakas, then swara-level defaults.

    Args:
        swara: swara name ('g', 'G', 'r', 'N', etc.)
        raga_name: raga name from nakshatra_ragas
        arc_position: 0.0-1.0 in compositional arc
        intensity_mult: authority-derived scaling

    Returns: GamakaInstruction or None (= no ornament)
    """
    import random

    # 1. Check svara-raga-rasa triangle (most specific)
    tri = _SRR_INDEX.get((swara, raga_name))
    if tri:
        gamaka_name = tri["ornament"]
        return _build_instruction(gamaka_name, arc_position, intensity_mult)

    # 2. Check if this swara is in any gamaka's used_on for this raga
    for gname, gdata in GAMAKA_TYPES.items():
        if raga_name in gdata["characteristic_of"] and swara in gdata["used_on"]:
            return _build_instruction(gname, arc_position, intensity_mult)

    # 3. Check if any gamaka is characteristic of this raga (weaker)
    raga_gamakas = [
        name for name, data in GAMAKA_TYPES.items()
        if raga_name in data["characteristic_of"]
    ]
    if raga_gamakas and random.random() < 0.3:  # 30% chance for non-specific
        return _build_instruction(random.choice(raga_gamakas), arc_position, intensity_mult * 0.5)

    return None  # no ornament


def _build_instruction(gamaka_name: str, arc: float,
                       intensity_mult: float) -> GamakaInstruction:
    """Build a GamakaInstruction from type name and context."""
    import random
    data = GAMAKA_TYPES[gamaka_name]
    sp = data["sc_params"]

    # Depth and rate scale with arc position (more intense in later arc)
    arc_scale = 0.7 + 0.6 * arc
    i = data["intensity"] * intensity_mult * arc_scale

    depth = _lerp(sp["depth_min"], sp["depth_max"], min(1.0, i))
    rate = _lerp(sp["rate_min"], sp["rate_max"], min(1.0, i)) if sp["rate_max"] > 0 else 0.0
    dur = _lerp(sp["dur_min"], sp["dur_max"], min(1.0, i))

    # Add slight randomness for naturalness
    depth *= random.uniform(0.85, 1.15)
    if rate > 0:
        rate *= random.uniform(0.9, 1.1)
    dur *= random.uniform(0.9, 1.1)

    return GamakaInstruction(
        type_name=gamaka_name,
        type_index=sp["type"],
        depth=round(depth, 1),
        rate=round(rate, 2),
        duration=round(dur, 4),
    )


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t
