"""
jyotish_bp.py — Flask blueprint for jyotisha chart routes.

Blueprint: jyotish_bp, prefix: /jyotish
"""

import os
from datetime import datetime, timezone
from flask import Blueprint, jsonify, request, send_from_directory

jyotish_bp = Blueprint("jyotish_bp", __name__, url_prefix="/jyotish")

# Gainesville FL defaults
_DEFAULT_LAT = 29.65
_DEFAULT_LON = -82.32
_STATIC = os.path.join(os.path.dirname(__file__), "..", "..", "static")


@jyotish_bp.route("/chart")
def chart_page():
    return send_from_directory(_STATIC, "jyotish_chart.html")


@jyotish_bp.route("/compute", methods=["POST"])
def compute():
    """Compute a chart from provided datetime + location."""
    from npu_engine.jyotisha_engine import compute_chart, load_natal_json

    body = request.get_json(silent=True) or {}
    dt_str = body.get("datetime_utc")
    lat = body.get("lat")
    lon = body.get("lon")
    ayanamsha = body.get("ayanamsha", "lahiri")
    house_system = body.get("house_system", "whole_sign")
    varga = body.get("varga", "D1")
    custom_aya = body.get("custom_ayanamsha_deg")
    if custom_aya is not None:
        custom_aya = float(custom_aya)

    kwargs = dict(ayanamsha=ayanamsha, house_system=house_system,
                  varga=varga, custom_ayanamsha_deg=custom_aya)

    if dt_str and lat is not None and lon is not None:
        dt_utc = datetime.fromisoformat(dt_str)
        chart = compute_chart(dt_utc, float(lat), float(lon), **kwargs)
    else:
        natal = load_natal_json()
        chart = compute_chart(natal["dt_utc"], natal["lat"], natal["lon"], **kwargs)

    return jsonify(chart)


@jyotish_bp.route("/natal")
def natal():
    """Natal chart from natal.json using defaults (Lahiri, whole sign, D1)."""
    from npu_engine.jyotisha_engine import compute_chart, load_natal_json

    natal_data = load_natal_json()
    chart = compute_chart(natal_data["dt_utc"], natal_data["lat"], natal_data["lon"])
    return jsonify(chart)


@jyotish_bp.route("/transits")
def transits():
    """Current sky chart — real Swiss Ephemeris, Gainesville coords."""
    from npu_engine.jyotisha_engine import compute_chart

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    chart = compute_chart(now, _DEFAULT_LAT, _DEFAULT_LON)
    return jsonify(chart)


@jyotish_bp.route("/tara/<nakshatra>")
def tara(nakshatra):
    """Tara Bala for a transit nakshatra relative to natal Moon."""
    from npu_engine.jyotisha_engine import compute_tara_bala, load_natal_json, compute_chart
    from npu_engine.jyotish_utils import NAKSHATRAS, nak_index_from_longitude

    # Get natal Moon nakshatra
    natal_data = load_natal_json()
    natal_chart = compute_chart(natal_data["dt_utc"], natal_data["lat"], natal_data["lon"])
    birth_nak = natal_chart["grahas"]["Moon"]["nakshatra"]
    birth_idx = NAKSHATRAS.index(birth_nak) if birth_nak in NAKSHATRAS else 0

    # Find transit nakshatra index
    nak_lower = nakshatra.lower().strip()
    transit_idx = None
    for i, n in enumerate(NAKSHATRAS):
        if n.lower() == nak_lower:
            transit_idx = i
            break
    if transit_idx is None:
        return jsonify({"error": f"unknown nakshatra: {nakshatra}"}), 400

    result = compute_tara_bala(transit_idx, birth_idx)
    result["transit_nakshatra"] = NAKSHATRAS[transit_idx]
    result["birth_nakshatra"] = birth_nak
    return jsonify(result)


@jyotish_bp.route("/compatibility")
def compatibility():
    """Tara Bala + tithi for current moment relative to natal."""
    from npu_engine.jyotisha_engine import (
        compute_chart, compute_tara_bala, load_natal_json,
    )
    from npu_engine.jyotish_utils import NAKSHATRAS

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    transit_chart = compute_chart(now, _DEFAULT_LAT, _DEFAULT_LON)
    natal_data = load_natal_json()
    natal_chart = compute_chart(natal_data["dt_utc"], natal_data["lat"], natal_data["lon"])

    # Tara from transit Moon nak vs natal Moon nak
    transit_moon_nak = transit_chart["grahas"]["Moon"]["nakshatra"]
    birth_moon_nak = natal_chart["grahas"]["Moon"]["nakshatra"]
    t_idx = NAKSHATRAS.index(transit_moon_nak) if transit_moon_nak in NAKSHATRAS else 0
    b_idx = NAKSHATRAS.index(birth_moon_nak) if birth_moon_nak in NAKSHATRAS else 0
    tara = compute_tara_bala(t_idx, b_idx)

    return jsonify({
        "tara_bala": tara,
        "transit_moon_nakshatra": transit_moon_nak,
        "birth_moon_nakshatra": birth_moon_nak,
        "tithi": transit_chart["tithi"],
        "transit_ascendant": transit_chart["ascendant"]["rashi"],
    })


@jyotish_bp.route("/wave_field")
def wave_field():
    """Wave field analysis for natal or transit chart."""
    from npu_engine.jyotisha_engine import compute_chart, load_natal_json, compute_wave_field

    chart_type = request.args.get("chart_type", "natal")
    if chart_type == "transit":
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        chart = compute_chart(now, _DEFAULT_LAT, _DEFAULT_LON)
    else:
        natal = load_natal_json()
        chart = compute_chart(natal["dt_utc"], natal["lat"], natal["lon"])

    return jsonify({
        "phase_pairs": chart.get("phase_pairs", {}),
        "nakshatras": chart.get("chladni_field", {}).get("nakshatras", {}),
        "field_vector": chart.get("chladni_field", {}).get("field_vector", []),
        "active_nakshatras": chart.get("chladni_field", {}).get("active_nakshatras", []),
    })


@jyotish_bp.route("/wave_field/pair/<graha1>/<graha2>")
def wave_field_pair(graha1, graha2):
    """Single pair interference across 27 nakshatra arcs."""
    from npu_engine.jyotisha_engine import compute_chart, load_natal_json, compute_pair_nakshatra_pattern
    from npu_engine.jyotish_utils import normalize_graha

    chart_type = request.args.get("chart_type", "natal")
    k_param = request.args.get("k")

    if chart_type == "transit":
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        chart = compute_chart(now, _DEFAULT_LAT, _DEFAULT_LON)
    else:
        natal = load_natal_json()
        chart = compute_chart(natal["dt_utc"], natal["lat"], natal["lon"])

    # Normalize graha names
    g1 = normalize_graha(graha1)
    g2 = normalize_graha(graha2)
    if not g1 or not g2:
        return jsonify({"error": f"unknown graha: {graha1} or {graha2}"}), 400

    g1_eng = g1["english"]
    g2_eng = g2["english"]
    if g1_eng not in chart["grahas"] or g2_eng not in chart["grahas"]:
        return jsonify({"error": f"graha not in chart: {g1_eng} or {g2_eng}"}), 400

    lon1 = chart["grahas"][g1_eng]["deg_absolute"]
    lon2 = chart["grahas"][g2_eng]["deg_absolute"]

    k_values = [int(k_param)] if k_param else None
    pattern = compute_pair_nakshatra_pattern(lon1, lon2, k_values=k_values)

    return jsonify({
        "pair": f"{g1_eng}-{g2_eng}",
        "longitudes": [lon1, lon2],
        "separation_deg": round(abs((lon1 - lon2 + 180) % 360 - 180), 2),
        "pattern": pattern,
    })


@jyotish_bp.route("/sound_state")
def sound_state():
    """Current wave-derived sound parameters."""
    import math
    from itertools import combinations
    from npu_engine.jyotisha_engine import compute_chart, compute_pair_interference
    from npu_engine.jyotish_utils import NAKSHATRAS

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    chart = compute_chart(now, _DEFAULT_LAT, _DEFAULT_LON)
    grahas = chart['grahas']
    moon = grahas['Moon']
    moon_nak = moon['nakshatra']
    moon_long = moon['deg_absolute']
    nak_size = 360.0 / 27.0
    moon_nak_mid = int(moon_long / nak_size) * nak_size + nak_size / 2

    NAK_RAGA = {
        'Ashwini': 'Bilawal', 'Bharani': 'Kalyani', 'Krittika': 'Todi',
        'Rohini': 'Bhairavi', 'Mrigashira': 'Hindol', 'Ardra': 'Darbari',
        'Punarvasu': 'Yaman', 'Pushya': 'Kafi', 'Ashlesha': 'Bhairav',
        'Magha': 'Marwa', 'Purva Phalguni': 'Puriya', 'Uttara Phalguni': 'Bihag',
        'Hasta': 'Miyan ki Todi', 'Chitra': 'Ahir Bhairav', 'Swati': 'Desh',
        'Vishakha': 'Jaunpuri', 'Anuradha': 'Malkauns', 'Jyeshtha': 'Bageshri',
        'Mula': 'Shree', 'Purva Ashadha': 'Kedar', 'Uttara Ashadha': 'Hamir',
        'Shravana': 'Durga', 'Dhanishta': 'Sarang', 'Shatabhisha': 'Lalit',
        'Purva Bhadrapada': 'Basant', 'Uttara Bhadrapada': 'Jayjaywanti',
        'Revati': 'Hansadhwani',
    }
    K_LABELS = {1: 'conjunction', 2: 'opposition', 3: 'trine', 4: 'square',
                6: 'sextile', 7: 'septile', 12: 'rashi'}
    K_PARTIAL = {1: 'sa', 3: 'ga', 4: 'ma', 6: 'dha', 7: 'ni', 12: 'pa'}
    k_values = [1, 3, 4, 6, 7, 12]

    graha_names = [g for g in grahas if g != 'Moon']
    pairs = list(combinations(graha_names, 2))
    activation = 0.0
    k_scores = {k: 0.0 for k in k_values}
    for a, b in pairs:
        for k in k_values:
            amp = abs(compute_pair_interference(
                grahas[a]['deg_absolute'], grahas[b]['deg_absolute'], moon_nak_mid, k))
            activation += amp
            k_scores[k] += amp

    max_possible = len(pairs) * len(k_values) * 2.0
    gamak = min(activation / max_possible, 1.0) if max_possible > 0 else 0.5
    dominant_k = max(k_scores, key=k_scores.get) if k_scores else 12

    phase = chart['tithi']['sun_moon_phase_deg']
    wave_bpm = 81 + 27 * math.sin(math.radians(phase))

    # Import sound engine helpers for enriched state
    from npu_engine.sound.sound_engine import (
        _compute_interval_mix, _compute_rhythm_mode,
        _compute_natal_filter, _compute_breath,
    )

    interval_mix = _compute_interval_mix(grahas, moon_nak_mid, k_scores)
    rhythm = _compute_rhythm_mode(k_scores)
    natal_filter = _compute_natal_filter(gamak)
    breath = _compute_breath(gamak, phase)
    wave_bpm_wide = 90 + 30 * math.sin(math.radians(phase))

    return jsonify({
        "moon_nakshatra": moon_nak,
        "suggested_raga": NAK_RAGA.get(moon_nak, ''),
        "gamak_intensity": round(gamak, 3),
        "wave_bpm": round(wave_bpm_wide, 1),
        "dominant_k": dominant_k,
        "dominant_k_name": K_LABELS.get(dominant_k, f'k={dominant_k}'),
        "partial_emphasis": K_PARTIAL.get(dominant_k, 'pa'),
        "tithi_phase_deg": round(phase, 1),
        "transit_time_utc": now.isoformat(),
        "interval_mix": {str(k): round(v, 3) for k, v in interval_mix.items()},
        "rhythm_mode": rhythm,
        "natal_filter": natal_filter,
        "breath": breath,
    })


# ── Calendar projection cache ────────────────────────────
_calendar_cache = {}
_calendar_cache_ts = 0


@jyotish_bp.route("/calendar")
def calendar():
    """Compute per-day chart data for a date range. Real ephemeris."""
    import time
    from datetime import timedelta
    from itertools import combinations
    import math
    from npu_engine.jyotisha_engine import (
        compute_chart, load_natal_json, compute_pair_interference,
        compute_tara_bala, compute_tithi,
    )
    from npu_engine.jyotish_utils import (
        NAKSHATRAS, nak_from_longitude, nak_index_from_longitude,
        pada_from_longitude, nak_lord_from_longitude,
        rashi_from_longitude, TITHIS, TITHI_DEITIES,
    )

    global _calendar_cache, _calendar_cache_ts

    start_str = request.args.get("start")
    end_str = request.args.get("end")
    if not start_str or not end_str:
        return jsonify({"error": "provide start=YYYY-MM-DD&end=YYYY-MM-DD"}), 400

    cache_key = f"{start_str}_{end_str}"
    now_ts = time.time()
    if cache_key in _calendar_cache and (now_ts - _calendar_cache_ts) < 3600:
        return jsonify(_calendar_cache[cache_key])

    start = datetime.strptime(start_str, "%Y-%m-%d")
    end = datetime.strptime(end_str, "%Y-%m-%d")
    if (end - start).days > 90:
        return jsonify({"error": "max 90 day range"}), 400

    # Load natal data for tara bala + lagna wave score
    natal = load_natal_json()
    natal_chart = compute_chart(natal["dt_utc"], natal["lat"], natal["lon"])
    natal_lagna_long = natal_chart["ascendant"]["deg_absolute"]
    birth_moon_nak = natal_chart["grahas"]["Moon"]["nakshatra"]
    birth_moon_idx = NAKSHATRAS.index(birth_moon_nak) if birth_moon_nak in NAKSHATRAS else 0

    # Tithi quality map (1-indexed within paksha)
    TQ = {1:'auspicious',2:'mixed',3:'mixed',4:'inauspicious',5:'auspicious',
          6:'auspicious',7:'mixed',8:'mixed',9:'inauspicious',10:'auspicious',
          11:'auspicious',12:'mixed',13:'mixed',14:'inauspicious',15:'auspicious'}

    # Bio map from nakshatra name
    BIO = {}
    _bio_list = ['Fruit','Root','Root','Root','Flower','Flower','Leaf','Leaf','Leaf',
                 'Fruit','Fruit','Fruit','Fruit','Fruit','Flower','Fruit','Leaf','Leaf',
                 'Fruit','Leaf','Root','Flower','Flower','Flower','Flower','Leaf','Flower']
    for i, n in enumerate(NAKSHATRAS):
        BIO[n] = _bio_list[i] if i < len(_bio_list) else 'Leaf'

    VARAS = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

    k_values = [1, 2, 3, 4, 6, 7, 12]
    days_result = {}

    d = start
    while d <= end:
        dt_utc = datetime(d.year, d.month, d.day, 17, 0)  # noon ET ≈ 17:00 UTC
        date_str = d.strftime("%Y-%m-%d")

        try:
            import swisseph as swe
            swe.set_sid_mode(swe.SIDM_LAHIRI)
            hour_dec = dt_utc.hour + dt_utc.minute / 60.0
            jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, hour_dec)
            aya = swe.get_ayanamsa_ut(jd)

            # Sun + Moon positions (fast — only 2 bodies)
            sun_trop = swe.calc_ut(jd, swe.SUN)[0][0]
            moon_trop = swe.calc_ut(jd, swe.MOON)[0][0]
            sun_sid = (sun_trop - aya) % 360
            moon_sid = (moon_trop - aya) % 360

            # All 9 graha longitudes for wave score
            graha_longs = {}
            for gname, gid in [("Sun", swe.SUN), ("Moon", swe.MOON), ("Mars", swe.MARS),
                                ("Mercury", swe.MERCURY), ("Jupiter", swe.JUPITER),
                                ("Venus", swe.VENUS), ("Saturn", swe.SATURN)]:
                graha_longs[gname] = (swe.calc_ut(jd, gid)[0][0] - aya) % 360
            rahu_sid = (swe.calc_ut(jd, swe.MEAN_NODE)[0][0] - aya) % 360
            graha_longs["Rahu"] = rahu_sid
            graha_longs["Ketu"] = (rahu_sid + 180) % 360

            # Nakshatra + pada
            nak_name = nak_from_longitude(moon_sid)
            nak_idx = nak_index_from_longitude(moon_sid)
            pada = pada_from_longitude(moon_sid)
            nak_lord = nak_lord_from_longitude(moon_sid)

            # Tithi
            phase = (moon_sid - sun_sid) % 360
            tidx = min(int(phase / 12), 29)
            tithi_num = (tidx % 15) + 1
            paksha = "Shukla" if tidx < 15 else "Krishna"
            tq = TQ.get(tithi_num, 'mixed')
            tithi_name = TITHIS[tidx] if tidx < len(TITHIS) else ""
            deity = TITHI_DEITIES[tidx] if tidx < len(TITHI_DEITIES) else ""

            # Lightweight wave score: 36 pairs at lagna, mean |amp|
            pairs = list(combinations(list(graha_longs.keys()), 2))
            total_amp = 0.0
            peak_amp = 0.0
            peak_pair = ""
            peak_k = 0
            for a, b in pairs:
                for k in k_values:
                    amp = compute_pair_interference(graha_longs[a], graha_longs[b], natal_lagna_long, k)
                    total_amp += abs(amp)
                    if abs(amp) > peak_amp:
                        peak_amp = abs(amp)
                        peak_pair = f"{a}-{b}"
                        peak_k = k
            wave_score = total_amp / (len(pairs) * len(k_values) * 2)  # normalize to 0-1
            wave_peak_str = f"{peak_pair} k={peak_k}"

            # Tara Bala
            tara = compute_tara_bala(nak_idx, birth_moon_idx)

            # Moon dignity (simple: friend/neutral/enemy of sign lord)
            moon_rashi = rashi_from_longitude(moon_sid)
            sun_rashi = rashi_from_longitude(sun_sid)

            # Approaching events
            days_to_eka = min(((10 - tidx) % 30 + 30) % 30, ((25 - tidx) % 30 + 30) % 30)
            days_to_purn = ((14 - tidx) % 30 + 30) % 30
            days_to_ama = ((29 - tidx) % 30 + 30) % 30
            approaching = None
            for name, days_to, in [("Ekadashi", days_to_eka), ("Purnima", days_to_purn), ("Amavasya", days_to_ama)]:
                if days_to <= 2:
                    approaching = {"name": name, "days": days_to}
                    break

            # Vibe
            if tq == 'auspicious' and tara.get('favorable'):
                vibe = 'favorable'
            elif tq == 'inauspicious' or not tara.get('favorable'):
                vibe = 'caution'
            else:
                vibe = 'mixed'

            vara = VARAS[d.weekday()]

            days_result[date_str] = {
                "nakshatra": nak_name,
                "nakshatra_lord": nak_lord,
                "pada": pada,
                "tithi_index": tidx,
                "tithi_name": tithi_name,
                "tithi_num": tithi_num,
                "paksha": paksha,
                "tithi_quality": tq,
                "sun_moon_phase_deg": round(phase, 1),
                "moon_rashi": moon_rashi,
                "sun_rashi": sun_rashi,
                "moon_long": round(moon_sid, 1),
                "sun_long": round(sun_sid, 1),
                "bio": BIO.get(nak_name, "Leaf"),
                "guna": "sattva",  # simplified
                "deity": deity,
                "element": "fire",  # simplified
                "vara": vara,
                "approaching": approaching,
                "wave_score": round(wave_score, 3),
                "wave_peak_pair": wave_peak_str,
                "tara_bala": tara,
                "dignity_summary": f"Moon in {moon_rashi}",
                "vibe": vibe,
            }
        except Exception as exc:
            days_result[date_str] = {"error": str(exc)}

        d += timedelta(days=1)

    result = {"days": days_result}
    _calendar_cache[cache_key] = result
    _calendar_cache_ts = now_ts
    return jsonify(result)
