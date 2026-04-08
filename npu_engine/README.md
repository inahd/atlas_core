# NPU Engine — Relational Field Computation

The intelligence layer of Atlas 330. Loads 136 CSVs into a 3400-node
relational graph, resolves field state from panchanga + natal data,
and drives sound, geometry, and practice layers via OSC.

## Core

| File | Purpose |
|------|---------|
| `datasets.py` | Load & normalize all CSV datasets (entities, metadata, relations) |
| `graph_engine.py` | Canonical relation graph — query, expand, score |
| `build_field_state.py` | Construct FieldState from panchanga + graph |
| `field_state.py` | FieldState dataclass |
| `field_layers.py` | S0–S6 layer mapping |
| `field_to_sound.py` | Element → Sa, treatment vector, devi table |
| `coherence_engine_v2.py` | Entity reranking & active-relation extraction |
| `modulation_engine.py` | Semantic modulation (ψ derivation) |
| `lifecycle_engine.py` | Lifecycle phase computation |
| `orientation.py` | Entity signal & orientation from field |
| `layer_engine.py` | Per-layer entity summaries & data loading |

## Geometry & Topology

| File | Purpose |
|------|---------|
| `toroidal_field.py` | Torus coordinates for all entities |
| `torus_queries.py` | 108-pada torus knot distance queries |
| `temple_geometry.py` | Sacred geometry projections |
| `igpu.py` | 64-node spatial layout for SVG cosmos |
| `mandala_schema.py` | Vastu mandala zone resolver, CONTENT_TYPES, NAVIGATION |
| `vastu_engine.py` | Vastu zone activation from field |
| `ui_vastu_engine.py` | UI layout derivation from vastu |
| `yantra_engine.py` | Yantra generation |
| `yantra_generator.py` | Yantra data for field state |

## Sound & Performance

| File | Purpose |
|------|---------|
| `phrase_engine.py` | Live raga graph traversal → note events |
| `raga_graph.py` | Raga graph structures & JI ratios |
| `swara_engine.py` | Swara selection engine |
| `aspect_repair.py` | Aspect repair tables for swara |
| `tanpura_field.py` | Field → tanpura tuning parameters |
| `tanpura_engine.py` | Tanpura physics engine |
| `relational_params.py` | Field state → physical instrument parameters |
| `relational_synth.py` | Compute synth params from relations |
| `sarangi_voice.py` | Bowed gut string synthesis |
| `bija_synth.py` | Pure formant bija mantra synthesis |
| `tabla_sampler.py` | Tabla sample rendering |
| `natal_musician.py` | Natal chart → musician reading |
| `composition_db.py` | Playlist & mantra scheduling |
| `mudra_graph.py` | Mudra selection from field |

## Domain Engines

| File | Purpose |
|------|---------|
| `s5_kernel.py` | Plant wheel (3 rings: shastra/sadhu/guru) |
| `card_engine.py` | Devi tarot card engine |
| `codex_engine.py` | Sacred manuscript study modes |
| `codex_interaction.py` | Entity → codex passages & paths |
| `codex_modes.py` | Codex mode definitions |
| `library_kernel.py` | Library state builder |
| `passage_resolver.py` | Find relevant text passages |
| `relational_engine.py` | Relational graph operations |
| `treasury.py` | Treasury resolution |
| `vector_store.py` | Vector similarity store |

## Query & Generation

| File | Purpose |
|------|---------|
| `query_engine.py` | Graph query interface |
| `generator.py` | Entity generation & path finding |
| `path_engine.py` | Path finding & flow detection |

## Subpackages

| Directory | Purpose |
|-----------|---------|
| `engines/` | S0–S6 domain engine classes (CENTER, ENGINE_MAP) |
| `mix/` | 11-layer mix graph → OSC |
| `rhythm/` | Tala/theka/tihai/layakari → OSC |
| `sympathetic/` | 13 taraf strings → OSC |
| `vocal/` | Formant vocal engine (not yet wired) |

## Retired → `purana/npu_legacy/`

Files moved out of active tree (unused or superseded):

`attention_vector.py`, `cello_voice.py`, `coherence_engine.py`,
`entity_resolver.py`, `hex_projection.py`, `iching_edges.py`,
`om_audio.py`, `om_engines.py`, `relational_repair.py`,
`rules_engine.py`, `sound_engine.py`, `species_repair.py`,
`tradition_weights.py`, `vocal_relational.py`
