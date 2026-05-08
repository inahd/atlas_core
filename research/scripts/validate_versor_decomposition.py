"""
Validation: versor-aware (complex Z_k) vs real-cosine-sum reductions over
the 2025 10-min panchanga grid.

Generates per-timestamp per-pair-per-k complex amplitudes Z_k from the
full transit chart at Gainesville, computes both old and new pipelines,
and reports:

  1. |Z_k|² == Re² + Im²   (sanity check on the complex math)
  2. Distribution of (old composite_mean, new composite_mean) discrepancy
  3. Distribution of composite_mode_ratio across the year

Outputs PNGs to research/scripts/plots_versor/. No commits.
"""
from __future__ import annotations

import math
import os
import sys
import time
from datetime import timezone
from itertools import combinations
from multiprocessing import Pool

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = "/home/inahd/atlas_core"
sys.path.insert(0, ROOT)

GRID = os.path.join(ROOT, "datasets/panchanga/grid_10min_2025.parquet")
OUT_DIR = os.path.join(ROOT, "research/scripts/plots_versor")
os.makedirs(OUT_DIR, exist_ok=True)

LAT, LON = 29.65, -82.34
K_VALUES = [1, 3, 4, 6, 7, 12]   # _DEFAULT_K from jyotisha_engine

# Grahas as ordered by compute_chart insertion: from _SWE_GRAHAS, plus Rahu/Ketu.
GRAHA_NAMES = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]


def _worker(ts_chunk):
    """Per chunk: compute (old_composite_mean_avg, new_composite_mean_avg,
    composite_mode_ratio, sanity_max_residual) for each timestamp."""
    from npu_engine.jyotisha_engine import compute_chart
    out = np.empty((len(ts_chunk), 5), dtype=np.float64)
    for i, ts in enumerate(ts_chunk):
        dt = ts.to_pydatetime()
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        ch = compute_chart(dt, LAT, LON)
        grahas = ch["grahas"]
        # Targets = all grahas (matches compute_wave_field default)
        # +Lagna (matches compute_chart's wave_targets — line 209)
        longs = {n: float(grahas[n]["deg_absolute"]) for n in GRAHA_NAMES if n in grahas}
        longs["Lagna"] = float(ch["ascendant"]["deg_absolute"])
        names = list(longs.keys())
        targets = list(longs.keys())

        # Vectorize all (target, k, pair) at once
        L = np.array([longs[n] for n in names], dtype=np.float64)  # source longs
        T = np.array([longs[t] for t in targets], dtype=np.float64)  # target longs
        pairs = list(combinations(range(len(names)), 2))

        # Old: Re-only cosine sum per (target, pair, k)
        # New: complex Z_k per (target, pair, k)
        # Shape: (n_targets, n_pairs, n_k)
        nt = len(targets); np_pairs = len(pairs); nk = len(K_VALUES)
        K = np.array(K_VALUES, dtype=np.float64)

        old_amp = np.empty((nt, np_pairs, nk), dtype=np.float64)
        z_amp = np.empty((nt, np_pairs, nk), dtype=np.complex128)
        for pi, (a, b) in enumerate(pairs):
            la = L[a]; lb = L[b]
            d_a = np.radians(T - la)[:, None] * K[None, :]    # (nt, nk)
            d_b = np.radians(T - lb)[:, None] * K[None, :]
            old_amp[:, pi, :] = np.cos(d_a) + np.cos(d_b)
            z_amp[:, pi, :] = np.exp(1j * d_a) + np.exp(1j * d_b)

        # ── sanity: |Z|² == Re² + Im² ─────────────
        residual = np.abs(np.abs(z_amp)**2 - (z_amp.real**2 + z_amp.imag**2)).max()

        # ── OLD pipeline: composite[t][k] = sum_pairs |cos+cos|, normalize, mean k
        old_comp = np.abs(old_amp).sum(axis=1)   # (nt, nk) sum_pairs |cos+cos|
        mn_o = old_comp.min(axis=0, keepdims=True)
        mx_o = old_comp.max(axis=0, keepdims=True)
        rng_o = np.where(mx_o > mn_o, mx_o - mn_o, 1.0)
        old_norm = (old_comp - mn_o) / rng_o
        old_cm = old_norm.mean(axis=1)
        old_avg = float(old_cm.mean())

        # ── NEW (current engine) pipeline: composite[t][k] = sum_pairs |Re(Z)|
        # which equals sum_pairs |cos+cos| by identity. Should match old exactly.
        new_comp = np.abs(z_amp.real).sum(axis=1)
        mn_n = new_comp.min(axis=0, keepdims=True)
        mx_n = new_comp.max(axis=0, keepdims=True)
        rng_n = np.where(mx_n > mn_n, mx_n - mn_n, 1.0)
        new_norm = (new_comp - mn_n) / rng_n
        new_cm = new_norm.mean(axis=1)
        new_avg = float(new_cm.mean())

        # ── mode decomposition ─────────────────────
        z_sum = z_amp.sum(axis=1)               # (nt, nk) complex vector sum across pairs
        mag = np.abs(z_sum.real)
        die = np.abs(z_sum.imag)
        eps = 1e-12
        total_mag = mag.sum(); total_die = die.sum()
        mode_ratio = float(total_die / (total_mag + total_die + eps))

        # ── degeneracy check: |Z_k| collapse across targets ─────────
        # |Z_k| at fixed (pair, k) is target-invariant. Verify that
        # sum_pairs |Z_k| at fixed k is identical across all targets.
        absZ_sum_per_t_k = np.abs(z_amp).sum(axis=1)  # (nt, nk)
        # Spread (max-min) across targets per k, max across k:
        absZ_spread = (absZ_sum_per_t_k.max(axis=0) - absZ_sum_per_t_k.min(axis=0)).max()

        out[i] = (old_avg, new_avg, mode_ratio, residual, absZ_spread)
    return out


def main():
    t0 = time.time()
    print(f"[load] grid {GRID}")
    grid = pd.read_parquet(GRID, columns=["timestamp"])
    ts = grid["timestamp"]
    if ts.dt.tz is None:
        ts = ts.dt.tz_localize("UTC")
    n = len(ts)
    print(f"  rows: {n:,}")

    n_workers = max(1, min(12, (os.cpu_count() or 4) - 2))
    chunk_size = max(1, n // (n_workers * 8))
    chunks = [ts.iloc[i:i + chunk_size].tolist() for i in range(0, n, chunk_size)]
    print(f"  workers={n_workers}  chunks={len(chunks)}  chunk_size~{chunk_size}")

    out = np.empty((n, 5), dtype=np.float64)
    cursor = 0
    with Pool(processes=n_workers) as pool:
        for j, arr in enumerate(pool.imap(_worker, chunks)):
            k = arr.shape[0]
            out[cursor:cursor + k] = arr
            cursor += k
            if (j + 1) % max(1, len(chunks) // 10) == 0 or j + 1 == len(chunks):
                pct = 100.0 * cursor / n
                print(f"  progress: {cursor:,}/{n:,} ({pct:.1f}%)  elapsed {time.time()-t0:.1f}s")

    old_cm = out[:, 0]
    new_cm = out[:, 1]
    mode_ratio = out[:, 2]
    residual = out[:, 3]
    absZ_spread = out[:, 4]

    # ── 1. sanity ─────────
    max_res = float(residual.max())
    print(f"\n[1] |Z|² == Re² + Im² sanity: max residual = {max_res:.3e}  (should be ~ 1e-14 or smaller)")
    print(f"[1b] |Z_k| target-invariance check (max spread across targets at any (t,k)):")
    print(f"     mean spread = {absZ_spread.mean():.3e}, max spread = {absZ_spread.max():.3e}")
    print(f"     (should be ~ machine precision; confirms |Z_k| is target-invariant by identity)")

    # ── 2. discrepancy distribution ─────────
    diff_abs = np.abs(new_cm - old_cm)
    denom = np.maximum(np.abs(old_cm), 1e-9)
    diff_pct = 100.0 * diff_abs / denom
    print(f"\n[2] (old, new) composite_mean averaged across targets")
    print(f"    old:  mean={old_cm.mean():.4f}  std={old_cm.std():.4f}  range=[{old_cm.min():.4f}, {old_cm.max():.4f}]")
    print(f"    new:  mean={new_cm.mean():.4f}  std={new_cm.std():.4f}  range=[{new_cm.min():.4f}, {new_cm.max():.4f}]")
    print(f"    abs diff:   mean={diff_abs.mean():.5f}  median={np.median(diff_abs):.5f}  p95={np.percentile(diff_abs, 95):.5f}  max={diff_abs.max():.5f}")
    print(f"    pct diff:   mean={diff_pct.mean():.2f}%  median={np.median(diff_pct):.2f}%  p95={np.percentile(diff_pct, 95):.2f}%  max={diff_pct.max():.2f}%")
    print(f"    fraction of timestamps differing by >5%:  {100.0 * (diff_pct > 5).mean():.2f}%")
    print(f"    fraction of timestamps differing by >10%: {100.0 * (diff_pct > 10).mean():.2f}%")
    print(f"    fraction of timestamps differing by >25%: {100.0 * (diff_pct > 25).mean():.2f}%")
    pearson = float(np.corrcoef(old_cm, new_cm)[0, 1])
    print(f"    pearson(old, new): {pearson:+.4f}")

    # ── 3. mode_ratio distribution ─────────
    print(f"\n[3] composite_mode_ratio across 2025")
    print(f"    n: {len(mode_ratio)}")
    print(f"    mean: {mode_ratio.mean():.4f}")
    print(f"    std : {mode_ratio.std():.4f}")
    print(f"    min : {mode_ratio.min():.4f}    p05: {np.percentile(mode_ratio, 5):.4f}    p25: {np.percentile(mode_ratio, 25):.4f}")
    print(f"    p50 : {np.percentile(mode_ratio, 50):.4f}    p75: {np.percentile(mode_ratio, 75):.4f}    p95: {np.percentile(mode_ratio, 95):.4f}    max: {mode_ratio.max():.4f}")

    # ── plots ─────────
    print("\n[plots]")

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.hist(mode_ratio, bins=60, color="#3a76c4", edgecolor="black", linewidth=0.4)
    ax.axvline(0.5, color="#bf3030", linestyle="--", linewidth=1.0, label="0.5 (perfectly mixed)")
    ax.axvline(mode_ratio.mean(), color="#cc8030", linestyle="--", linewidth=1.0, label=f"mean={mode_ratio.mean():.3f}")
    ax.set_xlabel("composite_mode_ratio = die / (mag + die + eps)")
    ax.set_ylabel("count (10-min timestamps in 2025)")
    ax.set_title(f"Mode ratio distribution across 2025  (std={mode_ratio.std():.3f})")
    ax.legend()
    ax.grid(True, linestyle=":", alpha=0.4)
    fig.tight_layout()
    p = os.path.join(OUT_DIR, "composite_mode_ratio_hist.png")
    fig.savefig(p, dpi=120); plt.close(fig)
    print(f"  {p}")

    # Sample for the scatter plot to keep file manageable.
    rng = np.random.default_rng(20260508)
    if len(old_cm) > 10000:
        idx = rng.choice(len(old_cm), size=10000, replace=False)
    else:
        idx = np.arange(len(old_cm))
    fig, ax = plt.subplots(figsize=(6.5, 6.5))
    ax.scatter(old_cm[idx], new_cm[idx], s=3, alpha=0.25, color="#308050", edgecolors="none")
    lo = min(old_cm.min(), new_cm.min()); hi = max(old_cm.max(), new_cm.max())
    ax.plot([lo, hi], [lo, hi], color="#bf3030", linewidth=1.2, label="y=x")
    ax.set_xlabel("OLD composite_mean (real-cosine-sum reduction)")
    ax.set_ylabel("NEW composite_mean (|Z_k| reduction)")
    ax.set_title(f"Old vs new composite_mean (avg across targets)\npearson={pearson:+.4f}  median |%diff|={np.median(diff_pct):.1f}%")
    ax.legend()
    ax.grid(True, linestyle=":", alpha=0.4)
    fig.tight_layout()
    p = os.path.join(OUT_DIR, "old_vs_new_composite_mean.png")
    fig.savefig(p, dpi=120); plt.close(fig)
    print(f"  {p}")

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.hist(diff_pct, bins=60, color="#cc8030", edgecolor="black", linewidth=0.4)
    ax.axvline(np.median(diff_pct), color="#bf3030", linestyle="--", linewidth=1.0, label=f"median={np.median(diff_pct):.2f}%")
    ax.set_xlabel("100 · |new − old| / |old|   (per-timestamp)")
    ax.set_ylabel("count")
    ax.set_title("Per-timestamp percent discrepancy: NEW vs OLD composite_mean")
    ax.legend()
    ax.grid(True, linestyle=":", alpha=0.4)
    fig.tight_layout()
    p = os.path.join(OUT_DIR, "discrepancy_percent_hist.png")
    fig.savefig(p, dpi=120); plt.close(fig)
    print(f"  {p}")

    print(f"\nTotal wall: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
