"""
bhava_engine.py — Maps current rasa + arc_position to bhava state.

Bhava transitions smoothly — no sudden jumps, lerp over 4-8 beats.
Each bhava maps to SC vocal parameters: brightness, vibRate, vibDepth,
breathiness, register.
"""

from typing import Dict, Optional
from .graph_seed_data import BHAVA_STATES, BHAVA_INDEX


class BhavaState:
    """Smoothly interpolated bhava (emotional vocal coloring)."""

    def __init__(self):
        self.current = "shanta"
        self.target = "shanta"
        self.blend = 1.0  # 0=current, 1=target (starts converged)
        self.blend_rate = 0.15  # per-call increment (~6-8 calls to converge)

    def update(self, rasa: str, arc_position: float) -> Dict:
        """Compute bhava from rasa + arc, return SC-ready params.

        Args:
            rasa: current rasa name
            arc_position: 0.0-1.0 position in the compositional arc

        Returns: dict with brightness, vib_rate, vib_depth, breathiness,
                 register, bhava_name, bhava_index, intensity
        """
        # Find best bhava for current rasa + arc
        new_bhava = _select_bhava(rasa, arc_position)

        if new_bhava != self.target:
            self.current = self.target
            self.target = new_bhava
            self.blend = 0.0

        # Advance blend toward target
        self.blend = min(1.0, self.blend + self.blend_rate)

        # Interpolate parameters
        cur = BHAVA_STATES.get(self.current, BHAVA_STATES["shanta"])
        tgt = BHAVA_STATES.get(self.target, BHAVA_STATES["shanta"])

        b = self.blend
        return {
            "bhava_name": self.target if b > 0.5 else self.current,
            "bhava_index": BHAVA_INDEX.get(self.target, 5),
            "intensity": b,
            "brightness": _lerp(cur["brightness"], tgt["brightness"], b),
            "vib_rate": _lerp(cur["vib_rate"], tgt["vib_rate"], b),
            "vib_depth": _lerp(cur["vib_depth"], tgt["vib_depth"], b),
            "breathiness": _lerp(cur["breathiness"], tgt["breathiness"], b),
            "register": tgt["register"] if b > 0.5 else cur["register"],
        }


def _select_bhava(rasa: str, arc: float) -> str:
    """Select bhava based on rasa and arc position."""
    best = "shanta"
    best_fit = -1.0

    for name, state in BHAVA_STATES.items():
        if state["rasa"] != rasa:
            continue
        # Score by how well arc fits this bhava's range
        if state["arc_min"] <= arc <= state["arc_max"]:
            range_width = state["arc_max"] - state["arc_min"]
            center = (state["arc_min"] + state["arc_max"]) / 2
            fit = 1.0 - abs(arc - center) / max(range_width, 0.1)
            if fit > best_fit:
                best_fit = fit
                best = name

    return best


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t
