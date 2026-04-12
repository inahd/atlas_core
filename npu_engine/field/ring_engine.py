"""
ring_engine.py — Atlas ring specifications.

A ring is a circle of nodes with a cursor.
10 ring types, each driven by a dataset.
Any renderer (canvas/SVG) consumes the RingSpec.

Pattern follows ui_vastu_engine.py.
"""

import csv
import io
import math
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))

_PATHS = {
    "nakshatra": (
        os.path.join(_ROOT, "datasets", "astro", "nakshatra_canonical.csv")
        if os.path.exists(os.path.join(_ROOT, "datasets", "astro", "nakshatra_canonical.csv"))
        else os.path.join(_ROOT, "datasets", "astro", "nakshatra_master.csv")
    ),
    "graha": os.path.join(_ROOT, "datasets", "cosmology", "graha_master.csv"),
    "ashtakala": os.path.join(_ROOT, "datasets", "cosmology", "ashtakala.csv"),
    "nitya_devi": os.path.join(_ROOT, "datasets", "cosmology", "nitya_devi_master.csv"),
    "tala": os.path.join(_ROOT, "datasets", "carnatic", "tala_master.csv"),
    "herbs": os.path.join(_ROOT, "datasets", "ayurveda", "herb_spine_108.csv"),
    "plants": os.path.join(_ROOT, "datasets", "plants", "nakshatra_plants.csv"),
    "ashtakala_lila": os.path.join(_ROOT, "datasets", "cosmology", "goloka", "ashtakala_lila.csv"),
}

_cache: Dict[str, list] = {}


def _load(key):
    if key in _cache:
        return _cache[key]
    try:
        with open(_PATHS[key], encoding="utf-8") as f:
            text = f.read().lstrip()
        rows = list(csv.DictReader(io.StringIO(text)))
        _cache[key] = rows
        return rows
    except Exception:
        _cache[key] = []
        return []


# ══════════════════════════════════════════════════════════
# STYLE DEFAULTS
# ══════════════════════════════════════════════════════════

_STYLE = {
    "bg_color": "#0a0d1a",
    "ring_color": "rgba(212,168,75,0.15)",
    "active_color": "#f0c040",
    "cursor_color": "#d4a84b",
    "font": "Cormorant Garamond",
}

_QUALITY_COLOR = {
    "auspicious": "#1d9e75",
    "mixed": "#d4a84b",
    "inauspicious": "#8b1a1a",
}

_ELEM_COLOR = {
    "fire": "#CC2200", "water": "#4878c8", "air": "#A78BFA",
    "earth": "#00AA44", "ether": "#d4a84b",
}

_GRAHA_COLOR = {
    "Sun": "#FFB300", "Moon": "#E8E8FF", "Mars": "#CC2200",
    "Mercury": "#00AA44", "Jupiter": "#FFDD44", "Venus": "#FFAADD",
    "Saturn": "#445566", "Rahu": "#6600AA", "Ketu": "#887755",
}


# ══════════════════════════════════════════════════════════
# MUHURTA NAMES (30 per day, from tradition)
# ══════════════════════════════════════════════════════════

_MUHURTA_NAMES = [
    "Rudra", "Ahi", "Mitra", "Pitri", "Vasu",
    "Vara", "Vishvedeva", "Vidhi", "Satamukhi", "Puruhuta",
    "Vahini", "Naktanakara", "Varuna", "Aryaman", "Bhaga",
    "Girisha", "Ajapada", "Ahir Budhnya", "Pushan", "Ashvini",
    "Yama", "Agni", "Vidhata", "Chanda", "Aditi",
    "Jiva", "Vishnu", "Yumigadyuti", "Brahma", "Samudram",
]

_MUHURTA_QUALITY = {
    0: "mixed", 1: "inauspicious", 2: "auspicious", 3: "mixed", 4: "auspicious",
    5: "mixed", 6: "auspicious", 7: "auspicious", 8: "mixed", 9: "auspicious",
    10: "mixed", 11: "inauspicious", 12: "mixed", 13: "auspicious", 14: "auspicious",
    15: "auspicious", 16: "mixed", 17: "mixed", 18: "auspicious", 19: "auspicious",
    20: "inauspicious", 21: "mixed", 22: "auspicious", 23: "mixed", 24: "auspicious",
    25: "auspicious", 26: "auspicious", 27: "mixed", 28: "auspicious", 29: "mixed",
}

_RASHI_NAMES = [
    "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
    "Tula", "Vrischika", "Dhanu", "Makara", "Kumbha", "Meena",
]
_RASHI_SYMBOLS = [
    "\u2648", "\u2649", "\u264A", "\u264B", "\u264C", "\u264D",
    "\u264E", "\u264F", "\u2650", "\u2651", "\u2652", "\u2653",
]


# ══════════════════════════════════════════════════════════
# RING BUILDERS
# ══════════════════════════════════════════════════════════

def _ring_muhurta(fs):
    now = datetime.now()
    minutes = now.hour * 60 + now.minute
    sunrise = 360  # 6am
    idx = max(0, min(29, (minutes - sunrise + 96) // 48))  # 48min per muhurta, offset for brahma
    nodes = []
    for i in range(30):
        q = _MUHURTA_QUALITY.get(i, "mixed")
        nodes.append({
            "index": i, "angle_deg": i * 12.0,
            "entity_id": f"muhurta_{i}",
            "label": _MUHURTA_NAMES[i][:8], "label_full": _MUHURTA_NAMES[i],
            "color": _QUALITY_COLOR.get(q, "#d4a84b"),
            "size": 1.2 if q == "auspicious" else 0.8,
            "active": i == idx, "quality": q,
            "symbol": "\u2713" if q == "auspicious" else "\u223C" if q == "mixed" else "\u2717",
            "data": {},
        })
    return {
        "ring_id": "muhurta", "label": "Muhurta Ring", "total_nodes": 30,
        "nodes": nodes,
        "cursor": {"angle_deg": idx * 12.0, "speed_deg_per_min": 12.0 / 48,
                   "entity_id": f"muhurta_{idx}", "label": _MUHURTA_NAMES[idx]},
        "center": {"label": _MUHURTA_NAMES[idx], "value": _MUHURTA_QUALITY.get(idx, "mixed"),
                   "color": "#f0c040"},
        "style": _STYLE, "attestation": "SYNTHESIS",
    }


def _norm_nak(s):
    s = s.lower().replace(" ", "_").replace("ā", "a").replace("ī", "i").replace("ū", "u")
    s = s.replace("ṛ", "r").replace("ṣ", "sh").replace("ś", "sh").replace("ṇ", "n").replace("ṭ", "t")
    return s.replace("v", "w")  # Svati↔Swati


def _ring_nakshatra(fs):
    rows = _load("nakshatra")
    p5 = fs.get("panchanga", {})
    current = _norm_nak(p5.get("nakshatra", ""))
    nodes = []
    active_idx = 0
    for i, r in enumerate(rows):
        name = r.get("nakshatra", "")
        is_active = _norm_nak(name) in current or current in _norm_nak(name)
        if is_active:
            active_idx = i
        elem = r.get("element", "ether").lower()
        nodes.append({
            "index": i, "angle_deg": i * (360.0 / 27),
            "entity_id": f"nakshatra_{name.lower().replace(' ', '_')}",
            "label": name[:6], "label_full": name,
            "color": _ELEM_COLOR.get(elem, "#d4a84b"),
            "size": 1.5 if is_active else 0.8,
            "active": is_active, "quality": r.get("guna", ""),
            "symbol": r.get("emoji", "\u2736"), "data": {"element": elem, "guna": r.get("guna", "")},
        })
    return {
        "ring_id": "nakshatra", "label": "Nakshatra Ring", "total_nodes": len(nodes),
        "nodes": nodes,
        "cursor": {"angle_deg": active_idx * (360.0 / 27), "speed_deg_per_min": 0.55 / 60,
                   "entity_id": nodes[active_idx]["entity_id"] if nodes else "",
                   "label": p5.get("nakshatra", "")},
        "center": {"label": p5.get("nakshatra", ""), "value": p5.get("element", ""),
                   "color": "#f0c040"},
        "style": _STYLE, "attestation": "OBSERVED",
    }


def _ring_devi(fs):
    rows = _load("nitya_devi")
    p5 = fs.get("panchanga", {})
    tidx = int(p5.get("tidx", 0))
    tithi_num = (tidx % 15) + 1
    nodes = []
    for i, r in enumerate(rows):
        tn = int(r.get("tithi_num", i + 1))
        is_active = tn == tithi_num
        elem = r.get("element", "ether").lower()
        nodes.append({
            "index": i, "angle_deg": i * 24.0,
            "entity_id": r.get("id", ""),
            "label": r.get("name_iast", "")[:8], "label_full": r.get("name_iast", ""),
            "color": r.get("color_hex", _ELEM_COLOR.get(elem, "#d4a84b")),
            "size": 1.5 if is_active else 0.8,
            "active": is_active, "quality": r.get("rasa", ""),
            "symbol": r.get("bija", "")[:3], "data": {"rasa": r.get("rasa", ""), "shakti": r.get("shakti", "")},
        })
    active = [n for n in nodes if n["active"]]
    return {
        "ring_id": "devi", "label": "Nitya Devi Ring", "total_nodes": len(nodes),
        "nodes": nodes,
        "cursor": {"angle_deg": (tithi_num - 1) * 24.0, "speed_deg_per_min": 24.0 / 1440,
                   "entity_id": active[0]["entity_id"] if active else "",
                   "label": active[0]["label_full"] if active else ""},
        "center": {"label": active[0]["label_full"] if active else "",
                   "value": active[0]["data"]["rasa"] if active else "",
                   "color": active[0]["color"] if active else "#d4a84b"},
        "style": _STYLE, "attestation": "OBSERVED",
    }


def _ring_graha(fs):
    rows = _load("graha")
    p5 = fs.get("panchanga", {})
    hora_lord = fs.get("hora", {}).get("hora_lord", "Sun")
    nodes = []
    for i, r in enumerate(rows):
        name = r.get("graha", "")
        is_active = name.lower() == hora_lord.lower()
        nodes.append({
            "index": i, "angle_deg": i * 40.0,
            "entity_id": f"graha_{name.lower()}",
            "label": name[:4], "label_full": name,
            "color": _GRAHA_COLOR.get(name, "#d4a84b"),
            "size": 1.5 if is_active else 1.0,
            "active": is_active, "quality": r.get("guna", ""),
            "symbol": r.get("symbol", ""), "data": {"element": r.get("element", ""), "domain": r.get("domain", "")},
        })
    return {
        "ring_id": "graha", "label": "Graha Ring", "total_nodes": len(nodes),
        "nodes": nodes,
        "cursor": {"angle_deg": next((n["angle_deg"] for n in nodes if n["active"]), 0),
                   "speed_deg_per_min": 0, "entity_id": "", "label": hora_lord},
        "center": {"label": hora_lord, "value": "hora lord", "color": _GRAHA_COLOR.get(hora_lord, "#d4a84b")},
        "style": _STYLE, "attestation": "OBSERVED",
    }


def _ring_tala(fs):
    rows = _load("tala")
    ss = fs.get("sound_state", {})
    tala_name = ss.get("tala", "Adi")
    bpm = float(ss.get("bpm", 72))
    # Find tala definition
    tala_row = None
    for r in rows:
        if tala_name.lower() in r.get("name_iast", "").lower():
            tala_row = r
            break
    beats = int(tala_row.get("beat_count", 8)) if tala_row else 8
    nodes = []
    for i in range(beats):
        nodes.append({
            "index": i, "angle_deg": i * (360.0 / beats),
            "entity_id": f"beat_{i}",
            "label": str(i + 1), "label_full": f"Beat {i + 1}",
            "color": "#f0c040" if i == 0 else "#d4a84b",
            "size": 1.5 if i == 0 else 0.8,
            "active": False, "quality": "sam" if i == 0 else "",
            "symbol": "\u25CF" if i == 0 else "\u25CB",
            "data": {"bol": "", "swara": "", "vel": 0.5},
        })
    speed = (360.0 / beats) * (bpm / 60.0)  # degrees per second → per minute
    return {
        "ring_id": "tala", "label": f"{tala_name} ({beats} beats)", "total_nodes": beats,
        "nodes": nodes,
        "cursor": {"angle_deg": 0, "speed_deg_per_min": speed * 60,
                   "entity_id": "beat_0", "label": f"{tala_name} · {bpm} bpm"},
        "center": {"label": tala_name, "value": f"{beats} beats · {bpm} bpm", "color": "#d4a84b"},
        "style": _STYLE, "attestation": "OBSERVED",
    }


def _ring_herb_dosha(fs):
    rows = _load("herbs")
    p5 = fs.get("panchanga", {})
    element = p5.get("element", "ether").lower()
    nodes = []
    for i, r in enumerate(rows):
        dosha = r.get("dosha_effect", "").lower()
        color = "#A78BFA" if "vata" in dosha else "#CC2200" if "pitta" in dosha else "#00AA44"
        nodes.append({
            "index": i, "angle_deg": i * (360.0 / max(len(rows), 1)),
            "entity_id": r.get("herb_id", f"herb_{i}"),
            "label": r.get("name_common", "")[:6], "label_full": r.get("name_common", ""),
            "color": color, "size": 0.6, "active": False,
            "quality": dosha[:10], "symbol": "",
            "data": {"rasa": r.get("rasa", ""), "virya": r.get("virya", "")},
        })
    return {
        "ring_id": "herb_dosha", "label": "Herb Dosha Ring", "total_nodes": len(nodes),
        "nodes": nodes,
        "cursor": {"angle_deg": 0, "speed_deg_per_min": 0,
                   "entity_id": "", "label": element},
        "center": {"label": "108 herbs", "value": element, "color": "#d4a84b"},
        "style": _STYLE, "attestation": "OBSERVED",
    }


def _ring_agricultural(fs):
    rows = _load("plants")
    p5 = fs.get("panchanga", {})
    current_nak = _norm_nak(p5.get("nakshatra", ""))
    nodes = []
    active_idx = 0
    for i, r in enumerate(rows):
        nak = r.get("nakshatra", "")
        is_active = _norm_nak(nak) in current_nak or current_nak in _norm_nak(nak)
        if is_active:
            active_idx = i
        elem = r.get("element", "earth").lower()
        nodes.append({
            "index": i, "angle_deg": i * (360.0 / 27),
            "entity_id": "plant_" + r.get("plant", "").lower().replace(" ", "_"),
            "label": r.get("plant", "")[:7], "label_full": r.get("plant", ""),
            "color": _ELEM_COLOR.get(elem, "#00AA44"),
            "size": 1.3 if is_active else 0.7,
            "active": is_active, "quality": r.get("use", ""),
            "symbol": "\u2767", "data": {"nakshatra": nak, "season": r.get("season", "")},
        })
    return {
        "ring_id": "agricultural", "label": "Agricultural Ring", "total_nodes": len(nodes),
        "nodes": nodes,
        "cursor": {"angle_deg": active_idx * (360.0 / 27), "speed_deg_per_min": 0,
                   "entity_id": nodes[active_idx]["entity_id"] if nodes else "",
                   "label": nodes[active_idx]["label_full"] if nodes else ""},
        "center": {"label": nodes[active_idx]["label_full"] if nodes else "",
                   "value": "nakshatra plant", "color": "#5cb87a"},
        "style": _STYLE, "attestation": "OBSERVED",
    }


def _ring_zodiac(fs):
    p5 = fs.get("panchanga", {})
    tidx = int(p5.get("tidx", 0))
    # Rough rashi from tidx (not astronomical — approximate)
    rashi_idx = (tidx * 12 // 30) % 12
    nodes = []
    for i in range(12):
        nodes.append({
            "index": i, "angle_deg": i * 30.0,
            "entity_id": f"rashi_{_RASHI_NAMES[i].lower()}",
            "label": _RASHI_NAMES[i][:4], "label_full": _RASHI_NAMES[i],
            "color": _ELEM_COLOR.get(["fire", "earth", "air", "water"][i % 4], "#d4a84b"),
            "size": 1.3 if i == rashi_idx else 0.8,
            "active": i == rashi_idx, "quality": "",
            "symbol": _RASHI_SYMBOLS[i], "data": {},
        })
    return {
        "ring_id": "zodiac", "label": "Zodiac Ring", "total_nodes": 12,
        "nodes": nodes,
        "cursor": {"angle_deg": rashi_idx * 30.0, "speed_deg_per_min": 0,
                   "entity_id": f"rashi_{_RASHI_NAMES[rashi_idx].lower()}",
                   "label": _RASHI_NAMES[rashi_idx]},
        "center": {"label": _RASHI_NAMES[rashi_idx], "value": "Moon rashi", "color": "#E8E8FF"},
        "style": _STYLE, "attestation": "SYNTHESIS",
    }


def _ring_raga_time(fs):
    rows = _load("ashtakala")
    now = datetime.now()
    hour = now.hour
    nodes = []
    active_idx = 0
    for i, r in enumerate(rows):
        # Parse time range
        start_str = r.get("time_start", "0:00am")
        try:
            h = int(start_str.replace("am", "").replace("pm", "").split(":")[0])
            if "pm" in start_str and h != 12:
                h += 12
        except ValueError:
            h = i * 3
        if h <= hour:
            active_idx = i
        nodes.append({
            "index": i, "angle_deg": i * 45.0,
            "entity_id": f"ashtakala_{i}",
            "label": r.get("name", "")[:8], "label_full": r.get("name", ""),
            "color": ["#4a2a6a", "#d4a84b", "#FFB300", "#f0b060", "#FFAADD", "#1d9e75", "#4878c8", "#2a1a4a"][i % 8],
            "size": 1.3, "active": i == active_idx,
            "quality": r.get("activity", ""), "symbol": "",
            "data": {"raga": r.get("raga", ""), "time": f"{r.get('time_start','')}–{r.get('time_end','')}"},
        })
    return {
        "ring_id": "raga_time", "label": "Raga Time Ring", "total_nodes": len(nodes),
        "nodes": nodes,
        "cursor": {"angle_deg": (hour / 24.0) * 360.0, "speed_deg_per_min": 360.0 / 1440,
                   "entity_id": nodes[active_idx]["entity_id"] if nodes else "",
                   "label": nodes[active_idx]["data"]["raga"] if nodes else ""},
        "center": {"label": nodes[active_idx]["data"]["raga"] if nodes else "",
                   "value": nodes[active_idx]["label_full"] if nodes else "",
                   "color": nodes[active_idx]["color"] if nodes else "#d4a84b"},
        "style": _STYLE, "attestation": "OBSERVED",
    }


def _ring_ashtakala(fs):
    rows = _load("ashtakala_lila")
    if not rows:
        return _ring_raga_time(fs)  # fallback to regular ashtakala
    now = datetime.now()
    hour = now.hour
    nodes = []
    active_idx = 0
    for i, r in enumerate(rows):
        time_range = r.get("time_range", "")
        # Extract hour from time range like "3:36 – 6:00 A.M."
        try:
            h_str = time_range.split("–")[0].strip().split(":")[0].strip()
            h = int(h_str)
            if "P.M." in time_range.upper() and h != 12:
                h += 12
        except (ValueError, IndexError):
            h = i * 3
        if h <= hour:
            active_idx = i
        sakhi = r.get("presiding_sakhi", "")
        raga = r.get("traditional_raga", "")
        nodes.append({
            "index": i, "angle_deg": i * 45.0,
            "entity_id": f"goloka_period_{i}",
            "label": r.get("period_name", "")[:10], "label_full": r.get("period_name", ""),
            "color": ["#4a2a6a", "#d4a84b", "#FFB300", "#f0b060", "#FFAADD", "#1d9e75", "#4878c8", "#2a1a4a"][i % 8],
            "size": 1.3, "active": i == active_idx,
            "quality": r.get("mood_rasa", ""), "symbol": "",
            "data": {"sakhi": sakhi, "raga": raga, "location": r.get("location", "")},
        })
    active = nodes[active_idx] if nodes else {}
    return {
        "ring_id": "ashtakala", "label": "Ashtakala Ring (Goloka)", "total_nodes": len(nodes),
        "nodes": nodes,
        "cursor": {"angle_deg": (hour / 24.0) * 360.0, "speed_deg_per_min": 360.0 / 1440,
                   "entity_id": active.get("entity_id", ""),
                   "label": active.get("data", {}).get("raga", "")},
        "center": {"label": active.get("label_full", ""),
                   "value": active.get("data", {}).get("sakhi", ""),
                   "color": active.get("color", "#d4a84b")},
        "style": _STYLE, "attestation": "OBSERVED",
    }


# ══════════════════════════════════════════════════════════
# RING REGISTRY
# ══════════════════════════════════════════════════════════

_RINGS = {
    "muhurta": _ring_muhurta,
    "nakshatra": _ring_nakshatra,
    "devi": _ring_devi,
    "graha": _ring_graha,
    "tala": _ring_tala,
    "herb_dosha": _ring_herb_dosha,
    "agricultural": _ring_agricultural,
    "zodiac": _ring_zodiac,
    "raga_time": _ring_raga_time,
    "ashtakala": _ring_ashtakala,
}


# ══════════════════════════════════════════════════════════
# PUBLIC API
# ══════════════════════════════════════════════════════════

def derive_ring_spec(ring_id: str, field_state: dict) -> dict:
    """Generate ring specification. Never raises."""
    try:
        builder = _RINGS.get(ring_id)
        if builder is None:
            return {"ring_id": ring_id, "label": "Unknown", "total_nodes": 0,
                    "nodes": [], "cursor": {"angle_deg": 0, "speed_deg_per_min": 0,
                    "entity_id": "", "label": ""},
                    "center": {"label": "", "value": "", "color": "#d4a84b"},
                    "style": _STYLE, "attestation": "SYNTHESIS"}
        return builder(field_state)
    except Exception:
        return {"ring_id": ring_id, "label": ring_id, "total_nodes": 0,
                "nodes": [], "cursor": {"angle_deg": 0, "speed_deg_per_min": 0,
                "entity_id": "", "label": ""},
                "center": {"label": "", "value": "", "color": "#d4a84b"},
                "style": _STYLE, "attestation": "SYNTHESIS"}


def derive_all_rings(field_state: dict) -> dict:
    """All 10 ring specs in one call."""
    return {ring_id: derive_ring_spec(ring_id, field_state)
            for ring_id in _RINGS}
