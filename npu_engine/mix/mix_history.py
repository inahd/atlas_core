"""
mix_history.py — Smoothing and change detection for mix state.

Prevents rapid flickering, overcrowded moments, sudden silences.
"""

from typing import Dict, List
from collections import deque


class MixHistory:
    """Circular buffer of mix states with smoothing."""

    def __init__(self, size: int = 32):
        self._buffer: deque = deque(maxlen=size)
        self._last_sent: Dict[str, float] = {}

    def smooth(self, new_mix: Dict[str, float],
               time_constant: float = 0.3) -> Dict[str, float]:
        """Smooth new mix values against recent history.

        time_constant: 0=no smoothing, 1=maximum smoothing.
        Returns smoothed mix values.
        """
        if not self._buffer:
            self._buffer.append(dict(new_mix))
            return dict(new_mix)

        prev = self._buffer[-1]
        smoothed = {}
        tc = max(0.0, min(0.95, time_constant))

        for key in new_mix:
            old = prev.get(key, new_mix[key])
            smoothed[key] = round(old * tc + new_mix[key] * (1 - tc), 4)

        self._buffer.append(smoothed)
        return smoothed

    def detect_change(self, new_mix: Dict[str, float],
                      threshold: float = 0.02) -> bool:
        """Only return True if meaningful change detected.

        Prevents sending OSC on every tick when nothing changed.
        """
        if not self._last_sent:
            self._last_sent = dict(new_mix)
            return True

        for key, val in new_mix.items():
            if abs(val - self._last_sent.get(key, 0)) > threshold:
                self._last_sent = dict(new_mix)
                return True
        return False

    def get_density_arc(self) -> float:
        """Compute overall mix density over recent history.

        Returns 0.0 (sparse) to 1.0 (dense).
        """
        if not self._buffer:
            return 0.5
        recent = list(self._buffer)[-8:]
        total = sum(sum(m.values()) / max(len(m), 1) for m in recent)
        return min(1.0, total / max(len(recent), 1))
