"""
M4 ↔ spring/neap envelope, stratified by mode_ratio, plus interaction regression.

Replaces linear Pearson on raw separation (which the prior 1h-quintile
analysis flagged as confounded by non-monotonicity) with the harmonic
predictor:

    envelope = |cos(2 · sep_rad)|     where sep is Sun-Moon angular separation.

This is the "spring/neap envelope": 1 at conjunction (0°) and opposition
(180°), 0 at quadrature (90°, 270°). It linearizes the M4 ↔ separation
relationship so a Pearson r is interpretable.

Tests:
  - Pooled Pearson r (m4_amp, envelope) with 30-day block-bootstrap CI.
  - Per-quintile r using the same q20=0.4451, q80=0.5749 mode_ratio cuts
    as the 1h-quintile prior run.
  - Interaction regression:
       m4_amp ~ envelope + mode_ratio + envelope*mode_ratio
    OLS via numpy.linalg.lstsq, SE from residual variance, t-stats and
    block-bootstrap CI on the interaction coefficient.

The interaction coefficient is the cleanest single-number test of mode-
mediated moderation: does the (envelope → m4_amp) slope vary as a
function of mode_ratio, after accounting for both main effects?

Inputs: research/geosolar/exploratory/m4_mode_stratified_1h_quintile/windows_1h.parquet
Outputs: research/geosolar/exploratory/m4_envelope_mode_stratified/
"""
from __future__ import annotations

import math
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path("/home/inahd/atlas_core")
IN_PARQUET = ROOT / "research/geosolar/exploratory/m4_mode_stratified_1h_quintile/windows_1h.parquet"
OUT = ROOT / "research/geosolar/exploratory/m4_envelope_mode_stratified"

N_BOOT = 1000
BLOCK_HOURS = 24 * 30
RNG = np.random.default_rng(20260508)
sns.set_theme(style="whitegrid", context="paper")

# Match 1h-quintile cuts (locked here for consistency with prior commit)
Q20 = 0.4451
Q80 = 0.5749


# ── helpers ─────────────────────────────────────────────────

def block_bootstrap_ci_r(x, y, block_size=BLOCK_HOURS, n_boot=N_BOOT):
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


def ols_with_se(X: np.ndarray, y: np.ndarray) -> dict:
    """OLS via numpy. Returns coefficients, SE, t-stats, p-values."""
    n, p = X.shape
    # Solve via lstsq (numerically stable)
    beta, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    y_hat = X @ beta
    resid = y - y_hat
    rss = float(resid @ resid)
    sigma2 = rss / (n - p)
    XtX_inv = np.linalg.pinv(X.T @ X)
    var_beta = sigma2 * np.diag(XtX_inv)
    se_beta = np.sqrt(np.maximum(var_beta, 0.0))
    t_stat = beta / np.where(se_beta > 0, se_beta, np.nan)
    p_val = 2.0 * stats.t.sf(np.abs(t_stat), df=n - p)
    # R²
    ss_tot = float((y - y.mean()) @ (y - y.mean()))
    r2 = 1.0 - rss / ss_tot if ss_tot > 0 else float("nan")
    return {
        "beta": beta, "se": se_beta, "t": t_stat, "p": p_val,
        "r2": r2, "sigma2": sigma2, "n": n, "p_params": p,
        "resid": resid,
    }


def block_bootstrap_ci_ols(X: np.ndarray, y: np.ndarray, coef_idx: int,
                           block_size=BLOCK_HOURS, n_boot=N_BOOT):
    """Block-bootstrap CI for one OLS coefficient. Refits OLS each resample."""
    n = len(y)
    if n < max(block_size * 2, 30):
        return (float("nan"), float("nan"))
    n_blocks = int(np.ceil(n / block_size))
    max_start = n - block_size
    bs = np.empty(n_boot)
    for b in range(n_boot):
        starts = RNG.integers(0, max_start + 1, size=n_blocks)
        idx = (starts[:, None] + np.arange(block_size)[None, :]).ravel()[:n]
        Xb = X[idx]; yb = y[idx]
        try:
            beta, _, _, _ = np.linalg.lstsq(Xb, yb, rcond=None)
            bs[b] = beta[coef_idx]
        except Exception:
            bs[b] = np.nan
    bs = bs[~np.isnan(bs)]
    if len(bs) == 0:
        return (float("nan"), float("nan"))
    return float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


# ── main ───────────────────────────────────────────────────

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    print(f"[load] {IN_PARQUET}")
    df = pd.read_parquet(IN_PARQUET)
    print(f"  rows: {len(df):,}")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True).astype("datetime64[ns, UTC]")
    df = df.sort_values("timestamp").reset_index(drop=True)

    print("[derive] envelope = |cos(2·sep_rad)|")
    sep_rad = np.radians(df["sun_moon_sep"].to_numpy(dtype=np.float64))
    envelope = np.abs(np.cos(2.0 * sep_rad)).astype(np.float64)
    df["envelope"] = envelope.astype(np.float32)
    print(f"  envelope: range=[{envelope.min():.4f}, {envelope.max():.4f}]  mean={envelope.mean():.4f}")

    # Re-stratify to match the prior 1h-quintile cuts (locked)
    df["regime"] = pd.cut(
        df["mode_ratio"],
        bins=[-np.inf, Q20, Q80, np.inf],
        labels=["bottom_quintile", "middle", "top_quintile"],
    )

    # ── pooled r ────────────────────────────────────
    print("\n[pooled] m4_amp ↔ envelope")
    x_all = envelope
    y_all = df["m4_amp"].to_numpy(dtype=np.float64)
    r_pool, p_pool = stats.pearsonr(x_all, y_all)
    ci_pool = block_bootstrap_ci_r(x_all, y_all)
    print(f"  pooled (n={len(df):,})  r={r_pool:+.4f}  CI=[{ci_pool[0]:+.3f},{ci_pool[1]:+.3f}]  p={p_pool:.3g}")

    # ── per-stratum r ────────────────────────────────
    print("\n[stratified] per-quintile r")
    results = []
    for name in ["bottom_quintile", "middle", "top_quintile"]:
        sub = df[df["regime"] == name].sort_values("timestamp").reset_index(drop=True)
        n = len(sub)
        x = sub["envelope"].to_numpy(dtype=np.float64)
        y = sub["m4_amp"].to_numpy(dtype=np.float64)
        r, p = stats.pearsonr(x, y)
        ci = block_bootstrap_ci_r(x, y)
        results.append({"regime": name, "n": int(n), "r": float(r), "p": float(p),
                        "ci_lo": ci[0], "ci_hi": ci[1]})
        print(f"  {name:>20s}  n={n:>7,}  r={r:+.4f}  CI=[{ci[0]:+.3f},{ci[1]:+.3f}]  p={p:.3g}")

    bot = next(r for r in results if r["regime"] == "bottom_quintile")
    top = next(r for r in results if r["regime"] == "top_quintile")
    overlap = (bot["ci_lo"] <= top["ci_hi"]) and (top["ci_lo"] <= bot["ci_hi"])
    diff = top["r"] - bot["r"]
    print(f"  → top - bottom r difference: {diff:+.4f}  CIs {'OVERLAP' if overlap else 'DO NOT OVERLAP'}")

    # ── interaction regression ───────────────────────
    print("\n[regression] m4_amp ~ envelope + mode_ratio + envelope*mode_ratio")
    # Center predictors to reduce multicollinearity in interaction term
    env = envelope
    mr = df["mode_ratio"].to_numpy(dtype=np.float64)
    env_c = env - env.mean()
    mr_c = mr - mr.mean()
    inter_c = env_c * mr_c

    X = np.column_stack([np.ones(len(df)), env_c, mr_c, inter_c])
    y = y_all
    fit = ols_with_se(X, y)
    print(f"  n={fit['n']:,}  R² = {fit['r2']:.4f}")
    names = ["intercept", "envelope (centered)", "mode_ratio (centered)", "envelope×mode_ratio"]
    for i, nm in enumerate(names):
        print(f"  β[{nm:>22s}] = {fit['beta'][i]:+.5f}  SE={fit['se'][i]:.5f}  "
              f"t={fit['t'][i]:+7.2f}  p={fit['p'][i]:.3g}")

    # Block-bootstrap CI on interaction coefficient
    print("  [bootstrap] CI on interaction coefficient (1000 resamples)")
    inter_idx = 3
    inter_ci = block_bootstrap_ci_ols(X, y, inter_idx)
    print(f"  β[envelope×mode_ratio] = {fit['beta'][inter_idx]:+.5f}  "
          f"95% CI=[{inter_ci[0]:+.5f}, {inter_ci[1]:+.5f}]  "
          f"OLS p={fit['p'][inter_idx]:.3g}")
    interaction_significant = (inter_ci[0] > 0) or (inter_ci[1] < 0)
    print(f"  → interaction CI {'EXCLUDES' if interaction_significant else 'INCLUDES'} zero")

    # Compare main-effects-only fit (drop interaction) for r² comparison
    X_main = np.column_stack([np.ones(len(df)), env_c, mr_c])
    fit_main = ols_with_se(X_main, y)
    delta_r2 = fit['r2'] - fit_main['r2']
    print(f"  R²(main+interaction)={fit['r2']:.5f}  R²(main only)={fit_main['r2']:.5f}  "
          f"Δ={delta_r2:.5f}")

    # ── plots ───────────────────────────────────────
    print("\n[plots]")

    # (a) m4_vs_envelope_pooled.png
    fig, ax = plt.subplots(figsize=(10.0, 6.0))
    rng_sample = np.random.default_rng(20260508)
    n = len(df)
    idx = rng_sample.choice(n, size=min(15000, n), replace=False)
    ax.scatter(envelope[idx], y_all[idx], s=2, alpha=0.18, color="#3a76c4", edgecolors="none")
    b1, b0 = np.polyfit(envelope, y_all, 1)
    xs = np.linspace(0, 1, 50)
    ax.plot(xs, b0 + b1 * xs, color="black", linewidth=1.2, label=f"linear fit r={r_pool:+.4f}")
    ax.set_xlabel("spring/neap envelope = |cos(2·sep)| — 1 at syzygy, 0 at quadrature")
    ax.set_ylabel("M4 amplitude (m) — 6h-centered rolling tide range")
    ax.set_title(f"M4 amplitude vs spring/neap envelope, pooled — n={n:,}, "
                 f"r={r_pool:+.4f}, CI=[{ci_pool[0]:+.3f},{ci_pool[1]:+.3f}]")
    ax.legend()
    fig.tight_layout()
    p1 = OUT / "m4_vs_envelope_pooled.png"
    fig.savefig(p1, dpi=120); plt.close(fig); print(f"  → {p1.name}")

    # (b) m4_vs_envelope_by_quintile.png
    fig, axes = plt.subplots(1, 3, figsize=(15.0, 5.5), sharey=True)
    color_map = {"bottom_quintile": "#bf3030", "middle": "#cc8030", "top_quintile": "#3a76c4"}
    for ax, regime in zip(axes, ["bottom_quintile", "middle", "top_quintile"]):
        sub = df[df["regime"] == regime]
        n_s = len(sub)
        sample = sub.sample(n=min(10000, n_s), random_state=20260508) if n_s > 10000 else sub
        ax.scatter(sample["envelope"], sample["m4_amp"], s=2, alpha=0.20,
                   color=color_map[regime], edgecolors="none")
        if n_s >= 3 and sub["envelope"].std() > 0:
            xx = sub["envelope"].to_numpy(dtype=np.float64)
            yy = sub["m4_amp"].to_numpy(dtype=np.float64)
            b1, b0 = np.polyfit(xx, yy, 1)
            xs = np.linspace(0, 1, 50)
            ax.plot(xs, b0 + b1 * xs, color="black", linewidth=1.0)
        m = next(r for r in results if r["regime"] == regime)
        ax.set_title(f"{regime}\nn={m['n']:,}  r={m['r']:+.3f}  CI=[{m['ci_lo']:+.3f},{m['ci_hi']:+.3f}]")
        ax.set_xlabel("envelope = |cos(2·sep)|")
        ax.set_xlim(-0.02, 1.02)
    axes[0].set_ylabel("M4 amplitude (m)")
    fig.suptitle("M4 amplitude vs spring/neap envelope, stratified by 1h mode_ratio quintile", y=1.0)
    fig.tight_layout()
    p2 = OUT / "m4_vs_envelope_by_quintile.png"
    fig.savefig(p2, dpi=120); plt.close(fig); print(f"  → {p2.name}")

    # (c) correlation_envelope_by_quintile_with_bootstrap.png
    fig, ax = plt.subplots(figsize=(9.0, 5.5))
    names = [r["regime"] for r in results]
    rs = [r["r"] for r in results]
    err_lo = [rs[i] - results[i]["ci_lo"] for i in range(len(rs))]
    err_hi = [results[i]["ci_hi"] - rs[i] for i in range(len(rs))]
    colors = ["#bf3030", "#cc8030", "#3a76c4"]
    xs_b = np.arange(len(names))
    ax.bar(xs_b, rs, color=colors, edgecolor="black", linewidth=0.5)
    ax.errorbar(xs_b, rs, yerr=[err_lo, err_hi], fmt="none", ecolor="black", capsize=4, linewidth=1.0)
    ax.axhline(r_pool, color="black", linestyle="--", linewidth=0.7, label=f"pooled r={r_pool:+.3f}")
    ax.axhline(0, color="black", linewidth=0.4)
    ax.set_xticks(xs_b)
    ax.set_xticklabels([f"{n}\n(n={results[i]['n']:,})" for i, n in enumerate(names)])
    ax.set_ylabel("Pearson r (M4_amp ↔ envelope)")
    ax.set_title(f"M4 ↔ envelope correlation by 1h mode_ratio quintile\n"
                 f"top − bottom = {diff:+.4f}, CIs {'OVERLAP' if overlap else 'DO NOT OVERLAP'}")
    ax.legend()
    fig.tight_layout()
    p3 = OUT / "correlation_envelope_by_quintile_with_bootstrap.png"
    fig.savefig(p3, dpi=120); plt.close(fig); print(f"  → {p3.name}")

    # (d) interaction_regression_diagnostic.png — residuals from main-effects-only model,
    #     plotted vs envelope and colored by mode_ratio. If the interaction is real,
    #     residual slope should differ across mode_ratio strata.
    resid_main = fit_main["resid"]
    fig, axes = plt.subplots(1, 2, figsize=(14.0, 6.0))
    # Left: residuals vs envelope, colored by mode_ratio
    n_plot = 15000
    idx_p = rng_sample.choice(len(df), size=min(n_plot, len(df)), replace=False)
    sc = axes[0].scatter(envelope[idx_p], resid_main[idx_p], c=df["mode_ratio"].iloc[idx_p],
                         s=2, alpha=0.30, cmap="coolwarm", vmin=Q20, vmax=Q80, edgecolors="none")
    plt.colorbar(sc, ax=axes[0], label="mode_ratio")
    # Per-stratum residual regression line
    for regime, color in zip(["bottom_quintile", "middle", "top_quintile"], colors):
        mask = (df["regime"] == regime).to_numpy()
        if mask.sum() < 3:
            continue
        b1_r, b0_r = np.polyfit(envelope[mask], resid_main[mask], 1)
        xs_fit = np.linspace(0, 1, 50)
        axes[0].plot(xs_fit, b0_r + b1_r * xs_fit, color=color, linewidth=1.4,
                     label=f"{regime} slope={b1_r:+.4f}")
    axes[0].axhline(0, color="black", linewidth=0.4)
    axes[0].set_xlabel("envelope")
    axes[0].set_ylabel("residual (m4_amp − main-effects-only fit)")
    axes[0].set_title("Residual after main-effects model, by mode_ratio")
    axes[0].legend(loc="best", fontsize=8)

    # Right: residual histograms by stratum
    for regime, color in zip(["bottom_quintile", "middle", "top_quintile"], colors):
        mask = (df["regime"] == regime).to_numpy()
        axes[1].hist(resid_main[mask], bins=50, alpha=0.4, color=color, density=True, label=regime)
    axes[1].set_xlabel("residual after main-effects model")
    axes[1].set_ylabel("density")
    axes[1].set_title("Residual distribution per stratum (should be ≈identical if no interaction)")
    axes[1].legend(loc="best", fontsize=8)
    fig.suptitle(f"Interaction diagnostic — interaction β = {fit['beta'][inter_idx]:+.5f}, "
                 f"95% bootstrap CI=[{inter_ci[0]:+.5f}, {inter_ci[1]:+.5f}], "
                 f"OLS t={fit['t'][inter_idx]:+.2f}", y=1.0)
    fig.tight_layout()
    p4 = OUT / "interaction_regression_diagnostic.png"
    fig.savefig(p4, dpi=120); plt.close(fig); print(f"  → {p4.name}")

    # ── synthesis ───────────────────────────────────
    write_synthesis(r_pool, ci_pool, p_pool, results, fit, fit_main, inter_ci,
                    delta_r2, overlap, diff, interaction_significant, len(df),
                    time.time() - t0)

    # ── console summary ─────────────────────────────
    print()
    print("=" * 70)
    print(f"  SF gauge tide range, harmonic predictor (envelope = |cos(2·sep)|)")
    print("=" * 70)
    print(f"  POOLED  n={len(df):,}  r={r_pool:+.4f}  CI=[{ci_pool[0]:+.3f},{ci_pool[1]:+.3f}]")
    for r in results:
        print(f"  {r['regime']:>20s}  n={r['n']:>7,}  r={r['r']:+.4f}  "
              f"CI=[{r['ci_lo']:+.3f},{r['ci_hi']:+.3f}]")
    print(f"  Top - bottom: {diff:+.4f}  CIs {'OVERLAP' if overlap else 'DO NOT OVERLAP'}")
    print()
    print(f"  Interaction (envelope × mode_ratio) coefficient:")
    print(f"    β = {fit['beta'][inter_idx]:+.5f}")
    print(f"    SE = {fit['se'][inter_idx]:.5f}")
    print(f"    OLS t = {fit['t'][inter_idx]:+.2f}, OLS p = {fit['p'][inter_idx]:.3g}")
    print(f"    95% block-bootstrap CI = [{inter_ci[0]:+.5f}, {inter_ci[1]:+.5f}]")
    print(f"    {'EXCLUDES' if interaction_significant else 'INCLUDES'} zero")
    print(f"  R² gain from interaction: {delta_r2:+.5f}  ({'meaningful' if delta_r2 > 0.001 else 'tiny'})")
    print(f"\nTotal wall: {time.time() - t0:.1f}s")


def write_synthesis(r_pool, ci_pool, p_pool, results, fit, fit_main, inter_ci,
                    delta_r2, overlap, diff, interaction_significant, n_total,
                    total_wall):
    inter_idx = 3
    md = []
    md.append("# M4 ↔ spring/neap envelope, mode-stratified — SYNTHESIS\n")
    md.append("**Status:** EXPLORATORY. Not pre-registered. Not citable as confirmatory.\n")
    md.append("Date: 2026-05-08\n")

    md.append("## What this is\n")
    md.append("Follow-up to the 1h-quintile mode-stratification (commit f2b45d1)")
    md.append("where the prior result (non-overlapping CIs across mode_ratio")
    md.append("quintiles) was flagged as confounded because:")
    md.append("")
    md.append("- M4 ↔ Sun-Moon angular separation is non-monotonic")
    md.append("  (|cos(2·sep)| envelope, 4 cycles per 360°).")
    md.append("- Stratifying by mode_ratio implicitly stratifies by the")
    md.append("  separation distribution.")
    md.append("- Linear Pearson r on a non-monotonic relationship gives different")
    md.append("  values across sub-ranges of the predictor by construction —")
    md.append("  selection bias indistinguishable from genuine moderation.")
    md.append("")
    md.append("This pass replaces the linear-separation predictor with the harmonic")
    md.append("**spring/neap envelope = |cos(2·sep)|** (1 at syzygy, 0 at quadrature),")
    md.append("which linearizes the relationship and makes Pearson r interpretable.")
    md.append("Adds an interaction-regression test that directly tests whether the")
    md.append("(envelope → m4_amp) slope varies as a function of mode_ratio after")
    md.append("controlling for both main effects.")
    md.append("")

    md.append("## Pooled m4_amp ↔ envelope\n")
    md.append(f"- Pearson r = **{r_pool:+.4f}**")
    md.append(f"- 95% block-bootstrap CI = [{ci_pool[0]:+.3f}, {ci_pool[1]:+.3f}]")
    md.append(f"- raw p = {p_pool:.3g}")
    md.append(f"- n = {n_total:,}")
    md.append("")
    if r_pool > 0.05:
        md.append(f"r ≈ +{r_pool:.3f} positive — confirms the basic spring/neap effect:")
        md.append("M4 amplitude is materially larger when Sun-Moon are at conjunction or")
        md.append("opposition, smaller at quadrature. The envelope predictor recovers")
        md.append("the structure that linear separation hid in the prior pass.")
    else:
        md.append(f"r ≈ +{r_pool:.3f} smaller than expected for a spring/neap signal.")
        md.append("Either SF tide is dominated by other constituents, or the")
        md.append("envelope formulation is sub-optimal.")
    md.append("")

    md.append("## Per-stratum r\n")
    md.append("Same q20=0.4451, q80=0.5749 cuts as the 1h-quintile prior run.")
    md.append("")
    md.append("| Quintile | n | Pearson r | 95% bootstrap CI | raw p |")
    md.append("|---|---:|---:|---|---:|")
    for r in results:
        md.append(f"| {r['regime']} | {r['n']:,} | {r['r']:+.4f} | "
                  f"[{r['ci_lo']:+.3f}, {r['ci_hi']:+.3f}] | {r['p']:.3g} |")
    md.append(f"| **POOLED** | {n_total:,} | {r_pool:+.4f} | "
              f"[{ci_pool[0]:+.3f}, {ci_pool[1]:+.3f}] | {p_pool:.3g} |")
    md.append("")
    md.append(f"top − bottom: {diff:+.4f}, CIs {'OVERLAP' if overlap else 'DO NOT OVERLAP'}.")
    md.append("")

    md.append("## Interaction regression\n")
    md.append("Centered predictors (mean-subtracted) to reduce collinearity in interaction term.")
    md.append("")
    md.append("    m4_amp = β₀ + β₁·envelope_c + β₂·mode_ratio_c + β₃·(envelope_c × mode_ratio_c) + ε\n")
    md.append("| Coefficient | β | SE | t | OLS p |")
    md.append("|---|---:|---:|---:|---:|")
    rownames = ["intercept", "envelope (centered)", "mode_ratio (centered)", "envelope × mode_ratio"]
    for i, nm in enumerate(rownames):
        md.append(f"| {nm} | {fit['beta'][i]:+.5f} | {fit['se'][i]:.5f} | "
                  f"{fit['t'][i]:+.2f} | {fit['p'][i]:.3g} |")
    md.append("")
    md.append(f"- R²(main + interaction) = **{fit['r2']:.5f}**")
    md.append(f"- R²(main only)         = **{fit_main['r2']:.5f}**")
    md.append(f"- ΔR² from interaction  = **{delta_r2:+.5f}**")
    md.append(f"- Block-bootstrap 95% CI on interaction β: [{inter_ci[0]:+.5f}, {inter_ci[1]:+.5f}]")
    md.append(f"- Interaction CI {'**EXCLUDES**' if interaction_significant else '**INCLUDES**'} zero")
    md.append("")

    md.append("## Honest interpretation\n")
    if interaction_significant:
        md.append(f"The interaction term β₃ = {fit['beta'][inter_idx]:+.5f} has 95% block-bootstrap")
        md.append("CI excluding zero, meaning the (envelope → m4_amp) slope")
        md.append("**does** vary with mode_ratio after controlling for both main effects.")
        if delta_r2 > 0.005:
            md.append(f"ΔR² = {delta_r2:.5f} indicates the interaction adds meaningful")
            md.append("explanatory power beyond main effects.")
        else:
            md.append(f"However ΔR² = {delta_r2:.5f} is very small — the interaction is")
            md.append("statistically distinguishable from zero but explains very little")
            md.append("additional variance. Likely a weak real effect or a residual")
            md.append("artifact from the geometric coupling that the envelope predictor")
            md.append("doesn't fully resolve.")
    else:
        md.append(f"The interaction term β₃ = {fit['beta'][inter_idx]:+.5f} has 95% block-bootstrap")
        md.append("CI **including** zero. The (envelope → m4_amp) slope does NOT")
        md.append("statistically vary with mode_ratio under the cleaner test.")
        md.append("The non-overlapping CIs in the prior 1h-quintile pass were")
        md.append("therefore consistent with the selection-bias artifact and not")
        md.append("with genuine moderation.")
    md.append("")

    md.append("## Does the envelope predictor resolve the prior confound?\n")
    md.append("Partially. The envelope predictor removes the non-monotonicity issue")
    md.append("(linear Pearson r is now interpretable for the envelope-vs-m4 relationship),")
    md.append("but a residual coupling remains: mode_ratio at the lagna is determined")
    md.append("by lagna-Sun-Moon geometry, which is also what determines the envelope")
    md.append("value. Strata might still over-/under-sample envelope sub-ranges, though")
    md.append("the relationship is now monotonic so the bias is smaller.")
    md.append("")
    md.append("The interaction regression is the cleaner test: it directly asks whether")
    md.append("the envelope→m4 slope varies across mode_ratio levels, controlling for")
    md.append("both main effects. The interaction coefficient is the answer.")
    md.append("")

    md.append("## Plots\n")
    md.append("- `m4_vs_envelope_pooled.png` — the envelope predictor at the basic level.")
    md.append("- `m4_vs_envelope_by_quintile.png` — three-panel scatter, per-stratum.")
    md.append("- `correlation_envelope_by_quintile_with_bootstrap.png` — bar chart with CIs.")
    md.append("- `interaction_regression_diagnostic.png` — residuals from main-effects-only")
    md.append("  fit, plotted vs envelope by stratum; if the interaction is real, residual")
    md.append("  slopes should differ across mode_ratio levels.")
    md.append("")

    md.append("## Caveats\n")
    md.append("- Single-window test on data already used in PREREG_001 and the 1h-quintile")
    md.append("  prior run. Cannot serve as confirmatory.")
    md.append("- Quintile cuts are the same as the prior pass (q20=0.4451, q80=0.5749) —")
    md.append("  carrying forward the post-hoc data-driven boundaries.")
    md.append("- The envelope predictor is one canonical choice; harmonic regression with")
    md.append("  cos(2·sep) and sin(2·sep) jointly would be more general (allowing arbitrary")
    md.append("  phase) but adds a degree of freedom.")
    md.append("- Residual coupling between mode_ratio and envelope (both functions of")
    md.append("  Sun-Moon-lagna geometry) is mitigated but not fully removed. Cleanest")
    md.append("  test would stratify by a variable independent of Sun-Moon geometry")
    md.append("  (Kp, season, hour-of-day).")
    md.append(f"\n*Total wall: {total_wall:.1f}s*")

    p = OUT / "SYNTHESIS.md"
    p.write_text("\n".join(md))


if __name__ == "__main__":
    main()
