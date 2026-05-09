# Sivaduti · Tithi 7 · Card

**Source compilation**: 2026-04-23
**Schema version**: Atlas Tithi Card Master Table (user-provided, 2026)
**Population status**: 62/82 fields sourced, 20 SOURCE_NEEDED flags

---

## Identity

- **tithi_number**: 7
- **tithi_name**: Saptami
- **paksha_mode**: Both shukla and krishna. Surya is tithi deity in both pakshas. Quality: mixed.
- **devi_name**: Sivaduti
- **devi_alt_names**: Sivaduti (शिवदूती), Shivaduti. Devanagari: शिवदूती.
- **seed_keywords**: messenger, boundary-crossing, aperiodic field, heptagonal, CUT/DEFEND, ether-tamas

## Canonical Devi

- **iconography_summary**: Bright like the midday sun in complexion, wearing red garments, crowned with Navaratna (nine-gem) crown and other ornaments. Carries six weapons — a warrior-messenger form, not devotional-passive. She is Shiva's emissary between the absolute and the manifest. (nitya_devi_master.csv, OBSERVED:PRIMARY, attested_classical)
- **weapons_items**: Ankusha (goad), sword, axe, pasha (noose), shield, gada (mace). Six implements — the most of any Nitya Devi in the first 10. Capability signature: CUT, DEFEND. (nitya_devi_master.csv, OBSERVED:PRIMARY)
- **mudras_gestures**: SOURCE_NEEDED: No mudra data in nitya_devi_master.csv for Sivaduti (field is empty in row 7). Primary text consultation needed (Dakshinamurti Samhita, Tantraraja Tantra).
- **vahana_mount**: SOURCE_NEEDED: No vahana data in on-disk sources. The name "Sivaduti" (Shiva's messenger) suggests a mount suited for rapid transit, but no attested source specifies one.
- **body_color**: Bright like the midday sun. Color hex: #4b0082 (indigo in the dataset, but textual description says "bright like midday sun" — the hex may represent her aura/field color rather than skin tone). (nitya_devi_master.csv)
- **ornamentation**: Navaratna crown and other ornaments. (nitya_devi_master.csv, OBSERVED:PRIMARY)
- **faces_arms_count**: SOURCE_NEEDED: Not specified in on-disk sources. Six weapons implies at least 6 arms (or some weapons are held in reserve/offered symbolically). Tantric iconographic texts needed.
- **shakti_statement**: She carries messages between the absolute and the manifest — the boundary-crossing shakti. (nitya_devi_master.csv, OBSERVED:PRIMARY)
- **expanded_function**: Sivaduti is Shiva's emissary. Her function is communication across ontological boundaries — she moves where coherent signal must travel through incoherent space. In the wave model, this maps to the 7-fold aperiodic field: a calm bindu center surrounded by irrational, never-repeating peripheral structure. The message reaches its destination, but the medium it crosses is irreducibly complex. (SYNTHESIS from nitya_devi_master.csv + CONSTRUCTION_CHOICES.md)
- **bhava_mood**: Bhayanaka (terrible/fearsome). Rasa: bhayanaka. This is not terror for its own sake — it is the awe at the boundary crossing, the uncanny. Guna: tamas. (nitya_devi_master.csv, OBSERVED:PRIMARY)
- **mantra_bija**: Hum. Full mantra: Om Hum Sivadutyai. (nitya_devi_master.csv, OBSERVED:PRIMARY)

## Lunar/Time

- **lunar_phase_arc**: 72°-84° from conjunction (shukla saptami), or 252°-264° (krishna saptami). The 7th tithi spans 12° of Sun-Moon elongation.
- **phase_quality**: Mixed (tithi_master.csv). Good for: buying property or vehicles, agriculture, community work. Avoid: marriage, sacred ceremonies. Tithi deity: Surya.
- **nitya_cycle_position**: 7th of 15. In the shukla progression, Sivaduti sits at the exact midpoint minus one — the hinge between the ascending first half and the culminating second half. After the fire-dweller (5) and the diamond-sovereign (6), the messenger arrives.
- **weekday_links**: Saptami's tithi deity is Surya; Sunday (Ravivara) is Surya's day. However, Sivaduti's own graha correspondence is Budha (Mercury) per devi_master — Wednesday (Budhavara). **Discrepancy noted**: nitya_yantra_geometry.csv assigns Saturn as graha_correspondence for tithi 7, while nitya_devi_master.csv assigns Budha. The devi_master is treated as authoritative for the devi's own graha; the yantra geometry assignment may reflect a different mapping tradition.
- **nakshatra_overlays**: SOURCE_NEEDED: No tithi-to-nakshatra fixed mapping exists in on-disk data. The wave fine structure (RESEARCH-017, Finding 10) shows that tithi-group classification (Saptami = Nanda group, tithi 2/7/12) has its strongest differentiation at even harmonics k=6 (sextile) and k=12 (rashi). Gandanta nakshatras avoid the Jaya tithis but show elevated differentiation for Nanda tithis (which includes Saptami). This is a statistical relationship, not a fixed overlay.

## Yantra

- **yantra_family**: Downward triangle (trikona) with eight petals and bhupura. (nitya_yantra_geometry.csv, SYNTHESIS — "No explicit yantra geometry is given for Sivaduti; based on patterns, assume a downward triangle with eight petals and bhupura.")
- **yantra_geometry_notes**: The yantra assignment is synthetic, not attested from Dakshinamurti Samhita or other primary tantric sources. The CONSTRUCTION_CHOICES.md notes that for the quasicrystal projection, Sivaduti uses a 7-fold multigrid — "irrational aperiodic field, still bindu, churning periphery." The traditional yantra (triangle + 8 petals + bhupura) and the computed quasicrystal (7-fold aperiodic) are complementary but distinct representations.
- **yantra_symmetry_order**: N=7 (heptagonal). This is the first non-standard, non-crystallographic symmetry in the Nitya sequence. 7-fold symmetry does not tile the plane periodically — the field is irreducibly aperiodic. (devi_engine.py DEVI_N, CONSTRUCTION_CHOICES.md)
- **yantra_center_logic**: Still bindu. In the 7-fold multigrid, the center is where all 7 plane waves constructively interfere — a calm point surrounded by chaos. "Still bindu, churning periphery." (CONSTRUCTION_CHOICES.md)
- **yantra_outer_boundary**: Bhupura with 4 gates (nitya_yantra_geometry.csv). Interference radius fraction: 0.6. Wave function: cosine, frequency multiplier: 2.
- **yantra_layer_count**: 3 layers minimum: bindu (inner circle at 0.82 scale) → 8-petal lotus → bhupura. Triangle at 0.78 scale, orientation: down. (nitya_yantra_geometry.csv)

## Field Math

- **graha_k**: Budha = k=3, magic constant M=24. (yantra_eigenvalue_exploration.md, Finding 2). However, if Saturn assignment is used (per yantra_geometry), then k=6, M=33. The Budha assignment (k=3) is used here as primary.
- **magic_constant_M**: 24 (Budha, k=3). Eigenvalues: {24, +4.899, -4.899}. The +/-2sqrt(6) invariant is universal across all grahas.
- **invariant_secondary_modes**: +/-2sqrt(6) = +/-4.8990. These are the irreducible spatial asymmetry of the Vastu Purusha Mandala. They do not depend on which graha is active. (yantra_eigenvalue_exploration.md, Finding 1)
- **coherence_ratio**: lambda_2/M = 4.899/24 = 0.2041 (Budha). This is the 4th most coherent position in the graha sequence (after Shukra 0.1633, Shani 0.1485, Rahu 0.1361, Ketu 0.1256). (Finding 2)
- **eigenvector_axes**: For Budha (k=3): Brahmasthana eigenvector = uniform [-0.577, -0.577, -0.577]. Primary tension axis and secondary tension axis are spatial polarities of the Lo Shu. (Finding 6, specific eigenvectors computed for Guru k=4; Budha k=3 follows the same structure with M=24.)
- **brahmasthana_definition**: Not a cell position but a geometric principle — the state of maximum coherence where all directions are in balance. The eigenvector for lambda_1 = M is ALWAYS uniform. This vector IS the Brahmasthana. It persists at every Kronecker level. (Finding 4)
- **kronecker_level**: Level 1: 3x3, M=24. Level 2: 9x9, M=576. Level 3: 27x27, M=13824. Scaling law: M_n = M_1^n. (Finding 3)
- **navagraha_composite_role**: Budha occupies the k=3 position in the Navagraha 9x9 composite (M_composite = 81, rank 5, null 4). The block magic constants form 3*Lo_Shu + 12*J — the composite is a magic square of magic squares. (Finding 5)

## Wave/Interference

- **boundary_harmonic_mode**: At k=7, the septile aspect appears at ~51.4° angular separation. This is NOT a classical Jyotish aspect — it falls outside the BPHS canon. The septile is the Mars prime harmonic. (two-source-interference-v3.md, Finding 8)
- **two_source_pattern**: A(theta) = cos(k(theta-alpha)) + cos(k(theta-beta)) = 2 * cos(k(theta - midpoint)) * cos(k * separation/2). At k=7: constructive maximum when separation = 360/7 = 51.43°. The carrier oscillates 7 times around the zodiac; the envelope selects pairs 51.4° apart. (Finding 8)
- **nodal_interior_pattern**: For N=7 multigrid in the disk interior: irrational aperiodic field. Unlike N=3 (periodic triangle), N=5 (Penrose), or N=6 (periodic hexagon), the 7-fold pattern never repeats. This is the first truly quasicrystalline Nitya field. (CONSTRUCTION_CHOICES.md)
- **ring_vs_disk_distinction**: On the boundary (1D zodiacal ring): 7-source pattern is SILENT for k<7, produces standing wave only at k=7 (self-resonance). In the disk interior: the 7-fold multigrid produces rich aperiodic nodal structure at all scales. The two descriptions are complementary. (Finding 7)
- **gandanta_gain**: Gandanta nakshatras (fire-water junctions) show 1.6x stronger tithi-group differentiation than non-gandanta (mean 1.72 vs 1.08, t=9.727, p<0.0001). All 6 gandanta nakshatras avoid Jaya tithis. Saptami is a Nanda tithi — gandanta nakshatras at the fire-starting end (Ashwini, Magha, Mula) PREFER Nanda tithis. (Finding 11)
- **wave_panchaka_relation**: The Panchaka system (mod-9 arithmetic, rank 9) and the wave system (trigonometric interference, effective rank 15) are orthogonal: Pearson r = -0.011. They describe independent structures on the 27x30 nakshatra-tithi space. (Finding 12)
- **quantized_prime_modes**: The planetary primes {3, 5, 7, 11} are the retrograde station symmetries. 7 = Mars. In the quantized field, overlaying cos(n*theta) for n in {3,5,7,11} with tidal weights produces 44 enclosed regions = Sri Yantra 43+1. Mars's contribution (n=7) is the weakest by tidal weight (0.013 relative to Jupiter's 1.00) but geometrically essential — removing it collapses the region count. (planetary-primes-v1.md, Section 3)

## Quasicrystal/Chladni

- **quasicrystal_line_style**: 7-fold multigrid. Generalized Penrose / multigrid method with 7 equispaced plane waves using cos interference. The construction is mathematically well-defined but does not produce a substitution tiling with known tile shapes — unlike N=5 (Penrose) or N=8 (Ammann-Beenker). (CONSTRUCTION_CHOICES.md)
- **nodal_density**: SOURCE_NEEDED: No computed nodal density metric exists on disk for N=7 specifically. The DEVI_CHARACTER description says "churning periphery" implying high peripheral density. The interference_radius_fraction (0.6) in nitya_yantra_geometry.csv is the lowest of the first 7 Nityas, suggesting a tighter central concentration.
- **radial_bands**: SOURCE_NEEDED: No explicit radial band count for N=7 computed and stored. The wave_function is cosine with frequency_multiplier=2 (nitya_yantra_geometry.csv), which would produce 2 radial nodes within the unit disk.
- **interference_centers**: The primary interference center is the bindu — where all 7 waves constructively superpose. Secondary centers exist at the 7 vertices of a regular heptagon inscribed at the interference_radius_fraction. The 3D mediator polyhedron is a heptagonal antiprism (14 triangular faces + 2 heptagonal caps). The two caps represent the two pakshas; the 14 triangular side faces represent the 14 intermediate tithis. (CONSTRUCTION_CHOICES.md)

## Pasaka/Magic Cube

- **cube_type**: Andrews 1917 (verified). 3x3x3 magic cube, values 1-27. (magic_cube_analysis.json)
- **cube_magic_constant**: M = 42. Formula: n*(n^3+1)/2, n=3. (magic_cube_analysis.json, Finding 1)
- **cube_layer_squares**: Every horizontal layer is a doubly-magic square (row sums = column sums = 42). Layer eigenvalues: layer_0 {42, -9, -9}, layer_1 {42, 0, 0}, layer_2 {42, +9, +9}. (Finding 1)
- **cube_invariant**: +/-9 = +/-3^2. This replaces the 2D Lo Shu invariant +/-2sqrt(6). The 3D invariant is rational (perfect square), unlike the 2D invariant (irrational). (Finding 2)
- **cube_center_value**: 14 = (1+27)/2. Middle layer is spectrally null when centered — the 3D Brahmasthana. (Finding 3)
- **cube_associative_sum**: Every antipodal pair sums to 28 = n^3 + 1. This is the 3D analog of Lo Shu's opposite-cell sum of 10 = n^2+1. (Finding 4)
- **cube_tensor_isotropy**: sigma_1 = 72.75 across all three tensor modes (mode-1, mode-2, mode-3 unfoldings). The cube is spectrally isotropic — no preferred axis. (Finding 6)
- **cube_kronecker_scaling**: Level-n Kronecker product: M_n = 42^n. Secondary = 9 * 42^(n-1). Same multiplicative eigenvalue scaling as Lo Shu. (magic_cube_extension.json, Finding 1)
- **cyclic_composite_eigenvalues**: 9x9 block-circulant composite: M = 126 = 3*42. Eigenvalues {126, +/-2.598, 0, 0, 0, 0}. Rank 5, null 4 — identical topology to Navagraha 9x9 (rank 5, null 4). Composite invariant: 3*sqrt(3)/2 = 2.598. (Finding 2, 6)
- **loshu_weighted_cube_mode**: Lo Shu-weighted placement concentrates all spectral energy into the uniform mode — eigenvalues collapse to {126, 0, 0, ...}. Lo Shu ordering is the maximally coherent arrangement of the 3D layers. (Finding 3)

### Pasaka at total=7

12 dice outcomes produce total=7 (the Sivaduti-resonant sum). These span the full quality range:

| ID | Dice | Name | Quality | Body | Graha | Rasa |
|----|------|------|---------|------|-------|------|
| 8 | 1,2,4 | Riddhi | good | mouth | Moon | madhura |
| 11 | 1,3,3 | Dhriti | good | left_shoulder | Saturn | tikta |
| 14 | 1,4,2 | Kirti | good | right_hand | Sun | katu |
| 20 | 2,1,4 | Maya | mixed | stomach | Rahu | tikta |
| 23 | 2,2,3 | Durga | good | right_hip | Mars | katu |
| 26 | 2,3,2 | Savitri | very_good | left_thigh | Sun | madhura |
| 29 | 2,4,1 | Indrani | very_good | right_calf | Jupiter | madhura |
| 35 | 3,1,3 | Camunda | mixed | right_sole | Saturn | tikta |
| 38 | 3,2,2 | Priya | good | back_of_head | Venus | madhura |
| 41 | 3,3,1 | Jayanti | excellent | right_cheek | Sun | katu |
| 50 | 4,1,2 | Varada | good | left_side | Jupiter | madhura |
| 53 | 4,2,1 | Tara | excellent | sternum | Moon | madhura |

Distribution: 2 excellent, 2 very_good, 6 good, 2 mixed. The total=7 family leans positive (10/12 good or better). Graha distribution: Sun 3, Moon 2, Jupiter 2, Saturn 2, Mars 1, Venus 1, Rahu 1 — Sun-dominant, echoing Saptami's tithi deity (Surya). Body distribution spans crown-to-sole with notable right-side emphasis (5 right-side points vs 2 left-side).

## I Ching

- **hexagram_id**: SOURCE_NEEDED: No fixed tithi-to-hexagram mapping exists on disk. The I Ching engine derives hexagrams from field state (Lo Shu weighted), not from a static lookup. Hexagram 7 (Shi, "The Army") is the numerical correspondent but this mapping is not attested in the Atlas system.
- **hexagram_arrangement**: The I Ching system operates across two arrangements: Fuxi (rank 2, maximally ordered, separable) and King Wen (rank 8, full rank, maximally complex). These are spectral opposites. (iching_spectral_analysis.json, Finding 7)
- **rank_complexity**: Q6 hypercube eigenvalues: {6, 4, 2, 0, -2, -4, -6} with multiplicities C(6,k) = {1, 6, 15, 20, 15, 6, 1}. The I Ching's deep structure IS Pascal's row 6. (Finding 3)
- **yin_yang_balance_mode**: Complement permutation (XOR with 63) has eigenvalues exactly {+1, -1}, each with multiplicity 32. The hexagram pairs form a perfect yin-yang partition. (Finding 6)
- **hypercube_distance_signature**: Hamming distance matrix: rank 7, eigenvalues {192 (x1), 0 (x57), -32 (x6)}. Only 3 unique eigenvalues — the distance structure is simpler than the adjacency structure. (Finding 5)
- **pascal_row_signature**: Row 6: {1, 6, 15, 20, 15, 6, 1}. Total = 64 = 2^6. The central multiplicity (20, for eigenvalue 0) is the largest — 20 of 64 hexagrams live in the null eigenspace. (Finding 3)

## Lo Shu x I Ching Bridge

- **trigram_loshu_weight_map**: Li=9, Kan=1, Zhen=3, Dui=7, Xun=4, Gen=8, Kun=2, Qian=6. Note: Dui=7 — the trigram at the Saptami position in the Lo Shu receives weight 7. (loshu_iching_interaction.json)
- **weighted_spectral_breaking**: Unweighted Q6 has 7 unique eigenvalues. Lo Shu weighting breaks this to 27 unique eigenvalues — the nakshatra number. Degeneracy is completely broken. (test4_weighted_Q6)
- **spectral_gap_change**: Unweighted gap = 2.0, weighted gap = 0.4624. Fiedler value drops from 2.0 to 0.1944. Lo Shu weighting makes the hexagram graph less uniformly connected — introduces hierarchical structure. (test5_spectral_gap)

## Alchemical/Bhasma

- **material_classical_class**: Mercury (Hg, Parada) is Budha's metal. In the rasashastra classification: Parada is the Rasa (first-class, supreme substance). (Bhasma docx, substance ontology)
- **material_scientific_type**: Hg — liquid metal, element 80. Amalgam-forming with Ag (Moon), Sn (Jupiter), Au (Sun). Uniquely liquid at room temperature among metals.
- **base_material**: Parada (mercury/quicksilver). The rasashastra tradition treats Parada as the king of substances. Budha's gem correspondence is emerald (Panna / Marakata).
- **prepared_substance_type**: Kajjali (mercury-sulphur black powder) is the starting material for most mercurial preparations. Parada Bhasma is mercury incinerated to oxide form. (Bhasma docx, process ontology)
- **shodhana_media**: SOURCE_NEEDED: Specific shodhana (purification) media for Parada not detailed in on-disk sources. Classical texts specify sequential quenching in defined plant juices and acids. The Bhasma docx describes the general shodhana-bhavana-marana cascade but not Parada-specific media.
- **bhavana_media**: SOURCE_NEEDED: Specific trituration media for Parada bhasma preparation not in on-disk sources. Generally involves plant decoctions (e.g., kumari/aloe, nimba/neem) as wet grinding media.
- **marana_cycles**: SOURCE_NEEDED: Number of incineration cycles for Parada bhasma not specified in on-disk sources. Different texts prescribe different counts. The general principle: repeated puta cycles until the bhasma passes quality tests (nischandratva, rekhapurnatva, varitaratva).
- **puta_profile**: SOURCE_NEEDED: Temperature/duration profile for Parada-specific puta not on disk. The Bhasma docx describes puta as a "heat-cycle unit" but gives specific examples only for Praval (coral) and Lauha (iron) bhasma.
- **quality_tests**: Classical tests: nischandratva (no metallic lustre), rekhapurnatva (fills finger lines), varitaratva (floats on water). Phase transformation: from metallic Hg to HgO or HgS. (Bhasma docx, general framework)
- **completion_stop_rule**: When all classical quality tests pass simultaneously. Modern lab verification: XRD phase identification, particle size below threshold. (Bhasma docx)
- **phase_transformation**: Hg (liquid metal) -> HgO (mercuric oxide, red/yellow) or HgS (cinnabar, when sulphur-processed). The liquid-to-solid transformation is the most dramatic in all bhasma preparation — the only metal that starts liquid. (SYNTHESIS from chemistry + Bhasma docx context)
- **particle_scale_overlay**: SOURCE_NEEDED: No specific particle size data for Parada bhasma on disk. The general principle from the docx: bhasmas are submicron to nanoscale after proper marana.
- **safety_conditions**: Mercury compounds are toxic. Parada preparations require strict processing governance. The Bhasma docx notes: "Visa / Upavisa: toxic plants/substances used with strict processing frameworks." Mercury is the paradigm case of a substance that is supremely therapeutic when properly prepared and supremely toxic when improperly handled. (SYNTHESIS)

## Graha/Material

- **graha_material_map**: Budha (Mercury) -> Parada (mercury metal), Marakata (emerald). In the BPHS friendship table: Budha's friends are Sun and Venus; enemies: Moon (asymmetric — Moon considers Budha a friend). Budha is neutral to Mars, Jupiter, Saturn. (Graha Material docx)
- **friend_enemy_interaction**: Moon-Mercury asymmetry (Ag-Hg): Silver forms amalgams with mercury — Moon "dissolves into" Budha's influence. The asymmetry is materialized: Ag dissolves readily into Hg (Moon into Mercury), but Hg does not dissolve into solid Ag (Mercury does not enter Moon's domain). Jupiter-Mercury (Sn-Hg): Tin-mercury amalgam (Sn8Hg, gamma-2) is corrosion-susceptible — the "problematic phase" in dental amalgam. Jupiter lists Mercury as enemy; Mercury lists Jupiter as neutral. (Graha Material docx)
- **ritual_vs_medical_flag**: Medical. Parada preparations are therapeutic (rasaushadhi), not ritual objects. However, the Parada Shivalinga (mercury solidified into linga form) IS a ritual object. The distinction: bhasma = medical; solidified form = ritual. (SYNTHESIS)

## Plant/Ecology

- **plant_allies**: SOURCE_NEEDED: No graha-to-plant mapping at the Budha level exists in the on-disk plant datasets (guild_full.csv has no graha column). Traditional Budha-associated plants include: Tulsi (Ocimum), Ashwagandha (Withania), green leafy herbs generally. Emerald-green plants carry the Budha signature in doctrine of signatures.
- **processing_plants**: Plants used as bhavana/shodhana media in Parada processing: Kumari (Aloe vera), Nimba (Azadirachta indica), Triphala (three-fruit combination), cow urine. These are the "plant operators" in the metal transformation pipeline. (Bhasma docx, general framework)
- **doctrine_of_signatures_overlay**: SOURCE_NEEDED: No systematic doctrine-of-signatures dataset on disk. The principle: Budha-plants should show mercurial qualities — quick-growing, nervous-system-active, communication-enhancing, green-stemmed. This needs sourcing from the plant profiles docx.
- **astrobotanical_timing**: SOURCE_NEEDED: No Budha-specific planting/harvesting timing dataset. The general framework exists in the Atlas (nakshatra overlays in tithi_master + plant data in guild_full), but the cross-reference for Saptami-specific timing is not computed.

## Body/Therapeutics

- **dosha_predicates**: Tithi 7 element: air (tithi_master.csv), guna: sattva. Devi element: ether (nitya_devi_master.csv), guna: tamas. Chakra: Svadhishthana (Mercury/Budha correspondence) — water element, Vata & Pitta dosha, Rakini shakti. (chakra_cross_domain.csv). The air/ether/water triad across the three source systems suggests a Vata-dominant profile with Pitta secondary.
- **dhatu_targets**: SOURCE_NEEDED: No dhatu (tissue) targeting data for Budha/Saptami on disk. Traditional: Budha governs Rasa dhatu (plasma/lymph) and Majja dhatu (nerve/marrow) — the communication tissues.
- **organ_targets**: Svadhishthana (Budha chakra): reproductive and urinary organs (ovaries/testes). Body system: "Sexual organs, kidneys, urinary system." Psychological domain: "Creativity, sexuality, pleasure and self-worth." (chakra_cross_domain.csv). Pasaka body mapping at total=7 spans: mouth, left shoulder, right hand, stomach, right hip, left thigh, right calf, right sole, back of head, right cheek, left side, sternum — a full-body distribution with right-side emphasis.
- **indication_clusters**: SOURCE_NEEDED: No specific therapeutic indication clusters for Saptami/Budha on disk. Traditional: Budha disorders include speech problems, skin conditions, nervous disorders, learning difficulties.
- **anupana_vehicle**: SOURCE_NEEDED: No anupana (carrier substance) data for Budha-specific preparations on disk.
- **preparation_dependency_warning**: Mercury preparations require expert supervision. Improperly prepared Parada compounds are neurotoxic. Never self-administer Parada bhasma without verified provenance and classical quality tests. (SYNTHESIS from safety literature)

## Prime/Morphology

- **prime_signature**: 7 is Mars's retrograde station count and the 4th prime. In the planetary prime sequence {3, 5, 7, 11}, 7 is the third element — the "middle voice" between the inner planets' quick primes (3, 5) and Jupiter's large prime (11). Mars traces a heptagram across 15 years. (planetary-primes-v1.md, Section 2)
- **morphology_correlates**: C7 = 7 cervical vertebrae in virtually all mammals. This is Mars's prime, the most conserved vertebral count in Mammalia (exceptions: manatees C6, sloths C6-9). The Hox gene expression boundary at the cervical-thoracic transition is deeply conserved. Mars's tidal influence is 75x weaker than Jupiter's, yet the morphological encoding is the most invariant. (planetary-primes-v1.md, Section 4). Micro-CT trabecular bone prediction (untested): cervical trabeculae should show 7-fold symmetry clusters in cross-section. (Section 4, "what would strengthen the case")
- **sri_yantra_region_relation**: The 44-region tidal-weighted quantized field uses Mars at n=7 with weight 0.013 (relative to Jupiter=1.00). Mars's geometric contribution (k=7 mode) is essential to reach the 44-region count; removing it drops the count. The k=7 mode provides fine angular partitioning that lower-k modes cannot. (planetary-primes-v1.md, Section 3)

## Sound/Rhythm

- **svara_link**: SOURCE_NEEDED: No tithi-to-svara mapping on disk. Budha's traditional svara association is not specified in the raga_data.csv. In Gandharva Veda tradition, Budha corresponds to the note Ri (Rishabha) — but this needs primary source attestation.
- **raga_link**: Mercury-associated ragas in raga_data.csv: Lalit (dawn, spring, air/sattva, shanta; vadi Ma#, samvadi Re), Miya Malhar (evening, monsoon, water/rajas, adbhuta), Jhinjhoti (night, monsoon, water/rajas, hasya). Of these, Lalit is the closest to Sivaduti's character — a dawn raga with an augmented 4th (Ma#) that creates an eerie, boundary-crossing tonal quality. (raga_data.csv)
- **tala_link**: SOURCE_NEEDED: No tithi-to-tala mapping on disk. The 7-fold prime suggests a 7-beat cycle (Misra Chapu in Carnatic, or Rupak in Hindustani — both 7-beat talas). This is structural correspondence, not attested mapping.

## Vastu/Spatial

- **mandala_zone_map**: Budha at k=3 in the Lo Shu places the yantra values as Lo_Shu + 3*J = {7, 12, 11; 14, 8, 6; 9, 10, 13}. The Brahmasthana (center cell) = 8 = Budha's yantra center. The eigenvector structure follows Finding 6: uniform (M=24), primary tension (NE-SW axis), secondary tension (perpendicular). (yantra_eigenvalue_exploration.md)
- **directional_emphasis**: SOURCE_NEEDED: No Budha-specific Vastu directional prescription on disk. Traditional: Budha governs the North direction in some systems, Northeast in others. The Lo Shu placement puts Budha at the NW (Gen=8) / SE axis region in the eigenvector polarity.

## Visual Grammar

- **palette_logic**: Primary: #4b0082 (indigo, from nitya_devi_master.csv). Secondary: #F8BBD0 (light pink, from nitya_yantra_geometry.csv). Bindu: #D50000 (deep red). Line weight: medium. Body color: bright midday sun (suggests gold/white render for the figure itself, indigo for the field surround).
- **density_logic**: interference_radius_fraction = 0.6 (tightest of first 7 Nityas). The 7-fold aperiodic field has high peripheral density but a clear center — "still bindu, churning periphery." Render should show sparse center, dense fractal-like edges.
- **line_weight_logic**: Medium (nitya_yantra_geometry.csv). The 7-fold multigrid lines should be rendered at consistent weight — the aperiodic complexity comes from geometry, not line variation.
- **panel_layout**: SOURCE_NEEDED: No panel layout specification exists for the card deck yet. This is a design decision for the diviner's manual, not a data field.
- **symbol_strip**: CUT + DEFEND (capability signature). 6 weapons (ankusha, sword, axe, pasha, shield, gada). Navaratna crown. Heptagram star. Bija: Hum.
- **caption_motto**: "She carries messages between the absolute and the manifest." (nitya_devi_master.csv, description field)

---

## Cross-layer observations

The most striking resonance across layers is the **7-fold structural constant operating at three scales simultaneously**. In the sky, Mars traces a heptagram of retrograde stations across 15 years (planetary-primes). In the body, 7 cervical vertebrae are the most conserved morphological count in all of Mammalia (vertebral-primes). In the wave field, the k=7 septile harmonic is the boundary between classical and non-classical Jyotish aspects — the first aspect mode that BPHS does not name (two-source-interference, Finding 8). And in the quasicrystal, N=7 is the first non-crystallographic symmetry that produces a genuinely aperiodic field — it cannot tile periodically, cannot repeat, cannot be reduced.

The second resonance is the **messenger paradox in the bhasma/material layer**: Sivaduti's graha is Budha (Mercury), whose metal is the only one that is liquid at room temperature. A messenger must be fluid to cross boundaries. The shodhana process for Parada (mercury) transforms liquid into solid — the message crystallized, the boundary crossing completed. The Moon-Mercury asymmetry in the BPHS friendship table (Moon considers Mercury a friend; Mercury considers Moon an enemy) has a direct material analog: silver dissolves readily into liquid mercury (amalgam), but mercury does not enter solid silver. The messenger receives but does not reciprocate.

The third resonance is the **Saptami as Nanda tithi and the gandanta amplification pattern**. Saptami belongs to the Nanda group (tithis 2, 7, 12) — the "bliss" tithis. Fire-starting gandanta nakshatras (Ashwini, Magha, Mula) specifically PREFER Nanda tithis in the wave fine structure, with elevated differentiation scores (mean 1.72 vs 1.08). So when a gandanta nakshatra falls on Saptami, the Sivaduti field is amplified — the messenger's signal is strongest at the fire-water boundary crossings.

---

## Attestation summary

- **OBSERVED:PRIMARY** (direct from primary text / dataset row): Identity (name, bija, mantra, weapons, description, body color, ornamentation, rasa, element, guna, shakti from nitya_devi_master.csv); Lunar/Time (tithi quality, deity, good_for/avoid from tithi_master.csv); Pasaka outcomes (pasaka.csv).
- **OBSERVED:TRADITIONAL** (widely accepted, multi-source): Yantra base structure (triangle + 8 petals + bhupura pattern from Dakshinamurti Samhita tradition, though Sivaduti's specific geometry is synthetic); Bhasma substance classes and process spine (docx sources citing API, classical texts).
- **SYNTHESIS** (Atlas-level inference): Field Math (graha_k assignment, eigenvalue derivation); Wave/Interference (all findings from two-source interference research); Quasicrystal (7-fold multigrid construction); Prime/Morphology (correspondence claims); Cross-layer observations; expanded_function; safety_conditions; phase_transformation; raga/tala associations.
- **GENERATED** (invented for this card): None. All SOURCE_NEEDED fields are left flagged rather than filled with invented content.

---

## SOURCE_NEEDED flags

1. **mudras_gestures**: Primary tantric text (Dakshinamurti Samhita, Tantraraja Tantra) consultation for Sivaduti-specific mudra. Chat history retrieval from session where devi data was compiled.
2. **vahana_mount**: Same sources as above. May not exist in texts — not all Nitya Devis have attested vahanas.
3. **faces_arms_count**: Tantric iconographic source. The 6 weapons suggest multi-armed form but exact count unattested.
4. **nakshatra_overlays**: Compute the specific wave fine structure profile for Saptami across all 27 nakshatras. The data exists in the engine (RESEARCH-017 methodology) but hasn't been extracted to a lookup table.
5. **nodal_density**: Run N=7 multigrid computation and extract density metric. The code exists in cut_and_project.py.
6. **radial_bands**: Same computation as nodal_density.
7. **hexagram_id**: User decision: whether to map tithi 7 → hexagram 7 (Shi) statically, or to keep the dynamic field-derived mapping. The engine currently uses field derivation.
8. **shodhana_media / bhavana_media / marana_cycles / puta_profile / particle_scale_overlay**: Parada-specific rasashastra processing details. The 4 docx files in research/ contain general framework but not Parada-specific protocols. Primary text: Rasa Ratna Samucchaya (RRS), Rasarnava, Rasaprakasha Sudhakara.
9. **plant_allies**: Create graha-to-plant cross-reference from guild_full.csv + traditional Budha plant associations. The plant profiles docx may contain this.
10. **doctrine_of_signatures_overlay**: Extract from plant profiles docx or create from traditional sources.
11. **astrobotanical_timing**: Compute Saptami-specific planting windows from nakshatra x tithi matrix.
12. **dhatu_targets / indication_clusters / anupana_vehicle**: Ayurvedic text consultation for Budha-specific therapeutic protocols.
13. **svara_link**: Gandharva Veda source for tithi-svara mapping.
14. **tala_link**: Same source as svara_link, or user decision on 7-beat cycle assignment.
15. **directional_emphasis**: Vastu text consultation for Budha directional governance.
16. **panel_layout**: Design decision, not a data retrieval task.
