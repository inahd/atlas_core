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
