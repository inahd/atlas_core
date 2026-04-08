"""
graph_seed_data.py — Seeds all rhythm-relational data.

Tala structures, bol properties, theka sequences, rasa-tala affinities,
characteristic tihai phrases, fill patterns, layakari rules.
All stability: working, authority: sadhu.

Carnatic enrichment loaded from datasets/carnatic/:
    gati_definitions.csv   — 5 gati with element/guna correspondence
    tala_families.csv      — 7 tala families with graha links
    korvai_rules.csv       — triple-repetition cadence rules
    sollukattu.csv         — rhythmic syllable patterns
"""
import csv
import os
import logging

log = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────
# TALA STRUCTURES
# ──────────────────────────────────────────────────────────────

TALA_STRUCTURES = {
    "Teentaal": {
        "beats": 16,
        "vibhag": [4, 4, 4, 4],
        "vibhag_gravity": [1.0, 0.6, 0.1, 0.8],  # sam, mid, khali, build-back
        "sam": 0,
        "khali": 8,
        "theka": ["dha","dhin","dhin","dha", "dha","dhin","dhin","dha",
                  "dha","tin","tin","ta", "ta","dhin","dhin","dha"],
        "rasa_affinity": {"shringara": 0.9, "vira": 0.8, "shanta": 0.7, "hasya": 0.6,
                          "karuna": 0.4, "raudra": 0.5, "adbhuta": 0.5},
    },
    "Rupak": {
        "beats": 7,
        "vibhag": [3, 2, 2],
        "vibhag_gravity": [0.3, 0.7, 0.6],  # sam IS light in Rupak — unique
        "sam": 0,
        "khali": 0,  # sam position is khali in Rupak
        "theka": ["tin","tin","na", "dhin","na", "dhin","na"],
        "rasa_affinity": {"karuna": 0.9, "shringara": 0.7, "shanta": 0.6},
        "characteristic": "sam_is_light",
    },
    "Jhaptal": {
        "beats": 10,
        "vibhag": [2, 3, 2, 3],
        "vibhag_gravity": [1.0, 0.6, 0.1, 0.7],
        "sam": 0,
        "khali": 4,
        "theka": ["dhin","na", "dhin","dhin","na", "tin","na", "dhin","dhin","na"],
        "rasa_affinity": {"vira": 0.9, "adbhuta": 0.8, "raudra": 0.6},
    },
    "Adi": {
        "beats": 8,
        "vibhag": [4, 4],
        "vibhag_gravity": [1.0, 0.2],
        "sam": 0,
        "khali": 4,
        "theka": ["dha","dhin","dhin","dha", "dha","tin","tin","ta"],
        "rasa_affinity": {"shringara": 0.8, "shanta": 0.7, "hasya": 0.6, "vira": 0.5},
    },
    "Ektal": {
        "beats": 12,
        "vibhag": [2, 2, 2, 2, 2, 2],
        "vibhag_gravity": [1.0, 0.4, 0.6, 0.1, 0.5, 0.8],
        "sam": 0,
        "khali": 6,
        "theka": ["dhin","dhin", "dhage","trkte", "tu","na",
                  "kat","ta", "dhage","trkte", "dhin","na"],
        "rasa_affinity": {"shanta": 0.9, "karuna": 0.8, "adbhuta": 0.5},
        "characteristic": "meditative",
    },
    "Dadra": {
        "beats": 6,
        "vibhag": [3, 3],
        "vibhag_gravity": [1.0, 0.3],
        "sam": 0,
        "khali": 3,
        "theka": ["dha","dhin","na", "dha","tin","na"],
        "rasa_affinity": {"shringara": 0.9, "hasya": 0.7, "karuna": 0.5},
    },
    "Chautal": {
        "beats": 12,
        "vibhag": [4, 4, 2, 2],
        "vibhag_gravity": [1.0, 0.2, 0.6, 0.7],
        "sam": 0,
        "khali": 4,
        "theka": ["dha","dha","din","ta", "kite","dha","din","ta",
                  "tite","kata", "gadi","gana"],
        "rasa_affinity": {"vira": 0.8, "raudra": 0.7, "shanta": 0.6},
    },
    "Keherwa": {
        "beats": 8,
        "vibhag": [4, 4],
        "vibhag_gravity": [1.0, 0.3],
        "sam": 0,
        "khali": 4,
        "theka": ["dha","ge","na","tin", "na","ke","dhin","na"],
        "rasa_affinity": {"shringara": 0.8, "hasya": 0.8, "karuna": 0.5},
    },
}

# ──────────────────────────────────────────────────────────────
# BOL PROPERTIES — every stroke is a relational node
# ──────────────────────────────────────────────────────────────

BOL_PROPERTIES = {
    "dha":   {"weight": 1.0,  "hand": "both",        "resonance": "open",          "rasa": ["shringara", "vira"]},
    "dhin":  {"weight": 0.9,  "hand": "both",        "resonance": "resonant_long", "rasa": ["shringara"]},
    "dhi":   {"weight": 0.85, "hand": "both",        "resonance": "resonant",      "rasa": ["vira"]},
    "din":   {"weight": 0.7,  "hand": "both",        "resonance": "resonant",      "rasa": ["vira"]},
    "tin":   {"weight": 0.5,  "hand": "right_closed", "resonance": "closed",       "rasa": ["karuna", "shanta"]},
    "ta":    {"weight": 0.4,  "hand": "right_open",  "resonance": "dry",           "rasa": ["raudra", "vira"]},
    "na":    {"weight": 0.3,  "hand": "right_open",  "resonance": "open",          "rasa": ["shanta", "karuna"]},
    "ne":    {"weight": 0.3,  "hand": "right_open",  "resonance": "open",          "rasa": ["shanta"]},
    "ge":    {"weight": 0.5,  "hand": "left",        "resonance": "resonant",      "rasa": ["shringara"]},
    "ke":    {"weight": 0.4,  "hand": "left",        "resonance": "dry",           "rasa": ["vira"]},
    "te":    {"weight": 0.35, "hand": "right_closed", "resonance": "closed",       "rasa": ["vira"]},
    "ti":    {"weight": 0.35, "hand": "right_closed", "resonance": "closed",       "rasa": ["shanta"]},
    "tu":    {"weight": 0.3,  "hand": "right_closed", "resonance": "closed",       "rasa": ["shanta"]},
    "kat":   {"weight": 0.4,  "hand": "left",        "resonance": "dry",           "rasa": ["raudra"]},
    "tite":  {"weight": 0.3,  "hand": "right_closed", "resonance": "ornamental",   "rasa": ["vira"]},
    "tete":  {"weight": 0.25, "hand": "right_closed", "resonance": "ornamental",   "rasa": ["hasya"]},
    "kre":   {"weight": 0.2,  "hand": "right_closed", "resonance": "fill",         "rasa": ["vira"]},
    "kata":  {"weight": 0.35, "hand": "left",        "resonance": "fill",          "rasa": ["vira"]},
    "kite":  {"weight": 0.35, "hand": "left",        "resonance": "fill",          "rasa": ["vira"]},
    "gadi":  {"weight": 0.4,  "hand": "left",        "resonance": "fill",          "rasa": ["shringara"]},
    "gana":  {"weight": 0.4,  "hand": "left",        "resonance": "fill",          "rasa": ["shringara"]},
    "trkte": {"weight": 0.3,  "hand": "right_closed", "resonance": "ornamental",   "rasa": ["vira"]},
    "dhage": {"weight": 0.6,  "hand": "both",        "resonance": "ornamental",    "rasa": ["shringara"]},
}

# ──────────────────────────────────────────────────────────────
# LAYAKARI TRANSITIONS
# ──────────────────────────────────────────────────────────────

LAYAKARI = {
    "aadh":    {"factor": 0.5, "mode": ["alap", "vistar"], "arc_range": (0.0, 0.3)},
    "thah":    {"factor": 1,   "mode": ["gat", "alap"],    "arc_range": (0.0, 0.6)},
    "dugun":   {"factor": 2,   "mode": ["gat", "taan"],    "arc_range": (0.3, 0.8)},
    "tigun":   {"factor": 3,   "mode": ["taan", "jhala"],  "arc_range": (0.5, 0.9)},
    "chaugun": {"factor": 4,   "mode": ["jhala"],          "arc_range": (0.7, 1.0)},
}

# ──────────────────────────────────────────────────────────────
# CHARACTERISTIC TIHAI PHRASES (bol index sequences per tala)
# ──────────────────────────────────────────────────────────────
# Each phrase: list of bol names. Tihai = phrase x3, landing on sam.

TIHAI_PHRASES = {
    "Teentaal": [
        ["dha", "dhin", "dhin", "dha"],
        ["dha", "tin", "tin", "ta", "ta", "dhin"],
        ["dha", "ge", "tin", "ta"],
        ["dha", "dhin", "dha", "ge", "na", "tin"],
    ],
    "Rupak": [
        ["tin", "na", "dhin"],
        ["dhin", "na", "tin", "na"],
    ],
    "Jhaptal": [
        ["dhin", "na", "dhin", "dhin"],
        ["tin", "na", "dhin", "na"],
        ["dhin", "dhin", "na", "tin", "na"],
    ],
    "Adi": [
        ["dha", "dhin", "dhin", "dha"],
        ["dha", "tin", "ta"],
        ["dha", "dhin", "dha", "tin", "tin", "ta"],
    ],
    "Ektal": [
        ["dhin", "dhin", "dhage", "trkte"],
        ["tu", "na", "kat", "ta"],
    ],
    "Dadra": [
        ["dha", "dhin", "na"],
        ["dha", "tin"],
    ],
    "Chautal": [
        ["dha", "dha", "din", "ta"],
        ["kite", "dha", "din"],
    ],
    "Keherwa": [
        ["dha", "ge", "na", "tin"],
        ["na", "ke", "dhin"],
    ],
}

# ──────────────────────────────────────────────────────────────
# FILL PATTERNS
# ──────────────────────────────────────────────────────────────

FILL_TYPES = {
    "peshkar": {"intensity": 0.4, "mode": ["alap", "gat"], "bols": ["dha", "ge", "tin", "na", "ke", "dhin"]},
    "kaida":   {"intensity": 0.6, "mode": ["gat"],         "bols": ["dha", "dhin", "dhin", "dha", "tin", "tin", "ta", "ta"]},
    "palte":   {"intensity": 0.7, "mode": ["gat", "taan"], "bols": ["dha", "tin", "dha", "ge", "dha", "tin", "dha", "na"]},
    "chakradar": {"intensity": 0.9, "mode": ["taan", "jhala"], "bols": ["dha", "dhin", "dha"]},  # tihai of a tihai
}

# ──────────────────────────────────────────────────────────────
# CROSS RHYTHM — polyrhythm affinities
# ──────────────────────────────────────────────────────────────

CROSS_RHYTHMS = {
    "tisra":    {"subdivision": 3, "rasa": ["shringara", "karuna"], "tension": 0.4},
    "chatusra": {"subdivision": 4, "rasa": ["vira", "raudra"],     "tension": 0.3},
    "khanda":   {"subdivision": 5, "rasa": ["vira", "adbhuta"],    "tension": 0.7},
    "misra":    {"subdivision": 7, "rasa": ["adbhuta"],            "tension": 0.9},
}

# Rasa → cross rhythm preference (None = no cross rhythm)
RASA_CROSS = {
    "shringara": "tisra",
    "vira":      "khanda",
    "karuna":    None,
    "raudra":    "chatusra",
    "adbhuta":   "misra",
    "hasya":     "tisra",
    "bhayanaka": None,
    "bibhatsa":  None,
    "shanta":    None,
}

# ──────────────────────────────────────────────────────────────
# CARNATIC ENRICHMENT (loaded from datasets/carnatic/)
# ──────────────────────────────────────────────────────────────

_CARNATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "datasets", "carnatic")
_carnatic_cache = {}


def _load_carnatic(name, filename):
    if name in _carnatic_cache:
        return _carnatic_cache[name]
    try:
        path = os.path.join(_CARNATIC_DIR, filename)
        with open(path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        _carnatic_cache[name] = rows
        log.info("loaded %d rows from carnatic/%s", len(rows), filename)
        return rows
    except Exception:
        _carnatic_cache[name] = []
        return []


def get_gati_definitions():
    """5 gati subdivisions with element/guna correspondence."""
    return _load_carnatic("gati", "gati_definitions.csv")


def get_tala_families():
    """7 carnatic tala families with anga sequences."""
    return _load_carnatic("tala_families", "tala_families.csv")


def get_korvai_rules():
    """Korvai cadence rules — triple-repetition patterns."""
    return _load_carnatic("korvai", "korvai_rules.csv")


def get_sollukattu():
    """Sollukattu — rhythmic syllable counting patterns."""
    return _load_carnatic("sollukattu", "sollukattu.csv")


def gati_for_element(element: str) -> dict:
    """Map element to gati subdivision (fire→tisra, earth→catusra, etc.)."""
    for g in get_gati_definitions():
        if g.get("element_correspondence", "").lower() == element.lower():
            return g
    return {}
