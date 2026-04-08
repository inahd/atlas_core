"""
sam_field.py — Computes sam-gravity for every beat position.

Every moment is felt as a distance from Sam. Gravity increases
exponentially in the last 2-3 beats approaching sam.
"""

import math
from .tala_graph import get_tala, beat_to_vibhag, TalaStructure


def get_gravity(beat: int, tala_name: str, layakari: float = 1.0) -> float:
    """Compute sam-gravity for a beat position.

    Returns 0.0 (khali, furthest from sam) to 1.0 (sam).
    Gravity increases exponentially as beat approaches sam.
    Layakari compresses (>1) or expands (<1) the gravity field.
    """
    tala = get_tala(tala_name)
    pos = beat % tala.beats
    beats = tala.beats

    # Distance to next sam (wrapping)
    dist_to_sam = (beats - pos) % beats
    if dist_to_sam == 0:
        return 1.0  # at sam

    # Normalized distance (0=at sam, 1=halfway through cycle)
    norm_dist = dist_to_sam / beats

    # Base gravity from vibhag
    vib_idx = beat_to_vibhag(pos, tala)
    vib_gravity = tala.vibhag_gravity[vib_idx]

    # Exponential approach: gravity spikes in last 3 beats before sam
    approach_factor = 0.0
    if dist_to_sam <= 3:
        approach_factor = math.exp(-dist_to_sam * 0.8) * 0.4

    # Combine: vibhag gravity + approach factor
    gravity = vib_gravity * (1 - approach_factor) + approach_factor

    # Layakari scaling: dugun compresses field, aadh expands
    if layakari > 1:
        gravity = gravity ** (1 / layakari)  # compress: more beats feel heavy
    elif layakari < 1 and layakari > 0:
        gravity = gravity ** (1 / layakari)  # expand: beats feel lighter

    return max(0.0, min(1.0, gravity))


def get_tension(beat: int, tala_name: str, cross_sub: int = 0) -> float:
    """Compute rhythmic tension from polyrhythm against base tala.

    Returns 0.0 (no tension) to 1.0 (maximum cross-rhythm tension).
    """
    if cross_sub <= 0:
        return 0.0

    tala = get_tala(tala_name)
    pos = beat % tala.beats

    # Tension peaks where cross-rhythm and base tala are most misaligned
    cross_pos = pos % cross_sub
    base_unit = tala.beats / len(tala.vibhag)

    # Measure misalignment between cross subdivision and vibhag grid
    nearest_grid = round(pos / base_unit) * base_unit
    offset = abs(pos - nearest_grid) / base_unit
    return min(1.0, offset * 2)


def is_approaching_sam(beat: int, tala_name: str, lookahead: int = 3) -> bool:
    """Check if we're within lookahead beats of sam."""
    tala = get_tala(tala_name)
    pos = beat % tala.beats
    dist = (tala.beats - pos) % tala.beats
    return 0 < dist <= lookahead


def beats_to_sam(beat: int, tala_name: str) -> int:
    """Return number of beats until next sam."""
    tala = get_tala(tala_name)
    pos = beat % tala.beats
    return (tala.beats - pos) % tala.beats
