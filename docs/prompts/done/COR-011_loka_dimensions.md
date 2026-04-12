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
