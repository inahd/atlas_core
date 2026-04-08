"""
phrase_engine.py — Live relational composition engine.

Walks the raga_graph in real time, weighted by:
  - Field state (rasa, arc, tithi, element)
  - Natal musician reading (tempo_feel, rest_density, phrase_arc,
    gamak_emphasis, field_tensions)
  - Performance mode (alap / gat / taan)

Not a sequencer. Not a random walk.
A musician reading a field and choosing the next swara.

Output: stream of NoteEvents consumed by om.py fill_buffer()
Each NoteEvent: {swara, freq_hz, duration_beats, amplitude, gamak}
"""

import threading
import time
import random
import math
from typing import List, Dict, Optional, NamedTuple
from collections import deque

from .raga_graph import RAGA_GRAPHS, JI_RATIOS, get_raga_graph

# Gamaka engine from vocal/ — queries svara-raga-rasa graph for ornaments
try:
    from .vocal.gamaka_engine import get_gamaka as _graph_gamaka
except ImportError:
    _graph_gamaka = None

# Bhava engine for emotional contour shaping
try:
    from .vocal.bhava_engine import BhavaState as _BhavaState
except ImportError:
    _BhavaState = None

# Swara engine — planetary gaze → note character
try:
    from .swara_engine import SwaraEngine, NODE_TO_SWARA
except ImportError:
    SwaraEngine = None
    NODE_TO_SWARA = {}

# Node name → gamaka engine swara key mapping
_NODE_TO_GAMAKA_KEY = {
    "Sa": "S", "Re_k": "r", "Re": "R", "Ga_k": "g", "Ga": "G",
    "Ma": "M", "Ma_t": "M", "Pa": "P", "Dha_k": "d", "Dha": "D",
    "Ni_k": "n", "Ni": "N",
}


class NoteEvent(NamedTuple):
    swara:        str      # e.g. "Ga", "Pa", "Re_k"
    freq_hz:      float    # absolute frequency
    duration_sec: float    # how long to hold
    amplitude:    float    # 0-1
    gamak:        str      # "none", "meend", "andolana", "kan", "silence"
    is_nyasa:     bool     # landing note — hold longer


# ── Performance modes ─────────────────────────────────────────────
PERF_MODES = {
    "alap":  {"density": 0.2, "speed": 0.4, "rest_mult": 2.0,  "taan": False},
    "jod":   {"density": 0.5, "speed": 0.7, "rest_mult": 1.2,  "taan": False},
    "gat":   {"density": 0.7, "speed": 1.0, "rest_mult": 0.8,  "taan": False},
    "taan":  {"density": 1.0, "speed": 2.5, "rest_mult": 0.2,  "taan": True},
}


def arc_to_mode(arc: float) -> str:
    if arc < 0.15:  return "alap"
    if arc < 0.45:  return "jod"
    if arc < 0.85:  return "gat"
    return "taan"


class PhraseEngine:
    """Live relational composition engine.

    Runs on its own thread. Produces NoteEvents into a queue.
    om.py fill_buffer() reads from the queue and renders notes.
    """

    def __init__(self, sa_hz: float = 130.81, bpm: float = 72):
        self.sa_hz    = sa_hz
        self.bpm      = bpm
        self.playing  = False

        # Current raga state
        self._raga_name   = "Yaman"
        self._raga_graph  = RAGA_GRAPHS.get("Yaman", {})
        self._current_swara = "Sa"
        self._perf_mode   = "gat"

        # Musician reading from natal_musician
        self._musician    = {}

        # Field state
        self._arc         = 0.5
        self._rasa        = "shanta"
        self._element     = "ether"
        self._density     = 0.7

        # Bhava state for emotional arc shaping
        self._bhava = _BhavaState() if _BhavaState else None

        # Swara engine — planetary gaze (initialized on first field load)
        self._swara_engine = None
        self._direction = "ascending"
        self._said_swaras: set = set()

        # Output queue — om.py reads from here
        self._queue: deque = deque(maxlen=32)
        self._thread  = None

    # ── Public API ────────────────────────────────────────────────

    def load_from_field(self, field_state: dict, natal: dict = None):
        """Update engine from field state + natal chart."""
        p5       = field_state.get("panchanga", {})
        raga_def = field_state.get("devi_raga_def") or {}
        raga_name = field_state.get("devi_raga", "Yaman")

        self._raga_name  = raga_name
        self._raga_graph = get_raga_graph(raga_name) or \
                           RAGA_GRAPHS.get("Yaman") or {}
        self._arc        = float(p5.get("tidx", 15)) / 30.0
        self._rasa       = p5.get("element", "ether")
        self._element    = p5.get("element", "ether")
        self._perf_mode  = arc_to_mode(self._arc)

        # Musician reading
        if natal:
            try:
                from .natal_musician import derive_musician_reading
                self._musician = derive_musician_reading(natal, field_state)
            except Exception:
                self._musician = {}

        # Rasa from raga definition
        rasa_raw = (field_state.get("devi_raga_def") or {}).get("rasa", "shanta")
        self._rasa = rasa_raw.split("·")[0].strip().lower() if rasa_raw else "shanta"

        # Density from arc, modulated by rasa/guna
        base_density = 0.3 + 0.7 * math.sin(self._arc * math.pi)
        guna = p5.get("guna", "sattva").lower()
        _GUNA_DENSITY = {"sattva": 0.7, "rajas": 1.0, "tamas": 0.4}
        self._density = base_density * _GUNA_DENSITY.get(guna, 0.7)

        # Initialize swara engine with graph if available
        if SwaraEngine is not None and self._swara_engine is None:
            try:
                from .graph_engine import GraphEngine
                graph = GraphEngine()
                self._swara_engine = SwaraEngine(graph, field_state)
            except Exception:
                self._swara_engine = None
        elif self._swara_engine is not None:
            self._swara_engine.field_state = field_state
            self._swara_engine._load_raga(field_state)

    def update_sa(self, sa_hz: float, bpm: float):
        self.sa_hz = sa_hz
        self.bpm   = bpm

    def next_note(self) -> Optional[NoteEvent]:
        """Pop next note from queue. Returns None if empty."""
        try:
            return self._queue.popleft()
        except IndexError:
            return None

    def start(self):
        if self.playing:
            return
        self.playing = True
        self._thread = threading.Thread(
            target=self._compose_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.playing = False

    # ── Composition loop ──────────────────────────────────────────

    def _compose_loop(self):
        """Main composition loop — chooses next swara and enqueues it."""
        while self.playing:
            try:
                event = self._choose_next()
                if event is not None:
                    self._queue.append(event)
                time.sleep(event.duration_sec if event else 0.5)
            except Exception:
                time.sleep(0.5)

    def _choose_next(self) -> Optional[NoteEvent]:
        """Choose next swara using raga graph + aroha/avaroha + field weights."""
        graph  = self._raga_graph
        if not graph:
            return None

        edges  = graph.get("edges", {})
        vadi   = graph.get("vadi", "Sa")
        nyasa  = graph.get("nyasa", ["Sa", "Pa"])
        if not isinstance(nyasa, list):
            nyasa = [nyasa]
        aroha   = graph.get("aroha", [])
        avaroha = graph.get("avaroha", [])
        mode   = PERF_MODES.get(self._perf_mode, PERF_MODES["gat"])
        musician = self._musician

        # ── 1. Should we rest? ────────────────────────────────────
        rest_density = musician.get("rest_density", 0.3) * mode["rest_mult"]
        if random.random() < rest_density * (1.0 - self._density):
            return self._make_silence()

        # ── 2. Get edges from current swara ───────────────────────
        current = self._current_swara
        next_edges = edges.get(current, {})

        if not next_edges:
            self._current_swara = vadi
            next_edges = edges.get(vadi, {"Sa": 1.0})

        # ── 3. Weight edges by field + natal + aroha/avaroha + gaze ──
        weights = dict(next_edges)

        phrase_arc = musician.get("phrase_arc", "wave")
        nodes = graph.get("nodes", [])
        current_idx = nodes.index(current) if current in nodes else 0

        # Determine ascending/descending tendency from arc position
        ascending_bias = 1.0 - self._arc if self._arc > 0.5 else self._arc + 0.5

        for swara, w in list(weights.items()):
            swara_clean = swara.rstrip("+")
            target_idx = nodes.index(swara_clean) \
                         if swara_clean in nodes else current_idx
            is_ascending = target_idx > current_idx

            # Aroha/avaroha compliance — boost notes that follow the sequence
            if aroha and is_ascending:
                if swara_clean in aroha:
                    weights[swara] *= 1.0 + 0.4 * ascending_bias
            if avaroha and not is_ascending:
                if swara_clean in avaroha:
                    weights[swara] *= 1.0 + 0.4 * (1.0 - ascending_bias)

            # Planetary gaze — gazed notes attract, ungrazed pass
            if self._swara_engine is not None:
                swara_entity = NODE_TO_SWARA.get(swara_clean, "")
                if swara_entity:
                    direction = "ascending" if is_ascending else "descending"
                    char = self._swara_engine.get_swara_character(
                        swara_entity, direction)
                    if char.get("gazed"):
                        weights[swara] *= 1.0 + char.get("force", 0) * 0.8
                    elif char.get("skip_probability", 0) > 0:
                        weights[swara] *= 1.0 - char["skip_probability"] * 0.3

            # Phrase arc influence
            if phrase_arc == "ascent" and is_ascending:
                weights[swara] *= 1.4
            elif phrase_arc == "descent" and not is_ascending:
                weights[swara] *= 1.4
            elif phrase_arc == "circle":
                if swara_clean in nyasa:
                    weights[swara] *= 1.3

            # Vadi gravity
            if swara_clean == vadi:
                weights[swara] *= 1.5

            # Gamak emphasis from natal
            gamak_list = musician.get("gamak_emphasis", [])
            if swara_clean in gamak_list:
                weights[swara] *= 1.2

            # Field tensions
            for tension in musician.get("field_tensions", []):
                if tension.get("swara") == swara_clean:
                    weights[swara] *= (1.0 + tension.get("pull", 0) * 0.3)

        # ── 4. Weighted random choice ─────────────────────────────
        total = sum(weights.values())
        if total <= 0:
            chosen = vadi
        else:
            r = random.random() * total
            cumul = 0.0
            chosen = vadi
            for swara, w in weights.items():
                cumul += w
                if r <= cumul:
                    chosen = swara
                    break

        chosen_clean = chosen.rstrip("+")
        is_ascending = (nodes.index(chosen_clean) if chosen_clean in nodes else 0) > current_idx
        self._direction = "ascending" if is_ascending else "descending"
        self._current_swara = chosen_clean
        self._said_swaras.add(chosen_clean)

        # ── 5. Compute note parameters via planetary gaze ─────────
        is_nyasa = chosen_clean in nyasa
        is_vadi  = chosen_clean == vadi

        # Query swara engine for gaze character
        gaze_char = None
        if self._swara_engine is not None:
            swara_entity = NODE_TO_SWARA.get(chosen_clean, "")
            if swara_entity:
                gaze_char = self._swara_engine.get_swara_character(
                    swara_entity, self._direction)

        beat_sec = 60.0 / max(self.bpm, 30)
        if self._perf_mode == "taan":
            dur = beat_sec * 0.25
        elif is_nyasa:
            dur = beat_sec * random.choice([2.0, 3.0, 4.0])
        elif is_vadi:
            dur = beat_sec * random.choice([1.5, 2.0])
        else:
            dur = beat_sec * random.choice([1.0, 1.5, 2.0])

        # Slow down in alap
        dur *= mode["speed"] ** -1 if mode["speed"] > 0 else 1.0

        # Planetary gaze shapes duration — gazed notes held, released notes pass
        if gaze_char:
            dur *= gaze_char.get("duration_factor", 1.0)

        # Bhava-shaped duration — karuna lingers, vira is crisp
        if self._bhava:
            bhava_state = self._bhava.update(self._rasa, self._arc)
            breathiness = bhava_state.get("breathiness", 0.3)
            dur *= 1.0 + breathiness * 0.5
            if self._rasa == "karuna" and chosen_clean in ("Ga_k", "Dha_k", "Ni_k", "Re_k"):
                dur *= 1.3

        # Amplitude — gazed notes louder
        amp = 0.6
        if is_vadi:   amp = 0.85
        if is_nyasa:  amp = 0.75
        if gaze_char and gaze_char.get("gazed"):
            amp *= 1.0 + gaze_char.get("force", 0) * 0.3
        amp *= self._density * 0.5 + 0.5

        # Gamak — planet-specific first, then raga graph, then fallback
        gamak = "none"
        andolana = graph.get("andolana", [])
        gamak_list = musician.get("gamak_emphasis", [])

        if gaze_char and gaze_char.get("gazed") and gaze_char.get("gamaka_type"):
            gamak = gaze_char["gamaka_type"]
        elif _graph_gamaka is not None:
            swara_key = _NODE_TO_GAMAKA_KEY.get(chosen_clean, "S")
            gi = _graph_gamaka(swara_key, self._raga_name, self._arc)
            if gi is not None:
                gamak = gi.type_name
        elif chosen_clean in andolana:
            gamak = "andolana"
        elif chosen_clean in gamak_list:
            gamak = "meend"
        elif is_nyasa and random.random() < 0.3:
            gamak = "kan"

        # ── 6. Frequency from just intonation ─────────────────────
        octave_mult = 2.0 if chosen.endswith("+") else 1.0
        ratio = JI_RATIOS.get(chosen_clean, 1.0)
        freq  = self.sa_hz * ratio * octave_mult

        return NoteEvent(
            swara        = chosen_clean,
            freq_hz      = round(freq, 2),
            duration_sec = round(dur, 3),
            amplitude    = round(amp, 3),
            gamak        = gamak,
            is_nyasa     = is_nyasa,
        )

    def _make_silence(self) -> NoteEvent:
        """Return a silence event."""
        beat_sec = 60.0 / max(self.bpm, 30)
        mode = PERF_MODES.get(self._perf_mode, PERF_MODES["gat"])
        dur = beat_sec * random.choice([1.0, 2.0]) * mode["rest_mult"]
        return NoteEvent(
            swara="silence", freq_hz=0.0, duration_sec=round(dur, 3),
            amplitude=0.0, gamak="silence", is_nyasa=False,
        )
