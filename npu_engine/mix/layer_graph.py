"""
layer_graph.py — Queries layer-rasa-arc relations from graph.
"""

from typing import Dict
from .graph_seed_data import (
    LAYERS, RASA_LAYER_WEIGHTS, ARC_DENSITY, MODE_OVERRIDES,
)


def get_layer_weights(rasa: str, arc: float, mode: str = "gat") -> Dict[str, float]:
    """Return weight for each layer based on rasa, arc, and mode.

    Returns dict mapping layer_name → float (0-1).
    """
    # Base weights from rasa
    base = RASA_LAYER_WEIGHTS.get(rasa, RASA_LAYER_WEIGHTS["shanta"])

    # Arc density multiplier
    density = _arc_density(arc)

    # Compute weighted values
    weights = {}
    for layer in LAYERS:
        w = base.get(layer, 0.3) * density
        weights[layer] = round(max(0.0, min(1.0, w)), 3)

    # Mode overrides
    overrides = MODE_OVERRIDES.get(mode, {})
    for layer, override in overrides.items():
        if layer in weights:
            weights[layer] = round(min(weights[layer], override), 3)

    return weights


def _arc_density(arc: float) -> float:
    """Get density multiplier for arc position."""
    for start, end, density in ARC_DENSITY:
        if start <= arc < end:
            return density
    return 0.5
