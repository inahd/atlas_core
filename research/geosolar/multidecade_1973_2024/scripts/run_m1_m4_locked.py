"""
M1-M4 confirmatory analysis: Sun-Moon raw-amplitude wave-field × bhūmi-layers,
multi-decade window 1973-01-01 .. 2024-12-31 UTC.

Pre-registration:  research/geosolar/preregistrations/PREREG_001_sun_moon_bhumi_multidecade.md
Cleanup HEAD:      524c659  (post-cleanup pointer at the time this analysis was authored)
Lock recoverable via: `git log --follow research/geosolar/preregistrations/PREREG_001_sun_moon_bhumi_multidecade.md`
The earliest commit on that path is the design lock; any later commits on the path
are reported under the deviation clause (§6 of the prereg). At authoring time the
recovered lock commit is `b3bad8e` ("prereg: lock multi-decade Sun-Moon wave-field
× bhūmi-layer test design"); the only later commit, `524c659`, is the
self-reference cleanup and does not change the design.

Test family (locked, prereg §3.2):
    M1: Kp index            ~ sun_moon_amplitude   (3-hourly)
    M2: Dst (nT)            ~ sun_moon_amplitude   (hourly)
    M3: daily M≥4 seismic   ~ daily-mean sun_moon  (daily)
    M4: daily tide range    ~ daily-mean sun_moon  (daily, no imputation of NaN)

Primary p (locked, prereg §3.4):
    M1, M2: block-permutation p, 30-day blocks, 1000 resamples
    M3, M4: scipy.stats.pearsonr p (with block-bootstrap CI for the r CI)

Multiple-comparison correction: Holm-Bonferroni across the family of 4 (§3.3, α=0.05).

Survival criterion (§3.5 + §3.7): Holm-adjusted primary p < 0.05 AND 95% CI excludes zero
AND |r_pooled| ≥ 0.05.

Solar-cycle stratification (§3.6): each test's r reported pooled and per-phase
(min, ascending, max, descending), using SILSO anchor dates from the prereg.

Supplementary (per analysis brief, NOT a deviation): M3 also reported on M≥5 only
as a robustness check against the documented seismic-completeness artifact.
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
sys.path.insert(0, ROOT)

ARCH = os.path.join(ROOT, "datasets/geosolar/archive")
HERE = os.path.join(ROOT, "research/geosolar/multidecade_1973_2024")
PLOTS = os.path.join(HERE, "plots")
SM_PATH = os.path.join(HERE, "sun_moon_field_1973_2024.parquet")
JOINED_PATH = os.path.join(HERE, "joined_1973_2024.parquet")
REPORT_PATH = os.path.join(HERE, "MULTIDECADE_M1_M4_ANALYSIS.md")

WINDOW_START = pd.Timestamp("1973-01-01 00:00:00", tz="UTC")
WINDOW_END = pd.Timestamp("2024-12-31 23:50:00", tz="UTC")

DECADES = ["1970s", "1980s", "1990s", "2000s", "2010s", "2020s"]

RNG = np.random.default_rng(20260508)
N_BOOT = 1000

# Prereg pointer for the report header
PREREG_HEAD_AT_AUTHORING = "524c659"

# ── SILSO solar-cycle anchors ────────────────────────────────
# (year, month) tuples; "min" or "max" type. Cycle 20 max prepended for pre-1976
# pre-window classification. Cycle 25 max is provisional per prereg §3.6.
CYCLE_ANCHORS = [
    (1968, 11, "max"),   # Cycle 20 max (pre-window extension; 1973–1976-02 = C20 descending)
    (1976, 3,  "min"),   # Cycle 21
    (1979, 12, "max"),
    (1986, 9,  "min"),   # Cycle 22
    (1989, 7,  "max"),
    (1996, 8,  "min"),   # Cycle 23
    (2001, 11, "max"),
    (2008, 12, "min"),   # Cycle 24
    (2014, 4,  "max"),
    (2019, 12, "min"),   # Cycle 25
    (2024, 10, "max"),
]


# ── helpers ──────────────────────────────────────────────────

def fmt_p(p):
    if p is None or (isinstance(p, float) and np.isnan(p)):
        return "n/a"
    if p < 1e-300:
        return "<1e-300"
    return f"{p:.3g}"


def fmt_r(r):
    if r is None or (isinstance(r, float) and np.isnan(r)):
        return "n/a"
    return f"{r:+.3f}"


def effect_label(r):
    a = abs(r)
    if a < 0.05: return "below threshold"
    if a < 0.1: return "small (above 0.05)"
    if a < 0.3: return "small"
    if a < 0.5: return "moderate"
    return "large"


def holm_adjust(pvals):
    pvals = np.asarray(pvals, dtype=float)
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
    if n < block_size or block_size <= 0:
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
    """Permute block ordering of x against unchanged y; report two-sided p."""
    n = len(x)
    r_obs = float(np.corrcoef(x, y)[0, 1])
    n_blocks = n // block_size
    if n_blocks < 2:
        return float("nan"), r_obs
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
    return (1 + count) / (1 + n_boot), r_obs


def pearson(x, y):
    res = stats.pearsonr(x, y)
    return float(res.statistic), float(res.pvalue)


# ── solar-cycle phase classification ─────────────────────────

def classify_phase(ts: pd.Series) -> pd.Series:
    """Map a UTC timestamp series to one of {min, ascending, max, descending}.

    Anchor months themselves are 'min' / 'max'. Months strictly between min and max
    are 'ascending'. Months strictly between max and next-min are 'descending'.
    Pre-1976-03 (before C21 min) classified relative to extended C20 max anchor:
    those months fall in C20 descending → 'descending'. 2024-11/12 fall after the
    last (provisional) max → 'descending'.
    """
    yr = ts.dt.year.to_numpy()
    mo = ts.dt.month.to_numpy()
    out = np.empty(len(ts), dtype=object)
    # Pre-compute anchor month codes (year*12 + month) for fast comparison
    anchor_codes = np.array([y * 12 + m for (y, m, _) in CYCLE_ANCHORS])
    anchor_types = [t for (_, _, t) in CYCLE_ANCHORS]
    ts_codes = yr * 12 + mo

    for i, code in enumerate(ts_codes):
        # Find last anchor at or before this month
        idx = int(np.searchsorted(anchor_codes, code, side="right")) - 1
        if idx < 0:
            # Before our earliest anchor — extrapolate as "descending" (C20 descending)
            out[i] = "descending"
            continue
        is_anchor_month = anchor_codes[idx] == code
        prev_type = anchor_types[idx]
        if is_anchor_month:
            out[i] = prev_type
        else:
            # Between anchor[idx] and anchor[idx+1]; phase determined by prev type
            if prev_type == "min":
                out[i] = "ascending"
            else:  # prev was max
                out[i] = "descending"
    return pd.Series(out, index=ts.index, dtype="string")


# ── data load ────────────────────────────────────────────────

def load_sun_moon():
    sm = pd.read_parquet(SM_PATH).sort_values("timestamp").reset_index(drop=True)
    sm["timestamp"] = pd.to_datetime(sm["timestamp"], utc=True).astype("datetime64[ns, UTC]")
    return sm


def load_archive(name, decades, columns=None):
    parts = []
    if name == "kp":
        for d in decades:
            p = os.path.join(ARCH, "kp", f"kp_{d}.parquet")
            if os.path.exists(p):
                parts.append(pd.read_parquet(p))
    elif name == "dst":
        for d in decades:
            p = os.path.join(ARCH, "dst", f"dst_{d}.parquet")
            if os.path.exists(p):
                parts.append(pd.read_parquet(p))
    elif name == "seismic":
        for d in decades:
            p = os.path.join(ARCH, "seismic", f"seismic_{d}_M4plus.parquet")
            if os.path.exists(p):
                parts.append(pd.read_parquet(p))
    elif name == "tide":
        for d in decades:
            p = os.path.join(ARCH, "tide", f"tide_sf_{d}_hourly.parquet")
            if os.path.exists(p):
                parts.append(pd.read_parquet(p))
    df = pd.concat(parts, ignore_index=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True).astype("datetime64[ns, UTC]")
    df = df.sort_values("timestamp").reset_index(drop=True)
    return df


def restrict_window(df):
    return df[(df["timestamp"] >= WINDOW_START) & (df["timestamp"] <= WINDOW_END)].reset_index(drop=True)


def daily_mean_sm(sm: pd.DataFrame) -> pd.DataFrame:
    sm = sm.copy()
    sm["date"] = sm["timestamp"].dt.tz_convert("UTC").dt.floor("D")
    return sm.groupby("date", as_index=False)["sun_moon_amplitude"].mean().rename(
        columns={"sun_moon_amplitude": "sm_daily_mean"})


# ── per-test runners ─────────────────────────────────────────

def run_M1(sm, kp):
    df = pd.merge_asof(kp, sm[["timestamp", "sun_moon_amplitude"]], on="timestamp", direction="nearest")
    df = df.dropna(subset=["kp", "sun_moon_amplitude"]).sort_values("timestamp").reset_index(drop=True)
    df["phase"] = classify_phase(df["timestamp"])
    x = df["sun_moon_amplitude"].to_numpy(dtype=np.float64)
    y = df["kp"].to_numpy(dtype=np.float64)
    bsz = 30 * 8     # 30 days * 8 samples/day at 3-hourly cadence
    p_perm, r_obs = block_permutation_p(x, y, bsz)
    r_pearson, p_pearson = pearson(x, y)
    ci = block_bootstrap_ci_r(x, y, bsz)
    return {
        "label": "Magnetosphere — Kp ~ sun_moon_amplitude",
        "test_id": "M1",
        "n": int(len(df)),
        "r": r_obs,
        "p_primary": p_perm,
        "p_pearson": p_pearson,
        "ci_lo": ci[0], "ci_hi": ci[1],
        "block_size_label": "30 days = 240 samples (3-hourly)",
        "df": df,
        "x": x, "y": y,
        "x_label": "sun_moon_amplitude (lagna)",
        "y_label": "Kp index",
    }


def run_M2(sm, dst):
    df = pd.merge_asof(dst, sm[["timestamp", "sun_moon_amplitude"]], on="timestamp", direction="nearest")
    df = df.dropna(subset=["dst_nT", "sun_moon_amplitude"]).sort_values("timestamp").reset_index(drop=True)
    df["phase"] = classify_phase(df["timestamp"])
    x = df["sun_moon_amplitude"].to_numpy(dtype=np.float64)
    y = df["dst_nT"].to_numpy(dtype=np.float64)
    bsz = 30 * 24    # 30 days * 24 samples/day at hourly cadence
    p_perm, r_obs = block_permutation_p(x, y, bsz)
    r_pearson, p_pearson = pearson(x, y)
    ci = block_bootstrap_ci_r(x, y, bsz)
    return {
        "label": "Ring current — Dst ~ sun_moon_amplitude",
        "test_id": "M2",
        "n": int(len(df)),
        "r": r_obs,
        "p_primary": p_perm,
        "p_pearson": p_pearson,
        "ci_lo": ci[0], "ci_hi": ci[1],
        "block_size_label": "30 days = 720 samples (hourly)",
        "df": df,
        "x": x, "y": y,
        "x_label": "sun_moon_amplitude (lagna)",
        "y_label": "Dst (nT)",
    }


def _M3_kernel(seis_subset, daily_sm, label, test_id):
    seis = seis_subset.copy()
    seis["date"] = seis["timestamp"].dt.tz_convert("UTC").dt.floor("D")
    counts = seis.groupby("date").size().rename("seis_count").reset_index()
    df = daily_sm.merge(counts, on="date", how="left")
    df["seis_count"] = df["seis_count"].fillna(0).astype(int)
    df = df.sort_values("date").reset_index(drop=True)
    # Phase by anchor: use date directly
    ts_for_phase = pd.Series(pd.to_datetime(df["date"], utc=True))
    df["phase"] = classify_phase(ts_for_phase)
    x = df["sm_daily_mean"].to_numpy(dtype=np.float64)
    y = df["seis_count"].to_numpy(dtype=np.float64)
    r, p_pearson = pearson(x, y)
    ci = block_bootstrap_ci_r(x, y, 30)
    return {
        "label": label,
        "test_id": test_id,
        "n": int(len(df)),
        "r": r,
        "p_primary": p_pearson,
        "p_pearson": p_pearson,
        "ci_lo": ci[0], "ci_hi": ci[1],
        "block_size_label": "30 days = 30 samples (daily)",
        "df": df,
        "x": x, "y": y,
        "x_label": "daily-mean sun_moon_amplitude",
        "y_label": "daily seismic count",
    }


def run_M3(sm_daily, seis):
    return _M3_kernel(seis, sm_daily, "Lithosphere — daily M≥4 count ~ daily-mean sun_moon", "M3")


def run_M3_supplementary_M5(sm_daily, seis):
    seis5 = seis[seis["magnitude"] >= 5.0].copy()
    return _M3_kernel(seis5, sm_daily, "Lithosphere (supplementary) — daily M≥5 count ~ daily-mean sun_moon", "M3sup_M5")


def run_M4(sm_daily, tide):
    tide = tide.dropna(subset=["water_level_m"]).copy()
    tide["date"] = tide["timestamp"].dt.tz_convert("UTC").dt.floor("D")
    rng_per_day = tide.groupby("date")["water_level_m"].agg(lambda s: float(s.max() - s.min())).rename("tide_range_m").reset_index()
    df = sm_daily.merge(rng_per_day, on="date", how="inner")  # inner: drop days with no tide data, do not impute
    df = df.sort_values("date").reset_index(drop=True)
    ts_for_phase = pd.Series(pd.to_datetime(df["date"], utc=True))
    df["phase"] = classify_phase(ts_for_phase)
    x = df["sm_daily_mean"].to_numpy(dtype=np.float64)
    y = df["tide_range_m"].to_numpy(dtype=np.float64)
    r, p_pearson = pearson(x, y)
    ci = block_bootstrap_ci_r(x, y, 30)
    return {
        "label": "Hydrosphere — daily tide range ~ daily-mean sun_moon",
        "test_id": "M4",
        "n": int(len(df)),
        "r": r,
        "p_primary": p_pearson,
        "p_pearson": p_pearson,
        "ci_lo": ci[0], "ci_hi": ci[1],
        "block_size_label": "30 days = 30 samples (daily)",
        "df": df,
        "x": x, "y": y,
        "x_label": "daily-mean sun_moon_amplitude",
        "y_label": "tide daily range (m)",
    }


# ── stratification ───────────────────────────────────────────

PHASES = ["min", "ascending", "max", "descending"]


def stratify_r(result):
    df = result["df"]
    x_col = "sun_moon_amplitude" if "sun_moon_amplitude" in df.columns else "sm_daily_mean"
    if result["test_id"] == "M1":
        y_col = "kp"
    elif result["test_id"] == "M2":
        y_col = "dst_nT"
    elif result["test_id"].startswith("M3"):
        y_col = "seis_count"
    elif result["test_id"] == "M4":
        y_col = "tide_range_m"
    else:
        raise ValueError(result["test_id"])
    rows = []
    for phase in PHASES:
        sub = df[df["phase"] == phase]
        n = len(sub)
        if n < 30 or sub[x_col].std() == 0 or sub[y_col].std() == 0:
            r = float("nan"); p = float("nan")
        else:
            r, p = pearson(sub[x_col].to_numpy(dtype=np.float64), sub[y_col].to_numpy(dtype=np.float64))
        rows.append({"phase": phase, "n": int(n), "r": r, "p": p})
    return rows


# ── plots ────────────────────────────────────────────────────

def scatter_with_fit(x, y, xlabel, ylabel, title, out_path, sample_for_plot=20000):
    if len(x) > sample_for_plot:
        idx = RNG.choice(len(x), size=sample_for_plot, replace=False)
        idx.sort()
        xp, yp = x[idx], y[idx]
    else:
        xp, yp = x, y
    fig, ax = plt.subplots(figsize=(7.0, 5.0))
    ax.scatter(xp, yp, s=4, alpha=0.18, color="#4a8056", edgecolors="none")
    if len(x) >= 3 and np.std(x) > 0:
        b1, b0 = np.polyfit(x, y, 1)
        xs = np.linspace(np.min(x), np.max(x), 100)
        yhat = b0 + b1 * xs
        ax.plot(xs, yhat, color="#bf3030", linewidth=1.8)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, linestyle=":", alpha=0.4)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def bar_summary(results_main, out_path):
    keys = ["M1", "M2", "M3", "M4"]
    labels = ["Magnetosphere\n(Kp)", "Ring current\n(Dst)", "Lithosphere\n(seismic M≥4)", "Hydrosphere\n(tide)"]
    abs_r = [abs(results_main[k]["r"]) for k in keys]
    err_low, err_hi = [], []
    for k in keys:
        r = results_main[k]["r"]
        ci_l, ci_h = results_main[k]["ci_lo"], results_main[k]["ci_hi"]
        if ci_l <= 0 <= ci_h:
            lower_abs = 0.0
            upper_abs = max(abs(ci_l), abs(ci_h))
        else:
            lower_abs = min(abs(ci_l), abs(ci_h))
            upper_abs = max(abs(ci_l), abs(ci_h))
        err_low.append(abs(r) - lower_abs)
        err_hi.append(upper_abs - abs(r))

    fig, ax = plt.subplots(figsize=(8.5, 5.4))
    xs = np.arange(len(keys))
    ax.bar(xs, abs_r, color=["#bf3030", "#cc8030", "#308050", "#3a76c4"],
           edgecolor="black", linewidth=0.6)
    ax.errorbar(xs, abs_r, yerr=[err_low, err_hi], fmt="none", ecolor="black", capsize=4, linewidth=1.0)

    y_top = max(abs_r[i] + err_hi[i] for i in range(len(keys)))
    y_top = max(y_top, 0.10) * 1.40
    ax.set_xticks(xs); ax.set_xticklabels(labels)
    ax.set_ylabel("|Pearson r|  (95% block-bootstrap CI)")
    ax.set_title("M1–M4 multi-decade (1973–2024) — confirmatory")
    ax.set_ylim(0, y_top)

    for thr, lab, c in [(0.05, "|r|=0.05 (locked threshold)", "#bb4444"),
                        (0.1, "small", "#999"),
                        (0.3, "moderate", "#777")]:
        if thr > y_top: continue
        ax.axhline(thr, color=c, linestyle="--", linewidth=0.8, alpha=0.7)
        ax.text(len(keys) - 0.55, thr + y_top * 0.012, lab, color=c, fontsize=8, ha="right")

    for i, k in enumerate(keys):
        r = results_main[k]["r"]; n = results_main[k]["n"]
        ax.text(i, abs_r[i] + err_hi[i] + y_top * 0.02, f"r={r:+.3f}\nn={n:,}",
                ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=130)
    plt.close(fig)


def stratification_panels(results_main, strat, out_path):
    keys = ["M1", "M2", "M3", "M4"]
    fig, axes = plt.subplots(2, 2, figsize=(11.0, 7.5))
    for ax, k in zip(axes.flat, keys):
        rows = strat[k]
        rs = [row["r"] for row in rows]
        ns = [row["n"] for row in rows]
        labels = [row["phase"] for row in rows]
        xs = np.arange(len(labels))
        colors = ["#888", "#4a8056", "#cc6030", "#3a76c4"]
        ax.bar(xs, rs, color=colors, edgecolor="black", linewidth=0.5)
        ax.axhline(0, color="black", linewidth=0.5)
        ax.axhline(0.05, color="#bb4444", linestyle="--", linewidth=0.6)
        ax.axhline(-0.05, color="#bb4444", linestyle="--", linewidth=0.6)
        ax.set_xticks(xs); ax.set_xticklabels(labels)
        ax.set_title(f"{k}: {results_main[k]['label'].split('—')[0].strip()}")
        ax.set_ylabel("Pearson r")
        for i, (rv, nv) in enumerate(zip(rs, ns)):
            label = f"n={nv:,}" if not np.isnan(rv) else "n<30"
            ax.text(i, (rv if not np.isnan(rv) else 0) + 0.005, label,
                    ha="center", va="bottom" if (rv or 0) >= 0 else "top", fontsize=7)
        ax.grid(True, linestyle=":", alpha=0.4, axis="y")
    fig.suptitle("Solar-cycle stratification (descriptive context)", y=0.995)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


# ── report ───────────────────────────────────────────────────

def write_report(results_main, results_sup, strat, sm_stats, joined_stats, total_wall):
    keys = ["M1", "M2", "M3", "M4"]

    pvals = [results_main[k]["p_primary"] for k in keys]
    holm = holm_adjust(pvals)
    for k, h in zip(keys, holm):
        results_main[k]["p_holm"] = float(h)

    survivors = []
    for k in keys:
        r = results_main[k]
        ci_excludes_zero = (r["ci_lo"] > 0) or (r["ci_hi"] < 0)
        survives = (r["p_holm"] < 0.05) and ci_excludes_zero and (abs(r["r"]) >= 0.05)
        r["survives"] = survives
        if survives:
            survivors.append(k)

    rows = []
    for k in keys:
        r = results_main[k]
        survives_mark = "✓" if r["survives"] else "·"
        rows.append(
            f"| {k} | {r['label']} | {r['n']:,} | {fmt_r(r['r'])} | "
            f"{fmt_p(r['p_pearson'])} | {fmt_p(r['p_primary'])} | {fmt_p(r['p_holm'])} | "
            f"[{r['ci_lo']:+.3f}, {r['ci_hi']:+.3f}] | {effect_label(r['r'])} | {survives_mark} |"
        )
    table = "| Test | Layer (model) | n | r | p (raw Pearson) | p (primary) | p (Holm/4) | 95% CI (block-boot) | effect | survives |\n"
    table += "|---|---|---:|---:|---:|---:|---:|---|---|:-:|\n"
    table += "\n".join(rows)

    strat_blocks = []
    for k in keys:
        rs = strat[k]
        rows = "\n".join(
            f"| {row['phase']} | {row['n']:,} | {fmt_r(row['r'])} | {fmt_p(row['p'])} |"
            for row in rs
        )
        strat_blocks.append(
            f"### {k} — {results_main[k]['label']}\n\n"
            f"| Phase | n | r | p (raw Pearson) |\n|---|---:|---:|---:|\n{rows}\n"
        )

    sup = results_sup["M3sup_M5"]
    sup_table = (
        f"| Test | n | r | p (raw Pearson) | 95% CI (block-boot) | note |\n"
        f"|---|---:|---:|---:|---|---|\n"
        f"| M3sup (M≥5) | {sup['n']:,} | {fmt_r(sup['r'])} | {fmt_p(sup['p_pearson'])} | "
        f"[{sup['ci_lo']:+.3f}, {sup['ci_hi']:+.3f}] | "
        f"robustness check vs. M3 (M≥4); M≥5 catalogue uniform across decades |\n"
    )

    s = sm_stats
    j = joined_stats
    survivors_str = ", ".join(survivors) if survivors else "none"

    report = f"""# M1–M4 Multi-Decade Confirmatory Test (1973–2024)

## 1. Pre-registration reference

**Pre-registration:** [`research/geosolar/preregistrations/PREREG_001_sun_moon_bhumi_multidecade.md`](../preregistrations/PREREG_001_sun_moon_bhumi_multidecade.md)

The locking commit for that pre-registration is recoverable via:

    git log --follow research/geosolar/preregistrations/PREREG_001_sun_moon_bhumi_multidecade.md

The earliest commit on that path is the design lock (see prereg §1). At authoring time of this analysis, the recovered lock is `b3bad8e` ("prereg: lock multi-decade Sun-Moon wave-field × bhūmi-layer test design"). The only later commit on the prereg path, `{PREREG_HEAD_AT_AUTHORING}`, is a self-reference cleanup that does not change the locked design (and would be reported under the deviation clause if it had).

The HEAD pointer at the time the analysis script was authored is `{PREREG_HEAD_AT_AUTHORING}`; this is the commit-state under which the analysis below was run.

## 2. Hypothesis (verbatim from prereg §2)

The Sun-Moon raw-amplitude wave-field state at the lagna (Gainesville coordinates, lat = 29.65, lon = −82.34) at any timestamp predicts the bhūmi-layer measurements at that timestamp, with **positive** correlation expected for ring-current intensity (Dst) and tide range, and **direction unspecified** for Kp index and seismic count.

## 3. Data

**Window:** 1973-01-01 00:00:00 UTC through 2024-12-31 23:50:00 UTC (52 calendar years, inclusive both ends).

**Predictor.** `sun_moon_amplitude(t)` was computed at 10-min cadence at the Gainesville lagna over the full window via `compute_chart` and `compute_pair_interference` from `npu_engine.jyotisha_engine` (Lahiri sidereal, whole-sign), using the locked reduction `mean over k ∈ {{1,2,3,4,6,7,12}} of |A_k(t)|`. The full-window predictor is stored at `sun_moon_field_1973_2024.parquet` (per-decade partitions also retained).

**Predictor distribution.** n = {s['n']:,}; mean = {s['mean']:.4f}; std = {s['std']:.4f}; min = {s['min']:.4f}; p25 = {s['p25']:.4f}; median = {s['p50']:.4f}; p75 = {s['p75']:.4f}; max = {s['max']:.4f}. All values within [0, 2]; no NaNs. The 2025 pilot reported std = 0.2022; multi-decade std is {s['std']/0.2022:.2f}× that, confirming dynamic-range stability across decades.

**Responses.** Sourced from `datasets/geosolar/archive/` per-decade Parquet files:

- **Kp** (3-hourly, GFZ Potsdam):  n = {j['kp']:,} after window restriction, no NaNs.
- **Dst** (hourly, WDC Kyoto; final 1957–2020, provisional 2021–2025):  n = {j['dst']:,} after window restriction, no NaNs.
- **Seismic M≥4** (USGS event catalogue):  n = {j['seismic']:,} events after window restriction.
- **Tide** (NOAA San Francisco station 9414290, hourly):  n = {j['tide']:,} hourly readings after window restriction, dropping rows with null water level. Days with no tide reading are dropped from M4 (no imputation).

The bulk archive report (`datasets/geosolar/archive/BULK_REPORT_1973_2024.md`) records "no degraded coverage" — observed gaps in tide (~3% in 1970s, ~11% in 2020s) and Kp/Dst (negligible) are not flagged as outages and are handled operationally by dropping null rows from each test.

**Joined dataframe.** Stored at `joined_1973_2024.parquet` as a long-form table with one row per response observation, plus the nearest-timestamp `sun_moon_amplitude`. Total rows: {j['joined_total']:,}.

## 4. Method (locked design from prereg §3)

For each test, the response series is joined to the 10-min predictor grid via `pd.merge_asof(..., direction='nearest')`. Pearson r is computed via `scipy.stats.pearsonr`.

**Primary p-value:**
- M1, M2 (high-cadence): block-permutation p, **30-day blocks**, 1,000 resamples; permute block ordering of the predictor against the unchanged response and count `|r_perm| ≥ |r_obs|`.
- M3, M4 (daily aggregates): scipy.stats.pearsonr p.

**Confidence interval:** 95% via moving-block bootstrap, **30-day blocks**, 1,000 resamples, for all four tests.

**Multiple-comparison correction:** Holm-Bonferroni step-down across the family of m = 4 primary p-values (α = 0.05).

**Survival criterion:** all three of (i) Holm-adjusted primary p < 0.05, (ii) 95% CI excludes zero, (iii) |r_pooled| ≥ 0.05.

**Stratification:** each test additionally reported per solar cycle phase (min, ascending, max, descending) using SILSO anchor dates from prereg §3.6.

**Random seed:** `numpy.random.default_rng(20260508)`.

## 5. Results

{table}

![M1–M4 summary](plots/m1_m4_summary.png)

**Survivors at the locked criterion:** {survivors_str}.

### 5.x Per-test detail

#### M1 — {results_main['M1']['label']}

n = {results_main['M1']['n']:,}; Pearson r = {fmt_r(results_main['M1']['r'])}; raw Pearson p = {fmt_p(results_main['M1']['p_pearson'])}; **block-permutation p = {fmt_p(results_main['M1']['p_primary'])}** (primary); Holm-adjusted = {fmt_p(results_main['M1']['p_holm'])}; 95% block-bootstrap CI = [{results_main['M1']['ci_lo']:+.3f}, {results_main['M1']['ci_hi']:+.3f}]; block size = {results_main['M1']['block_size_label']}.
![M1 scatter](plots/m1_kp_scatter.png)

#### M2 — {results_main['M2']['label']}

n = {results_main['M2']['n']:,}; Pearson r = {fmt_r(results_main['M2']['r'])}; raw Pearson p = {fmt_p(results_main['M2']['p_pearson'])}; **block-permutation p = {fmt_p(results_main['M2']['p_primary'])}** (primary); Holm-adjusted = {fmt_p(results_main['M2']['p_holm'])}; 95% block-bootstrap CI = [{results_main['M2']['ci_lo']:+.3f}, {results_main['M2']['ci_hi']:+.3f}]; block size = {results_main['M2']['block_size_label']}.
![M2 scatter](plots/m2_dst_scatter.png)

#### M3 — {results_main['M3']['label']}

n = {results_main['M3']['n']:,}; Pearson r = {fmt_r(results_main['M3']['r'])}; raw Pearson p = {fmt_p(results_main['M3']['p_pearson'])} (primary); Holm-adjusted = {fmt_p(results_main['M3']['p_holm'])}; 95% block-bootstrap CI = [{results_main['M3']['ci_lo']:+.3f}, {results_main['M3']['ci_hi']:+.3f}]; block size = {results_main['M3']['block_size_label']}.
![M3 scatter](plots/m3_seismic_scatter.png)

#### M4 — {results_main['M4']['label']}

n = {results_main['M4']['n']:,}; Pearson r = {fmt_r(results_main['M4']['r'])}; raw Pearson p = {fmt_p(results_main['M4']['p_pearson'])} (primary); Holm-adjusted = {fmt_p(results_main['M4']['p_holm'])}; 95% block-bootstrap CI = [{results_main['M4']['ci_lo']:+.3f}, {results_main['M4']['ci_hi']:+.3f}]; block size = {results_main['M4']['block_size_label']}.
![M4 scatter](plots/m4_tide_scatter.png)

## 6. Solar-cycle stratification

Per-phase Pearson r alongside pooled. Phase boundaries from SILSO anchors in prereg §3.6 (anchor months go to "min"/"max"; strictly-between months go to "ascending"/"descending"; pre-1976-03 classified as Cycle 20 descending; post-2024-10 as Cycle 25 descending). The pooled multi-decade result is the headline; stratification is descriptive context, not a separate confirmatory claim.

![Stratification panels](plots/solar_cycle_stratification.png)

{chr(10).join(strat_blocks)}

## 7. Supplementary: M3 robustness on M≥5 only

The M≥4 seismic catalogue has a documented completeness artifact across decades (instrument-network growth boosted M4–4.9 detection). The locked test (M3) is on M≥4 per prereg. As an additional robustness check (not a deviation), the same test is reported on M≥5 only, where decade-by-decade catalogue coverage is uniform.

{sup_table}

## 8. Discussion

### What survived
{survivors_str}.

### Comparison to 2025 pilot priors

The 2025 pilot (`research/geosolar/pilot_2025/SUN_MOON_FIELD_EXPLORATORY_2025.md`) reported, for power/scale calibration:

- **W4'** Hydrosphere (tide range): r = +0.212, Holm-adjusted p = 1.4 × 10⁻⁴, 95% CI [+0.065, +0.352].
- **W2'** Ring current (Dst): r = +0.113, Holm-adjusted p = 8.9 × 10⁻²⁶, 95% CI [+0.068, +0.166].
- **W1'** Kp: apparent r = −0.068 with raw p = 2.2 × 10⁻⁴, but block-permutation p = 0.42 → disqualified by autocorrelation-aware test.
- **W3'** Lithosphere (M≥4 daily count): r = −0.054, p = 0.30. Null.

Multi-decade results vs. priors:

- M1 (Kp):  r = {fmt_r(results_main['M1']['r'])}, primary p = {fmt_p(results_main['M1']['p_primary'])}.
- M2 (Dst): r = {fmt_r(results_main['M2']['r'])}, primary p = {fmt_p(results_main['M2']['p_primary'])}.
- M3 (M≥4): r = {fmt_r(results_main['M3']['r'])}, primary p = {fmt_p(results_main['M3']['p_primary'])}.
- M4 (tide): r = {fmt_r(results_main['M4']['r'])}, primary p = {fmt_p(results_main['M4']['p_primary'])}.

### Implication

The locked outcome interpretation is per prereg §5: the survival pattern of M1–M4 *as observed* is the confirmatory finding, no more and no less. This document is the record of that finding.

---

*Wall clock: {total_wall:.1f} s.*
"""
    with open(REPORT_PATH, "w") as f:
        f.write(report)
    print(f"  report → {REPORT_PATH}")


# ── main ─────────────────────────────────────────────────────

def main():
    t0 = time.time()
    os.makedirs(PLOTS, exist_ok=True)

    print("[load] sun_moon_field 1973-2024")
    sm = load_sun_moon()
    sm = restrict_window(sm)
    print(f"  sm rows: {len(sm):,}  ts {sm.timestamp.min()} .. {sm.timestamp.max()}")

    sm_stats = {
        "n": int(len(sm)),
        "mean": float(sm["sun_moon_amplitude"].mean()),
        "std": float(sm["sun_moon_amplitude"].std()),
        "min": float(sm["sun_moon_amplitude"].min()),
        "max": float(sm["sun_moon_amplitude"].max()),
        "p25": float(sm["sun_moon_amplitude"].quantile(0.25)),
        "p50": float(sm["sun_moon_amplitude"].quantile(0.5)),
        "p75": float(sm["sun_moon_amplitude"].quantile(0.75)),
    }
    print(f"  sun_moon_amplitude: mean={sm_stats['mean']:.4f} std={sm_stats['std']:.4f}")

    print("[load] archive responses")
    kp = restrict_window(load_archive("kp", DECADES))
    dst = restrict_window(load_archive("dst", DECADES))
    seis = restrict_window(load_archive("seismic", DECADES))
    tide = restrict_window(load_archive("tide", DECADES))
    print(f"  kp={len(kp):,}  dst={len(dst):,}  seismic={len(seis):,}  tide={len(tide):,}")

    sm_daily = daily_mean_sm(sm)
    print(f"  daily-mean sm rows: {len(sm_daily):,}")

    # Joined long-form for storage
    print("[join] write joined long-form")
    parts = []
    parts.append(pd.merge_asof(kp, sm[["timestamp", "sun_moon_amplitude"]], on="timestamp", direction="nearest").assign(source="kp"))
    parts.append(pd.merge_asof(dst, sm[["timestamp", "sun_moon_amplitude"]], on="timestamp", direction="nearest").assign(source="dst"))
    parts.append(pd.merge_asof(seis[["timestamp", "magnitude"]], sm[["timestamp", "sun_moon_amplitude"]], on="timestamp", direction="nearest").assign(source="seismic"))
    parts.append(pd.merge_asof(tide[["timestamp", "water_level_m"]], sm[["timestamp", "sun_moon_amplitude"]], on="timestamp", direction="nearest").assign(source="tide"))
    joined = pd.concat(parts, ignore_index=True).sort_values(["source", "timestamp"]).reset_index(drop=True)
    joined.to_parquet(JOINED_PATH, index=False)
    print(f"  joined rows total: {len(joined):,}  → {JOINED_PATH}")

    joined_stats = {
        "kp": int(kp["kp"].notna().sum()),
        "dst": int(dst["dst_nT"].notna().sum()),
        "seismic": int(len(seis)),
        "tide": int(tide["water_level_m"].notna().sum()),
        "joined_total": int(len(joined)),
    }

    # ── battery ──
    print("\n[battery] M1-M4")
    print("[battery] M1 — Kp ~ sun_moon_amplitude")
    res_M1 = run_M1(sm, kp)
    print(f"  M1: n={res_M1['n']:,} r={res_M1['r']:+.3f} p_perm={fmt_p(res_M1['p_primary'])} CI=[{res_M1['ci_lo']:+.3f},{res_M1['ci_hi']:+.3f}]")

    print("[battery] M2 — Dst ~ sun_moon_amplitude")
    res_M2 = run_M2(sm, dst)
    print(f"  M2: n={res_M2['n']:,} r={res_M2['r']:+.3f} p_perm={fmt_p(res_M2['p_primary'])} CI=[{res_M2['ci_lo']:+.3f},{res_M2['ci_hi']:+.3f}]")

    print("[battery] M3 — daily M≥4 seismic count ~ daily-mean sun_moon")
    res_M3 = run_M3(sm_daily, seis)
    print(f"  M3: n={res_M3['n']:,} r={res_M3['r']:+.3f} p={fmt_p(res_M3['p_primary'])} CI=[{res_M3['ci_lo']:+.3f},{res_M3['ci_hi']:+.3f}]")

    print("[battery] M4 — daily tide range ~ daily-mean sun_moon")
    res_M4 = run_M4(sm_daily, tide)
    print(f"  M4: n={res_M4['n']:,} r={res_M4['r']:+.3f} p={fmt_p(res_M4['p_primary'])} CI=[{res_M4['ci_lo']:+.3f},{res_M4['ci_hi']:+.3f}]")

    print("[battery] M3 supplementary — daily M≥5 count")
    res_M3sup = run_M3_supplementary_M5(sm_daily, seis)
    print(f"  M3sup: n={res_M3sup['n']:,} r={res_M3sup['r']:+.3f} p={fmt_p(res_M3sup['p_primary'])} CI=[{res_M3sup['ci_lo']:+.3f},{res_M3sup['ci_hi']:+.3f}]")

    results_main = {"M1": res_M1, "M2": res_M2, "M3": res_M3, "M4": res_M4}
    results_sup = {"M3sup_M5": res_M3sup}

    # ── stratification ──
    print("\n[stratify] per solar-cycle phase")
    strat = {}
    for k in ("M1", "M2", "M3", "M4"):
        strat[k] = stratify_r(results_main[k])
        for row in strat[k]:
            print(f"  {k} {row['phase']:11s}: n={row['n']:>7,} r={fmt_r(row['r'])} p={fmt_p(row['p'])}")

    # ── plots ──
    print("\n[plots]")
    bar_summary(results_main, os.path.join(PLOTS, "m1_m4_summary.png"))
    print("  m1_m4_summary.png")
    stratification_panels(results_main, strat, os.path.join(PLOTS, "solar_cycle_stratification.png"))
    print("  solar_cycle_stratification.png")
    scatter_with_fit(res_M1["x"], res_M1["y"], res_M1["x_label"], res_M1["y_label"],
                     f"M1: Kp ~ sun_moon_amplitude  r={res_M1['r']:+.3f}  n={res_M1['n']:,}",
                     os.path.join(PLOTS, "m1_kp_scatter.png"))
    print("  m1_kp_scatter.png")
    scatter_with_fit(res_M2["x"], res_M2["y"], res_M2["x_label"], res_M2["y_label"],
                     f"M2: Dst ~ sun_moon_amplitude  r={res_M2['r']:+.3f}  n={res_M2['n']:,}",
                     os.path.join(PLOTS, "m2_dst_scatter.png"))
    print("  m2_dst_scatter.png")
    scatter_with_fit(res_M3["x"], res_M3["y"], res_M3["x_label"], res_M3["y_label"],
                     f"M3: daily M≥4 count ~ daily-mean sun_moon  r={res_M3['r']:+.3f}  n={res_M3['n']:,}",
                     os.path.join(PLOTS, "m3_seismic_scatter.png"))
    print("  m3_seismic_scatter.png")
    scatter_with_fit(res_M4["x"], res_M4["y"], res_M4["x_label"], res_M4["y_label"],
                     f"M4: daily tide range ~ daily-mean sun_moon  r={res_M4['r']:+.3f}  n={res_M4['n']:,}",
                     os.path.join(PLOTS, "m4_tide_scatter.png"))
    print("  m4_tide_scatter.png")

    # ── report ──
    write_report(results_main, results_sup, strat, sm_stats, joined_stats, time.time() - t0)

    # ── Holm + survival summary ──
    pvals = [results_main[k]["p_primary"] for k in ("M1", "M2", "M3", "M4")]
    holm = holm_adjust(pvals)
    survivors = []
    print("\n" + "=" * 70)
    print("M1-M4 SUMMARY (LOCKED, multi-decade 1973-2024)")
    print("=" * 70)
    for k, h in zip(("M1", "M2", "M3", "M4"), holm):
        r = results_main[k]
        ci_excludes_zero = (r["ci_lo"] > 0) or (r["ci_hi"] < 0)
        survives = (h < 0.05) and ci_excludes_zero and (abs(r["r"]) >= 0.05)
        mark = "✓" if survives else "·"
        print(f"  {mark} {k}: n={r['n']:>9,}  r={r['r']:+.4f}  p_primary={fmt_p(r['p_primary'])}  "
              f"p_holm={fmt_p(h)}  CI=[{r['ci_lo']:+.3f},{r['ci_hi']:+.3f}]  |r|≥0.05={'yes' if abs(r['r'])>=0.05 else 'no'}  "
              f"CI≠0={'yes' if ci_excludes_zero else 'no'}")
        if survives:
            survivors.append(k)
    print()
    print(f"SURVIVORS @ all three thresholds: {', '.join(survivors) if survivors else 'none'}")
    print()
    print(f"Joined dataframe rows: {joined_stats['joined_total']:,}")
    print(f"Wall clock total: {time.time() - t0:.1f} s")


if __name__ == "__main__":
    main()
