"""
fill_engine.py — Generates rhythmic fills approaching sam.

Fill intensity scales with sam-gravity: more intense as sam approaches.
"""

from typing import List, NamedTuple, Optional
from .graph_seed_data import FILL_TYPES
from .sam_field import get_gravity, is_approaching_sam


class Fill(NamedTuple):
    bols: List[str]
    start_beat: int
    intensity: float
    fill_type: str


def get_fill(beat: int, tala_name: str, mode: str = "gat",
             rasa: str = "shanta", arc: float = 0.5) -> Optional[Fill]:
    """Get a rhythmic fill if appropriate for this beat position.

    Only returns fills when approaching sam and in the right mode.
    Intensity scales with gravity (more intense closer to sam).
    """
    if not is_approaching_sam(beat, tala_name, lookahead=4):
        return None

    gravity = get_gravity(beat, tala_name)

    # Find appropriate fill type for mode
    for name, data in FILL_TYPES.items():
        if mode not in data["mode"]:
            continue
        if data["intensity"] > arc + 0.3:
            continue  # too intense for current arc position

        intensity = data["intensity"] * gravity * (0.5 + arc * 0.5)

        return Fill(
            bols=data["bols"],
            start_beat=beat,
            intensity=round(min(1.0, intensity), 3),
            fill_type=name,
        )

    return None
