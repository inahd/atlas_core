"""
tala_graph.py — Queries tala/vibhag/beat/bol nodes from graph.

Merges hardcoded Hindustani tala data with CSV-loaded Carnatic data
from datasets/carnatic/ via graph_seed_data.py.
"""

from typing import Dict, List, Optional, NamedTuple
from .graph_seed_data import (
    TALA_STRUCTURES, BOL_PROPERTIES,
    get_tala_master_index, get_35_talas_index,
    get_sollukattu_index, get_tala_families_index,
)


class TalaStructure(NamedTuple):
    name: str
    beats: int
    vibhag: List[int]
    vibhag_gravity: List[float]
    sam: int
    khali: int
    theka: List[str]
    rasa_affinity: Dict[str, float]


class BolProperties(NamedTuple):
    name: str
    weight: float
    hand: str
    resonance: str
    rasa: List[str]


# ── lazy cache for CSV-built structures ──────────────────────
_csv_tala_cache: Dict[str, dict] = {}
_csv_loaded = False


def _ensure_csv_talas():
    """Lazy-load all CSV talas into _csv_tala_cache once."""
    global _csv_loaded
    if _csv_loaded:
        return
    _csv_loaded = True

    master_by_id, master_by_name = get_tala_master_index()
    talas35_by_id, talas35_by_fj = get_35_talas_index()
    families_by_id = get_tala_families_index()

    for tala_id, row in master_by_id.items():
        name = row.get("name_iast", "")
        try:
            beat_count = int(row.get("beat_count", 0))
        except (ValueError, TypeError):
            beat_count = 0
        if beat_count == 0:
            continue

        # Parse anga_structure "4+2+4" -> vibhag list
        anga_str = row.get("anga_structure", "")
        vibhag = []
        for part in anga_str.split("+"):
            try:
                vibhag.append(int(part.strip()))
            except ValueError:
                pass
        if not vibhag:
            vibhag = [beat_count]

        # Gravity: sam=1.0, rest evenly spaced
        vibhag_gravity = [1.0] + [round(0.5 / max(len(vibhag) - 1, 1) * (len(vibhag) - i), 2)
                                   for i in range(1, len(vibhag))]

        # Theka/sollukattu from 35_talas or sollukattu
        theka = []
        # strip the "tala_" prefix to match 35_talas tala_id format
        short_id = tala_id.replace("tala_", "")
        t35 = talas35_by_id.get(short_id, {})
        sollu_str = t35.get("sollukattu", "")
        if not sollu_str:
            # Fallback: try short_id_catusra as default jati
            t35 = talas35_by_id.get(f"{short_id}_catusra", {})
            sollu_str = t35.get("sollukattu", "")
        if sollu_str:
            theka = sollu_str.strip().split()

        # Rasa from tala_master
        rasa = row.get("rasa", "")
        rasa_affinity = {}
        if rasa:
            rasa_affinity[rasa] = 0.9

        # Enrich rasa from family graha_correspondence
        family_name = name.lower()
        fam = families_by_id.get(family_name, {})
        graha = fam.get("graha_correspondence", "")
        if graha:
            # graha→rasa mapping (traditional)
            _graha_rasa = {
                "Surya": "vira", "Chandra": "shringara", "Mangala": "raudra",
                "Budha": "hasya", "Guru": "shanta", "Shukra": "shringara",
                "Shani": "karuna", "Rahu": "bhayanaka", "Ketu": "adbhuta",
            }
            graha_rasa = _graha_rasa.get(graha)
            if graha_rasa and graha_rasa not in rasa_affinity:
                rasa_affinity[graha_rasa] = 0.7

        entry = {
            "beats": beat_count,
            "vibhag": vibhag,
            "vibhag_gravity": vibhag_gravity,
            "sam": 0,
            "khali": vibhag[0] if len(vibhag) > 1 else 0,
            "theka": theka,
            "rasa_affinity": rasa_affinity,
            "tradition": row.get("tradition", "carnatic"),
            "element": row.get("element", ""),
            "guna": row.get("guna", ""),
            "deity": row.get("deity", ""),
        }

        # Index by multiple keys for flexible lookup
        _csv_tala_cache[tala_id] = entry
        _csv_tala_cache[short_id] = entry
        # Also by lowercase name + jati for convenience
        jati = ""
        if "_" in short_id:
            parts = short_id.rsplit("_", 1)
            if len(parts) == 2:
                jati = parts[1]
        name_lower = name.lower()
        name_jati_key = f"{name_lower}_{jati}" if jati else name_lower
        _csv_tala_cache[name_jati_key] = entry
        # Default: first occurrence by name (already handled by master_by_name order)
        if name_lower not in _csv_tala_cache:
            _csv_tala_cache[name_lower] = entry


def _resolve_tala(tala_name: str) -> dict:
    """Look up tala by name: hardcoded first, then CSV, then fallback to Adi."""
    # Direct match in hardcoded
    if tala_name in TALA_STRUCTURES:
        return TALA_STRUCTURES[tala_name]

    # Try lowercase in hardcoded
    for k, v in TALA_STRUCTURES.items():
        if k.lower() == tala_name.lower():
            return v

    # Load CSV talas and try
    _ensure_csv_talas()
    key = tala_name.lower()
    if key in _csv_tala_cache:
        return _csv_tala_cache[key]

    # Try with tala_ prefix
    if f"tala_{key}" in _csv_tala_cache:
        return _csv_tala_cache[f"tala_{key}"]

    # Fallback
    return TALA_STRUCTURES["Adi"]


def get_tala(tala_name: str) -> TalaStructure:
    """Return full tala structure from graph."""
    t = _resolve_tala(tala_name)
    return TalaStructure(
        name=tala_name,
        beats=t["beats"],
        vibhag=t["vibhag"],
        vibhag_gravity=t["vibhag_gravity"],
        sam=t["sam"],
        khali=t["khali"],
        theka=t["theka"],
        rasa_affinity=t.get("rasa_affinity", {}),
    )


def get_theka(tala_name: str, rasa: str = "") -> List[str]:
    """Return theka bol sequence, optionally weighted by rasa affinity."""
    t = _resolve_tala(tala_name)
    return list(t["theka"])


# ── lazy cache for CSV bol data ──────────────────────────────
_csv_bol_cache: Dict[str, dict] = {}
_csv_bol_loaded = False


def _ensure_csv_bols():
    """Lazy-load sollukattu syllables as bol properties."""
    global _csv_bol_loaded
    if _csv_bol_loaded:
        return
    _csv_bol_loaded = True

    sollu_index = get_sollukattu_index()
    for jati, row in sollu_index.items():
        syllables = row.get("syllables", "").split()
        for syl in syllables:
            syl_lower = syl.lower()
            if syl_lower not in BOL_PROPERTIES and syl_lower not in _csv_bol_cache:
                _csv_bol_cache[syl_lower] = {
                    "weight": 0.4,
                    "hand": "right_open",
                    "resonance": "syllabic",
                    "rasa": ["shanta"],
                }


def get_bol_properties(bol: str) -> BolProperties:
    """Return properties of a bol stroke."""
    # Check hardcoded first
    p = BOL_PROPERTIES.get(bol)
    if p:
        return BolProperties(name=bol, weight=p["weight"], hand=p["hand"],
                             resonance=p["resonance"], rasa=p["rasa"])

    # Check CSV-loaded sollukattu
    _ensure_csv_bols()
    p = _csv_bol_cache.get(bol.lower())
    if p:
        return BolProperties(name=bol, weight=p["weight"], hand=p["hand"],
                             resonance=p["resonance"], rasa=p["rasa"])

    # Fallback
    return BolProperties(name=bol, weight=0.3, hand="right_open",
                         resonance="dry", rasa=["shanta"])


def get_rasa_tala_affinity(rasa: str) -> List[str]:
    """Return talas ranked by rasa fit (best first).

    Merges hardcoded Hindustani talas with CSV Carnatic talas.
    """
    scored = []
    seen = set()

    # Hardcoded talas
    for name, t in TALA_STRUCTURES.items():
        aff = t.get("rasa_affinity", {}).get(rasa, 0.3)
        scored.append((name, aff))
        seen.add(name.lower())

    # CSV talas
    _ensure_csv_talas()
    for key, t in _csv_tala_cache.items():
        if key in seen:
            continue
        seen.add(key)
        aff = t.get("rasa_affinity", {}).get(rasa, 0.3)
        name_display = key.replace("_", " ").title()
        scored.append((name_display, aff))

    scored.sort(key=lambda x: -x[1])
    return [name for name, _ in scored]


def beat_to_vibhag(beat: int, tala: TalaStructure) -> int:
    """Return which vibhag a beat belongs to."""
    pos = beat % tala.beats
    acc = 0
    for i, v in enumerate(tala.vibhag):
        acc += v
        if pos < acc:
            return i
    return len(tala.vibhag) - 1
