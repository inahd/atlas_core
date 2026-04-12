# REL-006: Add Gaudiya composition relations

**Phase**: 4  
**Priority**: MEDIUM  
**Estimated time**: 2–3 hrs

## Context

`datasets/compositions/narottama_padas.csv` (8 rows), `gaudiya_compositions.csv` (21 rows),
and `nakshatra_kritis.csv` (12 rows) exist but are not wired into the relation graph.
These connect compositions to raga, tala, ashtakala, lila, and deity —
critical for the Gaudiya Vaishnava presentation and for the reading_engine's
composition selection.

## Instructions

### Step 1: Read all composition files

```bash
cat ~/atlas_core/datasets/compositions/narottama_padas.csv
cat ~/atlas_core/datasets/compositions/gaudiya_compositions.csv
cat ~/atlas_core/datasets/cosmology/ashtakala.csv
cat ~/atlas_core/datasets/cosmology/goloka/ashtakala_lila.csv
```

### Step 2: Read composition_db.py and reading_engine.py

```bash
cat ~/atlas_core/npu_engine/composition_db.py | head -80
grep -n "composition\|pada\|narottama" ~/atlas_core/npu_engine/field/reading_engine.py | head -20
```

Understand how compositions are currently selected.

### Step 3: Write derivation script

Write `scripts/derive_composition_relations.py`:

Derive the following relation types:
- `composition:{id}` → `composition_raga` → `raga:{id}` (from raga column)
- `composition:{id}` → `composition_tala` → `tala:{id}` (from tala column)
- `composition:{id}` → `composition_ashtakala` → `ashtakala:{period}` (from lila_reference or ashtakala_period)
- `composition:{id}` → `composition_deity` → `deity:{id}` (from deity column)
- `composition:{id}` → `composed_by` → `composer:{name}` (from composer column)

Output to `datasets/relations/composition_relations.csv`.

For Narottama das Thakura padas specifically, also link to:
- goloka topology: `composition:{id}` → `evokes_vraja_forest` → `vraja_forest:{id}`
  (derive from lila_reference or ashtakala period mapping)

### Step 4: Wire composition_db.py to use the relation graph

```bash
cat ~/atlas_core/npu_engine/composition_db.py
```

`composition_db.py` already loads compositions from CSVs. After this task,
it should also load `composition_relations.csv` to enable graph-traversal-based
composition selection (find compositions related to current field entities).

Add to `composition_db.py`:
```python
def get_compositions_for_entity(entity_id: str) -> list:
    """Find compositions related to an entity via composition_relations.csv"""
    ...
```

### Step 5: Test

```bash
cd ~/atlas_core
python3 -c "
from npu_engine.composition_db import get_compositions_for_entity
results = get_compositions_for_entity('raga:darbari')
print('Compositions for Darbari:', results[:3])
results = get_compositions_for_entity('ashtakala:sayahna')
print('Compositions for evening:', results[:3])
"
```

## Success check

```bash
python3 -c "
import csv
rows = list(csv.DictReader(open('datasets/relations/composition_relations.csv')))
assert len(rows) >= 20, f'Expected >= 20, got {len(rows)}'
preds = set(r['relation'] for r in rows)
print(f'composition_relations: {len(rows)} rows, predicates: {preds}')
"
```

## Output

- Write `scripts/derive_composition_relations.py`
- Create `datasets/relations/composition_relations.csv`
- Add `get_compositions_for_entity()` to `npu_engine/composition_db.py`
