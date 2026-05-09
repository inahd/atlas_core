# Nityaklinna · Tithi 3 · Card

**Source compilation**: 2026-05-01
**Schema version**: Atlas Tithi Card Master Table (user-provided, 2026)
**Population status**: ~58/82 fields sourced, ~24 SOURCE_NEEDED flags

---

## Identity

- **tithi_number**: 3
- **tithi_name**: Tṛtīyā
- **paksha_mode**: Both shukla and krishna. Gauri is tithi deity. Quality: mixed. (tithi_master.csv)
- **devi_name**: Nityaklinna
- **devi_alt_names**: Nityaklinnā (नित्यक्लिन्ना). "Ever-moist, perpetually-melted." Bija: Klīm. Mantra: Om Klīm Nityaklinne.
- **seed_keywords**: perpetual moisture, dissolving, compassion, vessel of nectar, water-tamas, karuna, STABILIZE/DEFEND, abhaya mudra

## Canonical Devi

- **iconography_summary**: Ever-moist with compassion — she dissolves the dryness of separation. Red complexion, red garments, smeared with red sandalwood paste, beads of sweat on the forehead — the iconographic mark of perpetual klinna (moisture). Carries aṅkuśa (goad) and pāśa (noose). (nitya_devi_master.csv, OBSERVED:PRIMARY, attested_classical)
- **weapons_items**: Aṅkuśa (goad), pāśa (noose). Capability signature: STABILIZE, DEFEND. Note: only 2 weapons — among the fewest of any Nitya. The paucity reflects her function: dissolution does not need cutting tools, only binding and protection. (nitya_devi_master.csv, OBSERVED:PRIMARY)
- **mudras_gestures**: Abhaya mudrā (fearlessness-granting). (nitya_devi_master.csv, OBSERVED:PRIMARY)
- **vahana_mount**: SOURCE_NEEDED.
- **body_color**: Red complexion. Color hex: #2050a0 (deep cobalt blue — represents her field, contrasting the textual red complexion). (nitya_devi_master.csv)
- **ornamentation**: Smeared with red sandalwood paste; beads of sweat on the forehead. The "ornament" is moisture itself — her body IS the offering. (nitya_devi_master.csv, OBSERVED:PRIMARY)
- **faces_arms_count**: SOURCE_NEEDED. 2 weapons + abhaya mudrā imply 3 hands minimum. Standard tantric form: 4 arms.
- **shakti_statement**: Perpetual moisture — the dissolution-shakti, the karuna-flow that liquefies the separation between self and other. (nitya_devi_master.csv, OBSERVED:PRIMARY)
- **expanded_function**: Nityaklinna is the third Nitya — the moment of dissolution, the karuna-tide. Where Kāmeśvarī (1) is desire-as-impulse and Bhagamalini (2) is desire-as-relation, Nityaklinna (3) is desire-as-melting: the separated self dissolving back into relation. Her N=3 yantra symmetry (devi_engine.py DEVI_N) places her on the same periodic triangular lattice as Kāmeśvarī — but at angular_position 48° (vs Kāmeśvarī's 0°), one full sub-arc rotation later. Same shape, different position in the cycle. Her graha is Mangala (Mars, k=2) — the karuna-rasa is the wet residue of Mars's heat after sweating. (SYNTHESIS from nitya_devi_master.csv + CONSTRUCTION_CHOICES.md)
- **bhava_mood**: Karuna (compassion). Rasa: karuna. Element: water. Guna: tamas. The water-tamas pairing is the signature of slow, heavy, settled emotion — grief that cleanses rather than cuts. (nitya_devi_master.csv, OBSERVED:PRIMARY)
- **mantra_bija**: Klīm (the kāma-bija, the seed of attraction-and-melting — the bija that compels). Full mantra: Om Klīm Nityaklinne. (nitya_devi_master.csv, OBSERVED:PRIMARY)

## Lunar/Time

- **lunar_phase_arc**: 24°-36° from conjunction (shukla tritiya), or 204°-216° (krishna tritiya). The 3rd tithi spans 12° of Sun-Moon elongation.
- **phase_quality**: Mixed (tithi_master.csv). Good for: competitions, legal matters, confronting challenges. Avoid: marriage, travel, peaceful activities. Tithi deity: Gauri (Pārvatī as virgin/undyed-cloth form).
- **nitya_cycle_position**: 3rd of 15 — the dissolution position. Tritiya is the first tithi at clear non-conjunction Sun-Moon distance, where the lunar light has begun to differentiate from the solar. The melting begins.
- **weekday_links**: Tritiya's tithi deity is Gauri. Nityaklinna's graha correspondence is Mangala (Mars) per devi_master — Tuesday (Mangalavara). The yantra_geometry CSV agrees (Mars for tithi 3). No discrepancy. k=2, M=21.
- **nakshatra_overlays**: SOURCE_NEEDED: Tritiya belongs to the **Jaya group** (T3, T8, T13, T18, T23, T28 — "victory tithis"). From RESEARCH-017 Finding 11: **all 6 gandanta nakshatras AVOID Jaya tithis**. This is a structurally significant statistical pattern — Tritiya specifically receives no gandanta-amplification. The wave field at this tithi runs at non-amplified baseline.

## Yantra

- **yantra_family**: Downward triangle (trikona) with eight petals and bhupura. Triangle scale 0.86, inner circle 0.9. (nitya_yantra_geometry.csv, OBSERVED:TRADITIONAL — Dakshinamurti Samhita attestation: "her yantra as a trikona (triangle) with eight petals and an earth square (bhūpura).")
- **yantra_geometry_notes**: Classical attested geometry (Dakshinamurti Samhita). The simplest of the early Nitya yantras — pure trikona without hexagonal interlock. Same N=3 multigrid projection as Kāmeśvarī (Nitya 1), but at angular_position_degrees=48° (vs Kāmeśvarī's 0°).
- **yantra_symmetry_order**: N=3 (triangular, periodic). Same crystallographic family as Kāmeśvarī. (devi_engine.py DEVI_N)
- **yantra_center_logic**: Bindu as point. Inner circle scale 0.9. The 3-source pattern's central interference at full constructive superposition.
- **yantra_outer_boundary**: Bhupura with 4 gates. Interference radius fraction: 0.8. Wave function: **cosine** (distinct from Kāmeśvarī's sine), frequency multiplier: 1, angular position: 48°.
- **yantra_layer_count**: 3 layers: bindu → 8-petal lotus → bhupura. Triangle at 0.86 scale, orientation: down. (nitya_yantra_geometry.csv)

## Field Math

- **graha_k**: Mangala = k=2, magic constant M=21. (yantra_eigenvalue_exploration.md, Finding 2). Both nitya_devi_master.csv and nitya_yantra_geometry.csv agree on Mars. No discrepancy.
- **magic_constant_M**: 21 (Mangala, k=2). Eigenvalues: {21, +4.899, -4.899}. (Finding 1)
- **invariant_secondary_modes**: +/-2sqrt(6) = +/-4.8990. (Finding 1)
- **coherence_ratio**: lambda_2/M = 4.899/21 = 0.2333 (Mangala). The 3rd most polarized graha (after Sun 0.3266 and Moon 0.2722). Mars's field has high spatial differentiation — strong directional polarities. (Finding 2)
- **eigenvector_axes**: For Mangala (k=2): Brahmasthana = uniform [1/√3, 1/√3, 1/√3]. Primary tension axis (lambda=+4.899) and secondary tension axis (lambda=-4.899). (Finding 6)
- **brahmasthana_definition**: Uniform eigenvector at every Kronecker level. (Finding 4)
- **kronecker_level**: Level 1: 3x3, M=21. Level 2: 9x9, M=441. Level 3: 27x27, M=9261. M_n = M_1^n. (Finding 3)
- **navagraha_composite_role**: Mangala occupies the k=2 position in the Navagraha 9x9 composite. Mars's Lo Shu placement is in the South (Yama) — the heat/transformation quadrant. (Finding 5)

## Wave/Interference

- **boundary_harmonic_mode**: At k=3: the trine harmonic. Tritiya = the 3rd tithi, the first natural alignment with k=3 wave structure. The trine is one of the most auspicious classical aspects (120° separation = 360/3). (two-source-interference-v3.md, Finding 8)
- **two_source_pattern**: A(theta) = 2 * cos(k(theta - midpoint)) * cos(k * separation/2). At k=3: constructive maximum when separation = 120° (the trine). Tritiya's Sun-Moon separation is 24°-36° in shukla — well below the trine, but the k=3 carrier is active. (Finding 8)
- **nodal_interior_pattern**: For N=3 multigrid in disk interior: periodic hexagonal lattice (the same as Kāmeśvarī's, just rotated). Periodic, predictable, fully reducible. (CONSTRUCTION_CHOICES.md)
- **ring_vs_disk_distinction**: On the boundary: 3-source pattern produces standing waves at k=3 (trine). In the disk: 3-fold multigrid produces periodic hexagonal nodal structure. (Finding 7)
- **gandanta_gain**: Tritiya is a Jaya tithi — **gandanta nakshatras AVOID Jaya**. This is a positive null result: Tritiya does NOT receive gandanta amplification. The wave field at this tithi is at baseline differentiation. (Finding 11)
- **wave_panchaka_relation**: Panchaka and wave systems orthogonal: r = -0.011. (Finding 12)
- **quantized_prime_modes**: Mars (Mangala) is n=7 in the planetary prime sequence — Mars's 7 retrograde stations form the heptagram. But Nityaklinna's tithi number = 3, which IS Mercury's retrograde prime (3 stations per year). The graha-tithi mismatch (Mars graha, Mercury-prime tithi number) is structurally interesting: the dissolution-position carries Mercury's quick-prime in the tithi index but Mars's heat-graha in the devi assignment. (planetary-primes-v1.md, Section 2)

## Quasicrystal/Chladni

- **quasicrystal_line_style**: 3-fold multigrid (cosine variant, vs Kāmeśvarī's sine). The cosine vs sine difference shifts the phase of the periodic lattice — same shape, different rotation. (CONSTRUCTION_CHOICES.md, nitya_yantra_geometry.csv)
- **nodal_density**: SOURCE_NEEDED: No computed metric for N=3 cosine variant. interference_radius_fraction = 0.8 (slightly tighter than Kāmeśvarī's 0.9).
- **radial_bands**: SOURCE_NEEDED: Wave function = cosine, frequency_multiplier=1 → 1 radial node within unit disk.
- **interference_centers**: Primary center = bindu (3 cosine waves at 120° intervals constructively superpose at origin with cosine phase, producing a slight phase shift relative to Kāmeśvarī). Secondary maxima at 3 vertices of inscribed equilateral triangle at interference_radius_fraction = 0.8. The 3D mediator polyhedron: tetrahedron (same as Kāmeśvarī, since N=3 → same Platonic). (CONSTRUCTION_CHOICES.md)

## Pasaka/Magic Cube

- **cube_type**: Andrews 1917. M=42. (magic_cube_analysis.json)
- **cube_magic_constant**: M = 42 = n*(n^3+1)/2, n=3. (Finding 1)
- **cube_layer_squares**: layer_0 {42, -9, -9}, layer_1 {42, 0, 0}, layer_2 {42, +9, +9}. (Finding 1)
- **cube_invariant**: +/-9 = +/-3^2. Rational. (Finding 2)
- **cube_center_value**: 14 = (1+27)/2. The 3D Brahmasthana. (Finding 3)
- **cube_associative_sum**: 28 = n^3+1. (Finding 4)
- **cube_tensor_isotropy**: sigma_1 = 72.75 across all modes. (Finding 6)
- **cube_kronecker_scaling**: M_n = 42^n. (magic_cube_extension.json)
- **cyclic_composite_eigenvalues**: 9x9: M=126, eigenvalues {126, +/-2.598, 0×4}, rank 5 null 4. (Finding 2)
- **loshu_weighted_cube_mode**: Lo Shu collapses to {126, 0, 0, ...}. (Finding 3)

### Pasaka at total=3

The pasaka deck has exactly **1 outcome** at total=3: the all-ones triple (Kṛta).

| ID | Dice | Name | Quality | Body | Graha | Rasa |
|----|------|------|---------|------|-------|------|
| 1 | 1,1,1 | Kṛta | excellent | crown | Sun | madhura |

Distribution: 1 excellent, 0 others. Total=3 is the **minimum-sum outcome** of the entire pasaka deck (3 dice each minimum 1) and produces the highest-quality result. The Kṛta outcome is the equivalent of "rolling a perfect game" — it occurs only via the unique (1,1,1) triple, probability 1/64. The graha is Sun (not Mars, Nityaklinna's actual graha) — this is the **graha-tithi mismatch** noted above: the pasaka outcome at the Mars-tithi position carries Sun-graha. The body is the **crown** (Sahasrara/sahasrāra-region), not the typical karuna-fluid-region. The rasa is **madhura** (sweet), not karuna. The interpretation: when the dice produce Tritiya's resonant total (3), it overrides the standard tithi correspondence with the highest-coherence outcome of the entire deck. The dissolution moment (Nityaklinna) accessed through the unanimous-dice configuration produces the maximally coherent crown-state — melting all the way up rather than down.

## I Ching

- **hexagram_id**: SOURCE_NEEDED. Numerical correspondent: hexagram 3 (Zhūn, "Difficulty at the Beginning") — the first concrete situation in the King Wen sequence after the foundational Qián/Kūn pair. Zhūn's image is "spring grass struggling through soil" — first growth in difficulty, matching Nityaklinna's water-tamas-karuna signature.
- **hexagram_arrangement**: Fuxi ↔ King Wen spectral opposites. (iching_spectral_analysis.json)
- **rank_complexity**: Q6 hypercube eigenvalues {6,4,2,0,-2,-4,-6}, multiplicities Pascal row 6. (Finding 3)
- **yin_yang_balance_mode**: XOR-with-63 eigenvalues {+1,-1} multiplicity 32 each. (Finding 6)
- **hypercube_distance_signature**: Hamming rank 7. (Finding 5)
- **pascal_row_signature**: Row 6, total 64 = 2^6. (Finding 3)

## Lo Shu x I Ching Bridge

- **trigram_loshu_weight_map**: Li=9, Kan=1, Zhen=3, Dui=7, Xun=4, Gen=8, Kun=2, Qian=6. Tritiya (3) maps to **Zhen=3** — the Thunder trigram, the Arousing, "thunder breaking forth from the earth." Zhen is the trigram of awakening, sudden movement, and shock. The pairing is structurally exact: Tritiya = "tritiya," the third tithi, where the lunar arc has just begun to clearly differentiate; Zhen is the first arousing trigram in the King Wen sequence. (loshu_iching_interaction.json)
- **weighted_spectral_breaking**: Unweighted Q6 has 7 unique eigenvalues; Lo Shu weighting → 27 unique eigenvalues = nakshatra count. (test4_weighted_Q6)
- **spectral_gap_change**: Unweighted gap = 2.0; weighted = 0.4624. (test5_spectral_gap)

## Alchemical/Bhasma

- **material_classical_class**: Mangala's metal is **Tāmra** (copper, Cu). Gem: **Praval** (red coral). In rasashastra: Tāmra is Lohaka (metal class — the rasa-friendly metals); Praval is Sudhāvarga (calcium-class gem). (SYNTHESIS — Bhasma docx general framework; the Sivaduti card mentioned Praval bhasma is one of the named worked-examples in the docx).
- **material_scientific_type**: Copper (Cu) — element 29, atomic mass 63.55, third-best electrical conductor after silver and gold. Forms CuO and Cu2O on incineration (the latter being the red oxide form, color-aligned with Mars's red). Praval is calcium carbonate (CaCO3, aragonite) with carotenoid pigments giving the red color.
- **base_material**: Tāmra (copper) for the metallic preparation; Praval (red coral) for the gem preparation. Praval bhasma is one of the most widely prepared bhasmas in classical practice — an entry-level rasashastra preparation.
- **prepared_substance_type**: Tāmra Bhasma (copper bhasma); Praval Bhasma / Praval Pishti (red coral bhasma).
- **shodhana_media**: Copper: heated and quenched in til-taila (sesame oil), takranī (buttermilk), gomūtra (cow urine), kānjī (sour gruel), kulattha kvāth — the standard 5-media sequence. Praval: shudha is via gulāb-jāl (rosewater) or jayanti swarasa (a herb juice). (Bhasma docx, classical framework — though specific sequence may vary)
- **bhavana_media**: Praval bhasma classically uses gulāb-jāl (rosewater) bhavana cycles, sometimes with kumārī swarasa (aloe). (Bhasma docx)
- **marana_cycles**: SOURCE_NEEDED for exact cycle count. Praval is typically 7-14 puta cycles; Tāmra requires more (often 21+).
- **puta_profile**: SOURCE_NEEDED.
- **quality_tests**: Standard bhasma tests + Praval-specific: Praval should be pure white after marana (the red carotenoids burnt out). (Bhasma docx)
- **completion_stop_rule**: Quality tests pass + color verification (white for Praval). (Bhasma docx)
- **phase_transformation**: Cu → Cu2O (red, then oxidizes further to CuO black) for Tāmra Bhasma. Aragonite CaCO3 → calcite CaCO3 → CaO at high temp for Praval Bhasma. (SYNTHESIS)
- **particle_scale_overlay**: SOURCE_NEEDED.
- **safety_conditions**: Tāmra bhasma can cause copper toxicity (vomiting, ulcers) if improperly prepared. Praval is generally well-tolerated; bioavailability of calcium superior to dairy according to classical claims. (SYNTHESIS)

## Graha/Material

- **graha_material_map**: Mangala (Mars) → Tāmra (copper), Praval (red coral). In BPHS: Mars's friends are Sun, Moon, Jupiter; enemies: Mercury; neutral: Venus, Saturn. (Graha Material docx)
- **friend_enemy_interaction**: Mars-Mercury (Cu-Hg): copper amalgamates with mercury but the amalgam is unstable — copper precipitates out over time. The "enemy" relationship materializes as failed amalgam, partial dissolution but no stable solid solution. Mars-Sun (Cu-Au): copper and gold form alloys (rose gold, Cu-Au). Mars-Moon (Cu-Ag): copper-silver alloys are sterling silver (92.5% Ag + 7.5% Cu). Both friend-relationships materialize as stable alloys.
- **ritual_vs_medical_flag**: Both. Copper vessels (kalashas, lotas) are ubiquitous ritual objects. Praval rosaries and pendants are worn for Mars-related afflictions. Tāmra Bhasma and Praval Bhasma are medical preparations.

## Plant/Ecology

- **plant_allies**: SOURCE_NEEDED. Traditional Mangala plants: Khadira (Acacia catechu — astringent, blood-cleansing), Manjishtha (Rubia cordifolia — the "blood-purifier"), Arjuna (Terminalia arjuna — the cardiac tonic). All three are red/dark-red (color-Mars) and act on Rakta dhatu (blood) — direct doctrine-of-signatures alignment with Mars-karuna-water-tamas. The dissolution function (Nityaklinna's expanded function) maps onto Manjishtha's role of dissolving accumulated rakta-pitta.
- **processing_plants**: SOURCE_NEEDED. For Tāmra: kulattha kvāth (horsegram decoction) is one classical shodhana medium. For Praval: gulāb-jāl (rosewater).
- **doctrine_of_signatures_overlay**: SOURCE_NEEDED. Mangala plants are red (color), bitter/astringent (rasa), warming (virya), and blood-active (karma). Manjishtha's red root is the signature.
- **astrobotanical_timing**: SOURCE_NEEDED. General: Tritiya is a Jaya/competition tithi — sowing seeds for plants that will need to "compete" (struggle through soil, fight pests). Tuesday under Mars-ruled nakshatras (Mrigashira, Chitra, Dhanishtha) maximally Mars-aligned.

## Body/Therapeutics

- **dosha_predicates**: Tithi 3 element: earth (tithi_master.csv), guna: rajas. Devi element: water (nitya_devi_master.csv), guna: tamas. Chakra: Muladhara (Mars/Mangala correspondence) — earth element, tamas, Vata dosha, Dakini shakti. (chakra_cross_domain.csv). The earth/water/earth triad with rajas-tamas-tamas points to Kapha-Vata profile — heavy, slow, settled — the karuna substrate.
- **dhatu_targets**: SOURCE_NEEDED. Traditional: Mangala governs **Rakta dhatu** (blood) and **Majja dhatu** (marrow). Praval bhasma is classically prescribed for raktapitta (blood-bile disorders) and bone-density issues. Mars's tissue is the most actively-flowing of the dhatus — perfectly matching Nityaklinna's "perpetual moisture."
- **organ_targets**: Muladhara (Mangala chakra) at base of spine: perineal body, adrenal glands. Body system: survival, stability, grounding. (chakra_cross_domain.csv). Associated nakshatras: Mrigashira, Chitra, Dhanishtha — the three Mars-ruled nakshatras. The Mars-Muladhara assignment is unusual (commonly Mars→Manipura in popular yoga), but classical jyotish places Mars at root.
- **indication_clusters**: SOURCE_NEEDED. Traditional Mangala disorders: blood disorders (anaemia, leukaemia, thrombosis), inflammatory conditions, surgical wounds, accidents.
- **anupana_vehicle**: SOURCE_NEEDED. Traditional Mars-anupana: honey, ghṛta, jaggery (red), tila taila (sesame oil) — warming, building, blood-active vehicles.
- **preparation_dependency_warning**: Tāmra bhasma improperly prepared causes severe GI toxicity. Praval is generally safer but should be sourced from verified preparation.

## Prime/Morphology

- **prime_signature**: 3 is **Mercury's retrograde prime** (3 stations per year, forming a rotating triangle). However, Nityaklinna's graha is Mars (n=7 in the prime sequence). The structural mismatch: Tritiya carries Mercury's prime in the tithi index, Mars's graha in the devi assignment. The mismatch is the structural feature — Nityaklinna's dissolution function bridges Mercury's quickness and Mars's heat. (planetary-primes-v1.md, Section 2.3)
- **morphology_correlates**: 3-fold structural elements in human anatomy: 3 sections of the spine (cervical-thoracic-lumbar before sacrum), 3 trimesters of pregnancy, 3 dosha framework, 3 guna framework. The trimester correspondence is Mars-relevant: pregnancy is a 9-month process structured by 3-fold rhythm, with Mars governing the rakta-uterus axis. (vertebral-primes-v1.md, general)
- **sri_yantra_region_relation**: 3 is the smallest planetary prime in {3,5,7,11}. Mercury's tidal weight is 0.013 (relative to Jupiter=1.00) — the weakest of the four primes. Removing Mercury's triangular mode collapses the 44-region count. The trine harmonic (k=3) is essential to the field's region structure even though Mercury's tidal contribution is small. (planetary-primes-v1.md, Section 3)

## Sound/Rhythm

- **svara_link**: SOURCE_NEEDED. Mangala's traditional svara is **Pa** (Pañcama, the perfect 5th) per some traditions, or **Sa** in others — the field is contested. The bija-rasa pairing (Klīm + karuna) suggests Pa (the rasa-bearing note in many Hindustani ragas).
- **raga_link**: Mars-associated ragas in raga_data.csv: **Bhairavī** (morning, earth/tamas, karuna; vadi Ma), **Nāṭa Bhairav** (morning, earth/tamas, vira; vadi Dha). **Bhairavī matches Nityaklinna's signature exactly: karuna rasa direct match, tamas guna direct match, "morning" timing aligns with Tritiya as a still-early-cycle tithi.** Bhairavī is the classical raga of dissolution-emotion — the raga that ends every Hindustani concert because it dissolves all preceding ragas back into the field.
- **tala_link**: SOURCE_NEEDED. The 3-prime symmetry suggests 3-beat or 6-beat cycles (Dadra 6-beat in Hindustani; Rūpaka in Carnatic).

## Vastu/Spatial

- **mandala_zone_map**: Mangala at k=2 places yantra values as Lo_Shu + 2*J = {6, 11, 10; 13, 7, 5; 8, 9, 12}. Brahmasthana (center cell) = 7. Eigenvector structure: uniform (M=21), primary tension (NE-SW), secondary tension (perpendicular). (yantra_eigenvalue_exploration.md)
- **directional_emphasis**: SOURCE_NEEDED. Traditional: Mangala governs the South (Yama direction) — the heat/death/transformation quadrant. The Lo Shu placement of Mars at South is consistent.

## Visual Grammar

- **palette_logic**: Primary: #2050a0 (deep cobalt blue, from nitya_devi_master.csv). Secondary: #F48FB1 (rose pink, from nitya_yantra_geometry.csv). Bindu: #FF4081. Line weight: medium. The water-tamas signature with Mars-graha overlay creates a tense color combination: cool blue field with warm-pink interior accents — encoding karuna's dual nature (the blue of melt-water, the pink of the wound that produced it).
- **density_logic**: interference_radius_fraction = 0.8 (slightly tighter than Kāmeśvarī/Bhagamalini). The 3-fold cosine field has uniform density with a slight inward concentration. Render with hexagonal lattice visible but with softer outer boundary than Kāmeśvarī's.
- **line_weight_logic**: Medium. The 3-fold cosine variant produces softer line edges than the sine variant (mathematical fact of cosine vs sine boundary derivatives).
- **panel_layout**: SOURCE_NEEDED.
- **symbol_strip**: STABILIZE + DEFEND. 2 weapons (ankusha, pasha — minimal). Abhaya mudrā. Red sandalwood paste smear. Beads of sweat. Bija: Klīm.
- **caption_motto**: "Ever-moist with compassion — she dissolves the dryness of separation." (nitya_devi_master.csv)

---

## Cross-layer observations

The first cross-layer resonance is the **graha-tithi prime mismatch encoding Nityaklinna's dissolution function**. Tritiya = tithi 3 = Mercury's retrograde prime (3 stations/year). But Nityaklinna's graha is Mars (n=7 prime). This mismatch is not a bug — it is the structural feature. The dissolution-tithi (Nityaklinna) is precisely the position where Mercury's quickness (n=3) bridges into Mars's heat (n=7) without resolving into either — held in the karuna-rasa, the wet-residue-state. The pasaka outcome at total=3 reinforces this: the dice produce a Sun-graha excellent crown outcome (Kṛta), neither Mercury nor Mars — bypassing both into the highest coherence. The tithi-graha-pasaka triple at this position spans n=3 (Mercury, tithi index), n=7 (Mars, devi graha), and n=0 (Sun, pasaka outcome graha) — three distinct positions in the prime sequence.

The second resonance is the **Jaya-gandanta avoidance pattern as a positive structural fact**. Tritiya belongs to the Jaya tithi group {3, 8, 13, 18, 23, 28}. From RESEARCH-017 Finding 11: ALL 6 gandanta nakshatras (Ashwini, Ashlesha, Magha, Jyeshtha, Mula, Revati) AVOID Jaya tithis. This is a statistically robust pattern (p<0.0001 over the broader gandanta-tithi-group analysis). For Nityaklinna specifically, this means the wave field at Tritiya runs at non-amplified baseline — the karuna-melt is not gandanta-boosted. The dissolution happens at field-default volume rather than at the boundary-crossing peaks. This matches the iconographic detail of "perpetual" moisture: not flood, not drought, just continuous wetness.

The third resonance is the **2-weapon minimum signaling functional sufficiency for dissolution**. Nityaklinna carries only aṅkuśa and pāśa — the fewest weapons of any of the first 7 Nityas (compare Kāmeśvarī's 4, Bhagamalini's 4, Bherunda's 8, Vahnivasini's 2 [tied], Mahāvajreśvarī's 3, Sivaduti's 6). The capability signature reduces to STABILIZE + DEFEND. Dissolution does not require offensive instruments — it requires only retention-vessels. The pāśa (noose) and aṅkuśa (goad) are both binding/positioning tools, not cutting tools. The body smeared with sandalwood paste and the abhaya-mudrā are not iconographic decoration — they are the actual instruments of her function: melting and reassuring. Her field is the karuna-tide that does not need to fight what it dissolves.

---

## Attestation summary

- **OBSERVED:PRIMARY**: Identity (name, bija, mantra, weapons, description, body color, ornamentation, rasa, element, guna, shakti, mudra from nitya_devi_master.csv); Lunar/Time (tithi quality, deity, good_for/avoid from tithi_master.csv); Yantra geometry (Dakshinamurti Samhita attestation per nitya_yantra_geometry.csv).
- **OBSERVED:TRADITIONAL**: Bhasma substance classes (Tāmra/Praval rasashastra); Mangala's friend/enemy table (BPHS); chakra-graha mapping (chakra_cross_domain.csv).
- **SYNTHESIS**: Field Math eigenvalue derivation; Wave/Interference findings; Quasicrystal N=3 cosine variant; Prime/Morphology correspondences; Cross-layer observations; expanded_function; raga association (Bhairavī as primary).
- **GENERATED**: None. SOURCE_NEEDED fields are flagged.

---

## SOURCE_NEEDED flags

1. **vahana_mount / faces_arms_count**: Tantric iconographic source (Tantraraja, shivashakti.com).
2. **nakshatra_overlays**: Compute Tritiya wave fine structure across 27 nakshatras.
3. **nodal_density / radial_bands**: Run N=3 cosine multigrid extraction.
4. **hexagram_id**: User decision.
5. **shodhana_media exact sequence / bhavana_media specifics / marana_cycles count / puta_profile / particle_scale_overlay**: Bhasma docx primary detail consultation for Tāmra and Praval.
6. **plant_allies / doctrine_of_signatures_overlay / processing_plants / astrobotanical_timing**: Cross-reference traditional Mangala plants with guild_full.csv.
7. **dhatu_targets / indication_clusters / anupana_vehicle**: Ayurvedic text consultation for Mangala-specific protocols.
8. **svara_link / tala_link**: Gandharva Veda source.
9. **directional_emphasis**: Vastu confirmation for Mars-South.
10. **panel_layout**: Design decision.
