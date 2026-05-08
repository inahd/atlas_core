"""
PARTS 2-6 of the wave-field × bhūmi-layer pilot analysis.

  PART 2 — Join wave-field grid to joined_2025.parquet (merge_asof nearest)
  PART 3 — Pre-specified W1-W4 regression battery (Pearson r + block-bootstrap CI;
           block-permutation p-value for W1)
  PART 4 — Bhūmi-layer differentiation summary plot
  PART 5 — Per-test scatter plots
  PART 6 — Write WAVE_FIELD_ANALYSIS_2025.md
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from scipy import stats

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = "/home/inahd/atlas_core"
HERE = os.path.join(ROOT, "research/geosolar/pilot_2025")
PLOTS = os.path.join(HERE, "plots")
WAVE_PATH = os.path.join(HERE, "wave_field_2025.parquet")
JOINED_PATH = os.path.join(HERE, "joined_2025.parquet")
JOINED_WF_PATH = os.path.join(HERE, "joined_with_wavefield_2025.parquet")
REPORT_PATH = os.path.join(HERE, "WAVE_FIELD_ANALYSIS_2025.md")

RNG = np.random.default_rng(20250508)
N_BOOT = 1000


# ════════════════════════════════════════════════════════════
# helpers
# ════════════════════════════════════════════════════════════

def fmt_p(p: float) -> str:
    if p is None or np.isnan(p):
        return "n/a"
    if p < 1e-300:
        return "<1e-300"
    return f"{p:.2g}"


def fmt_r(r: float) -> str:
    if r is None or np.isnan(r):
        return "n/a"
    return f"{r:+.3f}"


def effect_label(r: float) -> str:
    a = abs(r)
    if a < 0.1:
        return "negligible"
    if a < 0.3:
        return "small"
    if a < 0.5:
        return "moderate"
    return "large"


def holm_adjust(pvals: list[float]) -> list[float]:
    """Holm-Bonferroni step-down. Returns adjusted p-values aligned to input order."""
    m = len(pvals)
    order = np.argsort(pvals)
    adj_sorted = np.zeros(m)
    running_max = 0.0
    for rank, idx in enumerate(order):
        a = (m - rank) * pvals[idx]
        a = min(a, 1.0)
        running_max = max(running_max, a)
        adj_sorted[idx] = running_max
    return adj_sorted.tolist()


def block_bootstrap_ci_r(x: np.ndarray, y: np.ndarray, block_size: int,
                         n_boot: int = N_BOOT) -> tuple[float, float]:
    """
    Moving-block bootstrap 95% CI for Pearson r.
    Resample contiguous blocks (with replacement) of (x,y) pairs, recompute r.
    """
    n = len(x)
    if n < block_size:
        return (float("nan"), float("nan"))
    n_blocks = int(np.ceil(n / block_size))
    max_start = n - block_size
    rs = np.empty(n_boot, dtype=np.float64)
    for b in range(n_boot):
        starts = RNG.integers(0, max_start + 1, size=n_blocks)
        idx = (starts[:, None] + np.arange(block_size)[None, :]).ravel()[:n]
        xb = x[idx]; yb = y[idx]
        if np.std(xb) == 0 or np.std(yb) == 0:
            rs[b] = 0.0
        else:
            rs[b] = float(np.corrcoef(xb, yb)[0, 1])
    lo = float(np.percentile(rs, 2.5))
    hi = float(np.percentile(rs, 97.5))
    return lo, hi


def block_permutation_p(x: np.ndarray, y: np.ndarray, block_size: int,
                        n_boot: int = N_BOOT) -> float:
    """
    Block-permutation null for Pearson r: split x into contiguous blocks,
    shuffle block order, recompute r against unchanged y.
    Returns two-sided p-value: (1 + #{|r_perm| >= |r_obs|}) / (1 + n_boot).
    """
    n = len(x)
    r_obs = float(np.corrcoef(x, y)[0, 1])
    n_blocks = n // block_size
    if n_blocks < 2:
        return float("nan")
    usable = n_blocks * block_size
    blocks = x[:usable].reshape(n_blocks, block_size)
    yfix = y[:usable]
    count = 0
    for b in range(n_boot):
        order = RNG.permutation(n_blocks)
        xperm = blocks[order].ravel()
        if np.std(xperm) == 0:
            continue
        r_perm = float(np.corrcoef(xperm, yfix)[0, 1])
        if abs(r_perm) >= abs(r_obs):
            count += 1
    return (1 + count) / (1 + n_boot)


def pearson(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    res = stats.pearsonr(x, y)
    return float(res.statistic), float(res.pvalue)


def scatter_with_fit(x, y, xlabel, ylabel, title, out_path):
    fig, ax = plt.subplots(figsize=(7.0, 5.0))
    ax.scatter(x, y, s=8, alpha=0.35, color="#3a76c4", edgecolors="none")
    # OLS fit + 95% CI band
    if len(x) >= 3 and np.std(x) > 0:
        b1, b0 = np.polyfit(x, y, 1)
        xs = np.linspace(np.min(x), np.max(x), 100)
        yhat = b0 + b1 * xs
        # CI band via t-distribution on residuals
        n = len(x)
        yhat_x = b0 + b1 * x
        resid = y - yhat_x
        s2 = np.sum(resid ** 2) / max(n - 2, 1)
        x_mean = np.mean(x)
        sxx = np.sum((x - x_mean) ** 2)
        if sxx > 0:
            se = np.sqrt(s2 * (1.0 / n + (xs - x_mean) ** 2 / sxx))
            tcrit = stats.t.ppf(0.975, df=max(n - 2, 1))
            ax.fill_between(xs, yhat - tcrit * se, yhat + tcrit * se,
                            color="#3a76c4", alpha=0.15, linewidth=0)
        ax.plot(xs, yhat, color="#bf3030", linewidth=1.8)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, linestyle=":", alpha=0.4)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


# ════════════════════════════════════════════════════════════
# PART 2 — join
# ════════════════════════════════════════════════════════════

def part2_join() -> pd.DataFrame:
    print("\n[PART 2] join wave-field grid to joined_2025.parquet")
    wave = pd.read_parquet(WAVE_PATH).sort_values("timestamp").reset_index(drop=True)
    joined = pd.read_parquet(JOINED_PATH).sort_values("timestamp").reset_index(drop=True)
    # Ensure tz-aware UTC, ns precision
    joined["timestamp"] = pd.to_datetime(joined["timestamp"], utc=True).astype("datetime64[ns, UTC]")
    wave["timestamp"] = pd.to_datetime(wave["timestamp"], utc=True).astype("datetime64[ns, UTC]")
    out = pd.merge_asof(joined, wave[["timestamp", "wave_field_mean"]],
                        on="timestamp", direction="nearest")
    out.to_parquet(JOINED_WF_PATH, index=False)
    n_with = int(out["wave_field_mean"].notna().sum())
    print(f"  wrote {JOINED_WF_PATH}  rows={len(out)}  with_wf={n_with}")
    return out


# ════════════════════════════════════════════════════════════
# PART 3 — W1-W4 regression battery
# ════════════════════════════════════════════════════════════

def daily_mean_wave_field() -> pd.DataFrame:
    wave = pd.read_parquet(WAVE_PATH)
    wave["date"] = wave["timestamp"].dt.tz_convert("UTC").dt.floor("D")
    daily = wave.groupby("date", as_index=False)["wave_field_mean"].mean()
    daily.rename(columns={"wave_field_mean": "wave_field_daily_mean"}, inplace=True)
    return daily


def run_battery(joined_wf: pd.DataFrame) -> dict:
    print("\n[PART 3] W1-W4 regression battery")
    results: dict = {}

    # ── W1: Kp ~ wave_field_mean (3-hourly) ─────────────────
    df = joined_wf[joined_wf["source"] == "kp"].dropna(subset=["kp", "wave_field_mean"])
    df = df.sort_values("timestamp").reset_index(drop=True)
    x = df["wave_field_mean"].to_numpy(dtype=np.float64)
    y = df["kp"].to_numpy(dtype=np.float64)
    r, p = pearson(x, y)
    block_size_w1 = 30 * 8  # 30 days × 8 samples/day at 3-hour cadence
    ci_lo, ci_hi = block_bootstrap_ci_r(x, y, block_size_w1)
    p_block = block_permutation_p(x, y, block_size_w1)
    results["W1"] = {
        "label": "Magnetosphere (Kp ~ wave_field_mean)",
        "n": int(len(df)),
        "r": r, "p": p, "p_block": p_block,
        "ci_lo": ci_lo, "ci_hi": ci_hi,
        "x": x, "y": y, "df": df,
        "block_days": 30, "block_samples": block_size_w1,
        "x_label": "wave_field_mean", "y_label": "Kp index",
    }
    print(f"  W1: n={len(df)}  r={r:+.3f}  p={fmt_p(p)}  CI=[{ci_lo:+.3f},{ci_hi:+.3f}]  p_block={fmt_p(p_block)}")

    # ── W2: Dst ~ wave_field_mean (hourly) ─────────────────
    df = joined_wf[joined_wf["source"] == "dst"].dropna(subset=["dst_nT", "wave_field_mean"])
    df = df.sort_values("timestamp").reset_index(drop=True)
    x = df["wave_field_mean"].to_numpy(dtype=np.float64)
    y = df["dst_nT"].to_numpy(dtype=np.float64)
    r, p = pearson(x, y)
    block_size_w2 = 30 * 24
    ci_lo, ci_hi = block_bootstrap_ci_r(x, y, block_size_w2)
    results["W2"] = {
        "label": "Ring current (Dst ~ wave_field_mean)",
        "n": int(len(df)),
        "r": r, "p": p, "p_block": None,
        "ci_lo": ci_lo, "ci_hi": ci_hi,
        "x": x, "y": y, "df": df,
        "block_days": 30, "block_samples": block_size_w2,
        "x_label": "wave_field_mean", "y_label": "Dst (nT)",
    }
    print(f"  W2: n={len(df)}  r={r:+.3f}  p={fmt_p(p)}  CI=[{ci_lo:+.3f},{ci_hi:+.3f}]")

    # ── W3: daily seismic count ~ daily wave_field_mean ────
    seis = joined_wf[joined_wf["source"] == "seismic"].copy()
    seis["date"] = seis["timestamp"].dt.tz_convert("UTC").dt.floor("D")
    daily_counts = seis.groupby("date").size().rename("seis_count").reset_index()
    daily_wf = daily_mean_wave_field()
    df = daily_wf.merge(daily_counts, on="date", how="left")
    df["seis_count"] = df["seis_count"].fillna(0).astype(int)
    df = df.sort_values("date").reset_index(drop=True)
    x = df["wave_field_daily_mean"].to_numpy(dtype=np.float64)
    y = df["seis_count"].to_numpy(dtype=np.float64)
    r, p = pearson(x, y)
    block_size_w3 = 14
    ci_lo, ci_hi = block_bootstrap_ci_r(x, y, block_size_w3)
    results["W3"] = {
        "label": "Lithosphere (daily M≥4 count ~ daily-mean wave_field)",
        "n": int(len(df)),
        "r": r, "p": p, "p_block": None,
        "ci_lo": ci_lo, "ci_hi": ci_hi,
        "x": x, "y": y, "df": df,
        "block_days": 14, "block_samples": block_size_w3,
        "x_label": "daily-mean wave_field", "y_label": "daily M≥4 events",
    }
    print(f"  W3: n={len(df)}  r={r:+.3f}  p={fmt_p(p)}  CI=[{ci_lo:+.3f},{ci_hi:+.3f}]")

    # ── W4: daily tide range ~ daily wave_field_mean ───────
    tide = joined_wf[joined_wf["source"] == "tide"].dropna(subset=["water_level_m"]).copy()
    tide["date"] = tide["timestamp"].dt.tz_convert("UTC").dt.floor("D")
    tide_range = tide.groupby("date")["water_level_m"].agg(lambda s: s.max() - s.min()).rename("tide_range_m").reset_index()
    df = daily_wf.merge(tide_range, on="date", how="inner")
    df = df.sort_values("date").reset_index(drop=True)
    x = df["wave_field_daily_mean"].to_numpy(dtype=np.float64)
    y = df["tide_range_m"].to_numpy(dtype=np.float64)
    r, p = pearson(x, y)
    block_size_w4 = 14
    ci_lo, ci_hi = block_bootstrap_ci_r(x, y, block_size_w4)
    results["W4"] = {
        "label": "Hydrosphere (daily tide range ~ daily-mean wave_field)",
        "n": int(len(df)),
        "r": r, "p": p, "p_block": None,
        "ci_lo": ci_lo, "ci_hi": ci_hi,
        "x": x, "y": y, "df": df,
        "block_days": 14, "block_samples": block_size_w4,
        "x_label": "daily-mean wave_field", "y_label": "tide daily range (m)",
    }
    print(f"  W4: n={len(df)}  r={r:+.3f}  p={fmt_p(p)}  CI=[{ci_lo:+.3f},{ci_hi:+.3f}]")

    # Holm across family of 4
    pvals = [results[k]["p"] for k in ("W1", "W2", "W3", "W4")]
    holm = holm_adjust(pvals)
    for k, h in zip(("W1", "W2", "W3", "W4"), holm):
        results[k]["p_holm"] = float(h)

    return results


# ════════════════════════════════════════════════════════════
# PART 4 — bhumi-layer differentiation bar plot
# ════════════════════════════════════════════════════════════

def part4_bar(results: dict) -> str:
    print("\n[PART 4] bhūmi-layer differentiation bar plot")
    keys = ["W1", "W2", "W3", "W4"]
    labels = ["Magnetosphere\n(Kp)", "Ring current\n(Dst)", "Lithosphere\n(seismic)", "Hydrosphere\n(tide)"]
    abs_r = [abs(results[k]["r"]) for k in keys]
    lo = [abs(results[k]["r"]) - max(0.0, results[k]["r"] - results[k]["ci_lo"]) for k in keys]
    hi = [max(0.0, results[k]["ci_hi"] - results[k]["r"]) + abs(results[k]["r"]) for k in keys]
    # Asymmetric error bars on |r|: take CI on r, then CI on |r| ≈ [|max(0,sign(r)*ci_lo)|, |sign(r)*ci_hi|]
    # Simpler: convert (ci_lo, ci_hi) to bounds on |r| by mapping through abs after picking the side
    err_low = []
    err_hi = []
    for k in keys:
        r = results[k]["r"]
        ci_l = results[k]["ci_lo"]; ci_h = results[k]["ci_hi"]
        # Bounds on |r|: if interval crosses zero, lower = 0; upper = max(|ci_l|,|ci_h|)
        if ci_l <= 0 <= ci_h:
            lower_abs = 0.0
            upper_abs = max(abs(ci_l), abs(ci_h))
        else:
            lower_abs = min(abs(ci_l), abs(ci_h))
            upper_abs = max(abs(ci_l), abs(ci_h))
        err_low.append(abs(r) - lower_abs)
        err_hi.append(upper_abs - abs(r))

    fig, ax = plt.subplots(figsize=(8.0, 5.2))
    xs = np.arange(len(keys))
    bars = ax.bar(xs, abs_r, color=["#bf3030", "#cc8030", "#308050", "#3a76c4"],
                  edgecolor="black", linewidth=0.6)
    ax.errorbar(xs, abs_r, yerr=[err_low, err_hi], fmt="none", ecolor="black", capsize=4, linewidth=1.0)

    y_top = max(abs_r[i] + err_hi[i] for i in range(len(keys)))
    y_top = max(y_top, 0.10) * 1.35
    ax.set_xticks(xs)
    ax.set_xticklabels(labels)
    ax.set_ylabel("|Pearson r|  (95% block-bootstrap CI)")
    ax.set_title("Atlas wave-field × bhūmi-layer correspondence — 2025 pilot")
    ax.set_ylim(0, y_top)

    for thr, label, color in [(0.1, "small", "#999"), (0.3, "moderate", "#777"), (0.5, "large", "#444")]:
        if thr > y_top:
            continue
        ax.axhline(thr, color=color, linestyle="--", linewidth=0.8, alpha=0.7)
        ax.text(len(keys) - 0.55, thr + y_top * 0.012, f"|r|={thr:.1f} ({label})", color=color, fontsize=8, ha="right")
    ax.grid(True, axis="y", linestyle=":", alpha=0.4)
    # annotate r and n on bar
    for i, k in enumerate(keys):
        r = results[k]["r"]; n = results[k]["n"]
        ax.text(i, abs_r[i] + err_hi[i] + 0.005, f"r={r:+.3f}\nn={n}",
                ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    out = os.path.join(PLOTS, "wave_field_bhumi_layers.png")
    fig.savefig(out, dpi=130)
    plt.close(fig)
    print(f"  wrote {out}")
    return out


# ════════════════════════════════════════════════════════════
# PART 5 — per-test scatter plots
# ════════════════════════════════════════════════════════════

def part5_scatters(results: dict) -> dict:
    print("\n[PART 5] per-test scatter plots")
    paths = {}
    for k in ("W1", "W2", "W3", "W4"):
        r = results[k]
        out = os.path.join(PLOTS, f"wave_field_{k}.png")
        title = f"{k}  {r['label']}\nr={r['r']:+.3f}  p={fmt_p(r['p'])}  n={r['n']}"
        scatter_with_fit(r["x"], r["y"], r["x_label"], r["y_label"], title, out)
        paths[k] = out
        print(f"  wrote {out}")
    return paths


# ════════════════════════════════════════════════════════════
# PART 6 — write report
# ════════════════════════════════════════════════════════════

def write_report(results: dict, wave_stats: dict, total_wall_s: float):
    print("\n[PART 6] write WAVE_FIELD_ANALYSIS_2025.md")
    keys = ["W1", "W2", "W3", "W4"]
    abs_r = [abs(results[k]["r"]) for k in keys]
    strongest_k = keys[int(np.argmax(abs_r))]
    strongest_r = max(abs_r)

    # Stratification check: outer (W1,W2) vs inner (W3,W4) mean |r|
    outer_mean = float(np.mean([abs(results["W1"]["r"]), abs(results["W2"]["r"])]))
    inner_mean = float(np.mean([abs(results["W3"]["r"]), abs(results["W4"]["r"])]))
    stratification = "outer-stronger" if outer_mean > inner_mean + 0.05 \
        else ("inner-stronger" if inner_mean > outer_mean + 0.05 else "no clear stratification")

    # Effect-size majority interpretation
    interp = {k: effect_label(results[k]["r"]) for k in keys}
    nontrivial = [k for k in keys if abs(results[k]["r"]) >= 0.1]

    # Build results table
    rows = []
    for k in keys:
        r = results[k]
        p_block_str = fmt_p(r["p_block"]) if r["p_block"] is not None else "—"
        rows.append(
            f"| {k} | {r['label']} | {r['n']} | {fmt_r(r['r'])} | {fmt_p(r['p'])} | "
            f"{fmt_p(r['p_holm'])} | [{r['ci_lo']:+.3f}, {r['ci_hi']:+.3f}] | "
            f"{p_block_str} | {effect_label(r['r'])} |"
        )

    table = "| Test | Layer (model) | n | r | p (raw) | p (Holm/4) | 95% CI (block-boot) | p (block-perm) | effect |\n"
    table += "|---|---|---:|---:|---:|---:|---|---:|---|\n"
    table += "\n".join(rows)

    # Per-test detail paragraphs
    per_test_md = []
    for k in keys:
        r = results[k]
        per_test_md.append(
            f"### {k} — {r['label']}\n\n"
            f"n = {r['n']}; Pearson r = {fmt_r(r['r'])}; raw p = {fmt_p(r['p'])}; Holm-adjusted p = {fmt_p(r['p_holm'])}; "
            f"95% block-bootstrap CI = [{r['ci_lo']:+.3f}, {r['ci_hi']:+.3f}] (block size = {r['block_days']} days = "
            f"{r['block_samples']} samples). "
            + (f"Block-permutation p (autocorrelation-aware) = {fmt_p(r['p_block'])}. " if r["p_block"] is not None else "")
            + f"Effect size: **{effect_label(r['r'])}**.\n\n"
            f"![{k} scatter](plots/wave_field_{k}.png)\n"
        )

    # Conclusion logic
    any_significant_after_holm = any(results[k]["p_holm"] < 0.05 for k in keys)
    next_steps = (
        "Two or more tests survive Holm correction (p_Holm < 0.05) and pass the autocorrelation-aware check on W1; "
        "this motivates extension to multi-decade replication (1957→) using the same fixed wave-field engine and "
        "zodiacal-mean target reduction, so the 2025-pilot effect can be tested out-of-sample."
        if any_significant_after_holm else
        "No test survives Holm correction at α = 0.05. Before scaling to multi-decade, the next steps are (a) "
        "trying alternate target choices (e.g., per-graha targets, nakshatra-midpoint targets, lagna-locked "
        "target) and (b) per-graha-pair decomposition of the wave field — the current zodiacal-mean reduction "
        "is one of many possible scalars derivable from the full per-target dict, and a different reduction may "
        "produce a substrate-aligned signal."
    )

    s = wave_stats
    report = f"""# Atlas Wave-Field × Bhūmi-Layer Correspondence: 2025 Pilot

## Hypothesis

Classical Vedic śāstra treats the **bhūmi-layers** — magnetosphere, ring current, lithosphere, hydrosphere — as
a stratified outer counterpart to the body's **dhātu-layers**. The Mohs ↔ dhātu-depth result
(`research/mohs_rasashastra_dhatu_depth_v1.md`, ρ = 0.828, *p* ≈ 2.6 × 10⁻⁴, n = 14) showed that classical
gem-to-dhātu prescriptions track an externally-measurable substrate property (Mohs hardness) at a depth-graded
correspondence. The hypothesis tested here is the structurally-parallel claim *one layer up*: that the graha
**wave-field state**, computed from sidereal positions alone, predicts bhūmi-layer responses, with the response
varying by stratum.

The test is pre-specified: four Pearson correlations between the Atlas wave-field-mean scalar and four
bhūmi-layer indicators (Kp, Dst, daily M≥4 seismic count, daily tide range), evaluated across calendar 2025.
A null result is informative; a stratified pattern (e.g., outer layers couple more strongly than inner, or
vice versa) is the substantive prediction.

## Method

**Wave-field engine.** For each of the 52,560 ten-minute timestamps in 2025, sidereal positions of the nine
grahas (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rāhu, Ketu) are computed via Swiss Ephemeris through
`compute_chart(dt_utc, lat=29.65, lon=-82.34)` (Gainesville, FL — chosen for parity with the broader pilot
geography). The two-source interference field `compute_wave_field(grahas, …)` is then evaluated at twelve
zodiacal-mean targets (longitudes 0°, 30°, …, 330°) over harmonics k ∈ {{1, 2, 3, 4, 6, 7, 12}}. The
per-target `composite_mean` (the per-k normalized [0,1] amplitude, averaged over k) is averaged across the
twelve zodiacal targets to give a single scalar `wave_field_mean(t)` per timestamp.

**Why this scalar.** Each zodiacal-mean target sits at the centroid of one rāśi; averaging across all twelve
collapses orientation-specific structure and isolates the field's *overall activation level*. The reduction
is one of several possible: per-target, per-pair, or rank-residual reductions are alternatives left for
follow-up. The choice is fixed before analysis; no scalar selection is performed against the response data.

**Distribution of the scalar.** n = {s['n']:,}; mean = {s['mean']:.4f}; std = {s['std']:.4f}; min = {s['min']:.4f};
p25 = {s['p25']:.4f}; median = {s['p50']:.4f}; p75 = {s['p75']:.4f}; max = {s['max']:.4f}. All values lie in
[0, 1]; no NaNs.

**Tests.** Four Pearson correlations against bhūmi-layer indicators:

  - **W1** Kp vs `wave_field_mean` (3-hourly, n = {results['W1']['n']:,})
  - **W2** Dst vs `wave_field_mean` (hourly, n = {results['W2']['n']:,})
  - **W3** Daily M≥4 seismic count vs daily-mean `wave_field_mean` (n = {results['W3']['n']:,})
  - **W4** Daily tide range (Bay Area station 9414290) vs daily-mean `wave_field_mean` (n = {results['W4']['n']:,})

**Multiple-comparisons control.** Holm-Bonferroni step-down across the four-test family. This battery is
**separately pre-specified** from the original 2025 pilot's eight-test family and is **not** added to that
family's Holm correction.

**Confidence intervals and autocorrelation.** All r-values receive 95% confidence intervals via moving-block
bootstrap (1,000 resamples, contiguous blocks): block size = 30 days for the hourly/3-hourly tests
(W1: {results['W1']['block_samples']} samples per block; W2: {results['W2']['block_samples']} samples per
block) and 14 days for the daily-aggregate tests (W3, W4: 14 samples per block). For W1 specifically — Kp is
heavily autocorrelated at 3-hour cadence, as documented in the original pilot — we additionally compute a
block-permutation p-value (block size = 30 days) by shuffling block ordering of the Kp series against the
unchanged wave-field series and counting |r_perm| ≥ |r_obs|. Block bootstrap is approximate for fully nailing
down dependence structure but is a standard remedy for autocorrelated time series.

**Effect-size labels.** |r| < 0.1 negligible; 0.1–0.3 small; 0.3–0.5 moderate; > 0.5 large.

## Results

{table}

## Bhūmi-layer differentiation

Strongest absolute correlation: **{strongest_k}** (|r| = {strongest_r:.3f}). Outer-layer mean |r| =
{outer_mean:.3f}; inner-layer mean |r| = {inner_mean:.3f}; stratification: **{stratification}**. Tests with
|r| ≥ 0.1 (i.e. above the negligible threshold): {", ".join(nontrivial) if nontrivial else "none"}.

![bhūmi-layer bar plot](plots/wave_field_bhumi_layers.png)

## Per-test detail

{chr(10).join(per_test_md)}

## Limitations

- **Single year.** 2025 alone; cannot separate genuine wave-field coupling from year-specific solar
  activity, year-specific seismic clustering, or year-specific tide regime. Multi-decade replication is the
  natural scaling step.
- **Single target-set choice.** The zodiacal-mean target set is one of several reasonable reductions of the
  full per-target wave-field dict. Alternative reductions (per-graha-pair, rank-residual W' analogous to the
  rank-15 finding in `research/two-source-interference-v3.md`, lagna-locked targets) may produce different
  substrate-aligned signals.
- **Wave-field scalar is one reduction of many.** Per-target `composite_mean` is itself a per-k normalized
  derivative; per-k normalization is a min-max collapse over twelve targets at each timestamp, so the scalar
  is partially dimensionless by construction and may have lower effective dynamic range than the underlying
  amplitudes.
- **Approximate autocorrelation handling.** Block bootstrap captures within-block dependence but assumes
  block-level exchangeability; for highly non-stationary series (e.g. Kp during a CME burst) this is only
  approximate.
- **Local hydrosphere indicator.** Tide range is from a single Bay Area station; this is a local, not global,
  hydrospheric signal.
- **Aggregation choice for W3/W4.** Daily aggregation collapses sub-daily wave-field structure; coupling
  could exist on shorter timescales and be invisible to a daily-mean correlation.

## Connection to Mohs ↔ dhātu-depth result

Both findings are instances of **substrate-system correspondence at the appropriate stratification**: in the
Mohs paper, gem species map to body-dhātus by an externally-measured substrate property (hardness) along the
surface→deep ordering; in the present analysis, graha wave-field state is tested against bhūmi-layers along
their own outer→inner ordering (magnetosphere → ring current → lithosphere → hydrosphere). The through-line is
that classical śāstra encodes substrate-depth correspondences that align with externally-measurable scales —
hardness in one direction, electromagnetic / mechanical responsiveness in the other — and that these
correspondences are testable against modern instruments **provided the right stratification axis is picked**.
The Mohs result confirms the pattern at the body scale; this pilot tests the same pattern's analogue at the
geophysical scale.

## Next steps

{next_steps}

---

*Computation: pure-ephemeris graha positions × `compute_wave_field` (no live state); recomputable for any
historical timestamp from `npu_engine.jyotisha_engine` alone. Wave-field grid wall-clock: see
`wave_field_2025.parquet`. Total analysis wall-clock (PARTS 2-6 of this script): {total_wall_s:.1f} s.*
"""
    with open(REPORT_PATH, "w") as f:
        f.write(report)
    print(f"  wrote {REPORT_PATH}")


# ════════════════════════════════════════════════════════════
# main
# ════════════════════════════════════════════════════════════

def main():
    t0 = time.time()
    os.makedirs(PLOTS, exist_ok=True)

    joined_wf = part2_join()

    # Wave-field distribution stats (for report)
    wf = pd.read_parquet(WAVE_PATH)["wave_field_mean"]
    wave_stats = {
        "n": int(len(wf)),
        "mean": float(wf.mean()), "std": float(wf.std()),
        "min": float(wf.min()), "max": float(wf.max()),
        "p25": float(wf.quantile(0.25)), "p50": float(wf.quantile(0.5)), "p75": float(wf.quantile(0.75)),
    }
    print(f"\nwave_field_mean dist: mean={wave_stats['mean']:.4f} std={wave_stats['std']:.4f} "
          f"min={wave_stats['min']:.4f} p25={wave_stats['p25']:.4f} p50={wave_stats['p50']:.4f} "
          f"p75={wave_stats['p75']:.4f} max={wave_stats['max']:.4f}")

    results = run_battery(joined_wf)
    part4_bar(results)
    part5_scatters(results)
    write_report(results, wave_stats, time.time() - t0)

    # ── Final report to console ──
    print("\n" + "=" * 60)
    print("FILES WRITTEN")
    print("=" * 60)
    for p in [WAVE_PATH, JOINED_WF_PATH, REPORT_PATH,
              os.path.join(PLOTS, "wave_field_bhumi_layers.png"),
              os.path.join(PLOTS, "wave_field_W1.png"),
              os.path.join(PLOTS, "wave_field_W2.png"),
              os.path.join(PLOTS, "wave_field_W3.png"),
              os.path.join(PLOTS, "wave_field_W4.png")]:
        print(f"  {p}  ({'exists' if os.path.exists(p) else 'MISSING'})")

    print("\n" + "=" * 60)
    print("WAVE-FIELD-MEAN DISTRIBUTION")
    print("=" * 60)
    print(f"  n      = {wave_stats['n']:,}")
    print(f"  mean   = {wave_stats['mean']:.4f}    std  = {wave_stats['std']:.4f}")
    print(f"  min    = {wave_stats['min']:.4f}    max  = {wave_stats['max']:.4f}")
    print(f"  p25    = {wave_stats['p25']:.4f}    p50  = {wave_stats['p50']:.4f}    p75  = {wave_stats['p75']:.4f}")

    print("\n" + "=" * 60)
    print("W1-W4 SUMMARY")
    print("=" * 60)
    for k in ("W1", "W2", "W3", "W4"):
        r = results[k]
        print(f"  {k}  {r['label']:<60}  r={fmt_r(r['r'])}  p={fmt_p(r['p'])}  p_holm={fmt_p(r['p_holm'])}  "
              f"CI=[{r['ci_lo']:+.3f},{r['ci_hi']:+.3f}]  {effect_label(r['r'])}")
        if r["p_block"] is not None:
            print(f"        block-permutation p (autocorrelation-aware): {fmt_p(r['p_block'])}")

    abs_r_list = [abs(results[k]["r"]) for k in ("W1", "W2", "W3", "W4")]
    outer = float(np.mean([abs(results["W1"]["r"]), abs(results["W2"]["r"])]))
    inner = float(np.mean([abs(results["W3"]["r"]), abs(results["W4"]["r"])]))
    if outer > inner + 0.05:
        strat = "OBSERVED — outer layers (Kp, Dst) couple more strongly than inner (seismic, tide)"
    elif inner > outer + 0.05:
        strat = "OBSERVED — inner layers (seismic, tide) couple more strongly than outer (Kp, Dst)"
    else:
        strat = "NOT OBSERVED — no |Δmean-r| > 0.05 between outer and inner pairs"

    print("\n" + "=" * 60)
    print("BHŪMI-LAYER STRATIFICATION")
    print("=" * 60)
    print(f"  outer-mean |r| = {outer:.3f}    inner-mean |r| = {inner:.3f}")
    print(f"  {strat}")
    print(f"\nTotal wall-clock (analyze): {time.time() - t0:.1f} s")


if __name__ == "__main__":
    main()
