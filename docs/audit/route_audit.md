# Kernel Route Audit

Date: 2026-04-10

## Total Routes: 203

## Corpus/Research (8 routes)

| Path | Method | Function | Engine | Health |
|------|--------|----------|--------|--------|
| `/corpus/registry` | GET | _corpus_registry | — | PARTIAL |
| `/corpus/read` | GET | _corpus_read | — | PARTIAL |
| `/corpus/search` | GET | _corpus_search | — | PARTIAL |
| `/research/files` | GET | research_files | — | PARTIAL |
| `/research/file` | GET | research_file | — | PARTIAL |
| `/research/save` | "POST" | research_save | — | PARTIAL |
| `/research/gaps` | GET | research_gaps | — | PARTIAL |
| `/research/datasets` | GET | research_datasets | — | PARTIAL |

## Field/Spine (9 routes)

| Path | Method | Function | Engine | Health |
|------|--------|----------|--------|--------|
| `/field/override` | "POST", "DELETE" | _field_override_route | — | PARTIAL |
| `/field` | GET | _field | — | PARTIAL |
| `/observe` | "POST" | _observe | — | PARTIAL |
| `/spine` | GET | _spine | — | PARTIAL |
| `/field-stream` | GET | _field_stream | — | PARTIAL |
| `/yantra/field` | GET | _yantra_field | — | PARTIAL |
| `/symbols/field` | GET | _symbols_field | symbol_engine | FULL |
| `/glyphs/field` | GET | _glyphs_field | symbol_engine | FULL |
| `/plants/field` | GET | _plants_field | plant_engine | FULL |

## Other (92 routes)

| Path | Method | Function | Engine | Health |
|------|--------|----------|--------|--------|
| `/osc` | "POST", "OPTIONS" | _osc_proxy | — | PARTIAL |
| `/entity/<path:entity_id>` | GET | _entity | — | PARTIAL |
| `/interpret` | GET | _interpret | — | PARTIAL |
| `/attend` | "POST" | _attend | — | PARTIAL |
| `/natal` | GET | _natal | orientation | FULL |
| `/orientation` | GET | _orientation | orientation | FULL |
| `/interact` | "POST" | _interact | orientation | FULL |
| `/claims` | GET | _claims | — | PARTIAL |
| `/playlist` | GET | _playlist | — | PARTIAL |
| `/observance` | GET | _observance | — | PARTIAL |
| `/navigate` | "POST" | _navigate | — | PARTIAL |
| `/transits` | GET | _transits | — | PARTIAL |
| `/dasha` | GET | _dasha | — | PARTIAL |
| `/mode/contract` | GET | _mode_contract | — | PARTIAL |
| `/mode/surface/<surface>` | GET | _mode_for_surface | — | PARTIAL |
| `/visual/state` | GET | _visual_state | — | PARTIAL |
| `/bija/<bija_id>/play` | "POST", "GET" | _bija_play | — | PARTIAL |
| `/bija/<bija_id>/synthesize` | "POST", "GET" | _bija_synthesize | — | PARTIAL |
| `/musician` | GET | _musician | natal_musician | FULL |
| `/compose` | "GET", "POST" | _compose | — | PARTIAL |
| `/compose/variation` | "POST" | _compose_variation | — | PARTIAL |
| `/mandala/layout` | GET | _mandala_layout | — | PARTIAL |
| `/knowledge/relational` | GET | _knowledge_relational | — | PARTIAL |
| `/altar` | GET | _altar_get | — | PARTIAL |
| `/altar` | "POST" | _altar_update | — | PARTIAL |
| `/library` | GET | _library | — | PARTIAL |
| `/muhurta-quality` | GET | _muhurta_quality | — | PARTIAL |
| `/coherence-score` | GET | _coherence_score | — | PARTIAL |
| `/coherence` | GET | _coherence_route | — | PARTIAL |
| `/generate-composition` | GET | _generate_composition | — | PARTIAL |
| `/journal/save` | "POST" | _journal_save_legacy | — | PARTIAL |
| `/query/entity` | GET | _query_entity | — | PARTIAL |
| `/layers/summary` | GET | _layers_summary | layer_engine | FULL |
| `/hexfield-data` | GET | _hexfield_data | — | PARTIAL |
| `/coherence-field` | GET | _coherence_field | — | PARTIAL |
| `/vastu` | GET | _vastu_field | — | PARTIAL |
| `/s3/practice` | GET | _s3_practice | — | PARTIAL |
| `/bandhu/chat` | "POST" | _bandhu_chat | — | PARTIAL |
| `/bandhu/chat/full` | "POST" | _bandhu_chat_full | — | PARTIAL |
| `/graph/entities` | GET | _graph_entities | datasets | FULL |
| `/tarot/deck/<deck>` | GET | _tarot_deck | — | PARTIAL |
| `/tarot/draw` | "POST" | _tarot_draw | — | PARTIAL |
| `/layer-data` | GET | _layer_data | — | PARTIAL |
| `/layers` | GET | _layers | layer_engine | FULL |
| `/layers/<layer>` | GET | _layer_detail | — | PARTIAL |
| `/ollama` | "POST" | _ollama_proxy | — | PARTIAL |
| `/helix` | GET | _helix | helix_engine | FULL |
| `/passages` | GET | _passages | — | PARTIAL |
| `/shell/state` | GET | _shell_state | — | PARTIAL |
| `/beat` | "POST" | _beat_post | — | PARTIAL |
| `/beat` | GET | _beat_stream | — | PARTIAL |
| `/npu-commentary` | GET | _npu_commentary | — | PARTIAL |
| `/brahmanda/state` | GET | _brahmanda_state | — | PARTIAL |
| `/kala/day/data` | GET | _kala_day_data | — | PARTIAL |
| `/kala/week/data` | GET | _kala_week_data | — | PARTIAL |
| `/kala/month/data` | GET | _kala_month_data | — | PARTIAL |
| `/music/<int:tithi>` | GET | _music | — | PARTIAL |
| `/practice/<int:tithi>` | GET | _practice | — | PARTIAL |
| `/agriculture/today` | GET | _agri_today | — | PARTIAL |
| `/agriculture/week` | GET | _agri_week | — | PARTIAL |
| `/agriculture/month` | GET | _agri_month | — | PARTIAL |
| `/generated/mandala` | GET | _gen_mandala | — | PARTIAL |
| `/generated/tala` | GET | _gen_tala | — | PARTIAL |
| `/generated/<key>` | GET | _get_generated | — | PARTIAL |
| `/generated/save` | "POST" | _save_generated | — | PARTIAL |
| `/generated/list` | GET | _list_generated | — | PARTIAL |
| `/docs-list` | GET | _docs_list | — | PARTIAL |
| `/docs/<path:filename>` | GET | _docs | — | PARTIAL |
| `/item/<item_name>` | GET | _item_query | — | PARTIAL |
| `/vahana/<vahana>` | GET | _vahana_query | — | PARTIAL |
| `/gemstone/<gem>` | GET | _gemstone_query | — | PARTIAL |
| `/treasury` | GET | _treasury | treasury | FULL |
| `/wheel/options` | GET | _wheel_options | — | PARTIAL |
| `/wheel` | GET | _wheel | — | PARTIAL |
| `/intention/classify` | "POST" | _intention_classify | intention_engine | FULL |
| `/intention/windows` | "POST" | _intention_windows | intention_engine | FULL |
| `/intention/now` | GET | _intention_now | intention_engine | FULL |
| `/calendar/day` | GET | _calendar_day | — | PARTIAL |
| `/journal` | "GET" | _journal_list | — | PARTIAL |
| `/journal` | "POST" | _journal_save | — | PARTIAL |
| `/trajectory` | GET | _trajectory | trajectory_engine | FULL |
| `/goloka` | GET | _goloka | goloka_engine | FULL |
| `/character` | GET | _character | character_engine | FULL |
| `/character/lineages` | GET | _character_lineages | lineage_engine | FULL |
| `/character/orientation` | GET | _character_orientation | orientation_engine | FULL |
| `/hexd/object` | GET | _hexd_object_payload | — | PARTIAL |
| `/site/state` | GET | _site_state | — | PARTIAL |
| `/site/swales` | GET | _site_swales | — | PARTIAL |
| `/site/suitability` | GET | _site_suitability | — | PARTIAL |
| `/api` | GET | _api_index | — | PARTIAL |
| `/apps/<path:name>` | GET | serve_app | — | PARTIAL |
| `/widgets/<path:name>` | GET | widgets | — | PARTIAL |

## Plants/Land (22 routes)

| Path | Method | Function | Engine | Health |
|------|--------|----------|--------|--------|
| `/plants/today` | GET | _plants_today | — | PARTIAL |
| `/plants/season` | GET | _plants_season | — | PARTIAL |
| `/plants/catalog` | GET | _plants_catalog | — | PARTIAL |
| `/plants/search` | GET | _plants_search | — | PARTIAL |
| `/plants/guild/<nakshatra_id>` | GET | _plants_guild | — | PARTIAL |
| `/plants/related/<path:entity_id>` | GET | _plants_related | graph_engine | FULL |
| `/plants/guild_matrix` | GET | _plants_guild_matrix | — | PARTIAL |
| `/plants/region` | GET | _plants_region | — | PARTIAL |
| `/plants/<path:plant_key>` | GET | _plants_lookup | — | PARTIAL |
| `/guild/generate` | "POST" | _guild_generate | — | PARTIAL |
| `/guild/search` | GET | _guild_search | — | PARTIAL |
| `/guild/state` | GET | _guild_state | guild_engine | FULL |
| `/guild/timing` | GET | _guild_timing | guild_engine | FULL |
| `/guild/plan` | GET | _guild_plan | guild_planner | FULL |
| `/guild/plan/current` | GET | _guild_plan_current | guild_planner | FULL |
| `/land` | GET | _land | land_engine | FULL |
| `/land/plot` | "POST" | _land_plot | land_engine | FULL |
| `/land/layout` | GET | _land_layout | land_engine | FULL |
| `/land/mandala` | GET | _land_mandala | land_engine | FULL |
| `/land/mandala/recommend` | "POST" | _land_mandala_recommend | — | PARTIAL |
| `/plants/entity/<path:plant_id>` | GET | _plant_entity | — | PARTIAL |
| `/plants/schema` | GET | _plants_schema | — | PARTIAL |

## Reading/Oracle (15 routes)

| Path | Method | Function | Engine | Health |
|------|--------|----------|--------|--------|
| `/card/draw` | "POST" | _card_draw | card_engine | FULL |
| `/card/spread` | "POST" | _card_spread_post | card_engine | FULL |
| `/card/deck/<deck>` | GET | _card_deck | card_engine | FULL |
| `/codex-context` | GET | _codex_context | — | PARTIAL |
| `/codex/generate` | "POST" | _codex_generate | — | PARTIAL |
| `/codex/entity/<path:entity_id>` | GET | _codex_entity | codex_interaction | FULL |
| `/codex/paths/<path:entity_id>` | GET | _codex_paths | codex_interaction | FULL |
| `/codex/cluster` | "POST" | _codex_cluster | — | PARTIAL |
| `/archana/cards` | GET | _archana_cards | — | PARTIAL |
| `/generated/card_spread` | GET | _card_spread | — | PARTIAL |
| `/reading` | "POST" | _reading | reading_engine | FULL |
| `/reading/tarot` | GET | _reading_tarot | reading_engine | FULL |
| `/reading/iching` | GET | _reading_iching | reading_engine | FULL |
| `/reading/bandhu` | GET | _reading_bandhu | reading_engine | FULL |
| `/reading/context` | GET | _reading_context | reading_engine | FULL |

## Render/Geometry (14 routes)

| Path | Method | Function | Engine | Health |
|------|--------|----------|--------|--------|
| `/render/toroid` | "POST", "GET" | _render_toroid | — | PARTIAL |
| `/render` | GET | _render | — | PARTIAL |
| `/render/eternal` | GET | _render_eternal | — | PARTIAL |
| `/render/4d` | GET | _render_4d | — | PARTIAL |
| `/render/stream` | GET | _render_stream | — | PARTIAL |
| `/yantra` | GET | _yantra | yantra_engine | FULL |
| `/codex/render` | "POST" | _codex_render | — | PARTIAL |
| `/yantra/svg` | GET | _yantra_svg | yantra_generator | FULL |
| `/yantra/data` | GET | _yantra_field_data | yantra_generator | FULL |
| `/yantra-data` | GET | _yantra_data | — | PARTIAL |
| `/yantra/deposit` | "POST" | _yantra_deposit | — | PARTIAL |
| `/render/bandhu` | GET | _render_bandhu | figure_renderer | FULL |
| `/render/species/<species_id>` | GET | _render_species | species_renderer | FULL |
| `/render/shrine` | GET | _render_shrine | figure_renderer | FULL |

## S-layers (8 routes)

| Path | Method | Function | Engine | Health |
|------|--------|----------|--------|--------|
| `/s5` | GET | _s5 | — | PARTIAL |
| `/s0` | GET | s0 | — | PARTIAL |
| `/s1` | GET | s1 | — | PARTIAL |
| `/s2` | GET | s2 | — | PARTIAL |
| `/s3` | GET | s3 | — | PARTIAL |
| `/s4` | GET | s4 | — | PARTIAL |
| `/s5` | GET | s5 | — | PARTIAL |
| `/s6` | GET | s6 | — | PARTIAL |

## Sound (16 routes)

| Path | Method | Function | Engine | Health |
|------|--------|----------|--------|--------|
| `/sound/spec` | GET | _sound_spec | graph_engine | FULL |
| `/sound/volume` | "GET", "POST" | _sound_volume | — | PARTIAL |
| `/sound/state` | GET | _sound_state | — | PARTIAL |
| `/sound/relational` | GET | _sound_relational | — | PARTIAL |
| `/sound/raga` | "POST" | _sound_raga | — | PARTIAL |
| `/sound/play_note` | "POST" | _sound_play_note | — | PARTIAL |
| `/sound/voice` | "POST" | _sound_voice | — | PARTIAL |
| `/sound/mantra` | "POST" | _sound_mantra | — | PARTIAL |
| `/sound/bols` | "POST" | _sound_bols | — | PARTIAL |
| `/sound/perform_mode` | "POST" | _sound_perform_mode | — | PARTIAL |
| `/sound/perform_mode` | GET | _get_perform_mode | — | PARTIAL |
| `/sound/stop` | "POST" | _sound_stop | — | PARTIAL |
| `/sound/mode` | "GET", "POST" | _sound_mode_endpoint | — | PARTIAL |
| `/sound/mix/state` | GET | _sound_mix_state | — | PARTIAL |
| `/sound/recommend` | GET | _sound_recommend | — | PARTIAL |
| `/sound/freesound-key` | GET | _sound_freesound_key | — | PARTIAL |

## Static/Pages (7 routes)

| Path | Method | Function | Engine | Health |
|------|--------|----------|--------|--------|
| `/` | GET | _index | — | PARTIAL |
| `/home` | GET | _home | — | PARTIAL |
| `/static/<path:name>` | GET | serve_static | — | PARTIAL |
| `/glyphs` | GET | _glyphs_page | — | PARTIAL |
| `/assets/wesnoth/<path:filename>` | GET | _wesnoth_assets | — | PARTIAL |
| `/hexd-portal` | GET | _hexd_portal | — | PARTIAL |
| `/dashboard` | GET | dashboard | — | PARTIAL |

## Symbols/Rings (6 routes)

| Path | Method | Function | Engine | Health |
|------|--------|----------|--------|--------|
| `/symbol/<path:symbol>` | GET | _symbol_lookup | symbol_engine | FULL |
| `/symbols/stats` | GET | _symbols_stats | symbol_engine | FULL |
| `/glyphs/all` | GET | _glyphs_all | symbol_engine | FULL |
| `/glyphs/<path:entity_id>` | GET | _glyph_lookup | symbol_engine | FULL |
| `/rings` | GET | rings | ring_engine | FULL |
| `/ring/<ring_id>` | GET | ring | ring_engine | FULL |

## System (6 routes)

| Path | Method | Function | Engine | Health |
|------|--------|----------|--------|--------|
| `/health` | GET | _health | — | PARTIAL |
| `/system/state` | GET | _system_state | system_engine | FULL |
| `/system/audio` | GET | _system_audio | system_engine | FULL |
| `/system/audio/restore` | "POST" | _system_audio_restore | system_engine | FULL |
| `/system/services` | GET | _system_services | — | PARTIAL |
| `/snapshot` | 'POST' | _snapshot | — | PARTIAL |

## Health Summary

- **FULL**: 55 routes
- **PARTIAL**: 148 routes
- **STUB**: 0 routes
