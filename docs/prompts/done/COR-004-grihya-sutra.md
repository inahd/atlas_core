# COR-004: Add Grihya Sutra corpus

**Phase**: 4  
**Priority**: MEDIUM  
**Estimated time**: 2–4 hrs

## Context

The Grihya Sutras (domestic ritual manuals) are missing from the corpus.
They are the primary textual source for ritual calendar prescriptions,
sacraments (samskaras), and festival observances — all directly relevant
to the svarodaya engine, the ritual_engine, and the calendar layer.

Key texts: Ashvalayana Grihya Sutra, Gobhila Grihya Sutra, Hiranyakeshi Grihya Sutra.

## Instructions

### Step 1: Check what's available

```bash
find ~/atlas_core -name "*grihya*" -o -name "*grhya*" 2>/dev/null | grep -v ".pyc"
find / -name "*grihya*sutra*" 2>/dev/null | grep -i "\.txt\|\.json\|\.epub" | head -10
```

Also check the datasets/sources/ directory for any related texts:
```bash
ls ~/atlas_core/datasets/sources/dharma/
```

### Step 2: Check for chunking infrastructure

```bash
ls ~/atlas_core/scripts/ | grep -i "chunk\|ingest\|corpus"
# Read the most relevant chunking script
```

### Step 3: Source the text

Check Project Gutenberg, Sacred Texts archive (sacred-texts.com),
or GRETIL (gretil.sub.uni-goettingen.de) for public domain translations.

If a source file exists locally or can be fetched:
```bash
# Example: check if wget/curl can reach Sacred Texts
curl -s --max-time 5 "https://www.sacred-texts.com/hin/sbe29/index.htm" | grep -i "grihya" | head -5
```

The Oldenberg translation (Sacred Books of the East vol. 29-30) is public domain.

### Step 4: Build chunking script

Write `scripts/chunk_grihya_sutra.py` following the pattern of other chunking scripts.

Chunk by sutra number (each numbered sutra = one chunk).
Each chunk:
```json
{
  "chunk_id": "grihya_ashvalayana_1_1",
  "text": "...",
  "source": "Ashvalayana Grihya Sutra",
  "tradition": "vedic_ritual",
  "language": "en",
  "book": 1,
  "sutra": 1,
  "entity_refs": []
}
```

### Step 5: HUMAN_REQUIRED condition

If no source text is available locally and network access to retrieve it
is unavailable or blocked, mark HUMAN_REQUIRED.

Document what was found:
```bash
echo "$(date) — COR-004 status: [what was found/attempted]" \
  >> ~/atlas_core/docs/ATLAS_CYCLE_LOG.md
```

### Step 6: Register in corpus

Add to corpus registry:
```json
{
  "file": "dharma/grihya_sutra_en_chunks.jsonl",
  "source": "Grihya Sutras (Oldenberg translation)",
  "tradition": "vedic_ritual",
  "language": "en",
  "authority": 0.95
}
```

## Success check

```bash
wc -l ~/atlas_core/datasets/sources/dharma/grihya_sutra_en_chunks.jsonl
# Should be > 100 chunks

python3 -c "
import json
chunks = [json.loads(l) for l in open('datasets/sources/dharma/grihya_sutra_en_chunks.jsonl')]
print(f'Grihya Sutra chunks: {len(chunks)}')
print('Sample:', chunks[0]['text'][:100])
"
```

## Output

- Write `scripts/chunk_grihya_sutra.py`
- Create `datasets/sources/dharma/grihya_sutra_en_chunks.jsonl`
- Update corpus registry
