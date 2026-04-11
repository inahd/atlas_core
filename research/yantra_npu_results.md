# Yantra–NPU Router Results

Generated: 2026-04-11 14:17

## T1: Navagraha Yantra Eigenvalue Verification

All pass: **True**
Invariant eigenvalues: ±2√6 = ±4.898979

| Graha | k | Magic Constant | Eigenvalues | Error | Pass |
|-------|---|----------------|-------------|-------|------|
| Sun | 0 | 15 | -4.8990, 4.8990, 15.0000 | 3.55e-15 | ✓ |
| Moon | 1 | 18 | -4.8990, 4.8990, 18.0000 | 1.07e-14 | ✓ |
| Mars | 2 | 21 | -4.8990, 4.8990, 21.0000 | 7.11e-15 | ✓ |
| Mercury | 3 | 24 | -4.8990, 4.8990, 24.0000 | 1.07e-14 | ✓ |
| Jupiter | 4 | 27 | -4.8990, 4.8990, 27.0000 | 1.42e-14 | ✓ |
| Venus | 5 | 30 | -4.8990, 4.8990, 30.0000 | 3.55e-15 | ✓ |
| Saturn | 6 | 33 | -4.8990, 4.8990, 33.0000 | 7.11e-15 | ✓ |
| Rahu | 7 | 36 | -4.8990, 4.8990, 36.0000 | 3.55e-15 | ✓ |
| Ketu | 8 | 39 | -4.8990, 4.8990, 39.0000 | 1.42e-14 | ✓ |

## T1 Extended: Eigenvector → Vastu Mapping

Lo Shu cell → Vastu direction mapping:

- cell_0=2 → vastu_se
- cell_1=7 → vastu_s
- cell_2=6 → vastu_sw
- cell_3=9 → vastu_e
- cell_4=5 → vastu_c
- cell_5=1 → vastu_w
- cell_6=4 → vastu_ne
- cell_7=3 → vastu_n
- cell_8=8 → vastu_nw

Eigenvectors:

- λ=15.0: [-0.57735, -0.57735, -0.57735]
- λ=-4.898979: [-0.741582, 0.666667, 0.074915]
- λ=4.898979: [-0.074915, -0.666667, 0.741582]

## T2: Graha Distance Matrix

Magic-like (equal row sums): **True**
Row sum variance: 76.05583
Mean row sum: 54.7793
Distance matrix eigenvalues: [-26.2992, -16.6781, -4.4335, -2.9131, -2.235, -1.7166, -0.9651, -0.4832, 55.7237]

Graha coordinates on toroid:

- graha_surya: θ=0.0, φ=2.6568
- graha_chandra: θ=0.8976, φ=0.8639
- graha_mangal (missing): θ=0, φ=0
- graha_budha: θ=2.6928, φ=5.6162
- graha_guru: θ=3.5904, φ=5.2776
- graha_shukra: θ=4.488, φ=1.2728
- graha_shani: θ=5.3856, φ=4.5304
- graha_rahu: θ=1.1636, φ=4.5304
- graha_ketu: θ=0.0, φ=1.7528

## T3: Ranking Comparison (Saturn)

Graha: Saturn (k=6, M=33)

Toroid top-5 entities by coherence:

- graha_shani: 1.0
- ratna_amethyst: 1.0
- ratna_blue_sapphire: 1.0
- bija_aim_hrim: 1.0
- specie_mahisha: 1.0

Yantra response: {'input_vector': [8.0, 13.0, 12.0], 'output_vector': [377.0, 347.0, 365.0], 'output_magnitude': 629.097}

Yantra operates in 3D algebraic space; toroid in geometric space. Direct entity ranking comparison requires mapping between these spaces.

## T4: NPU Timing

- Entities: 16412
- Toroidal distance: 0.228ms
- Yantra matmul (9×): 0.004ms
- Ratio: 55.47×
- Toroid: 16412 entities × geodesic. Yantra: 9 × 3×3 matmul. Not directly comparable — different operations.
