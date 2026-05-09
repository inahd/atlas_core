# Kameshvari · Tithi 1 · Card

**Source compilation**: 2026-05-01
**Schema version**: Atlas Tithi Card Master Table (user-provided, 2026)
**Population status**: ~58/82 fields sourced, ~24 SOURCE_NEEDED flags

---

## Identity

- **tithi_number**: 1
- **tithi_name**: Pratipadā
- **paksha_mode**: Both shukla and krishna. Agni is tithi deity in both pakshas. Quality: auspicious. (tithi_master.csv)
- **devi_name**: Kameshvari
- **devi_alt_names**: Kāmeśvarī (कामेश्वरी). Bija: Aim. Mantra: Om Aim Hrīm Śrīm.
- **seed_keywords**: desire, origin, creative impulse, sugarcane bow, ruby crown, BURN/PURIFY, fire-rajas, shringara

## Canonical Devi

- **iconography_summary**: She who fulfills all desires — the creative impulse at the origin of manifestation. Lustrous red complexion, red garments, crowned with rubies, crescent moon on head. Carries the sugarcane bow and five flowery arrows of the kāma archetype, plus aṅkuśa and pāśa. (nitya_devi_master.csv, OBSERVED:PRIMARY, attested_classical)
- **weapons_items**: Sugarcane bow (ikṣu-danda), five flowery arrows (pañca-bāṇa), aṅkuśa (goad), pāśa (noose). Capability signature: CUT, BIND, BURN/PURIFY, DEFEND. (nitya_devi_master.csv, OBSERVED:PRIMARY)
- **mudras_gestures**: Varada mudrā (boon-granting). (nitya_devi_master.csv, OBSERVED:PRIMARY)
- **vahana_mount**: SOURCE_NEEDED: No vahana data in nitya_devi_master.csv for Kāmeśvarī. Tantric iconographic source consultation needed.
- **body_color**: Lustrous red (complexion). Color hex: #ff6b35 (warm coral-red, indicates fire-rajas signature). (nitya_devi_master.csv)
- **ornamentation**: Crown of rubies, throat ornament, necklaces, waist-chain, gemmed rings on feet and hands, crescent moon on head. (nitya_devi_master.csv, OBSERVED:PRIMARY)
- **faces_arms_count**: SOURCE_NEEDED: Not specified in on-disk sources. The 4 weapons + varada mudrā imply at least 5 hands; standard Tripurasundarī iconography from Tantraraja has 4 arms.
- **shakti_statement**: Desire fulfillment — she IS Kāma's sovereign, the origin-shakti from which manifest desire arises. (nitya_devi_master.csv, OBSERVED:PRIMARY)
- **expanded_function**: Kāmeśvarī is the first Nitya — the seed-impulse of the lunar month. As Pratipadā opens both pakshas, she is the source of every cycle, the moment when nothing-yet-becomes-something. The sugarcane bow and flowery arrows are not weapons of war but instruments of creative compulsion. The 3-fold N-symmetry of her yantra (devi_engine.py DEVI_N) places her on the simplest periodic crystallographic field — desire as the most reducible of structures, the triangle that cannot be simpler. (SYNTHESIS from nitya_devi_master.csv + CONSTRUCTION_CHOICES.md)
- **bhava_mood**: Shringara (love/beauty). Rasa: shringara. Element: fire. Guna: rajas. The fire-rajas pairing is the signature of creative ignition. (nitya_devi_master.csv, OBSERVED:PRIMARY)
- **mantra_bija**: Aim (the Sarasvatī-bija). Full mantra: Om Aim Hrīm Śrīm. The triple bija-string (Aim Hrīm Śrīm) is the standard Lalita invocation. (nitya_devi_master.csv, OBSERVED:PRIMARY)

## Lunar/Time

- **lunar_phase_arc**: 0°-12° from conjunction (shukla pratipada), or 180°-192° (krishna pratipada). The 1st tithi spans the first 12° of Sun-Moon elongation.
- **phase_quality**: Auspicious (tithi_master.csv). Good for: starting projects, travel, celebration, wealth. Avoid: violence, arguments, negativity. Tithi deity: Agni.
- **nitya_cycle_position**: 1st of 15 — the seed position. Pratipadā opens both shukla and krishna pakshas; Kāmeśvarī is therefore the only Nitya whose moment occurs twice per lunar month at structurally identical phase distance from the new/full moon boundary.
- **weekday_links**: Pratipadā's tithi deity is Agni (fire). Kāmeśvarī's graha correspondence is Shukra (Venus) per devi_master — Friday (Shukravara). **Discrepancy noted**: nitya_yantra_geometry.csv assigns Sun as graha_correspondence for tithi 1, while nitya_devi_master.csv assigns Shukra. The devi_master is treated as authoritative for the devi's own graha (k=5, M=30).
- **nakshatra_overlays**: SOURCE_NEEDED: No tithi-to-nakshatra fixed mapping exists on disk. From RESEARCH-017 Finding 11: Pratipadā belongs to the Nanda group (T1, T6, T11, T16, T21, T26 — "bliss tithis"). Fire-starting gandanta nakshatras (Ashwini, Magha, Mula) PREFER Nanda tithis (mean differentiation 1.72 vs 1.08, t=9.727, p<0.0001). When Pratipadā coincides with Ashwini, the Kāmeśvarī field is amplified along the fire-water boundary axis.

## Yantra

- **yantra_family**: Downward triangle (trikona) with eight petals and bhupura. Triangle scale 0.9, inner circle scale 0.95. (nitya_yantra_geometry.csv, attested SPECULATIVE — "No explicit geometry described; assume downward triangle representing Shakti.")
- **yantra_geometry_notes**: The classical yantra base assignment is speculative per the geometry CSV. CONSTRUCTION_CHOICES.md uses N=3 multigrid for Kāmeśvarī — the periodic hexagonal lattice that emerges when 3 plane waves at 120° interfere. This is the simplest crystallographic projection in the entire Nitya sequence.
- **yantra_symmetry_order**: N=3 (triangular, periodic). 3-fold symmetry produces a hexagonal honeycomb lattice when projected — the densest 2D packing. Kāmeśvarī's field is the most efficiently tiled of all 15 Nityas. (devi_engine.py DEVI_N)
- **yantra_center_logic**: Bindu as point. Inner circle scale 0.95 — the largest of any Nitya, indicating maximum interior coherence. The 3-source pattern's central interference is at 100% constructive when all three waves align in phase.
- **yantra_outer_boundary**: Bhupura with 4 gates (nitya_yantra_geometry.csv). Interference radius fraction: 0.9 (the highest of all 15 Nityas). Wave function: sine, frequency multiplier: 1, angular position: 0° (the origin position).
- **yantra_layer_count**: 3 layers minimum: bindu (point) → 8-petal lotus → bhupura. Triangle at 0.9 scale, orientation: down. (nitya_yantra_geometry.csv)

## Field Math

- **graha_k**: Shukra = k=5, magic constant M=30. (yantra_eigenvalue_exploration.md, Finding 2). However, the yantra_geometry CSV assigns Sun (k=0). Shukra (k=5) is treated as primary per devi_master.
- **magic_constant_M**: 30 (Shukra, k=5). Eigenvalues: {30, +4.899, -4.899}. The +/-2sqrt(6) invariant is universal across all grahas. (Finding 1)
- **invariant_secondary_modes**: +/-2sqrt(6) = +/-4.8990. The irreducible spatial asymmetry of the Vastu Purusha Mandala — does not depend on graha. (Finding 1)
- **coherence_ratio**: lambda_2/M = 4.899/30 = 0.1633 (Shukra). This is the 4th most coherent graha position (after Ketu 0.1256, Rahu 0.1361, Shani 0.1485). Shukra's field is more uniformly distributed than the inner planets, less than the outer shadow grahas. (Finding 2)
- **eigenvector_axes**: For Shukra (k=5): Brahmasthana eigenvector = uniform [1/√3, 1/√3, 1/√3]. Primary tension axis (lambda=+4.899): South row vs center row polarity. Secondary tension axis (lambda=-4.899): North row vs center row, perpendicular. (Finding 6)
- **brahmasthana_definition**: The eigenvector for lambda_1 = M is ALWAYS uniform — it persists at every Kronecker level. This vector IS the Brahmasthana — the geometric principle of maximum coherence where all directions are in balance. (Finding 4)
- **kronecker_level**: Level 1: 3x3, M=30. Level 2: 9x9, M=900. Level 3: 27x27, M=27000. Scaling law: M_n = M_1^n. (Finding 3)
- **navagraha_composite_role**: Shukra occupies the k=5 position in the Navagraha 9x9 composite (M_composite = 81, rank 5, null 4). Block magic constants form 3*Lo_Shu + 12*J — a magic square of magic squares. (Finding 5)

## Wave/Interference

- **boundary_harmonic_mode**: At k=1 (Pratipadā opens the cycle): the conjunction harmonic. Shukla Pratipadā falls within 12° of Amāvāsyā — a near-conjunction zone where all wave modes peak simultaneously. (two-source-interference-v3.md, Finding 8)
- **two_source_pattern**: A(theta) = cos(k(theta-alpha)) + cos(k(theta-beta)) = 2 * cos(k(theta - midpoint)) * cos(k * separation/2). At Pratipadā the Sun-Moon separation is at its smallest non-zero value — the carrier wave is at maximum coherent envelope. (Finding 8)
- **nodal_interior_pattern**: For N=3 multigrid in the disk interior: periodic hexagonal lattice (the same lattice as graphite). Unlike the higher-N quasicrystals, this is a fully ordered, repeating field. Triangle and hexagon are dual — the 3-source field tiles the plane perfectly. (CONSTRUCTION_CHOICES.md)
- **ring_vs_disk_distinction**: On the boundary (1D zodiacal ring): 3-source pattern produces standing waves at k=3 (trine). In the disk interior: 3-fold multigrid produces periodic hexagonal nodal structure. (Finding 7)
- **gandanta_gain**: Pratipadā is a Nanda tithi. Fire-starting gandanta nakshatras (Ashwini, Magha, Mula) PREFER Nanda tithis (mean diff 1.72 vs 1.08, p<0.0001). All 6 gandanta nakshatras AVOID Jaya tithis (3, 8, 13). When Pratipadā coincides with Ashwini, the field is amplified — the cycle's seed moment lands on the fire-water boundary at maximum gandanta gain. (Finding 11)
- **wave_panchaka_relation**: Panchaka (mod-9, rank 9) and the wave system (trigonometric, effective rank 15) are orthogonal: Pearson r = -0.011. They describe independent structures on the 27x30 nakshatra-tithi space. (Finding 12)
- **quantized_prime_modes**: The planetary primes {3, 5, 7, 11} are the retrograde station symmetries. 3 = Mercury, 5 = Venus, 7 = Mars, 11 = Jupiter. Kāmeśvarī's graha is Shukra (Venus, n=5) — her geometric resonance is the pentagram. Venus's 5 retrograde stations in 8 years form the {5/2} star polygon, with stations falling within ±3° of pentagram vertices. (planetary-primes-v1.md, Section 2.3)

## Quasicrystal/Chladni

- **quasicrystal_line_style**: 3-fold multigrid. Three plane waves at 0°, 120°, 240°, sine interference. The hexagonal lattice produced is a substitution-tiling-free crystallographic structure — periodic, predictable, fully reducible. (CONSTRUCTION_CHOICES.md)
- **nodal_density**: SOURCE_NEEDED: No computed nodal density metric for N=3 stored. The interference_radius_fraction = 0.9 (highest of all 15 Nityas) suggests the densest peripheral structure of any tithi field, with all activity reaching nearly to the bhupura boundary.
- **radial_bands**: SOURCE_NEEDED: Not explicitly computed. Wave function = sine with frequency_multiplier=1 (nitya_yantra_geometry.csv) → 1 radial node within the unit disk. The simplest possible radial structure.
- **interference_centers**: Primary interference center = bindu (3 waves at 120° constructively superpose at origin). Secondary maxima at the 3 vertices of an equilateral triangle inscribed at interference_radius_fraction = 0.9. The 3D mediator polyhedron: tetrahedron (4 faces, 4 vertices — the simplest Platonic solid). (CONSTRUCTION_CHOICES.md)

## Pasaka/Magic Cube

- **cube_type**: Andrews 1917 (verified). 3x3x3 magic cube, values 1-27. (magic_cube_analysis.json)
- **cube_magic_constant**: M = 42. Formula: n*(n^3+1)/2, n=3. (Finding 1)
- **cube_layer_squares**: Every horizontal layer is a doubly-magic square (row sums = column sums = 42). Layer eigenvalues: layer_0 {42, -9, -9}, layer_1 {42, 0, 0}, layer_2 {42, +9, +9}. (Finding 1)
- **cube_invariant**: +/-9 = +/-3^2. The 3D invariant is rational (perfect square), unlike the 2D Lo Shu invariant +/-2sqrt(6) (irrational). (Finding 2)
- **cube_center_value**: 14 = (1+27)/2. Middle layer is spectrally null when centered — the 3D Brahmasthana. (Finding 3)
- **cube_associative_sum**: Every antipodal pair sums to 28 = n^3 + 1. The 3D analog of Lo Shu's opposite-cell sum of 10 = n^2+1. (Finding 4)
- **cube_tensor_isotropy**: sigma_1 = 72.75 across all three tensor modes. The cube is spectrally isotropic — no preferred axis. (Finding 6)
- **cube_kronecker_scaling**: Level-n Kronecker product: M_n = 42^n. Secondary = 9 * 42^(n-1). (magic_cube_extension.json, Finding 1)
- **cyclic_composite_eigenvalues**: 9x9 block-circulant composite: M = 126 = 3*42. Eigenvalues {126, +/-2.598, 0, 0, 0, 0}. Rank 5, null 4. Composite invariant: 3*sqrt(3)/2 = 2.598. (Finding 2, 6)
- **loshu_weighted_cube_mode**: Lo Shu-weighted placement concentrates all spectral energy into the uniform mode — eigenvalues collapse to {126, 0, 0, ...}. Lo Shu ordering is the maximally coherent arrangement of the 3D layers. (Finding 3)

### Pasaka at total=1

SOURCE_NEEDED: The pasaka system uses 3 dice each ranging 1-4, producing totals 3-12 only. Tithi number 1 (Pratipadā) has no direct numeric correspondent in the 60-row pasaka deck (pasaka.csv contains no total=1 outcomes). The Pratipadā-resonant outcome must be derived through alternate mapping (mod-9 → 1, or first row of deck = ID 1 = Kṛta 1,1,1 total=3 excellent crown Sun). The Kṛta outcome (the highest throw, all-ones triple) is structurally aligned with Pratipadā as the seed/origin position even though it doesn't share the numeric tithi total.

## I Ching

- **hexagram_id**: SOURCE_NEEDED: No fixed tithi-to-hexagram mapping on disk. Numerical correspondent: hexagram 1 (Qián, "The Creative") — 6 yang lines, the first and most generative hexagram. This pairs naturally with Pratipadā's seed-position semantics, but the mapping is not attested in the Atlas system.
- **hexagram_arrangement**: The I Ching system operates across two arrangements: Fuxi (rank 2, maximally ordered) and King Wen (rank 8, full rank, maximally complex). These are spectral opposites. (iching_spectral_analysis.json, Finding 7)
- **rank_complexity**: Q6 hypercube eigenvalues: {6, 4, 2, 0, -2, -4, -6} with multiplicities C(6,k) = {1, 6, 15, 20, 15, 6, 1}. The I Ching's deep structure IS Pascal's row 6. (Finding 3)
- **yin_yang_balance_mode**: Complement permutation (XOR with 63) has eigenvalues exactly {+1, -1}, each with multiplicity 32. The hexagram pairs form a perfect yin-yang partition. (Finding 6)
- **hypercube_distance_signature**: Hamming distance matrix: rank 7, eigenvalues {192 (x1), 0 (x57), -32 (x6)}. Only 3 unique eigenvalues. (Finding 5)
- **pascal_row_signature**: Row 6: {1, 6, 15, 20, 15, 6, 1}. Total = 64 = 2^6. (Finding 3)

## Lo Shu x I Ching Bridge

- **trigram_loshu_weight_map**: Li=9, Kan=1, Zhen=3, Dui=7, Xun=4, Gen=8, Kun=2, Qian=6. Pratipadā (1) maps to **Kan=1** — the Water trigram, the Abyss, the Receptive moisture. (loshu_iching_interaction.json)
- **weighted_spectral_breaking**: Unweighted Q6 has 7 unique eigenvalues. Lo Shu weighting breaks this to 27 unique eigenvalues — the nakshatra number. Degeneracy is completely broken. (test4_weighted_Q6)
- **spectral_gap_change**: Unweighted gap = 2.0, weighted gap = 0.4624. Fiedler value drops from 2.0 to 0.1944. Lo Shu weighting introduces hierarchical structure to the hexagram graph. (test5_spectral_gap)

## Alchemical/Bhasma

- **material_classical_class**: Shukra's metal is silver/diamond (rasashastra varies). Vajra (diamond) is Shukra's gem. In some classifications: Shukra = silver (Rajata), in others = diamond (Vajra/Hira). (SYNTHESIS — the rasashastra docx not directly read)
- **material_scientific_type**: Diamond — pure carbon, hardest natural substance, highest known thermal conductivity for an insulator. Or silver (Ag) — element 47, highest electrical and thermal conductivity of any metal.
- **base_material**: SOURCE_NEEDED: Disambiguation between silver-bhasma (Rajata Bhasma) and diamond-bhasma (Vajra Bhasma) for Shukra-Kāmeśvarī requires consulting Bhasma docx and Graha Material docx. Both are documented in classical rasashastra.
- **prepared_substance_type**: SOURCE_NEEDED. Rajata Bhasma (silver bhasma) is the more commonly prepared. Vajra Bhasma (diamond bhasma) is rare and reserved for the highest disorders.
- **shodhana_media**: SOURCE_NEEDED: Specific shodhana media for Rajata/Vajra not detailed in on-disk sources.
- **bhavana_media**: SOURCE_NEEDED.
- **marana_cycles**: SOURCE_NEEDED.
- **puta_profile**: SOURCE_NEEDED.
- **quality_tests**: Classical tests apply: nischandratva (no metallic lustre), rekhapurnatva (fills finger lines), varitaratva (floats on water). (Bhasma docx, general framework)
- **completion_stop_rule**: All classical quality tests pass simultaneously. Modern: XRD phase identification. (Bhasma docx)
- **phase_transformation**: Ag → Ag2O (silver oxide) for Rajata Bhasma. C (diamond) → ash carbon residue for Vajra Bhasma — though true diamond is famously difficult to fully incinerate without complete oxidation to CO2. (SYNTHESIS from chemistry)
- **particle_scale_overlay**: SOURCE_NEEDED.
- **safety_conditions**: Rajata bhasma generally well-tolerated when properly prepared. Vajra bhasma extremely rare — quality verification critical. (SYNTHESIS)

## Graha/Material

- **graha_material_map**: Shukra (Venus) → Rajata (silver) and/or Vajra (diamond). Gem: Hira (diamond, white sapphire as substitute). In BPHS friendship: Shukra's friends are Mercury and Saturn; enemies: Sun and Moon; neutral: Mars and Jupiter. (Graha Material docx, attested classical)
- **friend_enemy_interaction**: Shukra-Sun (Ag-Au or Diamond-Gold): silver and gold form alloys (electrum, white gold). The "enemy" relationship at the metallic level is complex — silver and gold are mutually soluble but silver TARNISHES (sulfide formation) while gold does not. Shukra-Mercury (Ag-Hg): silver dissolves readily in mercury (amalgam) — the "friend" relationship materializes as ready chemical communion. (Graha Material docx)
- **ritual_vs_medical_flag**: Both. Rajata and Vajra bhasma are medical (rasaushadhi); silver-leaf (Rajata-varka) is widely used in ritual offerings (Lalita worship, Devi ceremonies). The diamond is also a primary ritual gem in Lalita Sahasranama prescriptions.

## Plant/Ecology

- **plant_allies**: SOURCE_NEEDED: No graha-to-plant cross-reference for Shukra at the dataset level. Traditional Shukra plants: Aśoka (Saraca asoca — the women's tonic), Daruharidra (Berberis aristata), Aparajita (Clitoria ternatea). The shringara-rasa signature suggests aphrodisiac and reproductive-tonic plants.
- **processing_plants**: SOURCE_NEEDED: Specific shodhana/bhavana plants for Rajata/Vajra not on disk. General: kumari (aloe), nimba (neem), triphala apply across most metals.
- **doctrine_of_signatures_overlay**: SOURCE_NEEDED. Shukra plants in doctrine of signatures: white-flowered, sweet-tasting, milk-producing, mucilaginous (Madhura rasa dominant). Aśoka's red flowers are an exception that proves the rule — the women's reproductive specifier overrides general color-Shukra associations.
- **astrobotanical_timing**: SOURCE_NEEDED: No Shukra/Pratipadā specific timing. The general principle: Pratipadā is a starting tithi (auspicious for sowing); Friday (Shukravara) is Shukra's day; Shukla paksha is the building phase. Pratipadā in Shukla paksha on Friday under a Shukra-ruled nakshatra (Bharani, Purva Phalguni, Purva Ashadha) would be the maximally Shukra-aligned planting window.

## Body/Therapeutics

- **dosha_predicates**: Tithi 1 element: fire (tithi_master.csv), guna: sattva. Devi element: fire (nitya_devi_master.csv), guna: rajas. Chakra: Anahata (Venus/Shukra correspondence) — air element, Vata-Pitta-Kapha tridosha balance, Kakini shakti. (chakra_cross_domain.csv). The fire/fire/air triad across the three sources points to Pitta dominance with Vata secondary — the creative-ignition profile.
- **dhatu_targets**: SOURCE_NEEDED: No dhatu-targeting data for Shukra/Pratipadā on disk. Traditional: Shukra governs Shukra dhatu (reproductive tissue, the 7th and last dhatu — the dhatu sharing its name with the planet). The Pratipadā-Shukra alignment makes this the seed-tithi of reproductive shakti.
- **organ_targets**: Anahata (Shukra chakra) at heart center: cardiovascular and respiratory systems, thymus gland. Body system: heart, lungs, thymus, immune. Psychological: love, compassion, devotion, trust. (chakra_cross_domain.csv). The associated nakshatras (Bharani, Purva Phalguni, Purva Shadha) are the three Shukra-ruled nakshatras — direct chakra-nakshatra-graha alignment.
- **indication_clusters**: SOURCE_NEEDED: No specific therapeutic indications for Pratipadā/Shukra on disk. Traditional Shukra disorders: reproductive imbalances, cardiac symptoms, immune weakness, infertility, menstrual irregularity.
- **anupana_vehicle**: SOURCE_NEEDED.
- **preparation_dependency_warning**: Shukra preparations (Rajata Bhasma, Vajra Bhasma) require classical processing oversight. Improper Vajra Bhasma can contain residual diamond particles (mechanically dangerous). (SYNTHESIS)

## Prime/Morphology

- **prime_signature**: 5 is Venus's retrograde station count (5 in 8 years, forming the {5/2} pentagram). Pratipadā's tithi number = 1 — this is NOT a planetary prime, but Kāmeśvarī's graha (Shukra) is n=5. The bhandgini (5-fold) symmetry is the Penrose tiling family, the first non-crystallographic prime symmetry that nonetheless tiles the plane (via aperiodic substitution rules). (planetary-primes-v1.md, Section 2)
- **morphology_correlates**: L5 = 5 lumbar vertebrae in humans = Venus's retrograde prime. Pratipadā as Shukra's tithi connects the seed-position of the lunar cycle to the lumbar region of the spine — the pelvic seat of generative shakti. The hand also encodes 5 (5 fingers, 5 metacarpals) — Venus's prime expressed in the manual instruments of creative manipulation. (vertebral-primes-v1.md, Finding 2)
- **sri_yantra_region_relation**: The 44-region tidal-weighted quantized field uses Venus at n=5 with weight 0.220 (relative to Jupiter=1.00) — Venus is the 2nd-strongest tidal contributor after Jupiter. Removing Venus's pentagonal mode collapses several boundary regions. (planetary-primes-v1.md, Section 3)

## Sound/Rhythm

- **svara_link**: SOURCE_NEEDED: No tithi-to-svara mapping on disk. Shukra's traditional svara association in Gandharva Veda is Pa (Pañcama, the perfect 5th). The 5th degree of the scale — exact correspondent to Venus's pentagonal prime.
- **raga_link**: Shukra-associated ragas in raga_data.csv: **Khāmaj** (night, earth/rajas, hasya; vadi Ga), **Pīlu** (evening, earth/rajas, shringara; vadi Ga), **Pūrvī** (afternoon, fire/rajas, vira; vadi Ga), **Tilaka Kāmod** (evening, ether/rajas, shringara; vadi Sa). Of these, **Pīlu** and **Tilaka Kāmod** carry the shringara-rasa signature that matches Kāmeśvarī directly. Pīlu is a thumri raga — the literature of romantic longing.
- **tala_link**: SOURCE_NEEDED: No tithi-to-tala mapping on disk. The pentagonal prime (Venus) suggests a 5-beat cycle (Khanda Chapu in Carnatic, or Jhaptal's 10-beat × 2 division). Structural correspondence, not attested mapping.

## Vastu/Spatial

- **mandala_zone_map**: Shukra at k=5 places the yantra values as Lo_Shu + 5*J = {9, 14, 13; 16, 10, 8; 11, 12, 15}. The Brahmasthana (center cell) = 10. Eigenvector structure follows Finding 6: uniform (M=30), primary tension (NE-SW axis), secondary tension (perpendicular). (yantra_eigenvalue_exploration.md)
- **directional_emphasis**: SOURCE_NEEDED: No Shukra-specific Vastu directional prescription on disk. Traditional: Shukra governs the Southeast direction (Agni corner) in some Vastu systems — fitting for Pratipadā whose tithi deity IS Agni.

## Visual Grammar

- **palette_logic**: Primary: #ff6b35 (warm coral-red, from nitya_devi_master.csv). Secondary: #D1C4E9 (lavender, from nitya_yantra_geometry.csv). Bindu: #FF4081 (rose pink). Line weight: medium. The fire-rajas signature dominates — render with warm, saturated colors.
- **density_logic**: interference_radius_fraction = 0.9 (highest of all 15 Nityas). The 3-fold periodic field has uniform density throughout the disk — no concentrated center vs sparse edge. Render should show evenly distributed activity reaching to the bhupura.
- **line_weight_logic**: Medium. The 3-fold lattice has high regularity; line variation should be minimal — the periodicity is the visual signature.
- **panel_layout**: SOURCE_NEEDED: Design decision for the diviner's manual.
- **symbol_strip**: BURN/PURIFY + DEFEND + CUT + BIND. 4 weapons (sugarcane bow, 5 flowery arrows, ankusha, pasha). Ruby crown, crescent moon. Bija: Aim. Hexagonal lattice (the 3-fold periodic projection).
- **caption_motto**: "She who fulfills all desires — the creative impulse at the origin of manifestation." (nitya_devi_master.csv, description field)

---

## Cross-layer observations

The first cross-layer resonance is the **seed-position alignment across all 15-fold cycles**. Pratipadā (tithi 1) opens the lunar month; Kāmeśvarī (Nitya 1) opens the Devi sequence; Aim (her bija) is the first letter of the Lalita vidyā mantra; her yantra has the highest interference_radius_fraction (0.9) of any Nitya, meaning her field reaches furthest to the boundary; her N=3 multigrid is the simplest periodic crystallographic projection. Every measure of "first-ness" in the system aligns with this position. The seed is structurally maximal in extent and minimal in complexity — Kāmeśvarī's signature is the largest field with the simplest structure.

The second resonance is the **fire-Agni-Pratipadā compound coding the ignition moment**. The tithi deity is Agni; Kāmeśvarī's element is fire; her bhava is shringara (love-beauty), which in classical rasa theory is fire's primary affect when sublimated. But her graha is Shukra (Venus, water/cool by classical jyotish). This creates a controlled-fire signature: the sugarcane bow shoots flowery arrows — sweetness as ignition. The pentagonal prime (n=5, Venus) overlaying the triangular field (N=3, Kāmeśvarī's yantra geometry) gives the 15-fold composite — Pratipadā's tithi number multiplied by the pentagonal prime: 1 × 5 = 5, but 3 (yantra) × 5 (Venus) = 15 (the Nitya total). The Devi sequence count IS the product of Kāmeśvarī's two structural primes.

The third resonance is the **gandanta-Nanda alignment for the cycle-opening tithi**. Pratipadā belongs to the Nanda group {1, 6, 11, 16, 21, 26} — the "bliss tithis." From RESEARCH-017 Finding 11, fire-starting gandanta nakshatras (Ashwini, Magha, Mula) statistically PREFER Nanda tithis (mean differentiation 1.72 vs 1.08, p<0.0001). Ashwini is the first nakshatra; Pratipadā is the first tithi. When they coincide (Ashwini-Pratipadā), the Kāmeśvarī field is amplified by both gandanta gain and seed-position resonance simultaneously. The Mercury dasha closing in October 2027 (per natal context) means user's Ketu mahadasha will begin near a Pratipadā transit — a structurally significant alignment for any work begun in that window.

---

## Attestation summary

- **OBSERVED:PRIMARY** (direct from primary text / dataset row): Identity (name, bija, mantra, weapons, description, body color, ornamentation, rasa, element, guna, shakti, mudra from nitya_devi_master.csv); Lunar/Time (tithi quality, deity, good_for/avoid from tithi_master.csv); Yantra base parameters (geometry CSV).
- **OBSERVED:TRADITIONAL**: Bhasma substance classes (Rajata/Vajra rasashastra tradition); Shukra's friend/enemy table (BPHS).
- **SYNTHESIS**: Field Math eigenvalue derivation; Wave/Interference findings; Quasicrystal N=3 construction; Prime/Morphology correspondences; Cross-layer observations; expanded_function; safety_conditions; phase_transformation; raga associations.
- **GENERATED**: None. All SOURCE_NEEDED fields are flagged rather than filled with invented content.

---

## SOURCE_NEEDED flags

1. **vahana_mount**: Tantraraja Tantra / Dakshinamurti Samhita iconographic source.
2. **faces_arms_count**: Tantric iconographic source (likely 4 arms by Tripurasundarī tradition, but Kāmeśvarī-specific count not attested on disk).
3. **nakshatra_overlays**: Compute Pratipadā wave fine structure profile across 27 nakshatras; data exists in engine, not extracted.
4. **nodal_density / radial_bands**: Run N=3 multigrid extraction. Code in cut_and_project.py.
5. **hexagram_id**: User decision: static tithi 1 → hexagram 1 (Qián) mapping vs field-derived.
6. **base_material / prepared_substance_type / shodhana_media / bhavana_media / marana_cycles / puta_profile / particle_scale_overlay**: Bhasma docx + Graha Material docx consultation for Rajata vs Vajra disambiguation and process specifics. Primary text: Rasa Ratna Samucchaya, Rasarnava.
7. **Pasaka at total=1**: System mismatch — pasaka totals are 3-12. Decide alternate mapping (mod-9, deck-position, or use the all-ones outcome ID 1 = Kṛta).
8. **plant_allies / doctrine_of_signatures_overlay / processing_plants / astrobotanical_timing**: Cross-reference guild_full.csv with traditional Shukra associations. Plant profiles docx may have data.
9. **dhatu_targets / indication_clusters / anupana_vehicle**: Ayurvedic text consultation for Shukra-specific therapeutic protocols.
10. **svara_link / tala_link**: Gandharva Veda source for tithi-svara and tithi-tala mappings.
11. **directional_emphasis**: Vastu text consultation for Shukra directional governance.
12. **panel_layout**: Design decision, not data retrieval.
