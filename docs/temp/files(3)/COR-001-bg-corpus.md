# COR-001: Add Bhagavad Gita corpus

**Phase**: 1 — Stop the bleeding  
**Priority**: CRITICAL  
**Estimated time**: 2–4 hrs  
**Depends on**: COR-002 (registry metadata populated)

## Context

`datasets/sources/gaudiya/bg_chunks.jsonl` exists but has 0 chunks. The Bhagavad
Gita is the most central text in the Gaudiya Vaishnava tradition and its absence
from the corpus is the most significant content gap. A bg_verses_index.jsonl (18 chunks)
exists — this is just an index, not the full text.

## Instructions

### Step 1: Check what's available locally

```bash
ls ~/atlas_core/datasets/sources/gaudiya/
wc -l ~/atlas_core/datasets/sources/gaudiya/bg_chunks.jsonl
cat ~/atlas_core/datasets/sources/gaudiya/bg_verses_index.jsonl | head -5
```

### Step 2: Check for source text files

```bash
find ~/atlas_core -name "*gita*" -o -name "*bg_*" 2>/dev/null | grep -v ".pyc"
find ~/atlas_core -name "*.txt" | xargs grep -l "Bhagavad" 2>/dev/null | head -5
```

### Step 3: Check existing chunking scripts

```bash
ls ~/atlas_core/scripts/ | grep -i chunk
ls ~/atlas_core/scripts/ | grep -i corpus
```
   Read the most relevant one — match its chunking pattern exactly.

### Step 4: Source the text

If a BG text file exists locally, use it. If not, the public domain translation
by Swami Sivananda or the Prabhupada translation (if available) can be used.

Check for any existing BG text:
```bash
find / -name "*bhagavad*gita*" 2>/dev/null | grep -i "\.txt\|\.json" | head -10
```

### Step 5: Build the chunking script

Write `scripts/chunk_bg.py` that:
- Reads the source text
- Splits by chapter and verse (18 chapters, ~700 verses total)
- Each chunk: one verse + purport/commentary if available
- Output format matches existing gaudiya chunks exactly:
  ```json
  {"chunk_id": "bg_01_01", "text": "...", "source": "Bhagavad Gita As It Is",
   "tradition": "gaudiya_vaishnava", "language": "en", "chapter": 1, "verse": 1,
   "entity_refs": ["graha:surya", "deity:krishna"]}
  ```
- Read one existing gaudiya JSONL to verify the exact schema before writing

### Step 6: Run and verify

```bash
cd ~/atlas_core
python scripts/chunk_bg.py
wc -l datasets/sources/gaudiya/bg_chunks.jsonl
```

Should produce at minimum 700 chunks (one per verse). With purports, 2,000–5,000+.

### Step 7: Register in corpus registry

Add to corpus registry if not already present:
```json
{
  "file": "gaudiya/bg_chunks.jsonl",
  "source": "Bhagavad Gita As It Is",
  "tradition": "gaudiya_vaishnava",
  "language": "en",
  "authority": 0.99
}
```

## HUMAN_REQUIRED condition

If no BG source text is available anywhere on the filesystem and no chunking
script exists that can generate it from a known source, mark this task
HUMAN_REQUIRED — do not fabricate the text of the Bhagavad Gita.

## Success check

```bash
wc -l ~/atlas_core/datasets/sources/gaudiya/bg_chunks.jsonl
# Should be > 700

curl -s "localhost:5000/corpus/search?q=arjuna+krishna&tradition=gaudiya_vaishnava" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('Results:', len(d.get('results', [])))"
# Should return > 0 results
```

## Output

- Write `scripts/chunk_bg.py`
- Populate `datasets/sources/gaudiya/bg_chunks.jsonl`
- Update corpus registry
