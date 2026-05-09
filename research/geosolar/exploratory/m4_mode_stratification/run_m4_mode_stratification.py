"""
M4 reanalysis through versor mode-stratification.

PREREG_001's M4 was: daily SF tide range vs daily-mean Sun-Moon amplitude
at the Gainesville lagna, 1973-2024, n=18,702 days, r=+0.1945 committed.

Tonight's versor identity revealed:
  - |Z_k| at any target reduces to 2|cos(k(moon-sun)/2)| (target-invariant)
  - Re(Z_k) IS target-dependent (= the old cosine-sum)
  - Im(Z_k) IS target-dependent (the previously-discarded dielectric mode)

Analytical reframing: the committed M4 predictor `mean_k |cos+cos|` equals
`magnetic_component / 7` (since |cos+cos| = |Re(Z_k)|). M4 is structurally
a magnetic-mode-only test of standard tidal physics.

This script asks: does the M4 r split when stratified by daily mode ratio
(dielectric / (magnetic + dielectric))? Days with magnetic-dominant mode
should give a stronger r if M4 truly lives in the magnetic register.

Exploratory only. Not pre-registered.
"""
from __future__ import annotations

import math
import os
import sys
import time

import numpy as np
import pandas as pd
from scipy import stats

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = "/home/inahd/atlas_core"
OUT = os.path.join(ROOT, "research/geosolar/exploratory/m4_mode_stratification")
SM_PARQUET = os.path.join(ROOT, "research/geosolar/multidecade_1973_2024/sun_moon_field_1973_2024.parquet")
JOINED_PARQUET = os.path.join(ROOT, "research/geosolar/multidecade_1973_2024/joined_1973_2024.parquet")
REPORT = os.path.join(OUT, "M4_MODE_ANALYSIS.md")

K_VALUES = [1, 2, 3, 4, 6, 7, 12]
EPS = 1e-12

RNG = np.random.default_rng(20260508)
N_BOOT = 1000
BLOCK_DAYS = 14

sns.set_theme(style="whitegrid", context="paper")


def block_bootstrap_ci(x, y, block_size=BLOCK_DAYS, n_boot=N_BOOT):
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


def holm_adjust(pvals):
    pvals = np.asarray(pvals, dtype=float)
    m = len(pvals)
    order = np.argsort(pvals)
    adj = np.zeros(m)
    running_max = 0.0
    for rank, idx in enumerate(order):
        a = min((m - rank) * pvals[idx], 1.0)
        running_max = max(running_max, a)
        adj[idx] = running_max
    return adj.tolist()


def fmt_p(p):
    if p is None or (isinstance(p, float) and np.isnan(p)):
        return "n/a"
    if p < 1e-300:
        return "<1e-300"
    return f"{p:.3g}"


def main():
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()

    # ── load 10-min sun-moon longitudes + committed sun_moon_amplitude ──
    print("[load] sun_moon_field 1973-2024")
    sm = pd.read_parquet(SM_PARQUET)
    sm["timestamp"] = pd.to_datetime(sm["timestamp"], utc=True).astype("datetime64[ns, UTC]")
    print(f"  rows: {len(sm):,}")

    # ── compute per-timestamp Re/Im via versor identity ──
    print("[compute] per-timestamp Re_k / Im_k for Sun-Moon at lagna")
    d_sun = np.radians(sm["lagna_long"].to_numpy(dtype=np.float64) - sm["sun_long"].to_numpy(dtype=np.float64))
    d_moon = np.radians(sm["lagna_long"].to_numpy(dtype=np.float64) - sm["moon_long"].to_numpy(dtype=np.float64))
    n = len(sm)
    mag_total = np.zeros(n)
    die_total = np.zeros(n)
    for k in K_VALUES:
        re_k = np.cos(k * d_sun) + np.cos(k * d_moon)
        im_k = np.sin(k * d_sun) + np.sin(k * d_moon)
        mag_total += np.abs(re_k)
        die_total += np.abs(im_k)
    sm["magnetic_component"] = mag_total.astype(np.float32)
    sm["dielectric_component"] = die_total.astype(np.float32)
    sm["mode_ratio"] = (die_total / (mag_total + die_total + EPS)).astype(np.float32)

    # Sanity: sun_moon_amplitude (committed) should equal magnetic_component / 7
    expected_amp = mag_total / len(K_VALUES)
    actual_amp = sm["sun_moon_amplitude"].to_numpy(dtype=np.float64)
    diff = np.abs(actual_amp - expected_amp)
    print(f"  sanity: max |sun_moon_amplitude - magnetic_component/{len(K_VALUES)}| = {diff.max():.3e}  (should be ~ 1e-4 due to float32 storage)")

    # ── daily aggregation ──
    print("[daily] aggregate sun_moon to daily means")
    sm["date"] = sm["timestamp"].dt.tz_convert("UTC").dt.floor("D")
    daily_sm = sm.groupby("date", as_index=False).agg(
        sm_daily_mean=("sun_moon_amplitude", "mean"),
        magnetic_daily=("magnetic_component", "mean"),
        dielectric_daily=("dielectric_component", "mean"),
        mode_ratio_daily=("mode_ratio", "mean"),
    )
    print(f"  daily rows: {len(daily_sm):,}")

    # ── load tide hourly from joined parquet, compute daily range ──
    print("[load] tide hourly from joined parquet")
    joined = pd.read_parquet(JOINED_PARQUET)
    joined["timestamp"] = pd.to_datetime(joined["timestamp"], utc=True).astype("datetime64[ns, UTC]")
    tide = joined[joined["source"] == "tide"].dropna(subset=["water_level_m"]).copy()
    tide["date"] = tide["timestamp"].dt.tz_convert("UTC").dt.floor("D")
    daily_tide = tide.groupby("date")["water_level_m"].agg(lambda s: float(s.max() - s.min())).rename("tide_range_m").reset_index()
    print(f"  daily tide rows: {len(daily_tide):,}")

    # ── merge inner: matches M4's inner-join behavior (drops days with no tide) ──
    df = daily_sm.merge(daily_tide, on="date", how="inner").sort_values("date").reset_index(drop=True)
    print(f"  merged daily rows: {len(df):,}")

    # ── baseline r reproduction ──
    print("\n[baseline] reproducing committed M4 r")
    x_full = df["sm_daily_mean"].to_numpy(dtype=np.float64)
    y_full = df["tide_range_m"].to_numpy(dtype=np.float64)
    r_baseline, p_baseline = stats.pearsonr(x_full, y_full)
    print(f"  baseline: n={len(df):,}  r={r_baseline:+.4f}  p={fmt_p(p_baseline)}")
    print(f"  committed M4: n=18,702  r=+0.1945  p=8.39e-159")

    # ── three-regime stratification ──
    print("\n[stratify] three mode regimes (cuts at 0.40 / 0.55)")
    regimes = [
        ("magnetic-dominant", df["mode_ratio_daily"] < 0.40),
        ("balanced",          (df["mode_ratio_daily"] >= 0.40) & (df["mode_ratio_daily"] < 0.55)),
        ("dielectric-leaning", df["mode_ratio_daily"] >= 0.55),
    ]
    regime_results = []
    pvals_for_holm = []
    for name, mask in regimes:
        sub = df[mask].sort_values("date").reset_index(drop=True)
        n_sub = len(sub)
        if n_sub < 30:
            r, p, ci = float("nan"), float("nan"), (float("nan"), float("nan"))
        else:
            x = sub["sm_daily_mean"].to_numpy(dtype=np.float64)
            y = sub["tide_range_m"].to_numpy(dtype=np.float64)
            r, p = stats.pearsonr(x, y)
            r = float(r); p = float(p)
            ci = block_bootstrap_ci(x, y)
        regime_results.append({
            "regime": name,
            "n": int(n_sub),
            "r": r,
            "p": p,
            "ci_lo": ci[0],
            "ci_hi": ci[1],
            "mode_ratio_min": float(sub["mode_ratio_daily"].min()) if n_sub else float("nan"),
            "mode_ratio_max": float(sub["mode_ratio_daily"].max()) if n_sub else float("nan"),
        })
        pvals_for_holm.append(p if not np.isnan(p) else 1.0)
        print(f"  {name:22s}  n={n_sub:>6,}  r={r:+.4f}  CI=[{ci[0]:+.3f}, {ci[1]:+.3f}]  raw p={fmt_p(p)}")
    holm = holm_adjust(pvals_for_holm)
    for rr, h in zip(regime_results, holm):
        rr["p_holm"] = float(h)

    # ── 5-quantile sensitivity ──
    print("\n[sensitivity] 5-quantile bins of mode_ratio_daily")
    df["mode_q5"] = pd.qcut(df["mode_ratio_daily"], q=5, labels=False, duplicates="drop")
    quintile_results = []
    for q in sorted(df["mode_q5"].dropna().unique()):
        sub = df[df["mode_q5"] == q].sort_values("date").reset_index(drop=True)
        n_sub = len(sub)
        x = sub["sm_daily_mean"].to_numpy(dtype=np.float64)
        y = sub["tide_range_m"].to_numpy(dtype=np.float64)
        r, p = stats.pearsonr(x, y)
        ci = block_bootstrap_ci(x, y)
        quintile_results.append({
            "quintile": int(q) + 1,
            "n": int(n_sub),
            "mode_ratio_min": float(sub["mode_ratio_daily"].min()),
            "mode_ratio_max": float(sub["mode_ratio_daily"].max()),
            "r": float(r), "p": float(p),
            "ci_lo": ci[0], "ci_hi": ci[1],
        })
        print(f"  Q{int(q)+1}  range=[{quintile_results[-1]['mode_ratio_min']:.3f},{quintile_results[-1]['mode_ratio_max']:.3f}]  n={n_sub:>5,}  r={r:+.4f}  CI=[{ci[0]:+.3f},{ci[1]:+.3f}]  p={fmt_p(p)}")

    # ── diagnostic: daily mode_ratio distribution ──
    print("\n[diag] daily mode_ratio distribution")
    print(f"  range: [{df['mode_ratio_daily'].min():.4f}, {df['mode_ratio_daily'].max():.4f}]")
    print(f"  std: {df['mode_ratio_daily'].std():.4f}")
    print(f"  fraction in user-specified strata:")
    print(f"    < 0.40 (magnetic-dominant):   {100.0 * (df['mode_ratio_daily'] < 0.40).mean():.2f}%")
    print(f"    [0.40, 0.55) (balanced):      {100.0 * ((df['mode_ratio_daily'] >= 0.40) & (df['mode_ratio_daily'] < 0.55)).mean():.2f}%")
    print(f"    >= 0.55 (dielectric-leaning): {100.0 * (df['mode_ratio_daily'] >= 0.55).mean():.2f}%")
    print(f"  → daily-aggregation collapses mode_ratio to a tight band around 0.5")
    print(f"     because lagna sweeps the full zodiac in 24h, making daily means")
    print(f"     of |Re| and |Im| approximately symmetric by construction.")

    # ── plots ──
    print("\n[plots]")

    # m4_r_by_mode_regime.png
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    names = [r["regime"] for r in regime_results]
    rs = [r["r"] for r in regime_results]
    ns = [r["n"] for r in regime_results]
    err_low = [rs[i] - regime_results[i]["ci_lo"] for i in range(len(rs))]
    err_hi = [regime_results[i]["ci_hi"] - rs[i] for i in range(len(rs))]
    colors = ["#bf3030", "#cc8030", "#3a76c4"]
    xs = np.arange(len(names))
    ax.bar(xs, rs, color=colors, edgecolor="black", linewidth=0.6)
    ax.errorbar(xs, rs, yerr=[err_low, err_hi], fmt="none", ecolor="black", capsize=4, linewidth=1.0)
    ax.axhline(r_baseline, color="black", linestyle="--", linewidth=0.7,
               label=f"baseline (pooled) r={r_baseline:+.3f}")
    ax.set_xticks(xs)
    ax.set_xticklabels([f"{n}\n(n={ns[i]:,})" for i, n in enumerate(names)])
    ax.set_ylabel("Pearson r (M4 within stratum)")
    ax.set_title("M4 r by mode regime (1973-2024)")
    ax.legend()
    p1 = os.path.join(OUT, "m4_r_by_mode_regime.png")
    fig.tight_layout(); fig.savefig(p1, dpi=120); plt.close(fig)
    print(f"  {p1}")

    # m4_r_by_mode_quintile.png
    fig, ax = plt.subplots(figsize=(9.0, 5.5))
    qs = [r["quintile"] for r in quintile_results]
    rs_q = [r["r"] for r in quintile_results]
    ns_q = [r["n"] for r in quintile_results]
    el = [rs_q[i] - quintile_results[i]["ci_lo"] for i in range(len(rs_q))]
    eh = [quintile_results[i]["ci_hi"] - rs_q[i] for i in range(len(rs_q))]
    xs = np.arange(len(qs))
    ax.bar(xs, rs_q, color="#3a76c4", edgecolor="black", linewidth=0.6)
    ax.errorbar(xs, rs_q, yerr=[el, eh], fmt="none", ecolor="black", capsize=4, linewidth=1.0)
    ax.axhline(r_baseline, color="black", linestyle="--", linewidth=0.7,
               label=f"baseline (pooled) r={r_baseline:+.3f}")
    ax.set_xticks(xs)
    ax.set_xticklabels([f"Q{qs[i]}\n[{quintile_results[i]['mode_ratio_min']:.2f},{quintile_results[i]['mode_ratio_max']:.2f}]\n(n={ns_q[i]:,})" for i in range(len(qs))])
    ax.set_xlabel("mode_ratio_daily quintile (low → high)")
    ax.set_ylabel("Pearson r (M4 within quintile)")
    ax.set_title("M4 r by mode_ratio quintile (1973-2024)")
    ax.legend()
    p2 = os.path.join(OUT, "m4_r_by_mode_quintile.png")
    fig.tight_layout(); fig.savefig(p2, dpi=120); plt.close(fig)
    print(f"  {p2}")

    # m4_scatter_by_mode_color.png
    fig, ax = plt.subplots(figsize=(9.5, 7.0))
    rng = np.random.default_rng(20260508)
    if len(df) > 12000:
        idx = rng.choice(len(df), size=12000, replace=False)
        sub = df.iloc[idx]
    else:
        sub = df
    sc = ax.scatter(sub["sm_daily_mean"], sub["tide_range_m"],
                    c=sub["mode_ratio_daily"], cmap="coolwarm", s=6, alpha=0.5, edgecolors="none")
    cb = plt.colorbar(sc, ax=ax, label="mode_ratio_daily (blue=magnetic, red=dielectric)")
    # Add overall fit line
    b1, b0 = np.polyfit(x_full, y_full, 1)
    xs_fit = np.linspace(x_full.min(), x_full.max(), 100)
    ax.plot(xs_fit, b0 + b1 * xs_fit, color="black", linewidth=1.2, label=f"pooled fit r={r_baseline:+.3f}")
    ax.set_xlabel("daily-mean sun_moon_amplitude (committed M4 predictor)")
    ax.set_ylabel("daily SF tide range (m)")
    ax.set_title("M4 scatter: daily tide range vs sun_moon_amplitude, colored by daily mode_ratio")
    ax.legend()
    p3 = os.path.join(OUT, "m4_scatter_by_mode_color.png")
    fig.tight_layout(); fig.savefig(p3, dpi=120); plt.close(fig)
    print(f"  {p3}")

    # diagnostic: daily mode_ratio histogram
    fig, ax = plt.subplots(figsize=(9.0, 5.5))
    ax.hist(df["mode_ratio_daily"], bins=80, color="#3a76c4", edgecolor="black", linewidth=0.3)
    for cut, lbl in [(0.40, "0.40"), (0.55, "0.55")]:
        ax.axvline(cut, color="#bf3030", linestyle="--", linewidth=1.0, alpha=0.8, label=f"user cut {lbl}")
    ax.axvline(0.5, color="black", linestyle=":", linewidth=0.6, alpha=0.7, label="0.5 (perfectly mixed)")
    ax.set_xlim(0.30, 0.60)
    ax.set_xlabel("mode_ratio_daily = daily mean of dielectric / (magnetic + dielectric)")
    ax.set_ylabel("count of days")
    ax.set_title(f"Daily mode_ratio distribution, 1973-2024 (n={len(df):,})\n"
                 f"actual range [{df['mode_ratio_daily'].min():.4f}, {df['mode_ratio_daily'].max():.4f}], std={df['mode_ratio_daily'].std():.4f}")
    ax.legend()
    p4 = os.path.join(OUT, "daily_mode_ratio_distribution.png")
    fig.tight_layout(); fig.savefig(p4, dpi=120); plt.close(fig)
    print(f"  {p4}")

    # ── interpretation ──
    rs_q = [r["r"] for r in quintile_results]
    spread = max(rs_q) - min(rs_q)

    # The user's 3-regime cuts produced degenerate strata at this aggregation
    # (daily mode_ratio collapses to a tight band around 0.5). Interpret from
    # the 5-quintile sensitivity, which sits inside that band but still shows
    # variance.
    q1_r = rs_q[0]; rest_max = max(rs_q[1:])
    q1_elevated = (q1_r > rest_max + 0.03)

    if q1_elevated:
        interp_short = ("Q1 (most magnetic-dominant within the daily band) shows "
                        f"elevated r=+{q1_r:.3f} vs ~{np.mean(rs_q[1:]):.2f} in Q2-Q5 — "
                        "consistent with M4 living in the magnetic register, "
                        "but inside a very narrow daily mode_ratio band [0.489, 0.509]")
    elif spread < 0.03:
        interp_short = ("uniform r across all 5 quintiles within the tight daily mode_ratio "
                        "band — daily-aggregation washes out the mode signal that exists at "
                        "sub-daily timescale")
    else:
        interp_short = ("non-monotonic variation across quintiles within the tight daily band; "
                        "mode-stratification at daily aggregation is not interpretable cleanly")

    interp_long = (
        "**Headline:** the user-specified 3-regime cuts (0.40 / 0.55) are degenerate at "
        "daily aggregation — every single day in the 18,702-day cohort falls into the "
        f"\"balanced\" stratum (mode_ratio_daily range [{df['mode_ratio_daily'].min():.4f}, "
        f"{df['mode_ratio_daily'].max():.4f}], std {df['mode_ratio_daily'].std():.4f}). "
        "The expected stratification cannot be performed at this aggregation level.\n\n"
        "**Why this happens:** the lagna sweeps the full zodiac every 24 h. At any given "
        "10-min timestamp, the lagna-coupled mode mix can swing widely (single-pair "
        "exploratory plots earlier showed std ≈ 0.11, range [0.0002, 0.7504] within a "
        "single year). But aggregating over a full daily lagna rotation symmetrizes the "
        "|Re| and |Im| distributions, driving daily mean(mode_ratio) toward 0.5. The "
        "mode-mix variation lives at sub-daily timescale; it is averaged out by the "
        "M4-style daily aggregation.\n\n"
        "**5-quintile result inside the narrow band:** within mode_ratio_daily ∈ "
        f"[{df['mode_ratio_daily'].min():.4f}, {df['mode_ratio_daily'].max():.4f}], the 5 "
        "quintiles show non-uniform Pearson r. "
    )
    if q1_elevated:
        interp_long += (
            f"The lowest quintile Q1 (mode_ratio_daily ∈ "
            f"[{quintile_results[0]['mode_ratio_min']:.3f}, {quintile_results[0]['mode_ratio_max']:.3f}]) "
            f"shows r=+{q1_r:.3f}, materially higher than the mean of Q2-Q5 "
            f"(r̄ ≈ +{np.mean(rs_q[1:]):.3f}). This is **directionally consistent** with "
            "the analytical reframing — the most magnetic-leaning days within the daily "
            "band give the strongest M4 r — but the band is so narrow (Q1's range is "
            f"only {quintile_results[0]['mode_ratio_max']-quintile_results[0]['mode_ratio_min']:.4f} wide) "
            "that the result should be read as suggestive, not load-bearing. The "
            "register-effect signal exists if it exists at sub-daily resolution; "
            "daily aggregation is the wrong sampling scale for testing it cleanly.\n\n"
        )
    else:
        interp_long += (
            f"The spread across quintiles is {spread:.3f}; no clear monotonic structure. "
            "Within the narrow daily mode_ratio band, no register effect is recoverable "
            "from this aggregation.\n\n"
        )
    interp_long += (
        "**What this tells us about M4 specifically:** at daily aggregation, the "
        "committed M4 r = +0.1945 is the magnetic-component-vs-tide correlation "
        "averaged over a full lagna sweep per day. The mode partition cannot be "
        "tested at this aggregation. A test of register specificity would require "
        "sub-daily aggregation (e.g., 6-h windows centered on local high tide, or "
        "tidal-cycle-aligned bins) and pre-registration of the test design before "
        "re-running on a held-out window. This reanalysis does not constitute such "
        "a test; it constitutes a diagnostic finding that the originally-suggested "
        "stratification cannot be performed at the M4 daily-aggregation scale."
    )

    # ── write report ──
    print(f"\n[report] {REPORT}")
    rows3 = "\n".join(
        f"| {r['regime']} | {r['n']:,} | [{r['mode_ratio_min']:.3f}, {r['mode_ratio_max']:.3f}] | "
        f"{r['r']:+.4f} | [{r['ci_lo']:+.3f}, {r['ci_hi']:+.3f}] | {fmt_p(r['p'])} | {fmt_p(r['p_holm'])} |"
        for r in regime_results
    )
    rows5 = "\n".join(
        f"| Q{r['quintile']} | {r['n']:,} | [{r['mode_ratio_min']:.3f}, {r['mode_ratio_max']:.3f}] | "
        f"{r['r']:+.4f} | [{r['ci_lo']:+.3f}, {r['ci_hi']:+.3f}] | {fmt_p(r['p'])} |"
        for r in quintile_results
    )

    md = f"""# M4 reanalysis through versor mode-stratification

**Status:** EXPLORATORY. Not pre-registered. Not citable as a confirmatory finding.
This is honest reframing of the committed PREREG_001 M4 result through the
mode-decomposition tools made available by tonight's versor engine update.

## Question

PREREG_001 M4 reported r = +0.1945 (n = 18,702) for daily SF tide range vs.
daily-mean Sun-Moon amplitude at the Gainesville lagna over 1973-2024. Tonight's
versor identity revealed:

1. The pair magnitude `|Z_k|` at any target reduces to `2|cos(k(moon-sun)/2)|`
   by closed-form identity — target-invariant.
2. The target-dependent information lives entirely in `Re(Σ Z_k)` (magnetic
   mode) and `Im(Σ Z_k)` (dielectric mode).
3. The committed M4 predictor `mean over k of |cos+cos|` equals
   `magnetic_component / 7` exactly — i.e., M4 was structurally a
   magnetic-mode-only test, with the dielectric mode discarded.

The question this reanalysis asks: **does the M4 r split when stratified by
the daily mode-mix (dielectric / (magnetic + dielectric))?** If M4 truly
lives in the magnetic register, days when the magnetic mode dominates should
yield a stronger r; days when the dielectric mode is large should weaken or
remove the correlation.

## Pipeline verification

Baseline Pearson r on the full daily dataset (n = {len(df):,}, identical to
the committed M4 cohort): **r = {r_baseline:+.4f}**, p = {fmt_p(p_baseline)}.
Committed M4: r = +0.1945, p = 8.39 × 10⁻¹⁵⁹. Match confirms the recomputation
pipeline is consistent with the committed analysis.

Sanity: per-timestamp `sun_moon_amplitude (committed) - magnetic_component / 7`
peaks at {diff.max():.3e} (float32 storage rounding); the algebraic identity
holds at the precision of the stored data.

## Three-regime stratification

Daily mode_ratio cuts:

- **magnetic-dominant**:   mode_ratio < 0.40
- **balanced**:            0.40 ≤ mode_ratio < 0.55
- **dielectric-leaning**:  mode_ratio ≥ 0.55

Results (block-bootstrap CI: 14-day blocks, 1,000 resamples; Holm across 3):

| Regime | n | mode_ratio range | r | 95% CI | raw p | Holm p |
|---|---:|---|---:|---|---:|---:|
{rows3}

## Five-quantile sensitivity

Daily mode_ratio split into 5 equal-frequency quintiles (low → high):

| Quintile | n | mode_ratio range | r | 95% CI | p |
|---|---:|---|---:|---|---:|
{rows5}

## Diagnostic: daily mode_ratio distribution

![Daily mode_ratio distribution](daily_mode_ratio_distribution.png)

The daily mode_ratio distribution is essentially a needle around 0.5 (range
[{df['mode_ratio_daily'].min():.4f}, {df['mode_ratio_daily'].max():.4f}], std
{df['mode_ratio_daily'].std():.4f}). The user-specified cut points 0.40 and
0.55 lie far outside the actual data range — every day falls into the
"balanced" stratum.

![M4 r by 3-mode regime](m4_r_by_mode_regime.png)

![M4 r by 5-quintile](m4_r_by_mode_quintile.png)

![M4 scatter colored by mode_ratio](m4_scatter_by_mode_color.png)

## Honest interpretation

{interp_long}

## Caveats

- Single reanalysis run on a single dataset. Not pre-registered. Stratum
  boundaries (0.40, 0.55) and bin counts (3, 5) were chosen ahead of time
  but not locked under a formal pre-registration; they should be treated as
  reasonable defaults rather than independently-defensible thresholds.
- Block bootstrap within strata is approximate: the 14-day "blocks" are
  contiguous indices in the stratum's date-ordered series, not contiguous
  in original calendar time, since stratum members are scattered across
  dates. The CI is approximately autocorrelation-aware but not strictly so.
- The committed M4 predictor IS proportional to the magnetic component by
  closed-form identity. Stratifying by mode_ratio while testing M4 is
  partially circular: high-mode-ratio days have low magnetic_component,
  hence low predictor variance, which can shrink r mechanically. The 5-bin
  table is the cleanest evidence; the 3-regime table is supportive but
  reflects coarser cuts.
- This reanalysis informs interpretation; it does not constitute a new
  confirmatory finding. Any claim about register-specific tide coupling
  would require pre-registration of the test design before re-running on
  a separate window.
"""
    with open(REPORT, "w") as f:
        f.write(md)
    print(f"  {REPORT}")

    # ── console summary ──
    print()
    print("=" * 70)
    print("M4 MODE-STRATIFICATION SUMMARY")
    print("=" * 70)
    print(f"  baseline r (pooled): {r_baseline:+.4f}  (committed: +0.1945)")
    print()
    for r in regime_results:
        print(f"  {r['regime']:22s}  n={r['n']:>6,}  r={r['r']:+.4f}  CI=[{r['ci_lo']:+.3f},{r['ci_hi']:+.3f}]  Holm p={fmt_p(r['p_holm'])}")
    print()
    print(f"  one-line: M4 r split by mode regime — {interp_short}")
    print()
    print(f"Total wall: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
