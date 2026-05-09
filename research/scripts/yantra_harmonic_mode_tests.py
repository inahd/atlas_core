"""
yantra_harmonic_mode_tests.py — Hypothesis tests for Sri Yantra substrate claim.

Hypothesis: The 15 Nityā yantras are harmonic-mode views of one underlying
Sri Yantra substrate, rather than 15 separate yantras.

TEST 1 — Petal-count prediction:
  For each tithi 1-15, generate the cut_and_project field at that tithi's
  DEVI_N. Compute angular FFT (polar resample with spline interpolation +
  1D FFT over angle, averaged over radii). Extract top-3 dominant N-fold
  modes. Compare to traditional petal counts from nitya_yantra_geometry.csv.

TEST 2 — Superposition reconstruction:
  Compute sum over all 15 tithis of project_nfold(DEVI_N[i], phase_i).
  Compare to a synthetic 9-triangle Sri Yantra reference (constructive — no
  canonical raster of "the Sri Yantra" exists). Report Pearson correlation
  + region count.

TEST 3 — Substrate mode-dominance verification:
  Compute the substrate (sum of 15 fields). Run angular FFT on the substrate.
  Check: do the N values present in DEVI_N (with their multiplicities) show
  up as peaks in the substrate spectrum? This tests whether the substrate
  decomposes into the assumed N-fold components.

All numerical outputs are written to research/yantra_harmonic_mode_results.json
for downstream consumption by the writeup.
"""

import csv
import json
import os
import sys
import numpy as np
from collections import Counter
from scipy.fft import fft
from scipy.ndimage import label, map_coordinates, maximum_filter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from npu_engine.geometry.cut_and_project import (
    project_nfold,
    project_sri_yantra,
)


# ── Reference data ─────────────────────────────────────────────

DEVI_N = {1: 3, 2: 6, 3: 3, 4: 3, 5: 8, 6: 6, 7: 7, 8: 8,
          9: 9, 10: 10, 11: 11, 12: 12, 13: 13, 14: 14, 15: 15}


def load_traditional_petals():
    """Read petal_count from nitya_yantra_geometry.csv."""
    path = os.path.join(ROOT, "datasets", "cosmology", "nitya_yantra_geometry.csv")
    petals = {}
    with open(path) as f:
        for row in csv.DictReader(f):
            try:
                t = int(row["tithi_number"])
                p = int(row["petal_count"])
                petals[t] = p
            except (ValueError, KeyError, TypeError):
                continue
    return petals


# ── Angular FFT (polar slice → 1D FFT over angle) ─────────────

def angular_power_spectrum(field, n_angles=720, n_radii=40,
                           r_inner_frac=0.30, r_outer_frac=0.90,
                           interp_order=3):
    """
    Resample field on concentric rings using SPLINE INTERPOLATION,
    take 1D FFT around each ring, average power across rings.
    Returns power[k] for k in 0..n_angles//2.

    A k-fold symmetric pattern shows up as a power spike at k.
    Spline interpolation (order=3) is critical to avoid pixel-grid
    aliasing artifacts.
    """
    h, w = field.shape
    cy, cx = h / 2.0, w / 2.0
    rmax = min(cy, cx)
    radii = np.linspace(rmax * r_inner_frac, rmax * r_outer_frac, n_radii)
    angles = np.linspace(0, 2 * np.pi, n_angles, endpoint=False)

    cos_a = np.cos(angles)
    sin_a = np.sin(angles)

    powers = np.zeros(n_angles // 2)
    for r in radii:
        ys = cy + r * sin_a
        xs = cx + r * cos_a
        coords = np.vstack([ys, xs])
        ring = map_coordinates(field, coords, order=interp_order, mode="reflect")
        # Remove DC offset of the ring before FFT so we measure modulation only
        ring = ring - ring.mean()
        spec = np.abs(fft(ring))[: n_angles // 2]
        powers += spec
    return powers / n_radii


def top_modes(power, top_k=8, exclude_dc=True, max_k=40):
    """Return top-k modes by power, restricted to k <= max_k."""
    p = power.copy()
    if exclude_dc:
        p[0] = 0
    p = p[: max_k + 1]
    order = np.argsort(p)[::-1][:top_k]
    return [(int(k), float(p[k])) for k in order]


# ── Synthetic Sri Yantra reference (9 interlocking triangles) ─

def synthetic_sri_yantra(size=512, R_frac=0.45):
    """
    Synthetic Sri Yantra reference: union of 9 interlocking triangles
    (4 upward Shiva, 5 downward Shakti) inscribed in a circle.

    NB: The exact triangle scales of "the" Sri Yantra are not canonically
    fixed (different traditions use different proportions, and constructing
    9 triangles with all 24 intersections coincident is mathematically
    over-constrained). Scales here are a reasonable approximation.
    """
    field = np.zeros((size, size), dtype=np.float64)
    cx = cy = size / 2
    R = size * R_frac

    shiva_scales = [1.00, 0.78, 0.56, 0.34]      # upward
    shakti_scales = [0.95, 0.72, 0.50, 0.28, 0.10]  # downward

    yy, xx = np.indices((size, size))
    px = xx - cx
    py = -(yy - cy)

    def triangle_mask(s, polarity):
        h_tri = s * R
        if polarity == "up":
            top_y = h_tri
            base_y = -h_tri / 2
            cond_base = py >= base_y
            cond_left = py <= top_y - (top_y - base_y) * (-px) / (h_tri / np.sqrt(3))
            cond_right = py <= top_y - (top_y - base_y) * (px) / (h_tri / np.sqrt(3))
        else:
            top_y = -h_tri
            base_y = h_tri / 2
            cond_base = py <= base_y
            cond_left = py >= top_y + (base_y - top_y) * (-px) / (h_tri / np.sqrt(3))
            cond_right = py >= top_y + (base_y - top_y) * (px) / (h_tri / np.sqrt(3))
        return cond_base & cond_left & cond_right

    for s in shiva_scales:
        field = np.maximum(field, triangle_mask(s, "up").astype(np.float64))
    for s in shakti_scales:
        field = np.maximum(field, triangle_mask(s, "down").astype(np.float64))

    return field


# ── Region counting ────────────────────────────────────────────

def count_local_maxima(field, neighborhood=5, min_separation=4):
    """Count local maxima in field (proxy for 'enclosed bright regions')."""
    f = field.astype(np.float64)
    nbh = maximum_filter(f, size=neighborhood)
    is_max = (f == nbh) & (f > f.mean() + 0.5 * f.std())
    n = int(np.sum(is_max))
    return n


def count_threshold_components(field, threshold=0.5):
    """Connected components above threshold."""
    binary = (field > threshold).astype(np.int8)
    _, n_above = label(binary)
    binary_below = (field <= threshold).astype(np.int8)
    _, n_below = label(binary_below)
    return {"above": int(n_above), "below": int(n_below)}


# ── Pearson correlation ────────────────────────────────────────

def pearson(a, b):
    a = a.flatten() - a.mean()
    b = b.flatten() - b.mean()
    denom = np.sqrt((a * a).sum() * (b * b).sum())
    if denom == 0:
        return 0.0
    return float((a * b).sum() / denom)


# ──────────────────────────────────────────────────────────────
# RUN TESTS
# ──────────────────────────────────────────────────────────────

def run_test_1_petal_prediction(size=512, k=5.0):
    """
    For each tithi, generate project_nfold field at DEVI_N[tithi].
    Compute angular FFT. Report top modes. Compare to traditional petal count.

    Spatial frequency k=5.0 chosen so the field has multiple oscillations
    within the disk, making N-fold harmonics genuinely visible in the FFT.
    """
    petals = load_traditional_petals()
    results = {}

    for tithi in range(1, 16):
        N = DEVI_N[tithi]
        phase = 2 * np.pi * (tithi - 1) / 15
        field = project_nfold(N, phase=phase, k=k, size=size)

        power = angular_power_spectrum(field)
        top = top_modes(power, top_k=10, max_k=40)

        traditional = petals.get(tithi, None)
        top_3 = [m for m, _ in top[:3]]
        top_8 = [m for m, _ in top[:8]]

        # Match: traditional petal in any of top 3 (or top 8 — we report both)
        # Also check if N is in top, and if top mode is integer-multiple of N
        def is_harmonic_of_N(m, N):
            if N == 0:
                return False
            return m % N == 0 or (m * 2) % N == 0  # k or 2k multiples

        n_harmonics_in_top3 = sum(1 for m in top_3 if is_harmonic_of_N(m, N))
        n_harmonics_in_top8 = sum(1 for m in top_8 if is_harmonic_of_N(m, N))

        results[tithi] = {
            "tithi": tithi,
            "DEVI_N": N,
            "traditional_petals": traditional,
            "predicted_top3_modes": top_3,
            "predicted_top8_modes": top_8,
            "top3_powers": [round(p, 3) for _, p in top[:3]],
            "top1_mode": top_3[0] if top_3 else None,
            "petal_in_top3": traditional in top_3 if traditional else None,
            "petal_in_top8": traditional in top_8 if traditional else None,
            "n_DEVI_N_harmonics_in_top3": n_harmonics_in_top3,
            "n_DEVI_N_harmonics_in_top8": n_harmonics_in_top8,
        }
    return results


def run_test_2_superposition(size=512, k=5.0):
    """
    Compute composite = sum of 15 N-fold fields.
    Compare to: synthetic 9-triangle Sri Yantra reference.
    Also compare composite to project_sri_yantra (note: that function is
    itself a similar superposition — listed for reference, not as
    independent validation).
    """
    composite = np.zeros((size, size), dtype=np.float64)
    for tithi in range(1, 16):
        N = DEVI_N[tithi]
        phase = 2 * np.pi * (tithi - 1) / 15
        layer = project_nfold(N, phase=phase, k=k, size=size)
        composite += layer

    # Normalize
    cmin, cmax = composite.min(), composite.max()
    composite_norm = (composite - cmin) / (cmax - cmin) if cmax > cmin else composite

    # Reference: project_sri_yantra (in code default k=1.0; here at same k for fairness)
    ref_internal = project_sri_yantra(k=k, size=size)
    # And synthetic 9-triangle reference
    ref_triangle = synthetic_sri_yantra(size=size)

    corr_internal = pearson(composite_norm, ref_internal)
    corr_triangle = pearson(composite_norm, ref_triangle)

    # Region counts
    composite_thresh = count_threshold_components(composite_norm, threshold=0.5)
    composite_maxima = count_local_maxima(composite_norm)
    triangle_thresh = count_threshold_components(ref_triangle, threshold=0.5)
    triangle_maxima = count_local_maxima(ref_triangle)
    internal_thresh = count_threshold_components(ref_internal, threshold=0.5)

    # Angular FFT of the composite
    composite_power = angular_power_spectrum(composite_norm)
    composite_top = top_modes(composite_power, top_k=15, max_k=40)

    # Predict: which N values from DEVI_N appear in top modes?
    devi_N_set = set(DEVI_N.values())  # {3, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15}
    top_modes_set = set(m for m, _ in composite_top[:15])
    devi_N_in_top = sorted(devi_N_set & top_modes_set)

    return {
        "composite_shape": list(composite_norm.shape),
        "spatial_frequency_k": k,
        "pearson_vs_project_sri_yantra": round(corr_internal, 4),
        "pearson_vs_synthetic_9triangle": round(corr_triangle, 4),
        "composite_region_count_threshold": composite_thresh,
        "composite_local_maxima": composite_maxima,
        "synthetic_9triangle_region_count_threshold": triangle_thresh,
        "synthetic_9triangle_local_maxima": triangle_maxima,
        "project_sri_yantra_region_count_threshold": internal_thresh,
        "sri_yantra_canonical_region_count": 44,
        "composite_top15_modes": [(m, round(p, 3)) for m, p in composite_top],
        "DEVI_N_values_in_top15": devi_N_in_top,
        "DEVI_N_unique_values": sorted(devi_N_set),
        "alignment_assessment": {
            "vs_project_sri_yantra_note": (
                "project_sri_yantra is itself a sum-of-15 multigrid superposition; "
                "high correlation here reflects implementation alignment, not "
                "independent validation of the substrate hypothesis."),
            "vs_synthetic_9triangle": (
                "high (>0.85)" if corr_triangle > 0.85 else
                "moderate (0.5-0.85)" if corr_triangle > 0.5 else
                "low (<0.5)"),
        },
    }


def run_test_3_substrate_dominance(size=512, k=5.0):
    """
    Generate the substrate (sum of 15 fields). Compute angular FFT of the
    full substrate. Report which N values from DEVI_N appear as peaks in
    the substrate spectrum.

    This tests: does the substrate empirically decompose into the assumed
    N-fold components? If a DEVI_N value does NOT appear as a peak, that
    component is not detectable in the superposition.

    Also reports per-tithi: for project_nfold(DEVI_N[i]), is the dominant
    measured mode equal to (or a harmonic of) DEVI_N[i]? This is a sanity
    check on the FFT methodology.
    """
    # Build substrate
    substrate = np.zeros((size, size), dtype=np.float64)
    for tithi in range(1, 16):
        N = DEVI_N[tithi]
        phase = 2 * np.pi * (tithi - 1) / 15
        layer = project_nfold(N, phase=phase, k=k, size=size)
        substrate += layer

    s_min, s_max = substrate.min(), substrate.max()
    substrate_norm = (substrate - s_min) / (s_max - s_min) if s_max > s_min else substrate

    # FFT of substrate
    sub_power = angular_power_spectrum(substrate_norm)
    sub_top = top_modes(sub_power, top_k=20, max_k=40)
    sub_top_set = set(m for m, _ in sub_top)

    # Multiplicity table: how many tithis have each N
    devi_N_counts = Counter(DEVI_N.values())

    # For each unique DEVI_N, is it in the substrate's top-20 modes?
    detection = {}
    for N_val, count in sorted(devi_N_counts.items()):
        in_top = N_val in sub_top_set
        rank = None
        power_val = None
        for i, (m, p) in enumerate(sub_top):
            if m == N_val:
                rank = i + 1
                power_val = round(p, 3)
                break
        detection[N_val] = {
            "multiplicity_in_DEVI_N": count,
            "appears_in_substrate_top20": in_top,
            "rank_in_substrate_top20": rank,
            "power": power_val,
            "tithis_with_this_N": [t for t, n in DEVI_N.items() if n == N_val],
        }

    # Per-tithi sanity check: is project_nfold(N)'s dominant mode =N (or 2N)?
    per_tithi = {}
    for tithi in range(1, 16):
        N = DEVI_N[tithi]
        phase = 2 * np.pi * (tithi - 1) / 15
        field = project_nfold(N, phase=phase, k=k, size=size)
        power = angular_power_spectrum(field)
        top = top_modes(power, top_k=8, max_k=40)
        top_modes_list = [m for m, _ in top]
        N_dominant = top_modes_list[0]
        # Is N or harmonic of N in top 3?
        top3 = top_modes_list[:3]
        N_in_top3 = N in top3
        harmonic_in_top3 = any((m % N == 0) and m > 0 for m in top3) if N > 0 else False
        per_tithi[tithi] = {
            "N_assumed": N,
            "N_dominant_measured": N_dominant,
            "top3_modes": top3,
            "N_or_harmonic_in_top3": bool(N_in_top3 or harmonic_in_top3),
        }

    return {
        "spatial_frequency_k": k,
        "substrate_top20_modes": [(m, round(p, 3)) for m, p in sub_top],
        "DEVI_N_detection_in_substrate": detection,
        "per_tithi_dominance_check": per_tithi,
        "DEVI_N_values_detected_in_substrate": sorted(
            N for N, d in detection.items() if d["appears_in_substrate_top20"]),
        "DEVI_N_values_NOT_detected": sorted(
            N for N, d in detection.items() if not d["appears_in_substrate_top20"]),
    }


# ──────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("YANTRA HARMONIC-MODE HYPOTHESIS TESTS")
    print("=" * 70)
    SIZE = 512
    K = 5.0

    print(f"\nField size: {SIZE}x{SIZE}, spatial frequency k={K}")

    print("\n[TEST 1] Petal-count prediction via angular FFT")
    print("-" * 70)
    test1 = run_test_1_petal_prediction(size=SIZE, k=K)
    matches_top3 = sum(1 for v in test1.values() if v["petal_in_top3"])
    matches_top8 = sum(1 for v in test1.values() if v["petal_in_top8"])
    devi_n_harmonics = sum(1 for v in test1.values() if v["n_DEVI_N_harmonics_in_top3"] >= 1)
    print(f"  Tithis with traditional petal count in top-3 modes: {matches_top3}/15")
    print(f"  Tithis with traditional petal count in top-8 modes: {matches_top8}/15")
    print(f"  Tithis with at least 1 DEVI_N-harmonic in top-3:    {devi_n_harmonics}/15")
    print()
    for t in range(1, 16):
        v = test1[t]
        flag = "✓" if v["petal_in_top3"] else ("?" if v["petal_in_top8"] else "✗")
        print(f"  T{t:2d}  N={v['DEVI_N']:2d}  petals={v['traditional_petals']:>3}  "
              f"top3={str(v['predicted_top3_modes']):<14}  {flag}")

    print("\n[TEST 2] Superposition reconstruction")
    print("-" * 70)
    test2 = run_test_2_superposition(size=SIZE, k=K)
    print(f"  Pearson(composite, project_sri_yantra)    = {test2['pearson_vs_project_sri_yantra']}")
    print(f"  Pearson(composite, synthetic_9triangle)   = {test2['pearson_vs_synthetic_9triangle']}")
    print(f"  Composite local maxima:               {test2['composite_local_maxima']}")
    print(f"  Synthetic 9-triangle local maxima:    {test2['synthetic_9triangle_local_maxima']}")
    print(f"  Sri Yantra canonical region count:    44 (43 sub-triangles + bindu)")
    print(f"  Composite top-5 angular modes: {test2['composite_top15_modes'][:5]}")
    print(f"  DEVI_N unique values: {test2['DEVI_N_unique_values']}")
    print(f"  DEVI_N in composite top-15: {test2['DEVI_N_values_in_top15']}")

    print("\n[TEST 3] Substrate mode-dominance verification")
    print("-" * 70)
    test3 = run_test_3_substrate_dominance(size=SIZE, k=K)
    detected = test3["DEVI_N_values_detected_in_substrate"]
    not_detected = test3["DEVI_N_values_NOT_detected"]
    print(f"  DEVI_N values detected in substrate: {detected}")
    print(f"  DEVI_N values NOT detected:          {not_detected}")
    print(f"  Substrate top-10 modes: {test3['substrate_top20_modes'][:10]}")
    print()
    print("  Per-N detection:")
    for N_val, info in sorted(test3["DEVI_N_detection_in_substrate"].items()):
        flag = "✓" if info["appears_in_substrate_top20"] else "✗"
        print(f"    N={N_val:2d} (×{info['multiplicity_in_DEVI_N']})  "
              f"rank={info['rank_in_substrate_top20']}  "
              f"power={info['power']}  {flag}")
    print()
    print("  Per-tithi sanity (does project_nfold(N) show N or harmonic in top-3?):")
    sanity_pass = sum(1 for v in test3["per_tithi_dominance_check"].values()
                      if v["N_or_harmonic_in_top3"])
    print(f"  Pass: {sanity_pass}/15")
    for t in range(1, 16):
        v = test3["per_tithi_dominance_check"][t]
        flag = "✓" if v["N_or_harmonic_in_top3"] else "✗"
        print(f"    T{t:2d}  N={v['N_assumed']:2d}  measured-top1={v['N_dominant_measured']}  "
              f"top3={v['top3_modes']}  {flag}")

    out = {
        "size": SIZE,
        "spatial_frequency_k": K,
        "test_1_petal_prediction": test1,
        "test_2_superposition": test2,
        "test_3_substrate_dominance": test3,
        "summary": {
            "test1_petals_in_top3": f"{matches_top3}/15",
            "test1_petals_in_top8": f"{matches_top8}/15",
            "test2_pearson_synthetic_sri_yantra": test2["pearson_vs_synthetic_9triangle"],
            "test3_DEVI_N_detected": detected,
            "test3_DEVI_N_not_detected": not_detected,
            "test3_per_tithi_sanity_pass": f"{sanity_pass}/15",
        },
    }
    out_path = os.path.join(ROOT, "research", "yantra_harmonic_mode_results.json")
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nResults written to: {out_path}")
    return out


if __name__ == "__main__":
    main()
