# REL-003: Populate relations_raga_ritual.csv

**Phase**: 4  
**Priority**: MEDIUM  
**Estimated time**: 2–3 hrs

## Context

`datasets/relations/relations_raga_ritual.csv` exists but has 0 rows.
The data to populate it already exists across several CSVs — raga assignments
live in ashtakala.csv, daily_program.csv, gaudiya_festivals.csv, and raga_master.csv.
This task derives and writes the relation rows.

## Instructions

### Step 1: Read all source files

```bash
cat ~/atlas_core/datasets/cosmology/ashtakala.csv
cat ~/atlas_core/datasets/cosmology/daily_program.csv
cat ~/atlas_core/datasets/cosmology/gaudiya_festivals.csv
cat ~/atlas_core/datasets/sound/raga_master.csv
cat ~/atlas_core/datasets/relations/relations_raga_ritual.csv
```

Note the exact column schema of `relations_raga_ritual.csv` (even if empty, the header should exist).
If no header exists, use the canonical relation schema:
`from_id,relation,to_id,source_title,source_locator,excerpt,tradition,confidence,notes`

### Step 2: Write derivation script

Write `scripts/derive_raga_ritual_relations.py`:

Extract relations of the form:
- `raga:{id}` → `raga_prescribed_for` → `ashtakala:{period}` (from ashtakala.csv)
- `raga:{id}` → `raga_prescribed_for` → `festival:{id}` (from gaudiya_festivals.csv)
- `ashtakala:{period}` → `ashtakala_raga` → `raga:{id}` (inverse)

Use `category:slug` ID format. Slugify raga names to lowercase underscores.

Example output rows:
```
raga:bhairava,raga_prescribed_for,ashtakala:nisanta,Ashtakala CSV,cosmology/ashtakala.csv,,gaudiya_vaishnava,0.95,morning raga for pre-dawn period
raga:darbari,raga_prescribed_for,ashtakala:sayahna,Ashtakala CSV,cosmology/ashtakala.csv,,gaudiya_vaishnava,0.95,evening raga
```

### Step 3: Run and write

```bash
cd ~/atlas_core
python scripts/derive_raga_ritual_relations.py
```

Output to `datasets/relations/relations_raga_ritual.csv`.

### Step 4: Also populate from gaudiya_festivals.csv

```python
# gaudiya_festivals.csv has: festival_id, name, tithi, month, deity, raga
# derive: raga:{raga} → raga_prescribed_for → festival:{festival_id}
```

### Step 5: Verify

```bash
wc -l ~/atlas_core/datasets/relations/relations_raga_ritual.csv
head -5 ~/atlas_core/datasets/relations/relations_raga_ritual.csv
```

## Success check

```bash
python3 -c "
import csv
rows = list(csv.DictReader(open('datasets/relations/relations_raga_ritual.csv')))
assert len(rows) >= 8, f'Expected >= 8 rows, got {len(rows)}'
print(f'raga_ritual relations: {len(rows)} rows')
print('Sample:', rows[0])
"
```

## Output

- Write `scripts/derive_raga_ritual_relations.py`
- Populate `datasets/relations/relations_raga_ritual.csv` (was 0 rows)
