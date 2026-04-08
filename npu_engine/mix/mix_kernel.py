"""
mix_kernel.py — Top coordinator for the relational mixing engine.

Runs every 4 beats (mix changes slowly). Assembles MixState from
all sub-engines, applies smoothing, sends to SC only on meaningful change.

Sam events are immediate (not smoothed). Mode changes use 2-beat transition.
"""

import threading
import time
from typing import Dict, Optional, Callable

from .layer_graph import get_layer_weights
from .nakshatra_mix import get_nakshatra_bias
from .deity_mix import get_deity_bias
from .guna_mix import get_guna_character
from .authority_mix import get_confidence_scale
from .sam_mix import get_sam_event, get_khali_event
from .mix_history import MixHistory
from .mix_osc import MixOSC
from .graph_seed_data import LAYERS


class MixKernel:
    """Relational mixing engine — the balance of all layers."""

    def __init__(self, bpm: float = 72, osc_port: int = 57121):
        self.bpm = bpm
        self.rasa = "shanta"
        self.arc = 0.5
        self.mode = "gat"
        self.element = "ether"
        self.deity = ""
        self.guna = "sattva"
        self.authority = 0.6
        self.playing = False

        self._history = MixHistory()
        self._osc = MixOSC(port=osc_port)
        self._thread = None
        self._overrides: Dict[str, float] = {}
        self._override_expires: Dict[str, float] = {}

    def load_from_field(self, rasa: str, arc: float, mode: str,
                        element: str, deity: str, guna: str,
                        authority: float = 0.6, bpm: float = 72):
        """Update mix parameters from field state."""
        self.rasa = rasa
        self.arc = arc
        self.mode = mode
        self.element = element
        self.deity = deity
        self.guna = guna
        self.authority = authority
        self.bpm = bpm

    def set_override(self, layer: str, value: float, duration_beats: int = 16):
        """Manual override for a layer — returns to relational mix after duration."""
        if layer in LAYERS:
            self._overrides[layer] = value
            beat_dur = 60.0 / max(40, self.bpm)
            self._override_expires[layer] = time.monotonic() + duration_beats * beat_dur

    def start(self):
        if self.playing:
            return
        self.playing = True
        self._thread = threading.Thread(target=self._mix_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.playing = False

    def on_sam(self):
        """Called on sam beat — immediate convergence (bypasses smoothing)."""
        self._osc.send_sam_event()

    def on_khali(self):
        """Called on khali beat — immediate opening."""
        self._osc.send_khali_event()

    def _mix_loop(self):
        """Main loop — runs every 4 beats."""
        while self.playing:
            beat_dur = 60.0 / max(40, self.bpm)
            interval = beat_dur * 4  # mix updates every 4 beats

            try:
                self._compute_and_send()
            except Exception:
                pass

            time.sleep(interval)

    def _compute_and_send(self):
        """Compute full mix state and send if changed."""
        now = time.monotonic()

        # 1. Base layer weights from rasa + arc + mode
        weights = get_layer_weights(self.rasa, self.arc, self.mode)

        # 2. Apply nakshatra element bias (additive)
        nak_bias = get_nakshatra_bias(self.element)
        for layer, offset in nak_bias.items():
            if layer in weights:
                weights[layer] = max(0.0, min(1.0, weights[layer] + offset))

        # 3. Apply deity bias (additive)
        deity_bias = get_deity_bias(self.deity)
        for layer, offset in deity_bias.items():
            if layer in weights:
                weights[layer] = max(0.0, min(1.0, weights[layer] + offset))

        # 4. Authority scaling
        conf = get_confidence_scale(self.authority)
        for layer in weights:
            weights[layer] *= conf.overall_scale
        # Push drone higher when uncertain
        if "tanpura" in weights:
            weights["tanpura"] = min(1.0, weights["tanpura"] + conf.drone_bias)
        if "mantra_drone" in weights:
            weights["mantra_drone"] = min(1.0, weights["mantra_drone"] + conf.drone_bias)

        # 5. Apply manual overrides
        for layer, val in list(self._overrides.items()):
            if now > self._override_expires.get(layer, 0):
                del self._overrides[layer]
                self._override_expires.pop(layer, None)
            elif layer in weights:
                weights[layer] = val

        # 6. Smooth
        smoothed = self._history.smooth(weights, time_constant=0.4)

        # 7. Send if meaningful change
        if self._history.detect_change(smoothed, threshold=0.015):
            self._osc.send_layers(smoothed)

        # 8. Send global timbral character
        guna_char = get_guna_character(self.guna)
        self._osc.send_global(
            brightness=guna_char.get("brightness", 0.0),
            reverb_depth=guna_char.get("reverb", 0.0) + conf.reverb_add,
            reverb_decay=guna_char.get("reverb_decay", 0.0),
            sub=guna_char.get("sub", 0.0),
            compression=guna_char.get("compression", 0.0),
        )

        # 9. Send authority
        self._osc.send_confidence(self.authority)
