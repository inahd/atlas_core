"""
jyotisha_engine.py — Vedic chart computation engine.

Pure functions. No Flask, no routes, no kernel dependency.
Uses real Swiss Ephemeris for all positions.
"""

import json
import math
import os
from datetime import datetime
from itertools import combinations
from typing import Dict, List, Optional

import swisseph as swe

from npu_engine.jyotish_utils import (
    normalize_rashi, normalize_graha, rashi_from_longitude,
    rashi_index, parse_dms, load_rashi_lords, load_graha_dignity,
    load_graha_friendship, load_graha_aspects,
    nak_from_longitude, nak_index_from_longitude, pada_from_longitude,
    nak_lord_from_longitude, NAKSHATRAS, TITHIS, TITHI_DEITIES,
    _RASHI_IAST, _RASHI_ENGLISH,
)

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# ── swisseph graha constants ─────────────────────────────
_SWE_GRAHAS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
    "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER, "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
}
# Rahu = mean node; Ketu = Rahu + 180
_SWE_RAHU = swe.MEAN_NODE

# ── ayanamsha map ────────────────────────────────────────
_AYANAMSHA_MAP = {
    "lahiri": swe.SIDM_LAHIRI,
    "raman": swe.SIDM_RAMAN,
    "kp": swe.SIDM_KRISHNAMURTI,
    "krishnamurti": swe.SIDM_KRISHNAMURTI,
    "yukteshwar": swe.SIDM_YUKTESHWAR,
    "custom": None,  # requires custom_ayanamsha_deg parameter
}

# ── combustion orbs (degrees) ────────────────────────────
_COMBUST_ORBS = {
    "Moon": (12, 12), "Mars": (17, 17), "Mercury": (14, 12),
    "Jupiter": (11, 11), "Venus": (10, 8), "Saturn": (15, 15),
}

# ── tara bala names ──────────────────────────────────────
_TARA_NAMES = [
    "Janma", "Sampat", "Vipat", "Kshema", "Pratyari",
    "Sadhaka", "Vadha", "Mitra", "Ati-Mitra",
]
_TARA_FAVORABLE = {"Sampat", "Kshema", "Sadhaka", "Mitra", "Ati-Mitra"}
_TARA_UNFAVORABLE = {"Vipat", "Pratyari", "Vadha"}


# ══════════════════════════════════════════════════════════
# A) COMPUTE CHART
# ══════════════════════════════════════════════════════════

def compute_chart(
    dt_utc: datetime,
    lat: float,
    lon: float,
    ayanamsha: str = "lahiri",
    house_system: str = "whole_sign",
    varga: str = "D1",
    custom_ayanamsha_deg: float = None,
) -> dict:
    """Compute a full Vedic chart from datetime + location."""

    if house_system != "whole_sign":
        raise NotImplementedError(f"House system '{house_system}' not yet implemented. Use 'whole_sign'.")

    if varga not in ("D1", "D9"):
        raise NotImplementedError(f"Varga '{varga}' not yet implemented. Use 'D1' or 'D9'.")

    if ayanamsha.lower() == "custom" and custom_ayanamsha_deg is None:
        raise ValueError("ayanamsha='custom' requires custom_ayanamsha_deg to be provided.")

    # Julian day
    hour_dec = dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, hour_dec)

    # Ayanamsha: custom override or swe computed
    if custom_ayanamsha_deg is not None:
        aya_deg = custom_ayanamsha_deg
    else:
        sid_mode = _AYANAMSHA_MAP.get(ayanamsha.lower(), swe.SIDM_LAHIRI)
        swe.set_sid_mode(sid_mode)
        aya_deg = swe.get_ayanamsa_ut(jd)

    # Ascendant (tropical, then subtract ayanamsha)
    _cusps, ascmc = swe.houses(jd, lat, lon, b"W")
    asc_trop = ascmc[0]
    asc_sid = (asc_trop - aya_deg) % 360
    asc_rashi = rashi_from_longitude(asc_sid)
    asc_rashi_idx = rashi_index(asc_rashi)

    ascendant = {
        "rashi": asc_rashi,
        "rashi_english": _RASHI_ENGLISH[asc_rashi_idx] if 0 <= asc_rashi_idx < 12 else "",
        "deg_in_rashi": round(asc_sid % 30, 4),
        "deg_absolute": round(asc_sid, 4),
        "nakshatra": nak_from_longitude(asc_sid),
        "pada": pada_from_longitude(asc_sid),
        "nakshatra_lord": nak_lord_from_longitude(asc_sid),
    }

    # Graha positions
    grahas = {}
    sun_long = None

    for graha_name, swe_id in _SWE_GRAHAS.items():
        result = swe.calc_ut(jd, swe_id)
        trop_lon = result[0][0]
        speed = result[0][3]
        sid_lon = (trop_lon - aya_deg) % 360

        if varga == "D9":
            sid_lon = _navamsha_longitude(sid_lon)

        graha_rashi = rashi_from_longitude(sid_lon)
        graha_rashi_idx = rashi_index(graha_rashi)
        bhava = ((graha_rashi_idx - asc_rashi_idx) % 12) + 1

        entry = {
            "rashi": graha_rashi,
            "rashi_english": _RASHI_ENGLISH[graha_rashi_idx] if 0 <= graha_rashi_idx < 12 else "",
            "deg_in_rashi": round(sid_lon % 30, 4),
            "deg_absolute": round(sid_lon, 4),
            "nakshatra": nak_from_longitude(sid_lon),
            "pada": pada_from_longitude(sid_lon),
            "bhava": bhava,
            "retrograde": speed < 0,
            "speed": round(speed, 4),
            "combust": None,
            "dignity": None,
            "nakshatra_lord": nak_lord_from_longitude(sid_lon),
            "name_iast": normalize_graha(graha_name)["iast"],
        }
        grahas[graha_name] = entry
        if graha_name == "Sun":
            sun_long = sid_lon

    # Rahu & Ketu
    rahu_result = swe.calc_ut(jd, _SWE_RAHU)
    rahu_trop = rahu_result[0][0]
    rahu_speed = rahu_result[0][3]
    rahu_sid = (rahu_trop - aya_deg) % 360
    ketu_sid = (rahu_sid + 180) % 360

    if varga == "D9":
        rahu_sid = _navamsha_longitude(rahu_sid)
        ketu_sid = _navamsha_longitude(ketu_sid)

    for name, sid_lon, spd in [("Rahu", rahu_sid, rahu_speed), ("Ketu", ketu_sid, -rahu_speed)]:
        graha_rashi = rashi_from_longitude(sid_lon)
        graha_rashi_idx = rashi_index(graha_rashi)
        bhava = ((graha_rashi_idx - asc_rashi_idx) % 12) + 1
        grahas[name] = {
            "rashi": graha_rashi,
            "rashi_english": _RASHI_ENGLISH[graha_rashi_idx] if 0 <= graha_rashi_idx < 12 else "",
            "deg_in_rashi": round(sid_lon % 30, 4),
            "deg_absolute": round(sid_lon, 4),
            "nakshatra": nak_from_longitude(sid_lon),
            "pada": pada_from_longitude(sid_lon),
            "bhava": bhava,
            "retrograde": True,
            "speed": round(spd, 4),
            "combust": None,
            "dignity": None,
            "nakshatra_lord": nak_lord_from_longitude(sid_lon),
            "name_iast": normalize_graha(name)["iast"],
        }

    # Bhavas (whole-sign)
    rashi_lords = load_rashi_lords()
    bhavas = {}
    for b in range(1, 13):
        b_rashi_idx = (asc_rashi_idx + b - 1) % 12
        b_rashi = _RASHI_IAST[b_rashi_idx]
        b_lord = rashi_lords.get(b_rashi, "")
        occupants = [g for g, data in grahas.items() if data["bhava"] == b]
        bhavas[b] = {
            "rashi": b_rashi,
            "rashi_english": _RASHI_ENGLISH[b_rashi_idx],
            "lord": b_lord,
            "occupants": occupants,
        }

    # Combustion, dignity, aspects
    assess_combustion(grahas, sun_long)
    assess_dignity(grahas)
    aspects = compute_aspects(grahas)

    # Tithi
    moon_long = grahas["Moon"]["deg_absolute"]
    tithi = compute_tithi(sun_long, moon_long)

    # Wave field (two-source interference)
    # Include lagna as a target point
    wave_targets = {name: g["deg_absolute"] for name, g in grahas.items()}
    wave_targets["Lagna"] = asc_sid
    phase_pairs = compute_wave_field(grahas, targets=wave_targets)
    chladni_field = compute_nakshatra_field(grahas)

    return {
        "meta": {
            "ayanamsha": ayanamsha,
            "ayanamsha_deg": round(aya_deg, 4),
            "house_system": house_system,
            "varga": varga,
            "jd": round(jd, 6),
            "dt_utc": dt_utc.isoformat(),
        },
        "ascendant": ascendant,
        "grahas": grahas,
        "bhavas": bhavas,
        "aspects": aspects,
        "yogas_detected": [],
        "tara_bala": None,
        "tithi": tithi,
        "phase_pairs": phase_pairs,
        "chladni_field": chladni_field,
    }


def _navamsha_longitude(sid_lon: float) -> float:
    """D9 navamsha: compute navamsha sign index from rashi longitude."""
    rashi_idx = int((sid_lon % 360) / 30) % 12
    deg_in_rashi = sid_lon % 30
    navamsha_offset = int(deg_in_rashi / (30 / 9))
    # Origin depends on element of rashi
    element_group = rashi_idx % 4  # 0=fire, 1=earth, 2=air, 3=water
    # Fire rashis (0,4,8) start from Aries(0), Earth(1,5,9) from Capricorn(9),
    # Air(2,6,10) from Libra(7), Water(3,7,11) from Cancer(3)  -- Parashara
    # But element_group cycles as: Aries=fire(0), Taurus=earth(1), Gemini=air(2), Cancer=water(3)
    origins = {0: 0, 1: 9, 2: 6, 3: 3}
    nav_rashi_idx = (origins[element_group] + navamsha_offset) % 12
    return nav_rashi_idx * 30.0 + (deg_in_rashi % (30 / 9)) * 9


# ══════════════════════════════════════════════════════════
# B) COMBUSTION
# ══════════════════════════════════════════════════════════

def assess_combustion(grahas: dict, sun_long: float):
    """Update graha dicts with combustion status. Computed from elongation."""
    if sun_long is None:
        return
    for name, orbs in _COMBUST_ORBS.items():
        if name not in grahas:
            continue
        g = grahas[name]
        elongation = abs((g["deg_absolute"] - sun_long + 180) % 360 - 180)
        orb = orbs[1] if g.get("retrograde") else orbs[0]
        g["combust"] = elongation < orb
        g["_elongation"] = round(elongation, 2)
    # Rahu/Ketu: never combust
    for name in ("Rahu", "Ketu"):
        if name in grahas:
            grahas[name]["combust"] = False


# ══════════════════════════════════════════════════════════
# C) DIGNITY
# ══════════════════════════════════════════════════════════

def assess_dignity(grahas: dict):
    """Update graha dicts with dignity status from CSV data."""
    dignity_data = load_graha_dignity()
    friendship_data = load_graha_friendship()
    rashi_lords = load_rashi_lords()

    for name, g in grahas.items():
        dd = dignity_data.get(name)
        if not dd:
            g["dignity"] = "neutral"
            continue

        rashi = g["rashi"]
        deg = g["deg_in_rashi"]
        deg_abs = g["deg_absolute"]

        # Exaltation
        ex_rashi = dd.get("exaltation_rashi", "")
        ex_deg = float(dd.get("exaltation_deg", 0) or 0)
        if rashi == ex_rashi:
            if abs(deg - ex_deg) <= 1:
                g["dignity"] = "deeply_exalted"
                continue
            elif True:  # in the exaltation sign
                g["dignity"] = "exalted"
                continue

        # Debilitation
        deb_rashi = dd.get("debilitation_rashi", "")
        deb_deg = float(dd.get("debilitation_deg", 0) or 0)
        if rashi == deb_rashi:
            if abs(deg - deb_deg) <= 1:
                g["dignity"] = "deeply_debilitated"
                continue
            else:
                g["dignity"] = "debilitated"
                continue

        # Mooltrikona
        mt_rashi = dd.get("mooltrikona_rashi", "")
        mt_start = float(dd.get("mooltrikona_deg_start", 0) or 0)
        mt_end = float(dd.get("mooltrikona_deg_end", 30) or 30)
        if rashi == mt_rashi and mt_start <= deg <= mt_end:
            g["dignity"] = "mooltrikona"
            continue

        # Own sign
        own1 = dd.get("own_rashi_1", "")
        own2 = dd.get("own_rashi_2", "")
        if rashi == own1 or (own2 and rashi == own2):
            g["dignity"] = "own"
            continue

        # Friend/neutral/enemy of sign lord
        sign_lord = rashi_lords.get(rashi, "")
        if sign_lord and sign_lord != name:
            fr = friendship_data.get(name, {})
            if sign_lord in fr.get("friends", []):
                g["dignity"] = "friend"
            elif sign_lord in fr.get("enemies", []):
                g["dignity"] = "enemy"
            else:
                g["dignity"] = "neutral"
        else:
            g["dignity"] = "neutral"


# ══════════════════════════════════════════════════════════
# D) ASPECTS
# ══════════════════════════════════════════════════════════

def compute_aspects(grahas: dict) -> List[dict]:
    """Compute whole-sign aspects between grahas."""
    aspect_data = load_graha_aspects()
    aspects = []
    seen = set()

    for name, g in grahas.items():
        offsets = aspect_data.get(name, [7])
        g_rashi_idx = rashi_index(g["rashi"])
        if g_rashi_idx < 0:
            continue

        for offset in offsets:
            target_rashi_idx = (g_rashi_idx + offset) % 12

            for target_name, tg in grahas.items():
                if target_name == name:
                    continue
                t_rashi_idx = rashi_index(tg["rashi"])
                if t_rashi_idx == target_rashi_idx:
                    key = tuple(sorted([name, target_name])) + (str(offset),)
                    if key in seen:
                        continue

                    # Check if mutual
                    t_offsets = aspect_data.get(target_name, [7])
                    t_rashi = rashi_index(tg["rashi"])
                    reverse_hit = any(
                        (t_rashi + to) % 12 == g_rashi_idx for to in t_offsets
                    )

                    aspects.append({
                        "from": name,
                        "to": target_name,
                        "type": f"{offset}th",
                        "mutual": reverse_hit,
                    })
                    if reverse_hit:
                        seen.add(key)

    return aspects


# ══════════════════════════════════════════════════════════
# E) TARA BALA
# ══════════════════════════════════════════════════════════

def compute_tara_bala(transit_nak_index: int, birth_nak_index: int) -> dict:
    """Tara Bala assessment."""
    tara = (transit_nak_index - birth_nak_index) % 27
    category_idx = tara % 9
    cycle = (tara // 9) + 1
    category = _TARA_NAMES[category_idx]

    if category in _TARA_FAVORABLE:
        favorable = True
    elif category in _TARA_UNFAVORABLE:
        favorable = False
    else:
        # Janma — mixed, depends on cycle
        favorable = cycle != 2  # 1st and 3rd janma are less adverse

    return {
        "tara_index": tara,
        "category": category,
        "favorable": favorable,
        "cycle": cycle,
    }


# ══════════════════════════════════════════════════════════
# F) TITHI
# ══════════════════════════════════════════════════════════

def compute_tithi(sun_long: float, moon_long: float) -> dict:
    """Compute tithi from Sun and Moon sidereal longitudes."""
    phase = (moon_long - sun_long) % 360
    tidx = min(int(phase / 12), 29)
    paksha = "Shukla" if tidx < 15 else "Krishna"
    tithi_name = TITHIS[tidx] if tidx < len(TITHIS) else f"Tithi {tidx + 1}"
    deity = TITHI_DEITIES[tidx] if tidx < len(TITHI_DEITIES) else ""

    return {
        "index": tidx,
        "name": tithi_name,
        "paksha": paksha,
        "deity": deity,
        "sun_moon_phase_deg": round(phase, 4),
        "nitya": None,
        "chladni_k": None,
        "sri_yantra_alignment": None,
        "avarana": None,
    }


# ══════════════════════════════════════════════════════════
# G) LOAD NATAL JSON
# ══════════════════════════════════════════════════════════

def load_natal_json(path: str = None) -> dict:
    """Load natal.json, parse DMS to decimal, derive UTC datetime."""
    if path is None:
        path = os.path.join(_ROOT, "instance", "personal", "natal.json")
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    birth = raw.get("birth", {})

    # Parse date + time + timezone -> UTC
    date_str = birth.get("date", "1983-01-27")
    time_str = birth.get("time", "12:00")
    tz_name = birth.get("tz", "UTC")

    parts = date_str.split("-")
    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
    tparts = time_str.split(":")
    hour, minute = int(tparts[0]), int(tparts[1])
    second = int(tparts[2]) if len(tparts) > 2 else 0

    try:
        from zoneinfo import ZoneInfo
        dt_local = datetime(year, month, day, hour, minute, second, tzinfo=ZoneInfo(tz_name))
        dt_utc = dt_local.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)
    except Exception:
        # Fallback: assume EST for Montreal in January
        dt_utc = datetime(year, month, day, hour + 5, minute, second)

    lat = birth.get("lat", 0.0)
    lon = birth.get("lon", 0.0)

    # Parse planet longitudes
    planets = {}
    lagna_data = raw.get("lagna", {})
    if lagna_data.get("degree"):
        lagna_rashi = lagna_data.get("sign", "")
        lagna_deg_in_sign = parse_dms(lagna_data["degree"])
        lagna_rashi_norm = normalize_rashi(lagna_rashi)
        lagna_abs = (lagna_rashi_norm["index"] * 30 + lagna_deg_in_sign) if lagna_rashi_norm else lagna_deg_in_sign
        planets["lagna"] = {
            "sign": lagna_rashi,
            "deg_in_sign": round(lagna_deg_in_sign, 4),
            "deg_absolute": round(lagna_abs, 4),
            "nakshatra": lagna_data.get("nakshatra", ""),
            "pada": lagna_data.get("pada"),
            "navamsha": lagna_data.get("navamsha", ""),
        }

    for key, pdata in raw.get("planets", {}).items():
        if pdata.get("degree"):
            deg_in_sign = parse_dms(pdata["degree"])
            sign = pdata.get("sign", "")
            sign_norm = normalize_rashi(sign)
            abs_deg = (sign_norm["index"] * 30 + deg_in_sign) if sign_norm else deg_in_sign
            planets[key] = {
                "sign": sign,
                "deg_in_sign": round(deg_in_sign, 4),
                "deg_absolute": round(abs_deg, 4),
                "nakshatra": pdata.get("nakshatra", ""),
                "pada": pdata.get("pada"),
                "navamsha": pdata.get("navamsha", ""),
                "retrograde": pdata.get("retrograde", False),
            }

    return {
        "dt_utc": dt_utc,
        "lat": lat,
        "lon": lon,
        "tz": tz_name,
        "planets_parsed": planets,
        "raw": raw,
    }


# ══════════════════════════════════════════════════════════
# WAVE FIELD: TWO-SOURCE INTERFERENCE
# ══════════════════════════════════════════════════════════

_K_LABELS = {1: "conjunction", 2: "opposition", 3: "trine", 4: "square",
             6: "sextile", 7: "septile", 12: "rashi"}
_DEFAULT_K = [1, 2, 3, 4, 6, 7, 12]


def compute_pair_interference(
    source_1_long: float,
    source_2_long: float,
    target_long: float,
    k: int,
) -> complex:
    """
    Two-source wave interference at a target point (versor / phasor form).

    Sources and target are sidereal longitudes in degrees; k is the harmonic order.

    Returns a complex Z_k = exp(j·k·(θ-α)) + exp(j·k·(θ-β)) with:
        Re(Z_k) = cos(k·(θ-α)) + cos(k·(θ-β))   — broadside-radial / magnetic-mode component
        Im(Z_k) = sin(k·(θ-α)) + sin(k·(θ-β))   — axial-longitudinal / dielectric-mode component
        |Z_k|   = mathematically correct interference magnitude (range [0, 2])

    The previous implementation returned only Re(Z_k) (real-cosine-sum). That value
    is recoverable as `compute_pair_interference(...).real` for any caller that
    needs strict backward compatibility. Callers that take `abs(...)` of the result
    now get the proper magnitude |Z_k| instead of |cos(...)+cos(...)|; these scalars
    coincide only when phase geometry happens to align them.
    """
    d1 = math.radians(target_long - source_1_long)
    d2 = math.radians(target_long - source_2_long)
    z1 = complex(math.cos(k * d1), math.sin(k * d1))
    z2 = complex(math.cos(k * d2), math.sin(k * d2))
    return z1 + z2


def compute_wave_field(
    grahas: dict,
    targets: Dict[str, float] = None,
    k_values: List[int] = None,
) -> dict:
    """
    Two-source interference for all graha pairs at all target positions
    (versor / phasor form with magnetic/dielectric mode decomposition).

    grahas: {name: {"deg_absolute": float, ...}} from compute_chart
    targets: {name: longitude} — defaults to all graha positions
    k_values: harmonic orders — defaults to [1, 3, 4, 6, 7, 12]

    Each graha pair contributes a complex phasor Z_k = e^(jk(θ-α)) + e^(jk(θ-β))
    at every target θ and harmonic k. The vector sum across pairs at a given
    (target, k) splits into:

        Re(Σ Z_k)  →  broadside-radial / magnetic-mode component
        Im(Σ Z_k)  →  axial-longitudinal / dielectric-mode component
                       (Steinmetz/Dollard formalism)
        |Σ Z_k|    →  total interference magnitude

    Backward-compatibility note: the per-pair `amplitude` field stored under
    `peak_activation` / `peak_cancellation` / `nodal_lines` continues to hold
    Re(Z_k) (≡ the previous cosine-sum value), and the per-target `composite`
    / `composite_mean` continue to use sum-of-`abs(Re(Z_k))` per k (≡ the
    previous `sum |cos+cos|` aggregate) so existing UI consumers see identical
    data.

    Why composite is NOT switched to |Z_k|: a closed-form identity
    |Z_k| = 2|cos(k(β-α)/2)| shows |Z_k| depends only on the source-pair
    angular separation, not on the target θ. Sum-over-pairs of |Z_k| is
    therefore identical at every target at fixed k, and the per-target
    min-max normalization across targets becomes degenerate (it amplifies
    floating-point noise). The target-dependent interference structure lives
    entirely in Re/Im of Σ_pairs Z_k (the vector sum across pairs *before*
    abs), exposed via the new mode-decomposed fields below.

    New top-level fields exposed by this function:
        targets_magnetic[t][k]    = |Re(Σ_pairs Z_k)|
        targets_dielectric[t][k]  = |Im(Σ_pairs Z_k)|
        targets_mode_ratio[t][k]  = dielectric / (magnetic + dielectric + ε)
        composite_magnetic        = mean over (t,k) of magnetic[t][k]
        composite_dielectric      = mean over (t,k) of dielectric[t][k]
        composite_mode_ratio      = total_dielectric / (total_magnetic + total_dielectric + ε)
    """
    if k_values is None:
        k_values = _DEFAULT_K

    # Extract longitudes
    g_longs = {name: g["deg_absolute"] for name, g in grahas.items()}
    if targets is None:
        targets = dict(g_longs)

    # All pairs
    graha_names = list(g_longs.keys())
    pairs = list(combinations(graha_names, 2))

    # Compute complex Z_k per (target, k, pair); also accumulate the vector
    # sum across pairs for mode decomposition.
    raw = {t: {k: [] for k in k_values} for t in targets}
    pair_sum = {t: {k: 0+0j for k in k_values} for t in targets}

    for a, b in pairs:
        pair_name = f"{a}-{b}"
        lon_a = g_longs[a]
        lon_b = g_longs[b]
        for t_name, t_lon in targets.items():
            for k in k_values:
                z = compute_pair_interference(lon_a, lon_b, t_lon, k)
                raw[t_name][k].append((pair_name, z))
                pair_sum[t_name][k] += z

    # ── mode decomposition (vector-sum split) ───────────────────────
    eps = 1e-12
    targets_magnetic = {}
    targets_dielectric = {}
    targets_mode_ratio = {}
    total_magnetic_sum = 0.0
    total_dielectric_sum = 0.0
    nk_total = 0
    for t_name in targets:
        targets_magnetic[t_name] = {}
        targets_dielectric[t_name] = {}
        targets_mode_ratio[t_name] = {}
        for k in k_values:
            zs = pair_sum[t_name][k]
            mag = abs(zs.real)
            die = abs(zs.imag)
            targets_magnetic[t_name][k] = round(mag, 4)
            targets_dielectric[t_name][k] = round(die, 4)
            targets_mode_ratio[t_name][k] = round(die / (mag + die + eps), 4)
            total_magnetic_sum += mag
            total_dielectric_sum += die
            nk_total += 1

    composite_magnetic = round(total_magnetic_sum / nk_total, 4) if nk_total else 0.0
    composite_dielectric = round(total_dielectric_sum / nk_total, 4) if nk_total else 0.0
    composite_mode_ratio = round(
        total_dielectric_sum / (total_magnetic_sum + total_dielectric_sum + eps), 4
    )

    # ── per-target composite (now from |Z_k| not |cos+cos|) ─────────
    target_results = {}
    composites_by_k = {k: {} for k in k_values}  # k -> {target: sum |Z_k|}

    for t_name in targets:
        composite = {}
        all_activations = []
        for k in k_values:
            entries = raw[t_name][k]
            # Per-target backward-compat aggregate: sum_pairs |Re(Z_k)|
            # ≡ sum_pairs |cos(k(θ-α)) + cos(k(θ-β))|. See class docstring
            # for why we don't switch this to |Z_k| (would collapse targets).
            total = sum(abs(z.real) for _, z in entries)
            composite[k] = round(total, 4)
            composites_by_k[k][t_name] = total
            for pair_name, z in entries:
                # Backward-compat: store Re(Z_k) under "amplitude" — this is
                # exactly the previous cosine-sum value. Add "magnitude" for
                # callers that want the corrected scalar.
                all_activations.append({
                    "pair": pair_name,
                    "k": k,
                    "label": _K_LABELS.get(k, f"k={k}"),
                    "amplitude": round(z.real, 4),
                    "magnitude": round(abs(z), 4),
                })

        target_results[t_name] = {
            "composite": composite,
            "composite_normalized": {},  # filled below
            "composite_mean": 0.0,
            "peak_activation": sorted(all_activations, key=lambda x: x["amplitude"], reverse=True)[:3],
            "peak_cancellation": sorted(all_activations, key=lambda x: x["amplitude"])[:3],
            "nodal_lines": sorted(all_activations, key=lambda x: abs(x["amplitude"]))[:3],
        }

    # Normalize per k
    for k in k_values:
        vals = composites_by_k[k]
        if not vals:
            continue
        mn, mx = min(vals.values()), max(vals.values())
        rng = mx - mn if mx > mn else 1.0
        for t_name in targets:
            target_results[t_name]["composite_normalized"][k] = round(
                (vals[t_name] - mn) / rng, 4)

    # Compute mean across normalized k
    for t_name in targets:
        norms = target_results[t_name]["composite_normalized"]
        if norms:
            target_results[t_name]["composite_mean"] = round(
                sum(norms.values()) / len(norms), 4)

    # Field summary
    by_mean = sorted(target_results.items(), key=lambda x: x[1]["composite_mean"], reverse=True)
    strongest_res = max(
        ((t, e) for t in targets for e in target_results[t]["peak_activation"]),
        key=lambda x: x[1]["amplitude"],
        default=(None, {}),
    )
    strongest_cancel = min(
        ((t, e) for t in targets for e in target_results[t]["peak_cancellation"]),
        key=lambda x: x[1]["amplitude"],
        default=(None, {}),
    )

    return {
        "k_labels": _K_LABELS,
        "pair_count": len(pairs),
        "targets": target_results,
        "targets_magnetic": targets_magnetic,
        "targets_dielectric": targets_dielectric,
        "targets_mode_ratio": targets_mode_ratio,
        "composite_magnetic": composite_magnetic,
        "composite_dielectric": composite_dielectric,
        "composite_mode_ratio": composite_mode_ratio,
        "field_summary": {
            "most_activated": by_mean[0][0] if by_mean else None,
            "least_activated": by_mean[-1][0] if by_mean else None,
            "strongest_single_resonance": {
                "target": strongest_res[0],
                **(strongest_res[1] if strongest_res[1] else {}),
            },
            "strongest_single_cancellation": {
                "target": strongest_cancel[0],
                **(strongest_cancel[1] if strongest_cancel[1] else {}),
            },
        },
    }


def compute_nakshatra_field(
    grahas: dict,
    k_values: List[int] = None,
) -> dict:
    """
    Two-source interference integrated over each of the 27 nakshatra arcs.
    Sample at 1° resolution within each 13°20' arc.
    """
    if k_values is None:
        k_values = _DEFAULT_K

    g_longs = {name: g["deg_absolute"] for name, g in grahas.items()}
    pairs = list(combinations(list(g_longs.keys()), 2))
    nak_size = 360.0 / 27.0  # 13.333...

    nak_results = {}
    field_vector = []

    for nak_idx in range(27):
        nak_name = NAKSHATRAS[nak_idx]
        arc_start = nak_idx * nak_size
        # Sample at 1° within the arc (14 sample points for 13.33° arc)
        samples = [arc_start + d for d in range(int(nak_size) + 1)]

        total = 0.0
        count = 0
        for s in samples:
            for a, b in pairs:
                for k in k_values:
                    amp = compute_pair_interference(g_longs[a], g_longs[b], s, k)
                    total += abs(amp)
                    count += 1

        mean_amp = total / count if count else 0.0

        # Which grahas occupy this nakshatra?
        occupants = [name for name, g in grahas.items()
                     if int((g["deg_absolute"] % 360) / nak_size) % 27 == nak_idx]

        nak_results[nak_name] = {
            "composite": round(mean_amp, 4),
            "composite_normalized": 0.0,  # filled below
            "occupants": occupants,
            "lord": nak_lord_from_longitude(arc_start + nak_size / 2),
        }
        field_vector.append(mean_amp)

    # Normalize
    mn, mx = min(field_vector), max(field_vector)
    rng = mx - mn if mx > mn else 1.0
    norm_vector = [(v - mn) / rng for v in field_vector]
    for i, nak_name in enumerate(NAKSHATRAS):
        nak_results[nak_name]["composite_normalized"] = round(norm_vector[i], 4)

    # Sort for active/quiet
    by_composite = sorted(nak_results.items(), key=lambda x: x[1]["composite"], reverse=True)

    return {
        "nakshatras": nak_results,
        "field_vector": [round(v, 4) for v in norm_vector],
        "active_nakshatras": [n for n, _ in by_composite[:5]],
        "quiet_nakshatras": [n for n, _ in by_composite[-5:]],
    }


def compute_pair_nakshatra_pattern(
    graha1_long: float,
    graha2_long: float,
    k_values: List[int] = None,
) -> dict:
    """
    Single pair interference pattern across all 27 nakshatra arcs.
    Used by the /wave_field/pair route for mandala visualization.
    """
    if k_values is None:
        k_values = _DEFAULT_K

    nak_size = 360.0 / 27.0
    result = {}

    for nak_idx in range(27):
        nak_name = NAKSHATRAS[nak_idx]
        arc_start = nak_idx * nak_size
        samples = [arc_start + d for d in range(int(nak_size) + 1)]

        by_k = {}
        for k in k_values:
            # Use .real to preserve signed-cosine-sum semantics for the
            # per-arc pattern visualization (constructive vs destructive
            # average across the arc). The complex magnitude is always
            # nonneg and would lose the sign distinction the UI relies on.
            total = sum(compute_pair_interference(graha1_long, graha2_long, s, k).real
                        for s in samples)
            by_k[k] = round(total / len(samples), 4)

        result[nak_name] = by_k

    return result
