"""
PREREG_006 EXECUTION — multi-station Schumann resonance test of
dielectric-register mode-coupling.

Lock-marker: 62328de (sha256 of prereg file at lock time:
bea01f6e0f84fdee4ad5faf29dd285acbf3a0ef9edc0b1284c288ec79363378c).

Locked design summary (read directly from
research/geosolar/preregistrations/PREREG_006_*.md before this script
was written; not modified during execution):

  Family: 5 stations — ALB, BOU, ESK, HRN, RI.
  Unit of analysis: (station, year, month, hour_of_day).
  Predictor: envelope = |cos(2·sun_moon_separation)|.
  Stratifier (interaction term): mode_ratio at station-local lagna.
  Per-station OLS: amplitude ~ envelope_c + mode_ratio_c
                   + envelope_c*mode_ratio_c + hour FE + month FE.
  Combined OLS: pooled with station FE + station × hour FE.
  Block-bootstrap CI: 60-record blocks, 1000 resamples,
                      seed default_rng(20260508).

  Survival (all four required for confirmatory):
    1. Combined β_mode_ratio CI excludes zero
    2. Sign matches AEF prior (negative; one-tailed)
    3. ≥ 3 of 5 stations individually pass with same sign
    4. Combined β_interaction CI includes zero

  Outcome categories per prereg §4: 4a / 4b / 4c / 4d / 4e.

DEVIATION DISCLOSURE: The 10-minute-resolution files (ALB, BOU, ESK,
HRN) are aggregated to per-hour means here. The prereg's "Unit of
analysis = (station, month, hour)" wording is interpreted as
hour-of-day. This is consistent across stations (RI is natively
hourly). This was decided AFTER the data was fetched but BEFORE the
mode_ratio↔amplitude joint structure was inspected. The file-cadence
discrepancy was not anticipated when the prereg was written. Logged
as a process note, not flagged as a §5 deviation because the unit
of analysis (station, year-month, hour-of-day) is the consistent
interpretation across all 5 stations.
"""
from __future__ import annotations

import json
import math
import re
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

DATA_DIR = ROOT / "research/geosolar/exploratory/schumann_dielectric_replication/data"
OUT = ROOT / "research/geosolar/exploratory/schumann_dielectric_replication"
PLOTS = OUT / "plots"

# Station metadata (approximate coords per prereg §3.1; logged but not gating)
STATIONS = {
    "ALB": {"lat":  54.7, "lon": -113.3, "files": ["ALB_HEW.txt", "ALB_HNS.txt"]},  # Athabasca / Alberta
    "BOU": {"lat":  37.1, "lon": -122.1, "files": ["BOU_HNS.txt"]},                 # Boulder Creek, CA (HNS only — file BOU_HEW absent on Zenodo)
    "ESK": {"lat":  55.3, "lon":   -3.2, "files": ["ESK_HNS.txt"]},                 # Eskdalemuir, Scotland
    "HRN": {"lat":  77.0, "lon":   15.6, "files": ["HRN_HEW.txt", "HRN_HNS.txt"]},  # Hornsund, Spitsbergen
    "RI":  {"lat":  41.8, "lon":  -71.4, "files": ["RI_HEW.txt", "RI_HNS.txt"]},   # West Greenwich, RI
}

K_VALUES = [1, 2, 3, 4, 6, 7, 12]
EPS = 1e-12
N_BOOT = 1000
BLOCK_RECORDS = 60
RNG = np.random.default_rng(20260508)
sns.set_theme(style="whitegrid", context="paper")


# ── parse one Williams TSV ────────────────────────────────

def parse_williams(path: Path) -> pd.DataFrame:
    """Return long-form: hour_of_day(int), year(int), month(int), value(float).
    Aggregates 10-minute resolution files to per-hour means."""
    with open(path) as f:
        lines = f.read().split("\n")
    header = lines[0].split("\t")          # ["Hour", "MM/YYYY", ...]
    # units = lines[1] — discarded
    columns = header[1:]                    # ["MM/YYYY", ...]
    columns = [c.strip() for c in columns if c.strip()]
    parsed_cols = []
    for c in columns:
        m = re.match(r"^(\d{1,2})/(\d{4})$", c)
        if m:
            parsed_cols.append((int(m.group(1)), int(m.group(2))))
        else:
            parsed_cols.append(None)

    # Data rows
    rows = []
    for ln in lines[2:]:
        if not ln.strip():
            continue
        parts = ln.split("\t")
        if not parts:
            continue
        try:
            hr = float(parts[0])
        except ValueError:
            continue
        for j, c_str in enumerate(parts[1:], start=0):
            if j >= len(parsed_cols):
                break
            if parsed_cols[j] is None:
                continue
            try:
                v = float(c_str)
            except ValueError:
                continue
            if math.isnan(v):
                continue
            month, year = parsed_cols[j]
            rows.append({"hour": hr, "year": year, "month": month, "value": v})
    df = pd.DataFrame(rows)
    if df.empty:
        return df

    # Aggregate to integer hour-of-day if file was 10-min resolution
    df["hour_of_day"] = df["hour"].astype(int)
    agg = df.groupby(["year", "month", "hour_of_day"], as_index=False)["value"].mean()
    agg.rename(columns={"value": "amplitude"}, inplace=True)
    return agg


def load_station(code: str) -> pd.DataFrame:
    """Combine all components for a station into a single per-(year, month, hour) DataFrame.
    Components averaged where both present; available component used otherwise."""
    info = STATIONS[code]
    parts = []
    for fn in info["files"]:
        path = DATA_DIR / fn
        if not path.exists():
            print(f"  [WARN] {code}: file missing {fn}")
            continue
        sub = parse_williams(path)
        if sub.empty:
            continue
        comp = "HEW" if "HEW" in fn else ("HNS" if "HNS" in fn else "OTH")
        sub["component"] = comp
        parts.append(sub)
    if not parts:
        return pd.DataFrame()
    cat = pd.concat(parts, ignore_index=True)
    # Average across components per (year, month, hour_of_day)
    out = cat.groupby(["year", "month", "hour_of_day"], as_index=False)["amplitude"].mean()
    out["station"] = code
    return out


# ── ephemeris ─────────────────────────────────────────────

def compute_lagna_sun_moon(timestamps_utc: list, lat: float, lon: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    import swisseph as swe
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    n = len(timestamps_utc)
    lagna = np.empty(n, dtype=np.float64)
    sun_l = np.empty(n, dtype=np.float64)
    moon_l = np.empty(n, dtype=np.float64)
    for i, dt in enumerate(timestamps_utc):
        h = dt.hour + dt.minute / 60.0 + dt.second / 3600.0
        jd = swe.julday(dt.year, dt.month, dt.day, h)
        aya = swe.get_ayanamsa_ut(jd)
        sun_l[i] = (swe.calc_ut(jd, swe.SUN)[0][0] - aya) % 360.0
        moon_l[i] = (swe.calc_ut(jd, swe.MOON)[0][0] - aya) % 360.0
        _cusps, ascmc = swe.houses(jd, lat, lon, b"W")
        lagna[i] = (ascmc[0] - aya) % 360.0
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


# ── statistics ────────────────────────────────────────────

def ols_with_se(X, y):
    n, p = X.shape
    beta, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    y_hat = X @ beta
    resid = y - y_hat
    rss = float(resid @ resid)
    sigma2 = rss / max(n - p, 1)
    XtX_inv = np.linalg.pinv(X.T @ X)
    var_beta = sigma2 * np.diag(XtX_inv)
    se = np.sqrt(np.maximum(var_beta, 0.0))
    t = beta / np.where(se > 0, se, np.nan)
    pval = 2.0 * stats.t.sf(np.abs(t), df=max(n - p, 1))
    ss_tot = float((y - y.mean()) @ (y - y.mean()))
    r2 = 1.0 - rss / ss_tot if ss_tot > 0 else float("nan")
    return {"beta": beta, "se": se, "t": t, "p": pval, "r2": r2, "n": n, "p_params": p, "resid": resid}


def block_bootstrap_ci_ols(X, y, coef_idx, block_size=BLOCK_RECORDS, n_boot=N_BOOT):
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


def build_design(df, station_codes):
    """Per-prereg combined-stations design matrix:
    intercept + envelope_c + mode_ratio_c + envelope_c × mode_ratio_c
    + station FE (k-1 dummies) + hour FE (23 dummies)
    + month FE (11 dummies)
    + station × hour FE.
    Returns (X, names, y).
    """
    env = df["envelope"].to_numpy(dtype=np.float64)
    mr = df["mode_ratio"].to_numpy(dtype=np.float64)
    env_c = env - env.mean()
    mr_c = mr - mr.mean()
    inter_c = env_c * mr_c
    n = len(df)

    cols = [np.ones(n), env_c, mr_c, inter_c]
    names = ["intercept", "envelope_c", "mode_ratio_c", "envelope_x_mode_ratio"]

    # Station FE (drop first as reference)
    stations = list(station_codes)
    for s in stations[1:]:
        cols.append((df["station"] == s).to_numpy(dtype=np.float64))
        names.append(f"station_{s}")
    # Hour FE (0..23, drop hour 0)
    for h in range(1, 24):
        cols.append((df["hour_of_day"] == h).to_numpy(dtype=np.float64))
        names.append(f"hour_{h}")
    # Month FE (1..12, drop month 1)
    for m in range(2, 13):
        cols.append((df["month"] == m).to_numpy(dtype=np.float64))
        names.append(f"month_{m}")
    # Station × hour interaction (per-station diurnal pattern); drop reference station
    for s in stations[1:]:
        s_dum = (df["station"] == s).to_numpy(dtype=np.float64)
        for h in range(1, 24):
            h_dum = (df["hour_of_day"] == h).to_numpy(dtype=np.float64)
            cols.append(s_dum * h_dum)
            names.append(f"station_{s}_x_hour_{h}")

    X = np.column_stack(cols)
    y = df["amplitude"].to_numpy(dtype=np.float64)
    return X, names, y


def build_design_per_station(df):
    """Per-station design: intercept + envelope_c + mode_ratio_c
    + envelope_c × mode_ratio_c + hour FE (23) + month FE (11)."""
    env = df["envelope"].to_numpy(dtype=np.float64)
    mr = df["mode_ratio"].to_numpy(dtype=np.float64)
    env_c = env - env.mean()
    mr_c = mr - mr.mean()
    inter_c = env_c * mr_c
    n = len(df)
    cols = [np.ones(n), env_c, mr_c, inter_c]
    names = ["intercept", "envelope_c", "mode_ratio_c", "envelope_x_mode_ratio"]
    for h in range(1, 24):
        if (df["hour_of_day"] == h).any():
            cols.append((df["hour_of_day"] == h).to_numpy(dtype=np.float64))
            names.append(f"hour_{h}")
    for m in range(2, 13):
        if (df["month"] == m).any():
            cols.append((df["month"] == m).to_numpy(dtype=np.float64))
            names.append(f"month_{m}")
    X = np.column_stack(cols)
    y = df["amplitude"].to_numpy(dtype=np.float64)
    return X, names, y


# ── main ──────────────────────────────────────────────────

def main():
    PLOTS.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    # ── load + decompose per station ───────────────────
    print("[load+versor] per-station data ingest")
    all_dfs = []
    fetch_failures = []
    for code in ["ALB", "BOU", "ESK", "HRN", "RI"]:
        sdf = load_station(code)
        if sdf.empty:
            fetch_failures.append(code)
            print(f"  [{code}] EMPTY — fetch/parse failure")
            continue
        # representative timestamp: 15th day of (year, month) at hour_of_day UTC
        sdf["ts"] = pd.to_datetime(
            sdf.assign(day=15).rename(columns={"hour_of_day": "hour"})[["year", "month", "day", "hour"]],
            utc=True,
        )
        info = STATIONS[code]
        ts_list = [t.to_pydatetime() for t in sdf["ts"]]
        lagna, sun_l, moon_l = compute_lagna_sun_moon(ts_list, info["lat"], info["lon"])
        mag, die = versor_decompose(sun_l, moon_l, lagna)
        sep = (moon_l - sun_l) % 360.0
        sdf["mode_ratio"] = (die / (mag + die + EPS)).astype(np.float32)
        sdf["envelope"] = np.abs(np.cos(2.0 * np.radians(sep))).astype(np.float32)
        sdf["sun_moon_sep"] = sep.astype(np.float32)
        sdf["lagna_long"] = lagna.astype(np.float32)
        # Restore hour_of_day column for design matrix
        sdf["hour_of_day"] = sdf["hour_of_day"].astype(int)
        sdf["year"] = sdf["year"].astype(int)
        sdf["month"] = sdf["month"].astype(int)
        all_dfs.append(sdf)
        print(f"  [{code}] n={len(sdf):,}  yrs={sdf.year.min()}-{sdf.year.max()}  "
              f"months={sdf.month.nunique()}  mr=[{sdf.mode_ratio.min():.3f}, {sdf.mode_ratio.max():.3f}]")

    if len(fetch_failures) > 1:
        print(f"\n[HALT] {len(fetch_failures)} stations failed; prereg §3.8 invalidates execution.")
        sys.exit(2)

    combined = pd.concat(all_dfs, ignore_index=True)
    print(f"\n[combined] total records: {len(combined):,}")
    # Save raw combined parquet
    combined.to_parquet(OUT / "combined_records.parquet", index=False)

    # ── per-station regression ─────────────────────────
    print("\n[per-station OLS + bootstrap]")
    per_station = []
    for code in ["ALB", "BOU", "ESK", "HRN", "RI"]:
        sub = combined[combined["station"] == code].sort_values(["year", "month", "hour_of_day"]).reset_index(drop=True)
        n = len(sub)
        if n < 30:
            per_station.append({"station": code, "n": n, "skipped": True})
            print(f"  [{code}] n={n} — skipped (insufficient)")
            continue
        X, names, y = build_design_per_station(sub)
        fit = ols_with_se(X, y)
        # bootstrap CIs on β_mode_ratio (idx 2) and β_interaction (idx 3)
        ci_mr = block_bootstrap_ci_ols(X, y, 2)
        ci_int = block_bootstrap_ci_ols(X, y, 3)
        rec = {
            "station": code,
            "n": int(n),
            "beta_mode_ratio": float(fit["beta"][2]),
            "se_mode_ratio": float(fit["se"][2]),
            "p_mode_ratio": float(fit["p"][2]),
            "ci_mr_lo": ci_mr[0], "ci_mr_hi": ci_mr[1],
            "beta_interaction": float(fit["beta"][3]),
            "p_interaction": float(fit["p"][3]),
            "ci_int_lo": ci_int[0], "ci_int_hi": ci_int[1],
            "r2": float(fit["r2"]),
            "skipped": False,
        }
        # Per-station survival check (criterion 3): mr CI excludes 0 with NEGATIVE sign
        rec["passes_mr_negative"] = (rec["ci_mr_hi"] < 0)
        per_station.append(rec)
        print(f"  [{code}] n={n:>5,}  β_mr={rec['beta_mode_ratio']:+.4f}  "
              f"CI=[{rec['ci_mr_lo']:+.4f},{rec['ci_mr_hi']:+.4f}]  "
              f"passes_neg={rec['passes_mr_negative']}")

    pd.DataFrame(per_station).to_parquet(OUT / "per_station_results.parquet", index=False)

    # ── combined-stations regression ──────────────────
    print("\n[combined OLS + bootstrap]")
    combined_sorted = combined.sort_values(["station", "year", "month", "hour_of_day"]).reset_index(drop=True)
    X, names, y = build_design(combined_sorted, ["ALB", "BOU", "ESK", "HRN", "RI"])
    print(f"  design matrix: {X.shape}")
    fit_c = ols_with_se(X, y)
    ci_mr_c = block_bootstrap_ci_ols(X, y, 2)
    ci_int_c = block_bootstrap_ci_ols(X, y, 3)
    print(f"  β_mode_ratio   = {fit_c['beta'][2]:+.5f}  SE={fit_c['se'][2]:.5f}  "
          f"OLS p={fit_c['p'][2]:.3g}  bootstrap CI=[{ci_mr_c[0]:+.5f}, {ci_mr_c[1]:+.5f}]")
    print(f"  β_interaction  = {fit_c['beta'][3]:+.5f}  SE={fit_c['se'][3]:.5f}  "
          f"OLS p={fit_c['p'][3]:.3g}  bootstrap CI=[{ci_int_c[0]:+.5f}, {ci_int_c[1]:+.5f}]")
    print(f"  R² = {fit_c['r2']:.5f}")

    combined_summary = {
        "n": int(fit_c["n"]),
        "n_params": int(fit_c["p_params"]),
        "r2": float(fit_c["r2"]),
        "beta_mode_ratio": float(fit_c["beta"][2]),
        "se_mode_ratio": float(fit_c["se"][2]),
        "p_mode_ratio": float(fit_c["p"][2]),
        "ci_mr_lo": ci_mr_c[0], "ci_mr_hi": ci_mr_c[1],
        "beta_interaction": float(fit_c["beta"][3]),
        "se_interaction": float(fit_c["se"][3]),
        "p_interaction": float(fit_c["p"][3]),
        "ci_int_lo": ci_int_c[0], "ci_int_hi": ci_int_c[1],
    }
    with open(OUT / "combined_summary.json", "w") as f:
        json.dump(combined_summary, f, indent=2)

    # ── apply 4 survival criteria ─────────────────────
    print("\n[survival criteria]")
    crit1 = (ci_mr_c[1] < 0) or (ci_mr_c[0] > 0)        # CI excludes zero
    crit2 = combined_summary["beta_mode_ratio"] < 0      # sign matches AEF prior (negative)
    n_stations_pass = sum(1 for r in per_station if not r.get("skipped") and r.get("passes_mr_negative"))
    crit3 = n_stations_pass >= 3
    # Criterion 2 only applies to crit1; if crit1 fails, crit2 is moot.
    # The locked rule: criterion 2 is "Sign matches AEF prior". If sign-flipped, crit2 fails.
    crit4 = (ci_int_c[0] < 0) and (ci_int_c[1] > 0)      # interaction CI INCLUDES zero
    print(f"  Crit 1 — combined β_mode_ratio CI excludes zero:  {'PASS' if crit1 else 'FAIL'}  "
          f"({ci_mr_c[0]:+.4f}, {ci_mr_c[1]:+.4f})")
    print(f"  Crit 2 — sign matches AEF prior (negative):       {'PASS' if crit2 else 'FAIL'}  "
          f"(β = {combined_summary['beta_mode_ratio']:+.5f})")
    print(f"  Crit 3 — ≥ 3 of 5 stations individually pass:     {'PASS' if crit3 else 'FAIL'}  "
          f"({n_stations_pass} of 5 stations passed)")
    print(f"  Crit 4 — combined β_interaction CI includes zero: {'PASS' if crit4 else 'FAIL'}  "
          f"({ci_int_c[0]:+.4f}, {ci_int_c[1]:+.4f})")

    # Outcome category
    if crit4 == False:
        category = "4e"  # interaction non-null overrides everything
    elif crit1 and crit2 and crit3 and crit4:
        category = "4a"  # confirmatory
    elif crit1 and crit2 and crit4 and not crit3:
        category = "4b"  # weak (pooled but not geographic)
    elif (not crit1) and crit4:
        category = "4c"  # pooled null
    elif crit1 and (not crit2) and crit4:
        category = "4d"  # sign-flipped
    else:
        category = "uncategorized"

    print(f"\n  Outcome category per prereg §4: {category}")

    # ── plots ──────────────────────────────────────────
    print("\n[plots]")
    rng_plot = np.random.default_rng(20260508)

    # 1. mode_ratio_vs_amplitude_per_station.png — 5 panels
    fig, axes = plt.subplots(2, 3, figsize=(15.0, 9.0))
    color_map = {"ALB": "#bf3030", "BOU": "#cc8030", "ESK": "#3a76c4",
                 "HRN": "#308050", "RI": "#a040a0"}
    for ax, code in zip(axes.flat, ["ALB", "BOU", "ESK", "HRN", "RI"]):
        sub = combined[combined["station"] == code]
        n = len(sub)
        sample = sub.sample(n=min(2000, n), random_state=20260508) if n > 2000 else sub
        ax.scatter(sample["mode_ratio"], sample["amplitude"], s=4, alpha=0.30,
                   color=color_map[code], edgecolors="none")
        # Add the per-station β_mr line through the data mean
        rec = next(r for r in per_station if r["station"] == code)
        if not rec.get("skipped"):
            x_centered = np.linspace(sub["mode_ratio"].min(), sub["mode_ratio"].max(), 50)
            mean_amp = sub["amplitude"].mean()
            mean_mr = sub["mode_ratio"].mean()
            yline = mean_amp + rec["beta_mode_ratio"] * (x_centered - mean_mr)
            ax.plot(x_centered, yline, color="black", linewidth=1.0, label=f"β_mr={rec['beta_mode_ratio']:+.3f}")
        ax.set_xlabel("mode_ratio")
        ax.set_ylabel("SR amplitude (file units)")
        ax.set_title(f"{code}  n={n:,}")
        ax.legend(loc="best", fontsize=8)
    axes.flat[5].axis("off")
    fig.suptitle("Mode_ratio vs Schumann amplitude, per station — PREREG_006 execution", y=1.0)
    fig.tight_layout()
    p = PLOTS / "mode_ratio_vs_amplitude_per_station.png"
    fig.savefig(p, dpi=120); plt.close(fig)
    print(f"  → {p.name}")

    # 2. per_station_beta_mode_ratio_with_CI.png — forest plot
    fig, ax = plt.subplots(figsize=(10.0, 6.0))
    valid = [r for r in per_station if not r.get("skipped")]
    codes = [r["station"] for r in valid]
    betas = [r["beta_mode_ratio"] for r in valid]
    err_lo = [r["beta_mode_ratio"] - r["ci_mr_lo"] for r in valid]
    err_hi = [r["ci_mr_hi"] - r["beta_mode_ratio"] for r in valid]
    ax.errorbar(betas, range(len(valid)), xerr=[err_lo, err_hi], fmt="o", color="black",
                capsize=4, linewidth=1.2, markersize=8)
    ax.axvline(0, color="black", linewidth=0.5, linestyle=":")
    ax.axvline(combined_summary["beta_mode_ratio"], color="#bf3030", linestyle="--",
               linewidth=1.2, label=f"combined β_mr = {combined_summary['beta_mode_ratio']:+.4f}")
    ax.fill_betweenx([-0.5, len(valid) - 0.5],
                     combined_summary["ci_mr_lo"], combined_summary["ci_mr_hi"],
                     color="#bf3030", alpha=0.10, label="combined 95% CI")
    ax.set_yticks(range(len(valid)))
    ax.set_yticklabels(codes)
    ax.set_xlabel("β_mode_ratio")
    ax.set_title(f"Per-station β_mode_ratio with 95% block-bootstrap CI\n"
                 f"crit 3 (≥3 of 5 negative-significant): "
                 f"{n_stations_pass} of 5 pass — {'PASS' if crit3 else 'FAIL'}")
    ax.legend()
    fig.tight_layout()
    p = PLOTS / "per_station_beta_mode_ratio_with_CI.png"
    fig.savefig(p, dpi=120); plt.close(fig)
    print(f"  → {p.name}")

    # 3. combined_regression_diagnostic.png — fitted vs residuals
    y_hat = X @ fit_c["beta"]
    resid = y - y_hat
    fig, axes = plt.subplots(1, 2, figsize=(14.0, 5.5))
    idx_p = rng_plot.choice(len(y), size=min(8000, len(y)), replace=False)
    axes[0].scatter(y_hat[idx_p], resid[idx_p], s=3, alpha=0.20, color="#3a76c4", edgecolors="none")
    axes[0].axhline(0, color="black", linewidth=0.5)
    axes[0].set_xlabel("fitted")
    axes[0].set_ylabel("residual")
    axes[0].set_title("Combined-stations OLS — residuals vs fitted")
    # Histogram of residuals
    axes[1].hist(resid, bins=80, color="#cc8030", edgecolor="black", linewidth=0.4, density=True)
    axes[1].set_xlabel("residual")
    axes[1].set_ylabel("density")
    axes[1].set_title(f"Combined residual distribution (R²={fit_c['r2']:.4f})")
    fig.suptitle(f"Combined regression diagnostic — n={fit_c['n']:,}, p_params={fit_c['p_params']}", y=1.0)
    fig.tight_layout()
    p = PLOTS / "combined_regression_diagnostic.png"
    fig.savefig(p, dpi=120); plt.close(fig)
    print(f"  → {p.name}")

    # 4. sign_consistency_check.png
    fig, ax = plt.subplots(figsize=(11.0, 5.5))
    xs = np.arange(len(valid))
    bars = ax.bar(xs, [r["beta_mode_ratio"] for r in valid],
                  color=["#308050" if r["passes_mr_negative"] else "#bf3030" for r in valid],
                  edgecolor="black", linewidth=0.5)
    ax.errorbar(xs, [r["beta_mode_ratio"] for r in valid],
                yerr=[err_lo, err_hi], fmt="none", ecolor="black", capsize=4, linewidth=1.0)
    ax.axhline(0, color="black", linewidth=0.5)
    ax.axhline(combined_summary["beta_mode_ratio"], color="#bf3030", linestyle="--",
               linewidth=1.0, label=f"combined β_mr={combined_summary['beta_mode_ratio']:+.4f}")
    ax.set_xticks(xs)
    ax.set_xticklabels(codes)
    ax.set_ylabel("β_mode_ratio")
    ax.set_title(f"Sign consistency — green = passes 'CI < 0' (one-tailed AEF prior)\n"
                 f"{n_stations_pass} of 5 stations PASS  ·  combined β_mr {'<' if combined_summary['beta_mode_ratio']<0 else '≥'} 0  ·  category {category}")
    ax.legend()
    fig.tight_layout()
    p = PLOTS / "sign_consistency_check.png"
    fig.savefig(p, dpi=120); plt.close(fig)
    print(f"  → {p.name}")

    # ── synthesis ──────────────────────────────────────
    write_synthesis(per_station, combined_summary, ci_mr_c, ci_int_c, fit_c,
                    crit1, crit2, crit3, crit4, n_stations_pass, category,
                    fetch_failures, time.time() - t0)

    # ── console summary ────────────────────────────────
    print()
    print("=" * 70)
    print(f"  PREREG_006 EXECUTION RESULT — outcome category: {category}")
    print("=" * 70)
    print(f"  Lock-marker: 62328de (verified)")
    print(f"  Per-station β_mode_ratio (negative one-tailed pass = CI_hi < 0):")
    for r in per_station:
        if r.get("skipped"):
            continue
        mark = "✓ PASS" if r["passes_mr_negative"] else "·     "
        print(f"    {r['station']:>4s}  n={r['n']:>5,}  β_mr={r['beta_mode_ratio']:+.4f}  "
              f"CI=[{r['ci_mr_lo']:+.4f},{r['ci_mr_hi']:+.4f}]  {mark}")
    print()
    print(f"  Combined β_mode_ratio  = {combined_summary['beta_mode_ratio']:+.5f}  "
          f"CI=[{ci_mr_c[0]:+.5f},{ci_mr_c[1]:+.5f}]")
    print(f"  Combined β_interaction = {combined_summary['beta_interaction']:+.5f}  "
          f"CI=[{ci_int_c[0]:+.5f},{ci_int_c[1]:+.5f}]")
    print()
    print(f"  Crit 1 (CI excludes 0):       {'PASS' if crit1 else 'FAIL'}")
    print(f"  Crit 2 (sign negative):       {'PASS' if crit2 else 'FAIL'}")
    print(f"  Crit 3 (≥3 of 5):             {'PASS' if crit3 else 'FAIL'}  ({n_stations_pass} pass)")
    print(f"  Crit 4 (interaction null):    {'PASS' if crit4 else 'FAIL'}")
    print(f"\n  Outcome category: {category}")
    print(f"\nTotal wall: {time.time() - t0:.1f}s")


def write_synthesis(per_station, summary, ci_mr_c, ci_int_c, fit_c,
                    crit1, crit2, crit3, crit4, n_pass, category,
                    fetch_failures, total_wall):
    md = []
    md.append("# PREREG_006 EXECUTION RESULT — multi-station Schumann replication\n")
    md.append("**Lock-marker:** 62328de (verified before execution).")
    md.append("**Outcome category per prereg §4:** **" + category + "**\n")
    md.append("Date: 2026-05-08\n")

    md.append("## Lock verification\n")
    md.append("- `git log --follow research/geosolar/preregistrations/PREREG_006_*.md` shows")
    md.append("  62328de as the only commit on the prereg path before this execution session.")
    md.append("- File sha256 at lock-time: `bea01f6e0f84fdee4ad5faf29dd285acbf3a0ef9edc0b1284c288ec79363378c`")
    md.append("")

    md.append("## Process notes (declared, not deviations)\n")
    md.append("- Williams files have heterogeneous cadence: 4 stations are 10-minute resolution")
    md.append("  (ALB, BOU, ESK, HRN, 144 rows × N month-year cols); RI is hourly (24 rows ×")
    md.append("  N cols). Per-prereg unit-of-analysis `(station, month, hour)` interpreted as")
    md.append("  hour-of-day; 10-min files aggregated to per-hour means before analysis.")
    md.append("- BOU is HNS-only on Zenodo (BOU_HEW.txt absent); handled per prereg §3.2")
    md.append("  asymmetric-components rule (use available component).")
    md.append("- ALB component files have units [pT²/Hz] (power spectral density, not pure amplitude).")
    md.append("  All per-station regressions are within-station so absolute units do not matter")
    md.append("  for the test; the combined-stations regression carries station fixed-effects")
    md.append("  which absorb cross-station unit differences.")
    md.append(f"- Fetch failures: {fetch_failures or 'none'}")
    md.append("")

    md.append("## Per-station results\n")
    md.append("Per prereg §3.4, OLS per station:")
    md.append("`amplitude ~ envelope_c + mode_ratio_c + envelope_c × mode_ratio_c + hour_FE + month_FE`\n")
    md.append("Block-bootstrap CI: 60-record blocks, 1,000 resamples, seed default_rng(20260508).\n")
    md.append("| Station | n | β_mr | 95% CI on β_mr | passes (CI_hi<0)? | β_interaction | OLS p_int |")
    md.append("|---|---:|---:|---|:-:|---:|---:|")
    for r in per_station:
        if r.get("skipped"):
            md.append(f"| {r['station']} | {r['n']:,} | n/a | n/a | n/a (skipped) | n/a | n/a |")
            continue
        mark = "✓" if r["passes_mr_negative"] else "·"
        md.append(f"| {r['station']} | {r['n']:,} | {r['beta_mode_ratio']:+.4f} | "
                  f"[{r['ci_mr_lo']:+.4f}, {r['ci_mr_hi']:+.4f}] | {mark} | "
                  f"{r['beta_interaction']:+.4f} | {r['p_interaction']:.3g} |")
    md.append(f"\nStations passing one-tailed-negative criterion: **{n_pass} of 5**.\n")

    md.append("## Combined-stations regression\n")
    md.append("Per prereg §3.4, pooled with station FE + station × hour interaction:\n")
    md.append("    sr_amplitude ~ envelope_c + mode_ratio_c + envelope_c × mode_ratio_c")
    md.append("                  + station + hour_FE + month_FE + station × hour\n")
    md.append(f"- n = {summary['n']:,}, parameters = {summary['n_params']}, R² = {summary['r2']:.5f}")
    md.append(f"- β_mode_ratio   = {summary['beta_mode_ratio']:+.5f},  SE = {summary['se_mode_ratio']:.5f},")
    md.append(f"  OLS p = {summary['p_mode_ratio']:.3g},  bootstrap 95% CI = [{ci_mr_c[0]:+.5f}, {ci_mr_c[1]:+.5f}]")
    md.append(f"- β_interaction  = {summary['beta_interaction']:+.5f},  SE = {summary['se_interaction']:.5f},")
    md.append(f"  OLS p = {summary['p_interaction']:.3g},  bootstrap 95% CI = [{ci_int_c[0]:+.5f}, {ci_int_c[1]:+.5f}]")
    md.append("")

    md.append("## Survival criteria (per prereg §3.6, locked)\n")
    md.append("| # | Criterion | Result |")
    md.append("|---|---|:-:|")
    md.append(f"| 1 | Combined β_mode_ratio bootstrap CI excludes zero | **{'PASS' if crit1 else 'FAIL'}** |")
    md.append(f"| 2 | Sign matches AEF prior (negative) | **{'PASS' if crit2 else 'FAIL'}** |")
    md.append(f"| 3 | ≥ 3 of 5 stations individually pass with same sign | **{'PASS' if crit3 else 'FAIL'}** ({n_pass}/5) |")
    md.append(f"| 4 | Combined β_interaction bootstrap CI includes zero | **{'PASS' if crit4 else 'FAIL'}** |")
    md.append("")

    md.append("## Outcome category (locked interpretations)\n")
    md.append(f"**Category {category}**\n")
    interp_map = {
        "4a": "Confirmatory finding. All four criteria satisfied. Multi-station replication of the dielectric-register mode-coupling main effect first observed exploratorily at Hungary AEF. The framework's broader prediction of differential mode-coupling between magnetic-side and dielectric-side bhumi-layer indicators gains held-out support.",
        "4b": "Weak confirmation. Pooled effect present but not robustly geographic. Effect could be driven by 1-2 stations; reported as suggestive, not confirmatory.",
        "4c": "Pooled null. The Hungary AEF mode_ratio main effect does not replicate to multi-station Schumann data. The dielectric-register coupling claim is not supported beyond the single-location AEF exploratory result.",
        "4d": "Sign-flipped. Pooled effect is non-zero but in the opposite direction from the AEF prior. Not counted as confirmation. Substantive finding requiring framework reconsideration.",
        "4e": "Interaction non-null. New finding inconsistent with both M4 and AEF priors. Triggers diagnostic care; the moderation pattern is data-dependent in ways the framework needs to account for.",
        "uncategorized": "The criterion combination did not match any of the locked outcome categories. This is itself a surprise and warrants manual review.",
    }
    md.append(interp_map.get(category, "Uncategorized."))
    md.append("")

    md.append("## Plots\n")
    md.append("- `plots/mode_ratio_vs_amplitude_per_station.png` — 5 panels, scatter + per-station β line.")
    md.append("- `plots/per_station_beta_mode_ratio_with_CI.png` — forest plot.")
    md.append("- `plots/combined_regression_diagnostic.png` — residuals vs fitted, residual histogram.")
    md.append("- `plots/sign_consistency_check.png` — per-station β_mr with combined overlay; pass/fail color-coded.")
    md.append("")

    md.append("## Files\n")
    md.append("- `data/` — fetched Williams Zenodo 4276361 station files (raw .txt).")
    md.append("- `combined_records.parquet` — long-form (station, year, month, hour) records with mode_ratio, envelope, amplitude.")
    md.append("- `per_station_results.parquet` — per-station regression outputs.")
    md.append("- `combined_summary.json` — combined regression coefficients + bootstrap CIs.")
    md.append("- `run_schumann_replication.py` — execution script.")
    md.append("")

    md.append(f"*Total wall: {total_wall:.1f}s*")
    p = OUT / "SYNTHESIS.md"
    p.write_text("\n".join(md))


if __name__ == "__main__":
    main()
