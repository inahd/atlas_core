# DS-003: Add attestation_status columns to CSVs that lack them

**Phase**: 3  
**Priority**: MEDIUM  
**Estimated time**: 1–2 hrs

## Context

31 CSVs already have `attestation_status`. Many others don't. The relation promotion
pipeline and corpus search both use attestation to weight results. Adding the column
to all canonical datasets enables proper confidence tracking.

## Instructions

### Step 1: Find CSVs missing attestation

```bash
cd ~/atlas_core
python3 -c "
import csv, glob

missing = []
has_it = []
for f in sorted(glob.glob('datasets/**/*.csv', recursive=True)):
    if 'relations' in f: continue  # relations use 'confidence' not 'attestation_status'
    try:
        with open(f) as fh:
            reader = csv.DictReader(fh)
            if not reader.fieldnames: continue
            if 'attestation_status' not in (reader.fieldnames or []):
                row_count = sum(1 for _ in reader)
                if row_count > 3:  # skip tiny stub files
                    missing.append((f, row_count))
    except: pass

print(f'Missing attestation_status: {len(missing)} files')
for f, n in sorted(missing, key=lambda x: -x[1])[:25]:
    print(f'  {n:4d} rows  {f}')
"
```

### Step 2: Determine appropriate default values

For each file, the default `attestation_status` depends on its source:
- Core cosmological data (nakshatras, grahas, tithis from classical texts): `attested_classical`
- Derived/computed data (emoji mappings, auto-generated): `inferred_coherent`
- Practitioner data (herb recommendations, therapeutic ragas): `attested_secondary`
- Unknown/unchecked: `seed_unverified`

Domain defaults:
```python
DOMAIN_DEFAULTS = {
    'astro': 'attested_classical',
    'cosmology': 'attested_classical',
    'ayurveda': 'attested_secondary',
    'carnatic': 'attested_secondary',
    'gandharva': 'attested_secondary',
    'vastu': 'attested_secondary',
    'yoga': 'attested_secondary',
    'iching': 'inferred_coherent',
    'symbols': 'inferred_coherent',
    'plants': 'attested_secondary',
    'game': 'inferred_coherent',
    'geography': 'attested_secondary',
    'species': 'attested_secondary',
    'marma': 'attested_secondary',
    'svarodaya': 'attested_classical',
    'chandas': 'attested_classical',
    'ontology': 'attested_classical',
    'permaculture': 'inferred_coherent',
    'morphogenesis': 'inferred_coherent',
}
```

### Step 3: Write the repair script

Write `scripts/add_attestation_columns.py`:

```python
#!/usr/bin/env python3
"""Add attestation_status column to CSVs that lack it."""
import csv, glob, os, sys

DOMAIN_DEFAULTS = { ... }  # as above

def add_attestation(filepath, default):
    with open(filepath) as f:
        rows = list(csv.DictReader(f))
        fieldnames = list(csv.DictReader(open(filepath)).fieldnames or [])
    
    if not rows or 'attestation_status' in fieldnames:
        return False
    
    fieldnames.append('attestation_status')
    for row in rows:
        row['attestation_status'] = default
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return True

count = 0
for f in sorted(glob.glob('datasets/**/*.csv', recursive=True)):
    if 'relations' in f: continue
    domain = f.split('/')[1] if '/' in f else 'unknown'
    default = DOMAIN_DEFAULTS.get(domain, 'seed_unverified')
    if add_attestation(f, default):
        print(f'Added: {f} ({default})')
        count += 1

print(f'\nTotal updated: {count}')
```

### Step 4: Run it

```bash
cd ~/atlas_core
python scripts/add_attestation_columns.py
```

### Step 5: Verify a sample

```bash
python3 -c "
import csv
rows = list(csv.DictReader(open('datasets/carnatic/tala_master.csv')))
print('tala_master attestation:', rows[0].get('attestation_status'))
rows = list(csv.DictReader(open('datasets/iching/hexagrams.csv')))
print('hexagrams attestation:', rows[0].get('attestation_status'))
"
```

## Success check

```bash
python3 -c "
import csv, glob
missing = [f for f in glob.glob('datasets/**/*.csv', recursive=True)
           if 'relations' not in f
           and 'attestation_status' not in (list(csv.DictReader(open(f)).fieldnames or []))
           and sum(1 for _ in open(f)) > 3]
print(f'Still missing attestation_status: {len(missing)}')
# Should be significantly reduced from baseline
"
```

## Output

- Write `scripts/add_attestation_columns.py`
- Modify all qualifying CSVs in-place (adds one column, all existing data preserved)
