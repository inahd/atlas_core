"""
Structural inventory of the teslatech_lineage corpus.

Pure pattern-matching analysis on chunks.parquet — no interpretation,
no module drafting. Surfaces what's available for math_extracts work.

For each text:
  - equation density (math-operator count / chars)
  - dualities articulated (centripetal/centrifugal etc.)
  - named principles ("the X principle", "law of X", "X effect")
  - cross-author citations (mentions of other corpus authors)
  - candidate phenomena claims ("X produces Y", "X results in Y")

Outputs:
  research/corpus_analysis/structural_inventory.md   (human-readable)
  research/corpus_analysis/structural_inventory.json (machine-readable)
"""
from __future__ import annotations

import json
import re
import time
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path("/home/inahd/atlas_core")
CHUNKS = ROOT / "research/corpus_analysis/teslatech_lineage/embeddings/chunks.parquet"
PIPELINE_STATE = ROOT / "research/corpus_analysis/teslatech_lineage/pipeline/pipeline_state.json"
OUT_MD = ROOT / "research/corpus_analysis/structural_inventory.md"
OUT_JSON = ROOT / "research/corpus_analysis/structural_inventory.json"

# ── pattern definitions ────────────────────────────────────

# Math density
MATH_OPS = re.compile(r"[=+\-*/<>]")              # basic operators
MATH_SYMBOLS = re.compile(r"[Σ∫∂√∇∞∝≈≠≤≥]")     # higher math symbols
GREEK_LOWER = re.compile(r"[αβγδεζηθικλμνξπρστυφχψω]")
GREEK_UPPER = re.compile(r"[ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΠΡΣΤΥΦΧΨΩ]")
EQ_LINE = re.compile(r"\w+\s*=\s*[\w\d\(\-\+]")   # "X = Y" style
SUPERSCRIPT_DIGIT = re.compile(r"\^[\d]")          # "x^2"
NUMBER_DENSE = re.compile(r"\b\d+\.\d+\b")         # decimal numbers

# Dualities (lowercase patterns; we lowercase the chunk first)
DUALITY_PATTERNS = {
    "two-fold":              re.compile(r"\btwo[- ]?fold\b"),
    "polarity":              re.compile(r"\bpolarit"),
    "complementary":         re.compile(r"\bcomplementar"),
    "duality":               re.compile(r"\bdualit"),
    "dual":                  re.compile(r"\bdual\b"),
    "opposite":              re.compile(r"\boppos"),
    "centripetal":           re.compile(r"\bcentripetal\b"),
    "centrifugal":           re.compile(r"\bcentrifugal\b"),
    "expansion-compression": re.compile(r"\bexpansion[\s\S]{0,40}compression\b|\bcompression[\s\S]{0,40}expansion\b"),
    "dielectric-magnetic":   re.compile(r"\bdielectric[\s\S]{0,50}magnetic\b|\bmagnetic[\s\S]{0,50}dielectric\b"),
    "positive-negative":     re.compile(r"\bpositive\s+and\s+negative\b|\bnegative\s+and\s+positive\b"),
    "north-south":           re.compile(r"\bnorth\s+and\s+south\b"),
    "active-passive":        re.compile(r"\bactive[\s\S]{0,30}passive\b|\bpassive[\s\S]{0,30}active\b"),
    "generative-radiative":  re.compile(r"\bgenerative[\s\S]{0,30}radiative\b|\bradiative[\s\S]{0,30}generative\b"),
    "yin-yang":              re.compile(r"\byin[\s\S]{0,15}yang\b|\byang[\s\S]{0,15}yin\b"),
    "male-female":           re.compile(r"\bmale\s+and\s+female\b|\bfemale\s+and\s+male\b"),
}

# Named principles
PRINCIPLE_PATTERNS = [
    re.compile(
        r"\bthe\s+([A-Z][a-zA-Z\-]+(?:\s+[A-Z][a-zA-Z\-]+){0,2})\s+(principle|law|effect|theorem|theory|hypothesis|postulate|conjecture)\b"
    ),
    re.compile(
        r"\b(law|principle)\s+of\s+([a-z][a-z\s\-]{2,40}?)(?=[,\.\n;:])",
        re.IGNORECASE
    ),
]

# Authors (corpus + commonly-cited externals)
CORPUS_AUTHORS = {
    "Steinmetz":  "01_steinmetz",
    "Dollard":    "02_dollard",
    "Heaviside":  "03_heaviside",
    "Maxwell":    "04_maxwell_faraday",
    "Faraday":    "04_maxwell_faraday",
    "J. J. Thomson": "05_thomson_jj",
    "Thomson":    "05_thomson_jj",
    "Kennelly":   "06_kennelly",
    "MacFarlane": "07_macfarlane",
    "Macfarlane": "07_macfarlane",
    "Whittaker":  "08_whittaker",
    "Tesla":      "09_tesla_primary",
    "Jenny":      "10_jenny_cymatics",
    "Wachsmuth":  "11_wachsmuth_steiner_marti",
    "Steiner":    "11_wachsmuth_steiner_marti",
    "Marti":      "11_wachsmuth_steiner_marti",
    "Russell":    "12_russell",
    "Lawlor":     "14_lawlor_sacred_geom",
    "Bortoft":    "15_bortoft_goethe",
    "Goethe":     "15_bortoft_goethe",
    "Le Bon":     "18_lebon_lodge_crookes",
    "LeBon":      "18_lebon_lodge_crookes",
    "Lodge":      "18_lebon_lodge_crookes",
    "Crookes":    "18_lebon_lodge_crookes",
}
EXTERNAL_AUTHORS = [
    "Newton", "Einstein", "Planck", "Helmholtz", "Boltzmann",
    "Schrödinger", "Schauberger", "Reich", "Eddington", "Kelvin",
    "Hertz", "Edison", "Marconi", "Poincaré", "Coulomb",
]
ALL_AUTHORS = list(CORPUS_AUTHORS.keys()) + EXTERNAL_AUTHORS

# Phenomenon patterns
PHENOMENA_PATTERN = re.compile(
    r"\b(produces?|generates?|causes?|results?\s+in|gives?\s+rise\s+to|emits?|radiates?)\s+(an?\s+)?([a-z][\w\-]{2,30}(?:\s+[\w\-]{2,30}){0,3})",
    re.IGNORECASE
)


# ── per-chunk feature extraction ───────────────────────────

def chunk_features(content: str) -> dict:
    n_chars = max(len(content), 1)
    lower = content.lower()

    # Math density
    n_ops = len(MATH_OPS.findall(content))
    n_sym = len(MATH_SYMBOLS.findall(content))
    n_greek = len(GREEK_LOWER.findall(content)) + len(GREEK_UPPER.findall(content))
    n_eq = len(EQ_LINE.findall(content))
    n_sup = len(SUPERSCRIPT_DIGIT.findall(content))
    n_num = len(NUMBER_DENSE.findall(content))
    math_score = (n_ops + 3 * n_sym + 2 * n_greek + 5 * n_eq + 3 * n_sup + n_num) / n_chars
    has_equations = (n_eq >= 2 or n_sym >= 2 or n_sup >= 2)

    # Dualities
    dualities = [name for name, pat in DUALITY_PATTERNS.items() if pat.search(lower)]

    # Principles
    principles = []
    for m in PRINCIPLE_PATTERNS[0].finditer(content):
        # "the X principle/law/effect..."
        name = m.group(1).strip()
        kind = m.group(2).strip().lower()
        if 3 <= len(name) <= 60:
            principles.append(f"{name} {kind}")
    for m in PRINCIPLE_PATTERNS[1].finditer(content):
        # "law/principle of X"
        kind = m.group(1).lower()
        name = m.group(2).strip()
        if 3 <= len(name) <= 60:
            principles.append(f"{kind} of {name}")

    # Author mentions
    author_mentions = Counter()
    for a in ALL_AUTHORS:
        # word-boundary search for the surname (case-sensitive for proper-noun specificity)
        if a in content:
            author_mentions[a] = content.count(a)

    # Phenomena candidates (cap to first 5 per chunk to control output)
    phenomena = []
    for m in PHENOMENA_PATTERN.finditer(content):
        verb = m.group(1).lower()
        obj = m.group(3).strip().lower()
        phenomena.append(f"{verb} {obj}")
        if len(phenomena) >= 5:
            break

    return {
        "n_chars": n_chars,
        "math_score": math_score,
        "has_equations": has_equations,
        "n_eq": n_eq,
        "n_math_symbols": n_sym,
        "n_greek": n_greek,
        "dualities": dualities,
        "principles": principles,
        "author_mentions": dict(author_mentions),
        "phenomena": phenomena,
    }


# ── per-text aggregation ───────────────────────────────────

def aggregate_text(group: pd.DataFrame, tier: str) -> dict:
    feats = [chunk_features(c) for c in group["content"]]
    n_chunks = len(feats)
    if n_chunks == 0:
        return {}

    # Equation density (mean math_score; count chunks with equations)
    math_scores = [f["math_score"] for f in feats]
    eq_chunk_count = sum(1 for f in feats if f["has_equations"])
    eq_chunk_frac = eq_chunk_count / n_chunks

    # Dualities (set, with counts)
    dual_counter = Counter()
    for f in feats:
        for d in f["dualities"]:
            dual_counter[d] += 1

    # Principles (Counter)
    princ_counter = Counter()
    for f in feats:
        for p in f["principles"]:
            princ_counter[p] += 1

    # Author mentions (Counter)
    author_counter = Counter()
    for f in feats:
        for a, n in f["author_mentions"].items():
            author_counter[a] += n
    # Subtract self-tier mentions (e.g., Steinmetz mentioning Steinmetz)
    own_authors = [a for a, t in CORPUS_AUTHORS.items() if t == tier]
    for own in own_authors:
        author_counter.pop(own, None)

    # Phenomena (Counter)
    phen_counter = Counter()
    for f in feats:
        for p in f["phenomena"]:
            phen_counter[p] += 1

    # Equation-bearing chunk samples (first 5 indices into the original group)
    eq_chunks = []
    for i, f in enumerate(feats):
        if f["has_equations"]:
            row = group.iloc[i]
            eq_chunks.append({
                "chunk_index": int(row["chunk_index"]),
                "page_start": int(row["page_start"]),
                "page_end": int(row["page_end"]),
                "math_score": round(f["math_score"], 5),
                "n_eq": f["n_eq"],
                "n_math_symbols": f["n_math_symbols"],
                "n_greek": f["n_greek"],
                "preview": row["content"][:160].replace("\n", " "),
            })
        if len(eq_chunks) >= 5:
            break

    return {
        "n_chunks": int(n_chunks),
        "math_score_mean": round(sum(math_scores) / n_chunks, 5),
        "math_score_max": round(max(math_scores), 5),
        "eq_chunk_count": int(eq_chunk_count),
        "eq_chunk_frac": round(eq_chunk_frac, 3),
        "n_distinct_dualities": int(len(dual_counter)),
        "dualities": dict(dual_counter.most_common()),
        "n_distinct_principles": int(len(princ_counter)),
        "top_principles": dict(princ_counter.most_common(15)),
        "author_mentions": dict(author_counter.most_common(15)),
        "top_phenomena": dict(phen_counter.most_common(15)),
        "equation_chunks_sample": eq_chunks,
    }


# ── classification ─────────────────────────────────────────

# Classification thresholds (heuristic; tuned for typical printed-page math density)
MATH_DENSE_MEAN = 0.012        # mean math_score across text's chunks
MATH_DENSE_FRAC = 0.30         # fraction of chunks with has_equations
STRUCT_DENSE_DUAL = 5          # n distinct dualities
STRUCT_DENSE_PRINC = 8         # n distinct principles


def classify(text_summary: dict) -> str:
    math = (text_summary["math_score_mean"] >= MATH_DENSE_MEAN
            or text_summary["eq_chunk_frac"] >= MATH_DENSE_FRAC)
    struct = (text_summary["n_distinct_dualities"] >= STRUCT_DENSE_DUAL
              or text_summary["n_distinct_principles"] >= STRUCT_DENSE_PRINC)
    if math and struct:
        return "MIXED"
    if math:
        return "MATH-DENSE"
    if struct:
        return "STRUCTURAL-CLAIM-DENSE"
    return "NEITHER"


# ── main ───────────────────────────────────────────────────

def main():
    t0 = time.time()
    print(f"[load] {CHUNKS}")
    df = pd.read_parquet(CHUNKS, columns=["text_path", "tier", "chunk_index", "page_start", "page_end", "content"])
    print(f"  rows: {len(df):,}  unique texts: {df['text_path'].nunique()}")

    # OCR quality from pipeline_state if available
    state = json.loads(PIPELINE_STATE.read_text()) if PIPELINE_STATE.exists() else {}
    extraction_failures = set(state.get("extraction_failures", []))

    print(f"[scan] aggregating per-text features")
    per_text = {}
    text_paths = sorted(df["text_path"].unique())
    for i, tp in enumerate(text_paths):
        group = df[df["text_path"] == tp].sort_values("chunk_index")
        tier = group["tier"].iloc[0]
        summary = aggregate_text(group, tier)
        if not summary:
            continue
        summary["tier"] = tier
        summary["pages_max"] = int(group["page_end"].max())
        summary["category"] = classify(summary)
        per_text[tp] = summary
        if (i + 1) % 25 == 0 or i == len(text_paths) - 1:
            print(f"  [{i+1}/{len(text_paths)}]  elapsed {time.time()-t0:.1f}s")

    # ── corpus-wide aggregations ───────────────────────────
    print("[aggregate] corpus-wide rankings")

    # Citation map (intra-corpus)
    citation_map = defaultdict(Counter)  # citing_tier -> { cited_tier: count }
    for tp, s in per_text.items():
        citing_tier = s["tier"]
        for author, n in s["author_mentions"].items():
            cited_tier = CORPUS_AUTHORS.get(author)
            if cited_tier and cited_tier != citing_tier:
                citation_map[citing_tier][cited_tier] += n

    # Internal vs external citation totals
    internal_cites = 0
    external_cites = 0
    external_counter = Counter()
    for tp, s in per_text.items():
        for author, n in s["author_mentions"].items():
            if author in CORPUS_AUTHORS:
                internal_cites += n
            else:
                external_cites += n
                external_counter[author] += n

    # Top phenomena across corpus
    all_phen = Counter()
    for s in per_text.values():
        for p, n in s["top_phenomena"].items():
            all_phen[p] += n

    # Top principles across corpus
    all_princ = Counter()
    for s in per_text.values():
        for p, n in s["top_principles"].items():
            all_princ[p] += n

    # Per-category lists
    by_cat = defaultdict(list)
    for tp, s in per_text.items():
        by_cat[s["category"]].append(tp)

    # Math-dense ranked
    math_dense_ranked = sorted(
        [tp for tp, s in per_text.items() if s["category"] in ("MATH-DENSE", "MIXED")],
        key=lambda tp: per_text[tp]["math_score_mean"],
        reverse=True,
    )
    struct_dense_ranked = sorted(
        [tp for tp, s in per_text.items() if s["category"] in ("STRUCTURAL-CLAIM-DENSE", "MIXED")],
        key=lambda tp: (per_text[tp]["n_distinct_dualities"], per_text[tp]["n_distinct_principles"]),
        reverse=True,
    )

    # ── write JSON ─────────────────────────────────────────
    out = {
        "scan_time_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "corpus_stats": {
            "n_texts": len(per_text),
            "n_chunks": int(len(df)),
            "n_extraction_failures": int(len(extraction_failures)),
            "internal_citations_total": int(internal_cites),
            "external_citations_total": int(external_cites),
            "top_external_citations": dict(external_counter.most_common(15)),
        },
        "categories": {k: len(v) for k, v in by_cat.items()},
        "citation_map_intra_corpus": {k: dict(v) for k, v in citation_map.items()},
        "top_phenomena_corpus": dict(all_phen.most_common(20)),
        "top_principles_corpus": dict(all_princ.most_common(20)),
        "math_dense_ranked": math_dense_ranked,
        "struct_dense_ranked": struct_dense_ranked,
        "per_text": per_text,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"[write] {OUT_JSON}  ({OUT_JSON.stat().st_size/1024:.1f} KB)")

    # ── write Markdown ─────────────────────────────────────
    write_markdown(out)

    print(f"[write] {OUT_MD}")
    print()
    print("=" * 70)
    print(f"  texts analyzed:        {len(per_text):>4d}")
    print(f"  chunks scanned:        {len(df):>5,}")
    print(f"  intra-corpus citations:{internal_cites:>6,d}")
    print(f"  external citations:    {external_cites:>6,d}")
    print()
    print("  Top 5 MATH-DENSE texts (by mean math_score):")
    for tp in math_dense_ranked[:5]:
        s = per_text[tp]
        print(f"    [{s['math_score_mean']:.4f}] {tp}")
    print()
    print("  Top 5 STRUCTURAL-CLAIM-DENSE texts (by distinct dualities + principles):")
    for tp in struct_dense_ranked[:5]:
        s = per_text[tp]
        print(f"    [d={s['n_distinct_dualities']:>2d} p={s['n_distinct_principles']:>3d}] {tp}")
    print()
    print(f"  Categories: " + "  ".join(f"{k}={v}" for k, v in by_cat.items()))
    print(f"\nTotal wall: {time.time() - t0:.1f}s")


def write_markdown(out: dict):
    lines = []
    lines.append("# Structural inventory — teslatech_lineage corpus\n")
    lines.append(f"_Scan: {out['scan_time_utc']}_\n")
    cs = out["corpus_stats"]
    lines.append("## Corpus stats\n")
    lines.append(f"- Texts analyzed: **{cs['n_texts']}**")
    lines.append(f"- Chunks scanned: **{cs['n_chunks']:,}**")
    lines.append(f"- Extraction failures (low-text PDFs): **{cs['n_extraction_failures']}**")
    lines.append(f"- Intra-corpus citations: **{cs['internal_citations_total']:,}**")
    lines.append(f"- External citations: **{cs['external_citations_total']:,}**")
    lines.append("")

    lines.append("## Category breakdown\n")
    lines.append("| Category | n texts | meaning |")
    lines.append("|---|---:|---|")
    desc = {
        "MATH-DENSE": "high equation density; candidate for math_extracts module",
        "STRUCTURAL-CLAIM-DENSE": "many named principles + dualities; candidate for claim-encoding module (like Russell)",
        "MIXED": "both math-dense and structural-claim-dense",
        "NEITHER": "general reference / discursive; not module-target",
    }
    for cat, n in out["categories"].items():
        lines.append(f"| {cat} | {n} | {desc.get(cat, '')} |")
    lines.append("")

    lines.append("## Cross-author citation map (intra-corpus only)\n")
    lines.append("Counts of mentions of one tier's primary author within texts of another tier.\n")
    lines.append("| Citing tier | Most-cited corpus authors (by tier of mention) |")
    lines.append("|---|---|")
    for citing_tier, cited in out["citation_map_intra_corpus"].items():
        if not cited:
            continue
        cited_str = ", ".join(f"{k}={v}" for k, v in sorted(cited.items(), key=lambda x: -x[1])[:5])
        lines.append(f"| {citing_tier} | {cited_str} |")
    lines.append("")

    lines.append("## Top external citations\n")
    lines.append("| Author (external to corpus) | mentions |")
    lines.append("|---|---:|")
    for a, n in cs["top_external_citations"].items():
        lines.append(f"| {a} | {n} |")
    lines.append("")

    lines.append("## Top 20 named principles across the corpus\n")
    lines.append("| Principle/law/effect | total mentions |")
    lines.append("|---|---:|")
    for p, n in out["top_principles_corpus"].items():
        lines.append(f"| {p} | {n} |")
    lines.append("")

    lines.append("## Top 20 phenomena patterns across the corpus\n")
    lines.append("Pattern-matched verb-phrases (`produces`, `generates`, `causes`, `results in`, `gives rise to`, `emits`, `radiates`).\n")
    lines.append("| Phenomenon | mentions |")
    lines.append("|---|---:|")
    for p, n in out["top_phenomena_corpus"].items():
        lines.append(f"| {p} | {n} |")
    lines.append("")

    # MATH-DENSE list
    lines.append("## MATH-DENSE texts (ranked by mean math_score)\n")
    lines.append("Candidates for math_extracts module extraction.\n")
    lines.append("| math_score_mean | eq_frac | n_chunks | text |")
    lines.append("|---:|---:|---:|---|")
    for tp in out["math_dense_ranked"]:
        s = out["per_text"][tp]
        lines.append(f"| {s['math_score_mean']:.4f} | {s['eq_chunk_frac']:.2f} | {s['n_chunks']} | `{tp}` |")
    lines.append("")

    lines.append("### MATH-DENSE: equation-bearing chunk samples (top 3 texts, up to 5 chunks each)\n")
    for tp in out["math_dense_ranked"][:3]:
        s = out["per_text"][tp]
        lines.append(f"#### `{tp}`\n")
        lines.append("| chunk | pp | math_score | n_eq | n_sym | n_greek | preview |")
        lines.append("|---:|---|---:|---:|---:|---:|---|")
        for ec in s["equation_chunks_sample"]:
            preview = ec["preview"].replace("|", "\\|")
            lines.append(f"| {ec['chunk_index']} | {ec['page_start']}-{ec['page_end']} | "
                         f"{ec['math_score']:.4f} | {ec['n_eq']} | "
                         f"{ec['n_math_symbols']} | {ec['n_greek']} | {preview} |")
        lines.append("")

    # STRUCTURAL-CLAIM-DENSE list
    lines.append("## STRUCTURAL-CLAIM-DENSE texts\n")
    lines.append("Candidates for claim-encoding module (like russell_secret_of_light).\n")
    lines.append("Ranked by distinct dualities then distinct principles.\n")
    lines.append("| n_dualities | n_principles | n_chunks | text |")
    lines.append("|---:|---:|---:|---|")
    for tp in out["struct_dense_ranked"]:
        s = out["per_text"][tp]
        lines.append(f"| {s['n_distinct_dualities']} | {s['n_distinct_principles']} | "
                     f"{s['n_chunks']} | `{tp}` |")
    lines.append("")

    lines.append("### STRUCTURAL-CLAIM-DENSE: named principles per top text (up to 15 each)\n")
    for tp in out["struct_dense_ranked"][:5]:
        s = out["per_text"][tp]
        lines.append(f"#### `{tp}`\n")
        lines.append(f"Distinct dualities ({s['n_distinct_dualities']}): "
                     + ", ".join(f"`{k}`×{v}" for k, v in s["dualities"].items()) + "\n")
        lines.append(f"Top principles:\n")
        for p, n in s["top_principles"].items():
            lines.append(f"- `{p}` ×{n}")
        lines.append("")

    lines.append("## Per-text summary\n")
    lines.append("| Tier | Text | Pages | Chunks | Cat | math μ | eq% | dual | princ |")
    lines.append("|---|---|---:|---:|---|---:|---:|---:|---:|")
    sorted_paths = sorted(out["per_text"].keys())
    for tp in sorted_paths:
        s = out["per_text"][tp]
        cat = s["category"]
        lines.append(f"| {s['tier']} | `{tp.split('/')[-1][:80]}` | {s['pages_max']} | "
                     f"{s['n_chunks']} | {cat} | {s['math_score_mean']:.4f} | "
                     f"{int(s['eq_chunk_frac']*100)} | "
                     f"{s['n_distinct_dualities']} | {s['n_distinct_principles']} |")
    lines.append("")

    OUT_MD.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
