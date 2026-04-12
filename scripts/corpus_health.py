#!/usr/bin/env python3
"""Quick corpus health check — run anytime to verify registry vs filesystem."""
import json, os, glob, sys
from collections import Counter

REGISTRY_PATH = os.path.join(os.path.dirname(__file__), '..', 'datasets', 'sources', 'corpus_registry.json')
SOURCES_DIR = os.path.join(os.path.dirname(__file__), '..', 'datasets', 'sources')


def get_corpus_stats():
    """Return corpus health as a dict — importable by kernel or dashboard."""
    reg_path = os.path.normpath(REGISTRY_PATH)
    sources_dir = os.path.normpath(SOURCES_DIR)

    if not os.path.exists(reg_path):
        return {"error": "corpus_registry.json not found"}

    with open(reg_path) as f:
        entries = json.load(f)

    # Normalize chunk paths relative to datasets/sources/
    def rel_path(cp):
        if cp.startswith('datasets/sources/'):
            return cp[len('datasets/sources/'):]
        return cp

    registered_paths = {rel_path(e.get('chunks_path', '')) for e in entries}

    # Actual JSONL files on disk
    actual = set()
    for fp in glob.glob(os.path.join(sources_dir, '**', '*.jsonl'), recursive=True):
        actual.add(os.path.relpath(fp, sources_dir))

    unregistered = sorted(actual - registered_paths)
    missing = sorted(registered_paths - actual)

    # Per-entry checks
    zero_chunk = []
    chunk_mismatch = []
    for e in entries:
        eid = e.get('id', '?')
        declared = e.get('chunks', 0)
        cp = rel_path(e.get('chunks_path', ''))
        full = os.path.join(sources_dir, cp)
        if os.path.exists(full):
            actual_count = sum(1 for _ in open(full))
            if declared == 0 and actual_count == 0:
                zero_chunk.append(eid)
            elif declared == 0 and actual_count > 0:
                chunk_mismatch.append({"id": eid, "declared": 0, "actual": actual_count})
            elif actual_count > 0 and abs(actual_count - declared) / max(declared, 1) > 0.1:
                chunk_mismatch.append({"id": eid, "declared": declared, "actual": actual_count})

    # Tradition breakdown
    traditions = Counter(e.get('tradition', 'unknown') for e in entries)
    total_chunks = sum(e.get('chunks', 0) for e in entries)

    return {
        "total_entries": len(entries),
        "total_chunks": total_chunks,
        "traditions": dict(sorted(traditions.items())),
        "unregistered": unregistered,
        "missing_on_disk": missing,
        "zero_chunk_entries": zero_chunk,
        "chunk_mismatches": chunk_mismatch,
        "healthy": len(unregistered) == 0 and len(missing) == 0 and len(zero_chunk) == 0,
    }


def print_report(stats):
    """Pretty-print corpus health to stdout."""
    print("=== Corpus Health ===\n")
    print(f"  Entries:       {stats['total_entries']}")
    print(f"  Total chunks:  {stats['total_chunks']}")
    print(f"  Traditions:    {len(stats['traditions'])}")
    print()

    print("  Tradition breakdown:")
    for t, c in stats['traditions'].items():
        print(f"    {t:25s} {c:3d} texts")
    print()

    if stats['unregistered']:
        print(f"  UNREGISTERED ({len(stats['unregistered'])} files on disk, not in registry):")
        for f in stats['unregistered']:
            print(f"    - {f}")
    else:
        print("  Unregistered files: 0")

    if stats['missing_on_disk']:
        print(f"  MISSING ({len(stats['missing_on_disk'])} in registry, not on disk):")
        for f in stats['missing_on_disk']:
            print(f"    - {f}")
    else:
        print("  Missing on disk:    0")

    if stats['zero_chunk_entries']:
        print(f"  ZERO-CHUNK entries: {stats['zero_chunk_entries']}")
    else:
        print("  Zero-chunk entries: 0")

    if stats['chunk_mismatches']:
        print(f"\n  CHUNK MISMATCHES ({len(stats['chunk_mismatches'])}):")
        for m in stats['chunk_mismatches']:
            print(f"    {m['id']}: declared={m['declared']} actual={m['actual']}")
    else:
        print("  Chunk mismatches:   0")

    print()
    status = "HEALTHY" if stats['healthy'] else "NEEDS ATTENTION"
    print(f"  Status: {status}")


if __name__ == '__main__':
    stats = get_corpus_stats()
    if 'error' in stats:
        print(f"ERROR: {stats['error']}")
        sys.exit(1)
    print_report(stats)
