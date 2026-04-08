"""
vocal_osc.py — Sends vocal decisions to SuperCollider via OSC.

Maps vocal engine outputs to SC messages on port 57121.
Each message type corresponds to a specific SC handler.
"""

from typing import Optional

try:
    from pythonosc import udp_client
except ImportError:
    udp_client = None

from .syllable_sequencer import VocalElement
from .gamaka_engine import GamakaInstruction
from .graph_seed_data import BHAVA_INDEX

SC_HOST = "127.0.0.1"
SC_PORT = 57121


class VocalOSC:
    """Sends vocal decisions to SuperCollider."""

    def __init__(self, host: str = SC_HOST, port: int = SC_PORT):
        if udp_client is None:
            self._client = None
        else:
            self._client = udp_client.SimpleUDPClient(host, port)

    def send_phoneme(self, syllable: str, f1: float, f2: float,
                     f3: float, bw: float, dur: float, confidence: float):
        """/atlas/vocal/phoneme — trigger a formant syllable."""
        if self._client:
            self._client.send_message("/atlas/vocal/phoneme", [
                syllable, float(f1), float(f2), float(f3),
                float(bw), float(dur), float(confidence),
            ])

    def send_gamaka(self, type_index: int, depth: float,
                    rate: float, note_freq: float):
        """/atlas/vocal/gamaka — queue a gamaka for the next vocal note."""
        if self._client:
            self._client.send_message("/atlas/vocal/gamaka", [
                int(type_index), float(depth), float(rate), float(note_freq),
            ])

    def send_bhava(self, bhava_index: int, intensity: float):
        """/atlas/vocal/bhava — set emotional coloring."""
        if self._client:
            self._client.send_message("/atlas/vocal/bhava", [
                int(bhava_index), float(intensity),
            ])

    def send_breath(self, duration_seconds: float):
        """/atlas/vocal/breath — schedule a silence."""
        if self._client:
            self._client.send_message("/atlas/vocal/breath", [
                float(duration_seconds),
            ])

    def send_register(self, octave_shift: int):
        """/atlas/vocal/register — shift vocal register."""
        if self._client:
            self._client.send_message("/atlas/vocal/register", [
                int(octave_shift),
            ])

    def send_svara(self, freq: float, rasa_index: int, ornament_type: int):
        """/atlas/vocal/svara — trigger a melodic vocal note."""
        if self._client:
            self._client.send_message("/atlas/vocal/svara", [
                float(freq), int(rasa_index), int(ornament_type),
            ])

    def send_element(self, element: VocalElement, note_freq: float = 130.0):
        """Send a complete VocalElement as the appropriate OSC messages.

        This is the main method called by vocal_kernel — it figures out
        which messages to send based on the element's content.
        """
        if not self._client:
            return

        if element.is_breath:
            self.send_breath(element.duration)
            return

        # Send bhava first (sets coloring for subsequent notes)
        bhava = element.bhava_params
        if bhava:
            self.send_bhava(
                bhava.get("bhava_index", 5),
                bhava.get("intensity", 0.5),
            )

        # Send gamaka if present (queues for next note)
        if element.gamaka:
            g = element.gamaka
            self.send_gamaka(g.type_index, g.depth, g.rate, note_freq)

        # Send the phoneme
        f = element.formant
        self.send_phoneme(
            element.syllable,
            f["f1"], f["f2"], f["f3"], f["bw"],
            element.duration,
            element.confidence,
        )
