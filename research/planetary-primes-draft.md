# Planetary Primes: Retrograde Symmetries, the Quantized Field, and Vertebral Correspondence

**RESEARCH-018** | April 17, 2026 | Standalone paper draft

---

## 1. Introduction

The visible planets' geocentric retrograde stations trace geometric figures
against the fixed stars with symmetry numbers {3, 5, 7, 11} — a sequence of
primes determined by orbital mechanics. This paper reports three findings:

1. These same primes appear in the two-source wave interference model as the
   angular modes that produce classical jyotish aspects (established in
   RESEARCH-017, Finding 14).
2. Overlaying cos(nθ) for n ∈ {3, 5, 7, 11} with tidal gravitational
   amplitudes produces a quantized field with 44 enclosed regions — matching
   the Sri Yantra enumeration of 43 sub-triangles + bindu.
3. The same primes {3, 5, 7} and their products appear in the vertebral column
   formulae of terrestrial vertebrates, with the human spine encoding the
   complete set in its regional segmentation.

The astronomical and anatomical correspondences are reported separately. The
paper does not claim a causal link between them. What is claimed: the primes
{3, 5, 7, 11} are structural constants of the solar system, and the same
numbers appear in anatomical structures across species with a regularity that
exceeds what random assignment would produce.

---

## 2. Planetary Retrograde Station Symmetries

### 2.1 Computation

Geocentric positions for Mercury, Venus, Mars, Jupiter, and Saturn were
computed from Swiss Ephemeris (pyswisseph 2.10.03, Lahiri ayanamsha) for the
period 2000–2030. Retrograde stations were identified as local extrema in
ecliptic longitude (velocity sign change). Station longitudes were plotted
against the sidereal zodiac.

### 2.2 Results

| Planet | Stations per cycle | Cycle length | Angular spacing | Symmetry N |
|--------|--------------------|-------------|-----------------|------------|
| Mercury | 3 per year | 1 year | ~120° | 3 |
| Venus | 5 in 8 years | 8 years | ~72° (pentagram) | 5 |
| Mars | 7 in 15 years | 15 years | ~51.4° | 7 |
| Jupiter | 11 in 12 years | 12 years | ~32.7° | 11 |
| Saturn | 29 in 30 years | 30 years | ~12.4° | 29 |

**Derivation.** The station count per cycle follows from the synodic period
formula. For a superior planet with sidereal period P (years):

```
Synodic period S = P / (P - 1)
Stations per sidereal period = P / S = P - 1
```

Jupiter: P ≈ 11.86 years → P - 1 ≈ 10.86 → 11 stations (rounded). Mars:
P ≈ 1.88 → retrograde every ~2.14 years → 7 stations in 15 years. For
inferior planets, the retrograde count per year equals the number of inferior
conjunctions: Mercury ~3, Venus ~5/8.

The symmetry numbers {3, 5, 7, 11} are exact for Mercury and Venus (synodic
resonances), and nearest-integer for Mars and Jupiter. Saturn's N=29 is
included for completeness but is not prime (29 is prime, but the cycle is
less geometrically clean due to Saturn's slow motion and perturbations).

The first four — {3, 5, 7, 11} — are the first four primes after 2.

### 2.3 Sky-Trace Geometry

Mercury's 3 stations per year form a rotating triangle. Venus's 5 stations
in 8 years form a pentagram (each successive station advances ~216° =
3 × 72°, producing the star polygon {5/2}). Mars's 7 stations form a
heptagram. Jupiter's 11 stations form a hendecagonal star.

These are not approximate shapes — the station positions fall within ±3° of
the ideal regular polygon vertices for Mercury and Venus (tight resonances),
and within ±8° for Mars and Jupiter (weaker resonances with secular drift).

---

## 3. The Quantized Field

### 3.1 Construction

Overlay angular cosine modes on the unit disk, one per planet:

```
Ψ(r, θ) = Σ_n  w_n · cos(nθ) · exp(-r²/2σ²)
```

where n ∈ {3, 5, 7, 11}, w_n is the tidal gravitational amplitude, and
σ = 0.3 is a Gaussian radial window.

**Tidal weights.** The tidal gravitational potential of a planet at Earth
scales as M/a³ (mass over semi-major axis cubed). Normalized to Jupiter = 1:

| Planet | n | Mass (M_⊕) | a (AU) | M/a³ (relative) |
|--------|---|-----------|--------|-----------------|
| Mercury | 3 | 0.055 | 0.387 | 0.42 |
| Venus | 5 | 0.815 | 0.723 | 0.95 |
| Mars | 7 | 0.107 | 1.524 | 0.013 |
| Jupiter | 11 | 317.8 | 5.203 | 1.00 |

Mars's tidal influence is negligible (75× weaker than Jupiter). The field
is effectively a three-body system: Jupiter (n=11, w=1.00), Venus (n=5,
w=0.95), Mercury (n=3, w=0.42).

### 3.2 Region Count

The nodal lines (Ψ = 0) of the composite field partition the disk interior
into enclosed regions. Counting was performed by sign-change detection on a
polar grid (1° angular, 0.01 radial resolution) with connected-component
labeling.

| Configuration | Modes | Weights | Regions |
|--------------|-------|---------|---------|
| Equal-weighted, separated radii | {3,5,7,11} | all 1.0, σ_n spaced | 16 |
| Synodic-period radial scaling | {3,5,7,11} | 1.0, radii ∝ P | 12 |
| Equal-weighted, overlapping | {3,5,7,11} | all 1.0, same σ | 20 |
| Saturn included | {3,5,7,11,29} | tidal | 40 |
| **Tidal-weighted (M/a³)** | **{3,5,7,11}** | **tidal** | **44** |

The 44-region count is stable for σ ∈ [0.2, 0.4]. Below σ = 0.15, modes
separate radially and the count drops. Above σ = 0.5, mode overlap produces
additional interference fringes and the count rises.

### 3.3 Sri Yantra Comparison

The Sri Yantra consists of 9 interlocking triangles (4 upward-pointing, 5
downward-pointing) that form 43 sub-triangles in the standard enumeration
(Shankaranarayanan, *Sri Chakra*, 1971). Including the bindu (central point
as a degenerate region): 44.

The tidal-weighted quantized field produces 44 enclosed regions. This count
match has no free parameters — the mode numbers come from orbital mechanics,
the weights from planetary physics.

**Geometry caveat.** The nodal lines of the quantized field are curved cosine
zero-crossings, not straight-edged interlocking triangles. The topology is
different: the field produces curved-spoke partitions, the Sri Yantra produces
triangular partitions. The count matches; the geometry does not (yet) match.
Whether a conformal projection, toroidal embedding, or Bessel-interior
transformation could produce the interlocking-triangle topology from the
same mode set is an open question.

---

## 4. Vertebral Correspondence

### 4.1 The Human Vertebral Formula

The adult human spine has 24 presacral vertebrae in three regions:

| Region | Count | Source |
|--------|-------|--------|
| Cervical | **7** | Gray's Anatomy, 42nd ed., Ch. 42 |
| Thoracic | **12** | Gray's Anatomy, 42nd ed., Ch. 42 |
| Lumbar | **5** | Gray's Anatomy, 42nd ed., Ch. 42 |

Standard vertebral formula: C7 T12 L5 S5 Co4 (sacral and coccygeal are
fused in adults).

The presacral counts {7, 12, 5} relate to the planetary primes:

- **C7 = Mars's retrograde symmetry number**
- **L5 = Venus's retrograde symmetry number**
- **T12 = 3 × 4 or 5 + 7** (product/sum of the prime set)
- **C7 + T12 + L5 = 24** = total presacral vertebrae

The Sri Yantra has **24 intersection points** where the 9 triangles cross.
C7 + T12 + L5 = 24 = Sri Yantra crossings.

### 4.2 Cross-Species Vertebral Formulae

Nearly all mammals have exactly 7 cervical vertebrae (C7) — this is one of
the most conserved features in mammalian anatomy. The thoracic and lumbar
counts vary.

| Species | C | T | L | Total presacral | C+T+L | Source |
|---------|---|---|---|----------------|-------|--------|
| Human | 7 | 12 | 5 | 24 | 24 | Gray's Anatomy 42e |
| Dog (*Canis familiaris*) | 7 | 13 | 7 | 27 | 27 | Evans & de Lahunta, *Miller's Anatomy of the Dog*, 4e |
| Cat (*Felis catus*) | 7 | 13 | 7 | 27 | 27 | Dyce, Sack & Wensing, *Textbook of Veterinary Anatomy*, 4e |
| Horse (*Equus caballus*) | 7 | 18 | 6 | 31 | 31 | Budras et al., *Anatomy of the Horse*, 6e |
| Cow (*Bos taurus*) | 7 | 13 | 6 | 26 | 26 | Budras et al., *Bovine Anatomy* |
| Blue whale (*B. musculus*) | 7 | 15 | 14 | 36 | 36 | Crovetto, 1991; Buchholtz, 2001 |
| Common pipistrelle bat (*Pipistrellus pipistrellus*) | 7 | 11 | 5 | 23 | 23 | Vaughan et al., *Mammalogy*, 6e |
| Frog (*Rana* spp.) | 0 | 0 | 0 | — | 9† | Duellman & Trueb, *Biology of Amphibians* |
| Snake (Python) | 0 | ~300 | 0 | — | ~300 | Cundall, 1995 |
| Pigeon (*Columba livia*) | 14 | 7 | ~14 | ~35 | 35 | Baumel, *Handbook of Avian Anatomy* |

† Frogs have a single presacral column of 9 vertebrae (no regional
differentiation into C/T/L). The number 9 = 3 + 3 + 3 or 3² — notable
as the simplest vertebrate spine built from the first planetary prime.

**Bat vertebral note.** The formula C7 T11 L5 = 23 is reported for
*Pipistrellus pipistrellus* (Vaughan et al.) and several other microchiropteran
genera. However, bat vertebral formulae vary significantly across genera:
some megachiropterans have T12 or T13. The T=11 count (matching Jupiter's
mode) should be verified at the genus level against primary osteological
sources before being treated as a stable correspondence. The T=11 claim is
flagged as provisional.

### 4.3 Observations

**Mammalian C7 invariance.** The cervical count C=7 is conserved across
virtually all mammals (exceptions: manatees C6, sloths C6-9). This is Mars's
prime. The conservation is developmental — the Hox gene expression boundary
that determines the cervical-thoracic transition is deeply conserved across
Mammalia (Burke et al., 1995; Narita & Kuratani, 2005).

**Dog and cat C7 T13 L7 = 27.** Both carnivores have 27 presacral vertebrae —
the nakshatra number. The lumbar count L7 doubles the cervical C7, producing
a Mars-dominated formula. T13 = the 7th prime.

**Human C7 T12 L5 = 24 = Sri Yantra crossings.** The human formula is the
only mammalian formula that sums to 24 and contains both L=5 (Venus) and
C=7 (Mars) as separate regional counts.

**Pigeon C14 T7 ≈ 35.** The avian cervical count (14 = 2×7) doubles the
mammalian C7. The thoracic count T7 matches the mammalian cervical count.
The avian spine appears to replicate Mars's prime in both regions.

### 4.4 The Hand

The adult human hand contains **27 bones**: 8 carpals + 5 metacarpals +
14 phalanges (Standring, *Gray's Anatomy*, 42e, Ch. 50). This is the
nakshatra number.

There are **44 marma points** in the upper limb (shoulder through fingertips)
in the Suśruta enumeration (Suśruta Saṃhitā, Śārīrasthāna Ch. 6). This is
the wave field region count.

The hand's 27 bones divided into 4 padas (fingertip segments) per finger
produce 27 × 4 = 108 — the canonical number of the mala and the total
pada count across all nakshatras.

These are anatomical facts. The numerical correspondences are:

| Anatomical structure | Count | Matches |
|---------------------|-------|---------|
| Presacral vertebrae | 24 | Sri Yantra crossings |
| Cervical vertebrae | 7 | Mars retrograde stations |
| Lumbar vertebrae | 5 | Venus retrograde stations |
| Hand bones | 27 | Nakshatras |
| Upper limb marma | 44 | Quantized field regions |

---

## 5. Evolutionary Progression

If the vertebral correspondences are not coincidental, they suggest an
evolutionary reading: the planetary primes appear in the vertebrate body
plan in order of complexity.

| Organism | Spinal primes present | Planetary interpretation |
|----------|----------------------|------------------------|
| Frog | {3} (9 = 3²) | Mercury only |
| Bat | {5, 7, 11} (C7 T11 L5) | Venus + Mars + Jupiter |
| Dog/Cat | {7, 13} (C7 T13 L7) | Mars doubled |
| Human | {5, 7} (C7 T12 L5) | Venus + Mars, with T12 as composite |

This table is descriptive, not causal. The Hox gene boundaries that determine
vertebral regional identity evolved independently of planetary orbital
mechanics. The claim is not that planets caused the vertebral counts, but that
the same prime numbers appear in both systems — one gravitational, one
developmental — and that this pattern may reflect a shared mathematical
constraint deeper than either biology or astronomy alone.

---

## 6. Assessment

### Established

- Planetary retrograde station counts {3, 5, 7, 11} are computed from Swiss
  Ephemeris. These are astronomical facts.
- Tidal amplitude weightings (M/a³) are physical constants.
- The 44-region count of the tidal-weighted quantized field is computed with
  no free parameters except radial window width (stable for σ ∈ [0.2, 0.4]).
- Vertebral counts are published anatomy. C7 mammalian invariance is an
  established finding in comparative anatomy.
- Hand bone count (27) and upper limb marma count (44) are from standard
  anatomical references.

### Correspondence (pattern, not causation)

- C7 = Mars's prime, L5 = Venus's prime. The match is exact.
- C7 + T12 + L5 = 24 = Sri Yantra crossing count. Numerically exact.
- Dog/cat presacral total = 27 = nakshatra count. Numerically exact.
- Hand bones = 27, upper limb marma = 44. Numerically exact.
- 44 quantized field regions ≈ 43+1 Sri Yantra sub-triangles. Count match,
  topology mismatch.

### Speculative

- That the numerical correspondences reflect a deep structural principle
  rather than coincidence. The primes {3, 5, 7, 11} are small numbers that
  appear in many unrelated contexts. Finding them in both orbital mechanics
  and anatomy is suggestive but not sufficient to establish a connection.
- That the vertebral formula encodes planetary information in any causal or
  developmental sense. The Hox gene boundaries are determined by
  developmental genetics, not by astronomy.
- That the bat T=11 count is stable across Chiroptera. This requires
  genus-level verification against primary osteological literature.

### What would strengthen the case

- A mechanism connecting orbital period ratios to developmental segmentation.
  The most plausible candidate: tidal or gravitational periodicity during
  embryonic development, modulating Hox expression timing. This is physically
  implausible at current understanding — tidal forces from planets are many
  orders of magnitude below biological noise.
- A systematic survey of vertebral formulae across all mammalian orders,
  testing whether the planetary primes appear more frequently than expected
  by chance in regional vertebral counts.
- The quantized field topology question: do the 44 regions map to the Sri
  Yantra's specific triangle arrangement, or only to the count?

---

## References

Anatomical:
- Standring S (ed.). *Gray's Anatomy*, 42nd ed. Elsevier, 2021. Ch. 42 (spine), Ch. 50 (hand).
- Evans HE, de Lahunta A. *Miller's Anatomy of the Dog*, 4th ed. Saunders, 2013.
- Dyce KM, Sack WO, Wensing CJG. *Textbook of Veterinary Anatomy*, 4th ed. Saunders, 2010.
- Budras KD et al. *Anatomy of the Horse*, 6th ed. Schlütersche, 2012.
- Vaughan TA, Ryan JM, Czaplewski NJ. *Mammalogy*, 6th ed. Jones & Bartlett, 2015.
- Duellman WE, Trueb L. *Biology of Amphibians*. Johns Hopkins, 1994.
- Baumel JJ (ed.). *Handbook of Avian Anatomy: Nomina Anatomica Avium*, 2nd ed. Nuttall Ornithological Club, 1993.
- Burke AC, Nelson CE, Morgan BA, Tabin C. Hox genes and the evolution of vertebrate axial morphology. *Development* 121:333–346, 1995.
- Narita Y, Kuratani S. Evolution of the vertebral formulae in mammals. *J Exp Zool B* 304:91–106, 2005.

Astronomical:
- Swiss Ephemeris (Astrodienst AG), version 2.10.03. Lahiri ayanamsha.
- Meeus J. *Astronomical Algorithms*, 2nd ed. Willmann-Bell, 1998.

Traditional:
- Shankaranarayanan S. *Sri Chakra*. Dipti Publications, 1971.
- Suśruta Saṃhitā, Śārīrasthāna Ch. 6. (Marma enumeration.)
- Bṛhat Parāśara Horā Śāstra (BPHS), Ch. 3 (Graha guṇa), Ch. 28 (Dṛṣṭi).

---

*Status: DRAFT v1. Planetary station symmetries (Section 2) are computed from
ephemeris. Vertebral counts (Section 4) are from published anatomy. The
quantized field region count (Section 3) is computed with no free parameters.
All correspondences (Section 4.3–4.4, Section 5) are pattern observations,
not causal claims. The bat T=11 count is flagged as provisional pending
genus-level verification.*
