# Yantra Eigenvalue Exploration

**RESEARCH-016** | April 12, 2026 | Pratah-lila | Guru hora

## Current Field Yantra (Guru, k=4)

```
 6  11  10
13   9   5
 8   7  12
```

**Magic constant M = 27** | Eigenvalues: {27, +4.899, -4.899}

## Finding 1: Eigenvalue Invariance

Every 3x3 graha yantra = Lo Shu + k*J has exactly 3 eigenvalues:

| Eigenvalue | Value | Varies? |
|-----------|-------|---------|
| lambda_1 | M = 15 + 3k | Yes (per graha) |
| lambda_2 | +2sqrt(6) = +4.8990 | **No** (invariant) |
| lambda_3 | -2sqrt(6) = -4.8990 | **No** (invariant) |

The +/-2sqrt(6) is a **universal constant of the Lo Shu**. It does not depend
on which graha is active. It is the irreducible spatial asymmetry of the
Vastu Purusha Mandala.

**Proof**: Adding k*J to any matrix shifts only the eigenvalue corresponding
to the all-ones eigenvector. The orthogonal complement is unchanged.
Since Lo Shu's eigenvectors are: uniform (for M), and two orthogonal vectors
(for +/-2sqrt(6)), adding k*J shifts only lambda_1 by 3k.

## Finding 2: Graha Spectral Table

| Graha | k | M | lambda_2/M | Character |
|-------|---|---|-----------|-----------|
| Surya | 0 | 15 | 0.3266 | Most polarized |
| Candra | 1 | 18 | 0.2722 | |
| Mangala | 2 | 21 | 0.2333 | |
| Budha | 3 | 24 | 0.2041 | |
| Guru | 4 | 27 | 0.1814 | |
| Shukra | 5 | 30 | 0.1633 | |
| Shani | 6 | 33 | 0.1485 | |
| Rahu | 7 | 36 | 0.1361 | |
| Ketu | 8 | 39 | 0.1256 | Most coherent |

**Interpretation**: As k increases, M grows while +/-2sqrt(6) stays fixed.
The ratio lambda_2/M decreases — the field becomes more Brahmasthana-like.
Higher grahas produce more spatially uniform fields.

## Finding 3: Kronecker Extension Scaling

| Level | Size | M | Top eigenvalues |
|-------|------|---|----------------|
| 1 | 3x3 | 27 | {27, 4.899, -4.899} |
| 2 | 9x9 | 729 | {729, 132.27, 132.27, 24, 24, ...} |
| 3 | 27x27 | 19683 | {19683, 3571.36, ...} |
| 4 | 81x81 | 531441 | {531441, 96426.61, ...} |

**Scaling law**: M_n = M_1^n (magic constant raised to the level power).

The eigenvalues at level n are ALL PRODUCTS of n base eigenvalues chosen
from {M, +2sqrt(6), -2sqrt(6)}. So for 9x9:

```
M*M = M^2 = 729
M*(+2sqrt6) = +132.27  (multiplicity 2)
M*(-2sqrt6) = -132.27  (multiplicity 2)
(+2sqrt6)^2 = 24       (multiplicity 2)
(-2sqrt6)^2 = 24        (absorbed)
(+2sqrt6)*(-2sqrt6) = -24 (multiplicity 2)
```

**Magic property preserved at ALL levels**: row sums = column sums = M^n.

## Finding 4: The Brahmasthana Theorem

The eigenvector for lambda_1 = M is ALWAYS [1/sqrt(n), ..., 1/sqrt(n)] — uniform.

This means: when the field is projected onto this eigenvector, every Vastu zone
contributes equally. This vector IS the Brahmasthana — not a cell position,
but a **geometric principle**: the state of maximum coherence where all
directions are in balance.

At every Kronecker level, this uniform eigenvector persists. The center
holds at every scale of magnification.

## Finding 5: Navagraha Composite 9x9

Placing each graha's yantra in its Lo Shu position produces a 9x9 matrix
that IS a magic square (row sums = column sums = 81).

**Eigenvalues**: {81, +/-14.697, 0, 0, 0, 0, 0, 0}

Where 14.697 = 3 * 2sqrt(6). The factor of 3 comes from the Lo Shu structure
of the outer placement.

**Rank = 5** (not 9). Four zero eigenvalues mean four degrees of freedom
have collapsed — the composite is more constrained than a general 9x9 magic square.

The block magic constants form **3*Lo_Shu + 12*J** — the meta-structure
is itself a magic-square pattern. The navagraha composite is a
**magic square of magic squares**.

## Finding 6: Eigenvector Cosmology

For Guru (k=4), the eigenvectors define:

**lambda_1 = 27 (Brahmasthana)**: [-0.577, -0.577, -0.577] — uniform.
All zones equal. Maximum coherence.

**lambda_2 = +4.899 (primary tension)**: [-0.075, -0.667, +0.742]
Axis: South row (SE/Agni, S/Yama, SW/Nirrti) vs center row.
The field's dominant spatial polarity.

**lambda_3 = -4.899 (secondary tension)**: [-0.742, +0.667, +0.075]
Axis: North row (NE/Ishana, N/Kubera, NW/Vayu) vs center row.
The field's secondary mode of variation.

The field at any moment is a superposition:
```
field = M * (uniform) + lambda_2 * (NE-SW axis) + lambda_3 * (perpendicular)
```

## Finding 7: Time Series Insight

As the hora cycles through 7 grahas every 7 hours, the lambda_2/M ratio
oscillates between 0.149 (Saturn, most coherent) and 0.327 (Sun, most dynamic).

This is not random variation — it is the **breathing of the Vastu field**.
Sun hora = maximum spatial differentiation = most dynamic field.
Saturn hora = maximum spatial uniformity = most stable field.

The 2sqrt(6) invariant is the **heartbeat** that never changes.
Only the breath (M) varies.
