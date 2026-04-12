"""
chandas_engine.py

Domain: S2/S3 — Sound & Rhythm
Purpose: Derives current chandas (metre) context from field state using
         the chandas dataset layer (metres_forms.csv, metre_correspondence_matrix.csv).

Atlas Relations:
  nakshatra → element → metre correspondence (via metre_correspondence_matrix)
  time_of_day → metre preference (via metres_forms time_of_day column)
  field_state.panchanga → primary_metre, syllables_per_pada, cadence_pattern
"""

import csv
import os
from typing import Any, Dict, List, Optional, Tuple

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
_DATA = os.path.join(_ROOT, "datasets", "chandas")

# ── Caches ────────────────────────────────────────────────

_metres: Optional[Dict[str, dict]] = None
_correspondences: Optional[List[dict]] = None


def _load_csv(path: str) -> List[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _load_metres() -> Dict[str, dict]:
    global _metres
    if _metres is None:
        rows = _load_csv(os.path.join(_DATA, "metres_forms.csv"))
        _metres = {}
        for r in rows:
            _metres[r["metre_id"]] = r
    return _metres


def _load_correspondences() -> List[dict]:
    global _correspondences
    if _correspondences is None:
        _correspondences = _load_csv(os.path.join(_DATA, "metre_correspondence_matrix.csv"))
    return _correspondences


# ── Nakshatra element groups ──────────────────────────────

_NAKSHATRA_ELEMENT_GROUPS = {
    "fire nakshatras": [
        "ashwini", "bharani", "krittika", "magha", "purva phalguni",
        "uttara phalguni", "mula", "purva ashadha", "uttara ashadha",
    ],
    "earth nakshatras": [
        "rohini", "mrigashira", "hasta", "chitra", "shravana",
        "dhanishtha", "dhanistha", "uttara bhadrapada",
    ],
    "water nakshatras": [
        "ardra", "pushya", "ashlesha", "anuradha", "jyeshtha",
        "purva bhadrapada", "revati",
    ],
    "hasta family": [
        "hasta", "ashwini", "savitri",
    ],
    "center / ether": [
        "swati", "vishakha", "shatabhisha",
    ],
}


def _strip_diacritics(s: str) -> str:
    """Normalize IAST diacritics for fuzzy matching."""
    table = str.maketrans("āīūṛṝḷṃḥṅñṭḍṇśṣ", "aiurllmhnntdnss")
    return s.lower().translate(table)


def _nakshatra_matches_overlay(nakshatra: str, overlay: str) -> bool:
    if not nakshatra or not overlay:
        return False
    nak_norm = _strip_diacritics(nakshatra.strip())
    overlay_lower = overlay.lower().strip()
    if nak_norm in _strip_diacritics(overlay_lower):
        return True
    # Look up the overlay group
    for key, naks in _NAKSHATRA_ELEMENT_GROUPS.items():
        if key.lower() == overlay_lower:
            for gn in naks:
                if gn in nak_norm or nak_norm in gn:
                    return True
            break
    return False


# ── Time of day estimation ────────────────────────────────

def _estimate_time_of_day(field_state: dict) -> str:
    """Estimate time of day from field state muhurta or hour."""
    muhurta = field_state.get("muhurta", {})
    if isinstance(muhurta, dict):
        name = muhurta.get("name", "").lower()
        if "brahma" in name or "dawn" in name or "pratah" in name:
            return "dawn"
        if "madhyahna" in name or "midday" in name:
            return "midday"
        if "sayahna" in name or "evening" in name or "sandhya" in name:
            return "evening"
        if "nisha" in name or "night" in name:
            return "night_or_liminal"
    return ""


# ── Rasa extraction ──────────────────────────────────────

def _extract_rasa(field_state: dict) -> str:
    panchanga = field_state.get("panchanga", {})
    rasa = panchanga.get("rasa", "")
    if rasa:
        return rasa.lower().strip()
    sound_state = field_state.get("sound_state", {})
    if isinstance(sound_state, dict):
        r = sound_state.get("rasa", "")
        if r:
            return r.lower().strip()
    svarodaya = field_state.get("svarodaya", {})
    if isinstance(svarodaya, dict):
        r = svarodaya.get("rasa", "")
        if r:
            return r.lower().strip()
    devi = panchanga.get("devi", panchanga.get("nitya_devi", ""))
    if isinstance(devi, dict):
        r = devi.get("rasa", "")
        if r:
            return r.lower().strip()
    return ""


# ── Helpers ──────────────────────────────────────────────

def _parse_syllables(val: str) -> Optional[int]:
    try:
        return int(val)
    except (ValueError, TypeError):
        return None


_SYLLABLE_CHARACTER = {
    range(1, 8):   "rapid",
    range(8, 10):  "flowing",
    range(10, 13): "vigorous",
    range(13, 20): "stately",
}


def _rhythmic_character(syllables: int) -> str:
    for rng, label in _SYLLABLE_CHARACTER.items():
        if syllables in rng:
            return label
    return "stately"


def _time_key_matches(time_key: str, metre_time: str) -> bool:
    if not time_key or not metre_time:
        return False
    tk = time_key.lower().strip()
    mt = metre_time.lower().strip()
    if tk == mt:
        return True
    if tk in mt or mt in tk:
        return True
    return False


def _rasa_matches(field_rasa: str, metre_rasa: str) -> bool:
    if not field_rasa or not metre_rasa:
        return False
    fr = field_rasa.lower().strip()
    mr = metre_rasa.lower().strip()
    return fr in mr or mr in fr


# ── Multi-factor scoring ─────────────────────────────────

_W_NAKSHATRA = 0.30
_W_ELEMENT = 0.25
_W_TIME = 0.25
_W_RASA = 0.20


def derive_optimal_metre(field_state: dict) -> List[dict]:
    """Score each metre across 4 weighted factors, return top 3."""
    metres = _load_metres()
    corrs = _load_correspondences()

    panchanga = field_state.get("panchanga", {})
    nakshatra = panchanga.get("nakshatra", "")
    element = (panchanga.get("element") or "ether").lower().strip()
    time_key = _estimate_time_of_day(field_state)
    field_rasa = _extract_rasa(field_state)

    corr_by_metre: Dict[str, dict] = {}
    for row in corrs:
        mid = row.get("metre_id", "")
        if mid not in corr_by_metre:
            corr_by_metre[mid] = {
                "nakshatra_overlay": set(),
                "vastu_element": set(),
            }
        nak = row.get("nakshatra_overlay", "").strip()
        if nak and nak.lower() != "unspecified":
            corr_by_metre[mid]["nakshatra_overlay"].add(nak)
        ve = row.get("vastu_element", "").strip()
        if ve and ve.lower() != "unspecified":
            corr_by_metre[mid]["vastu_element"].add(ve.lower())

    scored: List[Tuple[float, str]] = []

    for mid, m in metres.items():
        score = 0.0
        cm = corr_by_metre.get(mid, {"nakshatra_overlay": set(), "vastu_element": set()})

        for overlay in cm["nakshatra_overlay"]:
            if _nakshatra_matches_overlay(nakshatra, overlay):
                score += _W_NAKSHATRA
                break

        # Element: check correspondence matrix first, then metres_forms fallback
        if element in cm["vastu_element"]:
            score += _W_ELEMENT
        elif element == (m.get("element_correspondence", "").lower().strip()):
            score += _W_ELEMENT

        metre_time = m.get("time_of_day", "")
        if _time_key_matches(time_key, metre_time):
            score += _W_TIME

        metre_rasa = m.get("rasa_primary", "")
        if _rasa_matches(field_rasa, metre_rasa):
            score += _W_RASA

        scored.append((score, mid))

    scored.sort(key=lambda x: -x[0])

    results = []
    for score, mid in scored[:3]:
        m = metres[mid]
        syl = _parse_syllables(m.get("syllables_per_pada", ""))
        results.append({
            "name_iast": m.get("name_iast", mid),
            "syllables_per_pada": syl if syl else m.get("syllables_per_pada", ""),
            "cadence_pattern": m.get("cadence_pattern", ""),
            "rasa_primary": m.get("rasa_primary", ""),
            "deity_correspondence": m.get("deity_correspondence", ""),
            "score": round(score, 2),
        })

    return results


# ── Public API ────────────────────────────────────────────

def derive_chandas(field_state: dict) -> dict:
    """
    Given current field_state, return chandas (metre) context.

    Returns structured primary_metre dict, alternative_metres from
    multi-factor scoring, field_summary, plus backward-compatible
    top-level keys (primary_metre as string, syllables_per_pada,
    cadence_pattern) for downstream engines like phrase_engine.
    """
    panchanga = field_state.get("panchanga", {})
    element = (panchanga.get("element") or "ether").lower()
    nakshatra = panchanga.get("nakshatra", "")
    time_key = _estimate_time_of_day(field_state)

    metres = _load_metres()
    alternatives = derive_optimal_metre(field_state)

    if alternatives and alternatives[0]["score"] > 0:
        best_name = alternatives[0]["name_iast"]
        best_id = None
        for mid, m in metres.items():
            if m.get("name_iast") == best_name:
                best_id = mid
                break
        if not best_id:
            best_id = "ved_anustubh"
    else:
        best_id = "ved_anustubh"

    metre_rec = metres.get(best_id, metres.get("ved_anustubh", {}))
    syllables = _parse_syllables(metre_rec.get("syllables_per_pada", "8")) or 8

    primary_metre_dict = {
        "name": metre_rec.get("name_iast", "Anuṣṭubh"),
        "syllables": syllables,
        "cadence_pattern": metre_rec.get("cadence_pattern", ""),
        "deity": metre_rec.get("deity_correspondence", ""),
        "direction": metre_rec.get("direction_correspondence", ""),
        "element": metre_rec.get("element_correspondence", element),
    }

    field_summary = " · ".join(filter(None, [
        nakshatra or "—",
        element,
        time_key or "—",
    ]))

    result = {
        "primary_metre": metre_rec.get("name_iast", "Anuṣṭubh"),
        "primary_metre_id": best_id,
        "primary_metre_detail": primary_metre_dict,
        "alternative_metres": alternatives,
        "field_summary": field_summary,
        "syllables_per_pada": syllables,
        "padas_per_verse": metre_rec.get("padas_per_verse", "4"),
        "cadence_pattern": metre_rec.get("cadence_pattern", ""),
        "rasa_primary": metre_rec.get("rasa_primary", "śānta"),
        "deity": metre_rec.get("deity_correspondence", ""),
        "element": metre_rec.get("element_correspondence", element),
        "rhythmic_character": _rhythmic_character(syllables),
        "source": "chandas_engine",
    }

    return result
