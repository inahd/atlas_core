"""
sympathetic_osc.py — Sends sympathetic string events to SC via OSC.

Messages:
  /atlas/sympathetic/tune    — retune all 13 strings (on raga change)
  /atlas/sympathetic/excite  — trigger resonance on specific strings
  /atlas/sympathetic/damp    — damp all strings (on silence/breath)
  /atlas/sympathetic/level   — set overall sympathetic volume
"""

from typing import List

try:
    from pythonosc import udp_client
except ImportError:
    udp_client = None

from .string_model import SympatheticString
from .excitation import ResonanceEvent

SC_HOST = "127.0.0.1"
SC_PORT = 57121


class SympatheticOSC:
    """Sends sympathetic string events to SuperCollider."""

    def __init__(self, host: str = SC_HOST, port: int = SC_PORT):
        self._client = udp_client.SimpleUDPClient(host, port) if udp_client else None

    def send_tune(self, strings: List[SympatheticString]):
        """/atlas/sympathetic/tune — retune all 13 strings.

        Sends: [freq0, decay0, freq1, decay1, ... freq12, decay12]
        """
        if not self._client:
            return
        msg = []
        for s in strings[:13]:
            msg.extend([float(s.freq), float(s.decay)])
        # Pad to 13 strings if fewer
        while len(msg) < 26:
            msg.extend([0.0, 0.0])
        self._client.send_message("/atlas/sympathetic/tune", msg)

    def send_excite(self, events: List[ResonanceEvent]):
        """/atlas/sympathetic/excite — trigger resonance on strings.

        Sends: [string_idx, intensity, decay, string_idx, intensity, decay, ...]
        Up to 4 simultaneous excitations per message.
        """
        if not self._client:
            return
        msg = []
        for e in events[:4]:
            msg.extend([int(e.string_index), float(e.intensity), float(e.decay)])
        if msg:
            self._client.send_message("/atlas/sympathetic/excite", msg)

    def send_damp(self):
        """/atlas/sympathetic/damp — damp all strings."""
        if self._client:
            self._client.send_message("/atlas/sympathetic/damp", [])

    def send_level(self, level: float):
        """/atlas/sympathetic/level — set overall volume 0-1."""
        if self._client:
            self._client.send_message("/atlas/sympathetic/level", [float(level)])
