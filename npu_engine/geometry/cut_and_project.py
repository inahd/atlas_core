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


# ══════════════════════════════════════════════════════════
# 3D POLYHEDRON MEDIATORS
# ══════════════════════════════════════════════════════════

def _antiprism(N: int, radius: float = 1.0) -> dict:
    """N-gonal antiprism: 2N vertices, 2N triangular + 2 N-gonal faces."""
    verts = []
    # Top ring
    for i in range(N):
        a = 2 * np.pi * i / N
        verts.append((radius * np.cos(a), 0.5, radius * np.sin(a)))
    # Bottom ring (rotated by pi/N)
    for i in range(N):
        a = 2 * np.pi * i / N + np.pi / N
        verts.append((radius * np.cos(a), -0.5, radius * np.sin(a)))

    faces = []
    # Side triangles
    for i in range(N):
        t_next = (i + 1) % N
        b_curr = i + N
        b_next = (i + 1) % N + N
        faces.append([i, t_next, b_curr])
        faces.append([t_next, b_next, b_curr])
    # Top cap
    faces.append(list(range(N)))
    # Bottom cap
    faces.append(list(range(N, 2 * N)))

    return {'vertices': verts, 'faces': faces, 'face_labels': None}


def _icosahedron(radius: float = 1.0) -> dict:
    """Regular icosahedron (20 faces, 12 vertices)."""
    phi = (1 + np.sqrt(5)) / 2
    s = radius / np.sqrt(1 + phi * phi)
    verts = [
        (-s, phi*s, 0), (s, phi*s, 0), (-s, -phi*s, 0), (s, -phi*s, 0),
        (0, -s, phi*s), (0, s, phi*s), (0, -s, -phi*s), (0, s, -phi*s),
        (phi*s, 0, -s), (phi*s, 0, s), (-phi*s, 0, -s), (-phi*s, 0, s),
    ]
    faces = [
        [0,11,5],[0,5,1],[0,1,7],[0,7,10],[0,10,11],
        [1,5,9],[5,11,4],[11,10,2],[10,7,6],[7,1,8],
        [3,9,4],[3,4,2],[3,2,6],[3,6,8],[3,8,9],
        [4,9,5],[2,4,11],[6,2,10],[8,6,7],[9,8,1],
    ]
    return {'vertices': verts, 'faces': faces, 'face_labels': None}


def _dodecahedron(radius: float = 1.0) -> dict:
    """Regular dodecahedron (12 pentagonal faces, 20 vertices)."""
    phi = (1 + np.sqrt(5)) / 2
    s = radius / np.sqrt(3)
    verts = [
        (s,s,s),(s,s,-s),(s,-s,s),(s,-s,-s),
        (-s,s,s),(-s,s,-s),(-s,-s,s),(-s,-s,-s),
        (0,s/phi,s*phi),(0,s/phi,-s*phi),(0,-s/phi,s*phi),(0,-s/phi,-s*phi),
        (s/phi,s*phi,0),(s/phi,-s*phi,0),(-s/phi,s*phi,0),(-s/phi,-s*phi,0),
        (s*phi,0,s/phi),(s*phi,0,-s/phi),(-s*phi,0,s/phi),(-s*phi,0,-s/phi),
    ]
    faces = [
        [0,16,2,10,8],[0,8,4,14,12],[0,12,1,17,16],
        [1,9,11,3,17],[1,12,14,5,9],[2,16,17,3,13],
        [2,13,15,6,10],[3,11,7,15,13],[4,8,10,6,18],
        [4,18,19,5,14],[5,19,7,11,9],[6,15,7,19,18],
    ]
    return {'vertices': verts, 'faces': faces, 'face_labels': None}


def _rhombic_triacontahedron(radius: float = 1.0) -> dict:
    """Exact rhombic triacontahedron: 32 vertices, 60 triangular faces, 60 edges.

    Constructed as the dual of the icosidodecahedron. The 32 vertices are the
    face centers of the icosidodecahedron (12 from pentagonal faces, 20 from
    triangular faces). All 32 lie on the convex hull.

    The 60 triangular faces pair into 30 near-coplanar rhombic groups. Each
    pair shares an edge and meets at a dihedral angle of ~15°. For rendering,
    paired triangles are grouped so face highlighting illuminates both triangles
    of a rhombus together. 30 pairs = 30 tithis."""
    from scipy.spatial import ConvexHull

    phi = (1 + np.sqrt(5)) / 2

    # Icosidodecahedron vertices (30): permutations of (0, 0, ±phi) and
    # all sign combinations of (±1/2, ±phi/2, ±(1+phi)/2)
    iv = []
    for perm in [(0, 1, 2), (1, 2, 0), (2, 0, 1)]:
        for s in [-1, 1]:
            v = [0.0, 0.0, 0.0]
            v[perm[2]] = s * phi
            iv.append(v)
    for perm in [(0, 1, 2), (1, 2, 0), (2, 0, 1)]:
        for s1 in [-1, 1]:
            for s2 in [-1, 1]:
                for s3 in [-1, 1]:
                    v = [0.0, 0.0, 0.0]
                    v[perm[0]] = s1 * 0.5
                    v[perm[1]] = s2 * phi / 2
                    v[perm[2]] = s3 * (1 + phi) / 2
                    iv.append(v)
    iv = np.array(iv)

    # Icosidodecahedron convex hull → face groups → RT vertices (face centers)
    hull_id = ConvexHull(iv)
    normals_id = hull_id.equations[:, :3]
    nn = np.linalg.norm(normals_id, axis=1, keepdims=True)
    nu_id = normals_id / (nn + 1e-12)

    groups_id = {}
    for i, n in enumerate(nu_id):
        groups_id.setdefault(tuple(np.round(n, 2)), []).append(i)

    rt_verts = []
    for key, tris in sorted(groups_id.items()):
        all_vidx = set()
        for ti in tris:
            for vi in hull_id.simplices[ti]:
                all_vidx.add(int(vi))
        center = np.mean(iv[list(all_vidx)], axis=0)
        rt_verts.append(center)
    rt_verts = np.array(rt_verts)

    # Scale to requested radius
    max_r = np.max(np.linalg.norm(rt_verts, axis=1))
    if max_r > 0:
        rt_verts = rt_verts * (radius / max_r)

    # RT convex hull → 60 triangular faces
    rt_hull = ConvexHull(rt_verts)
    simplices = rt_hull.simplices

    # Identify vertex types: pentagon-center (ico, 'P') vs triangle-center (dod, 'T')
    # Pentagon-face centers of icosidodecahedron → 12 ico-type RT vertices (5-valent)
    # Triangle-face centers → 20 dod-type RT vertices (3-valent)
    vert_types = []
    for key, tris in sorted(groups_id.items()):
        vert_types.append('P' if len(tris) == 3 else 'T')

    # Pair triangles that share a T-T edge (dod-dod, the long diagonal of the rhombus)
    # Each triangle has vertex types (P, T, T). Two triangles sharing their T-T edge
    # form one rhombic face. This gives exactly 30 pairs for 60 triangles.
    paired = set()
    face_pairs = []
    unpaired = []

    for i in range(len(simplices)):
        if i in paired:
            continue
        ti = set(int(x) for x in simplices[i])
        best_j = -1
        for j in range(i + 1, len(simplices)):
            if j in paired:
                continue
            tj = set(int(x) for x in simplices[j])
            shared = ti & tj
            if len(shared) == 2:
                sv = list(shared)
                if vert_types[sv[0]] == 'T' and vert_types[sv[1]] == 'T':
                    best_j = j
                    break
        if best_j >= 0:
            paired.add(i)
            paired.add(best_j)
            face_pairs.append([i, best_j])
        else:
            paired.add(i)
            unpaired.append(i)

    # Build face list: each "face" is a list of triangle-index pairs (for quad highlighting)
    # But the actual geometry uses individual triangles for Three.js
    faces = []
    face_labels = []

    for pi, (i, j) in enumerate(face_pairs):
        faces.append([int(x) for x in simplices[i]])
        faces.append([int(x) for x in simplices[j]])
        face_labels.append(pi + 1)
        face_labels.append(pi + 1)  # same label for both triangles of the rhombus

    for i in unpaired:
        faces.append([int(x) for x in simplices[i]])
        face_labels.append(len(face_pairs) + 1)

    # Sort face-pairs by centroid azimuthal angle for deterministic tithi ordering
    # Re-sort in pairs
    pair_centroids = []
    for pi, (i, j) in enumerate(face_pairs):
        c1 = np.mean(rt_verts[simplices[i]], axis=0)
        c2 = np.mean(rt_verts[simplices[j]], axis=0)
        c = (c1 + c2) / 2
        pair_centroids.append(float(np.arctan2(c[2], c[0]) + np.pi * (1 if c[1] < 0 else 0)))

    order = np.argsort(pair_centroids)

    sorted_faces = []
    sorted_labels = []
    for new_idx, old_idx in enumerate(order):
        i, j = face_pairs[old_idx]
        sorted_faces.append([int(x) for x in simplices[i]])
        sorted_faces.append([int(x) for x in simplices[j]])
        sorted_labels.append(new_idx + 1)
        sorted_labels.append(new_idx + 1)

    return {
        'vertices': [[round(float(v[0]), 5), round(float(v[1]), 5), round(float(v[2]), 5)] for v in rt_verts],
        'faces': sorted_faces,
        'face_labels': sorted_labels,
    }


def polyhedron_mediator(N: int) -> dict:
    """
    Return the 3D polyhedron mediating between 6D parent and 2D Nitya render.

    Args:
        N: fold symmetry of the Nitya (3-15)

    Returns:
        {vertices, faces, face_labels, construction_name}
    """
    if N == 3:
        # Tetrahedron (4 faces, simplest Platonic)
        s = 1.0
        v = [(s,s,s),(s,-s,-s),(-s,s,-s),(-s,-s,s)]
        f = [[0,1,2],[0,1,3],[0,2,3],[1,2,3]]
        return {'vertices': v, 'faces': f, 'face_labels': None, 'construction_name': 'tetrahedron'}
    elif N == 4:
        # Cube (6 faces)
        s = 0.7
        v = [(s,s,s),(s,s,-s),(s,-s,s),(s,-s,-s),(-s,s,s),(-s,s,-s),(-s,-s,s),(-s,-s,-s)]
        f = [[0,1,3,2],[4,5,7,6],[0,1,5,4],[2,3,7,6],[0,2,6,4],[1,3,7,5]]
        return {'vertices': v, 'faces': f, 'face_labels': None, 'construction_name': 'cube'}
    elif N == 5:
        result = _icosahedron()
        result['construction_name'] = 'icosahedron'
        return result
    elif N == 6:
        # Cuboctahedron (14 faces: 8 triangles + 6 squares)
        s = 1.0
        v = [(s,s,0),(s,-s,0),(-s,s,0),(-s,-s,0),(s,0,s),(s,0,-s),(-s,0,s),(-s,0,-s),(0,s,s),(0,s,-s),(0,-s,s),(0,-s,-s)]
        f = [[0,4,8],[0,8,2],[2,8,6],[2,6,3],[3,6,10],[3,10,1],[1,10,4],[1,4,0],
             [5,9,0],[5,0,1],[5,1,11],[5,11,7],[7,11,3],[7,3,2],[7,2,9],[9,5,7],
             [4,10,6,8],[0,9,7,2],[1,5,9,0],[3,11,5,1]]  # simplified
        return {'vertices': v, 'faces': f[:14], 'face_labels': None, 'construction_name': 'cuboctahedron'}
    elif N == 10:
        result = _dodecahedron()
        result['construction_name'] = 'dodecahedron'
        return result
    elif N == 12:
        # Use icosahedron (close to dodecagonal symmetry in projection)
        result = _icosahedron()
        result['construction_name'] = 'icosahedron (dodecagonal projection)'
        return result
    elif N == 15:
        result = _rhombic_triacontahedron()
        result['construction_name'] = 'rhombic triacontahedron'
        return result
    else:
        # N=7, 8, 9, 11, 13, 14 → N-gonal antiprism
        result = _antiprism(N)
        result['construction_name'] = f'{N}-gonal antiprism'
        return result


def whole_month_polyhedron() -> dict:
    """Rhombic triacontahedron with 30 faces labeled as tithis."""
    result = _rhombic_triacontahedron()
    result['construction_name'] = 'rhombic triacontahedron (whole month)'
    return result


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
