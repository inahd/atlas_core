"""
Step 1: revert the bad dedup moves (read manifest, move every file in
_duplicates/<tier>/<name> back to <tier>/<name>).
Step 2: re-run dedup with a fix:
  - PDFs whose extracted text volume is below MIN_TEXT_CHARS (1000 non-
    whitespace chars over first 150 pages) are flagged as 'low_text' and
    NOT grouped by content hash (their fingerprint would be empty/garbage).
  - Low-text PDFs fall back to a file-bytes SHA256 dedup: catches truly
    byte-identical scanned PDFs, leaves distinct scans alone.
  - Adds a separate file_bytes_hash field as well, so any byte-identical
    duplicates are caught regardless of text extraction.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sys
import time
from collections import defaultdict
from pathlib import Path

import fitz

ROOT = Path("/home/inahd/atlas_core")
CORPUS = ROOT / "corpus/teslatech_lineage"
DUPLICATES_DIR = CORPUS / "_duplicates"
PIPELINE = ROOT / "research/corpus_analysis/teslatech_lineage/pipeline"
MANIFEST = PIPELINE / "dedup_manifest.json"
REPORT = PIPELINE / "dedup_report.md"

FIRST_PAGES = 150
MIN_TEXT_CHARS = 1000           # below this, treat as image-only PDF
MIN_DISTINCT_WORDS = 100        # below this, treat as watermark-only / low-vocabulary
PAGE_COUNT_TOL_RATIO = 1.10     # accept text-hash union only if page counts within 10%
PAGE_COUNT_TOL_ABS = 20         # or within absolute 20 pages of each other

WORD_RE = re.compile(r"[A-Za-z]+")


def revert():
    if not DUPLICATES_DIR.exists():
        print("[revert] no _duplicates/ dir; nothing to revert")
        return
    moved = 0
    for path in DUPLICATES_DIR.rglob("*.pdf"):
        rel = path.relative_to(DUPLICATES_DIR)
        target = CORPUS / rel
        if target.exists():
            print(f"[revert] target exists, leaving in _duplicates: {rel}")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(path), str(target))
        moved += 1
    print(f"[revert] moved {moved} files back from _duplicates/")
    # Remove now-empty tier subdirs in _duplicates
    for sub in sorted(DUPLICATES_DIR.iterdir()):
        if sub.is_dir():
            remaining = list(sub.rglob("*"))
            if not remaining:
                sub.rmdir()


# ── reuse extract logic from dedup.py inlined ──

def extract_pages(pdf_path: Path):
    try:
        doc = fitz.open(str(pdf_path))
    except Exception:
        return [], 0
    try:
        pc = doc.page_count
    except Exception:
        try: doc.close()
        except: pass
        return [], 0
    pages = []
    for i in range(pc):
        try:
            page = doc.load_page(i)
            pages.append(page.get_text("text") or "")
        except Exception:
            pages.append("")
    try: doc.close()
    except: pass
    return pages, pc


def normalize_ws(s):
    return re.sub(r"\s+", " ", s).strip()


def file_bytes_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def filename_clean_score(name):
    base = name.rsplit(".", 1)[0]
    spaces = base.count(" ")
    hyphens = base.count("-")
    runtogether = len(re.findall(r"[a-z][A-Z]", base))
    return spaces - 0.4 * hyphens - 0.6 * runtogether


def root_of(parent, x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


def union(parent, a, b):
    ra, rb = root_of(parent, a), root_of(parent, b)
    if ra != rb:
        parent[ra] = rb


def dedup():
    pdfs = sorted([p for p in CORPUS.rglob("*.pdf") if "_duplicates" not in p.parts])
    print(f"[scan] {len(pdfs)} PDFs in corpus/teslatech_lineage/ (post-revert)")

    records = []
    for i, pdf in enumerate(pdfs):
        pages, pc = extract_pages(pdf)
        bytes_hash = file_bytes_sha256(pdf)
        if pc == 0:
            records.append({
                "path": str(pdf),
                "rel": str(pdf.relative_to(CORPUS)),
                "tier": pdf.relative_to(CORPUS).parts[0],
                "page_count": 0,
                "full_hash": None,
                "first150_hash": None,
                "bytes_hash": bytes_hash,
                "text_chars": 0,
                "low_text": True,
                "extract_failed": True,
            })
            continue

        full_text = "\f".join(pages)
        full_text_clean = re.sub(r"\s+", "", full_text)
        text_chars = len(full_text_clean)

        first_n = min(FIRST_PAGES, pc)
        first_text = " ".join(normalize_ws(pages[k]) for k in range(first_n))
        first_text_clean = re.sub(r"\s+", "", first_text)

        # Distinct word count: catches watermark-only PDFs (e.g. "AETHERFORCE"
        # repeated thousands of times) that pass char threshold but have no
        # vocabulary. WORD_RE matches A-Z only, so non-ASCII watermarks count 0.
        distinct_words = len({w.lower() for w in WORD_RE.findall(full_text)})

        low_text = (text_chars < MIN_TEXT_CHARS) or (distinct_words < MIN_DISTINCT_WORDS)

        full_hash = (None if low_text
                     else hashlib.sha256(full_text.encode("utf-8", errors="ignore")).hexdigest())
        first150_hash = (None if low_text or len(first_text_clean) < MIN_TEXT_CHARS
                         else hashlib.sha256(first_text.encode("utf-8", errors="ignore")).hexdigest())

        records.append({
            "path": str(pdf),
            "rel": str(pdf.relative_to(CORPUS)),
            "tier": pdf.relative_to(CORPUS).parts[0],
            "page_count": pc,
            "full_hash": full_hash,
            "first150_hash": first150_hash,
            "bytes_hash": bytes_hash,
            "text_chars": text_chars,
            "distinct_words": distinct_words,
            "low_text": low_text,
            "extract_failed": False,
        })
        if (i + 1) % 25 == 0 or i == len(pdfs) - 1:
            print(f"  [{i+1}/{len(pdfs)}] elapsed scan ongoing")

    # ── union-find ──
    parent = {r["path"]: r["path"] for r in records}
    rec_by_path = {r["path"]: r for r in records}

    def page_compatible(a_path, b_path):
        """True iff page counts are within tolerance — guard against false
        text-hash unions of different books that share boilerplate/watermark."""
        a = rec_by_path[a_path]["page_count"]
        b = rec_by_path[b_path]["page_count"]
        if a == 0 or b == 0:
            return True  # extraction-failed; fall back to other criteria
        lo, hi = min(a, b), max(a, b)
        return (hi - lo) <= PAGE_COUNT_TOL_ABS or (hi / lo) <= PAGE_COUNT_TOL_RATIO

    by_full = defaultdict(list)
    by_first = defaultdict(list)
    by_bytes = defaultdict(list)
    for r in records:
        if r["full_hash"]:
            by_full[r["full_hash"]].append(r["path"])
        if r["first150_hash"]:
            by_first[r["first150_hash"]].append(r["path"])
        # Bytes hash: always grouped (catches byte-identical files even if scan-only)
        by_bytes[r["bytes_hash"]].append(r["path"])

    # Text-hash unions are page-count-gated to prevent shared-boilerplate false positives.
    for paths in by_full.values():
        for p in paths[1:]:
            if page_compatible(paths[0], p):
                union(parent, paths[0], p)
    for paths in by_first.values():
        for p in paths[1:]:
            if page_compatible(paths[0], p):
                union(parent, paths[0], p)
    # Bytes-hash unions: trusted, no page check needed (byte-identical => same pages).
    for paths in by_bytes.values():
        for p in paths[1:]:
            union(parent, paths[0], p)

    groups = defaultdict(list)
    for r in records:
        root = root_of(parent, r["path"])
        groups[root].append(r)

    # ── canonical selection ──
    canonical_paths = set()
    duplicate_records = []
    group_summaries = []
    low_text_singletons = 0
    for root, members in groups.items():
        if len(members) == 1:
            canonical_paths.add(members[0]["path"])
            if members[0]["low_text"]:
                low_text_singletons += 1
            group_summaries.append({
                "group_size": 1,
                "canonical": members[0]["rel"],
                "duplicates": [],
                "tier": members[0]["tier"],
                "page_count": members[0]["page_count"],
                "low_text": members[0]["low_text"],
            })
            continue
        scored = sorted(
            members,
            key=lambda r: (-r["page_count"],
                           -filename_clean_score(Path(r["rel"]).name),
                           len(r["rel"])),
        )
        chosen = scored[0]
        rejected = scored[1:]
        canonical_paths.add(chosen["path"])
        duplicate_records.extend(rejected)
        group_summaries.append({
            "group_size": len(members),
            "canonical": chosen["rel"],
            "duplicates": [r["rel"] for r in rejected],
            "tier": chosen["tier"],
            "page_count": chosen["page_count"],
            "low_text": chosen["low_text"],
        })

    # Order summaries: large groups first
    group_summaries.sort(key=lambda g: (-g["group_size"], g["tier"]))

    # ── moves ──
    print(f"[move] {len(duplicate_records)} duplicates → _duplicates/")
    DUPLICATES_DIR.mkdir(exist_ok=True)
    for r in duplicate_records:
        src = Path(r["path"])
        dst_dir = DUPLICATES_DIR / r["tier"]
        dst_dir.mkdir(parents=True, exist_ok=True)
        dst = dst_dir / src.name
        if dst.exists():
            stem, suffix = src.stem, src.suffix
            j = 2
            while dst.exists():
                dst = dst_dir / f"{stem}__{j}{suffix}"
                j += 1
        shutil.move(str(src), str(dst))

    # ── per-tier counts ──
    by_tier_before = defaultdict(int)
    for r in records:
        by_tier_before[r["tier"]] += 1
    by_tier_after = defaultdict(int)
    for path in canonical_paths:
        for r in records:
            if r["path"] == path:
                by_tier_after[r["tier"]] += 1
                break

    # Low-text counts per tier (after dedup) — these are scan-only PDFs we can't text-fingerprint
    low_text_by_tier_after = defaultdict(int)
    for r in records:
        if r["path"] in canonical_paths and r["low_text"]:
            low_text_by_tier_after[r["tier"]] += 1

    manifest = {
        "scan_time_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_pdfs_scanned": len(records),
        "extract_failures": sum(1 for r in records if r["extract_failed"]),
        "low_text_pdfs_total": sum(1 for r in records if r["low_text"]),
        "unique_canonical_count": len(canonical_paths),
        "duplicates_moved": len(duplicate_records),
        "by_tier_before": dict(by_tier_before),
        "by_tier_after": dict(by_tier_after),
        "low_text_by_tier_after": dict(low_text_by_tier_after),
        "groups": group_summaries,
        "fix_note": (
            "Empty/low-text PDFs are NOT grouped by text-content hashes "
            "(would collapse all scan-only PDFs into one false group). "
            "They are still grouped via file-bytes SHA256, which catches "
            "truly byte-identical duplicates."
        ),
    }
    with open(MANIFEST, "w") as f:
        json.dump(manifest, f, indent=2)

    # report
    multi = [g for g in group_summaries if g["group_size"] > 1]
    lines = []
    lines.append("# Dedup report — teslatech_lineage corpus (FIXED)\n")
    lines.append(f"_Scan: {manifest['scan_time_utc']}_  ·  pymupdf {fitz.__version__}\n")
    lines.append("Note on the fix: a previous version of this script grouped scan-only PDFs "
                 "(image-only, no extractable text) into one giant false-duplicate group via "
                 "their identical empty text fingerprints. This version flags PDFs with "
                 f"<{MIN_TEXT_CHARS} non-whitespace chars of extracted text as `low_text` and "
                 "withholds them from text-content hashing. They are still deduplicated via "
                 "file-bytes SHA256, which catches truly byte-identical scan duplicates.\n")
    lines.append("## Summary\n")
    lines.append(f"- Scanned: **{len(records):,}** PDFs")
    lines.append(f"- Extraction failures: **{manifest['extract_failures']}**")
    lines.append(f"- PDFs flagged as low_text (scan-only, < {MIN_TEXT_CHARS} chars text): **{manifest['low_text_pdfs_total']}**")
    lines.append(f"- Unique canonical texts after dedup: **{len(canonical_paths):,}**")
    lines.append(f"- Duplicates moved to `_duplicates/<tier>/`: **{len(duplicate_records):,}**")
    lines.append(f"- Duplicate groups (size > 1): **{len(multi):,}**\n")

    lines.append("## Per-tier counts\n")
    lines.append("| Tier | Before | After | Removed | Low-text after |")
    lines.append("|---|---:|---:|---:|---:|")
    for t in sorted(set(by_tier_before) | set(by_tier_after)):
        b = by_tier_before.get(t, 0)
        a = by_tier_after.get(t, 0)
        lt = low_text_by_tier_after.get(t, 0)
        lines.append(f"| {t} | {b} | {a} | {b - a} | {lt} |")
    lines.append("")

    lines.append("## Duplicate groups (size > 1)\n")
    for g in multi:
        flag = "  [LOW-TEXT — bytes-hash dedup only]" if g.get("low_text") else ""
        lines.append(f"### {g['tier']} — group of {g['group_size']} ({g['page_count']} pp){flag}\n")
        lines.append(f"**Canonical:** `{g['canonical']}`\n")
        lines.append("**Duplicates moved:**")
        for d in g['duplicates']:
            lines.append(f"- `{d}`")
        lines.append("")

    with open(REPORT, "w") as f:
        f.write("\n".join(lines))
    print(f"[manifest] {MANIFEST.relative_to(ROOT)}")
    print(f"[report] {REPORT.relative_to(ROOT)}")
    print(f"\nBefore: {len(records):,}  After: {len(canonical_paths):,}  Moved: {len(duplicate_records):,}")
    print(f"Low-text (scan-only) after dedup: {sum(low_text_by_tier_after.values())}")


def main():
    t0 = time.time()
    print("=== STEP 1: revert previous (faulty) moves ===")
    revert()
    print()
    print("=== STEP 2: re-run dedup with low-text fix ===")
    dedup()
    print(f"\nTotal wall: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
