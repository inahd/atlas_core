# REL-002: Build entity ID registry

**Phase**: 3 — Data integrity  
**Priority**: HIGH  
**Estimated time**: 2–3 hrs  
**Blocks**: REL-001 (ID normalization)

## Context

1,682 of 1,687 relation subjects are "unresolved" — not because entities don't exist,
but because there is no canonical ID registry to resolve against. The live entity space
is distributed across domain CSVs. This task builds that registry.

## Instructions

### Step 1: Survey all domain CSVs for ID columns

```bash
cd ~/atlas_core
python3 -c "
import csv, os, glob

id_cols = ['id', 'graha_id', 'nakshatra_id', 'tithi_id', 'deity_id',
           'entity_id', 'species_id', 'herb_id', 'site_id', 'chakra_id',
           'dhatu_id', 'tala_id', 'raga_id', 'pitha_id', 'metre_id']

results = []
for f in glob.glob('datasets/**/*.csv', recursive=True):
    if 'relations' in f: continue
    try:
        with open(f) as fh:
            reader = csv.DictReader(fh)
            if not reader.fieldnames: continue
            matched = [c for c in reader.fieldnames if c in id_cols]
            if matched:
                rows = list(reader)
                print(f'{f}: {matched[0]} ({len(rows)} rows)')
    except: pass
"
```

### Step 2: Write the registry builder

Write `scripts/build_entity_registry.py` that:

1. Scans all domain CSVs for ID-like columns
2. For each file with an ID column:
   - Reads all rows
   - Determines the entity type from the filename or a `type` column
   - Generates canonical IDs in `category:slug` format
   - The slug is the lowercase, hyphen-normalized name
3. Outputs `datasets/entities/entity_registry.csv` with columns:
   `entity_id, entity_type, name, name_iast, source_file, row_index`

Canonical ID format rules:
```python
# entity_type:slug where slug = name.lower().replace(' ', '_').replace('-', '_')
# nakshatra:ashvini (not nakshatra:1, not nakshatra_ashvini)
# graha:chandra (not graha:moon, not graha:soma — use Sanskrit name)
# tithi:pratipada (not tithi:1)
# devi:kameshvari (not devi:1)

ENTITY_TYPE_MAP = {
    'nakshatra_master': 'nakshatra',
    'nakshatra_core': 'nakshatra',
    'grahas': 'graha',
    'graha_master': 'graha',
    'tithi_master': 'tithi',
    'nitya_devi_master': 'devi',
    'deity_master': 'deity',
    'tala_master': 'tala',
    'raga_master': 'raga',
    'marma_field': 'marma',
    # etc. — infer from filename
}
```

### Step 3: Run and review

```bash
cd ~/atlas_core
python scripts/build_entity_registry.py
wc -l datasets/entities/entity_registry.csv
head -20 datasets/entities/entity_registry.csv
```

### Step 4: Check coverage against relation subjects

```bash
python3 -c "
import csv

registry = {}
with open('datasets/entities/entity_registry.csv') as f:
    for row in csv.DictReader(f):
        registry[row['entity_id']] = row

relation_files = ['datasets/relations/deity_relations.csv',
                  'datasets/relations/species_relations.csv',
                  'datasets/relations/vastu_relations.csv']

unresolved = set()
for rf in relation_files:
    try:
        with open(rf) as f:
            for row in csv.DictReader(f):
                subj = row.get('from_id', '')
                if subj and subj not in registry:
                    unresolved.add(subj)
    except: pass

print(f'Registry size: {len(registry)}')
print(f'Sample unresolved: {list(unresolved)[:10]}')
"
```

## Success check

```bash
wc -l ~/atlas_core/datasets/entities/entity_registry.csv
# Should be > 200 rows

python3 -c "
import csv
reg = list(csv.DictReader(open('datasets/entities/entity_registry.csv')))
types = set(r['entity_type'] for r in reg)
print('Entity types:', sorted(types))
print('Total entities:', len(reg))
"
# Should show nakshatra(27), graha(9), tithi(30), devi(15), etc.
```

## Output

- Write `scripts/build_entity_registry.py`
- Create `datasets/entities/entity_registry.csv`
- No existing files modified
