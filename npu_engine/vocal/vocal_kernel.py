"""
vocal_kernel.py — Top-level coordinator for the relational vocal engine.

Called by composition_kernel on every phrase decision. Queries all
sub-engines, assembles vocal phrases, sends to SC via OSC.

Runs in its own thread, phrase generation rate tied to mode:
  alap: one phrase every 8-20 seconds
  gat:  phrases every 2-4 beats
  taan: continuous, phrases overlap

The epistemological principle:
  shastra → full voice, on the beat, ornaments bold
  sadhu   → present, slightly inflected, ornaments moderate
  guru    → quiet, between beats, ornaments subtle
  experimental → barely a whisper, breath more than tone
"""

import threading
import time
from typing import Dict, Optional

from .bhava_engine import BhavaState
from .gamaka_engine import get_gamaka
from .svara_voice import get_svara_quality
from .breath_engine import get_breath_positions
from .syllable_sequencer import (
    sequence_for_alap, sequence_for_bija, VocalElement,
)
from .vocal_osc import VocalOSC


class VocalKernel:
    """Relational vocal engine — the voice speaks the graph."""

    def __init__(self, sa_freq: float = 130.81, osc_port: int = 57121):
        self.sa = sa_freq
        self.playing = False
        self.mode = "gat"       # alap, gat, taan
        self.arc = 0.5          # compositional arc position 0-1
        self.rasa = "shanta"
        self.raga_name = "Yaman"
        self.tala_name = "Adi"
        self.nakshatra_entry = None
        self.graph = None       # GraphEngine instance if available
        self.bpm = 72

        self._bhava = BhavaState()
        self._osc = VocalOSC(port=osc_port)
        self._thread = None
        self._last_nakshatra = ""

    def load_from_field(self, field_state: dict, nakshatra_entry: dict,
                        graph=None):
        """Update vocal kernel from field state + nakshatra profile.

        Called by sc_bridge or live_sound on field change.
        """
        self.graph = graph
        self.nakshatra_entry = nakshatra_entry

        p = field_state.get("panchanga", {})
        ss = field_state.get("sound_state", {})
        mu = field_state.get("muhurta", {})

        self.raga_name = nakshatra_entry.get("raga", "Yaman")
        self.tala_name = nakshatra_entry.get("tala", "Adi")
        self.rasa = nakshatra_entry.get("guna", "sattva")  # rough rasa from guna
        self.bpm = int(ss.get("bpm") or mu.get("bpm") or 72)

        # Detect nakshatra change → trigger bija
        nak_name = p.get("nakshatra", "")
        if nak_name != self._last_nakshatra and self._last_nakshatra:
            self._trigger_bija()
        self._last_nakshatra = nak_name

    def start(self):
        """Start the vocal phrase generation thread."""
        if self.playing:
            return
        self.playing = True
        self._thread = threading.Thread(target=self._phrase_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.playing = False

    def set_mode(self, mode: str):
        """Set performance mode: alap, gat, taan."""
        if mode in ("alap", "gat", "taan"):
            self.mode = mode

    def set_arc(self, arc: float):
        """Set compositional arc position (0.0-1.0)."""
        self.arc = max(0.0, min(1.0, arc))

    def _phrase_loop(self):
        """Main generation loop — rate adapts to mode."""
        while self.playing:
            if self.nakshatra_entry is None:
                time.sleep(1)
                continue

            try:
                self._generate_phrase()
            except Exception as e:
                # Don't crash the thread
                time.sleep(2)
                continue

            # Pacing by mode
            beat_dur = 60.0 / max(40, self.bpm)
            if self.mode == "alap":
                import random
                time.sleep(random.uniform(8.0, 20.0))
            elif self.mode == "taan":
                time.sleep(beat_dur * 1.5)
            else:  # gat
                time.sleep(beat_dur * 3)

    def _generate_phrase(self):
        """Generate and send one vocal phrase.

        This is the core graph traversal:
          nakshatra → deity → phonemes
          raga → vadi → svara_quality
          rasa → bhava state
          tala → breath positions
          authority → confidence → dynamic placement
        """
        entry = self.nakshatra_entry
        if not entry:
            return

        # Build phrase from graph
        elements = sequence_for_alap(
            entry, self.raga_name, self._bhava, self.rasa,
            self.arc, self.tala_name, self.graph,
        )

        # Get register from bhava
        bhava_state = self._bhava.update(self.rasa, self.arc)
        register = bhava_state.get("register", 0)
        self._osc.send_register(register)

        # Send bhava coloring
        self._osc.send_bhava(
            bhava_state.get("bhava_index", 5),
            bhava_state.get("intensity", 0.5),
        )

        # Send each element
        note_freq = self.sa * (2 ** register)
        for elem in elements:
            if not self.playing:
                break

            # Confidence → placement timing
            delay = _confidence_delay(elem.confidence)
            if delay > 0:
                time.sleep(delay)

            # Send to SC
            self._osc.send_element(elem, note_freq)

            # Wait for element duration (scaled by confidence)
            wait = elem.duration
            if elem.is_breath:
                time.sleep(wait)
            else:
                time.sleep(wait * 0.7)  # slight overlap between elements

    def _trigger_bija(self):
        """Trigger a bija mantra phrase on nakshatra transition."""
        if not self.nakshatra_entry:
            return

        elements = sequence_for_bija(
            self.nakshatra_entry, self._bhava, self.rasa, self.arc)

        note_freq = self.sa * 0.5  # low register for bija
        for elem in elements:
            self._osc.send_element(elem, note_freq)
            time.sleep(elem.duration * 0.7)


def _confidence_delay(confidence: float) -> float:
    """Map confidence to micro-timing offset.

    High confidence = on the beat (0 delay).
    Low confidence = slightly late (grace note territory).
    Very low = very late (whispered suggestion).
    """
    if confidence > 0.8:
        return 0.0            # shastra: on the beat
    elif confidence > 0.5:
        return 0.02           # sadhu: barely perceptible delay
    elif confidence > 0.3:
        return 0.05           # inference: grace note timing
    else:
        return 0.1            # experimental: noticeably late
