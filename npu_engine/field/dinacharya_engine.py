"""
dinacharya_engine.py

Domain: S6 — Lived Experience
Purpose: Synthesizes field state into practical daily guidance — what to do,
         eat, study, avoid in this moment. The experiential layer of Atlas.

Atlas Relations:
  ashtakala → activity → mantra → offering
  muhurta → recommended_practices → herbs
  nakshatra → dosha → dietary_guidance
  nadi (svarodaya) → favored_activities

Datasets:
  datasets/cosmology/ashtakala.csv             — 8 time periods
  datasets/cosmology/daily_program.csv          — 8 ashtakala → activity/mantra
  datasets/ayurveda/dinacharya_panchanga.csv    — 8 muhurta → practice
  datasets/ayurveda/dosha_nakshatra_matrix.csv  — 27 nakshatra → dosha practice
  datasets/svarodaya/activity_matrix.csv        — 210 nadi → activity

Public:
  derive_dinacharya(field_state) → dict
"""

import csv
import os
import unicodedata
from datetime import datetime
from typing import Dict, List, Optional

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))

_ASHTAKALA_CSV = os.path.join(_ROOT, "datasets", "cosmology", "ashtakala.csv")
_PROGRAM_CSV = os.path.join(_ROOT, "datasets", "cosmology", "daily_program.csv")
_DINACHARYA_CSV = os.path.join(_ROOT, "datasets", "ayurveda", "dinacharya_panchanga.csv")
_DOSHA_NAK_CSV = os.path.join(_ROOT, "datasets", "ayurveda", "dosha_nakshatra_matrix.csv")
_ACTIVITY_CSV = os.path.join(_ROOT, "datasets", "svarodaya", "activity_matrix.csv")

# ── Cache ────────────────────────────────────────────────

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


# ── Time helpers ─────────────────────────────────────────

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
        if start <= end:
            if start <= cur_mins < end:
                return period
        else:
            if cur_mins >= start or cur_mins < end:
                return period
    return periods[0] if periods else {}


# ── Muhurta-window matching ──────────────────────────────

_MUHURTA_HOUR_RANGES = [
    ("Brahma Muhurta (pre-dawn)", 3, 5),
    ("Sunrise Sandhya", 5, 7),
    ("Morning Kapha Window (approx 6-10)", 6, 10),
    ("Midday Pitta Window (approx 10-14)", 10, 14),
    ("Afternoon Vata Window (approx 14-18)", 14, 18),
    ("Sunset Sandhya", 18, 19),
    ("Evening Kapha Window (approx 18-22)", 19, 22),
    ("Late Night to Midnight", 22, 3),
]


def _current_muhurta_row(now_hour: int) -> dict:
    """Find the dinacharya_panchanga row matching current hour."""
    rows = _load("dinacharya", _DINACHARYA_CSV)
    if not rows:
        return {}
    for name, start, end in _MUHURTA_HOUR_RANGES:
        if start <= end:
            match = start <= now_hour < end
        else:
            match = now_hour >= start or now_hour < end
        if match:
            for row in rows:
                if row.get("muhurta_name", "").strip() == name:
                    return row
    return rows[0] if rows else {}


# ── Program lookup ───────────────────────────────────────

def _program_for_period(period_num: int) -> dict:
    programs = _load("program", _PROGRAM_CSV)
    for p in programs:
        if str(p.get("ashtakala_period", "")) == str(period_num):
            return p
    return {}


# ── Nakshatra → dosha ────────────────────────────────────

def _strip_diacritics(s: str) -> str:
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if unicodedata.category(c) not in ("Mn", "So")).strip()


def _dosha_for_nakshatra(nak_name: str) -> dict:
    """Find dosha_nakshatra_matrix row for the current nakshatra."""
    rows = _load("dosha_nak", _DOSHA_NAK_CSV)
    if not rows or not nak_name:
        return {}
    nak_clean = _strip_diacritics(nak_name).lower()
    for row in rows:
        csv_name = _strip_diacritics(row.get("nakshatra", "")).lower()
        if csv_name == nak_clean or nak_clean.startswith(csv_name) or csv_name.startswith(nak_clean):
            return row
    return {}


# ── Svarodaya avoid-list ─────────────────────────────────

# Transcendental activities — never contraindicated
# Acintya bhedabheda: bhakti operates by bhakti-shakti, not prana-shakti
# Source: BRS 1.2; CC Antya 20.18; SB 7.5.23-24
_TRANSCENDENTAL = frozenset({
    'meditation', 'remembrance_of_supreme', 'yoga_sadhana',
})


def _svarodaya_avoid(nadi: str) -> List[str]:
    """Activities to avoid for the current nadi from activity_matrix.

    Applies acintya bhedabheda filter — transcendental practices
    (meditation, remembrance_of_supreme) are never placed in
    the avoid list regardless of nadi/element state.
    """
    rows = _load("activity", _ACTIVITY_CSV)
    avoid = set()
    for row in rows:
        if row.get("nadi", "") == nadi and row.get("recommendation", "") == "avoid":
            act = row.get("activity", "")
            if act not in _TRANSCENDENTAL:
                avoid.add(act)
    return sorted(avoid)


# ── Public API ───────────────────────────────────────────

def derive_dinacharya(field_state: dict) -> dict:
    """
    Synthesize current field state into a daily practice brief.

    Pulls from panchanga (time, nakshatra, tithi), ashtakala mapping,
    muhurta-based ayurvedic practices, nakshatra dosha, and svarodaya.
    """
    now = datetime.now()
    p5 = field_state.get("panchanga", {})
    nak_name = p5.get("nakshatra", "")

    # 1. Ashtakala period
    period = _current_ashtakala(now.hour, now.minute)
    period_num = 1
    period_name = period.get("name", "")
    if period:
        try:
            period_num = int(period.get("period", 1))
        except (ValueError, KeyError):
            period_num = 1

    # 2. Daily program for this ashtakala
    program = _program_for_period(period_num)

    # 3. Muhurta-based ayurvedic guidance
    muhurta_row = _current_muhurta_row(now.hour)

    # 4. Nakshatra → dosha guidance
    dosha_row = _dosha_for_nakshatra(nak_name)

    # 5. Svarodaya avoid list
    svarodaya = field_state.get("svarodaya", {})
    optimal_nadi = svarodaya.get("optimal_nadi", "ida")
    avoid_from_svarodaya = _svarodaya_avoid(optimal_nadi)

    # Parse practices and herbs from muhurta row
    practices_raw = muhurta_row.get("recommended_practices", "")
    practices = [p.strip() for p in practices_raw.split(";") if p.strip()]

    herbs_raw = muhurta_row.get("recommended_herbs", "")
    herbs = [h.strip() for h in herbs_raw.split(",") if h.strip()]

    # Nakshatra herb
    nak_herb = dosha_row.get("herb_recommendation", "")
    if nak_herb and nak_herb not in herbs:
        herbs.append(nak_herb)

    return {
        "ashtakala_period": period_name,
        "ashtakala_num": period_num,
        "primary_activity": program.get("practice", ""),
        "mantra": program.get("mantra", "").replace("_", " "),
        "offering": program.get("offering", "").replace("_", " "),
        "recommended_practices": practices,
        "recommended_herbs": herbs,
        "dietary_guidance": muhurta_row.get("dietary_guidance", ""),
        "avoid": avoid_from_svarodaya,
        "dosha_active": muhurta_row.get("dosha_active", ""),
        "dosha_nakshatra": dosha_row.get("primary_dosha", ""),
        "nakshatra_practice": dosha_row.get("recommended_practice_for_this_dosha", ""),
        "nakshatra_dietary": dosha_row.get("dietary_guidance", ""),
        "raga": period.get("raga", ""),
        "forest": period.get("forest", ""),
        "songs": program.get("songs", "").replace(";", ", "),
        "source": "dinacharya_engine",
        "ontological_note": (
            "Material activities follow svarodaya timing. "
            "Transcendental practices (bhakti) are always auspicious. "
            "Acintya bhedābheda — Caitanya Mahāprabhu"
        ),
    }
