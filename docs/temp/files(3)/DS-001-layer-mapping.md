# DS-001: Create datasets/layer_mapping.csv

**Phase**: 1 — Stop the bleeding  
**Priority**: CRITICAL  
**Estimated time**: 30 min  
**Blocks**: RTE-003 (/layers routes)

## Context

`npu_engine/layer_engine.py` reads `datasets/layer_mapping.csv` at startup.
This file is missing, causing the /layers and /layers/summary routes to 500.

## Instructions

1. Read `npu_engine/layer_engine.py` fully — find every column it reads from the CSV
2. Read `npu_engine/field_layers.py` — find any additional layer/dataset mappings
3. Read `kernel.py` grep for `layer_engine` — understand what the route expects back
4. Examine existing dataset subdirectories in `datasets/` to understand the domain names

Build the CSV to match exactly what `layer_engine.py` expects. Do not guess columns —
read the loader code first.

## Expected schema (verify against layer_engine.py before creating)

The file likely needs columns mapping S-layers to dataset domains. Based on the engine:
- `layer` — S0 through S6
- `domain` — dataset subdirectory name
- `dataset` — specific CSV filename
- `entity_type` — what kind of entity this layer covers
- `description` — human-readable

## Success check

```bash
curl -s localhost:5000/layers | python3 -c "import sys,json; d=json.load(sys.stdin); print('OK:', len(d))"
curl -s localhost:5000/layers/summary | python3 -c "import sys,json; d=json.load(sys.stdin); print('OK')"
```

Both should return OK, not 500.

## Output

- Create: `datasets/layer_mapping.csv`
- No other files modified
