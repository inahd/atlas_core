"""
jyotish_utils.py — Normalization, parsing, and CSV loaders for jyotisha engine.

No dependencies on kernel.py or Flask.
"""

import csv
import os
from typing import Dict, List, Optional

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, ".."))
_JYOTISH_DIR = os.path.join(_ROOT, "datasets", "jyotish")

# ══════════════════════════════════════════════════════════
# A) ALIAS MAPS
# ══════════════════════════════════════════════════════════

_RASHI_IAST = [
    "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
    "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena",
]
_RASHI_DIACRITICAL = [
    "Meṣa", "Vṛṣabha", "Mithuna", "Karkaṭa", "Siṃha", "Kanyā",
    "Tulā", "Vṛścika", "Dhanus", "Makara", "Kumbha", "Mīna",
]
# kernel.py RASHIS[] uses a slightly different set:
_RASHI_KERNEL = [
    "Meṣa", "Vṛṣabha", "Mithuna", "Karka", "Siṃha", "Kanyā",
    "Tulā", "Vṛścika", "Dhanu", "Makara", "Kumbha", "Mīna",
]
_RASHI_ENGLISH = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

_GRAHA_IAST = [
    "Surya", "Chandra", "Mangala", "Budha", "Guru", "Shukra", "Shani", "Rahu", "Ketu",
]
_GRAHA_DIACRITICAL = [
    "Sūrya", "Candra", "Maṅgala", "Budha", "Guru", "Śukra", "Śani", "Rāhu", "Ketu",
]
_GRAHA_ENGLISH = [
    "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu",
]

# Build lookup: any spelling -> index
_rashi_lookup: Dict[str, int] = {}
for i in range(12):
    for name in [_RASHI_IAST[i], _RASHI_DIACRITICAL[i], _RASHI_KERNEL[i], _RASHI_ENGLISH[i]]:
        _rashi_lookup[name.lower()] = i

_graha_lookup: Dict[str, int] = {}
for i in range(9):
    for name in [_GRAHA_IAST[i], _GRAHA_DIACRITICAL[i], _GRAHA_ENGLISH[i]]:
        _graha_lookup[name.lower()] = i


# ══════════════════════════════════════════════════════════
# B) NORMALIZE FUNCTIONS
# ══════════════════════════════════════════════════════════

def normalize_rashi(name: str) -> Optional[dict]:
    """Accept any rashi spelling, return all conventions + index."""
    idx = _rashi_lookup.get(name.lower().strip())
    if idx is None:
        return None
    return {
        "iast": _RASHI_IAST[idx],
        "diacritical": _RASHI_DIACRITICAL[idx],
        "english": _RASHI_ENGLISH[idx],
        "index": idx,
    }


def normalize_graha(name: str) -> Optional[dict]:
    """Accept any graha spelling, return all conventions + index."""
    idx = _graha_lookup.get(name.lower().strip())
    if idx is None:
        return None
    return {
        "iast": _GRAHA_IAST[idx],
        "diacritical": _GRAHA_DIACRITICAL[idx],
        "english": _GRAHA_ENGLISH[idx],
        "index": idx,
    }


def rashi_from_longitude(lon: float) -> str:
    """Sidereal longitude -> simplified IAST rashi name."""
    return _RASHI_IAST[int(lon % 360 / 30) % 12]


def rashi_index(name: str) -> int:
    """Any rashi name -> 0-11 index. Returns -1 if not found."""
    return _rashi_lookup.get(name.lower().strip(), -1)


def graha_index(name: str) -> int:
    """Any graha name -> 0-8 index. Returns -1 if not found."""
    return _graha_lookup.get(name.lower().strip(), -1)


# ══════════════════════════════════════════════════════════
# C) PARSE DMS
# ══════════════════════════════════════════════════════════

def parse_dms(dms_str: str) -> float:
    """Parse "13:34:22" or "13°34'22\"" to decimal degrees."""
    import re
    parts = re.split(r"[:\s°'\"]+", str(dms_str).strip())
    parts = [p for p in parts if p]
    d = float(parts[0]) if len(parts) > 0 else 0.0
    m = float(parts[1]) if len(parts) > 1 else 0.0
    s = float(parts[2]) if len(parts) > 2 else 0.0
    return d + m / 60.0 + s / 3600.0


# ══════════════════════════════════════════════════════════
# D) CSV LOADERS (cached)
# ══════════════════════════════════════════════════════════

_cache: Dict[str, object] = {}


def _csv_rows(filename: str) -> List[dict]:
    path = os.path.join(_JYOTISH_DIR, filename)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        # skip comment lines starting with #
        lines = [line for line in f if not line.startswith("#")]
    import io
    return list(csv.DictReader(io.StringIO("".join(lines))))


def load_rashi_lords() -> Dict[str, str]:
    """rashi (simplified IAST) -> lord (English)."""
    if "rashi_lords" in _cache:
        return _cache["rashi_lords"]
    result = {}
    for row in _csv_rows("rashi_lords.csv"):
        result[row["rashi"]] = row["lord"]
    _cache["rashi_lords"] = result
    return result


def load_graha_dignity() -> Dict[str, dict]:
    """graha (English) -> dignity data."""
    if "dignity" in _cache:
        return _cache["dignity"]
    result = {}
    for row in _csv_rows("graha_dignity.csv"):
        result[row["graha"]] = row
    _cache["dignity"] = result
    return result


def load_graha_friendship() -> Dict[str, dict]:
    """graha (English) -> friendship data."""
    if "friendship" in _cache:
        return _cache["friendship"]
    result = {}
    for row in _csv_rows("graha_friendship.csv"):
        friends = [row.get(f"friend_{i}", "") for i in range(1, 4)]
        neutrals = [row.get(f"neutral_{i}", "") for i in range(1, 3)]
        enemies = [row.get(f"enemy_{i}", "") for i in range(1, 4)]
        result[row["graha"]] = {
            "friends": [f for f in friends if f],
            "neutrals": [n for n in neutrals if n],
            "enemies": [e for e in enemies if e],
        }
    _cache["friendship"] = result
    return result


def load_graha_aspects() -> Dict[str, List[int]]:
    """graha (English) -> list of aspect house offsets (ints)."""
    if "aspects" in _cache:
        return _cache["aspects"]
    result = {}
    for row in _csv_rows("graha_aspects.csv"):
        offsets_str = row.get("aspect_house_offsets", "7")
        offsets = [int(x.strip()) for x in offsets_str.split(",") if x.strip()]
        result[row["graha"]] = offsets
    _cache["aspects"] = result
    return result


def load_graha_karakas() -> Dict[str, dict]:
    """graha (English) -> karaka data."""
    if "karakas" in _cache:
        return _cache["karakas"]
    result = {}
    for row in _csv_rows("graha_karakas.csv"):
        result[row["graha"]] = {
            "atma_karaka_rank": int(row["atma_karaka_rank"]) if row.get("atma_karaka_rank") else None,
            "naisargika_karakas": row.get("naisargika_karakas", ""),
        }
    _cache["karakas"] = result
    return result


# ══════════════════════════════════════════════════════════
# NAKSHATRA DATA (for engine use)
# ══════════════════════════════════════════════════════════

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

NAK_LORDS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu",
    "Jupiter", "Saturn", "Mercury", "Ketu", "Venus", "Sun",
    "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu",
    "Jupiter", "Saturn", "Mercury",
]

_NAK_SIZE = 360.0 / 27.0
_PADA_SIZE = _NAK_SIZE / 4.0


def nak_from_longitude(lon: float) -> str:
    return NAKSHATRAS[int((lon % 360) / _NAK_SIZE) % 27]


def nak_index_from_longitude(lon: float) -> int:
    return int((lon % 360) / _NAK_SIZE) % 27


def pada_from_longitude(lon: float) -> int:
    return int(((lon % 360) % _NAK_SIZE) / _PADA_SIZE) + 1


def nak_lord_from_longitude(lon: float) -> str:
    return NAK_LORDS[nak_index_from_longitude(lon)]


TITHIS = [
    "Shukla Pratipada", "Shukla Dvitiya", "Shukla Tritiya", "Shukla Chaturthi",
    "Shukla Panchami", "Shukla Shashthi", "Shukla Saptami", "Shukla Ashtami",
    "Shukla Navami", "Shukla Dashami", "Shukla Ekadashi", "Shukla Dvadashi",
    "Shukla Trayodashi", "Shukla Chaturdashi", "Purnima",
    "Krishna Pratipada", "Krishna Dvitiya", "Krishna Tritiya", "Krishna Chaturthi",
    "Krishna Panchami", "Krishna Shashthi", "Krishna Saptami", "Krishna Ashtami",
    "Krishna Navami", "Krishna Dashami", "Krishna Ekadashi", "Krishna Dvadashi",
    "Krishna Trayodashi", "Krishna Chaturdashi", "Amavasya",
]

TITHI_DEITIES = [
    "Agni", "Brahma", "Gauri", "Ganapati", "Naga", "Kartikeya",
    "Surya", "Shiva", "Durga", "Dharma", "Vishvadeva", "Vishnu",
    "Kama", "Shiva", "Chandra",
    "Pitris", "Brahma", "Gauri", "Ganapati", "Naga", "Kartikeya",
    "Surya", "Shiva", "Durga", "Dharma", "Vishvadeva", "Vishnu",
    "Kama", "Shiva", "Pitris",
]
