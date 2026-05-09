# Nitya · Tithi 10 · Card

**Source compilation**: 2026-05-02
**Schema version**: Atlas Tithi Card Master Table (user-provided, 2026)
**Population status**: ~62/82 fields sourced, ~20 SOURCE_NEEDED flags

---

## Identity

- **tithi_number**: 10
- **tithi_name**: Daśamī
- **paksha_mode**: Both shukla and krishna. Dharma is tithi deity. Quality: auspicious. (tithi_master.csv)
- **devi_name**: Nitya
- **devi_alt_names**: Nityā (नित्या). "The eternal one." Bija: Aim Hrīm Śrīm (the full Lalitā tribija). Mantra: Om Aim Hrīm Śrīm Nityāyai.
- **seed_keywords**: eternity, time-encompassing, name-shared-with-class, water-sattva, shanta, STABILIZE/DEFEND, Shukra-graha, conch+lotus

## Canonical Devi

- **iconography_summary**: The eternal one — she who IS beyond time while dwelling within it completely. Red complexion, red garments, smeared with red sandalwood paste with beads of sweat on the forehead — the iconographic mark she shares with Nityaklinnā (T3). Both are characterized by the same anointed-with-sweat motif; the difference is structural-temporal: Nityaklinnā is dissolution-as-melting; Nityā is dissolution-as-eternity. Carries aṅkuśa and pāśa. (nitya_devi_master.csv, OBSERVED:PRIMARY, attested_classical)
- **weapons_items**: Aṅkuśa (goad), pāśa (noose). 2 weapons — same minimal set as Nityaklinnā (T3) and Vahnivāsinī (T5). Capability signature: STABILIZE, DEFEND. (nitya_devi_master.csv, OBSERVED:PRIMARY)
- **mudras_gestures**: Abhaya mudrā (fearlessness-granting). Same single mudrā as Nityaklinnā. (nitya_devi_master.csv, OBSERVED:PRIMARY)
- **vahana_mount**: SOURCE_NEEDED.
- **body_color**: Red complexion. Color hex: #20b2aa (light sea green — represents her field, contrasting the textual red body). The sea-green field encodes the ether-sattva watery-luminous signature. (nitya_devi_master.csv)
- **ornamentation**: Smeared with red sandalwood paste; beads of sweat on the forehead. (nitya_devi_master.csv, OBSERVED:PRIMARY)
- **faces_arms_count**: SOURCE_NEEDED.
- **shakti_statement**: Eternal being — the time-encompassing shakti. The class itself ("the 15 Nityā Devīs") is named after her — she IS the principle of which all 15 are instances. (nitya_devi_master.csv, OBSERVED:PRIMARY)
- **expanded_function**: Nityā is the tenth Nitya — the eternity-position, the time-encompassing center of the second half of the paksha. Where Vahnivāsinī (T5) closes the first half with sublimation, Nityā opens the second half with eternal-presence. The class is named after her: "the 15 Nityā Devīs" derives from her name, suggesting she carries the structural principle that all 15 instantiate. The N=10 yantra symmetry (devi_engine.py DEVI_N) is decagonal — non-crystallographic, related to the 5-fold pentagonal prime of her graha (Shukra/Venus, n=5). 10 = 2×5 — Nityā's symmetry is the doubled Venus prime. Her graha is Shukra (k=5, M=30) — same as Kāmeśvarī (T1), making T1 and T10 the two Shukra-Devis, exactly half the lunar arc apart. (SYNTHESIS from nitya_devi_master.csv + CONSTRUCTION_CHOICES.md)
- **bhava_mood**: Shanta (peace). Rasa: shanta. Element: water. Guna: sattva. The water-sattva pairing matches Bhagamālinī (T2) exactly; the two Shanta-Sattva-Water Nityas are at opposite ends of the early-cycle / mid-cycle axis. (nitya_devi_master.csv, OBSERVED:PRIMARY)
- **mantra_bija**: Aim Hrīm Śrīm — the full Lalitā tribija. The complete three-syllable invocation is unique to Nityā among the 15 — she carries the entire Lalitā mantra as her own. (nitya_devi_master.csv, OBSERVED:PRIMARY)

## Lunar/Time

- **lunar_phase_arc**: 108°-120° from conjunction (shukla daśamī), or 288°-300° (krishna daśamī). The 10th tithi crosses the trine boundary (120°).
- **phase_quality**: **Auspicious** (tithi_master.csv). Good for: marriage, religious ceremonies, completion of projects (same set as Vahnivāsinī T5 and Nilapataka T11). Avoid: negative actions, quarrels. Tithi deity: Dharma (the principle of cosmic order).
- **nitya_cycle_position**: 10th of 15 — the eternity-position. Daśamī is the auspicious tithi associated with completion of long undertakings. The Dharma-Nityā pairing aligns: dharma is what is eternally ordered; Nityā is the personification of that orderly eternity.
- **weekday_links**: Daśamī's tithi deity is Dharma. Nityā's graha correspondence is Shukra (Venus) per devi_master — Friday (Shukravara). yantra_geometry CSV assigns **Sun** to tithi 10 — discrepancy. devi_master Shukra treated as authoritative. k=5, M=30.
- **nakshatra_overlays**: SOURCE_NEEDED: Daśamī belongs to the **Purna group** (T5, T10, T15, T20, T25, T30 — "full tithis"). Per RESEARCH-017 Finding 11, water-ending gandanta nakshatras (Aśleṣā, Jyeṣṭhā, Revatī) PREFER Purna tithis (mean differentiation 1.72 vs 1.08, p<0.0001). When Daśamī coincides with these, the Nityā field is amplified at the water-fire boundary.

## Yantra

- **yantra_family**: Downward triangle (trikona) with **12 petals** (double lotus implied) and bhupura. Triangle scale 0.72, inner circle 0.76. (nitya_yantra_geometry.csv, attested SYNTHESIS — "Geometry not provided in sources; assign pattern of downward triangle with twelve petals (double lotus).")
- **yantra_geometry_notes**: Classical yantra unattested for Nityā specifically — the 12-petal assignment is Atlas synthesis. The CONSTRUCTION_CHOICES.md uses N=10 multigrid for the wave projection — decagonal symmetry. The 12 petals (zodiacal ring) and the N=10 multigrid (decagonal symmetry) are decoupled at this position, in contrast to Vahnivāsinī (T5) where 12 petals + N=8 had similar decoupling.
- **yantra_symmetry_order**: N=10 (decagonal, quasicrystalline). 10-fold symmetry is non-crystallographic — like the Penrose 5-fold doubled. The 10-fold tilings are aperiodic but have substitution rules (related to the Penrose family). (devi_engine.py DEVI_N)
- **yantra_center_logic**: Bindu as point. Inner circle scale 0.76. The 10-source pattern's central interference produces a central rosette of 10 secondary maxima in the inner ring.
- **yantra_outer_boundary**: Bhupura with 4 gates. Interference radius fraction: 0.45. Wave function: sine, frequency multiplier: **3**, angular position: 216°.
- **yantra_layer_count**: 3 layers minimum: bindu → 12-petal lotus → bhupura. Triangle at 0.72 scale.

## Field Math

- **graha_k**: Shukra = k=5, magic constant **M=30**. (yantra_eigenvalue_exploration.md, Finding 2). Same graha and same M as Kāmeśvarī (T1).
- **magic_constant_M**: 30 (Shukra, k=5). Eigenvalues: {30, +4.899, -4.899}. (Finding 1)
- **invariant_secondary_modes**: +/-2sqrt(6) = +/-4.8990. (Finding 1)
- **coherence_ratio**: lambda_2/M = 4.899/30 = **0.1633** (Shukra). The 4th most coherent graha. (Finding 2)
- **eigenvector_axes**: For Shukra (k=5): Brahmasthana = uniform [1/√3, 1/√3, 1/√3]. Primary tension (lambda=+4.899) and secondary tension (lambda=-4.899) follow standard Lo Shu axes. (Finding 6)
- **brahmasthana_definition**: Uniform eigenvector at every Kronecker level. (Finding 4)
- **kronecker_level**: Level 1: 3x3, M=30. Level 2: 9x9, M=900. Level 3: 27x27, M=27000. (Finding 3)
- **navagraha_composite_role**: Shukra at k=5 in the 9x9 composite. Venus's Lo Shu placement encodes the same field-coherence ratio as Kāmeśvarī's; Nityā IS Kāmeśvarī's structural sister via shared graha. (Finding 5)

## Wave/Interference

- **boundary_harmonic_mode**: At k=10: not a classical jyotish aspect. The k=10 harmonic is the decile (36° aspect) — used in some modern astrological traditions but not BPHS-canonical. (two-source-interference-v3.md, Finding 8)
- **two_source_pattern**: A(theta) = 2 * cos(k(theta - midpoint)) * cos(k * separation/2). At k=10: constructive maximum at separation = 36°. Daśamī's actual Sun-Moon separation is 108°-120° (trine territory), well above the decile. The k=10 carrier is structurally active but at low amplitude given the actual separation. (Finding 8)
- **nodal_interior_pattern**: For N=10 multigrid in disk interior: aperiodic, quasicrystalline. The 10-fold tilings are derivable from the Penrose family by edge-doubling — share substitution structure but have visual decagonal symmetry. (CONSTRUCTION_CHOICES.md)
- **ring_vs_disk_distinction**: Boundary: 10-source pattern silent except at k=10. Disk: aperiodic 10-fold tiling. (Finding 7)
- **gandanta_gain**: Daśamī is Purna — water-ending gandantas prefer Purna. Amplification when Daśamī coincides with Aśleṣā/Jyeṣṭhā/Revatī. (Finding 11)
- **wave_panchaka_relation**: Orthogonal: r = -0.011. (Finding 12)
- **quantized_prime_modes**: Venus is n=5 in the planetary prime sequence. Nityā's tithi number 10 = 2×5 = "doubled Venus prime." Her graha (Shukra) and her tithi number share the pentagonal foundation. The decagonal yantra-symmetry (N=10) is the pentagonal-doubled. Three independent measures (graha-prime, tithi-number, yantra-fold) converge on the Venus pentagonal foundation. (planetary-primes-v1.md, Section 2)

## Quasicrystal/Chladni

- **quasicrystal_line_style**: 10-fold multigrid. Sister-symmetry to the Penrose 5-fold; the 10-fold pattern has substitution-tile structure (rhombs at 36° and 72° angles). (CONSTRUCTION_CHOICES.md)
- **nodal_density**: SOURCE_NEEDED. interference_radius_fraction = 0.45 (lower than the early Nityas, suggesting tighter central concentration).
- **radial_bands**: 3 radial nodes within unit disk (frequency_multiplier=3). Same density as Tvarita (T8) and Kulasundari (T9).
- **interference_centers**: Primary = bindu. Secondary maxima at 10 vertices of inscribed regular decagon at interference_radius=0.45. The 3D mediator polyhedron: **dodecahedron** (12 pentagonal faces — note: 10-fold and dodecahedron share the Φ-golden-ratio structure of regular pentagons). The dodecahedron's pentagonal symmetry is the 3D form of the 10-fold 2D symmetry. (CONSTRUCTION_CHOICES.md, polyhedron_mediator)

## Pasaka/Magic Cube

- **cube_type**: Andrews 1917. M=42. (magic_cube_analysis.json)
- **cube_magic_constant**: M = 42. (Finding 1)
- **cube_layer_squares**: layer eigenvalues {42, +/-9, ±9}. (Finding 1)
- **cube_invariant**: +/-9. Rational. (Finding 2)
- **cube_center_value**: 14. (Finding 3)
- **cube_associative_sum**: 28. (Finding 4)
- **cube_tensor_isotropy**: sigma_1 = 72.75. (Finding 6)
- **cube_kronecker_scaling**: M_n = 42^n. (magic_cube_extension.json)
- **cyclic_composite_eigenvalues**: 9x9: M=126, eigenvalues {126, +/-2.598, 0×4}. (Finding 2)
- **loshu_weighted_cube_mode**: Lo Shu collapses to {126, 0, ...}. (Finding 3)

### Pasaka at total=10

The pasaka deck has **6 outcomes** at total=10 (the Nityā-resonant sum):

| ID | Dice | Name | Quality | Body | Graha | Rasa |
|----|------|------|---------|------|-------|------|
| 32 | 2,4,4 | Vaiṣṇavī | mixed | left_ankle | Mercury | madhura |
| 44 | 3,3,4 | Vijayā | good | neck | Venus | madhura |
| 47 | 3,4,3 | Ugratārā | mixed | lower_back | Rahu | tikta |
| 56 | 4,2,4 | Mātaṅgī | mixed | spleen | Rahu | amla |
| 59 | 4,3,3 | Chinnamastā | mixed | kidneys | Mars | tikta |
| 62 | 4,4,2 | Saṅkarṣaṇī | good | bladder | Saturn | kaṣāya |

Distribution: 0 excellent, 0 very_good, 2 good, 4 mixed — heavily mixed. Graha distribution: **Rahu 2, Mars 1, Saturn 1, Mercury 1, Venus 1 — Rahu-prominent**, no Sun/Moon/Jupiter. Bodies cluster in the **lower trunk and limbs** (left_ankle, neck, lower_back, spleen, kidneys, bladder) — internal-organ + lower-body emphasis. Rasas: madhura 2, mixed (tikta+amla+kaṣāya) 4 — astringent/bitter dominant. The total=10 pasaka outcomes are the most "shadow-graha" weighted of any total in the deck — Daśamī's "eternity" carries the dark-deep characteristic of the auspicious-yet-difficult tithi.

## I Ching

- **hexagram_id**: SOURCE_NEEDED. Numerical correspondent: hexagram 10 (Lǚ, "Treading/Conduct") — proper conduct in dangerous proximity. The pairing is structurally interesting: Daśamī is the auspicious tithi for completion-of-projects, and Lǚ is the hexagram of "treading on the tiger's tail without being bitten" — successful navigation of high-stakes situations.
- **hexagram_arrangement**: Fuxi ↔ King Wen spectral opposites. (iching_spectral_analysis.json)
- **rank_complexity**: Q6 hypercube eigenvalues, Pascal row 6. (Finding 3)
- **yin_yang_balance_mode**: XOR-with-63 perfect partition. (Finding 6)
- **hypercube_distance_signature**: Hamming rank 7. (Finding 5)
- **pascal_row_signature**: Row 6, total 64. (Finding 3)

## Lo Shu x I Ching Bridge

- **trigram_loshu_weight_map**: Li=9, Kan=1, Zhen=3, Dui=7, Xun=4, Gen=8, Kun=2, Qian=6. **Daśamī (10) exceeds the 1-9 range of trigram weights** — same situation as tithis 11-15. No single trigram has weight 10. Tithi 10 maps via mod-9 reduction to weight 1 (Kan, Water). Alternatively: the early Lo Shu position 10 is the cell beyond the 3x3 grid's 1-9 range — the position that requires extending the Lo Shu to higher dimensions. (loshu_iching_interaction.json)
- **weighted_spectral_breaking**: 7 → 27 unique eigenvalues. (test4_weighted_Q6)
- **spectral_gap_change**: 2.0 → 0.4624. Fiedler 0.1944. (test5_spectral_gap)

## Alchemical/Bhasma

- **material_classical_class**: Shukra → Rajata (silver) and Vajra (diamond). Same as Kāmeśvarī (T1). See T1 card for full discussion.
- **material_scientific_type**: Silver (Ag, element 47); Diamond (pure C).
- **base_material**: Rajata for metallic preparation; Vajra for gem preparation.
- **prepared_substance_type**: Rajata Bhasma; Vajra Bhasma (rare).
- **shodhana_media / bhavana_media / marana_cycles / puta_profile / particle_scale_overlay**: SOURCE_NEEDED. (See T1 card for the same SOURCE_NEEDED chain.)
- **quality_tests**: Standard bhasma tests.
- **completion_stop_rule**: Quality tests pass.
- **phase_transformation**: Ag → Ag2O (Rajata Bhasma); diamond → nano-carbon residue (Vajra Bhasma).
- **safety_conditions**: Rajata generally safe; Vajra rare.

## Graha/Material

- **graha_material_map**: Shukra → Rajata, Vajra. (Same as T1.)
- **friend_enemy_interaction**: See T1 card. The Shukra-Sun and Shukra-Mercury relationships are the structurally significant ones.
- **ritual_vs_medical_flag**: Both. Pearl/silver/diamond all have extensive ritual use.

## Plant/Ecology

- **plant_allies**: SOURCE_NEEDED. Traditional Shukra plants: Aśoka, Daruharidra, Aparajita. (Same as T1 card.)
- **processing_plants / doctrine_of_signatures_overlay / astrobotanical_timing**: SOURCE_NEEDED.

## Body/Therapeutics

- **dosha_predicates**: Tithi 10 element: ether (tithi_master.csv), guna: sattva. Devi element: water (nitya_devi_master.csv), guna: sattva. Chakra: Anahata (Shukra/Venus correspondence) — air element, Vata-Pitta-Kapha tridosha balance, Kakini shakti. (chakra_cross_domain.csv). The ether/water/air triad with sattva-sattva-tridosha is the **balance-completion profile** — all three subtle elements (ether, water, air) at sattva grade, the dosha-neutral signature appropriate for the eternal tithi.
- **dhatu_targets**: SOURCE_NEEDED. Traditional: Shukra governs Shukra dhatu (reproductive tissue, the 7th dhatu). Daśamī as Shukra's tithi connects to the dhatu sharing its name with the planet.
- **organ_targets**: Anahata at heart center: cardiovascular and respiratory systems. Body system: love, compassion, devotion. (chakra_cross_domain.csv). Associated nakshatras: Bharani, Purva Phalguni, Purva Shadha — the three Shukra-ruled nakshatras (same as T1).
- **indication_clusters**: SOURCE_NEEDED.
- **anupana_vehicle**: SOURCE_NEEDED.
- **preparation_dependency_warning**: Same as T1.

## Prime/Morphology

- **prime_signature**: 10 = 2×5. Nityā's tithi number is the **first composite of 2 and 5** (after 5 itself). The 5 is Venus's prime; the 2 is the bilateral-symmetry root. 10 is the first number in the sequence to encode both. (planetary-primes-v1.md, Section 2)
- **morphology_correlates**: 10 is the count of fingers (5×2) and toes (5×2) — the doubled-Venus-prime expressed bilaterally. The 10 cranial nerves (counted in some classification schemes) and 10 sense gates of the body (5 jñāna + 5 karma indriyas) also encode this. (vertebral-primes-v1.md, general framework)
- **sri_yantra_region_relation**: 10 is not in {3,5,7,11} but is 2×5 (Venus's prime doubled). Removing Venus from the prime overlay collapses several boundary regions; doubling Venus would change the count differently. (planetary-primes-v1.md, Section 3)

## Sound/Rhythm

- **svara_link**: SOURCE_NEEDED. Shukra's svara is **Pa** (Pañcama, perfect 5th) per traditional assignment. (Same as T1.)
- **raga_link**: Shukra-associated ragas: Khāmaj, Pīlu, Pūrvī, Tilaka Kāmod (raga_data.csv). Of these, **Pūrvī** (afternoon, fire/rajas, vira) and **Khāmaj** (night, earth/rajas, hasya) are the most distinctive. Nityā's water-sattva-shanta signature is poorly matched by Shukra's actual ragas in the dataset (which lean rajas/hasya/shringara/vira). The mismatch is a structural feature: Shukra is a graha of evening/night ragas; Nityā's "eternity" function may be served better by the silence-between-ragas than by any specific raga. **Sound association may be tāra-Sa** (the upper-octave tonic, the eternity-anchor) rather than a specific raga.
- **tala_link**: SOURCE_NEEDED. The 10-fold yantra symmetry suggests 10-beat cycles (Jhaptal in Hindustani is 10-beat).

## Vastu/Spatial

- **mandala_zone_map**: Shukra at k=5 places yantra values as Lo_Shu + 5*J = {9, 14, 13; 16, 10, 8; 11, 12, 15}. Brahmasthana center = 10 — **Nityā's tithi number IS the Brahmasthana value at her own graha's yantra**. Same structural over-determination as Kulasundari at T9. (yantra_eigenvalue_exploration.md)
- **directional_emphasis**: SOURCE_NEEDED. Traditional: Shukra governs SE (Agni corner) — the heat-of-creativity quadrant.

## Visual Grammar

- **palette_logic**: Primary: #20b2aa (light sea green, from nitya_devi_master.csv). Secondary: #C5CAE9 (pale lavender-blue, from nitya_yantra_geometry.csv). Bindu: #3D5AFE (saturated blue). Line weight: medium. The water-sattva-Shukra signature creates a cool watery palette: sea-green field, lavender accents, deep-blue bindu — the depth-of-eternity signature.
- **density_logic**: interference_radius_fraction = 0.45. The 10-fold quasicrystalline field with frequency_multiplier=3 has tight central concentration. Render with the decagonal rosette around the bindu prominent.
- **line_weight_logic**: Medium.
- **panel_layout**: SOURCE_NEEDED.
- **symbol_strip**: STABILIZE + DEFEND. 2 weapons (ankusha, pasha). Abhaya mudrā. Red sandalwood paste (shared iconographic detail with Nityaklinnā T3). Bija: Aim Hrīm Śrīm (full Lalitā tribija — unique to Nityā).
- **caption_motto**: "The eternal one — she who IS beyond time while dwelling within it completely." (nitya_devi_master.csv)

---

## Cross-layer observations

The first cross-layer resonance is the **class-naming structural fact**: Nityā's name is the name of the entire 15-Devi class. Among the 15 Nityas, only she carries this naming-structural-identity with the whole. Her bija (Aim Hrīm Śrīm) is also the complete Lalitā tribija — three syllables that are individually the bijas of the foundational triad (Sarasvatī-Lakṣmī-Lalitā). Her position at tithi 10 — the structural center of the second half of the paksha — encodes her function as the eternity-anchor. The 15 Nityas all instantiate eternity; she is the principle they instantiate.

The second resonance is the **Kāmeśvarī-Nityā Shukra-pair structurally pinning the lunar arc**. Both T1 (Kāmeśvarī) and T10 (Nityā) have graha = Shukra (Venus, k=5, M=30). They are exactly halfway through the 15-tithi sequence apart (10−1 = 9 tithis ≈ half of 15). The Shukra-pair pins the structural ends of two 9-tithi sub-cycles. T1 has shringara rasa (love-as-impulse); T10 has shanta rasa (peace-as-arrival). Same graha, opposite affective temperature. The yantra symmetries differ: T1 = N=3 (triangle, periodic); T10 = N=10 (decagonal, quasicrystalline, the doubled Venus prime). The graha is the same; the geometric expression doubles in fold count and shifts from periodic to aperiodic.

The third resonance is the **Purna-tithi-water-ending-gandanta amplification cluster**. Daśamī, Pañcamī (T5 Vahnivāsinī), and Pūrṇimā (T15 Citra) are all Purna tithis. Per RESEARCH-017 Finding 11, water-ending gandantas (Aśleṣā, Jyeṣṭhā, Revatī) statistically prefer Purna tithis. Of the three Purna Nityas: Vahnivāsinī = fire-rajas-vira-yajña (Sun); Nityā = water-sattva-shanta-eternity (Venus); Citra = ether-sattva-adbhuta-bloom (Moon). Three radically different rasas occupying the same statistical-amplification position. The Purna group is structurally diverse despite tithi-group homogeneity. Nityā's eternity-position within this cluster is the "still-water" between Vahnivāsinī's "burning fire" and Citra's "full bloom." The water-sattva profile makes her the Purna anchor — eternity as the medium in which fire and bloom complete their cycle.

---

## Attestation summary

- **OBSERVED:PRIMARY**: Identity (name, bija, mantra, weapons, description, body color, ornamentation, rasa, element, guna, shakti, mudra from nitya_devi_master.csv); Lunar/Time (tithi quality, deity, good_for/avoid from tithi_master.csv).
- **OBSERVED:TRADITIONAL**: Bhasma substance classes (Rajata/Vajra rasashastra); Shukra's friend/enemy table (BPHS); chakra-graha mapping.
- **SYNTHESIS**: Yantra geometry (CSV explicitly attests "Geometry not provided in sources" — fallback pattern); Field Math eigenvalue derivation; Wave/Interference findings; Quasicrystal N=10 (Penrose-doubled); Cross-layer observations.
- **GENERATED**: None.

---

## SOURCE_NEEDED flags

1. **vahana_mount / faces_arms_count**: Tantric iconographic source.
2. **classical yantra geometry attestation**: nitya_yantra_geometry.csv explicitly notes "Geometry not provided in sources" for Nityā.
3. **nakshatra_overlays**: Compute Daśamī (Purna-group) wave fine structure.
4. **nodal_density**: Run N=10 sine frequency=3 multigrid.
5. **hexagram_id**: User decision for tithi 10 → hexagram 10 (Lǚ).
6. **shodhana_media / bhavana_media / marana_cycles / puta_profile / particle_scale_overlay**: Bhasma docx for Rajata/Vajra (same chain as T1).
7. **plant_allies / doctrine_of_signatures_overlay / processing_plants / astrobotanical_timing**: Shukra plant cross-reference.
8. **dhatu_targets / indication_clusters / anupana_vehicle**: Ayurvedic Shukra protocols.
9. **svara_link / tala_link**: Gandharva Veda source for Shukra-svara and 10-beat tala (Jhaptal).
10. **directional_emphasis**: Vastu confirmation.
11. **panel_layout**: Design decision.
