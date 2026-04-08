"""
pfaf_lookup.py — PFAF SQLite query utility
============================================
Queries the PFAF (Plants for a Future) database for raw plant data.

Returns ethnobotanical/horticultural data ONLY.
This is NOT Āyurveda. NOT Jyotiṣa. NOT synthesis.
Raw observational source data from PFAF.

Attestation: OBSERVED:PFAF

Usage:
    from datasets.plants.pfaf_lookup import get_pfaf_plant
    data = get_pfaf_plant("Ocimum tenuiflorum")
"""

import sqlite3
from pathlib import Path

_DB = Path(__file__).resolve().parent.parent / "datasets/plants/pfaf.sqlite"

# Columns relevant to Atlas (minimal set)
_ATLAS_COLUMNS = [
    "latin_name", "common_name", "family", "synonyms",
    "habit", "height", "hardiness", "growth", "soil", "shade", "moisture",
    "edibility_rating", "medicinal_rating", "other_uses_rating",
    "range", "known_hazards",
    "edible_uses", "medicinal_uses", "other_uses",
    "cultivation_details", "propagation", "habitats",
]


def get_pfaf_plant(latin_name):
    """Query PFAF SQLite for a single plant by latin name.

    Returns dict with raw PFAF data + attestation.
    Returns None if not found.
    """
    if not _DB.exists():
        return None
    conn = sqlite3.connect(str(_DB))
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT * FROM plants WHERE latin_name = ? LIMIT 1",
            (latin_name,)
        ).fetchone()
        if not row:
            # fuzzy match
            row = conn.execute(
                "SELECT * FROM plants WHERE latin_name LIKE ? LIMIT 1",
                (f"%{latin_name}%",)
            ).fetchone()
        if not row:
            return None
        data = {col: row[col] for col in _ATLAS_COLUMNS if col in row.keys()}
        data["source"] = "PFAF database · pfaf.org"
        data["attestation"] = "OBSERVED:PFAF"
        data["note"] = "Ethnobotanical data. NOT Āyurveda. NOT Jyotiṣa."
        return data
    finally:
        conn.close()


def search_pfaf(query, limit=10):
    """Search PFAF by latin or common name. Returns list of dicts."""
    if not _DB.exists():
        return []
    conn = sqlite3.connect(str(_DB))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT latin_name, common_name, family, edibility_rating, medicinal_rating "
            "FROM plants WHERE latin_name LIKE ? OR common_name LIKE ? LIMIT ?",
            (f"%{query}%", f"%{query}%", limit)
        ).fetchall()
        return [
            {"latin_name": r["latin_name"], "common_name": r["common_name"],
             "family": r["family"], "edibility": r["edibility_rating"],
             "medicinal": r["medicinal_rating"],
             "attestation": "OBSERVED:PFAF"}
            for r in rows
        ]
    finally:
        conn.close()


if __name__ == "__main__":
    import json
    result = get_pfaf_plant("Ocimum tenuiflorum")
    if result:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("Not found")
