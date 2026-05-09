"""
Multi-pair versor mode-decomposition dataset build for 2026 (May 9 - Dec 31).
Mirrors the 2024 / 2025 builds. PARQUET ONLY — no plots here.
"""
from __future__ import annotations
import math, os, sys, time
from datetime import timezone
from multiprocessing import Pool

import numpy as np
import pandas as pd

ROOT = "/home/inahd/atlas_core"
sys.path.insert(0, ROOT)

OUT_DIR = os.path.join(ROOT, "research/geosolar/exploratory/mode_phase_multi_pair_2026")
GRID = os.path.join(ROOT, "datasets/panchanga/grid_10min_2026.parquet")
OUT_PARQUET = os.path.join(OUT_DIR, "all_pairs_modes_2026.parquet")

LAT, LON = 29.65, -82.34
K_VALUES = [1, 2, 3, 4, 6, 7, 12]
EPS = 1e-12

PAIRS = [
    ("sun_moon",     "Sun",     "Moon"),
    ("sun_mars",     "Sun",     "Mars"),
    ("sun_mercury",  "Sun",     "Mercury"),
    ("sun_venus",    "Sun",     "Venus"),
    ("sun_jupiter",  "Sun",     "Jupiter"),
    ("sun_saturn",   "Sun",     "Saturn"),
    ("moon_mars",    "Moon",    "Mars"),
    ("moon_mercury", "Moon",    "Mercury"),
    ("moon_jupiter", "Moon",    "Jupiter"),
    ("jupiter_saturn", "Jupiter", "Saturn"),
]


def _worker(ts_chunk):
    from npu_engine.jyotisha_engine import compute_chart, compute_pair_interference
    n = len(ts_chunk)
    out = {"lagna_long": np.empty(n, dtype=np.float32)}
    grahas_needed = ["Sun", "Moon", "Mars", "Mercury", "Venus", "Jupiter", "Saturn"]
    for g in grahas_needed:
        out[f"{g.lower()}_long"] = np.empty(n, dtype=np.float32)
    for pname, _, _ in PAIRS:
        for k in K_VALUES:
            out[f"{pname}_re_k{k}"] = np.empty(n, dtype=np.float32)
            out[f"{pname}_im_k{k}"] = np.empty(n, dtype=np.float32)
        out[f"{pname}_magnetic"] = np.empty(n, dtype=np.float32)
        out[f"{pname}_dielectric"] = np.empty(n, dtype=np.float32)
        out[f"{pname}_mode_ratio"] = np.empty(n, dtype=np.float32)
        out[f"{pname}_mode_phase"] = np.empty(n, dtype=np.float32)
        out[f"{pname}_synodic_phase"] = np.empty(n, dtype=np.float32)
    for i, ts in enumerate(ts_chunk):
        dt = ts.to_pydatetime()
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        ch = compute_chart(dt, LAT, LON)
        lagna = float(ch["ascendant"]["deg_absolute"])
        out["lagna_long"][i] = lagna
        gl = {}
        for g in grahas_needed:
            v = float(ch["grahas"][g]["deg_absolute"])
            out[f"{g.lower()}_long"][i] = v
            gl[g] = v
        for pname, g1, g2 in PAIRS:
            mag_total = 0.0; die_total = 0.0
            for k in K_VALUES:
                z = compute_pair_interference(gl[g1], gl[g2], lagna, k)
                re = z.real; im = z.imag
                out[f"{pname}_re_k{k}"][i] = re
                out[f"{pname}_im_k{k}"][i] = im
                mag_total += abs(re); die_total += abs(im)
            out[f"{pname}_magnetic"][i] = mag_total
            out[f"{pname}_dielectric"][i] = die_total
            out[f"{pname}_mode_ratio"][i] = die_total / (mag_total + die_total + EPS)
            out[f"{pname}_mode_phase"][i] = math.atan2(die_total, mag_total)
            sep = (gl[g2] - gl[g1]) % 360.0
            out[f"{pname}_synodic_phase"][i] = math.radians(sep)
    return out


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    t0 = time.time()
    print(f"[load] {GRID}")
    grid = pd.read_parquet(GRID)
    grid["timestamp"] = pd.to_datetime(grid["timestamp"], utc=True).astype("datetime64[ns, UTC]")
    n = len(grid)
    print(f"  rows: {n:,}")

    n_workers = max(1, min(12, (os.cpu_count() or 4) - 2))
    chunk_size = max(1, n // (n_workers * 8))
    chunks = [grid["timestamp"].iloc[i:i + chunk_size].tolist() for i in range(0, n, chunk_size)]
    print(f"  workers={n_workers}  chunks={len(chunks)}  chunk_size~{chunk_size}")

    combined = None
    cursor = 0
    with Pool(processes=n_workers) as pool:
        for j, partial in enumerate(pool.imap(_worker, chunks)):
            k = len(next(iter(partial.values())))
            if combined is None:
                combined = {col: np.empty(n, dtype=np.float32) for col in partial}
            for col, arr in partial.items():
                combined[col][cursor:cursor + k] = arr
            cursor += k
            if (j + 1) % max(1, len(chunks) // 10) == 0 or j + 1 == len(chunks):
                print(f"  progress: {cursor:,}/{n:,} ({100.0*cursor/n:.1f}%)  elapsed {time.time()-t0:.1f}s")

    df = pd.DataFrame(combined)
    df.insert(0, "timestamp", grid["timestamp"].values)
    for col in ("tithi_num", "nakshatra_num", "paksha", "vara_num", "gandanta_flag"):
        if col in grid.columns:
            df[col] = grid[col].values
    df.to_parquet(OUT_PARQUET, index=False)
    print(f"[write] {OUT_PARQUET}  rows={len(df):,}  cols={len(df.columns)}  size={os.path.getsize(OUT_PARQUET)/1e6:.1f} MB")
    print(f"Total wall: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
