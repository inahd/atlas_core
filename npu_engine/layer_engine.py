"""
layer_engine.py — S-layer dataset mapping for the Atlas NPU.

Maps datasets to their canonical S-layer:
  S0 = Bindu / Source — Vaishnava philosophy, paramparā, ontology
  S1 = Archetype — Deities, grahas, Nitya Devīs, bīja
  S2 = Sound — Svara, rāga, tāla, chandas, gandharva
  S3 = Rhythm — Pañcāṅga, nakshatra, tithi, jyotish
  S4 = Geometry — Vāstu, yantra, mahābhūta, sacred geometry
  S5 = Nature — Āyurveda, plants, marma, ratna, ecology
  S6 = Līlā — 64 arts, ritual, federation

Reads datasets/layer_mapping.csv for the mapping.
Does NOT compute coherence — only indexes and retrieves.
"""

import csv
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from .datasets import _load_csv, DATASETS_ROOT


LAYER_NAMES = {
    "S0": "Bindu · Source",
    "S1": "Archetype · Deity",
    "S2": "Sound · Nāda",
    "S3": "Rhythm · Kāla",
    "S4": "Geometry · Vāstu",
    "S5": "Nature · Āyurveda",
    "S6": "Līlā · Arts",
}

LAYER_DOMAINS = {
    "S0": ["philosophy", "textual"],
    "S1": ["deity"],
    "S2": ["sound"],
    "S3": ["rhythm"],
    "S4": ["geometry"],
    "S5": ["nature"],
    "S6": ["lila"],
}


@lru_cache(maxsize=1)
def load_layer_mapping() -> Dict[str, List[Dict[str, str]]]:
    """Load layer_mapping.csv → {layer: [{dataset_path, domain, description}]}."""
    mapping_path = DATASETS_ROOT / "layer_mapping.csv"
    if not mapping_path.exists():
        return {}

    by_layer: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for row in _load_csv(mapping_path):
        layer = row.get("layer", "").strip()
        path = row.get("dataset_path", "").strip()
        if layer and path:
            by_layer[layer].append({
                "path": path,
                "domain": row.get("domain", ""),
                "description": row.get("description", ""),
            })

    return dict(by_layer)


def datasets_for_layer(layer: str) -> List[Dict[str, str]]:
    """Return dataset entries for a given S-layer."""
    mapping = load_layer_mapping()
    return mapping.get(layer, [])


def load_layer_data(layer: str) -> List[Dict[str, Any]]:
    """Load all rows from all datasets in a layer.

    Returns list of dicts, each tagged with _source and _layer.
    """
    entries = datasets_for_layer(layer)
    all_rows = []

    for entry in entries:
        path = DATASETS_ROOT / entry["path"]
        if not path.exists():
            continue
        suffix = path.suffix.lower()
        if suffix == ".csv":
            try:
                rows = _load_csv(path)
                for row in rows:
                    row["_source"] = entry["path"]
                    row["_layer"] = layer
                    row["_domain"] = entry["domain"]
                all_rows.extend(rows)
            except Exception:
                pass

    return all_rows


def layer_summary(layer: str) -> Dict[str, Any]:
    """Summary of a layer's dataset coverage."""
    entries = datasets_for_layer(layer)
    row_count = 0
    domains = set()
    files = []

    for entry in entries:
        path = DATASETS_ROOT / entry["path"]
        domains.add(entry["domain"])
        exists = path.exists()
        if exists and path.suffix.lower() == ".csv":
            try:
                rows = _load_csv(path)
                row_count += len(rows)
            except Exception:
                rows = []
        else:
            rows = []
        files.append({
            "path": entry["path"],
            "domain": entry["domain"],
            "exists": exists,
            "rows": len(rows),
            "description": entry["description"],
        })

    return {
        "layer": layer,
        "name": LAYER_NAMES.get(layer, layer),
        "datasets": len(entries),
        "files": files,
        "total_rows": row_count,
        "domains": sorted(domains),
    }


def all_layer_summaries() -> List[Dict[str, Any]]:
    """Summary for all 7 layers."""
    return [layer_summary(f"S{i}") for i in range(7)]


def entity_layer(entity_id: str) -> Optional[str]:
    """Guess which layer an entity belongs to based on its category prefix."""
    prefix = entity_id.split("_")[0] if "_" in entity_id else entity_id

    # Category → layer mapping
    _CAT_LAYER = {
        "tattva": "S0", "parampara": "S0", "bhava": "S0", "rasa_siddhanta": "S0",
        "deity": "S1", "devi": "S1", "graha": "S1", "bija": "S1",
        "raga": "S2", "tala": "S2", "svara": "S2", "shruti": "S2",
        "nakshatra": "S3", "tithi": "S3", "vara": "S3",
        "vastu": "S4", "yantra": "S4", "geometry": "S4",
        "plant": "S5", "herb": "S5", "marma": "S5", "dosha": "S5",
        "amidha": "S5", "ratna": "S5",
        "art": "S6", "ritual": "S6", "concept": "S6",
    }

    return _CAT_LAYER.get(prefix)
