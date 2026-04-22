"""
geosolar_engine.py — Geosolar Field Monitor

Real-time geomagnetic, solar, and seismic data from public feeds.
Every reading timestamped with panchanga state for cross-analysis.

Sources (public, no API key):
  NOAA SWPC: Kp index, GOES X-ray flux, solar wind
  USGS: earthquake feed (past hour, mag 2.5+)

Logs to datasets/geosolar/kp_log.csv — unified log with
  geosolar + panchanga columns for correlation analysis.
"""

import csv
import json
import math
import os
import threading
import time
from collections import defaultdict
from datetime import datetime
from typing import Callable, Dict, List, Optional
from urllib.request import urlopen, Request
from urllib.error import URLError

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
_LOG_DIR = os.path.join(_ROOT, "datasets", "geosolar")
_LOG_PATH = os.path.join(_LOG_DIR, "kp_log.csv")

_TIMEOUT = 12

# URLs
KP_URL = "https://services.swpc.noaa.gov/json/planetary_k_index_1m.json"
XRAY_URL = "https://services.swpc.noaa.gov/json/goes/primary/xrays-1-day.json"
WIND_URL = "https://services.swpc.noaa.gov/json/rtsw/rtsw_wind_1m.json"
SEIS_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_hour.geojson"

LOG_HEADERS = [
    "datetime", "kp", "kp_class", "solar_wind_speed", "solar_wind_bz",
    "flare_class", "flare_active", "xray_flux",
    "seismic_count", "max_magnitude", "field_modifier",
    "tithi", "nakshatra", "hora", "vara", "paksha",
]


# ═══════════════════════════════════════════════════════════
# FETCH HELPERS
# ═══════════════════════════════════════════════════════════

def _fetch(url: str):
    """Fetch JSON. Returns (data, None) or (None, error_string)."""
    try:
        req = Request(url, headers={"User-Agent": "Atlas330/1.0"})
        with urlopen(req, timeout=_TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8")), None
    except Exception as e:
        return None, f"{url.split('/')[-1]}: {e}"


# ═══════════════════════════════════════════════════════════
# FETCH: Kp INDEX
# ═══════════════════════════════════════════════════════════

def fetch_kp() -> dict:
    """Current Kp value + class + 3-hour trend."""
    data, err = _fetch(KP_URL)
    if not data or not isinstance(data, list) or len(data) < 2:
        return {"kp": 0, "kp_class": "unknown", "trend": "unknown",
                "_error": err}

    latest = data[-1]
    try:
        kp = float(latest.get("kp_index", latest.get("Kp", 0)))
    except (ValueError, TypeError):
        kp = 0

    # Classification
    if kp < 2:
        kp_class = "quiet"
    elif kp < 4:
        kp_class = "unsettled"
    elif kp < 5:
        kp_class = "active"
    else:
        kp_class = "storm"

    # 3-hour trend: compare last to 3 hours ago (~180 entries at 1/min)
    trend = "steady"
    if len(data) > 180:
        try:
            earlier = float(data[-180].get("kp_index", data[-180].get("Kp", kp)))
            delta = kp - earlier
            if delta > 0.5:
                trend = "rising"
            elif delta < -0.5:
                trend = "falling"
        except (ValueError, TypeError, KeyError):
            pass

    return {"kp": round(kp, 2), "kp_class": kp_class, "trend": trend}


# ═══════════════════════════════════════════════════════════
# FETCH: GOES X-RAY
# ═══════════════════════════════════════════════════════════

def fetch_xray() -> dict:
    """Current X-ray flux + flare classification."""
    data, err = _fetch(XRAY_URL)
    if not data or not isinstance(data, list):
        return {"flux": 0, "flare_class": "none", "active": False,
                "_error": err}

    latest = data[-1] if data else {}
    try:
        flux = float(latest.get("flux", 0))
    except (ValueError, TypeError):
        flux = 0

    # Flare classification by X-ray flux (W/m²)
    # C: 1e-6, M: 1e-5, X: 1e-4
    if flux >= 1e-4:
        flare_class = "X"
        active = True
    elif flux >= 1e-5:
        flare_class = "M"
        active = True
    elif flux >= 1e-6:
        flare_class = "C"
        active = False
    else:
        flare_class = "none"
        active = False

    return {"flux": flux, "flare_class": flare_class, "active": active}


# ═══════════════════════════════════════════════════════════
# FETCH: SOLAR WIND
# ═══════════════════════════════════════════════════════════

def fetch_solar_wind() -> dict:
    """Solar wind speed, density, Bz component."""
    data, err = _fetch(WIND_URL)
    if not data or not isinstance(data, list):
        return {"speed": 0, "density": 0, "bz": 0, "_error": err}

    latest = data[-1] if data else {}
    try:
        speed = float(latest.get("proton_speed", 0) or 0)
        density = float(latest.get("proton_density", 0) or 0)
        bz = float(latest.get("bz_gsm", 0) or 0)
    except (ValueError, TypeError):
        speed, density, bz = 0, 0, 0

    return {
        "speed": round(speed, 1),
        "density": round(density, 2),
        "bz": round(bz, 2),
    }


# ═══════════════════════════════════════════════════════════
# FETCH: SEISMIC
# ═══════════════════════════════════════════════════════════

def fetch_seismic() -> dict:
    """Recent earthquake events (last hour, mag 2.5+)."""
    data, err = _fetch(SEIS_URL)
    if not data or "features" not in data:
        return {"events": [], "count": 0, "max_magnitude": 0,
                "_error": err}

    events = []
    for f in data["features"]:
        props = f.get("properties", {})
        coords = f.get("geometry", {}).get("coordinates", [0, 0, 0])
        mag = float(props.get("mag", 0) or 0)
        events.append({
            "mag": round(mag, 1),
            "place": props.get("place", ""),
            "depth": round(float(coords[2]) if len(coords) > 2 else 0, 1),
            "time": props.get("time", 0),
            "lat": round(float(coords[1]), 3) if len(coords) > 1 else 0,
            "lon": round(float(coords[0]), 3),
        })

    events.sort(key=lambda e: e["mag"], reverse=True)
    max_mag = events[0]["mag"] if events else 0

    return {
        "events": events[:10],
        "count": len(events),
        "max_magnitude": max_mag,
    }


# ═══════════════════════════════════════════════════════════
# COMBINED STATE
# ═══════════════════════════════════════════════════════════

def get_geosolar_state() -> dict:
    """Fetch all four sources, return combined normalized state."""
    errors = []

    kp = fetch_kp()
    if "_error" in kp and kp["_error"]:
        errors.append(kp.pop("_error"))
    else:
        kp.pop("_error", None)

    xray = fetch_xray()
    if "_error" in xray and xray["_error"]:
        errors.append(xray.pop("_error"))
    else:
        xray.pop("_error", None)

    wind = fetch_solar_wind()
    if "_error" in wind and wind["_error"]:
        errors.append(wind.pop("_error"))
    else:
        wind.pop("_error", None)

    seis = fetch_seismic()
    if "_error" in seis and seis["_error"]:
        errors.append(seis.pop("_error"))
    else:
        seis.pop("_error", None)

    # Field modifier: 0.0 (quiet) to 1.0 (maximum disturbance)
    kp_norm = min(kp["kp"] / 9, 1.0)

    xray_norm = 0
    if xray["flux"] > 0:
        xray_norm = min(max((math.log10(xray["flux"]) + 8) / 5, 0), 1.0)

    wind_norm = 0
    if wind["speed"] > 0:
        wind_norm = min(wind["speed"] / 800, 1.0)  # 800 km/s = extreme
    bz_norm = min(max(-wind["bz"], 0) / 20, 1.0)  # southward Bz, 20nT = extreme

    seis_norm = min(seis["max_magnitude"] / 8, 1.0) if seis["count"] > 0 else 0

    modifier = round(
        0.30 * kp_norm +
        0.20 * xray_norm +
        0.15 * wind_norm +
        0.15 * bz_norm +
        0.20 * seis_norm,
        3,
    )

    return {
        "kp": kp["kp"],
        "kp_class": kp["kp_class"],
        "kp_trend": kp.get("trend", ""),
        "xray_flux": xray["flux"],
        "flare_class": xray["flare_class"],
        "flare_active": xray["active"],
        "solar_wind_speed": wind["speed"],
        "solar_wind_density": wind["density"],
        "solar_wind_bz": wind["bz"],
        "seismic_events": seis["events"],
        "seismic_count": seis["count"],
        "max_magnitude": seis["max_magnitude"],
        "field_modifier": modifier,
        "fetched_at": datetime.now().isoformat(timespec="seconds"),
        "source_errors": errors,
    }


# ═══════════════════════════════════════════════════════════
# LOGGING — unified CSV with panchanga columns
# ═══════════════════════════════════════════════════════════

def _ensure_log():
    """Create log directory and CSV header if needed."""
    os.makedirs(_LOG_DIR, exist_ok=True)
    if not os.path.exists(_LOG_PATH):
        with open(_LOG_PATH, "w", newline="") as f:
            csv.writer(f).writerow(LOG_HEADERS)


def log_geosolar_state(panchanga: Optional[dict] = None) -> dict:
    """
    Fetch current state and append one row to unified CSV.
    panchanga dict should have: tithi, nakshatra, hora/hora_lord, vara, paksha.
    Returns the fetched state.
    """
    _ensure_log()
    state = get_geosolar_state()
    pa = panchanga or {}

    # Normalize hora field
    hora = pa.get("hora_lord", pa.get("hora", ""))
    if isinstance(hora, dict):
        hora = hora.get("hora_lord", "")

    row = [
        state["fetched_at"],
        state["kp"],
        state["kp_class"],
        state["solar_wind_speed"],
        state["solar_wind_bz"],
        state["flare_class"],
        state["flare_active"],
        state["xray_flux"],
        state["seismic_count"],
        state["max_magnitude"],
        state["field_modifier"],
        pa.get("tithi", ""),
        pa.get("nakshatra", ""),
        hora,
        pa.get("vara", ""),
        pa.get("paksha", ""),
    ]

    with open(_LOG_PATH, "a", newline="") as f:
        csv.writer(f).writerow(row)

    return state


def read_log(n: int = 50) -> List[dict]:
    """Return last n rows of unified log as dicts."""
    if not os.path.exists(_LOG_PATH):
        return []
    with open(_LOG_PATH, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return rows[-n:]


# ═══════════════════════════════════════════════════════════
# CORRELATION ANALYSIS
# ═══════════════════════════════════════════════════════════

def correlate_with_panchanga() -> dict:
    """
    Descriptive statistics: mean Kp and flare frequency
    grouped by nakshatra, tithi, hora, vara.
    Requires ≥100 readings to be meaningful.
    """
    rows = read_log(n=100000)  # all rows
    total = len(rows)

    if total < 100:
        return {
            "total_readings": total,
            "status": "insufficient_data",
            "note": (
                f"Only {total} readings logged. "
                f"Need ≥100 for statistics. "
                f"At 6/hour, this takes ~17 hours of logging. "
                f"Descriptive statistics only — no causal inference."
            ),
            "by_nakshatra": {},
            "by_tithi": {},
            "by_hora": {},
            "by_vara": {},
        }

    def _group_stats(rows: list, key: str) -> dict:
        groups = defaultdict(lambda: {"kp_sum": 0, "mod_sum": 0,
                                       "flare_count": 0, "n": 0})
        for r in rows:
            val = r.get(key, "").strip()
            if not val:
                continue
            g = groups[val]
            try:
                g["kp_sum"] += float(r.get("kp", 0) or 0)
                g["mod_sum"] += float(r.get("field_modifier", 0) or 0)
                if r.get("flare_active", "").lower() in ("true", "1"):
                    g["flare_count"] += 1
                g["n"] += 1
            except (ValueError, TypeError):
                pass

        result = {}
        for val, g in sorted(groups.items()):
            if g["n"] == 0:
                continue
            result[val] = {
                "mean_kp": round(g["kp_sum"] / g["n"], 3),
                "mean_modifier": round(g["mod_sum"] / g["n"], 3),
                "flare_count": g["flare_count"],
                "n_readings": g["n"],
            }
        return result

    # Date range
    dates = [r.get("datetime", "") for r in rows if r.get("datetime")]
    date_range = [dates[0], dates[-1]] if dates else ["", ""]

    return {
        "total_readings": total,
        "date_range": date_range,
        "status": "ok",
        "note": "descriptive statistics only — no causal inference",
        "by_nakshatra": _group_stats(rows, "nakshatra"),
        "by_tithi": _group_stats(rows, "tithi"),
        "by_hora": _group_stats(rows, "hora"),
        "by_vara": _group_stats(rows, "vara"),
    }


# ═══════════════════════════════════════════════════════════
# BACKGROUND LOGGER
# ═══════════════════════════════════════════════════════════

_bg_thread = None
_bg_running = False


def _start_geosolar_logger(get_panchanga_fn: Callable, interval_s: int = 600):
    """
    Start background thread that logs geosolar + panchanga every interval_s.
    get_panchanga_fn: callable returning panchanga dict (injected from kernel).
    """
    global _bg_thread, _bg_running

    if _bg_running:
        return

    def _loop():
        global _bg_running
        _bg_running = True
        print(f"  [geosolar] background logger started (every {interval_s}s)")
        while _bg_running:
            try:
                pa = get_panchanga_fn()
                state = log_geosolar_state(pa)
                kp_v = state.get("kp", "?")
                flare = state.get("flare_class", "?")
                seis_c = state.get("seismic_count", "?")
                errs = state.get("source_errors", [])
                msg = f"Kp={kp_v} flare={flare} quakes={seis_c}"
                if errs:
                    msg += f" errors={len(errs)}"
                print(f"  [geosolar] {msg}")
            except Exception as e:
                print(f"  [geosolar] logger error: {e}")
            time.sleep(interval_s)

    _bg_thread = threading.Thread(target=_loop, daemon=True)
    _bg_thread.start()


def _stop_geosolar_logger():
    """Stop the background logger."""
    global _bg_running
    _bg_running = False
