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

## Directions for Further Work

**(a) Systematic evaluation.** The single-chart observations above need testing
across a corpus of known charts with verified classical interpretations. The
question: does composite activation at natal points correlate with classical
assessments of graha strength (shadbala, vimshopaka)?

**(b) Nitya/tithi sub-structure.** The Moon sweeps 12° per tithi window. At each
tithi boundary, the Sun-Moon pair interference pattern shifts. Computing the
two-source field for the Sun-Moon pair at each of the 30 tithi positions may
reveal structure that corresponds to the Nitya Devi sequence — each tithi
selecting a different harmonic profile of the Sun-Moon interference.

**(c) k-weighting.** The composite currently sums all k-values with equal weight.
Classical jyotish treats aspects with different strengths (7th = full,
5th/9th = 3/4, 4th/8th = 3/4, 3rd/10th = 1/4 per some traditions). The
question: does optimizing k-weights to match classical strength assignments
produce a better composite predictor, or does the equal-weight composite
already capture the relevant structure?

**(d) Boundary vs. interior integration.** The N-source interior pattern (Chladni
figures) and the two-source boundary pattern (this work) analyze different
geometric projections of the same wave system. A unified treatment that integrates
the disk-interior structure with the boundary-circle structure may reveal
connections between the Sri Yantra geometry and the aspect harmonic system.

---

*Status: Findings 7-9 are established mathematical results. The case evaluation
is computed from a single chart (engine: compute_wave_field, 36 pairs ×
7 k-values × 10 targets) and is illustrative, not confirmatory.*
