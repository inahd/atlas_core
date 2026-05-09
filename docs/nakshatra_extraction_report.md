# Nakshatra Dataset — Extraction Report (v3)

**Date**: 2026-04-23

## Deck dataset (production)

**Output files**: `data/nakshatra_deck.csv`, `data/nakshatra_deck.json`
**Rows**: 27 — **Columns**: 20 — **Fill rate**: 100%
**Build script**: `scripts/build_nakshatra_deck.py`
**Status**: 27 ready / 0 partial / 0 blocked

All 18 yoni conflicts from v2 resolved via `datasets/relations/species_relations.csv`
(BPHS-attributed `nakshatra_yoni` relations, lines 90-116).

### Yoni resolution summary

| Conflict type | Count | Source used | Resolution |
|--------------|-------|------------|------------|
| Gender swap (canonical vs species) | 15 | species_relations.csv (BPHS) | Gender overridden to BPHS values |
| Anuradha/Jyeshtha animal (deer vs hare) | 2 | species_relations.csv (BPHS) | Hare (shasha) — standard BPHS yoni #11; "deer" not in the 14-yoni system |
| Uttara Ashadha animal (monkey vs mongoose) | 1 | species_relations.csv (BPHS) | Mongoose (nakula) — the only unpaired yoni; "monkey" would break 14-yoni structure |

### Synthesis fields in deck

| Field | Status | Note |
|-------|--------|------|
| gift_expression | atlas_synthesis | Positive reading of canonical.csv `themes` |
| shadow_expression | atlas_synthesis | Negative reading of canonical.csv `themes` |
| panel_layout | atlas_synthesis | Designed per-nakshatra from symbol + element |
| visual_palette_logic | extracted+computed | `color_hex` + element label from canonical.csv |

All other fields are direct extraction from on-disk sources.

## Extended dataset (research/reference)

**Output files**: `data/nakshatra_master_table.csv`, `data/nakshatra_master_table.json`
**Rows**: 27 — **Columns**: 41
**Build script**: `scripts/build_nakshatra_master.py`
**Status**: 9 ready / 18 partial / 0 blocked (pre-resolution; superseded by deck dataset for production use)

---

## Source files used

| File | Fields extracted | Coverage |
|------|-----------------|----------|
| `datasets/astro/nakshatra_canonical.csv` | deity, planetary_lord, element, guna, gana, dosha, yoni_animal, yoni_gender, symbol, shakti, themes, tree, plant, gemstone, direction, varna, nadi, color_hex | 27/27 |
| `datasets/plants/nakshatra_plants.csv` | primary_plant, sacred_tree, tree_latin, body_part, metal, mantra, ritual_use, ayurvedic_use | 27/27 |
| `datasets/species/nakshatra_species.csv` | species_correspondence, relationship_type | 27/27 |
| `datasets/ayurveda/dosha_nakshatra_matrix.csv` | primary_dosha, secondary_dosha, dosha_modification, practice, dietary, herb | 27/27 |
| `datasets/yoga/nakshatra_body_map.csv` | body_region (Brihat Samhita Ch. 105) | 27/27 |
| `datasets/plants/nakshatra_agriculture.csv` | biodynamic quality, activity, avoid, crops | 27/27 |
| `datasets/astrobotany/biodynamic_vedic_mapping.csv` | biodynamic_category via rashi-element-Steiner mapping | 27/27 |
| `npu_engine/sound/sound_engine.py` (line 387, `_NAK_RAGA`) | raga_link | 27/27 |
| `research/two-source-interference-v3.md` (Finding 11) | gandanta_polarity, tithi_group_preference, boundary_harmonic_mode | 6/27 |
| `research/planetary-primes-v1.md` | Referenced for context only — no per-nakshatra data | 0/27 |

---

## Status logic (v2)

### Core fields (determine ready/partial/blocked)

A row is **ready** only if all 15 core fields are populated AND the row has no unresolved data conflicts:

`deck_id`, `nakshatra_number`, `nakshatra_name`, `zodiac_span`, `deity`, `planetary_lord`, `sacred_symbol`, `shakti_statement`, `yoni_animal`, `primary_plant`, `gana`, `nadi`, `attestation_level`, `source_file`, `citation_status`

### Status assignments

- **ready** (9 rows): All core fields present. No yoni conflicts between source files.
- **partial** (18 rows): All core fields present (`core_completeness_score=100`), but yoni gender and/or animal type conflicts exist between `nakshatra_canonical.csv` and `nakshatra_species.csv`. These are usable for card generation but have unresolved provenance issues.
- **blocked** (0 rows): No rows are missing core fields.

### Citation status per row

- `extracted`: Row's core fields come directly from on-disk CSV sources with no rewriting. 9 rows.
- `unresolved`: Row has an animal-type conflict (deer vs rabbit, or monkey vs mongoose) where the correct value cannot be determined from on-disk sources alone. 3 rows (Anuradha, Jyeshtha, Uttara Ashadha).
- `extracted` with `conflict_flag=yes`: Row has a yoni gender swap between sources but the animal type agrees. 15 rows. The gender conflict does not block extraction but needs BPHS reconciliation.

---

## Row-by-row status rationale for non-ready rows

| # | Nakshatra | Status | Reason | Conflict type |
|---|-----------|--------|--------|---------------|
| 2 | Bharani | partial | yoni gender swap (canonical: female, species: male) | gender |
| 3 | Krittika | partial | yoni gender swap | gender |
| 4 | Rohini | partial | yoni gender swap | gender |
| 5 | Mrigashira | partial | yoni gender swap | gender |
| 6 | Ardra | partial | yoni gender swap | gender |
| 7 | Punarvasu | partial | yoni gender swap | gender |
| 8 | Pushya | partial | yoni gender swap | gender |
| 9 | Ashlesha | partial | yoni gender swap | gender |
| 13 | Hasta | partial | yoni gender swap | gender |
| 14 | Chitra | partial | yoni gender swap | gender |
| 15 | Swati | partial | yoni gender swap | gender |
| 16 | Vishakha | partial | yoni gender swap | gender |
| 17 | Anuradha | partial | **animal type conflict**: deer (canonical) vs rabbit (species) | animal + gender |
| 18 | Jyeshtha | partial | **animal type conflict**: deer (canonical) vs rabbit (species) | animal + gender |
| 19 | Mula | partial | yoni gender swap | gender |
| 20 | Purva Ashadha | partial | yoni gender swap | gender |
| 21 | Uttara Ashadha | partial | **animal type conflict**: monkey (canonical) vs mongoose (species) | animal + gender |
| 27 | Revati | partial | yoni gender swap | gender |

---

## Conflict table

### Animal type conflicts (3 rows, citation_status=unresolved)

| Nakshatra | canonical.csv | species.csv | Likely BPHS value | Master table value | Resolution needed |
|-----------|--------------|-------------|-------------------|--------------------|-------------------|
| Anuradha | deer (female) | Rabbit (male) | deer (mriga) | deer (female) [CONFLICT annotated] | Verify BPHS Ch. 83 |
| Jyeshtha | deer (male) | Rabbit (female) | deer (mriga) | deer (male) [CONFLICT annotated] | Verify BPHS Ch. 83 |
| Uttara Ashadha | monkey (male) | Mongoose (female) | mongoose (nakula) | monkey (male) [CONFLICT annotated] | Fix canonical.csv to mongoose |

### Gender swap conflicts (15 rows, citation_status=extracted, conflict_flag=yes)

Both source files cite BPHS but assign opposite genders. This is a systematic error in one file — likely all 14 yoni pairs have their male/female assignments swapped in one of the two CSVs. Master table uses `nakshatra_canonical.csv` as primary.

Affected: Bharani, Krittika, Rohini, Mrigashira, Ardra, Punarvasu, Pushya, Ashlesha, Hasta, Chitra, Swati, Vishakha, Mula, Purva Ashadha, Revati.

### Spelling variant

"Dhanishta" vs "Dhanishtha" — normalized to "Dhanishta" in build script. Both are valid romanizations.

---

## Fields with strong coverage (27/27)

All core jyotish fields plus plant, dosha, body, agriculture, and raga:

- Identity: `nakshatra_name`, `nakshatra_number`, `deck_id`, `zodiac_span`, `padas`, `rashi_overlap`
- Canonical: `deity`, `planetary_lord`, `sacred_symbol`, `shakti_statement`, `yoni_animal`, `gana`, `varna`, `nadi`
- Ecology: `primary_plant`, `secondary_plants`, `biodynamic_category`, `astrobotanical_timing`
- Body: `dosha_profile`, `body_region`
- Divination: `species_correspondence`, `gandanta_flag`
- Sound: `raga_link`
- Visual: `visual_palette_logic`, `panel_layout`
- Meta: `attestation_level`, `source_file`, `citation_status`, `operational_status`, `core_completeness_score`, `conflict_flag`

## Fields correctly partial (6/27 — gandanta only)

- `gandanta_polarity`: only meaningful for the 6 gandanta nakshatras
- `tithi_group_preference`: wave research Finding 11 applies only to gandanta
- `boundary_harmonic_mode`: same

## Fields entirely empty (0/27 — no per-nakshatra source on disk)

| Field | Why empty | What would fill it |
|-------|-----------|-------------------|
| `nodal_interior_pattern` | Wave research is system-level, not per-nakshatra | Run `cut_and_project.py` per lord's N-fold |
| `prime_signature` | Planetary primes are per-graha, not per-nakshatra | Compute lord → retrograde prime mapping |
| `morphology_correlates` | Vertebral data is per-species | Map yoni animal → vertebral formula |
| `svara_link` | No svara-nakshatra mapping on disk | Source from Gandharva Veda / Narada Shiksha |

---

## Extracted vs Atlas synthesis

### Directly extracted (values copied from source CSV rows)

`deity`, `planetary_lord`, `sacred_symbol`, `shakti_statement`, `yoni_animal`, `species_correspondence`, `primary_plant`, `secondary_plants`, `gana`, `varna`, `nadi`, `dosha_profile`, `body_region`, `astrobotanical_timing`, `raga_link`, `gandanta_flag`

### Computed from extracted data (deterministic derivation)

`deck_id`, `nakshatra_number`, `zodiac_span`, `padas`, `rashi_overlap`, `biodynamic_category`, `gandanta_polarity`, `core_completeness_score`, `conflict_flag`, `operational_status`, `citation_status`

### Atlas synthesis (composed for this dataset — no source text)

| Field | Nature | Risk level |
|-------|--------|------------|
| `gift_expression` | Positive reading of extracted `themes` | Low — themes are on-disk; the split is editorial |
| `shadow_expression` | Negative reading of extracted `themes` | Low — same source, opposite polarity |
| `motto` | Aphoristic line composed from shakti + themes | Medium — entirely authored, no textual basis |
| `panel_layout` | Visual composition instruction | Medium — designed from symbol/element/color |
| `visual_palette_logic` | color_hex + element label | Low — mechanical concatenation |
| `tithi_group_preference` | From wave research Finding 11 | Low — directly supported by research paper |
| `boundary_harmonic_mode` | From wave research Finding 11 | Low — directly supported by research paper |

---

## Safe for card rendering now (9 rows)

These rows have all core fields, no unresolved conflicts, and can be used for deck generation immediately:

1. Ashwini
2. Magha
3. Purva Phalguni
4. Uttara Phalguni
5. Shravana
6. Dhanishta
7. Shatabhisha
8. Purva Bhadrapada
9. Uttara Bhadrapada

## Needs second extraction pass (18 rows)

All 18 partial rows need BPHS yoni reconciliation before they can be marked `ready`. The data is usable for draft card rendering, but the yoni field carries a known conflict.

**Priority tiers for the second pass:**

1. **High** (3 rows — animal type conflict): Anuradha, Jyeshtha, Uttara Ashadha. These need BPHS Ch. 83 verification to resolve which animal is correct.
2. **Medium** (15 rows — gender swap only): All others with `conflict_flag=yes`. A single BPHS reading session would resolve all 15 simultaneously since the error is systematic.

---

## Audit table

| nakshatra_name | suspect_field | reason_flagged | action_taken |
|---------------|---------------|----------------|--------------|
| Anuradha | yoni_animal | canonical=deer, species=rabbit; animal mismatch | kept canonical; annotated CONFLICT inline; citation=unresolved |
| Jyeshtha | yoni_animal | canonical=deer, species=rabbit; animal mismatch | kept canonical; annotated CONFLICT inline; citation=unresolved |
| Uttara Ashadha | yoni_animal | canonical=monkey, species=mongoose; BPHS=mongoose | kept canonical; annotated CONFLICT inline; citation=unresolved |
| 15 nakshatras | yoni gender | canonical and species disagree on male/female | both preserved in separate columns; conflict_flag=yes |
| All 27 | gift_expression | atlas_synthesis, not extraction | documented in synthesis table |
| All 27 | shadow_expression | atlas_synthesis, not extraction | documented in synthesis table |
| All 27 | motto | atlas_synthesis, no textual source | documented in synthesis table |
| All 27 | panel_layout | atlas_synthesis, designed not extracted | individualized (27 unique); documented |
| All 27 | raga_link | source is Atlas sound_engine.py, not traditional text | attestation noted as atlas_synthesis in code comments |
| Mula | element discrepancy | canonical=air; agriculture=fire; traditional=fire | canonical value used; noted |
| Dhanishta | element discrepancy | canonical=fire; agriculture=air | canonical value used; noted |
| All 27 | shakti_statement | single-word form (e.g., "Healing") | usable but terse; expansion recommended |

---

## Next pass recommended

1. **BPHS yoni reconciliation** — Read Ch. 83 directly. Fixes 18 partial rows in one pass. Resolves all gender swaps and the 3 animal-type conflicts. This is the single highest-leverage action.

2. **Svara mapping** — Source from Gandharva Veda or Narada Shiksha. Fills 27 blank cells.

3. **Prime signature per nakshatra lord** — Compute: Ketu→none, Venus→5, Sun→3(?), Moon→none, Mars→7, Rahu→none, Jupiter→11, Saturn→29, Mercury→3. This is atlas_synthesis but grounded in retrograde symmetry data.

4. **Nodal interior patterns** — Run `cut_and_project.py` per lord's N-fold and store density metrics.

5. **Shakti expansion** — Current values are single words. Expand to full sentences following tithi card pattern.

6. **Motto quality pass** — Current mottos are first-draft. Literary editing recommended.

7. **Cross-reference with tithi card** — Align column naming with `cards/tithi_07_sivaduti.md`.
