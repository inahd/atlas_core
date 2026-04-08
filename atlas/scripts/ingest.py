#!/usr/bin/env python3
"""Register a raw source into the corpus registry.

Usage:
    python scripts/ingest.py \
        --id rig_veda_oxford_1896 \
        --title "Rig Veda (Oxford 1896)" \
        --family veda \
        --layer S0 \
        --language en \
        --source sources/rig_veda/rig_veda_oxford_1896.txt \
        --source-type plain_text \
        --provenance public_domain

Writes one JSONL line to registry/corpus_registry.jsonl.
Skips if id already registered. Creates directories as needed.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ATLAS_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = ATLAS_ROOT / "registry" / "corpus_registry.jsonl"


def load_registry():
    """Load all registry entries, keyed by id."""
    entries = {}
    if REGISTRY_PATH.exists():
        for line in REGISTRY_PATH.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            entries[entry["id"]] = entry
    return entries


def save_entry(entry):
    """Append one entry to the registry file."""
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REGISTRY_PATH, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Register a raw corpus source.")
    parser.add_argument("--id", required=True, help="Unique text identifier (snake_case)")
    parser.add_argument("--title", required=True, help="Human-readable title")
    parser.add_argument("--family", required=True, help="Text family (veda, purana, ayurveda, ...)")
    parser.add_argument("--layer", required=True, help="S-layer reference (S0, S1, ...)")
    parser.add_argument("--language", required=True, help="Language code (en, sa, ...)")
    parser.add_argument("--source", required=True, help="Path to raw source file, relative to atlas/")
    parser.add_argument("--source-type", required=True,
                        choices=["plain_text", "html", "pdf", "jsonl", "xml"],
                        help="Format of the source file")
    parser.add_argument("--provenance", required=True, help="Origin (public_domain, archive_org, gretil, ...)")
    parser.add_argument("--notes", default="", help="Optional quality notes")
    args = parser.parse_args()

    # Check source file exists
    source_path = ATLAS_ROOT / args.source
    if not source_path.exists():
        print(f"error: source file not found: {source_path}", file=sys.stderr)
        sys.exit(1)

    # Check for duplicate
    registry = load_registry()
    if args.id in registry:
        print(f"skip: '{args.id}' already registered")
        sys.exit(0)

    entry = {
        "id": args.id,
        "title": args.title,
        "family": args.family,
        "layer_refs": [args.layer],
        "language": args.language,
        "source_path": args.source,
        "normalized_path": "",
        "chunks_path": "",
        "source_type": args.source_type,
        "provenance": args.provenance,
        "status": "registered",
        "readability": "",
        "quality_notes": args.notes,
        "registered_at": datetime.now(timezone.utc).isoformat(),
    }

    save_entry(entry)
    print(f"registered: {args.id} ({args.title})")
    print(f"  source: {args.source}")
    print(f"  family: {args.family} / {args.layer}")
    print(f"  status: registered")


if __name__ == "__main__":
    main()
