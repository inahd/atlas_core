"""
helix_engine.py — Dual helix toroidal field computation.

Computes moon helix (13 loops/year) and nodal axis (Rahu/Ketu)
on torus surface with favorability scoring.

Pattern follows ui_vastu_engine.py:
    canonical data → internal helpers → validation → public API
"""

import math
from datetime import datetime, timedelta

# ══════════════════════════════════════════════════════════
# CANONICAL MAPPINGS
# ══════════════════════════════════════════════════════════

R = 2.8   # torus major radius
r = 0.9   # torus minor radius

RASHI_SYMBOLS = {
    'Mesha': '♈', 'Vrishabha': '♉', 'Mithuna': '♊',
    'Karka': '♋', 'Simha': '♌', 'Kanya': '♍',
    'Tula': '♎', 'Vrischika': '♏', 'Dhanu': '♐',
    'Makara': '♑', 'Kumbha': '♒', 'Meena': '♓',
}

NAKSHATRA_NAMES = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
    'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni',
    'Uttara Phalguni', 'Hasta', 'Chitra', 'Swati', 'Vishakha',
    'Anuradha', 'Jyeshtha', 'Mula', 'Purva Ashadha', 'Uttara Ashadha',
    'Shravana', 'Dhanishtha', 'Shatabhisha', 'Purva Bhadrapada',
    'Uttara Bhadrapada', 'Revati',
]

NAKSHATRA_QUALITY = {
    'Ashwini': 1.0, 'Bharani': 0.3, 'Krittika': 0.6,
    'Rohini': 1.0, 'Mrigashira': 0.8, 'Ardra': 0.2,
    'Punarvasu': 1.0, 'Pushya': 1.0, 'Ashlesha': 0.1,
    'Magha': 0.6, 'Purva Phalguni': 0.7, 'Uttara Phalguni': 0.9,
    'Hasta': 1.0, 'Chitra': 0.8, 'Swati': 0.9,
    'Vishakha': 0.7, 'Anuradha': 0.9, 'Jyeshtha': 0.2,
    'Mula': 0.1, 'Purva Ashadha': 0.7, 'Uttara Ashadha': 0.9,
    'Shravana': 1.0, 'Dhanishtha': 0.7, 'Shatabhisha': 0.5,
    'Purva Bhadrapada': 0.4, 'Uttara Bhadrapada': 0.8, 'Revati': 1.0,
}

TITHI_QUALITY = {
    0: 0.1, 1: 0.7, 2: 0.8, 3: 1.0, 4: 0.5, 5: 1.0,
    6: 0.6, 7: 0.9, 8: 0.3, 9: 0.4, 10: 0.9, 11: 1.0,
    12: 0.9, 13: 0.8, 14: 0.5, 15: 1.0, 16: 0.7, 17: 0.8,
    18: 0.6, 19: 0.5, 20: 0.9, 21: 0.4, 22: 0.3, 23: 1.0,
    24: 0.9, 25: 0.8, 26: 0.3, 27: 0.8, 28: 0.5, 29: 0.1,
}

VARA_QUALITY = {0: 0.8, 1: 0.9, 2: 0.5, 3: 1.0, 4: 0.9, 5: 0.7, 6: 0.4}

# Rahu kala hours by weekday (approximate start hour, 1.5hr duration)
RAHU_KALA = {0: 7.5, 1: 15.0, 2: 12.0, 3: 13.5, 4: 10.5, 5: 9.0, 6: 12.0}

GRAHA_COLORS = {
    'Surya': '#e8c86a', 'Chandra': '#c8d8e8', 'Mangala': '#c84040',
    'Budha': '#40c080', 'Guru': '#c8a050', 'Shukra': '#e8a0c0',
    'Shani': '#8090a8', 'Rahu': '#9060c0', 'Ketu': '#806040',
}


# ══════════════════════════════════════════════════════════
# LOW-PRECISION EPHEMERIS (mean motion, no perturbations)
# ══════════════════════════════════════════════════════════

def _jdn(year, month, day):
    """Julian Day Number from date."""
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    return day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045


def _moon_lon(jd):
    """Mean lunar longitude (degrees, 0-360). Low-precision."""
    T = (jd - 2451545.0) / 36525.0  # centuries from J2000
    L = (218.3165 + 481267.8813 * T) % 360
    return L if L >= 0 else L + 360


def _rahu_lon(jd):
    """Mean Rahu longitude (degrees). Retrograde ~19.4°/year."""
    T = (jd - 2451545.0) / 36525.0
    omega = (125.0445 - 1934.1363 * T) % 360
    return omega if omega >= 0 else omega + 360


def _sun_lon(jd):
    """Mean solar longitude (degrees)."""
    T = (jd - 2451545.0) / 36525.0
    L = (280.46646 + 36000.76983 * T) % 360
    return L if L >= 0 else L + 360


def _tithi_num(moon_lon, sun_lon):
    """Tithi number 0-29 from moon-sun elongation."""
    diff = (moon_lon - sun_lon) % 360
    return int(diff / 12.0) % 30


def _nakshatra_idx(moon_lon):
    """Nakshatra index 0-26 from lunar longitude."""
    return int(moon_lon / (360.0 / 27)) % 27


def _torus_point(phi, theta):
    """3D point on torus surface."""
    return {
        'x': round((R + r * math.cos(theta)) * math.cos(phi), 4),
        'y': round(r * math.sin(theta), 4),
        'z': round((R + r * math.cos(theta)) * math.sin(phi), 4),
    }


# ══════════════════════════════════════════════════════════
# INTERNAL HELPERS
# ══════════════════════════════════════════════════════════

def _compute_helix_points(field_state, days):
    """Compute helix geometry for next N days."""
    now = datetime.now()
    year_start = datetime(now.year, 1, 1)
    points = []

    for d in range(days):
        dt = now + timedelta(days=d)
        jd = _jdn(dt.year, dt.month, dt.day) + 0.5  # noon

        doy = (dt - datetime(dt.year, 1, 1)).days
        day_frac = doy / 365.25

        ml = _moon_lon(jd)
        sl = _sun_lon(jd)
        rl = _rahu_lon(jd)

        tidx = _tithi_num(ml, sl)
        nak_idx = _nakshatra_idx(ml)
        nak_name = NAKSHATRA_NAMES[nak_idx]

        phi = day_frac * math.pi * 2          # toroidal (solar year)
        theta = (tidx / 30.0) * math.pi * 2   # poloidal (lunar month)

        # Rahu/Ketu positions on torus equator
        rahu_phi = (rl / 360.0) * math.pi * 2
        ketu_phi = (rahu_phi + math.pi) % (math.pi * 2)

        # Eclipse zone: moon within 18° of node
        moon_rahu_dist = abs(((ml - rl + 180) % 360) - 180)
        is_eclipse = moon_rahu_dist < 18

        # Torus surface point
        tp = _torus_point(phi, phi * 13)  # spiral: theta = phi * 13

        paksha = 'Shukla' if tidx < 15 else 'Krishna'
        weekday = dt.weekday()  # 0=Mon
        rk_start = RAHU_KALA.get(weekday, 12)

        # Favorability
        nak_q = NAKSHATRA_QUALITY.get(nak_name, 0.5)
        tit_q = TITHI_QUALITY.get(tidx, 0.5)
        rahu_q = min(1.0, moon_rahu_dist / 45.0)  # further = better
        vara_q = VARA_QUALITY.get(weekday, 0.5)
        fav = round(nak_q * 0.35 + tit_q * 0.30 + rahu_q * 0.20 + vara_q * 0.15, 3)

        points.append({
            'day_offset': d,
            'date_str': dt.strftime('%Y-%m-%d'),
            'phi': round(phi, 4),
            'theta': round(theta, 4),
            'x': tp['x'], 'y': tp['y'], 'z': tp['z'],
            'nakshatra': nak_name,
            'nak_idx': nak_idx,
            'tithi_num': tidx,
            'paksha': paksha,
            'rahu_phi': round(rahu_phi, 4),
            'ketu_phi': round(ketu_phi, 4),
            'is_ekadashi': tidx in (11, 26),
            'is_purnima': tidx == 15,
            'is_amavasya': tidx in (0, 29),
            'is_eclipse_zone': is_eclipse,
            'favorability': fav,
            'rahu_kala_hours': 1.5,
        })

    return points


def _compute_markers(points):
    """Extract special points for rendering."""
    ekadashi = [p for p in points if p['is_ekadashi']]
    purnima = [p for p in points if p['is_purnima']]
    amavasya = [p for p in points if p['is_amavasya']]
    eclipse = [p for p in points if p['is_eclipse_zone']]
    today = points[0] if points else {}

    # Nakshatra transitions
    transitions = []
    for i in range(1, len(points)):
        if points[i]['nak_idx'] != points[i - 1]['nak_idx']:
            transitions.append(points[i])

    return {
        'ekadashi': ekadashi,
        'purnima': purnima,
        'amavasya': amavasya,
        'eclipse_zones': eclipse,
        'nak_transitions': transitions[:30],
        'today': today,
    }


def _score_favorability(points):
    """7-day rolling average and trend analysis."""
    if not points:
        return {'current': 0.5, 'week_avg': 0.5, 'trend': 'stable',
                'best_day': 0, 'worst_day': 0}
    current = points[0]['favorability']
    week = [p['favorability'] for p in points[:7]]
    week_avg = round(sum(week) / len(week), 3) if week else 0.5
    n = min(14, len(points))
    best_day = max(range(n), key=lambda i: points[i]['favorability'])
    worst_day = min(range(n), key=lambda i: points[i]['favorability'])
    trend = 'stable'
    if len(points) >= 7:
        early = sum(p['favorability'] for p in points[:3]) / 3
        late = sum(p['favorability'] for p in points[3:7]) / 4
        if late > early + 0.05:
            trend = 'improving'
        elif late < early - 0.05:
            trend = 'declining'
    return {'current': current, 'week_avg': week_avg, 'trend': trend,
            'best_day': best_day, 'worst_day': worst_day}


def _compute_dasha_band(field_state):
    """Current dasha arc on torus."""
    try:
        dasha = field_state.get('panchanga', {}).get('dasha', {})
        if not dasha:
            dasha = field_state.get('dasha', {})
        lord = dasha.get('lord', dasha.get('mahadasha', 'Budha'))
        closes = dasha.get('closes', '2027-10')

        # Parse end date
        parts = closes.split('-')
        end_year = int(parts[0])
        end_month = int(parts[1]) if len(parts) > 1 else 1

        now = datetime.now()
        end_dt = datetime(end_year, end_month, 15)

        phi_start = ((now - datetime(now.year, 1, 1)).days / 365.25) * math.pi * 2
        days_to_end = (end_dt - now).days
        phi_end = phi_start + (days_to_end / 365.25) * math.pi * 2

        color = GRAHA_COLORS.get(lord, '#40c080')

        return {
            'lord': lord,
            'end_date': end_dt.strftime('%Y-%m-%d'),
            'phi_start': round(phi_start, 4),
            'phi_end': round(phi_end, 4),
            'color': color,
            'remaining_years': round(days_to_end / 365.25, 2),
        }
    except Exception:
        return {
            'lord': 'Budha', 'end_date': '2027-10-15',
            'phi_start': 0, 'phi_end': 3.14,
            'color': '#40c080', 'remaining_years': 1.5,
        }


# ══════════════════════════════════════════════════════════
# VALIDATION
# ══════════════════════════════════════════════════════════

def _validate(result):
    defaults = {
        'points': [],
        'markers': {
            'ekadashi': [], 'purnima': [], 'amavasya': [],
            'eclipse_zones': [], 'nak_transitions': [], 'today': {},
        },
        'favorability': {'current': 0.5, 'week_avg': 0.5, 'trend': 'stable',
                         'best_day': 0, 'worst_day': 0},
        'dasha_band': {
            'lord': '', 'end_date': '', 'phi_start': 0,
            'phi_end': 0, 'color': '#40c080', 'remaining_years': 0,
        },
        'days': 90,
        'torus': {'R': R, 'r': r},
        'rashis': RASHI_SYMBOLS,
        'attestation': 'SYNTHESIS',
    }
    for k, v in defaults.items():
        if k not in result or result[k] is None:
            result[k] = v
    return result


def _defaults(days):
    return _validate({'days': days})


# ══════════════════════════════════════════════════════════
# PUBLIC API
# ══════════════════════════════════════════════════════════

def derive_helix_field(field_state: dict, days: int = 90) -> dict:
    """Compute dual helix geometry + favorability for next N days.

    Returns parametric curves, favorability scores, special markers.
    Never raises — returns safe defaults on any error.
    """
    try:
        days = max(1, min(365, days))
        points = _compute_helix_points(field_state, days)
        markers = _compute_markers(points)
        favorability = _score_favorability(points)
        dasha_band = _compute_dasha_band(field_state)

        return _validate({
            'points': points,
            'markers': markers,
            'favorability': favorability,
            'dasha_band': dasha_band,
            'days': days,
        })
    except Exception:
        return _defaults(days)
