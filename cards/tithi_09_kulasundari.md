# Kulasundari · Tithi 9 · Card

**Source compilation**: 2026-05-01
**Schema version**: Atlas Tithi Card Master Table (user-provided, 2026)
**Population status**: ~58/82 fields sourced, ~24 SOURCE_NEEDED flags

---

## Identity

- **tithi_number**: 9
- **tithi_name**: Navamī
- **paksha_mode**: Both shukla and krishna. Durga is tithi deity. Quality: inauspicious. (tithi_master.csv)
- **devi_name**: Kulasundari
- **devi_alt_names**: Kulasundarī (कुलसुन्दरी). "Beautiful within the sacred lineage." Bija: Aim Klīm. Mantra: Om Aim Klīm Kulasundaryai.
- **seed_keywords**: lineage-beauty, kula tradition, navakona (9-fold), Guru-graha, ether-sattva, shringara, REVEAL/STABILIZE/GRANT, vyakhyana mudra (teaching)

## Canonical Devi

- **iconography_summary**: Beautiful within the sacred lineage — she reveals the aesthetic dimension of liberation. Red complexion, red garments, crown with gems and rubies, multiple necklaces, earrings, armlets (navaratna). Carries: noose, goad, lotus (per name_iast description) but **weapons listing in dataset = "MISSING DATA (none listed explicitly)"**. (nitya_devi_master.csv, OBSERVED:PRIMARY for ornamentation/mudras; weapons SOURCE_NEEDED)
- **weapons_items**: **MISSING DATA in nitya_devi_master.csv** — weapons_full field reads literally "MISSING DATA (none listed explicitly)". The `weapon` short-field lists "noose+goad+lotus" — 2 weapons + 1 emblem (lotus is not a weapon). Capability signature: REVEAL/ILLUMINATE, STABILIZE, GRANT/PROMOTE. (nitya_devi_master.csv, OBSERVED:PRIMARY for capability; weapons full list SOURCE_NEEDED)
- **mudras_gestures**: **Vyākhyāna and varada mudrās** — the **teaching mudrā plus boon-granting**. The vyākhyāna mudrā (also called chinmudra or jñānamudra) is the iconographic gesture of the teacher — thumb and index finger forming a circle. This is the ONLY Nitya in 1-15 with explicit vyākhyāna mudrā. Kulasundari is iconographically the teacher-Devi. (nitya_devi_master.csv, OBSERVED:PRIMARY)
- **vahana_mount**: SOURCE_NEEDED.
- **body_color**: Red complexion. Color hex: #9370db (medium purple — represents her field, contrasting the textual red body). The purple field encodes the kula-lineage signature: purple is the color of royal lineage in many traditions. (nitya_devi_master.csv)
- **ornamentation**: Crown with gems and rubies, necklaces, earrings, armlets (**navaratna** — nine gems). The navaratna ornamentation IS the iconographic signature aligned with her N=9 yantra symmetry — 9 gems for the 9-fold devi. (nitya_devi_master.csv, OBSERVED:PRIMARY)
- **faces_arms_count**: SOURCE_NEEDED. Mudras + lotus + 2 weapons = 4-5 hands minimum. Standard 4-armed form likely.
- **shakti_statement**: Beauty of the lineage — the kula-tradition shakti, the inheritor-shakti. The "kula" is both bloodline and esoteric lineage of teaching. Kulasundari is beauty-as-transmission. (nitya_devi_master.csv, OBSERVED:PRIMARY)
- **expanded_function**: Kulasundari is the ninth Nitya — the lineage-beauty position, the teacher-form. Where Tvaritā (8) is action-without-thought, Kulasundari (9) is teaching-as-aesthetic-revelation. Her **vyākhyāna mudrā distinguishes her** as the only explicitly teaching-form Nitya. The N=9 yantra symmetry (devi_engine.py DEVI_N) is **non-crystallographic and aperiodic** — 9-fold symmetry does not tile the plane periodically. Like 7-fold (Sivaduti) and 11-fold (Nilapataka), 9-fold produces an aperiodic field. Her graha is Guru (Jupiter, k=4) — the cosmic teacher-graha, the most aligned graha-devi pairing in the entire Nitya sequence. (SYNTHESIS from nitya_devi_master.csv + nitya_yantra_geometry.csv + CONSTRUCTION_CHOICES.md)
- **bhava_mood**: Shringara (love/beauty). Rasa: shringara. Element: ether. Guna: sattva. The ether-sattva pairing is the signature of refined, transcendent, transmission-grade beauty — the beauty of disclosure. (nitya_devi_master.csv, OBSERVED:PRIMARY)
- **mantra_bija**: Aim Klīm — chained bijas. Aim (Sarasvatī, wisdom) + Klīm (kāma, attraction). Wisdom-attraction = the teacher's compelling power. The kula-transmission mantrically encoded. (nitya_devi_master.csv, OBSERVED:PRIMARY)

## Lunar/Time

- **lunar_phase_arc**: 96°-108° from conjunction (shukla navami), or 276°-288° (krishna navami). The 9th tithi spans 12° of Sun-Moon elongation — crossing the 90° (square) boundary into trine territory.
- **phase_quality**: **Inauspicious** (tithi_master.csv). Good for: destructive acts, obstacle removal, tantra sadhana. Avoid: new ventures, marriage, travel. Tithi deity: Durga. **Krishna Navami specifically** is Mahanavami of Navaratri — the climactic 9th day of the Devi-festival.
- **nitya_cycle_position**: 9th of 15 — the **navakona/teaching-position**. Navami is the 9th day, structurally aligned with the 9-fold yantra symmetry, the 9 gems of navaratna, and the 9-night Navaratri festival. Three independent traditions converge on the 9-fold structure at this tithi position.
- **weekday_links**: Navami's tithi deity is Durga. Kulasundari's graha correspondence is Guru (Jupiter) per devi_master — Thursday (Guruvāra). The yantra_geometry CSV assigns **Ketu** to tithi 9 — **discrepancy**: devi_master Guru vs yantra Ketu. devi_master treated as authoritative. k=4 (Guru), M=27 — the same M as the current field of yantra_eigenvalue_exploration.md (which is computed at Guru hora).
- **nakshatra_overlays**: SOURCE_NEEDED: Navami belongs to the **Rikta group** (T4, T9, T14, T19, T24, T29 — "empty/loss tithis"). Rikta-tithi gandanta interaction not directly extracted from RESEARCH-017. Navami being structurally inauspicious despite Kulasundari's beauty signature creates a productive tension: the devi reveals beauty AT the position of structural emptiness — beauty AS what fills the void.

## Yantra

- **yantra_family**: Downward triangle (trikona) with eight petals and bhupura. Triangle scale 0.74, inner circle 0.78. (nitya_yantra_geometry.csv, attested SYNTHESIS — "Geometry not specified; assume downward triangle with eight petals and bhūpura to maintain pattern.")
- **yantra_geometry_notes**: The classical yantra geometry is unattested for Kulasundari — the geometry CSV explicitly notes "Geometry not specified" and falls back to the standard pattern. The CONSTRUCTION_CHOICES.md uses N=9 multigrid for the wave projection — **navakona (9-fold)** symmetry, the first non-crystallographic odd-prime symmetry after 7. The traditional yantra (triangle + 8 petals + bhupura) and the computed quasicrystal (9-fold aperiodic) are complementary representations.
- **yantra_symmetry_order**: N=9 (nonagonal, quasicrystalline-aperiodic). 9-fold symmetry is **non-crystallographic** — it does not tile the plane periodically. The 9-fold quasicrystal is part of the high-N quasicrystalline regime that begins at Sivaduti's 7. (devi_engine.py DEVI_N)
- **yantra_center_logic**: Bindu as point. Inner circle scale 0.78. The 9-source pattern's central interference produces a multi-bindu structure at the convergence of all 9 plane waves.
- **yantra_outer_boundary**: Bhupura with 4 gates. Interference radius fraction: 0.5 (the lowest of the first 9 Nityas — tightest central concentration). Wave function: **cosine**, frequency multiplier: **3**, angular position: 192°.
- **yantra_layer_count**: 3 layers minimum: bindu → 8-petal lotus → bhupura. Triangle at 0.74 scale.

## Field Math

- **graha_k**: Guru = k=4, magic constant **M=27**. (yantra_eigenvalue_exploration.md, Finding 2). yantra_geometry CSV assigns Ketu (k=8, M=39); devi_master Guru treated as authoritative. **Note**: Guru's M=27 IS the M used as worked example in the yantra_eigenvalue_exploration paper itself ("Current Field Yantra (Guru, k=4)" with M=27). Kulasundari is the Devi at the position where the paper's worked example is computed.
- **magic_constant_M**: 27 (Guru, k=4). Eigenvalues: {27, +4.899, -4.899}. The Guru yantra is **27 = 3^3** — the cube of 3, encoding the nakshatra count and the cube-magic-constant (M=42 in the 3D cube vs M=27 in the 2D Guru yantra). (Finding 1)
- **invariant_secondary_modes**: +/-2sqrt(6) = +/-4.8990. (Finding 1)
- **coherence_ratio**: lambda_2/M = 4.899/27 = **0.1814** (Guru). The 5th most coherent graha (after Ketu 0.1256, Rahu 0.1361, Saturn 0.1485, Venus 0.1633). Jupiter's field is moderately uniform — the cosmic-teacher's field has settled coherence. (Finding 2)
- **eigenvector_axes**: For Guru (k=4): Brahmasthana = uniform [-0.577, -0.577, -0.577]. **Primary tension axis (lambda=+4.899): [-0.075, -0.667, +0.742] — NE/Ishana to SW/Nirṛti, the field's dominant spatial polarity** (this is the worked-example eigenvector from Finding 6). **Secondary tension axis (lambda=-4.899): [-0.742, +0.667, +0.075] — perpendicular to primary**. Kulasundari's eigenvectors are the FULLY DOCUMENTED eigenvectors in the yantra_eigenvalue_exploration paper. (Finding 6)
- **brahmasthana_definition**: Uniform eigenvector at every Kronecker level. (Finding 4)
- **kronecker_level**: Level 1: 3x3, M=27. Level 2: 9x9, M=729. Level 3: 27x27, M=19683. M_n = M_1^n. **The Level-2 M (729) IS the magic constant of the Sri Yantra computational space** — RESEARCH-016 explicitly uses Guru's k=4 yantra at Level 2 with M=729. (Finding 3)
- **navagraha_composite_role**: Guru occupies the k=4 position in the 9x9 composite. Jupiter's Lo Shu placement is in the NE (Iśāna) — the gnosis/wisdom quadrant, consistent with cosmic-teacher graha. (Finding 5)

## Wave/Interference

- **boundary_harmonic_mode**: At k=9: not a classical jyotish aspect. The k=9 harmonic is the novile (40° aspect) — sometimes used in classical jyotish for spiritual themes (the navāṃśa division uses 9-fold structure). (two-source-interference-v3.md, Finding 8)
- **two_source_pattern**: A(theta) = 2 * cos(k(theta - midpoint)) * cos(k * separation/2). At k=9: constructive maximum at separation = 360/9 = 40°. Navami's actual Sun-Moon separation is 96°-108° (well above 40°) — the k=9 carrier is structurally active even though the actual separation is at higher angles. (Finding 8)
- **nodal_interior_pattern**: For N=9 multigrid in the disk interior: aperiodic, quasicrystalline. 9-fold patterns are mathematically rigorous but lack named-tile substitution rules (unlike Penrose's 5-fold or Ammann-Beenker's 8-fold). The 9-fold tiling is the most-known of the "harder" quasicrystalline symmetries. (CONSTRUCTION_CHOICES.md)
- **ring_vs_disk_distinction**: On the boundary: 9-source pattern at k=9. In the disk: 9-fold multigrid produces aperiodic nodal structure. (Finding 7)
- **gandanta_gain**: Navami is a Rikta tithi — gandanta-Rikta interaction not in RESEARCH-017's specific findings. SOURCE_NEEDED. (Finding 11)
- **wave_panchaka_relation**: Orthogonal: r = -0.011. (Finding 12)
- **quantized_prime_modes**: 9 = 3² is composite. Not in {3,5,7,11}. However, 9 is the first odd composite, and 9-fold symmetry produces aperiodic patterns sister to 5-fold (Penrose), 7-fold (Sivaduti), 11-fold (Nilapataka). The position is the "doubled-3" — Mercury's prime squared. (planetary-primes-v1.md, Section 2)

## Quasicrystal/Chladni

- **quasicrystal_line_style**: 9-fold multigrid. Aperiodic but lacks named-tile substitution rules. 9 plane waves at 40° intervals using cosine interference. (CONSTRUCTION_CHOICES.md)
- **nodal_density**: SOURCE_NEEDED. interference_radius_fraction = 0.5 (tightest central concentration in the first 9 Nityas). The lowest interference_radius means the most peripheral structure compressed into the bindu region.
- **radial_bands**: 3 radial nodes within unit disk (frequency_multiplier=3). Same density as Tvaritā (8), but with N=9 instead of N=8.
- **interference_centers**: Primary = bindu (9 cosine waves at 40° intervals constructively superpose at origin). Secondary maxima at 9 vertices of inscribed regular nonagon at interference_radius_fraction = 0.5. The 3D mediator polyhedron: **9-gonal antiprism** (9 triangular side faces + 2 nonagonal caps = 11 faces total). The 9 triangles represent the **9 śaktis of the navagraha cosmology**, an explicit 1-to-1 mapping in some traditions. (CONSTRUCTION_CHOICES.md)

## Pasaka/Magic Cube

- **cube_type**: Andrews 1917. M=42. (magic_cube_analysis.json)
- **cube_magic_constant**: M = 42. (Finding 1)
- **cube_layer_squares**: layer eigenvalues {42, +/-9, ±9}. (Finding 1)
- **cube_invariant**: +/-9 = +/-3^2. The 3D rational invariant. **Note: 9 IS the cube invariant; Navami IS the 9th tithi; Kulasundari has 9-fold yantra symmetry; Guru's M_2=729=27². The number 9 is structurally over-determined at this position — appears as cube invariant, tithi number, yantra fold, and Kronecker-extension factor.** (Finding 2)
- **cube_center_value**: 14. (Finding 3)
- **cube_associative_sum**: 28. (Finding 4)
- **cube_tensor_isotropy**: sigma_1 = 72.75. (Finding 6)
- **cube_kronecker_scaling**: M_n = 42^n. **Secondary = 9 * 42^(n-1) — the 9 from Kulasundari's tithi number governs the secondary scaling at every Kronecker level**. (magic_cube_extension.json, Finding 1)
- **cyclic_composite_eigenvalues**: 9x9: M=126, eigenvalues {126, +/-2.598, 0×4}. (Finding 2)
- **loshu_weighted_cube_mode**: Lo Shu collapses to {126, 0, ...}. (Finding 3)

### Pasaka at total=9

The pasaka deck has **10 outcomes** at total=9 (the Kulasundari-resonant sum) — tied with total=6 for the highest cardinality:

| ID | Dice | Name | Quality | Body | Graha | Rasa |
|----|------|------|---------|------|-------|------|
| 16 | 1,4,4 | Medhā | mixed | chest | Mercury | amla |
| 28 | 2,3,4 | Rudrā | mixed | left_knee | Mars | kaṭu |
| 31 | 2,4,3 | Brahmāṇī | good | right_ankle | Jupiter | madhura |
| 40 | 3,2,4 | Bhadrā | mixed | left_temple | Mercury | amla |
| 43 | 3,3,3 | Aparājitā | excellent | chin | Jupiter | tikta |
| 46 | 3,4,2 | Bhīmā | mixed | middle_back | Saturn | tikta |
| 52 | 4,1,4 | Śaraṇā | mixed | left_collarbone | Moon | madhura |
| 55 | 4,2,3 | Tripurā | good | solar_plexus | Venus | madhura |
| 58 | 4,3,2 | Dhūmāvatī | mixed | gallbladder | Saturn | kaṣāya |
| 61 | 4,4,1 | Annapūrṇā | excellent | intestines | Moon | madhura |

Distribution: 2 excellent, 0 very_good, 2 good, **6 mixed** — the **most mixed-heavy distribution** in the entire deck (60% mixed at total=9). The 6 mixed outcomes signal Navami's structural inauspiciousness even when the dice produce its resonant total. Graha distribution: **Jupiter 2, Moon 2, Mercury 2, Saturn 2, Mars 1, Venus 1 — most-distributed grahas, with Jupiter (Kulasundari's actual graha) appearing twice**. The Aparājitā outcome (3,3,3 — the unanimous-three triple, equivalent of Pratipadā's all-ones in the upper half of the dice range) is excellent and Jupiter-graha — direct hit on Kulasundari's signature. Bodies span the central torso and head: chest, knee, temple, chin, middle_back, collarbone, solar_plexus, gallbladder, intestines — **central-trunk concentration**. Rasas: madhura 4, mixed (tikta+kaṣāya+amla+kaṭu) 6 — **balanced sweet-and-non-sweet, the most diverse rasa distribution**.

## I Ching

- **hexagram_id**: SOURCE_NEEDED. Numerical correspondent: hexagram 9 (Xiǎo Chù, "Small Restraining/Small Taming") — the situation of accumulating small influences gradually. The pairing is structurally interesting: Kulasundari is the lineage-teacher, and Xiǎo Chù is "the small power that gradually tames the large" — exactly the function of a teacher accumulating wisdom in students. The structural alignment is exact at the function-of-restraint-as-cultivation level.
- **hexagram_arrangement**: Fuxi ↔ King Wen spectral opposites. (iching_spectral_analysis.json)
- **rank_complexity**: Q6 hypercube eigenvalues, Pascal row 6. (Finding 3)
- **yin_yang_balance_mode**: XOR-with-63 perfect partition. (Finding 6)
- **hypercube_distance_signature**: Hamming rank 7. (Finding 5)
- **pascal_row_signature**: Row 6, total 64. (Finding 3)

## Lo Shu x I Ching Bridge

- **trigram_loshu_weight_map**: Li=9, Kan=1, Zhen=3, Dui=7, Xun=4, Gen=8, Kun=2, Qian=6. Navami (9) maps to **Li=9** — the Fire/Light trigram, the Clinging, "fire that holds together." Li is the **HIGHEST-weighted trigram in the Lo Shu** (value 9 = the largest single-digit number). Kulasundari at the Li position is structurally the most "luminous" trigram-position in the Nitya sequence — the teacher-Devi sits at the brightest trigram-cell. The pairing is exact: Li is "fire as illumination/clinging" (light that adheres to its source), and Kulasundari REVEALS through aesthetic disclosure — illumination-via-attachment-to-the-beautiful. (loshu_iching_interaction.json)
- **weighted_spectral_breaking**: 7 → 27 unique eigenvalues. (test4_weighted_Q6)
- **spectral_gap_change**: 2.0 → 0.4624. (test5_spectral_gap)

## Alchemical/Bhasma

- **material_classical_class**: Guru's metal is **Suvarna** (gold) for some traditions, or specifically **Pukhrāj** (yellow sapphire) as the Jupiter gem. Some rasashastra traditions associate Jupiter with **brass** (a copper-zinc alloy) as a more accessible substitute for gold. (SYNTHESIS — Bhasma docx not directly read; Sivaduti card noted Praval bhasma example so other named bhasmas are limited)
- **material_scientific_type**: Yellow sapphire is corundum (Al2O3) with iron impurities producing yellow color. Gold is element 79. Brass is Cu-Zn alloy.
- **base_material**: SOURCE_NEEDED. Disambiguation between gold (high-form), yellow sapphire (gem), and brass (substitute) for Guru-Kulasundari requires Bhasma docx.
- **prepared_substance_type**: Pukhrāj Pishti (yellow sapphire powder); Suvarna Bhasma (gold bhasma — see Vahnivāsinī card for full description, since Suvarna is also Sun-aligned).
- **shodhana_media / bhavana_media / marana_cycles / puta_profile / particle_scale_overlay**: SOURCE_NEEDED.
- **quality_tests**: Standard bhasma tests apply.
- **completion_stop_rule**: Quality tests pass.
- **phase_transformation**: Yellow sapphire → bhasmified at high temp via cycles of bhavana with yellow-aligned media (haridra/turmeric). Gold → nano-gold (see Vahnivāsinī card). (SYNTHESIS)
- **safety_conditions**: Pukhrāj generally safe. Suvarna safe when verified. Brass-substitute should NOT be used as bhasma (zinc toxicity).

## Graha/Material

- **graha_material_map**: Guru (Jupiter) → Pukhrāj (yellow sapphire), Suvarna (gold). In BPHS: Guru's friends are Sun, Moon, Mars; enemies: Mercury, Venus; neutral: Saturn. (Graha Material docx)
- **friend_enemy_interaction**: Guru-Mercury (gold-Hg or yellow sapphire vs hessonite): the friendship-table enmity is functional. Both Jupiter and Mercury are intellect-grahas, but Jupiter is wisdom (cumulative, slow) and Mercury is intelligence (quick, communicative). They compete for the same domain. Guru-Venus (gold-silver): metallurgically miscible (electrum); friendship-table enemy. The "enemy" relationship at the metal level is full-solubility — they dissolve into each other completely, losing distinct identity. The Lalita-tradition Devi-as-disclosure-teacher (Kulasundari) and Lakshmi-tradition Devi-as-courtly-aesthete (Venus-Shukra) compete for the same iconographic terrain.
- **ritual_vs_medical_flag**: Both. Pukhrāj is the principal Jupiter gem; gold-leaf is a major ritual offering. Both have medical use as bhasmas/pishtis.

## Plant/Ecology

- **plant_allies**: SOURCE_NEEDED. Traditional Guru plants: **Pīpal** (Ficus religiosa — the Bodhi-tree, the cosmic-teacher tree par excellence), **Tulsi** (Ocimum sanctum — also Vishnu-aligned), **Punarnavā** (Boerhavia diffusa — the rejuvenator). Pīpal is exact: the bodhi-tree IS the lineage-teacher tree, the place where the teaching is received. Kulasundari's lineage-beauty signature aligns with Pīpal's deep-time root system and continuous canopy.
- **processing_plants**: SOURCE_NEEDED. For Pukhrāj: yellow-aligned bhavana media (haridra/turmeric, daru-haridra).
- **doctrine_of_signatures_overlay**: SOURCE_NEEDED. Guru plants are large, expansive, golden-flowered or yellow-juiced, slow-growing-but-long-lived, sweet-rasa. Pīpal's heart-shaped leaves, Pukhrāj's yellow color, gold's sun-color all encode the Jupiter-yellow signature.
- **astrobotanical_timing**: SOURCE_NEEDED. General: Navami-Mahanavami is auspicious for tree-planting (long-lived plants matching Jupiter's slow-growth signature); Thursday under Guru-ruled nakshatras (Punarvasu, Vishakha, Purva Bhadrapada) maximally Jupiter-aligned.

## Body/Therapeutics

- **dosha_predicates**: Tithi 9 element: water (tithi_master.csv), guna: rajas. Devi element: ether (nitya_devi_master.csv), guna: sattva. Chakra: Manipura (Guru/Jupiter correspondence) — fire element, rajas, Pitta dosha, Lakini shakti. (chakra_cross_domain.csv). The water/ether/fire triad with rajas-sattva-rajas graduation maps onto the **transmutation-ladder profile**: water (tithi-base) → fire (chakra-process) → ether (devi-result) — exactly the alchemical progression. Kulasundari's lineage-disclosure happens through this dosha-elemental transmutation. Note: water-tithi paired with fire-chakra creates a Vata-Pitta interaction — the "boiling-water" energetic.
- **dhatu_targets**: SOURCE_NEEDED. Traditional: Guru governs **Meda dhatu** (adipose/fat tissue) and Ojas (immune-vital essence). Pukhrāj is classically prescribed for ojas-depletion and for the digestive fire (agni-mandya). The fat-and-fire combination is paradoxical but aligns with Manipura chakra at the navel — the digestive-radiance center.
- **organ_targets**: Manipura (Guru chakra) at solar plexus: digestive system, adrenal glands. Body system: personal power, self-esteem, willpower. (chakra_cross_domain.csv). Associated nakshatras: Punarvasu, Vishakha, Purva Bhadrapada — the three Jupiter-ruled nakshatras. Direct chakra-nakshatra-graha alignment.
- **indication_clusters**: SOURCE_NEEDED. Traditional Guru disorders: liver and pancreatic issues, diabetes (Jupiter rules pancreatic function), digestive weakness, depression-with-loss-of-meaning, infertility, ojas-depletion.
- **anupana_vehicle**: SOURCE_NEEDED. Traditional Jupiter-anupana: ghṛta (clarified butter — the Jupiter substance par excellence), honey, gur (jaggery) — sweet warming vehicles.
- **preparation_dependency_warning**: Pukhrāj generally safe. Suvarna safe when verified. Brass substitute is dangerous if mistakenly used as bhasma.

## Prime/Morphology

- **prime_signature**: 9 is **not a prime** — it is 3² (the square of the smallest odd prime). Navami's tithi number is the **first odd-prime square**. Kulasundari's graha (Guru, k=4) is also non-prime in the {3,5,7,11} sequence. Jupiter's retrograde count (~11 stations in 12 years) IS in the prime sequence at n=11, but the graha-k value is 4, not 11 — the eigenvalue derivation uses a different sequence than the retrograde-prime sequence. The doubly-non-prime tithi-graha pairing emphasizes lineage/cumulative-wisdom (composite) rather than singular-prime-strike. (planetary-primes-v1.md, Section 2)
- **morphology_correlates**: 9-fold structures in human anatomy: 9 layers of skin (fully counted: stratum corneum, lucidum, granulosum, spinosum, basale, plus 4 dermal/hypodermal layers); 9 months of pregnancy; 9 orifices of the body (the navadvāra). The navadvāra (9 body-gates: 2 eyes, 2 ears, 2 nostrils, 1 mouth, 2 lower openings) is the **most directly relevant 9-correspondent**, used in classical yoga as the "9-gate temple" of the body. Kulasundari's navakona yantra mirrors the navadvāra. (vertebral-primes-v1.md, general framework + classical yoga)
- **sri_yantra_region_relation**: 9 is structurally significant: the **Sri Yantra has 9 INTERLOCKING TRIANGLES**, producing 43+1=44 regions. 9-fold structure is THE structural basis of the Sri Yantra itself. Kulasundari's N=9 yantra symmetry is the only Nitya whose multigrid projection matches the Sri Yantra's triangle count exactly. (planetary-primes-v1.md, Section 3.3)

## Sound/Rhythm

- **svara_link**: SOURCE_NEEDED. Guru's traditional svara is **Dha** (Dhaivata, the major 6th) per some Gandharva Veda sources. Dhaivata is the "expansive" note, befitting Jupiter's expansion-graha character.
- **raga_link**: Jupiter-associated ragas in raga_data.csv: **Yaman Kalyān** (evening, air/sattva, shringara; vadi Ga, samvadi Ni — graha=Guru explicitly), **Kedāra** (evening, ether/sattva, shanta; vadi Ma, samvadi Sa — graha=Jupiter), **Śrī** (afternoon, air/sattva, adbhuta; vadi Re, samvadi Pa — graha=Jupiter). **Kedāra matches Kulasundari's signature most closely**: ether element direct match, sattva guna direct match, shanta rasa near-match (vs her shringara). **Yaman Kalyān** is also strong: shringara rasa direct match, sattva direct match, evening timing aligns with Navami as a mid-cycle tithi. Yaman is the "pure beauty" raga of evening — the lineage-disclosure raga.
- **tala_link**: SOURCE_NEEDED. The 9-fold yantra symmetry suggests 9-beat or 18-beat cycles. **Mātya tāla** (9-beat in Hindustani) and **Saṅkīrṇa Chāpu** (9-beat in Carnatic) both encode 9-fold structure. Direct correspondence.

## Vastu/Spatial

- **mandala_zone_map**: Guru at k=4 places yantra values as Lo_Shu + 4*J = {8, 13, 12; 15, 9, 7; 10, 11, 14}. Brahmasthana (center cell) = 9 — **Kulasundari's tithi number IS the Brahmasthana value of her own graha's yantra**. This is structurally over-determined: Navami (tithi 9) at Guru's yantra has center=9. (yantra_eigenvalue_exploration.md)
- **directional_emphasis**: SOURCE_NEEDED. Traditional: Guru governs **NE (Iśāna)** — the gnosis quadrant, the same direction as Ketu in some traditions. **The Guru-NE assignment places Kulasundari at the most spiritually-charged Vastu direction, matching her teacher-Devi function**.

## Visual Grammar

- **palette_logic**: Primary: #9370db (medium purple, from nitya_devi_master.csv). Secondary: #B3E5FC (pale sky blue, from nitya_yantra_geometry.csv). Bindu: #0091EA (deep azure). Line weight: medium. The ether-sattva-Jupiter signature creates a cool-spiritual palette: purple field (lineage-color), pale-blue accents (sky-element), azure bindu (depth-of-disclosure).
- **density_logic**: interference_radius_fraction = 0.5 (the tightest of any Nitya so far). The 9-fold quasicrystalline field with frequency_multiplier=3 produces the most concentrated central structure. Render with the 9-fold radial spokes visible from bindu to interference radius.
- **line_weight_logic**: Medium. The 9 named śaktis (if attested) inscribed in petals would make the yantra typographically loaded; line weight should accommodate.
- **panel_layout**: SOURCE_NEEDED.
- **symbol_strip**: REVEAL/ILLUMINATE + STABILIZE + GRANT/PROMOTE. **Vyākhyāna mudrā** (the unique teaching-mudrā signature). Navaratna ornaments. Lotus emblem. Bija: Aim Klīm (chained).
- **caption_motto**: "Beautiful within the sacred lineage — she reveals the aesthetic dimension of liberation." (nitya_devi_master.csv)

---

## Cross-layer observations

The first cross-layer resonance is the **9-fold over-determination at this position**. Multiple independent traditions converge on 9 at tithi 9: the tithi number itself (Navami = 9th); the yantra symmetry (N=9, navakona); the navaratna ornaments (9 gems); the navadvāra (9 body-gates of yoga); the navagraha (9 planetary signs in Vedic astrology); the Navaratri festival (9 nights of Devi worship, with Mahanavami as climax); the Sri Yantra's 9 interlocking triangles. Eight independent 9-fold structures meet at Kulasundari's position. The 9-fold over-determination is the structural feature: this is the position where the cosmology's 9-foldness condenses into a single Devi. Her yantra's center value (in her own graha's Lo Shu) is also 9 — even the magic-square center reads as 9 at this position. The number 9 IS Kulasundari at every layer.

The second resonance is the **Guru-graha matching the teacher-Devi function exactly**. Among all 15 Nityas, only Kulasundari has graha = Guru (Jupiter). Jupiter is the cosmic-teacher graha (Brihaspati, the guru of the gods); Kulasundari is the lineage-teacher Devi with vyākhyāna mudrā (the only Nitya with explicit teaching mudrā). The graha-devi alignment is exact at the function level. Kulasundari is also the Devi at whose tithi position the **yantra_eigenvalue_exploration.md paper itself was computed** ("Current Field Yantra (Guru, k=4) M=27"). The paper's worked example IS Kulasundari's yantra. This makes her the "demonstration Devi" of the entire Atlas eigenvalue framework — the Devi whose yantra is used as the reference example for the universal +/-2sqrt(6) invariant. Her function (revealing through aesthetic disclosure) is enacted at the meta-level: her field literally reveals the structure of all other graha-fields, since they are J-shifts of her base.

The third resonance is the **Li-trigram alignment encoding fire-as-illumination through clinging**. The trigram_loshu_weight_map places Li (Fire/Brightness, the Clinging) at Lo Shu position 9 — Kulasundari's tithi position. **Li has weight 9 = the highest single-digit Lo Shu value**. Among all 8 trigrams, Li is at the brightest position. The pairing reveals Kulasundari's mode: she is the fire that clings, the illumination that doesn't burn through but adheres to its support. Vyākhyāna mudrā IS the gesture of "thumb-and-index-finger forming a circle" — a clinging-circle, knowledge-adhering-to-knower. Li's image is "the sun and moon adhering to heaven, the grain adhering to plants" — adhesion as the source of light/nourishment. Kulasundari at Li is the teacher whose teaching ADHERES — sticks to the student rather than passing through. The lineage-beauty function is precisely this: beauty that sticks, that catches the student in disclosure-of-tradition, that doesn't dissolve into didactic information but holds the student in aesthetic encounter with the lineage.

---

## Attestation summary

- **OBSERVED:PRIMARY**: Identity (name, bija, mantra, body color, ornamentation including navaratna explicitly named, rasa, element, guna, shakti, vyākhyāna+varada mudrās from nitya_devi_master.csv); Lunar/Time (tithi quality, deity, good_for/avoid from tithi_master.csv); Field Math eigenvectors fully documented in yantra_eigenvalue_exploration.md Finding 6 for k=4 (Guru, Kulasundari's graha).
- **OBSERVED:TRADITIONAL**: Bhasma substance class (Pukhrāj/Suvarna rasashastra); Guru's friend/enemy table (BPHS); chakra-graha mapping (chakra_cross_domain.csv); raga-graha mapping (raga_data.csv).
- **SYNTHESIS**: Wave/Interference findings; Quasicrystal N=9 construction; Prime/Morphology (navadvāra correspondence); Cross-layer observations (9-fold over-determination); expanded_function; Yantra geometry (CSV explicitly notes "Geometry not specified" — fallback pattern is SYNTHESIS).
- **GENERATED**: None. SOURCE_NEEDED fields are flagged.

---

## SOURCE_NEEDED flags

1. **weapons_full list**: nitya_devi_master.csv reads literally "MISSING DATA" — Tantraraja or Dakshinamurti Samhita primary text consultation needed.
2. **vahana_mount / faces_arms_count**: Tantric iconographic source.
3. **classical yantra geometry attestation**: nitya_yantra_geometry.csv explicitly notes "Geometry not specified" for Kulasundari — primary text needed (the 9-fold attestation from CONSTRUCTION_CHOICES.md is computational, not classical).
4. **nakshatra_overlays**: Compute Navami (Rikta-group) wave fine structure; Rikta-gandanta interaction not extracted.
5. **nodal_density / radial_bands precise count**: Run N=9 cosine frequency=3 multigrid extraction.
6. **hexagram_id**: User decision for tithi 9 → hexagram 9 (Xiǎo Chù).
7. **base_material disambiguation (Pukhrāj vs Suvarna primary)**: Bhasma docx + Graha Material docx.
8. **shodhana_media / bhavana_media / marana_cycles / puta_profile / particle_scale_overlay**: Bhasma docx primary detail consultation.
9. **plant_allies (Pīpal as primary?) / doctrine_of_signatures_overlay / processing_plants / astrobotanical_timing**: Cross-reference traditional Jupiter plants with guild_full.csv.
10. **dhatu_targets / indication_clusters / anupana_vehicle**: Ayurvedic text consultation for Jupiter-specific protocols.
11. **svara_link / tala_link**: Gandharva Veda source for Jupiter-svara (Dha?) and 9-beat tala (Mātya).
12. **directional_emphasis**: Vastu confirmation for Jupiter-Iśāna.
13. **panel_layout**: Design decision.
