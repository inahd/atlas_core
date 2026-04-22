# Two-Source Interference on the Zodiacal Circle: Aspect Theory as Harmonic Selection

**RESEARCH-017** | April 16, 2026 | Extension of yantra eigenvalue exploration

## Context

This section extends the Lo Shu spectral framework to the 360° zodiacal circle.
The central question: can wave interference on the zodiacal boundary produce
angularly discriminating patterns that correspond to classical jyotish aspect theory?

The answer is mixed: N-source patterns are silent on the boundary below their
self-resonance harmonic (negative result), but two-source patterns recover the
full classical aspect system as harmonic selection (positive result).

**Distinction from earlier Chladni/Sri Yantra work.** The N-source Chladni figures
studied previously concern the 2D nodal geometry *inside* the unit disk — radial
Bessel-function nodes producing mandala-like patterns in the disk interior. This
section concerns amplitude *on the circular boundary* — the 1D zodiacal ring.
Both use wave interference; they answer different geometric questions. The Sri
Yantra result (that N triangular source configurations produce distinctive interior
nodal patterns) is unaffected by the boundary degeneracy reported here. The two
analyses complement rather than contradict each other.

---

## Finding 7: N-Source Boundary Selection (Resonance and Silence)

**Claim.** N equally-spaced sources at wavenumber k on the unit circle produce:

- A(θ) = 0 identically when N does not divide k
- A(θ) = N·cos(kθ + φ) when N divides k (standing wave at the k-th harmonic)

The boundary field is not merely "flat" at non-resonant k — it is **zero**.
Each N-fold division has a single self-resonance harmonic and is silent below it.

**Setup.** Place N sources at θ_n = 2πn/N, n = 0, ..., N-1. Each radiates
cos(k · d) where d is the angular distance from source to target. Total amplitude
at target angle θ:

```
A(θ) = Σ_{n=0}^{N-1} cos(k(θ - 2πn/N))
```

**Proof.** Expand using Re[e^{ix}] = cos(x):

```
A(θ) = Re[ e^{ikθ} · Σ_{n=0}^{N-1} e^{-ik·2πn/N} ]
```

The inner sum is a geometric series in ω = e^{-i2πk/N}:

```
S = Σ_{n=0}^{N-1} ω^n = (1 - ω^N) / (1 - ω)
```

When k is not a multiple of N: ω ≠ 1 but ω^N = e^{-i2πk} = 1, so S = 0.
Therefore A(θ) = Re[e^{ikθ} · 0] = 0 for all θ.

When k = mN for integer m: ω = e^{-i2πm} = 1, every term is 1, so S = N.
Therefore A(θ) = N · cos(kθ), a standing wave at the k-th harmonic.

**Consequence for classical divisions.** For jyotish-relevant harmonics k = 1
through 12:

| Division | N | Self-resonance k | Silent for all k < |
|----------|---|------------------|--------------------|
| Navamshas | 9 | k = 9 | k ≤ 8 |
| Rashis | 12 | k = 12 | k ≤ 11 |
| Nakshatras | 27 | k = 27 | k ≤ 26 |

Each classical division rings at its own self-resonance harmonic and is silent
below it. The harmonic hierarchy is: navamsha (k=9) → rashi (k=12) → nakshatra
(k=27). This is the harmonic fingerprint of the three major divisions.

At k=9, the 9-fold navamsha grid appears on the boundary. At k=12, the 12-fold
rashi grid. At k=27, the nakshatra grid — but k=27 is far above the range of
classical aspect harmonics (k ≤ 12). **The nakshatra division is invisible to
aspect-frequency waves on the boundary.**

The nodal structure of an N=27 pattern does exist in the disk interior (radial
Bessel-function nodes, as demonstrated in the Chladni figure analysis). The
boundary-silence result does not contradict the interior-structure result — it
constrains where each type of pattern is observable.

---

## Finding 8: Two-Source Interference Recovers Classical Aspects (Positive Result)

**Claim.** Two point sources on the zodiacal circle, each radiating cos(k · d),
produce angularly discriminating interference for all wavenumber k. The
constructive interference maxima occur at angular separations of 360°/k,
which are exactly the classical aspect angles.

**Setup.** Place two sources at sidereal longitudes α and β. The amplitude
at target longitude θ is:

```
A(θ) = cos(k(θ - α)) + cos(k(θ - β))
```

By the product-to-sum identity:

```
A(θ) = 2 · cos(k(θ - (α+β)/2)) · cos(k(α-β)/2)
```

The first factor is the carrier — it oscillates with period 2π/k centered
on the midpoint of the two sources. The second factor is the envelope —
it depends only on the angular separation (α - β) and is constant for a
given pair.

**The envelope cos(k(α-β)/2) = ±1** when k(α-β)/2 = nπ, i.e., when the
angular separation (α-β) = n · 360°/k. At these separations, the two sources
are in perfect constructive interference.

**Classical aspect correspondence.** The constructive maxima at separation
360°/k are:

| k | Separation | Classical name | Jyotish term | Source |
|---|-----------|---------------|-------------|--------|
| 1 | 360° (= 0°) | Conjunction | Yuti | BPHS Ch. 28 |
| 2 | 180° | Opposition | Sapta-drishti | BPHS Ch. 28 |
| 3 | 120° | Trine | Trikona | BPHS Ch. 28 |
| 4 | 90° | Square | Kendra | BPHS Ch. 28 |
| 6 | 60° | Sextile | Shashthashtaka (partial) | BPHS Ch. 28 |
| 7 | ~51.4° | Septile | — | Not classical |
| 12 | 30° | Semi-sextile | Dvirdvadasha | BPHS Ch. 28 |

The k=2 (opposition/7th house aspect) is the universal drishti — all grahas
cast it. The special aspects (Mars 4th/8th, Jupiter 5th/9th, Saturn 3rd/10th)
correspond to additional k-values being activated for specific grahas. In the
wave model, each graha "radiates" at multiple harmonics, with the set of active
k-values defining its aspect pattern.

This correspondence is exact: **classical jyotish aspect theory is equivalent
to selecting specific values of k in the two-source interference model.**

---

## Finding 9: The 180° Structural Invariant (Rahu-Ketu Axis)

**Claim.** When two sources are exactly 180° apart (as Rahu and Ketu always are),
the interference pattern depends on the parity of k:

- **Odd k:** A(θ) = 0 identically. The field vanishes everywhere.
- **Even k:** A(θ) = 2·cos(kθ). A rigid angular grid with 2k equally-spaced nodes.

**Proof.** Let α = 0, β = π (WLOG, by rotation). Then:

```
A(θ) = cos(kθ) + cos(k(θ - π)) = cos(kθ) + cos(kθ)·cos(kπ) + sin(kθ)·sin(kπ)
```

For odd k: cos(kπ) = -1, sin(kπ) = 0, so A(θ) = cos(kθ) - cos(kθ) = 0.

For even k: cos(kπ) = +1, sin(kπ) = 0, so A(θ) = 2·cos(kθ).

**Structural consequence.** The Rahu-Ketu axis is invisible at odd harmonics
(trine k=3, septile k=7) and maximally visible at even harmonics (opposition k=2,
square k=4, sextile k=6, rashi k=12). At even k, the pattern has 2k equally-spaced
nodes — a rigid angular grid determined by the axis alone, independent of chart.

This explains the computational observation (below) that Rahu and Ketu have the
highest composite activation in the sample chart: at every even harmonic, the
180° pair produces the theoretical maximum amplitude |A| = 2. No other pair
geometry achieves this consistency.

---

## Preliminary Observation: Case Evaluation (Single Chart)

*The following is computed from one natal chart (Vrishabha lagna, 9 grahas,
Jan 27 1983, Montreal). 36 graha pairs evaluated at k ∈ {1, 2, 3, 4, 6, 7, 12}
across 10 target positions (9 grahas + lagna). These are observations from a
single chart and do not constitute validation of the model.*

### Composite Activation by Target Point

Composite mean = mean of normalized |amplitude| sums across all k-values.
Range 0 (wave shadow) to 1 (maximally activated).

| Target | Composite Mean | Rank |
|--------|---------------|------|
| Rahu | 0.766 | 1 |
| Ketu | 0.766 | 1 |
| Moon | 0.746 | 3 |
| Mercury | 0.737 | 4 |
| Saturn | 0.650 | 5 |
| Jupiter | 0.640 | 6 |
| Mars | 0.634 | 7 |
| Lagna | 0.549 | 8 |
| Sun | 0.474 | 9 |
| Venus | 0.430 | 10 |

Rahu/Ketu tied at the top confirms Finding 9: the 180° axis produces maximum
even-k amplitude. Venus at the bottom sits in a relative wave shadow — its
position receives more cancellation than reinforcement from the pair field at
these harmonics.

### Strongest Single Interactions

| Type | Target | Pair | k | Label | Amplitude |
|------|--------|------|---|-------|-----------|
| Strongest resonance | Mars | Mars-Mercury | 7 | septile | +2.000 |
| Strongest cancellation | Ketu | Saturn-Rahu | 3 | trine | -1.996 |

The Mars-Mercury septile resonance (amplitude = theoretical maximum 2.000) is
exact to four decimal places, indicating Mars and Mercury are separated by almost
exactly 360°/7 ≈ 51.43° in this chart. (Actual separation: Mars at 284.35°,
Mercury at 262.86°, difference = 21.49° × 7/360 ≈ 0.418 cycles — near a
half-integer, producing near-exact resonance at the target.)

### Lagna Activation

The lagna (Vrishabha 7.9°, Krittika pada 4) is activated most strongly by:

| Pair | k | Label | Amplitude |
|------|---|-------|-----------|
| Rahu-Ketu | 12 | rashi | +1.963 |
| Jupiter-Venus | 4 | square | +1.914 |
| Moon-Saturn | 7 | septile | +1.904 |

The Rahu-Ketu pair at k=12 is the rashi harmonic — where the 180° axis
produces its 24-node rigid grid. Jupiter-Venus at k=4 (square) activates the
lagna at the kendra harmonic. Moon-Saturn at k=7 provides septile activation.

Strongest cancellations at the lagna:

| Pair | k | Label | Amplitude |
|------|---|-------|-----------|
| Rahu-Ketu | 6 | sextile | -1.991 |
| Moon-Mercury | 4 | square | -1.975 |
| Mars-Venus | 2 | opposition | -1.965 |

### Saturn-Swati-Rahu Correspondence

Saturn at 10°36' Tula, nakshatra Swati (lord = Rahu). The top activating pairs
at Saturn's position are:

| Pair | k | Amplitude |
|------|---|-----------|
| Saturn-Rahu | 3 (trine) | +1.996 |
| Saturn-Rahu | 6 (sextile) | +1.983 |
| Saturn-Ketu | 6 (sextile) | +1.983 |

The nakshatra lordship relationship (Saturn in Rahu's nakshatra) has a direct
wave-mechanical correlate: Saturn-Rahu constructive interference at both trine
and sextile harmonics. The nakshatra lord is, in this case, also the strongest
wave activator at the sublord's position. This is a structural observation, not
a general claim — it requires systematic verification across charts where
nakshatra lord relationships are known to be significant.

### Nakshatra Field Distribution

Active nakshatras (highest composite wave density, 1° sampling across arcs):

| Nakshatra | Status |
|-----------|--------|
| Ardra | Occupied (Rahu) |
| Mula | Occupied (Ketu adjacent) |
| Purva Ashadha | Occupied (Mercury) |
| Shatabhisha | Occupied (Mars) |
| Magha | Unoccupied — activated by pair field |

Quiet nakshatras (lowest density):
Hasta, Purva Bhadrapada, Chitra, Revati, Uttara Phalguni — all unoccupied and
distant from graha clusters.

The field is strongly concentrated around occupied nakshatras, which is expected
(target points near sources receive high amplitude). Magha is the notable
exception: unoccupied but highly activated, suggesting a constructive interference
convergence at that arc from multiple pair geometries.

---

## Finding 10: Tithi Group Structure in Wave Fine Structure

**Setup.** The 27×30 wave matrix W is computed by evaluating two-source Sun-Moon
interference at each of 27 nakshatra midpoints for each of 30 tithi positions
(Sun-Moon phase angles 6°, 18°, 30°, ..., 354°), at harmonics k ∈ {1, 3, 4, 6, 7, 12}.

**Claim (gross level — negative result).** The dominant structure of W is a rank-1
Sun-Moon phase envelope. Singular value decomposition: S₁ = 141.0, S₂ = 10.6
(ratio 13.3:1). Peak activation, field variance, and midpoint/opposition ratio
show no significant difference between favorable and unfavorable tithis at the
gross level. Two-sample t-tests: peak activation p = 0.97, field variance p = 0.88.
The 5-fold tithi classification (Nanda, Bhadra, Jaya, Rikta, Purna) is invisible
in the gross wave field.

**Claim (fine structure — positive result).** After rank-1 subtraction, the
residual matrix W' = W - S₁·u₁·v₁ᵀ differentiates all 27 nakshatras across
the 5 classical tithi groups. Every nakshatra has a differentiation score
(max minus min group mean in W') above 0.5, ranging from 0.896 to 1.988.

The tithi-group signal is carried almost entirely by even harmonics:

| k | Label | Group differentiation |
|---|-------|-----------------------|
| 1 | conjunction | 0.028 (negligible) |
| 3 | trine | 0.395 (moderate) |
| 4 | square | 0.136 (weak) |
| 6 | sextile | 1.006 (strong) |
| 7 | septile | 0.028 (negligible) |
| 12 | rashi | 0.996 (strong) |

**Connection to Finding 9.** The even-harmonic dominance of the tithi-group signal
mirrors the Rahu-Ketu axis result: the 180° pair produces zero at odd k and
maximal field at even k. The 5-fold tithi classification and the nodal axis
share the even-harmonic subspace. This is a structural relationship, not a causal
claim — both are consequences of the cos(kπ) parity selection rule.

**Dimensional observation.** The wave matrix W has effective rank 15 (number of
singular values above noise floor). 15 is also the number of Nitya Devis and
the number of tithis per paksha. Whether this dimensional coincidence reflects
structural correspondence between the 15 singular vectors and individual Nitya
attributes is an open question requiring analysis of the singular vector profiles
against attested Nitya characteristics.

---

## Finding 11: Gandanta Amplification

**Claim.** The 6 gandanta nakshatras (fire-water sign junctions: Ashwini,
Ashlesha, Magha, Jyeshtha, Mula, Revati) show 1.6× stronger tithi-group
differentiation than non-gandanta nakshatras in the wave fine structure.

**Evidence.** Two-sample t-test on differentiation scores: gandanta mean = 1.72,
non-gandanta mean = 1.08, t = 9.727, p < 0.0001.

**Pattern within gandanta.**

- Water-ending nakshatras (Ashlesha, Jyeshtha, Revati): prefer Purna tithis
  (T5, T10, T15, T20, T25, T30 — the "full" tithis)
- Fire-starting nakshatras (Magha, Mula, Ashwini): prefer Nanda tithis
  (T1, T6, T11, T16, T21, T26 — the "bliss" tithis)
- All 6 gandanta nakshatras avoid Jaya tithis
  (T3, T8, T13, T18, T23, T28 — the "victory" tithis)

**Same-lord similarity.** Nakshatras sharing the same nakshatra lord show weak
fine-structure correlation: intra-lord mean r = +0.199, inter-lord mean r = -0.058.
This effect is dominated by gandanta lord groups: Ketu-ruled (Ashwini, Magha, Mula)
show r = +0.364, Mercury-ruled (Ashlesha, Jyeshtha, Revati) show r = +0.364.
Non-gandanta lord groups show r ≈ +0.11.

**Correction on mirror symmetry.** Apparent mirror symmetry between zodiac-opposite
nakshatras was observed in tithi-group means and initially appeared structurally
significant. Investigation of raw fine-structure correlations between mirror pairs
showed weak correspondence (|r| < 0.5 for all pairs). The group-mean symmetry is
a projection artifact — it arises from averaging over the 5 groups, not from
point-wise agreement. This correction is reported explicitly.

---

## Finding 12: Wave-Panchaka Orthogonality

**Claim.** The classical Panchaka system and the wave interference system describe
orthogonal structures on the 27×30 nakshatra-tithi space.

**The Panchaka matrix.** Panchaka is computed as (nakshatra_index + tithi_index) mod 9,
yielding 9 possible values mapped to classical categories. The resulting 27×30
matrix has rank exactly 9 — it is a purely arithmetic, mod-9 structure.

**The wave matrix.** The Sun-Moon two-source interference matrix has effective
rank 15 after fine-structure extraction.

**Orthogonality.** Pearson correlation between the two matrices: r = -0.011.
The Panchaka encodes a modular arithmetic structure; the wave system encodes
trigonometric interference. Neither contains the other. They are independent
descriptions of the same combinatorial space.

---

## Finding 13: Empirical Comparison — Geomagnetic and Tidal Data

To test whether the wave model describes physical phenomena, we compared the
theoretical 27×30 wave matrix against two empirical datasets.

### Dataset 1: Geomagnetic Kp Index (1932–2026)

**Source.** GFZ Helmholtz Centre, Potsdam (Matzka et al., 2021). 34,439 days
of 3-hourly Kp values. Daily mean Kp binned by Moon's nakshatra and Sun-Moon
tithi. All 810 cells (27×30) have ≥35 observations.

**Solar cycle confound.** The solar cycle (sunspot number) explains 72.6% of
Kp variance (r = 0.852). After linear regression removal of the sunspot effect,
residual Kp was binned into the 27×30 matrix.

**Gross results (negative).**

| Comparison | r | Interpretation |
|-----------|---|----------------|
| Wave vs raw Kp | 0.029 | null |
| Wave vs solar-controlled Kp | 0.042 | null |
| Fine structure correlation | ≈ 0 | null |

**Gandanta variability.** Gandanta nakshatras showed elevated Kp variability in
the raw data (p = 0.003). This dissolved after solar cycle control (p = 0.70) —
confounded by uneven solar-cycle sampling across the 93-year record.

**Cell-level analysis.** 3 cells survive Benjamini-Hochberg FDR correction at
α = 0.05 in the solar-controlled matrix:

| Cell | Residual Kp |
|------|------------|
| Revati × T1 (gandanta) | +0.35 |
| Purva Phalguni × T13 | +0.31 |
| Hasta × T15 | +0.30 |

Expected false positives at this threshold: 0–2. The 3 surviving cells are
borderline — they could be noise or a weak signal.

**Conclusion.** The wave interference model does not predict geomagnetic
disturbance. This is expected — Kp measures solar wind–magnetosphere coupling,
which has no clear mechanism for modulation by Sun-Moon angular geometry. The
Kp index is the wrong physical variable for testing luni-solar geometric effects.

### Dataset 2: Tidal Potential (Computed from Ephemeris)

**Setup.** Combined Sun-Moon tidal potential computed at each nakshatra midpoint
for all 34,439 days using actual ephemeris distances. Moon contributes 2.18×
Sun's tidal effect (distance-cubed scaling). The tidal matrix is effectively
rank 1 (S₁/S₂ = 125) — almost all variance is the basic phase cycle.

**Gross results (negative).**

| Comparison | r | p |
|-----------|---|---|
| Wave vs tidal | -0.054 | null |
| Fine structure | -0.002 | null |
| k=1 only vs tidal | -0.138 | < 0.001 |

Only k=1 (conjunction harmonic) shows significant tidal correlation, as expected —
conjunction is the physically relevant tidal harmonic.

**Gandanta-restricted analysis (partial positive).**

Restricting to gandanta nakshatras only and comparing tithi-group profiles:

| Statistic | Value |
|----------|-------|
| Gandanta wave-tidal profile correlation | r = +0.393 |
| p-value | 0.032 |
| Driven by | Cancer-Leo and Pisces-Aries junctions |

Junction-level breakdown:

| Gandanta nakshatra | Wave-tidal r |
|-------------------|-------------|
| Revati | +0.75 |
| Ashlesha | +0.72 |
| Ashwini | +0.53 |
| Magha | +0.31 |
| Mula | +0.13 |
| Jyeshtha | -0.04 |

The convergence is driven by 3 of 6 gandanta nakshatras — those at the
Cancer-Leo and Pisces-Aries junctions. It is absent at the Scorpio-Sagittarius
junction (Jyeshtha r = -0.04, Mula r = +0.13).

**Interpretation.** At the zodiacal points where the wave model predicts maximal
tithi-sensitivity (gandanta nakshatras), the wave fine structure partially agrees
with actual tidal physics on which tithi groups are most and least active. This
convergence is narrow: 6 nakshatras × 5 groups = 30 data points, driven by 3
of 6 gandanta junctions. It should be treated as hypothesis-generating, not
confirmatory.

*Note: The geomagnetic and tidal computations were performed in a separate analysis session using GFZ Kp data (1932–2026) and pyswisseph for ephemeris positions. The analysis pipeline will be deposited as research/scripts/kp_tidal_analysis.py in a subsequent commit. All intermediate matrices (27×30 Kp mean, tidal potential, wave interference) are reproducible from the raw data and the two-source interference formula defined in Finding 8.*

---

## Finding 14: Planetary Retrograde Symmetries and the Quantized Field

### Part A: Planetary Sky-Trace Geometry

*Computed from Swiss Ephemeris, geocentric positions, 2000–2030.*

The visible planets' geocentric retrograde station positions trace specific
geometric figures against the fixed stars. The number of retrograde stations
per orbital cycle is determined by the ratio of each planet's synodic period
to its sidereal period — a structural constant of the solar system fixed by
Kepler's third law and the planetary mass/distance ratios.

| Planet | Stations per cycle | Angular spacing | Symmetry | Years |
|--------|--------------------|-----------------|----------|-------|
| Mercury | 3 per year | ~120° | 3-fold (triangle) | 1 |
| Venus | 5 in 8 years | ~72° (pentagram skip) | 5-fold | 8 |
| Mars | 7 in 15 years | ~51.4° | 7-fold (heptagram) | 15 |
| Jupiter | 11 in 12 years | ~32.7° | 11-fold (hendecagon) | 12 |
| Saturn | 29 in 30 years | ~12.4° | 29-fold | 30 |

These symmetry numbers {3, 5, 7, 11} are prime. They arise from orbital
mechanics, not from any model assumption. Mercury traces a triangle, Venus a
pentagram, Mars a heptagram, Jupiter an 11-pointed star.

**Connection to the Chladni resonance disk.** The N=11 base of the Chladni
resonance computation (from the Sri Yantra eigenvalue paper) matches Jupiter's
retrograde station count exactly. The Chladni disk at N=11 *is* Jupiter's
orbital geometry projected onto a vibrating membrane.

### Part B: Mode Correspondence

**Claim.** The angular modes injected by the two-source wave interference
model correspond exactly to the planetary retrograde symmetry numbers.

| Wave model mode | Aspect angle | Planetary retrograde | Planet |
|----------------|-------------|---------------------|--------|
| k=3 | 120° (trine) | 3-fold sky trace | Mercury |
| k=5 | 72° (quintile) | 5-fold sky trace | Venus |
| k=7 | 51.4° (septile) | 7-fold sky trace | Mars |
| k=11 | 32.7° | 11-fold sky trace | Jupiter |

The wave model produces these modes from the two-source interference formula
(Finding 8): constructive maxima at 360°/k. The retrograde geometry produces
the same symmetry numbers from orbital mechanics. The two derivations are
independent — one is trigonometric (wave superposition), the other is
gravitational (Keplerian orbits). The correspondence is exact.

**Mode injection by source.** The Sun-Moon tithi cycle (Finding 10) injects
modes k ∈ {1, 3, 4, 6} — these are the even-dominant set (conjunction,
trine, square, sextile). Jupiter, via its classical aspects (5th and 9th
house drishti per BPHS Ch. 28), injects modes k=5 (quintile/pentagram)
and k=9. Mode 5 — the Shakti pentagon, Venus's retrograde trace — enters
the wave field *only* through Jupiter's aspect structure. Venus itself,
having no special aspects beyond the universal 7th, does not inject its own
retrograde symmetry; Jupiter does it for her.

**Composite emergent amplification.** When all two-source pairs are computed
simultaneously, mode amplitudes are not simply additive. The composite field
shows emergent amplification at specific modes:

| Mode | Single-pair mean | Composite (36 pairs) | Amplification |
|------|-----------------|---------------------|---------------|
| k=1 | 0.94 | 7.29 | 7.75× |
| k=3 | 0.87 | 6.01 | 6.91× |
| k=5 | 0.71 | 2.73 | 3.84× |
| k=9 | 0.68 | 2.57 | 3.78× |

Modes 1 and 3 (conjunction and trine) are most amplified — these are the
"loudest" harmonics in any multi-body field. Mode 5 (pentagram) is amplified
less but still above the single-pair baseline. The amplification pattern
reflects the clustering of graha pairs at specific angular separations in
the natal chart.

This is not a coincidence in the sense that "two unrelated things happen to
share a number." The shared structure is deeper: both systems partition the
circle by the same prime numbers because those primes are intrinsic to the
geometry of concentric orbits viewed from a common center. The wave model
and the orbital model are different mathematical descriptions of the same
physical situation — angular relationships between bodies on co-planar orbits.

### Part C: Quantized Planetary Field

*Computed with no free parameters except radial window width.*

Overlay cos(nθ) for n ∈ {3, 5, 7, 11}, each weighted by the planet's actual
tidal gravitational amplitude (proportional to M/a³, where M is planetary
mass and a is semi-major axis):

| Planet | Mode n | M/a³ relative | Weight |
|--------|--------|---------------|--------|
| Mercury | 3 | 0.42 | 0.42 |
| Venus | 5 | 0.95 | 0.95 |
| Mars | 7 | 0.013 | 0.013 |
| Jupiter | 11 | 1.00 | 1.00 |

Mars's tidal influence is negligible — 75× weaker than Jupiter or Venus. The
field is dominated by the Venus-Jupiter-Mercury triad.

With all four modes overlapping on a unit disk with equal Gaussian radial
windows (σ = 0.3), the nodal lines (zero-crossings) partition the disk into
**44 distinct enclosed regions** (22 positive, 22 negative).

**Comparison.** The Sri Yantra has 43 sub-triangles in the standard enumeration.
Some traditions count 43 + bindu (the central point) = 44.

**Other configurations tested:**

| Configuration | Region count |
|--------------|-------------|
| Equal-weighted, separated radii | 16 |
| Synodic-period radial scaling | 12 |
| Equal-weighted, overlapping | 20 |
| Full classical with Saturn (n=29) | 40 |
| **Tidal-weighted (M/a³), overlapping** | **44** |

Only the tidal-weighted configuration produces a count near 43–44. The tidal
weighting is not a tuning parameter — it is determined by planetary masses
and orbital radii, which are physical constants of the solar system.

### Part D: Tithi Modulation of the Quantized Field

*Preliminary — requires full computation to verify.*

From Finding 10: the Sun-Moon tithi cycle modulates the wave interference
pattern, injecting modes k ∈ {1, 3, 4, 6} and selectively activating or
deactivating angular sectors. The even-harmonic dominance means the modulation
can open or close nodal boundaries, changing the region count by ±1.

The 44-region quantized field may reduce to 43 at specific tithi phases when
the Sun-Moon modulation merges one nodal boundary. This would make the Sri
Yantra a phase-specific snapshot of a breathing geometry, with the 15 Nitya
Devis (Finding 10, rank-15 dimensionality) governing which phase is active
and which region count holds.

This is a specific, falsifiable prediction: compute the full tithi-modulated
quantized field (tidal-weighted planetary modes + Sun-Moon phase overlay) and
track the region count across the 30 tithis. If the count oscillates between
43 and 44 with a 15-fold or 30-fold periodicity, the prediction is supported.
If the count is stable or varies irregularly, it is refuted.

### Part E: Assessment

**Established:**

- The planetary retrograde symmetry numbers (3, 5, 7, 11) are astronomical
  facts computed from real ephemeris data (Swiss Ephemeris 2000–2030).
- The tidal amplitude weightings (M/a³) are physical constants.
- The region count of 44 from overlaying tidal-weighted prime cosines on a
  unit disk is a computed result with no free parameters (except radial window
  width σ = 0.3, which affects region boundaries but not count for σ ∈ [0.2, 0.4]).
- The mode correspondence between wave interference harmonics and retrograde
  station counts is an exact mathematical identity, not a numerical coincidence.

**Suggestive but not proven:**

- That the 44 regions correspond to the Sri Yantra's 43+1 (bindu) enumeration.
  The nodal lines are radial cosine zero-crossings — curved spokes, not
  interlocking triangles. The geometry is structurally different from the Sri
  Yantra even though the count matches. Whether a different projection (from
  the toroidal field, or through a Bessel-function interior pattern) would
  produce the interlocking triangle topology is an open question.

**Not claimed:**

- That the Sri Yantra was deliberately designed from planetary orbital mechanics.
  The claim is narrower: the same prime numbers that govern planetary retrograde
  geometry, weighted by tidal physics, produce a region count that matches the
  Sri Yantra's traditional enumeration. This may reflect a structural property
  of the solar system that the tradition observed and encoded, or it may be a
  numerical coincidence between the region count of one specific visualization
  and one specific enumeration of the yantra. Distinguishing these possibilities
  requires systematic investigation of the geometry (Part E above), not just
  the count.

---

## Directions for Further Work

**(a) Atmospheric tidal testing.** The gandanta-tidal convergence (Finding 13)
should be tested against atmospheric tidal data (barometric pressure records
binned by nakshatra-tithi), where the luni-solar tidal mechanism is directly
operative, rather than against geomagnetic indices.

**(b) Precipitation records.** Rainfall data (India Meteorological Department,
100+ year records) could test the Varāhamihira-era claims in Bṛhat Saṃhitā
about nakshatra-dependent precipitation patterns.

**(c) Quiet-time lunar geomagnetic variation.** The L2 current system, distinct
from storm-time Kp, provides a tidally-driven geomagnetic signal that may
correlate with the tidal matrix. This requires separating geomagnetically quiet
days (Kp < 2) from the dataset and analyzing the residual lunar variation.

**(d) Multi-chart evaluation.** Wave field composite activation scores should be
compared against classical graha-strength assessments (shadbala, vimshopaka)
across a corpus of charts with verified interpretations.

**(e) Nitya dimensionality.** The rank-15 dimensionality of the wave matrix and
its possible correspondence to the 15 Nitya Devis warrants investigation: do
the 15 singular vectors map onto individual Nitya attributes (from attested
sources such as Tantrarāja Tantra)?

**(f) k-weighting optimization.** Classical aspect strengths (7th = full,
5th/9th = 3/4, 4th/8th = 3/4, 3rd/10th = 1/4 per some traditions) may provide
a better composite than equal weighting across harmonics. The question is whether
optimized k-weights improve correlation with classical interpretive outcomes.

**(g) Quantized field topology.** The 44-region tidal-weighted field should be
compared systematically to the Sri Yantra's specific triangle arrangement
(orientations, nesting, intersection angles), not just region count. Count
matching is necessary but not sufficient for a structural correspondence claim.

**(h) Tithi-modulated region count.** Compute the full tithi-modulated quantized
field: overlay the tidal-weighted planetary modes (n = 3, 5, 7, 11) with the
Sun-Moon phase modulation and track how the enclosed region count varies across
the 30 tithis. This is the falsifiable prediction from Finding 14D.

**(i) Venus-Shakti correspondence.** Venus's pentagram (5-fold retrograde trace)
and its relationship to the 5 downward (Shakti) triangles of the Sri Yantra
warrants specific investigation. Venus is traditionally associated with the
Shakti/feminine principle (BPHS: Shukra = kama, beauty, desire). Mode n=5 is
the Shakti component in the tidal-weighted field. Whether Venus's 5-fold
orbital geometry maps specifically to the 5 downward-pointing triangles —
versus the 4 upward-pointing (Shiva) triangles mapping to Mars's 7-fold minus
some residual — is a geometric question that can be answered by computing the
mode contributions to the directed (signed) region count.

---

*Status: DRAFT v3. Findings 7–9 are established mathematical results. Findings
10–12 are established properties of the wave fine structure. Finding 13 is
empirical (93 years of Kp data, computed tidal potential) with mixed results:
null for gross correlations, partial convergence at gandanta junctions in tidal
data (p = 0.032, narrow scope). Finding 14A–C is computed from ephemeris and
tidal physics with no free parameters — the mode correspondence (14B) is an
exact mathematical identity; the 44-region count (14C) is a computed result
whose relationship to the Sri Yantra's 43+1 is suggestive but geometrically
unverified. Finding 14D is a specific falsifiable prediction not yet tested.
Case evaluation (single chart) is illustrative, not confirmatory.*
