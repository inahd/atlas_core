"""
pasaka_engine.py — Pāśaka Dice Oracle Engine

3d4 cast mapped to 64 devī-named outcomes, scored against
the current field state (tithi, nakshatra, hora graha).

Follows the iching_augury_engine.py pattern:
  _csv_rows() loader, _cache dict, scoring against field_state.

Data source:
  datasets/iching/pasaka.csv — 64 rows (Bower MS pāśaka tradition)
"""

import csv
import os
import random
from typing import Dict, List, Optional

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))


def _csv_rows(relpath: str) -> List[dict]:
    path = os.path.join(_ROOT, relpath)
    if not os.path.exists(path):
        return []
    with open(path, encoding='utf-8') as f:
        return list(csv.DictReader(f))


# ── DATA LOADING ──────────────────────────────────────────

_cache: Dict[str, object] = {}

QUALITY_WEIGHT = {
    'excellent': 1.0,
    'very_good': 0.8,
    'good':      0.6,
    'mixed':     0.3,
}

# Lo Shu (Chinese orientation, same as iching_augury_engine)
VASTU_TO_LOSHU = {
    'SE': 4, 'S': 9, 'SW': 2,
    'E': 3,  'C': 5, 'W': 7,
    'NE': 8, 'N': 1, 'NW': 6,
}

# Graha → vastu direction (trigram positions)
GRAHA_VASTU = {
    'surya': 'S', 'chandra': 'SW', 'mangala': 'E',
    'budha': 'SE', 'guru': 'NE', 'shukra': 'W',
    'shani': 'N', 'rahu': 'N', 'ketu': 'NE',
}

# Graha magic constants (same as iching engine)
GRAHA_M = {
    'surya': 15, 'chandra': 18, 'mangala': 21,
    'budha': 24, 'guru': 27, 'shukra': 30,
    'shani': 33, 'rahu': 36, 'ketu': 39,
}

# Element → vastu direction
ELEMENT_VASTU = {
    'fire': 'S', 'water': 'N', 'earth': 'SW',
    'air': 'SE', 'ether': 'NW',
}

# Graha → nakshatra lordship
GRAHA_NAKSHATRAS = {
    'Sun':     ['Krittika', 'Uttara Phalguni', 'Uttara Ashadha'],
    'Moon':    ['Rohini', 'Hasta', 'Shravana'],
    'Mars':    ['Mrigashira', 'Chitra', 'Dhanishta'],
    'Mercury': ['Ashlesha', 'Jyeshtha', 'Revati'],
    'Jupiter': ['Punarvasu', 'Vishakha', 'Purva Bhadrapada'],
    'Venus':   ['Bharani', 'Purva Phalguni', 'Purva Ashadha'],
    'Saturn':  ['Pushya', 'Anuradha', 'Uttara Bhadrapada'],
    'Rahu':    ['Ardra', 'Swati', 'Shatabhisha'],
    'Ketu':    ['Ashwini', 'Magha', 'Mula'],
}


def _load_pasaka() -> List[dict]:
    """Load pāśaka outcomes from CSV."""
    if 'pasaka' in _cache:
        return _cache['pasaka']
    rows = _csv_rows('datasets/iching/pasaka.csv')
    _cache['pasaka'] = rows
    return rows


def _extract_hora_lord(field_state: dict) -> str:
    """Extract hora lord as English graha name from field state."""
    hora = field_state.get('hora', {})
    lord = hora.get('hora_lord', '')
    if lord.startswith('graha_'):
        return lord[6:].capitalize()
    name_map = {
        'surya': 'Sun', 'chandra': 'Moon', 'mangala': 'Mars',
        'budha': 'Mercury', 'guru': 'Jupiter', 'shukra': 'Venus',
        'shani': 'Saturn', 'rahu': 'Rahu', 'ketu': 'Ketu',
    }
    return name_map.get(lord.lower(), lord)


def _extract_nak_key(field_state: dict) -> str:
    """Extract nakshatra name_key from field state."""
    pa = field_state.get('panchanga', {}) or {}
    nd = pa.get('nak_data', {}) or {}
    return nd.get('name_key', '') or pa.get('nakshatra', '')


def _extract_nak_lord(field_state: dict) -> str:
    """Extract nakshatra lord from field state."""
    pa = field_state.get('panchanga', {}) or {}
    return pa.get('nak_lord', '') or (pa.get('nak_data', {}) or {}).get('graha', '')


# ── CAST ──────────────────────────────────────────────────

def cast(field_state: dict, seed: Optional[int] = None) -> dict:
    """Roll 3d4 and return the matching pāśaka row."""
    if seed is not None:
        random.seed(seed)
    d1 = random.randint(1, 4)
    d2 = random.randint(1, 4)
    d3 = random.randint(1, 4)
    rows = _load_pasaka()
    for r in rows:
        if int(r['dice_1']) == d1 and int(r['dice_2']) == d2 and int(r['dice_3']) == d3:
            return {**r, 'dice': [d1, d2, d3]}
    # fallback — should never happen with complete 64-row CSV
    return {**rows[0], 'dice': [d1, d2, d3]}


def derive_field_cast(field_state: dict) -> dict:
    """
    Deterministic pāśaka cast from the Lo Shu cube coordinates.

    Same field geometry the hexagram uses — different projection.
    The hexagram reads the trigram pair (binary);
    the pāśaka reads the Lo Shu weights modulo 4.

    d1 = hora graha's Lo Shu weight (vastu position) → mod 4 → 1-4
    d2 = nakshatra element's Lo Shu weight → mod 4 → 1-4
    d3 = graha magic constant M → mod 4 → 1-4
    """
    hora_lord = _extract_hora_lord_key(field_state)
    element = (field_state.get('panchanga', {}) or {}).get('element', 'fire').lower()

    # d1: hora graha → vastu → Lo Shu weight
    graha_vastu = GRAHA_VASTU.get(hora_lord, 'C')
    w1 = VASTU_TO_LOSHU.get(graha_vastu, 5)
    d1 = ((w1 - 1) % 4) + 1

    # d2: element → vastu → Lo Shu weight
    el_vastu = ELEMENT_VASTU.get(element, 'C')
    w2 = VASTU_TO_LOSHU.get(el_vastu, 5)
    d2 = ((w2 - 1) % 4) + 1

    # d3: graha magic constant M
    M = GRAHA_M.get(hora_lord, 15)
    d3 = ((M - 1) % 4) + 1

    rows = _load_pasaka()
    row = None
    for r in rows:
        if int(r['dice_1']) == d1 and int(r['dice_2']) == d2 and int(r['dice_3']) == d3:
            row = {**r, 'dice': [d1, d2, d3]}
            break
    if not row:
        row = {**rows[0], 'dice': [d1, d2, d3]}

    row['derived'] = True
    row['lo_shu'] = {
        'graha_vastu': graha_vastu,
        'graha_weight': w1,
        'element_vastu': el_vastu,
        'element_weight': w2,
        'graha_M': M,
    }
    return row


def _extract_hora_lord_key(field_state: dict) -> str:
    """Extract hora lord as lowercase Sanskrit key (surya, guru, etc)."""
    hora = field_state.get('hora', {})
    lord = hora.get('hora_lord', '')
    if lord.startswith('graha_'):
        return lord[6:]
    english_map = {
        'Sun': 'surya', 'Moon': 'chandra', 'Mars': 'mangala',
        'Mercury': 'budha', 'Jupiter': 'guru', 'Venus': 'shukra',
        'Saturn': 'shani', 'Rahu': 'rahu', 'Ketu': 'ketu',
    }
    return english_map.get(lord, lord.lower() or 'surya')


def get_by_id(cast_id: int) -> Optional[dict]:
    """Return a specific pāśaka outcome by ID (1-64)."""
    rows = _load_pasaka()
    for r in rows:
        if int(r['id']) == cast_id:
            return dict(r)
    return None


# ── SCORING ───────────────────────────────────────────────

def score_cast(field_state: dict, seed: Optional[int] = None) -> dict:
    """
    Cast 3d4 and score the result against current field state.

    Weights:
      quality          0.40  (excellent=1.0, very_good=0.8, good=0.6, mixed=0.3)
      graha resonance  0.35  (cast graha vs hora lord / nakshatra lord)
      nakshatra match  0.25  (cast graha rules current nakshatra)

    Returns dict with dice, outcome, score, body_region, field_reading.
    """
    row = cast(field_state, seed=seed)

    # ── quality component ──
    quality_w = QUALITY_WEIGHT.get(row.get('quality', 'mixed'), 0.3)

    # ── graha resonance ──
    cast_graha = row.get('graha', '')
    hora_lord = _extract_hora_lord(field_state)
    nak_lord = _extract_nak_lord(field_state)

    graha_score = 0.0
    if cast_graha == hora_lord:
        graha_score = 1.0
    elif cast_graha == nak_lord:
        graha_score = 0.7

    # ── nakshatra match ──
    nak_key = _extract_nak_key(field_state)
    nak_score = 0.0
    ruled = GRAHA_NAKSHATRAS.get(cast_graha, [])
    for rn in ruled:
        if rn.lower() in nak_key.lower():
            nak_score = 1.0
            break

    # ── composite ──
    score = 0.40 * quality_w + 0.35 * graha_score + 0.25 * nak_score

    pa = field_state.get('panchanga', {}) or {}
    row['score'] = round(score, 3)
    row['score_components'] = {
        'quality': round(quality_w, 2),
        'graha_resonance': round(graha_score, 2),
        'nakshatra_match': round(nak_score, 2),
    }
    row['field_context'] = {
        'hora_lord': hora_lord,
        'nak_lord': nak_lord,
        'nakshatra': pa.get('nakshatra', ''),
        'tithi': pa.get('tithi', ''),
        'element': pa.get('element', ''),
    }
    return row
