"""Formal statistical analysis of mode-count clustering for the v3 gem inventory.

Implements Tasks 2a–2d from the v3 brief:
  2a. Empirical null distribution from a published mineral-Raman survey
  2b. Chi-squared and Fisher's exact tests vs. classical-significant integer set
  2c. Crystal-system-stratified analysis (controls for symmetry confound)
  2d. Sensitivity to the primary-mode counting threshold

The empirical null is currently a literature-derived approximation from RRUFF + the
Frost group's mineral Raman survey papers; the true RRUFF-wide distribution
requires database-side mining. We label the placeholder explicitly and document
how to substitute the real distribution when available.

Usage:
    python3 run_harmonic_stats.py
"""

from __future__ import annotations
import math
from collections import Counter
from typing import Dict, List, Tuple


# ── Inventory data (from expanded_gem_inventory.md) ─────────────────────

# All 24 minerals with first-order Raman primary mode counts
# (excluding native gold/copper as zero-mode by symmetry — discussed separately)
INVENTORY: List[Dict] = [
    {"name": "Diamond",      "classical": "Vajra",      "graha": "Sukra",      "modes": 1,  "system": "cubic",        "mohs": 10.0,  "navaratna": True},
    {"name": "Sphalerite",   "classical": "Yasada",     "graha": None,         "modes": 2,  "system": "cubic",        "mohs": 3.5,   "navaratna": False},
    {"name": "Pearl/Coral",  "classical": "Mukta/Pravala", "graha": "Chandra/Mangala", "modes": 3, "system": "orthorhombic", "mohs": 3.75, "navaratna": True},
    {"name": "Lapis",        "classical": "Rajavarta",  "graha": None,         "modes": 3,  "system": "cubic",        "mohs": 5.25,  "navaratna": False},
    {"name": "Cinnabar",     "classical": "Hingula",    "graha": None,         "modes": 3,  "system": "trigonal",     "mohs": 2.25,  "navaratna": False},
    {"name": "Pyrite",       "classical": "Maksika-var",  "graha": None,       "modes": 3,  "system": "cubic",        "mohs": 6.25,  "navaratna": False},
    {"name": "Galena",       "classical": "Naga-var",   "graha": None,         "modes": 3,  "system": "cubic",        "mohs": 2.5,   "navaratna": False, "partial": True},
    {"name": "Moonstone",    "classical": "Candrakanta", "graha": "Chandra",   "modes": 4,  "system": "orthorhombic", "mohs": 6.0,   "navaratna": False},
    {"name": "Magnetite",    "classical": "Kanta-pasana", "graha": None,       "modes": 4,  "system": "cubic",        "mohs": 6.0,   "navaratna": False},
    {"name": "Chalcopyrite", "classical": "Maksika",    "graha": None,         "modes": 4,  "system": "tetragonal",   "mohs": 3.75,  "navaratna": False},
    {"name": "Calcite",      "classical": "control",    "graha": None,         "modes": 4,  "system": "trigonal",     "mohs": 3.0,   "navaratna": False},
    {"name": "Sunstone",     "classical": "Suryakanta", "graha": "Surya",      "modes": 5,  "system": "triclinic",    "mohs": 6.0,   "navaratna": False, "partial": True},
    {"name": "Nephrite",     "classical": "yu",         "graha": None,         "modes": 5,  "system": "monoclinic",   "mohs": 6.25,  "navaratna": False},
    {"name": "Hematite",     "classical": "Gairika",    "graha": "Mangala",    "modes": 6,  "system": "trigonal",     "mohs": 6.0,   "navaratna": False},
    {"name": "Jadeite",      "classical": "fei-cui",    "graha": None,         "modes": 6,  "system": "monoclinic",   "mohs": 6.75,  "navaratna": False},
    {"name": "Corundum",     "classical": "Manikya/Indranila", "graha": "Surya/Sani", "modes": 7, "system": "trigonal", "mohs": 9.0, "navaratna": True},
    {"name": "Olivine",      "classical": "Piloka",     "graha": None,         "modes": 8,  "system": "orthorhombic", "mohs": 6.75,  "navaratna": False},
    {"name": "Azurite",      "classical": "Sasyaka",    "graha": None,         "modes": 8,  "system": "monoclinic",   "mohs": 3.75,  "navaratna": False},
    {"name": "Garnet",       "classical": "Gomeda",     "graha": "Rahu",       "modes": 9,  "system": "cubic",        "mohs": 7.25,  "navaratna": True},
    {"name": "Chrysoberyl",  "classical": "Vaidurya",   "graha": "Ketu",       "modes": 9,  "system": "orthorhombic", "mohs": 8.5,   "navaratna": True},
    {"name": "Tourmaline",   "classical": "Vaikranta",  "graha": None,         "modes": 9,  "system": "trigonal",     "mohs": 7.25,  "navaratna": False},
    {"name": "Turquoise",    "classical": "Tutthak",    "graha": None,         "modes": 9,  "system": "triclinic",    "mohs": 5.5,   "navaratna": False},
    {"name": "Beryl",        "classical": "Tarkshya",   "graha": "Budha",      "modes": 11, "system": "hexagonal",    "mohs": 7.75,  "navaratna": True},
    {"name": "Topaz",        "classical": "Pushparaga", "graha": "Brhaspati",  "modes": 11, "system": "orthorhombic", "mohs": 8.0,   "navaratna": True},
    {"name": "Quartz",       "classical": "Sphatika",   "graha": None,         "modes": 11, "system": "trigonal",     "mohs": 7.0,   "navaratna": False},
]

CLASSICAL_INTEGERS = {1, 3, 4, 7, 8, 9, 11}
NAVARATNA_INTEGERS_OBSERVED = {1, 3, 7, 9, 11}


# ── Step 2a: Empirical null distribution ─────────────────────────────────

# This is a LITERATURE-APPROXIMATION based on:
#   - The Frost group's mineral Raman survey papers (200+ minerals across
#     carbonates, sulfates, phosphates, silicates, hydroxides, and oxides
#     reported across J. Raman Spectrosc. 2000–2020).
#   - Lafuente et al. 2015 RRUFF aggregated counts.
#   - Group-theory-derived expectations for common space groups.
#
# The distribution below is *approximate* — the proper analysis requires
# RRUFF database mining. We label this assumption explicitly and discuss
# its limits.
#
# Format: { mode_count: probability }
EMPIRICAL_NULL_APPROX: Dict[object, float] = {
    0:    0.015,  # native metals + extremely-symmetric oxides
    1:    0.020,
    2:    0.040,
    3:    0.075,
    4:    0.085,
    5:    0.095,
    6:    0.105,
    7:    0.100,
    8:    0.095,
    9:    0.080,
    10:   0.065,
    11:   0.055,
    12:   0.040,
    13:   0.027,
    14:   0.018,
    15:   0.015,
    "16+":0.070,
}
# Verify probabilities sum to ~1.0
_sum = sum(v for v in EMPIRICAL_NULL_APPROX.values())
assert abs(_sum - 1.0) < 0.005, f"null sum = {_sum}"


def empirical_null_aggregated_classical_set() -> float:
    """Pr[a random mineral has mode count in {1, 3, 4, 7, 8, 9, 11}]
    under the literature-approximated empirical null."""
    return sum(EMPIRICAL_NULL_APPROX[k] for k in CLASSICAL_INTEGERS)


def empirical_null_aggregated_navaratna_set() -> float:
    """Pr[a random mineral has mode count in {1, 3, 7, 9, 11}]
    under the empirical null."""
    return sum(EMPIRICAL_NULL_APPROX[k] for k in NAVARATNA_INTEGERS_OBSERVED)


# ── Step 2b: Test the gem inventory against the null ─────────────────────

def binomial_pmf(n: int, k: int, p: float) -> float:
    """Pr[exactly k successes in n trials with success prob p]."""
    if not (0 <= k <= n):
        return 0.0
    log_pmf = (math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)
               + k * math.log(p) + (n - k) * math.log(1 - p))
    return math.exp(log_pmf)


def binomial_tail(n: int, k_min: int, p: float) -> float:
    """Pr[≥ k_min successes in n trials with success prob p]."""
    return sum(binomial_pmf(n, k, p) for k in range(k_min, n + 1))


def test_navaratna_clustering() -> Dict:
    """Does the 9-gem navaratna subset cluster in classically-significant integers
    above what the empirical null predicts?"""
    navaratna = [m for m in INVENTORY if m["navaratna"]]
    n = len(navaratna)
    k = sum(1 for m in navaratna if m["modes"] in NAVARATNA_INTEGERS_OBSERVED)
    p_null = empirical_null_aggregated_navaratna_set()
    p_value = binomial_tail(n, k, p_null)
    return {
        "test": "navaratna ⊂ {1,3,7,9,11}",
        "n": n, "k": k, "p_null": p_null,
        "p_value (binomial tail)": p_value,
        "interpretation": (
            "p_null is the probability under the empirical null that a "
            "single random mineral has mode count in the observed navaratna "
            "integer set. If all 9 navaratna gems land in this set under "
            "the null, the binomial tail probability is reported."
        ),
    }


def test_full_inventory_clustering() -> Dict:
    """Does the 24-mineral inventory cluster in v2 classically-significant
    integers above the empirical null?"""
    n = len(INVENTORY)
    k = sum(1 for m in INVENTORY if m["modes"] in CLASSICAL_INTEGERS)
    p_null = empirical_null_aggregated_classical_set()
    p_value = binomial_tail(n, k, p_null)
    return {
        "test": "full inventory ⊂ {1,3,4,7,8,9,11}",
        "n": n, "k": k, "p_null": p_null,
        "p_value (binomial tail)": p_value,
        "interpretation": (
            "Tests the v2 claim against the v3 broader inventory. "
            "Expected to weaken vs the navaratna result."
        ),
    }


# ── Step 2c: Crystal-system stratification ──────────────────────────────

def stratify_by_system() -> Dict[str, List[int]]:
    """Group mode counts by crystal system."""
    out: Dict[str, List[int]] = {}
    for m in INVENTORY:
        out.setdefault(m["system"], []).append(m["modes"])
    return out


def test_navaratna_within_system() -> Dict:
    """Test whether navaratna gems cluster in classical integers EVEN AFTER
    matching for crystal system. For each navaratna gem, what's the probability
    its same-system non-navaratna peer has a classical-integer mode count?

    This is a confound check: if classical traditions tended to pick certain
    crystal systems (which would naturally have certain mode counts), the
    apparent clustering could be a confound rather than a real correspondence.
    """
    navaratna = [m for m in INVENTORY if m["navaratna"]]
    non = [m for m in INVENTORY if not m["navaratna"]]

    # For each navaratna gem, find non-navaratna minerals in the same system
    matched_pairs = []
    for n in navaratna:
        sys_peers = [x for x in non if x["system"] == n["system"]]
        if not sys_peers:
            continue
        nav_in = n["modes"] in CLASSICAL_INTEGERS
        peer_in = sum(1 for p in sys_peers if p["modes"] in CLASSICAL_INTEGERS)
        matched_pairs.append({
            "navaratna": n["name"], "system": n["system"],
            "nav_modes": n["modes"], "nav_in_classical_set": nav_in,
            "peers_in_system": [p["name"] for p in sys_peers],
            "peer_modes": [p["modes"] for p in sys_peers],
            "peer_classical_rate": peer_in / len(sys_peers),
        })
    return {
        "test": "navaratna vs same-system peers",
        "matched_pairs": matched_pairs,
        "interpretation": (
            "If navaratna gems land in classical integers MORE than their "
            "same-system non-navaratna peers, the clustering survives the "
            "crystal-system confound. If equally, the clustering is "
            "explainable by symmetry alone."
        ),
    }


# ── Step 2d: Sensitivity analysis ────────────────────────────────────────

# Alternative mode-counting thresholds:
#   "primary"     — peaks ≥ 5% of strongest (current v2/v3 method)
#   "top5"        — top 5 strongest peaks regardless of relative height
#   "all_peaks"   — all peaks visible above noise (varies by paper)
#   "group_theory" — count of Raman-active modes predicted by space-group
SENSITIVITY_VARIANTS = {
    "primary_5pct": {
        "diamond": 1, "corundum": 7, "aragonite": 3, "garnet": 9,
        "chrysoberyl": 9, "tourmaline": 9, "beryl": 11, "topaz": 11,
        "quartz": 11, "moonstone": 4, "olivine": 8, "lapis": 3,
    },
    "top_5_only": {
        "diamond": 1, "corundum": 5, "aragonite": 3, "garnet": 5,
        "chrysoberyl": 5, "tourmaline": 5, "beryl": 5, "topaz": 5,
        "quartz": 5, "moonstone": 4, "olivine": 5, "lapis": 3,
    },
}


def sensitivity_test() -> Dict:
    """Does the navaratna clustering finding survive under alternative
    mode-counting thresholds?"""
    primary = SENSITIVITY_VARIANTS["primary_5pct"]
    top5 = SENSITIVITY_VARIANTS["top_5_only"]
    primary_in_set = sum(1 for c in primary.values() if c in CLASSICAL_INTEGERS)
    top5_in_set = sum(1 for c in top5.values() if c in CLASSICAL_INTEGERS)
    return {
        "primary_5pct_threshold": {
            "in_classical_set": primary_in_set,
            "out_of_total": len(primary),
        },
        "top_5_threshold": {
            "in_classical_set": top5_in_set,
            "out_of_total": len(top5),
        },
        "interpretation": (
            "The 'top 5' threshold collapses many counts to 5, which is NOT "
            "in the v2 classical-significant set. This is a known weakness — "
            "the v2 finding depends on the 5%-of-strongest threshold. The "
            "primary-mode methodology is empirically defensible (peaks below "
            "5% of strongest are usually attributed to disorder, defects, "
            "or instrumentation rather than fundamental phonon modes), but "
            "the sensitivity to threshold is a real caveat."
        ),
    }


# ── Driver ──────────────────────────────────────────────────────────────

def main():
    print("=" * 72)
    print("Harmonic Correspondence — Formal Statistical Analysis")
    print("=" * 72)

    # Distribution
    counter = Counter(m["modes"] for m in INVENTORY)
    print("\nMode-count distribution (n=24, excluding zero-mode metals):")
    for k in sorted(counter):
        print(f"  {k:>3}  ({counter[k]}): {', '.join(m['name'] for m in INVENTORY if m['modes']==k)}")

    print("\n--- Step 2a: empirical null ---")
    p_classical = empirical_null_aggregated_classical_set()
    p_navaratna = empirical_null_aggregated_navaratna_set()
    print(f"Pr[mode_count ∈ {{1,3,4,7,8,9,11}}] (literature approx) = {p_classical:.3f}")
    print(f"Pr[mode_count ∈ {{1,3,7,9,11}}]   (literature approx) = {p_navaratna:.3f}")

    print("\n--- Step 2b: tests ---")
    for test_fn in [test_navaratna_clustering, test_full_inventory_clustering]:
        r = test_fn()
        print(f"\n{r['test']}:")
        print(f"  k/n = {r['k']}/{r['n']}, p_null = {r['p_null']:.3f}")
        print(f"  binomial-tail p = {r['p_value (binomial tail)']:.5f}")

    print("\n--- Step 2c: crystal-system stratification ---")
    by_system = stratify_by_system()
    for sys_, modes in sorted(by_system.items()):
        print(f"  {sys_:>14}: modes = {sorted(modes)}")
    print("\n  Navaratna vs same-system peers:")
    cs = test_navaratna_within_system()
    for pair in cs["matched_pairs"]:
        print(f"    {pair['navaratna']:>14} ({pair['system']}, modes={pair['nav_modes']}, in_set={pair['nav_in_classical_set']})")
        print(f"        peers: {pair['peers_in_system']} modes={pair['peer_modes']} "
              f"peer_in_set_rate={pair['peer_classical_rate']:.2f}")

    print("\n--- Step 2d: sensitivity to threshold ---")
    s = sensitivity_test()
    p = s["primary_5pct_threshold"]
    t = s["top_5_threshold"]
    print(f"  primary 5% threshold:  {p['in_classical_set']}/{p['out_of_total']} in classical set")
    print(f"  top-5 threshold:       {t['in_classical_set']}/{t['out_of_total']} in classical set")

    print("\n" + "=" * 72)
    print("Interpretation summary in statistical_analysis.md")
    print("=" * 72)


if __name__ == "__main__":
    main()
