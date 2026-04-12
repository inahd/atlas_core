#!/usr/bin/env python3
"""COR-002: Populate corpus registry tradition and language fields.

Reads datasets/sources/corpus_registry.json, derives tradition + authority
from the subdirectory path, and writes the updated registry back.
Also registers any unregistered JSONL files found in the sources tree.
"""

import json
import os
import glob

REGISTRY_PATH = "datasets/sources/corpus_registry.json"

TRADITION_MAP = {
    "gaudiya":   {"tradition": "gaudiya_vaishnava", "authority": 0.99},
    "jyotish":   {"tradition": "jyotish",           "authority": 0.95},
    "ayurveda":  {"tradition": "ayurveda",           "authority": 0.95},
    "vastu":     {"tradition": "vastu",              "authority": 0.90},
    "vedic":     {"tradition": "vedic",              "authority": 0.95},
    "yoga":      {"tradition": "yoga_tantra",        "authority": 0.85},
    "cosmology": {"tradition": "puranic",            "authority": 0.90},
    "epics":     {"tradition": "itihasa",            "authority": 0.90},
    "dharma":    {"tradition": "dharmashastra",      "authority": 0.85},
    "music":     {"tradition": "sangita",            "authority": 0.85},
}


def derive_tradition(chunks_path: str) -> dict:
    """Extract tradition and authority from the subdirectory in chunks_path."""
    # Path like 'datasets/sources/ayurveda/foo_chunks.jsonl'
    parts = chunks_path.replace("datasets/sources/", "").split("/")
    subdir = parts[0] if len(parts) > 1 else ""
    return TRADITION_MAP.get(subdir, {"tradition": "general", "authority": 0.80})


def derive_language(chunks_path: str) -> str:
    """Derive language from filename pattern: _sa_ → 'sa', _en_ → 'en', else 'en'."""
    basename = os.path.basename(chunks_path)
    if "_sa_" in basename or basename.endswith("_sa_chunks.jsonl") or "_sa." in basename or basename.startswith("sa_"):
        return "sa"
    # Also check for explicit sa suffix before _chunks
    name_no_ext = basename.replace("_chunks.jsonl", "").replace(".jsonl", "")
    if name_no_ext.endswith("_sa"):
        return "sa"
    if "_en_" in basename:
        return "en"
    return "en"


def count_chunks(jsonl_path: str) -> int:
    """Count lines in a JSONL file."""
    if not os.path.exists(jsonl_path):
        return 0
    with open(jsonl_path) as f:
        return sum(1 for _ in f)


def main():
    with open(REGISTRY_PATH) as f:
        registry = json.load(f)

    print(f"Loaded {len(registry)} entries from {REGISTRY_PATH}")

    # Step 1: Populate tradition and authority for all existing entries
    updated = 0
    for entry in registry:
        chunks_path = entry.get("chunks_path", "")
        info = derive_tradition(chunks_path)
        entry["tradition"] = info["tradition"]
        entry["authority"] = info["authority"]
        # Ensure language field uses derive_language as fallback
        if not entry.get("lang") or entry["lang"] == "?":
            entry["lang"] = derive_language(chunks_path)
        updated += 1

    print(f"Updated tradition/authority for {updated} entries")

    # Step 2: Find and register unregistered JSONL files
    registered_paths = {e.get("chunks_path", "") for e in registry}
    actual = glob.glob("datasets/sources/**/*.jsonl", recursive=True)
    added = 0

    for fpath in sorted(actual):
        if fpath not in registered_paths:
            basename = os.path.basename(fpath)
            name_no_ext = basename.replace("_chunks.jsonl", "").replace(".jsonl", "")
            subdir = fpath.replace("datasets/sources/", "").split("/")[0]
            info = derive_tradition(fpath)
            lang = derive_language(fpath)

            # Determine layer_refs from tradition
            layer_map = {
                "gaudiya_vaishnava": ["S0", "S1"],
                "jyotish": ["S3"],
                "ayurveda": ["S5"],
                "vastu": ["S4"],
                "vedic": ["S0", "S2"],
                "yoga_tantra": ["S5", "S6"],
                "puranic": ["S0", "S1"],
                "itihasa": ["S0", "S1"],
                "dharmashastra": ["S6"],
                "sangita": ["S2"],
            }

            entry = {
                "id": name_no_ext,
                "title": name_no_ext.replace("_", " ").title(),
                "family": subdir.title(),
                "domain": subdir,
                "lang": lang,
                "layer_refs": layer_map.get(info["tradition"], ["S0"]),
                "chunks_path": fpath,
                "raw_path": "",
                "chunks": count_chunks(fpath),
                "status": "cached",
                "name": name_no_ext.replace("_", " ").title(),
                "tradition": info["tradition"],
                "authority": info["authority"],
            }
            registry.append(entry)
            added += 1
            print(f"  Added: {fpath} ({entry['tradition']}, {lang}, {entry['chunks']} chunks)")

    # Step 3: Write back
    with open(REGISTRY_PATH, "w") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)

    print(f"\nDone. {len(registry)} total entries ({added} new). Written to {REGISTRY_PATH}")

    # Verification
    blank = [e for e in registry if not e.get("tradition") or e["tradition"] == "?"]
    print(f"Blank tradition entries: {len(blank)} of {len(registry)}")


if __name__ == "__main__":
    main()
