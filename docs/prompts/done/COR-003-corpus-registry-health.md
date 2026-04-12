# COR-003: Register unregistered JSONL files + corpus health check

**Phase**: 3  
**Priority**: MEDIUM  
**Estimated time**: 1 hr  
**Depends on**: COR-002 (registry metadata populated)

## Context

The audit found 2 JSONL files present on disk but not in the corpus registry,
and 1 registered file that's missing on disk. This task resolves those gaps
and adds a corpus health check script.

## Instructions

### Step 1: Find the discrepancies

```bash
cd ~/atlas_core
python3 -c "
import json, os, glob

# Find registry file
for candidate in ['datasets/sources/corpus_registry.json',
                  'datasets/sources/manifest.json',
                  'datasets/sources/registry.json']:
    if os.path.exists(candidate):
        print('Registry:', candidate)
        reg = json.load(open(candidate))
        break

# Get registered files
if isinstance(reg, list):
    registered = {e.get('file','') for e in reg}
elif isinstance(reg, dict):
    registered = set(reg.keys())
else:
    registered = set()

# Get actual JSONL files
actual = set()
for f in glob.glob('datasets/sources/**/*.jsonl', recursive=True):
    rel = f.replace('datasets/sources/', '')
    actual.add(rel)

print(f'Registered: {len(registered)}')
print(f'On disk: {len(actual)}')
print()
print('UNREGISTERED (on disk, not in registry):')
for f in sorted(actual - registered): print(' ', f)
print()
print('MISSING (in registry, not on disk):')
for f in sorted(registered - actual): print(' ', f)
"
```

### Step 2: Add unregistered files to registry

For each unregistered file, determine tradition from path and language from filename,
then add to the registry using the same format established by COR-002.

### Step 3: Handle the missing registered file

If a file is in the registry but not on disk:
- If it's `bg_chunks.jsonl`: this is handled by COR-001 (BG corpus task)
- If it's another file: note it in the log, remove from registry or mark as missing

### Step 4: Write a corpus health script

Write `scripts/corpus_health.py`:

```python
#!/usr/bin/env python3
"""Quick corpus health check — run anytime to verify registry vs filesystem."""
import json, os, glob, csv

# Load registry
# Load actual files
# Compare
# For each file: chunk count, tradition, language, registration status
# Output summary table

# Also check:
# - Files with 0 chunks (like bg_chunks.jsonl was)
# - Files where chunk count differs significantly from registry
# - Total chunk count across all traditions

print("=== Corpus Health ===")
# ... implementation
```

Run it:
```bash
cd ~/atlas_core
python scripts/corpus_health.py
```

### Step 5: Add corpus health to the dashboard

Add corpus health data to the `/dashboard` endpoint (if RTE-004 has run):
```python
# In _dashboard():
try:
    from scripts.corpus_health import get_corpus_stats
    out["corpus"] = get_corpus_stats()
except: pass
```

## Success check

```bash
python3 -c "
import json, glob, os

# Load registry
reg_file = next((f for f in ['datasets/sources/corpus_registry.json',
                              'datasets/sources/manifest.json']
                 if os.path.exists(f)), None)
if not reg_file:
    print('ERROR: no registry file found')
    exit(1)

reg = json.load(open(reg_file))
entries = reg if isinstance(reg, list) else list(reg.values())

# Check all registered files exist
missing = [e for e in entries
           if not os.path.exists(f'datasets/sources/{e.get(\"file\",\"\")}')]
print(f'Missing files: {len(missing)}')

# Check all disk files are registered
registered = {e.get('file','') for e in entries}
actual = {f.replace('datasets/sources/','')
          for f in glob.glob('datasets/sources/**/*.jsonl', recursive=True)}
unregistered = actual - registered
print(f'Unregistered files: {len(unregistered)}')

assert len(missing) == 0, f'Still {len(missing)} missing'
assert len(unregistered) == 0, f'Still {len(unregistered)} unregistered'
print('Corpus registry: CLEAN')
"
```

## Output

- Update corpus registry JSON with unregistered files
- Remove or flag missing registry entries
- Write `scripts/corpus_health.py`
