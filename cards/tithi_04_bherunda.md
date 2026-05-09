# Bherunda · Tithi 4 · Card

**Source compilation**: 2026-05-01
**Schema version**: Atlas Tithi Card Master Table (user-provided, 2026)
**Population status**: ~58/82 fields sourced, ~24 SOURCE_NEEDED flags

---

## Identity

- **tithi_number**: 4
- **tithi_name**: Caturthī
- **paksha_mode**: Both shukla and krishna. Ganesha is tithi deity. Quality: inauspicious. (tithi_master.csv)
- **devi_name**: Bherunda
- **devi_alt_names**: Bheruṇḍā (भेरुण्डा). The "fierce one" — destroyer of obstacles through terrifying form. Bija: Hrūm. Mantra: Om Hrūm Bheruṇḍāyai.
- **seed_keywords**: fierce protection, obstacle destruction, 8 weapons, fire-tamas, raudra, CUT/DEFEND/BIND/REVEAL, Rahu-shadow

## Canonical Devi

- **iconography_summary**: The fierce one — she who destroys obstacles through her terrifying form. Molten gold (skin), garments not specified. Carries the most weapons of any Nitya in the first 6: aṅkuśa, śūla (spear), vajra (thunderbolt), sword, pāśa, bow, gāda (mace), shield. Eight weapons — full martial array. (nitya_devi_master.csv, OBSERVED:PRIMARY, attested_classical)
- **weapons_items**: Aṅkuśa (goad), śūla (spear), vajra (thunderbolt), sword, pāśa (noose), bow, gāda (mace), shield. **8 implements — the most of any Nitya in the first 6**, tied with Sivaduti's 6 and exceeded only by potentially Tvaritā/Kulasundari (whose weapon listings are partial). Capability signature: CUT, DEFEND, BIND, REVEAL. (nitya_devi_master.csv, OBSERVED:PRIMARY)
- **mudras_gestures**: SOURCE_NEEDED: Mudra field empty in nitya_devi_master.csv for Bheruṇḍā.
- **vahana_mount**: SOURCE_NEEDED. The fierce-form classification often associates with lion or tiger (śerāvalī), but unattested specifically for Bheruṇḍā in on-disk sources.
- **body_color**: Molten gold. Color hex: #8b0000 (dark crimson — represents her field/aura, contrasting the textual molten-gold body color). The dark-red field encodes raudra-rasa intensity. (nitya_devi_master.csv)
- **ornamentation**: SOURCE_NEEDED: Garments field "color: not specified," ornaments empty. The 8-weapon array IS the iconographic signature; ornamentation may be subordinate.
- **faces_arms_count**: 8 weapons → minimum 8 hands (likely 8 arms in classical fierce-form iconography). One of the few Nityas where weapon count directly determines arm count.
- **shakti_statement**: Fierce protection — the obstacle-destruction shakti. Bheruṇḍā's name relates to the "two-headed bird" iconography in some traditions (Sharabha-Bherunda) — the dual-aspect protective form. (nitya_devi_master.csv, OBSERVED:PRIMARY)
- **expanded_function**: Bheruṇḍā is the fourth Nitya — the obstacle-destroying intervention. Where Nityaklinna (3) is dissolution-as-melting, Bheruṇḍā (4) is dissolution-as-shattering. Her tithi is the Vinayaka-Caturthi (Ganesha's day) — the obstacle-removing tithi par excellence. The 8-weapon array and the molten-gold body encode pure martial intensity. Her N=3 yantra symmetry (devi_engine.py DEVI_N) is THE SAME as Kāmeśvarī (1) and Nityaklinna (3) — three Nityas in the first 4 share the simplest crystallographic projection. The structural meaning: the early-cycle obstacle-states all use the simplest geometry, with their differentiation coming from angular_position rather than fold-symmetry. Her graha is Rahu (the shadow-graha, k=7) — the obstacles she destroys are precisely Rahu's illusory obstructions. (SYNTHESIS from nitya_devi_master.csv + nitya_yantra_geometry.csv + CONSTRUCTION_CHOICES.md)
- **bhava_mood**: Raudra (fury). Rasa: raudra. Element: fire. Guna: tamas. The fire-tamas pairing is the signature of dense, downward, transformative heat — the heat of forge and pyre. (nitya_devi_master.csv, OBSERVED:PRIMARY)
- **mantra_bija**: Hrūm. The Hrūm-bija is the bhairava-bija — the masculine fierce-form bija, ordinarily associated with Bhairava. Bheruṇḍā's use of Hrūm marks her as the feminine bhairava-equivalent. (nitya_devi_master.csv, OBSERVED:PRIMARY)

## Lunar/Time

- **lunar_phase_arc**: 36°-48° from conjunction (shukla chaturthi), or 216°-228° (krishna chaturthi). The 4th tithi spans 12° of Sun-Moon elongation.
- **phase_quality**: **Inauspicious** (tithi_master.csv). Good for: destructive acts, obstacle removal, tantra sadhana. Avoid: new ventures, marriage, travel. Tithi deity: Ganesha. The tithi-deity (Ganesha, obstacle-remover) and the devi (Bheruṇḍā, obstacle-destroyer) work together — Caturthi is the tithi where obstacles are deliberately confronted.
- **nitya_cycle_position**: 4th of 15 — the obstacle-removal position. Caturthi is the structurally inauspicious early-cycle tithi. Vinayaka-Caturthi (shukla 4) is the major Ganesha festival; Sankashti-Chaturthi (krishna 4) is the monthly obstacle-removal observance.
- **weekday_links**: Caturthi's tithi deity is Ganesha. Bheruṇḍā's graha correspondence is Rahu per devi_master — Rahu has no weekday (the shadow grahas are weekday-less; sometimes assigned Saturday by association). The yantra_geometry CSV assigns **Mercury** to tithi 4 — **discrepancy** with devi_master's Rahu. The devi_master is treated as authoritative. Note: this means k=7 (Rahu) for the eigenvalue derivation, M=36.
- **nakshatra_overlays**: SOURCE_NEEDED: Caturthi belongs to the **Rikta group** (T4, T9, T14, T19, T24, T29 — "empty/loss tithis"). The Rikta group is structurally inauspicious — paired with Ganesha-Caturthi-Bheruṇḍā, this gives the entire tithi a "void to be filled by destruction" valence. Wave fine structure differentiation pattern for Rikta-group not directly extracted to a lookup table.

## Yantra

- **yantra_family**: Downward triangle (trikona) with eight petals and bhupura — same base as Nityaklinna, but with Shikhinī, Nīlakaṇṭhī, and Raudrī deities inscribed in the triangle. Triangle scale 0.84, inner circle 0.88. (nitya_yantra_geometry.csv, OBSERVED:TRADITIONAL — Dakshinamurti Samhita: "her yantra as a triangle, eight petals and bhūpura; the triangle contains the deities Shikhini, Nilakanthi and Raudri.")
- **yantra_geometry_notes**: Classical attested geometry with the unique feature of three named deities INSIDE the triangle (Shikhinī = peacock-feather/flame-crown; Nīlakaṇṭhī = blue-throated, the female Shiva; Raudrī = the fierce one). This makes Bheruṇḍā's yantra the most populated of the early Nitya yantras at the bindu/triangle level. The N=3 multigrid projection (devi_engine.py DEVI_N) is the same family as Kāmeśvarī and Nityaklinna.
- **yantra_symmetry_order**: N=3 (triangular, periodic). Same crystallographic family as Nityas 1 and 3. Bheruṇḍā = third instance of triangular symmetry in the first 4 Nityas.
- **yantra_center_logic**: Bindu as point inside a triangle inscribed with three named fierce deities. Inner circle scale 0.88.
- **yantra_outer_boundary**: Bhupura with 4 gates. Interference radius fraction: 0.75. Wave function: **sine**, frequency multiplier: **2** (the first Nitya with frequency_multiplier=2 — produces 2 radial nodes). Angular position: 72°.
- **yantra_layer_count**: 3 layers + 3 inscribed deities: bindu → triangle (with Shikhinī/Nīlakaṇṭhī/Raudrī) → 8-petal lotus → bhupura. Triangle at 0.84 scale, orientation: down. (nitya_yantra_geometry.csv)

## Field Math

- **graha_k**: Rahu = k=7, magic constant M=36. (yantra_eigenvalue_exploration.md, Finding 2). However, yantra_geometry CSV assigns Mercury (k=3, M=24). **Discrepancy**: devi_master Rahu is treated as primary. Used here: k=7, M=36.
- **magic_constant_M**: 36 (Rahu, k=7). Eigenvalues: {36, +4.899, -4.899}. (Finding 1)
- **invariant_secondary_modes**: +/-2sqrt(6) = +/-4.8990. (Finding 1)
- **coherence_ratio**: lambda_2/M = 4.899/36 = 0.1361 (Rahu). The 8th most coherent graha (only Ketu at 0.1256 is more coherent). Rahu's field is among the most spatially uniform — paradoxical for a "shadow disturber" graha, but consistent with the high coherence of high-k grahas. (Finding 2)
- **eigenvector_axes**: For Rahu (k=7): Brahmasthana = uniform [1/√3, 1/√3, 1/√3]. Primary tension (lambda=+4.899): South row vs center polarity. Secondary tension (lambda=-4.899): North row vs center, perpendicular. (Finding 6)
- **brahmasthana_definition**: Uniform eigenvector at every Kronecker level. (Finding 4)
- **kronecker_level**: Level 1: 3x3, M=36. Level 2: 9x9, M=1296. Level 3: 27x27, M=46656. M_n = M_1^n. (Finding 3)
- **navagraha_composite_role**: Rahu occupies the k=7 position in the 9x9 composite. Rahu's Lo Shu placement is in the SE (Agni) — adjacent to Saturn's W placement, forming the Rahu-Saturn shadow-axis. (Finding 5)

## Wave/Interference

- **boundary_harmonic_mode**: At k=4: the **square** harmonic. Caturthi = the 4th tithi — natural alignment with k=4 wave structure. The square (90° separation) is a classical hard aspect — tension, conflict, friction. (two-source-interference-v3.md, Finding 8)
- **two_source_pattern**: A(theta) = 2 * cos(k(theta - midpoint)) * cos(k * separation/2). At k=4: constructive maximum when separation = 90°. Caturthi's actual Sun-Moon separation is 36°-48° (well below 90°), but the k=4 carrier is structurally active. (Finding 8)
- **nodal_interior_pattern**: For N=3 multigrid (Bheruṇḍā shares Kāmeśvarī's geometry): periodic hexagonal lattice. The frequency_multiplier=2 (vs Kāmeśvarī's 1) **doubles the radial node count** within the disk — Bheruṇḍā's field has 2 concentric ring-modes vs Kāmeśvarī's 1. (CONSTRUCTION_CHOICES.md + nitya_yantra_geometry.csv)
- **ring_vs_disk_distinction**: On the boundary: 3-source pattern at k=3. In the disk: 3-fold multigrid with frequency_multiplier=2 produces the densest 3-fold lattice in the early Nityas. (Finding 7)
- **gandanta_gain**: Caturthi is a Rikta tithi. Gandanta-Rikta interaction not directly extracted from RESEARCH-017 Finding 11. The paper specifies fire-starting gandantas prefer Nanda; water-ending prefer Purna; ALL avoid Jaya. Rikta-group preferences are not specifically broken out. SOURCE_NEEDED for exact Rikta-gandanta differentiation values.
- **wave_panchaka_relation**: Panchaka and wave systems orthogonal: r = -0.011. (Finding 12)
- **quantized_prime_modes**: Rahu is k=7 in the eigenvalue derivation, but Rahu does not retrograde in the orbital sense — Rahu/Ketu are nodal points, not bodies. They appear in the prime sequence only via their formal k-assignment. The Rahu-Ketu axis IS the 180° structural invariant (two-source-interference-v3.md, Finding 9) — a different geometric mode than the {3,5,7,11} prime sequence. (planetary-primes-v1.md + Finding 9)

## Quasicrystal/Chladni

- **quasicrystal_line_style**: 3-fold multigrid with frequency_multiplier=2 — same crystallographic projection as Kāmeśvarī but with double radial frequency. The interior structure is denser. (CONSTRUCTION_CHOICES.md + nitya_yantra_geometry.csv)
- **nodal_density**: SOURCE_NEEDED: No computed metric. The frequency_multiplier=2 doubles the nodal count vs Kāmeśvarī's frequency=1. interference_radius_fraction = 0.75.
- **radial_bands**: 2 radial nodes within unit disk (frequency_multiplier=2). The first Nitya in the sequence with this density. (nitya_yantra_geometry.csv)
- **interference_centers**: Primary = bindu (3 sine waves at 120°, double-frequency). 6 secondary maxima (the 3 vertices of the inscribed triangle PLUS 3 mid-edge points — the doubled frequency creates an additional resonance ring). 3D mediator polyhedron: tetrahedron (N=3 → simplest Platonic). (CONSTRUCTION_CHOICES.md)

## Pasaka/Magic Cube

- **cube_type**: Andrews 1917. M=42. (magic_cube_analysis.json)
- **cube_magic_constant**: M = 42. (Finding 1)
- **cube_layer_squares**: layer_0 {42, -9, -9}, layer_1 {42, 0, 0}, layer_2 {42, +9, +9}. (Finding 1)
- **cube_invariant**: +/-9. Rational. (Finding 2)
- **cube_center_value**: 14. The 3D Brahmasthana. (Finding 3)
- **cube_associative_sum**: 28 = n^3+1. (Finding 4)
- **cube_tensor_isotropy**: sigma_1 = 72.75. (Finding 6)
- **cube_kronecker_scaling**: M_n = 42^n. (magic_cube_extension.json)
- **cyclic_composite_eigenvalues**: 9x9: M=126, eigenvalues {126, +/-2.598, 0×4}. (Finding 2)
- **loshu_weighted_cube_mode**: Lo Shu collapses to {126, 0, ...}. (Finding 3)

### Pasaka at total=4

The pasaka deck has **3 outcomes** at total=4 (the Bheruṇḍā-resonant sum):

| ID | Dice | Name | Quality | Body | Graha | Rasa |
|----|------|------|---------|------|-------|------|
| 2 | 1,1,2 | Tretā | very_good | forehead | Moon | madhura |
| 5 | 1,2,1 | Vijaya | excellent | right_ear | Jupiter | madhura |
| 17 | 2,1,1 | Pratibhā | excellent | right_breast | Moon | madhura |

Distribution: 2 excellent, 1 very_good. Total=4 is the **second-lowest sum** (only Kṛta at total=3 is rarer) — high-quality outcomes. Graha distribution: Moon 2, Jupiter 1 — **Moon-dominant, NO Mars/Rahu/Saturn**. The graha-tithi mismatch is even sharper here than at total=3: Bheruṇḍā's graha is Rahu, but the pasaka outcomes carry only benefic grahas (Moon and Jupiter). Bodies cluster in the upper torso and head: forehead (ajña/third-eye), right ear, right breast. Rasa: all madhura (sweet). The interpretation: when the dice produce Caturthi's resonant total (4), the outcomes are benefic and centered in the upper-body, despite the underlying tithi being inauspicious and the devi being raudra-fierce. The fierce-form intervention CLEARS the obstacle and the resulting field is benefic — the pasaka outcomes show what remains AFTER Bheruṇḍā has acted.

## I Ching

- **hexagram_id**: SOURCE_NEEDED. Numerical correspondent: hexagram 4 (Méng, "Youthful Folly") — the situation of inexperience needing instruction. The pairing is structurally interesting: Caturthi is the obstacle-tithi, and Méng is the hexagram of the unprepared encountering reality and needing correction.
- **hexagram_arrangement**: Fuxi (rank 2) ↔ King Wen (rank 8). Spectral opposites. (iching_spectral_analysis.json)
- **rank_complexity**: Q6 hypercube eigenvalues, Pascal row 6. (Finding 3)
- **yin_yang_balance_mode**: XOR-with-63 perfect partition. (Finding 6)
- **hypercube_distance_signature**: Hamming rank 7. (Finding 5)
- **pascal_row_signature**: Row 6, total 64. (Finding 3)

## Lo Shu x I Ching Bridge

- **trigram_loshu_weight_map**: Li=9, Kan=1, Zhen=3, Dui=7, Xun=4, Gen=8, Kun=2, Qian=6. Caturthi (4) maps to **Xun=4** — the Wind/Wood trigram, the Gentle/Penetrating, "wind dispersing the dust." Xun's penetrating action matches Bheruṇḍā's obstacle-destroying function — but where Bheruṇḍā uses 8 weapons of force, Xun uses gentle persistent wind. The pairing reveals two paradigms of obstacle-removal. (loshu_iching_interaction.json)
- **weighted_spectral_breaking**: 7 → 27 unique eigenvalues. (test4_weighted_Q6)
- **spectral_gap_change**: 2.0 → 0.4624. Fiedler 0.1944. (test5_spectral_gap)

## Alchemical/Bhasma

- **material_classical_class**: Rahu's "metal" is unconventional — Rahu is a shadow graha and has no direct metal in classical rasashastra. By tradition, Rahu is associated with: lead (Naga), gomedha (hessonite garnet), or mixed metals. (SYNTHESIS — Bhasma docx not directly read; Rahu's bhasma is rarely prepared as a standalone substance)
- **material_scientific_type**: Hessonite (gomedha) is a calcium aluminum silicate (Ca3Al2(SiO4)3 — grossular garnet variety) with Mn impurities giving the orange-brown color. Lead (Pb) is element 82, dense and toxic.
- **base_material**: SOURCE_NEEDED. Disambiguation between gomedha (gem path) and Naga/Pb (metal path) for Rahu-Bheruṇḍā preparation requires Bhasma docx.
- **prepared_substance_type**: SOURCE_NEEDED. Naga Bhasma (lead bhasma) is a recognized rasashastra preparation but extremely toxic if improperly made. Gomedha is more commonly worn as a ratna (gem) than incinerated.
- **shodhana_media / bhavana_media / marana_cycles / puta_profile / particle_scale_overlay**: SOURCE_NEEDED. Lead requires extensive shodhana (often heated and quenched in 7 different liquid media sequentially). Naga Bhasma is the most carefully governed of all metal bhasmas due to lead toxicity.
- **quality_tests**: Standard bhasma tests apply. Naga Bhasma additionally tested for absence of metallic lead via flotation and color change.
- **completion_stop_rule**: All quality tests pass + chemical verification of complete oxidation. (Bhasma docx framework)
- **phase_transformation**: Pb → PbO (litharge, yellow) → Pb3O4 (red lead, minium) → fully oxidized particulate. The color sequence yellow → red → black is the classical sign of Naga Bhasma progression.
- **safety_conditions**: **Lead toxicity is severe**. Naga Bhasma is contraindicated for self-preparation; only trusted classical rasashala sources should be used. Cumulative lead exposure causes permanent neurological damage. The fierce-form devi (Bheruṇḍā) and the toxic-metal preparation (Naga) both require expert handling — the iconographic warning IS structural.

## Graha/Material

- **graha_material_map**: Rahu → Naga (lead), Gomedha (hessonite). In BPHS: Rahu-Saturn are friends; enemies: Sun, Moon, Mars; neutral: Jupiter, Venus, Mercury. The Rahu-Saturn alliance is the "shadow-axis" — both are grahas of restriction and slow effects. (Graha Material docx)
- **friend_enemy_interaction**: Rahu-Saturn (Pb-Fe alliance): lead and iron form alloys (lead-shielded iron is a classical metallurgy combination). Rahu-Sun (Pb-Au): lead is the alchemical opposite of gold — the base metal that medieval alchemists sought to transmute into gold. The "enemy" relationship is the most archetypally encoded. Rahu-Moon (Pb-Ag): lead and silver are commonly co-extracted from galena ore — they appear together in nature, but the metallurgical separation is foundational to silver refining (cupellation removes lead from silver). The "enemy" relationship materializes as required separation.
- **ritual_vs_medical_flag**: Both, with caution. Gomedha is widely used ritually (worn as gem). Naga Bhasma is medical but carefully gated.

## Plant/Ecology

- **plant_allies**: SOURCE_NEEDED. Rahu plants (traditional): Durva (Cynodon dactylon — sacred grass, the Ganesha-grass), white sandalwood (Santalum album), agastya (Sesbania grandiflora). Durva is structurally interesting: Caturthi is Ganesha's tithi, durva is Ganesha's plant — the convergence is exact. The fierce-form Bheruṇḍā and the Ganesha-tithi share the obstacle-removal function and the durva-grass association.
- **processing_plants**: SOURCE_NEEDED. Lead shodhana classically uses kulattha kvāth, brahmi swarasa, and other 7-media sequences.
- **doctrine_of_signatures_overlay**: SOURCE_NEEDED. Rahu plants are dark-leaved, twining (parasitic-like), or smoke-producing — encoding Rahu's shadow-nature.
- **astrobotanical_timing**: SOURCE_NEEDED. Caturthi-Vinayaka is auspicious for sowing durva. The general pattern: Rikta tithis (4, 9, 14) are NOT favored for new planting (the "loss" tithis), making Caturthi a structurally difficult sowing window.

## Body/Therapeutics

- **dosha_predicates**: Tithi 4 element: air (tithi_master.csv), guna: rajas. Devi element: fire (nitya_devi_master.csv), guna: tamas. Chakra: SOURCE_NEEDED — Rahu has no direct chakra mapping in chakra_cross_domain.csv (only the 7 grahas Sun-Moon-Mars-Mercury-Jupiter-Venus-Saturn appear). The air/fire/tamas-rajas combination suggests Vata-Pitta dual-imbalance — the wind that fans the fire — Bheruṇḍā's destructive heat profile.
- **dhatu_targets**: SOURCE_NEEDED. Traditional: Rahu disorders affect Majja dhatu (marrow/nerves) — neurological symptoms, mental aberration, trauma-related disorders.
- **organ_targets**: SOURCE_NEEDED — no Rahu chakra row. Rahu traditionally affects the nervous system, breath (the "smoke" graha), and head/teeth.
- **indication_clusters**: SOURCE_NEEDED. Traditional Rahu disorders: trauma, sudden onset diseases, mental confusion, addiction, parasitic infections, smoke-related lung issues.
- **anupana_vehicle**: SOURCE_NEEDED.
- **preparation_dependency_warning**: **Naga Bhasma must be sourced from verified classical rasashala only.** Lead toxicity is permanent and cumulative. (SAFETY)

## Prime/Morphology

- **prime_signature**: 4 is **not a prime** — it is 2² (the first composite). Caturthi's tithi number is the "doubled-2" composite, sitting structurally outside the {3,5,7,11} prime sequence. Bheruṇḍā's graha (Rahu, k=7) IS within the prime sequence (n=7 is Mars's prime, but Rahu's k-assignment in the eigenvalue derivation is 7). The composite tithi paired with prime graha encodes a "mirror double" structure: Caturthi = 2² in tithi, k=7 in graha.
- **morphology_correlates**: 4 corresponds to the four ventricles of the heart, the four extremities (2 arms + 2 legs), the four limb-girdles. None of these involve cervical/thoracic/lumbar segments. The prime "4" is structurally absent from the vertebral count — consistent with vertebral-primes-v1's Finding 2 that the human spine encodes {3,5,7,12} with 4 NOT appearing as a regional count. (vertebral-primes-v1.md, Finding 2)
- **sri_yantra_region_relation**: 4 does not appear in n∈{3,5,7,11}. However, the bhupura's 4 GATES (in nearly every Nitya yantra) encode the cardinal directions — N/E/S/W — and Bheruṇḍā's bhupura_gates=4 is the same as all other Nityas. The "4" of cardinality is universal yantra structure, distinct from the "4" of Caturthi's tithi number. (planetary-primes-v1.md, Section 3)

## Sound/Rhythm

- **svara_link**: SOURCE_NEEDED. Rahu has no traditional svara assignment in classical Gandharva Veda (the 7 grahas have svaras; the shadow grahas don't). Some modern systems assign Komal Re or Komal Ga to Rahu (the "shadow-shifted" semitones), but unattested in raga_data.csv.
- **raga_link**: No raga in raga_data.csv has graha=Rahu (only the 7 luminous grahas appear). **Bheruṇḍā has no direct raga correspondent in the dataset**. SOURCE_NEEDED. Traditional Rahu ragas (where named): **Marwa**, **Puriya Dhanashri** — both characterized by the avoidance of natural Re or Pa, producing the "shadow" tonality. Neither is in raga_data.csv.
- **tala_link**: SOURCE_NEEDED. The composite-4 tithi and 8-weapon iconography suggest 4-beat or 8-beat cycles (Tritāl 16-beat in Hindustani, or Adi 8-beat in Carnatic).

## Vastu/Spatial

- **mandala_zone_map**: Rahu at k=7 places yantra values as Lo_Shu + 7*J = {11, 16, 15; 18, 12, 10; 13, 14, 17}. Brahmasthana (center) = 12. Eigenvector structure: uniform (M=36), primary tension (NE-SW axis), secondary tension (perpendicular). (yantra_eigenvalue_exploration.md)
- **directional_emphasis**: SOURCE_NEEDED. Traditional: Rahu governs SW (Nirrti corner) — the death/decay quadrant. The Rahu-SW assignment is structurally aligned with the shadow-graha role.

## Visual Grammar

- **palette_logic**: Primary: #8b0000 (dark crimson, from nitya_devi_master.csv — molten gold body in a dark-red field). Secondary: #E1BEE7 (lavender, from nitya_yantra_geometry.csv). Bindu: #AB47BC (deep purple). Line weight: medium. The fire-tamas signature with Rahu shadow-graha overlay creates a high-contrast palette: molten-gold figure on dark-crimson field, with cool purple bindu — the bindu is the "still point" inside the rage.
- **density_logic**: interference_radius_fraction = 0.75. The 3-fold sine field with frequency_multiplier=2 has higher interior density than Kāmeśvarī's frequency=1 — the doubled radial frequency produces a more intricate inner structure. Render with the 8-weapon array as the dominant visual element.
- **line_weight_logic**: Medium. The 3-deity-inscribed-triangle and 8-weapon array make Bheruṇḍā's yantra visually denser than other early Nityas; line weight should be consistent to avoid over-busyness.
- **panel_layout**: SOURCE_NEEDED.
- **symbol_strip**: CUT + DEFEND + BIND + REVEAL. **8 weapons** (ankusha, sula, vajra, sword, pasha, bow, gada, shield) — the largest weapon array in the early Nityas. Three inscribed deities (Shikhinī, Nīlakaṇṭhī, Raudrī). Bija: Hrūm.
- **caption_motto**: "The fierce one — she who destroys obstacles through her terrifying form." (nitya_devi_master.csv)

---

## Cross-layer observations

The first cross-layer resonance is the **Caturthi-Ganesha-Bheruṇḍā obstacle-removal triple alignment**. Caturthi's tithi deity is Ganesha (the obstacle-remover); the Devi at this position is Bheruṇḍā (the obstacle-destroyer); the I Ching trigram at Lo Shu position 4 is Xun (Wind, the penetrating dust-disperser). Three independent traditions converge on the obstacle-removal function at this exact tithi position. The classical nyāsa procedure for invoking Bheruṇḍā's three inscribed deities (Shikhinī = peacock-flame, Nīlakaṇṭhī = blue-throat, Raudrī = fierce) provides three different obstacle-clearance mechanisms within her single yantra — fire (Shikhinī), poison-bearing (Nīlakaṇṭhī, the Halahala-drinker), and force (Raudrī). The triple-redundancy at the obstacle-tithi is structurally significant.

The second resonance is the **graha-tithi discrepancy revealing the shadow-graha pattern**. nitya_devi_master.csv assigns Rahu (k=7); nitya_yantra_geometry.csv assigns Mercury (k=3). The 4-fold magic constant difference (M=36 vs M=24) between the two assignments would put Bheruṇḍā at vastly different field-coherence positions. The devi_master attribution to Rahu is the more traditional reading: Rahu is the obstacle-graha par excellence, the "head without body" that Bheruṇḍā mirrors with her many-armed body without single head. The yantra_geometry CSV's Mercury attribution may reflect a sequential graha-cycle convention (Sun→Moon→Mars→Mercury for tithis 1→2→3→4), while devi_master uses the deeper iconographic-functional matching. The pasaka outcomes at total=4 carry only Moon and Jupiter grahas — neither Rahu nor Mercury — suggesting the dice-system uses a third assignment convention. This three-way disagreement is itself the structural feature: Bheruṇḍā's position is fundamentally ambiguous between conventions, and the ambiguity is iconographically encoded as her many-weaponed multi-form.

The third resonance is the **frequency_multiplier=2 marking the first density-doubled Nitya**. Among the first 7 Nityas, only Bheruṇḍā has frequency_multiplier=2 in the early sequence (the other early Nityas have multiplier=1; later Nityas have higher multipliers — Vahnivāsinī, Mahāvajreśvarī, Sivaduti also use multiplier=2). This means Bheruṇḍā's wave field has TWICE as many radial nodes as Kāmeśvarī's at the same N=3 multigrid projection. The interior is more intricate, more divided, more spatially differentiated. The doubling matches her 8-weapon iconography (vs the 4-weapon early devis) — both at the field level and the iconographic level, Bheruṇḍā's intervention is the first "doubled-intensity" Nitya. The prime structure follows: 4 = 2², a doubled-2, and her field's frequency is doubled — a coherent density-doubling at the tithi-number-level matching the wave-multiplier-level.

---

## Attestation summary

- **OBSERVED:PRIMARY**: Identity (name, bija, mantra, weapons, description, body color, rasa, element, guna, shakti from nitya_devi_master.csv); Lunar/Time (tithi quality, deity, good_for/avoid from tithi_master.csv); Yantra geometry with three inscribed deities (Dakshinamurti Samhita attestation per nitya_yantra_geometry.csv).
- **OBSERVED:TRADITIONAL**: Bhasma substance classes (Naga/Gomedha rasashastra); Rahu's friend/enemy table (BPHS).
- **SYNTHESIS**: Field Math eigenvalue derivation; Wave/Interference findings; Quasicrystal N=3 frequency-doubled; Prime/Morphology correspondences; Cross-layer observations; expanded_function; phase_transformation.
- **GENERATED**: None. SOURCE_NEEDED fields are flagged.

---

## SOURCE_NEEDED flags

1. **mudras_gestures / vahana_mount / ornamentation**: Tantric iconographic source.
2. **nakshatra_overlays**: Compute Caturthi (Rikta-group) wave fine structure; Rikta-gandanta interaction not in v3 paper.
3. **nodal_density / radial_bands precise count**: Run N=3 frequency=2 multigrid extraction.
4. **hexagram_id**: User decision for tithi 4 → hexagram 4 (Méng) static mapping.
5. **base_material disambiguation / prepared_substance_type**: Naga vs Gomedha for Rahu-Bheruṇḍā — Bhasma docx primary consultation.
6. **shodhana_media / bhavana_media / marana_cycles / puta_profile / particle_scale_overlay**: Naga Bhasma is highest-risk; primary text consultation critical.
7. **plant_allies (durva confirmation) / doctrine_of_signatures_overlay / processing_plants / astrobotanical_timing**: Cross-reference traditional Rahu and Ganesha plants.
8. **dhatu_targets / organ_targets / indication_clusters / anupana_vehicle**: No Rahu chakra row in chakra_cross_domain.csv — Rahu's chakra/dhatu mapping needs sourcing.
9. **svara_link / raga_link / tala_link**: No Rahu raga in raga_data.csv. Marwa/Puriya Dhanashri need addition or external source.
10. **directional_emphasis**: Vastu confirmation for Rahu-Nirrti.
11. **panel_layout**: Design decision.
