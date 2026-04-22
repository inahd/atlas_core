"""
cut_and_project.py — N-fold quasicrystal projection for Nitya Devi portal.

Generates 2D intensity fields via the cut-and-project method from higher-
dimensional lattices. Each N-fold symmetry produces a distinct tiling/field.

For crystallographic N (2,3,4,6): periodic lattice.
For quasicrystalline N (5,7,8,9,10,11,12,13,14,15): aperiodic cut-and-project.

Construction choices documented in CONSTRUCTION_CHOICES.md.

# Atlas Relations:
#   datasets: cosmology/nitya_devi_master.csv, cosmology/nitya_yantra_geometry.csv
#   engines: npu_engine/nitya/devi_engine.py
#   routes: /nitya/field/<tithi>
"""

import numpy as np
from typing import Optional


def project_nfold(
    N: int,
    phase: float = 0.0,
    k: float = 1.0,
    size: int = 512,
    gamma: float = 0.0,
) -> np.ndarray:
    """
    Generate a 2D intensity field with N-fold quasicrystal symmetry.

    Uses the dual-grid / multigrid method: N sets of parallel lines at
    angles 2*pi*j/N (j=0..N-1), with spacing controlled by k. The
    intersection density of the dual grid produces the quasicrystal pattern.

    Args:
        N: fold symmetry (2-15)
        phase: global phase offset in radians
        k: spatial frequency (higher = finer structure)
        size: output field dimensions (size x size)
        gamma: per-grid phase shift (shifts the cut hyperplane)

    Returns:
        np.ndarray of shape (size, size), values in [0, 1].
    """
    # Coordinate grid centered on origin
    half = size / 2
    x = np.linspace(-half, half, size) / (size / (4 * k))
    y = np.linspace(-half, half, size) / (size / (4 * k))
    X, Y = np.meshgrid(x, y)

    # Multigrid method: sum cos waves at N equally-spaced angles
    # The interference pattern of N plane waves produces N-fold symmetry.
    # For quasicrystalline N, this is equivalent to the Fourier transform
    # of the cut-and-project tiling.
    field = np.zeros((size, size), dtype=np.float64)

    for j in range(N):
        angle = 2 * np.pi * j / N + phase
        # Project coordinates onto this direction
        proj = X * np.cos(angle) + Y * np.sin(angle)
        # Add cosine wave along this direction
        field += np.cos(proj + gamma * j)

    # Normalize to [0, 1]
    fmin, fmax = field.min(), field.max()
    if fmax > fmin:
        field = (field - fmin) / (fmax - fmin)
    else:
        field = np.full_like(field, 0.5)

    return field


def project_nfold_sharp(
    N: int,
    phase: float = 0.0,
    k: float = 1.0,
    size: int = 512,
    gamma: float = 0.0,
) -> np.ndarray:
    """
    Sharp-edge variant: uses floor() instead of cos() for tile boundaries.
    Produces the actual quasicrystal tiling rather than the smooth interference.
    """
    half = size / 2
    x = np.linspace(-half, half, size) / (size / (4 * k))
    y = np.linspace(-half, half, size) / (size / (4 * k))
    X, Y = np.meshgrid(x, y)

    field = np.zeros((size, size), dtype=np.float64)

    for j in range(N):
        angle = 2 * np.pi * j / N + phase
        proj = X * np.cos(angle) + Y * np.sin(angle)
        # Floor creates tile boundaries
        field += np.floor(proj + gamma * j) % 2

    # Normalize
    fmin, fmax = field.min(), field.max()
    if fmax > fmin:
        field = (field - fmin) / (fmax - fmin)
    return field


def project_sri_yantra(
    k: float = 1.0,
    size: int = 512,
    weights: Optional[dict] = None,
) -> np.ndarray:
    """
    Full Sri Yantra field: superposition of all 15 Nitya contributions.

    Each Nitya contributes her N-fold field weighted by her classical
    tithi-group amplitude. The composite is the complete field the
    per-Devi slices live inside.

    Args:
        k: spatial frequency
        size: output dimensions
        weights: optional {tithi_num: weight} override

    Returns:
        np.ndarray of shape (size, size), values in [0, 1].
    """
    # Default: N-fold symmetries for each tithi position
    # These are the construction choices from the Nitya tradition
    DEVI_N = {
        1: 3,   # Kameshvari — trikona (triangle)
        2: 6,   # Bhagamalini — hexagram
        3: 3,   # Nityaklinna — trikona
        4: 3,   # Bherunda — trikona
        5: 8,   # Vahnivasini — eight triangles (ashtakona)
        6: 6,   # Mahavajreshvari — hexagram
        7: 7,   # Shivaduti — heptagram (irrational, aperiodic)
        8: 8,   # Tvarita — octagonal
        9: 9,   # Kulasundari — navakona
        10: 10,  # Nitya — decagonal
        11: 11,  # Nilapataka — hendecagonal (quasicrystalline)
        12: 12,  # Vijaya — dodecagonal
        13: 13,  # Sarvangasundari — 13-fold
        14: 14,  # Jvalamalini — 14-fold (fire garland)
        15: 15,  # Chidagni Kala / Citra — full 15-fold bloom
    }

    composite = np.zeros((size, size), dtype=np.float64)

    for tithi, N in DEVI_N.items():
        w = 1.0
        if weights:
            w = weights.get(tithi, 1.0)
        # Phase offset per Devi: distribute around the circle
        phase = 2 * np.pi * (tithi - 1) / 15
        layer = project_nfold(N, phase=phase, k=k, size=size)
        composite += w * layer

    # Normalize
    fmin, fmax = composite.min(), composite.max()
    if fmax > fmin:
        composite = (composite - fmin) / (fmax - fmin)
    return composite


def field_to_image_data(field: np.ndarray, colormap: str = 'gold') -> list:
    """
    Convert a 2D field to a flat RGBA pixel list for canvas rendering.

    Args:
        field: 2D numpy array, values in [0, 1]
        colormap: 'gold' (warm), 'teal' (cool), 'devi' (per-devi color)

    Returns:
        flat list of [r, g, b, a, r, g, b, a, ...] values (0-255)
    """
    h, w = field.shape
    pixels = []

    for y in range(h):
        for x in range(w):
            v = field[y, x]
            if colormap == 'teal':
                r, g, b = int(20 + 73 * v), int(80 + 122 * v), int(100 + 65 * v)
            elif colormap == 'gold':
                r, g, b = int(40 + 160 * v), int(30 + 139 * v), int(10 + 100 * v)
            else:
                r, g, b = int(v * 255), int(v * 200), int(v * 150)
            a = int(40 + 200 * v)
            pixels.extend([r, g, b, a])

    return pixels
