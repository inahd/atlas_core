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
