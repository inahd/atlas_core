# Research↔Dataset Correspondence Matrix

Generated April 22, 2026

---

## Summary

| Metric | Count |
|--------|-------|
| Dataset domains | 42 |
| Research artifacts | 53 (32 md + 9 json + 8 docx + 4 duplicates) |
| FULL_PAIR | 3 (research + dataset + compendium volume) |
| RESEARCH_ONLY | 5 (prose exists, no structured dataset) |
| DATASET_ONLY | 18 (data exists, no research document) |
| RESEARCH_WITH_DATASET | 11 (both exist, compendium scaffold present) |
| ORPHAN scaffolds | 2 (compendium volume has no clear research-dataset pair) |
| Canonical research files | 20 |
| Superseded research files | 8 |
| docx pending conversion | 8 |

---

## Domain-by-Domain Mapping

### astro (16 CSV)
- **Dataset**: nakshatra_master, nakshatra_canonical, nakshatra_core, nakshatra_extended, nakshatra_full, nakshatra_deities, nakshatra_padas, nakshatra_syllables, nakshatra_num_to_name, tithi_master, tithi_core, tithi_list, tithi_data, tithi_deities, tithi_properties
- **Research**: planetary-primes-v1.md (partial), two-source-interference-v3.md (partial — nakshatra field), vertebral-primes-v1.md (partial — yoni animals)
- **Compendium**: research_papers/planetary_primes.typ, research_papers/two_source_interference.typ, field_dives/07_nakshatra_plant_correspondences.typ
- **Engine-live**: 6 (nakshatra_master, nakshatra_canonical, nakshatra_padas, tithi_master, tithi_deities). Rest loaded by layer_composer or datasets.py bulk loader.
- **Classification**: RESEARCH_WITH_DATASET
- **Gaps**: tithi_properties.csv and the 5 variant nakshatra files have no dedicated research doc

### astrobotany (4 CSV)
- **Dataset**: herbs_by_class, lunar_planting_matrix, nakshatra_botany, plant_remedy_bridge
- **Research**: research_astrobotanical_classes.md (30KB), research_astrobotany_lunar.md (51KB)
- **Compendium**: no direct scaffold
- **Engine-live**: 0 direct engine refs, but astrobotany_engine.py may load via datasets.py
- **Classification**: RESEARCH_WITH_DATASET (no compendium scaffold)
- **Proposed**: create field_dives/astrobotany.typ stub

### ayurveda (18 CSV)
- **Dataset**: amidha_herbs, dhatu_herb_matrix, dinacharya_panchanga, dosha_nakshatra_matrix, herb_dosha_matrix, herb_exemplars, herb_master, rasayana_herbs, sapta_dhatu, ... (18 total)
- **Research**: research_ayurveda_panchanga.md (30KB), "Ayurveda Sublayer Research — Bhasma _ Rasasastra" .docx (26KB)
- **Compendium**: field_dives/05_ayurveda_and_the_108_herbs.typ (scaffold)
- **Engine-live**: 4 (dhatu_herb_matrix, dinacharya_panchanga, dosha_nakshatra_matrix, herb_exemplars)
- **Classification**: RESEARCH_WITH_DATASET
- **Gaps**: 14 CSVs not referenced by any engine. Bhasma docx not converted to md.

### canonical (6 JSON)
- **Dataset**: nakshatras.json, rashis.json, grahas.json, tithis.json, elements.json, gunas.json
- **Research**: none directly
- **Compendium**: no direct scaffold
- **Classification**: DATASET_ONLY
- **Notes**: canonical reference tables. Small, stable. No prose argument needed — they ARE the canonical values.

### carnatic (7 CSV)
- **Dataset**: 35_talas, gati_definitions, korvai_rules, navagraha_kritis, sollukattu, tala_families, tala_master
- **Research**: research_carnatic_tala_complete.md (35KB, canonical), research_carnatic_tala.md (19KB, superseded)
- **Compendium**: no existing scaffold
- **Engine-live**: referenced by rhythm/ engines
- **Classification**: RESEARCH_WITH_DATASET (no compendium scaffold)
- **Proposed**: create field_dives/carnatic_tala.typ stub

### chandas (2 CSV)
- **Dataset**: correspondence_matrix, metres_forms
- **Research**: research_chandas.md (18KB)
- **Compendium**: no direct scaffold (could be part of field_dives/03_nada_and_raga_cosmology.typ)
- **Engine-live**: metres_forms via layer_composer
- **Classification**: RESEARCH_WITH_DATASET

### compositions (3 CSV + 1 JSON)
- **Dataset**: compositions.json, narottama_padas.csv, nakshatra_kritis.csv, composition_relations.csv
- **Research**: none directly
- **Compendium**: no direct scaffold
- **Classification**: DATASET_ONLY
- **Notes**: operational corpus for composition_engine. No prose argument.

### cosmology (20 CSV)
- **Dataset**: ashtakala, bhajan_corpus, daily_program, deity_attributes, deity_domains, deity_master, deity_vahana_extended, festival_master, gaudiya_festivals, goloka_ashtakala_lila, graha_avatar_bphs, graha_face_params, graha_master, nitya_devi_mapping, nitya_devi_master, nitya_yantra_geometry, vaishnava_calendar, vraja_forests, ...
- **Research**: two-source-interference-v3.md (Nitya wave matrix), yantra_eigenvalue_exploration.md (graha yantras), planetary-primes-v1.md (graha retrograde)
- **Compendium**: field_dives/02_nitya_devi_registry.typ, field_dives/04_yantra_geometry_and_chladni.typ, field_dives/08_vedic_cosmology_and_the_loka_system.typ, research_papers/lo_shu_spectral_carrier.typ
- **Engine-live**: 12+ via layer_composer, goloka_engine, devi_engine
- **Classification**: RESEARCH_WITH_DATASET (richest domain)

### entities (8 CSV + reference JSONs)
- **Dataset**: entity CSVs (nakshatra.csv, rashi.csv, jyotish.csv, ...), reference/ dir with detailed entity JSONs
- **Research**: none directly
- **Compendium**: technical_reference/ontology_and_attestation.typ (scaffold)
- **Classification**: DATASET_ONLY (entity schema is operational, no prose doc)

### game (4 CSV)
- **Dataset**: lineages, sura_asura_map, character_classes, terrain_types
- **Research**: none
- **Compendium**: field_dives/11_coherence_spectrum_and_devi_field.typ (scaffold)
- **Classification**: DATASET_ONLY

### gandharva (7 CSV)
- **Dataset**: bija_master, graha_bija, graha_raga_chords, gaudiya_musical_science, instrument_data, instruments, raga_therapeutic
- **Research**: research_gandharva_veda.md (38KB)
- **Compendium**: field_dives/03_nada_and_raga_cosmology.typ (scaffold)
- **Engine-live**: 4 via layer_composer
- **Classification**: RESEARCH_WITH_DATASET

### geography (7 CSV)
- **Dataset**: continental_body_map, ecoregions, sacred_sites_india, shakti_pitha_matrix, vraja_parikrama, sacred_sites_global, ...
- **Research**: none
- **Compendium**: no direct scaffold
- **Classification**: DATASET_ONLY

### geosolar (1 CSV)
- **Dataset**: kp_log.csv (rolling geomagnetic/solar data)
- **Research**: two-source-interference-v3.md (Finding 13, Kp analysis)
- **Compendium**: no direct scaffold
- **Classification**: RESEARCH_WITH_DATASET (the Kp analysis references this data)

### iching (9 CSV)
- **Dataset**: hexagrams, hexagram_nakshatra_resonance, pasaka, trigrams, trigram_vastu_map, ...
- **Research**: iching_spectral_analysis.json, loshu_iching_interaction.json, magic_cube_*.json (6 json artifacts)
- **Compendium**: field_dives/10_oracle_instruments.typ (scaffold), research_papers/lo_shu_spectral_carrier.typ (built)
- **Engine-live**: 4 (hexagrams, pasaka, trigrams, trigram_vastu_map)
- **Classification**: FULL_PAIR (Lo Shu paper is built and references this data)

### jyotish (5 CSV + 3 YAML)
- **Dataset**: graha_aspects, graha_dignity, graha_friendship, graha_karakas, rashi_lords, graha.yaml, nakshatra.yaml, rashi.yaml
- **Research**: two-source-interference-v3.md (aspect theory), planetary-primes-v1.md
- **Compendium**: field_dives/01_jyotish_and_wave_field.typ (scaffold), research_papers/two_source_interference.typ (scaffold)
- **Engine-live**: all 5 CSV via jyotish_utils.py loaders
- **Classification**: RESEARCH_WITH_DATASET

### karma (1 CSV)
- **Dataset**: dasha_meanings.csv
- **Research**: none
- **Engine-live**: 1 (referenced by engine but file may be missing)
- **Classification**: DATASET_ONLY

### mappings (1 JSON)
- **Dataset**: field_entity_map.json
- **Research**: none
- **Classification**: DATASET_ONLY

### marma (4 CSV)
- **Dataset**: body_region_marma, marma_coordinates, marma_field, marma_points
- **Research**: vertebral-primes-v1.md (44 upper-limb marma = wave field regions)
- **Compendium**: no direct scaffold
- **Classification**: RESEARCH_WITH_DATASET (partial — vertebral paper references marma count)

### morphogenesis (3 CSV)
- **Dataset**: archetype_matrix, body_archetype_map, doctrine_of_signatures
- **Research**: none
- **Compendium**: no direct scaffold
- **Classification**: DATASET_ONLY

### ontology (6 CSV + 1 YAML)
- **Dataset**: bhava_relations, bhava_types, rasa_siddhanta, vaishnava_tattva, ...
- **Research**: none
- **Compendium**: technical_reference/ontology_and_attestation.typ (scaffold)
- **Classification**: DATASET_ONLY (ontology tables, no prose argument)

### overlays (2 CSV)
- **Dataset**: vaishnava_hermeneutic, aboriginal_overlay
- **Research**: briefs/2026-04-04-aboriginal-overlay-brief.md
- **Classification**: RESEARCH_WITH_DATASET (brief exists)

### permaculture (1 CSV)
- **Dataset**: permaculture_principles.csv
- **Research**: "Vastu permaculture research" .docx (3 versions)
- **Compendium**: field_dives/06_vastu_and_ecological_design.typ (scaffold)
- **Classification**: RESEARCH_WITH_DATASET (docx not converted)

### plants (10 CSV + 1 JSON + 1 YAML)
- **Dataset**: guild_full, guild_matrix, guild_matrix_raw, guild_principles, guild_relations, herb_dosha_plant_map, nakshatra_agriculture, nakshatra_plants, pfaf_structured, sacred_plants
- **Research**: "Coherence Atlas – Plant Profiles" .docx (20KB), research_astrobotanical_classes.md (30KB)
- **Compendium**: field_dives/07_nakshatra_plant_correspondences.typ (scaffold)
- **Engine-live**: 4 (guild_principles, guild_relations, nakshatra_plants, sacred_plants)
- **Classification**: RESEARCH_WITH_DATASET

### ratna (1 CSV)
- **Dataset**: graha_gems.csv
- **Research**: "Electromagnetic and Crystallographic Properties..." .docx, "Graha Friendship_Enmity and Material Interactions..." .docx
- **Engine-live**: 1
- **Classification**: RESEARCH_WITH_DATASET (docx not converted)

### relations (27 CSV)
- **Dataset**: 27 relation CSVs including relations_resolved_canon.csv (DO NOT MODIFY)
- **Research**: none directly
- **Compendium**: technical_reference/ontology_and_attestation.typ (scaffold)
- **Classification**: DATASET_ONLY (operational graph edges, no prose argument)

### ritual (2 CSV + 1 YAML)
- **Dataset**: plant_ritual, vaishnava_calendar, ritual_types.yaml
- **Research**: none
- **Classification**: DATASET_ONLY

### sanskrit (1 CSV)
- **Dataset**: matrika_50.csv
- **Research**: none
- **Classification**: DATASET_ONLY
- **Notes**: file may be missing (referenced but not verified)

### schema, semantics, silpa (1 each)
- **Classification**: DATASET_ONLY (operational tables, no research)

### sound (11 CSV)
- **Dataset**: field_music_mood, gamak_properties, raga_data, raga_phrase_library, raga_seasonal, tabla_grammar, tala_data, tala_layakari, tala_phrases, tanpura_strings, vocal_phoneme_map
- **Research**: research_svara_shastra.md (15KB), research_gandharva_veda.md (38KB, partial)
- **Compendium**: field_dives/03_nada_and_raga_cosmology.typ (scaffold)
- **Engine-live**: 6 via sound engines
- **Classification**: RESEARCH_WITH_DATASET

### sources (4 CSV + 4 JSON + 140K JSONL chunks)
- **Dataset**: corpus_registry.json, entity_index.json, passages.csv, gaudiya_passages.csv, + 14 subdirectories of JSONL chunks
- **Research**: none directly (the corpus IS the source material)
- **Classification**: DATASET_ONLY (the corpus is the reference, not the subject of research)

### species (7 CSV)
- **Dataset**: nakshatra_species, species_entities, vpk_global_inference, ...
- **Research**: vertebral-primes-v1.md (cross-species analysis)
- **Compendium**: research_papers/vertebral_primes.typ (scaffold, private)
- **Classification**: RESEARCH_WITH_DATASET

### svarodaya (6 CSV)
- **Dataset**: activity_matrix, coherence_rules, elements, nadis, tithi_rules, vara_rules
- **Research**: research_svara_shastra.md (15KB)
- **Compendium**: no direct scaffold (covered by field_dives/01_jyotish_and_wave_field.typ tangentially)
- **Engine-live**: all 6
- **Classification**: RESEARCH_WITH_DATASET

### symbols (6 CSV + 1 JSON)
- **Dataset**: atlas_glyphs, emoji_vedic_map, profession_emoji_mapping, ...
- **Research**: none
- **Classification**: DATASET_ONLY

### system (4 CSV + 1 JSON)
- **Dataset**: capability_map, code_topology, system_topology, ...
- **Research**: gpu_benchmark_results.md, gpu_diagnosis.md, igpu_benchmark_full_report.md
- **Compendium**: technical_reference/architecture_and_api.typ (scaffold)
- **Classification**: RESEARCH_WITH_DATASET

### tantra (2 CSV)
- **Dataset**: chakra_cross_domain, (1 other)
- **Research**: none
- **Classification**: DATASET_ONLY

### tarot (3 JSON)
- **Dataset**: devi_cards.json, nakshatra_cards.json, (1 other)
- **Research**: none
- **Classification**: DATASET_ONLY

### temples (2 CSV)
- **Dataset**: temple sites
- **Research**: none
- **Classification**: DATASET_ONLY

### vastu (11 CSV)
- **Dataset**: pada_108, perimeter_deities, vastu_zone_prescriptions, ...
- **Research**: research_vastu_mandala.md (29KB)
- **Compendium**: field_dives/06_vastu_and_ecological_design.typ (scaffold)
- **Engine-live**: 1 (perimeter_deities)
- **Classification**: RESEARCH_WITH_DATASET

### views (1 CSV)
- **Dataset**: view_definitions
- **Classification**: DATASET_ONLY

### yoga (5 CSV)
- **Dataset**: asana_core, marma_master, nakshatra_body_map, pranayama, yoga_sutra_categories
- **Research**: research_pranayama_asana.md (55KB)
- **Compendium**: no direct scaffold
- **Classification**: RESEARCH_WITH_DATASET

---

## FULL_PAIR domains (3)

| Domain | Research | Dataset | Compendium |
|--------|----------|---------|-----------|
| iching | lo_shu papers + 6 JSON artifacts | 9 CSV | lo_shu_spectral_carrier.typ (built) |
| cosmology (Nitya) | two-source-interference-v3.md | nitya_devi_master + yantra_geometry | field_dives/02_nitya_devi_registry.typ (scaffold) |
| cosmology (Lo Shu) | yantra_eigenvalue_exploration.md | graha_master + canonical | research_papers/lo_shu_spectral_carrier.typ (built) |

## DATASET_ONLY domains (18) — silent operational claims

These datasets are loaded and used by engines but have no research document attesting to them:

| Domain | Files | Priority |
|--------|-------|----------|
| canonical | 6 JSON | Low — self-evident reference values |
| compositions | 3 CSV + 1 JSON | Medium — composition engine uses these |
| entities | 8 CSV | Low — entity schema, operational |
| game | 4 CSV | Low — game layer not active |
| geography | 7 CSV | Medium — sacred geography needs attestation doc |
| karma | 1 CSV | Low — may be missing file |
| mappings | 1 JSON | Low — operational |
| morphogenesis | 3 CSV | High — doctrine of signatures claims need attestation |
| ontology | 6 CSV + 1 YAML | Medium — bhava/rasa/tattva ontology |
| relations | 27 CSV | Low — operational graph edges |
| ritual | 2 CSV + 1 YAML | Medium — vaishnava calendar needs attestation |
| sanskrit | 1 CSV | Low — matrika reference |
| schema, semantics, silpa | 1 each | Low — operational |
| sources | corpus | Low — the corpus IS the attestation |
| symbols | 7 | Low — glyph/emoji mapping |
| tantra | 2 CSV | High — chakra cross-domain claims need attestation |
| tarot | 3 JSON | Medium — devi/nakshatra card correspondences |
| temples | 2 CSV | Low — site data |
| views | 1 CSV | Low — operational |

**Highest-priority DATASET_ONLY domains for research authoring:**
1. **morphogenesis** — doctrine of signatures (44 entries) makes strong claims with no prose argument
2. **tantra** — chakra cross-domain maps chakras to nakshatras with no attestation doc
3. **geography** — 63 Shakti Pithas + 34 sacred sites with geographic claims
4. **ritual** — vaishnava calendar with festival timing claims

## ORPHAN compendium scaffolds (2)

| Volume | Status |
|--------|--------|
| field_dives/11_coherence_spectrum_and_devi_field.typ | Scaffold — references game/narrative layer that has minimal dataset backing |
| technical_reference/federation_protocol.typ | Scaffold — speculative future architecture with no current dataset or research |

## Duplicate / superseded research files

| Canonical | Superseded | Size delta |
|-----------|-----------|-----------|
| two-source-interference-v3.md (32KB) | v1 (13KB), v2 (22KB), draft (32KB=same as v3) | draft is identical to v3 |
| planetary-primes-v1.md (16KB) | planetary-primes-draft.md (16KB, identical) | identical |
| vertebral-primes-v1.md (21KB) | vertebral-primes-draft.md (21KB, identical) | identical |
| research_carnatic_tala_complete.md (35KB) | research_carnatic_tala.md (19KB) | complete supersedes partial |
| deep-research-report.md (32KB) | deep-research-report (1-7).md | numbered are subtopics |

## docx files pending markdown conversion (8)

| File | Size | Domain |
|------|------|--------|
| Ayurveda Sublayer Research — Bhasma _ Rasasastra.docx | 26KB | ayurveda |
| brahmanda_toroid_research.docx | 16KB | cosmology |
| Coherence Atlas – Plant Profiles.docx | 20KB | plants |
| Electromagnetic and Crystallographic Properties...docx | 27KB | ratna |
| Graha Friendship_Enmity and Material Interactions...docx | 27KB | ratna/jyotish |
| Project Documentation Help (3 versions).docx | 21-28KB | meta/docs |
| Vastu permaculture research (3 versions).docx | 22-27KB | vastu/permaculture |

## New scaffolds needed

Based on this audit, these domains have research + dataset but no compendium scaffold:

| Proposed volume | Research source | Dataset domain |
|----------------|----------------|---------------|
| field_dives/carnatic_tala.typ | research_carnatic_tala_complete.md | carnatic/ |
| field_dives/astrobotany.typ | research_astrobotanical_classes.md + research_astrobotany_lunar.md | astrobotany/ |
| field_dives/yoga_and_pranayama.typ | research_pranayama_asana.md | yoga/ |
| field_dives/svarodaya.typ | research_svara_shastra.md | svarodaya/ |

## Recommendations (priority order)

1. **Convert the 3 identical draft/v1 pairs**: delete the `-draft.md` copies (they're byte-identical to the `-v1.md` versions). This eliminates 3 confusing duplicates.

2. **Author research docs for morphogenesis + tantra**: these DATASET_ONLY domains make strong claims (doctrine of signatures, chakra-nakshatra correspondence) with zero prose attestation. The data is live in engines. The attestation gap is a risk.

3. **Convert the 4 pending research papers to Typst**: two-source-interference, planetary-primes, vertebral-primes, sri_yantra_chladni. The Lo Shu conversion (done) is the template.

4. **Create the 4 new field dive scaffolds** (carnatic_tala, astrobotany, yoga_and_pranayama, svarodaya) and register them in MANIFEST.yaml.

5. **Convert 8 docx files to markdown**: these are research artifacts trapped in binary format. Priority: the Bhasma/Rasasastra and Vastu permaculture docs, which cover domains with live datasets.
