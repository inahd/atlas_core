#!/bin/bash
# install_cycle_wave4.sh — Atlas Wave 4: Corpus Ingestion
#
# Creates task prompts in docs/prompts/queue/
# Run with: bash scripts/install_cycle_wave4.sh
# Then: bash scripts/run_cycle.sh --auto

set -e
QUEUE="$HOME/atlas_core/docs/prompts/queue"
mkdir -p "$QUEUE"

echo "✦ Installing Wave 4 tasks: Corpus Ingestion"

# ── COR-010: Cross-Mapping Medicine Cards Animals ──────────
cat > "$QUEUE/COR-010_aboriginal_animals.md" << 'TASK'
COR-010: Ingest Cross-Mapping Medicine Cards Animals dataset

Source: ~/Downloads/Cross-Mapping Medicine Cards Animals to Vedic Cosmology_ A 61-Row Dataset.docx
Target CSV: datasets/species/aboriginal_animals.csv
Target JSONL: datasets/sources/species/aboriginal_animals_passages.jsonl

Steps:
1. Convert docx to markdown: pandoc "$SOURCE" -t markdown
2. Extract the table data (61 rows of animals with columns:
   animal_name, medicine_card_archetype, vpk_inference,
   graha, nakshatra, deity_myth, element, color, season,
   body_system, confidence, sources)
3. Parse from the markdown table or preview section
4. If table not parseable, extract from the prose descriptions
   (each animal has a section with mappings)
5. Write CSV to datasets/species/aboriginal_animals.csv
6. Convert each row to a natural-language JSONL passage:
   {"text_id":"aboriginal_animals","chunk_id":"aboriginal_animals_NNNN",
    "ordinal":N,"text":"[animal] is associated with [archetype]...",
    "tradition":"indigenous_vedic","authority":"synthesis",
    "entity_refs":["species_[animal]"],"tags":["animal","vpk"]}
7. Write JSONL to datasets/sources/species/aboriginal_animals_passages.jsonl
8. Register in datasets/sources/corpus_registry.json
   (add entry: id=aboriginal_animals, family=species, chunks=N, status=cached)
9. Verify: curl -s localhost:5000/corpus/search?q=eagle | python3 -m json.tool | head -10

Success: CSV has 50+ rows, JSONL has same count, corpus search returns results
TASK
echo "  ✓ COR-010 (aboriginal animals)"

# ── COR-011: Loka Dimensions from existing cosmology data ──
cat > "$QUEUE/COR-011_loka_dimensions.md" << 'TASK'
COR-011: Create Loka Dimensions dataset from Puranic sources

There is no loka_dimensions.csv in Downloads. Create it from known Puranic data.

Target CSV: datasets/cosmology/loka_dimensions.csv
Target JSONL: datasets/sources/puranic/loka_dimensions_passages.jsonl

Steps:
1. Create datasets/cosmology/loka_dimensions.csv with these 14 lokas:
   Columns: loka_name, loka_type (upper/lower), position (1-14),
   ruler, element, description, source_verse, attestation_status

   Upper 7 (Bhuvanas):
   Bhu (Earth), Bhuvar (Atmosphere), Svar (Heaven),
   Mahar (Saints), Jana (Sages), Tapa (Austerity), Satya/Brahma (Truth)

   Lower 7 (Patalas):
   Atala, Vitala, Sutala, Talatala, Mahatala, Rasatala, Patala

   Sources: Vishnu Purana 2.7, Bhagavata Purana 5.24-26
   Attestation: SHASTRA:PRIMARY

2. Convert each row to JSONL passage with source_verse preserved
3. Write to datasets/sources/puranic/loka_dimensions_passages.jsonl
4. Register in corpus_registry.json
5. Verify: curl -s localhost:5000/corpus/search?q=patala | python3 -m json.tool | head -10

Success: CSV has 14 rows with source_verse citations, JSONL registered
TASK
echo "  ✓ COR-011 (loka dimensions)"

# ── COR-012: VPK Global Inference for 63 Animals ──────────
cat > "$QUEUE/COR-012_vpk_global.md" << 'TASK'
COR-012: Extract and ingest VPK Global Inference dataset (63 animals)

Source: ~/Downloads/Extending a Vedic Cosmological Knowledge Graph With VPK Inferences for Sixty Animals.docx
Target CSV: datasets/species/vpk_global_inference.csv
Target JSONL: datasets/sources/species/vpk_global_passages.jsonl

Steps:
1. Convert docx: pandoc "$SOURCE" -t markdown
2. Extract the 63-row dataset. Look for table data or
   structured sections with per-animal attributes:
   animal_name, common_name, taxonomic_family,
   vpk_primary, vpk_secondary, vpk_confidence,
   ecological_niche, iucn_status, cultural_significance,
   vedic_resonance, graha, element, body_system, attestation
3. If table not directly parseable, extract from prose sections
   (each animal has structured attributes listed)
4. Write CSV to datasets/species/vpk_global_inference.csv
5. Convert to JSONL passages (one per animal)
6. Write to datasets/sources/species/vpk_global_passages.jsonl
7. Register in corpus_registry.json
8. Verify: curl -s localhost:5000/corpus/search?q=wolverine | python3 -m json.tool | head -10

Success: CSV has 60+ rows, JSONL registered, corpus search works
TASK
echo "  ✓ COR-012 (VPK global inference)"

# ── COR-013: Bhagavatam Canto 5 Patala descriptions ──────
cat > "$QUEUE/COR-013_bhagavatam_patala.md" << 'TASK'
COR-013: Create Bhagavatam Canto 5 Patala passages

Do NOT fetch from vedabase.io (avoid scraping external sites).
Instead, create passage summaries from known SB 5.24-25 content.

Target JSONL: datasets/sources/puranic/sb_canto5_patala_chunks.jsonl

Steps:
1. Create JSONL with 15-20 chunks covering SB 5.24-25 topics:
   - SB 5.24.8: Atala ruled by Maya Danava
   - SB 5.24.9-10: Vitala (Shiva as Hatakesvara, gold river)
   - SB 5.24.11-12: Sutala (Bali Maharaja, Vishnu as doorkeeper)
   - SB 5.24.13-14: Talatala (Maya Danava's abode)
   - SB 5.24.15: Mahatala (serpents, Kadru's sons)
   - SB 5.24.16: Rasatala (Daityas and Danavas)
   - SB 5.24.17-31: Patala (Ananta Sesha supports the universe)
   - SB 5.25: Ananta Sesha description

2. Each chunk:
   {"text_id":"sb_canto5_patala","chunk_id":"sb5_24_NN",
    "ordinal":N,"text":"SB 5.24.X — [paraphrase of verse content]",
    "verse":"SB 5.24.X","tradition":"gaudiya_vaishnava",
    "authority":"shastra","tags":["bhagavatam","patala","cosmology"],
    "entity_refs":["loka_[name]"]}

3. Register in corpus_registry.json
4. Verify: curl -s localhost:5000/corpus/search?q=ananta | python3 -m json.tool | head -10

Note: Use traditional knowledge of these verses, not web scraping.
Attestation: SHASTRA:PRIMARY
Success: 15+ chunks, corpus search returns Ananta/Patala results
TASK
echo "  ✓ COR-013 (Bhagavatam patala)"

# ── COR-014: Brhat Samhita Shakuna (bird omens) ──────────
cat > "$QUEUE/COR-014_brhat_samhita_shakuna.md" << 'TASK'
COR-014: Create Brhat Samhita Shakuna (bird omen) passages

Do NOT scrape wisdomlib.org or any external site.
Create passage summaries from known Brhat Samhita content.

Target JSONL: datasets/sources/jyotish/brhat_samhita_shakuna_chunks.jsonl

Steps:
1. Create JSONL with 12-15 chunks covering Brhat Samhita chapters
   on animal omens (Shakuna Shastra), especially chapters 86-95:
   - Crow omens (kaka shakuna) — directions, timing, calls
   - Lizard omens (chipkali) — body-part-fall significance
   - Cat omens — crossing direction, color
   - Dog omens — howling, direction
   - Bird flight omens — left/right, height, species
   - Owl omens — hooting timing
   - Snake omens — crossing path, species

2. Each chunk:
   {"text_id":"brhat_samhita_shakuna","chunk_id":"bs_shakuna_NN",
    "ordinal":N,"text":"Brhat Samhita on [topic] — [traditional content]",
    "tradition":"jyotish","authority":"shastra",
    "tags":["brhat_samhita","shakuna","omen","[animal]"],
    "entity_refs":["species_[animal]"]}

3. Register in corpus_registry.json
4. Verify: curl -s localhost:5000/corpus/search?q=crow | python3 -m json.tool | head -10

Note: Summarize traditional knowledge, cite BS chapter numbers.
Attestation: SHASTRA:PRIMARY
Success: 12+ chunks, corpus search returns crow/omen results
TASK
echo "  ✓ COR-014 (Brhat Samhita shakuna)"

echo ""
echo "✦ Wave 4 installed: $(ls "$QUEUE"/COR-01*.md 2>/dev/null | wc -l) tasks"
echo "  Queue: $QUEUE"
echo ""
echo "Run: bash scripts/run_cycle.sh --auto"
