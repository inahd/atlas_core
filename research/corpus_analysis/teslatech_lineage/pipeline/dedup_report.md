# Dedup report — teslatech_lineage corpus (FIXED)

_Scan: 2026-05-08T22:21:11Z_  ·  pymupdf 1.27.2.3

Note on the fix: a previous version of this script grouped scan-only PDFs (image-only, no extractable text) into one giant false-duplicate group via their identical empty text fingerprints. This version flags PDFs with <1000 non-whitespace chars of extracted text as `low_text` and withholds them from text-content hashing. They are still deduplicated via file-bytes SHA256, which catches truly byte-identical scan duplicates.

## Summary

- Scanned: **239** PDFs
- Extraction failures: **0**
- PDFs flagged as low_text (scan-only, < 1000 chars text): **76**
- Unique canonical texts after dedup: **217**
- Duplicates moved to `_duplicates/<tier>/`: **22**
- Duplicate groups (size > 1): **15**

## Per-tier counts

| Tier | Before | After | Removed | Low-text after |
|---|---:|---:|---:|---:|
| 01_steinmetz | 51 | 49 | 2 | 16 |
| 02_dollard | 55 | 42 | 13 | 26 |
| 03_heaviside | 7 | 7 | 0 | 3 |
| 04_maxwell_faraday | 5 | 5 | 0 | 1 |
| 05_thomson_jj | 5 | 5 | 0 | 0 |
| 06_kennelly | 7 | 7 | 0 | 2 |
| 07_macfarlane | 6 | 6 | 0 | 1 |
| 08_whittaker | 9 | 7 | 2 | 4 |
| 09_tesla_primary | 18 | 15 | 3 | 4 |
| 10_jenny_cymatics | 1 | 1 | 0 | 0 |
| 11_wachsmuth_steiner_marti | 7 | 7 | 0 | 0 |
| 12_russell | 20 | 18 | 2 | 2 |
| 14_lawlor_sacred_geom | 1 | 1 | 0 | 0 |
| 15_bortoft_goethe | 2 | 2 | 0 | 1 |
| 16_steinmetz_lineage_supports | 10 | 10 | 0 | 3 |
| 17_borderland_journal | 30 | 30 | 0 | 0 |
| 18_lebon_lodge_crookes | 5 | 5 | 0 | 4 |

## Duplicate groups (size > 1)

### 02_dollard — group of 4 (30 pp)

**Canonical:** `02_dollard/System for reception and Transmission of Telluric Waves by Eric Dollard (older version).pdf`

**Duplicates moved:**
- `02_dollard/System for reception and Transmission of Telluic Waves by Eric Dollard.pdf`
- `02_dollard/Eric Dollard EPD Teluric Currents Paper.pdf`
- `02_dollard/Eric-Dollard--Telluric-Currents-Paper.pdf`

### 02_dollard — group of 4 (43 pp)  [LOW-TEXT — bytes-hash dedup only]

**Canonical:** `02_dollard/Eric Dollard Introduction to Dielectric and Magnetic Discharges in Electrical Windings (older version).pdf`

**Duplicates moved:**
- `02_dollard/Eric Dollard Introduction to Dielectric Magnetic Discharges in Electrical Windings Electrical Oscillation.pdf`
- `02_dollard/Eric Dollard Introduction to Dielectric and Magnetic Discharges in Electrical Windings.pdf`
- `02_dollard/Introduction to Dielectric Magnetic Discharges in Electrical Windings.pdf`

### 02_dollard — group of 3 (93 pp)  [LOW-TEXT — bytes-hash dedup only]

**Canonical:** `02_dollard/Symbolic Representation of the Generalized Electric Wave by Eric Dollard (older version).pdf`

**Duplicates moved:**
- `02_dollard/Symbolic Representation of the Generalized Electric Wave by Eric Dollard.pdf`
- `02_dollard/Symbolic Representation of the Generalized Electric Wave.pdf`

### 08_whittaker — group of 3 (502 pp)

**Canonical:** `08_whittaker/Whittaker History of Theories of Aether and Electricity 502p.pdf`

**Duplicates moved:**
- `08_whittaker/Whittaker History of Theories of Aether and Electricity.pdf`
- `08_whittaker/ET-Whittaker--A-History-of-the-Theories-of-Aether-and-Electricity.pdf`

### 09_tesla_primary — group of 3 (22 pp)

**Canonical:** `09_tesla_primary/Nikola Tesla - Modern Physics for Engineers.pdf`

**Duplicates moved:**
- `09_tesla_primary/Nikola-Tesla--Modern-Physics-For-Engineers-1.pdf`
- `09_tesla_primary/Nikola-Tesla--Modern-Physics-for-Engineers-2.pdf`

### 01_steinmetz — group of 2 (186 pp)  [LOW-TEXT — bytes-hash dedup only]

**Canonical:** `01_steinmetz/Charles Steinmetz Electrical Discharges Waves and Impulses 2nd Ed.pdf`

**Duplicates moved:**
- `01_steinmetz/Charles Steinmetz - Electrical Discharges Waves and Impulses 2ndEd.pdf`

### 01_steinmetz — group of 2 (717 pp)

**Canonical:** `01_steinmetz/Steinmetz-CPTheory-and-Calculation-of-Transient-Electric-Phenomena-and-Oscillations.pdf`

**Duplicates moved:**
- `01_steinmetz/CharlesSteinmetzTheory-and-Calculation-of-Transient-Electric-Phenomena-and-Oscillations.pdf`

### 02_dollard — group of 2 (30 pp)

**Canonical:** `02_dollard/Eric Dollard - Teluric Currents Paper.pdf`

**Duplicates moved:**
- `02_dollard/Eric Dollard.pdf`

### 02_dollard — group of 2 (29 pp)  [LOW-TEXT — bytes-hash dedup only]

**Canonical:** `02_dollard/Eric Dollard Notes 1986 to 1991.pdf`

**Duplicates moved:**
- `02_dollard/Eric Dollard Notes.pdf`

### 02_dollard — group of 2 (50 pp)  [LOW-TEXT — bytes-hash dedup only]

**Canonical:** `02_dollard/Eric Dollard SFTS Powerpoint 01.pdf`

**Duplicates moved:**
- `02_dollard/Eric Dollard SFTS Powerpoint.pdf`

### 02_dollard — group of 2 (9 pp)  [LOW-TEXT — bytes-hash dedup only]

**Canonical:** `02_dollard/The Oscillating Current Transformer - Eric Dollard.pdf`

**Duplicates moved:**
- `02_dollard/Eric Dollard The Oscillating Current Transformer.pdf`

### 02_dollard — group of 2 (6 pp)

**Canonical:** `02_dollard/Understanding the Rotating Magnetic Field by Eric P. Dollard.pdf`

**Duplicates moved:**
- `02_dollard/Rotating Magnetic Field.pdf`

### 09_tesla_primary — group of 2 (262 pp)

**Canonical:** `09_tesla_primary/NIKOLA-TESLA-On-His-Work-With-Alternating-Currents-and-Their-Application-to-Wireless-Telgraphy-Telephony-and-Transmission-of-Power-Leland-I-Anders.pdf`

**Duplicates moved:**
- `09_tesla_primary/Nikola-Tesla--On-His-Work-With-Alternating-Currents-and-Their-Application-to-Wireless-Telgraphy-Telephony-and-Transmission-of-Power-Leland-I-Ande.pdf`

### 12_russell — group of 2 (163 pp)

**Canonical:** `12_russell/WalterRussellTheSecretofLight.pdf`

**Duplicates moved:**
- `12_russell/33365473TheSecretofLightbyWalterRussell.pdf`

### 12_russell — group of 2 (98 pp)

**Canonical:** `12_russell/ANewConceptoftheUniversebyWalterRussell.pdf`

**Duplicates moved:**
- `12_russell/Walter-RussellA-New-Concept-Of-The-Universe.pdf`
