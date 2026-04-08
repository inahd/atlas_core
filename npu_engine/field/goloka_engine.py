"""
goloka_engine.py — What is eternally occurring in Goloka.

Given the current panchanga (time of day, tithi, nakshatra),
maps to the corresponding eternal activity — which ashtakala period,
which forest, which sakhi presides, which raga sounds.

Uses only data from existing datasets:
    datasets/cosmology/ashtakala.csv        — 8 periods of the day
    datasets/cosmology/vraja_forests.csv    — 12 Vraja forests
    datasets/cosmology/nitya_devi_master.csv — 15 Nitya Devis
    datasets/cosmology/daily_program.csv    — 8 daily rituals

Anything not directly derivable from these sources is left empty.
The goloka_topology.csv skeleton is ready for research data.

Pattern follows ui_vastu_engine.py:
    canonical data → internal helpers → validation → public API
"""

from typing import Any, Dict, List, Optional
import csv
import os
from datetime import datetime

# ══════════════════════════════════════════════════════════
# DATA LOADING
# ══════════════════════════════════════════════════════════

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))

_ASHTAKALA_CSV = os.path.join(_ROOT, "datasets", "cosmology", "ashtakala.csv")
_FORESTS_CSV = os.path.join(_ROOT, "datasets", "cosmology", "vraja_forests.csv")
_NITYA_CSV = os.path.join(_ROOT, "datasets", "cosmology", "nitya_devi_master.csv")
_PROGRAM_CSV = os.path.join(_ROOT, "datasets", "cosmology", "daily_program.csv")

# Research-grade goloka data (previously orphaned)
_GOLOKA_DIR = os.path.join(_ROOT, "datasets", "cosmology", "goloka")
_SAKHI_CSV = os.path.join(_GOLOKA_DIR, "sakhi_seva.csv")
_VRAJA_TOPO_CSV = os.path.join(_GOLOKA_DIR, "vraja_topology.csv")
_GOLOKA_REL_CSV = os.path.join(_GOLOKA_DIR, "goloka_relations.csv")
_ASHTAKALA_LILA_CSV = os.path.join(_GOLOKA_DIR, "ashtakala_lila.csv")

_cache: Dict[str, list] = {}


def _load(key: str, path: str) -> List[dict]:
    if key in _cache:
        return _cache[key]
    try:
        with open(path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        _cache[key] = rows
        return rows
    except Exception:
        _cache[key] = []
        return []


# ══════════════════════════════════════════════════════════
# INTERNAL HELPERS
# ══════════════════════════════════════════════════════════

def _parse_time(s: str) -> int:
    """Parse time string like '3:36am' to minutes from midnight."""
    s = s.strip().lower()
    try:
        if "am" in s or "pm" in s:
            pm = "pm" in s
            s = s.replace("am", "").replace("pm", "").strip()
            parts = s.split(":")
            h = int(parts[0])
            m = int(parts[1]) if len(parts) > 1 else 0
            if pm and h != 12:
                h += 12
            if not pm and h == 12:
                h = 0
            return h * 60 + m
        parts = s.split(":")
        return int(parts[0]) * 60 + int(parts[1])
    except Exception:
        return 0


def _current_ashtakala(now_hour: int, now_min: int) -> dict:
    """Find which ashtakala period the current time falls in."""
    periods = _load("ashtakala", _ASHTAKALA_CSV)
    if not periods:
        return {}

    cur_mins = now_hour * 60 + now_min
    for period in periods:
        start = _parse_time(period.get("time_start", "0:00"))
        end = _parse_time(period.get("time_end", "23:59"))
        # Handle wrap-around (e.g. 10:48pm to 3:36am)
        if start <= end:
            if start <= cur_mins < end:
                return period
        else:
            if cur_mins >= start or cur_mins < end:
                return period
    return periods[0] if periods else {}


def _forest_for_period(period_num: int) -> dict:
    """Find the Vraja forest corresponding to an ashtakala period."""
    forests = _load("forests", _FORESTS_CSV)
    for f in forests:
        ak = f.get("ashtakala_period", "")
        if str(period_num) in str(ak):
            return f
    return {}


def _nitya_devi_for_tithi(tithi_num: int) -> dict:
    """Find the Nitya Devi for a given tithi (1-15)."""
    devis = _load("nitya", _NITYA_CSV)
    for d in devis:
        if str(d.get("tithi_num")) == str(tithi_num):
            return d
    return {}


def _program_for_period(period_num: int) -> dict:
    """Find the daily program entry for this ashtakala period."""
    programs = _load("program", _PROGRAM_CSV)
    for p in programs:
        if str(p.get("ashtakala_period")) == str(period_num):
            return p
    return {}


def _sakhi_for_period(period_name: str) -> dict:
    """Find sakhi details from research-grade sakhi_seva.csv."""
    sakhis = _load("sakhi_seva", _SAKHI_CSV)
    if not sakhis:
        return {}
    period_lower = period_name.lower()
    for s in sakhis:
        active = s.get("active_ashtakala_period", "").lower()
        if period_lower and any(tok in active for tok in period_lower.split()):
            return s
    return sakhis[0] if sakhis else {}


def _lila_for_period(period_name: str) -> dict:
    """Find detailed lila description from ashtakala_lila.csv."""
    lilas = _load("ashtakala_lila", _ASHTAKALA_LILA_CSV)
    if not lilas:
        return {}
    for row in lilas:
        name = row.get("period_name", "")
        if period_name and period_name.lower().split()[0] in name.lower():
            return row
    return {}


def _vraja_forest_detail(forest_name: str) -> dict:
    """Find detailed forest from vraja_topology.csv."""
    forests = _load("vraja_topo", _VRAJA_TOPO_CSV)
    if not forests:
        return {}
    for f in forests:
        if forest_name and forest_name.lower() in f.get("forest_name", "").lower():
            return f
    return {}


def _raga_matches(live_raga: str, eternal_raga: str) -> bool:
    """Check if the live raga matches the eternal ashtakala raga."""
    if not live_raga or not eternal_raga:
        return False
    return live_raga.lower().replace(" ", "") in eternal_raga.lower().replace(" ", "") or \
           eternal_raga.lower().replace(" ", "") in live_raga.lower().replace(" ", "")


# ══════════════════════════════════════════════════════════
# VALIDATION
# ══════════════════════════════════════════════════════════

def _validate(state: dict) -> dict:
    """Ensure all required keys exist. Never returns partial data."""
    defaults = {
        "ashtakala_period": {
            "name": "", "time_approximate": "", "location": "",
            "primary_seva": "", "presiding_sakhi": "",
            "sakhi_seva": "", "sakhi_rasa": "", "sakhi_flower": "",
            "rasa": "", "raga": "", "mood": "",
        },
        "active_forest": {
            "name": "", "sanskrit": "", "lila": "", "season": "",
            "sacred_sites": "",
        },
        "active_sakhis": [],
        "nitya_devi": {
            "name": "", "bija": "", "color": "",
        },
        "bridge_to_material": {
            "nakshatra_resonance": "", "tithi_resonance": "",
            "raga_match": False, "coherence": 0.0,
        },
        "attestation": "SYNTHESIS",
    }
    for key, default in defaults.items():
        if key not in state or state[key] is None:
            state[key] = default
        elif isinstance(default, dict) and isinstance(state[key], dict):
            for dk, dv in default.items():
                if dk not in state[key]:
                    state[key][dk] = dv
    return state


# ══════════════════════════════════════════════════════════
# PUBLIC API
# ══════════════════════════════════════════════════════════

def derive_goloka_state(field_state: dict) -> dict:
    """Given current panchanga, return what is eternally occurring in Goloka.

    All data from existing datasets. Empty rather than invented.
    attestation: 'shastra' for data directly from ashtakala/forest CSVs,
                 'synthesis' for derived bridges.

    Args:
        field_state: dict from kernel.py field_state()

    Returns:
        Validated dict — all keys guaranteed present. Never raises.
    """
    try:
        p5 = field_state.get("panchanga", {})
        now = datetime.now()
        tidx = int(p5.get("tidx", 0))
        tithi_num = (tidx % 15) + 1
        nak = p5.get("nakshatra", "")
        live_raga = field_state.get("devi_raga", "")
        if not live_raga:
            live_raga = field_state.get("muhurta", {}).get("raga", "")

        # Ashtakala period
        period = _current_ashtakala(now.hour, now.minute)
        period_num = int(period.get("period", period.get("", 1))) if period else 1
        # Try parsing the first column value
        for key in period:
            try:
                period_num = int(period[key])
                break
            except (ValueError, TypeError):
                continue

        # Forest for this period
        forest = _forest_for_period(period_num)

        # Sakhi from research data (sakhi_seva.csv), fallback to basic
        period_name = period.get("name", "")
        sakhi_detail = _sakhi_for_period(period_name)
        sakhi = sakhi_detail.get("sakhi_name", "") or period.get("sakhi_lead", forest.get("presiding_sakhi", ""))
        active_sakhis = [sakhi] if sakhi else []

        # Detailed lila from ashtakala_lila.csv
        lila_detail = _lila_for_period(period_name)

        # Detailed forest from vraja_topology.csv
        forest_detail = _vraja_forest_detail(forest.get("name", ""))

        # Nitya Devi from tithi
        devi = _nitya_devi_for_tithi(tithi_num)

        # Daily program
        program = _program_for_period(period_num)

        # Bridge to material
        eternal_raga = period.get("raga", "")
        raga_match = _raga_matches(live_raga, eternal_raga)

        # Nakshatra resonance from forest correspondence
        forest_nak = forest.get("nakshatra_correspondence", "")
        nak_resonance = ""
        if forest_nak and nak:
            nak_lower = nak.lower().replace(" ", "_")
            if forest_nak.lower().replace(" ", "_") in nak_lower or nak_lower in forest_nak.lower():
                nak_resonance = f"{nak} matches {forest.get('name', '')} forest"

        # Tithi resonance
        tithi_resonance = ""
        if devi:
            tithi_resonance = f"Tithi {tithi_num} → {devi.get('name_iast', '')}"

        # Coherence: how aligned material time is with eternal time
        coherence = 0.0
        if raga_match:
            coherence += 0.4
        if nak_resonance:
            coherence += 0.3
        if devi:
            coherence += 0.2
        if program:
            coherence += 0.1
        coherence = min(1.0, coherence)

        # Determine attestation
        attestation = "shastra" if period and forest else "SYNTHESIS"

        # Mood from rasa + activity
        mood = period.get("activity", "").replace("_", " ").replace("/", " · ")

        # Lila rasa from research
        lila_rasa = lila_detail.get("mood_rasa", "") or forest.get("rasa_quality", "")
        lila_raga = lila_detail.get("traditional_raga", "") or eternal_raga
        lila_activity = lila_detail.get("primary_activity", "")
        lila_location = lila_detail.get("location", "") or forest.get("name", "")

        state = {
            "ashtakala_period": {
                "name": lila_detail.get("period_name", "") or period.get("name", ""),
                "time_approximate": lila_detail.get("time_range", "") or f"{period.get('time_start', '')} – {period.get('time_end', '')}",
                "location": lila_location,
                "primary_seva": lila_activity or (program.get("practice", "") if program else mood),
                "presiding_sakhi": sakhi,
                "sakhi_seva": sakhi_detail.get("seva", ""),
                "sakhi_rasa": sakhi_detail.get("rasa_relationship", ""),
                "sakhi_flower": sakhi_detail.get("color_flower_association", ""),
                "rasa": lila_rasa,
                "raga": lila_raga,
                "mood": mood,
            },
            "active_forest": {
                "name": forest_detail.get("forest_name", "") or forest.get("name", ""),
                "sanskrit": forest.get("sanskrit", ""),
                "lila": forest_detail.get("lila_summary", "") or forest.get("lila_type", "").replace("_", " "),
                "season": lila_detail.get("season", "") or forest.get("season", ""),
                "sacred_sites": forest_detail.get("sacred_sites", ""),
            },
            "active_sakhis": active_sakhis,
            "nitya_devi": {
                "name": devi.get("name_iast", ""),
                "bija": devi.get("bija", ""),
                "color": devi.get("color_hex", ""),
            },
            "bridge_to_material": {
                "nakshatra_resonance": nak_resonance,
                "tithi_resonance": tithi_resonance,
                "raga_match": raga_match,
                "coherence": round(coherence, 2),
            },
            "attestation": attestation,
        }
        return _validate(state)

    except Exception:
        return _validate({"attestation": "SYNTHESIS"})
