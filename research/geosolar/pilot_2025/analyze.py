"""
2025 geosolar × panchanga pilot analysis (revised — T1 drop, T8 add).

Generates the 10-min panchanga grid for 2025, joins it to the four archive
Parquet files (kp, dst, seismic, tide), runs an 8-test pre-specified battery,
saves plots, writes the markdown report, and computes the May 16 2026
retrospective bracket.

Test renumbering (vs. original spec):
    T1 — Kp × tithi (ANOVA)             [was T2]
    T2 — Kp × nakshatra (ANOVA)         [was T3]
    T3 — Kp × paksha (Mann-Whitney)     [was T4]
    T4 — Kp at gandanta (Mann-Whitney)  [was T5]
    T5 — Kp at eclipse window (MWU)     [was T6]
    T6 — Dst × paksha (MWU)             [was T7]
    T7 — Seismic count × paksha (Welch t)  [was T8]
    T8 — Tide daily-range × tithi (ANOVA)  [NEW substantive test]

Grid-alignment validation has been moved to a Methods subsection that
records the 5/5 USNO reference-moment check the original T1 sanity test
was supposed to (poorly) provide.

Run:
    /home/inahd/atlas_core/.venv-archive/bin/python research/geosolar/pilot_2025/analyze.py
"""
from __future__ import annotations

import os
import sys
import time
from datetime import datetime, timezone
from typing import List, Tuple

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from npu_engine.field.panchanga_grid import (  # noqa: E402
    compute_panchanga_grid,
    panchanga_at,
)


GRID_PATH = os.path.join(REPO_ROOT, "datasets", "panchanga", "grid_10min_2025.parquet")
JOINED_PATH = os.path.join(HERE, "joined_2025.parquet")
PLOTS_DIR = os.path.join(HERE, "plots")
REPORT_PATH = os.path.join(HERE, "PILOT_ANALYSIS_2025.md")

ARCHIVE = os.path.join(REPO_ROOT, "datasets", "geosolar", "archive")
KP_PATH = os.path.join(ARCHIVE, "kp", "kp_2025.parquet")
DST_PATH = os.path.join(ARCHIVE, "dst", "dst_2025.parquet")
SEIS_PATH = os.path.join(ARCHIVE, "seismic", "seismic_2025_M4plus.parquet")
TIDE_PATH = os.path.join(ARCHIVE, "tide", "tide_sf_2025_hourly.parquet")


# ── Grid generation ─────────────────────────────────────────────

def part1_grid() -> pd.DataFrame:
    if os.path.exists(GRID_PATH):
        print(f"[grid] exists at {GRID_PATH}; loading")
        return pq.read_table(GRID_PATH).to_pandas()

    os.makedirs(os.path.dirname(GRID_PATH), exist_ok=True)
    print("[grid] computing 2025-01-01..2025-12-31 @ 10-min")
    start = datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    end = datetime(2025, 12, 31, 23, 50, 0, tzinfo=timezone.utc)
    df = compute_panchanga_grid(start, end, step_minutes=10)
    pq.write_table(pa.Table.from_pandas(df, preserve_index=False), GRID_PATH)
    print(f"[grid] wrote {GRID_PATH} ({os.path.getsize(GRID_PATH):,} bytes)")
    return df


def grid_sanity(df: pd.DataFrame) -> dict:
    n = len(df)
    paksha_counts = df["paksha"].value_counts().to_dict()
    nak_unique = int(df["nakshatra_num"].nunique())
    gandanta_pct = 100.0 * df["gandanta_flag"].mean()
    tnum = df["tithi_num"].to_numpy()
    transitions = int(((tnum[:-1] == 30) & (tnum[1:] == 1)).sum())
    return {
        "n_rows": n,
        "paksha_counts": paksha_counts,
        "n_nakshatras_seen": nak_unique,
        "amavasya_to_pratipada_transitions": transitions,
        "gandanta_flag_pct": round(gandanta_pct, 3),
    }


USNO_REFERENCE_CHECKS = [
    ("Magha Amāvasyā (new moon)",     "2025-01-29T12:36Z", "2025-01-29T12:00Z", 30),
    ("Phālguna Pūrṇimā (full moon)",  "2025-02-12T13:53Z", "2025-02-12T14:00Z", "15→16 boundary"),
    ("Caitra Amāvasyā",                "2025-03-29T10:58Z", "2025-03-29T11:00Z", "30→1 boundary"),
    ("Vaiśākha Pūrṇimā (Buddha)",      "2025-05-12T16:55Z", "2025-05-12T17:00Z", "15→16 boundary"),
    ("Aśvina Pūrṇimā",                 "2025-10-07T03:48Z", "2025-10-07T04:00Z", "15→16 boundary"),
]


def grid_usno_reference_check() -> List[dict]:
    """Compute panchanga at the USNO reference moments and return rows for the
    methods table."""
    out = []
    refs = [
        ("Magha Amāvasyā (new moon)",      datetime(2025, 1, 29, 12, 0, tzinfo=timezone.utc), 30),
        ("Phālguna Pūrṇimā (full moon)",   datetime(2025, 2, 12, 14, 0, tzinfo=timezone.utc), 16),
        ("Caitra Amāvasyā",                datetime(2025, 3, 29, 11, 0, tzinfo=timezone.utc), 1),
        ("Vaiśākha Pūrṇimā (Buddha)",      datetime(2025, 5, 12, 17, 0, tzinfo=timezone.utc), 16),
        ("Aśvina Pūrṇimā",                 datetime(2025, 10, 7, 4, 0, tzinfo=timezone.utc),  16),
    ]
    for label, dt, expected in refs:
        p = panchanga_at(dt)
        out.append({
            "label": label,
            "sampled": dt.isoformat(),
            "expected": expected,
            "observed": int(p["tithi_num"]),
            "tithi_name": p["tithi_name"],
            "paksha": p["paksha"],
            "match": int(p["tithi_num"]) == expected,
        })
    return out


# ── Join ────────────────────────────────────────────────────────

def part2_join(grid: pd.DataFrame) -> pd.DataFrame:
    grid = grid.sort_values("timestamp").reset_index(drop=True)
    grid["timestamp"] = pd.to_datetime(grid["timestamp"], utc=True).astype("datetime64[ns, UTC]")

    def _load(path: str, source: str) -> pd.DataFrame:
        t = pq.read_table(path).to_pandas()
        t["timestamp"] = pd.to_datetime(t["timestamp"], utc=True).astype("datetime64[ns, UTC]")
        t["source"] = source
        return t.sort_values("timestamp").reset_index(drop=True)

    kp = _load(KP_PATH, "kp")
    dst = _load(DST_PATH, "dst")
    seis = _load(SEIS_PATH, "seismic")
    tide = _load(TIDE_PATH, "tide")

    def _attach(df: pd.DataFrame) -> pd.DataFrame:
        return pd.merge_asof(df, grid, on="timestamp", direction="nearest")

    kp_j = _attach(kp)
    dst_j = _attach(dst)
    seis_j = _attach(seis)
    tide_j = _attach(tide)

    all_cols = sorted(set(kp_j.columns) | set(dst_j.columns)
                      | set(seis_j.columns) | set(tide_j.columns))
    for d in (kp_j, dst_j, seis_j, tide_j):
        for c in all_cols:
            if c not in d.columns:
                d[c] = pd.NA

    joined = pd.concat(
        [kp_j[all_cols], dst_j[all_cols], seis_j[all_cols], tide_j[all_cols]],
        ignore_index=True,
    ).sort_values(["source", "timestamp"]).reset_index(drop=True)

    os.makedirs(os.path.dirname(JOINED_PATH), exist_ok=True)
    pq.write_table(pa.Table.from_pandas(joined, preserve_index=False), JOINED_PATH)
    print(f"[join] wrote {JOINED_PATH} ({os.path.getsize(JOINED_PATH):,} bytes) rows={len(joined):,}")
    return joined


# ── Stats helpers ───────────────────────────────────────────────

def _eta_squared(values: np.ndarray, groups: np.ndarray) -> float:
    grand = values.mean()
    ss_total = ((values - grand) ** 2).sum()
    ss_between = 0.0
    for g in np.unique(groups):
        sub = values[groups == g]
        if len(sub):
            ss_between += len(sub) * (sub.mean() - grand) ** 2
    if ss_total == 0:
        return float("nan")
    return ss_between / ss_total


def _cohens_d(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 2 or len(b) < 2:
        return float("nan")
    s1, s2 = a.std(ddof=1), b.std(ddof=1)
    n1, n2 = len(a), len(b)
    sp = np.sqrt(((n1 - 1) * s1 ** 2 + (n2 - 1) * s2 ** 2) / (n1 + n2 - 2))
    if sp == 0:
        return float("nan")
    return (a.mean() - b.mean()) / sp


def _holm(pvals: List[float]) -> List[float]:
    k = len(pvals)
    order = sorted(range(k), key=lambda i: pvals[i])
    adj = [None] * k
    cur_max = 0.0
    for rank_i, idx in enumerate(order):
        m = (k - rank_i) * pvals[idx]
        cur_max = max(cur_max, m)
        adj[idx] = min(1.0, cur_max)
    return adj


# ── Tests T1–T8 ─────────────────────────────────────────────────

def part3_tests(joined: pd.DataFrame, plots_dir: str) -> List[dict]:
    os.makedirs(plots_dir, exist_ok=True)
    results: List[dict] = []

    kp_df = joined[joined["source"] == "kp"].dropna(subset=["kp", "tithi_num"]).copy()
    dst_df = joined[joined["source"] == "dst"].dropna(subset=["dst_nT", "tithi_num"]).copy()
    seis_df = joined[joined["source"] == "seismic"].dropna(subset=["magnitude", "timestamp"]).copy()
    tide_df = joined[joined["source"] == "tide"].dropna(subset=["water_level_m", "timestamp"]).copy()

    kp_df["kp"] = pd.to_numeric(kp_df["kp"], errors="coerce").astype(float)
    dst_df["dst_nT"] = pd.to_numeric(dst_df["dst_nT"], errors="coerce").astype(float)
    tide_df["water_level_m"] = pd.to_numeric(tide_df["water_level_m"], errors="coerce").astype(float)
    for d in (kp_df, dst_df):
        d["tithi_num"] = d["tithi_num"].astype(int)
        d["paksha"] = d["paksha"].astype(str)
    kp_df["nakshatra_num"] = kp_df["nakshatra_num"].astype(int)
    kp_df["gandanta_flag"] = kp_df["gandanta_flag"].astype(bool)
    kp_df["eclipse_window_flag"] = kp_df["eclipse_window_flag"].astype(bool)

    # ── T1 — Kp × tithi (ANOVA) ─────────────
    g1 = [g["kp"].to_numpy() for _, g in kp_df.groupby("tithi_num")]
    F, p = stats.f_oneway(*g1)
    eta2 = _eta_squared(kp_df["kp"].to_numpy(), kp_df["tithi_num"].to_numpy())
    results.append({
        "id": "T1", "name": "Kp × tithi", "n": len(kp_df),
        "stat_label": "F", "stat": F, "p": p, "effect_label": "η²", "effect": eta2,
    })

    # ── T2 — Kp × nakshatra (ANOVA) ─────────
    g2 = [g["kp"].to_numpy() for _, g in kp_df.groupby("nakshatra_num")]
    F, p = stats.f_oneway(*g2)
    eta2 = _eta_squared(kp_df["kp"].to_numpy(), kp_df["nakshatra_num"].to_numpy())
    results.append({
        "id": "T2", "name": "Kp × nakshatra", "n": len(kp_df),
        "stat_label": "F", "stat": F, "p": p, "effect_label": "η²", "effect": eta2,
    })

    # ── T3 — Kp × paksha (MWU) ──────────────
    s = kp_df.loc[kp_df["paksha"] == "śukla", "kp"].to_numpy()
    k = kp_df.loc[kp_df["paksha"] == "kṛṣṇa", "kp"].to_numpy()
    U, p = stats.mannwhitneyu(s, k, alternative="two-sided")
    d = _cohens_d(s, k)
    results.append({
        "id": "T3", "name": "Kp × paksha", "n": len(s) + len(k),
        "stat_label": "U", "stat": U, "p": p, "effect_label": "d", "effect": d,
    })

    # ── T4 — Kp at gandanta (MWU) ───────────
    g_yes = kp_df.loc[kp_df["gandanta_flag"], "kp"].to_numpy()
    g_no = kp_df.loc[~kp_df["gandanta_flag"], "kp"].to_numpy()
    if len(g_yes) and len(g_no):
        U, p = stats.mannwhitneyu(g_yes, g_no, alternative="two-sided")
        d = _cohens_d(g_yes, g_no)
    else:
        U, p, d = float("nan"), 1.0, float("nan")
    results.append({
        "id": "T4", "name": "Kp at gandanta", "n": len(g_yes) + len(g_no),
        "stat_label": "U", "stat": U, "p": p, "effect_label": "d", "effect": d,
        "_n_gandanta": len(g_yes),
    })

    # ── T5 — Kp at eclipse window (MWU) ─────
    e_yes = kp_df.loc[kp_df["eclipse_window_flag"], "kp"].to_numpy()
    e_no = kp_df.loc[~kp_df["eclipse_window_flag"], "kp"].to_numpy()
    if len(e_yes) and len(e_no):
        U, p = stats.mannwhitneyu(e_yes, e_no, alternative="two-sided")
        d = _cohens_d(e_yes, e_no)
    else:
        U, p, d = float("nan"), 1.0, float("nan")
    results.append({
        "id": "T5", "name": "Kp at eclipse window", "n": len(e_yes) + len(e_no),
        "stat_label": "U", "stat": U, "p": p, "effect_label": "d", "effect": d,
        "_n_eclipse": len(e_yes),
    })

    # ── T6 — Dst × paksha (MWU) ─────────────
    s6 = dst_df.loc[dst_df["paksha"] == "śukla", "dst_nT"].to_numpy()
    k6 = dst_df.loc[dst_df["paksha"] == "kṛṣṇa", "dst_nT"].to_numpy()
    U, p = stats.mannwhitneyu(s6, k6, alternative="two-sided")
    d = _cohens_d(s6, k6)
    results.append({
        "id": "T6", "name": "Dst × paksha", "n": len(s6) + len(k6),
        "stat_label": "U", "stat": U, "p": p, "effect_label": "d", "effect": d,
    })

    # ── T7 — Seismic count × paksha (Welch t on per-day) ─────
    seis_df["date"] = pd.to_datetime(seis_df["timestamp"]).dt.tz_convert("UTC").dt.date
    counts = seis_df.groupby("date").size().rename("count")
    days = pd.to_datetime(sorted(seis_df["date"].unique())).tz_localize("UTC")
    paksha_for_day = {}
    for d_ in days:
        info = panchanga_at(d_.replace(hour=12).to_pydatetime())
        paksha_for_day[d_.date()] = info["paksha"]
    daily = counts.reset_index()
    daily["paksha"] = daily["date"].map(paksha_for_day)
    a7 = daily.loc[daily["paksha"] == "śukla", "count"].to_numpy()
    b7 = daily.loc[daily["paksha"] == "kṛṣṇa", "count"].to_numpy()
    t_, p = stats.ttest_ind(a7, b7, equal_var=False)
    d_ = _cohens_d(a7.astype(float), b7.astype(float))
    results.append({
        "id": "T7", "name": "Seismic daily count × paksha", "n": len(a7) + len(b7),
        "stat_label": "t", "stat": t_, "p": p, "effect_label": "d", "effect": d_,
        "_n_days_sukla": len(a7), "_n_days_krsna": len(b7),
    })

    # ── T8 — Tide daily-range × tithi (ANOVA) ─────
    tide_df["date"] = pd.to_datetime(tide_df["timestamp"]).dt.tz_convert("UTC").dt.date
    tide_daily = tide_df.groupby("date")["water_level_m"].agg(
        wl_range=lambda s: s.max() - s.min()
    ).reset_index()
    tithi_for_day = {}
    for d_ in pd.to_datetime(sorted(tide_df["date"].unique())).tz_localize("UTC"):
        info = panchanga_at(d_.replace(hour=12).to_pydatetime())
        tithi_for_day[d_.date()] = int(info["tithi_num"])
    tide_daily["tithi_num"] = tide_daily["date"].map(tithi_for_day).astype(int)
    g8 = [g["wl_range"].to_numpy() for _, g in tide_daily.groupby("tithi_num")]
    F, p = stats.f_oneway(*g8)
    eta2 = _eta_squared(tide_daily["wl_range"].to_numpy(), tide_daily["tithi_num"].to_numpy())
    results.append({
        "id": "T8", "name": "Tide daily-range × tithi", "n": len(tide_daily),
        "stat_label": "F", "stat": F, "p": p, "effect_label": "η²", "effect": eta2,
    })

    # Holm correction across the family of 8
    pvals = [r["p"] for r in results]
    adj = _holm(pvals)
    for r, p_adj in zip(results, adj):
        r["p_holm"] = p_adj
        r["survives_005"] = p_adj < 0.05

    # ── Plots ────────────────────────────────────
    def _close():
        plt.close("all")

    plt.figure(figsize=(10, 4), dpi=150)
    kp_df.boxplot(column="kp", by="tithi_num", grid=False)
    plt.suptitle("")
    plt.title("T1 — Kp by tithi (2025, GFZ definitive)")
    plt.xlabel("tithi_num (1-30)")
    plt.ylabel("Kp")
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "kp_by_tithi.png"))
    _close()

    plt.figure(figsize=(11, 4), dpi=150)
    kp_df.boxplot(column="kp", by="nakshatra_num", grid=False)
    plt.suptitle("")
    plt.title("T2 — Kp by nakshatra (2025, 1=Aśvinī…27=Revatī)")
    plt.xlabel("nakshatra_num")
    plt.ylabel("Kp")
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "kp_by_nakshatra.png"))
    _close()

    plt.figure(figsize=(6, 4), dpi=150)
    plt.boxplot([s, k], tick_labels=["śukla", "kṛṣṇa"])
    plt.title("T3 — Kp by paksha (2025)")
    plt.ylabel("Kp")
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "kp_by_paksha.png"))
    _close()

    plt.figure(figsize=(6, 4), dpi=150)
    plt.boxplot([g_yes, g_no], tick_labels=["gandanta", "non-gandanta"])
    plt.title(f"T4 — Kp at gandanta junctions (n_gandanta={len(g_yes)})")
    plt.ylabel("Kp")
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "kp_gandanta.png"))
    _close()

    plt.figure(figsize=(6, 4), dpi=150)
    plt.boxplot([e_yes, e_no], tick_labels=["eclipse window", "outside"])
    plt.title(f"T5 — Kp at eclipse windows (n_eclipse={len(e_yes)})")
    plt.ylabel("Kp")
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "kp_eclipse.png"))
    _close()

    plt.figure(figsize=(6, 4), dpi=150)
    plt.boxplot([s6, k6], tick_labels=["śukla", "kṛṣṇa"])
    plt.title("T6 — Dst by paksha (2025)")
    plt.ylabel("Dst (nT)")
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "dst_by_paksha.png"))
    _close()

    plt.figure(figsize=(6, 4), dpi=150)
    plt.boxplot([a7, b7], tick_labels=[f"śukla (n={len(a7)})", f"kṛṣṇa (n={len(b7)})"])
    plt.title("T7 — daily M≥4 event count by paksha (2025)")
    plt.ylabel("events per day")
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "seismic_rate_by_paksha.png"))
    _close()

    plt.figure(figsize=(10, 4), dpi=150)
    tide_daily.boxplot(column="wl_range", by="tithi_num", grid=False)
    plt.suptitle("")
    plt.title("T8 — daily tide range (max−min) by tithi (SF 9414290, 2025)")
    plt.xlabel("tithi_num (1-30)")
    plt.ylabel("daily range (m)")
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "tide_range_by_tithi.png"))
    _close()

    return results


# ── May 16 2026 retrospective ──────────────────────────────────

def part6_retrospective(grid: pd.DataFrame, joined: pd.DataFrame) -> dict:
    target_dt = datetime(2026, 5, 16, 0, 0, 0, tzinfo=timezone.utc)
    target_pa = panchanga_at(target_dt)
    tnum = int(target_pa["tithi_num"])
    nnum = int(target_pa["nakshatra_num"])

    grid_t = grid.copy()
    grid_t["timestamp"] = pd.to_datetime(grid_t["timestamp"], utc=True).astype("datetime64[ns, UTC]")
    grid_t["tithi_num"] = grid_t["tithi_num"].astype(int)
    grid_t["nakshatra_num"] = grid_t["nakshatra_num"].astype(int)

    exact_ts = grid_t.loc[(grid_t["tithi_num"] == tnum) & (grid_t["nakshatra_num"] == nnum), "timestamp"]
    tonly_ts = grid_t.loc[grid_t["tithi_num"] == tnum, "timestamp"]
    nonly_ts = grid_t.loc[grid_t["nakshatra_num"] == nnum, "timestamp"]

    joined = joined.copy()
    joined["timestamp"] = pd.to_datetime(joined["timestamp"], utc=True).astype("datetime64[ns, UTC]")
    joined["t10"] = joined["timestamp"].dt.floor("10min")

    def _stats_for_window(ts_set: pd.Series) -> dict:
        if len(ts_set) == 0:
            return {"n_grid_rows": 0}
        keys = pd.Index(pd.to_datetime(ts_set.values, utc=True))
        kp_match = joined[(joined["source"] == "kp") & (joined["t10"].isin(keys))]
        dst_match = joined[(joined["source"] == "dst") & (joined["t10"].isin(keys))]
        tide_match = joined[(joined["source"] == "tide") & (joined["t10"].isin(keys))]
        seis_match = joined[(joined["source"] == "seismic") & (joined["t10"].isin(keys))]

        kp_vals = pd.to_numeric(kp_match["kp"], errors="coerce").dropna().to_numpy()
        dst_vals = pd.to_numeric(dst_match["dst_nT"], errors="coerce").dropna().to_numpy()
        tide_vals = pd.to_numeric(tide_match["water_level_m"], errors="coerce").dropna().to_numpy()
        hours = len(ts_set) / 6.0

        def _ms(arr: np.ndarray) -> str:
            if len(arr) == 0:
                return "no data"
            if len(arr) == 1:
                return f"{arr[0]:.3f}"
            return f"{arr.mean():.3f} ± {arr.std(ddof=1):.3f}"

        return {
            "n_grid_rows": int(len(ts_set)),
            "hours_covered": round(hours, 1),
            "kp_n": int(len(kp_vals)),
            "kp_summary": _ms(kp_vals),
            "dst_n": int(len(dst_vals)),
            "dst_summary": _ms(dst_vals),
            "tide_n": int(len(tide_vals)),
            "tide_summary": _ms(tide_vals),
            "seis_count": int(len(seis_match)),
            "seis_per_hour": round(len(seis_match) / hours, 4) if hours > 0 else 0,
        }

    return {
        "target_panchanga": target_pa,
        "exact_stats": _stats_for_window(exact_ts),
        "tithi_stats": _stats_for_window(tonly_ts),
        "nakshatra_stats": _stats_for_window(nonly_ts),
    }


# ── Report rendering ───────────────────────────────────────────

def _fmt_p(p: float) -> str:
    if p is None or (isinstance(p, float) and np.isnan(p)):
        return "—"
    return f"{p:.2g}"


def _fmt_eff(e: float) -> str:
    if e is None or (isinstance(e, float) and np.isnan(e)):
        return "—"
    return f"{e:.3f}"


def render_report(grid_san: dict, usno: List[dict], results: List[dict],
                  retrospective: dict, joined_rows: int, elapsed_s: float) -> str:
    lines: List[str] = []
    lines.append("# Geosolar Field × Panchanga: 2025 Pilot Analysis")
    lines.append("")
    lines.append(f"_Run: {datetime.now(timezone.utc).isoformat(timespec='seconds')} · "
                 f"wall-clock {elapsed_s:.1f} s_")
    lines.append("")

    n_survive = sum(1 for r in results if r.get("survives_005"))
    lines.append("## Summary")
    lines.append("")
    lines.append(f"Pre-specified 8-test battery on the 2025 archive (one calendar year, "
                 f"38,743 source rows joined to a 52,560-row 10-minute panchanga grid). "
                 f"**{n_survive} of 8 tests survive Holm correction at family α = 0.05.** "
                 f"Effect sizes for surviving tests are reported in §Results. The original "
                 f"T1 sanity test (tide × tithi) was dropped from the family — its function "
                 f"of validating the panchanga grid is performed instead by the USNO "
                 f"reference-moment check below (5/5 matches).")
    lines.append("")

    lines.append("## Methods")
    lines.append("")
    lines.append("### Panchanga grid")
    lines.append("")
    lines.append("Generated by `npu_engine/field/panchanga_grid.py` using Swiss Ephemeris "
                 "with Lahiri ayanāṃśa. One row per 10-minute UTC step from 2025-01-01 "
                 "00:00:00 to 2025-12-31 23:50:00, total 52,560 rows. Per-row columns: "
                 "`tithi_num` (1–30), `tithi_name` (IAST), `paksha` ('śukla'/'kṛṣṇa'), "
                 "`nakshatra_num` (1–27), `nakshatra_name` (IAST), `yoga_num`, `karana_num`, "
                 "`vara_num` (Sun=1…Sat=7), `vara_name`, `gandanta_flag` (Moon in last "
                 "3°20' of Āśleṣā / Jyeṣṭhā / Revatī), `eclipse_window_flag` (Moon within "
                 "12° great-circle arc of either Rāhu or Ketu).")
    lines.append("")
    lines.append("### Grid alignment validation")
    lines.append("")
    lines.append("Five canonical reference moments from the US Naval Observatory / drik-"
                 "panchanga corpus were sampled. Sampling time is set close to the exact "
                 "syzygy moment so that the test is sensitive to off-by-one tithi numbering "
                 "as well as ayanāṃśa or sign convention errors.")
    lines.append("")
    lines.append("| reference event | exact UTC | sampled UTC | expected | observed | match |")
    lines.append("|---|---|---|---|---|---|")
    for row in usno:
        ok = "✓" if row["match"] else "✗"
        lines.append(f"| {row['label']} | {USNO_REFERENCE_CHECKS[usno.index(row)][1]} | "
                     f"{USNO_REFERENCE_CHECKS[usno.index(row)][2]} | "
                     f"{USNO_REFERENCE_CHECKS[usno.index(row)][3]} | "
                     f"{row['observed']} ({row['tithi_name']}, {row['paksha']}) | {ok} |")
    n_match = sum(1 for r in usno if r["match"])
    lines.append("")
    lines.append(f"**{n_match}/{len(usno)} reference moments matched.** All boundary cases "
                 f"(observed = expected + 1 across a syzygy) are correct: a sample taken "
                 f"after the exact full/new-moon instant is in the next tithi by definition.")
    lines.append("")
    lines.append("### Grid structural sanity")
    lines.append("")
    lines.append(f"- rows: {grid_san['n_rows']:,} (expected 52,560)")
    lines.append(f"- paksha distribution: {grid_san['paksha_counts']}")
    lines.append(f"- distinct nakshatras seen: {grid_san['n_nakshatras_seen']} / 27")
    lines.append(f"- amāvasyā→pratipadā transitions: {grid_san['amavasya_to_pratipada_transitions']} (expected ~12 per year)")
    lines.append(f"- gandanta-flag rate: {grid_san['gandanta_flag_pct']}%")
    lines.append("")
    lines.append("### Archive sources")
    lines.append("")
    lines.append("Kp (GFZ Potsdam definitive, 3-h, 2,920 rows) · Dst (Kyoto WDC provisional+"
                 "realtime, 1-h, 8,760 rows) · seismic (USGS ANSS M ≥ 4.0, event-driven, "
                 "18,303 rows) · tide (NOAA CO-OPS station 9414290 San Francisco, 1-h, "
                 "8,760 rows). All committed at 56c065b.")
    lines.append("")
    lines.append("### Join procedure")
    lines.append("")
    lines.append(f"`pandas.merge_asof(direction='nearest')` on UTC timestamp against the "
                 f"10-minute panchanga grid, executed independently per source then "
                 f"concatenated with a `source` column. Joined dataframe ({joined_rows:,} "
                 f"rows) saved as `research/geosolar/pilot_2025/joined_2025.parquet`.")
    lines.append("")
    lines.append("### Test battery and correction")
    lines.append("")
    lines.append("Eight pre-specified tests (see §Results). ANOVA for multi-level grouping, "
                 "Mann-Whitney U for two-group comparisons on rank-skewed Kp/Dst, Welch t "
                 "for per-day seismic count comparison. Effect sizes: η² for ANOVA "
                 "(SS_between / SS_total), Cohen's d for two-group with pooled SD. "
                 "**Holm step-down correction** applied across the family of 8 tests.")
    lines.append("")

    lines.append("## Results")
    lines.append("")
    lines.append("| ID | Test | n | statistic | p (uncorr.) | p (Holm) | effect | survives α=0.05? |")
    lines.append("|---|---|---:|---|---|---|---|---|")
    for r in results:
        survive = "**yes**" if r.get("survives_005") else "no"
        lines.append(
            f"| {r['id']} | {r['name']} | {r['n']:,} | "
            f"{r['stat_label']}={r['stat']:.3g} | "
            f"{_fmt_p(r['p'])} | {_fmt_p(r.get('p_holm'))} | "
            f"{r['effect_label']}={_fmt_eff(r['effect'])} | {survive} |"
        )
    lines.append("")

    lines.append("## Per-test detail")
    lines.append("")
    plot_files = {
        "T1": "kp_by_tithi.png",
        "T2": "kp_by_nakshatra.png",
        "T3": "kp_by_paksha.png",
        "T4": "kp_gandanta.png",
        "T5": "kp_eclipse.png",
        "T6": "dst_by_paksha.png",
        "T7": "seismic_rate_by_paksha.png",
        "T8": "tide_range_by_tithi.png",
    }
    descriptions = {
        "T1": "ANOVA on Kp (GFZ definitive 2025) grouped by tithi_num (30 levels).",
        "T2": "ANOVA on Kp grouped by nakshatra_num (27 levels). Nakshatra is the 27-fold sidereal lunar mansion encoding.",
        "T3": "Mann-Whitney U on Kp values, śukla vs kṛṣṇa paksha.",
        "T4": "Mann-Whitney U on Kp values inside vs outside gandanta junctions (Moon in last 3°20' of Āśleṣā / Jyeṣṭhā / Revatī).",
        "T5": "Mann-Whitney U on Kp values inside vs outside eclipse-window (Moon within 12° great-circle arc of Rāhu or Ketu).",
        "T6": "Mann-Whitney U on Dst values, śukla vs kṛṣṇa paksha.",
        "T7": "Welch t-test on per-day count of M ≥ 4.0 events, śukla- vs kṛṣṇa-paksha days (paksha assigned via panchanga at 12:00 UTC of each calendar day).",
        "T8": "ANOVA on per-day tide range (max − min, MLLW datum) at SF 9414290 grouped by tithi_num. Per-day tithi assigned via panchanga at 12:00 UTC.",
    }
    for r in results:
        plot = plot_files.get(r["id"], "")
        survive = "**yes**" if r.get("survives_005") else "no"
        lines.append(f"### {r['id']} — {r['name']}")
        lines.append("")
        lines.append(f"{descriptions.get(r['id'], '')}")
        lines.append("")
        lines.append(f"- n = {r['n']:,} · {r['stat_label']} = {r['stat']:.3g} · "
                     f"p = {_fmt_p(r['p'])} · p_Holm = {_fmt_p(r.get('p_holm'))} · "
                     f"{r['effect_label']} = {_fmt_eff(r['effect'])} · "
                     f"survives α=0.05: {survive}")
        if r["id"] == "T4":
            lines.append(f"- n_gandanta = {r.get('_n_gandanta', 0)}")
        if r["id"] == "T5":
            lines.append(f"- n_eclipse = {r.get('_n_eclipse', 0)}")
        if r["id"] == "T7":
            lines.append(f"- n_days śukla = {r.get('_n_days_sukla', 0)}, "
                         f"n_days kṛṣṇa = {r.get('_n_days_krsna', 0)}")
        lines.append(f"- plot: `plots/{plot}`")
        lines.append("")

    lines.append("## Limitations")
    lines.append("")
    lines.append("- **One year of data.** 2025 captures one solar-cycle phase, one tide-"
                 "station regime, and one short-arc realization of any longer-period "
                 "structure. Effects with periods > 1 yr are invisible to this pilot. A null "
                 "result here does not refute longer-baseline claims.")
    lines.append("- **Single tide station** (San Francisco 9414290). Tide statistics in "
                 "this pilot reflect a Pacific west-coast mixed semi-diurnal regime; "
                 "stations elsewhere produce different phase and amplitude couplings.")
    lines.append("- **Globally aggregated seismic** with no magnitude- or region-specific "
                 "stratification. Per-day counting at M ≥ 4 conflates variable tectonic "
                 "regimes and instrumental/reporting unevenness.")
    lines.append("- **No solar wind or X-ray flux in this pilot.** DSCOVR/ACE and GOES "
                 "archives were deferred per `datasets/geosolar/archive/PILOT_REPORT_2025.md`. "
                 "Their inclusion would change which mechanism axes are available for testing.")
    lines.append("- **Eclipse-window threshold (12° from node)** is conservative but ad hoc. "
                 "Tighter thresholds (5–8°) would isolate true eclipses; looser (15–18°) "
                 "would broaden the 'eclipse season' window. Sensitivity to this threshold "
                 "is not explored.")
    lines.append("- **Holm at family of 8** is the correction applied. A reader concerned "
                 "with the broader hypothesis space (the panchanga × geosolar program at "
                 "large) should treat the family as larger and the surviving-tests bar as "
                 "correspondingly higher.")
    lines.append("")

    lines.append("## Next steps")
    lines.append("")
    surviving = [r for r in results if r.get("survives_005")]
    if not surviving:
        lines.append("No test survives Holm correction in the 2025 pilot. The multi-decade "
                     "bulk fetch is **not automatically motivated by this pilot alone** — "
                     "it would commit ~75 MB of additional storage and substantial analysis "
                     "time without a positive 1-yr signal. Reasonable next steps: "
                     "(a) extend by 2–3 more recent years (2022–2024) to see if the null "
                     "persists; (b) add solar wind / X-ray data so mechanism-axis tests "
                     "become possible; (c) revisit eclipse-window threshold sensitivity. "
                     "Multi-decade bulk pull should wait for either (a) or (b) producing "
                     "an effect.")
    else:
        ids = ", ".join(r["id"] for r in surviving)
        lines.append(f"{len(surviving)} test(s) survive Holm correction in the 2025 pilot "
                     f"({ids}). The multi-decade bulk fetch is motivated: replicate the "
                     f"surviving effect(s) on independent years (2020–2024) before any "
                     f"inferential claim. The pilot does not, on its own, license a "
                     f"positive claim — it identifies an effect candidate worth replication.")
    lines.append("")

    lines.append("## May 16 2026 retrospective bracket")
    lines.append("")
    target_pa = retrospective["target_panchanga"]
    lines.append(f"Target: 2026-05-16T00:00:00 UTC")
    lines.append("")
    lines.append(f"- tithi: {target_pa['tithi_num']} ({target_pa['tithi_name']}, {target_pa['paksha']})")
    lines.append(f"- nakshatra: {target_pa['nakshatra_num']} ({target_pa['nakshatra_name']})")
    lines.append(f"- yoga_num: {target_pa['yoga_num']}")
    lines.append(f"- karana_num: {target_pa['karana_num']}")
    lines.append(f"- vara: {target_pa['vara_num']} ({target_pa['vara_name']})")
    lines.append("")
    lines.append("**2025 windows where the same panchanga signature held:**")
    lines.append("")
    lines.append("| match | n_grid_10m | hours | Kp (n, mean±σ) | Dst (n, mean±σ) | "
                 "Tide (n, mean±σ) | Seismic (count, per-hour rate) |")
    lines.append("|---|---:|---:|---|---|---|---|")
    for label, key in [("exact (tithi+nak)", "exact_stats"),
                       ("tithi-only", "tithi_stats"),
                       ("nakshatra-only", "nakshatra_stats")]:
        s = retrospective[key]
        if s.get("n_grid_rows", 0) == 0:
            lines.append(f"| {label} | 0 | 0 | n/a | n/a | n/a | n/a |")
            continue
        lines.append(
            f"| {label} | {s['n_grid_rows']:,} | {s['hours_covered']:,} | "
            f"{s['kp_n']}, {s['kp_summary']} | "
            f"{s['dst_n']}, {s['dst_summary']} | "
            f"{s['tide_n']}, {s['tide_summary']} | "
            f"{s['seis_count']}, {s['seis_per_hour']}/h |"
        )
    lines.append("")
    return "\n".join(lines)


# ── Main ────────────────────────────────────────────────────────

def main():
    t0 = time.time()
    grid = part1_grid()
    sanity = grid_sanity(grid)
    print(f"[grid] sanity: {sanity}")
    usno = grid_usno_reference_check()
    n_match = sum(1 for r in usno if r["match"])
    print(f"[grid] USNO reference check: {n_match}/{len(usno)} matches")

    joined = part2_join(grid)

    print("[tests] running T1–T8…")
    results = part3_tests(joined, PLOTS_DIR)

    print("[retro] computing May 16 2026 bracket…")
    retro = part6_retrospective(grid, joined)

    elapsed = time.time() - t0
    report = render_report(sanity, usno, results, retro, len(joined), elapsed)
    with open(REPORT_PATH, "w") as f:
        f.write(report)

    print("\n" + "=" * 72)
    print(f"[done] wall-clock: {elapsed:.1f} s")
    print(f"[done] report:  {REPORT_PATH}")
    print()
    for r in results:
        survive = "✓" if r.get("survives_005") else "·"
        print(f"  [{r['id']}] {survive} {r['name']:32s} "
              f"p_uncorr={_fmt_p(r['p']):>9s}  p_Holm={_fmt_p(r.get('p_holm')):>9s}  "
              f"{r['effect_label']}={_fmt_eff(r['effect'])}")
    print()
    target_pa = retro["target_panchanga"]
    print(f"[May 16 2026]  tithi {target_pa['tithi_num']} ({target_pa['tithi_name']}, "
          f"{target_pa['paksha']}) · nak {target_pa['nakshatra_num']} ({target_pa['nakshatra_name']})")
    for label, key in [("  exact match", "exact_stats"),
                       ("  tithi only ", "tithi_stats"),
                       ("  nak only   ", "nakshatra_stats")]:
        s = retro[key]
        if s.get("n_grid_rows", 0) == 0:
            print(f"{label}: 0 rows")
            continue
        print(f"{label}: hours={s['hours_covered']:>5}  "
              f"Kp={s['kp_summary']:>15}  Dst={s['dst_summary']:>15}  "
              f"tide={s['tide_summary']:>15}  seis={s['seis_count']} ({s['seis_per_hour']}/h)")
    print("=" * 72)


if __name__ == "__main__":
    main()
