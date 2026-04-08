"""
layakari_engine.py — Manages rhythmic density multiplication.

Transitions smoothly: never jump from 1x to 4x directly.
All layakari transitions target sam as landing point.
"""

from .graph_seed_data import LAYAKARI


def get_layakari(mode: str, arc: float, current_factor: float = 1.0) -> float:
    """Determine target layakari factor from mode and arc position.

    Returns factor: 0.5 (aadh), 1 (thah), 2 (dugun), 3 (tigun), 4 (chaugun).
    Transitions smoothly — returns at most one step from current.
    """
    # Find best layakari for current mode + arc
    candidates = []
    for name, data in LAYAKARI.items():
        if mode not in data["mode"]:
            continue
        lo, hi = data["arc_range"]
        if lo <= arc <= hi:
            # Weight by how centered the arc is in the range
            center = (lo + hi) / 2
            fit = 1.0 - abs(arc - center) / max(hi - lo, 0.1)
            candidates.append((data["factor"], fit))

    if not candidates:
        return 1.0  # default: thah

    # Pick highest fit
    candidates.sort(key=lambda x: -x[1])
    target = candidates[0][0]

    # Smooth transition: at most one step at a time
    steps = [0.5, 1, 2, 3, 4]
    cur_idx = _nearest_idx(steps, current_factor)
    tgt_idx = _nearest_idx(steps, target)

    if tgt_idx > cur_idx:
        return steps[min(cur_idx + 1, len(steps) - 1)]
    elif tgt_idx < cur_idx:
        return steps[max(cur_idx - 1, 0)]
    return steps[cur_idx]


def _nearest_idx(steps, val):
    return min(range(len(steps)), key=lambda i: abs(steps[i] - val))
