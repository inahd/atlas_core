"""
Cost estimate for stages 02 (extract) and 03 (verify) on the deduplicated
corpus, EXCLUDING tier 17_borderland (which is journal issues, ingested
for search but skipped from the per-text-note pipeline).

Stage 02 inputs per text:
  - Table of contents (≈ 500 tokens, often missing)
  - First 30 pages (≈ 30 × 400 tokens = 12,000 tokens; capped at full text)
  - Last 10 pages (≈ 10 × 400 = 4,000 tokens; capped)
  - 5 random middle chunks (≈ 5 × 1000 = 5,000 tokens)
  - Prompt scaffolding (≈ 1,500 tokens)
  Per-text input total ≈ 23,000 tokens
  Per-text output ≈ 1,500 tokens (the structured note is bounded)

Stage 03 inputs per claim per chunk:
  - Claim statement (≈ 50 tokens)
  - Retrieved chunk (≈ 1000 tokens)
  - Prompt scaffolding (≈ 500 tokens)
  Per-call input ≈ 1,550 tokens
  Per-call output ≈ 200 tokens (support/contradict/irrelevant + quote)
  Calls per text: assume 4 claims × 5 chunks = 20.
  Plus 1 stage-03-summary call per text:
    - All claim statuses + 4 quotes = ≈ 2,000 input, 500 output

Pricing (USD, public list):
  Sonnet 4.6  : input $3.00 / MTok, output $15.00 / MTok
  Haiku  4.5  : input $0.80 / MTok, output $4.00 / MTok
  Opus   4.7  : input $15.00 / MTok, output $75.00 / MTok

Reads dedup_manifest.json + corpus tree to get exact deduped text count
per tier (excluding 17_borderland and excluding extraction failures).
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path("/home/inahd/atlas_core")
CORPUS = ROOT / "corpus/teslatech_lineage"
DUPLICATES = CORPUS / "_duplicates"
PIPELINE = ROOT / "research/corpus_analysis/teslatech_lineage/pipeline"
MANIFEST = PIPELINE / "dedup_manifest.json"

EXCLUDED_TIERS = {"17_borderland_journal"}

# Per-text token estimates
S02_INPUT_PER_TEXT = 23_000
S02_OUTPUT_PER_TEXT = 1_500

# Per-claim verification call estimates
S03_INPUT_PER_VERIFY = 1_550
S03_OUTPUT_PER_VERIFY = 200
CLAIMS_PER_TEXT = 4
CHUNKS_PER_CLAIM = 5

# Per-text stage-03 summary call
S03_SUMMARY_INPUT = 2_000
S03_SUMMARY_OUTPUT = 500

PRICES = {
    # USD per MTok
    "haiku":  {"in": 0.80,  "out": 4.00,  "label": "Haiku 4.5"},
    "sonnet": {"in": 3.00,  "out": 15.00, "label": "Sonnet 4.6"},
    "opus":   {"in": 15.00, "out": 75.00, "label": "Opus 4.7"},
}


def cost(input_toks, output_toks, model_key):
    p = PRICES[model_key]
    return (input_toks / 1_000_000) * p["in"] + (output_toks / 1_000_000) * p["out"]


def main():
    manifest = json.loads(MANIFEST.read_text())
    by_tier_after = manifest["by_tier_after"]
    low_by_tier = manifest.get("low_text_by_tier_after", {})
    print(f"Source: {MANIFEST.relative_to(ROOT)}")
    print()
    print(f"Cleaned corpus per tier (after dedup):")
    print(f"  {'tier':35s} {'after':>5s} {'low':>4s}  notes")
    excluded_n = 0
    included_n = 0
    excluded_low = 0
    included_low = 0
    for tier, n in sorted(by_tier_after.items()):
        lt = low_by_tier.get(tier, 0)
        marker = " [EXCLUDED from stages 02-04 — journal issues]" if tier in EXCLUDED_TIERS else ""
        print(f"  {tier:35s} {n:>5d} {lt:>4d}{marker}")
        if tier in EXCLUDED_TIERS:
            excluded_n += n
            excluded_low += lt
        else:
            included_n += n
            included_low += lt
    print()
    print(f"Total deduped:                  {included_n + excluded_n}")
    print(f"Excluded (tier 17):             {excluded_n}")
    print(f"In stages 02-04 (raw):          {included_n}")
    print(f"  of which low-text (no OCR):   {included_low}")
    print(f"  with extractable text:        {included_n - included_low}")
    print()

    # Two scenarios: (A) skip low-text PDFs from stages 02-04; (B) include them
    # (would require running OCR before stage 02, separate cost). Numbers below
    # under (A); (B) is shown as a multiplier note.
    n_a = included_n - included_low
    n_b = included_n
    s02_in_A = S02_INPUT_PER_TEXT * n_a
    s02_out_A = S02_OUTPUT_PER_TEXT * n_a
    s03_calls_A = CLAIMS_PER_TEXT * CHUNKS_PER_CLAIM * n_a
    s03_in_A = S03_INPUT_PER_VERIFY * s03_calls_A + S03_SUMMARY_INPUT * n_a
    s03_out_A = S03_OUTPUT_PER_VERIFY * s03_calls_A + S03_SUMMARY_OUTPUT * n_a

    print(f"Token estimates — scenario A: skip low-text PDFs (n={n_a}):")
    print(f"  Stage 02 (extract):     input {s02_in_A:>12,} tok   output {s02_out_A:>10,} tok")
    print(f"  Stage 03 (verify+sum):  input {s03_in_A:>12,} tok   output {s03_out_A:>10,} tok")
    print(f"  Stage 03 calls:         {s03_calls_A:,} verify + {n_a} summary = {s03_calls_A + n_a:,} total")
    print()
    print(f"Scenario B (include low-text via OCR pre-pass, n={n_b}):")
    print(f"  Multiplier on the cost numbers below: {n_b/n_a:.2f}x  (plus separate OCR cost ~$0 if local tesseract).")
    print()
    s02_in = s02_in_A; s02_out = s02_out_A; s03_in = s03_in_A; s03_out = s03_out_A

    # Cost matrix
    print(f"Cost matrix (USD):")
    print()
    print(f"  {'Stage 02 model':>15s}  {'Stage 03 model':>15s}  {'Stage 02 $':>12s}  {'Stage 03 $':>12s}  {'Total $':>10s}")
    print(f"  {'-'*15}  {'-'*15}  {'-'*12}  {'-'*12}  {'-'*10}")
    combos = [
        ("haiku",  "haiku"),
        ("sonnet", "haiku"),
        ("sonnet", "sonnet"),
        ("opus",   "haiku"),
        ("opus",   "sonnet"),
    ]
    for s2, s3 in combos:
        c2 = cost(s02_in, s02_out, s2)
        c3 = cost(s03_in, s03_out, s3)
        total = c2 + c3
        print(f"  {PRICES[s2]['label']:>15s}  {PRICES[s3]['label']:>15s}  {c2:>11.2f}   {c3:>11.2f}   {total:>9.2f}")
    print()

    # Highlight the recommended combo
    rec_s2, rec_s3 = "sonnet", "haiku"
    c2_r = cost(s02_in, s02_out, rec_s2)
    c3_r = cost(s03_in, s03_out, rec_s3)
    print(f"Recommended: {PRICES[rec_s2]['label']} for stage 02, {PRICES[rec_s3]['label']} for stage 03.")
    print(f"  Total estimate: ${c2_r + c3_r:.2f}")
    print()
    print(f"Sub-sample fallbacks (priced at Sonnet 02 + Haiku 03, scenario A — skip low-text):")

    def cost_for(n_texts):
        c2 = cost(S02_INPUT_PER_TEXT * n_texts, S02_OUTPUT_PER_TEXT * n_texts, rec_s2)
        c3_calls = CLAIMS_PER_TEXT * CHUNKS_PER_CLAIM * n_texts
        c3_in = S03_INPUT_PER_VERIFY * c3_calls + S03_SUMMARY_INPUT * n_texts
        c3_out = S03_OUTPUT_PER_VERIFY * c3_calls + S03_SUMMARY_OUTPUT * n_texts
        c3 = cost(c3_in, c3_out, rec_s3)
        return c2 + c3

    core_tiers = {f"0{i}_" for i in range(1, 10)}
    # tiers 01-09, after dedup, MINUS low_text in those tiers
    core_n = 0
    for t, n in by_tier_after.items():
        if t in EXCLUDED_TIERS:
            continue
        if not any(t.startswith(p) for p in core_tiers):
            continue
        core_n += n - low_by_tier.get(t, 0)
    if core_n:
        print(f"  Tiers 01-09 only (electrical engineering core, with text), n={core_n}: ${cost_for(core_n):.2f}")
    # Steinmetz tier alone as full-pipeline test
    s_total = by_tier_after.get("01_steinmetz", 0)
    s_low = low_by_tier.get("01_steinmetz", 0)
    s_with_text = s_total - s_low
    if s_with_text:
        print(f"  01_steinmetz tier alone (with text), n={s_with_text} (of {s_total} total): ${cost_for(s_with_text):.2f}")
    print()
    print(f"Note: low-text PDFs ({included_low} in stages 02-04) are PDFs where pymupdf")
    print(f"  extracted < 1000 non-whitespace chars OR < 100 distinct English words.")
    print(f"  They appear to be image-only scans (often with the AETHERFORCE watermark).")
    print(f"  Stage 02 would have nothing meaningful to read for these without OCR.")
    print(f"  Options: (i) skip them (scenario A above); (ii) run tesseract OCR before")
    print(f"  stage 02 to recover content; (iii) flag for manual review.")


if __name__ == "__main__":
    main()
