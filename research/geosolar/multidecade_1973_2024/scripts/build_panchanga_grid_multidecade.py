"""
Generate the 10-min panchanga grid for 1973-01-01 00:00:00 UTC through
2024-12-31 23:50:00 UTC, written per-decade to datasets/panchanga/.

Decade partitioning (matches datasets/geosolar/archive/ scheme):
    1970s  →  1973-01-01 .. 1979-12-31  (7 years)
    1980s  →  1980-01-01 .. 1989-12-31
    1990s  →  1990-01-01 .. 1999-12-31
    2000s  →  2000-01-01 .. 2009-12-31
    2010s  →  2010-01-01 .. 2019-12-31
    2020s  →  2020-01-01 .. 2024-12-31  (5 years)

Each output is `datasets/panchanga/grid_10min_{decade}s.parquet`.
Schema is identical to the existing `grid_10min_2025.parquet`.

Parallelized with multiprocessing (n_workers = min(12, cpu-2)).
Each worker computes panchanga rows for a contiguous sub-range. Per-row work
is ~3 swisseph calls; expected total runtime is well under an hour.
"""
from __future__ import annotations

import os
import sys
import time
from datetime import datetime, timedelta, timezone
from multiprocessing import Pool

import numpy as np
import pandas as pd

ROOT = "/home/inahd/atlas_core"
sys.path.insert(0, ROOT)

OUT_DIR = os.path.join(ROOT, "datasets/panchanga")

DECADES = [
    ("1970s", datetime(1973, 1, 1, 0, 0, tzinfo=timezone.utc),
              datetime(1979, 12, 31, 23, 50, tzinfo=timezone.utc)),
    ("1980s", datetime(1980, 1, 1, 0, 0, tzinfo=timezone.utc),
              datetime(1989, 12, 31, 23, 50, tzinfo=timezone.utc)),
    ("1990s", datetime(1990, 1, 1, 0, 0, tzinfo=timezone.utc),
              datetime(1999, 12, 31, 23, 50, tzinfo=timezone.utc)),
    ("2000s", datetime(2000, 1, 1, 0, 0, tzinfo=timezone.utc),
              datetime(2009, 12, 31, 23, 50, tzinfo=timezone.utc)),
    ("2010s", datetime(2010, 1, 1, 0, 0, tzinfo=timezone.utc),
              datetime(2019, 12, 31, 23, 50, tzinfo=timezone.utc)),
    ("2020s", datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc),
              datetime(2024, 12, 31, 23, 50, tzinfo=timezone.utc)),
]

STEP_MIN = 10


def _worker(args):
    start_ts_int, n_steps, step_seconds = args
    # Each worker re-imports — swisseph's set_sid_mode is per-process global.
    from npu_engine.field.panchanga_grid import panchanga_at
    import swisseph as swe
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    rows = []
    for i in range(n_steps):
        ts = pd.Timestamp(start_ts_int + i * step_seconds * 1_000_000_000, unit="ns", tz="UTC")
        rows.append(panchanga_at(ts.to_pydatetime()))
    return rows


def _generate_decade(label, start_dt, end_dt):
    out_path = os.path.join(OUT_DIR, f"grid_10min_{label}.parquet")
    if os.path.exists(out_path):
        existing = pd.read_parquet(out_path, columns=["timestamp"])
        n_existing = len(existing)
        first = existing["timestamp"].min()
        last = existing["timestamp"].max()
        print(f"[{label}] EXISTS: {n_existing:,} rows {first} .. {last} → skip")
        return

    step = timedelta(minutes=STEP_MIN)
    n_steps = int((end_dt - start_dt) / step) + 1
    n_workers = max(1, min(12, (os.cpu_count() or 4) - 2))
    chunk_size = max(1, n_steps // (n_workers * 4))
    print(f"[{label}] {start_dt} .. {end_dt}  steps={n_steps:,}  workers={n_workers}  chunk_size~{chunk_size}")

    start_ts_int = int(start_dt.timestamp() * 1_000_000_000)
    step_seconds = STEP_MIN * 60
    args_list = []
    for chunk_start in range(0, n_steps, chunk_size):
        chunk_n = min(chunk_size, n_steps - chunk_start)
        chunk_first_ts_ns = start_ts_int + chunk_start * step_seconds * 1_000_000_000
        args_list.append((chunk_first_ts_ns, chunk_n, step_seconds))

    t0 = time.time()
    all_rows = []
    with Pool(processes=n_workers) as pool:
        cursor = 0
        for j, rows in enumerate(pool.imap(_worker, args_list)):
            all_rows.extend(rows)
            cursor += len(rows)
            if (j + 1) % max(1, len(args_list) // 20) == 0 or j + 1 == len(args_list):
                pct = 100.0 * cursor / n_steps
                elapsed = time.time() - t0
                print(f"  [{label}] {cursor:,}/{n_steps:,} ({pct:.1f}%)  elapsed {elapsed:.1f}s")

    df = pd.DataFrame(all_rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["tithi_num"] = df["tithi_num"].astype("int8")
    df["nakshatra_num"] = df["nakshatra_num"].astype("int8")
    df["yoga_num"] = df["yoga_num"].astype("int8")
    df["karana_num"] = df["karana_num"].astype("int8")
    df["vara_num"] = df["vara_num"].astype("int8")
    df["tithi_name"] = df["tithi_name"].astype("string")
    df["nakshatra_name"] = df["nakshatra_name"].astype("string")
    df["paksha"] = df["paksha"].astype("string")
    df["vara_name"] = df["vara_name"].astype("string")
    df["gandanta_flag"] = df["gandanta_flag"].astype(bool)
    df["eclipse_window_flag"] = df["eclipse_window_flag"].astype(bool)
    df = df.sort_values("timestamp").reset_index(drop=True)

    df.to_parquet(out_path, index=False)
    print(f"  [{label}] wrote {out_path}  rows={len(df):,}  wall={time.time()-t0:.1f}s")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    t0 = time.time()
    for label, start_dt, end_dt in DECADES:
        _generate_decade(label, start_dt, end_dt)
    print(f"\nTOTAL panchanga grid wall: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
