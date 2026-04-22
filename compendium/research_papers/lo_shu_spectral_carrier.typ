#import "../_shared/preamble.typ": compendium-preamble, title-page

#compendium-preamble(
  title: "Lo Shu as Spectral Carrier",
  subtitle: "Coherence Atlas Research Paper",
  version: "1.0 — converted from markdown",
)

#title-page(
  title: "Lo Shu as Spectral Carrier",
  subtitle: "An invariant eigenvalue across all Navagraha yantras",
  volume: "COHERENCE ATLAS · RESEARCH PAPER",
  version: "1.0 · April 2026",
)

// ─── STATUS ──────────────────────────────────────────────────────

#v(0.6in)
#align(center)[#text(size: 11pt, weight: "semibold")[Status]]
#v(0.4em)

_Converted from `research/yantra_eigenvalue_exploration.md` (RESEARCH-016,
April 12 2026, Pratah-lila, Guru hora). Content-lossless conversion; no
claims added or removed._

#pagebreak()

#outline(
  title: [#text(size: 12pt, weight: "semibold")[Contents]],
  indent: 1.8em,
  depth: 2,
)

#pagebreak()

// ═════════════════════════════════════════════════════════════════
//  MAIN CONTENT
// ═════════════════════════════════════════════════════════════════

= Yantra Eigenvalue Exploration

*RESEARCH-016* #h(1em) April 12, 2026 #h(1em) Pratah-lila #h(1em) Guru hora

== Current Field Yantra (Guru, $k = 4$)

#align(center)[
  #raw(block: true, "  6  11  10\n 13   9   5\n  8   7  12")
]

*Magic constant $M = 27$* #h(1em) Eigenvalues: $\{27, +4.899, -4.899\}$

---

== Finding 1: Eigenvalue Invariance

Every $3 times 3$ graha yantra $= L + k bold(J)$ (Lo Shu plus $k$ times the
all-ones matrix) has exactly 3 eigenvalues:

#table(
  columns: (auto, auto, auto),
  align: (left, left, left),
  table.header(
    [*Eigenvalue*], [*Value*], [*Varies?*],
  ),
  [$lambda_1$], [$M = 15 + 3k$], [Yes (per graha)],
  [$lambda_2$], [$+2 sqrt(6) = +4.8990$], [*No* (invariant)],
  [$lambda_3$], [$-2 sqrt(6) = -4.8990$], [*No* (invariant)],
)

The $plus.minus 2 sqrt(6)$ is a *universal constant of the Lo Shu*. It does
not depend on which graha is active. It is the irreducible spatial asymmetry
of the Vastu Purusha Mandala.

*Proof.* Adding $k bold(J)$ to any matrix shifts only the eigenvalue
corresponding to the all-ones eigenvector. The orthogonal complement is
unchanged. Since Lo Shu's eigenvectors are: uniform (for $M$), and two
orthogonal vectors (for $plus.minus 2 sqrt(6)$), adding $k bold(J)$ shifts
only $lambda_1$ by $3k$.

---

== Finding 2: Graha Spectral Table

#table(
  columns: (auto, auto, auto, auto, auto),
  align: (left, right, right, right, left),
  table.header(
    [*Graha*], [*k*], [*M*], [$lambda_2 \/ M$], [*Character*],
  ),
  [Surya],   [0], [15], [0.3266], [Most polarized],
  [Candra],  [1], [18], [0.2722], [],
  [Mangala], [2], [21], [0.2333], [],
  [Budha],   [3], [24], [0.2041], [],
  [Guru],    [4], [27], [0.1814], [],
  [Shukra],  [5], [30], [0.1633], [],
  [Shani],   [6], [33], [0.1485], [],
  [Rahu],    [7], [36], [0.1361], [],
  [Ketu],    [8], [39], [0.1256], [Most coherent],
)

*Interpretation.* As $k$ increases, $M$ grows while $plus.minus 2 sqrt(6)$
stays fixed. The ratio $lambda_2 \/ M$ decreases --- the field becomes more
Brahmasthana-like. Higher grahas produce more spatially uniform fields.

---

== Finding 3: Kronecker Extension Scaling

#table(
  columns: (auto, auto, auto, auto),
  align: (left, left, right, left),
  table.header(
    [*Level*], [*Size*], [*M*], [*Top eigenvalues*],
  ),
  [1], [$3 times 3$],     [27],      [$\{27, 4.899, -4.899\}$],
  [2], [$9 times 9$],     [729],     [$\{729, 132.27, 132.27, 24, 24, ...\}$],
  [3], [$27 times 27$],   [19 683],  [$\{19 683, 3571.36, ...\}$],
  [4], [$81 times 81$],   [531 441], [$\{531 441, 96 426.61, ...\}$],
)

*Scaling law:* $M_n = M_1^n$ (magic constant raised to the level power).

The eigenvalues at level $n$ are *all products* of $n$ base eigenvalues
chosen from $\{M, +2 sqrt(6), -2 sqrt(6)\}$. So for $9 times 9$:

#align(center)[
  #raw(block: true, lang: "text",
"M × M           = M² = 729
M × (+2√6)       = +132.27  (multiplicity 2)
M × (−2√6)       = −132.27  (multiplicity 2)
(+2√6)²          = 24       (multiplicity 2)
(−2√6)²          = 24       (absorbed)
(+2√6) × (−2√6)  = −24      (multiplicity 2)")
]

*Magic property preserved at all levels:* row sums $=$ column sums $= M^n$.

---

== Finding 4: The Brahmasthana Theorem

The eigenvector for $lambda_1 = M$ is always
$[1 \/ sqrt(n), space ..., space 1 \/ sqrt(n)]$ --- uniform.

This means: when the field is projected onto this eigenvector, every Vastu
zone contributes equally. This vector *is* the Brahmasthana --- not a cell
position, but a *geometric principle*: the state of maximum coherence where
all directions are in balance.

At every Kronecker level, this uniform eigenvector persists. The center
holds at every scale of magnification.

---

== Finding 5: Navagraha Composite $9 times 9$

Placing each graha's yantra in its Lo Shu position produces a $9 times 9$
matrix that *is* a magic square (row sums $=$ column sums $= 81$).

*Eigenvalues:* $\{81, plus.minus 14.697, 0, 0, 0, 0, 0, 0\}$

Where $14.697 = 3 times 2 sqrt(6)$. The factor of 3 comes from the Lo Shu
structure of the outer placement.

*Rank $= 5$* (not 9). Four zero eigenvalues mean four degrees of freedom
have collapsed --- the composite is more constrained than a general
$9 times 9$ magic square.

The block magic constants form $3 times L + 12 times bold(J)$ --- the
meta-structure is itself a magic-square pattern. The navagraha composite is a
*magic square of magic squares*.

---

== Finding 6: Eigenvector Cosmology

For Guru ($k = 4$), the eigenvectors define:

*$lambda_1 = 27$ (Brahmasthana):* $[-0.577, -0.577, -0.577]$ --- uniform.
All zones equal. Maximum coherence.

*$lambda_2 = +4.899$ (primary tension):* $[-0.075, -0.667, +0.742]$ \
Axis: South row (SE/Agni, S/Yama, SW/Nirrti) vs center row.
The field's dominant spatial polarity.

*$lambda_3 = -4.899$ (secondary tension):* $[-0.742, +0.667, +0.075]$ \
Axis: North row (NE/Ishana, N/Kubera, NW/Vayu) vs center row.
The field's secondary mode of variation.

The field at any moment is a superposition:

$ "field" = M dot ("uniform") + lambda_2 dot ("NE-SW axis") + lambda_3 dot ("perpendicular") $

---

== Finding 7: Time Series Insight

As the hora cycles through 7 grahas every 7 hours, the $lambda_2 \/ M$ ratio
oscillates between 0.149 (Saturn, most coherent) and 0.327 (Sun, most dynamic).

This is not random variation --- it is the *breathing of the Vastu field*.
Sun hora $=$ maximum spatial differentiation $=$ most dynamic field.
Saturn hora $=$ maximum spatial uniformity $=$ most stable field.

The $2 sqrt(6)$ invariant is the *heartbeat* that never changes.
Only the breath ($M$) varies.

#pagebreak()

= References

- Bṛhat Parāśara Horā Śāstra (BPHS), Ch. 3 (Graha guṇa), for the classical
  graha ordering and $k$-offset values (Sūrya $= 0$, Candra $= 1$, ...,
  Ketu $= 8$).
- Standard 3#sym.times 3 Lo Shu magic square: $mat(4, 9, 2; 3, 5, 7; 8, 1, 6)$
  with magic constant $M = 15$.
- Kronecker (tensor) product $A times.o B$ used for level extension.
- Eigendecomposition computed via NumPy (`numpy.linalg.eigh`), verified
  against OpenVINO NPU inference path.
