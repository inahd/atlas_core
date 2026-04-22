"""
transit_engine.py — Tarabala Transit Analysis

Computes the Vedic Tarabala (star-strength) relationship
between natal Moon nakshatra and each graha's current transit
nakshatra. The 9-fold cycle:

  1 Janma      — intense, personal
  2 Sampat     — wealth, resources
  3 Vipat      — obstacles, challenges
  4 Kṣema      — comfort, ease
  5 Pratyak    — obstacles, setbacks
  6 Sādhaka    — achievement, success
  7 Vadha      — danger, strain
  8 Mitra      — friendly, supportive
  9 Parama Mitra — very friendly, best

Cycle repeats: 10=Janma, 11=Sampat, etc.
"""

from typing import Dict, List, Optional

# 27 nakshatras in sidereal order
NAK_ORDER = [
    'Aśvinī', 'Bharaṇī', 'Kṛttikā', 'Rohiṇī', 'Mṛgaśīrṣa', 'Ārdrā',
    'Punarvasu', 'Puṣya', 'Āśleṣā', 'Maghā', 'Pūrva Phālgunī', 'Uttara Phālgunī',
    'Hasta', 'Citrā', 'Svātī', 'Viśākhā', 'Anurādhā', 'Jyeṣṭhā',
    'Mūla', 'Pūrvāṣāḍhā', 'Uttarāṣāḍhā', 'Śravaṇa', 'Dhaniṣṭhā', 'Śatabhiṣā',
    'Pūrva Bhādrapadā', 'Uttara Bhādrapadā', 'Revatī',
]

# Simplified name variants for matching
_NAK_ALIASES = {}
for i, n in enumerate(NAK_ORDER):
    _NAK_ALIASES[n.lower()] = i
    # Strip diacritics for fuzzy match
    import unicodedata
    folded = unicodedata.normalize('NFKD', n)
    folded = ''.join(c for c in folded if unicodedata.category(c) != 'Mn')
    _NAK_ALIASES[folded.lower()] = i
    # Common short forms
    short = folded.lower().split()[0]
    if short not in _NAK_ALIASES:
        _NAK_ALIASES[short] = i

# Extra aliases for common spellings
_EXTRA = {
    'ashwini':0, 'ashvini':0, 'bharani':1, 'krittika':2, 'rohini':3,
    'mrigashira':4, 'mrigasirsa':4, 'ardra':5, 'punarvasu':6, 'pushya':7,
    'ashlesha':8, 'magha':9, 'purva phalguni':10, 'uttara phalguni':11,
    'hasta':12, 'chitra':13, 'swati':14, 'svati':14, 'vishakha':15,
    'anuradha':16, 'jyeshtha':17, 'mula':18, 'moola':18,
    'purva ashadha':19, 'purvashadha':19, 'uttara ashadha':20, 'uttarashadha':20,
    'shravana':21, 'sravana':21, 'dhanishta':22, 'shatabhisha':23, 'satabhisa':23,
    'purva bhadrapada':24, 'uttara bhadrapada':25, 'revati':26,
}
_NAK_ALIASES.update(_EXTRA)

TARABALA = {
    1: ('Janma', 'intense · personal', 'challenging'),
    2: ('Sampat', 'wealth · resources', 'favorable'),
    3: ('Vipat', 'obstacles · challenges', 'challenging'),
    4: ('Kṣema', 'comfort · ease', 'favorable'),
    5: ('Pratyak', 'obstacles · setbacks', 'challenging'),
    6: ('Sādhaka', 'achievement · success', 'favorable'),
    7: ('Vadha', 'danger · strain', 'challenging'),
    8: ('Mitra', 'friendly · supportive', 'favorable'),
    9: ('Parama Mitra', 'very friendly · best', 'favorable'),
}


def _nak_index(name: str) -> int:
    """Find nakshatra index (0-26) from name with fuzzy matching."""
    if not name:
        return -1
    n = name.lower().strip()
    if n in _NAK_ALIASES:
        return _NAK_ALIASES[n]
    # Try substring match
    for key, idx in _NAK_ALIASES.items():
        if key in n or n in key:
            return idx
    return -1


def _nak_distance(from_idx: int, to_idx: int) -> int:
    """Count forward from from_idx to to_idx in 27-nak cycle. Returns 1-27."""
    if from_idx < 0 or to_idx < 0:
        return 0
    d = (to_idx - from_idx) % 27
    return d if d > 0 else 27  # 0 distance = same = 27 (completes cycle)


def get_transit_analysis(natal: dict, positions: dict) -> dict:
    """
    Compute Tarabala transit analysis.

    natal: dict with keys sun, moon, mars, mercury, jupiter, venus, saturn, rahu, ketu
           each having {nak: '...', rashi: '...'}
    positions: dict with same keys, current sky positions
    """
    moon_nak = ''
    if isinstance(natal.get('moon'), dict):
        moon_nak = natal['moon'].get('nak', '')
    moon_idx = _nak_index(moon_nak)

    lagna_nak = natal.get('lagna_nak', '')
    lagna_idx = _nak_index(lagna_nak.split(' pada')[0] if ' pada' in lagna_nak else lagna_nak)

    dasha = natal.get('dasha', {})
    dasha_lord = dasha.get('lord', '')
    dasha_closes = dasha.get('closes', '')

    grahas = ['sun', 'moon', 'mars', 'mercury', 'jupiter', 'venus', 'saturn', 'rahu', 'ketu']
    graha_labels = {
        'sun': 'Sūrya', 'moon': 'Candra', 'mars': 'Maṅgala',
        'mercury': 'Budha', 'jupiter': 'Guru', 'venus': 'Śukra',
        'saturn': 'Śani', 'rahu': 'Rāhu', 'ketu': 'Ketu',
    }

    transits = []
    highlighted = []

    for g in grahas:
        natal_rec = natal.get(g, {})
        current_rec = positions.get(g, {})

        natal_nak = natal_rec.get('nak', '') if isinstance(natal_rec, dict) else ''
        current_nak = current_rec.get('nak', '') if isinstance(current_rec, dict) else ''

        natal_idx = _nak_index(natal_nak)
        current_idx = _nak_index(current_nak)

        # Tarabala from natal Moon
        dist = _nak_distance(moon_idx, current_idx) if moon_idx >= 0 and current_idx >= 0 else 0
        tara_num = ((dist - 1) % 9) + 1 if dist > 0 else 0
        tara = TARABALA.get(tara_num, ('', '', ''))

        # Flag notable transits
        notable = False
        note = ''

        # Transiting natal Moon nakshatra
        if current_idx == moon_idx and moon_idx >= 0:
            notable = True
            note = f'transiting natal Moon nakshatra ({moon_nak})'

        # Transiting natal Lagna nakshatra
        if current_idx == lagna_idx and lagna_idx >= 0:
            notable = True
            note = f'transiting natal Lagna nakshatra ({lagna_nak})'

        # Saturn near natal Saturn (within 3 nakshatras)
        if g == 'saturn':
            sat_natal_idx = _nak_index(natal_nak)
            if sat_natal_idx >= 0 and current_idx >= 0:
                sat_dist = min(abs(current_idx - sat_natal_idx),
                               27 - abs(current_idx - sat_natal_idx))
                if sat_dist <= 3:
                    notable = True
                    note = f'Saturn return territory — {sat_dist} nakshatras from natal Saturn ({natal_nak})'

        # Dasha lord position
        if graha_labels.get(g, '').lower() == dasha_lord.lower() or g == dasha_lord.lower():
            if not note:
                note = f'dasha lord ({dasha_lord}) — current position significant'
                notable = True

        # Rahu/Ketu axis
        if g in ('rahu', 'ketu'):
            natal_rahu_idx = _nak_index(natal.get('rahu', {}).get('nak', '') if isinstance(natal.get('rahu'), dict) else '')
            natal_ketu_idx = _nak_index(natal.get('ketu', {}).get('nak', '') if isinstance(natal.get('ketu'), dict) else '')
            if current_idx >= 0:
                for nidx, label in [(natal_rahu_idx, 'natal Rāhu'), (natal_ketu_idx, 'natal Ketu')]:
                    if nidx >= 0:
                        axis_dist = min(abs(current_idx - nidx), 27 - abs(current_idx - nidx))
                        if axis_dist <= 2 and not note:
                            notable = True
                            note = f'near {label} axis ({axis_dist} naks)'

        entry = {
            'graha': graha_labels.get(g, g),
            'graha_key': g,
            'natal_nak': natal_nak,
            'current_nak': current_nak,
            'distance': dist,
            'tara_name': tara[0],
            'tara_meaning': tara[1],
            'quality': tara[2],
            'notable': notable,
            'note': note,
        }
        transits.append(entry)
        if notable:
            highlighted.append(entry)

    # Dasha context
    dasha_ctx = ''
    if dasha_lord and dasha_closes:
        dasha_ctx = f'{dasha_lord} daśā closes {dasha_closes}'
        dasha_graha = [t for t in transits if dasha_lord.lower() in t['graha'].lower()]
        if dasha_graha:
            dg = dasha_graha[0]
            dasha_ctx += f' — {dg["graha"]} transiting {dg["current_nak"]} ({dg["tara_name"]})'

    # Summary
    favorable = sum(1 for t in transits if t['quality'] == 'favorable')
    challenging = sum(1 for t in transits if t['quality'] == 'challenging')
    summary = f'{favorable} favorable, {challenging} challenging transits from natal Moon ({moon_nak})'

    return {
        'graha_transits': transits,
        'highlighted': highlighted[:3],
        'dasha_context': dasha_ctx,
        'summary': summary,
        'natal_moon': moon_nak,
        'natal_lagna': lagna_nak,
    }
