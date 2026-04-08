"""
field_layers.py — Generative S-layer mapping from field state.

Takes a field_state dict (from /spine) and returns a structured
per-layer mapping that any app can consume directly.

S0 → metaphysical signal
S1 → active deity, graha, mantra, yantra
S2 → raga, tala, shruti, bols, gati
S3 → tithi, nakshatra, muhurta, dasha, transit
S4 → vastu zone, element, geometry signal
S5 → plant, herb, dosha, gem, marma, body region
S6 → practice, art, companion, codex mode
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict

_PLANT_CACHE: Dict[str, str] = {}

def _lookup_nakshatra_plant(nakshatra: str) -> str:
    """Look up canonical plant for a nakshatra from plants CSV."""
    if not _PLANT_CACHE:
        import csv
        plant_csv = Path(__file__).parent.parent / "datasets" / "plants" / "nakshatra_plants.csv"
        if plant_csv.exists():
            with plant_csv.open(encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    key = row.get("nakshatra", "").strip()
                    sanskrit = row.get("sanskrit_name", row.get("sanskrit", "")).strip()
                    english = row.get("english_name", row.get("plant", "")).strip()
                    _PLANT_CACHE[key] = sanskrit or english or key
    # Try exact match, then stripped diacritics
    if nakshatra in _PLANT_CACHE:
        return _PLANT_CACHE[nakshatra]
    # Strip IAST diacritics for lookup
    import unicodedata
    clean = unicodedata.normalize("NFKD", nakshatra).encode("ascii", "ignore").decode("ascii")
    for k, v in _PLANT_CACHE.items():
        k_clean = unicodedata.normalize("NFKD", k).encode("ascii", "ignore").decode("ascii")
        if k_clean == clean:
            return v
    return ""


# S0 paksha→signal map
_PAKSHA_SIGNAL = {
    "Śukla": "waxing · field building toward fullness · outward expression",
    "Kṛṣṇa": "waning · field contracting toward source · inward integration",
}

_ELEMENT_S0 = {
    "fire":  "radiance and will · the field burns clear",
    "water": "receptivity and flow · the field softens and receives",
    "earth": "stability and form · the field grounds and holds",
    "air":   "movement and transmission · the field disperses and connects",
    "ether": "pure space · the field rests in its own nature",
}

_GUNA_S0 = {
    "sattva": "clarity operative · witness mode available",
    "rajas":  "movement operative · action mode available",
    "tamas":  "depth operative · dissolution mode available",
}

# S4 element→vastu zone
_ELEMENT_ZONE = {
    "fire":  {"zone": "SE", "deity": "Agni", "function": "transformation and energy"},
    "water": {"zone": "NE", "deity": "Īśāna", "function": "receptivity and wisdom"},
    "earth": {"zone": "SW", "deity": "Nirṛti", "function": "stability and foundation"},
    "air":   {"zone": "NW", "deity": "Vāyu", "function": "movement and communication"},
    "ether": {"zone": "Center", "deity": "Brahmā", "function": "source and integration"},
}

# S6 guna→practice
_GUNA_PRACTICE = {
    "sattva": {"practice": "study and meditation", "art": "music and teaching", "codex_mode": "understand"},
    "rajas":  {"practice": "ritual and action", "art": "dance and craft", "codex_mode": "create"},
    "tamas":  {"practice": "rest and dissolution", "art": "silence and surrender", "codex_mode": "observe"},
}

# S6 phi→companion
_PHI_COMPANION = {
    "left":   "Shilpi",
    "center": "Bheruṇḍā",
    "right":  "Bandhu",
}


def generate_layer_mapping(spine: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate per-S-layer field mapping from a spine response.
    Returns dict keyed S0-S6, each with structured display data.
    """
    p = spine.get("panchanga", {})
    ss = spine.get("sound_state", {})
    nak = p.get("nak_data", {})
    phi_label = spine.get("phi_label", "center")

    element = (nak.get("element") or p.get("element") or "ether").lower()
    guna = (nak.get("guna") or p.get("guna") or "sattva").lower()
    paksha = p.get("paksha", "Śukla")
    nakshatra = p.get("nakshatra", "")
    tithi = p.get("tithi", "")
    vara = p.get("vara", "")
    tidx = p.get("tidx", 0)
    devi_raw = p.get("devi", {})
    # Support both dict (new) and tuple/list (legacy) format
    if isinstance(devi_raw, dict):
        devi = [devi_raw.get("name",""), devi_raw.get("symbol",""), devi_raw.get("description",""), devi_raw.get("raga","")]
    elif isinstance(devi_raw, (list, tuple)):
        devi = list(devi_raw)
    else:
        devi = [str(devi_raw)]

    # ── S0 ────────────────────────────────────────────────────
    s0 = {
        "signal": _PAKSHA_SIGNAL.get(paksha, paksha),
        "element_signal": _ELEMENT_S0.get(element, ""),
        "guna_signal": _GUNA_S0.get(guna, ""),
        "arc": round(tidx / 30.0, 3),
        "phase": "waxing" if tidx < 15 else "waning",
    }

    # ── S1 ────────────────────────────────────────────────────
    devi_name = devi[0] if devi else ""
    devi_raga = devi[3] if len(devi) > 3 else ""
    s1 = {
        "deity": nak.get("deity", ""),
        "devi": devi_name,
        "devi_raga": devi_raga,
        "graha": nak.get("graha", p.get("nak_lord", "")),
        "gana": nak.get("gana", ""),
        "shakti": nak.get("shakti", ""),
        "symbol": nak.get("symbol", ""),
        "themes": nak.get("themes", ""),
    }

    # ── S2 ────────────────────────────────────────────────────
    s2 = {
        "raga": ss.get("raga", ""),
        "raga_notes": ss.get("raga_notes", []),
        "raga_aroha": ss.get("raga_aroha", []),
        "raga_avaroha": ss.get("raga_avaroha", []),
        "raga_vadi": ss.get("raga_vadi", ""),
        "raga_rasa": ss.get("raga_rasa", ""),
        "raga_time": ss.get("raga_time", ""),
        "tala": ss.get("tala", ""),
        "tala_beats": ss.get("tala_beats", 8),
        "tala_bols": ss.get("tala_bols", []),
        "gati": ss.get("gati", "chatusra"),
        "bpm": ss.get("bpm", 72),
        "shruti_ratios": ss.get("shruti_ratios", []),
        "element_frequency": ss.get("element_frequency", 0),
        "tuning": ss.get("tuning", ""),
    }

    # ── S3 ────────────────────────────────────────────────────
    s3 = {
        "tithi": tithi,
        "tithi_num": tidx + 1,
        "paksha": paksha,
        "nakshatra": nakshatra,
        "nak_lord": p.get("nak_lord", ""),
        "vara": vara,
        "body_region": nak.get("body_region", ""),
        "dosha": nak.get("dosha", ""),
        "yoni": nak.get("yoni", ""),
        "qualities": nak.get("qualities", []),
    }

    # ── S4 ────────────────────────────────────────────────────
    entities = spine.get("entities", [])
    formations = spine.get("formations", [])
    vastu_st = spine.get("vastu_state", {})
    vs_summary = vastu_st.get("activation_summary", {})

    if vs_summary:
        # Prefer vastu_engine output
        dom_zone = vs_summary.get("dominant_zone", "Center")
        s4 = {
            "active_zone": dom_zone,
            "zone_deity": _ELEMENT_ZONE.get(
                vs_summary.get("dominant_element", element),
                _ELEMENT_ZONE["ether"])["deity"],
            "zone_function": _ELEMENT_ZONE.get(
                vs_summary.get("dominant_element", element),
                _ELEMENT_ZONE["ether"])["function"],
            "element": element,
            "guna": guna,
            "formation_count": vs_summary.get("formation_count", len(formations)),
            "top_formation": vs_summary.get("top_formation", ""),
            "entity_count": len(entities),
            "theta": spine.get("theta"),
            "phi": spine.get("phi"),
            "zone_weights": vastu_st.get("zone_weights", {}),
            "active_cells_preview": vastu_st.get("active_cells", [])[:6],
        }
    else:
        # Fallback: element → zone (original logic)
        zone_info = _ELEMENT_ZONE.get(element, _ELEMENT_ZONE["ether"])
        s4 = {
            "active_zone": zone_info["zone"],
            "zone_deity": zone_info["deity"],
            "zone_function": zone_info["function"],
            "element": element,
            "guna": guna,
            "formation_count": len(formations),
            "top_formation": formations[0]["name"] if formations else "",
            "entity_count": len(entities),
            "theta": spine.get("theta"),
            "phi": spine.get("phi"),
        }

    # ── S5 ────────────────────────────────────────────────────
    # Look up nakshatra plant from plant CSV if not in nak_data
    nak_plant = nak.get("plant", "")
    if not nak_plant and nakshatra:
        nak_plant = _lookup_nakshatra_plant(nakshatra)
    s5 = {
        "nakshatra_plant": nak_plant,
        "body_region": nak.get("body_region", ""),
        "dosha": nak.get("dosha", ""),
        "element": element,
        "guna": guna,
        "metal": nak.get("metal", ""),
        "mantra": nak.get("mantra", ""),
    }

    # ── S6 ────────────────────────────────────────────────────
    practice_info = _GUNA_PRACTICE.get(guna, _GUNA_PRACTICE["sattva"])
    companion = _PHI_COMPANION.get(phi_label, "Bandhu")
    s6 = {
        "practice": practice_info["practice"],
        "art": practice_info["art"],
        "codex_mode": practice_info["codex_mode"],
        "companion": companion,
        "nakshatra": nakshatra,
        "vara": vara,
        "dasha_lord": "",  # filled by kernel from dasha data
    }

    return {
        "S0": s0,
        "S1": s1,
        "S2": s2,
        "S3": s3,
        "S4": s4,
        "S5": s5,
        "S6": s6,
    }
