#!/usr/bin/env python3
"""Chunk a normalized text into paragraph-level segments.

Usage:
    python scripts/chunk.py --id rig_veda_oxford_1896

Reads normalized/<id>.txt, splits into chunks by paragraph blocks
(separated by blank lines), writes chunks/<id>/<ordinal>.json.

Each chunk:
  {
    "chunk_id": "<id>_0001",
    "text_id": "<id>",
    "ordinal": 1,
    "text": "...",
    "char_count": 420,
    "tags": [],
    "confidence": 1.0
  }
"""

import argparse
import json
import re
import sys
from pathlib import Path

ATLAS_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = ATLAS_ROOT / "registry" / "corpus_registry.jsonl"
NORMALIZED_DIR = ATLAS_ROOT / "normalized"
CHUNKS_DIR = ATLAS_ROOT / "chunks"

# Chunks smaller than this get merged with the next
MIN_CHUNK_CHARS = 40
# Chunks larger than this get split at sentence boundaries
MAX_CHUNK_CHARS = 2000


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
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REGISTRY_PATH, "w") as f:
        for entry in entries.values():
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def split_paragraphs(text: str) -> list:
    """Split on blank lines, producing paragraph blocks."""
    blocks = re.split(r"\n\s*\n", text)
    blocks = [b.strip() for b in blocks if b.strip()]
    return blocks


def split_long_block(block: str, max_chars: int) -> list:
    """Split a long block at sentence boundaries."""
    sentences = re.split(r"(?<=[.!?।॥])\s+", block)
    chunks = []
    current = ""
    for s in sentences:
        if current and len(current) + len(s) + 1 > max_chars:
            chunks.append(current.strip())
            current = s
        else:
            current = (current + " " + s).strip() if current else s
    if current:
        chunks.append(current.strip())
    return chunks


def chunk_text(text: str) -> list:
    """Produce final chunk list from normalized text."""
    paragraphs = split_paragraphs(text)

    # Merge tiny paragraphs with next
    merged = []
    buffer = ""
    for para in paragraphs:
        if buffer:
            buffer = buffer + "\n\n" + para
            if len(buffer) >= MIN_CHUNK_CHARS:
                merged.append(buffer)
                buffer = ""
        elif len(para) < MIN_CHUNK_CHARS:
            buffer = para
        else:
            merged.append(para)
    if buffer:
        if merged:
            merged[-1] = merged[-1] + "\n\n" + buffer
        else:
            merged.append(buffer)

    # Split oversized paragraphs
    final = []
    for para in merged:
        if len(para) > MAX_CHUNK_CHARS:
            final.extend(split_long_block(para, MAX_CHUNK_CHARS))
        else:
            final.append(para)

    return final


def main():
    parser = argparse.ArgumentParser(description="Chunk a normalized text.")
    parser.add_argument("--id", required=True, help="Text id from registry")
    args = parser.parse_args()

    entries = load_registry()
    if args.id not in entries:
        print(f"error: '{args.id}' not in registry", file=sys.stderr)
        sys.exit(1)

    entry = entries[args.id]
    norm_path = ATLAS_ROOT / "normalized" / f"{args.id}.txt"

    if not norm_path.exists():
        print(f"error: normalized file not found: {norm_path}", file=sys.stderr)
        print("  run: python scripts/normalize.py --id " + args.id)
        sys.exit(1)

    text = norm_path.read_text(encoding="utf-8")
    chunks = chunk_text(text)

    # Write chunks
    out_dir = CHUNKS_DIR / args.id
    out_dir.mkdir(parents=True, exist_ok=True)

    # Clear old chunks
    for old in out_dir.glob("*.json"):
        old.unlink()

    for i, chunk_text_str in enumerate(chunks):
        ordinal = i + 1
        chunk_id = f"{args.id}_{ordinal:04d}"
        chunk = {
            "chunk_id": chunk_id,
            "text_id": args.id,
            "ordinal": ordinal,
            "text": chunk_text_str,
            "char_count": len(chunk_text_str),
            "tags": [],
            "confidence": 1.0,
        }
        chunk_path = out_dir / f"{ordinal:04d}.json"
        chunk_path.write_text(
            json.dumps(chunk, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    # Update registry
    rel_path = f"chunks/{args.id}"
    entry["chunks_path"] = rel_path
    entry["status"] = "chunked"
    save_registry(entries)

    print(f"chunked: {args.id}")
    print(f"  output: {rel_path}/")
    print(f"  chunks: {len(chunks)}")
    total_chars = sum(len(c) for c in chunks)
    avg = total_chars // max(len(chunks), 1)
    print(f"  avg size: {avg} chars")


if __name__ == "__main__":
    main()
