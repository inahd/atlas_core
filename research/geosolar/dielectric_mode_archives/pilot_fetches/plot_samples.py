"""Quick plots of pilot fetches to verify data quality."""
import os
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid", context="paper")

HERE = Path("/home/inahd/atlas_core/research/geosolar/dielectric_mode_archives/pilot_fetches")

# ── PANGAEA Hungary PG ──────────────────────────────────────
print("[plot] PANGAEA Hungary PG, sample month")
panf = HERE / "PANGAEA_942036_szechenyi_hungary_PG_1962_2009.tab"

# PANGAEA tab format: descriptive header, then "*/" separator, then column header line, then data
# Find data start
with open(panf) as f:
    lines = f.read().split("\n")
sep_idx = next(i for i, l in enumerate(lines) if l.startswith("*/"))
header_idx = sep_idx + 1
# Parse from header_idx
df = pd.read_csv(panf, sep="\t", skiprows=header_idx, low_memory=False)
print(f"  rows: {len(df):,}  cols: {len(df.columns)}")
print(f"  columns: {list(df.columns)[:6]}...")
# First column is Date/Time
df.columns = [c.strip() for c in df.columns]
ts_col = df.columns[0]
df[ts_col] = pd.to_datetime(df[ts_col], errors="coerce")
df = df.dropna(subset=[ts_col])
# Find PG cols
pg_uncorr_col = next((c for c in df.columns if "uncorr" in c.lower() and "[V/m]" in c), None) or "PG (uncorr) [V/m]"
pg_corr_col = next((c for c in df.columns if "PG" in c and "uncorr" not in c.lower() and "[V/m]" in c), None) or "PG [V/m]"
print(f"  uncorrected col: {pg_uncorr_col}")
print(f"  corrected col:   {pg_corr_col}")

# Plot: sample year 1980 (mid-range), full month coverage to show diurnal/seasonal structure
sample = df[(df[ts_col] >= "1980-01-01") & (df[ts_col] < "1980-02-01")].copy()
print(f"  sample 1980-01 rows: {len(sample)}")

fig, axes = plt.subplots(2, 1, figsize=(11.0, 7.0), sharex=True)
ax = axes[0]
ax.plot(sample[ts_col], pd.to_numeric(sample[pg_uncorr_col], errors="coerce"),
        linewidth=0.6, color="#3a76c4", label="PG uncorrected")
if pg_corr_col != pg_uncorr_col:
    ax.plot(sample[ts_col], pd.to_numeric(sample[pg_corr_col], errors="coerce"),
            linewidth=0.6, color="#bf3030", alpha=0.7, label="PG corrected (tree shielding)")
ax.set_ylabel("PG (V/m)")
ax.set_title("Atmospheric Electric Potential Gradient — Széchenyi István Observatory, Hungary, January 1980 (sample month)")
ax.legend()

# Diurnal mean
sample["hour"] = sample[ts_col].dt.hour
diurnal = sample.groupby("hour")[pg_uncorr_col].apply(lambda s: pd.to_numeric(s, errors="coerce").mean()).reset_index()
ax2 = axes[1]
ax2.bar(diurnal["hour"], diurnal[pg_uncorr_col], color="#cc8030", edgecolor="black", linewidth=0.5)
ax2.set_xlabel("hour of day (UTC)")
ax2.set_ylabel("mean PG (V/m)")
ax2.set_title("Diurnal mean (Carnegie-curve check)")
ax2.set_xticks(range(0, 24))

fig.tight_layout()
out = HERE / "plot_pangaea_hungary_PG_jan1980.png"
fig.savefig(out, dpi=120)
plt.close(fig)
print(f"  → {out.name}")

# Coverage timeline: years with data per row count
yearly = df.groupby(df[ts_col].dt.year)[pg_uncorr_col].apply(
    lambda s: pd.to_numeric(s, errors="coerce").notna().sum()
).reset_index()
yearly.columns = ["year", "n_valid"]

fig, ax = plt.subplots(figsize=(10.0, 4.0))
ax.bar(yearly["year"], yearly["n_valid"], color="#308050", edgecolor="black", linewidth=0.4)
ax.axhline(8760, color="black", linestyle=":", linewidth=0.8, label="full year (8760 h)")
ax.set_xlabel("year")
ax.set_ylabel("valid PG hours per year")
ax.set_title("PANGAEA Hungary PG record — per-year coverage 1962-2009")
ax.legend()
fig.tight_layout()
out = HERE / "plot_pangaea_hungary_PG_coverage.png"
fig.savefig(out, dpi=120); plt.close(fig)
print(f"  → {out.name}")

# ── Zenodo Nagycenk Schumann monthly diurnal ────────────────
print()
print("[plot] Zenodo Nagycenk Schumann (monthly-diurnal averages)")
nckf = HERE / "Zenodo_4276361_NCK_EZ_schumann_nagycenk.txt"
nck = pd.read_csv(nckf, sep="\t", skiprows=2, header=None)
# Hour column + 48 months columns + trailing tab
nck.columns = ["hour"] + [f"m{i}" for i in range(1, len(nck.columns))]
print(f"  rows: {len(nck)}  cols: {len(nck.columns)} (hour + months)")

# Heatmap: x=month (48), y=hour (24), z=amplitude
cmap_vals = nck.iloc[:, 1:49].to_numpy(dtype=np.float64)
fig, ax = plt.subplots(figsize=(13.0, 5.5))
im = ax.imshow(cmap_vals, aspect="auto", cmap="viridis", origin="lower")
plt.colorbar(im, ax=ax, label="SR amplitude (a.u.)")
ax.set_xlabel("month index (0=Jan 1996, 47=Dec 1999)")
ax.set_ylabel("hour of day (UTC)")
ax.set_title("Nagycenk Schumann resonance — monthly-diurnal amplitude, 1996-1999\n(Zenodo 4276361, NCK_EZ.txt — note: monthly averages, not full time series)")
fig.tight_layout()
out = HERE / "plot_zenodo_nagycenk_schumann.png"
fig.savefig(out, dpi=120); plt.close(fig)
print(f"  → {out.name}")

print()
print("Done.")
