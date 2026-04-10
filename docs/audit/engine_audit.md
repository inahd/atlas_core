# NPU Engine Audit

Date: 2026-04-10

## Engine Files: 204

## npu_engine/__init__.py/ (1 files)

### `npu_engine/__init__.py` (5 lines)
- Route in kernel: no
- Status: STUB

## npu_engine/_compat.py/ (1 files)

### `npu_engine/_compat.py` (20 lines)
- Route in kernel: no
- Status: UNKNOWN

## npu_engine/aspect_repair.py/ (1 files)

### `npu_engine/aspect_repair.py` (227 lines)
- Functions: add_aspect_edges
- Route in kernel: no
- Status: WORKING

## npu_engine/bija_synth.py/ (1 files)

### `npu_engine/bija_synth.py` (247 lines)
- Functions: _bandpass, _glottal_source, _noise_source, _synth_varna, _envelope, _crossfade
- Route in kernel: YES
- Status: WORKING

## npu_engine/build_field_state.py/ (1 files)

### `npu_engine/build_field_state.py` (317 lines)
- Functions: _enrich_entity, _detect_soft_formations, build_field_state, apply_modulation, query_field_state
- Route in kernel: YES
- Status: WORKING

## npu_engine/card_engine.py/ (1 files)

### `npu_engine/card_engine.py` (461 lines)
- Classes: Card, CardEngine
- Functions: _first
- Route in kernel: YES
- Status: WORKING

## npu_engine/codex_engine.py/ (1 files)

### `npu_engine/codex_engine.py` (534 lines)
- Functions: select_entities, select_relations, generate, _generate_brief, _generate_practice, _generate_study
- Route in kernel: no
- Status: WORKING

## npu_engine/codex_interaction.py/ (1 files)

### `npu_engine/codex_interaction.py` (139 lines)
- Functions: codex_from_entity, codex_from_cluster, paths_from_entity
- Route in kernel: YES
- Status: WORKING

## npu_engine/codex_modes.py/ (1 files)

### `npu_engine/codex_modes.py` (16 lines)
- Route in kernel: no
- Status: STUB

## npu_engine/coherence_engine_v2.py/ (1 files)

### `npu_engine/coherence_engine_v2.py` (208 lines)
- Functions: _cat_w, _cat_w, rerank_entities, _entity_attestation, extract_active_relations, _edge_attestation
- Route in kernel: YES
- Status: WORKING

## npu_engine/composition_db.py/ (1 files)

### `npu_engine/composition_db.py` (241 lines)
- Functions: load_compositions, _normalize, _raga_match, _time_match, _vara_match, score_composition
- Route in kernel: YES
- Status: WORKING

## npu_engine/core/ (8 files)

### `npu_engine/core/__init__.py` (3 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/core/build.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/core/coherence.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/core/datasets.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/core/field_state.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/core/graph_engine.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/core/toroidal_field.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/core/vector_store.py` (1 lines)
- Route in kernel: no
- Status: STUB

## npu_engine/datasets.py/ (1 files)

### `npu_engine/datasets.py` (1365 lines)
- Functions: _load_csv, _load_json, _load_yaml, _slug, _clean, _title
- Route in kernel: YES
- Status: WORKING

## npu_engine/engines/ (12 files)

### `npu_engine/engines/__init__.py` (33 lines)
- Route in kernel: no
- Status: UNKNOWN

### `npu_engine/engines/action_engine.py` (30 lines)
- Classes: ActionEngine
- Route in kernel: no
- Status: WORKING

### `npu_engine/engines/archetype_engine.py` (35 lines)
- Classes: ArchetypeEngine
- Route in kernel: no
- Status: WORKING

### `npu_engine/engines/base_engine.py` (69 lines)
- Classes: ZoneEngine
- Field keys: layers, sound_state, panchanga
- Route in kernel: no
- Status: WORKING

### `npu_engine/engines/body_engine.py` (104 lines)
- Classes: BodyEngine
- Functions: _load_marma
- Datasets: datasets/marma/body_region_marma.csv, datasets/marma/marma_field.csv
- Field keys: panchanga
- Route in kernel: no
- Status: WORKING

### `npu_engine/engines/center_engine.py` (84 lines)
- Classes: CenterEngine
- Route in kernel: no
- Status: WORKING

### `npu_engine/engines/codex_engine.py` (30 lines)
- Classes: CodexEngine
- Route in kernel: no
- Status: WORKING

### `npu_engine/engines/ecology_engine.py` (32 lines)
- Classes: EcologyEngine
- Route in kernel: no
- Status: WORKING

### `npu_engine/engines/guild_engine.py` (506 lines)
- Classes: GuildEngine
- Functions: _load_plants, _load_guild_relations, _load_principles, _load_pfaf_structured, _pfaf_lookup, _load_guild_matrix
- Datasets: datasets/plants/nakshatra_plants.csv, datasets/plants/guild_relations.csv, datasets/plants/guild_principles.csv
- Route in kernel: YES
- Status: WORKING

### `npu_engine/engines/plant_engine.py` (213 lines)
- Classes: PlantEngine
- Functions: _load_plants, derive_plant_field
- Route in kernel: YES
- Status: WORKING

### `npu_engine/engines/rhythm_engine.py` (36 lines)
- Classes: RhythmEngine
- Route in kernel: no
- Status: WORKING

### `npu_engine/engines/sound_engine.py` (32 lines)
- Classes: SoundEngine
- Route in kernel: no
- Status: WORKING

## npu_engine/field/ (16 files)

### `npu_engine/field/__init__.py` (0 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/field/city_engine.py` (343 lines)
- Functions: _hex_direction, log_interaction, _recompute_scores, get_district_scores, get_gate_inscription, city_report
- Route in kernel: no
- Status: WORKING

### `npu_engine/field/code_engine.py` (395 lines)
- Functions: _load_topology, _split, _build_keyword_index, _score_file, _find_related, _row_to_context
- Datasets: datasets/system/code_topology.csv
- Route in kernel: no
- Status: WORKING

### `npu_engine/field/composition_engine.py` (616 lines)
- Functions: _load_csv, _load_natal, _all_compositions, _classify_message, _select_pada, _search_passage
- Route in kernel: YES
- Status: WORKING

### `npu_engine/field/goloka_engine.py` (353 lines)
- Functions: _load, _parse_time, _current_ashtakala, _forest_for_period, _nitya_devi_for_tithi, _program_for_period
- Datasets: datasets/cosmology/ashtakala.csv, datasets/cosmology/vraja_forests.csv, datasets/cosmology/nitya_devi_master.csv, datasets/cosmology/daily_program.csv
- Route in kernel: YES
- Status: WORKING

### `npu_engine/field/guild_planner.py` (411 lines)
- Functions: _load_csv, _guild_relations, _nak_plants, _herbs, _pfaf, _find_nak_plant
- Route in kernel: YES
- Status: WORKING

### `npu_engine/field/helix_engine.py` (338 lines)
- Functions: _jdn, _moon_lon, _rahu_lon, _sun_lon, _tithi_num, _nakshatra_idx
- Route in kernel: YES
- Status: WORKING

### `npu_engine/field/intention_engine.py` (650 lines)
- Functions: _load_rules, _split, _build_keyword_map, _normalize_vara, _normalize_nakshatra, _tithi_quality
- Route in kernel: YES
- Status: WORKING

### `npu_engine/field/land_engine.py` (795 lines)
- Functions: _load_zones, _load_dirs, _validate, derive_land_layout, _detect_ecoregion, _hardiness_zone
- Route in kernel: YES
- Status: WORKING

### `npu_engine/field/reading_engine.py` (666 lines)
- Functions: _load_json, _load_csv_rows, build_reading_context, _lens_tarot, _lens_iching, _lens_jyotish
- Route in kernel: YES
- Status: WORKING

### `npu_engine/field/region_engine.py` (406 lines)
- Functions: _get_requests, _ecoregion_name, _hardiness_zone, _hardiness_range, _fetch_inaturalist, _usda_lookup
- Route in kernel: YES
- Status: WORKING

### `npu_engine/field/ring_engine.py` (492 lines)
- Functions: _load, _ring_muhurta, _norm_nak, _ring_nakshatra, _ring_devi, _ring_graha
- Field keys: sound_state, hora, panchanga
- Route in kernel: YES
- Status: WORKING

### `npu_engine/field/site_engine.py` (711 lines)
- Functions: _get_np, _get_requests, _fetch_elevation_point, _fetch_elevation_grid, _cache_key, _load_cache
- Route in kernel: YES
- Status: WORKING

### `npu_engine/field/symbol_engine.py` (357 lines)
- Functions: _load, _build_index, lookup_symbol, lookup_by_graha, lookup_by_element, lookup_by_layer
- Datasets: datasets/symbols/emoji_vedic_map.csv, datasets/cosmology/graha_master.csv, datasets/cosmology/nitya_devi_master.csv, datasets/astro/nakshatra_master.csv
- Route in kernel: YES
- Status: WORKING

### `npu_engine/field/system_engine.py` (500 lines)
- Functions: _load_csv, _load_topology, _load_capabilities, _entity_by_id, _run, _is_process_running
- Datasets: datasets/system/system_topology.csv, datasets/system/capability_map.csv
- Route in kernel: YES
- Status: WORKING

### `npu_engine/field/trajectory_engine.py` (530 lines)
- Functions: _load_csv, _tithis, _nakshatras, _grahas, _load_natal, _arc_position
- Route in kernel: YES
- Status: WORKING

## npu_engine/field_layers.py/ (1 files)

### `npu_engine/field_layers.py` (252 lines)
- Functions: _lookup_nakshatra_plant, generate_layer_mapping
- Route in kernel: YES
- Status: WORKING

## npu_engine/field_state.py/ (1 files)

### `npu_engine/field_state.py` (101 lines)
- Classes: FieldState
- Route in kernel: no
- Status: WORKING

## npu_engine/field_to_sound.py/ (1 files)

### `npu_engine/field_to_sound.py` (428 lines)
- Functions: _slugify, get_devi_from_tithi, get_vastu_from_field, get_treatment_vector, element_to_sa, guna_to_character
- Route in kernel: YES
- Status: WORKING

## npu_engine/game/ (7 files)

### `npu_engine/game/__init__.py` (0 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/game/card_engine.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/game/character_engine.py` (198 lines)
- Functions: _load_natal, _load_objects, _load_interactions, _prakriti, _varna_tendency, _check_encounters
- Route in kernel: YES
- Status: WORKING

### `npu_engine/game/generator.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/game/lineage_engine.py` (162 lines)
- Functions: _load, _natal_elements, _graha_strong, _nak_match, calculate_accessible_lineages
- Datasets: datasets/game/lineages.csv.
- Route in kernel: YES
- Status: WORKING

### `npu_engine/game/orientation_engine.py` (82 lines)
- Functions: _load, derive_sura_asura
- Datasets: datasets/game/sura_asura_map.csv.
- Route in kernel: YES
- Status: WORKING

### `npu_engine/game/relational_engine.py` (1 lines)
- Route in kernel: no
- Status: STUB

## npu_engine/generator.py/ (1 files)

### `npu_engine/generator.py` (392 lines)
- Classes: FieldGenerator
- Functions: _slug, _first_attr, get_generator
- Field keys: muhurta, sound_state, active_relations, panchanga
- Route in kernel: no
- Status: WORKING

## npu_engine/geometry/ (8 files)

### `npu_engine/geometry/__init__.py` (0 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/geometry/igpu.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/geometry/orientation.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/geometry/temple_geometry.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/geometry/torus_queries.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/geometry/vastu_engine.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/geometry/yantra_engine.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/geometry/yantra_generator.py` (1 lines)
- Route in kernel: no
- Status: STUB

## npu_engine/graph_engine.py/ (1 files)

### `npu_engine/graph_engine.py` (276 lines)
- Classes: GraphEngine
- Functions: _safe_float, _classify_authority
- Route in kernel: YES
- Status: WORKING

## npu_engine/igpu.py/ (1 files)

### `npu_engine/igpu.py` (827 lines)
- Classes: RenderNode, RenderFlow, RenderEdge, RenderFormation, RenderState
- Functions: project_plane, project_toroid, project_hex, project_4d, layout_nodes, layout_edges
- Route in kernel: YES
- Status: WORKING

## npu_engine/layer_engine.py/ (1 files)

### `npu_engine/layer_engine.py` (159 lines)
- Functions: load_layer_mapping, datasets_for_layer, load_layer_data, layer_summary, all_layer_summaries, entity_layer
- Datasets: datasets/layer_mapping.csv
- Route in kernel: YES
- Status: WORKING

## npu_engine/library_kernel.py/ (1 files)

### `npu_engine/library_kernel.py` (284 lines)
- Functions: inventory_datasets, inventory_texts, inventory_graph, detect_gaps, track_growth, suggest_next
- Datasets: datasets/sanskrit/matrika_50.csv, datasets/geography/sacred_sites_india.csv, datasets/geography/vraja_parikrama.csv, datasets/sources/passages.csv
- Route in kernel: YES
- Status: WORKING

## npu_engine/lifecycle_engine.py/ (1 files)

### `npu_engine/lifecycle_engine.py` (68 lines)
- Functions: compute_lifecycle
- Route in kernel: no
- Status: WORKING

## npu_engine/mandala_schema.py/ (1 files)

### `npu_engine/mandala_schema.py` (2309 lines)
- Functions: _resolve_layout_zone, resolve_layout_map, _has_sub_zone, _entity_to_zone_row, _top_entities_for, _graph_neighbors
- Field keys: psi, sound_state
- Route in kernel: YES
- Status: WORKING

## npu_engine/mix/ (11 files)

### `npu_engine/mix/__init__.py` (7 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/mix/authority_mix.py` (30 lines)
- Classes: ConfidenceScale
- Functions: get_confidence_scale
- Route in kernel: no
- Status: WORKING

### `npu_engine/mix/deity_mix.py` (18 lines)
- Functions: get_deity_bias
- Route in kernel: no
- Status: WORKING

### `npu_engine/mix/graph_seed_data.py` (145 lines)
- Route in kernel: no
- Status: UNKNOWN

### `npu_engine/mix/guna_mix.py` (14 lines)
- Functions: get_guna_character
- Route in kernel: no
- Status: WORKING

### `npu_engine/mix/layer_graph.py` (42 lines)
- Functions: get_layer_weights, _arc_density
- Route in kernel: YES
- Status: WORKING

### `npu_engine/mix/mix_history.py` (65 lines)
- Classes: MixHistory
- Route in kernel: no
- Status: WORKING

### `npu_engine/mix/mix_kernel.py` (151 lines)
- Classes: MixKernel
- Route in kernel: no
- Status: WORKING

### `npu_engine/mix/mix_osc.py` (62 lines)
- Classes: MixOSC
- Route in kernel: no
- Status: WORKING

### `npu_engine/mix/nakshatra_mix.py` (14 lines)
- Functions: get_nakshatra_bias
- Route in kernel: no
- Status: WORKING

### `npu_engine/mix/sam_mix.py` (38 lines)
- Classes: MixEvent
- Functions: get_sam_event, get_khali_event
- Route in kernel: no
- Status: WORKING

## npu_engine/modulation_engine.py/ (1 files)

### `npu_engine/modulation_engine.py` (101 lines)
- Functions: semantic_modulation, derive_psi
- Route in kernel: no
- Status: WORKING

## npu_engine/mudra_graph.py/ (1 files)

### `npu_engine/mudra_graph.py` (422 lines)
- Functions: _normalize_nakshatra, _get_rasa_from_raga, _pick_weighted, get_mudra_for_field, generate_mudra_sequence, mudra_to_atlas_event
- Route in kernel: no
- Status: WORKING

## npu_engine/natal_musician.py/ (1 files)

### `npu_engine/natal_musician.py` (655 lines)
- Functions: _natal_nakshatras, _current_nakshatra, _match_natal_nak, _dasha_lord, _derive_field_tensions, _derive_rhythmic_tensions
- Route in kernel: YES
- Status: WORKING

## npu_engine/nature/ (6 files)

### `npu_engine/nature/__init__.py` (0 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/nature/guild_engine.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/nature/guild_planner.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/nature/land_engine.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/nature/ring_engine.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/nature/s5_kernel.py` (1 lines)
- Route in kernel: no
- Status: STUB

## npu_engine/orientation.py/ (1 files)

### `npu_engine/orientation.py` (191 lines)
- Functions: compute_natal_orientation, compute_entity_signal, nearest_position, traditions_near, orientation_note, compute_orientation
- Route in kernel: YES
- Status: WORKING

## npu_engine/passage_resolver.py/ (1 files)

### `npu_engine/passage_resolver.py` (176 lines)
- Functions: _load_entity_index, _load_passages_by_tag, _guess_tradition, _extract_entity_ids, find_passages
- Datasets: datasets/sources/entity_index.json, datasets/sources/passages.csv, datasets/relations/text_entity_relations.csv
- Route in kernel: YES
- Status: WORKING

## npu_engine/path_engine.py/ (1 files)

### `npu_engine/path_engine.py` (387 lines)
- Functions: _is_noise, _relation_value, find_paths, rank_paths, format_path, detect_flows
- Route in kernel: YES
- Status: WORKING

## npu_engine/phrase_engine.py/ (1 files)

### `npu_engine/phrase_engine.py` (392 lines)
- Classes: NoteEvent, PhraseEngine
- Functions: arc_to_mode
- Route in kernel: no
- Status: WORKING

## npu_engine/query_engine.py/ (1 files)

### `npu_engine/query_engine.py` (211 lines)
- Functions: _get_graph, query, _entity_domain, _id_domain, _find_relation, _find_hop
- Route in kernel: YES
- Status: WORKING

## npu_engine/raga_graph.py/ (1 files)

### `npu_engine/raga_graph.py` (441 lines)
- Functions: _svara_to_node, _build_edges_from_aroha, _load_ragas_from_csv, get_raga_graph, generate_phrase, phrase_to_freqs
- Route in kernel: no
- Status: WORKING

## npu_engine/relational_engine.py/ (1 files)

### `npu_engine/relational_engine.py` (177 lines)
- Classes: RelationalEngine
- Route in kernel: YES
- Status: WORKING

## npu_engine/relational_params.py/ (1 files)

### `npu_engine/relational_params.py` (181 lines)
- Classes: TanpuraPhysics, SympatheticPhysics
- Functions: _tithi_tension, _tithi_coupling, _arc_modes, derive_tanpura_physics, derive_sympathetic_physics
- Route in kernel: no
- Status: WORKING

## npu_engine/relational_synth.py/ (1 files)

### `npu_engine/relational_synth.py` (270 lines)
- Functions: _derive_sa_hz, compute_tanpura_params, compute_melody_voices, compute_rhythm_pattern, compute_master_params, compute_synth_params
- Route in kernel: no
- Status: WORKING

## npu_engine/renderers/ (3 files)

### `npu_engine/renderers/__init__.py` (0 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/renderers/figure_renderer.py` (1176 lines)
- Functions: _load_archetypes, toroidal_breath_params, _breath_keyframes, _load_geom, _val, _validate
- Route in kernel: YES
- Status: WORKING

### `npu_engine/renderers/species_renderer.py` (204 lines)
- Functions: _load, _render_params, _nak_species, _entities, _presence_score, _validate
- Route in kernel: YES
- Status: WORKING

## npu_engine/rhythm/ (11 files)

### `npu_engine/rhythm/__init__.py` (10 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/rhythm/cross_rhythm_engine.py` (53 lines)
- Classes: CrossRhythm
- Functions: get_cross_rhythm
- Route in kernel: no
- Status: WORKING

### `npu_engine/rhythm/fill_engine.py` (47 lines)
- Classes: Fill
- Functions: get_fill
- Route in kernel: no
- Status: WORKING

### `npu_engine/rhythm/graph_seed_data.py` (274 lines)
- Functions: _load_carnatic, get_gati_definitions, get_tala_families, get_korvai_rules, get_sollukattu, gati_for_element
- Datasets: datasets/carnatic/, datasets/carnatic/
- Route in kernel: no
- Status: WORKING

### `npu_engine/rhythm/layakari_engine.py` (49 lines)
- Functions: get_layakari, _nearest_idx
- Route in kernel: no
- Status: WORKING

### `npu_engine/rhythm/rhythm_kernel.py` (183 lines)
- Classes: RhythmKernel
- Route in kernel: no
- Status: WORKING

### `npu_engine/rhythm/rhythm_osc.py` (71 lines)
- Classes: RhythmOSC
- Route in kernel: no
- Status: WORKING

### `npu_engine/rhythm/sam_field.py` (85 lines)
- Functions: get_gravity, get_tension, is_approaching_sam, beats_to_sam
- Route in kernel: no
- Status: WORKING

### `npu_engine/rhythm/tala_graph.py` (75 lines)
- Classes: TalaStructure, BolProperties
- Functions: get_tala, get_theka, get_bol_properties, get_rasa_tala_affinity, beat_to_vibhag
- Route in kernel: no
- Status: WORKING

### `npu_engine/rhythm/theka_engine.py` (93 lines)
- Classes: BolEvent
- Functions: generate_theka_cycle
- Route in kernel: no
- Status: WORKING

### `npu_engine/rhythm/tihai_engine.py` (66 lines)
- Classes: Tihai
- Functions: find_tihai, is_tihai_possible
- Route in kernel: no
- Status: WORKING

## npu_engine/s5_kernel.py/ (1 files)

### `npu_engine/s5_kernel.py` (306 lines)
- Classes: PlantNode, S5State
- Functions: _nak_index, _angle, _load_nakshatra_plants, _load_dosha_herbs, _load_inferred_herbs, _day_type
- Route in kernel: YES
- Status: WORKING

## npu_engine/sarangi_voice.py/ (1 files)

### `npu_engine/sarangi_voice.py` (377 lines)
- Classes: SarangiString, SarangiVoice
- Route in kernel: no
- Status: WORKING

## npu_engine/sound/ (18 files)

### `npu_engine/sound/__init__.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/sound/aspect_repair.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/sound/bija_synth.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/sound/composition_db.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/sound/field_to_sound.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/sound/mudra_graph.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/sound/natal_musician.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/sound/osc_bridge.py` (57 lines)
- Functions: _get_client, send_sound_spec
- Route in kernel: YES
- Status: WORKING

### `npu_engine/sound/phrase_engine.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/sound/raga_graph.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/sound/relational_params.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/sound/relational_synth.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/sound/sarangi_voice.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/sound/sound_engine.py` (373 lines)
- Functions: _resolve_sound_params, _resolve_observance, _compute_layers, _compute_master, _build_osc_messages, _clamp
- Route in kernel: YES
- Status: WORKING

### `npu_engine/sound/swara_engine.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/sound/tabla_sampler.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/sound/tanpura_engine.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/sound/tanpura_field.py` (1 lines)
- Route in kernel: no
- Status: STUB

## npu_engine/swara_engine.py/ (1 files)

### `npu_engine/swara_engine.py` (335 lines)
- Classes: SwaraEngine
- Route in kernel: YES
- Status: WORKING

## npu_engine/sympathetic/ (5 files)

### `npu_engine/sympathetic/__init__.py` (15 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/sympathetic/excitation.py` (70 lines)
- Classes: Excitation, ResonanceEvent
- Functions: compute_resonances
- Route in kernel: no
- Status: WORKING

### `npu_engine/sympathetic/string_model.py` (117 lines)
- Classes: SympatheticString
- Functions: tune_strings, find_resonating_strings, _log2_safe
- Route in kernel: no
- Status: WORKING

### `npu_engine/sympathetic/sympathetic_kernel.py` (114 lines)
- Classes: SympatheticKernel
- Route in kernel: no
- Status: WORKING

### `npu_engine/sympathetic/sympathetic_osc.py` (68 lines)
- Classes: SympatheticOSC
- Route in kernel: no
- Status: WORKING

## npu_engine/system/ (4 files)

### `npu_engine/system/__init__.py` (0 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/system/city_engine.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/system/code_engine.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/system/system_engine.py` (1 lines)
- Route in kernel: no
- Status: STUB

## npu_engine/tabla_sampler.py/ (1 files)

### `npu_engine/tabla_sampler.py` (240 lines)
- Functions: load_samples, _synth_bol, _ensure_synth_samples, get_bol_audio, render_tala_beat
- Route in kernel: no
- Status: WORKING

## npu_engine/tanpura_engine.py/ (1 files)

### `npu_engine/tanpura_engine.py` (558 lines)
- Classes: TanpuraString, TanpuraEngine
- Functions: _load_string_defs, _load_graha_energy, _graha_jivari, _graha_decay, _build_lookups, _fallback_render
- Datasets: datasets/sound/tanpura_strings.csv., datasets/sound/tanpura_strings.csv.
- Field keys: pa, sa2
- Route in kernel: no
- Status: WORKING

## npu_engine/tanpura_field.py/ (1 files)

### `npu_engine/tanpura_field.py` (242 lines)
- Functions: tithi_string_weights, derive_tanpura_params
- Route in kernel: no
- Status: WORKING

## npu_engine/temple_geometry.py/ (1 files)

### `npu_engine/temple_geometry.py` (218 lines)
- Classes: TempleGeometry
- Route in kernel: YES
- Status: WORKING

## npu_engine/tests/ (2 files)

### `npu_engine/tests/__init__.py` (0 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/tests/test_toroid.py` (0 lines)
- Route in kernel: no
- Status: STUB

## npu_engine/text/ (11 files)

### `npu_engine/text/__init__.py` (0 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/text/codex_engine.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/text/codex_interaction.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/text/codex_modes.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/text/composition_engine.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/text/library_kernel.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/text/passage_resolver.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/text/path_engine.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/text/query_engine.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/text/reading_engine.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/text/treasury.py` (1 lines)
- Route in kernel: no
- Status: STUB

## npu_engine/time/ (8 files)

### `npu_engine/time/__init__.py` (0 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/time/field_layers.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/time/goloka_engine.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/time/intention_engine.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/time/layer_engine.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/time/lifecycle_engine.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/time/modulation_engine.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/time/trajectory_engine.py` (1 lines)
- Route in kernel: no
- Status: STUB

## npu_engine/toroidal_field.py/ (1 files)

### `npu_engine/toroidal_field.py` (664 lines)
- Classes: ToroidalField
- Functions: _init_npu, toroid_3d, toroidal_distance, max_toroidal_distance, coherence_from_distance, panchanga_to_coords
- Route in kernel: YES
- Status: WORKING

## npu_engine/torus_queries.py/ (1 files)

### `npu_engine/torus_queries.py` (175 lines)
- Functions: _knot_pos, torus_knot_distance, find_pada_for_nakshatra, nearest_padas_cross_ribbon, score_entity_against_triangle, torus_context_for_entity
- Route in kernel: YES
- Status: WORKING

## npu_engine/treasury.py/ (1 files)

### `npu_engine/treasury.py` (200 lines)
- Functions: _load, get_current_prahar, get_personalities_for_field, get_quotes_for_field, resolve_treasury
- Route in kernel: YES
- Status: WORKING

## npu_engine/ui/ (3 files)

### `npu_engine/ui/__init__.py` (0 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/ui/mandala_schema.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/ui/ui_vastu_engine.py` (1 lines)
- Route in kernel: no
- Status: STUB

## npu_engine/ui_vastu_engine.py/ (1 files)

### `npu_engine/ui_vastu_engine.py` (495 lines)
- Functions: _ring_xy, _compute_center_focus, _compute_layer_ring, _angle_to_zone, _compute_zone_regions, _compute_zone_action_state
- Route in kernel: YES
- Status: WORKING

## npu_engine/vastu_engine.py/ (1 files)

### `npu_engine/vastu_engine.py` (405 lines)
- Functions: _build_grid, _zone_weights_from_panchanga, _seasonal_rotation, _place_entities, derive_vastu_state
- Route in kernel: YES
- Status: WORKING

## npu_engine/vector_store.py/ (1 files)

### `npu_engine/vector_store.py` (698 lines)
- Classes: Chunk, VectorStore
- Functions: _get_st_model, _slug, _tokenize, _chunk_words, _read_text, _attestation_from_text
- Datasets: datasets/astro/, datasets/gandharva/, datasets/plants/
- Route in kernel: YES
- Status: WORKING

## npu_engine/vocal/ (10 files)

### `npu_engine/vocal/__init__.py` (16 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/vocal/bhava_engine.py` (81 lines)
- Classes: BhavaState
- Functions: _select_bhava, _lerp
- Route in kernel: no
- Status: WORKING

### `npu_engine/vocal/breath_engine.py` (98 lines)
- Classes: BreathMap
- Functions: get_breath_positions, _breath_duration
- Route in kernel: no
- Status: WORKING

### `npu_engine/vocal/gamaka_engine.py` (105 lines)
- Classes: GamakaInstruction
- Functions: get_gamaka, _build_instruction, _lerp
- Route in kernel: no
- Status: WORKING

### `npu_engine/vocal/graph_seed_data.py` (234 lines)
- Route in kernel: no
- Status: UNKNOWN

### `npu_engine/vocal/phoneme_graph.py` (90 lines)
- Functions: get_formant_profile, get_phonemes_for_deity, get_phonemes_for_element, get_phonemes_for_chakra, get_syllable_sequence, get_rasa_for_syllable
- Route in kernel: no
- Status: WORKING

### `npu_engine/vocal/svara_voice.py` (70 lines)
- Classes: SvaraQuality
- Functions: get_svara_quality
- Route in kernel: no
- Status: WORKING

### `npu_engine/vocal/syllable_sequencer.py` (149 lines)
- Classes: VocalElement
- Functions: sequence_for_alap, sequence_for_bija, sequence_for_bol, _authority_for_role
- Route in kernel: no
- Status: WORKING

### `npu_engine/vocal/vocal_kernel.py` (201 lines)
- Classes: VocalKernel
- Functions: _confidence_delay
- Route in kernel: no
- Status: WORKING

### `npu_engine/vocal/vocal_osc.py` (110 lines)
- Classes: VocalOSC
- Route in kernel: no
- Status: WORKING

## npu_engine/yantra_engine.py/ (1 files)

### `npu_engine/yantra_engine.py` (295 lines)
- Functions: _euclidean_rhythm, _polygon_points, _lotus_petals, generate_yantra
- Route in kernel: YES
- Status: WORKING

## npu_engine/yantra_generator.py/ (1 files)

### `npu_engine/yantra_generator.py` (246 lines)
- Functions: _dim, _mid, _triangle_points, _petal_path, generate_yantra, yantra_data_for_field
- Field keys: psi, yantra, co_triangulars, panchanga
- Route in kernel: YES
- Status: WORKING

## npu_engine/zones/ (12 files)

### `npu_engine/zones/__init__.py` (3 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/zones/action.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/zones/archetype.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/zones/base.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/zones/body.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/zones/center.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/zones/codex.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/zones/ecology.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/zones/guild.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/zones/plant.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/zones/rhythm.py` (1 lines)
- Route in kernel: no
- Status: STUB

### `npu_engine/zones/sound.py` (1 lines)
- Route in kernel: no
- Status: STUB

## S-Layer Engine Coverage

- **S0**: 2 engines — goloka_engine.py, goloka_engine.py
- **S1**: 12 engines — build_field_state.py, field_state.py, toroidal_field.py, field_layers.py
- **S2**: 5 engines — sound_engine.py, field_to_sound.py, field_to_sound.py, sound_engine.py
- **S3**: 7 engines — rhythm_engine.py, trajectory_engine.py, cross_rhythm_engine.py, rhythm_kernel.py
- **S4**: 4 engines — yantra_engine.py, yantra_generator.py, yantra_engine.py, yantra_generator.py
- **S5**: 4 engines — s5_kernel.py, s5_kernel.py, plant_engine.py, plant.py
- **S6**: 0 engines

## Dependency Graph (top importers)

- `npu_engine/mandala_schema.py` imports 4 npu modules
- `npu_engine/field/composition_engine.py` imports 2 npu modules
- `npu_engine/field/land_engine.py` imports 2 npu modules
- `npu_engine/aspect_repair.py` imports 1 npu modules
- `npu_engine/core/__init__.py` imports 1 npu modules
- `npu_engine/generator.py` imports 1 npu modules
- `npu_engine/library_kernel.py` imports 1 npu modules
- `npu_engine/tanpura_engine.py` imports 1 npu modules
