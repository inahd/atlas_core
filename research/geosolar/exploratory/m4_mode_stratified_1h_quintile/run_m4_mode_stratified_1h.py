"""
Sub-daily mode-stratified M4 reanalysis, v2 — 1-hour aggregation
+ data-driven quintile cuts.

Addresses two limitations of the 6-hour version (which collapsed
mode_ratio range to [0.39, 0.60] and put 99.97% of windows in 'mixed'):

  Fix 1: 1-hour cadence. Lagna sweeps 15° per hour vs 90° per 6h, so
         per-hour mode_ratio retains more variation.
  Fix 2: Quintile cuts (bottom 20% / middle 60% / top 20%) computed
         from the actual 1-hour mode_ratio distribution, not fixed
         0.40/0.60.

Methodological notes:
  - SF tide gauge is hourly resolution → 1 sample per 1-hour window.
    "max - min" within a 1-hour window is degenerate (=0). To preserve
    a sub-daily-tide-range predictand, M4_amp at each hourly timestamp
    is computed as a **6-hour-centered rolling max - min** of water
    level. Each hour t gets M4_amp(t) = max(wl[t-3h..t+3h]) - min(...).
  - Stratification variable (mode_ratio) is the per-hour value (no
    aggregation), keeping full 1-hour mode_ratio resolution.
  - Predictor (sun_moon_sep) is the per-hour value.

Output: research/geosolar/exploratory/m4_mode_stratified_1h_quintile/
"""
from __future__ import annotations

import math
import os
import sys
import time
from datetime import timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path("/home/inahd/atlas_core")
sys.path.insert(0, str(ROOT))

OUT = ROOT / "research/geosolar/exploratory/m4_mode_stratified_1h_quintile"
JOINED = ROOT / "research/geosolar/multidecade_1973_2024/joined_1973_2024.parquet"

LAT_SF, LON_SF = 37.806, -122.465
K_VALUES = [1, 2, 3, 4, 6, 7, 12]
EPS = 1e-12

ROLLING_HOURS = 6                # 6h-centered rolling max-min for M4_amp
N_BOOT = 1000
BLOCK_HOURS = 24 * 30            # 720 hourly samples = 30 days

RNG = np.random.default_rng(20260508)
sns.set_theme(style="whitegrid", context="paper")


def compute_lagna_sun_moon(timestamps_utc: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """SF lagna + Sun + Moon (sidereal Lahiri) per timestamp."""
    import swisseph as swe
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    n = len(timestamps_utc)
    lagna = np.empty(n, dtype=np.float64)
    sun_l = np.empty(n, dtype=np.float64)
    moon_l = np.empty(n, dtype=np.float64)
    py_dates = pd.to_datetime(timestamps_utc, utc=True).to_pydatetime()
    for i, dt in enumerate(py_dates):
        h = dt.hour + dt.minute / 60.0 + dt.second / 3600.0
        jd = swe.julday(dt.year, dt.month, dt.day, h)
        aya = swe.get_ayanamsa_ut(jd)
        sun_l[i] = (swe.calc_ut(jd, swe.SUN)[0][0] - aya) % 360.0
        moon_l[i] = (swe.calc_ut(jd, swe.MOON)[0][0] - aya) % 360.0
        _cusps, ascmc = swe.houses(jd, LAT_SF, LON_SF, b"W")
        lagna[i] = (ascmc[0] - aya) % 360.0
        if (i + 1) % 100000 == 0:
            print(f"    [{i+1}/{n}]")
    return lagna, sun_l, moon_l


def versor_decompose(sun_l, moon_l, lagna):
    n = len(sun_l)
    mag = np.zeros(n); die = np.zeros(n)
    d_sun = np.radians(lagna - sun_l)
    d_moon = np.radians(lagna - moon_l)
    for k in K_VALUES:
        re = np.cos(k * d_sun) + np.cos(k * d_moon)
        im = np.sin(k * d_sun) + np.sin(k * d_moon)
        mag += np.abs(re); die += np.abs(im)
    return mag, die


def block_bootstrap_ci_r(x, y, block_size, n_boot=N_BOOT):
    n = len(x)
    if n < max(block_size * 2, 30):
        return (float("nan"), float("nan"))
    n_blocks = int(np.ceil(n / block_size))
    max_start = n - block_size
    rs = np.empty(n_boot)
    for b in range(n_boot):
        starts = RNG.integers(0, max_start + 1, size=n_blocks)
        idx = (starts[:, None] + np.arange(block_size)[None, :]).ravel()[:n]
        xb = x[idx]; yb = y[idx]
        if np.std(xb) == 0 or np.std(yb) == 0:
            rs[b] = 0.0
        else:
            rs[b] = float(np.corrcoef(xb, yb)[0, 1])
    return float(np.percentile(rs, 2.5)), float(np.percentile(rs, 97.5))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    print("[load] joined_1973_2024.parquet (filter source=='tide')")
    df = pd.read_parquet(JOINED)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True).astype("datetime64[ns, UTC]")
    tide = df[df["source"] == "tide"].dropna(subset=["water_level_m"]).copy()
    tide = tide.sort_values("timestamp").reset_index(drop=True)
    n_hours = len(tide)
    print(f"  hourly tide rows: {n_hours:,}")

    print(f"[ephem] SF lagna + sun + moon for {n_hours:,} hourly timestamps")
    t_eph = time.time()
    lagna, sun_l, moon_l = compute_lagna_sun_moon(tide["timestamp"].to_numpy())
    print(f"  ephemeris wall: {time.time() - t_eph:.1f}s")

    print("[versor] decompose Sun-Moon at SF lagna")
    mag, die = versor_decompose(sun_l, moon_l, lagna)
    mode_ratio = die / (mag + die + EPS)
    sun_moon_sep = (moon_l - sun_l) % 360.0

    tide["mode_ratio"] = mode_ratio.astype(np.float32)
    tide["sun_moon_sep"] = sun_moon_sep.astype(np.float32)

    # M4_amp via 6h-centered rolling max-min
    print(f"[m4_amp] {ROLLING_HOURS}-hour-centered rolling max-min of water_level")
    win_size = ROLLING_HOURS + 1   # inclusive both ends ~6h centered
    half = ROLLING_HOURS // 2
    # pandas rolling needs a sorted, indexed series; we use timestamp-indexed
    tide = tide.set_index("timestamp")
    tide["wl_roll_max"] = tide["water_level_m"].rolling(f"{ROLLING_HOURS}h", center=True).max()
    tide["wl_roll_min"] = tide["water_level_m"].rolling(f"{ROLLING_HOURS}h", center=True).min()
    tide["m4_amp"] = (tide["wl_roll_max"] - tide["wl_roll_min"]).astype(np.float32)
    tide = tide.reset_index()

    # Drop rows where rolling window was incomplete (boundary or gap effects)
    valid = tide.dropna(subset=["m4_amp", "mode_ratio", "sun_moon_sep"]).copy()
    valid = valid[valid["m4_amp"] > 0].reset_index(drop=True)
    n_valid = len(valid)
    print(f"  valid rows after rolling: {n_valid:,}")

    mr_min = float(valid["mode_ratio"].min())
    mr_max = float(valid["mode_ratio"].max())
    mr_std = float(valid["mode_ratio"].std())
    print(f"  mode_ratio (1h cadence) range: [{mr_min:.4f}, {mr_max:.4f}]  std={mr_std:.4f}")
    print(f"  (vs 6h std=0.034: {mr_std/0.034:.2f}× wider)")

    # Quintile cuts
    q20 = float(valid["mode_ratio"].quantile(0.20))
    q80 = float(valid["mode_ratio"].quantile(0.80))
    print(f"[stratify] data-driven quintile cuts: q20={q20:.4f}  q80={q80:.4f}")

    valid["regime"] = pd.cut(
        valid["mode_ratio"],
        bins=[-np.inf, q20, q80, np.inf],
        labels=["bottom_quintile", "middle", "top_quintile"],
    )

    # ── per-stratum stats ─────────────────────────────
    results = []
    print("[stat] per-quintile Pearson r + 30-day block-bootstrap CI")
    for name in ["bottom_quintile", "middle", "top_quintile"]:
        sub = valid[valid["regime"] == name].sort_values("timestamp").reset_index(drop=True)
        n = len(sub)
        if n < 30:
            results.append({"regime": name, "n": n, "r": float("nan"), "p": float("nan"),
                            "ci_lo": float("nan"), "ci_hi": float("nan")})
            continue
        x = sub["sun_moon_sep"].to_numpy(dtype=np.float64)
        y = sub["m4_amp"].to_numpy(dtype=np.float64)
        r, p = stats.pearsonr(x, y)
        ci = block_bootstrap_ci_r(x, y, BLOCK_HOURS)
        results.append({"regime": name, "n": int(n), "r": float(r), "p": float(p),
                        "ci_lo": ci[0], "ci_hi": ci[1]})
        print(f"  {name:>20s}  n={n:>7,}  r={r:+.4f}  CI=[{ci[0]:+.3f},{ci[1]:+.3f}]  p={p:.3g}")

    # Pooled reference
    x_all = valid["sun_moon_sep"].to_numpy(dtype=np.float64)
    y_all = valid["m4_amp"].to_numpy(dtype=np.float64)
    r_pool, p_pool = stats.pearsonr(x_all, y_all)
    ci_pool = block_bootstrap_ci_r(x_all, y_all, BLOCK_HOURS)
    print(f"  {'POOLED':>20s}  n={n_valid:>7,}  r={r_pool:+.4f}  "
          f"CI=[{ci_pool[0]:+.3f},{ci_pool[1]:+.3f}]  p={p_pool:.3g}")

    # CI overlap check (top vs bottom)
    bot = next(r for r in results if r["regime"] == "bottom_quintile")
    top = next(r for r in results if r["regime"] == "top_quintile")
    overlap = (bot["ci_lo"] <= top["ci_hi"]) and (top["ci_lo"] <= bot["ci_hi"])
    diff = top["r"] - bot["r"]
    print(f"  → top - bottom r difference: {diff:+.4f}  CIs {'OVERLAP' if overlap else 'DO NOT OVERLAP'}")

    # ── save windows parquet ───────────────────────────
    valid_to_save = valid[["timestamp", "water_level_m", "m4_amp", "mode_ratio",
                           "sun_moon_sep", "regime"]].copy()
    out_parquet = OUT / "windows_1h.parquet"
    valid_to_save.to_parquet(out_parquet, index=False)
    print(f"[write] {out_parquet.relative_to(ROOT)}  rows={len(valid_to_save):,}")

    # ── plots ──────────────────────────────────────────
    print("[plots]")

    # (a) m4_vs_sun_moon_by_mode_quintile_1h.png
    fig, axes = plt.subplots(1, 3, figsize=(15.0, 5.5), sharey=True)
    color_map = {"bottom_quintile": "#bf3030", "middle": "#cc8030", "top_quintile": "#3a76c4"}
    for ax, regime in zip(axes, ["bottom_quintile", "middle", "top_quintile"]):
        sub = valid[valid["regime"] == regime]
        n = len(sub)
        sample = sub.sample(n=min(10000, n), random_state=20260508) if n > 10000 else sub
        ax.scatter(sample["sun_moon_sep"], sample["m4_amp"], s=2, alpha=0.20,
                   color=color_map[regime], edgecolors="none")
        if n >= 3 and sub["sun_moon_sep"].std() > 0:
            xx = sub["sun_moon_sep"].to_numpy(dtype=np.float64)
            yy = sub["m4_amp"].to_numpy(dtype=np.float64)
            b1, b0 = np.polyfit(xx, yy, 1)
            xs = np.linspace(0, 360, 50)
            ax.plot(xs, b0 + b1 * xs, color="black", linewidth=1.0)
        m = next(r for r in results if r["regime"] == regime)
        ax.set_title(f"{regime}\nn={m['n']:,}  r={m['r']:+.3f}  CI=[{m['ci_lo']:+.3f},{m['ci_hi']:+.3f}]")
        ax.set_xlabel("Sun-Moon angular separation (deg)")
        ax.set_xlim(0, 360)
    axes[0].set_ylabel("M4 amplitude (m) — 6-h-centered rolling tide range at hourly cadence")
    fig.suptitle("M4 amplitude vs Sun-Moon separation, stratified by 1-hour mode_ratio quintile — SF gauge, 1973-2024", y=1.0)
    fig.tight_layout()
    p1 = OUT / "m4_vs_sun_moon_by_mode_quintile_1h.png"
    fig.savefig(p1, dpi=120); plt.close(fig)
    print(f"  → {p1.name}")

    # (b) mode_ratio_distribution_1h_windows.png
    fig, ax = plt.subplots(figsize=(10.0, 5.5))
    ax.hist(valid["mode_ratio"], bins=100, color="#3a76c4", edgecolor="black", linewidth=0.3)
    ax.axvline(q20, color="#bf3030", linestyle="--", linewidth=1.0, label=f"q20={q20:.4f}")
    ax.axvline(q80, color="#3a76c4", linestyle="--", linewidth=1.0, label=f"q80={q80:.4f}")
    ax.axvline(0.50, color="black", linestyle=":", linewidth=0.6, alpha=0.7, label="0.50")
    ax.set_xlabel("1-hour mode_ratio (SF lagna)")
    ax.set_ylabel("count of hourly samples")
    ax.set_title(f"Mode ratio distribution at 1-hour cadence — n={n_valid:,}, "
                 f"range=[{mr_min:.4f}, {mr_max:.4f}], std={mr_std:.4f}")
    ax.legend()
    fig.tight_layout()
    p2 = OUT / "mode_ratio_distribution_1h_windows.png"
    fig.savefig(p2, dpi=120); plt.close(fig)
    print(f"  → {p2.name}")

    # (c) correlation_by_mode_quintile_with_bootstrap.png
    fig, ax = plt.subplots(figsize=(9.0, 5.5))
    names = [r["regime"] for r in results]
    rs = [r["r"] for r in results]
    err_lo = [rs[i] - results[i]["ci_lo"] if not np.isnan(rs[i]) else 0 for i in range(len(rs))]
    err_hi = [results[i]["ci_hi"] - rs[i] if not np.isnan(rs[i]) else 0 for i in range(len(rs))]
    colors = ["#bf3030", "#cc8030", "#3a76c4"]
    xs = np.arange(len(names))
    ax.bar(xs, [r if not np.isnan(r) else 0 for r in rs],
           color=colors, edgecolor="black", linewidth=0.5)
    ax.errorbar(xs, [r if not np.isnan(r) else 0 for r in rs],
                yerr=[err_lo, err_hi], fmt="none", ecolor="black", capsize=4, linewidth=1.0)
    ax.axhline(r_pool, color="black", linestyle="--", linewidth=0.7,
               label=f"pooled r={r_pool:+.3f}")
    ax.axhline(0, color="black", linewidth=0.4)
    ax.set_xticks(xs)
    ax.set_xticklabels([f"{n}\n(n={results[i]['n']:,})" for i, n in enumerate(names)])
    ax.set_ylabel("Pearson r (M4_amp ↔ Sun-Moon separation)")
    ax.set_title(f"M4 ↔ Sun-Moon-separation correlation by 1-hour mode_ratio quintile, "
                 f"30-day block-bootstrap CI\ntop − bottom = {diff:+.4f}, "
                 f"CIs {'OVERLAP' if overlap else 'DO NOT OVERLAP'}")
    ax.legend()
    fig.tight_layout()
    p3 = OUT / "correlation_by_mode_quintile_with_bootstrap.png"
    fig.savefig(p3, dpi=120); plt.close(fig)
    print(f"  → {p3.name}")

    # (d) m4_residual_after_standard_tidal_by_quintile.png
    b1_pool, b0_pool = np.polyfit(x_all, y_all, 1)
    valid["m4_residual"] = valid["m4_amp"] - (b0_pool + b1_pool * valid["sun_moon_sep"])
    fig, axes = plt.subplots(1, 3, figsize=(15.0, 5.5), sharey=True)
    for ax, regime in zip(axes, ["bottom_quintile", "middle", "top_quintile"]):
        sub = valid[valid["regime"] == regime]
        n = len(sub)
        sample = sub.sample(n=min(10000, n), random_state=20260508) if n > 10000 else sub
        ax.scatter(sample["sun_moon_sep"], sample["m4_residual"], s=2, alpha=0.20,
                   color=color_map[regime], edgecolors="none")
        ax.axhline(0, color="black", linewidth=0.5)
        if n >= 3:
            xx = sub["sun_moon_sep"].to_numpy(dtype=np.float64)
            yy = sub["m4_residual"].to_numpy(dtype=np.float64)
            r_res, _ = stats.pearsonr(xx, yy)
            b1r, b0r = np.polyfit(xx, yy, 1)
            xs_fit = np.linspace(0, 360, 50)
            ax.plot(xs_fit, b0r + b1r * xs_fit, color="black", linewidth=1.0)
            ax.set_title(f"{regime}\nresidual r={r_res:+.4f}")
        ax.set_xlabel("Sun-Moon separation (deg)")
        ax.set_xlim(0, 360)
    axes[0].set_ylabel("M4 residual (after pooled linear fit)")
    fig.suptitle("M4 residual after pooled tidal fit, by 1-hour mode_ratio quintile", y=1.0)
    fig.tight_layout()
    p4 = OUT / "m4_residual_after_standard_tidal_by_quintile.png"
    fig.savefig(p4, dpi=120); plt.close(fig)
    print(f"  → {p4.name}")

    # ── synthesis ───────────────────────────────────────
    write_synthesis(results, r_pool, ci_pool, p_pool, valid, mr_min, mr_max, mr_std,
                    q20, q80, diff, overlap, time.time() - t0)

    # console summary
    print()
    print("=" * 70)
    print(f"  SF gauge tide range, 1-hour cadence + quintile cuts, n={n_valid:,}")
    print("=" * 70)
    for r in results:
        if np.isnan(r["r"]):
            print(f"  {r['regime']:>20s}  n={r['n']:>7,}  r=n/a")
        else:
            print(f"  {r['regime']:>20s}  n={r['n']:>7,}  r={r['r']:+.4f}  "
                  f"CI=[{r['ci_lo']:+.3f},{r['ci_hi']:+.3f}]")
    print(f"  {'POOLED':>20s}  n={n_valid:>7,}  r={r_pool:+.4f}  "
          f"CI=[{ci_pool[0]:+.3f},{ci_pool[1]:+.3f}]")
    print()
    print(f"  Top - bottom r difference: {diff:+.4f}")
    print(f"  Top vs bottom CIs: {'OVERLAP — strata indistinguishable at the 95% level' if overlap else 'DO NOT OVERLAP — strata distinguishable'}")
    print(f"  Mode_ratio at 1h: range=[{mr_min:.4f},{mr_max:.4f}]  std={mr_std:.4f}  "
          f"({mr_std/0.034:.2f}× wider than 6h)")
    print(f"\nTotal wall: {time.time() - t0:.1f}s")


def write_synthesis(results, r_pool, ci_pool, p_pool, valid, mr_min, mr_max, mr_std,
                    q20, q80, diff, overlap, total_wall):
    md = []
    md.append("# Sub-daily mode-stratified M4 reanalysis, v2 — 1-hour quintile-cut SYNTHESIS\n")
    md.append("**Status:** EXPLORATORY. Not pre-registered. Not citable as confirmatory.\n")
    md.append("Date generated: 2026-05-08\n")

    md.append("## What this is\n")
    md.append("Re-run of the 6-hour mode-stratified M4 reanalysis after that pass's")
    md.append("stratification cuts (0.40 / 0.60) collapsed 99.97% of windows into one")
    md.append("bin (the 6-hour-mean mode_ratio range was [0.39, 0.60]). Two changes:")
    md.append("")
    md.append("1. **1-hour cadence** (instead of 6-hour aggregation) for the")
    md.append("   stratification variable. At 1-hour, lagna sweeps only 15° per")
    md.append("   sample vs 90° per 6h, so per-hour mode_ratio retains ~3× wider")
    md.append("   variation.")
    md.append("2. **Data-driven quintile cuts** (bottom 20% / middle 60% / top 20%)")
    md.append("   computed from the actual 1-hour mode_ratio distribution, instead of")
    md.append("   the fixed 0.40/0.60 cuts that the data didn't span at 6h.")
    md.append("")
    md.append("Methodological note (necessary, since SF tide gauge is hourly and")
    md.append("max-min within a 1-hour window is degenerate): **M4 amplitude at")
    md.append("each hourly timestamp is computed as a 6-hour-centered rolling")
    md.append("max − min** of water_level — i.e., M4_amp(t) = max(wl[t−3h..t+3h]) −")
    md.append("min(wl[t−3h..t+3h]). This preserves the sub-daily-tide-range semantics")
    md.append("of the predictand while letting the stratification variable mode_ratio")
    md.append("vary at full hourly resolution.")
    md.append("")

    md.append("## Diagnostics (mode_ratio at 1-hour cadence)\n")
    md.append(f"- Range: **[{mr_min:.4f}, {mr_max:.4f}]**")
    md.append(f"- Std:  **{mr_std:.4f}**  ({mr_std/0.034:.2f}× wider than 6h's 0.034)")
    md.append(f"- 20th percentile cut: **q20 = {q20:.4f}**")
    md.append(f"- 80th percentile cut: **q80 = {q80:.4f}**")
    md.append("")
    if mr_max < 0.6 or mr_min > 0.4:
        md.append("Note: the data-driven quintile cuts above lie INSIDE the prior fixed")
        md.append("cuts (0.40/0.60) — quintile cuts adapt to the actual data spread")
        md.append("and produce balanced strata regardless of where the data sits.")
        md.append("")

    md.append("## Sample sizes and per-quintile results\n")
    md.append("| Quintile | n hourly samples | Pearson r | 95% bootstrap CI | raw p |")
    md.append("|---|---:|---:|---|---:|")
    for r in results:
        if np.isnan(r["r"]):
            md.append(f"| {r['regime']} | {r['n']:,} | n/a | n/a | n/a |")
        else:
            md.append(f"| {r['regime']} | {r['n']:,} | {r['r']:+.4f} | "
                      f"[{r['ci_lo']:+.3f}, {r['ci_hi']:+.3f}] | {r['p']:.3g} |")
    md.append(f"| **POOLED** | {len(valid):,} | {r_pool:+.4f} | "
              f"[{ci_pool[0]:+.3f}, {ci_pool[1]:+.3f}] | {p_pool:.3g} |")
    md.append("")
    md.append(f"Block-bootstrap CI uses 30-day blocks (= {BLOCK_HOURS} hourly samples), 1,000 resamples.")
    md.append("")

    md.append("## Top vs bottom quintile comparison\n")
    md.append(f"- top - bottom r difference: **{diff:+.4f}**")
    md.append(f"- 95% CIs: **{'OVERLAP' if overlap else 'DO NOT OVERLAP'}**")
    md.append("")
    if overlap:
        md.append("The CIs of the bottom and top quintile r-values overlap, meaning")
        md.append("the strata are not distinguishable at the 95% level under this")
        md.append("design. Whatever differential mode-coupling exists, it is too small")
        md.append("to surface against the noise in this single-window-pair test.")
    else:
        md.append("The CIs of the bottom and top quintile r-values do NOT overlap,")
        md.append("meaning the strata are distinguishable at the 95% level under")
        md.append("this design. **This is suggestive but not confirmatory** — the")
        md.append("test was performed once, on the same year-window PREREG_001 used,")
        md.append("after the hypothesis was formed. A pre-registered held-out")
        md.append("replication is required before treating this as a finding.")
    md.append("")

    md.append("## Plots\n")
    md.append("- `m4_vs_sun_moon_by_mode_quintile_1h.png` — three panels (bottom /")
    md.append("  middle / top quintile), scatter of M4 amplitude vs Sun-Moon")
    md.append("  separation with regression line.")
    md.append("- `mode_ratio_distribution_1h_windows.png` — histogram of 1-hour")
    md.append("  mode_ratio with q20 and q80 cuts marked.")
    md.append("- `correlation_by_mode_quintile_with_bootstrap.png` — bar chart of")
    md.append("  per-quintile r with 95% block-bootstrap CI; pooled r as dashed line.")
    md.append("- `m4_residual_after_standard_tidal_by_quintile.png` — residual after")
    md.append("  pooled linear fit, stratified by quintile.")
    md.append("")

    md.append("## Caveats and limitations\n")
    md.append("- Single-window test on data already used in PREREG_001; cannot serve")
    md.append("  as an independent confirmatory test no matter how clean the strata")
    md.append("  separate.")
    md.append("- 6-hour-centered rolling M4_amp introduces autocorrelation in the")
    md.append("  predictand at hourly cadence (consecutive hours share 5 of 6 samples")
    md.append("  in the rolling window). Block-bootstrap with 30-day blocks is")
    md.append("  intended to absorb this.")
    md.append("- Sun-Moon angular separation is circular [0,360); Pearson r assumes")
    md.append("  linearity and underestimates the true relationship strength (the")
    md.append("  envelope is sinusoidal in the angle).")
    md.append("- Quintile cuts are post hoc to the data — the dataset itself")
    md.append("  defines the strata boundaries. This is acceptable for exploratory")
    md.append("  use but should be locked in advance for any confirmatory replication.")
    md.append("")
    md.append("## If results are suggestive: follow-up design\n")
    md.append("If the top-vs-bottom comparison shows non-overlapping CIs, a")
    md.append("confirmatory follow-up should:")
    md.append("- Pre-register with: lagna location, predictand cadence, predictor")
    md.append("  definition, stratification cuts (specified in advance, not")
    md.append("  data-driven at execution time), and survival criterion.")
    md.append("- Use a held-out gauge (e.g. Honolulu, Boston, or other multi-decade")
    md.append("  NOAA gauge) AND/OR held-out years.")
    md.append("- Use circular-statistics-aware predictor (harmonic regression on")
    md.append("  Sun-Moon angle, not linear Pearson).")
    md.append(f"\n*Total wall: {total_wall:.1f}s*")

    p = OUT / "SYNTHESIS.md"
    p.write_text("\n".join(md))


if __name__ == "__main__":
    main()
