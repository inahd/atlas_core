"""
deity_mix.py — Deity → domain → mix bias chain.
"""

from typing import Dict
from .graph_seed_data import DEITY_MIX_BIAS


def get_deity_bias(deity: str) -> Dict[str, float]:
    """Return mix bias from deity association.

    Returns dict of layer/timbre adjustments (additive offsets).
    """
    # Try exact match, then first word
    if deity in DEITY_MIX_BIAS:
        return dict(DEITY_MIX_BIAS[deity])
    key = deity.split()[0] if deity else ""
    return dict(DEITY_MIX_BIAS.get(key, {}))
