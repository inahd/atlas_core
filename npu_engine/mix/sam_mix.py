"""
sam_mix.py — Sam and khali mix events.

Sam: all layers converge to full rasa weight for 1 beat.
Khali: melodic/vocal layers pull back 25% for 1 beat.
"""

from typing import Dict, NamedTuple


class MixEvent(NamedTuple):
    event_type: str        # "sam" or "khali"
    duration_beats: int
    layer_scale: Dict[str, float]  # layer → multiplier


def get_sam_event() -> MixEvent:
    """Sam: brief full-system convergence."""
    return MixEvent(
        event_type="sam",
        duration_beats=1,
        layer_scale={},  # empty = all layers to 1.0 (full rasa weight)
    )


def get_khali_event() -> MixEvent:
    """Khali: melodic/vocal layers pull back 25%."""
    return MixEvent(
        event_type="khali",
        duration_beats=1,
        layer_scale={
            "melody": 0.75,
            "vocal_line": 0.75,
            "konnakol": 0.8,
            "bol": 0.8,
            "mantra_drone": 0.9,
        },
    )
