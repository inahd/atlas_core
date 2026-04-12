"""
raga_engine.py — Field-driven raga phrase generation with gamakas.

Gamakas are not ornaments — they ARE the notes (Pearson 2016).
SC implementation uses continuous pitch envelope (\raga_phrase SynthDef).

Loads:
  datasets/sound/raga_phrase_library.csv — 26 phrases across 13 ragas
  datasets/sound/gamak_properties.csv — 16 gamak types with coherence thresholds
  datasets/sound/field_music_mood.csv — 14 field state → music mood mappings
"""

import csv
import io
import os
import random
from typing import Dict, List, Optional

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))

_PHRASE_CSV = os.path.join(_ROOT, "datasets", "sound", "raga_phrase_library.csv")
_GAMAK_CSV = os.path.join(_ROOT, "datasets", "sound", "gamak_properties.csv")
_MOOD_CSV = os.path.join(_ROOT, "datasets", "sound", "field_music_mood.csv")

_phrases: Optional[List[dict]] = None
_gamaks: Optional[Dict[str, dict]] = None
_moods: Optional[List[dict]] = None

# Swara ratios (22-shruti Just Intonation)
SWARA_RATIOS = {
    'Sa': 1.0, 'Re': 9/8, 're': 16/15, 'Ga': 5/4, 'ga': 6/5,
    'Ma': 4/3, 'ma': 45/32, 'Pa': 3/2, 'Dha': 5/3, 'dha': 8/5,
    'Ni': 15/8, 'ni': 9/5, 'SA': 2.0,
}


def _load_csv(path):
    try:
        with open(path, encoding="utf-8") as f:
            return list(csv.DictReader(io.StringIO(f.read().lstrip())))
    except Exception:
        return []


def _get_phrases():
    global _phrases
    if _phrases is None:
        _phrases = _load_csv(_PHRASE_CSV)
    return _phrases


def _get_gamaks():
    global _gamaks
    if _gamaks is None:
        rows = _load_csv(_GAMAK_CSV)
        _gamaks = {r["gamak_id"]: r for r in rows if r.get("gamak_id")}
    return _gamaks


def _get_moods():
    global _moods
    if _moods is None:
        _moods = _load_csv(_MOOD_CSV)
    return _moods


def _swara_to_hz(swara: str, sa_hz: float) -> float:
    return sa_hz * SWARA_RATIOS.get(swara, 1.0)


def _get_field_mood(guna: str, element: str, time_period: str) -> dict:
    """Find best matching field mood."""
    moods = _get_moods()
    best = None
    best_score = -1
    for m in moods:
        score = 0
        if guna.lower() in m.get("guna", "").lower():
            score += 2
        if element.lower() in m.get("element", "").lower():
            score += 1
        if time_period.lower() in m.get("time_period", "").lower():
            score += 1
        if score > best_score:
            best_score = score
            best = m
    return best or {"phrase_density": "balanced", "gamak_intensity": "medium",
                     "note_duration_range": "0.5-1.2", "rest_probability": "0.3"}


def _parse_dur_range(s: str) -> tuple:
    try:
        parts = s.split("-")
        return float(parts[0]), float(parts[1])
    except (ValueError, IndexError):
        return 0.5, 1.2


def derive_raga_phrase(field_state: dict) -> dict:
    """Generate a raga phrase spec for the current field state.

    Returns dict with phrase info + OSC messages for SC.
    Gamak intensity driven by coherence:
      < 0.5:  no gamaks
      0.5-0.7: kampita on vadi only
      0.7-0.85: andolan on characteristic notes
      0.85+: full gamak per phrase_library spec
    """
    pa = field_state.get("panchanga", {})
    ss = field_state.get("sound_state", {})
    sv = field_state.get("svarodaya", {})

    raga_name = ss.get("raga", "Bihag")
    sa_hz = ss.get("sa_hz", 130.81)
    if isinstance(sa_hz, str):
        try:
            sa_hz = float(sa_hz)
        except ValueError:
            sa_hz = 130.81

    coherence = sv.get("coherence_score", 0.5)
    if isinstance(coherence, str):
        try:
            coherence = float(coherence)
        except ValueError:
            coherence = 0.5

    guna = pa.get("guna", "sattva") or "sattva"
    element = pa.get("element", "ether") or "ether"

    # Determine time period
    from datetime import datetime
    hour = datetime.now().hour
    if hour < 6:
        time_period = "dawn"
    elif hour < 10:
        time_period = "morning"
    elif hour < 14:
        time_period = "afternoon"
    elif hour < 18:
        time_period = "afternoon"
    elif hour < 21:
        time_period = "evening"
    else:
        time_period = "night"

    # Get mood
    mood = _get_field_mood(guna, element, time_period)

    # Find matching phrases for this raga
    phrases = _get_phrases()
    raga_phrases = [p for p in phrases if raga_name.lower() in p.get("raga", "").lower()]
    if not raga_phrases:
        # Fallback: use any pakad phrase
        raga_phrases = [p for p in phrases if p.get("phrase_type") == "pakad"]
    if not raga_phrases:
        raga_phrases = phrases[:3]

    # Select phrase
    phrase = random.choice(raga_phrases)
    swaras = [s.strip() for s in phrase.get("swaras", "Sa Ga Pa").split()]

    # Determine gamak parameters based on coherence
    gamak_type = "none"
    gamak_rate = 0
    gamak_depth = 0
    gamak_note_idx = 0

    if coherence >= 0.85:
        # Full gamak per phrase spec
        gt = phrase.get("gamak_type", "andolan")
        gamak_info = _get_gamaks().get(gt, {})
        gamak_type = gt
        gamak_rate = float(gamak_info.get("rate_hz", 3))
        gamak_depth = float(gamak_info.get("depth_cents", 30))
        # Find vadi position
        vadi_pos = phrase.get("vadi_position", "0")
        try:
            gamak_note_idx = int(vadi_pos)
        except ValueError:
            gamak_note_idx = 0
    elif coherence >= 0.7:
        gamak_type = "andolan"
        gamak_rate = 3
        gamak_depth = 25
        gamak_note_idx = 0  # first note
    elif coherence >= 0.5:
        gamak_type = "kampita"
        gamak_rate = 5
        gamak_depth = 15
        gamak_note_idx = 0

    # Convert swaras to frequencies
    freqs = [_swara_to_hz(s, sa_hz) for s in swaras]

    # Duration from mood
    dur_range = _parse_dur_range(mood.get("note_duration_range", "0.5-1.2"))

    # Build OSC messages for 3-note phrase segments
    osc_messages = []
    for i in range(0, len(freqs) - 2, 2):
        f1, f2, f3 = freqs[i], freqs[min(i + 1, len(freqs) - 1)], freqs[min(i + 2, len(freqs) - 1)]
        d1 = random.uniform(*dur_range)
        d2 = random.uniform(*dur_range)
        d3 = random.uniform(*dur_range)
        pan = random.uniform(-0.3, 0.3)

        osc_messages.append([
            "/atlas/phrase",
            [f1, f2, f3, d1, d2, d3,
             gamak_rate, gamak_depth,
             min(gamak_note_idx, 2),
             0.35, pan]
        ])

    return {
        "raga": raga_name,
        "phrase_type": phrase.get("phrase_type", ""),
        "swaras": swaras,
        "frequencies": [round(f, 2) for f in freqs],
        "gamak_type": gamak_type,
        "gamak_rate": gamak_rate,
        "gamak_depth": gamak_depth,
        "coherence": coherence,
        "guna": guna,
        "mood": mood.get("description", ""),
        "time_period": time_period,
        "osc_messages": osc_messages,
        "attestation": "OBSERVED",
    }
