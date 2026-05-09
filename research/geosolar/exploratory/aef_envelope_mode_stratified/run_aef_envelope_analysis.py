"""
AEF (atmospheric electric field potential gradient) versor mode-stratified
analysis — counterpart to the M4 envelope-mode-stratified test.

Framework prediction:
  - M4 (magnetic-mode rotational/equatorial phenomenon): no mode-coupling.
    VERIFIED in commit 7847576 — interaction β = -0.00475, p = 0.786,
    bootstrap CI [-0.022, +0.013].
  - AEF (dielectric-mode longitudinal/axial phenomenon): mode-coupling
    SHOULD be present. THIS test.

Source: PANGAEA 10.1594/PANGAEA.942036 (committed at e9329c8)
        Hungary Széchenyi István Observatory, Nagycenk
        47.632°N, 16.718°E, 1962-2009, hourly.

Methodology mirrors the M4 envelope analysis (commit 7847576) for direct
comparability:
  - Predictor: spring/neap envelope = |cos(2 · sun_moon_separation)|
  - Stratification: data-driven quintiles of mode_ratio at the Hungary lagna
  - Cleaner test: interaction regression
        AEF ~ envelope + mode_ratio + envelope*mode_ratio + controls
    where controls are fair-weather meteorological covariates.
  - Block-bootstrap CI: 30-day blocks, 1000 resamples.

Fair-weather filter (per AEF literature: Harrison, Marcz, etc.):
  - precip_era == 0
  - wind_speed_era < 8 m/s
  - RH_era < 90 %
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
sys.path.insert(0, str(ROOT))

PANGAEA_TSV = ROOT / "research/geosolar/dielectric_mode_archives/pilot_fetches/PANGAEA_942036_szechenyi_hungary_PG_1962_2009.tab"
OUT = ROOT / "research/geosolar/exploratory/aef_envelope_mode_stratified"

LAT_HU, LON_HU = 47.632, 16.718

K_VALUES = [1, 2, 3, 4, 6, 7, 12]
EPS = 1e-12

N_BOOT = 1000
BLOCK_HOURS = 24 * 30        # 30-day blocks at hourly cadence

RNG = np.random.default_rng(20260508)
sns.set_theme(style="whitegrid", context="paper")

# Fair-weather thresholds (conservative)
FAIR_WEATHER = {
    "precip_max": 0.0,      # no precipitation
    "wind_max": 8.0,        # m/s
    "rh_max": 90.0,         # %
}


# ── ephemeris ─────────────────────────────────────

def compute_lagna_sun_moon(timestamps_utc: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
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
        _cusps, ascmc = swe.houses(jd, LAT_HU, LON_HU, b"W")
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


# ── statistics helpers ────────────────────────────

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
    n, p = X.shape
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
    ss_tot = float((y - y.mean()) @ (y - y.mean()))
    r2 = 1.0 - rss / ss_tot if ss_tot > 0 else float("nan")
    return {"beta": beta, "se": se_beta, "t": t_stat, "p": p_val,
            "r2": r2, "n": n, "p_params": p, "resid": resid}


def block_bootstrap_ci_ols(X, y, coef_idx, block_size=BLOCK_HOURS, n_boot=N_BOOT):
    n = len(y)
    if n < max(block_size * 2, 30):
        return (float("nan"), float("nan"))
    n_blocks = int(np.ceil(n / block_size))
    max_start = n - block_size
    bs = np.empty(n_boot)
    for b in range(n_boot):
        starts = RNG.integers(0, max_start + 1, size=n_blocks)
        idx = (starts[:, None] + np.arange(block_size)[None, :]).ravel()[:n]
        try:
            beta, _, _, _ = np.linalg.lstsq(X[idx], y[idx], rcond=None)
            bs[b] = beta[coef_idx]
        except Exception:
            bs[b] = np.nan
    bs = bs[~np.isnan(bs)]
    if len(bs) == 0:
        return (float("nan"), float("nan"))
    return float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


# ── main ──────────────────────────────────────────

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    print(f"[load] {PANGAEA_TSV}")
    # Find header end
    with open(PANGAEA_TSV) as f:
        lines = f.read().split("\n")
    sep_idx = next(i for i, l in enumerate(lines) if l.startswith("*/"))
    df = pd.read_csv(PANGAEA_TSV, sep="\t", skiprows=sep_idx + 1, low_memory=False)
    df.columns = ["ts", "pg_uncorr", "pg_corr", "pg_unc",
                  "T_nck", "RH_nck", "precip_nck", "swd_nck",
                  "wind_nck", "wind_std_nck", "wdir_nck", "wdir_std_nck",
                  "T_era", "RH_era", "precip_era", "swd_era",
                  "wind_era", "wdir_era", "pres_era",
                  "snow_cov", "snow_dep", "cloud_tot", "cloud_low", "cbh"]
    df["ts"] = pd.to_datetime(df["ts"], errors="coerce", utc=True)
    df = df.dropna(subset=["ts"]).reset_index(drop=True)
    print(f"  raw rows: {len(df):,}  span: {df.ts.min()} → {df.ts.max()}")

    # ── fair-weather filter ───────────────────────
    print(f"[filter] fair-weather: precip_era==0, wind_era<{FAIR_WEATHER['wind_max']}, RH_era<{FAIR_WEATHER['rh_max']}")
    fw = df[
        df["pg_corr"].notna()
        & (df["precip_era"] == FAIR_WEATHER["precip_max"])
        & (df["wind_era"] < FAIR_WEATHER["wind_max"])
        & (df["RH_era"] < FAIR_WEATHER["rh_max"])
        & df["T_era"].notna()
    ].copy().reset_index(drop=True)
    print(f"  after filter: {len(fw):,} rows ({100.0*len(fw)/len(df):.1f}% of raw)")

    # ── ephemeris ─────────────────────────────────
    print(f"[ephem] Hungary lagna + sun + moon for {len(fw):,} timestamps")
    t_eph = time.time()
    lagna, sun_l, moon_l = compute_lagna_sun_moon(fw["ts"].to_numpy())
    print(f"  ephemeris wall: {time.time() - t_eph:.1f}s")

    print("[versor] decompose Sun-Moon at Hungary lagna")
    mag, die = versor_decompose(sun_l, moon_l, lagna)
    fw["mode_ratio"] = (die / (mag + die + EPS)).astype(np.float32)
    sep_rad = np.radians((moon_l - sun_l) % 360.0)
    fw["envelope"] = np.abs(np.cos(2.0 * sep_rad)).astype(np.float32)
    fw["sun_moon_sep"] = ((moon_l - sun_l) % 360.0).astype(np.float32)

    mr = fw["mode_ratio"].to_numpy(dtype=np.float64)
    print(f"  mode_ratio: range=[{mr.min():.4f}, {mr.max():.4f}]  std={mr.std():.4f}")

    # Quintile cuts for stratification
    q20 = float(np.quantile(mr, 0.20))
    q80 = float(np.quantile(mr, 0.80))
    print(f"[stratify] data-driven quintile cuts: q20={q20:.4f}, q80={q80:.4f}")
    fw["regime"] = pd.cut(fw["mode_ratio"],
                          bins=[-np.inf, q20, q80, np.inf],
                          labels=["bottom_quintile", "middle", "top_quintile"])

    # ── pooled r ──────────────────────────────
    print("\n[pooled] PG_corr ↔ envelope")
    x_all = fw["envelope"].to_numpy(dtype=np.float64)
    y_all = fw["pg_corr"].to_numpy(dtype=np.float64)
    r_pool, p_pool = stats.pearsonr(x_all, y_all)
    ci_pool = block_bootstrap_ci_r(x_all, y_all)
    print(f"  pooled (n={len(fw):,})  r={r_pool:+.4f}  CI=[{ci_pool[0]:+.3f},{ci_pool[1]:+.3f}]  p={p_pool:.3g}")

    # ── per-stratum r ─────────────────────────
    print("\n[stratified] per-quintile r")
    results = []
    for name in ["bottom_quintile", "middle", "top_quintile"]:
        sub = fw[fw["regime"] == name].sort_values("ts").reset_index(drop=True)
        n = len(sub)
        x = sub["envelope"].to_numpy(dtype=np.float64)
        y = sub["pg_corr"].to_numpy(dtype=np.float64)
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

    # ── interaction regression ────────────────
    print("\n[regression] PG_corr ~ envelope + mode_ratio + envelope*mode_ratio + controls")
    # Centered predictors
    env = fw["envelope"].to_numpy(dtype=np.float64)
    mr_a = fw["mode_ratio"].to_numpy(dtype=np.float64)
    env_c = env - env.mean()
    mr_c = mr_a - mr_a.mean()
    inter_c = env_c * mr_c
    # Controls: T_era, wind_era, RH_era (centered); season as sin/cos of day-of-year
    T_c = fw["T_era"].to_numpy(dtype=np.float64) - fw["T_era"].mean()
    W_c = fw["wind_era"].to_numpy(dtype=np.float64) - fw["wind_era"].mean()
    RH_c = fw["RH_era"].to_numpy(dtype=np.float64) - fw["RH_era"].mean()
    doy = fw["ts"].dt.dayofyear.to_numpy(dtype=np.float64)
    season_sin = np.sin(2.0 * np.pi * doy / 365.25)
    season_cos = np.cos(2.0 * np.pi * doy / 365.25)

    X = np.column_stack([
        np.ones(len(fw)),
        env_c, mr_c, inter_c,
        T_c, W_c, RH_c, season_sin, season_cos,
    ])
    fit = ols_with_se(X, y_all)
    coef_names = ["intercept", "envelope (centered)", "mode_ratio (centered)",
                  "envelope×mode_ratio",
                  "T_era (centered)", "wind_era (centered)", "RH_era (centered)",
                  "season_sin", "season_cos"]
    print(f"  n={fit['n']:,}  R² = {fit['r2']:.5f}")
    for i, nm in enumerate(coef_names):
        print(f"  β[{nm:>22s}] = {fit['beta'][i]:+.5f}  SE={fit['se'][i]:.5f}  "
              f"t={fit['t'][i]:+7.2f}  p={fit['p'][i]:.3g}")

    inter_idx = 3
    print("  [bootstrap] CI on interaction coefficient")
    inter_ci = block_bootstrap_ci_ols(X, y_all, inter_idx)
    print(f"  β[envelope×mode_ratio] = {fit['beta'][inter_idx]:+.5f}  "
          f"95% CI=[{inter_ci[0]:+.5f}, {inter_ci[1]:+.5f}]  "
          f"OLS p={fit['p'][inter_idx]:.3g}")
    inter_sig = (inter_ci[0] > 0) or (inter_ci[1] < 0)
    print(f"  → interaction CI {'EXCLUDES' if inter_sig else 'INCLUDES'} zero")

    # Compare to main-effects-only (envelope + mode_ratio + controls, no interaction)
    X_main = np.column_stack([
        np.ones(len(fw)), env_c, mr_c,
        T_c, W_c, RH_c, season_sin, season_cos,
    ])
    fit_main = ols_with_se(X_main, y_all)
    delta_r2 = fit["r2"] - fit_main["r2"]
    print(f"  R²(full)={fit['r2']:.5f}  R²(main only)={fit_main['r2']:.5f}  Δ={delta_r2:+.5f}")

    # CI on mode_ratio main effect (independent predictive power, after envelope+controls)
    print("  [bootstrap] CI on mode_ratio main coefficient (after envelope + controls)")
    mr_ci = block_bootstrap_ci_ols(X, y_all, 2)
    print(f"  β[mode_ratio] = {fit['beta'][2]:+.5f}  95% CI=[{mr_ci[0]:+.5f}, {mr_ci[1]:+.5f}]  "
          f"OLS p={fit['p'][2]:.3g}")

    # ── plots ──────────────────────────────────
    print("\n[plots]")

    # (a) aef_vs_envelope_pooled.png
    fig, ax = plt.subplots(figsize=(10.0, 6.0))
    rng = np.random.default_rng(20260508)
    n = len(fw)
    idx = rng.choice(n, size=min(15000, n), replace=False)
    ax.scatter(env[idx], y_all[idx], s=2, alpha=0.18, color="#3a76c4", edgecolors="none")
    b1, b0 = np.polyfit(env, y_all, 1)
    xs = np.linspace(0, 1, 50)
    ax.plot(xs, b0 + b1 * xs, color="black", linewidth=1.2, label=f"fit r={r_pool:+.4f}")
    ax.set_xlabel("spring/neap envelope = |cos(2·sep)|")
    ax.set_ylabel("PG_corr [V/m]  (corrected hourly potential gradient)")
    ax.set_title(f"AEF vs spring/neap envelope (fair-weather), pooled — n={n:,}, "
                 f"r={r_pool:+.4f}, CI=[{ci_pool[0]:+.3f},{ci_pool[1]:+.3f}]")
    ax.legend()
    fig.tight_layout()
    p1 = OUT / "aef_vs_envelope_pooled.png"
    fig.savefig(p1, dpi=120); plt.close(fig); print(f"  → {p1.name}")

    # (b) aef_vs_envelope_by_mode_quintile.png
    fig, axes = plt.subplots(1, 3, figsize=(15.0, 5.5), sharey=True)
    color_map = {"bottom_quintile": "#bf3030", "middle": "#cc8030", "top_quintile": "#3a76c4"}
    for ax, regime in zip(axes, ["bottom_quintile", "middle", "top_quintile"]):
        sub = fw[fw["regime"] == regime]
        n_s = len(sub)
        sample = sub.sample(n=min(10000, n_s), random_state=20260508) if n_s > 10000 else sub
        ax.scatter(sample["envelope"], sample["pg_corr"], s=2, alpha=0.20,
                   color=color_map[regime], edgecolors="none")
        if n_s >= 3 and sub["envelope"].std() > 0:
            xx = sub["envelope"].to_numpy(dtype=np.float64)
            yy = sub["pg_corr"].to_numpy(dtype=np.float64)
            b1, b0 = np.polyfit(xx, yy, 1)
            xs = np.linspace(0, 1, 50)
            ax.plot(xs, b0 + b1 * xs, color="black", linewidth=1.0)
        m = next(r for r in results if r["regime"] == regime)
        ax.set_title(f"{regime}\nn={m['n']:,}  r={m['r']:+.3f}  "
                     f"CI=[{m['ci_lo']:+.3f},{m['ci_hi']:+.3f}]")
        ax.set_xlabel("envelope")
        ax.set_xlim(-0.02, 1.02)
    axes[0].set_ylabel("PG_corr [V/m]")
    fig.suptitle("AEF vs spring/neap envelope, stratified by mode_ratio quintile", y=1.0)
    fig.tight_layout()
    p2 = OUT / "aef_vs_envelope_by_mode_quintile.png"
    fig.savefig(p2, dpi=120); plt.close(fig); print(f"  → {p2.name}")

    # (c) interaction_regression_AEF_diagnostic.png
    resid_main = fit_main["resid"]
    fig, axes = plt.subplots(1, 2, figsize=(14.0, 6.0))
    n_plot = min(15000, len(fw))
    idx_p = rng.choice(len(fw), size=n_plot, replace=False)
    sc = axes[0].scatter(env[idx_p], resid_main[idx_p], c=fw["mode_ratio"].iloc[idx_p],
                         s=2, alpha=0.30, cmap="coolwarm", vmin=q20, vmax=q80, edgecolors="none")
    plt.colorbar(sc, ax=axes[0], label="mode_ratio")
    for regime, color in zip(["bottom_quintile", "middle", "top_quintile"],
                              ["#bf3030", "#cc8030", "#3a76c4"]):
        mask = (fw["regime"] == regime).to_numpy()
        if mask.sum() < 3: continue
        b1_r, b0_r = np.polyfit(env[mask], resid_main[mask], 1)
        xs_fit = np.linspace(0, 1, 50)
        axes[0].plot(xs_fit, b0_r + b1_r * xs_fit, color=color, linewidth=1.4,
                     label=f"{regime} slope={b1_r:+.4f}")
    axes[0].axhline(0, color="black", linewidth=0.4)
    axes[0].set_xlabel("envelope")
    axes[0].set_ylabel("residual (PG_corr − main+controls fit)")
    axes[0].set_title("Residual after main-effects+controls model, by mode_ratio")
    axes[0].legend(loc="best", fontsize=8)
    for regime, color in zip(["bottom_quintile", "middle", "top_quintile"],
                              ["#bf3030", "#cc8030", "#3a76c4"]):
        mask = (fw["regime"] == regime).to_numpy()
        axes[1].hist(resid_main[mask], bins=60, alpha=0.4, color=color, density=True, label=regime)
    axes[1].set_xlabel("residual after main-effects+controls model")
    axes[1].set_ylabel("density")
    axes[1].set_title("Residual distribution per stratum")
    axes[1].legend(loc="best", fontsize=8)
    fig.suptitle(f"AEF interaction diagnostic — interaction β = {fit['beta'][inter_idx]:+.5f}, "
                 f"95% bootstrap CI = [{inter_ci[0]:+.5f}, {inter_ci[1]:+.5f}], "
                 f"OLS t = {fit['t'][inter_idx]:+.2f}", y=1.0)
    fig.tight_layout()
    p3 = OUT / "interaction_regression_AEF_diagnostic.png"
    fig.savefig(p3, dpi=120); plt.close(fig); print(f"  → {p3.name}")

    # (d) mode_ratio_vs_aef_marginal.png — does mode_ratio independently predict AEF
    # after controlling for envelope?
    # Plot: residuals from fit using only envelope + controls (no mode_ratio), vs mode_ratio.
    X_no_mr = np.column_stack([
        np.ones(len(fw)), env_c, T_c, W_c, RH_c, season_sin, season_cos,
    ])
    fit_no_mr = ols_with_se(X_no_mr, y_all)
    resid_no_mr = fit_no_mr["resid"]
    fig, ax = plt.subplots(figsize=(10.0, 6.0))
    ax.scatter(mr_a[idx_p], resid_no_mr[idx_p], s=2, alpha=0.20, color="#308050", edgecolors="none")
    b1m, b0m = np.polyfit(mr_a, resid_no_mr, 1)
    r_marg, _ = stats.pearsonr(mr_a, resid_no_mr)
    xs_fit = np.linspace(mr_a.min(), mr_a.max(), 50)
    ax.plot(xs_fit, b0m + b1m * xs_fit, color="black", linewidth=1.2,
            label=f"slope={b1m:+.3f}, residual r={r_marg:+.4f}")
    ax.axhline(0, color="black", linewidth=0.4)
    ax.set_xlabel("mode_ratio (Hungary lagna)")
    ax.set_ylabel("PG_corr residual after envelope + controls fit")
    ax.set_title(f"mode_ratio vs PG_corr residual — does mode_ratio independently predict AEF "
                 f"after envelope + controls?\nβ_mode_ratio = {fit['beta'][2]:+.4f}, "
                 f"95% CI = [{mr_ci[0]:+.4f}, {mr_ci[1]:+.4f}], OLS p = {fit['p'][2]:.3g}")
    ax.legend()
    fig.tight_layout()
    p4 = OUT / "mode_ratio_vs_aef_marginal.png"
    fig.savefig(p4, dpi=120); plt.close(fig); print(f"  → {p4.name}")

    # ── synthesis ──────────────────────────────
    write_synthesis(r_pool, ci_pool, p_pool, results, fit, fit_main, inter_ci, mr_ci,
                    delta_r2, overlap, diff, inter_sig, len(fw), len(df),
                    q20, q80, mr.min(), mr.max(), mr.std(),
                    coef_names, time.time() - t0)

    # ── console summary ────────────────────────
    print()
    print("=" * 70)
    print(f"  Hungary AEF (PG_corr), 1962-2009, fair-weather, n={len(fw):,}")
    print("=" * 70)
    print(f"  POOLED  r={r_pool:+.4f}  CI=[{ci_pool[0]:+.3f},{ci_pool[1]:+.3f}]")
    for r in results:
        print(f"  {r['regime']:>20s}  n={r['n']:>7,}  r={r['r']:+.4f}  "
              f"CI=[{r['ci_lo']:+.3f},{r['ci_hi']:+.3f}]")
    print(f"  Top - bottom: {diff:+.4f}  CIs {'OVERLAP' if overlap else 'DO NOT OVERLAP'}")
    print()
    print(f"  Interaction (envelope × mode_ratio):")
    print(f"    β = {fit['beta'][inter_idx]:+.5f}")
    print(f"    OLS t = {fit['t'][inter_idx]:+.2f}, p = {fit['p'][inter_idx]:.3g}")
    print(f"    bootstrap 95% CI = [{inter_ci[0]:+.5f}, {inter_ci[1]:+.5f}]")
    print(f"    {'EXCLUDES' if inter_sig else 'INCLUDES'} zero")
    print(f"  ΔR² (interaction): {delta_r2:+.5f}")
    print()
    print(f"  Mode_ratio main effect (after envelope + controls):")
    print(f"    β = {fit['beta'][2]:+.5f}")
    print(f"    bootstrap 95% CI = [{mr_ci[0]:+.5f}, {mr_ci[1]:+.5f}]")
    mr_sig = (mr_ci[0] > 0) or (mr_ci[1] < 0)
    print(f"    {'EXCLUDES' if mr_sig else 'INCLUDES'} zero")
    print()
    print("  ─── DIRECT M4 vs AEF COMPARISON ───")
    print(f"  M4  interaction β = -0.00475   OLS p = 0.786   ΔR² = 0.000")
    print(f"  AEF interaction β = {fit['beta'][inter_idx]:+.5f}   OLS p = {fit['p'][inter_idx]:.3g}   ΔR² = {delta_r2:+.5f}")
    print(f"\nTotal wall: {time.time() - t0:.1f}s")


def write_synthesis(r_pool, ci_pool, p_pool, results, fit, fit_main, inter_ci, mr_ci,
                    delta_r2, overlap, diff, inter_sig, n_fw, n_raw,
                    q20, q80, mr_min, mr_max, mr_std,
                    coef_names, total_wall):
    inter_idx = 3
    mr_sig = (mr_ci[0] > 0) or (mr_ci[1] < 0)

    md = []
    md.append("# AEF ↔ spring/neap envelope, mode-stratified — SYNTHESIS\n")
    md.append("**Status:** EXPLORATORY. Not pre-registered. Counterpart to the M4")
    md.append("envelope-mode-stratified test (commit 7847576).\n")
    md.append("Date: 2026-05-08\n")

    md.append("## What this is\n")
    md.append("Framework predicts opposite outcomes for two phenomena:")
    md.append("")
    md.append("- **M4** (magnetic-mode rotational/equatorial gravitational tide):")
    md.append("  no mode-coupling. **VERIFIED** in commit 7847576: interaction β = -0.00475,")
    md.append("  OLS p = 0.786, bootstrap CI [-0.022, +0.013], ΔR² = 0.")
    md.append("- **AEF** (dielectric-mode longitudinal/axial atmospheric-electric field):")
    md.append("  mode-coupling SHOULD be present. **THIS test.**")
    md.append("")
    md.append("Same predictor (envelope = |cos(2·sep)|), same statistical approach")
    md.append("(interaction regression with controls + block-bootstrap CI), same family")
    md.append("of plots, for direct comparability.")
    md.append("")

    md.append("## Data\n")
    md.append("- Source: PANGAEA 10.1594/PANGAEA.942036, Hungary Széchenyi István Observatory.")
    md.append("- Lagna: Nagycenk, 47.632°N, 16.718°E.")
    md.append("- Predictand: `pg_corr` (corrected hourly potential gradient, V/m).")
    md.append("- Years: 1962–2009.")
    md.append(f"- Raw rows: {n_raw:,}")
    md.append(f"- After fair-weather filter (precip_era=0, wind_era<8 m/s, RH_era<90%): **{n_fw:,}** rows ({100.0*n_fw/n_raw:.1f}%)")
    md.append("")

    md.append("## Versor decomposition diagnostics\n")
    md.append(f"- mode_ratio at Hungary lagna: range = [{mr_min:.4f}, {mr_max:.4f}], std = {mr_std:.4f}")
    md.append(f"- Quintile cuts (data-driven): q20 = {q20:.4f}, q80 = {q80:.4f}")
    md.append("")

    md.append("## Pooled AEF ↔ envelope correlation\n")
    md.append(f"- r = **{r_pool:+.4f}**, 95% CI = [{ci_pool[0]:+.3f}, {ci_pool[1]:+.3f}], p = {p_pool:.3g}")
    md.append("")

    md.append("## Per-stratum r\n")
    md.append("| Quintile | n | Pearson r | 95% bootstrap CI | raw p |")
    md.append("|---|---:|---:|---|---:|")
    for r in results:
        md.append(f"| {r['regime']} | {r['n']:,} | {r['r']:+.4f} | "
                  f"[{r['ci_lo']:+.3f}, {r['ci_hi']:+.3f}] | {r['p']:.3g} |")
    md.append(f"| **POOLED** | {n_fw:,} | {r_pool:+.4f} | [{ci_pool[0]:+.3f}, {ci_pool[1]:+.3f}] | {p_pool:.3g} |")
    md.append(f"\ntop − bottom = {diff:+.4f}, CIs {'OVERLAP' if overlap else 'DO NOT OVERLAP'}.\n")

    md.append("## Interaction regression\n")
    md.append("    pg_corr = β₀ + β₁·envelope_c + β₂·mode_ratio_c + β₃·envelope_c×mode_ratio_c")
    md.append("            + β₄·T_era_c + β₅·wind_era_c + β₆·RH_era_c + β₇·sin(season) + β₈·cos(season) + ε\n")
    md.append("All non-binary predictors mean-centered. Controls: temperature, wind, humidity")
    md.append("(ERA5 reanalysis), and seasonal harmonics.\n")
    md.append("| Coefficient | β | SE | t | OLS p |")
    md.append("|---|---:|---:|---:|---:|")
    for i, nm in enumerate(coef_names):
        md.append(f"| {nm} | {fit['beta'][i]:+.5f} | {fit['se'][i]:.5f} | {fit['t'][i]:+.2f} | {fit['p'][i]:.3g} |")
    md.append("")
    md.append(f"- R²(full)        = **{fit['r2']:.5f}**")
    md.append(f"- R²(no interaction) = **{fit_main['r2']:.5f}**")
    md.append(f"- ΔR² from interaction = **{delta_r2:+.5f}**")
    md.append(f"- Block-bootstrap 95% CI on interaction β: [{inter_ci[0]:+.5f}, {inter_ci[1]:+.5f}]")
    md.append(f"- Interaction CI {'**EXCLUDES**' if inter_sig else '**INCLUDES**'} zero")
    md.append(f"- Block-bootstrap 95% CI on mode_ratio main β: [{mr_ci[0]:+.5f}, {mr_ci[1]:+.5f}]")
    md.append(f"- mode_ratio main effect CI {'**EXCLUDES**' if mr_sig else '**INCLUDES**'} zero")
    md.append("")

    md.append("## Direct M4 vs AEF comparison\n")
    md.append("Both phenomena tested with identical methodology — interaction regression of")
    md.append("`{predictand} ~ envelope + mode_ratio + envelope·mode_ratio + controls`.")
    md.append("")
    md.append("| Phenomenon | n | interaction β | OLS p | bootstrap 95% CI | ΔR² |")
    md.append("|---|---:|---:|---:|---|---:|")
    md.append(f"| **M4** (SF tide range, 1973-2024) | 448,670 | -0.00475 | 0.786 | [-0.022, +0.013] | 0.00000 |")
    md.append(f"| **AEF** (Hungary PG, 1962-2009)    | {n_fw:,} | {fit['beta'][inter_idx]:+.5f} | {fit['p'][inter_idx]:.3g} | [{inter_ci[0]:+.5f}, {inter_ci[1]:+.5f}] | {delta_r2:+.5f} |")
    md.append("")

    md.append("## Honest interpretation\n")
    if inter_sig:
        md.append("The AEF interaction term is **statistically distinguishable from zero**")
        md.append(f"(β = {fit['beta'][inter_idx]:+.5f}, bootstrap CI {inter_ci[0]:+.5f} to {inter_ci[1]:+.5f}).")
        md.append("Combined with the M4 negative result, **the framework prediction of")
        md.append("differential mode-coupling between magnetic-side (M4) and")
        md.append("dielectric-side (AEF) phenomena is supported by the data.**")
        if delta_r2 < 0.001:
            md.append(f"")
            md.append(f"However ΔR² = {delta_r2:.5f} is small in absolute terms — the")
            md.append("interaction adds little explanatory power compared to main effects")
            md.append("plus controls. The coupling exists but is weak relative to known")
            md.append("meteorological drivers.")
    else:
        md.append("The AEF interaction term is **NOT statistically distinguishable from zero**")
        md.append(f"(β = {fit['beta'][inter_idx]:+.5f}, bootstrap CI {inter_ci[0]:+.5f} to {inter_ci[1]:+.5f}).")
        md.append("Combined with the M4 negative result, **the framework prediction of")
        md.append("differential mode-coupling between magnetic-side (M4) and dielectric-")
        md.append("side (AEF) phenomena is NOT supported by the data**: both phenomena show")
        md.append("a null interaction.")
    md.append("")
    if mr_sig:
        md.append(f"The mode_ratio main effect IS statistically distinguishable from zero")
        md.append(f"(β = {fit['beta'][2]:+.5f}, bootstrap CI {mr_ci[0]:+.5f} to {mr_ci[1]:+.5f}).")
        md.append("This indicates mode_ratio independently predicts AEF after controlling")
        md.append("for envelope and meteorology — a positive finding for dielectric-mode")
        md.append("coupling at the main-effects level even if the moderation hypothesis")
        md.append("doesn't hold.")
    else:
        md.append(f"The mode_ratio main effect is also not distinguishable from zero")
        md.append(f"(β = {fit['beta'][2]:+.5f}, bootstrap CI {mr_ci[0]:+.5f} to {mr_ci[1]:+.5f}).")
        md.append("mode_ratio does not independently predict AEF after controlling for")
        md.append("envelope and meteorology.")
    md.append("")

    md.append("## Plots\n")
    md.append("- `aef_vs_envelope_pooled.png` — basic envelope predictor.")
    md.append("- `aef_vs_envelope_by_mode_quintile.png` — three panels stratified.")
    md.append("- `interaction_regression_AEF_diagnostic.png` — residuals after")
    md.append("  main-effects+controls, by mode_ratio.")
    md.append("- `mode_ratio_vs_aef_marginal.png` — does mode_ratio independently")
    md.append("  predict AEF after controlling for envelope?")
    md.append("")

    md.append("## Caveats\n")
    md.append("- Single-window exploratory test; not pre-registered.")
    md.append("- Quintile cuts data-driven (post hoc), not locked.")
    md.append("- Hungary lagna is the geographic location of the gauge — same lagna")
    md.append("  position used for stratification variable and predictand.")
    md.append("- Fair-weather filter is a literature-standard choice but other")
    md.append("  filter formulations (stricter wind, RH<70, exclude sunrise/sunset, etc.)")
    md.append("  give different sample sizes. Sensitivity to filter choice not yet tested.")
    md.append("- AEF tree-shielding correction is itself uncertain (PANGAEA documents")
    md.append("  this; uncertainty column is in the data). Using `pg_corr` per dataset")
    md.append("  recommendation; a sensitivity check on `pg_uncorr` could show whether")
    md.append("  the correction influences the interaction.")
    md.append(f"\n*Total wall: {total_wall:.1f}s*")

    p = OUT / "SYNTHESIS.md"
    p.write_text("\n".join(md))


if __name__ == "__main__":
    main()
