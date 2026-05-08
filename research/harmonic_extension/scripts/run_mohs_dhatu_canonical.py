"""Canonical scipy-based stats + leave-one-out sensitivity + tie structure
for the Mohs hardness vs dhātu-depth correlation (Test 3a from
run_cross_axis.py).

Imports the DATA and DHATU_DEPTH from run_cross_axis.py so the inputs
remain authoritative.

Outputs three sections:
  1. Canonical scipy spearmanr + pearsonr on all 14 pairs
  2. Leave-one-out sensitivity table (sorted by rho ascending)
  3. Tie-structure descriptives

Usage:
    python3 run_mohs_dhatu_canonical.py
"""
from __future__ import annotations
import os
import sys
from collections import Counter

from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_cross_axis import DATA, DHATU_DEPTH  # noqa: E402


def load_pairs():
    mohs = [d["mohs"] for d in DATA]
    depth = [DHATU_DEPTH[d["dhatu_target"]] for d in DATA]
    names = [d["name"] for d in DATA]
    return names, mohs, depth


def task1(mohs, depth):
    print("=" * 72)
    print("TASK 1 — Canonical p-value via scipy")
    print("=" * 72)
    sp = stats.spearmanr(mohs, depth)
    pe = stats.pearsonr(mohs, depth)
    print(f"  n                  = {len(mohs)}")
    print(f"  spearman rho       = {sp.statistic!r}")
    print(f"  scipy_p_spearman   = {sp.pvalue!r}")
    print(f"  pearson r          = {pe.statistic!r}")
    print(f"  scipy_p_pearson    = {pe.pvalue!r}")


def task2(names, mohs, depth):
    print()
    print("=" * 72)
    print("TASK 2 — Leave-one-out sensitivity (Spearman)")
    print("=" * 72)
    rows = []
    for i, name in enumerate(names):
        m = mohs[:i] + mohs[i + 1:]
        d = depth[:i] + depth[i + 1:]
        sp = stats.spearmanr(m, d)
        rows.append((name, len(m), float(sp.statistic), float(sp.pvalue)))

    rows_sorted = sorted(rows, key=lambda r: r[2])

    print(f"  {'removed_gem':<22} {'n':>3} {'rho':>10} {'p_spearman':>14}")
    for name, n, rho, p in rows_sorted:
        print(f"  {name:<22} {n:>3} {rho:>+10.6f} {p:>14.6e}")

    rhos = [r[2] for r in rows]
    min_idx = rhos.index(min(rhos))
    max_idx = rhos.index(max(rhos))

    sp_full = stats.spearmanr(mohs, depth)
    full_rho = float(sp_full.statistic)
    drops = [(names[i], full_rho - rhos[i]) for i in range(len(rhos))]
    leverage = max(drops, key=lambda x: x[1])

    print()
    print(f"  full-sample rho             = {full_rho:+.6f}")
    print(f"  min rho (LOO)               = {rhos[min_idx]:+.6f}  (removed: {names[min_idx]})")
    print(f"  max rho (LOO)               = {rhos[max_idx]:+.6f}  (removed: {names[max_idx]})")
    print(f"  highest-leverage gem        = {leverage[0]}  (drop = {leverage[1]:+.6f})")


def task3(mohs, depth):
    print()
    print("=" * 72)
    print("TASK 3 — Tie structure")
    print("=" * 72)
    print(f"  unique Mohs values         = {len(set(mohs))}")
    print(f"  unique dhātu-depth values  = {len(set(depth))}")

    print()
    print("  Distribution of dhātu-depth (1..7):")
    depth_counts = Counter(depth)
    inv_depth = {v: k for k, v in DHATU_DEPTH.items()}
    for d in range(1, 8):
        c = depth_counts.get(d, 0)
        print(f"    depth {d} ({inv_depth[d]:<7}) : {c}")

    print()
    print("  Mohs duplicates (values shared by ≥2 gems):")
    mohs_counts = Counter(mohs)
    for val, c in sorted(mohs_counts.items()):
        if c >= 2:
            print(f"    Mohs = {val:>5} : {c} gems")


def main():
    names, mohs, depth = load_pairs()
    task1(mohs, depth)
    task2(names, mohs, depth)
    task3(mohs, depth)


if __name__ == "__main__":
    main()
