# Atlas Dataset Audit Summary

Date: 2026-04-10

## Scale

| Metric | Count |
|--------|-------|
| Total files | 953 |
| CSV files | 188 |
| JSON files | 677 |
| JSONL files | 82 |
| Total CSV rows | 21157 |
| Unique columns | 772 |
| Code references | 35 |
| **Missing** | **6** |
| Orphaned | 924 |

## Top 10 Column Overlaps

| Column | Files | Status |
|--------|-------|--------|
| `notes` | 71 | CONFLICT |
| `element` | 43 | CONFLICT |
| `name` | 33 | CONFLICT |
| `source` | 32 | CONFLICT |
| `attestation_status` | 31 | CONFLICT |
| `confidence` | 30 | CONFLICT |
| `relation` | 28 | CONFLICT |
| `deity` | 27 | CONFLICT |
| `id` | 26 | CONFLICT |
| `tradition` | 26 | CONFLICT |

## Top Gaps (Missing Files)

- `datasets/geography/sacred_sites_india.csv`
- `datasets/geography/vraja_parikrama.csv`
- `datasets/karma/dasha_meanings.csv`
- `datasets/layer_mapping.csv`
- `datasets/marma/marma_coordinates.csv`
- `datasets/sanskrit/matrika_50.csv`

## Entity Coverage Summary

- **nakshatra**: 40 files
- **graha**: 44 files
- **tithi**: 14 files
- **devi**: 8 files
- **raga**: 16 files
- **tala**: 7 files
- **plant**: 26 files
- **marma**: 7 files
- **vastu**: 27 files
- **dosha**: 29 files
- **element**: 64 files
- **body**: 25 files
- **deity**: 40 files

## Consolidation Priority

1. Fix 6 missing file references
2. Merge duplicate datasets (~15 directories)
3. Add attestation to CSVs that lack it
4. Unify entity ID format
5. Review 924 orphaned files

## Estimated Work

- Missing files: 6
- Merge candidates: 15 directories
- Orphaned review: 924 files
- Estimated: 3-5 focused sessions
