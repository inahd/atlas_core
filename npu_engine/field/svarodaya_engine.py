"""
svarodaya_engine.py — Breath-cycle (svarodaya) recommendations from field state.

Connects:
    datasets/svarodaya/tithi_rules.csv   — tithi+paksha → optimal nadi
    datasets/svarodaya/vara_rules.csv    — vara → optimal nadi
    datasets/svarodaya/activity_matrix.csv — activity × nadi × element → recommendation
    datasets/svarodaya/elements.csv      — element properties
    datasets/svarodaya/nadis.csv         — nadi properties
    datasets/svarodaya/coherence_rules.csv — coherence scoring rules

Public:
    derive_svarodaya(field_state) → dict
"""

import csv
import os
import unicodedata
from typing import Dict, List, Optional

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
_DATA = os.path.join(_ROOT, "datasets", "svarodaya")

# ── Caches ────────────────────────────────────────────────

_tithi_rules: Optional[List[dict]] = None
_vara_rules: Optional[List[dict]] = None
_activity_matrix: Optional[List[dict]] = None
_elements: Optional[Dict[str, dict]] = None
_nadis: Optional[Dict[str, dict]] = None
_coherence_rules: Optional[List[dict]] = None
_activity_ontology: Optional[Dict[str, dict]] = None

# Transcendental activities — never contraindicated per Gaudiya siddhanta
# Source: Bhakti Rasamrita Sindhu 1.2; CC Antya 20.18; SB 7.5.23-24
ALWAYS_AUSPICIOUS = frozenset({
    'meditation', 'remembrance_of_supreme', 'yoga_sadhana',
    'study', 'healing', 'amiable_work', 'prosperity_ritual',
})

# Strict bhakti — absolutely never avoid
TRANSCENDENTAL = frozenset({
    'meditation', 'remembrance_of_supreme',
})


def _load_csv(path: str) -> List[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _load_tithi_rules() -> List[dict]:
    global _tithi_rules
    if _tithi_rules is None:
        _tithi_rules = _load_csv(os.path.join(_DATA, "tithi_rules.csv"))
    return _tithi_rules


def _load_vara_rules() -> List[dict]:
    global _vara_rules
    if _vara_rules is None:
        _vara_rules = _load_csv(os.path.join(_DATA, "vara_rules.csv"))
    return _vara_rules


def _load_activity_matrix() -> List[dict]:
    global _activity_matrix
    if _activity_matrix is None:
        _activity_matrix = _load_csv(os.path.join(_DATA, "activity_matrix.csv"))
    return _activity_matrix


def _load_elements() -> Dict[str, dict]:
    global _elements
    if _elements is None:
        rows = _load_csv(os.path.join(_DATA, "elements.csv"))
        _elements = {r["element_id"]: r for r in rows}
    return _elements


def _load_nadis() -> Dict[str, dict]:
    global _nadis
    if _nadis is None:
        rows = _load_csv(os.path.join(_DATA, "nadis.csv"))
        _nadis = {r["nadi_id"]: r for r in rows}
    return _nadis


def _load_coherence_rules() -> List[dict]:
    global _coherence_rules
    if _coherence_rules is None:
        _coherence_rules = _load_csv(os.path.join(_DATA, "coherence_rules.csv"))
    return _coherence_rules


# ── Helpers ───────────────────────────────────────────────

def _strip_diacritics(s: str) -> str:
    """Remove diacritics and non-letter symbols for matching."""
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if unicodedata.category(c) not in ("Mn", "So")).strip()


def _normalize_paksha(paksha: str) -> str:
    """Map kernel paksha (Śukla / Kṛṣṇa) to CSV (shukla / krishna)."""
    p = _strip_diacritics(paksha).lower()
    if p.startswith("s"):
        return "shukla"
    if p.startswith("k"):
        return "krishna"
    return p


def _normalize_vara(vara: str) -> str:
    """Map kernel vara ('Ravivāra ☀') to CSV key ('Ravivara')."""
    return _strip_diacritics(vara.split()[0]) if vara else ""


# ── Core logic ────────────────────────────────────────────

def _resolve_nadi(tithi_num: int, paksha: str, vara: str) -> tuple:
    """
    Determine optimal nadi from tithi rules (primary) with vara cross-check.
    Returns (nadi, source_text, variant_id).
    Uses the 'tithi_intro_same_both_paksha' variant as default (most attested).
    """
    pak_norm = _normalize_paksha(paksha)
    vara_norm = _normalize_vara(vara)

    # Primary: tithi rule (prefer OBSERVED attestation, intro variant)
    tithi_nadi = None
    tithi_source = ""
    for row in _load_tithi_rules():
        try:
            row_num = int(row["tithi_number"])
        except (ValueError, KeyError):
            continue
        if row_num == tithi_num and row["paksha"] == pak_norm:
            if row.get("variant_id") == "tithi_intro_same_both_paksha":
                tithi_nadi = row["optimal_nadi"]
                tithi_source = row.get("source_text", "")
                break

    # Fallback: any tithi rule for this tithi+paksha
    if tithi_nadi is None:
        for row in _load_tithi_rules():
            try:
                row_num = int(row["tithi_number"])
            except (ValueError, KeyError):
                continue
            if row_num == tithi_num and row["paksha"] == pak_norm:
                tithi_nadi = row["optimal_nadi"]
                tithi_source = row.get("source_text", "")
                break

    # Vara cross-check
    vara_nadi = None
    vara_source = ""
    for row in _load_vara_rules():
        if _normalize_vara(row.get("vara", "")) == vara_norm:
            vara_nadi = row["optimal_nadi"]
            vara_source = row.get("source_text", "")
            break

    if tithi_nadi is None and vara_nadi is None:
        return ("ida", "no matching rule found", "fallback")

    # If both agree, strong signal. If they disagree, tithi takes precedence
    # but we note the conflict.
    if tithi_nadi and vara_nadi and tithi_nadi != vara_nadi:
        source = f"tithi rule: {tithi_nadi} (primary); vara rule: {vara_nadi} (secondary conflict)"
        return (tithi_nadi, source, "tithi_vara_conflict")

    nadi = tithi_nadi or vara_nadi
    source = tithi_source or vara_source
    return (nadi, source, "tithi_vara_aligned" if (tithi_nadi and vara_nadi) else "single_source")


def _get_element_for_nadi(nadi: str) -> str:
    """Get the primary element associated with a nadi."""
    nadis = _load_nadis()
    entry = nadis.get(nadi, {})
    return entry.get("element", "ether").lower()


def _score_activities(nadi: str, element: str) -> tuple:
    """
    Filter activity_matrix for the given nadi + element.
    Returns (recommended, avoid) lists.

    Applies acintya bhedabheda filter:
      Transcendental practices (meditation, remembrance_of_supreme)
      are NEVER placed in the avoid list — they are moved to
      recommended with a note.
      Source: Bhakti Rasamrita Sindhu 1.2; CC Antya 20.18
    """
    recommended = []
    avoid = []
    for row in _load_activity_matrix():
        if row["nadi"] != nadi:
            continue
        if row["element"] != element:
            continue
        rec = row["recommendation"]
        act = row["activity"]
        if rec in ("strongly_favored", "conditionally_favored"):
            recommended.append(act)
        elif rec == "avoid":
            if act in TRANSCENDENTAL:
                # Bhedabheda: transcendental practices are always auspicious
                # Shaiva reading restricts this — not applicable to bhakti
                recommended.append(act)
            else:
                avoid.append(act)
        elif rec == "acceptable" and act in TRANSCENDENTAL:
            recommended.append(act)
    return (recommended, avoid)


def _compute_coherence(nadi: str, element: str, variant: str) -> float:
    """Compute coherence score from coherence_rules.csv."""
    best = 0.5  # default mid-range

    for rule in _load_coherence_rules():
        cond = rule.get("condition", "")
        try:
            score = float(rule.get("coherence_score", 0.5))
        except ValueError:
            continue

        # Simple condition matching
        if f"nadi={nadi}" in cond:
            if f"element={element}" in cond or f"element in" in cond:
                # Check element-in-list conditions
                if f"element in" in cond:
                    import re
                    m = re.search(r"element in \(([^)]+)\)", cond)
                    if m and element in [e.strip() for e in m.group(1).split(",")]:
                        best = max(best, score)
                elif f"element={element}" in cond:
                    best = max(best, score)
            elif "element" not in cond:
                best = max(best, score)

    # Penalize conflict between tithi and vara
    if variant == "tithi_vara_conflict":
        best *= 0.7

    # Boost alignment
    if variant == "tithi_vara_aligned":
        best = min(1.0, best * 1.1)

    return round(best, 2)


# ── Public API ────────────────────────────────────────────

def derive_svarodaya(field_state: dict) -> dict:
    """
    Given current field_state, return svarodaya recommendation.

    Reads from panchanga: tidx/didx, paksha, vara.
    Returns optimal nadi, activities, element, coherence.
    """
    panchanga = field_state.get("panchanga", {})

    # tithi_num: 1-15 within paksha
    didx = panchanga.get("didx", 0)
    tithi_num = didx + 1

    paksha = panchanga.get("paksha", "Śukla")
    vara = panchanga.get("vara", "")

    # Resolve optimal nadi
    optimal_nadi, source, variant = _resolve_nadi(tithi_num, paksha, vara)

    # Element of breath from nadi correspondence
    element = _get_element_for_nadi(optimal_nadi)

    # Activity recommendations
    recommended, avoid = _score_activities(optimal_nadi, element)

    # Coherence
    coherence = _compute_coherence(optimal_nadi, element, variant)

    # Nadi properties
    nadis = _load_nadis()
    nadi_info = nadis.get(optimal_nadi, {})

    # Element properties
    elements = _load_elements()
    element_info = elements.get(element, {})

    return {
        "optimal_nadi": optimal_nadi,
        "nadi_side": nadi_info.get("side", ""),
        "nadi_graha": nadi_info.get("graha_correspondence", ""),
        "nadi_quality": nadi_info.get("quality", ""),
        "element_of_breath": element,
        "element_duration_minutes": element_info.get("duration_minutes", ""),
        "element_sensation": element_info.get("body_sensation", ""),
        "recommended_activities": recommended,
        "avoid_activities": avoid,
        "coherence_score": coherence,
        "variant": variant,
        "source": source,
        "tithi_num": tithi_num,
        "paksha": _normalize_paksha(paksha),
        "vara": _normalize_vara(vara),
        "bhedabheda_note": (
            "Bhakti practices (harināma, smaraṇa, kīrtana) are always auspicious "
            "regardless of nāḍī state. Source: Bhakti Rasāmṛta Sindhu 1.2; "
            "CC Antya 20.18 — nāma cintāmaṇiḥ kṛṣṇaḥ"
        ),
    }
