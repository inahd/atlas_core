# Mathematical Foundation — Beyond-Chladni Cut-and-Project Quasicrystal Pipeline

*Foundation document for Atlas's beyond-Chladni renderer. Establishes which mathematical framework will be used, where it differs from existing infrastructure, and what the per-Nityā cut-orientation specification is. Honest reporting of gaps and SOURCE_NEEDED entries throughout.*

**Date**: 2026-05-05
**Brief**: Beyond-Chladni Cut-and-Project Quasicrystal Implementation
**Output**: This document is RESEARCH-028. It is the prerequisite for Tasks 2–5.

---

## §1. What already exists vs. what this brief asks for

### Already in the repository

- **`npu_engine/geometry/cut_and_project.py`** (463 lines) implements the **multigrid method**: for a target N, sums N equispaced plane waves `cos(x cos(2πj/N) + y sin(2πj/N) + γⱼ)` over j = 0..N–1 and renders the resulting intensity field. Has per-Nityā `DEVI_N` table mapping each tithi to its symmetry order. Has 3D polyhedron mediator constructors (antiprism, icosahedron, rhombic triacontahedron).
- **`static/s4.html`** (349 lines) implements client-side multigrid in JavaScript, line 297: `// Client-side rendering: N-fold multigrid cos interference`. Renders to Canvas2D with tithi slider + Atlas panchanga integration.
- **`npu_engine/geometry/CONSTRUCTION_CHOICES.md`** documents per-Nityā choices and explicitly states: *"All non-standard N use the multigrid method ... The multigrid fields are the Fourier-space dual of the tiling and carry the same symmetry information. If specific substitution-rule tilings become available for these N values, they can replace the multigrid construction while keeping the same interface."*

### What the brief asks for

The brief asks for the **true cut-and-project pipeline** — the discrete tile-vertex output, not the smooth Fourier intensity. The two methods are mathematically related (de Bruijn duality, see §2) but produce different outputs:

| | Multigrid (existing) | True cut-and-project (this brief) |
|---|---|---|
| Output | continuous intensity field | discrete tile-vertex set |
| Phason dynamics | not visible (smooth gradients) | visible as discrete tile-rearrangement events |
| Per-Nityā | parameterized by N (symmetry order) | parameterized by cut-plane orientation in higher-D lattice |
| Computational cost | O(W·H·N) per frame | O(intersection_count) per frame |
| Aesthetic | watercolor / blur | crystalline / discrete |

**This work is additive.** The multigrid renderer continues to operate as-is in `s4.html` and `cut_and_project.py`. The new pipeline lives at `static/s4_quasicrystal.html` and `npu_engine/geometry/cut_and_project_lattice.py` (or equivalent).

---

## §2. Mathematical foundations — the de Bruijn–Mackay correspondence

### Why multigrid and cut-and-project are duals

de Bruijn (1981) proved that the **multigrid construction** in 2D (N families of equispaced parallel lines at angles 2πj/N) is the **direct dual** of the **cut-and-project tiling** of a Penrose-type quasicrystal. The N-grid intersection points correspond bijectively to tiles of the quasicrystal, and the line indices that bracket each intersection give that tile's lift to the higher-dimensional lattice.

Specifically: each intersection of two grid lines from families j and k gets coordinates (k_0, k_1, ..., k_{N-1}) where k_m is the index of the line from family m that the intersection lies just below or at. The intersection has a tile of shape determined by (j, k) — there are ⌊N²/4⌋ distinct tile shapes for an N-fold quasicrystal.

This means: **the existing multigrid code has all the geometric information needed to extract tile vertices**. We just need to identify the line intersections and their bracket-indices rather than rendering the cos sum.

### Why de Bruijn multigrid is the right approach for this work

- **Tractable in JavaScript.** Each direction j contributes a family of parallel lines `x·cos(θⱼ) + y·sin(θⱼ) = m + γⱼ` for integer m. Intersections are pairs of equations solved as a 2×2 linear system. For a viewport with k = 12 wave-density and N = 15 directions, the count is roughly 15·k = 180 lines per family, ~16,200 lines total, with O(N² · k²) ≈ 32,400 intersections — well within real-time JS budget.
- **Phason dynamics fall out for free.** The γⱼ values (per-direction phase offsets) parameterize the cut-plane offset in the higher-D lattice. Continuous γ evolution is continuous cut-plane motion. Discrete tile-rearrangement events occur when an intersection passes through a degenerate configuration (three lines meeting at a point) — these are the phason flips, and they are *directly identifiable* in the multigrid coordinates.
- **Per-Nityā cut-orientations are the γ-vector.** Each Nityā has its own (γ₀, ..., γ_{N-1}) that specifies which 2D cut-plane is being projected. The 15 Nityā orientations correspond to 15 specific γ-vector configurations.
- **Builds on existing infrastructure.** The multigrid methodology is already in the repo. We extend it to extract tile vertices from intersections rather than render Fourier intensity. The 3D polyhedron mediators are still meaningful: they are 3D representations of the cut-plane embedding in 8-D (for N=15) or N-D space.

### Why other approaches are weaker for this work

- **Cyclotomic lift to 8-D Z[ζ_15].** Mathematically clean (φ(15) = 8), but requires explicit construction of an 8-D lattice basis and projection matrices in JavaScript. Implementation is substantially more complex than de Bruijn multigrid for the same observable output. **OBSERVED:DEFERRED** — keep as a future-refinement option.
- **Composite 3-fold × 5-fold.** Since 15 = 3 × 5 and the 5-fold case has well-developed Penrose-tiling tools, this approach uses the 5-fold Penrose construction and modulates with 3-fold. Mathematically defensible (Hermann's theorem for compound symmetries), but the resulting tiling is *not* the same shape as the de Bruijn 15-fold tiling. **OBSERVED:DEFERRED** — would produce a different visual structure than the brief specifies; keep as alternative if de Bruijn approach hits an obstacle.
- **Bilateral 7+1 reduction.** Sri Yantra has D₁₅ symmetry (cyclic + reflection). 8 angular positions are independent (7 + 1 bindu). Reducing to 8 directions in multigrid = 8-fold output, not 15-fold. **OBSERVED:NOT-RECOMMENDED** — destroys the 15-fold structure that defines the Sri Yantra.

### Recommendation

**Use de Bruijn multigrid → tiling extraction.** Specifically:

1. For each Nityā with symmetry order N, use N families of parallel lines at angles 2πj/N for j = 0..N–1, with per-family offsets (γ₀, ..., γ_{N-1}).
2. Compute pairwise intersections of all line pairs (j, k) with j < k.
3. For each intersection, compute its lift coordinates (k₀, ..., k_{N-1}) where kₘ = ⌊p · ê_m + γₘ⌋ for p the intersection point and ê_m the direction unit vector.
4. The intersection's 2D position is the tile center (or vertex, depending on convention). The tile shape is determined by (j, k) — for de Bruijn convention, the rhomb has angles π·|j-k|/N and π·(1 - |j-k|/N).
5. Phason flips are detected when an intersection's lift coordinates change discretely — i.e., when γ rotation moves a lattice point across the cut-plane.

**This is the de Bruijn multigrid method as documented in Senechal (1995) chapter 7 and the original de Bruijn (1981) papers.**

---

## §3. Specifications

### §3.1 Lift dimension

For a multigrid with N directions, the natural higher-D lattice is **N-dimensional**: each direction corresponds to one lattice basis vector. The cut plane is the 2D plane spanned by the projection vectors `(cos θⱼ, sin θⱼ) = ê_j` (which span 2D). The internal/perpendicular space is (N-2)-dimensional.

For Sri Yantra at full 15-fold: **N=15, lift dim = 15, internal dim = 13**.

For each Nityā at her own symmetry order N: lift dim = N, internal dim = N-2.

(Note: this differs from the 8-D cyclotomic lift. The de Bruijn N-D lift is *redundant* — it has N-1 degrees of freedom too many, since N projection vectors span only 2D. The redundancy is part of the construction; the acceptance window in (N-2)-D internal space is what selects which lattice points project to the cut.)

### §3.2 Lattice basis

For symmetry order N, the lattice is the integer lattice ℤ^N. Basis vectors {e_j} for j = 0..N-1 are unit vectors of ℤ^N. The projection π_‖ : ℝ^N → ℝ^2 sends e_j ↦ (cos(2πj/N), sin(2πj/N)). The orthogonal complement π_⟂ : ℝ^N → ℝ^{N-2} sends e_j to a unit vector in (N-2)-D internal space; the explicit basis can be constructed via Gram-Schmidt or directly via the regular-N-gon character formula.

### §3.3 Cut-plane parameterization

The cut plane is specified by:
- **Position offset**: the γ-vector (γ₀, ..., γ_{N-1}) ∈ ℝ^N. Translates the cut plane in the higher-D space.
- **Orientation**: fixed by N. The cut plane is always the projection-image of {e_j ↦ unit-vector-at-angle-2πj/N}; rotating the cut plane corresponds to rotating the γ-vector in a specific way.

For Sri Yantra at the canonical orientation (bindu at center, no rotation): γ = (0, 0, ..., 0). Per-Nityā γ values are specified in §4.

### §3.4 Acceptance window

In the de Bruijn multigrid construction, the acceptance window is **the N-cube [0, 1]^N projected to the (N-2)-dimensional internal space**. A lattice point ℓ ∈ ℤ^N is accepted (i.e., included in the tiling) iff its perpendicular-space image π_⟂(ℓ - γ) lies inside this window.

Equivalently in 2D multigrid coordinates: the intersection of lines from families j and k is accepted as a tile center iff the lift indices (k₀, ..., k_{N-1}) computed at that intersection are *all* integers (which they are by construction) **and** the line-bracket conditions are satisfied. For standard de Bruijn this is automatic; the acceptance is the multigrid intersection set itself.

### §3.5 Phason-flip specification

A **phason flip** occurs when γ evolution causes three multigrid lines (one each from families j, k, l) to meet at a single point. At that exact γ-configuration, the local tile structure is degenerate; immediately after, two tiles have rearranged into different tile shapes covering the same area.

In the (N-2)-dimensional internal space, this corresponds to a lattice point passing through the boundary of the acceptance window from inside to outside (or vice versa). The lattice point's projection to the cut plane was a tile vertex; after the flip, it isn't.

**Detection**: precompute, for each candidate triple (j, k, l), the γ-configuration at which the three lines meet. As γ evolves smoothly over time, when γ approaches one of these critical configurations, we are near a phason flip; crossing it triggers the flip.

For 15-fold quasicrystals with line density k=12 in a viewport, the phason-flip count over a full 2π γ-cycle is roughly N(N-1)(N-2)/6 · k² ≈ 65,000 critical points. **Most of these are too small to be visible** at typical rendering resolution; only the flips affecting visible tiles are perceptually relevant. Implementation should compute flips lazily per-tile rather than enumerating all theoretical critical points.

---

## §4. Per-Nityā cut-orientations

Each Nityā has a documented symmetry order N (from `cut_and_project.py:DEVI_N` and `CONSTRUCTION_CHOICES.md`). The cut-orientation for each Nityā is parameterized by:
- **N**: the symmetry order (number of multigrid directions)
- **γ-vector**: the per-direction phase offsets

Below: the recommended per-Nityā γ-specification. **This is a synthesis** combining (a) the existing N values from `DEVI_N`, (b) the classical Sri Vidyā tradition's tithi-cycle ordering, and (c) the principle that γ-vectors should distribute the 15 Nityās around the cut-plane orientation circle so they are visually distinct.

| Tithi | Nityā | N | Polyhedron | γ-pattern | Notes |
|---|---|---|---|---|---|
| 1 | Kāmeśvarī | 3 | tetrahedron | (0, 0, 0) | trikona, periodic, simplest case |
| 2 | Bhagamālinī | 6 | cuboctahedron | (0, 0, 0, 0, 0, 0) | hexagram, periodic |
| 3 | Nityaklinnā | 3 | tetrahedron | (1/3, 0, 0) | trikona with one offset |
| 4 | Bheruṇḍā | 3 | tetrahedron | (1/3, 2/3, 0) | trikona with two offsets |
| 5 | Vahnivāsinī | 8 | octagonal antiprism | γⱼ = j/8 mod 1 | aṣṭakoṇa, Ammann–Beenker class |
| 6 | Mahāvajreśvarī | 6 | cuboctahedron | γⱼ = j/6 | hexagram, with linear offset |
| 7 | Śivadūtī | 7 | heptagonal antiprism | γⱼ = j(j+1)/14 mod 1 | irrational aperiodic — see §4.1 |
| 8 | Tvaritā | 8 | octagonal antiprism | γⱼ = j²/16 mod 1 | aṣṭakoṇa, **Task 2 proof-of-concept target** |
| 9 | Kulasundarī | 9 | nonagonal antiprism | γⱼ = j(j+1)/18 mod 1 | nested trikona, navāmśa |
| 10 | Nityā | 10 | dodecahedron | γⱼ = j/10 | decagonal Penrose-class |
| 11 | Nīlapatākā | 11 | hendecagonal antiprism | γⱼ = j(j+1)/22 mod 1 | Jupiter's prime, 85% Sri Yantra alignment |
| 12 | Vijayā | 12 | icosahedron (dodecagonal axis) | γⱼ = j/12 | dodecagonal soft-matter class |
| 13 | Sarvāṅgasundarī | 13 | 13-gonal antiprism | γⱼ = j²/26 mod 1 | irreducibly aperiodic |
| 14 | Jvālāmālinī | 14 | 14-gonal antiprism | γⱼ = j(j+1)/28 mod 1 | doubled-7-fold |
| 15 | Citrā / Cidagnikalā | 15 | rhombic triacontahedron | γⱼ = j(j+1)/30 mod 1 | full Sri Yantra |

### §4.1 The γ-vector formula

The γⱼ choice for non-trivial Nityās uses **j(j+1)/(2N) mod 1** as the canonical "tithi-advancement" pattern. Reasoning:

- For γ = 0, the multigrid produces the *symmetric* configuration (all lines through origin → degenerate flower pattern).
- For γⱼ = j/N (linear), the multigrid is a Bravais-lattice-equivalent configuration if N is crystallographic, and the standard Penrose-class quasicrystal if N is non-crystallographic.
- For γⱼ = j(j+1)/(2N) (quadratic), the multigrid is *generic* — neither degenerate nor periodic, exhibiting the full quasicrystalline aperiodicity.

The j(j+1)/2N pattern is **one defensible choice** that distributes the offsets evenly without producing degeneracies. It is *not* uniquely specified by the classical Sri Vidyā tradition. The classical tradition specifies each Nityā's *visible geometry* (number of petals, internal triangles, etc.) but does not specify γ-vectors of an underlying lift.

This is one of the brief's anticipated places to **flag honestly**: the mapping from classical visible-yantra-specification to mathematical γ-vector is a **synthesis**, not a derivation. **OBSERVED:SYNTHESIS** — alternative γ patterns may match the classical specifications equally well; verification against published yantra renderings (Task 3 verification criterion) will determine which γ-pattern best reproduces the tradition.

### §4.2 Phason-flip schedule across the lunar cycle

Phason flips occur as γ evolves. For the Atlas tithi-cycle integration (Task 4), γ should evolve continuously as the lunar cycle advances. The recommended schedule:

- **Discrete tithi advancement** (Nityā transitions): γ jumps from one Nityā's vector to the next at integer-tithi boundaries.
- **Continuous within-tithi evolution**: γ rotates smoothly within each Nityā's geometry. The rotation rate is `2π / (24 hours)` for a one-tithi-per-day approximation. Phason flips occur many times per tithi at this rate.
- **Cycle closure**: at tithi 30 → tithi 1, γ returns to its initial configuration. The full lunar cycle is one complete phason traversal.

This is testable. The next session implementing Task 4 should verify that:
1. Phason flips are visually identifiable (discrete tile-rearrangement events)
2. The flip rate matches the theoretical prediction for the chosen N and viewport size
3. Steady-state at integer-tithi-boundaries shows the per-Nityā distinct geometry

---

## §5. Honest gaps

### What I am confident about

- **De Bruijn multigrid → tiling extraction is correct math** for any N, periodic and aperiodic alike. (Senechal 1995 Ch. 7; de Bruijn 1981.)
- **Per-Nityā N values** are correct from `DEVI_N` and consistent with the classical Sri Vidyā tradition's specifications for each yantra's geometric symmetry.
- **Phason flips are detectable** via the multigrid line-coincidence criterion and correspond to lattice-point boundary-crossings in (N-2)-D internal space. (Senechal 1995 Ch. 5.)
- **The recommendation to use de Bruijn over cyclotomic-lift or composite-3×5** is a defensible engineering choice (tractability, builds on existing code) — neither approach is mathematically wrong, but de Bruijn is the path of least resistance for the brief's deliverables.

### What is OBSERVED:SYNTHESIS (not derived)

- **The j(j+1)/2N γ-pattern.** This is one defensible choice; the classical tradition does not specify γ-vectors. Other patterns may produce visually equivalent or even closer matches to published yantra renderings. This must be empirically validated against the tradition in Task 3.
- **The per-Nityā γ assignments (Table in §4).** The mapping of classical-tradition yantra → mathematical γ-vector is interpretive. Where tradition specifies a yantra in geometric terms (e.g., "8 lotus petals around a central trikona"), the corresponding γ may need adjustment to reproduce that exact geometry rather than a generic 8-fold field.

### What is SOURCE_NEEDED

- **Specific 15-fold quasicrystal literature beyond Senechal/de Bruijn.** I am confident the de Bruijn approach generalizes to 15-fold, but explicit 15-fold quasicrystal construction papers are sparse compared to 5-fold (Penrose) and 8-fold (Ammann–Beenker). A targeted lit search via WebSearch or RRUFF database scan is warranted before final commitment to the construction. This is a Task 1 follow-up, not a blocker.
- **Sri Vidyā tradition's per-Nityā yantra specifications.** The classical tradition has multiple lineages; specifications differ. Standard reference: Lakṣmīdhara's commentary on the Saundaryalaharī, plus Bhāskararāya's Varivasyā-rahasya. A published authoritative source for each Nityā's yantra-geometry would settle which γ-vectors should be empirically targeted.
- **NPU acceleration for high-density rendering.** Browser JS cannot directly access the NPU; implementation requires a backend (Flask kernel) endpoint that performs the cut-and-project computation and returns the tile-vertex set as JSON. This is Task 5 territory — out of Task 1 scope.

### What might invalidate this approach

The brief explicitly asks for honest discontinuation criteria. If subsequent literature search reveals:

1. **Published evidence that 15-fold tilings produced by de Bruijn multigrid do *not* exhibit the per-Nityā distinct geometries described by Sri Vidyā tradition** — the approach is wrong. Pause and reconsider.
2. **Computational impossibility of real-time rendering at the viewport size required** for the integrated Atlas portal. If the intersection count grows beyond browser budget, approximation is needed (γ-discretization, tile-clustering). Document approximations honestly.
3. **The classical Sri Vidyā tradition specifies geometries that are not derivable from any single higher-dimensional lattice cut** — the framework is wrong. Tradition may use multiple distinct lattices for different Nityās, or the geometry may not be lattice-derivable at all. This would be a substantial finding in its own right.

If any of these emerge in Task 2 verification, **the project should pause before proceeding to Task 3**.

---

## §6. Implementation plan summary

The following is for Tasks 2–5, sized at the brief's estimates:

| Task | Output | Estimate | Key risk |
|---|---|---|---|
| 2 | `static/s4_quasicrystal.html` proof-of-concept for Tvaritā (8-fold) | 8–16 hr | de Bruijn intersection extraction in JS |
| 3 | Full 15-Nityā renderer | 6–10 hr | per-Nityā γ-pattern empirical validation |
| 4 | Phason-dynamics animation | 8–16 hr | flip detection, real-time perf |
| 5 | Atlas panchanga integration | 2–4 hr | tithi → γ mapping in live state |

Total: **24–46 hours** beyond Task 1. Sized for 4–6 future sessions.

A minimum-viable Task 2 skeleton (de Bruijn intersection extraction at the simplest case, drawing tile vertices on Canvas2D) is included alongside this document at `static/s4_quasicrystal.html` so the next session has a runnable starting point — see `proof_of_concept_log.md` for what is and is not implemented.

---

## §7. References

### Primary mathematical sources
- de Bruijn, N.G. (1981) *Algebraic theory of Penrose's non-periodic tilings of the plane I, II*, Proc. Koninklijke Nederlandse Akademie van Wetenschappen 84:39–66
- Senechal, M. (1995) *Quasicrystals and Geometry*, Cambridge University Press — chapter 5 (acceptance windows, internal space) and chapter 7 (multigrid construction) are directly relevant
- Levine, D., Steinhardt, P.J. (1986) *Quasicrystals I: Definition and structure*, Phys. Rev. B 34:596 — foundational physics
- Mackay, A.L. (1981) *De Nive Quinquangula*, Sov. Phys. Crystallogr. 26:517 — independent discovery of multigrid duality

### Atlas substrate references
- `npu_engine/geometry/cut_and_project.py` — existing multigrid implementation
- `npu_engine/geometry/CONSTRUCTION_CHOICES.md` — per-Nityā construction documentation
- `static/s4.html` — existing Chladni-slice JS renderer
- `research/scripts/sri_yantra_alignment.py` — RESEARCH-018/019 alignment metric reproducer (computeAlignment); may be re-used for Task 3 verification of de Bruijn output

### To be sourced (for Task 2 deep dive)
- Specific 15-fold quasicrystal construction papers (SOURCE_NEEDED)
- Lakṣmīdhara commentary, Bhāskararāya Varivasyā-rahasya, or modern Sri Vidyā compendium with explicit per-Nityā yantra geometries (SOURCE_NEEDED)

🙏
