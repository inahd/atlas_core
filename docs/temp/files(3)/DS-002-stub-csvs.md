# DS-002: Create 5 missing stub CSVs

**Phase**: 1 — Stop the bleeding  
**Priority**: HIGH  
**Estimated time**: 30 min  
**Blocks**: library_kernel.py startup errors

## Context

`npu_engine/library_kernel.py` references 5 files that do not exist. Their absence
causes errors when the library inventory routes are called. We need stub CSVs with
correct headers — content can be populated later.

## Instructions

For each file below:
1. Read `npu_engine/library_kernel.py` — find the exact path reference and any
   column names it reads from that file
2. Read any sibling files in the same dataset subdirectory for column naming convention
3. Create the file with correct headers and zero data rows
4. Create the subdirectory if it doesn't exist

## Files to create

### 1. `datasets/marma/marma_coordinates.csv`
Check `library_kernel.py` and `npu_engine/engines/body_engine.py` for expected columns.
Likely columns: `marma_id, name_iast, x_ratio, y_ratio, body_view, region, notes`

### 2. `datasets/sanskrit/matrika_50.csv`
Create `datasets/sanskrit/` directory if needed.
50 Sanskrit matrika letters. Likely columns: `letter_id, devanagari, iast, element, guna, bija, deity, notes`

### 3. `datasets/geography/sacred_sites_india.csv`
Sibling: `datasets/geography/sacred_sites_global.csv` — match its columns exactly.
Read that file's header row first.

### 4. `datasets/geography/vraja_parikrama.csv`
Vraja pilgrimage circuit sites. Likely columns: `site_id, name, name_iast, lat, lon,
deity, forest, ashtakala_period, parikrama_order, notes`

### 5. `datasets/karma/dasha_meanings.csv`
Create `datasets/karma/` directory if needed.
Dasha period meanings. Likely columns: `dasha_lord, sub_lord, quality, themes,
recommended_practice, duration_years, notes`

## Success check

```bash
for f in datasets/marma/marma_coordinates.csv \
          datasets/sanskrit/matrika_50.csv \
          datasets/geography/sacred_sites_india.csv \
          datasets/geography/vraja_parikrama.csv \
          datasets/karma/dasha_meanings.csv; do
  echo "$f: $(head -1 ~/atlas_core/$f)"
done
```

All 5 files should print their header row (not an error).

```bash
curl -s localhost:5000/library | python3 -c "import sys,json; d=json.load(sys.stdin); print('OK')"
```

Should return OK or a meaningful response, not 500.

## Output

- Create 5 CSV files with headers, zero data rows
- Create 2 new subdirectories (`datasets/sanskrit/`, `datasets/karma/`)
- No other files modified
