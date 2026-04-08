# NPU Engine

24 Python modules in `npu_engine/`. Core computation layer.

## Key Modules

### Data Layer
| Module | Purpose |
|--------|---------|
| `datasets.py` | Loads all 110 CSVs, builds entity metadata + relation graph |
| `toroidal_field.py` | Toroidal coordinates — theta/phi mapping, field_query() |
| `coherence_engine.py` | Coherence scoring from toroidal distance |

### Graph Layer
| Module | Purpose |
|--------|---------|
| `graph_engine.py` | `GraphEngine` — neighbor lookup, expansion, path finding |
| `path_engine.py` | `find_paths()`, `rank_paths()`, `format_path()`, `detect_flows()` |
| `query_engine.py` | `query()` — focused entity search with boost/filter |

### Codex Layer
| Module | Purpose |
|--------|---------|
| `codex_engine.py` | `generate()` — brief/practice/study/commentary artifacts |
| `codex_interaction.py` | `codex_from_entity()`, `codex_from_cluster()`, `paths_from_entity()` |
| `codex_modes.py` | Mode definitions for codex generation |

### Sound Layer
| Module | Purpose |
|--------|---------|
| `sound_engine.py` | Sound state derivation from field |
| `mix/mix_kernel.py` | MixKernel — 11-layer amplitude mixing driven by rasa/arc/element |
| `mix/layer_graph.py` | `get_layer_weights()` — rasa-based layer amplitude computation |

### Structure Layer
| Module | Purpose |
|--------|---------|
| `layer_engine.py` | S-layer dataset mapping, `all_layer_summaries()` |
| `build_field_state.py` | Full field state construction from panchanga |
| `temple_geometry.py` | Vastu-based spatial geometry |
| `field_state.py` | Field state dataclass |
| `relational_engine.py` | Relational sound/dance law computation |

## Usage from kernel.py

```python
# Graph traversal
from npu_engine.graph_engine import GraphEngine
g = GraphEngine()
neighbors = g.get_neighbors('nakshatra_rohini')
expanded = g.expand_from_entities(['nakshatra_rohini'], depth=2)

# Codex generation
from npu_engine.codex_interaction import codex_from_entity
text = codex_from_entity(field_state(), 'nakshatra_rohini', mode='brief')

# Query
from npu_engine.query_engine import query
result = query(field_state(), focus='nakshatra_rohini', depth=2, top_n=10)

# Mix weights
from npu_engine.mix.layer_graph import get_layer_weights
weights = get_layer_weights('shringara', 0.5, 'gat')
```

## Consolidated Interface

`npu/graph.py` re-exports all graph/path/query/codex functions.
`npu/renderers.py` merges all tabla/sarod/voice/dance/visual renderers.

```python
from npu.graph import GraphEngine, query, format_path, codex_from_entity
from npu.renderers import render_tabla, render_sarod, render_voice
```
