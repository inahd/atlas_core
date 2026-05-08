"""
Compute the Atlas wave-field-mean scalar for every 10-min timestamp in 2025.

Per spec:
  - For each timestamp t in datasets/panchanga/grid_10min_2025.parquet:
      ch = compute_chart(t, lat=29.65, lon=-82.34)         # Gainesville
      wf = compute_wave_field(ch.grahas,
                              targets=ZODIACAL_MEAN_TARGETS,
                              k_values=[1,2,3,4,6,7,12])
      wave_field_mean = mean(composite_mean[i] for i in 12 zodiac points)
  - ZODIACAL_MEAN_TARGETS = {z0..z11} at longitudes 0,30,...,330 deg

Output:
  research/geosolar/pilot_2025/wave_field_2025.parquet
    timestamp:datetime64[ns,UTC]  wave_field_mean:float32
"""
from __future__ import annotations

import os
import sys
import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from multiprocessing import Pool

ROOT = "/home/inahd/atlas_core"
sys.path.insert(0, ROOT)

GRID_PATH = os.path.join(ROOT, "datasets/panchanga/grid_10min_2025.parquet")
OUT_PATH = os.path.join(ROOT, "research/geosolar/pilot_2025/wave_field_2025.parquet")

LAT, LON = 29.65, -82.34
K_VALUES = [1, 2, 3, 4, 6, 7, 12]
ZODIACAL_MEAN_TARGETS = {f"z{i:02d}": float(i * 30) for i in range(12)}


def _worker(ts_chunk: list[pd.Timestamp]) -> np.ndarray:
    """Compute wave_field_mean for a chunk of UTC timestamps. Returns float32 array."""
    from npu_engine.jyotisha_engine import compute_chart, compute_wave_field
    out = np.empty(len(ts_chunk), dtype=np.float32)
    for i, ts in enumerate(ts_chunk):
        dt = ts.to_pydatetime()
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        ch = compute_chart(dt, LAT, LON)
        wf = compute_wave_field(ch["grahas"], targets=ZODIACAL_MEAN_TARGETS, k_values=K_VALUES)
        means = [wf["targets"][k]["composite_mean"] for k in ZODIACAL_MEAN_TARGETS]
        out[i] = float(np.mean(means))
    return out


def main():
    t0 = time.time()
    grid = pd.read_parquet(GRID_PATH, columns=["timestamp"])
    ts = grid["timestamp"]
    if ts.dt.tz is None:
        ts = ts.dt.tz_localize("UTC")
    ts = ts.dt.tz_convert("UTC")
    n = len(ts)
    print(f"loaded grid: {n} timestamps")

    n_workers = max(1, min(12, os.cpu_count() - 2))
    chunk_size = max(1, n // (n_workers * 8))
    chunks = [ts.iloc[i:i + chunk_size].tolist() for i in range(0, n, chunk_size)]
    print(f"workers={n_workers} chunks={len(chunks)} chunk_size~{chunk_size}")

    out = np.empty(n, dtype=np.float32)
    cursor = 0
    with Pool(processes=n_workers) as pool:
        for j, arr in enumerate(pool.imap(_worker, chunks)):
            out[cursor:cursor + len(arr)] = arr
            cursor += len(arr)
            if (j + 1) % max(1, len(chunks) // 20) == 0:
                pct = 100.0 * cursor / n
                print(f"  progress: {cursor}/{n} ({pct:.1f}%)  elapsed {time.time() - t0:.1f}s")
    assert cursor == n

    df = pd.DataFrame({
        "timestamp": pd.to_datetime(ts.values, utc=True),
        "wave_field_mean": out,
    })
    df["timestamp"] = df["timestamp"].astype("datetime64[ns, UTC]")
    df.to_parquet(OUT_PATH, index=False)
    print(f"wrote {OUT_PATH}: {len(df)} rows")

    # ── sanity ────────────────────────────────────────────────
    s = df["wave_field_mean"]
    print()
    print("=== wave_field_mean distribution ===")
    print(f"  n           = {len(s)}")
    print(f"  n_nan       = {int(s.isna().sum())}")
    print(f"  min         = {float(s.min()):.6f}")
    print(f"  p25         = {float(s.quantile(0.25)):.6f}")
    print(f"  p50 (med)   = {float(s.quantile(0.50)):.6f}")
    print(f"  mean        = {float(s.mean()):.6f}")
    print(f"  p75         = {float(s.quantile(0.75)):.6f}")
    print(f"  max         = {float(s.max()):.6f}")
    print(f"  std         = {float(s.std()):.6f}")
    print(f"  in_[0,1]    = {bool((s >= 0).all() and (s <= 1).all())}")
    print(f"total wall: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
