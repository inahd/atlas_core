# REL-004: Promote seed_unverified relations via corpus search

**Phase**: 4  
**Priority**: MEDIUM  
**Estimated time**: 2–3 hrs  
**Depends on**: COR-002 (corpus registry must be populated)

## Context

`relations_resolved_overlays.csv` has 323 rows all marked `seed_unverified`.
Many of these are probably grounded in the corpus — they just haven't been checked.
This task runs each relation through corpus search to find textual evidence,
then promotes verified ones to `attested_secondary` or better.

## Instructions

### Step 1: Read the overlays file

```bash
head -10 ~/atlas_core/datasets/relations/relations_resolved_overlays.csv
wc -l ~/atlas_core/datasets/relations/relations_resolved_overlays.csv
```

### Step 2: Read passage_resolver

```bash
cat ~/atlas_core/npu_engine/passage_resolver.py
```

Understand how `find_passages(query)` works.

### Step 3: Write the promotion script

Write `scripts/promote_overlay_relations.py`:

```python
#!/usr/bin/env python3
"""
Promote seed_unverified relations in relations_resolved_overlays.csv
by searching the corpus for supporting passages.
"""
import csv, sys
sys.path.insert(0, '.')
from npu_engine.passage_resolver import find_passages

INPUT = 'datasets/relations/relations_resolved_overlays.csv'
OUTPUT = 'datasets/relations/relations_resolved_overlays.csv'  # update in place
CANON = 'datasets/relations/relations_resolved_canon.csv'
EVIDENCE_LOG = 'docs/audit/overlay_promotion_log.csv'

rows = list(csv.DictReader(open(INPUT)))
promoted_to_canon = []
updated = []

for row in rows:
    if row.get('confidence') != 'seed_unverified':
        updated.append(row)
        continue
    
    # Build a search query from the relation
    subj = row.get('from_id', '').replace(':', ' ').replace('_', ' ')
    pred = row.get('relation', '').replace('_', ' ')
    obj = row.get('to_id', '').replace(':', ' ').replace('_', ' ')
    query = f"{subj} {obj}"
    
    try:
        passages = find_passages(query, limit=3)
        if passages:
            # Found evidence — promote to attested_secondary
            row['confidence'] = '0.75'
            row['source_title'] = passages[0].get('source', 'corpus_search')
            row['excerpt'] = passages[0].get('text', '')[:200]
            print(f"PROMOTED: {row['from_id']} → {row['relation']} → {row['to_id']}")
        else:
            print(f"no evidence: {row['from_id']} → {row['to_id']}")
    except Exception as e:
        print(f"error searching {query}: {e}")
    
    updated.append(row)

# Write updated overlays
with open(OUTPUT, 'w', newline='') as f:
    if updated:
        writer = csv.DictWriter(f, fieldnames=updated[0].keys())
        writer.writeheader()
        writer.writerows(updated)

promoted_count = sum(1 for r in updated if r.get('confidence') != 'seed_unverified')
print(f"\nPromoted: {promoted_count} / {len(rows)} relations now have evidence")
```

### Step 4: Run it

```bash
cd ~/atlas_core
python scripts/promote_overlay_relations.py 2>&1 | tee docs/audit/overlay_promotion_log.txt
```

### Step 5: Review and commit

```bash
python3 -c "
import csv
rows = list(csv.DictReader(open('datasets/relations/relations_resolved_overlays.csv')))
verified = [r for r in rows if r.get('confidence') != 'seed_unverified']
still_seed = [r for r in rows if r.get('confidence') == 'seed_unverified']
print(f'Promoted to attested: {len(verified)}')
print(f'Still seed_unverified: {len(still_seed)}')
"
```

## Success check

```bash
python3 -c "
import csv
rows = list(csv.DictReader(open('datasets/relations/relations_resolved_overlays.csv')))
seed = sum(1 for r in rows if r.get('confidence') == 'seed_unverified')
pct = (1 - seed/len(rows)) * 100 if rows else 0
print(f'Promotion rate: {pct:.0f}% ({len(rows)-seed}/{len(rows)} have evidence)')
# Expect at least 20% promoted given corpus coverage
assert pct >= 10, f'Too few promoted: {pct:.0f}%'
print('OK')
"
```

## Output

- Write `scripts/promote_overlay_relations.py`
- Update `datasets/relations/relations_resolved_overlays.csv` in-place
- Write `docs/audit/overlay_promotion_log.txt`
