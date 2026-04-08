"""
theka_engine.py — Generates theka variations from graph.

Hard constraints: khali always gets na (not dha), sam always gets
heaviest bol. Variations respond to mode and rasa.
"""

from typing import Dict, List, NamedTuple
from .tala_graph import get_tala, get_bol_properties
from .sam_field import get_gravity


class BolEvent(NamedTuple):
    bol: str
    beat: int
    amp: float
    weight: float
    variation: str  # "canonical", "sparse", "fill", "accent"


def generate_theka_cycle(tala_name: str, mode: str = "gat",
                         arc: float = 0.5, rasa: str = "shanta") -> List[BolEvent]:
    """Generate one full theka cycle with mode/rasa variations.

    Mode effects:
      alap/jod: sparse — many bols replaced with silence
      gat: full canonical theka
      taan: theka with fills between bols
      jhala: compressed by layakari, vibhag starts accented
    """
    tala = get_tala(tala_name)
    theka = list(tala.theka)
    events = []

    for beat_idx, bol in enumerate(theka):
        pos_in_cycle = beat_idx % tala.beats
        gravity = get_gravity(beat_idx, tala_name)
        bp = get_bol_properties(bol)

        # Hard constraints
        is_sam = (pos_in_cycle == tala.sam)
        is_khali = (pos_in_cycle == tala.khali and not is_sam)

        # Khali always gets open hand — replace dha/dhin with tin/na
        if is_khali and bol in ("dha", "dhin", "dhi"):
            bol = "na" if bp.resonance == "open" else "tin"
            bp = get_bol_properties(bol)

        # Sam always gets heaviest available bol
        if is_sam and bol in ("tin", "na", "ta"):
            bol = "dha"
            bp = get_bol_properties(bol)

        # Base amplitude from gravity + weight
        amp = 0.5 + gravity * 0.3 + bp.weight * 0.2

        # Mode variations
        variation = "canonical"

        if mode == "alap":
            # Sparse: only play sam, khali, and occasional vibhag starts
            if not is_sam and not is_khali and gravity < 0.5:
                if beat_idx % 3 != 0:  # skip 2/3 of non-structural beats
                    bol = ""
                    amp = 0.0
                    variation = "sparse"
                else:
                    amp *= 0.5
                    variation = "sparse"

        elif mode == "taan":
            # Denser: accents on vibhag boundaries
            if gravity > 0.7:
                amp *= 1.2
                variation = "accent"

        elif mode == "jhala":
            # All vibhag starts get accent
            if gravity > 0.5:
                amp *= 1.3
                variation = "accent"

        amp = min(1.0, max(0.0, amp))

        events.append(BolEvent(
            bol=bol,
            beat=beat_idx,
            amp=round(amp, 3),
            weight=bp.weight,
            variation=variation,
        ))

    return events
