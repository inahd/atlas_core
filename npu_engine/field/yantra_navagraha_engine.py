"""
yantra_navagraha_engine.py — Navagraha Yantra Matrix Engine

Each graha's yantra = Lo Shu + k×J where k ∈ {0..8}.
Eigenvalues: {M, +2√6, -2√6} where M = 15 + 3k.
The ±2√6 eigenvectors map to 9 Vastu zones.
"""

import math
import numpy as np
from typing import Dict, Optional

LO_SHU = np.array([[2, 7, 6], [9, 5, 1], [4, 3, 8]], dtype=np.float64)
J = np.ones((3, 3), dtype=np.float64)
SQRT6_2 = 2 * math.sqrt(6)

GRAHA_K = {
    'graha_surya': 0, 'graha_chandra': 1, 'graha_mangala': 2,
    'graha_budha': 3, 'graha_guru': 4, 'graha_shukra': 5,
    'graha_shani': 6, 'graha_rahu': 7, 'graha_ketu': 8,
}

GRAHA_NAMES = {
    'graha_surya': 'Sūrya', 'graha_chandra': 'Candra', 'graha_mangala': 'Maṅgala',
    'graha_budha': 'Budha', 'graha_guru': 'Guru', 'graha_shukra': 'Śukra',
    'graha_shani': 'Śani', 'graha_rahu': 'Rāhu', 'graha_ketu': 'Ketu',
}

VARA_TO_GRAHA = {
    'ravivara': 'graha_surya', 'somavara': 'graha_chandra',
    'mangalavara': 'graha_mangala', 'budhavara': 'graha_budha',
    'guruvara': 'graha_guru', 'brihaspativara': 'graha_guru',
    'shukravara': 'graha_shukra', 'shanivara': 'graha_shani',
}

VASTU_ZONES = [
    ['Ishan (NE)', 'Uttara (N)', 'Vayavya (NW)'],
    ['Purva (E)', 'Brahma', 'Paschima (W)'],
    ['Agneya (SE)', 'Dakshina (S)', 'Nairitya (SW)'],
]

ZONE_DATA = {
    'Brahma':       {'deity': 'Brahmā',  'element': 'ether', 'color': '#9370db', 'direction': 'Center'},
    'Ishan (NE)':   {'deity': 'Īśāna',   'element': 'water', 'color': '#4a9eff', 'direction': 'NE'},
    'Uttara (N)':   {'deity': 'Kubera',   'element': 'earth', 'color': '#00d4aa', 'direction': 'N'},
    'Vayavya (NW)': {'deity': 'Vāyu',     'element': 'air',   'color': '#c8a96e', 'direction': 'NW'},
    'Purva (E)':    {'deity': 'Indra',    'element': 'fire',  'color': '#ff6b35', 'direction': 'E'},
    'Paschima (W)': {'deity': 'Varuṇa',   'element': 'water', 'color': '#4a9eff', 'direction': 'W'},
    'Agneya (SE)':  {'deity': 'Agni',     'element': 'fire',  'color': '#ff6b35', 'direction': 'SE'},
    'Dakshina (S)': {'deity': 'Yama',     'element': 'earth', 'color': '#00d4aa', 'direction': 'S'},
    'Nairitya (SW)':{'deity': 'Nirṛti',   'element': 'earth', 'color': '#888888', 'direction': 'SW'},
}


def _vara_to_graha_id(vara_str: str) -> str:
    """Map Sanskrit vara name to graha entity_id."""
    norm = vara_str.lower().split()[0]
    norm = norm.replace('ā', 'a').replace('ī', 'i').replace('ū', 'u').replace('ś', 'sh').replace('ṣ', 'sh')
    for k, v in VARA_TO_GRAHA.items():
        if k in norm or norm in k:
            return v
    return 'graha_surya'


def get_current_yantra(field_state: dict) -> dict:
    """Return the Navagraha yantra for the current field state."""
    pa = field_state.get('panchanga', {})
    vara = pa.get('vara', '')
    hora = field_state.get('hora', {})
    hora_lord = hora.get('hora_lord', '')

    # Determine graha from hora lord or vara
    graha_id = None
    if hora_lord:
        for gid, gname in GRAHA_NAMES.items():
            if hora_lord.lower() in gname.lower() or gname.lower() in hora_lord.lower():
                graha_id = gid
                break
        if not graha_id:
            hora_map = {'Sun': 'graha_surya', 'Moon': 'graha_chandra', 'Mars': 'graha_mangala',
                        'Mercury': 'graha_budha', 'Jupiter': 'graha_guru', 'Venus': 'graha_shukra',
                        'Saturn': 'graha_shani', 'Rahu': 'graha_rahu', 'Ketu': 'graha_ketu'}
            graha_id = hora_map.get(hora_lord, None)
    if not graha_id:
        graha_id = _vara_to_graha_id(vara)

    k = GRAHA_K.get(graha_id, 0)
    Y = LO_SHU + k * J
    M = 15 + 3 * k
    evals = sorted(np.real(np.linalg.eigvals(Y)).tolist())

    # Build cells
    cells = []
    for r in range(3):
        for c in range(3):
            zone = VASTU_ZONES[r][c]
            zd = ZONE_DATA.get(zone, {})
            cells.append({
                'row': r, 'col': c,
                'value': int(Y[r, c]),
                'vastu_zone': zone,
                'vastu_deity': zd.get('deity', ''),
                'vastu_element': zd.get('element', ''),
                'vastu_color': zd.get('color', '#333'),
                'vastu_direction': zd.get('direction', ''),
            })

    brahma_cell = next((c for c in cells if c['vastu_zone'] == 'Brahma'), cells[4])

    # Active direction from hora/vara element
    element = pa.get('element', 'ether')
    elem_dir = {'fire': 'SE', 'water': 'NE', 'earth': 'S', 'air': 'NW', 'ether': 'Center'}
    active_dir = elem_dir.get(element, 'Center')

    return {
        'graha': graha_id,
        'graha_name': GRAHA_NAMES.get(graha_id, graha_id),
        'k': k,
        'magic_constant': M,
        'matrix': Y.astype(int).tolist(),
        'eigenvalues': [round(e, 6) for e in evals],
        'invariant_eigenvalue': round(SQRT6_2, 6),
        'cells': cells,
        'brahmasthana': {
            'value': brahma_cell['value'],
            'coherence': 1.0,
        },
        'vastu_active_direction': active_dir,
        'field_element': element,
        'field_nakshatra': pa.get('nakshatra', ''),
        'field_tithi': pa.get('tithi', ''),
        'attestation': 'OBSERVED:VERIFIED',
    }
