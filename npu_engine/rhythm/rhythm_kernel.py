"""
rhythm_kernel.py — Top coordinator for the relational rhythm engine.

Runs on its own thread at tala beat resolution. Every beat:
  1. Compute sam-gravity
  2. Generate theka bol
  3. Check tihai opportunity
  4. Check fill opportunity
  5. Update layakari
  6. Send all decisions to SC
  7. Broadcast gravity to other kernels

Sam events trigger cross-system synchronization.
"""

import threading
import time
from typing import Callable, Optional

from .tala_graph import get_tala, beat_to_vibhag
from .sam_field import get_gravity, is_approaching_sam
from .theka_engine import generate_theka_cycle, BolEvent
from .layakari_engine import get_layakari
from .tihai_engine import find_tihai
from .fill_engine import get_fill
from .cross_rhythm_engine import get_cross_rhythm
from .rhythm_osc import RhythmOSC


class RhythmKernel:
    """Relational rhythm engine — the gravitational field of time."""

    def __init__(self, bpm: float = 72, osc_port: int = 57121):
        self.bpm = bpm
        self.tala_name = "Adi"
        self.mode = "gat"
        self.arc = 0.5
        self.rasa = "shanta"
        self.playing = False
        self.layakari = 1.0

        # Tracking
        self.current_beat = 0
        self.cycle_count = 0

        # Gravity field (read by other kernels)
        self.gravity = 0.5
        self.approaching_sam = False

        # OSC
        self._osc = RhythmOSC(port=osc_port)
        self._thread = None

        # Optional callbacks for cross-kernel sync
        self._on_sam: Optional[Callable] = None
        self._on_beat: Optional[Callable] = None

    def load_from_field(self, tala_name: str, bpm: float,
                        mode: str = "gat", rasa: str = "shanta",
                        arc: float = 0.5):
        """Update rhythm parameters from field state."""
        self.tala_name = tala_name
        self.bpm = max(40, min(200, bpm))
        self.mode = mode
        self.rasa = rasa
        self.arc = arc

    def start(self):
        if self.playing:
            return
        self.playing = True
        self._thread = threading.Thread(target=self._beat_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.playing = False

    def on_sam(self, callback: Callable):
        """Register callback for sam events (cross-kernel sync)."""
        self._on_sam = callback

    def on_beat(self, callback: Callable):
        """Register callback for every beat."""
        self._on_beat = callback

    def _beat_loop(self):
        """Main loop — one iteration per beat."""
        # Pre-generate theka for current cycle
        theka_cycle = []
        theka_idx = 0
        in_tihai = False
        tihai_remaining = []

        while self.playing:
            tala = get_tala(self.tala_name)
            beat_dur = 60.0 / max(40, self.bpm) / self.layakari
            pos_in_cycle = self.current_beat % tala.beats

            # ── 1. Sam-gravity ────────────────────────
            self.gravity = get_gravity(self.current_beat, self.tala_name, self.layakari)
            self.approaching_sam = is_approaching_sam(self.current_beat, self.tala_name)
            vib = beat_to_vibhag(self.current_beat, tala)

            # Broadcast beat
            self._osc.send_beat(pos_in_cycle, vib, self.gravity, self.approaching_sam)
            if self._on_beat:
                try:
                    self._on_beat(pos_in_cycle, self.gravity, self.approaching_sam)
                except Exception:
                    pass

            # ── 2. Sam event ──────────────────────────
            if pos_in_cycle == tala.sam:
                self._osc.send_sam()
                self.cycle_count += 1
                if self._on_sam:
                    try:
                        self._on_sam()
                    except Exception:
                        pass

                # Regenerate theka for new cycle
                theka_cycle = generate_theka_cycle(
                    self.tala_name, self.mode, self.arc, self.rasa)
                theka_idx = 0

            # ── 3. Generate bol ───────────────────────
            if not in_tihai and theka_idx < len(theka_cycle):
                event = theka_cycle[theka_idx]
                if event.bol:  # empty string = silence
                    from .tala_graph import get_bol_properties
                    bp = get_bol_properties(event.bol)
                    self._osc.send_bol(
                        event.bol, bp.weight, bp.resonance,
                        bp.hand, event.amp)
                theka_idx += 1

            # ── 4. Tihai check ────────────────────────
            if not in_tihai and self.approaching_sam and self.arc > 0.5:
                tihai = find_tihai(pos_in_cycle, self.tala_name, tala.beats)
                if tihai:
                    self._osc.send_tihai(tihai.phrase, tihai.gap_beats)
                    # Build tihai execution queue
                    tihai_remaining = []
                    for rep in range(3):
                        tihai_remaining.extend(tihai.phrase)
                        if rep < 2 and tihai.gap_beats > 0:
                            tihai_remaining.extend([""] * tihai.gap_beats)
                    in_tihai = True

            # Execute tihai if active
            if in_tihai and tihai_remaining:
                bol = tihai_remaining.pop(0)
                if bol:
                    from .tala_graph import get_bol_properties
                    bp = get_bol_properties(bol)
                    self._osc.send_bol(bol, bp.weight, bp.resonance, bp.hand, 0.85)
                if not tihai_remaining:
                    in_tihai = False

            # ── 5. Fill check ─────────────────────────
            if not in_tihai:
                fill = get_fill(pos_in_cycle, self.tala_name, self.mode,
                                self.rasa, self.arc)
                if fill:
                    self._osc.send_fill(fill.fill_type, fill.intensity)

            # ── 6. Layakari update ────────────────────
            if pos_in_cycle == tala.sam:
                new_lay = get_layakari(self.mode, self.arc, self.layakari)
                if new_lay != self.layakari:
                    self.layakari = new_lay
                    self._osc.send_layakari(new_lay)

            # ── 7. Cross rhythm ───────────────────────
            if pos_in_cycle == tala.sam and self.arc > 0.4:
                cross = get_cross_rhythm(self.tala_name, tala.beats,
                                         self.rasa, self.arc)
                if cross:
                    self._osc.send_cross(cross.subdivision, cross.resolution_beat)

            self.current_beat += 1
            time.sleep(beat_dur)
