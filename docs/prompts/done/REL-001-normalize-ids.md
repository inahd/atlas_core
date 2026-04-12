# REL-001: Normalize entity IDs in relation CSVs

**Phase**: 3 — Data integrity  
**Priority**: HIGH  
**Estimated time**: 1–2 days  
**Depends on**: REL-002 (entity registry must exist)

## Context

Relation CSVs use mixed ID formats: `nakshatra:rohini`, `nakshatra:1`, `nakshatra_rohini`,
`plant:Ashvagandha`. This makes graph traversal unreliable. The canonical format is
`category:slug` where slug is lowercase with underscores.

Do NOT modify `datasets/relations/relations_resolved_canon.csv` — that file is canonical.
Work on all other relation CSVs.

## Instructions

### Step 1: Read the entity registry

```bash
head -20 ~/atlas_core/datasets/entities/entity_registry.csv
```

This gives you the authoritative `entity_id → name` mapping.

### Step 2: Audit current ID formats

```bash
cd ~/atlas_core
python3 -c "
import csv, glob, collections

formats = collections.Counter()
for f in glob.glob('datasets/relations/*.csv'):
    if 'canon' in f: continue
    try:
        with open(f) as fh:
            for row in csv.DictReader(fh):
                subj = row.get('from_id', '')
                if subj:
                    cat = subj.split(':')[0] if ':' in subj else 'no_prefix'
                    formats[cat] += 1
    except: pass

for k, v in formats.most_common(20):
    print(f'{k}: {v}')
"
```

### Step 3: Write the repair script

Write `scripts/normalize_entity_ids.py` that:

1. Loads the entity registry as a lookup: `{old_id: canonical_id}`
   - Build multiple lookup keys per entity (numeric, slug, capitalized, etc.)
   - Example: for nakshatra Ashvini, map:
     `'nakshatra:1' → 'nakshatra:ashvini'`
     `'nakshatra:Ashvini' → 'nakshatra:ashvini'`
     `'nakshatra_ashvini' → 'nakshatra:ashvini'`
     `'ashvini' → 'nakshatra:ashvini'` (only if unambiguous)

2. For each relation CSV (excluding relations_resolved_canon.csv):
   - Read all rows
   - For each `from_id` and `to_id`:
     - Look up canonical ID in the registry
     - If found: replace
     - If not found: log to `docs/audit/id_repair_log.csv` for review
   - Write repaired file (overwrite in place — we have git)

3. Outputs:
   - Repaired relation CSVs
   - `docs/audit/id_repair_log.csv`: `file, original_id, status (repaired|unresolved), canonical_id`

### Step 4: Run on low-risk files first

Start with files that have high confidence scores and clear entity types:
- `datasets/relations/species_relations.csv` (163 rows, species: prefix)
- `datasets/relations/vastu_relations.csv` (145 rows, vastu: prefix)
- `datasets/relations/deity_relations.csv` (159 rows, deity: prefix)

Verify each before proceeding to larger files (iching_relations.csv is 1,946 rows).

```bash
cd ~/atlas_core
python scripts/normalize_entity_ids.py --file datasets/relations/species_relations.csv --dry-run
# Review output
python scripts/normalize_entity_ids.py --file datasets/relations/species_relations.csv
```

### Step 5: Check repair rate

```bash
python3 -c "
import csv
log = list(csv.DictReader(open('docs/audit/id_repair_log.csv')))
repaired = sum(1 for r in log if r['status'] == 'repaired')
unresolved = sum(1 for r in log if r['status'] == 'unresolved')
print(f'Repaired: {repaired}, Unresolved: {unresolved}')
"
```

If unresolved rate > 30% on any file, stop and mark HUMAN_REQUIRED for that file.

## Success check

```bash
python3 -c "
import csv, glob

registry = {r['entity_id'] for r in
    csv.DictReader(open('datasets/entities/entity_registry.csv'))}

resolved = unresolved = 0
for f in glob.glob('datasets/relations/*.csv'):
    if 'canon' in f: continue
    try:
        for row in csv.DictReader(open(f)):
            subj = row.get('from_id', '')
            if subj:
                if subj in registry: resolved += 1
                else: unresolved += 1
    except: pass

total = resolved + unresolved
pct = resolved/total*100 if total else 0
print(f'Resolved: {resolved}/{total} ({pct:.1f}%)')
"
# Should be > 70% resolved (up from ~0.3% before)
```

## Output

- Write `scripts/normalize_entity_ids.py`
- Modify relation CSVs in place (all except relations_resolved_canon.csv)
- Create `docs/audit/id_repair_log.csv`
