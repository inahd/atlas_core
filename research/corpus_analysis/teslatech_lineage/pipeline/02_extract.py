"""
Stage 02: extract a structured per-text note via local Ollama (qwen3:8b).

Inputs per text (assembled locally from chunks.parquet + raw PDF):
  - First 30 pages of extracted text (capped to fit context)
  - Last 10 pages of extracted text
  - 5 random middle chunks from chunks.parquet
  - Optional table-of-contents lines (heuristic detection)

Output: research/corpus_analysis/teslatech_lineage/notes/<tier>/<stem>_note.md
        (markdown per spec section "Required structured output")

Modes:
  --text path/under/corpus/<tier>/<file.pdf>   : single-text mode (test)
  --tiers-include 01,02,03,...                 : run on all texts in those tiers,
                                                 skipping low-text PDFs
  --dry-run                                    : print prompt, don't call model
  --model qwen3:8b                             : override Ollama model
  --limit N                                    : process at most N texts

Skips:
  - Tier 17_borderland_journal (per spec; journal issues)
  - Low-text PDFs (no chunks in chunks.parquet)
  - Texts whose note already exists (resumable)

Quality flag:
  Output that fails to include all 6 required section headers, or that
  comes in below MIN_NOTE_CHARS, is marked `low_quality_local: true` in
  pipeline_state.json so it can be selectively re-run on a stronger model
  later.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
import time
import urllib.request
from collections import defaultdict
from pathlib import Path

import fitz
import pandas as pd

ROOT = Path("/home/inahd/atlas_core")
CORPUS = ROOT / "corpus/teslatech_lineage"
PIPELINE = ROOT / "research/corpus_analysis/teslatech_lineage/pipeline"
NOTES_DIR = ROOT / "research/corpus_analysis/teslatech_lineage/notes"
EMB_PARQUET = ROOT / "research/corpus_analysis/teslatech_lineage/embeddings/chunks.parquet"
STATE_PATH = PIPELINE / "pipeline_state.json"

DEFAULT_MODEL = "qwen3:8b"
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_TIMEOUT_S = 600
NUM_CTX = 32768                # qwen3:8b context

EXCLUDED_TIERS = {"17_borderland_journal"}
DEFAULT_TIERS = [f"0{i}_" for i in range(1, 10)]   # 01-09

# Prompt budget: per-text input target ≈ 25K tokens. Page-text budget allocated:
FIRST_PAGES = 30
LAST_PAGES = 10
N_MID_CHUNKS = 5
PAGE_CHAR_BUDGET = 1800       # ~450 tokens per page; cap to avoid runaway
TOC_MAX_LINES = 80

MIN_NOTE_CHARS = 1500          # below this, mark low_quality_local
REQUIRED_HEADERS = [
    "## 1. Core claims",
    "## 2. Register classification",
    "## 3. Relationship to Atlas",
    "## 4. Drift risks",
    "## 5. Researcher's read",
    "## 6. Open questions",
]


# ── PDF helpers ────────────────────────────────────────────

def extract_pages(pdf_path: Path) -> list[str]:
    try:
        doc = fitz.open(str(pdf_path))
    except Exception:
        return []
    try:
        pc = doc.page_count
    except Exception:
        try: doc.close()
        except: pass
        return []
    out = []
    for i in range(pc):
        try:
            out.append(doc.load_page(i).get_text("text") or "")
        except Exception:
            out.append("")
    try: doc.close()
    except: pass
    return out


def truncate(s: str, n: int) -> str:
    if len(s) <= n:
        return s
    return s[:n].rstrip() + " […truncated]"


def extract_toc_heuristic(pages: list[str]) -> list[str]:
    """Cheap TOC extractor: scan first 20 pages for lines with section-y patterns."""
    import re
    candidates = []
    pat_chap = re.compile(r"^\s*(CHAPTER|chapter|Chapter|PART|part|Part|SECTION|Lecture|LECTURE)\b.{0,80}$")
    pat_dotleader = re.compile(r"\.{4,}\s*\d+\s*$")
    for p in pages[:20]:
        for line in p.split("\n"):
            if pat_chap.match(line) or pat_dotleader.search(line):
                trimmed = line.strip()
                if 5 <= len(trimmed) <= 200:
                    candidates.append(trimmed)
    seen = set()
    out = []
    for c in candidates:
        if c not in seen:
            out.append(c); seen.add(c)
        if len(out) >= TOC_MAX_LINES:
            break
    return out


# ── prompt assembly ────────────────────────────────────────

PROMPT_TEMPLATE = """You are reading a text from a research corpus on alternative-physics
lineage (Steinmetz, Heaviside, Maxwell, Faraday, Tesla, Whittaker, Russell,
Steiner-Marti, etc.). Produce a STRUCTURED ANALYSIS NOTE in markdown,
exactly matching the schema below.

## Hard constraints

- Do NOT invent quotes. If you cannot find a supporting quote of <15 words
  in the excerpts I provide below, write `"[no direct quote located in extract pass]"`
  for that quote — verification will retrieve real quotes in stage 03.
- Do NOT claim to have read more than the excerpts I have provided.
- Do NOT pattern-match between texts. This text is read on its own terms.
  Cross-text comparison happens in a later stage.
- If the text is in a register you find genuinely difficult (dense 19th-century
  mathematical notation, archaic English, etc.), say so explicitly in the
  "Researcher's read" section rather than papering over the difficulty.
- Cite pages using the PDF page numbering provided in the chunk excerpts
  (these are 1-indexed PDF pages, which may differ from the printed page
  numbers in old books).

## Atlas's framework — for §3 ("Relationship to Atlas's framework") only

Atlas is a research/computation system whose framework includes:
- Versor / phasor algebra for two-source wave interference at a target,
  with a magnetic-mode (Re part) and dielectric-mode (Im part) decomposition.
- Pre-registered statistical testing of geosolar / panchanga correlations.
- Sun-Moon angular geometry as a global driver of tidal/ring-current physics
  (with M4 tide-range survival in the multi-decade test).
- Sidereal Lahiri panchanga, jyotisha, S0–S6 layer system.
- Skepticism of unfalsifiable cosmological claims; preference for
  operational/empirical/theoretical registers over speculative/cosmological.

Use this only to inform §3 classification. Do not let it bias your reading.

## Required output schema

# [Text Title]

**Author:** [name]
**Year:** [year if known]
**Tier:** {tier}
**Pages:** [N]
**Source type:** [PRIMARY-MATHEMATICAL | PRIMARY-DISCURSIVE | SECONDARY-DISCURSIVE | REFERENCE-COMPILATION | UNCLASSIFIED]
**Status:** DRAFT (extracted by stage 02, not yet verified)

A note on **Source type** classification (mark this honestly — corpus has known
bias toward secondary sources because most heavy primary mathematical texts in
this collection are image-only watermarked scans that did not extract):

- PRIMARY-MATHEMATICAL: original technical/mathematical work by the named author
  (derivations, proofs, calculations, original theorems)
- PRIMARY-DISCURSIVE: original prose work by the named author (lectures, essays,
  letters, exposition without dense math)
- SECONDARY-DISCURSIVE: someone writing *about* a primary author (Dollard on
  Steinmetz, biographical/explanatory works)
- REFERENCE-COMPILATION: directories, indices, bibliographies, multi-author
  excerpt collections
- UNCLASSIFIED: cannot tell from excerpts (be willing to use this)

## 1. Core claims

The 3-5 main load-bearing claims of the text. Each:
- One sentence stating the claim plainly
- A page citation (e.g. "p. 47-52")
- A direct quote of <15 words from the text supporting it

### Claim 1: [one-sentence statement]
- Pages: [page range]
- Supporting quote: "[<15 words]"

### Claim 2: ...

(3 to 5 claims total)

## 2. Register classification

For each claim above, classify into ONE of:
- OPERATIONAL: testable, mathematical, with reproducible procedures
- EMPIRICAL: observational, descriptive, with reproducible observations
- THEORETICAL: framework-level, deductive, mathematically structured
- SPECULATIVE: extends framework into untested territory, often hedged
- COSMOLOGICAL: meaning-making, interpretive, not directly testable

State the classification with one sentence of justification per claim.

## 3. Relationship to Atlas's framework

For each claim, classify as ONE of:
- PARALLELS / CONTRADICTS / EXTENDS / SUPPORTS / ORTHOGONAL

State the relationship with one sentence of justification.

## 4. Drift risks

If Atlas were to uncritically integrate this text's framework, what
specific epistemic standards would be loosened? Or write "No drift risk
identified" if the text's standards meet or exceed Atlas's.

## 5. Researcher's read

One paragraph (4-8 sentences) of freeform synthesis: what is this text
*for* in Atlas's research program? When would you cite it? What's the
specific value it adds that other texts in the corpus don't?

## 6. Open questions

2-3 questions this text raises that Atlas should address but doesn't yet.
Each is one sentence.

## EXCERPTS PROVIDED FROM THE TEXT

### File metadata

- File path: {rel_path}
- Tier: {tier}
- PDF page count: {page_count}

### Heuristic table-of-contents (from first 20 pages)

{toc_block}

### First {first_pages} pages of extracted text

{first_block}

### Last {last_pages} pages of extracted text

{last_block}

### {n_mid} random middle-section chunks (with page citations)

{mid_block}

End of excerpts. Now produce the structured note. Begin with `# ` and the
inferred text title. Do not preface with any other commentary.
"""


def assemble_prompt(rel_path: str, tier: str, pdf_path: Path,
                    chunks_df: pd.DataFrame, seed: int = 0) -> tuple[str, dict]:
    pages = extract_pages(pdf_path)
    pc = len(pages)
    if pc == 0:
        raise RuntimeError(f"No extractable text from {pdf_path}")

    # First/last page slices, each page truncated to budget
    first_n = min(FIRST_PAGES, pc)
    last_n = min(LAST_PAGES, max(0, pc - first_n))
    first_block_parts = []
    for i in range(first_n):
        first_block_parts.append(f"[p. {i+1}]\n{truncate(pages[i].strip(), PAGE_CHAR_BUDGET)}")
    first_block = "\n\n".join(first_block_parts) or "[no text extracted from first pages]"

    last_block_parts = []
    last_start = max(first_n, pc - last_n)
    for i in range(last_start, pc):
        last_block_parts.append(f"[p. {i+1}]\n{truncate(pages[i].strip(), PAGE_CHAR_BUDGET)}")
    last_block = "\n\n".join(last_block_parts) or "[no text extracted from last pages]"

    # Random middle chunks
    text_chunks = chunks_df[chunks_df["text_path"] == rel_path].sort_values("chunk_index").reset_index(drop=True)
    n = len(text_chunks)
    mid_block_parts = []
    if n > 0:
        # Sample from the middle 70% to avoid first/last overlap
        lo = int(n * 0.15)
        hi = int(n * 0.85)
        candidate_idx = list(range(lo, max(hi, lo + 1)))
        rnd = random.Random(seed)
        sample_n = min(N_MID_CHUNKS, len(candidate_idx))
        picked = sorted(rnd.sample(candidate_idx, sample_n))
        for i in picked:
            row = text_chunks.iloc[i]
            mid_block_parts.append(
                f"[chunk #{int(row.chunk_index)}, pp. {int(row.page_start)}-{int(row.page_end)}]\n"
                f"{truncate(row.content, 4000)}"
            )
    mid_block = "\n\n".join(mid_block_parts) or "[no middle chunks available]"

    toc_lines = extract_toc_heuristic(pages)
    toc_block = "\n".join(f"  - {l}" for l in toc_lines) or "  [no TOC pattern detected]"

    prompt = PROMPT_TEMPLATE.format(
        rel_path=rel_path,
        tier=tier,
        page_count=pc,
        toc_block=toc_block,
        first_pages=first_n,
        last_pages=last_n,
        n_mid=len(mid_block_parts),
        first_block=first_block,
        last_block=last_block,
        mid_block=mid_block,
    )
    meta = {
        "first_pages": first_n,
        "last_pages": last_n,
        "n_mid_chunks": len(mid_block_parts),
        "page_count": pc,
        "approx_input_chars": len(prompt),
    }
    return prompt, meta


# ── note path helper ────────────────────────────────────────

def note_path_for(rel_path: str) -> Path:
    parts = Path(rel_path).parts
    tier = parts[0]
    stem = Path(rel_path).stem
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in stem)
    safe = safe[:120]
    return NOTES_DIR / tier / f"{safe}_note.md"


# ── API call ────────────────────────────────────────────────

def call_ollama(prompt: str, model: str) -> tuple[str, dict]:
    """Call local Ollama /api/chat. Returns (response_text, usage_dict)."""
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "think": False,            # disable Qwen3 think mode for analysis output
        "options": {
            "temperature": 0.2,
            "num_ctx": NUM_CTX,
            "num_predict": 4096,
        },
    }
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT_S) as r:
        data = json.load(r)
    text = data.get("message", {}).get("content", "") or ""
    usage = {
        "input_tokens": data.get("prompt_eval_count", 0),
        "output_tokens": data.get("eval_count", 0),
        "total_duration_s": (data.get("total_duration", 0) or 0) / 1e9,
        "model": data.get("model", model),
        "done_reason": data.get("done_reason"),
    }
    return text, usage


def quality_check(note_text: str) -> dict:
    """Return {'low_quality_local': bool, 'reasons': list[str]}."""
    reasons = []
    if len(note_text) < MIN_NOTE_CHARS:
        reasons.append(f"length {len(note_text)} < {MIN_NOTE_CHARS}")
    missing = [h for h in REQUIRED_HEADERS if h.lower() not in note_text.lower()]
    if missing:
        reasons.append(f"missing headers: {len(missing)}/{len(REQUIRED_HEADERS)}")
    if not re.search(r"^\*\*Source type:\*\*", note_text, re.M):
        reasons.append("missing Source type marker")
    return {"low_quality_local": bool(reasons), "reasons": reasons}


# ── candidate text list ─────────────────────────────────────

def list_candidates(chunks_df: pd.DataFrame, tiers_include: list[str]) -> list[str]:
    """Return rel_paths of texts in the included tiers that have chunks
    (i.e., extractable text), sorted for deterministic ordering."""
    by_text = chunks_df.groupby("text_path").agg(
        tier=("tier", "first"),
        chunks=("chunk_index", "size"),
    )
    out = []
    for path, row in by_text.iterrows():
        tier = row["tier"]
        if tier in EXCLUDED_TIERS:
            continue
        if tiers_include and not any(tier.startswith(p) for p in tiers_include):
            continue
        if row["chunks"] == 0:
            continue
        out.append(path)
    return sorted(out)


# ── main ────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", help="Single-text mode: rel path under corpus/teslatech_lineage/")
    ap.add_argument("--tiers-include", default=",".join(DEFAULT_TIERS),
                    help="Comma-separated tier prefixes (e.g. '01_,02_,03_'). Default 01-09.")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print prompt + token estimate, don't call API")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--limit", type=int, default=0,
                    help="Process at most N texts (for partial runs)")
    args = ap.parse_args()

    chunks_df = pd.read_parquet(EMB_PARQUET, columns=["text_path", "tier", "chunk_index", "page_start", "page_end", "content"])

    tiers_inc = [t.strip() for t in args.tiers_include.split(",") if t.strip()]
    if args.text:
        targets = [args.text]
    else:
        targets = list_candidates(chunks_df, tiers_inc)
    if args.limit:
        targets = targets[:args.limit]

    print(f"[stage02] {len(targets)} text(s) to process. dry_run={args.dry_run} model={args.model} ollama={OLLAMA_URL}")

    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    t_run = time.time()

    # Load existing pipeline_state to merge with
    if STATE_PATH.exists():
        state = json.loads(STATE_PATH.read_text())
    else:
        state = {}
    stage02 = state.setdefault("stage_02", {"notes": {}})
    notes_state = stage02["notes"]

    total_in = 0; total_out = 0; processed = 0; skipped = 0; low_quality = 0; failed = []
    for rel in targets:
        out_path = note_path_for(rel)
        if out_path.exists():
            print(f"  [skip] {rel}  (note already exists at {out_path.relative_to(ROOT)})")
            skipped += 1
            continue

        pdf_path = CORPUS / rel
        try:
            prompt, meta = assemble_prompt(rel, Path(rel).parts[0], pdf_path, chunks_df, seed=args.seed)
        except Exception as e:
            print(f"  [fail-prompt] {rel}: {e}")
            failed.append((rel, f"prompt: {e}"))
            continue

        if args.dry_run:
            print(f"  [dry] {rel}  approx_chars={meta['approx_input_chars']:,}  pp={meta['page_count']}")
            continue

        try:
            t0 = time.time()
            text, usage = call_ollama(prompt, args.model)
            dt = time.time() - t0
        except Exception as e:
            print(f"  [fail-api] {rel}: {e}")
            failed.append((rel, f"ollama: {e}"))
            continue

        total_in += usage.get("input_tokens", 0)
        total_out += usage.get("output_tokens", 0)
        processed += 1

        # Strip leading thinking-block <think>...</think> if present (qwen3 leftover)
        text = re.sub(r"^<think>.*?</think>\s*", "", text, flags=re.S)

        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text)

        q = quality_check(text)
        if q["low_quality_local"]:
            low_quality += 1
            mark = " [LOW-QUALITY-LOCAL]"
        else:
            mark = ""
        notes_state[rel] = {
            "note_path": str(out_path.relative_to(ROOT)),
            "processed_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "model": args.model,
            "tokens_in": usage.get("input_tokens", 0),
            "tokens_out": usage.get("output_tokens", 0),
            "wall_s": round(dt, 1),
            "low_quality_local": q["low_quality_local"],
            "quality_reasons": q["reasons"],
            "verified_status": None,   # filled by stage 03
        }

        print(f"  [ok]{mark} {rel}  in={usage.get('input_tokens',0):,} out={usage.get('output_tokens',0):,} "
              f"dt={dt:.1f}s  → {out_path.relative_to(ROOT)}")

        # Flush state after each text (resumable)
        STATE_PATH.write_text(json.dumps(state, indent=2))

    print()
    print(f"[stage02] processed={processed}  skipped(existing)={skipped}  low_quality_local={low_quality}  failed={len(failed)}")
    if failed:
        print("  failures:")
        for r, e in failed:
            print(f"    {r}  ::  {e}")
    if total_in or total_out:
        print(f"[tokens] input={total_in:,}  output={total_out:,}  (local — $0)")
    print(f"[wall] {time.time() - t_run:.1f}s")


if __name__ == "__main__":
    main()
