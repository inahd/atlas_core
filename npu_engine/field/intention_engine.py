"""
intention_engine.py — Intention-based calendar scoring from field state + jyotish rules.

This is the single place where intention→time favorability is computed.
Calendar UIs consume the result; they never recompute it.

Hierarchy:
    kernel / field_state / calc_panchanga
        → field_state dict (panchanga, muhurta, hora, rahu_kala, yoga, karana)
        → intention_rules.csv (favorable/avoid conditions per intention)
        → scored windows (this module)
        → apps/calendar/ / clients

Three public functions:
    A. classify_intention(text)  — keyword match → intention_id
    B. derive_windows(id, fs, days) — score muhurta windows across N days
    C. score_moment(id, fs)     — score the current moment for an intention
"""

from typing import Any, Dict, List, Optional
import csv
import os
import re
from datetime import datetime, timedelta

# ══════════════════════════════════════════════════════════
# DATA LOADING
# ══════════════════════════════════════════════════════════

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
_RULES_PATH = os.path.join(_ROOT, "datasets", "views", "intention_rules.csv")

_rules_cache: Optional[List[dict]] = None


def _load_rules() -> List[dict]:
    global _rules_cache
    if _rules_cache is not None:
        return _rules_cache
    rows = []
    with open(_RULES_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    _rules_cache = rows
    return rows


def _split(val: str) -> List[str]:
    """Split semicolon-delimited field, strip whitespace, drop empties."""
    if not val:
        return []
    return [s.strip() for s in val.split(";") if s.strip()]


# ══════════════════════════════════════════════════════════
# KEYWORD INDEX — built from intention labels + categories
# ══════════════════════════════════════════════════════════

_KEYWORD_MAP: Optional[Dict[str, List[dict]]] = None


_SYNONYMS = {
    "wedding": "marriage", "wed": "marriage", "marry": "marriage",
    "trip": "travel", "voyage": "travel", "move": "travel",
    "garden": "plant", "grow": "plant", "sow": "plant",
    "pray": "ritual", "worship": "ritual", "puja": "ritual",
    "read": "study", "learn": "study", "scripture": "study",
    "write": "compose", "create": "creative", "art": "creative",
    "song": "music", "sing": "music", "raga": "music",
    "buy": "financial", "sell": "financial", "invest": "financial",
    "rest": "recovery", "sleep": "recovery", "relax": "recovery",
    "medicine": "herb", "cure": "healing", "remedy": "healing",
    "build": "construct", "house": "construct",
    "fast": "fasting", "vrata": "fasting", "ekadashi": "fasting",
    "ancestors": "ancestor", "shraddha": "ancestor", "pitri": "ancestor",
    "celebrate": "celebration", "festival": "celebration", "party": "celebration",
    "meditate": "meditation", "contemplate": "meditation",
    "compost": "composting", "prune": "clearing", "clear": "clearing",
    "water": "irrigation", "irrigate": "irrigation",
    "dispute": "legal", "court": "legal", "lawsuit": "legal",
    "obstacle": "obstacle", "block": "obstacle", "stuck": "obstacle",
}


def _build_keyword_map() -> Dict[str, List[dict]]:
    global _KEYWORD_MAP
    if _KEYWORD_MAP is not None:
        return _KEYWORD_MAP
    rules = _load_rules()
    kmap: Dict[str, List[dict]] = {}
    for rule in rules:
        # Extract keywords from intention_id, label, category, and notes
        tokens = set()
        for field in ("intention_id", "intention_label", "category", "notes"):
            val = rule.get(field, "")
            for word in re.split(r"[^a-zA-Z]+", val.lower()):
                if len(word) >= 3:
                    tokens.add(word)
        for token in tokens:
            kmap.setdefault(token, []).append(rule)
    _KEYWORD_MAP = kmap
    return kmap


# ══════════════════════════════════════════════════════════
# VARA / NAKSHATRA NORMALIZATION
# ══════════════════════════════════════════════════════════

# Map display names (with symbols) to canonical vara names
_VARA_DISPLAY_TO_ID = {
    "Ravivara": "Ravivara", "Somavara": "Somavara",
    "Mangalavara": "Mangalavara", "Budhavara": "Budhavara",
    "Guruvara": "Guruvara", "Shukravara": "Shukravara",
    "Shanivara": "Shanivara",
}

_WEEKDAY_TO_VARA = {
    0: "Somavara",    # Monday
    1: "Mangalavara",
    2: "Budhavara",
    3: "Guruvara",
    4: "Shukravara",
    5: "Shanivara",
    6: "Ravivara",
}

# kernel.py uses (weekday+1)%7 to index into VARAS which starts with Ravivara
# So we need to extract the plain vara name from display strings like "Ravivara ☀"
def _normalize_vara(vara_str: str) -> str:
    """Extract canonical vara name from display string."""
    if not vara_str:
        return ""
    # Strip emoji/symbols
    clean = vara_str.split()[0] if vara_str else ""
    # Strip diacritics pattern
    clean = clean.replace("ā", "a").replace("ṅ", "n").replace("ī", "i")
    for canonical in _VARA_DISPLAY_TO_ID:
        if clean.lower().startswith(canonical.lower()[:4]):
            return canonical
    return clean


def _normalize_nakshatra(nak_str: str) -> str:
    """Normalize nakshatra name for matching."""
    if not nak_str:
        return ""
    return nak_str.replace(" ", "_").replace("ā", "a").replace("ī", "i").replace("ṛ", "ri").replace("ṣ", "sh")


# ══════════════════════════════════════════════════════════
# TITHI TYPE CLASSIFICATION
# ══════════════════════════════════════════════════════════

# From tithi_master.csv quality column
_TITHI_NUM_TO_QUALITY = {
    1: "auspicious", 2: "mixed", 3: "mixed", 4: "inauspicious",
    5: "auspicious", 6: "auspicious", 7: "mixed", 8: "mixed",
    9: "inauspicious", 10: "auspicious", 11: "auspicious", 12: "mixed",
    13: "mixed", 14: "inauspicious", 15: "auspicious",
}

# Rikta tithis — Chaturthi, Navami, Chaturdashi (4, 9, 14)
_RIKTA_TITHIS = {4, 9, 14}


def _tithi_quality(tidx: int) -> str:
    """Return tithi quality from 0-based index."""
    num = (tidx % 15) + 1
    return _TITHI_NUM_TO_QUALITY.get(num, "mixed")


def _is_rikta(tidx: int) -> bool:
    num = (tidx % 15) + 1
    return num in _RIKTA_TITHIS


# ══════════════════════════════════════════════════════════
# MUHURTA WINDOWS — 30 muhurtas per day (48 min each)
# ══════════════════════════════════════════════════════════

_MUHURTA_NAMES = [
    "Rudra", "Ahi", "Mitra", "Pitri", "Vasu",
    "Vara", "Vishvedeva", "Vidhi", "Satamukhi", "Puruhuta",
    "Vahini", "Naktanakara", "Varuna", "Aryaman", "Bhaga",
    "Girisha", "Ajapada", "Ahir Budhnya", "Pushan", "Ashvini",
    "Yama", "Agni", "Vidhata", "Chanda", "Aditi",
    "Jiva", "Vishnu", "Yumigadyuti", "Brahma", "Samudram",
]

# Quality classification of muhurtas
_MUHURTA_QUALITY = {
    "Abhijit": "excellent",      # midday — always auspicious
    "Brahma": "excellent",       # pre-dawn
    "Vijaya": "excellent",       # victory muhurta
}

# Special named windows overlaid on the 30-muhurta grid
_SPECIAL_WINDOWS = [
    {"name": "Brahma Muhurta", "start_min": 264, "end_min": 360, "quality": "excellent"},
    {"name": "Abhijit",        "start_min": 726, "end_min": 774, "quality": "excellent"},
]


def _muhurta_windows_for_day(base_date: datetime) -> List[dict]:
    """Generate 30 muhurta windows for a given day, starting at sunrise (6:00 AM)."""
    sunrise_min = 360  # 6:00 AM
    windows = []

    # Pre-sunrise: Brahma Muhurta (4:24 - 5:12 AM)
    bm_start = base_date.replace(hour=4, minute=24, second=0, microsecond=0)
    windows.append({
        "datetime": bm_start.isoformat(),
        "start_min": 264,
        "end_min": 312,
        "muhurta_name": "Brahma Muhurta",
        "muhurta_quality": "excellent",
        "index": -1,
    })

    # 30 muhurtas from sunrise, each 48 minutes
    for i in range(30):
        m_start = sunrise_min + i * 48
        m_end = m_start + 48
        h = m_start // 60
        m = m_start % 60
        if h >= 24:
            h -= 24
        dt = base_date.replace(hour=h, minute=m, second=0, microsecond=0)
        if h < base_date.hour and i > 15:
            dt += timedelta(days=1)

        name = _MUHURTA_NAMES[i] if i < len(_MUHURTA_NAMES) else f"Muhurta_{i+1}"

        # Check for Abhijit overlay (midday, ~12:06-12:54)
        if 726 <= m_start < 774:
            name = "Abhijit"
            quality = "excellent"
        else:
            quality = _MUHURTA_QUALITY.get(name, "neutral")

        windows.append({
            "datetime": dt.isoformat(),
            "start_min": m_start,
            "end_min": m_end,
            "muhurta_name": name,
            "muhurta_quality": quality,
            "index": i,
        })

    return windows


# ══════════════════════════════════════════════════════════
# SCORING ENGINE
# ══════════════════════════════════════════════════════════

def _score_window(rule: dict, vara: str, nakshatra: str, tidx: int,
                  hora_lord: str, paksha: str, rahu_active: bool,
                  yoga_quality: str, muhurta_quality: str) -> tuple:
    """Score a single window against an intention rule.

    Returns (score: float, favorable: list, caution: list).
    Score range: 0.0 (very unfavorable) to 1.0 (highly auspicious).
    """
    score = 0.5  # baseline
    favorable = []
    caution = []

    # — Vara match (+0.15 / -0.15)
    fav_vara = _split(rule.get("favorable_vara", ""))
    avoid_vara = _split(rule.get("avoid_vara", ""))
    if vara in fav_vara:
        score += 0.15
        favorable.append(f"vara:{vara}")
    elif vara in avoid_vara:
        score -= 0.15
        caution.append(f"avoid_vara:{vara}")

    # — Nakshatra match (+0.20 / -0.20)
    fav_nak = _split(rule.get("favorable_nakshatra", ""))
    avoid_nak = _split(rule.get("avoid_nakshatra", ""))
    nak_norm = _normalize_nakshatra(nakshatra)
    if nak_norm in fav_nak or nakshatra in fav_nak:
        score += 0.20
        favorable.append(f"nakshatra:{nakshatra}")
    elif nak_norm in avoid_nak or nakshatra in avoid_nak:
        score -= 0.20
        caution.append(f"avoid_nakshatra:{nakshatra}")

    # — Tithi quality match (+0.10 / -0.15)
    fav_tithi_type = rule.get("favorable_tithi_type", "")
    avoid_tithi_type = rule.get("avoid_tithi_type", "")
    tq = _tithi_quality(tidx)
    if fav_tithi_type and tq == fav_tithi_type:
        score += 0.10
        favorable.append(f"tithi:{tq}")
    elif avoid_tithi_type and tq == avoid_tithi_type:
        score -= 0.15
        caution.append(f"avoid_tithi:{tq}")

    # — Rikta tithi penalty (-0.10)
    if _is_rikta(tidx):
        score -= 0.10
        caution.append("rikta_tithi")

    # — Hora lord match (+0.10 / -0.10)
    fav_hora = _split(rule.get("favorable_hora_lord", ""))
    avoid_hora = _split(rule.get("avoid_hora", ""))
    if hora_lord in fav_hora:
        score += 0.10
        favorable.append(f"hora:{hora_lord}")
    elif hora_lord in avoid_hora:
        score -= 0.10
        caution.append(f"avoid_hora:{hora_lord}")

    # — Paksha preference (+0.05 / -0.05)
    pref_paksha = rule.get("paksha", "")
    if pref_paksha:
        paksha_norm = "shukla" if "ukla" in paksha.lower() else "krishna"
        if paksha_norm == pref_paksha:
            score += 0.05
            favorable.append(f"paksha:{paksha_norm}")
        else:
            score -= 0.05
            caution.append(f"paksha_mismatch:{paksha_norm}")

    # — Rahu Kala hard penalty (-0.20)
    if rahu_active:
        score -= 0.20
        caution.append("rahu_kala")

    # — Inauspicious yoga penalty (-0.10)
    if yoga_quality == "inauspicious":
        score -= 0.10
        caution.append("inauspicious_yoga")
    elif yoga_quality == "auspicious":
        score += 0.05
        favorable.append("auspicious_yoga")

    # — Muhurta quality bonus
    if muhurta_quality == "excellent":
        score += 0.10
        favorable.append(f"muhurta:excellent")

    # Clamp
    score = max(0.0, min(1.0, round(score, 3)))

    return score, favorable, caution


# ══════════════════════════════════════════════════════════
# VALIDATION
# ══════════════════════════════════════════════════════════

def _validate_result(result: dict) -> dict:
    """Ensure all required keys exist. Never returns partial data."""
    defaults = {
        "intention_id": "",
        "intention_label": "",
        "windows": [],
        "best_window": None,
        "today_summary": "",
        "attestation": "SYNTHESIS",
    }
    for key, default in defaults.items():
        if key not in result or result[key] is None:
            result[key] = default

    # Validate each window
    window_defaults = {
        "datetime": "",
        "muhurta_name": "",
        "score": 0.0,
        "favorable_factors": [],
        "caution_factors": [],
        "nakshatra": "",
        "tithi": "",
        "vara": "",
        "hora_lord": "",
    }
    for w in result.get("windows", []):
        for wk, wv in window_defaults.items():
            if wk not in w:
                w[wk] = wv
        w["score"] = max(0.0, min(1.0, float(w.get("score", 0.0))))

    return result


# ══════════════════════════════════════════════════════════
# PUBLIC API
# ══════════════════════════════════════════════════════════

def classify_intention(text: str) -> dict:
    """Classify free text into an intention from intention_rules.csv.

    Keyword match against intention labels, categories, and notes.
    Returns the best-matching intention with confidence score.

    Args:
        text: Free text describing what the user wants to do.

    Returns:
        {intention_id, label, category, confidence}
        confidence: 0.0–1.0 based on keyword overlap.
        If no match, returns intention_id="" with confidence=0.
    """
    kmap = _build_keyword_map()
    rules = _load_rules()

    raw_words = set(re.split(r"[^a-zA-Z]+", text.lower()))
    raw_words = {w for w in raw_words if len(w) >= 3}
    # Expand synonyms
    words = set(raw_words)
    for w in raw_words:
        syn = _SYNONYMS.get(w)
        if syn:
            words.add(syn)

    if not words:
        return {"intention_id": "", "label": "", "category": "", "confidence": 0.0}

    # Score each rule by keyword hits
    scores: Dict[str, float] = {}
    for word in words:
        matches = kmap.get(word, [])
        for rule in matches:
            rid = rule["intention_id"]
            scores[rid] = scores.get(rid, 0) + 1.0

    if not scores:
        return {"intention_id": "", "label": "", "category": "", "confidence": 0.0}

    best_id = max(scores, key=scores.get)
    best_score = scores[best_id]
    confidence = min(1.0, round(best_score / max(len(words), 1), 2))

    for rule in rules:
        if rule["intention_id"] == best_id:
            return {
                "intention_id": best_id,
                "label": rule.get("intention_label", ""),
                "category": rule.get("category", ""),
                "confidence": confidence,
            }

    return {"intention_id": "", "label": "", "category": "", "confidence": 0.0}


def derive_windows(intention_id: str, field_state: dict, days: int = 7) -> dict:
    """Score muhurta windows across N days for a given intention.

    Reads panchanga progression from field_state and projects forward.
    Each window is scored against the intention's jyotish rules.

    Args:
        intention_id: ID from intention_rules.csv.
        field_state: dict from kernel.py field_state() — must contain
                     panchanga, hora, rahu_kala, yoga, karana keys.
        days: Number of days to project (default 7).

    Returns:
        Validated dict with windows, best_window, today_summary, attestation.
        All keys guaranteed present. Safe to render without checks.
    """
    rules = _load_rules()
    rule = None
    for r in rules:
        if r["intention_id"] == intention_id:
            rule = r
            break

    if not rule:
        return _validate_result({
            "intention_id": intention_id,
            "intention_label": "",
            "today_summary": "Unknown intention.",
        })

    p5 = field_state.get("panchanga", {})
    now = p5.get("now", datetime.now())
    if isinstance(now, str):
        try:
            now = datetime.fromisoformat(now)
        except (ValueError, TypeError):
            now = datetime.now()

    base_tidx = p5.get("tidx", 0)
    base_nak_idx = 0

    # Resolve current nakshatra index from name
    nak_name = p5.get("nakshatra", "")
    _NAK_NAMES = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
        "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
        "Purva_Phalguni", "Uttara_Phalguni", "Hasta", "Chitra", "Swati",
        "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva_Ashadha",
        "Uttara_Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
        "Purva_Bhadrapada", "Uttara_Bhadrapada", "Revati",
    ]
    for i, n in enumerate(_NAK_NAMES):
        if n.lower() in nak_name.lower().replace(" ", "_") or nak_name.lower().replace(" ", "_") in n.lower():
            base_nak_idx = i
            break

    all_windows = []

    for day_offset in range(days):
        day_dt = (now + timedelta(days=day_offset)).replace(
            hour=0, minute=0, second=0, microsecond=0)
        weekday = day_dt.weekday()

        # Project panchanga forward (approximate)
        # Tithi advances ~1 per day, nakshatra ~1 per day
        proj_tidx = (base_tidx + day_offset) % 30
        proj_nak_idx = (base_nak_idx + day_offset) % 27
        proj_nak = _NAK_NAMES[proj_nak_idx]
        proj_vara = _WEEKDAY_TO_VARA[weekday]
        proj_paksha = "shukla" if proj_tidx < 15 else "krishna"

        # Yoga quality (approximate from current)
        yoga_quality = field_state.get("yoga", {}).get("yoga_quality", "mixed")

        # Rahu Kala slot for this weekday
        _RAHU_SLOTS = {6: 8, 0: 2, 1: 7, 2: 5, 3: 6, 4: 4, 5: 3}
        rahu_slot = _RAHU_SLOTS.get(weekday, 8)
        rahu_start_min = 360 + int(rahu_slot * 90)
        rahu_end_min = rahu_start_min + 90

        muhurtas = _muhurta_windows_for_day(day_dt)

        for mw in muhurtas:
            m_start = mw["start_min"]
            m_mid = m_start + 24  # midpoint

            # Hora at this window's midpoint
            hora_hour = m_mid // 60
            _HORA_SEQ = {
                6: [0, 5, 4, 1, 6, 3, 2],  # Sunday: Sun start
                0: [1, 6, 3, 2, 0, 5, 4],  # Monday: Moon start
                1: [2, 0, 5, 4, 1, 6, 3],  # Tuesday: Mars
                2: [4, 1, 6, 3, 2, 0, 5],  # Wednesday: Mercury
                3: [3, 2, 0, 5, 4, 1, 6],  # Thursday: Jupiter
                4: [5, 4, 1, 6, 3, 2, 0],  # Friday: Venus
                5: [6, 3, 2, 0, 5, 4, 1],  # Saturday: Saturn
            }
            _GRAHA_NAMES = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
            hora_idx = (hora_hour - 6) % 24
            seq = _HORA_SEQ.get(weekday, _HORA_SEQ[6])
            hora_lord = _GRAHA_NAMES[seq[hora_idx % 7]]

            # Is this window in Rahu Kala?
            rahu_active = rahu_start_min <= m_mid < rahu_end_min

            score, favorable, caution_factors = _score_window(
                rule, proj_vara, proj_nak, proj_tidx,
                hora_lord, proj_paksha, rahu_active,
                yoga_quality, mw["muhurta_quality"],
            )

            # Build tithi display name
            tithi_num = (proj_tidx % 15) + 1
            tithi_name = f"{'Shukla' if proj_tidx < 15 else 'Krishna'} {tithi_num}"

            all_windows.append({
                "datetime": mw["datetime"],
                "muhurta_name": mw["muhurta_name"],
                "score": score,
                "favorable_factors": favorable,
                "caution_factors": caution_factors,
                "nakshatra": proj_nak,
                "tithi": tithi_name,
                "vara": proj_vara,
                "hora_lord": hora_lord,
            })

    # Sort by score descending
    all_windows.sort(key=lambda w: w["score"], reverse=True)
    best = all_windows[0] if all_windows else None

    # Today summary
    today_windows = [w for w in all_windows
                     if w["datetime"].startswith(now.strftime("%Y-%m-%d"))]
    today_best = max(today_windows, key=lambda w: w["score"]) if today_windows else None
    if today_best and today_best["score"] >= 0.7:
        summary = f"Today is favorable for {rule['intention_label'].lower()}. Best window: {today_best['muhurta_name']} ({today_best['datetime'][11:16]})."
    elif today_best and today_best["score"] >= 0.5:
        summary = f"Today is moderately suitable for {rule['intention_label'].lower()}. Best: {today_best['muhurta_name']}."
    else:
        summary = f"Today is not ideal for {rule['intention_label'].lower()}. Consider waiting for a better window."

    # Collect attestation from rule
    attestation = rule.get("attestation", "SYNTHESIS")

    result = {
        "intention_id": intention_id,
        "intention_label": rule.get("intention_label", ""),
        "windows": all_windows,
        "best_window": best,
        "today_summary": summary,
        "attestation": attestation,
    }

    return _validate_result(result)


def score_moment(intention_id: str, field_state: dict) -> float:
    """Score the CURRENT moment for an intention.

    0.0 = very unfavorable, 1.0 = highly auspicious.
    Uses live field_state panchanga, hora, rahu_kala, yoga.

    Args:
        intention_id: ID from intention_rules.csv.
        field_state: dict from kernel.py field_state().

    Returns:
        Float score clamped to [0.0, 1.0].
    """
    rules = _load_rules()
    rule = None
    for r in rules:
        if r["intention_id"] == intention_id:
            rule = r
            break
    if not rule:
        return 0.0

    p5 = field_state.get("panchanga", {})
    vara = _normalize_vara(p5.get("vara", ""))
    nakshatra = p5.get("nakshatra", "")
    tidx = p5.get("tidx", 0)
    paksha = p5.get("paksha", "")
    hora_lord = field_state.get("hora", {}).get("hora_lord", "")
    rahu_active = field_state.get("rahu_kala", {}).get("rahu_kala_active", False)
    yoga_quality = field_state.get("yoga", {}).get("yoga_quality", "mixed")

    # Current muhurta quality
    muhurta = field_state.get("muhurta", {})
    mname = muhurta.get("name", "")
    mq = "excellent" if "Abhijit" in mname or "Brahma" in mname else "neutral"

    score, _, _ = _score_window(
        rule, vara, nakshatra, tidx,
        hora_lord, paksha, rahu_active,
        yoga_quality, mq,
    )
    return score
