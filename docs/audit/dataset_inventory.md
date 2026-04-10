# Dataset Inventory

Generated: 2026-04-10

| Metric | Count |
|--------|-------|
| CSV files | 188 |
| JSON files | 677 |
| JSONL files | 82 |
| YAML files | 6 |
| Total files | 953 |
| Total CSV rows | 21157 |

## astro/ (14 files)

- `astro/grahas.csv` — 9 rows, 6 cols: `graha_id, name, element, guna, color, metal`
- `astro/nakshatra_core.csv` — 27 rows, 3 cols: `nakshatra, graha, deity`
- `astro/nakshatra_deities.csv` — 27 rows, 2 cols: `nakshatra, deity`
- `astro/nakshatra_extended.csv` — 27 rows, 10 cols: `nakshatra, deity, ruling_graha, tree, plant, gemstone, shakti, direction`
- `astro/nakshatra_full.csv` — 27 rows, 8 cols: `nakshatra, graha, deity, symbol, shakti, guna, element, themes`
- `astro/nakshatra_master.csv` — 27 rows, 12 cols: `nakshatra, element, guna, gana, dosha, yoni_animal, yoni_gender, symbol`
- `astro/nakshatra_num_to_name.csv` — 27 rows, 3 cols: `num, name, key`
- `astro/nakshatra_padas.csv` — 108 rows, 2 cols: `nakshatra, pada`
- `astro/nakshatra_syllables.csv` — 20 rows, 3 cols: `nakshatra, pada, sound`
- `astro/tithi_core.csv` — 16 rows, 2 cols: `tithi, deity`
- `astro/tithi_deities.csv` — 16 rows, 3 cols: `tithi, deity, quality`
- `astro/tithi_list.csv` — 15 rows, 3 cols: `id, name, sanskrit`
- `astro/tithi_master.csv` — 30 rows, 12 cols: `tithi_num, id, name_iast, paksha, deity, element, guna, quality`
- `astro/tithi_properties.csv` — 15 rows, 4 cols: `tithi, element, guna, dosha`

## astrobotany/ (4 files)

- `astrobotany/astrobotanical_classes.csv` — 5 rows, 19 cols: `class_id, class_name, primary_element, dosha_correspondence, guna_primary, rasa_primary, virya, biodynamic_day_type`
- `astrobotany/biodynamic_vedic_mapping.csv` — 12 rows, 10 cols: `zodiac_sign, biodynamic_day_type, element, plant_focus, nakshatra_equivalents_sidereal_major, dosha_heuristic, best_activities_biodynamic, notes`
- `astrobotany/herbs_by_class.csv` — 100 rows, 5 cols: `herb_name, class_id, class_name, notes, attestation_status`
- `astrobotany/lunar_plant_biology.csv` — 8 rows, 5 cols: `claim, evidence_type, peer_reviewed, notes, attestation_status`

## ayurveda/ (17 files)

- `ayurveda/amidha_herbs.csv` — 704 rows, 13 cols: `amidha_id, name, link, preview, pacify, aggravate, tridosha, rasa`
- `ayurveda/coherence_rules.csv` — 5 rows, 7 cols: `rule_id, IF, THEN, label, coherence_weight, source_text, attestation_status`
- `ayurveda/dhatu_herb_matrix.csv` — 27 rows, 6 cols: `dhatu_id, herb_id, herb_name, action_type, attestation, source`
- `ayurveda/dhatu_render_params.csv` — 7 rows, 13 cols: `dhatu_id, geometric_form, physics_model, branch_angle, amplitude, frequency, primary_color, secondary_color`
- `ayurveda/dinacharya_panchanga.csv` — 8 rows, 10 cols: `muhurta_name, quality, recommended_practices, recommended_herbs, dietary_guidance, dosha_active, nakshatra_influence, tithi_influence`
- `ayurveda/dosha.csv` — 3 rows, 2 cols: `id, name`
- `ayurveda/dosha_nakshatra_matrix.csv` — 27 rows, 9 cols: `nakshatra, primary_dosha, secondary_dosha, dosha_modification_when_active, recommended_practice_for_this_dosha, dietary_guidance, herb_recommendation, source`
- `ayurveda/doshas.csv` — 3 rows, 5 cols: `dosha_id, name, elements, qualities, body_systems`
- `ayurveda/guna.csv` — 10 rows, 2 cols: `id, name`
- `ayurveda/gunas.csv` — 3 rows, 3 cols: `guna_id, name, qualities`
- `ayurveda/herb_exemplars.csv` — 5 rows, 24 cols: `herb_id, name_sanskrit, name_iast, name_common, name_latin, rasa, virya, vipaka`
- `ayurveda/herb_spine_108.csv` — 108 rows, 11 cols: `herb_id, name_common, attestation_status, rasa, virya, vipaka, guna, dosha_balance`
- `ayurveda/mahabhutas.csv` — 5 rows, 5 cols: `element_id, name, qualities, sense, organ`
- `ayurveda/rasa.csv` — 6 rows, 2 cols: `id, name`
- `ayurveda/sapta_dhatu.csv` — 7 rows, 25 cols: `dhatu_id, name_iast, tissue_type, governing_graha, nakshatra_correspondence, element, dosha_affinity, signs_of_health`
- `ayurveda/vipaka.csv` — 3 rows, 2 cols: `id, name`
- `ayurveda/virya.csv` — 2 rows, 2 cols: `id, name`

## canonical/ (6 files)

- +6 JSON/JSONL files

## carnatic/ (7 files)

- `carnatic/35_talas.csv` — 35 rows, 11 cols: `tala_id, family, jati, laghu_aksharas, beat_count, anga_breakdown, sollukattu, traditional_usage`
- `carnatic/gati_definitions.csv` — 5 rows, 8 cols: `gati_id, name, subdivisions, element_correspondence, guna_correspondence, attestation_cosmological, source_text, attestation_status`
- `carnatic/korvai_rules.csv` — 6 rows, 6 cols: `rule_id, structure, formula, example, source_text, attestation_status`
- `carnatic/navagraha_kritis.csv` — 3 rows, 6 cols: `graha, tala_family, jati, composer, kriti_name, attestation_status`
- `carnatic/sollukattu.csv` — 7 rows, 8 cols: `syllable_group, jati, anga_type, syllables, count, usage_context, source_text, attestation_status`
- `carnatic/tala_families.csv` — 7 rows, 9 cols: `family_id, name_iast, anga_sequence, description, graha_correspondence, navagraha_kriti_example, attestation_graha_link, source_text`
- `carnatic/tala_master.csv` — 50 rows, 13 cols: `id, name_iast, tradition, beat_count, anga_structure, element, guna, deity`

## chandas/ (2 files)

- `chandas/metre_correspondence_matrix.csv` — 32 rows, 13 cols: `metre_id, name_iast, correspondence_type, correspondence_value, secondary_value, weight, attestation_status, source`
- `chandas/metres_forms.csv` — 24 rows, 17 cols: `metre_id, name_iast, name_deva, syllables_per_pada, padas_per_verse, total_syllables, cadence_pattern, caesura_position`

## compositions/ (4 files)

- `compositions/gaudiya_compositions.csv` — 21 rows, 11 cols: `entity_id, entity_type, composition_name, composer, raga, tala, language, pallavi_text`
- `compositions/nakshatra_kritis.csv` — 12 rows, 11 cols: `entity_id, entity_type, composition_name, composer, raga, tala, language, pallavi_text`
- `compositions/narottama_padas.csv` — 8 rows, 12 cols: `entity_id, entity_type, composition_name, composer, raga, tala, language, pallavi_text`
- +1 JSON/JSONL files

## cosmology/ (19 files)

- `cosmology/ashtakala.csv` — 8 rows, 14 cols: `period, name, time_start, time_end, activity, raga, raga_alt, forest`
- `cosmology/bhajan_corpus.csv` — 12 rows, 12 cols: `bhajan_id, title, composer, language, ashtakala, lila_reference, raga, deity`
- `cosmology/daily_program.csv` — 8 rows, 11 cols: `program_id, name, time, ashtakala_period, deity_activity, songs, mantra, offering`
- `cosmology/deity_attributes.csv` — 27 rows, 20 cols: `deity_id, nakshatra, deity, item_1, item_2, item_3, item_4, vahana`
- `cosmology/deity_domains.csv` — 13 rows, 4 cols: `deity, domain, element, notes`
- `cosmology/deity_master.csv` — 27 rows, 8 cols: `deity, category, vahana, primary_weapon, associated_graha, element, domain, notes`
- `cosmology/deity_vahana_extended.csv` — 15 rows, 3 cols: `deity, vahana, symbolism`
- `cosmology/element_master.csv` — 5 rows, 15 cols: `id, element, guna, dosha, rasa, tanmatra, jnanendriya, karmendriya`
- `cosmology/gaudiya_festivals.csv` — 14 rows, 12 cols: `festival_id, name, tithi, month, paksha, deity, lila_reference, raga`
- `cosmology/goloka/ashtakala_lila.csv` — 8 rows, 11 cols: `period_name, time_range, location, primary_activity, presiding_sakhi, mood_rasa, traditional_raga, season`
- `cosmology/goloka/goloka_relations.csv` — 27 rows, 5 cols: `subject_entity, relation, object_entity, source, notes`
- `cosmology/goloka/sakhi_seva.csv` — 8 rows, 10 cols: `sakhi_name, seva, grove_location, rasa_relationship, instrument, color_flower_association, active_ashtakala_period, source`
- `cosmology/goloka/vraja_topology.csv` — 12 rows, 9 cols: `forest_name, location, lila_summary, season_or_time, presiding_deity_or_sakhi, sacred_sites, source, notes`
- `cosmology/goloka_topology.csv` — 0 rows, 0 cols: ``
- `cosmology/graha_master.csv` — 9 rows, 14 cols: `graha, category, element, guna, dosha, vehicle, weapon, domain`
- `cosmology/nitya_devi_mapping.csv` — 15 rows, 4 cols: `tithi_id, nitya_devi, color_hex, color_meaning`
- `cosmology/nitya_devi_master.csv` — 15 rows, 21 cols: `tithi_num, id, name_iast, name_devanagari, bija, mantra_short, element, guna`
- `cosmology/vedic_arts_64.csv` — 62 rows, 6 cols: `art, category, domain, from_layer, to_layer, gaudiya_priority`
- `cosmology/vraja_forests.csv` — 12 rows, 14 cols: `forest_id, name, sanskrit, direction, deity, presiding_sakhi, season, nakshatra_correspondence`

## entities/ (12 files)

- `entities/concept.csv` — 2 rows, 6 cols: `id, type, name, aliases, notes, source_file`
- `entities/deity.csv` — 2 rows, 6 cols: `id, type, name, aliases, notes, source_file`
- `entities/graha.csv` — 9 rows, 6 cols: `id, type, name, aliases, notes, source_file`
- `entities/jyotish.csv` — 4 rows, 6 cols: `id, type, name, aliases, notes, source_file`
- `entities/nakshatra.csv` — 27 rows, 6 cols: `id, type, name, aliases, notes, source_file`
- `entities/rashi.csv` — 12 rows, 6 cols: `id, type, name, aliases, notes, source_file`
- `entities/text.csv` — 1 rows, 6 cols: `id, type, name, aliases, notes, source_file`
- +5 JSON/JSONL files

## game/ (4 files)

- `game/chimera_types.csv` — 5 rows, 9 cols: `chimera_id, name, natal_calculation, graha_required, nakshatra_required, element_threshold, form_description, accessible_districts`
- `game/lineages.csv` — 11 rows, 13 cols: `lineage_id, name_sanskrit, name_iast, name_english, lineage_type, natal_requirements, graha_primary, nakshatra_trigger`
- `game/sacred_objects.csv` — 8 rows, 12 cols: `object_id, name_sanskrit, name_english, entity_link, district_location, recognition_relation, recognition_text, attestation_level`
- `game/sura_asura_map.csv` — 9 rows, 5 cols: `entity_id, orientation, direction, quality, notes`

## gandharva/ (5 files)

- `gandharva/bija_master.csv` — 8 rows, 4 cols: `bija, element, deity, domain`
- `gandharva/graha_bija.csv` — 9 rows, 2 cols: `graha, bija`
- `gandharva/graha_raga_chords.csv` — 9 rows, 6 cols: `graha, raga_primary, raga_secondary, scale_degrees, mood, time_of_day`
- `gandharva/instruments.csv` — 25 rows, 20 cols: `id, name_iast, name_sanskrit, category, element, guna, chakra, deity`
- `gandharva/raga_therapeutic.csv` — 9 rows, 7 cols: `raga, dosha_target, time, conditions, duration, attestation, source`

## geography/ (4 files)

- `geography/ecoregions_na.csv` — 8 rows, 10 cols: `ecoregion_name, biome, elemental_character, dosha_correspondence, keystone_species, indigenous_traditions, seasonal_rhythms, ecological_wounds`
- `geography/geographic_body_relations.csv` — 45 rows, 10 cols: `relation_id, source_type, source_id, target_type, target_id, relation, direction, weight`
- `geography/sacred_sites_global.csv` — 50 rows, 21 cols: `site_id, site_name, lat, lon, tradition, body_correspondence, element, graha`
- `geography/shakti_pitha_matrix.csv` — 63 rows, 14 cols: `pitha_id, site_name, body_part, devi_name, bhairava, latitude, longitude, country`

## iching/ (8 files)

- `iching/changing_lines.csv` — 384 rows, 8 cols: `from_hexagram, from_line, to_hexagram, transition_quality, field_movement, rasa_shift, lifecycle_shift, notes`
- `iching/hexagram_devi_resonance.csv` — 416 rows, 6 cols: `hexagram_id, devi_id, tithi_alignment, resonance_score, quality_match, notes`
- `iching/hexagram_lines.csv` — 384 rows, 8 cols: `hexagram_id, line_number, yang_or_yin, line_text_wilhelm, field_meaning, changing_to_hexagram, lifecycle_transition, intensity_threshold`
- `iching/hexagram_nakshatra_resonance.csv` — 1015 rows, 8 cols: `hexagram_id, nakshatra_id, resonance_score, resonance_reason, shared_element, shared_quality, shared_graha, notes`
- `iching/hexagram_raga_resonance.csv` — 1084 rows, 7 cols: `hexagram_id, raga_id, resonance_reason, time_of_day_match, rasa_match, element_match, notes`
- `iching/hexagrams.csv` — 64 rows, 29 cols: `entity_id, number, name_chinese, name_pinyin, name_english, symbol, lower_trigram, upper_trigram`
- `iching/trigram_vastu_map.csv` — 8 rows, 8 cols: `trigram, vastu_position, deity, zone_engine, layer, graha_correspondence, element_correspondence, notes`
- `iching/trigrams.csv` — 8 rows, 22 cols: `entity_id, name_chinese, name_pinyin, name_english, symbol, lines, element, quality`

## jyotish/ (3 files)


## mappings/ (1 files)

- +1 JSON/JSONL files

## marma/ (2 files)

- `marma/body_region_marma.csv` — 20 rows, 8 cols: `body_region, marma_name, marma_location, marma_type, therapeutic_action, contraindication, source_text, attestation_status`
- `marma/marma_field.csv` — 37 rows, 15 cols: `name_iast, body_region, count, size_angula, category, element, dosha, chakra_nearest`

## morphogenesis/ (2 files)

- `morphogenesis/body_archetype_map.csv` — 26 rows, 14 cols: `body_region, archetype, graha, dhatu, mathematical_equation, render_geometry, natal_weight_key, asana_that_loads`
- `morphogenesis/doctrine_of_signatures.csv` — 44 rows, 17 cols: `signature_id, plant_id, plant_common, plant_part, body_target, body_system, form_correspondence, chemistry_correspondence`

## ontology/ (7 files)

- `ontology/bhava_relations.csv` — 12 rows, 3 cols: `relation, description, bhava_class`
- `ontology/bhava_types.csv` — 12 rows, 5 cols: `id, sanskrit, iast, description, category`
- `ontology/knowledge_layers.csv` — 6 rows, 3 cols: `layer_id, name, description`
- `ontology/parampara.csv` — 11 rows, 8 cols: `id, name_iast, name_sk, position, role, era, source, attestation`
- `ontology/rasa_siddhanta.csv` — 12 rows, 8 cols: `id, name_iast, name_sk, type, description, sthayi_bhava, source, attestation`
- `ontology/vaishnava_tattva.csv` — 15 rows, 7 cols: `id, name_iast, name_sk, category, description, source, attestation`

## overlays/ (1 files)

- `overlays/relations_layered.csv` — 317 rows, 6 cols: `from_id, relation, to_id, layer, confidence, notes`

## permaculture/ (1 files)

- `permaculture/design_principles.csv` — 12 rows, 7 cols: `principle_name, description, elemental_correspondence, vedic_parallel, vastu_zone, dosha_quality, attestation`

## plants/ (11 files)

- `plants/ethnobotany_na.csv` — 15 rows, 12 cols: `common_name, latin_name, ecoregion, indigenous_use, indigenous_nations, ecological_role, guild_function, animal_relationships`
- `plants/guild_matrix.csv` — 84 rows, 32 cols: `plant_id, latin_name, common_name, family, layer, guild_function_primary, nitrogen_fixer, succession_role`
- `plants/guild_matrix_raw.csv` — 91 rows, 33 cols: `plant_id, common_name, latin_name, ecoregion, layer, succession_role, mature_height_m, canopy_spread_m`
- `plants/guild_principles.csv` — 8 rows, 8 cols: `permaculture_principle, vedic_equivalent, vastu_zone, element, graha, description, source`
- `plants/guild_relations.csv` — 216 rows, 15 cols: `guild_id, anchor_plant, companion_plant, relationship_type, guild_function, vastu_zone, element, graha_companion`
- `plants/nakshatra_agriculture.csv` — 27 rows, 8 cols: `nakshatra, quality, activity, avoid, crops, element, guna, notes`
- `plants/nakshatra_plants.csv` — 27 rows, 21 cols: `nakshatra, plant, common_name, sanskrit_name, deity, element, dosha, use`
- `plants/pfaf_structured.csv` — 2514 rows, 33 cols: `latin_name, common_name, family, habit, mature_height_m, canopy_spread_m, hardiness_zone_min, hardiness_zone_max`
- `plants/sacred_plants.csv` — 10 rows, 4 cols: `plant, deity, element, use`
- +1 JSON/JSONL files

## ratna/ (1 files)

- `ratna/graha_gems.csv` — 9 rows, 9 cols: `graha, primary_gem, substitute_gem, metal, finger, day_to_wear, mantra_for_consecration, source_text`

## relations/ (26 files)

- `relations/bija_relations.csv` — 33 rows, 9 cols: `from_id, relation, to_id, source_title, source_locator, excerpt, tradition, confidence`
- `relations/carnatic_relations.csv` — 82 rows, 9 cols: `from_id, relation, to_id, source_title, source_locator, excerpt, tradition, confidence`
- `relations/deity_relations.csv` — 159 rows, 9 cols: `from_id, relation, to_id, source_title, source_locator, excerpt, tradition, confidence`
- `relations/dosha_relations.csv` — 74 rows, 9 cols: `from_id, relation, to_id, source_title, source_locator, excerpt, tradition, confidence`
- `relations/gaudiya_relations.csv` — 28 rows, 7 cols: `from_id, relation, to_id, source, confidence, stability, authority`
- `relations/iching_relations.csv` — 1946 rows, 8 cols: `from_id, relation, to_id, tradition, source, confidence, gaudiya_aligned, notes`
- `relations/mythic_relations.csv` — 5 rows, 9 cols: `from_id, relation, to_id, source_title, source_locator, excerpt, tradition, confidence`
- `relations/nadi_relations.csv` — 31 rows, 9 cols: `from_id, relation, to_id, source_title, source_locator, excerpt, tradition, confidence`
- `relations/nakshatra_associated_deity.csv` — 73 rows, 9 cols: `from_id, relation, to_id, source_title, source_locator, excerpt, tradition, confidence`
- `relations/ratna_relations.csv` — 45 rows, 9 cols: `from_id, relation, to_id, source_title, source_locator, excerpt, tradition, confidence`
- `relations/relational_repair.csv` — 209 rows, 8 cols: `from_id, relation, to_id, tradition, source, confidence, gaudiya_aligned, notes`
- `relations/relations_devi_weapon.csv` — 15 rows, 9 cols: `from_id, relation, to_id, source_title, source_locator, excerpt, tradition, confidence`
- `relations/relations_nakshatra_deity.csv` — 27 rows, 9 cols: `from_id, relation, to_id, source_title, source_locator, excerpt, tradition, confidence`
- `relations/relations_nakshatra_graha.csv` — 27 rows, 9 cols: `from_id, relation, to_id, source_title, source_locator, excerpt, tradition, confidence`
- `relations/relations_nakshatra_plants.csv` — 135 rows, 9 cols: `from_id, relation, to_id, source_title, source_locator, excerpt, tradition, confidence`
- `relations/relations_raga_ritual.csv` — 0 rows, 0 cols: ``
- `relations/relations_resolved_canon.csv` — 44 rows, 9 cols: `from_id, relation, to_id, source_title, source_locator, excerpt, tradition, confidence`
- `relations/relations_resolved_inference.csv` — 132 rows, 9 cols: `from_id, relation, to_id, source_title, source_locator, excerpt, tradition, confidence`
- `relations/relations_resolved_overlays.csv` — 323 rows, 9 cols: `from_id, relation, to_id, source_title, source_locator, excerpt, tradition, confidence`
- `relations/relations_resolved_proto_canon.csv` — 0 rows, 0 cols: ``
- `relations/relations_ritual_calendar.csv` — 10 rows, 9 cols: `from_id, relation, to_id, source_title, source_locator, excerpt, tradition, confidence`
- `relations/s0_roots.csv` — 84 rows, 5 cols: `from_id, relation, to_id, attestation, notes`
- `relations/sound_relations.csv` — 315 rows, 9 cols: `from_id, relation, to_id, source_title, source_locator, excerpt, tradition, confidence`
- `relations/species_relations.csv` — 163 rows, 8 cols: `from_id, relation, to_id, tradition, source, confidence, gaudiya_aligned, notes`
- `relations/text_entity_relations.csv` — 1442 rows, 9 cols: `from_id, relation, to_id, source_title, source_locator, excerpt, tradition, confidence`
- `relations/vastu_relations.csv` — 145 rows, 9 cols: `from_id, relation, to_id, source_title, source_locator, excerpt, tradition, confidence`

## ritual/ (3 files)

- `ritual/plant_ritual.csv` — 7 rows, 7 cols: `plant, mantra, offering_type, deity_affinity, tithi_best, graha, element`
- `ritual/vaishnava_calendar.csv` — 43 rows, 10 cols: `masa_num, paksha, tithi_num, observance_name, observance_name_iast, observance_type, deity, parampara_ref`

## schema/ (1 files)

- +1 JSON/JSONL files

## semantics/ (1 files)

- `semantics/vedic_arts_semantic_layer.csv` — 32 rows, 5 cols: `stable_id, english_name, sanskrit_devanagari, sanskrit_iast, category`

## silpa/ (1 files)

- `silpa/bandhu_geometry.csv` — 8 rows, 4 cols: `measure, parts, notes, source`

## sound/ (2 files)

- `sound/raga_master.csv` — 20 rows, 17 cols: `id, name_iast, tradition, time_of_day, season, element, guna, rasa_primary`
- `sound/tanpura_strings.csv` — 7 rows, 13 cols: `string_id, name, default_ratio, graha, jivari, decay_s, level, pluck_offset_s`

## sources/ (741 files)

- `sources/passages.csv` — 1219 rows, 5 cols: `passage_id, source_id, locator, excerpt, tags`
- `sources/sources.csv` — 34 rows, 4 cols: `source_id, title, path, notes`
- +739 JSON/JSONL files

## species/ (5 files)

- `species/nakshatra_species.csv` — 27 rows, 8 cols: `nakshatra_id, nakshatra_name, species_id, species_name, relationship_type, source, confidence, notes`
- `species/species_entities.csv` — 22 rows, 27 cols: `entity_id, name_sanskrit, name_iast, name_english, species_latin, element_primary, element_secondary, guna`
- `species/species_plant_matrix.csv` — 35 rows, 10 cols: `species_id, plant_id, shared_element, shared_graha, shared_nakshatra, shared_quality, correspondence_type, source`
- `species/species_render_params.csv` — 22 rows, 16 cols: `species_id, body_form_primary, body_form_secondary, proportion_head, proportion_body, proportion_limbs, proportion_tail, dominant_curve`
- `species/vahana_relationships.csv` — 13 rows, 9 cols: `species_id, deity_id, deity_tradition, vahana_quality, what_species_expresses, what_deity_expresses, why_this_pairing, source`

## svarodaya/ (6 files)

- `svarodaya/activity_matrix.csv` — 210 rows, 7 cols: `activity, nadi, element, recommendation, knowledge_status, source_text, attestation_status`
- `svarodaya/coherence_rules.csv` — 6 rows, 5 cols: `rule_id, condition, recommendation, coherence_score, attestation_status`
- `svarodaya/elements.csv` — 5 rows, 10 cols: `element_id, name, duration_minutes, how_to_detect, activities_best, activities_worst, direction_favored, body_sensation`
- `svarodaya/nadis.csv` — 3 rows, 11 cols: `nadi_id, name_iast, side, graha_correspondence, element, quality, activities_favored, activities_avoid`
- `svarodaya/tithi_rules.csv` — 60 rows, 7 cols: `tithi_number, paksha, optimal_nadi, variant_id, deviation_effect, source_text, attestation_status`
- `svarodaya/vara_rules.csv` — 7 rows, 6 cols: `vara, optimal_nadi, reasoning, deviation_indicates, source_text, attestation_status`

## symbols/ (6 files)

- `symbols/atlas_glyphs.csv` — 98 rows, 12 cols: `entity_id, entity_type, name, glyph, glyph_type, unicode, color, size_default`
- `symbols/emoji_auto_mapped.csv` — 1906 rows, 14 cols: `emoji, unicode_name, group, graha, element, layer, nakshatra, varna`
- `symbols/emoji_master.csv` — 1906 rows, 6 cols: `emoji, unicode_name, group, subgroup, slug, codepoint`
- `symbols/emoji_vedic_map.csv` — 105 rows, 14 cols: `emoji, name, unicode_codepoint, varna, graha, element, layer, nakshatra`
- `symbols/icon_packs.csv` — 15 rows, 7 cols: `pack_name, source_url, license, icon_count, category, priority, notes`
- +1 JSON/JSONL files

## system/ (5 files)

- `system/capability_map.csv` — 16 rows, 8 cols: `capability_id, name, status, entity_id, install_time, blocked_by, priority, notes`
- `system/code_topology.csv` — 105 rows, 10 cols: `entity_id, file_path, status, what_it_does, inputs, outputs, imports_from, imported_by`
- `system/layer_mapping.csv` — 75 rows, 4 cols: `layer, dataset_path, domain, description`
- `system/system_topology.csv` — 29 rows, 10 cols: `entity_id, entity_type, name, status, stability, depends_on, provides, protocol`
- +1 JSON/JSONL files

## tantra/ (1 files)

- `tantra/chakra_master.csv` — 7 rows, 20 cols: `id, name_iast, sanskrit, location, element, guna, bija, petals`

## tarot/ (3 files)

- +3 JSON/JSONL files

## vastu/ (11 files)

- `vastu/ayadi_formulas.csv` — 6 rows, 7 cols: `formula_id, name, calculation, divisor, remainder_meanings, source_text, attestation_status`
- `vastu/element_geometry.csv` — 5 rows, 6 cols: `element, sides, color_hex, yantra_name, meaning, rasa`
- `vastu/geometry_archetypes.csv` — 7 rows, 4 cols: `geometry, element, symbolism, yantra_use`
- `vastu/inner_deities.csv` — 13 rows, 6 cols: `deity, x, y, domain, source_text, attestation_status`
- `vastu/marma_sthana.csv` — 9 rows, 8 cols: `marma_id, x, y, type, avoidance_rule, mitigation, source_text, attestation_status`
- `vastu/pada_topology.csv` — 108 rows, 16 cols: `id, idx, nakshatra, pada_n, element, ribbon, longitude_deg, knot_x`
- `vastu/perimeter_deities.csv` — 32 rows, 9 cols: `position, deity, x, y, direction, element, function, source_text`
- `vastu/vastu_directions.csv` — 9 rows, 6 cols: `direction, element, guna, deity, graha, zone_activity`
- `vastu/vastu_land_zones.csv` — 9 rows, 8 cols: `Direction, Traditional_Use, Element, Deity, Reason, Modern_Permaculture_Equivalent, Sources`
- `vastu/vastu_pada_grid.csv` — 81 rows, 8 cols: `pada_number, row, col, deity_name, deity_type, direction, source_text, attestation`
- `vastu/vastu_zones.csv` — 9 rows, 5 cols: `zone, direction, deity, element, planet`

## views/ (1 files)

- `views/intention_rules.csv` — 24 rows, 15 cols: `intention_id, intention_label, category, favorable_vara, avoid_vara, favorable_nakshatra, avoid_nakshatra, favorable_tithi_type`

## yoga/ (5 files)

- `yoga/asana_core.csv` — 22 rows, 7 cols: `asana, element, effect, type, graha_affinity, dosha_balance, body_region`
- `yoga/bandha_core.csv` — 4 rows, 6 cols: `bandha, element, effect, location, graha_affinity, chakra`
- `yoga/marma_master.csv` — 37 rows, 13 cols: `id, name_iast, name_english, body_region, element, guna, dosha, chakra_affinity`
- `yoga/nakshatra_body_map.csv` — 27 rows, 3 cols: `nakshatra, body_region, source`
- `yoga/pranayama_core.csv` — 6 rows, 6 cols: `pranayama, element, effect, dosha_balance, graha_affinity, duration_minutes`

