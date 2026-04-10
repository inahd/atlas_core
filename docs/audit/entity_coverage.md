# Entity Coverage Matrix

## nakshatra (40 files)

- `astro/nakshatra_core.csv` (27r): nakshatra, graha, deity
- `astro/nakshatra_deities.csv` (27r): nakshatra, deity
- `astro/nakshatra_extended.csv` (27r): nakshatra, deity, ruling_graha, tree, plant, gemstone
- `astro/nakshatra_full.csv` (27r): nakshatra, graha, deity, symbol, shakti, guna
- `astro/nakshatra_master.csv` (27r): nakshatra, element, guna, gana, dosha, yoni_animal
- `astro/nakshatra_num_to_name.csv` (27r): num, name, key
- `astro/nakshatra_padas.csv` (108r): nakshatra, pada
- `astro/nakshatra_syllables.csv` (20r): nakshatra, pada, sound
- `views/intention_rules.csv` (24r): intention_id, intention_label, category, favorable_vara, avoid_vara, favorable_nakshatra
- `entities/nakshatra.csv` (27r): id, type, name, aliases, notes, source_file
- `relations/nakshatra_associated_deity.csv` (73r): from_id, relation, to_id, source_title, source_locator, excerpt
- `relations/relations_nakshatra_deity.csv` (27r): from_id, relation, to_id, source_title, source_locator, excerpt
- +28 more

## graha (44 files)

- `sound/raga_master.csv` (20r): id, name_iast, tradition, time_of_day, season, element
- `sound/tanpura_strings.csv` (7r): string_id, name, default_ratio, graha, jivari, decay_s
- `astro/grahas.csv` (9r): graha_id, name, element, guna, color, metal
- `astro/nakshatra_core.csv` (27r): nakshatra, graha, deity
- `astro/nakshatra_extended.csv` (27r): nakshatra, deity, ruling_graha, tree, plant, gemstone
- `astro/nakshatra_full.csv` (27r): nakshatra, graha, deity, symbol, shakti, guna
- `geography/sacred_sites_global.csv` (50r): site_id, site_name, lat, lon, tradition, body_correspondence
- `geography/shakti_pitha_matrix.csv` (63r): pitha_id, site_name, body_part, devi_name, bhairava, latitude
- `entities/graha.csv` (9r): id, type, name, aliases, notes, source_file
- `relations/relations_nakshatra_graha.csv` (27r): from_id, relation, to_id, source_title, source_locator, excerpt
- `species/species_entities.csv` (22r): entity_id, name_sanskrit, name_iast, name_english, species_latin, element_primary
- `species/species_plant_matrix.csv` (35r): species_id, plant_id, shared_element, shared_graha, shared_nakshatra, shared_quality
- +32 more

## tithi (14 files)

- `astro/tithi_core.csv` (16r): tithi, deity
- `astro/tithi_deities.csv` (16r): tithi, deity, quality
- `astro/tithi_list.csv` (15r): id, name, sanskrit
- `astro/tithi_master.csv` (30r): tithi_num, id, name_iast, paksha, deity, element
- `astro/tithi_properties.csv` (15r): tithi, element, guna, dosha
- `views/intention_rules.csv` (24r): intention_id, intention_label, category, favorable_vara, avoid_vara, favorable_nakshatra
- `ayurveda/dinacharya_panchanga.csv` (8r): muhurta_name, quality, recommended_practices, recommended_herbs, dietary_guidance, dosha_active
- `iching/hexagram_devi_resonance.csv` (416r): hexagram_id, devi_id, tithi_alignment, resonance_score, quality_match, notes
- `cosmology/gaudiya_festivals.csv` (14r): festival_id, name, tithi, month, paksha, deity
- `cosmology/nitya_devi_mapping.csv` (15r): tithi_id, nitya_devi, color_hex, color_meaning
- `cosmology/nitya_devi_master.csv` (15r): tithi_num, id, name_iast, name_devanagari, bija, mantra_short
- `svarodaya/tithi_rules.csv` (60r): tithi_number, paksha, optimal_nadi, variant_id, deviation_effect, source_text
- +2 more

## devi (8 files)

- `astro/tithi_master.csv` (30r): tithi_num, id, name_iast, paksha, deity, element
- `geography/shakti_pitha_matrix.csv` (63r): pitha_id, site_name, body_part, devi_name, bhairava, latitude
- `relations/relations_devi_weapon.csv` (15r): from_id, relation, to_id, source_title, source_locator, excerpt
- `iching/hexagram_devi_resonance.csv` (416r): hexagram_id, devi_id, tithi_alignment, resonance_score, quality_match, notes
- `cosmology/nitya_devi_mapping.csv` (15r): tithi_id, nitya_devi, color_hex, color_meaning
- `cosmology/nitya_devi_master.csv` (15r): tithi_num, id, name_iast, name_devanagari, bija, mantra_short
- `svarodaya/tithi_rules.csv` (60r): tithi_number, paksha, optimal_nadi, variant_id, deviation_effect, source_text
- `svarodaya/vara_rules.csv` (7r): vara, optimal_nadi, reasoning, deviation_indicates, source_text, attestation_status

## raga (16 files)

- `sound/raga_master.csv` (20r): id, name_iast, tradition, time_of_day, season, element
- `sound/tanpura_strings.csv` (7r): string_id, name, default_ratio, graha, jivari, decay_s
- `relations/relations_raga_ritual.csv` (0r): 
- `iching/hexagram_raga_resonance.csv` (1084r): hexagram_id, raga_id, resonance_reason, time_of_day_match, rasa_match, element_match
- `gandharva/graha_raga_chords.csv` (9r): graha, raga_primary, raga_secondary, scale_degrees, mood, time_of_day
- `gandharva/instruments.csv` (25r): id, name_iast, name_sanskrit, category, element, guna
- `gandharva/raga_therapeutic.csv` (9r): raga, dosha_target, time, conditions, duration, attestation
- `cosmology/ashtakala.csv` (8r): period, name, time_start, time_end, activity, raga
- `cosmology/bhajan_corpus.csv` (12r): bhajan_id, title, composer, language, ashtakala, lila_reference
- `cosmology/daily_program.csv` (8r): program_id, name, time, ashtakala_period, deity_activity, songs
- `cosmology/gaudiya_festivals.csv` (14r): festival_id, name, tithi, month, paksha, deity
- `cosmology/goloka/ashtakala_lila.csv` (8r): period_name, time_range, location, primary_activity, presiding_sakhi, mood_rasa
- +4 more

## tala (7 files)

- `carnatic/35_talas.csv` (35r): tala_id, family, jati, laghu_aksharas, beat_count, anga_breakdown
- `carnatic/navagraha_kritis.csv` (3r): graha, tala_family, jati, composer, kriti_name, attestation_status
- `carnatic/tala_families.csv` (7r): family_id, name_iast, anga_sequence, description, graha_correspondence, navagraha_kriti_example
- `carnatic/tala_master.csv` (50r): id, name_iast, tradition, beat_count, anga_structure, element
- `compositions/gaudiya_compositions.csv` (21r): entity_id, entity_type, composition_name, composer, raga, tala
- `compositions/nakshatra_kritis.csv` (12r): entity_id, entity_type, composition_name, composer, raga, tala
- `compositions/narottama_padas.csv` (8r): entity_id, entity_type, composition_name, composer, raga, tala

## plant (26 files)

- `astro/nakshatra_extended.csv` (27r): nakshatra, deity, ruling_graha, tree, plant, gemstone
- `relations/relations_nakshatra_plants.csv` (135r): from_id, relation, to_id, source_title, source_locator, excerpt
- `species/species_plant_matrix.csv` (35r): species_id, plant_id, shared_element, shared_graha, shared_nakshatra, shared_quality
- `plants/ethnobotany_na.csv` (15r): common_name, latin_name, ecoregion, indigenous_use, indigenous_nations, ecological_role
- `plants/guild_matrix.csv` (84r): plant_id, latin_name, common_name, family, layer, guild_function_primary
- `plants/guild_matrix_raw.csv` (91r): plant_id, common_name, latin_name, ecoregion, layer, succession_role
- `plants/guild_principles.csv` (8r): permaculture_principle, vedic_equivalent, vastu_zone, element, graha, description
- `plants/guild_relations.csv` (216r): guild_id, anchor_plant, companion_plant, relationship_type, guild_function, vastu_zone
- `plants/nakshatra_agriculture.csv` (27r): nakshatra, quality, activity, avoid, crops, element
- `plants/nakshatra_plants.csv` (27r): nakshatra, plant, common_name, sanskrit_name, deity, element
- `plants/pfaf_structured.csv` (2514r): latin_name, common_name, family, habit, mature_height_m, canopy_spread_m
- `plants/sacred_plants.csv` (10r): plant, deity, element, use
- +14 more

## marma (7 files)

- `geography/shakti_pitha_matrix.csv` (63r): pitha_id, site_name, body_part, devi_name, bhairava, latitude
- `ayurveda/sapta_dhatu.csv` (7r): dhatu_id, name_iast, tissue_type, governing_graha, nakshatra_correspondence, element
- `yoga/marma_master.csv` (37r): id, name_iast, name_english, body_region, element, guna
- `vastu/marma_sthana.csv` (9r): marma_id, x, y, type, avoidance_rule, mitigation
- `morphogenesis/body_archetype_map.csv` (26r): body_region, archetype, graha, dhatu, mathematical_equation, render_geometry
- `marma/body_region_marma.csv` (20r): body_region, marma_name, marma_location, marma_type, therapeutic_action, contraindication
- `marma/marma_field.csv` (37r): name_iast, body_region, count, size_angula, category, element

## vastu (27 files)

- `permaculture/design_principles.csv` (12r): principle_name, description, elemental_correspondence, vedic_parallel, vastu_zone, dosha_quality
- `astro/nakshatra_padas.csv` (108r): nakshatra, pada
- `astro/nakshatra_syllables.csv` (20r): nakshatra, pada, sound
- `relations/vastu_relations.csv` (145r): from_id, relation, to_id, source_title, source_locator, excerpt
- `species/species_entities.csv` (22r): entity_id, name_sanskrit, name_iast, name_english, species_latin, element_primary
- `symbols/emoji_auto_mapped.csv` (1906r): emoji, unicode_name, group, graha, element, layer
- `symbols/emoji_vedic_map.csv` (105r): emoji, name, unicode_codepoint, varna, graha, element
- `chandas/metre_correspondence_matrix.csv` (32r): metre_id, name_iast, correspondence_type, correspondence_value, secondary_value, weight
- `chandas/metres_forms.csv` (24r): metre_id, name_iast, name_deva, syllables_per_pada, padas_per_verse, total_syllables
- `plants/guild_principles.csv` (8r): permaculture_principle, vedic_equivalent, vastu_zone, element, graha, description
- `plants/guild_relations.csv` (216r): guild_id, anchor_plant, companion_plant, relationship_type, guild_function, vastu_zone
- `ayurveda/dhatu_render_params.csv` (7r): dhatu_id, geometric_form, physics_model, branch_angle, amplitude, frequency
- +15 more

## dosha (29 files)

- `sound/raga_master.csv` (20r): id, name_iast, tradition, time_of_day, season, element
- `permaculture/design_principles.csv` (12r): principle_name, description, elemental_correspondence, vedic_parallel, vastu_zone, dosha_quality
- `astro/nakshatra_master.csv` (27r): nakshatra, element, guna, gana, dosha, yoni_animal
- `astro/tithi_properties.csv` (15r): tithi, element, guna, dosha
- `geography/ecoregions_na.csv` (8r): ecoregion_name, biome, elemental_character, dosha_correspondence, keystone_species, indigenous_traditions
- `relations/dosha_relations.csv` (74r): from_id, relation, to_id, source_title, source_locator, excerpt
- `species/species_entities.csv` (22r): entity_id, name_sanskrit, name_iast, name_english, species_latin, element_primary
- `symbols/emoji_auto_mapped.csv` (1906r): emoji, unicode_name, group, graha, element, layer
- `symbols/emoji_vedic_map.csv` (105r): emoji, name, unicode_codepoint, varna, graha, element
- `plants/nakshatra_plants.csv` (27r): nakshatra, plant, common_name, sanskrit_name, deity, element
- `ayurveda/amidha_herbs.csv` (704r): amidha_id, name, link, preview, pacify, aggravate
- `ayurveda/dinacharya_panchanga.csv` (8r): muhurta_name, quality, recommended_practices, recommended_herbs, dietary_guidance, dosha_active
- +17 more

## element (64 files)

- `sound/raga_master.csv` (20r): id, name_iast, tradition, time_of_day, season, element
- `sound/tanpura_strings.csv` (7r): string_id, name, default_ratio, graha, jivari, decay_s
- `permaculture/design_principles.csv` (12r): principle_name, description, elemental_correspondence, vedic_parallel, vastu_zone, dosha_quality
- `astro/grahas.csv` (9r): graha_id, name, element, guna, color, metal
- `astro/nakshatra_full.csv` (27r): nakshatra, graha, deity, symbol, shakti, guna
- `astro/nakshatra_master.csv` (27r): nakshatra, element, guna, gana, dosha, yoni_animal
- `astro/tithi_master.csv` (30r): tithi_num, id, name_iast, paksha, deity, element
- `astro/tithi_properties.csv` (15r): tithi, element, guna, dosha
- `geography/ecoregions_na.csv` (8r): ecoregion_name, biome, elemental_character, dosha_correspondence, keystone_species, indigenous_traditions
- `geography/sacred_sites_global.csv` (50r): site_id, site_name, lat, lon, tradition, body_correspondence
- `geography/shakti_pitha_matrix.csv` (63r): pitha_id, site_name, body_part, devi_name, bhairava, latitude
- `species/species_entities.csv` (22r): entity_id, name_sanskrit, name_iast, name_english, species_latin, element_primary
- +52 more

## body (25 files)

- `geography/geographic_body_relations.csv` (45r): relation_id, source_type, source_id, target_type, target_id, relation
- `geography/sacred_sites_global.csv` (50r): site_id, site_name, lat, lon, tradition, body_correspondence
- `geography/shakti_pitha_matrix.csv` (63r): pitha_id, site_name, body_part, devi_name, bhairava, latitude
- `species/species_render_params.csv` (22r): species_id, body_form_primary, body_form_secondary, proportion_head, proportion_body, proportion_limbs
- `plants/ethnobotany_na.csv` (15r): common_name, latin_name, ecoregion, indigenous_use, indigenous_nations, ecological_role
- `plants/nakshatra_plants.csv` (27r): nakshatra, plant, common_name, sanskrit_name, deity, element
- `ayurveda/dhatu_herb_matrix.csv` (27r): dhatu_id, herb_id, herb_name, action_type, attestation, source
- `ayurveda/dhatu_render_params.csv` (7r): dhatu_id, geometric_form, physics_model, branch_angle, amplitude, frequency
- `ayurveda/doshas.csv` (3r): dosha_id, name, elements, qualities, body_systems
- `ayurveda/herb_exemplars.csv` (5r): herb_id, name_sanskrit, name_iast, name_common, name_latin, rasa
- `ayurveda/sapta_dhatu.csv` (7r): dhatu_id, name_iast, tissue_type, governing_graha, nakshatra_correspondence, element
- `tantra/chakra_master.csv` (7r): id, name_iast, sanskrit, location, element, guna
- +13 more

## deity (40 files)

- `sound/raga_master.csv` (20r): id, name_iast, tradition, time_of_day, season, element
- `astro/nakshatra_core.csv` (27r): nakshatra, graha, deity
- `astro/nakshatra_deities.csv` (27r): nakshatra, deity
- `astro/nakshatra_extended.csv` (27r): nakshatra, deity, ruling_graha, tree, plant, gemstone
- `astro/nakshatra_full.csv` (27r): nakshatra, graha, deity, symbol, shakti, guna
- `astro/tithi_core.csv` (16r): tithi, deity
- `astro/tithi_deities.csv` (16r): tithi, deity, quality
- `astro/tithi_master.csv` (30r): tithi_num, id, name_iast, paksha, deity, element
- `entities/deity.csv` (2r): id, type, name, aliases, notes, source_file
- `relations/deity_relations.csv` (159r): from_id, relation, to_id, source_title, source_locator, excerpt
- `relations/nakshatra_associated_deity.csv` (73r): from_id, relation, to_id, source_title, source_locator, excerpt
- `relations/relations_nakshatra_deity.csv` (27r): from_id, relation, to_id, source_title, source_locator, excerpt
- +28 more

