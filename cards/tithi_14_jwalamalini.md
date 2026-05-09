# Jvalamalini · Tithi 14 · Card

**Source compilation**: 2026-05-03
**Schema version**: Atlas Tithi Card Master Table (user-provided, 2026)
**Population status**: ~62/82 fields sourced, ~20 SOURCE_NEEDED flags

---

## Identity

- **tithi_number**: 14
- **tithi_name**: Caturdaśī
- **paksha_mode**: Both shukla and krishna. Śiva is tithi deity. Quality: inauspicious. **Krishna Caturdaśī is Maśivarātri-eve**, and the monthly Maśivarātri (mostly krishna 14) is one of the most observance-heavy tithis in Śaiva practice. (tithi_master.csv)
- **devi_name**: Jvalamalini
- **devi_alt_names**: Jvālāmālinī (ज्वालामालिनी). "Garlanded with flames." Bija: Hrīm Śrīm. Mantra: Om Hrīm Śrīm Jvālāmālinyai.
- **seed_keywords**: garland of flames, karmic burning, threshold-purification, fire-rajas, raudra, Mangala-graha, fire garland+sword, **32-petal yantra (highest petal count)**

## Canonical Devi

- **iconography_summary**: Garlanded with flames — she who burns away the residue of karma at the threshold. The flame-garland is the primary iconographic signature; she stands at the boundary (Caturdaśī = the day before the new/full moon transition) and burns what cannot cross. **Body color, garments, ornaments, mudras, vahana all empty in nitya_devi_master.csv** for Jvālāmālinī. The textual description "garlanded with flames... burns away the residue of karma at the threshold" is the primary attestation. (nitya_devi_master.csv, OBSERVED:PRIMARY for name/bija/description/weapon; many fields empty)
- **weapons_items**: Fire garland (jvālā-mālā) and sword (khaḍga) per the `weapon` short field. **Full weapons listing empty in nitya_devi_master.csv**. The fire-garland-sword pair: the garland is what she IS (fire surrounding her), the sword is what she USES (the cutting instrument that severs karmic residue). Capability signature: SOURCE_NEEDED — the field is empty.
- **mudras_gestures**: SOURCE_NEEDED.
- **vahana_mount**: SOURCE_NEEDED. The fire-warrior iconography traditionally has a tiger or lion vahana for goddess-fierce forms.
- **body_color**: SOURCE_NEEDED. Color hex: #ff8c00 (dark orange — represents the fire-garland-color directly).
- **ornamentation**: SOURCE_NEEDED.
- **faces_arms_count**: SOURCE_NEEDED. The fire-garland implies surrounding fire-form; classical iconography would suggest 4 arms with the sword in one and the garland enveloping all.
- **shakti_statement**: Garland of flames — the karma-burning shakti. She burns at the threshold; what cannot pass through her flames is precisely the karmic residue that has not been integrated. (nitya_devi_master.csv, OBSERVED:PRIMARY)
- **expanded_function**: Jvālāmālinī is the fourteenth Nitya — the **threshold-burning position**. Caturdaśī is the day before transition (Pūrṇimā shukla 15 or Amāvāsyā krishna 15). Her function is to burn what cannot cross the threshold — to purify the field before the lunation completes its bright or dark phase. The N=14 yantra symmetry (devi_engine.py DEVI_N) is 14-fold — fully quasicrystalline, structurally close to but distinct from the 13-fold (Sarvāṅgasundarī) and 15-fold (Citra) sister symmetries. 14 = 2×7; combines bilateral symmetry with Mars's prime — the bilateral-Mars pair gives the warrior-cleavage form. Her graha is Mangala (Mars, k=2, M=21) — same as Nityaklinnā (T3). The two Mars-Devis are T3 (dissolution-as-melting) and T14 (dissolution-as-burning). Same graha, water vs fire elements — Mars's two opposite material expressions. Her petal count is **32** (per nitya_yantra_geometry.csv) — the highest among the Nityā set, with classical attestation from Dakshinamurti Samhita ("one of her mandalas has 32 petals and another variant has 40 petals"). (SYNTHESIS from nitya_devi_master.csv + nitya_yantra_geometry.csv + CONSTRUCTION_CHOICES.md)
- **bhava_mood**: Raudra (fury). Rasa: raudra. Element: fire. Guna: rajas. Same fire-rajas-raudra triple as Bheruṇḍā (T4) — wait, T4 is fire-tamas-raudra, not rajas. Jvālāmālinī's fire-rajas-raudra is unique. The rajas guna distinguishes her from the tamas-fierce form of Bheruṇḍā: Jvālāmālinī is active-burning, Bheruṇḍā is dense-shattering. (nitya_devi_master.csv, OBSERVED:PRIMARY)
- **mantra_bija**: Hrīm Śrīm — chained bijas. Hrīm (māyā) + Śrīm (Lakṣmī, prosperity) — the māyā-prosperity pair. Structurally significant: at the threshold of dissolution, the bija combination is "illusion-with-abundance" — the karmic residue includes prosperity-attachments that must be released before transition. (nitya_devi_master.csv, OBSERVED:PRIMARY)

## Lunar/Time

- **lunar_phase_arc**: 156°-168° from conjunction (shukla caturdaśī), or 336°-348° (krishna caturdaśī). The 14th tithi is in opposition zone (approaching 180°).
- **phase_quality**: **Inauspicious** (tithi_master.csv). Good for: destructive acts, obstacle removal, tantra sadhana (same set as T4 Bheruṇḍā and T9 Kulasundari). Avoid: new ventures, marriage, travel. Tithi deity: **Śiva**. **Krishna Caturdaśī is Maśiva-rātri-eve / Maśivarātri itself in many traditions** — the principal Śaiva tithi of monthly observance.
- **nitya_cycle_position**: 14th of 15 — the threshold-burning position immediately preceding Citra at Pūrṇimā/Amāvāsyā. Jvālāmālinī's burning prepares the field for the full-bloom or full-dissolution event of T15.
- **weekday_links**: Caturdaśī's tithi deity is Śiva. Jvālāmālinī's graha correspondence is Mangala (Mars) per devi_master — Tuesday (Mangalavara). yantra_geometry CSV assigns **Jupiter** to tithi 14 — discrepancy. devi_master Mangala treated as authoritative. k=2, M=21.
- **nakshatra_overlays**: SOURCE_NEEDED: Caturdaśī belongs to the **Rikta group** (T4, T9, T14, T19, T24, T29 — empty/loss tithis). Three Rikta-Nityas: Bheruṇḍā (T4), Kulasundari (T9), Jvālāmālinī (T14). All three have inauspicious tithi quality and are good-for-tantra-sadhana. Jvālāmālinī is the third in this Rikta cluster — the fire-rajas-raudra burning that completes the Rikta sequence. Gandanta-Rikta interaction not specifically documented in RESEARCH-017 Finding 11.

## Yantra

- **yantra_family**: Downward triangle (trikona) with **32 petals** and bhupura. **Triangle scale 0.64, inner circle 0.68. Petal count 32 — THE HIGHEST in the Nityā set**. (nitya_yantra_geometry.csv, OBSERVED:TRADITIONAL — Dakshinamurti Samhita: "one of her mandalas has 32 petals and another variant has 40 petals.")
- **yantra_geometry_notes**: Classical yantra ATTESTED from Dakshinamurti Samhita with explicit 32-petal (or 40-petal variant) count. Among the Nityas, only Jvālāmālinī has classical attestation of such a high petal count. The 32-petal lotus in tantric architecture corresponds to the **Upādhi-pīṭha** layer (32 dynastic śaktis) in some Lalitā cosmologies. The CONSTRUCTION_CHOICES.md uses N=14 multigrid for the wave projection — 14-fold symmetry distinct from the 32-petal iconography. The petal-count and the multigrid-N are decoupled here, in contrast to Vahnivāsinī (T5, both 12-petal and N=8 multigrid).
- **yantra_symmetry_order**: N=14 (14-fold, fully quasicrystalline). 14 = 2×7 — bilateral symmetry combined with Mars's prime. Among the 15 Nityas, only Jvālāmālinī has N=14. (devi_engine.py DEVI_N)
- **yantra_center_logic**: Bindu as point. Inner circle scale 0.68. The 14-source pattern's central interference produces a 14-fold rosette.
- **yantra_outer_boundary**: Bhupura with 4 gates. Interference radius fraction: 0.25 (very tight). Wave function: sine, frequency multiplier: **5** (the highest in the Nityā set — produces 5 radial nodes), angular position: 312°.
- **yantra_layer_count**: 3 layers minimum: bindu → 32-petal lotus → bhupura. Triangle at 0.64 scale. **The 32-petal layer is the densest petal structure in the Nityā set** — render this with care.

## Field Math

- **graha_k**: Mangala = k=2, magic constant **M=21**. (yantra_eigenvalue_exploration.md, Finding 2). Same graha and same M as Nityaklinnā (T3). The two Mars-Devis are T3 and T14.
- **magic_constant_M**: 21 (Mangala, k=2). Eigenvalues: {21, +4.899, -4.899}. (Finding 1)
- **invariant_secondary_modes**: +/-2sqrt(6) = +/-4.8990. (Finding 1)
- **coherence_ratio**: lambda_2/M = 4.899/21 = **0.2333** (Mangala). The 3rd most polarized graha. Same value as T3. (Finding 2)
- **eigenvector_axes**: For Mangala (k=2): same as T3. (Finding 6)
- **brahmasthana_definition**: Uniform eigenvector at every Kronecker level. (Finding 4)
- **kronecker_level**: Level 1: 3x3, M=21. Level 2: 9x9, M=441. Level 3: 27x27, M=9261. (Finding 3)
- **navagraha_composite_role**: Mangala at k=2. Mars's Lo Shu placement is South (Yama direction). Same as T3. (Finding 5)

## Wave/Interference

- **boundary_harmonic_mode**: At k=14: not a classical jyotish aspect. The k=14 harmonic is the 25.71° aspect — non-classical. (two-source-interference-v3.md, Finding 8)
- **two_source_pattern**: A(theta) = 2 * cos(k(theta - midpoint)) * cos(k * separation/2). At k=14: constructive maximum at separation = 360/14 ≈ 25.71°. Caturdaśī's actual Sun-Moon separation is 156°-168° (opposition zone), well above this. (Finding 8)
- **nodal_interior_pattern**: For N=14 multigrid in disk interior: aperiodic, fully quasicrystalline. The 14-fold pattern has the structural feature that its even decomposition (14=2×7) gives partial bilateral symmetry to the otherwise-aperiodic field. (CONSTRUCTION_CHOICES.md)
- **ring_vs_disk_distinction**: Boundary: 14-source pattern silent except at k=14. Disk: aperiodic 14-fold tiling with partial bilateral symmetry. (Finding 7)
- **gandanta_gain**: Caturdaśī is Rikta. Rikta-gandanta interaction not specifically documented. (Finding 11)
- **wave_panchaka_relation**: Orthogonal: r = -0.011. (Finding 12)
- **quantized_prime_modes**: 14 = 2×7 contains Mars's retrograde prime (7) doubled (×2 for bilateral). Jvālāmālinī's tithi number is the **doubled-Mars**. Her graha is also Mars (Mangala). The double-Mars convergence at this tithi position is structurally meaningful: T3 (Nityaklinnā, also Mars) is single-Mars dissolution; T14 (Jvālāmālinī) is doubled-Mars burning. The intensity doubles at the threshold-tithi. (planetary-primes-v1.md, Section 2)

## Quasicrystal/Chladni

- **quasicrystal_line_style**: 14-fold multigrid. Aperiodic with bilateral-symmetry partial structure. (CONSTRUCTION_CHOICES.md)
- **nodal_density**: SOURCE_NEEDED. interference_radius_fraction = 0.25 (very tight — among the tightest in the Nityā set).
- **radial_bands**: 5 radial nodes within unit disk (frequency_multiplier=5). The first Nitya with this density level — among the highest in the entire set.
- **interference_centers**: Primary = bindu. Secondary maxima at 14 vertices of inscribed regular 14-gon at interference_radius=0.25. The 3D mediator polyhedron: **14-gonal antiprism** (28 triangular side faces + 2 14-gonal caps = 30 faces total). The 30 faces correspond exactly to the **30 tithis of the lunar month** — Jvālāmālinī's 3D mediator encodes the full lunar month at its face count. (CONSTRUCTION_CHOICES.md, polyhedron_mediator)

## Pasaka/Magic Cube

- **cube_type**: Andrews 1917. M=42. (magic_cube_analysis.json)
- **cube_magic_constant**: M = 42. (Finding 1)
- **cube_layer_squares**: layer eigenvalues {42, +/-9, ±9}. (Finding 1)
- **cube_invariant**: +/-9. Rational. (Finding 2)
- **cube_center_value**: **14 = (1+27)/2 — Caturdaśī's tithi number IS the cube center value.** This is structurally over-determined: Magic Cube center = 14 = T14's tithi number. (Finding 3)
- **cube_associative_sum**: 28 = n^3+1. (Finding 4)
- **cube_tensor_isotropy**: sigma_1 = 72.75. (Finding 6)
- **cube_kronecker_scaling**: M_n = 42^n. (magic_cube_extension.json)
- **cyclic_composite_eigenvalues**: 9x9: M=126, eigenvalues {126, +/-2.598, 0×4}. (Finding 2)
- **loshu_weighted_cube_mode**: Lo Shu collapses to {126, 0, ...}. (Finding 3)

### Pasaka at total=14

**SOURCE_NEEDED: System mismatch** — pasaka totals are 3-12 only. **No pasaka outcome corresponds to total=14**. Same situation as T13. Possible alternate mappings: (a) mod-12 reduction (14 mod 12 = 2 → no outcome at total=2 either); (b) deck-position 14 (ID 14 = Kīrti 1,4,2 total=7); (c) deck-extension. **Note: 14 IS the Magic Cube center value**, so the pasaka system's gap at this position is structurally compensated by the Magic Cube center alignment.

## I Ching

- **hexagram_id**: SOURCE_NEEDED. Numerical correspondent: hexagram 14 (Dà Yǒu, "Possession in Great Measure") — fire above heaven, abundant possession. The pairing is structurally interesting: Jvālāmālinī's fire-garland matches Dà Yǒu's "fire above" image; the burning-of-residue function is "great possession" of the karmic residue, holding it in fire to be consumed.
- **hexagram_arrangement**: Fuxi ↔ King Wen spectral opposites. (iching_spectral_analysis.json)
- **rank_complexity**: Q6 hypercube eigenvalues, Pascal row 6. (Finding 3)
- **yin_yang_balance_mode**: XOR-with-63 perfect partition. (Finding 6)
- **hypercube_distance_signature**: Hamming rank 7. (Finding 5)
- **pascal_row_signature**: Row 6, total 64. (Finding 3)

## Lo Shu x I Ching Bridge

- **trigram_loshu_weight_map**: Tithi 14 exceeds 1-9 trigram-weight range. Mod-9: 14 mod 9 = 5 → **center cell** (Vahnivāsinī's position, no trigram). Same modular position as T5 Vahnivāsinī. **The two fire-element Nityas (T5 fire-rajas-vira and T14 fire-rajas-raudra) both mod-9 to the center cell** — the unrepresented Lo Shu position. The fire-element Nityas occupy the trigram-gap position by mod-9 reduction. (loshu_iching_interaction.json)
- **weighted_spectral_breaking**: 7 → 27 unique eigenvalues. (test4_weighted_Q6)
- **spectral_gap_change**: 2.0 → 0.4624. Fiedler 0.1944. (test5_spectral_gap)

## Alchemical/Bhasma

- **material_classical_class**: Mangala → Tāmra (copper) and Praval (red coral). Same as Nityaklinnā (T3). See T3 card for full discussion.
- **material_scientific_type**: Copper (Cu, element 29); Praval (CaCO3 aragonite + carotenoid).
- **base_material**: Tāmra for metallic preparation; Praval for gem preparation.
- **prepared_substance_type**: Tāmra Bhasma; Praval Bhasma.
- **shodhana_media / bhavana_media / marana_cycles / puta_profile / particle_scale_overlay**: SOURCE_NEEDED. (See T3 card.)
- **quality_tests**: Standard tests + Praval-specific (white color after marana per dhātu compendium Volume V).
- **completion_stop_rule**: Quality tests pass.
- **phase_transformation**: Cu → Cu2O → CuO (Tāmra Bhasma); aragonite → calcite → CaO (Praval Bhasma). (Volume V)
- **safety_conditions**: Tāmra Bhasma toxicity if improperly prepared; Praval well-tolerated.

## Graha/Material

- **graha_material_map**: Mangala → Tāmra, Praval. (Same as T3.) Mars-copper-coral chain.
- **friend_enemy_interaction**: See T3 card. Mars-Mercury (Cu-Hg) failed amalgam is the materially-significant case.
- **ritual_vs_medical_flag**: Both. Copper vessels and Praval rosaries have extensive ritual use.

## Plant/Ecology

- **plant_allies**: SOURCE_NEEDED. Traditional Mangala plants: Khadira, Manjishtha, Arjuna. (Same as T3.)
- **processing_plants / doctrine_of_signatures_overlay / astrobotanical_timing**: SOURCE_NEEDED. **Caturdaśī as Maśivarātri-eve has special botanical significance**: traditional fasting alternatives for Maśivarātri include cooling milk-based preparations and bel (Bilva) leaves as offerings. The Bilva-Śiva-Caturdaśī alignment is structurally exact even though Bilva is also Sun-aligned (see T5 card). Multi-graha plant alignments are common at threshold tithis.

## Body/Therapeutics

- **dosha_predicates**: Tithi 14 element: fire (tithi_master.csv), guna: tamas. Devi element: fire (nitya_devi_master.csv), guna: rajas. Chakra: Muladhara (Mangala/Mars correspondence) — earth element, tamas, Vata dosha, Dakini shakti. (chakra_cross_domain.csv). The fire/fire/earth triad with tamas-rajas-tamas is the **threshold-burning profile**: outer fire (tithi) + active fire (Devi) + earth-base (chakra) = burning that is rooted in the body's foundation. The Muladhara chakra at the base of the spine is where Jvālāmālinī's fire actually burns — the kuṇḍalinī-rooted fire that purifies upward. Same chakra as Nityaklinnā T3 — the two Mars-Devis share Muladhara root.
- **dhatu_targets**: SOURCE_NEEDED. Mars governs Rakta (blood) and Majja (marrow/nerves). Same as T3.
- **organ_targets**: Muladhara at base of spine: perineal body, adrenal glands. (chakra_cross_domain.csv). Associated nakshatras: Mrigashira, Chitra, Dhanishtha — Mars-ruled.
- **indication_clusters**: SOURCE_NEEDED.
- **anupana_vehicle**: SOURCE_NEEDED.
- **preparation_dependency_warning**: Same as T3.

## Prime/Morphology

- **prime_signature**: 14 = 2×7. **Doubled-Mars-prime**. The combination of bilateral symmetry (2) with Mars's retrograde prime (7) gives the warrior-bilateral structure. 14 is also the count of **manvantaras** in Hindu cosmology (14 Manus per kalpa) and the **count of years of Vanavāsa** in the Rāmāyaṇa. (planetary-primes-v1.md, Section 2)
- **morphology_correlates**: 14 is not a primary vertebral count in major mammals. However, **14 days = half a synodic month** — the structural significance of T14 is exactly this: the 14-day mark from new/full moon, the threshold day. Per `vertebral-primes-v1.md` general framework, 14 doesn't carry a specific anatomical assignment, but the bilateral pairs (×7) suggest structural decompositions: 7 cervical pairs of joints, 7 cranial nerve pairs, etc., though these are not commonly enumerated as "14."
- **sri_yantra_region_relation**: 14 not in {3,5,7,11}. The 14-fold antiprism mediator's 30 faces = 30 tithis structurally. Not a primary Sri Yantra contributor but the 14-fold symmetry is in the high-N quasicrystalline regime where phason rearrangements occur (per RESEARCH-019). (planetary-primes-v1.md §3 + RESEARCH-019)

## Sound/Rhythm

- **svara_link**: SOURCE_NEEDED. Mangala's traditional svara is **Pa** (Pañcama, perfect 5th) per some Gandharva Veda sources. Same as T3.
- **raga_link**: Mars-associated ragas in raga_data.csv: **Bhairavī** (morning, earth/tamas, karuna; vadi Ma), **Nāṭa Bhairav** (morning, earth/tamas, vira). Same set as T3. **Nāṭa Bhairav** matches Jvālāmālinī better than T3's Bhairavī because its rasa is vira (warrior/fierce) rather than karuna (compassionate). The two Mars-Devis prefer different ragas: T3 = Bhairavī (compassion-dissolution), T14 = Nāṭa Bhairav (warrior-dissolution).
- **tala_link**: SOURCE_NEEDED. The 14-fold yantra symmetry suggests **14-beat cycles** (Dhamāra in Hindustani is 14-beat — used for dhrupad-style compositions). The 14-petal-symmetry-Dhamāra alignment is structural.

## Vastu/Spatial

- **mandala_zone_map**: Mangala at k=2 places yantra values as Lo_Shu + 2*J = {6,11,10;13,7,5;8,9,12}. Brahmasthana center = 7. Same as T3. (yantra_eigenvalue_exploration.md)
- **directional_emphasis**: Mangala governs South (Yama). Same as T3.

## Visual Grammar

- **palette_logic**: Primary: #ff8c00 (dark orange, from nitya_devi_master.csv — fire-garland color directly). Secondary: #FFAB91 (peach, from nitya_yantra_geometry.csv). Bindu: #D84315 (deep burnt orange). Line weight: medium. The fire-rajas-Mars signature with the threshold-burning iconography produces a fully-warm-orange palette: fire-orange field, peach accents, burnt-orange bindu — the burning-coal signature.
- **density_logic**: interference_radius_fraction = 0.25 (very tight). The 14-fold quasicrystalline field with frequency_multiplier=5 (the highest in the Nityā set) produces extremely concentrated central structure with 5 radial bands. **Render the 32-petal layer with full prominence** — the highest petal count in the Nityā set is the primary visual signature.
- **line_weight_logic**: Medium. The 32-petal layer requires careful rendering to avoid visual saturation; consistent medium line weight is essential.
- **panel_layout**: SOURCE_NEEDED. **Special design constraint**: this card may need to call out the 32-petal Dakshinamurti Samhita attestation visually — the 32 petals AND the 14-fold multigrid are structurally distinct features deserving separate visual emphasis.
- **symbol_strip**: SOURCE_NEEDED for capability_signature. Iconographic: **fire garland (jvālā-mālā)** as primary symbol; sword (khaḍga) as secondary. Bija: Hrīm Śrīm.
- **caption_motto**: "Garlanded with flames — she who burns away the residue of karma at the threshold." (nitya_devi_master.csv)

---

## Cross-layer observations

The first cross-layer resonance is the **Magic Cube center alignment at T14**. The 3×3×3 Magic Cube has center value 14 (= (1+27)/2, the average of the cube's value range 1-27). Jvālāmālinī's tithi number IS this cube center value. Among all 15 tithi positions, only T14 has its tithi number equal to the Magic Cube's center value. **The threshold-burning Nitya is the 3D Brahmasthana of the cube** — the spectrally null center of the magic structure. The pasaka system's gap at total=14 (no dice configuration produces this total) is structurally compensated by the Magic Cube center: where the 1D-3-dice system has no roll, the 3D-cube system has its center.

The second resonance is the **32-petal classical attestation as the densest Nityā lotus structure**. Among the 15 Nityā yantras, only Jvālāmālinī has classical-attested 32 petals (per Dakshinamurti Samhita, with a 40-petal variant noted). The 32-petal lotus corresponds to the Upādhi-pīṭha layer in some Lalitā cosmologies (32 dynastic śaktis). The 32 petals also align with: 32 vertebrae in some count systems (24 presacral + 5 sacral fused + 3-4 coccygeal), 32 teeth in adult human dentition, the 32 mahā-purusha lakṣaṇa (great-being marks). **The threshold-burning tithi has the densest petal mandala** — the field's full lotus-array activates at the threshold before transition.

The third resonance is the **dual-Mars structure of T3-T14 as dissolution-water vs dissolution-fire**. Both Nityaklinnā (T3) and Jvālāmālinī (T14) have graha = Mangala (Mars, k=2, M=21). T3 is element-water-tamas-karuna; T14 is element-fire-rajas-raudra. Same graha, opposite elemental and emotional polarities. The dissolution-Devi pair occupies opposite quarters of the lunar arc (T3 in shukla early-phase, T14 in shukla late-phase or krishna late-phase) and uses opposite material substrates (water vs fire). **Mars's two material faces — the wet-cooling rakta-dhātu and the dry-burning agni-dhātu — are the two Mars-Devi forms**. Together they bracket the main lunar-arc activity: Nityaklinnā opens the dissolution moment in the early cycle; Jvālāmālinī closes it at the threshold before transition.

---

## Attestation summary

- **OBSERVED:PRIMARY**: Identity (name, bija, mantra, weapon "fire garland+sword", description, rasa, element, guna, shakti from nitya_devi_master.csv); Lunar/Time (tithi quality, deity Śiva, good_for/avoid from tithi_master.csv); Yantra geometry — **32-petal classical attestation from Dakshinamurti Samhita** (one of only a few Nityas with attested petal count, per nitya_yantra_geometry.csv).
- **OBSERVED:TRADITIONAL**: Bhasma substance classes (Tāmra/Praval rasashastra); Mars's friend/enemy table (BPHS); chakra-graha mapping (Muladhara); raga-graha mapping (Nāṭa Bhairav).
- **SYNTHESIS**: Field Math eigenvalue derivation; Wave/Interference findings; Quasicrystal N=14 (bilateral-Mars); Cross-layer observations including Magic-Cube-center alignment, 32-petal density, and dual-Mars (T3+T14) reading.
- **GENERATED**: None.

---

## SOURCE_NEEDED flags

1. **mudras / vahana / body_color hue / ornaments / faces_arms_count / capability_signature**: nitya_devi_master.csv has multiple empty fields for Jvālāmālinī.
2. **nakshatra_overlays**: Compute Caturdaśī (Rikta-group) wave fine structure; Rikta-gandanta interaction not extracted.
3. **nodal_density / radial_bands explicit count**: Run N=14 sine frequency=5 multigrid extraction. **Highest frequency_multiplier in the Nityā set — important for proper rendering**.
4. **hexagram_id**: User decision for tithi 14 → hexagram 14 (Dà Yǒu).
5. **Pasaka at total=14**: System mismatch. Decide alternate mapping (Magic Cube center alignment is the structural compensation).
6. **shodhana_media / bhavana_media / marana_cycles / puta_profile / particle_scale_overlay**: Bhasma docx for Tāmra/Praval (same as T3).
7. **plant_allies / doctrine_of_signatures_overlay / processing_plants / astrobotanical_timing**: Mangala plant cross-reference + Maśivarātri-Bilva-Caturdaśī alignment.
8. **dhatu_targets / indication_clusters / anupana_vehicle**: Ayurvedic Mars protocols.
9. **svara_link / tala_link**: Gandharva Veda for Mars-svara and 14-beat tala (Dhamāra).
10. **directional_emphasis**: Vastu confirmation.
11. **panel_layout**: Design decision — 32-petal layer needs careful visual emphasis.
12. **40-petal variant**: Dakshinamurti Samhita attests both 32-petal and 40-petal forms. The 32-petal version is used in Atlas; 40-petal alternative attestation may deserve secondary documentation.
