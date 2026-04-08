# Atlas Corpus Pipeline

Corpus-first ingestion pipeline. Texts are the primary substrate;
datasets are derived outputs.

## Architecture

```
atlas/
  sources/          ← raw texts (any format)
  registry/         ← corpus_registry.jsonl (ground truth index)
  normalized/       ← UTF-8 cleaned plain text
  chunks/           ← paragraph-level JSON segments
  annotations/      ← entity tags, relations (future)
  datasets/         ← derived CSVs, graphs (future)
  scripts/          ← CLI tools
  config/           ← pipeline config (future)
```

Texts flow left to right: **source → normalize → chunk → annotate → derive**.
Each stage is a separate script. Each stage updates the registry.
All paths are deterministic from the text id.

## Commands

### 1. Register a source

```sh
cd atlas/
python scripts/ingest.py \
    --id isha_upanishad_muller_1884 \
    --title "Isha Upanishad (Müller 1884)" \
    --family upanishad \
    --layer S0 \
    --language en \
    --source sources/sample/isha_upanishad.txt \
    --source-type plain_text \
    --provenance public_domain
```

### 2. Normalize

```sh
python scripts/normalize.py --id isha_upanishad_muller_1884
```

Writes `normalized/isha_upanishad_muller_1884.txt`.

### 3. Chunk

```sh
python scripts/chunk.py --id isha_upanishad_muller_1884
```

Writes `chunks/isha_upanishad_muller_1884/0001.json` through `NNNN.json`.

## Registry

`registry/corpus_registry.jsonl` — one JSON object per line:

```json
{
  "id": "isha_upanishad_muller_1884",
  "title": "Isha Upanishad (Müller 1884)",
  "family": "upanishad",
  "layer_refs": ["S0"],
  "language": "en",
  "source_path": "sources/sample/isha_upanishad.txt",
  "normalized_path": "normalized/isha_upanishad_muller_1884.txt",
  "chunks_path": "chunks/isha_upanishad_muller_1884",
  "source_type": "plain_text",
  "provenance": "public_domain",
  "status": "chunked",
  "readability": "readable",
  "quality_notes": ""
}
```

Status progression: `registered → normalized → chunked → annotated`.

## Chunk format

Each chunk is one JSON file:

```json
{
  "chunk_id": "isha_upanishad_muller_1884_0001",
  "text_id": "isha_upanishad_muller_1884",
  "ordinal": 1,
  "text": "paragraph text...",
  "char_count": 420,
  "tags": [],
  "confidence": 1.0
}
```

## Assumptions

- Source files are UTF-8 or close to it (errors replaced on read).
- Chunking splits on blank lines (paragraph boundaries).
- Tiny chunks (<40 chars) merge with neighbors.
- Large chunks (>2000 chars) split at sentence boundaries.
- No external dependencies — stdlib only.
- No vector DBs, web services, or metaphysical modeling.

## Not yet implemented

- `annotations/` — entity tagging, relation extraction
- `datasets/` — derived CSVs from annotated chunks
- `config/` — chunking params, family-specific rules
- HTML/PDF source type handling in normalize.py
- Batch processing (process all registered texts at once)
