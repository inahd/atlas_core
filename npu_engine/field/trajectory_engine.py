"""
trajectory_engine.py — Temporal arc of the field.

A skilled musician doesn't just play the moment — they play the arc
through the moment. Coming from Purnima, moving toward Ekadashi,
in Mercury dasha — the music breathes with time.

This is the single place where temporal trajectory is computed.
om.py and sound_engine.py consume the result; they never compute arcs.

Hierarchy:
    field_state (panchanga: tidx, nakshatra, paksha)
    + natal.json (dasha, lagna)
    + datasets (tithi_master, nakshatra_master, ashtakala, graha_master)
    → trajectory spec (this module)
    → om.py / sound_engine / shell field strip

Pattern follows ui_vastu_engine.py:
    canonical mappings → internal helpers → validation → public API
"""

from typing import Any, Dict, List, Optional
import csv
import json
import os
from datetime import datetime

# ══════════════════════════════════════════════════════════
# DATA LOADING
# ══════════════════════════════════════════════════════════

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
_TITHI_CSV = os.path.join(_ROOT, "datasets", "astro", "tithi_master.csv")
_NAK_CSV = os.path.join(_ROOT, "datasets", "cosmology", "nakshatra_master.csv")
_GRAHA_CSV = os.path.join(_ROOT, "datasets", "cosmology", "graha_master.csv")
_ASHTAKALA_CSV = os.path.join(_ROOT, "datasets", "cosmology", "ashtakala.csv")
_NATAL_PATH = os.path.join(_ROOT, "instance", "personal", "natal.json")


def _load_csv(path: str) -> List[dict]:
    try:
        with open(path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except Exception:
        return []


_tithi_cache = None
_nak_cache = None
_graha_cache = None


def _tithis():
    global _tithi_cache
    if _tithi_cache is None:
        _tithi_cache = _load_csv(_TITHI_CSV)
    return _tithi_cache


def _nakshatras():
    global _nak_cache
    if _nak_cache is None:
        _nak_cache = _load_csv(_NAK_CSV)
    return _nak_cache


def _grahas():
    global _graha_cache
    if _graha_cache is None:
        _graha_cache = _load_csv(_GRAHA_CSV)
    return _graha_cache


def _load_natal() -> dict:
    try:
        with open(_NATAL_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


# ══════════════════════════════════════════════════════════
# CANONICAL MAPPINGS
# ══════════════════════════════════════════════════════════

_NAK_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "Purva_Phalguni", "Uttara_Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva_Ashadha",
    "Uttara_Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva_Bhadrapada", "Uttara_Bhadrapada", "Revati",
]

# Dasha lord → musical character (from graha domains + tradition)
_DASHA_MUSICAL = {
    "sun":     {"quality": "sattva",  "musical": "majestic, sustained, slow development",
                "phrase": "articulate", "tempo_bias": 0.95},
    "moon":    {"quality": "sattva",  "musical": "lyrical, flowing, emotional",
                "phrase": "contemplative", "tempo_bias": 1.0},
    "mars":    {"quality": "rajas",   "musical": "energetic, rhythmic, driving",
                "phrase": "articulate", "tempo_bias": 1.1},
    "mercury": {"quality": "rajas",   "musical": "articulate, clear, quick phrases, witty",
                "phrase": "articulate", "tempo_bias": 1.05},
    "jupiter": {"quality": "sattva",  "musical": "expansive, teaching, long arcs",
                "phrase": "contemplative", "tempo_bias": 0.9},
    "venus":   {"quality": "rajas",   "musical": "beautiful, ornamented, romantic",
                "phrase": "articulate", "tempo_bias": 1.0},
    "saturn":  {"quality": "tamas",   "musical": "patient, deep, very slow development",
                "phrase": "searching", "tempo_bias": 0.85},
    "rahu":    {"quality": "tamas",   "musical": "unconventional, searching, restless",
                "phrase": "searching", "tempo_bias": 1.0},
    "ketu":    {"quality": "sattva",  "musical": "sparse, modal, renunciate",
                "phrase": "contemplative", "tempo_bias": 0.9},
}

# Tithi quality lookup (1-indexed, tithi_num within paksha)
_TITHI_QUALITY = {
    1: "auspicious", 2: "mixed", 3: "mixed", 4: "inauspicious",
    5: "auspicious", 6: "auspicious", 7: "mixed", 8: "mixed",
    9: "inauspicious", 10: "auspicious", 11: "auspicious", 12: "mixed",
    13: "mixed", 14: "inauspicious", 15: "auspicious",
}


# ══════════════════════════════════════════════════════════
# INTERNAL HELPERS
# ══════════════════════════════════════════════════════════

def _arc_position(tidx: int) -> float:
    """Lunar arc: 0.0=amavasya, 0.5=purnima, 1.0=amavasya."""
    return tidx / 30.0


def _energy_direction(arc: float) -> str:
    if arc < 0.1:
        return "ascending"   # just past amavasya, building
    elif arc < 0.45:
        return "ascending"
    elif arc < 0.55:
        return "peak"        # purnima zone
    elif arc < 0.9:
        return "descending"
    else:
        return "descending"  # approaching amavasya


def _tempo_multiplier(arc: float) -> float:
    """Lunar arc → tempo scaling."""
    if 0.4 <= arc <= 0.6:
        return 1.1    # purnima zone — slightly faster
    elif 0.6 < arc <= 0.9:
        return 0.95   # waning — gently slowing
    elif arc > 0.9 or arc < 0.05:
        return 0.85   # amavasya zone — quiet
    else:
        return 1.0    # waxing — building


def _days_to_tithi(tidx: int, target: int) -> int:
    """Days from current tidx to a target tithi (0-29). Approximate: 1 tithi ≈ 1 day."""
    return (target - tidx) % 30


def _compute_coming_from(tidx: int, nak_idx: int) -> dict:
    arc = _arc_position(tidx)
    # Days since last purnima (tidx 14) and amavasya (tidx 29)
    days_since_purnima = (tidx - 14) % 30
    days_since_amavasya = (tidx - 29) % 30

    # Recent nakshatra (3 days back ≈ 3 nakshatra positions)
    recent_nak_idx = (nak_idx - 3) % 27
    recent_nak = _NAK_NAMES[recent_nak_idx]

    # Most recent significant event
    if days_since_purnima <= 3:
        recent_event = "purnima"
    elif days_since_amavasya <= 3:
        recent_event = "amavasya"
    elif (tidx - 10) % 30 <= 3:  # shukla ekadashi
        recent_event = "ekadashi"
    elif (tidx - 25) % 30 <= 3:  # krishna ekadashi
        recent_event = "ekadashi"
    else:
        recent_event = ""

    return {
        "days_since_purnima": days_since_purnima,
        "days_since_amavasya": days_since_amavasya,
        "recent_nakshatra": recent_nak,
        "recent_event": recent_event,
        "energy_direction": _energy_direction(arc),
    }


def _compute_now(tidx: int, nak_name: str, paksha: str) -> dict:
    arc = _arc_position(tidx)
    tithi_num = (tidx % 15) + 1
    tithi_quality = _TITHI_QUALITY.get(tithi_num, "mixed")

    # Nakshatra quality from dataset
    nak_quality = "neutral"
    nak_lower = nak_name.lower().replace(" ", "_")
    for row in _nakshatras():
        csv_name = row.get("nakshatra", "").lower().replace(" ", "_")
        if csv_name == nak_lower or nak_lower in csv_name:
            guna = row.get("guna", "")
            gana = row.get("gana", "")
            if guna == "sattva":
                nak_quality = "auspicious"
            elif guna == "tamas" and gana == "rakshasa":
                nak_quality = "challenging"
            elif guna == "rajas":
                nak_quality = "active"
            else:
                nak_quality = "neutral"
            break

    return {
        "nakshatra": nak_name,
        "tithi": f"{'Shukla' if tidx < 15 else 'Krishna'} {tithi_num}",
        "paksha": paksha,
        "tithi_quality": tithi_quality,
        "nakshatra_quality": nak_quality,
        "arc_position": round(arc, 3),
    }


def _compute_moving_toward(tidx: int, nak_idx: int) -> dict:
    next_purnima = _days_to_tithi(tidx, 14)
    next_amavasya = _days_to_tithi(tidx, 29)
    # Ekadashi = tithi 10 (shukla) and 25 (krishna) in 0-indexed
    next_shukla_ek = _days_to_tithi(tidx, 10)
    next_krishna_ek = _days_to_tithi(tidx, 25)
    next_ekadashi = min(next_shukla_ek, next_krishna_ek)

    next_nak_idx = (nak_idx + 1) % 27
    next_nak = _NAK_NAMES[next_nak_idx]

    # Most significant approaching event
    events = [
        ("purnima", next_purnima),
        ("amavasya", next_amavasya),
        ("ekadashi", next_ekadashi),
    ]
    events.sort(key=lambda x: x[1])
    approaching_event = events[0][0]
    approaching_days = events[0][1]

    return {
        "next_purnima_days": next_purnima,
        "next_amavasya_days": next_amavasya,
        "next_ekadashi_days": next_ekadashi,
        "next_nakshatra": next_nak,
        "approaching_event": approaching_event,
        "approaching_days": approaching_days,
    }


def _compute_dasha(natal: dict) -> dict:
    if not natal:
        return {
            "current_dasha": "", "dasha_lord": "", "dasha_closes": "",
            "dasha_quality": "", "dasha_musical": "", "years_remaining": 0.0,
        }

    special = natal.get("special", {})
    dasha_name = special.get("dasha_current", "")
    dasha_lord = dasha_name.lower() if dasha_name else ""

    # Dasha close date — from CLAUDE.md: Mercury closes Oct 2027
    dasha_closes = ""
    years_remaining = 0.0
    if dasha_lord == "mercury":
        dasha_closes = "Oct 2027"
        try:
            now = datetime.now()
            close = datetime(2027, 10, 1)
            years_remaining = max(0.0, (close - now).days / 365.25)
        except Exception:
            years_remaining = 1.5

    # Musical character from dasha lord
    dm = _DASHA_MUSICAL.get(dasha_lord, {})

    return {
        "current_dasha": dasha_name,
        "dasha_lord": dasha_lord,
        "dasha_closes": dasha_closes,
        "dasha_quality": dm.get("quality", ""),
        "dasha_musical": dm.get("musical", ""),
        "years_remaining": round(years_remaining, 1),
    }


def _compute_musical(arc: float, tidx: int, dasha_lord: str,
                     now_hour: int) -> dict:
    # Base tempo from lunar arc
    tempo_mult = _tempo_multiplier(arc)

    # Dasha tempo bias
    dm = _DASHA_MUSICAL.get(dasha_lord, {})
    tempo_mult *= dm.get("tempo_bias", 1.0)
    tempo_mult = round(max(0.7, min(1.3, tempo_mult)), 2)

    # Tempo trend from energy direction
    direction = _energy_direction(arc)
    tempo_trend = {
        "ascending": "quickening",
        "peak": "stable",
        "descending": "slowing",
    }.get(direction, "stable")

    # Volume trend
    volume_trend = "stable"
    if direction == "descending" and arc > 0.75:
        volume_trend = "softening"
    elif direction == "ascending" and arc < 0.2:
        volume_trend = "building"

    # Ekadashi proximity
    next_shukla_ek = _days_to_tithi(tidx, 10)
    next_krishna_ek = _days_to_tithi(tidx, 25)
    days_to_ek = min(next_shukla_ek, next_krishna_ek)

    tabla_active = True
    if days_to_ek <= 2:
        volume_trend = "softening"
    if days_to_ek <= 1:
        tabla_active = False
    if days_to_ek == 0:
        tabla_active = False
        volume_trend = "silence"

    # Phrase character: dasha primary, modified by lunar arc
    phrase = dm.get("phrase", "articulate")
    if days_to_ek <= 1:
        phrase = "contemplative"
    elif direction == "descending" and arc > 0.8:
        phrase = "searching"

    # Raga family by time of day (ashtakala principle)
    if 4 <= now_hour < 7:
        raga_family = "morning"
    elif 7 <= now_hour < 10:
        raga_family = "morning"
    elif 10 <= now_hour < 16:
        raga_family = "any"
    elif 16 <= now_hour < 19:
        raga_family = "evening"
    elif 19 <= now_hour < 22:
        raga_family = "evening"
    else:
        raga_family = "night"

    # Energy arc summary
    parts = []
    parts.append(direction)
    if days_to_ek <= 3:
        parts.append(f"toward Ekadashi ({days_to_ek}d)")
    elif _days_to_tithi(tidx, 14) <= 3:
        parts.append(f"toward Purnima ({_days_to_tithi(tidx, 14)}d)")
    if dasha_lord:
        parts.append(f"{dasha_lord} dasha")
    energy_arc = " · ".join(parts)

    return {
        "tempo_multiplier": tempo_mult,
        "tempo_trend": tempo_trend,
        "volume_trend": volume_trend,
        "tabla_active": tabla_active,
        "phrase_character": phrase,
        "raga_family": raga_family,
        "energy_arc": energy_arc,
    }


def _compute_session_arc(now_hour: int, arc: float) -> dict:
    # Duration and pacing by time of day + lunar energy
    if 4 <= now_hour < 10:
        base_dur = 30
        suggested_arc = "vilambit → madhya"
        opening = "still, meditative"
        closing = "gently awake"
    elif 10 <= now_hour < 16:
        base_dur = 20
        suggested_arc = "madhya"
        opening = "present, clear"
        closing = "centered"
    elif 16 <= now_hour < 21:
        base_dur = 30
        suggested_arc = "madhya → vilambit"
        opening = "alert, evening energy"
        closing = "settling, devotional"
    else:
        base_dur = 15
        suggested_arc = "vilambit"
        opening = "quiet, interior"
        closing = "dissolving"

    # Lunar energy modulates duration
    if arc > 0.9 or arc < 0.05:
        base_dur = max(10, base_dur - 10)  # amavasya — shorter
    elif 0.4 <= arc <= 0.6:
        base_dur += 10  # purnima — can sustain longer

    return {
        "suggested_duration_min": base_dur,
        "suggested_arc": suggested_arc,
        "opening_mood": opening,
        "closing_mood": closing,
    }


# ══════════════════════════════════════════════════════════
# VALIDATION
# ══════════════════════════════════════════════════════════

def _validate(traj: dict) -> dict:
    """Ensure all required keys exist. Never returns partial data."""
    defaults = {
        "coming_from": {
            "days_since_purnima": 0, "days_since_amavasya": 0,
            "recent_nakshatra": "", "recent_event": "",
            "energy_direction": "stable",
        },
        "now": {
            "nakshatra": "", "tithi": "", "paksha": "",
            "tithi_quality": "mixed", "nakshatra_quality": "neutral",
            "arc_position": 0.5,
        },
        "moving_toward": {
            "next_purnima_days": 15, "next_amavasya_days": 15,
            "next_ekadashi_days": 11, "next_nakshatra": "",
            "approaching_event": "", "approaching_days": 0,
        },
        "dasha_context": {
            "current_dasha": "", "dasha_lord": "", "dasha_closes": "",
            "dasha_quality": "", "dasha_musical": "", "years_remaining": 0.0,
        },
        "musical_implication": {
            "tempo_multiplier": 1.0, "tempo_trend": "stable",
            "volume_trend": "stable", "tabla_active": True,
            "phrase_character": "articulate", "raga_family": "any",
            "energy_arc": "",
        },
        "session_arc": {
            "suggested_duration_min": 20, "suggested_arc": "madhya",
            "opening_mood": "", "closing_mood": "",
        },
        "attestation": "SYNTHESIS",
    }
    for key, default in defaults.items():
        if key not in traj or traj[key] is None:
            traj[key] = default
        elif isinstance(default, dict) and isinstance(traj[key], dict):
            for dk, dv in default.items():
                if dk not in traj[key]:
                    traj[key][dk] = dv
    return traj


# ══════════════════════════════════════════════════════════
# PUBLIC API
# ══════════════════════════════════════════════════════════

def derive_trajectory(field_state: dict, natal: dict = None,
                      days_back: int = 3, days_forward: int = 14) -> dict:
    """Compute the temporal arc of the field.

    Returns validated TrajectorySpec — all keys guaranteed. Never raises.

    Args:
        field_state: dict from kernel.py field_state() — must contain panchanga.
        natal: dict from instance/personal/natal.json. Optional.
        days_back: how far back to look for context (default 3).
        days_forward: how far forward to project (default 14).

    Returns:
        Validated dict with coming_from, now, moving_toward, dasha_context,
        musical_implication, session_arc, attestation.
    """
    try:
        p5 = field_state.get("panchanga", {})
        tidx = int(p5.get("tidx", 15))
        paksha = p5.get("paksha", "Shukla")
        nak_name = p5.get("nakshatra", "Rohini")

        # Resolve nakshatra index
        nak_idx = 0
        nak_lower = nak_name.lower().replace(" ", "_").replace("ā", "a").replace("ī", "i")
        for i, n in enumerate(_NAK_NAMES):
            if n.lower() in nak_lower or nak_lower in n.lower():
                nak_idx = i
                break

        # Load natal if not provided
        if natal is None:
            natal = _load_natal()

        now = datetime.now()
        now_hour = now.hour
        arc = _arc_position(tidx)

        # Dasha lord
        dasha_lord = ""
        if natal:
            dasha_lord = natal.get("special", {}).get("dasha_current", "").lower()

        coming_from = _compute_coming_from(tidx, nak_idx)
        now_ctx = _compute_now(tidx, nak_name, paksha)
        moving_toward = _compute_moving_toward(tidx, nak_idx)
        dasha_context = _compute_dasha(natal)
        musical = _compute_musical(arc, tidx, dasha_lord, now_hour)
        session = _compute_session_arc(now_hour, arc)

        traj = {
            "coming_from": coming_from,
            "now": now_ctx,
            "moving_toward": moving_toward,
            "dasha_context": dasha_context,
            "musical_implication": musical,
            "session_arc": session,
            "attestation": "SYNTHESIS",
        }
        return _validate(traj)

    except Exception:
        return _validate({"attestation": "SYNTHESIS"})
