# REL-005: Deduplicate inverse and duplicate relations

**Phase**: 4  
**Priority**: LOW  
**Estimated time**: 1–2 hrs

## Context

The relation graph likely contains duplicate edges and near-duplicate inverse pairs —
e.g. `(nakshatra:rohini, ruling_graha, graha:chandra)` in one file and
`(graha:chandra, rules_nakshatra, nakshatra:rohini)` in another.
These inflate edge counts and can cause double-weighting in graph traversal.

## Instructions

### Step 1: Find exact duplicates across all relation files

```bash
cd ~/atlas_core
python3 -c "
import csv, glob, collections

all_triples = []
for f in glob.glob('datasets/relations/*.csv'):
    try:
        for row in csv.DictReader(open(f)):
            triple = (row.get('from_id',''), row.get('relation',''), row.get('to_id',''))
            if all(triple):
                all_triples.append((triple, f))
    except: pass

# Find duplicates
triple_files = collections.defaultdict(list)
for triple, f in all_triples:
    triple_files[triple].append(f)

dups = {t: fs for t, fs in triple_files.items() if len(fs) > 1}
print(f'Exact duplicates: {len(dups)}')
for triple, files in list(dups.items())[:10]:
    print(f'  {triple} — in {files}')
"
```

### Step 2: Find near-inverse pairs

```bash
python3 -c "
import csv, glob

INVERSE_PAIRS = {
    'nakshatra_ruling_graha': 'graha_rules_nakshatra',
    'nakshatra_associated_deity': 'deity_presides_nakshatra',
    'composed_by': 'composer_of',
    'element': 'has_element',
    'dosha': 'associated_dosha',
}

triples = []
for f in glob.glob('datasets/relations/*.csv'):
    try:
        for row in csv.DictReader(open(f)):
            triples.append((row.get('from_id',''), row.get('relation',''), row.get('to_id','')))
    except: pass

triple_set = set(triples)
inverse_count = 0
for subj, pred, obj in triples:
    inv_pred = INVERSE_PAIRS.get(pred)
    if inv_pred and (obj, inv_pred, subj) in triple_set:
        inverse_count += 1
        
print(f'Inverse pairs found: {inverse_count}')
"
```

### Step 3: Write dedup script

Write `scripts/deduplicate_relations.py`:

Policy:
- **Exact duplicates**: keep the one with higher confidence; remove the other
- **Inverse pairs**: keep both (they serve different traversal directions) but
  log them so humans can decide later
- **Same subject+object, different predicate**: keep all (they encode different relations)

```python
#!/usr/bin/env python3
"""Remove exact duplicate relations across all relation CSVs."""
import csv, glob, os

seen = set()
dedup_log = []

for f in sorted(glob.glob('datasets/relations/*.csv')):
    if 'canon' in f: continue  # never touch canon
    try:
        rows = list(csv.DictReader(open(f)))
        if not rows: continue
        
        clean = []
        for row in rows:
            key = (row.get('from_id',''), row.get('relation',''), row.get('to_id',''))
            if key in seen:
                dedup_log.append({'file': f, 'removed': str(key)})
            else:
                seen.add(key)
                clean.append(row)
        
        if len(clean) < len(rows):
            removed = len(rows) - len(clean)
            print(f'Removed {removed} duplicates from {os.path.basename(f)}')
            with open(f, 'w', newline='') as fh:
                writer = csv.DictWriter(fh, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(clean)
    except Exception as e:
        print(f'Error processing {f}: {e}')

print(f'Total removed: {len(dedup_log)}')

# Write log
with open('docs/audit/dedup_log.csv', 'w', newline='') as f:
    if dedup_log:
        writer = csv.DictWriter(f, fieldnames=dedup_log[0].keys())
        writer.writeheader()
        writer.writerows(dedup_log)
```

### Step 4: Run

```bash
cd ~/atlas_core
python scripts/deduplicate_relations.py
```

## Success check

```bash
python3 -c "
import csv, glob, collections

all_triples = []
for f in glob.glob('datasets/relations/*.csv'):
    try:
        for row in csv.DictReader(open(f)):
            t = (row.get('from_id',''), row.get('relation',''), row.get('to_id',''))
            if all(t): all_triples.append(t)
    except: pass

from collections import Counter
counts = Counter(all_triples)
dups = {t: c for t, c in counts.items() if c > 1}
print(f'Remaining duplicates: {len(dups)}')
print(f'Total triples: {len(all_triples)}')
# Should be 0 duplicates
"
```

## Output

- Write `scripts/deduplicate_relations.py`
- Modify relation CSVs in-place (removes duplicates)
- Write `docs/audit/dedup_log.csv`
