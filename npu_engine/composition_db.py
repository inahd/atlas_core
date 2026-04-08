"""
composition_db.py — Field-state driven composition selection.

Reads field state → scores each composition → returns ranked playlist.
No synthesis. No audio. Pure relational scoring.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

_HERE = Path(__file__).resolve().parent
_DEFAULT_PATH = _HERE.parent / "datasets" / "compositions.json"

_CACHE: List[Dict] = []


def load_compositions(path: Optional[str] = None) -> List[Dict]:
    """Load compositions from JSON. Cached after first call."""
    global _CACHE
    if _CACHE:
        return _CACHE
    p = Path(path) if path else _DEFAULT_PATH
    if not p.exists():
        return []
    _CACHE = json.loads(p.read_text(encoding="utf-8"))
    return _CACHE


def _normalize(s: str) -> str:
    """Lowercase, strip diacritics roughly for matching."""
    return (s.lower()
            .replace("ā", "a").replace("ī", "i").replace("ū", "u")
            .replace("ṛ", "r").replace("ṣ", "sh").replace("ś", "sh")
            .replace("ṇ", "n").replace("ṅ", "n").replace("ṭ", "t")
            .replace("ḍ", "d").replace("ñ", "n").replace("ḥ", "h")
            .replace("ṃ", "m").replace(" ", "_"))


def _raga_match(comp_raga: str, comp_aliases: list, field_raga: str) -> bool:
    """Check if composition raga matches field raga (fuzzy)."""
    if not field_raga or comp_raga == "any":
        return False
    fr = _normalize(field_raga)
    if _normalize(comp_raga) == fr:
        return True
    for alias in comp_aliases:
        if _normalize(alias) == fr:
            return True
    return False


def _time_match(comp_times: list, field_muhurta: str) -> bool:
    """Check if composition time matches current muhurta."""
    if not field_muhurta or "any" in comp_times:
        return "any" in comp_times
    fm = _normalize(field_muhurta)
    for t in comp_times:
        if _normalize(t) == fm or _normalize(t) in fm or fm in _normalize(t):
            return True
    return False


def _vara_match(comp_varas: list, field_vara: str) -> bool:
    """Check if composition vara matches."""
    if "any" in comp_varas:
        return False  # "any" means no bonus, not a match
    if not field_vara:
        return False
    fv = _normalize(field_vara).split("_")[0]  # strip symbol
    for v in comp_varas:
        if _normalize(v).startswith(fv):
            return True
    return False


def score_composition(comp: Dict, field_state: Dict,
                      natal: Optional[Dict] = None) -> float:
    """Score a composition against current field state.

    Returns 0.0–1.0 with explanation reasons list.
    """
    score = 0.0
    reasons = []

    p = field_state.get("panchanga", {})
    ss = field_state.get("sound_state", field_state)
    field_raga = ss.get("raga") or field_state.get("raga", "")
    field_element = (p.get("element") or "ether").lower()
    field_guna = (p.get("guna") or "sattva").lower()
    field_vara = p.get("vara", "")
    field_nak = p.get("nakshatra", "")
    field_devi = ""
    devi_list = p.get("devi", [])
    if isinstance(devi_list, list) and devi_list:
        field_devi = devi_list[0] if isinstance(devi_list[0], str) else ""

    # Muhurta name
    muhurta = field_state.get("muhurta", {})
    if isinstance(muhurta, dict):
        muhurta_name = muhurta.get("name", "")
    else:
        muhurta_name = ""

    # Observance
    obs = field_state.get("observance")
    obs_type = ""
    if isinstance(obs, dict):
        obs_type = obs.get("type", "")
    elif isinstance(obs, list) and obs:
        obs_type = obs[0].get("type", "")

    # ── Rāga match: +0.30 ──
    if _raga_match(comp.get("raga", ""), comp.get("raga_aliases", []), field_raga):
        score += 0.30
        reasons.append(f"raga match: {field_raga}")

    # ── Deity match: +0.25 ──
    comp_deity = _normalize(comp.get("deity", ""))
    if field_devi and comp_deity and (_normalize(field_devi) in comp_deity or comp_deity in _normalize(field_devi)):
        score += 0.25
        reasons.append(f"deity: {comp.get('deity')} (field devī)")

    # ── Rasa match: +0.15 ──
    comp_rasas = [r.lower() for r in comp.get("rasa", [])]
    field_rasa = (ss.get("rasa_primary") or ss.get("raga_rasa") or field_guna).lower()
    if field_rasa in comp_rasas:
        score += 0.15
        reasons.append(f"rasa: {field_rasa}")

    # ── Time match: +0.10 ──
    if _time_match(comp.get("time", []), muhurta_name):
        score += 0.10
        reasons.append(f"time: {muhurta_name}")

    # ── Observance: +0.15 or -0.50 penalty ──
    comp_obs = [o.lower() for o in comp.get("observance", ["any"])]
    if obs_type:
        ot = obs_type.lower()
        if ot in comp_obs:
            score += 0.15
            reasons.append(f"observance: {obs_type}")
        elif ot == "ekadashi":
            # Ekādaśī: only nirguṇa, Viṣṇu, or "any" compositions
            comp_deity_raw = comp.get("deity", "").lower()
            if comp_deity_raw not in ("nirguṇa", "viṣṇu", "viththala", "rāma", "all-saints") and "any" not in comp_obs:
                score -= 0.50
                reasons.append("penalty: wrong deity for ekādaśī")

    # ── Element match: +0.05 ──
    if comp.get("element", "").lower() == field_element:
        score += 0.05
        reasons.append(f"element: {field_element}")

    # ── Vara match: +0.05 ──
    if _vara_match(comp.get("vara", []), field_vara):
        score += 0.05
        reasons.append(f"vara: {field_vara}")

    # ── Nakṣatra deity match: +0.10 ──
    comp_nak_deities = [_normalize(n) for n in comp.get("nakshatra_deity", [])]
    if field_nak and _normalize(field_nak) in comp_nak_deities:
        score += 0.10
        reasons.append(f"nakshatra: {field_nak}")

    # ── Natal match: +0.15 ──
    if natal:
        natal_nak = natal.get("janma_nakshatra", "")
        if natal_nak:
            natal_nak_n = _normalize(natal_nak)
            if natal_nak_n in comp_nak_deities:
                score += 0.15
                reasons.append(f"natal nakshatra: {natal_nak}")

    return max(0.0, min(1.0, score)), reasons


def get_playlist(field_state: Dict, natal: Optional[Dict] = None,
                 limit: int = 5) -> List[Dict]:
    """Score all compositions, return top `limit` with scores and reasons."""
    comps = load_compositions()
    scored = []
    for comp in comps:
        s, reasons = score_composition(comp, field_state, natal)
        scored.append({
            "composition": comp,
            "score": round(s, 3),
            "reasons": reasons,
        })
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:limit]


def get_mantra_for_now(field_state: Dict) -> Optional[Dict]:
    """Return single highest-scoring mantra/stotra for current moment.

    Hard rules:
      - Ekādaśī → Viṣṇu Sahasranāma
      - Pūrṇimā → Lalitā Sahasranāma
      - Dawn/Brahma Mūhūrta → Gāyatrī
    """
    comps = load_compositions()
    mantras = [c for c in comps if c.get("type") in ("mantra", "stotra")]
    if not mantras:
        return None

    # Observance overrides
    obs = field_state.get("observance")
    obs_type = ""
    if isinstance(obs, dict):
        obs_type = obs.get("type", "")
    elif isinstance(obs, list) and obs:
        obs_type = obs[0].get("type", "")

    if obs_type.lower() == "ekadashi":
        for m in mantras:
            if "vishnu_sahasranama" in m["id"]:
                return {"composition": m, "score": 1.0, "reasons": ["ekādaśī → Viṣṇu Sahasranāma"]}

    p = field_state.get("panchanga", {})
    tidx = p.get("tidx", 0)
    if tidx == 14:  # Pūrṇimā
        for m in mantras:
            if "lalita_sahasranama" in m["id"]:
                return {"composition": m, "score": 1.0, "reasons": ["pūrṇimā → Lalitā Sahasranāma"]}

    # Dawn
    muhurta = field_state.get("muhurta", {})
    mu_name = muhurta.get("name", "") if isinstance(muhurta, dict) else ""
    if "brahma" in mu_name.lower() or "dawn" in mu_name.lower() or "pratah" in mu_name.lower():
        for m in mantras:
            if "gayatri" in m["id"]:
                return {"composition": m, "score": 1.0, "reasons": ["dawn → Gāyatrī Mantra"]}

    # Score remaining mantras normally
    scored = []
    for m in mantras:
        s, reasons = score_composition(m, field_state)
        scored.append({"composition": m, "score": round(s, 3), "reasons": reasons})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[0] if scored else None
