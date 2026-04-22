"""
iching_augury_engine.py — I Ching Augury Engine

Yantra-contextualised hexagram reading.
Scores hexagrams and natural omens against the current field state
using Lo Shu trigram weights derived from trigram_vastu_map.csv.

Research basis (April 12 2026):
  - Lo Shu weighted Q₆ breaks binomial degeneracy (7→27 eigenvalues)
  - Polarity |w_upper - w_lower| is spectrally richest (full rank 8)
  - ±2√6 does NOT transfer — systems interact without merging
  - Lo Shu differentiates hexagram space without imposing its own invariant
  - Fiedler value drops 2.0→0.19 under weighting (looser = more selective)

Data sources:
  datasets/iching/trigram_vastu_map.csv — canonical trigram→vastu positions
  datasets/iching/trigrams.csv          — trigram metadata
  datasets/iching/hexagrams.csv         — 64 hexagrams with vastu/graha/lifecycle
  datasets/vedic_omens.csv              — Brhat Samhita shakuna omens
"""

import csv
import os
import numpy as np
from typing import Dict, List, Optional

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))

# Lo Shu in Chinese orientation (S at top): 4 9 2 / 3 5 7 / 8 1 6
LO_SHU_CHINESE = np.array([[4, 9, 2], [3, 5, 7], [8, 1, 6]])

# Vastu direction → Lo Shu value (Chinese orientation)
VASTU_TO_LOSHU = {
    'SE': 4, 'S': 9, 'SW': 2,
    'E': 3,  'C': 5, 'W': 7,
    'NE': 8, 'N': 1, 'NW': 6,
}

# Graha magic constants from yantra_navagraha_engine
GRAHA_M = {
    'surya': 15, 'chandra': 18, 'mangala': 21,
    'budha': 24, 'guru': 27, 'shukra': 30,
    'shani': 33, 'rahu': 36, 'ketu': 39,
}


def _csv_rows(relpath: str) -> List[dict]:
    path = os.path.join(_ROOT, relpath)
    if not os.path.exists(path):
        return []
    with open(path, encoding='utf-8') as f:
        return list(csv.DictReader(f))


# ── DATA LOADING ───────────────────────────────────────────

_cache: Dict[str, object] = {}


def _load_trigrams() -> Dict[str, dict]:
    """Load trigram metadata keyed by entity_id."""
    if 'trigrams' in _cache:
        return _cache['trigrams']
    rows = _csv_rows('datasets/iching/trigrams.csv')
    result = {}
    for r in rows:
        eid = r.get('entity_id', '')
        vastu = r.get('vastu_position', '')
        lo_weight = VASTU_TO_LOSHU.get(vastu, 0)
        result[eid] = {
            **r,
            'lo_shu_weight': lo_weight,
            'binary': int(r.get('lines', '000'), 2),
        }
    _cache['trigrams'] = result
    return result


def _load_hexagrams() -> Dict[str, dict]:
    """Load hexagram metadata keyed by entity_id."""
    if 'hexagrams' in _cache:
        return _cache['hexagrams']
    rows = _csv_rows('datasets/iching/hexagrams.csv')
    result = {}
    for r in rows:
        result[r.get('entity_id', '')] = r
    _cache['hexagrams'] = result
    return result


def _load_omens() -> List[dict]:
    """Load vedic omens from Brhat Samhita dataset."""
    if 'omens' in _cache:
        return _cache['omens']
    rows = _csv_rows('datasets/vedic_omens.csv')
    _cache['omens'] = rows
    return rows


def _trigram_by_binary(binary: int) -> Optional[dict]:
    """Find trigram by its 3-bit binary value."""
    trigs = _load_trigrams()
    for t in trigs.values():
        if t.get('binary') == binary:
            return t
    return None


def _hexagram_by_number(num: int) -> Optional[dict]:
    """Find hexagram by King Wen number (1-64)."""
    hexes = _load_hexagrams()
    for h in hexes.values():
        if str(h.get('number', '')) == str(num):
            return h
    return None


# ── SCORING ────────────────────────────────────────────────

def score_hexagram(hex_binary: int, field_state: dict) -> dict:
    """
    Score a hexagram (0-63 binary) against the current field state.

    Polarity |w_upper - w_lower| is the richest spectral measure
    (full rank 8 in the 8×8 difference matrix — research finding).

    Returns dict with trigram info, scores, line analysis,
    and privileged transitions.
    """
    upper_bin = (hex_binary >> 3) & 0x7
    lower_bin = hex_binary & 0x7
    upper = _trigram_by_binary(upper_bin)
    lower = _trigram_by_binary(lower_bin)

    if not upper or not lower:
        return {'error': f'trigram lookup failed for {hex_binary}'}

    wu = upper['lo_shu_weight']
    wl = lower['lo_shu_weight']

    polarity = abs(wu - wl)
    sum_score = wu + wl
    product = wu * wl

    # Hora scaling
    hora_lord = _extract_hora_lord(field_state)
    M = GRAHA_M.get(hora_lord, 15)
    scaled_sum = sum_score * M / 15

    # Field resonance: high polarity + high weight = strong signal
    # Normalized to 0-1
    max_polarity = 8  # max |9-1|
    max_sum = 18      # max 9+9
    resonance = 0.5 * (polarity / max_polarity) + 0.5 * (sum_score / max_sum)

    # Line analysis
    lines = _score_lines(hex_binary)

    # Find matching hexagram metadata
    hex_meta = _find_hex_meta(upper, lower)

    return {
        'hexagram_binary': hex_binary,
        'upper_trigram': _trigram_summary(upper),
        'lower_trigram': _trigram_summary(lower),
        'polarity': polarity,
        'sum_score': sum_score,
        'product_score': product,
        'scaled_sum': round(scaled_sum, 2),
        'field_resonance': round(resonance, 3),
        'hora_lord': hora_lord,
        'hora_M': M,
        'lines': lines,
        'transitions': _privileged_transitions(hex_binary)[:3],
        'hexagram_meta': hex_meta,
    }


def _trigram_summary(t: dict) -> dict:
    return {
        'entity_id': t.get('entity_id', ''),
        'name': t.get('name_english', ''),
        'symbol': t.get('symbol', ''),
        'element': t.get('element', ''),
        'direction': t.get('vastu_position', ''),
        'lo_shu_weight': t['lo_shu_weight'],
        'graha': t.get('graha', ''),
        'animal': t.get('animal', ''),
    }


def _find_hex_meta(upper: dict, lower: dict) -> Optional[dict]:
    """Find hexagram metadata by upper/lower trigram entity_ids."""
    hexes = _load_hexagrams()
    uid = upper.get('entity_id', '')
    lid = lower.get('entity_id', '')
    for h in hexes.values():
        if h.get('upper_trigram') == uid and h.get('lower_trigram') == lid:
            return {
                'entity_id': h.get('entity_id', ''),
                'number': h.get('number', ''),
                'name_english': h.get('name_english', ''),
                'name_chinese': h.get('name_chinese', ''),
                'field_quality': h.get('field_quality', ''),
                'lifecycle_phase': h.get('lifecycle_phase', ''),
                'guna_primary': h.get('guna_primary', ''),
                'rasa_primary': h.get('rasa_primary', ''),
                'graha_primary': h.get('graha_primary', ''),
            }
    return None


def _score_lines(hex_binary: int) -> list:
    """
    Score each of the 6 lines for spectral activity.
    A line flip that increases sum weight is 'privileged';
    one that decreases is 'quieting'.
    """
    scores = []
    for line in range(6):
        adjacent = hex_binary ^ (1 << line)
        cur_w = _hex_weight(hex_binary)
        adj_w = _hex_weight(adjacent)
        delta = adj_w - cur_w

        scores.append({
            'line': line + 1,
            'position': 'upper' if line >= 3 else 'lower',
            'delta': delta,
            'direction': (
                'privileged' if delta > 0
                else 'neutral' if delta == 0
                else 'quieting'
            ),
        })
    return scores


def _hex_weight(hex_binary: int) -> int:
    upper = _trigram_by_binary((hex_binary >> 3) & 0x7)
    lower = _trigram_by_binary(hex_binary & 0x7)
    if not upper or not lower:
        return 0
    return upper['lo_shu_weight'] + lower['lo_shu_weight']


def _privileged_transitions(hex_binary: int) -> list:
    """Adjacent hexagrams ranked by Lo Shu weight (highest first)."""
    neighbors = []
    for line in range(6):
        adj = hex_binary ^ (1 << line)
        neighbors.append({
            'hexagram': adj,
            'weight': _hex_weight(adj),
            'line_changed': line + 1,
        })
    return sorted(neighbors, key=lambda x: x['weight'], reverse=True)


def _extract_hora_lord(field_state: dict) -> str:
    """Extract hora lord graha name from field state."""
    hora = field_state.get('hora', {})
    lord = hora.get('hora_lord', '')
    # Normalize: "graha_guru" → "guru", "Jupiter" → "guru"
    if lord.startswith('graha_'):
        return lord[6:]
    name_map = {
        'Sun': 'surya', 'Moon': 'chandra', 'Mars': 'mangala',
        'Mercury': 'budha', 'Jupiter': 'guru', 'Venus': 'shukra',
        'Saturn': 'shani', 'Rahu': 'rahu', 'Ketu': 'ketu',
    }
    return name_map.get(lord, 'surya')


# ── OMEN SCORING ───────────────────────────────────────────

def score_omen(phenomenon: str, direction: str,
               field_state: dict) -> dict:
    """
    Score a natural omen against the current field state.

    Uses vedic_omens.csv (Brhat Samhita) for traditional readings,
    then layers Lo Shu trigram weight for spectral context.
    """
    omens = _load_omens()
    phenomenon_lower = phenomenon.lower().strip()
    direction_lower = direction.lower().strip() if direction else ''

    # Find matching omens from Brhat Samhita
    matches = []
    for o in omens:
        species = o.get('bird_species', '').lower()
        obs = o.get('specific_observation', '').lower()
        odir = o.get('direction', '').lower()
        if phenomenon_lower in species or phenomenon_lower in obs:
            if not direction_lower or direction_lower in odir:
                matches.append(o)

    # Get direction Lo Shu weight
    dir_weight = VASTU_TO_LOSHU.get(direction.upper(), 5) if direction else 5

    # Find trigram for the direction
    trigs = _load_trigrams()
    dir_trigram = None
    for t in trigs.values():
        if t.get('vastu_position', '').upper() == direction.upper():
            dir_trigram = t
            break

    hora_lord = _extract_hora_lord(field_state)
    M = GRAHA_M.get(hora_lord, 15)

    return {
        'phenomenon': phenomenon,
        'direction': direction,
        'lo_shu_weight': dir_weight,
        'scaled_weight': round(dir_weight * M / 15, 2),
        'hora_lord': hora_lord,
        'hora_M': M,
        'trigram': _trigram_summary(dir_trigram) if dir_trigram else None,
        'traditional_readings': [
            {
                'observation': o.get('specific_observation', ''),
                'meaning': o.get('omen_meaning', ''),
                'quality': o.get('omen_quality', ''),
                'field_indicated': o.get('field_state_indicated', ''),
                'source': o.get('source_text', ''),
            }
            for o in matches[:5]
        ],
        'match_count': len(matches),
    }


# ── FIELD MAP ──────────────────────────────────────────────

def trigram_field_map(field_state: dict) -> dict:
    """
    Return the full Lo Shu trigram weight map for current field.
    Each trigram weighted by its vastu→Lo Shu position,
    scaled by current hora M.
    """
    trigs = _load_trigrams()
    hora_lord = _extract_hora_lord(field_state)
    M = GRAHA_M.get(hora_lord, 15)

    weights = {}
    for eid, t in trigs.items():
        w = t['lo_shu_weight']
        weights[eid] = {
            'name': t.get('name_english', ''),
            'symbol': t.get('symbol', ''),
            'direction': t.get('vastu_position', ''),
            'lo_shu_weight': w,
            'scaled_weight': round(w * M / 15, 2),
            'element': t.get('element', ''),
            'graha': t.get('graha', ''),
        }

    return {
        'hora_lord': hora_lord,
        'hora_M': M,
        'trigram_weights': weights,
        'spectral_note': (
            'Lo Shu weighting breaks Q6 binomial degeneracy '
            '(7→27 unique eigenvalues). Polarity = |w_upper - w_lower| '
            'is the spectrally richest scoring measure.'
        ),
    }


# ── CAST ───────────────────────────────────────────────────

def cast_hexagram(field_state: dict, seed: Optional[int] = None) -> dict:
    """Cast a hexagram scored against current field state."""
    import random
    if seed is not None:
        random.seed(seed)
    hex_binary = random.randint(0, 63)
    result = score_hexagram(hex_binary, field_state)
    result['cast'] = True
    return result


# ── FLASK ROUTE REGISTRATION ──────────────────────────────

def register_augury_routes(app, get_field_state):
    """Register I Ching augury routes with Atlas Flask kernel."""

    @app.route('/lila/augury/hexagram/<int:hex_int>')
    def augury_hexagram(hex_int):
        if not 0 <= hex_int <= 63:
            return {'error': 'hexagram must be 0-63'}, 400
        return score_hexagram(hex_int, get_field_state())

    @app.route('/lila/augury/omen/<phenomenon>')
    @app.route('/lila/augury/omen/<phenomenon>/<direction>')
    def augury_omen(phenomenon, direction=None):
        return score_omen(phenomenon, direction or '', get_field_state())

    @app.route('/lila/augury/cast')
    def augury_cast():
        return cast_hexagram(get_field_state())

    @app.route('/lila/augury/field')
    def augury_field():
        return trigram_field_map(get_field_state())

    print("  [augury] /lila/augury/hexagram/<0-63>")
    print("  [augury] /lila/augury/omen/<phenomenon>[/<direction>]")
    print("  [augury] /lila/augury/cast")
    print("  [augury] /lila/augury/field")
