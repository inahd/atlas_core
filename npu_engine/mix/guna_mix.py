"""
guna_mix.py — Guna → timbral character.
"""

from typing import Dict
from .graph_seed_data import GUNA_CHARACTER


def get_guna_character(guna: str) -> Dict[str, float]:
    """Return timbral character offsets from guna.

    Returns dict with brightness, reverb, compression, sub, etc.
    """
    return dict(GUNA_CHARACTER.get(guna.lower(), GUNA_CHARACTER["sattva"]))
