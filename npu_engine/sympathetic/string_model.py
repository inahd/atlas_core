"""
string_model.py — Sympathetic string tuning and resonance model.

13 strings spanning 2 octaves, tuned to the current raga's scale.
Each string has a frequency, a resonance bandwidth, and a decay time.
When an excitation frequency falls within a string's bandwidth, it rings.
"""

from typing import List, NamedTuple

# Shruti ratios for just-intonation tuning
_SEMI_SHRUTI = {
    0: 1.0, 1: 256/243, 2: 9/8, 3: 32/27, 4: 5/4, 5: 4/3,
    6: 45/32, 7: 3/2, 8: 128/81, 9: 5/3, 10: 16/9, 11: 15/8,
}


class SympatheticString(NamedTuple):
    index: int          # 0-12
    freq: float         # Hz
    semitone: int       # 0-11, or 12+ for upper octave
    octave: int         # 0=middle, 1=upper
    bandwidth: float    # Hz — resonance window
    decay: float        # seconds
    is_vadi: bool
    is_samvadi: bool


def tune_strings(sa: float, scale_degrees: List[int],
                 vadi: int = -1, samvadi: int = -1) -> List[SympatheticString]:
    """Tune 13 sympathetic strings to the current raga.

    Args:
        sa: Sa frequency in Hz
        scale_degrees: list of semitones in the raga (e.g. [0,2,4,5,7,9,11])
        vadi: vadi semitone (-1 if unknown)
        samvadi: samvadi semitone (-1 if unknown)

    Returns:
        13 SympatheticString objects spanning 2 octaves
    """
    strings = []
    idx = 0

    # Lower octave: first 6-7 degrees of the scale
    for i, semi in enumerate(scale_degrees[:7]):
        ratio = _SEMI_SHRUTI.get(semi % 12, 2 ** (semi / 12))
        freq = sa * ratio
        is_v = (semi % 12) == (vadi % 12) if vadi >= 0 else False
        is_s = (semi % 12) == (samvadi % 12) if samvadi >= 0 else False

        # Vadi/samvadi strings ring longer and have wider bandwidth
        bw = 8.0 if is_v else 6.0 if is_s else 4.0
        dec = 4.0 if is_v else 3.0 if is_s else 2.0

        strings.append(SympatheticString(
            index=idx, freq=round(freq, 2), semitone=semi,
            octave=0, bandwidth=bw, decay=dec,
            is_vadi=is_v, is_samvadi=is_s,
        ))
        idx += 1

    # Upper octave: remaining degrees to reach 13 strings
    for i, semi in enumerate(scale_degrees):
        if idx >= 13:
            break
        ratio = _SEMI_SHRUTI.get(semi % 12, 2 ** (semi / 12))
        freq = sa * 2 * ratio  # upper octave
        is_v = (semi % 12) == (vadi % 12) if vadi >= 0 else False
        is_s = (semi % 12) == (samvadi % 12) if samvadi >= 0 else False

        strings.append(SympatheticString(
            index=idx, freq=round(freq, 2), semitone=semi + 12,
            octave=1, bandwidth=3.0, decay=1.5,
            is_vadi=is_v, is_samvadi=is_s,
        ))
        idx += 1

    return strings


def find_resonating_strings(strings: List[SympatheticString],
                            excitation_freq: float,
                            threshold_cents: float = 50.0
                            ) -> List[tuple]:
    """Find which strings resonate with an excitation frequency.

    Returns list of (string, intensity) where intensity 0-1 is
    proportional to proximity (closer = stronger resonance).

    threshold_cents: how close the excitation must be to trigger resonance.
    50 cents = quarter tone — generous, models real sympathetic behavior.
    """
    results = []
    for s in strings:
        if s.freq <= 0:
            continue
        # Distance in cents
        cents = abs(1200 * _log2_safe(excitation_freq / s.freq))
        if cents <= threshold_cents:
            # Intensity: 1.0 at exact match, 0.0 at threshold
            intensity = 1.0 - (cents / threshold_cents)
            # Vadi/samvadi strings resonate more strongly
            if s.is_vadi:
                intensity *= 1.3
            elif s.is_samvadi:
                intensity *= 1.15
            intensity = min(1.0, intensity)
            results.append((s, round(intensity, 3)))
    return results


def _log2_safe(x):
    import math
    if x <= 0:
        return 0
    return math.log2(x)
