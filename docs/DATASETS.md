# Datasets

110 CSV files across 33 knowledge domains in `datasets/`.

## Directory Structure

| Directory | Files | Content |
|-----------|-------|---------|
| `astro/` | 6 | Nakshatra full, tithi, vara, graha, muhurta |
| `astrobotany/` | 4 | Biodynamic mapping, lunar plant biology |
| `ayurveda/` | 3 | Dosha, dhatu, rasa |
| `canonical/` | 2 | Field contracts, canon registry |
| `carnatic/` | 3 | Tala, melakarta, swara |
| `chandas/` | 1 | Vedic meters |
| `cosmology/` | 8 | Graha master, element geometry, nakshatra master |
| `gandharva/` | 2 | Graha-raga chords, raga time |
| `jyotish/` | 3 | Dasha, yoga, karana |
| `mappings/` | 4 | Cross-domain mappings |
| `marma/` | 2 | Marma points, marma field |
| `ontology/` | 2 | Bhava relations, category schema |
| `overlays/` | 1 | Layered relations |
| `plants/` | 4 | Nakshatra plants, agriculture, PFAF SQLite (8504 plants) |
| `ratna/` | 1 | Gemstones |
| `relations/` | 1 | Curated nakshatra-deity relations (207 rows) |
| `ritual/` | 2 | Plant ritual, ritual calendar |
| `semantics/` | 2 | Attestation rules, confidence schema |
| `silpa/` | 1 | Sacred geometry |
| `svara/` | 2 | Shruti ratios, swara-rasa |
| `vastu/` | 2 | Vastu pada, directions |
| `yoga/` | 5 | Asana, bandha, pranayama, nakshatra body map |

## Key Files

- `astro/nakshatra_full.csv` — 27 nakshatras (name, graha, deity, element, guna, shakti)
- `cosmology/graha_master.csv` — 9 grahas (element, guna, dosha, domain)
- `plants/nakshatra_plants.csv` — 27 sacred plants (ayurvedic use, mantra, ritual)
- `plants/pfaf.sqlite` — 8504 plants from PFAF database
- `relations/nakshatra_associated_deity.csv` — 207 curated deity relations

## Archived

- `_archive/seed/` — Empty TODO scaffolding
- `_archive/relations_auto/` — Auto-generated (unreliable)
- `_archive/relations_strict/` — Subset of curated relations
- `_inbox/relations_inbox.csv` — Awaiting review

## How Data Loads

`npu_engine/datasets.py` uses `rglob("*.csv")` to find all CSVs recursively.
Files in `_archive/` and `_inbox/` are excluded.
Result: 2314 entity nodes, 2092 relation edges.
