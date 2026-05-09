"""
Multi-pair versor mode-decomposition exploratory characterization,
2025 calendar year, 10-min cadence at the Gainesville lagna.

Reuses npu_engine.jyotisha_engine.compute_chart and
       npu_engine.jyotisha_engine.compute_pair_interference

NO statistical tests. NO pre-registration. Visualization + parquet only.

Pairs (10):
  sun_moon, sun_mars, sun_mercury, sun_venus, sun_jupiter, sun_saturn
  moon_mars, moon_mercury, moon_jupiter
  jupiter_saturn

Output:
  research/geosolar/exploratory/mode_phase_multi_pair_2025/
    all_pairs_modes_2025.parquet   (~52,560 rows × ~180 cols)
    mode_phase_polar_overlay.png
    mode_phase_vs_synodic_phase_grid.png
    mode_ratio_distribution_by_pair.png
    mode_ratio_correlation_matrix.png
    multi_pair_simultaneous_alignment.png
    README.md
"""
from __future__ import annotations

import math
import os
import sys
import time
from datetime import timezone
from multiprocessing import Pool

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = "/home/inahd/atlas_core"
sys.path.insert(0, ROOT)

OUT = os.path.join(ROOT, "research/geosolar/exploratory/mode_phase_multi_pair_2025")
GRID = os.path.join(ROOT, "datasets/panchanga/grid_10min_2025.parquet")
OUT_PARQUET = os.path.join(OUT, "all_pairs_modes_2025.parquet")

LAT, LON = 29.65, -82.34
K_VALUES = [1, 2, 3, 4, 6, 7, 12]
EPS = 1e-12

PAIRS = [
    ("sun_moon",     "Sun",     "Moon"),
    ("sun_mars",     "Sun",     "Mars"),
    ("sun_mercury",  "Sun",     "Mercury"),
    ("sun_venus",    "Sun",     "Venus"),
    ("sun_jupiter",  "Sun",     "Jupiter"),
    ("sun_saturn",   "Sun",     "Saturn"),
    ("moon_mars",    "Moon",    "Mars"),
    ("moon_mercury", "Moon",    "Mercury"),
    ("moon_jupiter", "Moon",    "Jupiter"),
    ("jupiter_saturn", "Jupiter", "Saturn"),
]
PAIR_NAMES = [p[0] for p in PAIRS]

sns.set_theme(style="whitegrid", context="paper")


def _worker(ts_chunk):
    """Per chunk: compute longitudes + per-pair Re/Im per k. Returns dict of arrays."""
    from npu_engine.jyotisha_engine import compute_chart, compute_pair_interference
    n = len(ts_chunk)
    # Output arrays: per-pair per-k Re and Im, plus composites
    out = {
        "lagna_long": np.empty(n, dtype=np.float32),
    }
    grahas_needed = ["Sun", "Moon", "Mars", "Mercury", "Venus", "Jupiter", "Saturn"]
    for g in grahas_needed:
        out[f"{g.lower()}_long"] = np.empty(n, dtype=np.float32)

    for pname, g1, g2 in PAIRS:
        for k in K_VALUES:
            out[f"{pname}_re_k{k}"] = np.empty(n, dtype=np.float32)
            out[f"{pname}_im_k{k}"] = np.empty(n, dtype=np.float32)
        out[f"{pname}_magnetic"] = np.empty(n, dtype=np.float32)
        out[f"{pname}_dielectric"] = np.empty(n, dtype=np.float32)
        out[f"{pname}_mode_ratio"] = np.empty(n, dtype=np.float32)
        out[f"{pname}_mode_phase"] = np.empty(n, dtype=np.float32)
        out[f"{pname}_synodic_phase"] = np.empty(n, dtype=np.float32)

    for i, ts in enumerate(ts_chunk):
        dt = ts.to_pydatetime()
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        ch = compute_chart(dt, LAT, LON)
        lagna = float(ch["ascendant"]["deg_absolute"])
        out["lagna_long"][i] = lagna
        gl = {}
        for g in grahas_needed:
            v = float(ch["grahas"][g]["deg_absolute"])
            out[f"{g.lower()}_long"][i] = v
            gl[g] = v

        for pname, g1, g2 in PAIRS:
            mag_total = 0.0
            die_total = 0.0
            for k in K_VALUES:
                z = compute_pair_interference(gl[g1], gl[g2], lagna, k)
                re = z.real
                im = z.imag
                out[f"{pname}_re_k{k}"][i] = re
                out[f"{pname}_im_k{k}"][i] = im
                mag_total += abs(re)
                die_total += abs(im)
            out[f"{pname}_magnetic"][i] = mag_total
            out[f"{pname}_dielectric"][i] = die_total
            out[f"{pname}_mode_ratio"][i] = die_total / (mag_total + die_total + EPS)
            out[f"{pname}_mode_phase"][i] = math.atan2(die_total, mag_total)
            # Synodic phase = (g2 - g1) mod 360 mapped to [0, 2π)
            sep = (gl[g2] - gl[g1]) % 360.0
            out[f"{pname}_synodic_phase"][i] = math.radians(sep)

    return out


def build_dataset() -> pd.DataFrame:
    print(f"[load] {GRID}")
    grid = pd.read_parquet(GRID)
    grid["timestamp"] = pd.to_datetime(grid["timestamp"], utc=True).astype("datetime64[ns, UTC]")
    n = len(grid)
    print(f"  rows: {n:,}")

    n_workers = max(1, min(12, (os.cpu_count() or 4) - 2))
    chunk_size = max(1, n // (n_workers * 8))
    ts_list = grid["timestamp"]
    chunks = [ts_list.iloc[i:i + chunk_size].tolist() for i in range(0, n, chunk_size)]
    print(f"  workers={n_workers}  chunks={len(chunks)}  chunk_size~{chunk_size}")

    # Pre-allocate combined arrays
    combined = None
    cursor = 0
    t0 = time.time()
    with Pool(processes=n_workers) as pool:
        for j, partial in enumerate(pool.imap(_worker, chunks)):
            k = len(next(iter(partial.values())))
            if combined is None:
                combined = {col: np.empty(n, dtype=np.float32) for col in partial}
            for col, arr in partial.items():
                combined[col][cursor:cursor + k] = arr
            cursor += k
            if (j + 1) % max(1, len(chunks) // 10) == 0 or j + 1 == len(chunks):
                pct = 100.0 * cursor / n
                print(f"  progress: {cursor:,}/{n:,} ({pct:.1f}%)  elapsed {time.time()-t0:.1f}s")

    df = pd.DataFrame(combined)
    df.insert(0, "timestamp", grid["timestamp"].values)
    # Carry through useful panchanga columns
    for col in ("tithi_num", "nakshatra_num", "paksha", "vara_num", "gandanta_flag"):
        if col in grid.columns:
            df[col] = grid[col].values
    return df


# ── plots ─────────────────────────────────────────────────────

def _save(fig, name):
    p = os.path.join(OUT, name)
    fig.tight_layout()
    fig.savefig(p, dpi=120)
    plt.close(fig)
    return p


def plot_polar_overlay(df, paths, sample_per_pair=4000):
    print("[plot] a. mode_phase_polar_overlay.png")
    rng = np.random.default_rng(20260508)
    fig = plt.figure(figsize=(10.0, 10.0))
    ax = fig.add_subplot(111, projection="polar")
    cmap = plt.cm.tab10
    for i, pname in enumerate(PAIR_NAMES):
        col_phase = f"{pname}_mode_phase"
        col_ratio = f"{pname}_mode_ratio"
        n = len(df)
        idx = rng.choice(n, size=min(sample_per_pair, n), replace=False)
        # Use mode_phase as theta (0..π/2 since both abs); use mode_ratio as r
        theta = df[col_phase].iloc[idx].to_numpy()
        r = df[col_ratio].iloc[idx].to_numpy()
        ax.scatter(theta, r, s=3, alpha=0.30, color=cmap(i % 10),
                   label=pname, edgecolors="none")
    ax.set_thetamin(0)
    ax.set_thetamax(90)
    ax.set_ylim(0, 1)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xticks([0, np.pi/8, np.pi/4, 3*np.pi/8, np.pi/2])
    ax.set_xticklabels(["0", "π/8", "π/4", "3π/8", "π/2"])
    ax.set_title(
        "Mode phase angle (θ) × mode ratio (r), 10 pairs at Gainesville lagna, 2025\n"
        "θ = atan2(dielectric, magnetic) ∈ [0, π/2]   r = mode_ratio ∈ [0, 1]",
        pad=20,
    )
    ax.legend(loc="lower left", bbox_to_anchor=(1.05, 0.0), fontsize=8)
    paths.append(_save(fig, "mode_phase_polar_overlay.png"))


def plot_phase_vs_synodic_grid(df, paths, sample_per_pair=4000):
    print("[plot] b. mode_phase_vs_synodic_phase_grid.png")
    rng = np.random.default_rng(20260508)
    fig, axes = plt.subplots(3, 4, figsize=(14.0, 10.0), sharey=True)
    cmap = plt.cm.tab10
    for i, pname in enumerate(PAIR_NAMES):
        ax = axes.flat[i]
        idx = rng.choice(len(df), size=min(sample_per_pair, len(df)), replace=False)
        x = df[f"{pname}_synodic_phase"].iloc[idx].to_numpy()
        y = df[f"{pname}_mode_phase"].iloc[idx].to_numpy()
        ax.scatter(x, y, s=3, alpha=0.3, color=cmap(i % 10), edgecolors="none")
        ax.set_title(pname)
        ax.set_xlabel("synodic phase (rad)")
        ax.set_ylabel("mode phase (rad)")
        ax.set_xlim(0, 2 * np.pi)
        ax.set_ylim(0, np.pi/2)
        ax.set_xticks([0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi])
        ax.set_xticklabels(["0", "π/2", "π", "3π/2", "2π"])
    # Hide unused panels
    for i in range(len(PAIR_NAMES), 12):
        axes.flat[i].axis("off")
    fig.suptitle("Mode phase vs synodic phase, per pair, 2025", y=1.0)
    paths.append(_save(fig, "mode_phase_vs_synodic_phase_grid.png"))


def plot_mode_ratio_distribution(df, paths):
    print("[plot] c. mode_ratio_distribution_by_pair.png")
    long = pd.DataFrame({
        pname: df[f"{pname}_mode_ratio"].values for pname in PAIR_NAMES
    }).melt(var_name="pair", value_name="mode_ratio")
    fig, ax = plt.subplots(figsize=(11.0, 6.5))
    sns.boxplot(data=long, x="pair", y="mode_ratio", ax=ax,
                color="#3a76c4", fliersize=1, linewidth=0.6)
    ax.axhline(0.5, color="black", linestyle=":", linewidth=0.5, alpha=0.5)
    ax.set_xlabel("graha pair")
    ax.set_ylabel("mode_ratio = dielectric / (magnetic + dielectric)")
    ax.set_title("Mode ratio distribution by pair, 2025 (Gainesville lagna, 10-min cadence)")
    ax.tick_params(axis="x", rotation=30)
    paths.append(_save(fig, "mode_ratio_distribution_by_pair.png"))


def plot_correlation_matrix(df, paths):
    print("[plot] d. mode_ratio_correlation_matrix.png")
    cols = [f"{p}_mode_ratio" for p in PAIR_NAMES]
    sub = df[cols].copy()
    sub.columns = PAIR_NAMES
    corr = sub.corr(method="pearson")
    fig, ax = plt.subplots(figsize=(9.0, 7.5))
    sns.heatmap(corr, annot=True, fmt="+.2f", cmap="RdBu_r",
                vmin=-1, vmax=1, center=0, square=True,
                cbar_kws={"label": "Pearson r"}, ax=ax,
                annot_kws={"size": 8})
    ax.set_title("Pairwise Pearson correlation of mode_ratio time series, 2025")
    paths.append(_save(fig, "mode_ratio_correlation_matrix.png"))


def plot_simultaneous_alignment(df, paths, lo=0.30, hi=0.70):
    print("[plot] e. multi_pair_simultaneous_alignment.png")
    # For each timestamp, count pairs whose mode_ratio is in extreme
    cols = [f"{p}_mode_ratio" for p in PAIR_NAMES]
    arr = df[cols].to_numpy()
    extreme = (arr < lo) | (arr > hi)
    count_extreme = extreme.sum(axis=1)
    fig, axes = plt.subplots(2, 1, figsize=(13.0, 7.0), sharex=True,
                              gridspec_kw={"height_ratios": [3, 1]})
    ax = axes[0]
    ax.plot(df["timestamp"], count_extreme, linewidth=0.4, color="#bf3030", alpha=0.8)
    ax.set_ylabel(f"# pairs with mode_ratio < {lo} or > {hi}\n(out of {len(PAIR_NAMES)})")
    ax.set_title(f"Simultaneous mode-extreme alignment across {len(PAIR_NAMES)} pairs, 2025")
    ax.set_ylim(-0.5, len(PAIR_NAMES) + 0.5)
    # Histogram of counts
    ax2 = axes[1]
    ax2.hist(count_extreme, bins=range(0, len(PAIR_NAMES) + 2), color="#3a76c4",
             edgecolor="black", linewidth=0.4, align="left")
    ax2.set_xlabel("number of pairs simultaneously in mode-extreme  (timestamp-frequency)")
    ax2.set_ylabel("count of timestamps")
    ax2.set_xticks(range(0, len(PAIR_NAMES) + 1))
    paths.append(_save(fig, "multi_pair_simultaneous_alignment.png"))


# ── README ─────────────────────────────────────────────────

def write_readme(stats: dict):
    path = os.path.join(OUT, "README.md")
    txt = f"""# Multi-pair mode-phase exploratory plots — Gainesville lagna, 2025

**Status:** exploratory visualization. NOT pre-registered, NO statistical tests.
Builds on `research/geosolar/exploratory/mode_decomposition_2025/` (single-pair
Sun-Moon) by extending to 10 graha pairs.

## Pairs

{chr(10).join(f"- `{p}`: {g1}–{g2}" for (p, g1, g2) in PAIRS)}

## Dataset

`all_pairs_modes_2025.parquet` — 52,560 rows × ~180 cols at 10-min cadence.
Per pair, columns include `re_k{{1..12}}`, `im_k{{1..12}}`, `magnetic`,
`dielectric`, `mode_ratio`, `mode_phase`, `synodic_phase`.

## Plots

- **mode_phase_polar_overlay.png** — polar plot, 10 pairs as different-colored
  point clouds. θ = mode_phase = atan2(dielectric, magnetic). r = mode_ratio.
  Look for: do different pairs occupy different regions?
- **mode_phase_vs_synodic_phase_grid.png** — 3×4 small multiples, one panel
  per pair, plotting mode_phase vs synodic_phase. Look for: does mode_phase
  rotate monotonically with synodic phase, or in some more complex pattern?
- **mode_ratio_distribution_by_pair.png** — boxplot per pair. Does mode mix
  vary systematically across pair identity?
- **mode_ratio_correlation_matrix.png** — pairwise Pearson correlations
  between the 10 pairs' mode_ratio time series. Synchronized? anti-correlated?
- **multi_pair_simultaneous_alignment.png** — for each timestamp, count of
  pairs with mode_ratio in extreme regime (< 0.30 or > 0.70). Time series
  + histogram. Look for: moments when many pairs simultaneously align.

## Caveat

The pair magnitude `|Z_k|` at any target reduces to `2|cos(k(β-α)/2)|` by
closed-form identity (target-invariant, independent of lagna). The mode
decomposition into Re/Im is what carries target-dependent information.
These plots therefore reflect the lagna-coupled component geometry, not
the pair-magnitude (which is a global function of pair separation).
"""
    with open(path, "w") as f:
        f.write(txt)
    print(f"[readme] {path}")


# ── main ──────────────────────────────────────────────────

def main():
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()

    t_ds = time.time()
    df = build_dataset()
    t_ds_done = time.time() - t_ds
    print(f"[time] dataset build: {t_ds_done:.1f}s  rows={len(df):,}  cols={len(df.columns)}")

    print(f"[write] {OUT_PARQUET}")
    df.to_parquet(OUT_PARQUET, index=False)
    size_mb = os.path.getsize(OUT_PARQUET) / 1e6
    print(f"  size: {size_mb:.1f} MB")

    t_pl = time.time()
    paths = []
    plot_polar_overlay(df, paths)
    plot_phase_vs_synodic_grid(df, paths)
    plot_mode_ratio_distribution(df, paths)
    plot_correlation_matrix(df, paths)
    plot_simultaneous_alignment(df, paths)
    t_pl_done = time.time() - t_pl
    print(f"[time] plots: {t_pl_done:.1f}s")

    # Per-pair mode_ratio summary
    print()
    print("Per-pair mode_ratio (mean / std / range):")
    summary_lines = []
    for pname in PAIR_NAMES:
        v = df[f"{pname}_mode_ratio"]
        line = f"  {pname:18s}  mean={v.mean():.3f}  std={v.std():.3f}  range=[{v.min():.3f}, {v.max():.3f}]"
        print(line)
        summary_lines.append(line)

    write_readme({})

    # File list
    print()
    print("=" * 70)
    print("FILES PRODUCED")
    print("=" * 70)
    print(f"  {OUT_PARQUET}  ({size_mb:.1f} MB)")
    print(f"  {os.path.join(OUT, 'README.md')}")
    for p in paths:
        print(f"  {p}")

    # One-line summary
    means = [df[f"{p}_mode_ratio"].mean() for p in PAIR_NAMES]
    stds = [df[f"{p}_mode_ratio"].std() for p in PAIR_NAMES]
    print()
    print(f"One-liner: across 10 pairs, mode_ratio means span "
          f"[{min(means):.3f}, {max(means):.3f}] (extremes at pair-level), "
          f"per-pair stds [{min(stds):.3f}, {max(stds):.3f}].")
    print(f"\nTotal wall: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
