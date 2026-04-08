"""
mix_osc.py — Sends mix decisions to SC via OSC.
"""

from typing import Dict, List

try:
    from pythonosc import udp_client
except ImportError:
    udp_client = None

from .graph_seed_data import LAYERS

SC_HOST = "127.0.0.1"
SC_PORT = 57121


class MixOSC:
    """Sends mix decisions to SuperCollider."""

    def __init__(self, host: str = SC_HOST, port: int = SC_PORT):
        self._client = udp_client.SimpleUDPClient(host, port) if udp_client else None

    def send_layers(self, weights: Dict[str, float]):
        """/atlas/mix/layers — all 11 layer amps as floats."""
        if not self._client:
            return
        msg = [float(weights.get(layer, 0.0)) for layer in LAYERS]
        self._client.send_message("/atlas/mix/layers", msg)

    def send_global(self, brightness: float = 0.0, reverb_depth: float = 0.0,
                    reverb_decay: float = 0.0, sub: float = 0.0,
                    compression: float = 0.0):
        """/atlas/mix/global — master timbral parameters."""
        if self._client:
            self._client.send_message("/atlas/mix/global", [
                float(brightness), float(reverb_depth),
                float(reverb_decay), float(sub), float(compression),
            ])

    def send_spatial(self, stereo_width: float = 0.5,
                     center_weight: float = 0.5):
        """/atlas/mix/spatial — stereo field."""
        if self._client:
            self._client.send_message("/atlas/mix/spatial", [
                float(stereo_width), float(center_weight),
            ])

    def send_confidence(self, authority: float):
        """/atlas/mix/confidence — overall boldness."""
        if self._client:
            self._client.send_message("/atlas/mix/confidence", [float(authority)])

    def send_sam_event(self):
        """/atlas/mix/sam_event — immediate convergence."""
        if self._client:
            self._client.send_message("/atlas/mix/sam_event", [])

    def send_khali_event(self):
        """/atlas/mix/khali_event — immediate opening."""
        if self._client:
            self._client.send_message("/atlas/mix/khali_event", [])
