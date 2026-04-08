"""
authority_mix.py — Maps mean authority score to mix character.

High confidence (shastra): bold, less reverb, direct.
Low confidence (experimental): quiet, more reverb, tentative.
"""

from typing import Dict, NamedTuple


class ConfidenceScale(NamedTuple):
    overall_scale: float   # 0.7-1.0 master amplitude
    reverb_add: float      # extra reverb depth (0-0.3)
    drone_bias: float      # push toward drone (0-0.2)
    melody_bias: float     # push toward melody (-0.1 to 0.1)


def get_confidence_scale(mean_authority: float) -> ConfidenceScale:
    """Map mean authority score to mix confidence parameters.

    Args:
        mean_authority: 0.0-1.0 average authority of active relations
    """
    a = max(0.0, min(1.0, mean_authority))
    return ConfidenceScale(
        overall_scale=0.7 + a * 0.3,           # 0.7 at low, 1.0 at high
        reverb_add=(1.0 - a) * 0.25,           # more reverb when uncertain
        drone_bias=(1.0 - a) * 0.15,           # lean on drone when uncertain
        melody_bias=a * 0.1 - 0.05,            # melody forward when confident
    )
