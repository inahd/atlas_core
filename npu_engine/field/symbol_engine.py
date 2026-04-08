"""
symbol_engine.py — Vedic cosmological mapping for symbols and emoji.

Aggregates symbol data from:
  datasets/symbols/emoji_vedic_map.csv  — emoji → varna/graha/element/layer
  datasets/cosmology/graha_master.csv   — graha symbols
  datasets/cosmology/nitya_devi_master.csv — devi bija + devanagari
  datasets/astro/nakshatra_master.csv   — nakshatra glyph + emoji
  datasets/iching/hexagrams.csv         — hexagram symbols
  datasets/iching/trigrams.csv          — trigram symbols

Pattern follows ui_vastu_engine.py.
"""

import csv
import io
import os
from typing import Dict, List, Optional

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))

_EMOJI_CSV = os.path.join(_ROOT, "datasets", "symbols", "emoji_vedic_map.csv")
_AUTO_CSV = os.path.join(_ROOT, "datasets", "symbols", "emoji_auto_mapped.csv")
_GRAHA_CSV = os.path.join(_ROOT, "datasets", "cosmology", "graha_master.csv")
_DEVI_CSV = os.path.join(_ROOT, "datasets", "cosmology", "nitya_devi_master.csv")
_NAK_CSV = os.path.join(_ROOT, "datasets", "astro", "nakshatra_master.csv")
_HEX_CSV = os.path.join(_ROOT, "datasets", "iching", "hexagrams.csv")
_TRI_CSV = os.path.join(_ROOT, "datasets", "iching", "trigrams.csv")

_cache: Dict[str, list] = {}
_symbol_index: Optional[Dict[str, dict]] = None


def _load(key, path):
    if key in _cache:
        return _cache[key]
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read().lstrip()
        rows = list(csv.DictReader(io.StringIO(text)))
        _cache[key] = rows
        return rows
    except Exception:
        _cache[key] = []
        return []


def _build_index():
    """Build unified symbol lookup: emoji/symbol → vedic metadata."""
    global _symbol_index
    if _symbol_index is not None:
        return _symbol_index
    _symbol_index = {}

    # Emoji vedic map (primary)
    for r in _load("emoji", _EMOJI_CSV):
        emoji = r.get("emoji", "").strip()
        if emoji:
            _symbol_index[emoji] = {
                "emoji": emoji,
                "name": r.get("name", ""),
                "varna": r.get("varna", ""),
                "graha": r.get("graha", ""),
                "element": r.get("element", ""),
                "layer": r.get("layer", ""),
                "nakshatra": r.get("nakshatra", ""),
                "ashtakala": r.get("ashtakala", ""),
                "vastu_zone": r.get("vastu_zone", ""),
                "rasa": r.get("rasa", ""),
                "dosha": r.get("dosha", ""),
                "notes": r.get("notes", ""),
                "attestation": r.get("attestation", "SYNTHESIS"),
                "source": "emoji_vedic_map",
            }

    # Auto-mapped full emoji set (lower priority — don't overwrite manual)
    for r in _load("auto", _AUTO_CSV):
        emoji = r.get("emoji", "").strip()
        if emoji and emoji not in _symbol_index:
            _symbol_index[emoji] = {
                "emoji": emoji,
                "name": r.get("unicode_name", ""),
                "varna": r.get("varna", ""),
                "graha": r.get("graha", ""),
                "element": r.get("element", ""),
                "layer": r.get("layer", ""),
                "nakshatra": r.get("nakshatra", ""),
                "rasa": r.get("rasa", ""),
                "dosha": r.get("dosha", ""),
                "vastu_zone": r.get("vastu_zone", ""),
                "confidence": float(r.get("confidence", 0.3)),
                "attestation": r.get("attestation", "SYNTHESIS"),
                "source": "auto_mapped",
            }

    # Graha symbols
    for r in _load("graha", _GRAHA_CSV):
        for col in ("symbol", "emoji"):
            sym = r.get(col, "").strip()
            if sym and sym not in _symbol_index:
                _symbol_index[sym] = {
                    "emoji": sym,
                    "name": r.get("graha", ""),
                    "varna": "universal",
                    "graha": r.get("graha", "").lower(),
                    "element": r.get("element", ""),
                    "layer": "S1",
                    "attestation": "OBSERVED",
                    "source": "graha_master",
                }

    # Nakshatra glyphs
    for r in _load("nak", _NAK_CSV):
        for col in ("glyph", "emoji"):
            sym = r.get(col, "").strip()
            if sym and sym not in _symbol_index:
                _symbol_index[sym] = {
                    "emoji": sym,
                    "name": r.get("nakshatra", ""),
                    "varna": "universal",
                    "element": r.get("element", ""),
                    "layer": "S3",
                    "nakshatra": r.get("nakshatra", ""),
                    "attestation": "OBSERVED",
                    "source": "nakshatra_master",
                }

    # Devi bija as symbols
    for r in _load("devi", _DEVI_CSV):
        bija = r.get("bija", "").strip()
        deva = r.get("name_devanagari", "").strip()
        for sym in (bija, deva):
            if sym and sym not in _symbol_index:
                _symbol_index[sym] = {
                    "emoji": sym,
                    "name": r.get("name_iast", ""),
                    "varna": "brahmana",
                    "graha": r.get("graha", "").lower(),
                    "element": r.get("element", ""),
                    "layer": "S1",
                    "rasa": r.get("rasa", ""),
                    "attestation": "OBSERVED",
                    "source": "nitya_devi_master",
                }

    # I Ching hexagram + trigram symbols
    for r in _load("hex", _HEX_CSV):
        sym = r.get("symbol", "").strip()
        if sym:
            _symbol_index[sym] = {
                "emoji": sym,
                "name": r.get("name_english", ""),
                "element": r.get("element_lower", ""),
                "layer": "S3",
                "attestation": "OBSERVED",
                "source": "hexagrams",
            }
    for r in _load("tri", _TRI_CSV):
        sym = r.get("symbol", "").strip()
        if sym:
            _symbol_index[sym] = {
                "emoji": sym,
                "name": r.get("name_english", ""),
                "element": r.get("element", ""),
                "layer": "S3",
                "attestation": "OBSERVED",
                "source": "trigrams",
            }

    return _symbol_index


# ══════════════════════════════════════════════════════════
# PUBLIC API
# ══════════════════════════════════════════════════════════

def lookup_symbol(symbol: str) -> dict:
    """Look up a single symbol/emoji. Returns empty dict if not found."""
    idx = _build_index()
    return dict(idx.get(symbol.strip(), {}))


def lookup_by_graha(graha: str) -> List[dict]:
    """All symbols ruled by a graha."""
    idx = _build_index()
    g = graha.lower()
    return [v for v in idx.values() if v.get("graha", "").lower() == g]


def lookup_by_element(element: str) -> List[dict]:
    """All symbols of an element."""
    idx = _build_index()
    e = element.lower()
    return [v for v in idx.values() if v.get("element", "").lower() == e]


def lookup_by_layer(layer: str) -> List[dict]:
    """All symbols in an S-layer."""
    idx = _build_index()
    return [v for v in idx.values() if v.get("layer", "") == layer]


def lookup_by_varna(varna: str) -> List[dict]:
    """All symbols of a varna."""
    idx = _build_index()
    return [v for v in idx.values() if v.get("varna", "") == varna]


def field_symbols(field_state: dict) -> List[dict]:
    """Symbols most coherent with current field. Returns top 10."""
    idx = _build_index()
    p5 = field_state.get("panchanga", {})
    nak = p5.get("nakshatra", "").lower()
    element = p5.get("element", "").lower()
    hora = field_state.get("hora", {}).get("hora_lord", "").lower()

    scored = []
    for sym, data in idx.items():
        score = 0.0
        if data.get("element", "").lower() == element:
            score += 0.3
        if data.get("graha", "").lower() == hora:
            score += 0.25
        if nak and data.get("nakshatra", "").lower().replace("_", " ") in nak.replace("_", " "):
            score += 0.35
        if score > 0:
            scored.append({**data, "field_score": round(score, 3)})

    scored.sort(key=lambda x: -x["field_score"])
    return scored[:10]


def stats() -> dict:
    """Symbol database statistics."""
    idx = _build_index()
    sources = {}
    for v in idx.values():
        s = v.get("source", "unknown")
        sources[s] = sources.get(s, 0) + 1
    return {"total_symbols": len(idx), "by_source": sources}
