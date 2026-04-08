"""
nakshatra_mix.py — Nakshatra → element → mix bias chain.
"""

from typing import Dict
from .graph_seed_data import ELEMENT_MIX_BIAS


def get_nakshatra_bias(element: str) -> Dict[str, float]:
    """Return mix bias from nakshatra's element.

    Returns dict of layer/timbre adjustments (additive offsets).
    """
    return dict(ELEMENT_MIX_BIAS.get(element.lower(), {}))
