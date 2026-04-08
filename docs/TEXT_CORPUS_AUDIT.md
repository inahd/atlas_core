# TEXT CORPUS AUDIT

Date: 2026-04-07

## A. Actually available texts
- `datasets/sources/manifest.json` plus `corpus_registry.json` define ~40 corpus entries (Bg, Purana cantos, Gaudiya scripture, Yoga, Ayurveda, Jyotish, cosmology) and their cached status.
- Raw sources (primarily `.txt` files) live under `datasets/sources/<domain>/`. Every cached manifest entry points to `raw_path`.
- Chunked abstractions exist as JSONL under `datasets/sources/<domain>/*_chunks.jsonl` (e.g., `datasets/sources/gaudiya/bg_chunks.jsonl`, `datasets/sources/ayurveda/charaka_samhita_chunks.jsonl`).
- Verse-level JSON is present for Bhagavata Purana (`datasets/sources/gaudiya/bg_verses/*.json`).
- Research-oriented documents are listed in `datasets/sources/sources.csv` and stored under `docs/sources/` (`bhakti_rasamrita_sindhu.pdf`, `tattva_viveka.pdf`, etc.) plus `/opt/atlas/research/_text` text dumps (e.g., `Nakshatra-Sooktam-Eng-v1.txt`).
- Passage registry data is available at `datasets/sources/passages.csv` for fast reference lookups.

## B. Canonical usable core
| Title | ID | Domain | Status | Path(s) | Best local format |
|-|-|-|-|-|-|
| Bhagavad Gita (Bhagavatam 10 excerpts + stand-alone) | `bg` | gaudiya | cached | `datasets/sources/gaudiya/bg_chunks.jsonl`, `datasets/sources/gaudiya/bg_verses/*.json` | Verse JSON (`bg_verses/*.json`) gives chant-level splits; JSONL chunk is the entry point for study UI. |
| Bhagavata Purana Canto 1/5/10 | `bhagavata_purana_*` | cosmology | cached | `datasets/sources/cosmology/bhagavata_purana_*_chunks.jsonl` + raw `.txt` | JSONL chunk (canto-specific) to keep text manageable; `bg_verses` only exists for canto 10. |
| Bhakti-rasamrita-sindhu | `bhakti_rasamrita_sindhu_en` | gaudiya | cached | `datasets/sources/gaudiya/bhakti_rasamrita_sindhu_en.txt` + `*_chunks.jsonl` | JSONL chunk ideal for UI; raw `.txt` in the same folder for manual lookup. |
| Brahma-saṃhitā ch.5 | `brahma_samhita` | gaudiya | cached | `datasets/sources/gaudiya/brahma_samhita.txt`, `.jsonl` | JSONL chunk for ingestion; raw text for proofs. |
| Sikṣāṣṭaka | `sikshashtakam` | gaudiya | cached | `datasets/sources/gaudiya/sikshashtakam.txt` + `*_chunks.jsonl` | JSONL chunk. |

## C. Adjacent/supporting texts
### Vedic / Upanishads / Brahmanas
- Rigveda, Atharvaveda, Upanishads, Aitareya & Isha Upanishads (`datasets/sources/vedic/*_chunks.jsonl`) — all cached, raw `.txt` available; best read via JSONL for chunked search.
### Yoga / Tantra
- Yoga Sutras, Hatha Yoga Pradīpikā, Gheranda Samhitā, Śiva Samhitā, Tantrāloka, Kularṇava Tantra, Vijñāna Bhairava (`datasets/sources/yoga/*_chunks.jsonl`) — chunked caches plus Sanskrit (`*_sa_chunks`). Raw `.txt` files exist for each.
### Jyotiṣa
- Brihat Jātaka, Surya Siddhanta, Brihat Saṃhitā, (Brihat Parāśara Hora failed), numerous Sanskrit/English chunk pairs under `datasets/sources/jyotish/`.
### Ayurveda / Plant knowledge
- Bhāvaprakāśa, Cakra Samhitā (in English & Sanskrit chunks), Yogasataka (cache), plus digital files. Best explored via `*_chunks.jsonl`.
### Cosmology / Purana & dharma
- Bhagavata Purana, Skanda, Devi Bhāgavatam, Brahma Vaivarta, Śiva Purana, Markandeya Purana, etc., `datasets/sources/cosmology/*_chunks.jsonl`.
### Dharmashastra / Vastu
- Arthaśāstra, Manusmṛti, Nītiśāstra, Mānasāra, Bṛhat Saṃhitā (Vastu-focused), with chunked caches.
### Gaudiya research PDFs
- `docs/sources/gaudiya/*.pdf` (Rūpa Gosvāmī, Bhaktivinoda, etc.) plus `datasets/sources/sources.csv` entries pointing to `/opt/atlas/research/_text/*`. Those are ready for `/study` search if added to manifest.
### Internal research texts
- Files under `/opt/atlas/research/_text/` (Nakṣatra-Vidnyāna, Kīrtan guides, infographics) listed in `sources.csv`: plain `.txt`, so usable once registry references them.

## D. Partial / broken / unavailable
- `brihat_parashara_hora`, `ashtanga_hridayam`, `sushruta_samhita`, `taittiriya_brahmana`, `natya_shastra` — manifest says `status: failed` because remote URLs returned 404; no local `.txt` or chunks exist.
- Many Sanskrit-language sets have only partial chunk coverage (e.g., `brihat_jataka_sa_chunks`, `charaka_samhita_sa_chunks`) — cached but readability relies on unstructured transliteration splits.
- Research manifest hints at PDF/converted text duplicates (some `djvu` conversions) that are unindexed until added to `corpus_registry.json`.

## E. Best local source format per major text
- **Bhagavad Gita / Bhagavata Purana**: prefer `datasets/sources/gaudiya/bg_verses/*.json` for verse-level retrieval; fallback to `*_chunks.jsonl` for aggregated fetches; raw `.txt` for verification.
- **Gītas & Sutras (Yoga, Ayurveda, Jyotiṣa)**: JSONL chunks under each domain keep the best tradeoff between search speed and readability.
- **Research PDFs (Gaudiya classics)**: keep as stored in `docs/sources/gaudiya/*.pdf` with `sources.csv` mapping; convert to plain `.txt` for text-mode ingestion (already done).
- **Vedic corpora**: use the chunked indexes in `datasets/sources/vedic/`, e.g., `atharvaveda_en_chunks.jsonl`; Sanskrit-specific `*_sa_chunks` are there when precise transliteration is required.
- **Cosmology / puranas**: `datasets/sources/cosmology/*_chunks.jsonl` and `passages.csv` (for canonical cross-references) are the best immediate formats.
- **Verse JSON (BG cantos)**: `datasets/sources/gaudiya/bg_verses_index.jsonl` plus per-canto files allow precise page navigation; use when referencing `bhagavata_purana_10`.

## F. Top-priority fixes or reacquisitions
1. Re-fetch the `failed` manifest entries (`brihat_parashara_hora`, `ashtanga_hridayam`, `sushruta_samhita`, `taittiriya_brahmana`, `natya_shastra`) from alternate mirrors or mirror the source by hand.
2. Surface the research text registry (`sources.csv`) inside `corpus_registry.json` so `/study` knows the ready `.txt`/PDF conversions in `/opt/atlas/research/_text` and `docs/sources`.
3. Clean up duplicate raw text copies (e.g., `bhakti_rasamrita_sindhu_en` vs `_1` vs `_chunks`) so manifest and UI pull from a single canonical file.
4. Document the verse JSON pipeline (`bg_verses/*.json`) and expose it to `/study` as the preferred canonical format for Bhagavata Purana canto 10.
5. Confirm chunk coverage for Sanskrit versions tagged `*_sa_chunks.jsonl` so `/study` can switch languages without falling back to raw text each time.
