"""
sympathetic_kernel.py — Top coordinator for sympathetic string resonance.

Monitors melody/vocal/tabla activity and triggers sympathetic resonance.
Retunes strings on raga change. Damps on breath/silence.

The sympathetic strings are the raga made physical — they ARE the scale,
vibrating in sympathy with whatever is being played.
"""

import threading
import time
from typing import List, Optional

from .string_model import tune_strings, SympatheticString
from .excitation import Excitation, compute_resonances
from .sympathetic_osc import SympatheticOSC


class SympatheticKernel:
    """Relational sympathetic string resonance engine."""

    def __init__(self, sa_freq: float = 261.63, osc_port: int = 57121):
        self.sa = sa_freq
        self.playing = False
        self.level = 0.12  # subtle shimmer, not loud

        # Current string tuning
        self._strings: List[SympatheticString] = []
        self._scale = [0, 2, 4, 5, 7, 9, 11]
        self._vadi = 4
        self._samvadi = 11
        self._last_raga = ""

        # Excitation queue (thread-safe via simple replacement)
        self._pending_excitations: List[Excitation] = []

        self._osc = SympatheticOSC(port=osc_port)
        self._thread = None

    def load_from_field(self, raga_name: str, scale: List[int],
                        vadi: int = -1, samvadi: int = -1,
                        sa: float = 0):
        """Update from field state. Retunes strings on raga change."""
        if sa > 0:
            self.sa = sa

        raga_changed = (raga_name != self._last_raga or scale != self._scale)
        self._scale = scale
        self._vadi = vadi
        self._samvadi = samvadi
        self._last_raga = raga_name

        if raga_changed:
            self._retune()

    def _retune(self):
        """Retune all 13 strings and send to SC."""
        self._strings = tune_strings(
            self.sa, self._scale, self._vadi, self._samvadi)
        self._osc.send_tune(self._strings)

    def excite_melody(self, freq: float, amp: float = 0.8):
        """Called when a melody note fires."""
        self._pending_excitations.append(
            Excitation(freq=freq, amp=amp, source="melody", decay_hint=1.0))

    def excite_vocal(self, freq: float, amp: float = 0.6):
        """Called when a vocal svara fires."""
        self._pending_excitations.append(
            Excitation(freq=freq, amp=amp, source="vocal", decay_hint=0.8))

    def excite_tabla(self, freq: float, source: str = "dayan",
                     amp: float = 0.4):
        """Called when tabla fires — dayan excites at Sa harmonics."""
        self._pending_excitations.append(
            Excitation(freq=freq, amp=amp, source=source, decay_hint=0.6))

    def damp(self):
        """Damp all strings — called on breath/silence."""
        self._osc.send_damp()

    def start(self):
        """Start the resonance processing thread."""
        if self.playing:
            return
        self.playing = True
        self._retune()
        self._osc.send_level(self.level)
        self._thread = threading.Thread(target=self._process_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.playing = False
        self._osc.send_damp()

    def _process_loop(self):
        """Process excitation queue and send resonance events to SC.

        Runs at ~30Hz — fast enough for musical responsiveness,
        slow enough to batch excitations within a beat subdivision.
        """
        while self.playing:
            # Grab and clear pending excitations
            excitations = self._pending_excitations
            self._pending_excitations = []

            if excitations and self._strings:
                events = compute_resonances(
                    self._strings, excitations, threshold_cents=50.0)
                if events:
                    self._osc.send_excite(events[:4])  # max 4 per frame

            time.sleep(0.033)  # ~30Hz
