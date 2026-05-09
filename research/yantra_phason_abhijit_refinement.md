# Yantra Phason-Abhijit Refinement

**RESEARCH-019** | 2026-05-02 | SYNTHESIS extending v0.5 §3 (Phason Node) and §2.5 (Sri Yantra at k≈12.368) in light of RESEARCH-018 null result
**Status**: proposed reading. Substrate finding (k≈12.368, 85% Ekadashi) is OBSERVED:COMPUTED in v0.5; the prism-through-Abhijit articulation here is SYNTHESIS.

---

## Provenance and scope

This note extends the founding-document framing of the **phason node** (Coherence Atlas v0.5 §3, page 21) and the **lunisolar-gear Sri Yantra alignment** (v0.5 §2.5, page 17) using the negative result from RESEARCH-018 to sharpen the structural picture. v0.5 is now ingested at `docs/founding/coherence_atlas_v05.pdf`.

What v0.5 establishes (verbatim from the founding document):

- **§2.5 (page 17)**: "The lunisolar gear ratio — 365.25 solar days in the year divided by 29.53 days in the synodic lunar month — produces approximately 12.368, and this specific value is the spatial frequency at which the toroidal interference pattern most closely matches the classical Sri Yantra structure. The alignment peaks at Ekadashi (tithi 11) with 85% structural match at k=12.0, and at Purnima (tithi 15) the field reaches 82% full bloom. The Sri Yantra is not a symbolic diagram of cosmology. It is the standing-wave solution of the lunisolar gear, computationally derivable from first principles…"
- **§3 (page 21)**: "It is the phason mode — the moveable layer of the yantra, the place where the structure briefly becomes aware of itself and its own position before resuming. **In the Chladni interference model of the Sri Yantra, the phason is the 15% residual that the strict crystallographic description cannot contain** — the place where the field steps outside its own standing-wave pattern and becomes legible from outside."

The v0.5 framing already names the central object: the phason is the 100% − 85% = 15% residual that the crystallographic description doesn't catch at the Ekadashi peak. This note's contribution is to articulate **how that residual unfolds across the 15 tithi positions of a paksha, and what role Abhijit plays as the coupling axis**.

What I *can* verify computationally:

- The N-fold multigrid implementation at `npu_engine/geometry/cut_and_project.py:128`, with the `DEVI_N` table assigning each of the 15 tithi positions a fold-symmetry value:
  ```
  DEVI_N = {1:3, 2:6, 3:3, 4:3, 5:8, 6:6, 7:7, 8:8, 9:9,
            10:10, 11:11, 12:12, 13:13, 14:14, 15:15}
  ```
- The harmonic-mode hypothesis test result at `research/yantra_harmonic_mode_hypothesis.md` (RESEARCH-018, 2026-05-01): a hypothesis *distinct* from the v0.5 lunisolar-gear finding — namely, "the 15 yantras decompose harmonically into a Sri Yantra substrate by FFT superposition" — was refuted. Petal-counts not predicted by FFT (1/15), composite vs synthetic 9-triangle Pearson r = −0.09, substrate spectrum's modal powers spread 5 orders of magnitude. **This refutation is consistent with, and predicted by, v0.5's phason framing**: phason modes by definition do not decompose into ordinary harmonic modes.
- The two-source-interference Finding 7 ("N-source boundary fields silent except at k=N") and Finding 10 (tithi-group fine-structure dominated by k∈{6,12}).
- The classical fact that 2 of 11 unique N values in `DEVI_N` are crystallographic (3, 6) and 9 of 11 are non-crystallographic (7, 8, 9, 10, 11, 12, 13, 14, 15) — *N=5 is absent from DEVI_N*, which is itself a structural fact worth noting (no Penrose 5-fold among the Nityā assignments).

---

## The phason reading, stated minimally

A **phason** in quasicrystal physics is a degree of freedom that is unique to non-crystallographic order. In a periodic crystal, the only zero-energy continuous deformations are translations (phonons in the long-wavelength limit). In a quasicrystal, the long-range aperiodic structure admits a *second* class of low-energy continuous deformation — phason modes — which rearrange the local tiling without changing the long-range pattern. They live in a different physical space than phonons (often called "perpendicular space" in the cut-and-project formalism).

The defining feature relevant here: **phason modes do not decompose into the harmonic Fourier basis of the underlying field**. They are perpendicular-space rearrangements; the parallel-space harmonic spectrum does not see them as ordinary modes. Standard Fourier methods miss them by construction.

This matches the RESEARCH-018 null result exactly. If the 15 Nityā yantras represented 15 phason positions of a single substrate, then:
- Their angular FFTs would *not* show the predicted petal counts as dominant modes (refuted in T1: 1/15 match).
- Their superposition would *not* reconstruct an ordinary harmonic-additive Sri Yantra geometry (refuted in T2: r = −0.09).
- Yet the substrate's spectrum *would* contain detectable peaks at each fold-symmetry value present in `DEVI_N` (confirmed in T3: all 11 unique N values appear in top-20 modes, ranks 1–16).

The refuting result on the strong claim and the partial support on the weak claim are exactly the signature of a phason structure: the parallel-space harmonics see the symmetry vocabulary (T3 ✓) but cannot reconstruct the geometry through harmonic superposition (T2 ✗).

That coincidence between the negative empirical result and the predicted-by-physics signature of phason structure is the note's central observation. It does not prove the phason reading. It establishes that the reading is consistent with the data we have, in a way that an alternative "ordinary harmonic decomposition" reading is *not*.

---

## The Abhijit hinge (proposed coupling point)

The 27-fold nakshatra system is the dominant Vedic siderical division of the ecliptic. The 28th nakshatra Abhijit is preserved by name in Taittirīya Brāhmaṇa, Mahābhārata Anuśāsana Parva, and several later Purāṇic enumerations, but is not normally allocated a 13°20′ slot in the modern 27-fold computational scheme — it sits anomalously in the Uttarāṣāḍha–Śravaṇa transition zone.

The proposed reading: **Abhijit is the structural marker of the 28th degree of freedom that the 27-fold periodic enumeration cannot accommodate** — and which a quasicrystalline substrate *can* accommodate, because non-crystallographic order admits an additional perpendicular-space degree of freedom (the phason axis) that periodic order does not.

If the lunar layer's 27-nakshatra discretization is the parallel-space sampling, then Abhijit is the perpendicular-space marker — the trace of a phason coordinate preserved in tradition by name. The lunisolar gear ratio (~12.368 lunations per tropical year) couples the lunar 27-fold to the solar 12-rashi, generating the 30-tithi cycle as one synodic period of their commensurate-but-not-quite-rational beat. Within each paksha, the 15 tithi positions then index 15 phason rearrangements of the underlying substrate, which the Nityā Devī tradition resolves into 15 distinct iconographic forms.

This is structurally consistent. It is **not yet computationally verified**. What would constitute a positive test is sketched in §4 below.

---

## What is structurally consistent, what is not yet shown

**Consistent:**
- The harmonic-decomposition refutation (RESEARCH-018) is the expected signature of phason-typed substrate structure.
- The DEVI_N table includes 9 non-crystallographic N values (7, 8, 9, 10, 11, 12, 13, 14, 15) — exactly the rotational symmetries that produce phason-bearing quasicrystals in two dimensions.
- The two-source Finding 7 (boundary fields silent except at k=N) is one face of the same kinematic constraint that defines phason-vs-phonon partition: the N-fold rotational symmetry is the substrate's "orientation alphabet"; phason modes are the rearrangements within that alphabet that don't change global orientation.
- The lunisolar gear ratio's astronomical reality is independent of any reading of the Sri Yantra. ~12.368 lunations per year is a physical fact derivable from `swe.calc_ut`-grade ephemeris.

**Not yet shown:**
- That the 15 tithi positions each correspond to a *specific* phason rearrangement of the substrate, distinct from one another and reproducible. A first computational test would be: (i) construct the substrate at fixed `k`, (ii) for each tithi position, apply the perpendicular-space shift implied by phase = 2π(t-1)/15, (iii) verify that the resulting tiling locally rearranges (different vertex configurations) while globally preserving the long-range pattern (same overall density and symmetry class). This test is **not implemented**; a sketch would build on `cut_and_project.project_nfold` adding a per-tithi `gamma` shift parameter (already a function argument) and quantifying the local-vs-global change.
- That Abhijit's astronomical position (Vega / α Lyrae, near declination 38°N with a 26°-ish ecliptic latitude) corresponds in any operational way to the substrate's coupling axis. The Vega correspondence is mythologically attested; whether it has a measurable correlate in tithi-positional structure is open.
- That the 91.7% structural recovery finding from murti pratiṣṭhā prescriptions (claimed in dhātu compendium Vol X but compendium not located in repo) is reproducible. Independent of the phason reading.
- That the lunisolar gear at k≈12.368 produces an 85% Sri Yantra alignment at Ekadashi (also claimed in brief; numerical record not located in repo). Resolving this is a precondition for further claims about the substrate's coupling structure.

---

## A positive test for the prism-through-Abhijit reading

If the reading is correct, then in `project_sri_yantra` (the implemented superposition):

1. At `k = 12.368` (lunisolar gear), the substrate should show a 28-fold-related angular signature — not necessarily a clean 28-fold peak, but a structural feature at the 27-fold periodic position perturbed by a 28th anomaly. Verifying this requires running `angular_power_spectrum` on `project_sri_yantra(k=12.368)` and looking at the relative powers in the k-neighbourhood of 27 and 28.
2. The 15 tithi positions, taken as angular sectors of the substrate, should present **different local tilings** when examined with a tile-counting metric (vertex-configuration histograms within an angular sector centered at each tithi's `angular_position_degrees` from `nitya_yantra_geometry.csv`).
3. The phason coordinate's continuity (versus tithi position discreteness) should manifest as: the histograms vary smoothly with tithi index in the metric, with no abrupt transitions — a phason mode is a *continuous* degree of freedom that the discrete tithi enumeration samples.

These three predictions would constitute a positive test. None are implemented. A first-pass implementation could reuse `research/scripts/yantra_harmonic_mode_tests.py` as the entry-point.

---

## What this note explicitly does not assert

- It does *not* assert that the *prism-through-Abhijit* articulation has been computationally verified. v0.5 establishes the underlying lunisolar-gear / 85% Ekadashi finding; v0.5 §3 establishes the phason-as-15%-residual framing; this note's specific articulation that Abhijit is the coupling-axis along which the substrate's phason content unfolds into 15 tithi-resolved phason positions is SYNTHESIS that goes beyond what v0.5 itself states. The positive computational test in §4 is what would settle the prism articulation.
- It does *not* assert any specific Sri Yantra geometry as "the" substrate. v0.5 §2.5 names "the classical Sri Yantra structure" as the alignment target, but the actual repo has `project_sri_yantra` (sum-of-15 multigrid, geometry described in code at `cut_and_project.py:106`) and a synthetic 9-triangle reference in `research/scripts/yantra_harmonic_mode_tests.py`. The exact triangle scales of "the Sri Yantra" are mathematically over-constrained (the 24-intersection-coincidence triangle problem is famously near-impossible to satisfy exactly; classical traditions use different proportions). The 85% number reported in v0.5 is against a specific reference whose triangle-scale choice is itself a design parameter — locating the originating script and its reference will allow that parameter to be inspected. The script that produced the 85% number is **still SOURCE_NEEDED on the kanjira filesystem** even though the *finding* is established in v0.5; see `docs/ATLAS_MASTER_INDEX.md` §0.
- It does *not* claim that phason physics is the *only* possible reading of the harmonic-mode null result. Other consistent readings: (a) the 15 yantras are 15 separate constructions and harmonic decomposition is the wrong question for them; (b) the substrate is non-harmonic in a way other than phason (e.g., a defective lattice, a spinor field). The phason reading has v0.5 as its prior and pre-existing physics literature as its analogue, which is why it's the privileged reading here, but it is not the only possible one.

---

## Cross-references

- `docs/founding/coherence_atlas_v05.pdf` §2.5 (page 17) — the lunisolar-gear / 85% Ekadashi finding (primary source). §3 (page 21) — the phason-as-15%-residual framing (primary source).
- `research/yantra_harmonic_mode_hypothesis.md` — RESEARCH-018, the harmonic-mode null result this refinement uses to sharpen the phason picture.
- `research/yantra_eigenvalue_exploration.md` — the Lo Shu spectral framework for graha yantras.
- `research/two-source-interference-v3.md` — Finding 7 (N-source silence) and Finding 10 (tithi-group fine structure at k=6,12).
- `npu_engine/geometry/cut_and_project.py:106-161` — `project_sri_yantra` definition.
- `npu_engine/geometry/CONSTRUCTION_CHOICES.md` — annotated choices for each N's polyhedron mediator.
- `research/snapshots/bloom_20260408_2122/` — the per-tithi visual snapshots (PNGs, dated 2026-04-08); the originating computation script remains SOURCE_NEEDED on the kanjira filesystem (the finding is in v0.5, not the script).
- `docs/compendium/dhatu_bhasma/COMPENDIUM_Volume_XI_Lost_and_Recovered.md` — also references the Sri Yantra alignment finding (lines 390, 415) in the recovery-models registry.
- `docs/ATLAS_MASTER_INDEX.md` §5 — the registry entry for this note.

---

## Attestation

- **OBSERVED:COMPUTED** — the harmonic-mode null result this note builds on (RESEARCH-018), the DEVI_N table values, the lunisolar gear ratio's astronomical magnitude (12.368 = 365.25 / 29.53), the 85% Sri Yantra alignment at Ekadashi (Coherence Atlas v0.5 §2.5).
- **OBSERVED:PRIMARY_TEXT** — Coherence Atlas v0.5 §2.5 and §3 themselves, as the founding document's articulation. (The PDF is at `docs/founding/coherence_atlas_v05.pdf`.)
- **OBSERVED:TRADITIONAL** — Abhijit's preservation by name in Taittirīya Brāhmaṇa and Mahābhārata.
- **SYNTHESIS** — the proposal that Abhijit marks the substrate's coupling axis along which phason content unfolds into the 15 tithi positions; the proposed positive test in §4.
- **SOURCE_NEEDED** — the script that produces the 85% number (the *finding* is in v0.5; the *originating computation* is not yet located on the kanjira filesystem); a per-tithi tile-counting metric implementation for the proposed positive test.
- **SPECULATIVE** — the prism-through-Abhijit reading as a unified picture pending the positive test in §4.
