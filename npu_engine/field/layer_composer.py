"""
layer_composer.py — Self-assembling S-layer engine.

Each S-layer draws from its dataset manifest,
filters by current field state, and returns
structured sections ready for rendering.

LLM assembly (Qwen3) is optional — the core value
is the structured dataset query.
"""

import csv
import io
import logging
import os
import time
from typing import Any, Dict, List, Optional

log = logging.getLogger(__name__)

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
_DATASETS = os.path.join(_ROOT, "datasets")

# ── Cache ──────────────────────────────────────────────────

_csv_cache: Dict[str, List[dict]] = {}
_layer_cache: Dict[str, dict] = {}  # keyed by "layer_id:nak:tithi:devi"


def _load_csv(relpath: str) -> List[dict]:
    """Load a CSV file relative to datasets/, with caching."""
    if relpath in _csv_cache:
        return _csv_cache[relpath]
    path = os.path.join(_DATASETS, relpath)
    if not os.path.exists(path):
        return []
    try:
        with open(path, newline="", encoding="utf-8") as f:
            raw = f.read().lstrip("\ufeff")
            rows = list(csv.DictReader(io.StringIO(raw)))
        _csv_cache[relpath] = rows
        return rows
    except Exception as e:
        log.warning("Failed to load %s: %s", relpath, e)
        return []


# ── Layer dataset manifests ────────────────────────────────

LAYER_DATASETS: Dict[str, List[str]] = {
    "s0": [
        "cosmology/ashtakala.csv",
        "cosmology/vraja_forests.csv",
        "cosmology/nitya_devi_master.csv",
        "ontology/vaishnava_tattva.csv",
        "ontology/rasa_siddhanta.csv",
        "ontology/parampara.csv",
    ],
    "s1": [
        "cosmology/deity_attributes.csv",
        "cosmology/deity_master.csv",
        "cosmology/deity_domains.csv",
        "cosmology/deity_vahana_extended.csv",
        "cosmology/nitya_devi_mapping.csv",
        "cosmology/nitya_devi_master.csv",
        "gandharva/graha_bija.csv",
        "gandharva/graha_raga_chords.csv",
    ],
    "s2": [
        "sound/raga_master.csv",
        "sound/raga_phrase_library.csv",
        "sound/gamak_properties.csv",
        "gandharva/bija_master.csv",
        "gandharva/instruments.csv",
        "gandharva/raga_therapeutic.csv",
        "carnatic/tala_master.csv",
    ],
    "s3": [
        "astro/nakshatra_canonical.csv",
        "astro/tithi_master.csv",
        "astro/tithi_deities.csv",
        "cosmology/deity_attributes.csv",
        "cosmology/nitya_devi_mapping.csv",
        "chandas/metres_forms.csv",
    ],
    "s4": [
        "vastu/pada_topology.csv",
        "vastu/vastu_pada_grid.csv",
        "vastu/vastu_zones.csv",
        "vastu/element_geometry.csv",
        "vastu/geometry_archetypes.csv",
    ],
    "s5": [
        "ayurveda/dhatu_herb_matrix.csv",
        "plants/sacred_plants.csv",
        "plants/nakshatra_plants.csv",
        "species/nakshatra_species.csv",
        "yoga/asana_core.csv",
        "yoga/nakshatra_body_map.csv",
        "marma/marma_field.csv",
    ],
    "s6": [
        "ritual/vaishnava_calendar.csv",
        "ritual/plant_ritual.csv",
        "cosmology/daily_program.csv",
        "cosmology/bhajan_corpus.csv",
        "morphogenesis/doctrine_of_signatures.csv",
    ],
}

# ── Field state helpers ────────────────────────────────────


def _get_nakshatra(field_state: dict) -> str:
    pa = field_state.get("panchanga", {})
    nak = pa.get("nakshatra", "")
    if isinstance(nak, dict):
        nak = nak.get("name", "")
    return nak


def _get_nakshatra_key(field_state: dict) -> str:
    """Get the ASCII-friendly nakshatra key for CSV matching."""
    pa = field_state.get("panchanga", {})
    nd = pa.get("nak_data", {})
    if isinstance(nd, dict) and nd.get("name_key"):
        return nd["name_key"]
    return _get_nakshatra(field_state)


def _get_tithi(field_state: dict) -> str:
    pa = field_state.get("panchanga", {})
    t = pa.get("tithi", "")
    if isinstance(t, dict):
        t = t.get("name", "")
    return t


def _get_devi(field_state: dict) -> str:
    pa = field_state.get("panchanga", {})
    d = pa.get("devi", "")
    if isinstance(d, dict):
        d = d.get("name", "")
    return d


def _get_tidx(field_state: dict) -> int:
    pa = field_state.get("panchanga", {})
    return int(pa.get("didx", pa.get("tidx", 0)) or 0)


def _get_raga(field_state: dict) -> str:
    ss = field_state.get("sound_state", {})
    return ss.get("raga", "")


def _normalize(s: str) -> str:
    """Strip diacritics for fuzzy matching."""
    table = str.maketrans("āīūṛṝḷṃḥṅñṭḍṇśṣ", "aiurllmhnntdnss")
    return s.lower().translate(table).strip()


def _row_matches(row: dict, key: str, value: str) -> bool:
    """Check if any column matching 'key' pattern contains 'value'."""
    if not value:
        return False
    val_norm = _normalize(value)
    for col, cell in row.items():
        if key in col.lower():
            if val_norm in _normalize(str(cell)):
                return True
    return False


# ── Dataset query ──────────────────────────────────────────


def query_datasets_for_field(
    layer_id: str, field_state: dict
) -> Dict[str, List[dict]]:
    """Load each dataset in the layer manifest, filter by field state."""
    manifest = LAYER_DATASETS.get(layer_id, [])
    nak = _get_nakshatra(field_state)
    nak_key = _get_nakshatra_key(field_state)
    tithi = _get_tithi(field_state)
    devi = _get_devi(field_state)
    tidx = _get_tidx(field_state)
    raga = _get_raga(field_state)

    result: Dict[str, List[dict]] = {}

    for csv_path in manifest:
        name = os.path.splitext(os.path.basename(csv_path))[0]
        rows = _load_csv(csv_path)
        if not rows:
            continue

        # Determine the best filter for this dataset
        matched = []
        cols_lower = [c.lower() for c in rows[0].keys()] if rows else []
        has_nak = any("nakshatra" in c for c in cols_lower)
        has_tithi = any("tithi" in c for c in cols_lower)
        has_deity = any("deity" in c or "devi" in c for c in cols_lower)
        has_raga = any("raga" in c for c in cols_lower)

        # Determine if any standard filter column exists
        has_tithi_id = any("tithi_id" in c for c in cols_lower)
        can_filter = has_nak or has_tithi or has_tithi_id or has_deity or has_raga

        if not can_filter:
            # Reference dataset — include all rows (capped)
            matched = rows[:20]
        else:
            for row in rows:
                # Exact tithi_id match (highest priority for devi mappings)
                if has_tithi_id and tidx:
                    tid = row.get("tithi_id", "")
                    if tid and str(tidx) == str(tid):
                        matched.append(row)
                        continue

                # Nakshatra match
                if has_nak and (nak or nak_key):
                    if _row_matches(row, "nakshatra", nak) or _row_matches(row, "nakshatra", nak_key):
                        matched.append(row)
                        continue

                # Tithi name match
                if has_tithi and tithi:
                    if _row_matches(row, "tithi", tithi):
                        matched.append(row)
                        continue

                # Deity/devi match (exact normalize, not substring)
                if has_deity and devi:
                    devi_norm = _normalize(devi)
                    for col, cell in row.items():
                        if ("deity" in col.lower() or "devi" in col.lower()):
                            if _normalize(str(cell)) == devi_norm:
                                matched.append(row)
                                break
                    else:
                        continue
                    continue

                # Raga match
                if has_raga and raga:
                    if _row_matches(row, "raga", raga):
                        matched.append(row)
                        continue

        result[name] = matched

    return result


# ── Section assemblers (per-layer) ─────────────────────────


def _current_ashtakala_period() -> int:
    """Determine ashtakala period (1-8) from current hour."""
    from datetime import datetime
    h = datetime.now().hour + datetime.now().minute / 60.0
    # 8 periods of ~3h each starting at 3:36am
    boundaries = [3.6, 6.0, 8.4, 10.8, 15.6, 18.0, 20.4, 22.8]
    for i, b in enumerate(boundaries):
        if h < b:
            return i + 1 if i > 0 else 8
    return 8


def _assemble_s0(data: Dict[str, List[dict]], field_state: dict) -> List[dict]:
    """Goloka · ashtakala · tattva."""
    sections = []

    # Find current ashtakala period from all rows
    all_ak = _load_csv("cosmology/ashtakala.csv")
    period_num = _current_ashtakala_period()
    ak_row = None
    for row in all_ak:
        if str(row.get("period", "")) == str(period_num):
            ak_row = row
            break
    if ak_row is None and all_ak:
        ak_row = all_ak[0]

    if ak_row:
        sections.append({
            "title": "ASHTAKALA",
            "content": {
                "period": ak_row.get("name", ""),
                "time": f"{ak_row.get('time_start', '')} – {ak_row.get('time_end', '')}",
                "activity": ak_row.get("activity", ""),
                "raga": ak_row.get("raga", ""),
                "forest": ak_row.get("forest", ""),
                "sakhi": ak_row.get("sakhi_lead", ""),
            },
        })

    # Find matching vraja forest by ashtakala period
    all_forests = _load_csv("cosmology/vraja_forests.csv")
    for f in all_forests:
        ap = str(f.get("ashtakala_period", ""))
        if str(period_num) in ap.replace("_and_", ",").replace("-", ",").split(","):
            sections.append({
                "title": "VRAJA FOREST",
                "content": {
                    "name": f.get("name", f.get("sanskrit", "")),
                    "lila": f.get("lila_type", f.get("lila", "")),
                    "season": f.get("season", ""),
                    "deity": f.get("deity", ""),
                    "element": f.get("element", ""),
                    "rasa": f.get("rasa_quality", ""),
                    "plant": f.get("key_plant", ""),
                },
            })
            break

    # Devi from nitya_devi_mapping (already filtered by tidx)
    devi_rows = data.get("nitya_devi_master", data.get("nitya_devi_mapping", []))
    if not devi_rows:
        # Direct lookup from nitya_devi_mapping
        tidx = _get_tidx(field_state)
        for row in _load_csv("cosmology/nitya_devi_mapping.csv"):
            if str(row.get("tithi_id", "")) == str(tidx):
                devi_rows = [row]
                break
    if devi_rows:
        d = devi_rows[0]
        sections.append({
            "title": "NITYA DEVI",
            "content": {
                "name": d.get("nitya_devi", d.get("name", "")),
                "color": d.get("color_hex", ""),
                "meaning": d.get("color_meaning", ""),
            },
        })

    tattva = data.get("vaishnava_tattva", [])
    if tattva:
        sections.append({
            "title": "TATTVA",
            "content": [
                {"name": t.get("tattva", t.get("name", "")),
                 "description": t.get("description", t.get("notes", ""))}
                for t in tattva[:5]
            ],
        })

    rasa = data.get("rasa_siddhanta", [])
    if rasa:
        sections.append({
            "title": "RASA",
            "content": [
                {"name": r.get("rasa", r.get("name", "")),
                 "description": r.get("description", r.get("notes", ""))}
                for r in rasa[:5]
            ],
        })

    return sections


def _assemble_s1(data: Dict[str, List[dict]], field_state: dict) -> List[dict]:
    """Archetype · Devi · deity attributes · weapons · vahana."""
    sections = []

    # Nitya Devi from mapping
    devi_map = data.get("nitya_devi_mapping", [])
    devi_master = data.get("nitya_devi_master", [])
    if devi_map:
        d = devi_map[0]
        sections.append({
            "title": "NITYA DEVI",
            "content": {
                "name": d.get("nitya_devi", ""),
                "tithi": d.get("tithi_id", ""),
                "color": d.get("color_hex", ""),
                "color_meaning": d.get("color_meaning", ""),
            },
        })
    elif devi_master:
        d = devi_master[0]
        sections.append({
            "title": "NITYA DEVI",
            "content": {
                "name": d.get("nitya_devi", d.get("name", "")),
                "color": d.get("color_hex", ""),
                "color_meaning": d.get("color_meaning", ""),
            },
        })

    # Nakshatra deity attributes (the rich one)
    attrs = data.get("deity_attributes", [])
    if attrs:
        a = attrs[0]
        weapons = [a.get(f"item_{i}", "") for i in range(1, 5)]
        weapons = [w for w in weapons if w]
        sections.append({
            "title": "NAKSHATRA DEITY",
            "content": {
                "deity": a.get("deity", ""),
                "nakshatra": a.get("nakshatra", ""),
                "weapons": weapons,
                "vahana": a.get("vahana", ""),
                "mudra": a.get("mudra", ""),
                "color_body": a.get("color_body", ""),
                "color_garment": a.get("color_garment", ""),
                "direction": a.get("direction", ""),
                "gemstone": a.get("gemstone", ""),
                "metal": a.get("metal", ""),
                "time_of_day": a.get("time_of_day", ""),
                "day": a.get("day", ""),
                "mantra_bija": a.get("mantra_bija", ""),
                "shakti_name": a.get("shakti_name", ""),
                "tattva": a.get("tattva", ""),
                "rasa": a.get("rasa", ""),
            },
        })

    # Deity master entry
    master = data.get("deity_master", [])
    if master:
        m = master[0]
        sections.append({
            "title": "DEITY",
            "content": {
                "name": m.get("deity", ""),
                "category": m.get("category", ""),
                "vahana": m.get("vahana", ""),
                "weapon": m.get("primary_weapon", ""),
                "graha": m.get("associated_graha", ""),
                "element": m.get("element", ""),
                "domain": m.get("domain", ""),
            },
        })

    # Deity domains
    domains = data.get("deity_domains", [])
    if domains:
        sections.append({
            "title": "DOMAINS",
            "content": [
                {"deity": d.get("deity", ""), "domain": d.get("domain", ""),
                 "element": d.get("element", "")}
                for d in domains
            ],
        })

    # Vahana
    vahana = data.get("deity_vahana_extended", [])
    if vahana:
        v = vahana[0]
        sections.append({
            "title": "VAHANA",
            "content": {
                "deity": v.get("deity", ""),
                "vahana": v.get("vahana", ""),
                "symbolism": v.get("symbolism", ""),
            },
        })

    # Graha bija
    bija = data.get("graha_bija", [])
    if bija:
        sections.append({
            "title": "GRAHA BIJA",
            "content": [
                {"graha": b.get("graha", b.get("deity", "")),
                 "bija": b.get("bija", b.get("mantra_bija", ""))}
                for b in bija[:3]
            ],
        })

    # Graha raga chords
    chords = data.get("graha_raga_chords", [])
    if chords:
        sections.append({
            "title": "GRAHA RAGA",
            "content": [
                {"graha": c.get("graha", ""), "raga": c.get("raga", ""),
                 "chord": c.get("chord", "")}
                for c in chords[:3]
            ],
        })

    return sections


def _assemble_s3(data: Dict[str, List[dict]], field_state: dict) -> List[dict]:
    """Kala · nakshatra · tithi · panchanga."""
    sections = []

    # Nakshatra canonical
    nak = data.get("nakshatra_canonical", [])
    if nak:
        n = nak[0]
        sections.append({
            "title": "NAKSHATRA",
            "content": {
                "name": n.get("nakshatra", ""),
                "deity": n.get("deity", ""),
                "graha": n.get("graha", ""),
                "element": n.get("element", ""),
                "guna": n.get("guna", ""),
                "gana": n.get("gana", ""),
                "dosha": n.get("dosha", ""),
                "symbol": n.get("symbol", ""),
                "shakti": n.get("shakti", ""),
                "themes": n.get("themes", ""),
                "gemstone": n.get("gemstone", ""),
                "tree": n.get("tree", ""),
                "plant": n.get("plant", ""),
                "yoni_animal": n.get("yoni_animal", ""),
                "direction": n.get("direction", ""),
                "color": n.get("color_hex", ""),
            },
        })

    # Tithi
    tithi_m = data.get("tithi_master", [])
    if tithi_m:
        t = tithi_m[0]
        sections.append({
            "title": "TITHI",
            "content": {k: v for k, v in t.items() if v and k != "attestation_status"},
        })

    # Tithi deity
    td = data.get("tithi_deities", [])
    if td:
        d = td[0]
        sections.append({
            "title": "TITHI DEITY",
            "content": {
                "tithi": d.get("tithi", ""),
                "deity": d.get("deity", ""),
                "quality": d.get("quality", ""),
            },
        })

    # Deity attributes for this nakshatra
    attrs = data.get("deity_attributes", [])
    if attrs:
        a = attrs[0]
        weapons = [a.get(f"item_{i}", "") for i in range(1, 5)]
        weapons = [w for w in weapons if w]
        sections.append({
            "title": "NAKSHATRA DEITY PROFILE",
            "content": {
                "deity": a.get("deity", ""),
                "weapons": weapons,
                "vahana": a.get("vahana", ""),
                "mudra": a.get("mudra", ""),
                "color": a.get("color_body", ""),
                "bija": a.get("mantra_bija", ""),
                "shakti": a.get("shakti_name", ""),
                "gemstone": a.get("gemstone", ""),
                "metal": a.get("metal", ""),
            },
        })

    # Devi mapping
    devi = data.get("nitya_devi_mapping", [])
    if devi:
        d = devi[0]
        sections.append({
            "title": "NITYA DEVI",
            "content": {
                "name": d.get("nitya_devi", ""),
                "color": d.get("color_hex", ""),
                "meaning": d.get("color_meaning", ""),
            },
        })

    # Chandas
    chandas = data.get("metres_forms", [])
    if chandas:
        # Don't filter — just note the chandas data is available
        sections.append({
            "title": "CHANDAS",
            "content": {"available_metres": len(chandas)},
        })

    return sections


def _assemble_generic(data: Dict[str, List[dict]], field_state: dict) -> List[dict]:
    """Generic assembler for layers without custom logic."""
    sections = []
    for name, rows in data.items():
        if not rows:
            continue
        sections.append({
            "title": name.upper().replace("_", " "),
            "content": rows[:5] if len(rows) > 5 else rows,
        })
    return sections


_ASSEMBLERS = {
    "s0": _assemble_s0,
    "s1": _assemble_s1,
    "s3": _assemble_s3,
}


# ── Main API ───────────────────────────────────────────────


def assemble_layer(layer_id: str, field_state: dict) -> dict:
    """Assemble a layer from its datasets for the current field state.

    Returns {sections, raw_data, cached, layer_id}.
    Cached by layer_id + nakshatra + tithi + devi.
    """
    nak = _get_nakshatra(field_state)
    tithi = _get_tithi(field_state)
    devi = _get_devi(field_state)
    cache_key = f"{layer_id}:{nak}:{tithi}:{devi}"

    if cache_key in _layer_cache:
        cached = _layer_cache[cache_key]
        cached["cached"] = True
        return cached

    if layer_id not in LAYER_DATASETS:
        return {"sections": [], "raw_data": {}, "cached": False,
                "layer_id": layer_id, "error": f"Unknown layer: {layer_id}"}

    t0 = time.time()

    # Query all datasets
    raw_data = query_datasets_for_field(layer_id, field_state)

    # Assemble sections
    assembler = _ASSEMBLERS.get(layer_id, _assemble_generic)
    sections = assembler(raw_data, field_state)

    # Build raw_data summary (counts, not full rows)
    raw_summary = {k: len(v) for k, v in raw_data.items()}

    result = {
        "sections": sections,
        "raw_data": raw_data,
        "raw_summary": raw_summary,
        "cached": False,
        "layer_id": layer_id,
        "field_key": {
            "nakshatra": nak,
            "tithi": tithi,
            "devi": devi,
        },
        "duration_ms": int((time.time() - t0) * 1000),
    }

    _layer_cache[cache_key] = result
    return result


def clear_cache():
    """Clear layer and CSV caches."""
    _layer_cache.clear()
    _csv_cache.clear()
