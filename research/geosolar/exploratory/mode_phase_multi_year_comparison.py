"""
Cross-year comparison of multi-pair versor mode-decomposition correlation
structure. Years compared: 2024 (full), 2025 (full), 2026 (May 9 - Dec 31).

Reads:
  research/geosolar/exploratory/mode_phase_multi_pair_2024/all_pairs_modes_2024.parquet
  research/geosolar/exploratory/mode_phase_multi_pair_2025/all_pairs_modes_2025.parquet
  research/geosolar/exploratory/mode_phase_multi_pair_2026/all_pairs_modes_2026.parquet

Outputs (4 plots + 3 READMEs):
  research/geosolar/exploratory/mode_phase_multi_year_comparison/
    correlation_matrix_3year_comparison.png
    mercury_pair_correlations_by_year.png
    mediator_strength_by_graha_year.png
    top_correlations_by_year.png
    mode_phase_multi_year_comparison.md   (synthesis)
  research/geosolar/exploratory/mode_phase_multi_pair_2024/README.md
  research/geosolar/exploratory/mode_phase_multi_pair_2026/README.md
  (existing 2025 README left as-is)
"""
from __future__ import annotations
import os
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid", context="paper")

ROOT = Path("/home/inahd/atlas_core")
OUT = ROOT / "research/geosolar/exploratory/mode_phase_multi_year_comparison"
OUT.mkdir(parents=True, exist_ok=True)

PAIRS = [
    "sun_moon", "sun_mars", "sun_mercury", "sun_venus", "sun_jupiter", "sun_saturn",
    "moon_mars", "moon_mercury", "moon_jupiter",
    "jupiter_saturn",
]

# Per-graha containment
GRAHA_PAIRS = {
    "Sun":     ["sun_moon", "sun_mars", "sun_mercury", "sun_venus", "sun_jupiter", "sun_saturn"],
    "Moon":    ["sun_moon", "moon_mars", "moon_mercury", "moon_jupiter"],
    "Mercury": ["sun_mercury", "moon_mercury"],
    "Venus":   ["sun_venus"],
    "Mars":    ["sun_mars", "moon_mars"],
    "Jupiter": ["sun_jupiter", "moon_jupiter", "jupiter_saturn"],
    "Saturn":  ["sun_saturn", "jupiter_saturn"],
}

YEARS = {
    "2024": ROOT / "research/geosolar/exploratory/mode_phase_multi_pair_2024/all_pairs_modes_2024.parquet",
    "2025": ROOT / "research/geosolar/exploratory/mode_phase_multi_pair_2025/all_pairs_modes_2025.parquet",
    "2026": ROOT / "research/geosolar/exploratory/mode_phase_multi_pair_2026/all_pairs_modes_2026.parquet",
}


def load_corr_matrix(path: Path) -> tuple[pd.DataFrame, int]:
    cols = [f"{p}_mode_ratio" for p in PAIRS]
    df = pd.read_parquet(path, columns=cols)
    df.columns = PAIRS
    return df.corr(method="pearson"), len(df)


def mediator_strength(corr: pd.DataFrame, graha: str) -> tuple[float, int]:
    """Mean off-diagonal correlation entries that touch any pair containing `graha`."""
    p_set = set(GRAHA_PAIRS[graha])
    vals = []
    for i, j in combinations(PAIRS, 2):
        if i in p_set or j in p_set:
            vals.append(corr.loc[i, j])
    return float(np.mean(vals)) if vals else float("nan"), len(vals)


def top_offdiag(corr: pd.DataFrame, n: int = 10):
    rows = []
    for i, j in combinations(PAIRS, 2):
        rows.append((i, j, corr.loc[i, j]))
    rows.sort(key=lambda r: abs(r[2]), reverse=True)
    return rows[:n]


def plot_3year_matrices(corrs: dict, n_rows: dict):
    fig, axes = plt.subplots(1, 3, figsize=(20.0, 6.5))
    vmin = min(c.values.min() for c in corrs.values())
    vmax = max(c.values.max() for c in corrs.values())
    # Symmetric scale around 0
    vlim = max(abs(vmin), abs(vmax))
    for ax, (year, c) in zip(axes, corrs.items()):
        sns.heatmap(c, annot=True, fmt="+.2f", cmap="RdBu_r",
                    vmin=-vlim, vmax=vlim, center=0, square=True,
                    cbar=ax is axes[-1], cbar_kws={"label": "Pearson r"} if ax is axes[-1] else None,
                    annot_kws={"size": 7}, ax=ax)
        ax.set_title(f"{year}  (n={n_rows[year]:,})")
    fig.suptitle("Pair–pair Pearson correlation of mode_ratio time series, three-year comparison",
                 y=1.0)
    fig.tight_layout()
    p = OUT / "correlation_matrix_3year_comparison.png"
    fig.savefig(p, dpi=120); plt.close(fig)
    print(f"  → {p.name}")


def plot_mercury_pair_correlations(corrs: dict):
    """Each Mercury-containing pair's correlation with each non-Mercury pair, by year."""
    mercury_pairs = ["sun_mercury", "moon_mercury"]
    non_mercury = [p for p in PAIRS if p not in mercury_pairs]
    fig, axes = plt.subplots(2, 1, figsize=(13.0, 9.0), sharex=True)
    width = 0.27
    x = np.arange(len(non_mercury))
    colors_yr = {"2024": "#3a76c4", "2025": "#cc8030", "2026": "#308050"}
    for ax, mpair in zip(axes, mercury_pairs):
        for k, (year, corr) in enumerate(corrs.items()):
            vals = [corr.loc[mpair, p] for p in non_mercury]
            ax.bar(x + (k - 1) * width, vals, width=width,
                   color=colors_yr[year], edgecolor="black", linewidth=0.4,
                   label=f"{year}")
        ax.axhline(0, color="black", linewidth=0.4)
        ax.set_xticks(x)
        ax.set_xticklabels(non_mercury, rotation=20, ha="right")
        ax.set_ylabel(f"corr({mpair}, *)")
        ax.set_title(f"{mpair} correlated with each non-Mercury pair, by year")
        ax.legend(loc="best", fontsize=8)
    fig.suptitle("Mercury-containing pair correlations across years", y=1.0)
    fig.tight_layout()
    p = OUT / "mercury_pair_correlations_by_year.png"
    fig.savefig(p, dpi=120); plt.close(fig)
    print(f"  → {p.name}")


def plot_mediator_strength(corrs: dict):
    grahas_order = ["Sun", "Moon", "Mars", "Mercury", "Venus", "Jupiter", "Saturn"]
    fig, ax = plt.subplots(figsize=(11.0, 6.0))
    width = 0.27
    x = np.arange(len(grahas_order))
    colors_yr = {"2024": "#3a76c4", "2025": "#cc8030", "2026": "#308050"}
    for k, (year, corr) in enumerate(corrs.items()):
        vals = [mediator_strength(corr, g)[0] for g in grahas_order]
        ax.bar(x + (k - 1) * width, vals, width=width,
               color=colors_yr[year], edgecolor="black", linewidth=0.4,
               label=year)
    ax.axhline(0, color="black", linewidth=0.4)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{g}\n(k={len(GRAHA_PAIRS[g])} pairs)" for g in grahas_order])
    ax.set_ylabel("mean off-diagonal corr touching pairs containing graha")
    ax.set_title("Mediator-strength T(m) per graha, three-year comparison")
    ax.legend()
    fig.tight_layout()
    p = OUT / "mediator_strength_by_graha_year.png"
    fig.savefig(p, dpi=120); plt.close(fig)
    print(f"  → {p.name}")


def plot_top_correlations(corrs: dict):
    fig, axes = plt.subplots(1, 3, figsize=(17.0, 6.5))
    for ax, (year, corr) in zip(axes, corrs.items()):
        rows = top_offdiag(corr, n=10)
        labels = [f"{a} ×\n{b}" for a, b, _ in rows]
        vals = [v for _, _, v in rows]
        colors = ["#bf3030" if v < 0 else "#3a76c4" for v in vals]
        ax.barh(range(len(rows))[::-1], vals, color=colors, edgecolor="black", linewidth=0.4)
        ax.set_yticks(range(len(rows))[::-1])
        ax.set_yticklabels(labels, fontsize=8)
        ax.axvline(0, color="black", linewidth=0.4)
        ax.set_xlabel("Pearson r")
        ax.set_title(year)
    fig.suptitle("Top-10 |off-diagonal correlation| per year (sorted by |r|)", y=1.0)
    fig.tight_layout()
    p = OUT / "top_correlations_by_year.png"
    fig.savefig(p, dpi=120); plt.close(fig)
    print(f"  → {p.name}")


def write_per_year_readme(year, n_rows, corr):
    if year == "2025":
        return  # leave existing
    path = ROOT / f"research/geosolar/exploratory/mode_phase_multi_pair_{year}/README.md"
    note_partial = ""
    if year == "2026":
        note_partial = (" (partial year: 2026-05-09 00:00 UTC through 2026-12-31 23:50 UTC, "
                        "since today is 2026-05-08)")
    txt = f"""# Multi-pair mode-phase dataset, {year}{note_partial}

10-min cadence Sun-Moon, Sun-Mars, Sun-Mercury, Sun-Venus, Sun-Jupiter,
Sun-Saturn, Moon-Mars, Moon-Mercury, Moon-Jupiter, Jupiter-Saturn pair
versor decomposition at the Gainesville lagna (lat=29.65, lon=-82.34).

- Rows: **{n_rows:,}**
- Columns: 204 (per-pair re_k/im_k for k∈{{1,2,3,4,6,7,12}}, magnetic,
  dielectric, mode_ratio, mode_phase, synodic_phase, plus base
  panchanga columns)
- Generated using `npu_engine.jyotisha_engine.compute_pair_interference`
  (post-DEVIATION_001 versor-aware engine).

Cross-year comparison plots and synthesis live at
`research/geosolar/exploratory/mode_phase_multi_year_comparison/`.

This dataset is exploratory. NOT pre-registered.
"""
    path.write_text(txt)
    print(f"  → {path.relative_to(ROOT)}")


def write_synthesis(corrs: dict, n_rows: dict):
    grahas_order = ["Sun", "Moon", "Mars", "Mercury", "Venus", "Jupiter", "Saturn"]
    # Mediator strengths
    rows_med = []
    for g in grahas_order:
        vals_by_yr = {y: mediator_strength(c, g)[0] for y, c in corrs.items()}
        k = len(GRAHA_PAIRS[g])
        rows_med.append((g, k, vals_by_yr))
    # Top-10 per year
    tops = {y: top_offdiag(c, n=10) for y, c in corrs.items()}
    # Mercury-pair specific correlations table
    mercury_pairs = ["sun_mercury", "moon_mercury"]
    non_mercury = [p for p in PAIRS if p not in mercury_pairs]
    mp_rows = []
    for mp in mercury_pairs:
        row = {y: {p: c.loc[mp, p] for p in non_mercury} for y, c in corrs.items()}
        mp_rows.append((mp, row))

    lines = []
    lines.append("# Multi-year mode-phase comparison — 2024 / 2025 / 2026\n")
    lines.append("Cross-year comparison of pair–pair correlation structure of the\n"
                 "versor-decomposed mode_ratio time series at the Gainesville lagna.\n"
                 "Exploratory only. Generated 2026-05-08.\n")
    lines.append("## Datasets\n")
    lines.append("| Year | Source parquet | Rows | Coverage |")
    lines.append("|---|---|---:|---|")
    for y, c in corrs.items():
        cov = "full year" if y in ("2024", "2025") else "2026-05-09 → 2026-12-31 (partial)"
        leap = " (leap year)" if y == "2024" else ""
        lines.append(f"| {y} | all_pairs_modes_{y}.parquet | {n_rows[y]:,} | {cov}{leap} |")
    lines.append("")

    lines.append("## Mediator-strength T(m) per graha, by year\n")
    lines.append("Mean off-diagonal correlation across pair-pair matrix entries that\n"
                 "touch at least one pair containing the named graha. Higher values\n"
                 "indicate that pairs containing that graha are more correlated with\n"
                 "the rest of the system.\n")
    lines.append("| Graha | k pairs | T(m) 2024 | T(m) 2025 | T(m) 2026 | Δ 2024→2025 | Δ 2025→2026 |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for g, k, vals in rows_med:
        v24, v25, v26 = vals["2024"], vals["2025"], vals["2026"]
        d1 = v25 - v24; d2 = v26 - v25
        lines.append(f"| **{g}** | {k} | {v24:+.3f} | {v25:+.3f} | {v26:+.3f} | {d1:+.3f} | {d2:+.3f} |")
    lines.append("")

    lines.append("## Top-10 strongest |off-diagonal correlation| per year\n")
    for y, top in tops.items():
        lines.append(f"### {y}\n")
        lines.append("| Pair A | Pair B | r |")
        lines.append("|---|---|---:|")
        for a, b, v in top:
            lines.append(f"| {a} | {b} | {v:+.3f} |")
        lines.append("")

    lines.append("## Mercury-pair × non-Mercury-pair correlations, by year\n")
    for mp, by_yr in mp_rows:
        lines.append(f"### {mp}\n")
        lines.append("| Other pair | 2024 | 2025 | 2026 |")
        lines.append("|---|---:|---:|---:|")
        for p in non_mercury:
            v24 = by_yr["2024"][p]; v25 = by_yr["2025"][p]; v26 = by_yr["2026"][p]
            lines.append(f"| {p} | {v24:+.3f} | {v25:+.3f} | {v26:+.3f} |")
        lines.append("")

    lines.append("## Caveats\n")
    lines.append("- 2026 is a partial year (May–Dec only, 34,128 timestamps vs ~52,560 "
                 "for full years). Sample size affects correlation estimate variance.\n")
    lines.append("- Mode-decomposition `mode_ratio` time series have substantial within-year "
                 "autocorrelation; pair-pair correlations should be interpreted as long-window "
                 "summaries, not as independent-sample statistics.\n")
    lines.append("- Three years is too few to cover synodic cycles between the slower grahas "
                 "(Jupiter ≈12 yr, Saturn ≈29.5 yr). The pattern of pair-pair coupling can shift "
                 "across years for reasons that are deterministic from the ephemeris.\n")
    lines.append("- This document reports values without interpretation. Whether Mercury "
                 "appears as a stable mediator across years, or whether the role wanders, is "
                 "for the reader to judge from the tables and plots.\n")

    p = OUT / "mode_phase_multi_year_comparison.md"
    p.write_text("\n".join(lines))
    print(f"  → {p.relative_to(ROOT)}")


def main():
    print("[load] correlation matrices")
    corrs = {}
    n_rows = {}
    for year, path in YEARS.items():
        if not path.exists():
            raise SystemExit(f"missing: {path}")
        c, n = load_corr_matrix(path)
        corrs[year] = c
        n_rows[year] = n
        print(f"  {year}: n={n:,}")

    print("\n[plots]")
    plot_3year_matrices(corrs, n_rows)
    plot_mercury_pair_correlations(corrs)
    plot_mediator_strength(corrs)
    plot_top_correlations(corrs)

    print("\n[per-year READMEs]")
    for year, _ in corrs.items():
        write_per_year_readme(year, n_rows[year], corrs[year])

    print("\n[synthesis]")
    write_synthesis(corrs, n_rows)

    # ── console one-liner: Mercury T(m) across years ──
    print("\n" + "=" * 70)
    print("MEDIATOR-STRENGTH T(m) per graha × year")
    print("=" * 70)
    grahas_order = ["Sun", "Moon", "Mars", "Mercury", "Venus", "Jupiter", "Saturn"]
    print(f"  {'graha':>10s}  {'k':>3s}    {'2024':>7s}    {'2025':>7s}    {'2026':>7s}")
    for g in grahas_order:
        v24 = mediator_strength(corrs["2024"], g)[0]
        v25 = mediator_strength(corrs["2025"], g)[0]
        v26 = mediator_strength(corrs["2026"], g)[0]
        flag = " ← Mercury" if g == "Mercury" else ""
        print(f"  {g:>10s}  {len(GRAHA_PAIRS[g]):>3d}    {v24:+.4f}    {v25:+.4f}    {v26:+.4f}{flag}")

    # Mercury comparison
    merc = [mediator_strength(corrs[y], "Mercury")[0] for y in ("2024", "2025", "2026")]
    rest = []
    for g in [x for x in grahas_order if x != "Mercury"]:
        for y in ("2024", "2025", "2026"):
            rest.append(mediator_strength(corrs[y], g)[0])
    rest_mean = np.mean(rest)
    print()
    print(f"Mercury T(m): 2024={merc[0]:+.4f}  2025={merc[1]:+.4f}  2026={merc[2]:+.4f}")
    print(f"  vs other-graha mean over all years: {rest_mean:+.4f}")


if __name__ == "__main__":
    main()
