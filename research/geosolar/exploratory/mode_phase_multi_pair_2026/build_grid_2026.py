"""
Build 2026 panchanga grid at 10-min cadence for the partial year
2026-05-09 00:00 UTC through 2026-12-31 23:50 UTC (today + future).

Saves: datasets/panchanga/grid_10min_2026.parquet
"""
from __future__ import annotations
import os, sys, time
from datetime import datetime, timedelta, timezone
from multiprocessing import Pool

import numpy as np
import pandas as pd

ROOT = "/home/inahd/atlas_core"
sys.path.insert(0, ROOT)

OUT = os.path.join(ROOT, "datasets/panchanga/grid_10min_2026.parquet")

START = datetime(2026, 5, 9, 0, 0, tzinfo=timezone.utc)
END = datetime(2026, 12, 31, 23, 50, tzinfo=timezone.utc)
STEP_MIN = 10


def _worker(args):
    start_ts_ns, n_steps, step_seconds = args
    from npu_engine.field.panchanga_grid import panchanga_at
    import swisseph as swe
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    rows = []
    for i in range(n_steps):
        ts = pd.Timestamp(start_ts_ns + i * step_seconds * 1_000_000_000, unit="ns", tz="UTC")
        rows.append(panchanga_at(ts.to_pydatetime()))
    return rows


def main():
    t0 = time.time()
    step = timedelta(minutes=STEP_MIN)
    n_steps = int((END - START) / step) + 1
    print(f"[grid 2026] {START} .. {END}  steps={n_steps:,}")

    n_workers = max(1, min(12, (os.cpu_count() or 4) - 2))
    chunk_size = max(1, n_steps // (n_workers * 4))
    args_list = []
    start_ns = int(START.timestamp() * 1_000_000_000)
    step_secs = STEP_MIN * 60
    for c in range(0, n_steps, chunk_size):
        cn = min(chunk_size, n_steps - c)
        args_list.append((start_ns + c * step_secs * 1_000_000_000, cn, step_secs))
    print(f"  workers={n_workers}  chunks={len(args_list)}  chunk_size~{chunk_size}")

    rows_all = []
    with Pool(processes=n_workers) as pool:
        cursor = 0
        for j, rows in enumerate(pool.imap(_worker, args_list)):
            rows_all.extend(rows)
            cursor += len(rows)
            if (j + 1) % max(1, len(args_list) // 4) == 0 or j + 1 == len(args_list):
                print(f"  [{cursor:,}/{n_steps:,}]  elapsed {time.time()-t0:.1f}s")

    df = pd.DataFrame(rows_all)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    for c in ("tithi_num", "nakshatra_num", "yoga_num", "karana_num", "vara_num"):
        df[c] = df[c].astype("int8")
    for c in ("tithi_name", "nakshatra_name", "paksha", "vara_name"):
        df[c] = df[c].astype("string")
    df["gandanta_flag"] = df["gandanta_flag"].astype(bool)
    df["eclipse_window_flag"] = df["eclipse_window_flag"].astype(bool)
    df = df.sort_values("timestamp").reset_index(drop=True)
    df.to_parquet(OUT, index=False)
    print(f"\n[write] {OUT}  rows={len(df):,}  size={os.path.getsize(OUT)/1e6:.2f} MB")
    print(f"Total wall: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
