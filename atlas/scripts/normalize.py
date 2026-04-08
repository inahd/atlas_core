#!/usr/bin/env python3
"""Normalize a registered source to UTF-8 plain text.

Usage:
    python scripts/normalize.py --id rig_veda_oxford_1896

Reads the source file registered for this id, normalizes it to clean
UTF-8 plain text, writes to normalized/<id>.txt, and updates the
registry entry.

Normalization steps:
  - Decode to UTF-8 (replace errors)
  - Strip control characters except newlines
  - Normalize Unicode (NFC)
  - Collapse runs of 3+ blank lines to 2
  - Strip trailing whitespace per line
  - Ensure trailing newline
"""

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

ATLAS_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = ATLAS_ROOT / "registry" / "corpus_registry.jsonl"
NORMALIZED_DIR = ATLAS_ROOT / "normalized"


def load_registry():
    entries = {}
    if REGISTRY_PATH.exists():
        for line in REGISTRY_PATH.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            entries[entry["id"]] = entry
    return entries


def save_registry(entries):
    """Rewrite the full registry (preserves order by id)."""
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REGISTRY_PATH, "w") as f:
        for entry in entries.values():
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def normalize_text(raw: str) -> str:
    """Clean raw text to normalized UTF-8."""
    # NFC normalization
    text = unicodedata.normalize("NFC", raw)

    # Strip control chars except \n \t
    text = re.sub(r"[^\S\n\t]", " ", text)  # non-newline whitespace → space
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    # Strip trailing whitespace per line
    lines = [line.rstrip() for line in text.splitlines()]
    text = "\n".join(lines)

    # Collapse 3+ blank lines to 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Strip leading/trailing whitespace, ensure trailing newline
    text = text.strip() + "\n"

    return text


def assess_readability(text: str) -> str:
    """Quick heuristic readability label."""
    lines = text.splitlines()
    if not lines:
        return "empty"
    avg_len = sum(len(l) for l in lines) / len(lines)
    alpha_ratio = sum(c.isalpha() for c in text) / max(len(text), 1)
    if alpha_ratio < 0.3:
        return "low_alpha"
    if avg_len < 10:
        return "short_lines"
    if avg_len > 500:
        return "dense"
    return "readable"


def main():
    parser = argparse.ArgumentParser(description="Normalize a registered source.")
    parser.add_argument("--id", required=True, help="Text id from registry")
    args = parser.parse_args()

    entries = load_registry()
    if args.id not in entries:
        print(f"error: '{args.id}' not in registry", file=sys.stderr)
        sys.exit(1)

    entry = entries[args.id]
    source_path = ATLAS_ROOT / entry["source_path"]

    if not source_path.exists():
        print(f"error: source not found: {source_path}", file=sys.stderr)
        sys.exit(1)

    # Read raw
    try:
        raw = source_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"error reading source: {e}", file=sys.stderr)
        sys.exit(1)

    # Normalize
    text = normalize_text(raw)
    readability = assess_readability(text)

    # Write
    NORMALIZED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = NORMALIZED_DIR / f"{args.id}.txt"
    out_path.write_text(text, encoding="utf-8")

    # Update registry
    rel_path = f"normalized/{args.id}.txt"
    entry["normalized_path"] = rel_path
    entry["status"] = "normalized"
    entry["readability"] = readability
    save_registry(entries)

    line_count = len(text.splitlines())
    char_count = len(text)
    print(f"normalized: {args.id}")
    print(f"  output: {rel_path}")
    print(f"  lines: {line_count}, chars: {char_count}")
    print(f"  readability: {readability}")


if __name__ == "__main__":
    main()
