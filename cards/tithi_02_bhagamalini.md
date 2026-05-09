# Bhagamalini · Tithi 2 · Card

**Source compilation**: 2026-05-01
**Schema version**: Atlas Tithi Card Master Table (user-provided, 2026)
**Population status**: ~60/82 fields sourced, ~22 SOURCE_NEEDED flags

---

## Identity

- **tithi_number**: 2
- **tithi_name**: Dvitīyā
- **paksha_mode**: Both shukla and krishna. Brahma is tithi deity in both pakshas. Quality: mixed. (tithi_master.csv)
- **devi_name**: Bhagamalini
- **devi_alt_names**: Bhagamālinī (भगमालिनी). "Garlanded with Bhaga (auspiciousness/six-fold blessing)." Bija: Hrīm. Mantra: Om Hrīm Bhagamālinyai.
- **seed_keywords**: auspiciousness, garland, hexagram, water-sattva, shanta, BIND/STABILIZE, bhaga (six blessings), Star-of-David yantra

## Canonical Devi

- **iconography_summary**: Garlanded with auspiciousness — she who bestows the six blessings of the Bhaga (sovereignty, dharma, fame, fortune, knowledge, dispassion). Beautiful and red (complexion), green garments. Carries the kāma archetype's full weapon set: aṅkuśa, pāśa, sugarcane bow, 5 flowery arrows. (nitya_devi_master.csv, OBSERVED:PRIMARY, attested_classical)
- **weapons_items**: Aṅkuśa (goad), pāśa (noose), sugarcane bow (ikṣu-danda), 5 flowery arrows. Capability signature: BIND, STABILIZE. (nitya_devi_master.csv, OBSERVED:PRIMARY)
- **mudras_gestures**: SOURCE_NEEDED: Mudra field empty in nitya_devi_master.csv for Bhagamālinī. Tantric source consultation needed (Dakshinamurti Samhita).
- **vahana_mount**: SOURCE_NEEDED.
- **body_color**: Beautiful and red (complexion). Color hex: #4878c8 (cool steel-blue/indigo — represents her field/aura, contrasting with the textual red complexion). (nitya_devi_master.csv)
- **ornamentation**: SOURCE_NEEDED: Ornaments field empty in nitya_devi_master.csv. The "garland of bhaga" is the defining ornament-by-name but specific bodily ornaments unattested.
- **faces_arms_count**: SOURCE_NEEDED: 4-armed by default Tripurasundarī iconography (4 weapons listed), but specific count unattested.
- **shakti_statement**: Auspiciousness — the bestower of bhaga. Bhaga in Sanskrit denotes both "fortune" and the female generative organ — Bhagamalini's shakti is doubly fertile. (nitya_devi_master.csv, OBSERVED:PRIMARY)
- **expanded_function**: Bhagamalini is the second Nitya — the moment of pairing, of relationship, of the dual emerging from the singular. Where Kāmeśvarī (1) is the seed-impulse, Bhagamalini (2) is the first relation: the desire that has now found an object. Her yantra is the unique hexagram-bearing (Star of David) configuration in the early Nitya sequence — the only Nitya whose primary form combines downward triangle and hexagon, encoding Shiva-Shakti union explicitly. The 6-fold N-symmetry of her wave field places her on the periodic hexagonal lattice — sister-symmetry to Mahāvajreśvarī (Nitya 6). (SYNTHESIS from nitya_devi_master.csv + nitya_yantra_geometry.csv + CONSTRUCTION_CHOICES.md)
- **bhava_mood**: Shanta (peace). Rasa: shanta. Element: water. Guna: sattva. The water-sattva pairing is the signature of clear, settled, fertile receptivity. (nitya_devi_master.csv, OBSERVED:PRIMARY)
- **mantra_bija**: Hrīm (the Bhuvaneshvari-bija, the māyā-bija, the heart of all goddess worship). Full mantra: Om Hrīm Bhagamālinyai. (nitya_devi_master.csv, OBSERVED:PRIMARY)

## Lunar/Time

- **lunar_phase_arc**: 12°-24° from conjunction (shukla dvitiya), or 192°-204° (krishna dvitiya). The 2nd tithi spans 12° of Sun-Moon elongation.
- **phase_quality**: Mixed (tithi_master.csv). Good for: buying property or vehicles, agriculture, community work. Avoid: marriage, sacred ceremonies. Tithi deity: Brahma.
- **nitya_cycle_position**: 2nd of 15 — the pairing position. Dvitiya is the first tithi where Sun and Moon are clearly distinguished as separate luminaries (after Pratipadā's near-conjunction). Bhagamalini governs the moment when the unity of Amāvāsyā/Pūrṇimā splits into duality.
- **weekday_links**: Dvitiya's tithi deity is Brahma (the creator). Bhagamalini's graha correspondence is Chandra (Moon) per devi_master — Monday (Somavara). The yantra_geometry CSV agrees here (Moon for tithi 2). No discrepancy. k=1, M=18.
- **nakshatra_overlays**: SOURCE_NEEDED: No fixed mapping on disk. Dvitiya belongs to the Bhadra group (T2, T7, T12, T17, T22, T27 — "auspicious tithis") per the v3 paper's classification. Bhadra group differentiation in wave fine structure peaks at k=6 (sextile) and k=12 (rashi) — the same harmonics as Bhagamalini's yantra symmetry (N=6). The hexagonal symmetry is built into the tithi-group structure.

## Yantra

- **yantra_family**: **Triangle-down + hexagon (hexagram, Star of David)** + 16-petal lotus + 8-petal lotus + bhupura. Triangle scale 0.88, hexagon scale 0.6, inner circle 0.92. The hexagram is unique in the early Nitya sequence — only Bhagamalini has explicit hexagonal interlock at this position. (nitya_yantra_geometry.csv, OBSERVED:TRADITIONAL — Dakshinamurti Samhita attestation: "The DS describes the yantra as a triangle, hexagon, 16 petals, eight petals, then bhūpura.")
- **yantra_geometry_notes**: This is one of only TWO Nityas with attested classical hexagonal geometry (Bhagamalini and Mahāvajreśvarī, both N=6 in the multigrid projection). The Star of David / Shatkona is the visual signature of Shiva-Shakti union — the union of upward triangle (Shiva, fire ascending) and downward triangle (Shakti, water descending). The element designation (water) is the descending Shakti aspect.
- **yantra_symmetry_order**: N=6 (hexagonal, periodic). 6-fold symmetry produces a triangular-hexagonal periodic lattice — the same lattice as the honeycomb. Both Bhagamalini and Mahāvajreśvarī occupy this symmetry; their wave fields are isomorphic up to phase rotation. (devi_engine.py DEVI_N)
- **yantra_center_logic**: Bindu as **triangle** (not point — distinct from most other Nityas). The triangular bindu inside the hexagram is the kāma-bīja seed-form within the union-geometry. Inner circle scale 0.92.
- **yantra_outer_boundary**: Bhupura with 4 gates. Interference radius fraction: 0.85 (second-highest of 15 Nityas, after Kāmeśvarī's 0.9). Wave function: sine, frequency multiplier: 1, angular position: 24°.
- **yantra_layer_count**: 5 layers: triangle bindu → hexagon (shatkona) → 16-petal lotus → 8-petal lotus → bhupura. The most layers of any Nitya in positions 1-7. (nitya_yantra_geometry.csv)

## Field Math

- **graha_k**: Chandra = k=1, magic constant M=18. (yantra_eigenvalue_exploration.md, Finding 2). Both nitya_devi_master.csv and nitya_yantra_geometry.csv agree on Chandra/Moon. No discrepancy.
- **magic_constant_M**: 18 (Chandra, k=1). Eigenvalues: {18, +4.899, -4.899}. The Lo Shu shifts only by 1*J = adding 1 to every cell. (Finding 1)
- **invariant_secondary_modes**: +/-2sqrt(6) = +/-4.8990. Universal across all grahas. (Finding 1)
- **coherence_ratio**: lambda_2/M = 4.899/18 = 0.2722 (Chandra). The 2nd most polarized graha (only Sun is more polarized at 0.3266). The Moon's field has nearly the maximum spatial differentiation possible — high contrast between zones. (Finding 2)
- **eigenvector_axes**: For Chandra (k=1): Brahmasthana eigenvector = uniform [1/√3, 1/√3, 1/√3]. Primary tension axis (lambda=+4.899): South row vs center. Secondary tension (lambda=-4.899): North row vs center, perpendicular. (Finding 6)
- **brahmasthana_definition**: Uniform eigenvector persists at every Kronecker level — the geometric principle of maximum coherence. (Finding 4)
- **kronecker_level**: Level 1: 3x3, M=18. Level 2: 9x9, M=324. Level 3: 27x27, M=5832. Scaling law: M_n = M_1^n. (Finding 3)
- **navagraha_composite_role**: Chandra occupies the k=1 position in the Navagraha 9x9 composite. Moon's Lo Shu placement is in the Northwest (Vayu) — the wind quadrant. (Finding 5)

## Wave/Interference

- **boundary_harmonic_mode**: At k=2: the opposition harmonic. Dvitiya is structurally near opposition only in krishna paksha (where Sun and Moon are 180° apart at full moon, then separating). In shukla, Dvitiya is near conjunction. The same tithi's two paksha occurrences sit at opposite ends of the wave-amplitude envelope. (two-source-interference-v3.md, Finding 8)
- **two_source_pattern**: A(theta) = 2 * cos(k(theta - midpoint)) * cos(k * separation/2). At k=6 (Bhagamalini's symmetry harmonic), constructive maxima appear at separation = 360/6 = 60° — the sextile, traditionally the most auspicious minor aspect. The k=6 harmonic is one of the two strongest tithi-group differentiators (1.006). (Finding 8, 10)
- **nodal_interior_pattern**: For N=6 multigrid in disk interior: periodic hexagonal-triangular lattice (the same as graphene). Fully ordered, fully reducible. The 6-fold field is the densest 2D packing achievable. (CONSTRUCTION_CHOICES.md)
- **ring_vs_disk_distinction**: On the boundary: 6-source pattern produces standing waves at k=6 (sextile resonance). In the disk: 6-fold multigrid produces hexagonal nodal structure. (Finding 7)
- **gandanta_gain**: Dvitiya is a Bhadra tithi — the auspicious group. Bhadra-group differentiation peaks at k=6 (sextile) — exact match for Bhagamalini's N=6 yantra symmetry. The system is self-resonant at this position. (Finding 10)
- **wave_panchaka_relation**: Panchaka (mod-9) and wave (trig) systems are orthogonal: r = -0.011. (Finding 12)
- **quantized_prime_modes**: The planetary primes {3, 5, 7, 11} produce the 44-region quantized field. Bhagamalini's graha (Chandra) is NOT a planetary prime contributor — the Moon does not retrograde. The Moon enters the quantized field only as Sun-Moon modulation (the rank-1 envelope of Finding 10). (planetary-primes-v1.md, Section 3)

## Quasicrystal/Chladni

- **quasicrystal_line_style**: 6-fold multigrid. Six plane waves at 0°, 60°, 120°, 180°, 240°, 300° — sine interference. Same lattice family as graphite/graphene. Periodic, crystallographic, fully reducible. (CONSTRUCTION_CHOICES.md)
- **nodal_density**: SOURCE_NEEDED: No computed nodal density metric for N=6. Interference_radius_fraction = 0.85 (2nd highest), suggesting near-uniform density throughout the disk like Kāmeśvarī's 3-fold field but with finer hexagonal subdivision.
- **radial_bands**: SOURCE_NEEDED: Wave function = sine with frequency_multiplier=1 → 1 radial node within unit disk.
- **interference_centers**: Primary interference center = bindu (6 waves at 60° intervals constructively superpose at origin). Secondary maxima at 6 vertices of inscribed regular hexagon at interference_radius_fraction = 0.85. The 3D mediator polyhedron: cuboctahedron (14 faces: 8 triangles + 6 squares — the Vajra/Indra polyhedron, also called Archimedean Solid #1). (CONSTRUCTION_CHOICES.md)

## Pasaka/Magic Cube

- **cube_type**: Andrews 1917 (verified). 3x3x3 magic cube, values 1-27. (magic_cube_analysis.json)
- **cube_magic_constant**: M = 42. (Finding 1)
- **cube_layer_squares**: Layer eigenvalues: layer_0 {42, -9, -9}, layer_1 {42, 0, 0}, layer_2 {42, +9, +9}. (Finding 1)
- **cube_invariant**: +/-9 = +/-3^2. The 3D rational invariant. (Finding 2)
- **cube_center_value**: 14 = (1+27)/2. The 3D Brahmasthana. (Finding 3)
- **cube_associative_sum**: Antipodal pairs sum to 28 = n^3+1. (Finding 4)
- **cube_tensor_isotropy**: sigma_1 = 72.75 across all three modes. Cube is spectrally isotropic. (Finding 6)
- **cube_kronecker_scaling**: M_n = 42^n. Secondary = 9 * 42^(n-1). (magic_cube_extension.json, Finding 1)
- **cyclic_composite_eigenvalues**: 9x9 block-circulant: M = 126. Eigenvalues {126, +/-2.598, 0×4}. Rank 5, null 4. (Finding 2, 6)
- **loshu_weighted_cube_mode**: Lo Shu weighting collapses eigenvalues to {126, 0, 0, ...} — maximally coherent. (Finding 3)

### Pasaka at total=2

SOURCE_NEEDED: pasaka totals are 3-12, no total=2 outcome exists in the deck. The system mismatch is identical to Pratipadā's. Possible alternate mappings: mod-9 → 2 (no direct outcome at total=2); use the Tretā outcome (ID 2, dice 1,1,2, total=4, very_good, forehead, Moon, madhura) which IS Bhagamalini-graha-aligned (Moon) and "very_good" quality matches the Bhadra/auspicious tithi-group classification. The deck-position mapping may be the more useful for tithis below 3.

## I Ching

- **hexagram_id**: SOURCE_NEEDED: No fixed mapping on disk. Numerical correspondent: hexagram 2 (Kūn, "The Receptive") — 6 yin lines, the perfect counterpart to Pratipadā's hexagram 1 (Qián, all yang). Kūn's earth-receptivity matches Bhagamalini's water-sattva-shanta signature precisely. The 1↔2 pairing of Pratipadā↔Dvitiya mirrors the Qián↔Kūn polarity that opens both the I Ching and the Lalita sequence.
- **hexagram_arrangement**: Fuxi (rank 2) ↔ King Wen (rank 8). Spectral opposites. (iching_spectral_analysis.json)
- **rank_complexity**: Q6 hypercube eigenvalues {6,4,2,0,-2,-4,-6} with multiplicities Pascal row 6 = {1,6,15,20,15,6,1}. (Finding 3)
- **yin_yang_balance_mode**: XOR-with-63 has eigenvalues {+1,-1} each with multiplicity 32 — perfect yin-yang partition. (Finding 6)
- **hypercube_distance_signature**: Hamming distance matrix rank 7; eigenvalues {192, 0×57, -32×6}. (Finding 5)
- **pascal_row_signature**: Row 6 = {1,6,15,20,15,6,1}, total 64 = 2^6. (Finding 3)

## Lo Shu x I Ching Bridge

- **trigram_loshu_weight_map**: Li=9, Kan=1, Zhen=3, Dui=7, Xun=4, Gen=8, Kun=2, Qian=6. Dvitiya (2) maps to **Kun=2** — the Earth trigram, the Receptive, the Mother. This pairing is structurally exact: Dvitiya's tithi deity is Brahma (the creator-receptive); the Kun trigram IS receptivity in the I Ching. (loshu_iching_interaction.json)
- **weighted_spectral_breaking**: Unweighted Q6 has 7 unique eigenvalues; Lo Shu weighting breaks degeneracy to 27 unique eigenvalues — the nakshatra count. (test4_weighted_Q6)
- **spectral_gap_change**: Unweighted gap = 2.0; weighted = 0.4624. Fiedler value drops to 0.1944. (test5_spectral_gap)

## Alchemical/Bhasma

- **material_classical_class**: Chandra's metal is silver (Rajata, Ag). Gem: pearl (Mukta). In rasashastra: Rajata is Uparasa (secondary substance class) when applied to medicinal preparations; Mukta is Ratna (gem class). (SYNTHESIS — Bhasma docx not directly read; using classical jyotish convention)
- **material_scientific_type**: Silver (Ag) — element 47, atomic mass 107.87, highest electrical and thermal conductivity of any metal. Forms Ag2O on incineration. Pearl is calcium carbonate (CaCO3) in aragonite form with conchiolin protein matrix.
- **base_material**: Rajata (silver) for the metallic preparation; Mukta (pearl) for the gem preparation. Both are classical Chandra substances.
- **prepared_substance_type**: Rajata Bhasma (silver bhasma); Mukta Pinga (pearl powder).
- **shodhana_media**: SOURCE_NEEDED: Specific shodhana for Rajata not detailed on disk. Classical: silver heated and quenched in cow's urine, takranī (buttermilk), or kānjī (sour gruel) cycles.
- **bhavana_media**: SOURCE_NEEDED: Triphala kvath, kumari swarasa (aloe juice) typically.
- **marana_cycles**: SOURCE_NEEDED: Rajata typically requires 7-21 puta cycles per classical texts.
- **puta_profile**: SOURCE_NEEDED.
- **quality_tests**: nischandratva, rekhapurnatva, varitaratva (classical bhasma tests). (Bhasma docx framework)
- **completion_stop_rule**: All quality tests pass simultaneously.
- **phase_transformation**: Ag (metallic silver) → Ag2O (silver oxide, brown-black) → fully oxidized particulate Bhasma. The phase change is reversible at high temp without sulphur — Rajata Bhasma is one of the more chemically labile bhasmas. (SYNTHESIS)
- **particle_scale_overlay**: SOURCE_NEEDED.
- **safety_conditions**: Properly prepared Rajata Bhasma is generally safe in classical doses. Argyria (silver-grey skin discoloration) from chronic high-dose silver exposure is the principal concern.

## Graha/Material

- **graha_material_map**: Chandra (Moon) → Rajata (silver), Mukta (pearl). In BPHS: Moon's friends are Sun and Mercury (asymmetric — Mercury considers Moon an enemy); enemies: none (Moon is neutral or friendly to all); neutral: Mars, Jupiter, Venus, Saturn. Moon is the most universally friendly graha. (Graha Material docx)
- **friend_enemy_interaction**: Moon-Mercury asymmetry (Ag-Hg): silver dissolves readily into liquid mercury (amalgam, electrum-mercury). Moon "enters" Mercury's domain; Mercury does not reciprocate. This is the same asymmetry observed in the BPHS friendship table — Moon considers Mercury a friend; Mercury considers Moon an enemy. The metallurgical fact and the friendship-table asymmetry are isomorphic. (See Sivaduti card cross-layer notes for the symmetric description from Mercury's side.) Moon-Sun (Ag-Au): silver and gold form alloys (electrum); the friend relationship materializes as solid-solution miscibility.
- **ritual_vs_medical_flag**: Both. Pearl and silver have extensive ritual use (silver-plate offerings, pearl rosaries). Rajata Bhasma and Mukta Pishti are medical (rasaushadhi).

## Plant/Ecology

- **plant_allies**: SOURCE_NEEDED: No graha-plant cross-reference on disk. Traditional Chandra plants: Brāhmī (Bacopa monnieri — the chief mind-tonic), Śatāvarī (Asparagus racemosus — the women's soma plant), Yashtimadhu (licorice — sweet-soothing). All three are Madhura rasa, cooling, and reproductive/nervine tonic — directly aligned with Chandra-Bhagamalini's water-sattva-shanta signature.
- **processing_plants**: SOURCE_NEEDED: Specific bhavana plants for Rajata. General: triphala, aloe.
- **doctrine_of_signatures_overlay**: SOURCE_NEEDED. Chandra plants are pale, juicy, mucilaginous, milky (sap). Soma is the original Chandra plant — debate continues about its botanical identity (Sarcostemma, Ephedra, Amanita).
- **astrobotanical_timing**: SOURCE_NEEDED. General: Dvitiya in shukla paksha is excellent for transplanting young plants (the "first growth" tithi); Monday (Somavara) under Chandra-ruled nakshatras (Rohini, Hasta, Shravana) is the maximally Chandra-aligned planting window.

## Body/Therapeutics

- **dosha_predicates**: Tithi 2 element: water (tithi_master.csv), guna: rajas. Devi element: water (nitya_devi_master.csv), guna: sattva. Chakra: Sahasrara (Chandra/Moon correspondence) — beyond elements, sattva (transcendent), Vata, Nirvana Shakti / Kundalini. (chakra_cross_domain.csv). The water/water/transcendent triad with rajas-sattva interplay is the Kapha-Vata profile — moisture and lightness, the lymph-and-mind axis.
- **dhatu_targets**: SOURCE_NEEDED. Traditional: Chandra governs Rasa dhatu (plasma/lymph) — the first dhatu, the medium of all subsequent transformation. Pearl bhasma is classically prescribed for Rasa-dhatu disorders (anaemia, lymphatic stagnation).
- **organ_targets**: Sahasrara at crown: pituitary, hypothalamus, central nervous system. Body system: spirituality, enlightenment, unity. (chakra_cross_domain.csv). Associated nakshatras: Rohini, Hasta, Shravana — the three Chandra-ruled nakshatras. Direct chakra-nakshatra-graha alignment.
- **indication_clusters**: SOURCE_NEEDED. Traditional Chandra disorders: lunacy, mania-depression, menstrual irregularities, milk insufficiency, lymphatic stagnation, sleep disorders.
- **anupana_vehicle**: SOURCE_NEEDED. Traditional Chandra anupana: cow's milk, ghṛta, honey, sugar.
- **preparation_dependency_warning**: Pearl and silver bhasmas are among the safer bhasmas in classical use. Quality verification still essential.

## Prime/Morphology

- **prime_signature**: 2 is not a planetary prime (the prime sequence {3,5,7,11} excludes 2 because no planet has 2 retrograde stations in any natural cycle). However, 2 is THE prime — the first prime, the only even prime, the basis of the binary system that produces the I Ching's 64 hexagrams via 2^6. Bhagamalini's tithi number IS the dimensionality of the I Ching root. (planetary-primes-v1.md, Section 2; iching_spectral_analysis.json)
- **morphology_correlates**: 2 corresponds to bilateral symmetry — the chordate body plan, paired organs (eyes, ears, lungs, kidneys, gonads, hands, feet). The vertebral column has bilateral symmetry but no segments labelled with prime "2." Bilateral symmetry is the substrate on which all primes are expressed in the body. (vertebral-primes-v1.md, general framework)
- **sri_yantra_region_relation**: 2 does not appear in the n∈{3,5,7,11} prime overlay producing the 44-region count. However, 2 is the foundational symmetry of the up/down triangle pair — without bilateral mirror, no Sri Yantra exists. Bhagamalini's hexagram (shatkona) is the explicit pairing of two oppositely-oriented triangles. (planetary-primes-v1.md, Section 3; SYNTHESIS)

## Sound/Rhythm

- **svara_link**: SOURCE_NEEDED. Chandra's traditional svara association in Gandharva Veda is **Sa** (Ṣaḍja, the tonic) — Chandra IS the field, the tonic from which all other notes are measured. Bhagamalini at Sa = the field-itself-named.
- **raga_link**: Chandra-associated ragas in raga_data.csv: **Bhūp** (evening, ether/sattva, shanta; vadi Ga), **Bihāg** (night, air/sattva, shringara; vadi Ga), **Deśa** (night, water/sattva, adbhuta; vadi Ri). Of these, **Bhūp** matches Bhagamalini's water-sattva-shanta signature most closely (though Bhūp's element is ether, the rasa shanta and guna sattva align). **Deśa** is also strong: water + sattva direct match. Moon-graha ragas additionally: **Bāgeshrī** (night, water/sattva, shringara; vadi Ma) — the most aligned by element-guna pair.
- **tala_link**: SOURCE_NEEDED. The bilateral-2 prime and 6-fold yantra symmetry suggest 2-beat or 6-beat cycles (Dadra in Hindustani, Rūpaka 6-beat in Carnatic).

## Vastu/Spatial

- **mandala_zone_map**: Chandra at k=1 places the yantra values as Lo_Shu + 1*J = {5, 10, 9; 12, 6, 4; 7, 8, 11}. The Brahmasthana center cell = 6. Eigenvector structure: uniform (M=18), primary tension axis (NE-SW), secondary tension (perpendicular). (yantra_eigenvalue_exploration.md)
- **directional_emphasis**: SOURCE_NEEDED. Traditional: Chandra governs Northwest (Vayu corner) in Vastu. The Lo Shu placement of Moon at NW (Vayu) is consistent across multiple Vastu traditions. (SYNTHESIS)

## Visual Grammar

- **palette_logic**: Primary: #4878c8 (cool steel-blue, from nitya_devi_master.csv). Secondary: #FF8A80 (coral pink, from nitya_yantra_geometry.csv). Bindu: #F06292 (rose). Line weight: medium. The water-sattva signature suggests cool flowing colors with a pink bindu accent.
- **density_logic**: interference_radius_fraction = 0.85. The 6-fold periodic field has uniform density. Render with hexagonal symmetry visible — the shatkona must be the dominant visual feature.
- **line_weight_logic**: Medium. The 6-fold lattice's regularity is the visual point.
- **panel_layout**: SOURCE_NEEDED.
- **symbol_strip**: BIND + STABILIZE. 4 weapons (ankusha, pasha, sugarcane bow, 5 flowery arrows). Hexagram (Star of David). 16-petal lotus + 8-petal lotus (24 petals total — same as 24 presacral vertebrae per planetary-primes-v1 Finding 4). Bija: Hrīm.
- **caption_motto**: "Garlanded with auspiciousness — she who bestows the six blessings of the Bhaga." (nitya_devi_master.csv)

---

## Cross-layer observations

The first cross-layer resonance is the **6-fold structural alignment between yantra symmetry, Bhadra-tithi-group differentiation, and the I Ching trigram weight**. Bhagamalini's yantra is hexagonal (N=6); Dvitiya belongs to the Bhadra tithi group whose wave-fine-structure differentiation peaks at k=6 (sextile, value 1.006); the trigram at the Lo Shu position 2 is Kun (Earth) which contains pure Earth duplicated three times (a "doubled-2" structure). The hexagonal layer count (16+8 petals = 24 petals) matches the 24 presacral vertebrae count from planetary-primes-v1 Finding 4 — the "Sri Yantra crossings" number. Bhagamalini's geometry is calibrated to this cross-system constant.

The second resonance is the **shatkona (Star of David) as the unique Shiva-Shakti union signal in the early Nityas**. Among the first 7 Nityas, only Bhagamalini's yantra geometry explicitly describes a hexagon — encoded in Dakshinamurti Samhita as "triangle, hexagon, 16 petals, 8 petals, bhupura." The downward triangle (water-Shakti-descending) interlocks with the upward-implied second triangle that completes the hexagram. This makes Bhagamalini the structural locus of pairing-itself in the Nitya sequence — the Devi who governs the moment when two distinct things first relate. Her tithi number (2) is the dimensionality of pairing; her bija (Hrīm) is the universal feminine seed; her tithi deity (Brahma) is the universal creator-pair (Brahmā-Saraswatī).

The third resonance is the **Bhagamalini-Mahāvajreśvarī sister symmetry**. Both Nitya 2 (Bhagamalini, Moon, sattva, water, shanta) and Nitya 6 (Mahāvajreśvarī, Saturn per devi_master, rajas, air, adbhuta) share N=6 yantra symmetry. They are the only two Nityas in the first 7 with hexagonal multigrid projection. Their wave fields are isomorphic up to the angular_position_degrees offset (Bhagamalini at 24°, Mahāvajreśvarī at 120°). The 96° angular gap = 360°/3.75 — close to but not exactly a quarter-rotation. This pair encodes the same 6-fold geometric structure but at different phase positions in the lunar cycle: Bhagamalini at the dyadic-pairing moment, Mahāvajreśvarī at the established-coupling moment. Same shape, different arc-position — sextile siblings.

---

## Attestation summary

- **OBSERVED:PRIMARY**: Identity (name, bija, mantra, weapons, description, body color, rasa, element, guna, shakti from nitya_devi_master.csv); Lunar/Time (tithi quality, deity, good_for/avoid from tithi_master.csv); Yantra full geometry (hexagram structure attested in Dakshinamurti Samhita per nitya_yantra_geometry.csv).
- **OBSERVED:TRADITIONAL**: Bhasma substance classes (Rajata/Mukta rasashastra); Chandra's friend/enemy table (BPHS); chakra-graha mapping (chakra_cross_domain.csv).
- **SYNTHESIS**: Field Math eigenvalue derivation; Wave/Interference findings; Quasicrystal N=6 construction; Prime/Morphology correspondences; Cross-layer observations; expanded_function; phase_transformation; raga associations.
- **GENERATED**: None. SOURCE_NEEDED fields are flagged.

---

## SOURCE_NEEDED flags

1. **mudras_gestures / vahana_mount / ornamentation / faces_arms_count**: Tantric iconographic source consultation (Dakshinamurti Samhita, Tantraraja, shivashakti.com primary attestation cited in geometry CSV).
2. **nakshatra_overlays**: Compute Dvitiya wave fine structure across 27 nakshatras.
3. **nodal_density / radial_bands**: Run N=6 multigrid extraction.
4. **hexagram_id**: User decision: tithi 2 → hexagram 2 (Kun) static mapping vs field-derived.
5. **Pasaka at total=2**: System mismatch (deck range 3-12). Decide alternate mapping.
6. **shodhana_media / bhavana_media / marana_cycles / puta_profile / particle_scale_overlay**: Bhasma docx + classical rasashastra texts for Rajata/Mukta specifics.
7. **plant_allies / doctrine_of_signatures_overlay / processing_plants / astrobotanical_timing**: Cross-reference traditional Chandra plants with guild_full.csv.
8. **dhatu_targets / indication_clusters / anupana_vehicle**: Ayurvedic text consultation for Chandra-specific protocols.
9. **svara_link / tala_link**: Gandharva Veda source.
10. **directional_emphasis**: Vastu confirmation for Chandra-Vayu.
11. **panel_layout**: Design decision.
