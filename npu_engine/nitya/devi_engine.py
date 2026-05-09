"""
devi_engine.py — Nitya Devi computation engine.

Returns the active Nitya Devi for the current tithi with all attested
attributes, plus render parameters for the quasicrystal projection.

Follows the derive_*() pattern. Reads from nitya_devi_master.csv.

# Atlas Relations:
#   datasets: cosmology/nitya_devi_master.csv, cosmology/nitya_yantra_geometry.csv,
#             astro/tithi_master.csv
#   engines: npu_engine/geometry/cut_and_project.py
#   graph: devi_* entities, tithi_* entities
#   routes: /nitya/devi/today, /nitya/devi/<id>, /nitya/field/<tithi>
"""

import csv
import os
from typing import Dict, Optional

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))

_cache: Dict[str, object] = {}

# N-fold symmetry per tithi position (construction choices in CONSTRUCTION_CHOICES.md)
DEVI_N = {
    1: 3, 2: 6, 3: 3, 4: 3, 5: 8, 6: 6, 7: 7, 8: 8,
    9: 9, 10: 10, 11: 11, 12: 12, 13: 13, 14: 14, 15: 15,
}

# Character descriptions for render calibration
DEVI_CHARACTER = {
    1:  "creative impulse, desire initiating — triangle pointing down, single thrust",
    2:  "solar manifestation chain, luminaries as garland — hexagonal symmetry, bright",
    3:  "ever-wet, perpetual moisture — soft triangle, water element, dissolving edges",
    4:  "the terrible pair, dual-force — triangle with inner tension, dark fire",
    5:  "dwelling in fire, purification — eight-pointed star, radiating outward",
    6:  "diamond sovereignty, indestructible will — hexagonal, crystalline, hard edges",
    7:  "irrational aperiodic field, still bindu, churning periphery — calm center, complex edges",
    8:  "the swift one, time compression — octagonal, rapid, sharp transitions",
    9:  "lineage transmission, kula beauty — nested triangular motifs at two scales",
    10: "the eternal itself, pure permanence — decagonal, smooth, self-similar",
    11: "85% Sri Yantra alignment — approaching full structure, almost-there tension",
    12: "complete victory, dharmic culmination — dodecagonal, resolved, stable",
    13: "all-limbed beauty, every part unique — irreducibly aperiodic, high complexity",
    14: "fire-garlanded, transformation ring — 7-fold doubled into a ring, penultimate",
    15: "the variegated, all colors present — full 15-fold bloom, Sri Yantra itself",
}


def _load_devi_master() -> Dict[int, dict]:
    """Load nitya_devi_master.csv keyed by tithi_num."""
    if 'devi_master' in _cache:
        return _cache['devi_master']
    path = os.path.join(_ROOT, 'datasets', 'cosmology', 'nitya_devi_master.csv')
    result = {}
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            # Skip comment lines
            lines = [line for line in f if not line.startswith('#')]
        import io
        for row in csv.DictReader(io.StringIO(''.join(lines))):
            try:
                num = int(row.get('tithi_num', 0))
                result[num] = row
            except (ValueError, TypeError):
                pass
    _cache['devi_master'] = result
    return result


def _load_yantra_geometry() -> Dict[int, dict]:
    """Load nitya_yantra_geometry.csv keyed by devi_id (tithi_number)."""
    if 'yantra_geo' in _cache:
        return _cache['yantra_geo']
    path = os.path.join(_ROOT, 'datasets', 'cosmology', 'nitya_yantra_geometry.csv')
    result = {}
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            lines = [line for line in f if not line.startswith('#')]
        import io
        for row in csv.DictReader(io.StringIO(''.join(lines))):
            try:
                num = int(row.get('tithi_number', 0))
                result[num] = row
            except (ValueError, TypeError):
                pass
    _cache['yantra_geo'] = result
    return result


def get_devi_by_tithi(tithi: int) -> dict:
    """
    Look up Nitya Devi by tithi number (1-30).

    Tithis 1-15 map directly. Tithis 16-30 map to 15-1 (reverse in Krishna).
    Returns full attribute dict with render params.
    """
    # Map to 1-15
    if tithi <= 0:
        tithi = 1
    if tithi > 15:
        tithi = 30 - tithi + 1  # Krishna paksha reverse
        if tithi <= 0:
            tithi = 1

    master = _load_devi_master()
    geo = _load_yantra_geometry()

    devi = dict(master.get(tithi, {}))
    yantra = geo.get(tithi, {})

    # Add render params
    N = DEVI_N.get(tithi, 3)
    devi['N'] = N
    devi['character'] = DEVI_CHARACTER.get(tithi, '')
    devi['tithi_position'] = tithi

    # Yantra geometry params
    devi['wave_function'] = yantra.get('wave_function', 'sine')
    devi['frequency_multiplier'] = float(yantra.get('frequency_multiplier', 1) or 1)
    devi['angular_position_degrees'] = float(yantra.get('angular_position_degrees', 0) or 0)
    devi['petal_count'] = int(yantra.get('petal_count', 8) or 8)
    devi['triangle_count'] = int(yantra.get('triangle_count', 1) or 1)
    devi['avarana_correspondence'] = yantra.get('avarana_correspondence', '')
    devi['sri_yantra_triangle'] = yantra.get('triangle_in_sri_yantra', '')
    devi['attestation'] = yantra.get('attestation', 'SPECULATIVE')
    devi['source_text'] = yantra.get('source_text', '')

    return devi


def get_current_devi(field_state: dict) -> dict:
    """
    Get the active Nitya Devi from the current field state.

    Reads tidx from panchanga, maps to Devi.
    """
    pa = field_state.get('panchanga', {}) or {}
    tidx = pa.get('tidx', 0)
    # tidx is 0-29, tithi_num is 1-30
    tithi = tidx + 1
    devi = get_devi_by_tithi(tithi)

    # Add live field context
    devi['tithi_name'] = pa.get('tithi', '')
    devi['paksha'] = pa.get('paksha', '')
    devi['nakshatra'] = pa.get('nakshatra', '')

    return devi


def get_render_params(tithi: int) -> dict:
    """
    Return render parameters for the cut-and-project call.

    Args:
        tithi: 1-15 (or 1-30, auto-mapped)

    Returns:
        {N, phase, k_default, construction, character}
    """
    if tithi > 15:
        tithi = 30 - tithi + 1
    if tithi <= 0:
        tithi = 1

    geo = _load_yantra_geometry()
    yantra = geo.get(tithi, {})

    N = DEVI_N.get(tithi, 3)
    phase = float(yantra.get('angular_position_degrees', 0) or 0) * np.pi / 180
    k_default = float(yantra.get('frequency_multiplier', 1) or 1)

    return {
        'N': N,
        'phase': round(phase, 4),
        'k_default': k_default,
        'construction': 'multigrid' if N > 6 else 'periodic',
        'character': DEVI_CHARACTER.get(tithi, ''),
    }


def get_mediator_params(tithi: int) -> dict:
    """
    Return 3D polyhedron mediator parameters for a Nitya Devi.

    The polyhedron sits between the 6D hypercubic parent and the 2D Nitya
    render — it is the intermediate object whose shadow is the quasicrystal.
    """
    from npu_engine.geometry.cut_and_project import polyhedron_mediator

    if tithi > 15:
        tithi = 30 - tithi + 1
    if tithi <= 0:
        tithi = 1

    N = DEVI_N.get(tithi, 3)
    poly = polyhedron_mediator(N)

    # 6D parent description
    phi_str = "1/φ" if N in (5, 10, 15) else f"2π/{N}"
    if N <= 6:
        parent_desc = f"{N}D periodic parent lattice, projected to 3D via standard crystallographic cut"
    else:
        parent_desc = f"6D hypercubic parent, cut at irrational angle θ = {phi_str} to produce {N}-fold quasicrystal"

    # Projection angle from yantra geometry
    geo = _load_yantra_geometry()
    yantra = geo.get(tithi, {})
    proj_angle = float(yantra.get('projection_angle_degrees', 15) or 15)

    return {
        'polyhedron': {
            'vertices': poly['vertices'],
            'faces': poly['faces'],
            'face_labels': poly.get('face_labels'),
            'construction_name': poly.get('construction_name', ''),
        },
        'N': N,
        'projection_angle': proj_angle,
        'sixd_parent_description': parent_desc,
    }


def render_devi_field(
    tithi: int,
    k: float = None,
    size: int = 512,
) -> np.ndarray:
    """
    Render the quasicrystal field for one Nitya Devi.

    Args:
        tithi: 1-15 (or 1-30)
        k: spatial frequency (default from yantra geometry)
        size: output dimensions

    Returns:
        np.ndarray of shape (size, size), values in [0, 1]
    """
    from npu_engine.geometry.cut_and_project import project_nfold

    params = get_render_params(tithi)
    if k is None:
        k = params['k_default']

    return project_nfold(
        N=params['N'],
        phase=params['phase'],
        k=k,
        size=size,
    )
