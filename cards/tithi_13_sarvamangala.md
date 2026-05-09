# Sarvamangala / Sarvangasundari · Tithi 13 · Card

**Source compilation**: 2026-05-03
**Schema version**: Atlas Tithi Card Master Table (user-provided, 2026)
**Population status**: ~58/82 fields sourced, ~24 SOURCE_NEEDED flags
**Naming discrepancy noted**: tithi_master.csv and nitya_yantra_geometry.csv use **Sarvamaṅgalā** ("auspicious in all"); nitya_devi_master.csv uses **Sarvāṅgasundarī** ("beautiful in all limbs"). The two names refer to the same Nityā position by tradition; the user-provided filename `tithi_13_sarvamangala.md` follows the tithi/yantra-CSV naming. Both names are preserved here.

---

## Identity

- **tithi_number**: 13
- **tithi_name**: Trayodaśī
- **paksha_mode**: Both shukla and krishna. Kāmadeva is tithi deity. Quality: mixed. (tithi_master.csv)
- **devi_name**: Sarvamaṅgalā / Sarvāṅgasundarī
- **devi_alt_names**: Sarvāṅgasundarī (सर्वाङ्गसुन्दरी, "beautiful in all limbs") in nitya_devi_master.csv. Sarvamaṅgalā (सर्वमङ्गला, "auspicious in all") in nitya_yantra_geometry.csv and tithi_master.csv. Bija: Aim Klīm Sauḥ. Mantra: Om Aim Klīm Sauḥ Sarvāṅgasundaryai.
- **seed_keywords**: beauty-of-all-limbs, auspicious-in-all, Kāmadeva-tithi, earth-sattva, shringara, Chandra-graha, mirror+lotus, 13-fold quasicrystal

## Canonical Devi

- **iconography_summary**: Beautiful in every limb — she is the perfection of form as a pathway to formlessness. **Body color, garments, ornaments, mudras, vahana all empty in nitya_devi_master.csv**. Carries mirror (darpaṇa) and lotus (padma) per the `weapon` short field. The mirror-lotus pair is the beauty-witnessing-itself signature: the mirror reflects, the lotus is what is reflected. (nitya_devi_master.csv, OBSERVED:PRIMARY for name/bija/description/weapon; many fields empty)
- **weapons_items**: Mirror (darpaṇa), lotus (padma). **Full weapons listing empty in nitya_devi_master.csv**. The mirror is unique among Nityā implements — only Sarvāṅgasundarī carries it. Capability signature: SOURCE_NEEDED.
- **mudras_gestures**: SOURCE_NEEDED.
- **vahana_mount**: SOURCE_NEEDED.
- **body_color**: SOURCE_NEEDED. Color hex: #daa520 (goldenrod, lighter than Vijayā's dark goldenrod) — represents her field, encoding the warm-beauty signature.
- **ornamentation**: SOURCE_NEEDED.
- **faces_arms_count**: SOURCE_NEEDED.
- **shakti_statement**: Beauty in all limbs — the form-perfection-as-formlessness shakti. The full-body beauty is not aesthetic surface but the moment when form so fully expresses its essence that it points beyond itself. (nitya_devi_master.csv, OBSERVED:PRIMARY for name; functional interpretation SYNTHESIS)
- **expanded_function**: Sarvāṅgasundarī is the thirteenth Nitya — the form-perfection position, immediately preceding the burning-away-of-residue Jvālāmālinī (T14) and the full-bloom Citra (T15). Where Vijayā (T12) is dharmic-victory and Jvālāmālinī (T14) is karmic-burning, Sarvāṅgasundarī (T13) sits between them as **the perfection-of-form before its dissolution into pure light**. The N=13 yantra symmetry (devi_engine.py DEVI_N) is 13-fold — non-crystallographic, fully quasicrystalline, related to the 5-fold Penrose family by the Fibonacci-prime-step structure (5, 8, 13 are consecutive Fibonacci numbers; 13 is the first prime in this sequence). Her graha is Chandra (Moon, k=1, M=18) — same as Bhagamālinī (T2). The two Chandra-Devis are T2 and T13 (with T15 being Chandra by tithi-deity but Citra's specific graha varies). (SYNTHESIS from nitya_devi_master.csv + CONSTRUCTION_CHOICES.md)
- **bhava_mood**: Shringara (love/beauty). Rasa: shringara. Element: earth. Guna: sattva. The earth-sattva-shringara triple is unique among the 15 Nityas — the only Nitya with element=earth in the rasa-shringara cluster. Earth-shringara is the "embodied beauty" signature; Kāmeśvarī's fire-rajas-shringara is desire-as-impulse, Sarvāṅgasundarī's earth-sattva-shringara is desire-as-fulfilled-form. (nitya_devi_master.csv, OBSERVED:PRIMARY)
- **mantra_bija**: Aim Klīm Sauḥ — three chained bijas. **The first appearance of Sauḥ (the para-bija) in any Nityā mantra**. Sauḥ is the supreme bija of Para-Trika tantra (Kashmir Shaivism), encoding the "śiva-śakti-jīva integration." Aim (Sarasvatī) + Klīm (Kāma) + Sauḥ (integration) — wisdom-attraction-integration as the three-step mantra of full-bodied beauty. (nitya_devi_master.csv, OBSERVED:PRIMARY)

## Lunar/Time

- **lunar_phase_arc**: 144°-156° from conjunction (shukla trayodaśī), or 324°-336° (krishna trayodaśī). The 13th tithi approaches but does not reach opposition (180°).
- **phase_quality**: **Mixed** (tithi_master.csv). Good for: competitions, legal matters, confronting challenges (same set as Tritīyā T3 and Aṣṭamī T8). Avoid: marriage, travel, peaceful activities. Tithi deity: **Kāmadeva** — the god of love/desire, structurally aligned with the shringara rasa of Sarvāṅgasundarī.
- **nitya_cycle_position**: 13th of 15 — the form-perfection position immediately preceding burning (T14) and full bloom (T15). The Kāmadeva tithi-deity makes this a desire-position; the form-perfection of T13's Devi is the ripening of desire into beauty before its consumption in fire (T14) or expansion in bloom (T15).
- **weekday_links**: Trayodaśī's tithi deity is Kāmadeva. Sarvāṅgasundarī's graha correspondence is Chandra (Moon) per devi_master — Monday (Somavara). yantra_geometry CSV assigns **Mercury** to tithi 13 — discrepancy. devi_master Chandra treated as authoritative. k=1, M=18.
- **nakshatra_overlays**: SOURCE_NEEDED: Trayodaśī belongs to the **Jaya group** (T3, T8, T13 — victory tithis). All gandanta nakshatras AVOID Jaya tithis (RESEARCH-017 Finding 11). T13 specifically does not receive gandanta amplification — same null-amplification as T3 and T8.

## Yantra

- **yantra_family**: Downward triangle (trikona) with eight petals and bhupura. Triangle scale 0.66, inner circle 0.7. (nitya_yantra_geometry.csv, attested SYNTHESIS — "Sarvamaṅgalā is described with a lotus yantra but geometry details are absent; assume a downward triangle with eight petals and bhūpura.")
- **yantra_geometry_notes**: Classical yantra geometry partial — the source describes "a lotus yantra" but does not specify triangle structure. The CONSTRUCTION_CHOICES.md uses N=13 multigrid for the wave projection — 13-fold symmetry, fully quasicrystalline.
- **yantra_symmetry_order**: N=13 (13-fold, fully quasicrystalline). 13 is the first **Fibonacci prime** that appears in DEVI_N; the Fibonacci structure 5, 8, 13 is a sub-sequence of the yantra fold counts (T8=8 is the 6th Fibonacci, T13=13 is the 7th Fibonacci — the consecutive Fibonacci pair appears at consecutive tithi positions T8 and T13, separated by 5 tithi-steps). Among the 15 Nityas, only Sarvāṅgasundarī has N=13. (devi_engine.py DEVI_N + Fibonacci structure observation)
- **yantra_center_logic**: Bindu as point. Inner circle scale 0.7. The 13-source pattern's central interference produces a 13-fold rosette in the inner ring.
- **yantra_outer_boundary**: Bhupura with 4 gates. Interference radius fraction: 0.3 (very tight). Wave function: cosine, frequency multiplier: **4**, angular position: 288°.
- **yantra_layer_count**: 3 layers minimum: bindu → 8-petal lotus → bhupura. Triangle at 0.66 scale.

## Field Math

- **graha_k**: Chandra = k=1, magic constant **M=18**. (yantra_eigenvalue_exploration.md, Finding 2). Same graha and same M as Bhagamālinī (T2). The two Chandra-Devis (devi-master attribution) are T2 and T13.
- **magic_constant_M**: 18 (Chandra, k=1). Eigenvalues: {18, +4.899, -4.899}. (Finding 1)
- **invariant_secondary_modes**: +/-2sqrt(6) = +/-4.8990. (Finding 1)
- **coherence_ratio**: lambda_2/M = 4.899/18 = **0.2722** (Chandra). The 2nd most polarized graha. Same value as T2. (Finding 2)
- **eigenvector_axes**: For Chandra (k=1): same as T2. (Finding 6)
- **brahmasthana_definition**: Uniform eigenvector at every Kronecker level. (Finding 4)
- **kronecker_level**: Level 1: 3x3, M=18. Level 2: 9x9, M=324. Level 3: 27x27, M=5832. (Finding 3)
- **navagraha_composite_role**: Chandra at k=1. Moon's Lo Shu placement is NW (Vayu) — same as T2. (Finding 5)

## Wave/Interference

- **boundary_harmonic_mode**: At k=13: not a classical jyotish aspect. The k=13 harmonic is the 27.69° aspect — non-classical. (two-source-interference-v3.md, Finding 8)
- **two_source_pattern**: A(theta) = 2 * cos(k(theta - midpoint)) * cos(k * separation/2). At k=13: constructive maximum at separation = 360/13 ≈ 27.69°. (Finding 8)
- **nodal_interior_pattern**: For N=13 multigrid in disk interior: aperiodic, fully quasicrystalline. The 13-fold pattern is structurally related to the 5-fold Penrose by the Fibonacci-substitution rules (5→8→13 in the Fibonacci sequence corresponds to substitution-tile-replication levels). (CONSTRUCTION_CHOICES.md)
- **ring_vs_disk_distinction**: Boundary: 13-source pattern silent except at k=13. Disk: aperiodic 13-fold tiling. (Finding 7)
- **gandanta_gain**: Trayodaśī is Jaya — gandantas avoid Jaya. **No gandanta amplification.** Same null-amplification as T3 and T8. (Finding 11)
- **wave_panchaka_relation**: Orthogonal: r = -0.011. (Finding 12)
- **quantized_prime_modes**: 13 is a prime, but **not a planetary prime** ({3,5,7,11} are Mercury, Venus, Mars, Jupiter; Saturn's count of 29 is sometimes excluded). 13 is the first prime beyond the planetary primes. Astronomical relevance: 13 is the count of full moons in some lunar years (the leap year addition); a "blue moon" year has 13 full moons. (planetary-primes-v1.md, Section 2)

## Quasicrystal/Chladni

- **quasicrystal_line_style**: 13-fold multigrid. Fully quasicrystalline, with Fibonacci-substitution structure shared with the Penrose 5-fold and 8-fold families. (CONSTRUCTION_CHOICES.md)
- **nodal_density**: SOURCE_NEEDED. interference_radius_fraction = 0.3 (the tightest yet — even tighter than T11 and T12).
- **radial_bands**: 4 radial nodes within unit disk (frequency_multiplier=4).
- **interference_centers**: Primary = bindu. Secondary maxima at 13 vertices of inscribed regular 13-gon at interference_radius=0.3. The 3D mediator polyhedron: **13-gonal antiprism** (26 triangular side faces + 2 13-gonal caps = 28 faces total — note: 28 = 27+1 = nakshatras+Abhijit, the structural nakshatra count). The 26 triangular sides correspond to the 27 nakshatras minus 1 — the antiprism's geometry naturally encodes the Abhijit-removed-from-27 structure that the prism-through-Abhijit refinement (RESEARCH-019) discusses. (CONSTRUCTION_CHOICES.md, polyhedron_mediator)

## Pasaka/Magic Cube

- **cube_type**: Andrews 1917. M=42. (magic_cube_analysis.json)
- **cube_magic_constant**: M = 42. (Finding 1)
- **cube_layer_squares**: layer eigenvalues {42, +/-9, ±9}. (Finding 1)
- **cube_invariant**: +/-9. Rational. (Finding 2)
- **cube_center_value**: 14. (Finding 3)
- **cube_associative_sum**: 28 = n^3+1. **Note: 28 = T13's antiprism mediator face count. The Magic Cube's antipodal sum equals the 3D mediator's face count for N=13.** (Finding 4)
- **cube_tensor_isotropy**: sigma_1 = 72.75. (Finding 6)
- **cube_kronecker_scaling**: M_n = 42^n. (magic_cube_extension.json)
- **cyclic_composite_eigenvalues**: 9x9: M=126, eigenvalues {126, +/-2.598, 0×4}. (Finding 2)
- **loshu_weighted_cube_mode**: Lo Shu collapses to {126, 0, ...}. (Finding 3)

### Pasaka at total=13

**SOURCE_NEEDED: System mismatch** — pasaka totals are 3–12 only (3 dice each ranging 1–4 give max 12). **No pasaka outcome corresponds to total=13**. This is identical to the situations at T1 (total=1, no outcome) and T2 (total=2, no outcome). Tithis 13, 14, 15 all face the same gap on the upper end of the deck. Possible alternate mappings: (a) mod-12 reduction (13 mod 12 = 1, mapping to Kṛta total=3 — strange); (b) deck-position 13 (ID 13 in pasaka.csv = Tuṣṭi 1,4,1 total=6); (c) define a deck-extension for tithis 13–15. The Sivaduti card (T7) used direct numeric matching; for T13 we acknowledge the mismatch as a structural feature of the pasaka system rather than papering over it.

## I Ching

- **hexagram_id**: SOURCE_NEEDED. Numerical correspondent: hexagram 13 (Tóng Rén, "Fellowship with Men") — community based on shared principle. The pairing is structurally interesting: Trayodaśī's mixed-quality tithi with Kāmadeva-deity is the "shared desire" tithi; Tóng Rén is the "shared principle" hexagram. Desire and principle as fellowship-foundations.
- **hexagram_arrangement**: Fuxi ↔ King Wen spectral opposites. (iching_spectral_analysis.json)
- **rank_complexity**: Q6 hypercube eigenvalues, Pascal row 6. (Finding 3)
- **yin_yang_balance_mode**: XOR-with-63 perfect partition. (Finding 6)
- **hypercube_distance_signature**: Hamming rank 7. (Finding 5)
- **pascal_row_signature**: Row 6, total 64. (Finding 3)

## Lo Shu x I Ching Bridge

- **trigram_loshu_weight_map**: Tithi 13 exceeds 1-9 trigram-weight range. Mod-9: 13 mod 9 = 4 → **Xun** (Wind/Wood). Same trigram-mod as Bheruṇḍā (T4) — both T4 and T13 mod-9 to Xun. The Wind-trigram pair at T4 (Bheruṇḍā fierce-protection) and T13 (Sarvāṅgasundarī beauty-of-all-limbs) is structurally non-obvious — fierce wind and gentle wind, perhaps. (loshu_iching_interaction.json)
- **weighted_spectral_breaking**: 7 → 27 unique eigenvalues. (test4_weighted_Q6)
- **spectral_gap_change**: 2.0 → 0.4624. Fiedler 0.1944. (test5_spectral_gap)

## Alchemical/Bhasma

- **material_classical_class**: Chandra → Rajata (silver) and Mukta (pearl). Same as Bhagamālinī (T2). See T2 card for full discussion.
- **material_scientific_type**: Silver (Ag, element 47); Pearl (CaCO3 aragonite + conchiolin protein matrix).
- **base_material**: Rajata for metallic preparation; Mukta for gem preparation.
- **prepared_substance_type**: Rajata Bhasma; Mukta Pinga.
- **shodhana_media / bhavana_media / marana_cycles / puta_profile / particle_scale_overlay**: SOURCE_NEEDED. (See T2 card.)
- **quality_tests**: Standard bhasma tests. Per dhātu compendium Volume III, Rajata Bhasma is empirically Ag2S (acanthite) — chemistry diverges from "pure silver" expectation.
- **completion_stop_rule**: Quality tests pass.
- **phase_transformation**: Ag → Ag2O → eventually Ag2S in sulphur-rich preparation. (Volume III)
- **safety_conditions**: Rajata Bhasma generally safe; argyria risk at chronic high doses.

## Graha/Material

- **graha_material_map**: Chandra → Rajata, Mukta. (Same as T2.)
- **friend_enemy_interaction**: See T2 card. The Moon-Mercury asymmetry (Ag-Hg amalgam) is the structurally significant case.
- **ritual_vs_medical_flag**: Both. Pearl/silver have extensive ritual and medical use.

## Plant/Ecology

- **plant_allies**: SOURCE_NEEDED. Traditional Chandra plants: Brāhmī, Śatāvarī, Yashtimadhu. (Same as T2.)
- **processing_plants / doctrine_of_signatures_overlay / astrobotanical_timing**: SOURCE_NEEDED.

## Body/Therapeutics

- **dosha_predicates**: Tithi 13 element: water (tithi_master.csv), guna: sattva. Devi element: earth (nitya_devi_master.csv), guna: sattva. Chakra: Sahasrara (Chandra/Moon correspondence) — beyond elements, transcendent sattva, Vata, Nirvana Shakti. (chakra_cross_domain.csv). The water/earth/transcendent triad with sattva-sattva-sattva is the **embodied-transcendence profile** — fluid (water) + grounded (earth) + transcendent (beyond) at sattva grade. The Sahasrara chakra placement aligns with Sarvāṅgasundarī's "perfection of form as pathway to formlessness" — the beautiful body that points beyond itself.
- **dhatu_targets**: SOURCE_NEEDED. Chandra governs Rasa dhatu. Same as T2.
- **organ_targets**: Sahasrara at crown: pituitary, hypothalamus, central nervous system. (chakra_cross_domain.csv). Associated nakshatras: Rohini, Hasta, Shravana — Chandra-ruled.
- **indication_clusters**: SOURCE_NEEDED.
- **anupana_vehicle**: SOURCE_NEEDED.
- **preparation_dependency_warning**: Same as T2.

## Prime/Morphology

- **prime_signature**: 13 is a **prime, but not a planetary prime**. It is the **7th Fibonacci number** and the **2nd Fibonacci prime** (after 2,3,5 — though 2 and 3 are technically Fibonacci primes too: 2=F3, 3=F4, 5=F5, 13=F7, then 89=F11, 233=F13...). 13 also appears in mammalian vertebral counts (per `vertebral-primes-v1.md` Finding 4: "Dog, cat, tiger, lion, sheep all share C7 T13 L7 = 27" — 13 thoracic vertebrae). The dog-cat-felid-sheep group has T=13 thoracic, distinct from human T=12. (planetary-primes-v1.md + vertebral-primes-v1.md Finding 4)
- **morphology_correlates**: **T13 = 13 thoracic vertebrae** in dogs, cats, tigers, lions, sheep — animals not central to human anthropology but central to nakshatra-yoni assignments (the lion-tiger-dog-cat group). The 13-fold structure links Sarvāṅgasundarī to the carnivore-mammal yonis through anatomical thoracic count. **Sarvāṅgasundarī's "beautiful in all limbs" applies to a 13-thoracic body archetype** — the lion-yoni body with full presacral count of 27 (= nakshatra count!) per `vertebral-primes-v1.md` Finding 4 ("27 mobile vertebrae, the nakshatra count").
- **sri_yantra_region_relation**: 13 not in {3,5,7,11}. Not directly part of the 44-region overlay. But the 13-fold antiprism mediator's 28 faces = 27 nakshatras + Abhijit, structurally aligning with the prism-through-Abhijit refinement (RESEARCH-019). (planetary-primes-v1.md §3 + RESEARCH-019)

## Sound/Rhythm

- **svara_link**: SOURCE_NEEDED. Chandra's traditional svara is **Sa** (Ṣaḍja, the tonic). Same as T2.
- **raga_link**: Chandra-associated ragas in raga_data.csv: Bhūp, Bihāg, Deśa, Bāgeshrī. Same set as T2. **Deśa** (water-sattva, adbhuta) and **Bāgeshrī** (water-sattva, shringara) are the closest matches for Sarvāṅgasundarī. Bāgeshrī's shringara rasa is the exact match for her stated rasa; the water element instead of earth is the variance.
- **tala_link**: SOURCE_NEEDED. The 13-fold yantra symmetry suggests **13-beat cycles**. **Aṣṭa-mangala tāla** in some Carnatic traditions is 13-beat; in Hindustani, the 13-beat **Yati / Mata tala** (rare) carries the structure. The 13-beat is unusual in concert tradition but exists in temple and ritual contexts.

## Vastu/Spatial

- **mandala_zone_map**: Chandra at k=1 places yantra values as Lo_Shu + 1*J = {5,10,9;12,6,4;7,8,11}. Brahmasthana center = 6. Same as T2. (yantra_eigenvalue_exploration.md)
- **directional_emphasis**: Chandra governs NW (Vayu corner). Same as T2.

## Visual Grammar

- **palette_logic**: Primary: #daa520 (goldenrod, from nitya_devi_master.csv). Secondary: #FFE0B2 (pale peach, from nitya_yantra_geometry.csv). Bindu: #FF6D00 (saturated orange). Line weight: medium. The earth-sattva-Chandra signature with shringara iconography produces a warm-earthy palette: goldenrod field, peach accents, orange bindu — the autumn-harvest beauty signature.
- **density_logic**: interference_radius_fraction = 0.3 (very tight). The 13-fold quasicrystalline field with frequency_multiplier=4 produces extremely concentrated central structure. Render with the 13-rosette pattern dominant.
- **line_weight_logic**: Medium.
- **panel_layout**: SOURCE_NEEDED.
- **symbol_strip**: SOURCE_NEEDED for capability_signature. Iconographic: **mirror (darpaṇa) — unique to T13** + lotus (padma). Bija: Aim Klīm Sauḥ (the only Nityā mantra to use Sauḥ).
- **caption_motto**: "Beautiful in every limb — she is the perfection of form as a pathway to formlessness." (nitya_devi_master.csv)

---

## Cross-layer observations

The first cross-layer resonance is the **mirror-darpaṇa as the unique iconographic instrument**. Among all 15 Nityā Devīs, only Sarvāṅgasundarī carries the mirror. The mirror is the "form-witnessing-itself" instrument — beauty that knows itself as beauty. In tantric philosophy, the mirror IS the Devi: the cosmic śakti reflects the absolute back to itself, generating the appearance of difference through which difference is dissolved. Sarvāṅgasundarī's name "Beautiful in all limbs" is what the mirror sees when it looks at the Devi; the answer to "who is in the mirror?" is "the Devi who is in all limbs of all creatures." The lotus accompanies the mirror as "what is reflected" — the lotus is the form that beauty takes; the mirror is the witness-mode that recognizes form as beauty.

The second resonance is the **Sauḥ-bija unique appearance and the para-Trika anchoring**. Sarvāṅgasundarī's mantra Aim Klīm Sauḥ is the only Nityā mantra to include Sauḥ. Sauḥ is the supreme bija of Para-Trika (Kashmir Shaivism), encoding "śiva-śakti-jīva integration." Wisdom (Aim) + attraction (Klīm) + integration (Sauḥ) is a complete cosmological progression that ends in non-dual integration. **Sarvāṅgasundarī's position at T13 carries the Para-Trika mantra-completion** — the form-perfection moment is also the integration-with-source moment. The mirror she carries IS Sauḥ in iconographic form: the integration of seer and seen.

The third resonance is the **Fibonacci structure embedded in the high-N Nityas**. The Fibonacci sequence is 1, 1, 2, 3, 5, 8, 13, 21, 34, 55... Among DEVI_N values: T8 = 8 (6th Fibonacci) and T13 = 13 (7th Fibonacci) are consecutive Fibonacci numbers at consecutive odd-position tithi numbers (8 = 2³ is also a Fibonacci-prime-relative; 13 IS a Fibonacci prime). The Fibonacci-substitution rules that generate the Penrose 5-fold (T5 absent from DEVI_N) extend to 8-fold (T8) and 13-fold (T13) tilings. **The high-Nityā tithi positions 8 and 13 are the Fibonacci-sister positions in DEVI_N**, separated by 5 tithis (also Fibonacci). The number 5 is conspicuously absent from DEVI_N itself; the Fibonacci structure manifests as the *step* between tithi positions T8 and T13 rather than as a yantra-fold value. Sarvāṅgasundarī's 13-fold field is the Fibonacci-completion of Tvaritā's 8-fold field — the same substitution structure at higher refinement.

---

## Attestation summary

- **OBSERVED:PRIMARY**: Identity (name, bija, mantra, weapon "mirror+lotus", description, rasa, element, guna from nitya_devi_master.csv); Lunar/Time (tithi quality, deity Kāmadeva, good_for/avoid from tithi_master.csv); naming discrepancy (Sarvamaṅgalā vs Sarvāṅgasundarī) verified across CSVs.
- **OBSERVED:TRADITIONAL**: Bhasma substance classes (Rajata/Mukta rasashastra); Moon's friend/enemy table (BPHS); chakra-graha mapping; raga-graha mapping (Bāgeshrī as best-match).
- **SYNTHESIS**: Yantra geometry (CSV explicitly attests "geometry details are absent"); Field Math eigenvalue derivation; Wave/Interference findings; Quasicrystal N=13 (Fibonacci-prime); Cross-layer observations including mirror-Sauḥ-Para-Trika reading and Fibonacci structure.
- **GENERATED**: None.

---

## SOURCE_NEEDED flags

1. **mudras / vahana / body_color hue / ornaments / faces_arms_count / capability_signature**: nitya_devi_master.csv has multiple empty fields for Sarvāṅgasundarī.
2. **classical yantra geometry attestation**: nitya_yantra_geometry.csv: "geometry details are absent."
3. **nakshatra_overlays**: Compute Trayodaśī (Jaya-group, no-gandanta-amplification) wave fine structure.
4. **nodal_density / radial_bands explicit count**: Run N=13 cosine frequency=4 multigrid extraction.
5. **hexagram_id**: User decision for tithi 13 → hexagram 13 (Tóng Rén).
6. **Pasaka at total=13**: System mismatch — pasaka totals are 3-12. Decide alternate mapping (mod-12, deck-position, deck-extension, or accept gap).
7. **shodhana_media / bhavana_media / marana_cycles / puta_profile / particle_scale_overlay**: Bhasma docx for Rajata/Mukta (same as T2).
8. **plant_allies / doctrine_of_signatures_overlay / processing_plants / astrobotanical_timing**: Chandra plant cross-reference.
9. **dhatu_targets / indication_clusters / anupana_vehicle**: Ayurvedic Chandra protocols.
10. **svara_link / tala_link**: Gandharva Veda; 13-beat tala (Yati/Mata) attestation needs sourcing.
11. **directional_emphasis**: Vastu confirmation.
12. **panel_layout**: Design decision.
13. **Naming canonicalization**: User to decide whether **Sarvamaṅgalā** (per tithi/yantra CSV, "auspicious in all") or **Sarvāṅgasundarī** (per devi-master CSV, "beautiful in all limbs") is the canonical name. Both names refer to the same tithi 13 Nityā position; the user filename uses sarvamangala.
