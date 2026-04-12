# COR-002: Populate corpus registry tradition and language fields

**Phase**: 1 — Stop the bleeding  
**Priority**: HIGH  
**Estimated time**: 1 hr  
**Blocks**: /corpus/search tradition filtering

## Context

The corpus registry has 81 entries but tradition and language fields are blank ('?')
across all of them. This prevents /corpus/search from filtering by tradition and
prevents the passage_resolver from weighting results by authority.

The JSONL files are organized in subdirectories by tradition:
`ayurveda/`, `cosmology/`, `dharma/`, `epics/`, `gaudiya/`, `jyotish/`,
`vastu/`, `vedic/`, `yoga/`

The language is encoded in the filename: `_en_` = English, `_sa_` = Sanskrit,
no suffix = mixed or English default.

## Instructions

1. Find the corpus registry file:
```bash
find ~/atlas_core/datasets/sources -name "*.json" | head -20
ls ~/atlas_core/datasets/sources/
```
   It is likely `datasets/sources/corpus_registry.json` or similar.

2. Read the registry file — understand its structure.

3. Write a Python script `scripts/populate_corpus_registry.py` that:
   - Reads the registry
   - For each entry, derives tradition from the file path (subdirectory name)
   - Derives language from the filename pattern: `_en_` → 'en', `_sa_` → 'sa', else 'en'
   - Maps subdirectory to tradition authority weight:
     ```python
     TRADITION_MAP = {
         'gaudiya': {'tradition': 'gaudiya_vaishnava', 'authority': 0.99},
         'jyotish': {'tradition': 'jyotish', 'authority': 0.95},
         'ayurveda': {'tradition': 'ayurveda', 'authority': 0.95},
         'vastu': {'tradition': 'vastu', 'authority': 0.90},
         'vedic': {'tradition': 'vedic', 'authority': 0.95},
         'yoga': {'tradition': 'yoga_tantra', 'authority': 0.85},
         'cosmology': {'tradition': 'puranic', 'authority': 0.90},
         'epics': {'tradition': 'itihasa', 'authority': 0.90},
         'dharma': {'tradition': 'dharmashastra', 'authority': 0.85},
     }
     ```
   - Updates the registry entries in place
   - Writes the updated registry back

4. Run the script:
```bash
cd ~/atlas_core && python scripts/populate_corpus_registry.py
```

5. Also identify and register the 2 unregistered JSONL files:
```bash
# Find JSONL files not in registry:
python3 -c "
import json, os, glob
reg = json.load(open('datasets/sources/corpus_registry.json'))
registered = {e.get('file','') for e in reg} if isinstance(reg, list) else set()
actual = glob.glob('datasets/sources/**/*.jsonl', recursive=True)
for f in actual:
    rel = f.replace('datasets/sources/', '')
    if rel not in registered:
        print('UNREGISTERED:', f)
"
```
   Add any unregistered files to the registry with correct metadata.

## Success check

```bash
curl -s "localhost:5000/corpus/search?q=nakshatra&tradition=gaudiya_vaishnava" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('Results:', len(d.get('results', d)))"
```

Should return results, not an error or empty list.

```bash
python3 -c "
import json
reg = json.load(open('datasets/sources/corpus_registry.json'))
entries = reg if isinstance(reg, list) else list(reg.values())
blank = [e for e in entries if not e.get('tradition') or e.get('tradition') == '?']
print(f'Blank tradition entries: {len(blank)} of {len(entries)}')
"
```

Should report 0 blank entries.

## Output

- Write `scripts/populate_corpus_registry.py`
- Update `datasets/sources/corpus_registry.json` (or equivalent registry file)
- No other files modified
