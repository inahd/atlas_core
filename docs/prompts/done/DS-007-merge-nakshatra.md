# DS-007: Merge duplicate nakshatra files into canonical master

**Phase**: 4  
**Priority**: LOW  
**Estimated time**: 2–3 hrs

## Context

5 nakshatra CSV files overlap heavily:
- `astro/nakshatra_core.csv` (27r, 3 cols)
- `astro/nakshatra_deities.csv` (27r, 2 cols)
- `astro/nakshatra_extended.csv` (27r, 10 cols)
- `astro/nakshatra_full.csv` (27r, 8 cols)
- `astro/nakshatra_master.csv` (27r, 12 cols) ← most complete

This creates confusion about which is authoritative and wastes loader calls.
The goal: one fat canonical file, keep old files as backward-compatible symlinks.

## Instructions

### Step 1: Compare all 5 files

```bash
cd ~/atlas_core
python3 -c "
import csv, os
files = [
    'datasets/astro/nakshatra_core.csv',
    'datasets/astro/nakshatra_deities.csv',
    'datasets/astro/nakshatra_extended.csv',
    'datasets/astro/nakshatra_full.csv',
    'datasets/astro/nakshatra_master.csv',
]
for f in files:
    rows = list(csv.DictReader(open(f)))
    cols = list(rows[0].keys()) if rows else []
    print(f'{os.path.basename(f)}: {len(cols)} cols — {cols}')
"
```

### Step 2: Identify the superset columns

Across all 5 files, collect every unique column. `nakshatra_master.csv` is the base —
add any columns that appear in the others but are missing from master.

Likely superset:
`nakshatra, element, guna, gana, dosha, yoni_animal, yoni_gender, symbol, shakti,
deity, ruling_graha, tree, plant, gemstone, themes, direction, pada_sounds, notes`

### Step 3: Write merge script

Write `scripts/merge_nakshatra_files.py`:

```python
#!/usr/bin/env python3
"""Merge all nakshatra CSV files into a single canonical dataset."""
import csv

# Load each file keyed by nakshatra name
# For each nakshatra (27 total), merge all fields from all files
# Where conflicts exist, prefer: master > full > extended > core > deities
# Output to datasets/astro/nakshatra_canonical.csv

files_in_priority = [
    'datasets/astro/nakshatra_master.csv',
    'datasets/astro/nakshatra_full.csv',
    'datasets/astro/nakshatra_extended.csv',
    'datasets/astro/nakshatra_core.csv',
    'datasets/astro/nakshatra_deities.csv',
]

merged = {}  # nakshatra_name -> merged row

for filepath in reversed(files_in_priority):  # lower priority first
    try:
        for row in csv.DictReader(open(filepath)):
            key = row.get('nakshatra', row.get('name', '')).lower().strip()
            if key not in merged:
                merged[key] = {}
            merged[key].update({k: v for k, v in row.items() if v})  # higher priority overwrites
    except: pass

# Collect all columns
all_cols = []
for row in merged.values():
    for k in row:
        if k not in all_cols:
            all_cols.append(k)

# Write
with open('datasets/astro/nakshatra_canonical.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=all_cols, extrasaction='ignore')
    writer.writeheader()
    for row in sorted(merged.values(), key=lambda r: r.get('num', r.get('nakshatra',''))):
        writer.writerow(row)

print(f'Written: {len(merged)} nakshatras, {len(all_cols)} columns')
print('Columns:', all_cols)
```

### Step 4: Run and verify

```bash
cd ~/atlas_core
python scripts/merge_nakshatra_files.py
wc -l datasets/astro/nakshatra_canonical.csv
head -2 datasets/astro/nakshatra_canonical.csv
```

Verify: exactly 27 data rows, all expected columns present.

### Step 5: Check what uses the old files

```bash
grep -rn "nakshatra_master\|nakshatra_full\|nakshatra_core\|nakshatra_extended\|nakshatra_deities" \
  ~/atlas_core/npu_engine/ | grep -v ".pyc" | grep "\.csv"
```

For each engine that loads the old files, add a fallback that also accepts
`nakshatra_canonical.csv`. Do NOT remove old files yet — update engines to
prefer canonical but fall back gracefully.

## Success check

```bash
python3 -c "
import csv
rows = list(csv.DictReader(open('datasets/astro/nakshatra_canonical.csv')))
assert len(rows) == 27, f'Expected 27, got {len(rows)}'
assert len(rows[0]) >= 15, f'Expected >= 15 cols, got {len(rows[0])}'
print(f'nakshatra_canonical: {len(rows)} rows, {len(rows[0])} columns')
print('Columns:', list(rows[0].keys()))
"
```

## Output

- Write `scripts/merge_nakshatra_files.py`
- Create `datasets/astro/nakshatra_canonical.csv`
- Old files remain (backward compat) — not deleted
