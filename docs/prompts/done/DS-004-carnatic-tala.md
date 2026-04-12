# DS-004: Wire carnatic/ datasets to tala_graph.py

**Phase**: 4 — Expand dark territory  
**Priority**: MEDIUM  
**Estimated time**: 1 day

## Context

`npu_engine/rhythm/tala_graph.py` exists (75 lines) and is WORKING, but uses
hardcoded tala data instead of reading from the 7 rich carnatic CSVs.

`npu_engine/rhythm/graph_seed_data.py` (274 lines) already has functions
`get_gati_definitions()`, `get_tala_families()`, `get_korvai_rules()`, `get_sollukattu()`
that load from `datasets/carnatic/`. Wire tala_graph.py to use these.

## Instructions

### Step 1: Read everything first

```bash
cat ~/atlas_core/npu_engine/rhythm/tala_graph.py
cat ~/atlas_core/npu_engine/rhythm/graph_seed_data.py
head -5 ~/atlas_core/datasets/carnatic/tala_master.csv
head -5 ~/atlas_core/datasets/carnatic/35_talas.csv
head -5 ~/atlas_core/datasets/carnatic/tala_families.csv
head -5 ~/atlas_core/datasets/carnatic/gati_definitions.csv
```

### Step 2: Understand the current hardcoded data

In `tala_graph.py`, find the hardcoded tala dictionaries. Map each hardcoded field
to the corresponding CSV column.

### Step 3: Refactor tala_graph.py

- Replace hardcoded data with lazy-loaded CSV data via `graph_seed_data.py`
- `get_tala()` should read from `tala_master.csv` by tala id
- `get_theka()` should read bol sequence from `35_talas.csv`
- `get_bol_properties()` should read from `carnatic/sollukattu.csv`
- `get_rasa_tala_affinity()` should use `tala_families.csv` graha_correspondence → rasa
- Preserve the existing function signatures — do not break callers

### Step 4: Test

```bash
cd ~/atlas_core
python3 -c "
from npu_engine.rhythm.tala_graph import get_tala, get_theka
t = get_tala('adi')
print('Adi tala:', t)
theka = get_theka('adi')
print('Theka:', theka[:5] if theka else 'None')
"
```

### Step 5: Verify route still works

```bash
curl -s localhost:5000/field | python3 -c "import sys,json; d=json.load(sys.stdin); print('field OK')"
# Sound spec should still generate without errors
curl -s localhost:5000/sound/spec | python3 -c "import sys,json; d=json.load(sys.stdin); print('sound_spec OK')"
```

## Success check

```bash
python3 -c "
from npu_engine.rhythm.tala_graph import get_tala, TalaStructure
t = get_tala('rupaka')
assert t is not None, 'get_tala returned None'
assert hasattr(t, 'beat_count') or isinstance(t, dict), 'unexpected type'
print('tala_graph CSV wiring: OK')
"
```

## Output

- Modify `npu_engine/rhythm/tala_graph.py`
- No new files required
