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
