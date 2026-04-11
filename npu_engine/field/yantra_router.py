"""
yantra_router.py — Navagraha Yantra Matrix Engine

Investigates whether the 9 Navagraha 3×3 yantra matrices
(Lo Shu magic square shifted by k for each graha)
have algebraic structure that maps to the toroidal field.

Four tests:
  T1: Eigenvalue verification — all yantra matrices have eigenvalues {M, ±2√6}
  T2: 9×9 graha distance matrix from toroid — test for magic properties
  T3: Yantra matrix-vector multiply vs toroidal distance — entity ranking comparison
  T4: NPU timing — matrix operations vs toroidal geodesic
"""

import math
import time
import numpy as np
from typing import Dict, List, Tuple

# ── Lo Shu base magic square ──
LO_SHU = np.array([
    [2, 7, 6],
    [9, 5, 1],
    [4, 3, 8]
], dtype=np.float64)

# ── 9 Grahas with traditional offsets k ──
# The Navagraha yantra for graha k = Lo Shu + k*J
# where J is the 3×3 all-ones matrix.
# This shifts the magic constant from 15 to 15 + 3k.
GRAHA_K = {
    'Sun':     0,   # Surya — Lo Shu itself
    'Moon':    1,   # Chandra
    'Mars':    2,   # Mangala
    'Mercury': 3,   # Budha
    'Jupiter': 4,   # Guru
    'Venus':   5,   # Shukra
    'Saturn':  6,   # Shani
    'Rahu':    7,   # Ascending node
    'Ketu':    8,   # Descending node
}

GRAHA_ENTITY_IDS = {
    'Sun':     'graha_surya',
    'Moon':    'graha_chandra',
    'Mars':    'graha_mangal',
    'Mercury': 'graha_budha',
    'Jupiter': 'graha_guru',
    'Venus':   'graha_shukra',
    'Saturn':  'graha_shani',
    'Rahu':    'graha_rahu',
    'Ketu':    'graha_ketu',
}

VASTU_DIRECTIONS = [
    'vastu_se', 'vastu_s', 'vastu_sw',
    'vastu_e',  'vastu_c', 'vastu_w',
    'vastu_ne', 'vastu_n', 'vastu_nw',
]

J = np.ones((3, 3), dtype=np.float64)
SQRT6_2 = 2 * math.sqrt(6)


def build_graha_yantra(k: int) -> np.ndarray:
    """Build 3×3 yantra matrix for graha with offset k."""
    return LO_SHU + k * J


def test_eigenvalues():
    """T1: Verify all 9 yantra matrices have eigenvalues {M, ±2√6}.

    For Lo Shu + k*J:
      eigenvalue 1 = 15 + 3k (magic constant = sum of any row)
      eigenvalue 2 = +2√6 ≈ +4.899
      eigenvalue 3 = -2√6 ≈ -4.899

    The ±2√6 eigenvalues are INVARIANT across all k.
    Only the magic constant shifts.
    """
    results = []
    all_pass = True

    for graha, k in GRAHA_K.items():
        Y = build_graha_yantra(k)
        evals = np.sort(np.real(np.linalg.eigvals(Y)))  # general matrix eigenvalues
        M = 15 + 3 * k  # predicted magic constant

        # Check eigenvalues
        predicted = sorted([-SQRT6_2, SQRT6_2, M])
        actual = sorted(evals)
        errors = [abs(a - p) for a, p in zip(actual, predicted)]
        max_err = max(errors)
        passed = max_err < 1e-10

        if not passed:
            all_pass = False

        results.append({
            'graha': graha,
            'k': k,
            'magic_constant': M,
            'eigenvalues_actual': [round(e, 6) for e in actual],
            'eigenvalues_predicted': [round(e, 6) for e in predicted],
            'max_error': max_err,
            'pass': passed,
        })

    return {
        'test': 'T1_eigenvalue_verification',
        'all_pass': all_pass,
        'invariant_eigenvalues': f'±2√6 = ±{SQRT6_2:.6f}',
        'results': results,
    }


def test_distance_matrix():
    """T2: Build 9×9 graha distance matrix from toroid.

    Extract theta/phi for all 9 grahas from the toroidal field.
    Build pairwise distance matrix.
    Test if row/column sums satisfy any magic-like conditions.
    """
    try:
        from npu_engine.toroidal_field import ToroidalField
        field = ToroidalField()
    except Exception as e:
        return {'test': 'T2_distance_matrix', 'error': str(e)}

    grahas = list(GRAHA_ENTITY_IDS.values())
    n = len(grahas)

    # Extract coordinates
    coords = []
    found = []
    for eid in grahas:
        if eid in field.entities:
            theta, phi = field.entities[eid]
            coords.append((theta, phi))
            found.append(eid)
        else:
            coords.append((0, 0))
            found.append(eid + ' (missing)')

    # Build distance matrix
    from npu_engine.toroidal_field import toroidal_distance
    D = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            D[i, j] = toroidal_distance(
                coords[i][0], coords[i][1],
                coords[j][0], coords[j][1]
            )

    # Test magic properties
    row_sums = D.sum(axis=1)
    col_sums = D.sum(axis=0)
    diag_sum = np.trace(D)
    anti_diag_sum = np.trace(np.fliplr(D))

    row_variance = np.var(row_sums)
    col_variance = np.var(col_sums)
    is_magic_like = row_variance < 0.1 * np.mean(row_sums)**2

    # Eigenvalues of distance matrix
    D_evals = np.sort(np.real(np.linalg.eigvals(D)))

    return {
        'test': 'T2_distance_matrix',
        'graha_entities': found,
        'graha_coords': [(round(t, 4), round(p, 4)) for t, p in coords],
        'row_sums': [round(s, 4) for s in row_sums],
        'row_sum_variance': round(float(row_variance), 6),
        'col_sum_variance': round(float(col_variance), 6),
        'diag_sum': round(float(diag_sum), 4),
        'anti_diag_sum': round(float(anti_diag_sum), 4),
        'magic_like': is_magic_like,
        'distance_matrix_eigenvalues': [round(float(e), 4) for e in D_evals],
        'mean_row_sum': round(float(np.mean(row_sums)), 4),
    }


def test_eigenvector_vastu():
    """T1 extended: Map Lo Shu eigenvectors to 9 vastu directional entities.

    Compare eigenvector clustering to toroidal coherence
    between vastu entities.
    """
    evals, evecs = np.linalg.eig(LO_SHU)
    evals = np.real(evals); evecs = np.real(evecs)
    # evecs columns are eigenvectors
    # Flatten each 3×3 eigenvector component to map to 9 directions

    try:
        from npu_engine.toroidal_field import ToroidalField, toroidal_distance
        field = ToroidalField()
    except Exception as e:
        return {'test': 'T1_eigenvector_vastu', 'error': str(e)}

    # Get vastu entity positions
    vastu_coords = []
    vastu_found = []
    for vid in VASTU_DIRECTIONS:
        if vid in field.entities:
            vastu_coords.append(field.entities[vid])
            vastu_found.append(vid)
        else:
            vastu_coords.append((0, 0))
            vastu_found.append(vid + ' (missing)')

    # Lo Shu values → position indices (value 1-9 maps to Lo Shu cell)
    lo_shu_flat = LO_SHU.flatten()  # [2,7,6,9,5,1,4,3,8]

    # Eigenvector components map to these 9 cells
    ev_data = []
    for i in range(3):
        ev = evecs[:, i]  # eigenvector i (3-component)
        # Outer product gives 3×3 contribution
        contribution = np.outer(ev, ev).flatten()
        ev_data.append({
            'eigenvalue': round(float(evals[i]), 6),
            'eigenvector': [round(float(v), 6) for v in ev],
            'directional_weights': [round(float(c), 6) for c in contribution],
        })

    return {
        'test': 'T1_eigenvector_vastu',
        'lo_shu_to_vastu': dict(zip(
            [f'cell_{i}={int(v)}' for i, v in enumerate(lo_shu_flat)],
            VASTU_DIRECTIONS
        )),
        'vastu_entities': vastu_found,
        'eigenvectors': ev_data,
    }


def test_ranking_comparison():
    """T3: For current vara graha, compare yantra matrix-vector multiply
    vs toroidal distance ranking of top-5 entities."""

    try:
        from npu_engine.toroidal_field import ToroidalField
        field = ToroidalField()
    except Exception as e:
        return {'test': 'T3_ranking_comparison', 'error': str(e)}

    # Use Saturn (current vara) as test graha
    test_graha = 'Saturn'
    k = GRAHA_K[test_graha]
    Y = build_graha_yantra(k)
    graha_eid = GRAHA_ENTITY_IDS[test_graha]

    if graha_eid not in field.entities:
        return {'test': 'T3_ranking_comparison', 'error': f'{graha_eid} not in field'}

    # Toroidal ranking: top-5 entities by coherence with Saturn
    theta_g, phi_g = field.entities[graha_eid]
    n = len(field.entity_ids)
    d_theta = np.pi - np.abs(np.abs(field.entity_theta - theta_g) - np.pi)
    d_phi = np.pi - np.abs(np.abs(field.entity_phi - phi_g) - np.pi)
    arc_theta = d_theta * (field.R + field.r)
    arc_phi = d_phi * field.r
    distances = np.sqrt(arc_theta**2 + arc_phi**2)
    coherences = (np.cos(distances / field.max_dist * np.pi) + 1) / 2
    toroid_top_idx = np.argsort(-coherences)[:10]
    toroid_top = [(field.entity_ids[i], round(float(coherences[i]), 4)) for i in toroid_top_idx]

    # Yantra ranking: multiply Y by a 3-vector representing the graha
    # Use the graha's row in Lo Shu as input vector
    graha_row_idx = list(GRAHA_K.keys()).index(test_graha) % 3
    input_vec = Y[graha_row_idx]
    output_vec = Y @ input_vec  # matrix-vector multiply
    yantra_response = {
        'input_vector': [round(float(v), 2) for v in input_vec],
        'output_vector': [round(float(v), 2) for v in output_vec],
        'output_magnitude': round(float(np.linalg.norm(output_vec)), 4),
    }

    return {
        'test': 'T3_ranking_comparison',
        'graha': test_graha,
        'graha_k': k,
        'yantra_magic_constant': 15 + 3 * k,
        'toroid_top_5': toroid_top[:5],
        'yantra_matrix_response': yantra_response,
        'note': 'Yantra operates in 3D algebraic space; toroid in geometric space. Direct entity ranking comparison requires mapping between these spaces.',
    }


def test_npu_timing():
    """T4: Time both operations on NPU. Report speedup."""
    try:
        from npu_engine.toroidal_field import ToroidalField
        field = ToroidalField()
    except Exception as e:
        return {'test': 'T4_npu_timing', 'error': str(e)}

    n = len(field.entity_ids)
    theta_g = field.entity_theta[0]
    phi_g = field.entity_phi[0]
    iterations = 100

    # Toroidal distance (numpy batch)
    t0 = time.perf_counter()
    for _ in range(iterations):
        d_theta = np.pi - np.abs(np.abs(field.entity_theta - theta_g) - np.pi)
        d_phi = np.pi - np.abs(np.abs(field.entity_phi - phi_g) - np.pi)
        arc_theta = d_theta * (field.R + field.r)
        arc_phi = d_phi * field.r
        distances = np.sqrt(arc_theta**2 + arc_phi**2)
        scores = (np.cos(distances / field.max_dist * np.pi) + 1) / 2
    t_toroid = (time.perf_counter() - t0) / iterations

    # Yantra matrix multiply (all 9)
    yantras = [build_graha_yantra(k) for k in range(9)]
    input_vecs = [Y[0] for Y in yantras]
    t0 = time.perf_counter()
    for _ in range(iterations):
        for Y, v in zip(yantras, input_vecs):
            result = Y @ v
    t_yantra = (time.perf_counter() - t0) / iterations

    return {
        'test': 'T4_npu_timing',
        'entities': n,
        'iterations': iterations,
        'toroidal_distance_ms': round(t_toroid * 1000, 3),
        'yantra_matmul_ms': round(t_yantra * 1000, 3),
        'speedup': round(t_toroid / max(t_yantra, 1e-9), 2),
        'note': f'Toroid: {n} entities × geodesic. Yantra: 9 × 3×3 matmul. Not directly comparable — different operations.',
    }


def run_all_tests() -> dict:
    """Run all 4 tests and return combined results."""
    return {
        'T1_eigenvalues': test_eigenvalues(),
        'T1_eigenvector_vastu': test_eigenvector_vastu(),
        'T2_distance_matrix': test_distance_matrix(),
        'T3_ranking_comparison': test_ranking_comparison(),
        'T4_npu_timing': test_npu_timing(),
    }


def write_results(output_path: str = None):
    """Run all tests and write results to markdown."""
    import json
    from pathlib import Path

    if output_path is None:
        output_path = str(Path(__file__).resolve().parent.parent.parent / "research" / "yantra_npu_results.md")

    results = run_all_tests()

    with open(output_path, 'w') as f:
        f.write("# Yantra–NPU Router Results\n\n")
        f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M')}\n\n")

        # T1: Eigenvalues
        t1 = results['T1_eigenvalues']
        f.write("## T1: Navagraha Yantra Eigenvalue Verification\n\n")
        f.write(f"All pass: **{t1['all_pass']}**\n")
        f.write(f"Invariant eigenvalues: {t1['invariant_eigenvalues']}\n\n")
        f.write("| Graha | k | Magic Constant | Eigenvalues | Error | Pass |\n")
        f.write("|-------|---|----------------|-------------|-------|------|\n")
        for r in t1['results']:
            evals_str = ', '.join(f'{e:.4f}' for e in r['eigenvalues_actual'])
            f.write(f"| {r['graha']} | {r['k']} | {r['magic_constant']} | {evals_str} | {r['max_error']:.2e} | {'✓' if r['pass'] else '✗'} |\n")

        # T1 ext: Eigenvector vastu
        t1v = results['T1_eigenvector_vastu']
        f.write(f"\n## T1 Extended: Eigenvector → Vastu Mapping\n\n")
        if 'error' not in t1v:
            f.write("Lo Shu cell → Vastu direction mapping:\n\n")
            for cell, direction in t1v.get('lo_shu_to_vastu', {}).items():
                f.write(f"- {cell} → {direction}\n")
            f.write("\nEigenvectors:\n\n")
            for ev in t1v.get('eigenvectors', []):
                f.write(f"- λ={ev['eigenvalue']}: {ev['eigenvector']}\n")
        else:
            f.write(f"Error: {t1v['error']}\n")

        # T2: Distance matrix
        t2 = results['T2_distance_matrix']
        f.write(f"\n## T2: Graha Distance Matrix\n\n")
        if 'error' not in t2:
            f.write(f"Magic-like (equal row sums): **{t2['magic_like']}**\n")
            f.write(f"Row sum variance: {t2['row_sum_variance']}\n")
            f.write(f"Mean row sum: {t2['mean_row_sum']}\n")
            f.write(f"Distance matrix eigenvalues: {t2['distance_matrix_eigenvalues']}\n\n")
            f.write("Graha coordinates on toroid:\n\n")
            for eid, (t, p) in zip(t2['graha_entities'], t2['graha_coords']):
                f.write(f"- {eid}: θ={t}, φ={p}\n")
        else:
            f.write(f"Error: {t2['error']}\n")

        # T3: Ranking comparison
        t3 = results['T3_ranking_comparison']
        f.write(f"\n## T3: Ranking Comparison (Saturn)\n\n")
        if 'error' not in t3:
            f.write(f"Graha: {t3['graha']} (k={t3['graha_k']}, M={t3['yantra_magic_constant']})\n\n")
            f.write("Toroid top-5 entities by coherence:\n\n")
            for eid, score in t3['toroid_top_5']:
                f.write(f"- {eid}: {score}\n")
            f.write(f"\nYantra response: {t3['yantra_matrix_response']}\n")
            f.write(f"\n{t3['note']}\n")
        else:
            f.write(f"Error: {t3['error']}\n")

        # T4: Timing
        t4 = results['T4_npu_timing']
        f.write(f"\n## T4: NPU Timing\n\n")
        if 'error' not in t4:
            f.write(f"- Entities: {t4['entities']}\n")
            f.write(f"- Toroidal distance: {t4['toroidal_distance_ms']}ms\n")
            f.write(f"- Yantra matmul (9×): {t4['yantra_matmul_ms']}ms\n")
            f.write(f"- Ratio: {t4['speedup']}×\n")
            f.write(f"- {t4['note']}\n")
        else:
            f.write(f"Error: {t4['error']}\n")

    print(f"✦ Results written to {output_path}")
    return results


if __name__ == '__main__':
    write_results()
