# Mahavajreshvari · Tithi 6 · Card

**Source compilation**: 2026-05-01
**Schema version**: Atlas Tithi Card Master Table (user-provided, 2026)
**Population status**: ~60/82 fields sourced, ~22 SOURCE_NEEDED flags

---

## Identity

- **tithi_number**: 6
- **tithi_name**: Ṣaṣṭhī
- **paksha_mode**: Both shukla and krishna. Kartikeya (Skanda) is tithi deity. Quality: auspicious. (tithi_master.csv)
- **devi_name**: Mahavajreshvari
- **devi_alt_names**: Mahāvajreśvarī (महावाज्रेश्वरी). "Great Mistress of the Vajra (Thunderbolt)." Bija: Aim Hrīm. Mantra: Om Aim Hrīm Mahāvajreśvaryai.
- **seed_keywords**: thunderbolt, vajra, instant cutting, air-rajas, adbhuta (wonder), CUT/BIND/DEFEND, Saturn-graha, four+eight petal yantra

## Canonical Devi

- **iconography_summary**: Mistress of the great thunderbolt — her power cuts through delusion instantly. Red complexion, red garments, garland of red flowers. Carries aṅkuśa, sugarcane bow, pāśa. (nitya_devi_master.csv, OBSERVED:PRIMARY, attested_classical)
- **weapons_items**: Aṅkuśa (goad), sugarcane bow, pāśa (noose). 3 weapons — slightly fewer than the kāma-archetype's standard 4. The "missing" implement (the flowery arrows) is replaced FUNCTIONALLY by the vajra named in her title — vajra is not in the weapons_full list because vajra IS her, not a tool she carries. Capability signature: CUT, BIND, DEFEND. (nitya_devi_master.csv, OBSERVED:PRIMARY)
- **mudras_gestures**: SOURCE_NEEDED.
- **vahana_mount**: SOURCE_NEEDED. Her tithi-deity Kartikeya rides a peacock — possible iconographic borrowing.
- **body_color**: Red complexion. Color hex: #7b68ee (medium slate blue — represents her field, contrasting the textual red body). The slate-blue field encodes the color of distant lightning and the air-rajas signature. (nitya_devi_master.csv)
- **ornamentation**: Garland of red flowers. Minimal additional ornamentation specified — the GARLAND of red flowers is the singular distinctive ornament (echoing Bhagamalini's "garland of bhaga" — different garlands at different positions). (nitya_devi_master.csv, OBSERVED:PRIMARY)
- **faces_arms_count**: SOURCE_NEEDED. 3 weapons + presumed mudrās imply 4-armed standard form.
- **shakti_statement**: Thunderbolt power — the instant-cutting shakti. The vajra is the instrument that destroys without fragmentation — it converts solid into vapor, not solid into pieces. (nitya_devi_master.csv, OBSERVED:PRIMARY)
- **expanded_function**: Mahāvajreśvarī is the sixth Nitya — the vajra-strike position, the moment of instant clarity. Where Vahnivāsinī (5) is sustained-fire-sublimation, Mahāvajreśvarī (6) is single-strike vapor-conversion. The vajra (thunderbolt) is the iconographic complement to the agni-yajña — both transmute, but at radically different speeds. Her N=6 yantra symmetry (devi_engine.py DEVI_N) places her on the **same hexagonal lattice as Bhagamalini (Nitya 2)** — the second instance of N=6 in the Nitya sequence, but rotated to angular_position 120°. Her graha is Shani (Saturn, k=6) — the slow-and-heavy graha, which seems opposed to vajra's instant-cut, but resolves through the Saturn function of "solidifying what was insubstantial" — vajra is the lightning that solidifies into karma. (SYNTHESIS from nitya_devi_master.csv + nitya_yantra_geometry.csv + CONSTRUCTION_CHOICES.md)
- **bhava_mood**: Adbhuta (wonder). Rasa: adbhuta. Element: air. Guna: rajas. The air-rajas pairing is the signature of moving wind, mobile mental energy — the carrier-wave for the vajra. (nitya_devi_master.csv, OBSERVED:PRIMARY)
- **mantra_bija**: Aim Hrīm — **two bijas chained**, unique among the early Nityas (Sivaduti also has chained bijas later). Aim (Sarasvatī, the wisdom-bija) + Hrīm (the māyā-bija) → wisdom-piercing-illusion, the vajra-action mantrically encoded. (nitya_devi_master.csv, OBSERVED:PRIMARY)

## Lunar/Time

- **lunar_phase_arc**: 60°-72° from conjunction (shukla shashthi), or 240°-252° (krishna shashthi). The 6th tithi spans 12° of Sun-Moon elongation.
- **phase_quality**: **Auspicious** (tithi_master.csv). Good for: starting projects, travel, celebration, wealth (same set as Pratipadā). Avoid: violence, arguments, negativity. Tithi deity: Kartikeya (Skanda, the warrior-god, son of Shiva and Parvati).
- **nitya_cycle_position**: 6th of 15 — the vajra-strike position. Shashthi is the auspicious tithi associated with Kartikeya — particularly Skanda Sashti (krishna shashthi after Diwali) is a major southern Indian observance.
- **weekday_links**: Shashthi's tithi deity is Kartikeya. Mahāvajreśvarī's graha correspondence is Shani (Saturn) per devi_master — Saturday (Shanivara). The yantra_geometry CSV assigns **Venus** to tithi 6 — **discrepancy**. devi_master Saturn is treated as authoritative. k=6, M=33.
- **nakshatra_overlays**: SOURCE_NEEDED: Shashthi belongs to the **Nanda group** (T1, T6, T11, T16, T21, T26 — "bliss tithis"). From RESEARCH-017 Finding 11: fire-starting gandanta nakshatras (Ashwini, Magha, Mula) PREFER Nanda tithis (mean differentiation 1.72 vs 1.08, p<0.0001). When Shashthi coincides with Ashwini/Magha/Mula, the Mahāvajreśvarī field is amplified — vajra's heat at the fire-water boundary.

## Yantra

- **yantra_family**: Downward triangle (trikona) + **four petals** + eight petals + bhupura. Triangle scale 0.8, inner circle 0.84. **The unique feature: 4-petal layer in addition to 8-petal lotus**, making this the only Nitya yantra with explicit 4-petal layer. (nitya_yantra_geometry.csv, OBSERVED:TRADITIONAL — Dakshinamurti Samhita: "her yantra as consisting of a triangle, four petals, eight petals and a bhūpura.")
- **yantra_geometry_notes**: Classical attested geometry. The 4+8 petal arrangement (12 petals total) matches the 12 zodiac signs but in a different proportion than Vahnivāsinī's 12-petal single ring. The 4-petal inner ring + 8-petal outer ring encodes a 4-cardinal + 8-direction structure — direct alignment with the 4-gate bhupura framing.
- **yantra_symmetry_order**: N=6 (hexagonal, periodic). Sister-symmetry to Bhagamalini (Nitya 2). The hexagonal lattice is fully crystallographic (graphene-family). (devi_engine.py DEVI_N)
- **yantra_center_logic**: Bindu as point, surrounded by triangle, surrounded by 4 cardinal petals, then 8 petals. Inner circle scale 0.84.
- **yantra_outer_boundary**: Bhupura with 4 gates. Interference radius fraction: 0.65. Wave function: **sine**, frequency multiplier: **2**, angular position: 120°.
- **yantra_layer_count**: 5 layers: bindu → triangle → 4-petal lotus → 8-petal lotus → bhupura. The most layers in the early Nitya sequence (tied with Bhagamalini's 5 layers). (nitya_yantra_geometry.csv)

## Field Math

- **graha_k**: Shani = k=6, magic constant **M=33**. (yantra_eigenvalue_exploration.md, Finding 2). yantra_geometry CSV assigns Venus (k=5, M=30); devi_master Saturn is treated as authoritative.
- **magic_constant_M**: 33 (Shani, k=6). Eigenvalues: {33, +4.899, -4.899}. (Finding 1)
- **invariant_secondary_modes**: +/-2sqrt(6) = +/-4.8990. (Finding 1)
- **coherence_ratio**: lambda_2/M = 4.899/33 = **0.1485** (Shani). The 7th most coherent graha (only Rahu 0.1361 and Ketu 0.1256 are more coherent). Saturn's field is highly uniform — the slow steady-state graha. (Finding 2)
- **eigenvector_axes**: For Shani (k=6): Brahmasthana = uniform [1/√3, 1/√3, 1/√3]. Primary tension (lambda=+4.899): South row vs center. Secondary tension (lambda=-4.899): North row vs center. (Finding 6)
- **brahmasthana_definition**: Uniform eigenvector at every Kronecker level. (Finding 4)
- **kronecker_level**: Level 1: 3x3, M=33. Level 2: 9x9, M=1089. Level 3: 27x27, M=35937. M_n = M_1^n. (Finding 3)
- **navagraha_composite_role**: Shani occupies the k=6 position in the 9x9 composite. Saturn's Lo Shu placement is in the W (Varuna) — the dissolution/decay quadrant. (Finding 5)

## Wave/Interference

- **boundary_harmonic_mode**: At k=6: the **sextile** harmonic (60° aspect). Shashthi = the 6th tithi — natural alignment with k=6 wave structure. The sextile is the strong tithi-group differentiator (k=6 differentiation = 1.006, the second-highest after k=12 rashi). (two-source-interference-v3.md, Finding 8 + Finding 10)
- **two_source_pattern**: A(theta) = 2 * cos(k(theta - midpoint)) * cos(k * separation/2). At k=6: constructive maximum at 60° separation. Shashthi's actual Sun-Moon separation is 60°-72° — this is the **first tithi where the actual separation crosses the 60° sextile boundary**, putting Mahāvajreśvarī's wave field at maximum k=6 resonance. (Finding 8)
- **nodal_interior_pattern**: For N=6 multigrid (graphene lattice): periodic, hexagonal, fully crystallographic. Same lattice family as Bhagamalini (Nitya 2). The frequency_multiplier=2 doubles the radial nodes within Bhagamalini's structure. (CONSTRUCTION_CHOICES.md + nitya_yantra_geometry.csv)
- **ring_vs_disk_distinction**: On the boundary: 6-source pattern at k=6. In the disk: 6-fold multigrid produces hexagonal nodal structure with frequency_multiplier=2 doubling. (Finding 7)
- **gandanta_gain**: Shashthi is a Nanda tithi. Fire-starting gandantas PREFER Nanda — amplification when Shashthi coincides with Ashwini/Magha/Mula. (Finding 11)
- **wave_panchaka_relation**: Orthogonal: r = -0.011. (Finding 12)
- **quantized_prime_modes**: Saturn (Shani) is k=6 in the eigenvalue derivation but NOT in the planetary prime sequence {3,5,7,11}. Saturn's retrograde count (~1 per year, 29-year cycle for Saturn-29 prime — but 29 is excluded from the v1 paper's prime set as "less geometrically clean"). The graha-prime mismatch: Mahāvajreśvarī's tithi number (6) is composite (2×3), and her graha (Saturn) is also outside the prime sequence. The position is structurally non-prime — appropriate for the slow, cumulative, settled Saturn function. (planetary-primes-v1.md, Section 2)

## Quasicrystal/Chladni

- **quasicrystal_line_style**: 6-fold multigrid (sister to Bhagamalini's). Periodic hexagonal lattice (graphene family). Frequency_multiplier=2 doubles the radial frequency. (CONSTRUCTION_CHOICES.md + nitya_yantra_geometry.csv)
- **nodal_density**: SOURCE_NEEDED. interference_radius_fraction = 0.65 (lower than Bhagamalini's 0.85, suggesting tighter central concentration).
- **radial_bands**: 2 radial nodes within unit disk (frequency_multiplier=2). Same density as Bheruṇḍā (4) and Vahnivāsinī (5).
- **interference_centers**: Primary = bindu (6 sine waves at 60°, double-frequency). Secondary maxima at 12 points: 6 at vertices of inscribed hexagon at interference_radius=0.65 + 6 at mid-edges (frequency=2 produces additional resonance ring). 3D mediator polyhedron: cuboctahedron (same as Bhagamalini, since N=6 → 14 faces). (CONSTRUCTION_CHOICES.md)

## Pasaka/Magic Cube

- **cube_type**: Andrews 1917. M=42. (magic_cube_analysis.json)
- **cube_magic_constant**: M = 42. (Finding 1)
- **cube_layer_squares**: layer_0 {42, -9, -9}, layer_1 {42, 0, 0}, layer_2 {42, +9, +9}. (Finding 1)
- **cube_invariant**: +/-9. Rational. (Finding 2)
- **cube_center_value**: 14. (Finding 3)
- **cube_associative_sum**: 28. (Finding 4)
- **cube_tensor_isotropy**: sigma_1 = 72.75. (Finding 6)
- **cube_kronecker_scaling**: M_n = 42^n. (magic_cube_extension.json)
- **cyclic_composite_eigenvalues**: 9x9: M=126, eigenvalues {126, +/-2.598, 0×4}. (Finding 2)
- **loshu_weighted_cube_mode**: Lo Shu collapses to {126, 0, ...}. (Finding 3)

### Pasaka at total=6

The pasaka deck has **10 outcomes** at total=6 (the Mahāvajreśvarī-resonant sum):

| ID | Dice | Name | Quality | Body | Graha | Rasa |
|----|------|------|---------|------|-------|------|
| 4 | 1,1,4 | Kali | mixed | left_eye | Rahu | tikta |
| 7 | 1,2,3 | Siddhi | good | nose | Mercury | amla |
| 10 | 1,3,2 | Hrī | very_good | right_shoulder | Sun | kaṭu |
| 13 | 1,4,1 | Tuṣṭi | very_good | left_arm | Moon | madhura |
| 19 | 2,1,3 | Śraddhā | good | heart | Sun | madhura |
| 22 | 2,2,2 | Sarasvatī | excellent | lower_abdomen | Moon | madhura |
| 25 | 2,3,1 | Gāyatrī | excellent | right_thigh | Sun | madhura |
| 34 | 3,1,2 | Māheśvarī | excellent | left_foot | Moon | madhura |
| 37 | 3,2,1 | Śāntā | very_good | top_of_head | Moon | madhura |
| 49 | 4,1,1 | Śubhā | very_good | right_side | Venus | madhura |

Distribution: 3 excellent, 4 very_good, 2 good, 1 mixed — strongly positive (9/10 good or better). Graha distribution: **Moon 4, Sun 3, Venus 1, Rahu 1, Mercury 1 — Moon-Sun dominance, no Saturn**. The Saturn-tithi (Mahāvajreśvarī's graha) produces pasaka outcomes carrying NO Saturn — the dice-system completely sidesteps the devi's actual graha. The interpretation: Saturn's slow-cumulative function is invisible to the dice; only fast-luminous outcomes (Sun, Moon) and sweet outcomes (Venus, mixed Rahu) appear at total=6. The vajra-strike (Mahāvajreśvarī's iconographic action) does not show up in the dice — what shows up is the AFTER-state, dominated by Moon (luminous reception) and Sun (luminous projection). Bodies span across all major regions: head (left_eye, top_of_head, nose), shoulders (right_shoulder), arms (left_arm), trunk (heart, lower_abdomen, right_side), thighs/legs (right_thigh, left_foot) — the most distributed body coverage of any total in the deck. Rasas: madhura dominant (7/10), with bitter/sour/pungent at edges. The 10-outcome bin at total=6 has the **highest cardinality of any total** (tied with total=9) — Shashthi is the position of maximal pasaka diversity.

## I Ching

- **hexagram_id**: SOURCE_NEEDED. Numerical correspondent: hexagram 6 (Sòng, "Conflict") — the situation of unresolved opposition. The pairing is structurally interesting: Mahāvajreśvarī's vajra resolves conflict instantly through superior force; the I Ching's hexagram 6 advice is to "withdraw before harm comes." Two opposed strategies for the same situation.
- **hexagram_arrangement**: Fuxi ↔ King Wen spectral opposites. (iching_spectral_analysis.json)
- **rank_complexity**: Q6 hypercube eigenvalues, Pascal row 6. (Finding 3)
- **yin_yang_balance_mode**: XOR-with-63 perfect partition. (Finding 6)
- **hypercube_distance_signature**: Hamming rank 7. (Finding 5)
- **pascal_row_signature**: Row 6, total 64. (Finding 3)

## Lo Shu x I Ching Bridge

- **trigram_loshu_weight_map**: Li=9, Kan=1, Zhen=3, Dui=7, Xun=4, Gen=8, Kun=2, Qian=6. Shashthi (6) maps to **Qian=6** — the Heaven trigram, the Creative, the pure-yang trigram. **Note**: Qián (the hexagram, all-yang) and Qian (the trigram, three-yang-lines) share the name; the trigram value of 6 in the Lo Shu is the position of pure-yang. The pairing with Mahāvajreśvarī's vajra (the masculine instant-cutting power) is exact: Qian's purest masculine creative force matches the vajra's pure-yang piercing function. The vajra IS the Heaven-trigram instantiated as weapon. (loshu_iching_interaction.json)
- **weighted_spectral_breaking**: 7 → 27 unique eigenvalues. (test4_weighted_Q6)
- **spectral_gap_change**: 2.0 → 0.4624. Fiedler 0.1944. (test5_spectral_gap)

## Alchemical/Bhasma

- **material_classical_class**: Shani's metal is **Lauha** (iron, Fe). Gem: **Nīla** (blue sapphire). Iron-blue-sapphire is the standard Saturn pairing. In rasashastra: Lauha is among the most prepared bhasmas (extensive textual treatment). (SYNTHESIS — Bhasma docx general framework; the Sivaduti card mentioned Lauha bhasma is one of the named worked-examples.)
- **material_scientific_type**: Iron (Fe) — element 26, the most abundant heavy element on Earth, the metal of the planet's core. Forms Fe2O3 (red rust) → Fe3O4 (magnetite, black) → various oxide states. Blue sapphire is corundum (Al2O3) with iron-titanium impurities (the same crystal as ruby with different impurities — sapphire-titanium-iron vs ruby-chromium).
- **base_material**: Lauha (iron) for the metallic preparation; Nīla (blue sapphire) for the gem preparation. Both are major Saturn substances.
- **prepared_substance_type**: Lauha Bhasma (iron bhasma); Nīla Pishti (sapphire powder).
- **shodhana_media**: Iron: heated and quenched in til-taila, takranī, gomūtra, kānjī, kulattha kvāth — the standard 5-media sequence. Sapphire: shodhana via kshira (milk) bhavana. (Bhasma docx, classical framework)
- **bhavana_media**: Lauha bhasma is bhavana'd with triphala kvāth (the iron-affinity decoction), aloe juice, and brahmi swarasa. (Bhasma docx)
- **marana_cycles**: SOURCE_NEEDED for exact count. Lauha typically 100+ puta cycles per classical texts — the most labor-intensive bhasma due to iron's stable oxidation states. The Lauha process is often cited as the model for all metal bhasmas.
- **puta_profile**: SOURCE_NEEDED.
- **quality_tests**: Standard tests + Lauha-specific: should not respond to magnet after sufficient marana (the metallic Fe phase fully oxidized to non-magnetic forms). (Bhasma docx)
- **completion_stop_rule**: Quality tests pass + non-magnetic verification.
- **phase_transformation**: Fe → Fe2O3 (hematite, red) → Fe3O4 (magnetite, black) → fully amorphous oxide. The bhasmification removes magnetism; the test is structurally elegant — magnetism IS the macroscopic signature of metallic Fe. (SYNTHESIS)
- **particle_scale_overlay**: SOURCE_NEEDED.
- **safety_conditions**: Lauha bhasma is one of the most-used bhasmas (treats iron-deficiency anaemia classically). Generally safe when properly prepared. Iron overdose risk if amounts exceed therapeutic (cumulative iron toxicity is well-documented in modern medicine).

## Graha/Material

- **graha_material_map**: Shani (Saturn) → Lauha (iron), Nīla (blue sapphire). In BPHS: Saturn's friends are Mercury, Venus; enemies: Sun, Moon, Mars; neutral: Jupiter. Saturn-Sun is the most pronounced enmity in the friendship table. (Graha Material docx)
- **friend_enemy_interaction**: Saturn-Sun (Fe-Au): iron and gold form alloys but with limited solubility. The "enemy" relationship metallurgically: iron RUSTS (oxidation, decay over time) while gold does NOT — Saturn's slow corruption against Sun's incorruption. Saturn-Mars (Fe-Cu): iron and copper form alloys (cast iron variants); the enmity is functional not metallurgical. Saturn-Mercury (Fe-Hg): iron does NOT amalgamate with mercury — friend by absence of interaction (Mercury's solvent power does not affect iron). The "friend" relationship materializes as mutual non-interference.
- **ritual_vs_medical_flag**: Both. Iron ritual objects (sacred swords, ritual implements) are moderate-frequency in tantric tradition. Lauha Bhasma is one of the most prescribed bhasmas. Nīla Sapphire is the principal Saturn gem and also has medical use.

## Plant/Ecology

- **plant_allies**: SOURCE_NEEDED. Traditional Shani plants: **Śamī** (Prosopis cineraria — the Saturn-tree, sacred to Shani worship), Triphalā (the three-fruit combo: Amalaki + Bibhitaki + Haritaki — all astringent, all Saturn-rasa), Aśvagandhā (Withania somnifera — the slow-building rasāyana). Śamī is the most directly Shani-aligned: dark, dense, slow-growing, drought-tolerant — the encoding of saturn-time-tolerance.
- **processing_plants**: SOURCE_NEEDED. For Lauha: triphalā kvāth is the primary bhavana medium.
- **doctrine_of_signatures_overlay**: SOURCE_NEEDED. Shani plants are dark-leaved, slow-growing, often spiny or thorny (Śamī, Khadira), astringent-tasting, drought-tolerant. The "Saturn signature" in plants encodes endurance, contraction, time-binding.
- **astrobotanical_timing**: SOURCE_NEEDED. General: Shashthi-Skanda is auspicious for transplanting (the structuring tithi); Saturday under Shani-ruled nakshatras (Pushya, Anuradha, Uttara Bhadrapada) maximally Shani-aligned.

## Body/Therapeutics

- **dosha_predicates**: Tithi 6 element: earth (tithi_master.csv), guna: sattva. Devi element: air (nitya_devi_master.csv), guna: rajas. Chakra: Vishuddha (Shani/Saturn correspondence) — ether element, sattva, Vata-Kapha dosha, Shakini shakti. (chakra_cross_domain.csv). The earth/air/ether triad with sattva-rajas-sattva graduation is the **vapor-conversion profile**: solid → wind → space. The vajra strike turns earth into air into ether — the Mahāvajreśvarī function expressed as dosha-element gradient.
- **dhatu_targets**: SOURCE_NEEDED. Traditional: Shani governs **Asthi dhatu** (bone) — particularly bone-density disorders (osteoporosis, arthritis, bone-tumors). Lauha bhasma is also classically used for raktakshaya (anemia) — iron's most direct medical correspondent.
- **organ_targets**: Vishuddha (Shani chakra) at throat: thyroid and parathyroid glands, throat and ears. Body system: communication, expression, inspiration, discrimination. (chakra_cross_domain.csv). Associated nakshatras: Pushya, Anuradha, Uttara Bhadrapada — the three Saturn-ruled nakshatras. Direct chakra-nakshatra-graha alignment.
- **indication_clusters**: SOURCE_NEEDED. Traditional Shani disorders: chronic wasting diseases, paralysis, arthritis, bone disorders, melancholia, nerve degeneration, hearing loss, voice disorders.
- **anupana_vehicle**: SOURCE_NEEDED. Traditional Saturn-anupana: castor oil (eraṇḍa taila), gur (jaggery), sesame oil, ghṛta — heavy, oily, downward-moving vehicles to balance Saturn's drying nature.
- **preparation_dependency_warning**: Lauha bhasma well-tolerated; iron overdose risk if therapeutic dose exceeded.

## Prime/Morphology

- **prime_signature**: 6 is **not a prime** — it is 2×3 (the smallest perfect number, sum of its proper divisors 1+2+3=6, AND product of the two smallest primes). Shashthi's tithi number is the **most composite of small numbers**. Mahāvajreśvarī's graha (Saturn, k=6) shares this number — Saturn's k=6 is also outside the {3,5,7,11} prime sequence. The doubly-composite position: composite tithi + composite-k-graha. (planetary-primes-v1.md, Section 2)
- **morphology_correlates**: 6-fold structures in human anatomy: 6 layers of cerebral cortex (the laminar architecture of all mammals), 6 cervical vertebrae in some species (manatees, sloths), 6-pointed star structure of red blood cells (rouleaux formation). The cerebral 6-layer count is the most morphologically significant — the brain's 6-fold lamination is universal mammalian architecture. (vertebral-primes-v1.md, general framework + neuroanatomy)
- **sri_yantra_region_relation**: 6 is the **product** of the smallest two primes 2×3. In the 44-region quantized field overlay, 6 does not appear as a primary mode (the overlay uses {3,5,7,11}), but the sextile aspect (k=6 wave harmonic) is one of the two strongest tithi-group differentiators. The "6" of Shashthi is structurally tied to the wave-harmonic level rather than the prime-symmetry level. (planetary-primes-v1.md, Section 3 + two-source-interference-v3.md, Finding 10)

## Sound/Rhythm

- **svara_link**: SOURCE_NEEDED. Shani's traditional svara is **Ni** (Niṣāda, the major 7th) per some Gandharva Veda sources — the "highest" svara before octave return, encoding Saturn's "edge of completion" function.
- **raga_link**: Saturn-associated ragas in raga_data.csv: **Ṭoḍī** (midday, water/rajas, vira; vadi Ma), **Pūriyā** (evening, air/rajas, raudra; vadi Ga), **Mālkauns** (latenight, earth/tamas, shanta; vadi Ma). Of these, **Pūriyā** matches Mahāvajreśvarī's signature most closely: air-rajas direct match (her own element-guna), evening timing aligns with Shashthi as a mid-cycle tithi. Pūriyā is rasa raudra (fierce) — the closest rasa to vajra-character even though Mahāvajreśvarī's stated rasa is adbhuta. The raudra-adbhuta near-match suggests Pūriyā is structurally close. **Ṭoḍī** is also strong (vira rasa, water element — the "thunderbolt-water" pairing of vajra-as-storm).
- **tala_link**: SOURCE_NEEDED. The 6-fold yantra symmetry suggests 6-beat or 12-beat cycles (Dādrā 6-beat, Ektāl 12-beat in Hindustani; Rūpaka 6-beat in Carnatic).

## Vastu/Spatial

- **mandala_zone_map**: Shani at k=6 places yantra values as Lo_Shu + 6*J = {10, 15, 14; 17, 11, 9; 12, 13, 16}. Brahmasthana (center cell) = 11. Eigenvector structure: uniform (M=33), primary tension (NE-SW), secondary tension (perpendicular). (yantra_eigenvalue_exploration.md)
- **directional_emphasis**: SOURCE_NEEDED. Traditional: Shani governs the **West** (Varuṇa direction) — the dissolution/sunset quadrant. The Lo Shu placement of Saturn at West is consistent across Vastu traditions.

## Visual Grammar

- **palette_logic**: Primary: #7b68ee (medium slate blue, from nitya_devi_master.csv). Secondary: #FFCDD2 (pale pink, from nitya_yantra_geometry.csv). Bindu: #E91E63 (rose-magenta). Line weight: medium. The air-rajas-Saturn signature creates a stormy palette: slate-blue field (distant lightning sky), pale-pink accents (the rose-flower garland), magenta bindu (the lightning-flash core).
- **density_logic**: interference_radius_fraction = 0.65. The 6-fold periodic field with frequency_multiplier=2 has medium-tight density. Render with the 4-petal+8-petal layered structure visible — Mahāvajreśvarī's distinguishing geometric feature.
- **line_weight_logic**: Medium. The 5-layer structure (bindu + triangle + 4-petal + 8-petal + bhupura) is the most layered yantra in the early sequence; consistent line weight prevents over-busyness.
- **panel_layout**: SOURCE_NEEDED.
- **symbol_strip**: CUT + BIND + DEFEND. 3 weapons + the implicit vajra (named in title, not in weapons_full). 4-petal inner lotus + 8-petal outer lotus = 12 petals total (zodiacal). Garland of red flowers. Bija: Aim Hrīm (chained).
- **caption_motto**: "Mistress of the great thunderbolt — her power cuts through delusion instantly." (nitya_devi_master.csv)

---

## Cross-layer observations

The first cross-layer resonance is the **Bhagamalini-Mahāvajreśvarī N=6 sister-symmetry pair completing the hexagonal Nityas**. Among the first 7 Nityas, only Bhagamalini (2) and Mahāvajreśvarī (6) have N=6 yantra symmetry. Both project onto the same hexagonal lattice (graphene-family), but at different angular positions (24° vs 120°) and with different frequency multipliers (1 vs 2). The pair encodes the same shape at different lunar arc-positions: Bhagamalini at the "first pairing" moment (Sun-Moon just separating), Mahāvajreśvarī at the "first sextile aspect" moment (Sun-Moon at 60°-72°, crossing the sextile boundary). The same crystallographic structure appears twice in the cycle — once at low-arc (Bhagamalini, freq=1) and once at sextile-crossing (Mahāvajreśvarī, freq=2). The frequency doubling marks Mahāvajreśvarī as the "intensified Bhagamalini" — same shape, doubled radial density, vajra-instead-of-bhaga.

The second resonance is the **Qian-trigram alignment with vajra-as-pure-yang-instrument**. The trigram_loshu_weight_map places Qian (Heaven, pure yang, three solid lines) at Lo Shu position 6 — Mahāvajreśvarī's tithi position. Qian's iconographic signature is "the dragon flying in the sky" — the vajra is precisely this: lightning, the dragon's flight made instant. Among all 8 trigrams, Qian is the most directly aligned to the vajra's iconographic function. The pairing is structurally exact at the I Ching layer. Note: this is NOT the case for any other Nitya — only Bhagamalini (2 → Kun, Earth/Receptive) and Mahāvajreśvarī (6 → Qian, Heaven/Creative) sit at the **trigram archetype positions** of pure-yin and pure-yang. They are the only two "archetype-pole" Nityas in the first 7. Together they encode the Earth-Heaven polarity at the trigram level.

The third resonance is the **Saturn-Skanda apparent contradiction resolving through the slow-strike duality**. Tithi deity Kartikeya (Skanda) is the warrior-god, son of Shiva, fast-moving, peacock-mounted, six-headed. Devi-graha is Saturn (Shani), the slowest graha, the time-binder, the contraction-master. Vajra is the lightning-bolt, instant. Saturn is the slow-cumulative. How does Mahāvajreśvarī's vajra (instant strike) reconcile with her graha (Saturn, slow)? The resolution: Saturn is the cause of the storm, not the lightning itself. Storms accumulate slowly (Saturn-time) and discharge instantly (vajra-time). The same dual time-scale is encoded in Skanda's iconography (six heads = 6-fold simultaneity, but he is also the warrior who STRIKES and finishes). Mahāvajreśvarī's tithi is the moment when slow accumulation discharges into instant clarity — the lightning-flash that is the visible signature of an entire weather-system's prior buildup. The Saturn-vajra pair encodes karma's cumulative-into-instant nature: deeds accumulate (Saturn) until they discharge (vajra) into karmic resolution.

---

## Attestation summary

- **OBSERVED:PRIMARY**: Identity (name, bija, mantra, weapons, description, body color, ornamentation, rasa, element, guna, shakti from nitya_devi_master.csv); Lunar/Time (tithi quality, deity, good_for/avoid from tithi_master.csv); Yantra geometry (Dakshinamurti Samhita: triangle + 4 petals + 8 petals + bhupura per nitya_yantra_geometry.csv).
- **OBSERVED:TRADITIONAL**: Bhasma substance classes (Lauha/Nīla rasashastra); Saturn's friend/enemy table (BPHS); chakra-graha mapping (chakra_cross_domain.csv); raga-graha mapping (raga_data.csv).
- **SYNTHESIS**: Field Math eigenvalue derivation; Wave/Interference findings; Quasicrystal N=6 frequency-doubled construction; Prime/Morphology correspondences; Cross-layer observations; expanded_function; phase_transformation (iron oxide cascade); Saturn-vajra slow-fast resolution.
- **GENERATED**: None. SOURCE_NEEDED fields are flagged.

---

## SOURCE_NEEDED flags

1. **mudras_gestures / vahana_mount / faces_arms_count**: Tantric iconographic source.
2. **nakshatra_overlays**: Compute Shashthi (Nanda-group) wave fine structure.
3. **nodal_density / radial_bands precise count**: Run N=6 sine frequency=2 multigrid.
4. **hexagram_id**: User decision for tithi 6 → hexagram 6 (Sòng).
5. **shodhana_media exact / bhavana_media exact / marana_cycles count / puta_profile / particle_scale_overlay**: Bhasma docx primary detail consultation for Lauha.
6. **plant_allies confirmation (Śamī primary?) / doctrine_of_signatures_overlay / processing_plants / astrobotanical_timing**: Cross-reference traditional Shani plants with guild_full.csv.
7. **dhatu_targets / indication_clusters / anupana_vehicle**: Ayurvedic text consultation for Shani-specific protocols.
8. **svara_link / tala_link**: Gandharva Veda source.
9. **directional_emphasis**: Vastu confirmation for Saturn-West.
10. **panel_layout**: Design decision.
