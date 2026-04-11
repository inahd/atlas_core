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
