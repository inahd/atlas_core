"""
Stage 01: ingest + embed.

Walks the deduplicated corpus at corpus/teslatech_lineage/ (skipping
_duplicates/ which dedup.py moved out of the analysis path), extracts
text per page via pymupdf, chunks into ~1000-token chunks with 200-token
overlap, embeds with sentence-transformers all-MiniLM-L6-v2 (matching
Atlas's existing vector store), writes chunks.parquet.

Tier 17_borderland is INCLUDED here (per spec — searchable reference
material) but will be skipped in stages 02-04.

Token approximation for chunking: whitespace-split words, ~0.75
tokens/word average → 1000 tokens ≈ 1330 words. Overlap ≈ 270 words.

Embedding model: all-MiniLM-L6-v2 (384-dim), CPU.

Output:
  research/corpus_analysis/teslatech_lineage/embeddings/chunks.parquet
    columns: text_path, tier, page_start, page_end, chunk_index,
             content, embedding (list[float], 384 dims)
"""
from __future__ import annotations

import json
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import fitz  # pymupdf
from sentence_transformers import SentenceTransformer

ROOT = Path("/home/inahd/atlas_core")
CORPUS = ROOT / "corpus/teslatech_lineage"
OUT_DIR = ROOT / "research/corpus_analysis/teslatech_lineage/embeddings"
OUT_PARQUET = OUT_DIR / "chunks.parquet"
PIPELINE = ROOT / "research/corpus_analysis/teslatech_lineage/pipeline"
STATE_PATH = PIPELINE / "pipeline_state.json"

CHUNK_WORDS = 1330       # ~1000 tokens at 0.75 tokens/word
OVERLAP_WORDS = 270      # ~200 tokens overlap
EMBED_BATCH = 64
MODEL_NAME = os.environ.get("ATLAS_EMBED_MODEL", "all-MiniLM-L6-v2")


def collect_pdfs():
    pdfs = []
    for p in sorted(CORPUS.rglob("*.pdf")):
        if "_duplicates" in p.parts:
            continue
        pdfs.append(p)
    return pdfs


def extract_pages(pdf_path: Path) -> tuple[list[str], int]:
    """Resilient to malformed PDFs (cycle in page tree, etc.)."""
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


def chunk_pages(pages: list[str]) -> list[dict]:
    """Chunk pages into ~1330-word chunks with ~270-word overlap.

    Each chunk records (content, page_start, page_end) where pages are
    1-indexed PDF pages (NOT the printed page numbers — preserved for
    citation, with the caveat that printed pagination may differ).

    Strategy: walk pages, accumulate words tagged by source page. When
    word count >= CHUNK_WORDS, emit chunk with page_start..page_end
    derived from the tagged words. For overlap, retain the last
    OVERLAP_WORDS words to seed the next chunk.
    """
    # Build a flat list of (page_1based, word) tuples.
    flat = []
    for pi, ptxt in enumerate(pages):
        for w in ptxt.split():
            flat.append((pi + 1, w))

    chunks = []
    n = len(flat)
    if n == 0:
        return chunks
    cursor = 0
    while cursor < n:
        end = min(cursor + CHUNK_WORDS, n)
        slice_ = flat[cursor:end]
        words = [w for _, w in slice_]
        page_start = slice_[0][0]
        page_end = slice_[-1][0]
        chunks.append({
            "content": " ".join(words),
            "page_start": int(page_start),
            "page_end": int(page_end),
        })
        if end >= n:
            break
        cursor = end - OVERLAP_WORDS
        if cursor <= 0:
            cursor = end  # safeguard against tiny chunks
    return chunks


def main():
    t0 = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[scan] corpus = {CORPUS}")
    pdfs = collect_pdfs()
    print(f"  {len(pdfs):,} PDFs (excluding _duplicates/)")

    by_tier = defaultdict(int)
    for p in pdfs:
        by_tier[p.relative_to(CORPUS).parts[0]] += 1
    for tier in sorted(by_tier):
        print(f"    {tier}: {by_tier[tier]}")

    # ── extract + chunk ──
    all_chunks = []
    failed = []
    print(f"\n[extract+chunk] over {len(pdfs)} PDFs")
    for i, pdf in enumerate(pdfs):
        rel = pdf.relative_to(CORPUS)
        tier = rel.parts[0]
        pages, pc = extract_pages(pdf)
        if pc == 0 or not any(pages):
            failed.append(str(rel))
            continue
        chunks = chunk_pages(pages)
        for ci, ch in enumerate(chunks):
            all_chunks.append({
                "text_path": str(rel),
                "tier": tier,
                "page_start": ch["page_start"],
                "page_end": ch["page_end"],
                "chunk_index": ci,
                "content": ch["content"],
            })
        if (i + 1) % 25 == 0 or i == len(pdfs) - 1:
            print(f"  [{i+1}/{len(pdfs)}] chunks={len(all_chunks):,}  failed={len(failed)}  elapsed={time.time()-t0:.1f}s")

    if failed:
        print(f"\n[warn] {len(failed)} extraction failures:")
        for f in failed:
            print(f"  - {f}")

    print(f"\n[df] {len(all_chunks):,} chunks total")
    df = pd.DataFrame(all_chunks)
    print(f"  per-tier chunk counts:")
    for tier, n in sorted(df["tier"].value_counts().items()):
        print(f"    {tier}: {n:,}")

    # ── embed ──
    print(f"\n[embed] loading {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)
    print(f"  embedding dim = {model.get_sentence_embedding_dimension()}")

    contents = df["content"].tolist()
    print(f"  encoding {len(contents):,} chunks (batch_size={EMBED_BATCH})")
    t_emb = time.time()
    embeddings = model.encode(
        contents,
        batch_size=EMBED_BATCH,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    print(f"  embed wall: {time.time()-t_emb:.1f}s  shape={embeddings.shape}")

    df["embedding"] = [emb.astype(np.float32).tolist() for emb in embeddings]

    # ── write ──
    df.to_parquet(OUT_PARQUET, index=False)
    print(f"\n[write] {OUT_PARQUET.relative_to(ROOT)}  rows={len(df):,}  size={OUT_PARQUET.stat().st_size/1e6:.1f} MB")

    # ── pipeline state ──
    state = {
        "stage_01_completed_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "embedding_model": MODEL_NAME,
        "embedding_dim": int(embeddings.shape[1]),
        "n_pdfs_ingested": int(df["text_path"].nunique()),
        "n_chunks_total": len(df),
        "extraction_failures": failed,
        "per_tier_pdf_count": {tier: int((df.groupby("tier")["text_path"].nunique())[tier])
                                for tier in sorted(df["tier"].unique())},
        "per_tier_chunk_count": {tier: int(df[df["tier"] == tier].shape[0])
                                  for tier in sorted(df["tier"].unique())},
    }
    if STATE_PATH.exists():
        existing = json.loads(STATE_PATH.read_text())
        existing.update(state)
        state = existing
    STATE_PATH.write_text(json.dumps(state, indent=2))
    print(f"[state] {STATE_PATH.relative_to(ROOT)}")

    print(f"\nTotal wall: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
