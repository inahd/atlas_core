"""Cross-axis correlation tests for harmonic correspondence v3.

Implements Task 3 of the brief:
  3a. Mohs-hardness vs dhātu-depth — does softness correlate with surface-tissue prescription?
  3b. Crystal symmetry vs graha-class — do certain crystal systems cluster with certain grahas?
  3c. Internal mode-octave-span vs body-system breadth — does spectral bandwidth match clinical breadth?

Uses Spearman rank correlation (no scipy dependency — implemented inline).

Usage:
    python3 run_cross_axis.py
"""
from __future__ import annotations
import math
from collections import Counter
from typing import List, Dict, Tuple


# ── Inventory subset with classical body-region prescriptions ─────────────
# Body-region attribution from Bhāva-prakāśa, Rasa-ratna-samuccaya, and the
# standard navaratna prescription compendia.  Only entries with a defensible
# classical body-region attribution are listed; non-prescribed minerals omitted.
DATA: List[Dict] = [
    # (mode_count is the v3 primary-5pct count)
    {"name": "Diamond",     "modes": 1,  "mohs": 10.0, "system": "cubic",        "graha": "Sukra",
     "body_region": "reproductive",   "dhatu_target": "shukra",  "graha_class": "tridosha-supreme",  "clinical_breadth": 5},
    {"name": "Pearl",       "modes": 3,  "mohs": 3.5,  "system": "orthorhombic", "graha": "Chandra",
     "body_region": "calcium/skin",   "dhatu_target": "rasa",    "graha_class": "soma-cooling",      "clinical_breadth": 4},
    {"name": "Coral",       "modes": 3,  "mohs": 3.5,  "system": "orthorhombic", "graha": "Mangala",
     "body_region": "blood",          "dhatu_target": "rakta",   "graha_class": "agni-active",       "clinical_breadth": 4},
    {"name": "Corundum-Ruby","modes": 7, "mohs": 9.0,  "system": "trigonal",     "graha": "Surya",
     "body_region": "heart",          "dhatu_target": "majja",   "graha_class": "agni-supreme",      "clinical_breadth": 6},
    {"name": "Corundum-Sapphire","modes": 7,"mohs":9.0, "system": "trigonal",    "graha": "Sani",
     "body_region": "joints/nervous", "dhatu_target": "asthi",   "graha_class": "tamas-deep",        "clinical_breadth": 6},
    {"name": "Beryl-Emerald","modes": 11,"mohs": 7.75, "system": "hexagonal",    "graha": "Budha",
     "body_region": "nervous/skin",   "dhatu_target": "majja",   "graha_class": "buddhi-quick",      "clinical_breadth": 7},
    {"name": "Topaz",       "modes": 11, "mohs": 8.0,  "system": "orthorhombic", "graha": "Brhaspati",
     "body_region": "liver/wisdom",   "dhatu_target": "majja",   "graha_class": "buddhi-deep",       "clinical_breadth": 7},
    {"name": "Garnet-Hessonite","modes": 9,"mohs":7.25,"system": "cubic",        "graha": "Rahu",
     "body_region": "lower-extremities","dhatu_target": "asthi",  "graha_class": "karmic-incoming",  "clinical_breadth": 5},
    {"name": "Chrysoberyl", "modes": 9,  "mohs": 8.5,  "system": "orthorhombic", "graha": "Ketu",
     "body_region": "feet/spiritual", "dhatu_target": "majja",   "graha_class": "karmic-outgoing",   "clinical_breadth": 5},
    # uparatnas / classical extensions
    {"name": "Moonstone",   "modes": 4,  "mohs": 6.0,  "system": "orthorhombic", "graha": "Chandra",
     "body_region": "mind/cycle",     "dhatu_target": "rasa",    "graha_class": "soma-cooling",      "clinical_breadth": 4},
    {"name": "Lapis",       "modes": 3,  "mohs": 5.25, "system": "cubic",        "graha": None,
     "body_region": "throat/speech",  "dhatu_target": "rasa",    "graha_class": None,                "clinical_breadth": 3},
    {"name": "Olivine",     "modes": 8,  "mohs": 6.75, "system": "orthorhombic", "graha": None,
     "body_region": "digestive",      "dhatu_target": "meda",    "graha_class": None,                "clinical_breadth": 4},
    {"name": "Tourmaline",  "modes": 9,  "mohs": 7.25, "system": "trigonal",     "graha": None,
     "body_region": "fascia/electric","dhatu_target": "mamsa",   "graha_class": None,                "clinical_breadth": 5},
    {"name": "Quartz",      "modes": 11, "mohs": 7.0,  "system": "trigonal",     "graha": None,
     "body_region": "mental",         "dhatu_target": "majja",   "graha_class": None,                "clinical_breadth": 6},
]

# Dhātu depth ranking: 1 = surface (rasa), 7 = deepest (shukra/ojas)
DHATU_DEPTH = {
    "rasa":   1,  # plasma
    "rakta":  2,  # blood
    "mamsa":  3,  # muscle
    "meda":   4,  # adipose
    "asthi":  5,  # bone
    "majja":  6,  # marrow / nervous tissue
    "shukra": 7,  # generative essence
}


# ── Spearman rank correlation (inline) ──────────────────────────────────

def rank(xs):
    """Return ranks of xs, averaging ties."""
    n = len(xs)
    pairs = sorted(enumerate(xs), key=lambda p: p[1])
    ranks = [0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and pairs[j + 1][1] == pairs[i][1]:
            j += 1
        avg_rank = (i + j + 2) / 2  # 1-based ranks
        for k in range(i, j + 1):
            ranks[pairs[k][0]] = avg_rank
        i = j + 1
    return ranks


def pearson(x, y):
    n = len(x)
    mx = sum(x) / n
    my = sum(y) / n
    num = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    sx = math.sqrt(sum((xi - mx) ** 2 for xi in x))
    sy = math.sqrt(sum((yi - my) ** 2 for yi in y))
    if sx == 0 or sy == 0:
        return float("nan")
    return num / (sx * sy)


def spearman(x, y):
    return pearson(rank(x), rank(y))


def spearman_p_two_sided(rho, n):
    """Approximate two-sided p-value via t-distribution (large-n).
    For small n this is a rough approximation; use as guidance, not proof.
    """
    if n < 4 or abs(rho) >= 1.0:
        return float("nan")
    t = rho * math.sqrt((n - 2) / max(1e-12, 1 - rho * rho))
    # Approximate two-sided p using survival function of |t|
    # via crude integration of the t-distribution (n-2 dof).  For n small
    # this is approximate; we report it labeled "approx".
    df = n - 2
    # Use Abramowitz & Stegun 26.7.8 large-df Gaussian approximation
    # adjusted with a small-df correction (Bailey 1981).
    z = abs(t) * (1 - (1 / (4 * df)))
    # Cumulative normal via error function
    p_one = 0.5 * (1 - math.erf(z / math.sqrt(2)))
    return min(1.0, 2 * p_one)


# ── Test 3a: Mohs vs dhātu depth ────────────────────────────────────────

def test_3a():
    mohs = [d["mohs"] for d in DATA]
    depth = [DHATU_DEPTH[d["dhatu_target"]] for d in DATA]
    rho = spearman(mohs, depth)
    n = len(mohs)
    p = spearman_p_two_sided(rho, n)
    return {
        "test": "3a — Mohs hardness vs dhātu-depth",
        "n": n, "spearman_rho": rho, "p_approx": p,
        "interpretation": (
            "Hypothesis: softer gems → surface dhātus (rasa, rakta), harder "
            "gems → deeper dhātus (asthi, majja, shukra). Positive rho "
            "supports the hypothesis."
        ),
    }


# ── Test 3b: Crystal system vs graha class ──────────────────────────────

def test_3b():
    """Two-way table of crystal system vs graha class.
    Reports the contingency for visual inspection."""
    rows = [d for d in DATA if d["graha"] is not None]
    counter = Counter()
    for r in rows:
        counter[(r["system"], r["graha_class"])] += 1
    table = sorted(counter.items())
    return {
        "test": "3b — crystal system × graha class",
        "n": len(rows),
        "contingency": table,
        "interpretation": (
            "Visual inspection: do specific systems concentrate in specific "
            "graha-classes? Examples: cubic gems for karmic-axis (Rāhu/Ketu); "
            "trigonal/orthorhombic for the agni-axis grahas (Sūrya, Maṅgala, "
            "Bṛhaspati). Formal chi-squared not run on this small n."
        ),
    }


# ── Test 3c: Mode-octave-span vs clinical breadth ────────────────────────

# Octave spans (log2(max_mode/min_mode)) for v3 minerals:
OCTAVE_SPANS = {
    "Diamond": 0.0,                     # one mode
    "Pearl": math.log2(1086 / 206),     # ≈ 2.40
    "Coral": math.log2(1086 / 206),
    "Corundum-Ruby": math.log2(750 / 379),       # ≈ 0.984
    "Corundum-Sapphire": math.log2(750 / 379),
    "Beryl-Emerald": math.log2(1244 / 320),      # ≈ 1.96
    "Topaz": math.log2(1156 / 159),              # ≈ 2.86
    "Garnet-Hessonite": math.log2(1010 / 167),   # ≈ 2.60
    "Chrysoberyl": math.log2(924 / 161),         # ≈ 2.52
    "Moonstone": math.log2(815 / 285),           # ≈ 1.52
    "Lapis": math.log2(1096 / 258),              # ≈ 2.09
    "Olivine": math.log2(962 / 225),             # ≈ 2.10
    "Tourmaline": math.log2(1072 / 220),         # ≈ 2.29
    "Quartz": math.log2(1163 / 128),             # ≈ 3.18
}

def test_3c():
    pairs = []
    for d in DATA:
        span = OCTAVE_SPANS.get(d["name"])
        if span is None or span == 0:
            continue
        pairs.append((span, d["clinical_breadth"], d["name"]))
    spans = [p[0] for p in pairs]
    breadth = [p[1] for p in pairs]
    rho = spearman(spans, breadth)
    n = len(pairs)
    p = spearman_p_two_sided(rho, n)
    return {
        "test": "3c — octave span vs clinical breadth",
        "n": n, "spearman_rho": rho, "p_approx": p,
        "data": pairs,
        "interpretation": (
            "Hypothesis: gems prescribed for broad-spectrum conditions (multi-"
            "system, chronic, multi-dhātu) have wider octave-spans of internal "
            "modes. Positive rho supports."
        ),
    }


# ── Driver ──────────────────────────────────────────────────────────────

def main():
    print("=" * 72)
    print("Cross-Axis Correlation Tests — Harmonic Correspondence v3 / Task 3")
    print("=" * 72)

    for fn in [test_3a, test_3b, test_3c]:
        r = fn()
        print(f"\n{r['test']}  (n={r['n']})")
        if "spearman_rho" in r:
            print(f"  Spearman ρ = {r['spearman_rho']:+.3f}")
            print(f"  approx two-sided p = {r['p_approx']:.4f}")
        if "contingency" in r:
            for (system, gclass), count in r["contingency"]:
                print(f"  {system:>14} × {gclass:<22} : {count}")
        if "data" in r:
            print("  span (octaves) | breadth | gem")
            for s, b, n in sorted(r["data"]):
                print(f"  {s:>13.2f} | {b:>7} | {n}")
        print(f"  → {r['interpretation']}")

    print("\n" + "=" * 72)
    print("See cross_axis_correlations.md for synthesis.")
    print("=" * 72)


if __name__ == "__main__":
    main()
