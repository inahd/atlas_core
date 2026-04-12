# RTE-001: Wire /corpus/search fully

**Phase**: 3 — Data integrity  
**Priority**: HIGH  
**Estimated time**: 2–3 hrs  
**Depends on**: COR-002 (corpus registry metadata)

## Context

`/corpus/search`, `/corpus/registry`, and `/corpus/read` are all PARTIAL.
`npu_engine/passage_resolver.py` is WORKING (176 lines) but the routes don't
fully use its capabilities. Tradition filtering doesn't work because registry
metadata is blank (fixed by COR-002). This task wires the routes to the engine.

## Instructions

### Step 1: Read the existing code

```bash
grep -n "corpus" ~/atlas_core/kernel.py | grep "def \|route" | head -20
cat ~/atlas_core/npu_engine/passage_resolver.py
```

### Step 2: Understand the current route implementation

```bash
# Find the corpus route functions in kernel.py:
grep -n "_corpus_" ~/atlas_core/kernel.py
# Read each function body
```

### Step 3: Test the current state

```bash
curl -s "localhost:5000/corpus/search?q=nakshatra" | python3 -m json.tool | head -30
curl -s "localhost:5000/corpus/registry" | python3 -m json.tool | head -30
```

### Step 4: Wire the routes

The `/corpus/search` route should:
1. Accept params: `q` (query string), `tradition` (optional), `limit` (default 10)
2. Call `passage_resolver.find_passages(query, tradition=tradition, limit=limit)`
3. Return: `{"results": [...], "query": q, "count": n}`

The `/corpus/registry` route should:
1. Read the corpus registry JSON
2. Return summary: file list, chunk counts, tradition breakdown

The `/corpus/read` route should:
1. Accept params: `chunk_id` or `file` + `offset`
2. Return the actual chunk content

### Step 5: Add entity-linked search

The passage_resolver can find passages linked to a specific entity via
`text_entity_relations.csv`. Wire this as `/corpus/search?entity=nakshatra:rohini`.

### Step 6: Test

```bash
curl -s "localhost:5000/corpus/search?q=tithi+nakshatra&limit=5" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); [print(r['text'][:80]) for r in d['results']]"

curl -s "localhost:5000/corpus/search?q=krishna&tradition=gaudiya_vaishnava&limit=3" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('count', 0), 'results')"
```

## Success check

```bash
# Basic search works:
curl -s "localhost:5000/corpus/search?q=nakshatra" | python3 -c \
  "import sys,json; d=json.load(sys.stdin); assert d.get('count',0)>0, 'No results'; print('OK:', d['count'])"

# Tradition filter works (after COR-002):
curl -s "localhost:5000/corpus/search?q=tithi&tradition=gaudiya_vaishnava" | python3 -c \
  "import sys,json; d=json.load(sys.stdin); assert d.get('count',0)>0; print('Tradition filter OK')"

# Registry returns meaningful data:
curl -s "localhost:5000/corpus/registry" | python3 -c \
  "import sys,json; d=json.load(sys.stdin); assert len(d)>10; print('Registry OK:', len(d))"
```

## Output

- Modify corpus route functions in `kernel.py`
- No new files required (passage_resolver.py already handles the logic)
