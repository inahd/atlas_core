"""
excitation.py — Detects excitation events from melody/tabla/vocal.

Listens to what other engines are playing and determines which
sympathetic strings should resonate. The excitation sources are:

  Melody notes → primary excitation (strongest)
  Vocal svara → secondary excitation
  Tabla dayan → excitation at Sa harmonics (tuned drum)
  Tabla bayan → excitation at low fundamental

Each excitation event has: frequency, amplitude, source, decay_hint.
"""

from typing import List, NamedTuple, Optional
from .string_model import SympatheticString, find_resonating_strings


class Excitation(NamedTuple):
    freq: float          # Hz
    amp: float           # 0-1
    source: str          # "melody", "vocal", "dayan", "bayan"
    decay_hint: float    # suggested resonance duration multiplier


class ResonanceEvent(NamedTuple):
    string_index: int
    string_freq: float
    intensity: float     # 0-1
    decay: float         # seconds
    source: str


def compute_resonances(strings: List[SympatheticString],
                       excitations: List[Excitation],
                       threshold_cents: float = 50.0
                       ) -> List[ResonanceEvent]:
    """Compute which strings resonate given current excitations.

    Returns sorted list of ResonanceEvents (strongest first).
    """
    events = []
    seen_strings = set()

    for exc in excitations:
        resonating = find_resonating_strings(strings, exc.freq, threshold_cents)
        for string, proximity in resonating:
            if string.index in seen_strings:
                continue  # each string only fires once per frame
            seen_strings.add(string.index)

            intensity = proximity * exc.amp
            # Source scaling: melody excites most, tabla less
            source_scale = {
                "melody": 1.0, "vocal": 0.8,
                "dayan": 0.5, "bayan": 0.3,
            }.get(exc.source, 0.5)
            intensity *= source_scale

            decay = string.decay * exc.decay_hint
            events.append(ResonanceEvent(
                string_index=string.index,
                string_freq=string.freq,
                intensity=round(min(1.0, intensity), 3),
                decay=round(decay, 2),
                source=exc.source,
            ))

    events.sort(key=lambda e: -e.intensity)
    return events
