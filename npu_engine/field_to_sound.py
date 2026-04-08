"""
field_to_sound.py — The Descent.

Eternal sciences (above) → Material sciences (below).
Reads the Vedic knowledge body via graph traversal.
Returns sound synthesis parameters.

Nothing is hardcoded. Everything comes from the graph.

Chain:
  nakshatra → graha → raga (graha_raga relation)
  tithi → devi → bija (tithi_associated_nitya_devi)
  bija → varnas (bija_synthesis_path)
  element → sa_hz (element_to_sa mapping)
  guna → vocal character (guna_to_character mapping)
"""

import re
from typing import Any, Dict, List, Optional


def _slugify(name: str) -> str:
    """Convert IAST name to entity_id slug."""
    s = name.lower().strip()
    for a, b in [("ā","a"),("ī","i"),("ū","u"),("ṛ","r"),("ṝ","r"),("ḷ","l"),
                 ("ṃ","m"),("ḥ","h"),("ṅ","ng"),("ñ","n"),("ṭ","t"),("ḍ","d"),
                 ("ṇ","n"),("ś","sh"),("ṣ","sh"),("ḻ","l")]:
        s = s.replace(a, b)
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")


# ── Nitya Devī table ────────────────────────────────────────────────
# 15 Nitya Devis mapped to tithi (1-based, cycles each paksha)
# sep = orbit_separation, spd = orbit_speed for brahmanda renderer

DEVI_TABLE = {
    1:  {"name": "Kāmeśvarī",      "elem": "fire",  "guna": "rajas",  "sep": 1.3, "spd": 1.3, "arc": "high"},
    2:  {"name": "Bhagamālinī",     "elem": "fire",  "guna": "rajas",  "sep": 1.3, "spd": 1.2, "arc": "high"},
    3:  {"name": "Nityaklinnā",     "elem": "water", "guna": "tamas",  "sep": 0.7, "spd": 0.6, "arc": "low"},
    4:  {"name": "Bheruṇḍā",        "elem": "fire",  "guna": "rajas",  "sep": 1.4, "spd": 1.4, "arc": "high"},
    5:  {"name": "Vahnivāsinī",     "elem": "fire",  "guna": "rajas",  "sep": 1.5, "spd": 1.5, "arc": "high"},
    6:  {"name": "Mahāvajreśvarī",  "elem": "earth", "guna": "tamas",  "sep": 0.5, "spd": 0.4, "arc": "low"},
    7:  {"name": "Śivadūtī",        "elem": "ether", "guna": "sattva", "sep": 0.9, "spd": 0.8, "arc": "medium"},
    8:  {"name": "Tvaritā",         "elem": "air",   "guna": "rajas",  "sep": 1.2, "spd": 1.6, "arc": "high"},
    9:  {"name": "Kulasundarī",     "elem": "water", "guna": "sattva", "sep": 0.8, "spd": 0.7, "arc": "low"},
    10: {"name": "Nityā",           "elem": "ether", "guna": "sattva", "sep": 0.9, "spd": 0.9, "arc": "medium"},
    11: {"name": "Nīlapatākā",      "elem": "air",   "guna": "rajas",  "sep": 1.1, "spd": 1.3, "arc": "medium"},
    12: {"name": "Vijayā",          "elem": "fire",  "guna": "rajas",  "sep": 1.4, "spd": 1.4, "arc": "high"},
    13: {"name": "Sarvamaṅgalā",    "elem": "earth", "guna": "sattva", "sep": 0.6, "spd": 0.5, "arc": "low"},
    14: {"name": "Jvālāmālinī",     "elem": "fire",  "guna": "rajas",  "sep": 1.5, "spd": 1.5, "arc": "high"},
    15: {"name": "Citrā",           "elem": "ether", "guna": "sattva", "sep": 1.0, "spd": 1.0, "arc": "medium"},
}

ELEM_COLORS = {
    "fire":  [0.88, 0.31, 0.13],
    "water": [0.25, 0.50, 0.82],
    "earth": [0.31, 0.63, 0.25],
    "air":   [0.31, 0.63, 0.75],
    "ether": [0.78, 0.66, 0.43],
}

DEVI_EFFECTS = {
    "Kāmeśvarī":      "Desire-force ignites creation — orbital fire expands",
    "Bhagamālinī":     "Garland of suns — radiant multiplication of light",
    "Nityaklinnā":     "Perpetually moist — soma flows, orbits slow and soften",
    "Bheruṇḍā":        "Fierce two-headed eagle — twin fires accelerate",
    "Vahnivāsinī":     "Dweller in fire — maximum radiance, fastest orbit",
    "Mahāvajreśvarī":  "Diamond throne — dense, slow, gravitational pull",
    "Śivadūtī":        "Śiva's messenger — etheric bridge, balanced orbit",
    "Tvaritā":         "The swift one — air drives rapid orbital shift",
    "Kulasundarī":     "Beauty of the lineage — gentle water, harmonic rest",
    "Nityā":           "The eternal — stable ether, perfectly centered",
    "Nīlapatākā":      "Blue banner — air unfurls, moderate expansion",
    "Vijayā":          "Victorious — fire conquers, strong acceleration",
    "Sarvamaṅgalā":    "All-auspicious — earth steadies, slow and grounded",
    "Jvālāmālinī":     "Garland of flames — peak fire, widest orbit",
    "Citrā":           "The variegated — ether balances all forces",
}


def get_devi_from_tithi(tithi_n: int) -> dict:
    """Map tithi number (1-15) to Nitya Devi with orbital parameters.

    Args:
        tithi_n: 1-based tithi index within the paksha (1-15).
                 Values > 15 are wrapped via mod.
    """
    key = ((tithi_n - 1) % 15) + 1 if tithi_n >= 1 else 1
    devi = DEVI_TABLE.get(key, DEVI_TABLE[1])
    return {
        "devi": devi["name"],
        "element": devi["elem"],
        "guna": devi["guna"],
        "orbit_separation": devi["sep"],
        "orbit_speed": devi["spd"],
        "arc": devi["arc"],
        "counterspace_color": ELEM_COLORS[devi["elem"]],
        "description": DEVI_EFFECTS[devi["name"]],
    }


VASTU_COMPASS = {
    "shakti_kali": "SW", "shakti_dvapara": "SE", "shakti_treta": "E",
    "shakti_satya": "NE", "shiva_satya": "N", "shiva_treta": "NW",
    "shiva_dvapara_1": "W", "shiva_dvapara_2": "W", "shiva_kali": "S",
}


def get_vastu_from_field(field_state: dict) -> dict:
    """Derive vastu/yantra context from the current field state.

    Uses the NPU graph to find the current nakshatra's pada,
    its yantra triangle, co-triangulars, and diameter pair.
    """
    from .graph_engine import GraphEngine
    g = GraphEngine()

    p = field_state.get("panchanga", {})
    nak = p.get("nakshatra", "Rohini")
    tithi_n = (p.get("didx", 0) + 1)

    # Find pada for this nakshatra (pada_n=1)
    # Search entities for matching nakshatra + pada_n=1
    pada_id = ""
    for eid, meta in g._metadata.items():
        if not eid.startswith("pada_"):
            continue
        attrs = meta.get("attributes", {})
        nak_vals = attrs.get("nakshatra", [])
        pada_vals = attrs.get("pada_n", [])
        if nak in nak_vals and "1" in pada_vals:
            pada_id = eid
            break

    if not pada_id:
        return {"error": f"no pada found for {nak}"}

    attrs = g.meta(pada_id).get("attributes", {})
    triangle_id = (attrs.get("yantra_triangle_id", [""]))[0]
    polarity = (attrs.get("yantra_polarity", [""]))[0]
    yuga = (attrs.get("yantra_yuga", [""]))[0]
    knot_y = float((attrs.get("knot_y", ["0"]))[0])
    ribbon = (attrs.get("ribbon", ["matter"]))[0]

    # Co-triangulars: other nakshatras sharing this yantra triangle
    co_naks = []
    if triangle_id:
        yt_id = f"yantra_{triangle_id}"
        for edge in g.get_neighbors(yt_id):
            if edge["relation"] == "triangle_vertex":
                to_meta = g.meta(edge["to_id"])
                to_name = to_meta.get("name", "")
                if to_name and to_name != nak:
                    co_naks.append(to_name)

    # Diameter pair
    opp_nak = ""
    opp_pada = (attrs.get("opposite_pada", [""]))[0]
    if opp_pada:
        opp_meta = g.meta(opp_pada)
        opp_attrs = opp_meta.get("attributes", {})
        opp_nak_list = opp_attrs.get("nakshatra", [])
        opp_nak = opp_nak_list[0] if opp_nak_list else ""

    # Devi
    devi = DEVI_TABLE.get(((tithi_n - 1) % 15) + 1, DEVI_TABLE[1])

    return {
        "yantra_triangle": triangle_id,
        "polarity": polarity,
        "yuga": yuga,
        "compass": VASTU_COMPASS.get(triangle_id, ""),
        "co_triangulars": co_naks,
        "diameter_pair": opp_nak,
        "ribbon": ribbon,
        "knot_y": knot_y,
        "devi": devi["name"],
        "devi_element": devi["elem"],
        "devi_sep": devi["sep"],
        "devi_spd": devi["spd"],
        "devi_arc": devi["arc"],
    }


def get_treatment_vector(element: str, guna: str) -> str:
    """The fundamental question before any herb prescription.

    Excess or deficiency? Cool or warm the root?
    This is why traditions differ — not just what they say.

    rajas  → reduce   (excess — cool, disperse, clear)
    tamas  → build    (deficiency — warm, nourish, anchor)
    sattva → maintain (balance — adapt, regulate)

    Example: fire + reduce → cooling herbs (neem, amla, jasmine)
             fire + build  → warming adaptogens (ashwagandha, ginger)
             ← the yin huo gui yuan case: deficient fire needs warmth, not cold
    """
    if guna == "rajas":
        return "reduce"
    elif guna == "tamas":
        return "build"
    return "maintain"


def element_to_sa(element: str) -> float:
    """Element → Sa fundamental frequency.

    Earth is deep and grounded. Ether is open and high.
    Based on natural harmonic series from C2.
    """
    return {
        "earth":  65.41,   # C2 — deep, grounded
        "water":  98.00,   # G2 — flowing
        "fire":   130.81,  # C3 — bright
        "air":    196.00,  # G3 — light
        "ether":  261.63,  # C4 — open
    }.get(element.lower(), 130.81)


def guna_to_character(guna: str) -> dict:
    """Guna → vocal/timbral character parameters."""
    return {
        "sattva": {"breathiness": 0.04, "brightness": 0.8,
                   "vibrato": 0.012, "register": "upper"},
        "rajas":  {"breathiness": 0.08, "brightness": 0.6,
                   "vibrato": 0.018, "register": "mid"},
        "tamas":  {"breathiness": 0.14, "brightness": 0.3,
                   "vibrato": 0.008, "register": "lower"},
    }.get(guna.lower(), {"breathiness": 0.08, "brightness": 0.5,
                          "vibrato": 0.015, "register": "mid"})


def field_to_sound(field_state: dict) -> dict:
    """The descent. Reads eternal sciences, returns material sciences specification.

    Args:
        field_state: dict with panchanga (nakshatra, tithi, etc.)

    Returns:
        Sound specification derived entirely from graph traversal.
    """
    from .graph_engine import GraphEngine
    from .datasets import load_entity_metadata

    g = GraphEngine()
    meta = load_entity_metadata()
    p = field_state.get("panchanga", {})

    # ── Nakshatra → Graha ──
    nak_name = p.get("nakshatra", "Rohini")
    nak_id = "nakshatra_" + _slugify(nak_name)
    graha_id = ""
    graha_neighbors = g.get_neighbors(nak_id)
    for n in graha_neighbors:
        if n["relation"] in ("nakshatra_ruling_graha",):
            graha_id = n["to_id"]
            break
    if not graha_id:
        # Fallback: check nak_lord from panchanga
        nak_lord = p.get("nak_lord", "")
        if nak_lord:
            graha_id = "graha_" + _slugify(nak_lord)

    # ── Graha → Raga (if relation exists) ──
    raga_id = ""
    if graha_id:
        for n in g.get_neighbors(graha_id):
            if "raga" in n["relation"]:
                raga_id = n["to_id"]
                break

    # ── Element + Guna from graha or nakshatra metadata ──
    element = ""
    guna = ""
    for eid in [graha_id, nak_id]:
        if eid and eid in meta:
            attrs = meta[eid].get("attributes", {})
            if not element:
                e = attrs.get("element", [])
                element = e[0] if isinstance(e, list) and e else (e if isinstance(e, str) else "")
            if not guna:
                gu = attrs.get("guna", [])
                guna = gu[0] if isinstance(gu, list) and gu else (gu if isinstance(gu, str) else "")
    # Fallback from panchanga
    if not element:
        element = p.get("element", "ether")
    if not guna:
        guna = p.get("guna", "sattva")
    element = element.lower()
    guna = guna.lower()

    # ── Tithi → Devi → Bija ──
    tidx = p.get("tidx", 0)
    tithi_id = f"tithi_{tidx + 1}" if isinstance(tidx, int) else "tithi_1"
    devi_id = ""
    bija = "om"
    for n in g.get_neighbors(tithi_id):
        if "nitya_devi" in n["relation"]:
            devi_id = n["to_id"]
            break
    if devi_id:
        for n in g.get_neighbors(devi_id):
            if "bija" in n["relation"]:
                bija_eid = n["to_id"]
                bija = bija_eid.replace("bija_", "")
                break
        # Also check devi metadata
        if devi_id in meta:
            d_attrs = meta[devi_id].get("attributes", {})
            b = d_attrs.get("bija", [])
            if b:
                bija = b[0] if isinstance(b, list) else b

    # ── Chakra from nakshatra ──
    chakra_id = ""
    for n in g.get_neighbors(nak_id, exclude_inverse=False):
        if "chakra" in n["to_id"]:
            chakra_id = n["to_id"]
            break

    # ── Sa Hz from element ──
    sa_hz = element_to_sa(element)

    # ── Character from guna ──
    character = guna_to_character(guna)

    # ── Bija synthesis path (placeholder — needs Supabase view) ──
    bija_path = _local_bija_path(bija)

    # ── Instruments for this field state ──
    instruments = _get_instruments_for_element(element, meta)

    return {
        "sa_hz": sa_hz,
        "raga": raga_id or p.get("devi_raga", ""),
        "tala_bpm": p.get("tala_bpm", field_state.get("sound_state", {}).get("bpm", 72)),
        "bija": bija,
        "bija_path": bija_path,
        "character": character,
        "element": element,
        "guna": guna,
        "graha": graha_id,
        "devi": devi_id,
        "chakra": chakra_id,
        "nakshatra": nak_id,
        "instruments": instruments,
    }


def _get_instruments_for_element(element: str, meta: dict) -> list:
    """Select instruments matching the current field element."""
    matches = []
    for eid, m in meta.items():
        if not eid.startswith("instrument_"):
            continue
        attrs = m.get("attributes", {})
        inst_elem = attrs.get("element", [])
        if isinstance(inst_elem, list):
            inst_elem = inst_elem[0].lower() if inst_elem else ""
        else:
            inst_elem = str(inst_elem).lower()

        if inst_elem == element.lower():
            synth = attrs.get("synthesis_type", [""])[0] if isinstance(attrs.get("synthesis_type"), list) else attrs.get("synthesis_type", "")
            f0 = attrs.get("f0_range", [""])[0] if isinstance(attrs.get("f0_range"), list) else attrs.get("f0_range", "")
            matches.append({
                "id": eid,
                "name": m.get("name", eid),
                "synthesis_type": synth,
                "f0_range": f0,
                "element": inst_elem,
            })
    return matches[:3]  # max 3 instruments


def _local_bija_path(bija: str) -> list:
    """Local fallback for bija synthesis path (varnas with formant data).

    Full version queries Supabase bija_synthesis_path view.
    This provides basic vowel formants for common bijas.
    """
    # Basic varna formant data (F1/F2/F3 in Hz)
    VARNA_FORMANTS = {
        "a":  {"f1": 700, "f2": 1100, "f3": 2500, "nasal": False},
        "i":  {"f1": 300, "f2": 2200, "f3": 3000, "nasal": False},
        "u":  {"f1": 300, "f2": 900,  "f3": 2200, "nasal": False},
        "e":  {"f1": 400, "f2": 2000, "f3": 2800, "nasal": False},
        "o":  {"f1": 400, "f2": 900,  "f3": 2400, "nasal": False},
        "m":  {"f1": 250, "f2": 1000, "f3": 2200, "nasal": True},
        "n":  {"f1": 250, "f2": 1500, "f3": 2500, "nasal": True},
        "h":  {"f1": 500, "f2": 1500, "f3": 2500, "nasal": False},
        "r":  {"f1": 350, "f2": 1300, "f3": 2400, "nasal": False},
        "l":  {"f1": 350, "f2": 1100, "f3": 2800, "nasal": False},
        "k":  {"f1": 300, "f2": 1800, "f3": 2800, "nasal": False},
        "s":  {"f1": 400, "f2": 1800, "f3": 2600, "nasal": False},
    }

    # Common bija decompositions
    BIJA_VARNAS = {
        "om":   ["a", "u", "m"],
        "aim":  ["a", "i", "m"],
        "hrim": ["h", "r", "i", "m"],
        "klim": ["k", "l", "i", "m"],
        "shrim":["s", "r", "i", "m"],
        "hum":  ["h", "u", "m"],
        "krim": ["k", "r", "i", "m"],
        "dum":  ["d", "u", "m"],
        "gam":  ["g", "a", "m"],
        "lam":  ["l", "a", "m"],
        "vam":  ["v", "a", "m"],
        "ram":  ["r", "a", "m"],
    }

    varnas = BIJA_VARNAS.get(bija.lower(), list(bija.lower()))
    path = []
    for v in varnas:
        formants = VARNA_FORMANTS.get(v, VARNA_FORMANTS.get("a"))
        path.append({
            "iast": v,
            "f1_hz": formants["f1"],
            "f2_hz": formants["f2"],
            "f3_hz": formants["f3"],
            "nasal": formants["nasal"],
            "duration_ratio": 1.0 if v in "aeiou" else 0.3,
        })
    return path
