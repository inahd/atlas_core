"""
tabla_intelligence.py — Field-driven tabla cycle generation.

Uses bol grammar, tihai formulas, and layakari rules
to generate contextually appropriate tabla cycles
driven by the current field state (guna, rasa, coherence).

Grammar source: datasets/sound/tabla_grammar.csv
Tihai source: datasets/sound/tala_layakari.csv
Tala structures: from graph_seed_data.py (canonical)
"""

import csv
import io
import os
import random
from typing import Dict, List, Optional, Tuple

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))

_GRAMMAR_CSV = os.path.join(_ROOT, "datasets", "sound", "tabla_grammar.csv")
_LAYAKARI_CSV = os.path.join(_ROOT, "datasets", "sound", "tala_layakari.csv")

_grammar: Optional[Dict[str, dict]] = None
_layakari: Optional[List[dict]] = None


def _load_grammar():
    global _grammar
    if _grammar is not None:
        return _grammar
    _grammar = {}
    try:
        with open(_GRAMMAR_CSV, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                bol = row["bol"].lower()
                _grammar[bol] = {
                    "can_follow": [b.strip().lower() for b in row.get("can_follow", "").split(";") if b.strip()],
                    "cannot_follow": [b.strip().lower() for b in row.get("cannot_follow", "").split(";") if b.strip()],
                    "weight": float(row.get("weight", 0.5)),
                    "hand": row.get("hand", "both"),
                    "position_rule": row.get("position_rule", "any"),
                }
    except Exception:
        pass
    return _grammar


def _load_layakari_rules():
    global _layakari
    if _layakari is not None:
        return _layakari
    _layakari = []
    try:
        with open(_LAYAKARI_CSV, encoding="utf-8") as f:
            _layakari = list(csv.DictReader(f))
    except Exception:
        pass
    return _layakari


def _get_tala_structure(tala_name: str) -> Optional[dict]:
    """Get tala structure from graph_seed_data."""
    try:
        from .graph_seed_data import TALA_STRUCTURES
        # Try exact match then case-insensitive
        if tala_name in TALA_STRUCTURES:
            return TALA_STRUCTURES[tala_name]
        for k, v in TALA_STRUCTURES.items():
            if k.lower() == tala_name.lower():
                return v
    except ImportError:
        pass
    # Fallback: Rupak
    return {
        "beats": 7, "vibhag": [3, 2, 2],
        "vibhag_gravity": [0.3, 0.7, 0.6],
        "sam": 0, "khali": 0,
        "theka": ["tin", "tin", "na", "dhin", "na", "dhin", "na"],
    }


# ═══════════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════════

def get_valid_bols(tala_name: str, beat_position: int,
                   preceding_bol: str = "") -> List[str]:
    """Return valid bols for this tala position based on grammar.

    Respects:
    - can_follow rules from grammar
    - Sam position: prefer Dha or Tit (never Na/Ka/Ti alone)
    - Khali position: never Dha — use Tin
    - Rupak special: sam IS khali, so beat 0 = Tin
    """
    grammar = _load_grammar()
    tala = _get_tala_structure(tala_name)
    if not tala:
        return ["dha"]

    beats = tala["beats"]
    sam = tala.get("sam", 0)
    khali = tala.get("khali", 0)
    is_sam = (beat_position % beats) == sam
    is_khali = (beat_position % beats) == khali
    is_rupak_sam = tala_name.lower() == "rupak" and is_sam

    # Start with theka bol for this position
    theka = tala.get("theka", [])
    canonical = theka[beat_position % len(theka)] if theka else "dha"

    # Filter by grammar: what can follow the preceding bol
    preceding = preceding_bol.lower() if preceding_bol else ""
    if preceding and preceding in grammar:
        valid = grammar[preceding]["can_follow"]
        cannot = grammar[preceding]["cannot_follow"]
    else:
        valid = list(grammar.keys())
        cannot = []

    # Position constraints
    sam_bols = {"dha", "tit", "dhin"}
    khali_bols = {"tin", "na", "ti", "ta"}

    candidates = []
    for bol in valid:
        if bol in cannot:
            continue
        if is_rupak_sam and bol == "dha":
            continue  # Rupak sam is khali — never Dha
        if is_sam and not is_rupak_sam and bol not in sam_bols and bol != canonical.lower():
            continue  # Regular sam: prefer heavy bols
        if is_khali and bol == "dha" and not is_sam:
            continue  # Khali: avoid Dha
        candidates.append(bol)

    if not candidates:
        candidates = [canonical.lower()]

    # Weight by grammar weight
    weighted = []
    for bol in candidates:
        w = grammar.get(bol, {}).get("weight", 0.5)
        if bol == canonical.lower():
            w *= 1.5  # prefer canonical
        weighted.append((bol, w))

    return [b for b, _ in sorted(weighted, key=lambda x: -x[1])]


def should_play_tihai(beat_position: int, tala_name: str,
                      coherence: float) -> Optional[dict]:
    """Check if a tihai should start at this beat position.

    Returns tihai dict if conditions met, else None.
    Conditions:
    - coherence > 0.8
    - tihai phrase length fits: start + 3*phrase lands on sam
    """
    if coherence < 0.8:
        return None

    tala = _get_tala_structure(tala_name)
    if not tala:
        return None

    beats = tala["beats"]
    sam = tala.get("sam", 0)
    rules = _load_layakari_rules()

    for rule in rules:
        if rule.get("tala", "").lower() != tala_name.lower():
            continue
        try:
            phrase_len = int(rule.get("tihai_length_beats", 0))
            gap = int(rule.get("tihai_gap", 0))
            total = 3 * phrase_len + 2 * gap
        except ValueError:
            continue

        # Check if tihai from current beat lands on sam
        landing = (beat_position + total) % beats
        if landing == sam:
            phrase_bols = [b.strip() for b in rule.get("tihai_phrase", "").split()]
            return {
                "phrase": phrase_bols,
                "start_beat": beat_position,
                "phrase_beats": phrase_len,
                "gap_beats": gap,
                "total_beats": total,
            }

    return None


def get_layakari(guna: str, coherence: float) -> int:
    """Return layakari multiplier based on guna and coherence.

    Returns 1 (thah/normal), 2 (dugun/double), 3 (tigun/triple).
    """
    guna_lower = (guna or "").lower()

    if "tamas" in guna_lower:
        return 1  # Always normal in tamas

    if "rajas" in guna_lower:
        if coherence > 0.8:
            return 3 if random.random() < 0.2 else 2  # Occasionally tigun
        if coherence > 0.6:
            return 2 if random.random() < 0.4 else 1  # Sometimes dugun
        return 1

    if "sattva" in guna_lower:
        if coherence > 0.7:
            return 2 if random.random() < 0.3 else 1  # Balanced
        return 1

    return 1


def generate_cycle(field_state: dict, tala_name: str = "Rupak",
                   bpm: float = 84) -> List[dict]:
    """Generate one full tala cycle of bols driven by field state.

    Returns list of {"bol": name, "timing_ms": float, "velocity": float}
    """
    pa = field_state.get("panchanga", {})
    guna = pa.get("guna", "sattva")
    element = pa.get("element", "ether")
    coherence = field_state.get("svarodaya", {}).get("coherence_score", 0.5)
    if isinstance(coherence, str):
        try:
            coherence = float(coherence)
        except ValueError:
            coherence = 0.5

    tala = _get_tala_structure(tala_name)
    if not tala:
        return []

    beats = tala["beats"]
    beat_dur_ms = (60.0 / max(bpm, 30)) * 1000
    layakari = get_layakari(guna, coherence)
    effective_beats = beats * layakari

    # Gravity map for velocity
    vibhag = tala.get("vibhag", [beats])
    gravity = tala.get("vibhag_gravity", [1.0] * len(vibhag))

    # Rasa → velocity scaling
    rasa_vel = {"shringara": 0.7, "vira": 0.9, "karuna": 0.5,
                "raudra": 1.0, "shanta": 0.4, "hasya": 0.6,
                "adbhuta": 0.8, "bibhatsa": 0.3}
    field_rasa = pa.get("rasa", "shanta") if isinstance(pa.get("rasa"), str) else "shanta"
    base_vel = rasa_vel.get(field_rasa, 0.6)

    # Check for tihai opportunity
    tihai = should_play_tihai(beats - 5, tala_name, coherence) if coherence > 0.8 else None

    cycle = []
    prev_bol = ""
    tihai_active = False
    tihai_idx = 0

    for beat in range(effective_beats):
        real_beat = beat // layakari
        timing_ms = beat * (beat_dur_ms / layakari)

        # Gravity-based velocity
        vib_idx = 0
        acc = 0
        for vi, vlen in enumerate(vibhag):
            if real_beat < acc + vlen:
                vib_idx = vi
                break
            acc += vlen
        vel = base_vel * gravity[min(vib_idx, len(gravity) - 1)]
        vel = min(1.0, max(0.1, vel + random.uniform(-0.05, 0.05)))

        # Tihai insertion
        if tihai and not tihai_active and beat >= effective_beats - tihai["total_beats"] * layakari:
            tihai_active = True
            tihai_idx = 0

        if tihai_active and tihai:
            phrase = tihai["phrase"]
            rep_pos = tihai_idx % (len(phrase) + tihai["gap_beats"])
            if rep_pos < len(phrase):
                bol = phrase[rep_pos].lower()
            else:
                bol = ""  # gap
            tihai_idx += 1
        else:
            # Normal bol selection
            valid = get_valid_bols(tala_name, real_beat, prev_bol)
            bol = valid[0] if valid else "na"

        if bol:
            cycle.append({
                "bol": bol.capitalize(),
                "timing_ms": round(timing_ms, 1),
                "velocity": round(vel, 2),
                "beat": real_beat,
                "layakari": layakari,
                "tihai": tihai_active,
            })
            prev_bol = bol

    return cycle
