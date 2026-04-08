"""
treasury.py — Content treasury resolver.

Field-matched sourced content from the living canon:
  ashtakaliya_lila — 8 daily pastimes
  vaishnava_personalities — saints and their tithis
  canonical_quotes — field-tagged quotes

Everything derived from current field state.
"""

import csv
import math
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
TREASURY = ROOT / "datasets"
COSMO = ROOT / "datasets" / "cosmology"

_cache = {}


def _load(name: str) -> list:
    """Load and cache a treasury CSV."""
    if name in _cache:
        return _cache[name]
    # Check treasury first, then cosmology
    for base in [TREASURY, COSMO]:
        path = base / f"{name}.csv"
        if path.exists():
            with path.open(encoding="utf-8") as f:
                _cache[name] = list(csv.DictReader(f))
                return _cache[name]
    return []


def get_current_prahar(now: datetime = None) -> dict:
    """Determine current prahar from time of day."""
    if now is None:
        now = datetime.now()
    hour = now.hour + now.minute / 60.0

    prahars = _load("ashtakaliya_lila")
    if not prahars:
        # Fallback to cosmology ashtakala
        prahars = _load("ashtakala")

    for p in prahars:
        ts = p.get("time_start", "")
        te = p.get("time_end", "")
        try:
            sh, sm = ts.replace("am","").replace("pm","").split(":")
            eh, em = te.replace("am","").replace("pm","").split(":")
            start = float(sh) + float(sm) / 60.0
            end = float(eh) + float(em) / 60.0
            # Handle AM/PM
            if "pm" in ts.lower() and start < 12:
                start += 12
            if "pm" in te.lower() and end < 12:
                end += 12
            # Handle wraparound (ratri: 22:48 to 03:36)
            if end < start:
                if hour >= start or hour < end:
                    return p
            elif start <= hour < end:
                return p
        except (ValueError, AttributeError):
            continue

    return prahars[0] if prahars else {}


def get_personalities_for_field(field_state: dict) -> list:
    """Find personalities whose appearance/disappearance matches current field."""
    p = field_state.get("panchanga", {})
    tithi = p.get("tithi", "")
    nak = p.get("nakshatra", "")
    # Normalize tithi name for matching
    tithi_lower = tithi.lower().replace("\u0101", "a").replace("\u012b", "i")

    personalities = _load("vaishnava_personalities")
    matches = []
    for per in personalities:
        reason = ""
        app_tithi = (per.get("appearance_tithi", "") or "").lower()
        app_nak = per.get("appearance_nakshatra", "") or ""
        dis_tithi = (per.get("disappearance_tithi", "") or "").lower()
        dis_nak = per.get("disappearance_nakshatra", "") or ""

        if app_tithi and app_tithi in tithi_lower:
            reason = "appearance_tithi_match"
        elif dis_tithi and dis_tithi in tithi_lower:
            reason = "disappearance_tithi_match"
        elif app_nak and app_nak.lower() in nak.lower():
            reason = "appearance_nakshatra_match"
        elif dis_nak and dis_nak.lower() in nak.lower():
            reason = "disappearance_nakshatra_match"

        if reason:
            matches.append({
                "entity_id": per.get("entity_id", ""),
                "name": per.get("name", ""),
                "iast_name": per.get("iast_name", ""),
                "reason": reason,
                "speciality": per.get("speciality", ""),
                "key_teachings": per.get("key_teachings", ""),
                "symbol": per.get("symbol", "✦"),
                "color": per.get("color", "#f0c040"),
            })
    return matches


def get_quotes_for_field(field_state: dict, limit: int = 3) -> list:
    """Find quotes matching current field state, ranked by relevance."""
    p = field_state.get("panchanga", {})
    nak = p.get("nakshatra", "")
    element = p.get("element", "")
    guna = p.get("guna", "")
    prahar = get_current_prahar()
    prahar_name = prahar.get("prahar", "").lower()

    quotes = _load("canonical_quotes")
    scored = []
    for q in quotes:
        score = 0.0
        # Tradition weight
        trad = q.get("tradition", "")
        trad_w = {"bhagavatam": 1.0, "gaudiya_commentary": 0.95,
                  "bhakti_rasamrita": 0.92, "vaishnava": 0.8}.get(trad, 0.5)
        score += trad_w * 0.3

        # Field tag matching
        nak_tags = q.get("nakshatra_tags", "")
        elem_tags = q.get("element_tags", "")
        guna_tags = q.get("guna_tags", "")
        prahar_tags = q.get("prahar_tags", "")

        if nak and nak.lower() in nak_tags.lower():
            score += 0.3
        if element and element.lower() in elem_tags.lower():
            score += 0.15
        if guna and guna.lower() in guna_tags.lower():
            score += 0.15
        if prahar_name and (prahar_name in prahar_tags.lower() or "all" in prahar_tags.lower()):
            score += 0.2

        # Confidence
        try:
            score += float(q.get("confidence", 0)) * 0.1
        except (ValueError, TypeError):
            pass

        if score > 0.3:  # threshold
            scored.append((score, q))

    scored.sort(key=lambda x: -x[0])
    return [{"score": round(s, 2), **q} for s, q in scored[:limit]]


def resolve_treasury(field_state: dict = None, prahar: str = None,
                     limit: int = 5) -> dict:
    """Resolve complete treasury for current field moment.

    Returns pastime, personalities, quotes — all field-matched.
    """
    fs = field_state or {}

    # Current prahar
    if prahar:
        prahars = _load("ashtakaliya_lila") or _load("ashtakala")
        current_prahar = next((p for p in prahars
                               if p.get("prahar", "").lower() == prahar.lower()), {})
    else:
        current_prahar = get_current_prahar()

    # Personalities present
    personalities = get_personalities_for_field(fs) if fs else []

    # Field-matched quotes
    quotes = get_quotes_for_field(fs, limit=limit) if fs else []

    return {
        "pastime": {
            "name": current_prahar.get("pastime_name", current_prahar.get("activity", "")),
            "sanskrit": current_prahar.get("pastime_sanskrit", current_prahar.get("name", "")),
            "ref": current_prahar.get("bhagavatam_ref", ""),
            "description": current_prahar.get("description", ""),
            "raga": current_prahar.get("raga_primary", current_prahar.get("raga", "")),
            "forest": current_prahar.get("forest", ""),
            "sakhi": current_prahar.get("sakhi", current_prahar.get("sakhi_lead", "")),
            "flower": current_prahar.get("flower", ""),
            "offering": current_prahar.get("offering", current_prahar.get("food", "")),
            "devi": current_prahar.get("devi", ""),
            "prahar": current_prahar.get("prahar", ""),
        },
        "personalities": personalities,
        "quotes": quotes,
    }
