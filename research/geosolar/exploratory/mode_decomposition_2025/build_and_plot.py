"""
Exploratory mode-decomposition visualization for Sun-Moon at the Gainesville
lagna across calendar 2025 (10-min cadence).

NO statistical tests. NO pre-registration. Visualization-only.

Outputs:
    sun_moon_modes_2025.parquet   (per-timestamp dataset)
    14 PNG plots
    README.md
"""
from __future__ import annotations

import math
import os
import sys
import time
from datetime import datetime

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = "/home/inahd/atlas_core"
sys.path.insert(0, ROOT)

OUT = os.path.join(ROOT, "research/geosolar/exploratory/mode_decomposition_2025")
SM_PARQUET = os.path.join(ROOT, "research/geosolar/pilot_2025/sun_moon_field_2025.parquet")
GRID_PARQUET = os.path.join(ROOT, "datasets/panchanga/grid_10min_2025.parquet")
OUT_PARQUET = os.path.join(OUT, "sun_moon_modes_2025.parquet")

K_VALUES = [1, 2, 3, 4, 6, 7, 12]
EPS = 1e-12

sns.set_theme(style="whitegrid", context="paper")


# ── 1. dataset build ────────────────────────────────────────

def build_dataset() -> pd.DataFrame:
    print(f"[load] {SM_PARQUET}")
    sm = pd.read_parquet(SM_PARQUET)
    sm["timestamp"] = pd.to_datetime(sm["timestamp"], utc=True).astype("datetime64[ns, UTC]")
    print(f"  rows: {len(sm):,}")

    print(f"[load] {GRID_PARQUET}")
    grid = pd.read_parquet(GRID_PARQUET)
    grid["timestamp"] = pd.to_datetime(grid["timestamp"], utc=True).astype("datetime64[ns, UTC]")
    print(f"  rows: {len(grid):,}")

    df = sm.merge(grid, on="timestamp", how="inner")
    print(f"  joined: {len(df):,}")

    # Sun-Moon pair at lagna: per-k Re/Im components.
    # d_sun = lagna - sun  (degrees)
    # d_moon = lagna - moon
    # For each k:
    #   Re_k = cos(k·d_sun) + cos(k·d_moon)        (= old cosine-sum value)
    #   Im_k = sin(k·d_sun) + sin(k·d_moon)        (= dielectric component)
    #   magnetic_k   = |Re_k|
    #   dielectric_k = |Im_k|
    #   mode_ratio_k = dielectric_k / (magnetic_k + dielectric_k + ε)
    print("[compute] per-k Re/Im for Sun-Moon at lagna")
    d_sun = np.radians(df["lagna_long"].to_numpy() - df["sun_long"].to_numpy())
    d_moon = np.radians(df["lagna_long"].to_numpy() - df["moon_long"].to_numpy())

    n = len(df)
    mag_total = np.zeros(n, dtype=np.float64)
    die_total = np.zeros(n, dtype=np.float64)

    for k in K_VALUES:
        re_k = np.cos(k * d_sun) + np.cos(k * d_moon)
        im_k = np.sin(k * d_sun) + np.sin(k * d_moon)
        mag_k = np.abs(re_k)
        die_k = np.abs(im_k)
        df[f"magnetic_k{k}"] = mag_k.astype(np.float32)
        df[f"dielectric_k{k}"] = die_k.astype(np.float32)
        df[f"mode_ratio_k{k}"] = (die_k / (mag_k + die_k + EPS)).astype(np.float32)
        mag_total += mag_k
        die_total += die_k

    df["composite_magnetic"] = (mag_total / len(K_VALUES)).astype(np.float32)
    df["composite_dielectric"] = (die_total / len(K_VALUES)).astype(np.float32)
    df["composite_mode_ratio"] = (die_total / (mag_total + die_total + EPS)).astype(np.float32)
    df["mode_phase_angle"] = np.arctan2(die_total, mag_total).astype(np.float32)  # radians, [0, π/2]

    print(f"[write] {OUT_PARQUET}")
    df.to_parquet(OUT_PARQUET, index=False)
    print(f"  rows: {len(df):,}")
    return df


# ── 2. plot helpers ─────────────────────────────────────────

def _save(fig, name):
    p = os.path.join(OUT, name)
    fig.tight_layout()
    fig.savefig(p, dpi=120)
    plt.close(fig)
    return p


def _figsize_default():
    return (10.0, 6.7)  # ≈ 1200×800 px @ 120 dpi


def plot_timeseries(df: pd.DataFrame, paths: list):
    print("[plot] a. magnetic_dielectric_timeseries.png")
    fig, ax = plt.subplots(figsize=_figsize_default())
    ax.plot(df["timestamp"], df["composite_magnetic"], linewidth=0.5, alpha=0.8,
            label="magnetic mode |Re(Z_k)|", color="#bf3030")
    ax.plot(df["timestamp"], df["composite_dielectric"], linewidth=0.5, alpha=0.8,
            label="dielectric mode |Im(Z_k)|", color="#3a76c4")
    ax.set_xlabel("date (UTC)")
    ax.set_ylabel("composite amplitude (mean over k ∈ {1,2,3,4,6,7,12})")
    ax.set_title("Magnetic mode vs Dielectric mode, Sun-Moon at Gainesville lagna, 2025")
    ax.legend(loc="upper right")
    paths.append(_save(fig, "magnetic_dielectric_timeseries.png"))

    print("[plot] b. magnetic_dielectric_timeseries_january.png")
    jan = df[df["timestamp"].dt.month == 1]
    fig, ax = plt.subplots(figsize=_figsize_default())
    ax.plot(jan["timestamp"], jan["composite_magnetic"], linewidth=0.7, alpha=0.9,
            label="magnetic mode", color="#bf3030")
    ax.plot(jan["timestamp"], jan["composite_dielectric"], linewidth=0.7, alpha=0.9,
            label="dielectric mode", color="#3a76c4")
    ax.set_xlabel("date (UTC)")
    ax.set_ylabel("composite amplitude")
    ax.set_title("Magnetic vs Dielectric mode, January 2025 zoom")
    ax.legend(loc="upper right")
    paths.append(_save(fig, "magnetic_dielectric_timeseries_january.png"))

    print("[plot] c. mode_ratio_timeseries.png")
    fig, ax = plt.subplots(figsize=_figsize_default())
    ax.plot(df["timestamp"], df["composite_mode_ratio"], linewidth=0.5, alpha=0.8,
            color="#308050")
    # ekadashi markers (tithi == 11 or tithi == 26 — i.e. 11th in either paksha)
    ekadashi = df[df["tithi_num"] == 11]
    # Mark only first tithi-11 timestamp per ekadashi event (deduplicate consecutive)
    eka_dates = ekadashi["timestamp"].dt.floor("D").drop_duplicates()
    for d in eka_dates:
        ax.axvline(d, color="#cc8030", linestyle="--", linewidth=0.4, alpha=0.5)
    ax.axhline(0.5, color="black", linestyle=":", linewidth=0.5, alpha=0.5)
    ax.set_xlabel("date (UTC)")
    ax.set_ylabel("composite_mode_ratio = dielectric / (magnetic + dielectric)")
    ax.set_title("Mode ratio across 2025 (orange dashes = ekadashi tithis)")
    paths.append(_save(fig, "mode_ratio_timeseries.png"))


def plot_distributions(df: pd.DataFrame, paths: list):
    print("[plot] d. mode_ratio_by_tithi.png")
    fig, ax = plt.subplots(figsize=_figsize_default())
    sns.boxplot(data=df, x="tithi_num", y="composite_mode_ratio", ax=ax,
                color="#3a76c4", fliersize=1, linewidth=0.7)
    ax.set_xlabel("tithi number (1-30)")
    ax.set_ylabel("composite_mode_ratio")
    ax.set_title("Mode ratio distribution by tithi, 2025")
    paths.append(_save(fig, "mode_ratio_by_tithi.png"))

    print("[plot] e. mode_ratio_by_nakshatra.png")
    fig, ax = plt.subplots(figsize=(11.0, 6.7))
    sns.boxplot(data=df, x="nakshatra_num", y="composite_mode_ratio", ax=ax,
                color="#cc8030", fliersize=1, linewidth=0.7)
    ax.set_xlabel("nakshatra number (1-27)")
    ax.set_ylabel("composite_mode_ratio")
    ax.set_title("Mode ratio distribution by nakshatra, 2025")
    paths.append(_save(fig, "mode_ratio_by_nakshatra.png"))

    print("[plot] f. mode_ratio_paksha_comparison.png")
    fig, ax = plt.subplots(figsize=_figsize_default())
    for paksha, color in [("śukla", "#cc8030"), ("kṛṣṇa", "#444aaa")]:
        sub = df[df["paksha"] == paksha]
        ax.hist(sub["composite_mode_ratio"], bins=60, alpha=0.5, label=paksha, color=color)
    ax.set_xlabel("composite_mode_ratio")
    ax.set_ylabel("count (10-min timestamps)")
    ax.set_title("Mode ratio distribution by paksha, 2025")
    ax.legend()
    paths.append(_save(fig, "mode_ratio_paksha_comparison.png"))

    print("[plot] g. mode_ratio_gandanta_vs_normal.png")
    fig, ax = plt.subplots(figsize=_figsize_default())
    normal = df[~df["gandanta_flag"]]["composite_mode_ratio"]
    gan = df[df["gandanta_flag"]]["composite_mode_ratio"]
    ax.hist(normal, bins=60, alpha=0.5, label=f"non-gandanta (n={len(normal):,})", color="#308050", density=True)
    ax.hist(gan, bins=40, alpha=0.7, label=f"gandanta (n={len(gan):,})", color="#bf3030", density=True)
    ax.set_xlabel("composite_mode_ratio")
    ax.set_ylabel("density")
    ax.set_title("Mode ratio: gandanta vs non-gandanta, 2025")
    ax.legend()
    paths.append(_save(fig, "mode_ratio_gandanta_vs_normal.png"))


def plot_per_k(df: pd.DataFrame, paths: list):
    print("[plot] h. magnetic_by_k.png")
    fig, axes = plt.subplots(len(K_VALUES), 1, figsize=(11.0, 1.4 * len(K_VALUES)),
                             sharex=True)
    for ax, k in zip(axes, K_VALUES):
        ax.plot(df["timestamp"], df[f"magnetic_k{k}"], linewidth=0.4, color="#bf3030", alpha=0.9)
        ax.set_ylabel(f"k={k}")
    axes[0].set_title("Magnetic mode |Re(Z_k)| per k, Sun-Moon at lagna, 2025")
    axes[-1].set_xlabel("date (UTC)")
    paths.append(_save(fig, "magnetic_by_k.png"))

    print("[plot] i. dielectric_by_k.png")
    fig, axes = plt.subplots(len(K_VALUES), 1, figsize=(11.0, 1.4 * len(K_VALUES)),
                             sharex=True)
    for ax, k in zip(axes, K_VALUES):
        ax.plot(df["timestamp"], df[f"dielectric_k{k}"], linewidth=0.4, color="#3a76c4", alpha=0.9)
        ax.set_ylabel(f"k={k}")
    axes[0].set_title("Dielectric mode |Im(Z_k)| per k, Sun-Moon at lagna, 2025")
    axes[-1].set_xlabel("date (UTC)")
    paths.append(_save(fig, "dielectric_by_k.png"))

    print("[plot] j. mode_ratio_by_k.png")
    fig, axes = plt.subplots(len(K_VALUES), 1, figsize=(11.0, 1.4 * len(K_VALUES)),
                             sharex=True)
    for ax, k in zip(axes, K_VALUES):
        ax.plot(df["timestamp"], df[f"mode_ratio_k{k}"], linewidth=0.4, color="#308050", alpha=0.8)
        ax.axhline(0.5, color="black", linestyle=":", linewidth=0.5, alpha=0.4)
        ax.set_ylabel(f"k={k}")
        ax.set_ylim(0, 1)
    axes[0].set_title("Mode ratio per k, Sun-Moon at lagna, 2025")
    axes[-1].set_xlabel("date (UTC)")
    paths.append(_save(fig, "mode_ratio_by_k.png"))


def plot_phase_space(df: pd.DataFrame, paths: list):
    print("[plot] k. magnetic_vs_dielectric_scatter.png")
    fig, ax = plt.subplots(figsize=(8.5, 8.0))
    # Subsample for plot legibility
    rng = np.random.default_rng(20260508)
    n = len(df)
    if n > 15000:
        idx = rng.choice(n, size=15000, replace=False)
        sub = df.iloc[idx]
    else:
        sub = df
    sc = ax.scatter(sub["composite_magnetic"], sub["composite_dielectric"],
                    c=sub["tithi_num"], s=4, alpha=0.5, cmap="twilight", edgecolors="none")
    cb = plt.colorbar(sc, ax=ax, label="tithi number (1-30)")
    ax.set_xlabel("composite_magnetic |Re(Z_k)|")
    ax.set_ylabel("composite_dielectric |Im(Z_k)|")
    ax.set_title("Phase space: magnetic vs dielectric, colored by tithi, 2025")
    ax.set_aspect("equal", adjustable="datalim")
    paths.append(_save(fig, "magnetic_vs_dielectric_scatter.png"))

    print("[plot] l. magnetic_vs_dielectric_by_paksha.png")
    fig, axes = plt.subplots(1, 2, figsize=(13.0, 6.5), sharex=True, sharey=True)
    for ax, paksha, color in zip(axes, ["śukla", "kṛṣṇa"], ["#cc8030", "#444aaa"]):
        s = df[df["paksha"] == paksha]
        if len(s) > 12000:
            idx = rng.choice(len(s), size=12000, replace=False)
            s = s.iloc[idx]
        ax.scatter(s["composite_magnetic"], s["composite_dielectric"],
                   c=color, s=3, alpha=0.4, edgecolors="none")
        ax.set_xlabel("magnetic")
        ax.set_ylabel("dielectric")
        ax.set_title(f"{paksha} paksha")
        ax.set_aspect("equal", adjustable="box")
    fig.suptitle("Phase space by paksha, Sun-Moon at lagna, 2025", y=1.0)
    paths.append(_save(fig, "magnetic_vs_dielectric_by_paksha.png"))

    print("[plot] m. polar_mode_phase.png")
    fig = plt.figure(figsize=(9.0, 9.0))
    ax = fig.add_subplot(111, projection="polar")
    # tithi_num 1..30 → angular position 0..2π
    theta = (df["tithi_num"].to_numpy() - 0.5) / 30.0 * 2 * np.pi
    r = df["mode_phase_angle"].to_numpy()  # [0, π/2]
    n = len(df)
    if n > 15000:
        idx = rng.choice(n, size=15000, replace=False)
        theta = theta[idx]
        r = r[idx]
        paksha = df["paksha"].to_numpy()[idx]
    else:
        paksha = df["paksha"].to_numpy()
    colors = np.where(paksha == "śukla", "#cc8030", "#444aaa")
    ax.scatter(theta, r, c=colors, s=4, alpha=0.4, edgecolors="none")
    # draw tithi sector labels
    for t in [1, 8, 15, 22, 30]:
        a = (t - 0.5) / 30.0 * 2 * np.pi
        ax.text(a, np.pi/2 * 1.08, f"T{t}", ha="center", fontsize=9)
    ax.set_ylim(0, np.pi/2 * 1.05)
    ax.set_yticks([0, np.pi/8, np.pi/4, 3*np.pi/8, np.pi/2])
    ax.set_yticklabels(["0", "π/8", "π/4", "3π/8", "π/2"])
    ax.set_title("Mode phase angle atan2(dielectric, magnetic) around the lunar cycle, 2025\n"
                 "(orange = śukla, blue = kṛṣṇa)")
    paths.append(_save(fig, "polar_mode_phase.png"))


def plot_spectrum(df: pd.DataFrame, paths: list):
    print("[plot] n. mode_ratio_spectrum.png")
    # Detrend / mean-subtract; uniform 10-min cadence assumed.
    series = df.sort_values("timestamp")["composite_mode_ratio"].to_numpy(dtype=np.float64)
    series = series - series.mean()
    n = len(series)
    cadence_hours = 10.0 / 60.0
    freqs = np.fft.rfftfreq(n, d=cadence_hours)  # cycles per hour
    spec = np.abs(np.fft.rfft(series))
    # Skip the DC bin
    freqs = freqs[1:]
    spec = spec[1:]
    period_days = 1.0 / (freqs * 24.0)

    fig, ax = plt.subplots(figsize=_figsize_default())
    ax.loglog(period_days, spec, linewidth=0.6, color="#444aaa")
    # Mark physically interesting periods
    for period, label, color in [
        (29.530, "synodic 29.53d", "#bf3030"),
        (27.321, "sidereal 27.32d", "#cc8030"),
        (1.0,    "1 day",            "#308050"),
        (0.5,    "12 h (M2)",        "#005599"),
        (365.25, "1 year",            "#666"),
    ]:
        ax.axvline(period, color=color, linestyle="--", linewidth=0.7, alpha=0.7)
        ax.text(period, spec.max() * 0.6, label, rotation=90, va="top", ha="right",
                fontsize=8, color=color, alpha=0.9)
    ax.set_xlabel("period (days, log)")
    ax.set_ylabel("|FFT| amplitude (log)")
    ax.set_title("FFT spectrum of composite_mode_ratio, 2025 (10-min cadence)")
    ax.invert_xaxis()  # short periods to the right
    paths.append(_save(fig, "mode_ratio_spectrum.png"))


# ── 3. README ───────────────────────────────────────────────

def write_readme(stats: dict):
    path = os.path.join(OUT, "README.md")
    txt = f"""# Mode-decomposition exploratory plots — Sun-Moon at Gainesville lagna, 2025

**Status:** exploratory visualization, NOT pre-registered. No statistical
tests are performed. The intent is to look at what the versor-aware engine
exposes — i.e., the magnetic-mode (|Re(Z_k)|) and dielectric-mode (|Im(Z_k)|)
components — across calendar 2025 at the Gainesville lagna, and ask: do the
two modes have different temporal structure, regimes, or relationships to
panchanga state?

This document describes what each plot is. Look at the plots fresh and
draw your own observations.

## Dataset

`sun_moon_modes_2025.parquet` — 52,560 rows at 10-min cadence. Columns:
`timestamp`, `sun_long`, `moon_long`, `lagna_long`, panchanga columns from
the canonical grid (`tithi_num`, `nakshatra_num`, `paksha`, `gandanta_flag`,
etc.), and per-k + composite mode-decomposition fields:
`magnetic_k{{1,2,3,4,6,7,12}}`, `dielectric_k{{...}}`, `mode_ratio_k{{...}}`,
`composite_magnetic`, `composite_dielectric`, `composite_mode_ratio`,
`mode_phase_angle = atan2(dielectric, magnetic) ∈ [0, π/2]`.

Headline distribution: composite_mode_ratio mean = {stats['mean']:.4f},
std = {stats['std']:.4f}, range [{stats['min']:.4f}, {stats['max']:.4f}].

## Plots

### Time series
- **magnetic_dielectric_timeseries.png** — both modes plotted across 2025.
- **magnetic_dielectric_timeseries_january.png** — January zoom for fine structure.
- **mode_ratio_timeseries.png** — composite_mode_ratio across the year, with
  ekadashi tithis (11th) marked as orange dashed verticals.

### Distributions across panchanga state
- **mode_ratio_by_tithi.png** — boxplot grouped by tithi 1-30.
- **mode_ratio_by_nakshatra.png** — boxplot grouped by nakshatra 1-27.
- **mode_ratio_paksha_comparison.png** — overlaid histograms for
  śukla vs kṛṣṇa paksha.
- **mode_ratio_gandanta_vs_normal.png** — density overlay at gandanta moments
  vs non-gandanta.

### Per-k breakdown
- **magnetic_by_k.png** — small multiples, magnetic component for each k.
- **dielectric_by_k.png** — same for dielectric.
- **mode_ratio_by_k.png** — per-k mode ratio across 2025.

### Phase-space
- **magnetic_vs_dielectric_scatter.png** — (magnetic, dielectric) scatter,
  colored by tithi.
- **magnetic_vs_dielectric_by_paksha.png** — same, split into two panels
  by paksha.
- **polar_mode_phase.png** — polar plot. Theta = tithi (0-30 mapped to
  0-2π). r = mode_phase_angle = atan2(dielectric, magnetic). Orange = śukla,
  blue = kṛṣṇa.

### Spectrum
- **mode_ratio_spectrum.png** — FFT of composite_mode_ratio time series.
  Periods marked: synodic 29.53d, sidereal 27.32d, 1 day, 12h (M2 tidal),
  1 year.

## Caveat

The Sun-Moon pair-magnitude `|Z_k|` at any target reduces to
`2|cos(k(moon-sun)/2)|` by closed-form identity (target-invariant).
The mode decomposition into Re/Im is what carries target-dependent
information. These plots therefore reflect the lagna-coupled component
geometry, not the pair-magnitude (which is a global Sun-Moon function).
Anything appearing in these plots that varies systematically with
panchanga state is a candidate phenomenon for follow-up pre-registered
testing.
"""
    with open(path, "w") as f:
        f.write(txt)
    print(f"[readme] {path}")


# ── 4. main ──────────────────────────────────────────────────

def main():
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()

    t_ds = time.time()
    df = build_dataset()
    t_ds_done = time.time() - t_ds
    print(f"[time] dataset build: {t_ds_done:.1f}s")

    t_pl = time.time()
    paths = []
    plot_timeseries(df, paths)
    plot_distributions(df, paths)
    plot_per_k(df, paths)
    plot_phase_space(df, paths)
    plot_spectrum(df, paths)
    t_pl_done = time.time() - t_pl
    print(f"[time] plots: {t_pl_done:.1f}s")

    stats = {
        "mean": float(df["composite_mode_ratio"].mean()),
        "std": float(df["composite_mode_ratio"].std()),
        "min": float(df["composite_mode_ratio"].min()),
        "max": float(df["composite_mode_ratio"].max()),
    }
    write_readme(stats)

    print()
    print("=" * 70)
    print("FILES PRODUCED")
    print("=" * 70)
    print(f"  {OUT_PARQUET}")
    print(f"  {os.path.join(OUT, 'README.md')}")
    for p in paths:
        print(f"  {p}")

    print()
    print(f"composite_mode_ratio summary (52,560 timestamps): "
          f"mean={stats['mean']:.4f}  std={stats['std']:.4f}  "
          f"range=[{stats['min']:.4f}, {stats['max']:.4f}]")
    print(f"\nTotal wall: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
