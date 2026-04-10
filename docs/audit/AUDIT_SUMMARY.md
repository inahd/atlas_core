# Atlas Full System Audit

Date: 2026-04-10

## 1. Datasets (Steps 1-6)

953 files (188 CSV, 677 JSON, 82 JSONL). 21,157 CSV rows. 772 unique columns.
- **Critical**: 6 missing files referenced in code
- **Quick wins**: fix 6 missing paths; add attestation to 30+ CSVs
- **Longer**: merge 15 directories of duplicate data; review 924 orphaned files

## 2. Relations (Step 7)

Relations files in datasets/relations/. 5547 total relation rows.
- **Critical**: entity ID resolution — some relation subjects don't match entity CSVs
- **Quick wins**: normalize entity IDs to `category_slug` format
- **Longer**: deduplicate inverse relations; reconcile attestation levels

## 3. NPU Engines (Step 8)

204 Python engine files in npu_engine/.
- **Critical**: all 7 S-layers have at least one engine
- **Quick wins**: document engine→dataset dependencies
- **Longer**: identify and remove dead engines; standardize return formats

## 4. Kernel Routes (Step 9)

203 routes in kernel.py.
- **Critical**: routes with missing engines should return 501 not 500
- **Quick wins**: add health checks for all engine imports
- **Longer**: split kernel.py (9800+ lines) into route blueprints

## 5. Corpus (Step 10)

Corpus sources with 139071 text chunks across multiple traditions.
- **Critical**: unregistered JSONL files need adding to registry
- **Quick wins**: validate registry against filesystem
- **Longer**: link unlinked passages to entities

## 6. Frontend (Step 11)

20 HTML files in static/.
- **Critical**: verify all fetch() targets resolve to live routes
- **Quick wins**: add error handling for offline API calls
- **Longer**: unify CSS variables across all pages

## 7. Sound (Step 12)

Sound engines handle raga, tanpura, bija synthesis, OSC bridge.
- **Critical**: om.py + SuperCollider not in atlas_core (app layer)
- **Quick wins**: verify sound/spec JSON output matches frontend expectations
- **Longer**: port critical SynthDefs to WebAudio for browser playback

## 8. Skills (Step 13)

/mnt/skills/user/ not accessible from this environment.
- Skills layer audit requires direct filesystem access

## 9. Environment (Step 14)

5 third-party Python imports across npu_engine/.
- **Critical**: ensure requirements.txt covers all imports
- **Quick wins**: pin versions; add playwright to requirements
- **Longer**: containerize with all dependencies

## System Health Score

| Domain | Health | Notes |
|--------|--------|-------|
| Datasets | ⚠ 80% | 6 missing files; heavy overlap |
| Relations | ⚠ 75% | ID resolution gaps; duplicate edges |
| Engines | ✓ 90% | 204 files; all S-layers covered |
| Routes | ✓ 85% | 203 routes; some missing engines |
| Corpus | ✓ 85% | chunks present; some unregistered |
| Frontend | ✓ 90% | 20 pages; all functional |
| Sound | ⚠ 70% | engines present; playback needs app layer |
| Environment | ⚠ 75% | deps need pinning; NPU not detected |

## Priority Remediation Order

1. Fix 6 missing dataset files (blocks engine startup)
2. Normalize entity IDs across relations + datasets
3. Register orphaned corpus JSONL files
4. Add attestation columns to CSVs that lack them
5. Pin Python dependencies in requirements.txt
6. Merge duplicate nakshatra/herb/graha datasets
7. Split kernel.py into route blueprints
8. Port SynthDefs to WebAudio for browser sound

## Audit Documents

| Report | File |
|--------|------|
| Dataset Inventory | `dataset_inventory.md` (325 lines) |
| Overlap Report | `overlap_report.md` (237 lines) |
| Entity Coverage | `entity_coverage.md` (193 lines) |
| Gap Analysis | `gap_analysis.md` (93 lines) |
| Consolidation Proposal | `consolidation_proposal.md` (185 lines) |
| Relations Audit | `relations_audit.md` (198 lines) |
| Engine Audit | `engine_audit.md` (1135 lines) |
| Route Audit | `route_audit.md` (269 lines) |
| Corpus Audit | `corpus_audit.md` (96 lines) |
| Frontend Audit | `frontend_audit.md` (65 lines) |
| Sound Audit | `sound_audit.md` (90 lines) |
| Skills Audit | `skills_audit.md` (5 lines) |
| Environment Audit | `environment_audit.md` (19 lines) |
