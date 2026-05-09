"""
panchanga_grid.py — bulk panchanga-state generator for arbitrary time ranges.

Wrapper around Swiss Ephemeris (Lahiri ayanāṃśa) producing the canonical
schema used by the geosolar archive pilot:

    timestamp           datetime64[ns, UTC]
    tithi_num           int8     (1..30)
    tithi_name          string   (IAST)
    paksha              string   ('śukla' or 'kṛṣṇa')
    nakshatra_num       int8     (1..27)
    nakshatra_name      string   (IAST)
    yoga_num            int8     (1..27)
    karana_num          int8     (1..11)
    vara_num            int8     (1..7, Sunday=1)
    vara_name           string   (IAST, no emoji)
    gandanta_flag       bool
    eclipse_window_flag bool

Definitions:
    Tithi:        floor((moon_sid - sun_sid) mod 360 / 12), 0..29 → 1..30 (1-based)
    Nakshatra:    floor(moon_sid mod 360 / (360/27)), 0..26 → 1..27 (1-based)
    Yoga:         floor((moon_sid + sun_sid) mod 360 / (360/27)) + 1, 1..27
    Karana:       see _karana_num() — 4 fixed (Śakuni 8, Catuṣpāda 9, Nāga 10,
                  Kiṃstughna 11) at half-tithi indices 57, 58, 59, 0;
                  7 movable (Bava 1 .. Viṣṭi 7) cycle through 1..56.
    Gandanta:     Moon within last 3°20' (= 3.3333°) of Āśleṣā (nak idx 8),
                  Jyeṣṭhā (nak idx 17), or Revatī (nak idx 26). The "last
                  3°20'" is the final quarter of each 13°20' nakshatra arc;
                  i.e., position within nakshatra > (13.3333 − 3.3333) = 10°.
    Eclipse window: Moon within 12° of either Rāhu (mean node) or Ketu
                  (Rāhu + 180°), measured as great-circle arc-distance modulo
                  360.

This module performs ~3 swisseph calls per timestamp (Sun, Moon, Mean Node).
For a one-year 10-minute grid (52,560 rows) total runtime is ~10–20 s.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Iterable

import numpy as np
import pandas as pd
import swisseph as swe


# ── Canonical IAST tables ─────────────────────────────────────────

TITHI_NAMES_IAST = [
    "Pratipadā", "Dvitīyā", "Tṛtīyā", "Caturthī", "Pañcamī",
    "Ṣaṣṭhī", "Saptamī", "Aṣṭamī", "Navamī", "Daśamī",
    "Ekādaśī", "Dvādaśī", "Trayodaśī", "Caturdaśī", "Pūrṇimā",
    "Pratipadā", "Dvitīyā", "Tṛtīyā", "Caturthī", "Pañcamī",
    "Ṣaṣṭhī", "Saptamī", "Aṣṭamī", "Navamī", "Daśamī",
    "Ekādaśī", "Dvādaśī", "Trayodaśī", "Caturdaśī", "Amāvasyā",
]

NAKSHATRA_NAMES_IAST = [
    "Aśvinī", "Bharaṇī", "Kṛttikā", "Rohiṇī", "Mṛgaśīrṣā",
    "Ārdrā", "Punarvasu", "Puṣya", "Āśleṣā", "Maghā",
    "Pūrva Phalgunī", "Uttara Phalgunī", "Hasta", "Citrā", "Svātī",
    "Viśākhā", "Anurādhā", "Jyeṣṭhā", "Mūla", "Pūrva Āṣāḍhā",
    "Uttara Āṣāḍhā", "Śravaṇa", "Dhaniṣṭhā", "Śatabhiṣā",
    "Pūrva Bhādrapadā", "Uttara Bhādrapadā", "Revatī",
]

# vara_num: Sunday=1 ... Saturday=7
# Python datetime.weekday(): Monday=0 ... Sunday=6
# Mapping: vara_num = ((weekday + 1) % 7) + 1
VARA_NAMES_IAST = [
    None,            # 0 — unused
    "Ravivāra",      # 1 Sun
    "Somavāra",      # 2 Mon
    "Maṅgalavāra",   # 3 Tue
    "Budhavāra",     # 4 Wed
    "Guruvāra",      # 5 Thu
    "Śukravāra",     # 6 Fri
    "Śanivāra",      # 7 Sat
]

# Gandanta nakshatras (0-indexed): Āśleṣā=8, Jyeṣṭhā=17, Revatī=26
_GANDANTA_NAK_IDX = {8, 17, 26}
_NAK_DEG = 360.0 / 27.0      # 13.333…
_GANDANTA_TAIL_DEG = 3.0 + 20.0 / 60.0   # 3°20' = 3.3333°

# Eclipse window: 12° from node (Rāhu or Ketu)
_ECLIPSE_THRESHOLD_DEG = 12.0


# ── Karana numbering ──────────────────────────────────────────────

def _karana_num(half_tithi_idx: int) -> int:
    """Return canonical karana number 1..11.

    Layout used here:
       1 Bava, 2 Balava, 3 Kaulava, 4 Taitila, 5 Garaja, 6 Vaṇij, 7 Viṣṭi
       8 Śakuni    (half-tithi 57)
       9 Catuṣpāda (half-tithi 58)
      10 Nāga      (half-tithi 59)
      11 Kiṃstughna (half-tithi 0)
    """
    n = int(half_tithi_idx) % 60
    if n == 0:
        return 11
    if n == 57:
        return 8
    if n == 58:
        return 9
    if n == 59:
        return 10
    # Movable karanas cycle Bava→Viṣṭi across half-tithis 1..56
    return ((n - 1) % 7) + 1


# ── Helpers ───────────────────────────────────────────────────────

def _vara_num(dt: datetime) -> int:
    """Sunday=1 .. Saturday=7 from a UTC-aware datetime."""
    return ((dt.weekday() + 1) % 7) + 1


def _arc_distance(a_deg: float, b_deg: float) -> float:
    """Smaller of the two arcs between two longitudes (degrees, 0..180)."""
    d = abs((a_deg - b_deg) % 360.0)
    return min(d, 360.0 - d)


# ── Single-timestamp computation ──────────────────────────────────

def panchanga_at(dt_utc: datetime) -> dict:
    """Compute all canonical-schema fields for one UTC timestamp."""
    if dt_utc.tzinfo is None:
        dt_utc = dt_utc.replace(tzinfo=timezone.utc)

    swe.set_sid_mode(swe.SIDM_LAHIRI)

    hour_dec = dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, hour_dec)
    aya = swe.get_ayanamsa_ut(jd)

    sun_trop = swe.calc_ut(jd, swe.SUN)[0][0]
    moon_trop = swe.calc_ut(jd, swe.MOON)[0][0]
    rahu_trop = swe.calc_ut(jd, swe.MEAN_NODE)[0][0]

    sun_sid = (sun_trop - aya) % 360.0
    moon_sid = (moon_trop - aya) % 360.0
    rahu_sid = (rahu_trop - aya) % 360.0
    ketu_sid = (rahu_sid + 180.0) % 360.0

    # Tithi 0..29, then 1..30
    phase = (moon_sid - sun_sid) % 360.0
    tidx0 = int(phase // 12.0) % 30
    tithi_num = tidx0 + 1
    paksha = "śukla" if tidx0 < 15 else "kṛṣṇa"
    tithi_name = TITHI_NAMES_IAST[tidx0]

    # Nakshatra 0..26 (1-based 1..27)
    nidx0 = int(moon_sid // _NAK_DEG) % 27
    nakshatra_num = nidx0 + 1
    nakshatra_name = NAKSHATRA_NAMES_IAST[nidx0]

    # Yoga 1..27
    yoga_num = int(((moon_sid + sun_sid) % 360.0) // _NAK_DEG) % 27 + 1

    # Karana 1..11
    half_tithi = int(phase // 6.0) % 60
    karana_num = _karana_num(half_tithi)

    # Vara
    vnum = _vara_num(dt_utc)
    vara_name = VARA_NAMES_IAST[vnum]

    # Gandanta: position within current nakshatra
    pos_in_nak = moon_sid - nidx0 * _NAK_DEG
    gandanta_flag = (nidx0 in _GANDANTA_NAK_IDX) and (pos_in_nak > (_NAK_DEG - _GANDANTA_TAIL_DEG))

    # Eclipse window: Moon within 12° of either node
    d_rahu = _arc_distance(moon_sid, rahu_sid)
    d_ketu = _arc_distance(moon_sid, ketu_sid)
    eclipse_window_flag = (d_rahu <= _ECLIPSE_THRESHOLD_DEG) or (d_ketu <= _ECLIPSE_THRESHOLD_DEG)

    return {
        "timestamp": dt_utc,
        "tithi_num": np.int8(tithi_num),
        "tithi_name": tithi_name,
        "paksha": paksha,
        "nakshatra_num": np.int8(nakshatra_num),
        "nakshatra_name": nakshatra_name,
        "yoga_num": np.int8(yoga_num),
        "karana_num": np.int8(karana_num),
        "vara_num": np.int8(vnum),
        "vara_name": vara_name,
        "gandanta_flag": bool(gandanta_flag),
        "eclipse_window_flag": bool(eclipse_window_flag),
    }


# ── Bulk grid ─────────────────────────────────────────────────────

def compute_panchanga_grid(
    start_dt: datetime,
    end_dt: datetime,
    step_minutes: int = 10,
    progress_every: int = 5000,
) -> pd.DataFrame:
    """Compute panchanga grid for [start_dt, end_dt] inclusive at step_minutes cadence.

    Both bounds are UTC-aware (tzinfo set to UTC if naïve).
    """
    if start_dt.tzinfo is None:
        start_dt = start_dt.replace(tzinfo=timezone.utc)
    if end_dt.tzinfo is None:
        end_dt = end_dt.replace(tzinfo=timezone.utc)

    swe.set_sid_mode(swe.SIDM_LAHIRI)

    step = timedelta(minutes=step_minutes)
    n_steps = int((end_dt - start_dt) / step) + 1

    rows = []
    cur = start_dt
    for i in range(n_steps):
        rows.append(panchanga_at(cur))
        cur = cur + step
        if progress_every and (i + 1) % progress_every == 0:
            pct = int((i + 1) / n_steps * 100)
            print(f"  [grid] {i+1}/{n_steps} ({pct}%)")

    df = pd.DataFrame(rows)
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
    return df
