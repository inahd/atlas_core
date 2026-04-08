# Missing Dependencies Audit — 2026-04-08

56 local module imports in kernel.py. 55 present, 1 missing.

## Results

| Import | Status | Found at | Action |
|--------|--------|----------|--------|
| `core.coherence_engine` | **RECOVERED** | `atlas_330 git:289f494` | Recovered from git history, fixed CSV paths |
| `npu_engine.bija_synth` | OK | — | — |
| `npu_engine.build_field_state` | OK | — | — |
| `npu_engine.card_engine` | OK | — | — |
| `npu_engine.codex_interaction` | OK | — | — |
| `npu_engine.coherence_engine_v2` | OK | — | — |
| `npu_engine.composition_db` | OK | — | — |
| `npu_engine.datasets` | OK | — | — |
| `npu_engine.engines` | OK | — | — |
| `npu_engine.engines.guild_engine` | OK | — | — |
| `npu_engine.engines.plant_engine` | OK | — | — |
| `npu_engine.field.composition_engine` | OK | — | — |
| `npu_engine.field.goloka_engine` | OK | — | — |
| `npu_engine.field.guild_planner` | OK | — | — |
| `npu_engine.field.helix_engine` | OK | — | — |
| `npu_engine.field.intention_engine` | OK | — | — |
| `npu_engine.field.land_engine` | OK | — | — |
| `npu_engine.field_layers` | OK | — | — |
| `npu_engine.field.reading_engine` | OK | — | — |
| `npu_engine.field.region_engine` | OK | — | — |
| `npu_engine.field.ring_engine` | OK | — | — |
| `npu_engine.field.site_engine` | OK | — | — |
| `npu_engine.field.symbol_engine` | OK | — | — |
| `npu_engine.field.system_engine` | OK | — | — |
| `npu_engine.field_to_sound` | OK | — | — |
| `npu_engine.field.trajectory_engine` | OK | — | — |
| `npu_engine.game.character_engine` | OK | — | — |
| `npu_engine.game.lineage_engine` | OK | — | — |
| `npu_engine.game.orientation_engine` | OK | — | — |
| `npu_engine.graph_engine` | OK | — | — |
| `npu_engine.igpu` | OK | — | — |
| `npu_engine.layer_engine` | OK | — | — |
| `npu_engine.library_kernel` | OK | — | — |
| `npu_engine.mandala_schema` | OK | — | — |
| `npu_engine.mix.layer_graph` | OK | — | — |
| `npu_engine.natal_musician` | OK | — | — |
| `npu_engine.orientation` | OK | — | — |
| `npu_engine.passage_resolver` | OK | — | — |
| `npu_engine.path_engine` | OK | — | — |
| `npu_engine.query_engine` | OK | — | — |
| `npu_engine.relational_engine` | OK | — | — |
| `npu_engine.renderers.figure_renderer` | OK | — | — |
| `npu_engine.renderers.species_renderer` | OK | — | — |
| `npu_engine.s5_kernel` | OK | — | — |
| `npu_engine.sound.osc_bridge` | OK | — | — |
| `npu_engine.sound.sound_engine` | OK | — | — |
| `npu_engine.swara_engine` | OK | — | — |
| `npu_engine.temple_geometry` | OK | — | — |
| `npu_engine.toroidal_field` | OK | — | — |
| `npu_engine.torus_queries` | OK | — | — |
| `npu_engine.treasury` | OK | — | — |
| `npu_engine.ui_vastu_engine` | OK | — | — |
| `npu_engine.vastu_engine` | OK | — | — |
| `npu_engine.vector_store` | OK | — | — |
| `npu_engine.yantra_engine` | OK | — | — |
| `npu_engine.yantra_generator` | OK | — | — |
| `scripts.ollama_client` | OK | — | — |

## Fix applied

- `core/__init__.py` created (make `core/` a Python package)
- `core/coherence_engine.py` recovered from `atlas_330` git history (commit `289f494`)
- CSV paths updated: `cosmology/tithi_deities.csv` → `astro/tithi_deities.csv`, etc.
- Vector store fallback works (rule-only scoring when embeddings unavailable)

## Notes

- `CoherenceEngine` uses `score_hybrid(tithi_num, limit, fs)` → returns `[CoherenceScore]`
- Each `CoherenceScore` has: `.score`, `.candidate`, `.reasons`, `.node_class`
- Falls back to rule-only scoring when vector store is absent
- `/coherence-score` endpoint should now return real scores instead of `{"error": "CoherenceEngine not available"}`
