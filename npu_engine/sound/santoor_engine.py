"""
santoor_engine.py — Santoor melodic layer engine.

Generates raga phrases from field state and sends
them to SuperCollider via OSC with correct timing.

The santoor is the melodic voice of the Atlas sound field.
4 detuned CombL strings per note create the characteristic shimmer.
"""

import logging
import random
import threading
import time
from typing import Dict, List, Optional, Tuple

log = logging.getLogger(__name__)

SC_HOST = "127.0.0.1"
SC_PORT = 57120

# ── Swara ratios (22-shruti Just Intonation) ──
SWARA_RATIOS = {
    'Sa':  1.0,
    'Re':  9/8,       # shuddha Re
    're':  16/15,     # komal Re
    'Ga':  5/4,       # shuddha Ga
    'ga':  6/5,       # komal Ga
    'Ma':  4/3,       # shuddha Ma
    'ma':  45/32,     # tivra Ma
    'Pa':  3/2,
    'Dha': 5/3,       # shuddha Dha
    'dha': 8/5,       # komal Dha
    'Ni':  15/8,      # shuddha Ni
    'ni':  9/5,       # komal Ni
    'SA':  2.0,       # upper Sa
}

# ── Raga phrase profiles ──
RAGA_PROFILES = {
    'Bihag': {
        'aroha': ['Sa', 'Ga', 'ma', 'Pa', 'Ni', 'SA'],
        'avaroha': ['SA', 'Ni', 'Dha', 'Pa', 'Ma', 'Ga', 'Re', 'Sa'],
        'vadi': 'Ga',
        'samvadi': 'Ni',
        'characteristic_phrases': [
            ['Sa', 'Ga', 'ma', 'Pa'],
            ['Pa', 'Ma', 'Ga'],         # descending gamak
            ['Ga', 'ma', 'Pa', 'Ni', 'SA'],
            ['SA', 'Ni', 'Dha', 'Pa'],
            ['Pa', 'Ma', 'Ga', 'Re', 'Sa'],
            ['Ga', 'ma', 'Ga'],         # oscillation on Ga
            ['Ni', 'SA', 'Ni', 'Dha', 'Pa'],
        ],
        'pakad': ['Ga', 'ma', 'Pa', 'Ni', 'SA', 'Ni', 'Dha', 'Pa', 'Ma', 'Ga'],
    },
    'Yaman': {
        'aroha': ['Sa', 'Re', 'Ga', 'ma', 'Pa', 'Dha', 'Ni', 'SA'],
        'avaroha': ['SA', 'Ni', 'Dha', 'Pa', 'ma', 'Ga', 'Re', 'Sa'],
        'vadi': 'Ga',
        'samvadi': 'Ni',
        'characteristic_phrases': [
            ['Ni', 'Re', 'Ga', 'Re', 'Sa'],
            ['Pa', 'ma', 'Ga', 'Re', 'Sa'],
            ['Ga', 'ma', 'Dha', 'Ni', 'SA'],
        ],
        'pakad': ['Ni', 'Re', 'Ga', 'Re', 'Sa'],
    },
    'Bhairav': {
        'aroha': ['Sa', 're', 'Ga', 'Ma', 'Pa', 'dha', 'Ni', 'SA'],
        'avaroha': ['SA', 'Ni', 'dha', 'Pa', 'Ma', 'Ga', 're', 'Sa'],
        'vadi': 'dha',
        'samvadi': 're',
        'characteristic_phrases': [
            ['Sa', 're', 'Ga', 'Ma'],
            ['Ma', 'Ga', 're', 'Sa'],
            ['Pa', 'dha', 'Ni', 'SA'],
        ],
        'pakad': ['re', 'Ga', 're', 'Sa'],
    },
}


def _swara_to_hz(swara: str, sa_hz: float) -> float:
    """Convert swara name to frequency."""
    ratio = SWARA_RATIOS.get(swara, 1.0)
    return sa_hz * ratio


def get_phrase_style(field_state: dict) -> dict:
    """Determine phrase style from field state."""
    pa = field_state.get("panchanga", {})
    guna = (pa.get("guna", "") or "").lower()
    coherence = field_state.get("svarodaya", {}).get("coherence_score", 0.5)
    if isinstance(coherence, str):
        try:
            coherence = float(coherence)
        except ValueError:
            coherence = 0.5

    if "tamas" in guna:
        return {"tempo": "slow", "density": "sparse",
                "note_dur": (0.8, 2.0), "rest_prob": 0.4,
                "amp_range": (0.2, 0.35)}
    elif "rajas" in guna:
        return {"tempo": "medium", "density": "medium",
                "note_dur": (0.3, 0.8), "rest_prob": 0.15,
                "amp_range": (0.3, 0.45)}
    else:  # sattva
        return {"tempo": "medium", "density": "balanced",
                "note_dur": (0.5, 1.2), "rest_prob": 0.25,
                "amp_range": (0.25, 0.4)}


def santoor_phrase(field_state: dict, sa_hz: float = 130.81) -> List[Tuple[float, float, float, float]]:
    """Generate one santoor phrase as list of (freq, amp, dur, pan)."""
    ss = field_state.get("sound_state", {})
    raga_name = ss.get("raga", "Bihag")

    # Normalize raga name
    raga_key = None
    for k in RAGA_PROFILES:
        if k.lower() in raga_name.lower() or raga_name.lower() in k.lower():
            raga_key = k
            break
    if not raga_key:
        raga_key = "Bihag"  # default

    profile = RAGA_PROFILES[raga_key]
    style = get_phrase_style(field_state)

    # Choose phrase source
    sources = profile["characteristic_phrases"] + [profile["aroha"], profile["avaroha"]]
    phrase_swaras = random.choice(sources)

    # Occasionally use pakad (signature phrase)
    if random.random() < 0.25 and "pakad" in profile:
        phrase_swaras = profile["pakad"]

    # Vary length: sometimes truncate, sometimes extend
    if random.random() < 0.3:
        phrase_swaras = phrase_swaras[:random.randint(3, len(phrase_swaras))]

    notes = []
    for swara in phrase_swaras:
        freq = _swara_to_hz(swara, sa_hz)
        is_vadi = swara == profile.get("vadi", "")
        is_samvadi = swara == profile.get("samvadi", "")

        # Duration: vadi gets longer, samvadi slightly longer
        min_dur, max_dur = style["note_dur"]
        dur = random.uniform(min_dur, max_dur)
        if is_vadi:
            dur *= 1.5  # Emphasize vadi
        elif is_samvadi:
            dur *= 1.2

        # Amplitude: vadi louder
        min_amp, max_amp = style["amp_range"]
        amp = random.uniform(min_amp, max_amp)
        if is_vadi:
            amp *= 1.3
        amp = min(0.5, amp)

        # Pan: slight random stereo for shimmer
        pan = random.uniform(-0.3, 0.3)

        notes.append((freq, amp, dur, pan))

    return notes


class SantoorEngine:
    """Plays santoor phrases via OSC to SuperCollider."""

    def __init__(self, sc_port=SC_PORT):
        self.playing = False
        self._thread = None
        self._client = None
        self._sc_port = sc_port

    def _get_client(self):
        if self._client is None:
            try:
                from pythonosc.udp_client import SimpleUDPClient
                self._client = SimpleUDPClient(SC_HOST, self._sc_port)
            except ImportError:
                log.warning("pythonosc not installed")
                return None
        return self._client

    def start(self, field_state):
        if self.playing:
            return
        self.playing = True
        client = self._get_client()
        if client:
            client.send_message("/atlas/santoor/start", [])
        self._thread = threading.Thread(
            target=self._phrase_loop,
            args=(field_state,),
            daemon=True,
        )
        self._thread.start()
        log.info("Santoor started")

    def stop(self):
        self.playing = False
        client = self._get_client()
        if client:
            client.send_message("/atlas/santoor/stop", [])
        log.info("Santoor stopped")

    def _phrase_loop(self, field_state):
        client = self._get_client()
        if not client:
            return

        ss = field_state.get("sound_state", {})
        sa_hz = ss.get("sa_hz", 130.81)
        if isinstance(sa_hz, str):
            try:
                sa_hz = float(sa_hz)
            except ValueError:
                sa_hz = 130.81

        while self.playing:
            try:
                style = get_phrase_style(field_state)
                notes = santoor_phrase(field_state, sa_hz)

                for freq, amp, dur, pan in notes:
                    if not self.playing:
                        break
                    client.send_message(
                        "/atlas/santoor/note",
                        [float(freq), float(amp), float(dur), float(pan)],
                    )
                    time.sleep(dur)

                # Rest between phrases
                rest_time = random.uniform(0.5, 2.0) * (1.0 + style.get("rest_prob", 0.3))
                time.sleep(rest_time)

            except Exception as e:
                log.warning("santoor phrase error: %s", e)
                time.sleep(1.0)


# Module-level instance
_engine = SantoorEngine()


def start_santoor(field_state: dict):
    _engine.start(field_state)


def stop_santoor():
    _engine.stop()


def is_playing() -> bool:
    return _engine.playing
