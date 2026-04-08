"""
rhythm_osc.py — Sends all rhythm decisions to SC via OSC.
"""

from typing import List, Optional

try:
    from pythonosc import udp_client
except ImportError:
    udp_client = None

SC_HOST = "127.0.0.1"
SC_PORT = 57121


class RhythmOSC:
    """Sends rhythm decisions to SuperCollider."""

    def __init__(self, host: str = SC_HOST, port: int = SC_PORT):
        self._client = udp_client.SimpleUDPClient(host, port) if udp_client else None

    def send_beat(self, beat_num: int, vibhag: int,
                  gravity: float, approaching_sam: bool):
        """/atlas/rhythm/beat — broadcast every beat."""
        if self._client:
            self._client.send_message("/atlas/rhythm/beat", [
                int(beat_num), int(vibhag), float(gravity),
                int(approaching_sam),
            ])

    def send_bol(self, bol_name: str, weight: float, resonance: str,
                 hand: str, amp: float):
        """/atlas/rhythm/bol — trigger a tabla bol."""
        # Map resonance/hand to indices for SC
        res_idx = {"open": 0, "closed": 1, "resonant": 2, "resonant_long": 3,
                   "dry": 4, "ornamental": 5, "fill": 6}.get(resonance, 0)
        hand_idx = {"both": 0, "left": 1, "right_open": 2, "right_closed": 3}.get(hand, 2)
        if self._client:
            self._client.send_message("/atlas/rhythm/bol", [
                bol_name, float(weight), int(res_idx), int(hand_idx), float(amp),
            ])

    def send_layakari(self, factor: float):
        """/atlas/rhythm/layakari — set density multiplication."""
        if self._client:
            self._client.send_message("/atlas/rhythm/layakari", [float(factor)])

    def send_tihai(self, phrase_bols: List[str], gap_beats: int):
        """/atlas/rhythm/tihai — announce upcoming tihai."""
        if self._client:
            msg = phrase_bols + [str(gap_beats), "3"]  # always 3 reps
            self._client.send_message("/atlas/rhythm/tihai", msg)

    def send_sam(self):
        """/atlas/rhythm/sam — the gravitational center announces itself."""
        if self._client:
            self._client.send_message("/atlas/rhythm/sam", [])

    def send_cross(self, subdivision: int, resolution_beat: int):
        """/atlas/rhythm/cross — cross-rhythm activation."""
        if self._client:
            self._client.send_message("/atlas/rhythm/cross", [
                int(subdivision), int(resolution_beat),
            ])

    def send_fill(self, fill_type: str, intensity: float):
        """/atlas/rhythm/fill — rhythmic fill activation."""
        if self._client:
            self._client.send_message("/atlas/rhythm/fill", [
                fill_type, float(intensity),
            ])
