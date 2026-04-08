"""
cross_rhythm_engine.py — Generates polyrhythm against tala base.

Only activates when resolution fits within current phrase.
Shanta = no cross rhythm (pure, undivided).
"""

from typing import Optional, NamedTuple
from .graph_seed_data import CROSS_RHYTHMS, RASA_CROSS


class CrossRhythm(NamedTuple):
    subdivision: int        # 3, 4, 5, 7
    resolution_beat: int    # when it resolves back to tala grid
    tension: float          # 0-1


def get_cross_rhythm(tala_name: str, tala_beats: int,
                     rasa: str, arc: float) -> Optional[CrossRhythm]:
    """Get appropriate cross rhythm for current rasa and arc.

    Only returns a cross rhythm when:
    1. The rasa supports it (shanta/karuna/bhayanaka = None)
    2. The resolution point lands within 2 tala cycles
    3. Arc position is past the opening (>0.3)
    """
    if arc < 0.3:
        return None  # too early for polyrhythm

    cross_name = RASA_CROSS.get(rasa)
    if cross_name is None:
        return None  # this rasa prefers undivided rhythm

    cross = CROSS_RHYTHMS.get(cross_name)
    if cross is None:
        return None

    sub = cross["subdivision"]

    # Calculate resolution: where does the cross rhythm
    # land back on a tala beat? LCM of sub and tala_beats
    from math import gcd
    lcm = (sub * tala_beats) // gcd(sub, tala_beats)

    # Only use if resolution is within 2 cycles
    if lcm > tala_beats * 2:
        return None

    return CrossRhythm(
        subdivision=sub,
        resolution_beat=lcm,
        tension=cross["tension"] * (0.5 + arc * 0.5),
    )
