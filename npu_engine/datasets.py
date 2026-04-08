"""
datasets.py — all-dataset loader for the NPU toroidal engine

Reads every file under datasets/, normalizes semantic entities,
derives toroidal coordinates where possible, and exposes:

  load_all_entities()        -> {entity_id: (theta, phi)}
  load_entity_metadata()     -> {entity_id: metadata}
  load_nakshatra_metadata()  -> {nakshatra_name: metadata}
  load_relations()           -> graph keyed by entity_id

YAML loading is optional. If PyYAML is unavailable, YAML files are
still inventoried but skipped for semantic extraction.
"""

from __future__ import annotations

import csv
import json
import math
import re
import unicodedata
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

try:
    import yaml  # type: ignore
except Exception:
    yaml = None


ROOT = Path(__file__).resolve().parents[1]
DATASETS_ROOT = ROOT / "datasets"


def _load_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _load_yaml(path: Path) -> Any:
    if yaml is None:
        return None
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _slug(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = value.encode("ascii", "ignore").decode("ascii")
    value = value.lower()
    replacements = {
        "purvashada": "purva_ashadha",
        "uttarashada": "uttara_ashadha",
        "purvabhadrapada": "purva_bhadrapada",
        "uttarabhadrapada": "uttara_bhadrapada",
        "purvaphalguni": "purva_phalguni",
        "uttaraphalguni": "uttara_phalguni",
        "margasirsha": "mrigashira",
        "mrigasirsha": "mrigashira",
        "dhanistha": "dhanishtha",
        "shravan": "shravana",
        "caturthi": "chaturthi",
        "caturdashi": "chaturdashi",
        "bhairavi": "bhairavi",
    }
    value = re.sub(r"[^a-z0-9]+", "_", value).strip("_")
    return replacements.get(value, value)


def _clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _title(value: str) -> str:
    return _clean(value).replace("_", " ")


def _singular(category: str) -> str:
    category = _slug(category)
    aliases = {
        "grahas": "graha",
        "nakshatras": "nakshatra",
        "rashis": "rashi",
        "gunass": "guna",
        "mahabhutas": "element",
        "directions": "direction",
        "plants": "plant",
        "rituals": "ritual",
        "texts": "text",
        "schools": "concept",
        "concepts": "concept",
        "vedic_arts": "art",
        "vedic_arts_64": "art",
        "sources": "source",
        "passages": "passage",
        "body_map": "body_region",
        "bandhu_geometry": "measure",
        "raga_therapeutic": "raga",
        "35_talas": "tala",
        "body_region_marma": "marma",
        "graha_gems": "ratna",
        "inner_deities": "vastu_deity",
        "perimeter_deities": "vastu_deity",
        "vastu_deities": "vastu_deity",
        "vastu_deity": "vastu_deity",
        "pada_topology": "pada",
        "padas": "pada",
        "yantra_triangle": "yantra_triangle",
        "deity_attr": "deity_attr",
        "deity_attributes": "deity_attr",
        "sacred_item": "sacred_item",
    }
    return aliases.get(category, category[:-1] if category.endswith("s") else category)


def _circular_mean(angle_weight_pairs: Iterable[Tuple[float, float]]) -> float:
    pairs = [(angle, weight) for angle, weight in angle_weight_pairs if weight > 0]
    if not pairs:
        return 0.0
    sin_sum = sum(weight * math.sin(angle) for angle, weight in pairs)
    cos_sum = sum(weight * math.cos(angle) for angle, weight in pairs)
    if abs(sin_sum) < 1e-12 and abs(cos_sum) < 1e-12:
        return 0.0
    return math.atan2(sin_sum, cos_sum) % (2 * math.pi)


_NAK_ORDER = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha",
    "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha",
    "Shravana", "Dhanishtha", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati",
]
NAKSHATRA_ANGLE = {
    _slug(name): (idx / len(_NAK_ORDER)) * 2 * math.pi
    for idx, name in enumerate(_NAK_ORDER)
}

_TITHI_ORDER = [
    "Pratipada", "Dvitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi",
    "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dvadashi",
    "Trayodashi", "Chaturdashi", "Purnima", "Amavasya",
]
TITHI_ANGLE = {
    _slug(name): (idx / 30.0) * 2 * math.pi for idx, name in enumerate(_TITHI_ORDER)
}

_VARA_ORDER = [
    "ravivara", "somavara", "mangalavara", "budhavara",
    "guruvara", "shukravara", "shanivara",
]
VARA_ANGLE = {name: (idx / 7.0) * 2 * math.pi for idx, name in enumerate(_VARA_ORDER)}

_ELEMENT_ORDER = ["earth", "water", "fire", "air", "ether"]
ELEMENT_ANGLE = {name: (idx / len(_ELEMENT_ORDER)) * 2 * math.pi for idx, name in enumerate(_ELEMENT_ORDER)}
ELEMENT_ALIASES = {
    "prithvi": "earth",
    "jala": "water",
    "agni": "fire",
    "vayu": "air",
    "akasha": "ether",
    "space": "ether",
}

_GUNA_ORDER = ["tamas", "rajas", "sattva"]
GUNA_ANGLE = {name: (idx / len(_GUNA_ORDER)) * 2 * math.pi for idx, name in enumerate(_GUNA_ORDER)}

_RASA_ORDER = ["shringara", "hasya", "karuna", "raudra", "vira", "bhayanaka", "bibhatsa", "adbhuta", "shanta"]
RASA_ANGLE = {name: (idx / len(_RASA_ORDER)) * 2 * math.pi for idx, name in enumerate(_RASA_ORDER)}

GRAHA_ID_ALIASES = {
    "sun": "surya",
    "surya": "surya",
    "moon": "chandra",
    "chandra": "chandra",
    "candra": "chandra",
    "mars": "mangala",
    "mangala": "mangala",
    "mercury": "budha",
    "budha": "budha",
    "jupiter": "guru",
    "guru": "guru",
    "brihaspati": "guru",
    "venus": "shukra",
    "shukra": "shukra",
    "saturn": "shani",
    "shani": "shani",
    "rahu": "rahu",
    "ketu": "ketu",
}

GRAHA_TO_VARA = {
    "surya": "ravivara",
    "chandra": "somavara",
    "mangala": "mangalavara",
    "budha": "budhavara",
    "guru": "guruvara",
    "shukra": "shukravara",
    "shani": "shanivara",
}

DOSHA_TO_ELEMENT = {
    "vata": ["air", "ether"],
    "pitta": ["fire", "water"],
    "kapha": ["water", "earth"],
}


def _build_num_to_nak() -> Dict[str, str]:
    mapping = {}
    path = DATASETS_ROOT / "nakshatra_num_to_name.csv"
    if path.exists():
        for row in _load_csv(path):
            mapping[_clean(row.get("num"))] = _clean(row.get("name"))
            mapping[_clean(row.get("key"))] = _clean(row.get("name"))
    for idx, name in enumerate(_NAK_ORDER, start=1):
        mapping[str(idx)] = name
    return mapping


NUM_TO_NAK = _build_num_to_nak()


def _build_nitya_mapping() -> Dict[str, int]:
    mapping: Dict[str, int] = {}
    path = DATASETS_ROOT / "nitya_devi_mapping.csv"
    if path.exists():
        for row in _load_csv(path):
            name = _clean(row.get("nitya_devi"))
            if not name:
                continue
            try:
                mapping[_slug(name)] = int(row.get("tithi_id", "0") or "0")
            except ValueError:
                continue
    return mapping


NITYA_DEVI_TO_TITHI = _build_nitya_mapping()


def _entity_id(category: str, name: str) -> str:
    category = _singular(category)
    slug = _slug(name)
    if category == "graha":
        slug = GRAHA_ID_ALIASES.get(slug, slug)
    return f"{category}_{slug}"


def _primary_name_from_row(row: Dict[str, Any], category: str, relpath: str) -> str:
    category = _singular(category)
    candidates = {
        "nakshatra": ["nakshatra", "name", "key"],
        "graha": ["graha", "name", "sanskrit", "planet"],
        "deity": ["deity", "name"],
        "plant": ["plant", "common_name", "name"],
        "tithi": ["tithi", "name", "sanskrit"],
        "rashi": ["rashi", "name", "sanskrit"],
        "direction": ["direction", "zone", "name"],
        "element": ["name", "element", "geometry"],
        "guna": ["name"],
        "dosha": ["name"],
        "rasa": ["name"],
        "art": ["art", "english_name", "name"],
        "body_region": ["body_region"],
        "measure": ["measure"],
        "source": ["title", "source_id"],
        "passage": ["passage_id"],
        "ritual": ["name", "ritual"],
        "concept": ["name", "id", "relation", "layer_id", "stable_id", "bhava_class"],
        "yantra": ["geometry", "symbol", "name"],
        "raga": ["raga", "name"],
        "tala": ["tala_id", "name"],
        "marma": ["marma_name", "name"],
        "ratna": ["primary_gem", "name"],
        "svara": ["name", "element_id"],
        "vastu_deity": ["deity", "name"],
        "pada": ["id"],
        "deity_attr": ["deity_id"],
        "sacred_item": ["name", "id"],
    }
    for key in candidates.get(category, []) + ["name", "id"]:
        value = _clean(row.get(key))
        if value:
            return value
    return f"{Path(relpath).stem}_{row.get('_row_index', 0)}"


def _dataset_category(relpath: str, row: Optional[Dict[str, Any]] = None) -> str:
    path = Path(relpath)
    stem = _slug(path.stem)
    parts = [_slug(part) for part in path.parts]
    if any("relation" in part for part in parts) or "relation" in stem:
        return "relation"
    if parts and parts[0] == "canonical":
        return _singular(stem)
    if "pada_topology" in stem:
        return "pada"
    if "deity_attributes" in stem:
        return "deity_attr"
    if parts and parts[0] == "astro":
        if "nakshatra" in stem:
            return "nakshatra_pada" if "pada" in stem else "nakshatra"
        if "tithi" in stem:
            return "tithi"
    if parts and parts[0] == "plants":
        return "plant"
    if parts and parts[0] == "ayurveda":
        return _singular(stem)
    if parts and parts[0] == "ontology":
        # Route by stem so entity IDs preserve their native prefix
        if "tattva" in stem:
            return "tattva"
        if "parampara" in stem:
            return "parampara"
        if "rasa_siddhanta" in stem:
            return "rasa_siddhanta"
        if "bhava" in stem:
            return "bhava"
        if "knowledge" in stem:
            return "knowledge"
        return "concept"
    if parts and parts[0] == "semantics":
        return "art"
    if parts and parts[0] == "sources":
        return "passage" if stem == "passages" else "source"
    if parts and parts[0] == "gandharva":
        return "raga"
    if parts and parts[0] == "carnatic":
        return "tala"
    if parts and parts[0] == "marma":
        return "marma"
    if parts and parts[0] == "ratna":
        return "ratna"
    if parts and parts[0] == "svara":
        return "svara"
    if parts and parts[0] == "vastu":
        return "vastu_deity"
    if parts and parts[0] == "silpa":
        return "measure"
    if parts and parts[0] == "yoga":
        return "body_region"
    if parts and parts[0] == "ritual":
        return "ritual"
    if parts and parts[0] == "entities" and row:
        return _singular(_clean(row.get("type")) or stem)
    if stem.startswith("nakshatra"):
        return "nakshatra"
    if stem.startswith("graha") or stem == "grahas":
        return "graha"
    if stem.startswith("deity") or stem == "deities":
        return "deity"
    if stem.startswith("rashi"):
        return "rashi"
    if stem.startswith("tithi"):
        return "tithi"
    if "plant" in stem:
        return "plant"
    if "geometry" in stem or "mandala" in stem:
        return "yantra"
    if "bija" in stem:
        return "bija"
    if "text" in stem:
        return "text"
    return "concept"


def _collect_scalar_values(value: Any) -> Iterable[str]:
    if value is None:
        return []
    if isinstance(value, (str, int, float, bool)):
        text = _clean(value)
        return [text] if text else []
    if isinstance(value, list):
        out: List[str] = []
        for item in value:
            out.extend(_collect_scalar_values(item))
        return out
    if isinstance(value, dict):
        out: List[str] = []
        for item in value.values():
            out.extend(_collect_scalar_values(item))
        return out
    return []


def _ensure_metadata(metadata: Dict[str, Dict[str, Any]], entity_id: str, category: str, name: str) -> Dict[str, Any]:
    if entity_id not in metadata:
        metadata[entity_id] = {
            "entity_id": entity_id,
            "category": _singular(category),
            "name": _title(name),
            "aliases": set(),
            "sources": set(),
            "attributes": defaultdict(list),
            "raw_rows": [],
            "authorities": set(),
            "theta_authority": "",
            "phi_authority": "",
        }
    return metadata[entity_id]


def _merge_attributes(meta: Dict[str, Any], row: Dict[str, Any], source: str):
    meta["sources"].add(source)
    meta["raw_rows"].append({"source": source, "data": dict(row)})
    for key, value in row.items():
        text = _clean(value)
        if not text:
            continue
        values = meta["attributes"][key]
        if text not in values:
            values.append(text)
    for key in ("aliases", "sanskrit", "sanskrit_name", "iast", "common_name", "deity", "graha", "nakshatra", "name"):
        for value in _collect_scalar_values(row.get(key)):
            meta["aliases"].add(value)
    for key in ("source", "source_file", "source_id", "source_title", "notes", "tradition", "path"):
        value = _clean(row.get(key))
        if value:
            meta["authorities"].add(value)


@lru_cache(maxsize=1)
def _inventory() -> Dict[str, Any]:
    files = []
    for path in sorted(DATASETS_ROOT.rglob("*")):
        if not path.is_file():
            continue
        # Skip archived files
        if "_archive" in path.parts or "_inbox" in path.parts:
            continue
        rel = path.relative_to(DATASETS_ROOT).as_posix()
        suffix = path.suffix.lower()
        payload: Any = None
        if suffix == ".csv":
            payload = _load_csv(path)
        elif suffix == ".json":
            payload = _load_json(path)
        elif suffix in {".yaml", ".yml"}:
            payload = _load_yaml(path)
        files.append({"path": rel, "suffix": suffix, "data": payload})
    return {"files": files}


def _extract_yaml_entities(payload: Any, relpath: str, metadata: Dict[str, Dict[str, Any]]):
    if payload is None:
        return
    if isinstance(payload, dict):
        for key, value in payload.items():
            if isinstance(value, dict):
                category = _dataset_category(relpath, value)
                name = value.get("name") or key
                entity_id = _entity_id(category, name)
                meta = _ensure_metadata(metadata, entity_id, category, name)
                row = {"name": name, **value}
                _merge_attributes(meta, row, relpath)
            elif isinstance(value, list):
                category = _dataset_category(relpath, {"type": key})
                for index, item in enumerate(value, start=1):
                    if isinstance(item, dict):
                        name = item.get("name") or item.get("title") or item.get("english_name") or item.get("id") or f"{key}_{index}"
                        entity_id = _entity_id(category, name)
                        meta = _ensure_metadata(metadata, entity_id, category, name)
                        _merge_attributes(meta, item, relpath)
                    else:
                        name = _clean(item)
                        if not name:
                            continue
                        entity_id = _entity_id(category, name)
                        meta = _ensure_metadata(metadata, entity_id, category, name)
                        _merge_attributes(meta, {"name": name}, relpath)


def _extract_json_entities(payload: Any, relpath: str, metadata: Dict[str, Dict[str, Any]]):
    stem = Path(relpath).stem
    if isinstance(payload, dict) and isinstance(payload.get("items"), list):
        category = _dataset_category(relpath)
        for item in payload["items"]:
            if not isinstance(item, dict):
                continue
            name = item.get("name") or item.get("english_name") or item.get("id")
            if not name:
                continue
            entity_id = _entity_id(category, name)
            meta = _ensure_metadata(metadata, entity_id, category, name)
            _merge_attributes(meta, item, relpath)
        return
    if isinstance(payload, dict) and stem == "atlas_mandala":
        bindu = payload.get("bindu") or {}
        entity_id = _entity_id("yantra", "bindu")
        meta = _ensure_metadata(metadata, entity_id, "yantra", "bindu")
        _merge_attributes(meta, bindu if isinstance(bindu, dict) else {"value": bindu}, relpath)
        for index, item in enumerate(payload.get("petals", []), start=1):
            entity_id = _entity_id("yantra", f"petal_{index}")
            meta = _ensure_metadata(metadata, entity_id, "yantra", f"petal_{index}")
            _merge_attributes(meta, item if isinstance(item, dict) else {"value": item}, relpath)
        return
    if isinstance(payload, dict) and stem == "output":
        for key, value in payload.items():
            entity_id = _entity_id("concept", key)
            meta = _ensure_metadata(metadata, entity_id, "concept", key)
            _merge_attributes(meta, {"name": key, "value": json.dumps(value, ensure_ascii=False)[:200]}, relpath)


def _extract_csv_entities(rows: List[Dict[str, str]], relpath: str, metadata: Dict[str, Dict[str, Any]]):
    if not rows:
        return
    category = _dataset_category(relpath)
    if category == "relation":
        return
    for index, row in enumerate(rows, start=1):
        row = dict(row)
        row["_row_index"] = str(index)
        entity_category = _dataset_category(relpath, row)
        if entity_category in {"source", "passage"}:
            continue
        if relpath == "astro/nakshatra_padas.csv":
            nak = _clean(row.get("nakshatra"))
            pada = _clean(row.get("pada"))
            if not nak or not pada:
                continue
            pada_name = f"{nak} pada {pada}"
            pada_id = _entity_id("nakshatra_pada", pada_name)
            pada_meta = _ensure_metadata(metadata, pada_id, "nakshatra_pada", pada_name)
            _merge_attributes(pada_meta, row, relpath)
            continue
        if "pada_topology" in relpath:
            pid = _clean(row.get("id", ""))
            if not pid:
                continue
            meta = _ensure_metadata(metadata, pid, "pada", pid)
            _merge_attributes(meta, row, relpath)
            continue
        if "deity_attributes" in relpath:
            did = _clean(row.get("deity_id", ""))
            if not did:
                continue
            deity_name = _clean(row.get("deity", did))
            meta = _ensure_metadata(metadata, did, "deity_attr", deity_name)
            _merge_attributes(meta, row, relpath)
            continue
        if relpath == "nitya_devi_mapping.csv":
            name = _clean(row.get("nitya_devi"))
            if not name:
                continue
            entity_id = _entity_id("devi", name)
            meta = _ensure_metadata(metadata, entity_id, "devi", name)
            _merge_attributes(meta, {"name": name, **row}, relpath)
            continue
        # Ontology CSVs carry pre-formed IDs — use them directly
        _ONTOLOGY_CATS = {"tattva", "parampara", "rasa_siddhanta", "bhava", "knowledge"}
        _raw_id = str(row.get("id", "")).strip()
        if entity_category in _ONTOLOGY_CATS and _raw_id:
            entity_id = _raw_id
            name = str(row.get("name_iast") or row.get("name") or _raw_id).strip()
        else:
            name = _primary_name_from_row(row, entity_category, relpath)
            entity_id = _entity_id(entity_category, name)
        meta = _ensure_metadata(metadata, entity_id, entity_category, name)
        _merge_attributes(meta, row, relpath)
        if relpath == "yoga/nakshatra_body_map.csv":
            body_region = _clean(row.get("body_region"))
            if body_region:
                body_id = _entity_id("body_region", body_region)
                body_meta = _ensure_metadata(metadata, body_id, "body_region", body_region)
                _merge_attributes(body_meta, row, relpath)


def _canonical_endpoint(raw: str) -> Optional[Tuple[str, str, str]]:
    raw = _clean(raw)
    if not raw:
        return None
    if ":" in raw:
        prefix, value = raw.split(":", 1)
        prefix = _singular(prefix)
        value = value.strip()
        if prefix == "nakshatra" and value.isdigit():
            value = NUM_TO_NAK.get(value, value)
        if prefix == "nakshatra_pada":
            match = re.fullmatch(r"(\d+)[_:](\d+)", value)
            if match:
                nak_name = NUM_TO_NAK.get(match.group(1), match.group(1))
                value = f"{nak_name} pada {match.group(2)}"
        return prefix, _title(value), _entity_id(prefix, value)
    return None


@lru_cache(maxsize=1)
def load_relations() -> Dict[str, List[Dict[str, Any]]]:
    metadata = load_entity_metadata()
    graph: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    relation_paths: List[Path] = []
    for path in sorted(DATASETS_ROOT.rglob("*.csv")):
        if "_archive" in path.parts or "_inbox" in path.parts:
            continue
        rel = path.relative_to(DATASETS_ROOT).as_posix()
        if "relation" in path.stem or any(part.startswith("relations") for part in path.parts):
            relation_paths.append(path)
    for path in relation_paths:
        relpath = path.relative_to(DATASETS_ROOT).as_posix()
        rows = _load_csv(path)
        for row in rows:
            from_raw = row.get("from_id") or row.get("source") or row.get("from")
            to_raw = row.get("to_id") or row.get("target") or row.get("to")
            relation = _clean(row.get("relation") or row.get("predicate") or path.stem)
            left = _canonical_endpoint(_clean(from_raw))
            right = _canonical_endpoint(_clean(to_raw))
            if left is None or right is None or not relation:
                continue
            _, left_name, left_id = left
            _, right_name, right_id = right
            if left_id not in metadata:
                _ensure_metadata(metadata, left_id, left[0], left_name)
            if right_id not in metadata:
                _ensure_metadata(metadata, right_id, right[0], right_name)
            edge = {
                "from_id": left_id,
                "to_id": right_id,
                "relation": relation,
                "source_file": relpath,
                "confidence": _clean(row.get("confidence")) or "dataset",
                "authority": _clean(row.get("source_title") or row.get("tradition") or relpath),
            }
            graph[left_id].append(edge)
            graph[right_id].append({**edge, "from_id": right_id, "to_id": left_id, "inverse": True})

    # ── Derive relations from mapping files ──────────────────
    _derive_relations_from_mappings(graph, metadata)

    return dict(graph)


def _derive_relations_from_mappings(graph: Dict, metadata: Dict) -> None:
    """Generate relation edges from mapping CSVs that aren't in relations/ dir.

    These files contain entity associations but in attribute format,
    not from_id/relation/to_id format. We derive edges from them.
    """

    def _add_edge(from_id, to_id, relation, source):
        if not from_id or not to_id:
            return
        edge = {"from_id": from_id, "to_id": to_id, "relation": relation,
                "source_file": source, "confidence": "derived", "authority": source}
        graph[from_id].append(edge)
        graph[to_id].append({**edge, "from_id": to_id, "to_id": from_id, "inverse": True})
        for eid in (from_id, to_id):
            if eid not in metadata:
                cat = eid.split("_")[0]
                name = eid.replace(cat + "_", "").replace("_", " ").title()
                _ensure_metadata(metadata, eid, cat, name)

    # 1. nakshatra → plant + plant → element/dosha/deity (from plants/nakshatra_plants.csv)
    plant_path = DATASETS_ROOT / "plants" / "nakshatra_plants.csv"
    if plant_path.exists():
        for row in _load_csv(plant_path):
            nak = _clean(row.get("nakshatra", ""))
            plant = _clean(row.get("plant") or row.get("common_name", ""))
            if nak and plant:
                nak_id = _entity_id("nakshatra", nak)
                plant_id = _entity_id("plant", plant)
                _add_edge(nak_id, plant_id, "nakshatra_plant", "plants/nakshatra_plants.csv")
                # Plant → element, dosha, deity (forward edges)
                elem = _clean(row.get("element", ""))
                if elem:
                    _add_edge(plant_id, _entity_id("element", elem), "plant_element", "plants/nakshatra_plants.csv")
                dosha = _clean(row.get("dosha", ""))
                if dosha:
                    _add_edge(plant_id, _entity_id("dosha", dosha), "plant_dosha", "plants/nakshatra_plants.csv")
                deity = _clean(row.get("deity", ""))
                if deity:
                    _add_edge(plant_id, _entity_id("deity", deity), "plant_deity", "plants/nakshatra_plants.csv")

    # 2. tithi → nitya devi (from nitya_devi_mapping.csv)
    devi_map_path = DATASETS_ROOT / "nitya_devi_mapping.csv"
    if devi_map_path.exists():
        for row in _load_csv(devi_map_path):
            tithi_id = _clean(row.get("tithi_id", ""))
            devi = _clean(row.get("nitya_devi", ""))
            if tithi_id and devi:
                _add_edge(tithi_id, _entity_id("nitya_devi", devi),
                          "tithi_associated_nitya_devi", "nitya_devi_mapping.csv")

    # 3. nakshatra → body region (from yoga/nakshatra_body_map.csv)
    body_path = DATASETS_ROOT / "yoga" / "nakshatra_body_map.csv"
    if body_path.exists():
        for row in _load_csv(body_path):
            nak = _clean(row.get("nakshatra", ""))
            body = _clean(row.get("body_region", ""))
            if nak and body:
                _add_edge(_entity_id("nakshatra", nak), _entity_id("body", body),
                          "nakshatra_body_region", "yoga/nakshatra_body_map.csv")

    # 4. bija → element, deity (from cosmology/bija_master.csv)
    bija_path = DATASETS_ROOT / "cosmology" / "bija_master.csv"
    if bija_path.exists():
        for row in _load_csv(bija_path):
            bija = _clean(row.get("bija", ""))
            if not bija:
                continue
            bija_id = _entity_id("bija", bija)
            for rel, col in [("element", "element"), ("deity", "deity"), ("domain", "domain")]:
                val = _clean(row.get(col, ""))
                if val:
                    _add_edge(bija_id, _entity_id(rel if rel != "domain" else "concept", val),
                              f"bija_{rel}", "gandharva/bija_master.csv")

    # 5. graha → bija, ratna (already in ratna_relations.csv — skip if exists)

    # 5b. deity → element, domain (from cosmology/deity_master.csv)
    deity_path = DATASETS_ROOT / "cosmology" / "deity_master.csv"
    if deity_path.exists():
        for row in _load_csv(deity_path):
            deity = _clean(row.get("deity", ""))
            if not deity:
                continue
            did = _entity_id("deity", deity)
            elem = _clean(row.get("element", ""))
            if elem:
                _add_edge(did, _entity_id("element", elem), "deity_element", "cosmology/deity_master.csv")
            domain = _clean(row.get("domain", ""))
            if domain:
                _add_edge(did, _entity_id("domain", domain), "deity_domain", "cosmology/deity_master.csv")
            graha = _clean(row.get("associated_graha", ""))
            if graha:
                _add_edge(did, _entity_id("graha", graha), "deity_graha", "cosmology/deity_master.csv")

    # 5c. nakshatra → gemstone, shakti, direction (from cosmology/nakshatra_extended.csv)
    nak_ext_path = DATASETS_ROOT / "cosmology" / "nakshatra_extended.csv"
    if nak_ext_path.exists():
        for row in _load_csv(nak_ext_path):
            nak = _clean(row.get("nakshatra", ""))
            if not nak:
                continue
            nid = _entity_id("nakshatra", nak)
            gem = _clean(row.get("gemstone", ""))
            if gem:
                _add_edge(nid, _entity_id("ratna", gem), "nakshatra_gemstone", "astro/nakshatra_extended.csv")
            tree = _clean(row.get("tree", ""))
            if tree:
                _add_edge(nid, _entity_id("plant", tree), "nakshatra_tree", "astro/nakshatra_extended.csv")

    # 5d. tala → element, deity + attribute update (from carnatic/tala_master.csv)
    tala_path = DATASETS_ROOT / "carnatic" / "tala_master.csv"
    if tala_path.exists():
        for row in _load_csv(tala_path):
            tid = _clean(row.get("id", ""))
            if not tid:
                continue
            # Ensure entity exists, then update attributes
            if tid not in metadata:
                name = _clean(row.get("name_iast", tid))
                _ensure_metadata(metadata, tid, "tala", name)
            attrs = metadata[tid].setdefault("attributes", {})
            for col in ("element", "guna", "deity", "rasa", "time_of_day", "tradition",
                        "beat_count", "anga_structure", "tempo_range", "color_hex"):
                val = _clean(row.get(col, ""))
                if val:
                    attrs.setdefault(col, [])
                    if val not in attrs[col]:
                        attrs[col].append(val)
            # Edges
            elem = _clean(row.get("element", ""))
            if elem:
                _add_edge(tid, _entity_id("element", elem), "tala_element", "carnatic/tala_master.csv")
            deity = _clean(row.get("deity", ""))
            if deity:
                _add_edge(tid, _entity_id("deity", deity), "tala_deity", "carnatic/tala_master.csv")

    # 5e. tithi_master → deity, nitya_devi, element + attribute update (from astro/tithi_master.csv)
    tithi_m2_path = DATASETS_ROOT / "astro" / "tithi_master.csv"
    if tithi_m2_path.exists():
        for row in _load_csv(tithi_m2_path):
            tid = _clean(row.get("id", ""))
            if not tid:
                continue
            # Ensure entity exists, then update attributes
            if tid not in metadata:
                name = _clean(row.get("name_iast", tid))
                _ensure_metadata(metadata, tid, "tithi", name)
            attrs = metadata[tid].setdefault("attributes", {})
            for col in ("element", "guna", "deity", "quality", "good_for", "avoid",
                        "nitya_devi", "paksha", "color_hex"):
                val = _clean(row.get(col, ""))
                if val:
                    attrs.setdefault(col, [])
                    if val not in attrs[col]:
                        attrs[col].append(val)
            # Edges
            deity = _clean(row.get("deity", ""))
            if deity:
                _add_edge(tid, _entity_id("deity", deity), "tithi_deity", "astro/tithi_master.csv")
            ndevi = _clean(row.get("nitya_devi", ""))
            if ndevi:
                _add_edge(tid, _entity_id("devi", ndevi), "tithi_nitya_devi_master", "astro/tithi_master.csv")
            elem = _clean(row.get("element", ""))
            if elem:
                _add_edge(tid, _entity_id("element", elem), "tithi_element_master", "astro/tithi_master.csv")

    # 5f. raga → deity, graha, element (from carnatic/raga_master_extended.csv)
    raga_ext_path = DATASETS_ROOT / "carnatic" / "raga_master_extended.csv"
    if raga_ext_path.exists():
        for row in _load_csv(raga_ext_path):
            rid = _clean(row.get("id", ""))
            if not rid:
                continue
            if rid not in metadata:
                name = _clean(row.get("name_iast", rid))
                _ensure_metadata(metadata, rid, "raga", name)
            attrs = metadata[rid].setdefault("attributes", {})
            for col in ("element", "guna", "rasa_primary", "deity", "graha",
                        "time_of_day", "season", "vadi", "samvadi", "tradition",
                        "aroha", "avaroha", "dosha_balance", "color_hex"):
                val = _clean(row.get(col, ""))
                if val:
                    attrs.setdefault(col, [])
                    if val not in attrs[col]:
                        attrs[col].append(val)
            deity = _clean(row.get("deity", ""))
            if deity:
                _add_edge(rid, _entity_id("deity", deity), "raga_deity", "carnatic/raga_master_extended.csv")
            graha = _clean(row.get("graha", ""))
            if graha:
                _add_edge(rid, _entity_id("graha", graha), "raga_graha", "carnatic/raga_master_extended.csv")
            elem = _clean(row.get("element", ""))
            if elem:
                _add_edge(rid, _entity_id("element", elem), "raga_element", "carnatic/raga_master_extended.csv")

    # 5g. marma → element, chakra, nakshatra (from yoga/marma_master.csv)
    marma_ext_path = DATASETS_ROOT / "yoga" / "marma_master.csv"
    if marma_ext_path.exists():
        for row in _load_csv(marma_ext_path):
            mid = _clean(row.get("id", ""))
            if not mid:
                continue
            # Normalize marma:adhipati → marma_adhipati
            mid = mid.replace(":", "_")
            if mid not in metadata:
                name = _clean(row.get("name_iast", mid))
                _ensure_metadata(metadata, mid, "marma", name)
            attrs = metadata[mid].setdefault("attributes", {})
            for col in ("element", "guna", "dosha", "body_region", "chakra_affinity",
                        "tissue_type", "function", "therapeutic_note"):
                val = _clean(row.get(col, ""))
                if val:
                    attrs.setdefault(col, [])
                    if val not in attrs[col]:
                        attrs[col].append(val)
            elem = _clean(row.get("element", ""))
            if elem:
                _add_edge(mid, _entity_id("element", elem), "marma_element", "yoga/marma_master.csv")
            chakra = _clean(row.get("chakra_affinity", ""))
            if chakra:
                _add_edge(mid, _entity_id("chakra", chakra.lower()), "marma_chakra", "yoga/marma_master.csv")

    # 5h. instrument → deity, graha, chakra, element (from gandharva/instruments.csv)
    inst_path = DATASETS_ROOT / "gandharva" / "instruments.csv"
    if inst_path.exists():
        for row in _load_csv(inst_path):
            iid = _clean(row.get("id", ""))
            if not iid:
                continue
            if iid not in metadata:
                name = _clean(row.get("name_iast", iid))
                _ensure_metadata(metadata, iid, "instrument", name)
            attrs = metadata[iid].setdefault("attributes", {})
            for col in ("element", "guna", "chakra", "deity", "graha", "rasa_primary",
                        "time_of_day", "synthesis_type", "f0_range", "varna_affinity",
                        "body_region", "category", "timbre_character", "color_hex"):
                val = _clean(row.get(col, ""))
                if val:
                    attrs.setdefault(col, [])
                    if val not in attrs[col]:
                        attrs[col].append(val)
            # Edges
            deity = _clean(row.get("deity", ""))
            if deity:
                _add_edge(iid, _entity_id("deity", deity), "instrument_deity", "gandharva/instruments.csv")
            graha = _clean(row.get("graha", ""))
            if graha:
                _add_edge(iid, _entity_id("graha", graha), "instrument_graha", "gandharva/instruments.csv")
            chakra = _clean(row.get("chakra", ""))
            if chakra:
                _add_edge(iid, _entity_id("chakra", chakra), "instrument_chakra", "gandharva/instruments.csv")
            elem = _clean(row.get("element", ""))
            if elem:
                _add_edge(iid, _entity_id("element", elem), "instrument_element", "gandharva/instruments.csv")

    # 6. chakra → nakshatra, deity, element, graha, bija (from tantra/chakra_master.csv)
    chakra_path = DATASETS_ROOT / "tantra" / "chakra_master.csv"
    if chakra_path.exists():
        for row in _load_csv(chakra_path):
            cid = _clean(row.get("id", ""))
            if not cid:
                continue
            # nakshatra relations (comma-separated)
            naks = row.get("nakshatras", "")
            for nak in naks.split(","):
                nak = nak.strip()
                if nak:
                    _add_edge(cid, _entity_id("nakshatra", nak),
                              "chakra_nakshatra", "tantra/chakra_master.csv")
            # deity, element, graha, bija
            for rel, col in [("deity", "deity"), ("element", "element"),
                             ("graha", "graha"), ("bija", "bija")]:
                val = _clean(row.get(col, ""))
                if val:
                    _add_edge(cid, _entity_id(rel if rel != "bija" else "bija", val.lower()),
                              f"chakra_{rel}", "tantra/chakra_master.csv")

    # 7. tithi master → element, guna, devi (from astro/tithi_master.csv)
    tithi_master_path = DATASETS_ROOT / "astro" / "tithi_master.csv"
    if tithi_master_path.exists():
        for row in _load_csv(tithi_master_path):
            tnum = _clean(row.get("tithi_num", ""))
            name = _clean(row.get("name_iast", ""))
            if not tnum:
                continue
            t_id = f"tithi_{tnum}"
            for rel, col in [("element", "element"), ("guna", "guna"),
                             ("dosha", "dosha"), ("nitya_devi", "nitya_devi")]:
                val = _clean(row.get(col, ""))
                if val:
                    _add_edge(t_id, _entity_id(rel if rel != "nitya_devi" else "devi", val),
                              f"tithi_{rel}", "astro/tithi_master.csv")

    # 8. nitya devi → element, graha, bija (from cosmology/nitya_devi_master.csv)
    ndevi_path = DATASETS_ROOT / "cosmology" / "nitya_devi_master.csv"
    if ndevi_path.exists():
        for row in _load_csv(ndevi_path):
            did = _clean(row.get("id", ""))
            if not did:
                continue
            for rel, col in [("element", "element"), ("graha", "graha"),
                             ("bija", "bija"), ("guna", "guna")]:
                val = _clean(row.get(col, ""))
                if val:
                    _add_edge(did, _entity_id(rel if rel != "bija" else "bija", val.lower()),
                              f"devi_{rel}", "cosmology/nitya_devi_master.csv")

    # 9. tithi → element, guna (from tithi_properties.csv — original)
    tithi_prop_path = DATASETS_ROOT / "tithi_properties.csv"
    if tithi_prop_path.exists():
        for i, row in enumerate(_load_csv(tithi_prop_path)):
            tithi = _clean(row.get("tithi", ""))
            element = _clean(row.get("element", ""))
            guna = _clean(row.get("guna", ""))
            if tithi:
                t_id = _entity_id("tithi", tithi)
                if element:
                    _add_edge(t_id, _entity_id("element", element),
                              "tithi_element", "tithi_properties.csv")
                if guna:
                    _add_edge(t_id, _entity_id("guna", guna),
                              "tithi_guna", "tithi_properties.csv")

    # 10. pada_topology → pada relations + yantra_triangle entities
    _YANTRA_COMPASS = {
        "shakti_kali": "SW", "shakti_dvapara": "SE", "shakti_treta": "E",
        "shakti_satya": "NE", "shiva_satya": "N", "shiva_treta": "NW",
        "shiva_dvapara_1": "W", "shiva_dvapara_2": "W", "shiva_kali": "S",
    }
    _YANTRA_POLARITY = {
        "shakti_kali": "Shakti", "shakti_dvapara": "Shakti",
        "shakti_treta": "Shakti", "shakti_satya": "Shakti",
        "shiva_satya": "Shiva", "shiva_treta": "Shiva",
        "shiva_dvapara_1": "Shiva", "shiva_dvapara_2": "Shiva",
        "shiva_kali": "Shiva",
    }
    _YANTRA_YUGA = {
        "shakti_kali": "Kali", "shakti_dvapara": "Dvapara",
        "shakti_treta": "Treta", "shakti_satya": "Satya",
        "shiva_satya": "Satya", "shiva_treta": "Treta",
        "shiva_dvapara_1": "Dvapara", "shiva_dvapara_2": "Dvapara",
        "shiva_kali": "Kali",
    }

    # Create 9 yantra_triangle entities
    for tri_id, compass in _YANTRA_COMPASS.items():
        yt_id = f"yantra_{tri_id}"
        if yt_id not in metadata:
            _ensure_metadata(metadata, yt_id, "yantra_triangle", tri_id)
        attrs = metadata[yt_id].setdefault("attributes", {})
        attrs.setdefault("polarity", []).append(_YANTRA_POLARITY[tri_id])
        attrs.setdefault("yuga", []).append(_YANTRA_YUGA[tri_id])
        attrs.setdefault("compass", []).append(compass)
        # compass relation
        _add_edge(yt_id, _entity_id("direction", compass),
                  "triangle_vastu", "vastu/pada_topology.csv")

    # Pada relations
    pada_path = DATASETS_ROOT / "cosmology" / "pada_topology.csv"
    if pada_path.exists():
        _pada_rows = _load_csv(pada_path)
        for row in _pada_rows:
            pid = _clean(row.get("id", ""))
            if not pid:
                continue
            nak = _clean(row.get("nakshatra", ""))
            elem = _clean(row.get("element", ""))
            tri = _clean(row.get("yantra_triangle_id", ""))
            opp = _clean(row.get("opposite_pada", ""))
            tri_padas = _clean(row.get("triangle_pada", ""))

            if nak:
                _add_edge(pid, _entity_id("nakshatra", nak),
                          "pada_nakshatra", "vastu/pada_topology.csv")
            if elem:
                _add_edge(pid, _entity_id("element", elem),
                          "pada_element", "vastu/pada_topology.csv")
            if opp:
                _add_edge(pid, opp, "pada_opposite", "vastu/pada_topology.csv")
            if tri:
                yt_id = f"yantra_{tri}"
                _add_edge(pid, yt_id, "pada_yantra_triangle", "vastu/pada_topology.csv")
                # triangle_vertex from yantra → nakshatra
                if nak and _clean(row.get("pada_n", "")) == "1":
                    _add_edge(yt_id, _entity_id("nakshatra", nak),
                              "triangle_vertex", "vastu/pada_topology.csv")
            if tri_padas:
                for tp in tri_padas.split(";"):
                    tp = tp.strip()
                    if tp:
                        _add_edge(pid, tp, "pada_triangle_vertex", "vastu/pada_topology.csv")


    # 11. deity_attributes → nakshatra, items, vahana relations + sacred_item entities
    da_path = DATASETS_ROOT / "cosmology" / "deity_attributes.csv"
    if da_path.exists():
        for row in _load_csv(da_path):
            did = _clean(row.get("deity_id", ""))
            nak = _clean(row.get("nakshatra", ""))
            if not did:
                continue

            # deity → nakshatra
            if nak:
                _add_edge(did, _entity_id("nakshatra", nak),
                          "deity_of_nakshatra", "cosmology/deity_attributes.csv")

            # Items: create sacred_item entities and edges
            for col in ("item_1", "item_2", "item_3", "item_4"):
                item_name = _clean(row.get(col, ""))
                if not item_name:
                    continue
                item_id = f"item_{item_name}"
                if item_id not in metadata:
                    _ensure_metadata(metadata, item_id, "sacred_item", _title(item_name))
                _add_edge(did, item_id, "deity_carries_item", "cosmology/deity_attributes.csv")

            # Vahana
            vahana = _clean(row.get("vahana", ""))
            if vahana:
                vah_id = f"vahana_{vahana}"
                if vah_id not in metadata:
                    _ensure_metadata(metadata, vah_id, "vahana", _title(vahana))
                _add_edge(did, vah_id, "deity_vahana", "cosmology/deity_attributes.csv")

            # Gemstone → ratna
            gem = _clean(row.get("gemstone", ""))
            if gem:
                _add_edge(did, _entity_id("ratna", gem),
                          "deity_gemstone", "cosmology/deity_attributes.csv")

            # Direction
            direction = _clean(row.get("direction", ""))
            if direction:
                _add_edge(did, _entity_id("direction", direction),
                          "deity_direction", "cosmology/deity_attributes.csv")

            # Tattva → element
            tattva = _clean(row.get("tattva", ""))
            if tattva:
                elem_name = {"agni": "fire", "jala": "water", "vayu": "air",
                             "earth": "earth", "akasha": "ether", "air": "air"}.get(tattva, tattva)
                _add_edge(did, _entity_id("element", elem_name),
                          "deity_tattva", "cosmology/deity_attributes.csv")

            # Rasa
            rasa = _clean(row.get("rasa", ""))
            if rasa:
                _add_edge(did, _entity_id("rasa", rasa),
                          "deity_rasa", "cosmology/deity_attributes.csv")


@lru_cache(maxsize=1)
def load_entity_metadata() -> Dict[str, Dict[str, Any]]:
    metadata: Dict[str, Dict[str, Any]] = {}
    for file_info in _inventory()["files"]:
        relpath = file_info["path"]
        suffix = file_info["suffix"]
        data = file_info["data"]
        if suffix == ".csv":
            _extract_csv_entities(data or [], relpath, metadata)
        elif suffix == ".json":
            _extract_json_entities(data, relpath, metadata)
        elif suffix in {".yaml", ".yml"}:
            _extract_yaml_entities(data, relpath, metadata)
    # normalize mutable containers for callers
    for meta in metadata.values():
        meta["aliases"] = sorted(set(meta["aliases"]))
        meta["sources"] = sorted(set(meta["sources"]))
        meta["authorities"] = sorted(set(meta["authorities"]))
        meta["attributes"] = {key: values for key, values in meta["attributes"].items()}
    return metadata


def _first(meta: Dict[str, Any], *keys: str) -> str:
    attrs = meta.get("attributes", {})
    for key in keys:
        values = attrs.get(key)
        if values:
            return _clean(values[0])
    return ""


def _theta_candidates(meta: Dict[str, Any]) -> List[Tuple[float, float, str]]:
    candidates: List[Tuple[float, float, str]] = []
    category = meta["category"]
    name_slug = _slug(meta["name"])
    if category == "nakshatra" and name_slug in NAKSHATRA_ANGLE:
        candidates.append((NAKSHATRA_ANGLE[name_slug], 1.0, f"nakshatra:{meta['name']}"))
    nakshatra_value = _first(meta, "nakshatra", "name_key", "key")
    if _slug(nakshatra_value) in NAKSHATRA_ANGLE:
        candidates.append((NAKSHATRA_ANGLE[_slug(nakshatra_value)], 0.95, f"row.nakshatra:{nakshatra_value}"))
    if category == "nakshatra_pada":
        nak = _first(meta, "nakshatra")
        if _slug(nak) in NAKSHATRA_ANGLE:
            candidates.append((NAKSHATRA_ANGLE[_slug(nak)], 0.9, f"nakshatra_pada:{nak}"))
    tithi_name = meta["name"] if category == "tithi" else _first(meta, "tithi", "nitya_devi")
    tithi_key = _slug(tithi_name)
    if tithi_key in TITHI_ANGLE:
        candidates.append((TITHI_ANGLE[tithi_key], 0.9, f"tithi:{tithi_name}"))
    tithi_id = _first(meta, "tithi_id", "id")
    if tithi_id.isdigit():
        candidates.append((((int(tithi_id) - 1) / 30.0) * 2 * math.pi, 0.9, f"tithi_id:{tithi_id}"))
    if category == "graha":
        graha_key = GRAHA_ID_ALIASES.get(name_slug, name_slug)
        vara = GRAHA_TO_VARA.get(graha_key)
        if vara:
            candidates.append((VARA_ANGLE[vara], 0.85, f"graha_vara:{graha_key}"))
    associated_graha = _first(meta, "associated_graha", "graha", "ruler", "ruling_graha", "planet")
    graha_key = GRAHA_ID_ALIASES.get(_slug(associated_graha), "")
    vara = GRAHA_TO_VARA.get(graha_key)
    if vara:
        candidates.append((VARA_ANGLE[vara], 0.8, f"associated_graha:{associated_graha}"))
    vara_name = _first(meta, "vara", "day")
    vara_key = _slug(vara_name)
    if vara_key in VARA_ANGLE:
        candidates.append((VARA_ANGLE[vara_key], 0.8, f"vara:{vara_name}"))
    if category == "devi":
        tithi_num = NITYA_DEVI_TO_TITHI.get(name_slug)
        if tithi_num:
            candidates.append((((tithi_num - 1) / 30.0) * 2 * math.pi, 0.85, f"nitya_devi:{meta['name']}"))
    if category == "tala":
        family = _first(meta, "family")
        _TALA_FAMILIES = ["dhruva", "matya", "rupaka", "jhampa", "triputa", "ata", "eka"]
        family_slug = _slug(family)
        if family_slug in _TALA_FAMILIES:
            candidates.append(((_TALA_FAMILIES.index(family_slug) / len(_TALA_FAMILIES)) * 2 * math.pi, 0.8, f"tala_family:{family}"))
    if category == "vastu_deity":
        x_val = _first(meta, "x")
        y_val = _first(meta, "y")
        if x_val and y_val:
            try:
                x, y = float(x_val), float(y_val)
                candidates.append(((math.atan2(y - 4.5, x - 4.5) % (2 * math.pi)), 0.85, f"vastu_grid:{x_val},{y_val}"))
            except ValueError:
                pass
    return candidates


def _phi_candidates(meta: Dict[str, Any]) -> List[Tuple[float, float, str]]:
    candidates: List[Tuple[float, float, str]] = []
    category = meta["category"]
    name_slug = _slug(meta["name"])
    if category == "element":
        key = ELEMENT_ALIASES.get(name_slug, name_slug)
        if key in ELEMENT_ANGLE:
            candidates.append((ELEMENT_ANGLE[key], 1.0, f"element:{meta['name']}"))
    element_value = _first(meta, "element", "elements")
    for token in re.split(r"[^a-zA-Z]+", element_value.lower()):
        token = ELEMENT_ALIASES.get(token, token)
        if token in ELEMENT_ANGLE:
            candidates.append((ELEMENT_ANGLE[token], 0.9, f"element:{token}"))
    if category == "guna" and name_slug in GUNA_ANGLE:
        candidates.append((GUNA_ANGLE[name_slug], 1.0, f"guna:{meta['name']}"))
    guna_value = _first(meta, "guna", "qualities")
    for token in re.split(r"[^a-zA-Z]+", guna_value.lower()):
        if token in GUNA_ANGLE:
            candidates.append((GUNA_ANGLE[token], 0.75, f"guna:{token}"))
    rasa_value = _first(meta, "rasa")
    for token in re.split(r"[^a-zA-Z]+", rasa_value.lower()):
        if token in RASA_ANGLE:
            candidates.append((RASA_ANGLE[token], 0.8, f"rasa:{token}"))
    if category == "dosha":
        for element in DOSHA_TO_ELEMENT.get(name_slug, []):
            candidates.append((ELEMENT_ANGLE[element], 0.6, f"dosha:{name_slug}->{element}"))
    dosha_value = _first(meta, "dosha", "dosha_target")
    for token in re.split(r"[^a-zA-Z]+", dosha_value.lower()):
        for element in DOSHA_TO_ELEMENT.get(token, []):
            candidates.append((ELEMENT_ANGLE[element], 0.55, f"dosha:{token}->{element}"))
    if category == "rasa" and name_slug in RASA_ANGLE:
        candidates.append((RASA_ANGLE[name_slug], 0.9, f"rasa:{name_slug}"))
    if category == "vastu_deity":
        direction = _slug(_first(meta, "direction"))
        _DIR_ELEMENT = {"east": "fire", "south": "earth", "west": "water", "north": "air"}
        elem = _DIR_ELEMENT.get(direction)
        if elem and elem in ELEMENT_ANGLE:
            candidates.append((ELEMENT_ANGLE[elem], 0.75, f"vastu_direction:{direction}"))
    if category == "marma":
        body = _slug(_first(meta, "body_region"))
        _BODY_ELEMENT = {"head": "ether", "chest": "air", "abdomen": "fire", "pelvis": "water", "legs": "earth",
                         "arms": "air", "back": "earth", "ears": "ether", "eyes": "fire", "face": "ether",
                         "feet": "earth", "hands": "air", "neck": "ether", "shoulders": "air"}
        elem = _BODY_ELEMENT.get(body)
        if elem and elem in ELEMENT_ANGLE:
            candidates.append((ELEMENT_ANGLE[elem], 0.7, f"marma_body:{body}"))
    return candidates


def _resolve_coordinate(meta: Dict[str, Any], relations: Dict[str, List[Dict[str, Any]]], coordinates: Dict[str, Tuple[float, float]]) -> Tuple[float, float]:
    theta_candidates = _theta_candidates(meta)
    phi_candidates = _phi_candidates(meta)

    for edge in relations.get(meta["entity_id"], []):
        other_id = edge["to_id"]
        if other_id not in coordinates:
            continue
        other_theta, other_phi = coordinates[other_id]
        if not theta_candidates:
            theta_candidates.append((other_theta, 0.45, f"relation:{edge['relation']}->{other_id}"))
        if not phi_candidates:
            phi_candidates.append((other_phi, 0.45, f"relation:{edge['relation']}->{other_id}"))

    if not theta_candidates:
        fallback = (_slug(meta["entity_id"]).__hash__() % 360) / 360.0 * 2 * math.pi
        theta_candidates.append((fallback, 0.1, "fallback:stable_hash"))
    if not phi_candidates:
        category = meta["category"]
        if category in {"yantra", "bija", "art", "concept", "ritual", "text", "measure", "body_region"}:
            fallback = ELEMENT_ANGLE["ether"]
            phi_candidates.append((fallback, 0.2, f"fallback:{category}->ether"))
        else:
            fallback = ((_slug(meta["name"]).__hash__() % 180) / 180.0) * 2 * math.pi
            phi_candidates.append((fallback, 0.1, "fallback:stable_hash"))

    theta = _circular_mean((angle, weight) for angle, weight, _ in theta_candidates)
    phi = _circular_mean((angle, weight) for angle, weight, _ in phi_candidates)
    meta["theta_authority"] = theta_candidates[0][2]
    meta["phi_authority"] = phi_candidates[0][2]
    return theta, phi


@lru_cache(maxsize=1)
def load_all_entities() -> Dict[str, Tuple[float, float]]:
    metadata = load_entity_metadata()
    relations = load_relations()
    coordinates: Dict[str, Tuple[float, float]] = {}

    ordered_ids = sorted(metadata.keys(), key=lambda eid: (
        metadata[eid]["category"] not in {"nakshatra", "tithi", "graha", "devi", "plant"},
        metadata[eid]["category"],
        eid,
    ))

    for _ in range(3):
        changed = False
        for entity_id in ordered_ids:
            coords = _resolve_coordinate(metadata[entity_id], relations, coordinates)
            if coordinates.get(entity_id) != coords:
                coordinates[entity_id] = coords
                changed = True
        if not changed:
            break
    return coordinates


@lru_cache(maxsize=1)
def load_nakshatra_metadata() -> Dict[str, Dict[str, Any]]:
    merged: Dict[str, Dict[str, Any]] = {name: {"name": name, "position": idx + 1, "sources": []} for idx, name in enumerate(_NAK_ORDER)}
    relevant = [
        "astro/nakshatra_core.csv",
        "astro/nakshatra_full.csv",
        "astro/nakshatra_core.csv",
        "astro/nakshatra_master.csv",
        "astro/nakshatra_extended.csv",
        "astro/nakshatra_deities.csv",
        "cosmology/nakshatra_syllables.csv",
        "plants/nakshatra_plants.csv",
        "plants/nakshatra_agriculture.csv",
        "yoga/nakshatra_body_map.csv",
    ]
    inventory = {entry["path"]: entry["data"] for entry in _inventory()["files"]}
    for relpath in relevant:
        rows = inventory.get(relpath) or []
        if not isinstance(rows, list):
            continue
        for row in rows:
            name = _clean(row.get("nakshatra"))
            if not name or name not in merged:
                continue
            target = merged[name]
            target["sources"].append(relpath)
            for key, value in row.items():
                text = _clean(value)
                if not text:
                    continue
                if key == "sound":
                    target.setdefault("sounds", []).append(text)
                elif key not in target:
                    target[key] = text
    for value in merged.values():
        value["sources"] = sorted(set(value["sources"]))
        if "sounds" in value:
            value["sounds"] = sorted(set(value["sounds"]))
        value["entity_id"] = _entity_id("nakshatra", value["name"])
        coords = load_all_entities().get(value["entity_id"])
        if coords:
            value["theta"], value["phi"] = coords
    return merged


def _category_counts(coordinates: Dict[str, Tuple[float, float]]) -> Counter:
    counts: Counter = Counter()
    for entity_id in coordinates:
        counts[entity_id.split("_", 1)[0]] += 1
    return counts


def _yaml_status() -> str:
    return "enabled" if yaml is not None else "skipped (PyYAML unavailable)"


if __name__ == "__main__":
    entity_coords = load_all_entities()
    metadata = load_entity_metadata()
    relations = load_relations()
    counts = _category_counts(entity_coords)
    print("✦ NPU dataset loader")
    print(f"Dataset root: {DATASETS_ROOT}")
    print(f"Files inventoried: {len(_inventory()['files'])}")
    print(f"YAML: {_yaml_status()}")
    print(f"Entities registered: {len(entity_coords)}")
    print(f"Relations loaded: {sum(len(v) for v in relations.values())}")
    print("Categories:")
    for category, count in sorted(counts.items()):
        print(f"  {category:14s} {count}")
    print()
    print("Sample coordinates:")
    for entity_id in sorted(entity_coords)[:15]:
        theta, phi = entity_coords[entity_id]
        meta = metadata[entity_id]
        print(f"  {entity_id:32s} θ={theta:.3f} φ={phi:.3f}  [{meta['theta_authority']} | {meta['phi_authority']}]")
