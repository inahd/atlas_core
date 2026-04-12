# COR-005: Add Rasashastra corpus

**Phase**: 4  
**Priority**: MEDIUM  
**Estimated time**: 2–4 hrs

## Context

Rasashastra (Ayurvedic alchemy/mineral medicine) is missing from the corpus.
It connects the herb_exemplars, dhatu_herb_matrix, and ratna (gemstone) layers
to textual grounding. Key texts: Rasa Ratna Samuccaya, Rasendra Chudamani,
Rasa Tarangini.

## Instructions

### Step 1: Check what's available locally

```bash
find ~/atlas_core -name "*rasa*" -o -name "*rasashastra*" 2>/dev/null | grep -v ".pyc"
find / -name "*rasashastra*" -o -name "*rasa_ratna*" 2>/dev/null | \
  grep -i "\.txt\|\.json" 2>/dev/null | head -10
```

Check existing ayurveda corpus:
```bash
ls ~/atlas_core/datasets/sources/ayurveda/
wc -l ~/atlas_core/datasets/sources/ayurveda/*.jsonl
```

### Step 2: Check for overlap with existing Charaka/Sushruta

Charaka Samhita and Sushruta Samhita both have mineral/rasayana sections.
Check what's already in the corpus:
```bash
python3 -c "
import json
chunks = [json.loads(l) for l in
          open('datasets/sources/ayurveda/charaka_samhita_en_chunks.jsonl')]
rasa = [c for c in chunks if 'mercury' in c['text'].lower() or
        'mineral' in c['text'].lower() or 'rasa' in c['text'].lower()]
print(f'Charaka rasa-related chunks: {len(rasa)}')
if rasa: print('Sample:', rasa[0]['text'][:200])
"
```

If coverage is adequate from existing texts, document that and close this task.

### Step 3: Source Rasa Tarangini

Rasa Tarangini (Sadananda Sharma, 1920) has partial English translations
available via academic sources.

Check:
```bash
curl -s --max-time 5 "https://www.wisdomlib.org/hinduism/book/rasa-tarangini" | \
  grep -i "chapter\|section" | head -10
```

### Step 4: Build minimal Rasashastra dataset even without full text

If no full text is available, build a structured CSV dataset instead:
`datasets/ayurveda/rasashastra_minerals.csv`:

```
mineral_id, name_sanskrit, name_iast, name_english, processing_method,
dhatu_affinity, dosha_effect, rasa, virya, vipaka, contraindications,
source_text, attestation_status
```

Populate with the classical 8 mahadhatus (mercury, sulfur, gold, silver, copper,
iron, tin, lead) and their Ayurvedic properties.

This is high-value even without the full text corpus.

### Step 5: HUMAN_REQUIRED condition

If full text corpus is not achievable, fall back to the CSV dataset.
Mark as PARTIAL in the log — not FAILED.

## Success check

```bash
# Either corpus file OR mineral CSV:
test -f ~/atlas_core/datasets/sources/ayurveda/rasashastra_en_chunks.jsonl && \
  echo "Corpus: $(wc -l < ~/atlas_core/datasets/sources/ayurveda/rasashastra_en_chunks.jsonl) chunks" || \
  (test -f ~/atlas_core/datasets/ayurveda/rasashastra_minerals.csv && \
   echo "Mineral CSV: $(wc -l < ~/atlas_core/datasets/ayurveda/rasashastra_minerals.csv) rows") || \
  echo "Neither file created"
```

## Output

- Either: `datasets/sources/ayurveda/rasashastra_en_chunks.jsonl`
- Or: `datasets/ayurveda/rasashastra_minerals.csv` (fallback)
- Update corpus registry if JSONL created
