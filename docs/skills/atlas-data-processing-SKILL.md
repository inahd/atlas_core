---
name: atlas-data-processing
description: >
  Use this skill for ANY task involving Atlas data ingestion, corpus expansion,
  CSV processing, dataset conversion, or text corpus management. Triggers include:
  ingesting research CSVs, fetching Vedic texts, chunking JSONL corpus files,
  converting research output to passages, building entity registries, running
  deduplication, normalizing IDs, promoting overlay relations, or any task
  that moves data from raw source into the Atlas datasets/ or corpus/ directories.
  Read before writing ANY ingestion or processing script.
---

# Atlas Data Processing Skill

## Core Principle

The Atlas knowledge graph has three layers of data with different authority levels.
Never mix them. Never promote data upward without explicit confirmation.

```
SHASTRA layer  — canonical shastra citations, primary text passages
                 attestation: SHASTRA:PRIMARY or SHASTRA:SECONDARY
                 location: corpus/*.jsonl (tradition=vedic/gaudiya etc)
                 NEVER overwritten by inference

SYNTHESIS layer — cross-traditional research, VPK inference, species data
                  attestation: SYNTHESIS or INFERRED:BIOLOGY
                  location: datasets/species/, datasets/geography/ etc
                  Can be promoted if corpus evidence found

SEED layer     — unverified, speculative, working hypotheses
                 attestation: seed_unverified
                 location: datasets/relations/relations_resolved_overlays.csv
                 Promoted by REL-004 pattern when corpus evidence found
```

---

## Directory Structure

```
~/atlas_core/
  corpus/                  NOT USED — JSONL files live in:
  datasets/sources/        ← all JSONL corpus files go here
    corpus_registry.json   ← register every JSONL here
    bg/                    Bhagavad Gita
    gaudiya/               Gaudiya Vaishnava texts
    dharma/                Grihya Sutras, Dharmashastra
    itihasa/               Mahabharata, Ramayana
    ayurveda/              Charaka, Sushruta, Ashtanga Hridayam
    jyotish/               Brhat Samhita, BPHS
    yoga_tantra/           Upanishads, Yoga Sutras
    puranic/               Puranas
  datasets/
    astro/                 nakshatra, tithi, graha CSVs
    species/               animal/plant species data
    geography/             sacred sites, continental maps
    relations/             relation CSVs (see below)
    entities/              entity_registry.csv
  scripts/                 processing scripts (reusable)
```

---

## JSONL Corpus Schema

Every chunk in every JSONL file must have these fields:

```json
{
  "id": "corpus_name",
  "chunk_id": "corpus_name:0042",
  "char_start": 1840,
  "char_end": 2310,
  "text": "The passage text goes here...",
  "source": "Source Book Name",
  "domain": "cosmology",
  "tradition": "gaudiya_vaishnava",
  "language": "en",
  "chapter": "5",
  "verse": "25.12",
  "authority": "shastra",
  "entity_refs": ["graha:shani", "cosmology:patala"]
}
```

Valid `tradition` values (match corpus_registry.json exactly):
```
vedic, gaudiya_vaishnava, itihasa, puranic, ayurveda,
jyotish, yoga_tantra, dharmashastra, vastu, vedic_ritual,
cross_traditional, synthesis
```

Valid `authority` values:
```
shastra, sadhu, guru
```

**Chunk size target**: 400-600 characters. Never under 100, never over 1000.

---

## corpus_registry.json Entry Schema

After creating any JSONL file, add an entry to
`datasets/sources/corpus_registry.json`:

```json
{
  "corpus_id": "my_corpus_name",
  "file": "datasets/sources/subdir/my_corpus_name_chunks.jsonl",
  "source_title": "Full Title of the Source Text",
  "tradition": "gaudiya_vaishnava",
  "authority": "shastra",
  "language": "en",
  "chunk_count": 259,
  "status": "chunked",
  "notes": "Source: Ganguli translation, public domain"
}
```

Also append to `atlas/registry/corpus_registry.jsonl` (one JSON object per line).

---

## Research CSV → JSONL Passage Conversion

When converting research CSVs (species, geography, loka etc) to corpus passages,
generate natural-language passages from the structured data. Each row becomes
1-2 passages.

### Pattern for species rows:
```python
def row_to_passage(row):
    text = (
        f"{row['common_name']} ({row['latin_name']}) is a {row['dosha_primary']}-"
        f"dominant creature associated with {row['graha_resonance']} in Vedic cosmology. "
        f"{row['dosha_reasoning']} "
        f"Its medicine quality is {row['medicine_quality']}. "
        f"Contrary quality: {row['contrary_quality']}. "
        f"Ecological role: {row['ecological_role']}. "
        f"Nakshatra resonance: {row['nakshatra_association']}."
    )
    return {
        "id": f"species_{row['species_id']}",
        "chunk_id": f"species_passages:{row['species_id']}",
        "text": text,
        "source": "VPK Species Research Dataset",
        "domain": "species",
        "tradition": "cross_traditional",
        "language": "en",
        "authority": "sadhu",
        "entity_refs": [
            f"graha:{row['graha_resonance'].lower()}",
            f"nakshatra:{row['nakshatra_association'].lower().replace(' ', '_')}"
        ]
    }
```

### Pattern for loka/cosmology rows:
```python
def loka_to_passage(row):
    text = (
        f"{row['loka_name']} (level {row['level_from_human']} from the human plane) "
        f"is ruled by {row['ruling_being']}. "
        f"Its primary quality is {row['quality_primary']}: {row['quality_description']} "
        f"The naga resident is {row['naga_resident']}. "
        f"Element: {row['element_primary']}. "
        f"Consciousness state: {row['consciousness_state']}. "
        f"Source: {row['source_text']} {row['source_verse']}."
    )
```

---

## Vedic Text Fetching Patterns

### Vedabase (vedabase.io)
Use web search first to get the URL, then fetch:
```python
# Search pattern that works:
# "Srimad Bhagavatam 5.24 Patala description site:vedabase.io"
# Then fetch the returned URL

# URL pattern:
# https://vedabase.io/en/library/sb/5/24/  (chapter)
# https://vedabase.io/en/library/sb/5/24/31/  (verse)
```

Vedabase returns verse text + word-for-word Sanskrit + purport.
Chunk as: verse_text (one chunk) + purport_paragraphs (one chunk each).
Set `verse` field to "SB 5.24.31" format.
Set `authority` to "shastra".

### Wisdomlib (wisdomlib.org)
```
URL pattern: https://www.wisdomlib.org/hinduism/book/[text-name]/d/doc[id].html
Search: "[text name] wisdomlib [chapter topic]"
```
Good for: Brhat Samhita chapters, Panchatantra, Arthashastra, Ayurvedic texts.

### GRETIL (gretil.sub.uni-goettingen.de)
Plain text files in IAST. No direct fetch — download via URL pattern:
```
https://gretil.sub.uni-goettingen.de/gretil/1_sanskr/[path]/[filename].txt
```
Use the Tyler Neill mirror for reliability:
```
https://tylergneill.github.io/gretil-mirror/gretil.html
```

---

## Entity ID Normalization

All entity references use `type:name` format with lowercase snake_case:

```
nakshatra:ashwini          NOT nakshatra_ashwini, nakshatra:Ashwini
graha:surya                NOT graha:Sun, graha_surya
dosha:vata                 NOT ayurveda:Vata, dosha_vata
species:wolf_spider        NOT species:WolfSpider
cosmology:patala           NOT loka:patala, cosmology:Patala
```

The normalization script is at `scripts/normalize_entity_ids.py`.
Run it with `--dry-run` first, always.

---

## Relation CSV Schema

All relation files in `datasets/relations/` use this schema:
```
from_id, relation, to_id, confidence, attestation, tradition, source, notes
```

Valid attestation values:
```
SHASTRA:PRIMARY    — direct primary text citation with verse number
SHASTRA:SECONDARY  — from named commentary or secondary Vedic source
OBSERVED:TRADITIONAL — documented traditional practice
SYNTHESIS          — cross-traditional inference, reasoned mapping
INFERRED:BIOLOGY   — derived from biological/behavioral observation
INFERRED:COHERENT  — derived from system coherence logic
seed_unverified    — working hypothesis, needs corpus verification
```

**Canon file is sacred**: `datasets/relations/relations_resolved_canon.csv`
Never modify it directly. Never run deduplication on it.

---

## Ingestion Pipeline Sequence

For any new dataset, follow this sequence in order:

```
1. RECEIVE raw data (CSV, JSONL, text file, web fetch)

2. VALIDATE schema
   — Check all required columns present
   — Check entity IDs are in type:name format
   — Check no commas in field values (use semicolons)
   — Check attestation values are valid

3. NORMALIZE IDs
   scripts/normalize_entity_ids.py --file [file] --dry-run
   Review output, then run without --dry-run

4. DEDUPLICATE (for relation files)
   scripts/deduplicate_relations.py --file [file]

5. WRITE to correct location
   Species data → datasets/species/
   Geography → datasets/geography/
   Relations → datasets/relations/
   Corpus passages → datasets/sources/[tradition]/

6. REGISTER (for JSONL files)
   Update datasets/sources/corpus_registry.json
   Append to atlas/registry/corpus_registry.jsonl

7. VERIFY
   curl localhost:5000/corpus/search?q=[key_term]
   Check entity refs resolve in entity_registry.csv

8. LOG in ATLAS_CYCLE_LOG.md
   Format: YYYY-MM-DD HH:MM — [TASK] DONE — [what was done]
```

---

## Current Research Outputs Ready for Ingestion

These files exist in outputs and are ready to be ingested into Atlas:

| File | Target | Rows | Status |
|------|--------|------|--------|
| `aboriginal_animals.csv` | `datasets/species/aboriginal_animals.csv` | 40 | Ready |
| `loka_dimensions.csv` | `datasets/cosmology/loka_dimensions.csv` + JSONL | 15 | Ready |
| VPK 63-row docx | `datasets/species/vpk_global_inference.csv` | 63 | Needs CSV extraction |
| Medicine Cards 10-row | `datasets/species/medicine_cards_vedic.csv` | 10 | Partial — needs full 61 rows |

---

## Corpus Expansion Priority Queue

These text corpora should be ingested in priority order:

```
HIGH PRIORITY (primary shastra — highest attestation):
  1. Bhagavatam Canto 5 Ch 24-25 (Patala + Ananta) — verse-level fetch from Vedabase
  2. Brhat Samhita shakuna chapters (crow omens, bird omens) — Wisdomlib
  3. Panchatantra (psychological types) — Wisdomlib or GRETIL

MEDIUM PRIORITY (secondary shastra):
  4. Bhagavatam Canto 2 (Virat Purusha, loka structure) — Vedabase
  5. Arthashastra animal chapters — GRETIL
  6. Hastyayurveda elephant medicine — if available

SYNTHESIS LAYER (research CSV → JSONL):
  7. aboriginal_animals.csv → passages
  8. loka_dimensions.csv → passages
  9. vpk_global_inference.csv → passages
  10. medicine_cards_vedic.csv → passages (when complete)
```

---

## Key Scripts Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/normalize_entity_ids.py` | Fix entity ID format | `--file [csv] --dry-run` |
| `scripts/deduplicate_relations.py` | Remove duplicate relations | `--file [csv]` |
| `scripts/promote_overlay_relations.py` | Promote seed→attested | `--threshold 0.7` |
| `scripts/build_entity_registry.py` | Rebuild entity_registry.csv | no args |
| `scripts/corpus_health.py` | Check corpus integrity | no args |
| `scripts/chunk_bg.py` | BG chunking reference pattern | read before writing new chunkers |

---

## What Claude Must Never Do

- Write to `relations_resolved_canon.csv` directly
- Set `authority: shastra` on synthesized or inferred data
- Create JSONL chunks without `chunk_id` and `entity_refs` fields
- Skip corpus_registry.json registration after creating JSONL
- Use commas inside CSV field values (breaks parsing)
- Assume an entity ID is valid without checking entity_registry.csv
- Promote relations from seed_unverified without corpus evidence
- Create a new tradition value not in the valid list above
- Run normalize_entity_ids.py without --dry-run first
