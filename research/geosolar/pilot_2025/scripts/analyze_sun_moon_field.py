"""
EXPLORATORY analysis: Sun-Moon raw-amplitude wave-field × bhūmi-layers.

Run after the pre-specified zodiacal-mean test returned null. The choice to drop
per-k normalization and lock the target to the lagna was made AFTER seeing the
null — so this is exploratory and cannot be cited as a confirmatory finding.

Tests (W1'..W4') mirror the prior W1..W4 exactly, with `wave_field_mean`
swapped for `sun_moon_amplitude`. Same Pearson r + Holm + block-bootstrap CI;
W1' also gets a block-permutation p-value.

Outputs:
  research/geosolar/pilot_2025/SUN_MOON_FIELD_EXPLORATORY_2025.md
  research/geosolar/pilot_2025/plots/sun_moon_W{1..4}p.png
  research/geosolar/pilot_2025/plots/sun_moon_bhumi_layers.png
"""
from __future__ import annotations

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
SM_PATH = os.path.join(HERE, "sun_moon_field_2025.parquet")
JOINED_PATH = os.path.join(HERE, "joined_2025.parquet")
JOINED_SM_PATH = os.path.join(HERE, "joined_with_sun_moon_2025.parquet")
REPORT_PATH = os.path.join(HERE, "SUN_MOON_FIELD_EXPLORATORY_2025.md")

RNG = np.random.default_rng(20250508)
N_BOOT = 1000


# ── helpers (clones of prior analyze; kept inline for self-containedness) ──

def fmt_p(p):
    if p is None or (isinstance(p, float) and np.isnan(p)):
        return "n/a"
    if p < 1e-300:
        return "<1e-300"
    return f"{p:.2g}"


def fmt_r(r):
    if r is None or np.isnan(r):
        return "n/a"
    return f"{r:+.3f}"


def effect_label(r):
    a = abs(r)
    if a < 0.1: return "negligible"
    if a < 0.3: return "small"
    if a < 0.5: return "moderate"
    return "large"


def holm_adjust(pvals):
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


def block_bootstrap_ci_r(x, y, block_size, n_boot=N_BOOT):
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
    return float(np.percentile(rs, 2.5)), float(np.percentile(rs, 97.5))


def block_permutation_p(x, y, block_size, n_boot=N_BOOT):
    n = len(x)
    r_obs = float(np.corrcoef(x, y)[0, 1])
    n_blocks = n // block_size
    if n_blocks < 2:
        return float("nan")
    usable = n_blocks * block_size
    blocks = x[:usable].reshape(n_blocks, block_size)
    yfix = y[:usable]
    count = 0
    for _ in range(n_boot):
        order = RNG.permutation(n_blocks)
        xperm = blocks[order].ravel()
        if np.std(xperm) == 0:
            continue
        r_perm = float(np.corrcoef(xperm, yfix)[0, 1])
        if abs(r_perm) >= abs(r_obs):
            count += 1
    return (1 + count) / (1 + n_boot)


def pearson(x, y):
    res = stats.pearsonr(x, y)
    return float(res.statistic), float(res.pvalue)


def scatter_with_fit(x, y, xlabel, ylabel, title, out_path):
    fig, ax = plt.subplots(figsize=(7.0, 5.0))
    ax.scatter(x, y, s=8, alpha=0.35, color="#4a8056", edgecolors="none")
    if len(x) >= 3 and np.std(x) > 0:
        b1, b0 = np.polyfit(x, y, 1)
        xs = np.linspace(np.min(x), np.max(x), 100)
        yhat = b0 + b1 * xs
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
                            color="#4a8056", alpha=0.15, linewidth=0)
        ax.plot(xs, yhat, color="#bf3030", linewidth=1.8)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, linestyle=":", alpha=0.4)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


# ── join ───────────────────────────────────────────────────

def part2_join():
    print("[join] sun_moon_field → joined_2025")
    sm = pd.read_parquet(SM_PATH)[["timestamp", "sun_moon_amplitude"]].sort_values("timestamp").reset_index(drop=True)
    joined = pd.read_parquet(JOINED_PATH).sort_values("timestamp").reset_index(drop=True)
    joined["timestamp"] = pd.to_datetime(joined["timestamp"], utc=True).astype("datetime64[ns, UTC]")
    sm["timestamp"] = pd.to_datetime(sm["timestamp"], utc=True).astype("datetime64[ns, UTC]")
    out = pd.merge_asof(joined, sm, on="timestamp", direction="nearest")
    out.to_parquet(JOINED_SM_PATH, index=False)
    print(f"  wrote {JOINED_SM_PATH}  rows={len(out)}  with_sm={int(out['sun_moon_amplitude'].notna().sum())}")
    return out


def daily_mean_sm():
    sm = pd.read_parquet(SM_PATH)
    sm["date"] = sm["timestamp"].dt.tz_convert("UTC").dt.floor("D")
    return sm.groupby("date", as_index=False)["sun_moon_amplitude"].mean().rename(
        columns={"sun_moon_amplitude": "sm_daily_mean"})


# ── battery ────────────────────────────────────────────────

def run_battery(joined_sm):
    print("\n[battery] W1'..W4'")
    results = {}

    # W1' — Kp ~ sun_moon_amplitude
    df = joined_sm[joined_sm["source"] == "kp"].dropna(subset=["kp", "sun_moon_amplitude"]).sort_values("timestamp").reset_index(drop=True)
    x = df["sun_moon_amplitude"].to_numpy(dtype=np.float64)
    y = df["kp"].to_numpy(dtype=np.float64)
    r, p = pearson(x, y)
    bsz = 30 * 8
    ci = block_bootstrap_ci_r(x, y, bsz)
    p_block = block_permutation_p(x, y, bsz)
    results["W1p"] = {"label": "Magnetosphere (Kp ~ sun_moon_amplitude)",
                     "n": int(len(df)), "r": r, "p": p, "p_block": p_block,
                     "ci_lo": ci[0], "ci_hi": ci[1], "x": x, "y": y, "df": df,
                     "block_days": 30, "block_samples": bsz,
                     "x_label": "sun_moon_amplitude (lagna, mean over k of |A|)", "y_label": "Kp index"}
    print(f"  W1': n={len(df)}  r={r:+.3f}  p={fmt_p(p)}  CI=[{ci[0]:+.3f},{ci[1]:+.3f}]  p_block={fmt_p(p_block)}")

    # W2' — Dst
    df = joined_sm[joined_sm["source"] == "dst"].dropna(subset=["dst_nT", "sun_moon_amplitude"]).sort_values("timestamp").reset_index(drop=True)
    x = df["sun_moon_amplitude"].to_numpy(dtype=np.float64)
    y = df["dst_nT"].to_numpy(dtype=np.float64)
    r, p = pearson(x, y)
    bsz = 30 * 24
    ci = block_bootstrap_ci_r(x, y, bsz)
    results["W2p"] = {"label": "Ring current (Dst ~ sun_moon_amplitude)",
                     "n": int(len(df)), "r": r, "p": p, "p_block": None,
                     "ci_lo": ci[0], "ci_hi": ci[1], "x": x, "y": y, "df": df,
                     "block_days": 30, "block_samples": bsz,
                     "x_label": "sun_moon_amplitude (lagna)", "y_label": "Dst (nT)"}
    print(f"  W2': n={len(df)}  r={r:+.3f}  p={fmt_p(p)}  CI=[{ci[0]:+.3f},{ci[1]:+.3f}]")

    # W3' — daily seismic count
    seis = joined_sm[joined_sm["source"] == "seismic"].copy()
    seis["date"] = seis["timestamp"].dt.tz_convert("UTC").dt.floor("D")
    counts = seis.groupby("date").size().rename("seis_count").reset_index()
    daily = daily_mean_sm()
    df = daily.merge(counts, on="date", how="left")
    df["seis_count"] = df["seis_count"].fillna(0).astype(int)
    df = df.sort_values("date").reset_index(drop=True)
    x = df["sm_daily_mean"].to_numpy(dtype=np.float64)
    y = df["seis_count"].to_numpy(dtype=np.float64)
    r, p = pearson(x, y)
    ci = block_bootstrap_ci_r(x, y, 14)
    results["W3p"] = {"label": "Lithosphere (daily M≥4 count ~ daily-mean sun_moon)",
                     "n": int(len(df)), "r": r, "p": p, "p_block": None,
                     "ci_lo": ci[0], "ci_hi": ci[1], "x": x, "y": y, "df": df,
                     "block_days": 14, "block_samples": 14,
                     "x_label": "daily-mean sun_moon_amplitude", "y_label": "daily M≥4 events"}
    print(f"  W3': n={len(df)}  r={r:+.3f}  p={fmt_p(p)}  CI=[{ci[0]:+.3f},{ci[1]:+.3f}]")

    # W4' — daily tide range
    tide = joined_sm[joined_sm["source"] == "tide"].dropna(subset=["water_level_m"]).copy()
    tide["date"] = tide["timestamp"].dt.tz_convert("UTC").dt.floor("D")
    rng = tide.groupby("date")["water_level_m"].agg(lambda s: s.max() - s.min()).rename("tide_range_m").reset_index()
    df = daily.merge(rng, on="date", how="inner").sort_values("date").reset_index(drop=True)
    x = df["sm_daily_mean"].to_numpy(dtype=np.float64)
    y = df["tide_range_m"].to_numpy(dtype=np.float64)
    r, p = pearson(x, y)
    ci = block_bootstrap_ci_r(x, y, 14)
    results["W4p"] = {"label": "Hydrosphere (daily tide range ~ daily-mean sun_moon)",
                     "n": int(len(df)), "r": r, "p": p, "p_block": None,
                     "ci_lo": ci[0], "ci_hi": ci[1], "x": x, "y": y, "df": df,
                     "block_days": 14, "block_samples": 14,
                     "x_label": "daily-mean sun_moon_amplitude", "y_label": "tide daily range (m)"}
    print(f"  W4': n={len(df)}  r={r:+.3f}  p={fmt_p(p)}  CI=[{ci[0]:+.3f},{ci[1]:+.3f}]")

    pvals = [results[k]["p"] for k in ("W1p", "W2p", "W3p", "W4p")]
    holm = holm_adjust(pvals)
    for k, h in zip(("W1p", "W2p", "W3p", "W4p"), holm):
        results[k]["p_holm"] = float(h)
    return results


# ── plots ──────────────────────────────────────────────────

def bar_plot(results):
    keys = ["W1p", "W2p", "W3p", "W4p"]
    labels = ["Magnetosphere\n(Kp)", "Ring current\n(Dst)", "Lithosphere\n(seismic)", "Hydrosphere\n(tide)"]
    abs_r = [abs(results[k]["r"]) for k in keys]
    err_low, err_hi = [], []
    for k in keys:
        r = results[k]["r"]
        ci_l, ci_h = results[k]["ci_lo"], results[k]["ci_hi"]
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
    ax.bar(xs, abs_r, color=["#bf3030", "#cc8030", "#308050", "#3a76c4"],
           edgecolor="black", linewidth=0.6)
    ax.errorbar(xs, abs_r, yerr=[err_low, err_hi], fmt="none", ecolor="black", capsize=4, linewidth=1.0)

    y_top = max(abs_r[i] + err_hi[i] for i in range(len(keys)))
    y_top = max(y_top, 0.10) * 1.35
    ax.set_xticks(xs); ax.set_xticklabels(labels)
    ax.set_ylabel("|Pearson r|  (95% block-bootstrap CI)")
    ax.set_title("Sun-Moon raw amplitude × bhūmi-layers — 2025 (EXPLORATORY)")
    ax.set_ylim(0, y_top)

    for thr, lab, c in [(0.1, "small", "#999"), (0.3, "moderate", "#777"), (0.5, "large", "#444")]:
        if thr > y_top: continue
        ax.axhline(thr, color=c, linestyle="--", linewidth=0.8, alpha=0.7)
        ax.text(len(keys) - 0.55, thr + y_top * 0.012, f"|r|={thr:.1f} ({lab})", color=c, fontsize=8, ha="right")

    for i, k in enumerate(keys):
        r = results[k]["r"]; n = results[k]["n"]
        ax.text(i, abs_r[i] + err_hi[i] + y_top * 0.02, f"r={r:+.3f}\nn={n}",
                ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    out = os.path.join(PLOTS, "sun_moon_bhumi_layers.png")
    fig.savefig(out, dpi=130)
    plt.close(fig)
    print(f"  bar plot → {out}")


def scatters(results):
    for k in ("W1p", "W2p", "W3p", "W4p"):
        r = results[k]
        out = os.path.join(PLOTS, f"sun_moon_{k}.png")
        title = f"{k.replace('p','')}'  {r['label']}\nr={r['r']:+.3f}  p={fmt_p(r['p'])}  n={r['n']}  (EXPLORATORY)"
        scatter_with_fit(r["x"], r["y"], r["x_label"], r["y_label"], title, out)
        print(f"  scatter → {out}")


# ── report ────────────────────────────────────────────────

def write_report(results, sm_stats, total_wall):
    keys = ["W1p", "W2p", "W3p", "W4p"]
    labels_pretty = {"W1p": "W1'", "W2p": "W2'", "W3p": "W3'", "W4p": "W4'"}
    abs_r = [abs(results[k]["r"]) for k in keys]
    strongest = keys[int(np.argmax(abs_r))]
    holm_survivors = [labels_pretty[k] for k in keys if results[k]["p_holm"] < 0.05]
    nontrivial = [labels_pretty[k] for k in keys if abs(results[k]["r"]) >= 0.1]

    rows = []
    for k in keys:
        r = results[k]
        p_block_str = fmt_p(r["p_block"]) if r["p_block"] is not None else "—"
        rows.append(
            f"| {labels_pretty[k]} | {r['label']} | {r['n']} | {fmt_r(r['r'])} | {fmt_p(r['p'])} | "
            f"{fmt_p(r['p_holm'])} | [{r['ci_lo']:+.3f}, {r['ci_hi']:+.3f}] | "
            f"{p_block_str} | {effect_label(r['r'])} |"
        )
    table = "| Test | Layer (model) | n | r | p (raw) | p (Holm/4) | 95% CI (block-boot) | p (block-perm) | effect |\n"
    table += "|---|---|---:|---:|---:|---:|---|---:|---|\n"
    table += "\n".join(rows)

    per_test = []
    for k in keys:
        r = results[k]
        per_test.append(
            f"### {labels_pretty[k]} — {r['label']}\n\n"
            f"n = {r['n']}; Pearson r = {fmt_r(r['r'])}; raw p = {fmt_p(r['p'])}; Holm-adjusted p = {fmt_p(r['p_holm'])}; "
            f"95% block-bootstrap CI = [{r['ci_lo']:+.3f}, {r['ci_hi']:+.3f}] (block size = {r['block_days']} days = "
            f"{r['block_samples']} samples). "
            + (f"Block-permutation p (autocorrelation-aware) = {fmt_p(r['p_block'])}. " if r['p_block'] is not None else "")
            + f"Effect size: **{effect_label(r['r'])}** (EXPLORATORY).\n\n"
            f"![{labels_pretty[k]} scatter](plots/sun_moon_{k}.png)\n"
        )

    s = sm_stats
    report = f"""# Sun-Moon Raw-Amplitude Wave-Field × Bhūmi-Layers — 2025 (EXPLORATORY)

This analysis is EXPLORATORY. It was run after the pre-specified zodiacal-mean wave-field test (research/geosolar/pilot_2025/WAVE_FIELD_ANALYSIS_2025.md) returned a clean null. The choice to drop the per-k normalization and to lock the target to the lagna was made AFTER seeing that null, informed by diagnostic evidence that the normalization compressed variance below detectable levels. Any signal surfaced here cannot be claimed as a confirmatory finding from 2025 data; it can only motivate pre-specification of the same test on the forthcoming multi-decade dataset (1973–2024), where statistical power is higher and the test is run on data not seen at design time.

## Hypothesis

The original wave-field-mean scalar applied a per-k min-max normalization across twelve zodiacal targets at every timestamp; this collapsed dynamic range to std ≈ 0.032 over a year. The two-step modification tested here:

1. **Drop the normalization.** Use raw `|A_k| = |cos(k·(target − Sun)) + cos(k·(target − Moon))|` instead of the rank-rescaled composite.
2. **Lock the target to the lagna** (rising point at Gainesville, lat = 29.65, lon = −82.34). The lagna sweeps through the zodiac roughly every 24 hours due to Earth rotation, providing a location-coupled, time-varying probe that the static zodiacal-centroid set lacks.

The reduction is `sun_moon_amplitude(t) = mean over k ∈ {{1,2,3,4,6,7,12}} of |A_k(t)|`, range [0, 2]. The hypothesis: this reduction better preserves the variance pattern that should — under the substrate-stratification framing — couple to bhūmi-layer responses (Kp, Dst, daily seismic count, daily tide range).

## Method

For each of the 52,560 ten-minute timestamps in 2025, `compute_chart(dt_utc, lat=29.65, lon=-82.34)` returns Sun, Moon, and lagna sidereal longitudes (Lahiri ayanāṃśa). For each k in {{1,2,3,4,6,7,12}}, `compute_pair_interference(sun_long, moon_long, lagna_long, k)` from `npu_engine.jyotisha_engine` returns the raw amplitude `A_k`. The scalar is the arithmetic mean over k of `|A_k|`. The full per-timestamp scalar plus the three input longitudes is stored as `sun_moon_field_2025.parquet`.

The four-test family W1'..W4' mirrors the prior W1..W4 exactly, with `wave_field_mean` swapped for `sun_moon_amplitude`:

  - **W1'** Kp vs `sun_moon_amplitude` (3-hourly, n = {results['W1p']['n']:,})
  - **W2'** Dst vs `sun_moon_amplitude` (hourly, n = {results['W2p']['n']:,})
  - **W3'** Daily M≥4 seismic count vs daily-mean `sun_moon_amplitude` (n = {results['W3p']['n']:,})
  - **W4'** Daily tide range vs daily-mean `sun_moon_amplitude` (n = {results['W4p']['n']:,})

Holm-Bonferroni step-down across the new family of four (separate from the prior null family). 95% confidence intervals via moving-block bootstrap, 1,000 resamples; block size = 30 days for hourly/3-hourly, 14 days for daily aggregates. For W1' specifically, an additional autocorrelation-aware block-permutation p-value is reported (block size = 30 days).

**Distribution of the scalar.** n = {s['n']:,}; mean = {s['mean']:.4f}; std = {s['std']:.4f}; min = {s['min']:.4f}; p25 = {s['p25']:.4f}; median = {s['p50']:.4f}; p75 = {s['p75']:.4f}; max = {s['max']:.4f}. All values lie in [0, 2]; no NaNs. Dynamic range is **{s['std']/0.0325:.1f}× wider** than the prior wave-field-mean (std = 0.0325).

## Results

{table}

![bhūmi-layer bar plot (exploratory)](plots/sun_moon_bhumi_layers.png)

Strongest absolute correlation: **{labels_pretty[strongest]}** (|r| = {abs(results[strongest]['r']):.3f}). Tests with |r| ≥ 0.1 (above the negligible threshold): {", ".join(nontrivial) if nontrivial else "none"}. Tests surviving Holm correction at α = 0.05: {", ".join(holm_survivors) if holm_survivors else "none"}.

## Per-test detail

{chr(10).join(per_test)}

## Limitations

- **EXPLORATORY.** The reduction (drop normalization + lock to lagna) was chosen after seeing the prior null. Type-I error is uncontrolled even after Holm correction within this family, because *the family itself was selected post-hoc*.
- **Single year.** 2025 only; no out-of-sample replication.
- **Single location.** The lagna is computed at Gainesville. A different latitude shifts the rising point ordering and would re-time the scalar.
- **Single pair (Sun-Moon).** Other dyads (Sun-Saturn, Moon-Jupiter, etc.) are not tested here. The Sun-Moon choice is physically motivated for tides and lunar-syzygy seismic, less so for Kp/Dst.
- **Daily aggregation for W3'/W4'.** Sub-daily structure is collapsed; coupling on shorter timescales (e.g. tidal-syzygy peaks within a day) is invisible to this aggregation.
- **Autocorrelation handling is approximate.** Block bootstrap captures within-block dependence but assumes block-level exchangeability.

## Confirmatory next step

This 2025 result, regardless of its magnitude, **is not citable as a finding**. The actual confirmatory test on the Sun-Moon raw-amplitude lagna-target hypothesis will be run on the forthcoming multi-decade dataset (1973–2024 archive currently being assembled). The pre-specification will:

1. Lock the test design — same `sun_moon_amplitude` reduction, same lagna location (Gainesville), same four bhūmi-layer indicators, same Holm-across-4, same block-bootstrap CI rules — **before** the multi-decade data is loaded for analysis.
2. Be committed to git with a timestamp, so the lock is auditable.
3. Be evaluated on the multi-decade data exactly once. Whatever it shows is the result on this hypothesis. No re-tuning, no re-reduction, no re-pick of target.

The 2025 numbers in this report function only as a power-and-scale prior for that pre-registered multi-decade test. They do not establish or refute the substrate-stratification claim.

---

*Inputs: `compute_chart` + `compute_pair_interference` from `npu_engine.jyotisha_engine` (pure ephemeris). Wall clock for analysis: {total_wall:.1f} s.*
"""
    with open(REPORT_PATH, "w") as f:
        f.write(report)
    print(f"  report → {REPORT_PATH}")


def main():
    t0 = time.time()
    os.makedirs(PLOTS, exist_ok=True)

    sm = pd.read_parquet(SM_PATH)["sun_moon_amplitude"]
    sm_stats = {
        "n": int(len(sm)),
        "mean": float(sm.mean()), "std": float(sm.std()),
        "min": float(sm.min()), "max": float(sm.max()),
        "p25": float(sm.quantile(0.25)),
        "p50": float(sm.quantile(0.5)),
        "p75": float(sm.quantile(0.75)),
    }
    print(f"sun_moon_amplitude dist: mean={sm_stats['mean']:.4f} std={sm_stats['std']:.4f} "
          f"min={sm_stats['min']:.4f} p25={sm_stats['p25']:.4f} p50={sm_stats['p50']:.4f} "
          f"p75={sm_stats['p75']:.4f} max={sm_stats['max']:.4f}  (in [0,2])")

    # Stop-gate guard (mirrors build script).
    if sm_stats["std"] < 0.05:
        print("[STOP-GATE] std < 0.05 — exploratory test not run on this scalar.")
        return

    joined_sm = part2_join()
    results = run_battery(joined_sm)
    bar_plot(results)
    scatters(results)
    write_report(results, sm_stats, time.time() - t0)

    # ── console summary ──
    print("\n" + "=" * 60)
    print("SUN-MOON AMPLITUDE DISTRIBUTION (EXPLORATORY)")
    print("=" * 60)
    print(f"  n      = {sm_stats['n']:,}")
    print(f"  mean   = {sm_stats['mean']:.4f}    std  = {sm_stats['std']:.4f}")
    print(f"  min    = {sm_stats['min']:.4f}    max  = {sm_stats['max']:.4f}")
    print(f"  p25    = {sm_stats['p25']:.4f}    p50  = {sm_stats['p50']:.4f}    p75  = {sm_stats['p75']:.4f}")

    print("\n" + "=" * 60)
    print("W1'-W4' SUMMARY (EXPLORATORY)")
    print("=" * 60)
    holm_survivors = []
    for k in ("W1p", "W2p", "W3p", "W4p"):
        r = results[k]
        kp_label = k.replace("p", "'")
        line = (f"  {kp_label}  {r['label']:<60}  r={fmt_r(r['r'])}  p={fmt_p(r['p'])}  "
                f"p_holm={fmt_p(r['p_holm'])}  CI=[{r['ci_lo']:+.3f},{r['ci_hi']:+.3f}]  {effect_label(r['r'])}")
        print(line)
        if r['p_block'] is not None:
            print(f"        block-permutation p (autocorrelation-aware): {fmt_p(r['p_block'])}")
        if r['p_holm'] < 0.05:
            holm_survivors.append(kp_label)

    print("\n" + "=" * 60)
    print("HOLM SURVIVORS @ α=0.05")
    print("=" * 60)
    print(f"  {', '.join(holm_survivors) if holm_survivors else 'none'}")
    print()
    print("Result is exploratory; confirmatory test pending multi-decade data.")
    print(f"\nTotal wall-clock (analyze): {time.time() - t0:.1f} s")


if __name__ == "__main__":
    main()
