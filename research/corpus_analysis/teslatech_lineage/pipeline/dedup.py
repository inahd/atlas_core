"""
Dedup pass for the teslatech_lineage corpus.

Walks corpus/teslatech_lineage/, extracts text from every PDF via pymupdf,
computes:
  - SHA256 of full extracted text (catches byte-identical post-extraction)
  - First-150-page text fingerprint: first min(150, page_count) pages
    concatenated with whitespace normalized, then SHA256 (catches re-OCR
    near-duplicates)

Two PDFs are duplicates if EITHER hash matches. Builds union-find groups.
For each group, keeps the canonical copy (max page_count, then cleanest
filename score) and moves the rest to corpus/teslatech_lineage/_duplicates/
preserving the tier subdirectory.

NEVER deletes files. Only moves.

Outputs:
  - corpus/teslatech_lineage/_duplicates/<tier>/<filename>  (moved)
  - research/corpus_analysis/teslatech_lineage/pipeline/dedup_manifest.json
  - research/corpus_analysis/teslatech_lineage/pipeline/dedup_report.md
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

import fitz  # pymupdf

ROOT = Path("/home/inahd/atlas_core")
CORPUS = ROOT / "corpus/teslatech_lineage"
DUPLICATES_DIR = CORPUS / "_duplicates"
PIPELINE = ROOT / "research/corpus_analysis/teslatech_lineage/pipeline"
MANIFEST = PIPELINE / "dedup_manifest.json"
REPORT = PIPELINE / "dedup_report.md"

FIRST_PAGES = 150


def extract_pages(pdf_path: Path) -> tuple[list[str], int]:
    """Return (per-page text, page_count). Empty list on extraction failure.

    Resilient to malformed PDFs: catches exceptions on page iteration AND
    on per-page text fetch, returning whatever pages succeeded.
    """
    try:
        doc = fitz.open(str(pdf_path))
    except Exception:
        return [], 0
    try:
        pc = doc.page_count
    except Exception:
        try:
            doc.close()
        except Exception:
            pass
        return [], 0
    pages = []
    for i in range(pc):
        try:
            page = doc.load_page(i)
            pages.append(page.get_text("text") or "")
        except Exception:
            pages.append("")
    try:
        doc.close()
    except Exception:
        pass
    return pages, pc


def normalize_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def filename_clean_score(name: str) -> float:
    """Heuristic: more spaces / fewer hyphens / fewer run-together caps = cleaner."""
    base = name.rsplit(".", 1)[0]
    spaces = base.count(" ")
    hyphens = base.count("-")
    # run-together caps like "CPElectrical" or "amp" patterns
    runtogether = len(re.findall(r"[a-z][A-Z]", base))
    # prefer presence of " " over "-"
    return spaces - 0.4 * hyphens - 0.6 * runtogether


def parents_root(parent: dict, x: str) -> str:
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


def union(parent: dict, a: str, b: str):
    ra, rb = parents_root(parent, a), parents_root(parent, b)
    if ra != rb:
        parent[ra] = rb


def main():
    t0 = time.time()
    pdfs = sorted([p for p in CORPUS.rglob("*.pdf") if "_duplicates" not in p.parts])
    print(f"[scan] {len(pdfs)} PDFs in corpus/teslatech_lineage/")
    print(f"[extract] computing hashes...")

    records = []  # one per pdf
    for i, pdf in enumerate(pdfs):
        pages, pc = extract_pages(pdf)
        if pc == 0:
            print(f"  [skip] {pdf.relative_to(CORPUS)}  (extraction failed)")
            records.append({
                "path": str(pdf),
                "rel": str(pdf.relative_to(CORPUS)),
                "tier": pdf.relative_to(CORPUS).parts[0],
                "page_count": 0,
                "full_hash": None,
                "first150_hash": None,
                "size_bytes": pdf.stat().st_size,
                "extract_failed": True,
            })
            continue

        full_text = "\f".join(pages)
        full_hash = hashlib.sha256(full_text.encode("utf-8", errors="ignore")).hexdigest()

        first_n = min(FIRST_PAGES, pc)
        first_text = " ".join(normalize_ws(pages[k]) for k in range(first_n))
        first150_hash = hashlib.sha256(first_text.encode("utf-8", errors="ignore")).hexdigest()

        records.append({
            "path": str(pdf),
            "rel": str(pdf.relative_to(CORPUS)),
            "tier": pdf.relative_to(CORPUS).parts[0],
            "page_count": pc,
            "full_hash": full_hash,
            "first150_hash": first150_hash,
            "size_bytes": pdf.stat().st_size,
            "extract_failed": False,
        })
        if (i + 1) % 25 == 0 or i == len(pdfs) - 1:
            print(f"  [{i+1}/{len(pdfs)}] elapsed {time.time()-t0:.1f}s")

    # ── union-find on either hash ──
    print(f"[group] building duplicate groups via union-find")
    parent = {r["path"]: r["path"] for r in records if not r["extract_failed"]}

    by_full = defaultdict(list)
    by_first = defaultdict(list)
    for r in records:
        if r["extract_failed"]:
            continue
        by_full[r["full_hash"]].append(r["path"])
        by_first[r["first150_hash"]].append(r["path"])

    for paths in by_full.values():
        for p in paths[1:]:
            union(parent, paths[0], p)
    for paths in by_first.values():
        for p in paths[1:]:
            union(parent, paths[0], p)

    groups = defaultdict(list)
    for r in records:
        if r["extract_failed"]:
            groups[f"_failed::{r['path']}"].append(r)
            continue
        root = parents_root(parent, r["path"])
        groups[root].append(r)

    # ── pick canonical per group ──
    print(f"[canonical] choosing canonical per duplicate group")
    canonical_paths = set()
    duplicate_records = []  # records to move
    group_summaries = []
    for root, members in sorted(groups.items()):
        if root.startswith("_failed::"):
            # Keep failed ones in place; flagged in report.
            for m in members:
                canonical_paths.add(m["path"])
            continue
        if len(members) == 1:
            canonical_paths.add(members[0]["path"])
            group_summaries.append({
                "group_size": 1,
                "canonical": members[0]["rel"],
                "duplicates": [],
                "tier": members[0]["tier"],
                "page_count": members[0]["page_count"],
            })
            continue

        # Sort: max page_count desc, then filename_clean_score desc, then shortest path
        scored = sorted(
            members,
            key=lambda r: (-r["page_count"],
                           -filename_clean_score(Path(r["rel"]).name),
                           len(r["rel"])),
        )
        chosen = scored[0]
        rejected = scored[1:]
        canonical_paths.add(chosen["path"])
        for r in rejected:
            duplicate_records.append(r)
        group_summaries.append({
            "group_size": len(members),
            "canonical": chosen["rel"],
            "duplicates": [r["rel"] for r in rejected],
            "tier": chosen["tier"],
            "page_count": chosen["page_count"],
        })

    # ── execute moves ──
    print(f"[move] {len(duplicate_records)} duplicates → {DUPLICATES_DIR}/<tier>/")
    DUPLICATES_DIR.mkdir(exist_ok=True)
    for r in duplicate_records:
        src = Path(r["path"])
        # Mirror tier structure
        tier = r["tier"]
        dst_dir = DUPLICATES_DIR / tier
        dst_dir.mkdir(parents=True, exist_ok=True)
        dst = dst_dir / src.name
        # If a name collision in _duplicates (unlikely but possible), suffix
        if dst.exists():
            stem, suffix = src.stem, src.suffix
            i = 2
            while dst.exists():
                dst = dst_dir / f"{stem}__{i}{suffix}"
                i += 1
        shutil.move(str(src), str(dst))

    # ── per-tier counts before/after ──
    by_tier_before = defaultdict(int)
    for r in records:
        by_tier_before[r["tier"]] += 1
    by_tier_after = defaultdict(int)
    for path in canonical_paths:
        for r in records:
            if r["path"] == path:
                by_tier_after[r["tier"]] += 1
                break

    # ── manifest + report ──
    manifest = {
        "scan_time_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_pdfs_scanned": len(records),
        "extract_failures": sum(1 for r in records if r["extract_failed"]),
        "unique_canonical_count": len(canonical_paths),
        "duplicates_moved": len(duplicate_records),
        "duplicates_dir": str(DUPLICATES_DIR.relative_to(ROOT)),
        "by_tier_before": dict(by_tier_before),
        "by_tier_after": dict(by_tier_after),
        "groups": group_summaries,
    }
    with open(MANIFEST, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"[manifest] {MANIFEST.relative_to(ROOT)}")

    # Markdown report
    multi_groups = [g for g in group_summaries if g["group_size"] > 1]
    multi_groups.sort(key=lambda g: (-g["group_size"], g["tier"]))
    lines = []
    lines.append("# Dedup report — teslatech_lineage corpus\n")
    lines.append(f"_Scan: {manifest['scan_time_utc']}_  ·  pymupdf {fitz.__version__}\n")
    lines.append(f"## Summary\n")
    lines.append(f"- Scanned: **{len(records):,}** PDFs")
    lines.append(f"- Extraction failures: **{manifest['extract_failures']}**")
    lines.append(f"- Unique canonical texts after dedup: **{len(canonical_paths):,}**")
    lines.append(f"- Duplicates moved to `{manifest['duplicates_dir']}/<tier>/`: **{len(duplicate_records):,}**")
    lines.append(f"- Duplicate groups (size > 1): **{len(multi_groups):,}**\n")
    lines.append("## Per-tier counts\n")
    lines.append("| Tier | Before | After | Removed |")
    lines.append("|---|---:|---:|---:|")
    all_tiers = sorted(set(by_tier_before) | set(by_tier_after))
    for t in all_tiers:
        b = by_tier_before.get(t, 0)
        a = by_tier_after.get(t, 0)
        lines.append(f"| {t} | {b} | {a} | {b - a} |")
    lines.append("")

    if manifest["extract_failures"]:
        lines.append("## Extraction failures (kept in place, flagged for review)\n")
        for r in records:
            if r["extract_failed"]:
                lines.append(f"- `{r['rel']}`")
        lines.append("")

    lines.append("## Duplicate groups (size > 1)\n")
    for g in multi_groups:
        lines.append(f"### {g['tier']} — group of {g['group_size']} ({g['page_count']} pp)\n")
        lines.append(f"**Canonical:** `{g['canonical']}`")
        lines.append(f"**Moved to _duplicates/{g['tier']}/:**")
        for d in g['duplicates']:
            lines.append(f"- `{d}`")
        lines.append("")

    with open(REPORT, "w") as f:
        f.write("\n".join(lines))
    print(f"[report] {REPORT.relative_to(ROOT)}")
    print(f"\nTotal wall: {time.time()-t0:.1f}s")
    print(f"Before: {len(records):,} PDFs.  After: {len(canonical_paths):,} canonical, {len(duplicate_records):,} duplicates moved.")


if __name__ == "__main__":
    main()
