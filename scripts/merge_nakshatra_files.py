#!/usr/bin/env python3
"""Merge all nakshatra CSV files into a single canonical dataset.

Priority order: master > full > extended > core > deities
Output: datasets/astro/nakshatra_canonical.csv
"""
import csv
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

files_in_priority = [
    'datasets/astro/nakshatra_master.csv',
    'datasets/astro/nakshatra_full.csv',
    'datasets/astro/nakshatra_extended.csv',
    'datasets/astro/nakshatra_core.csv',
    'datasets/astro/nakshatra_deities.csv',
]

# Column renames to normalize across files
COLUMN_RENAMES = {
    'ruling_graha': 'graha',  # extended uses ruling_graha, others use graha
}

merged = {}  # nakshatra_name -> merged row

# Load lower-priority first so higher-priority overwrites
for filepath in reversed(files_in_priority):
    fullpath = os.path.join(ROOT, filepath)
    try:
        for row in csv.DictReader(open(fullpath)):
            # Normalize column names
            row = {COLUMN_RENAMES.get(k, k): v for k, v in row.items()}
            raw_key = row.get('nakshatra', '').strip()
            if not raw_key:
                continue
            # Normalize: underscores → spaces for consistent keying
            key = raw_key.replace('_', ' ')
            # Use the space-delimited form as canonical name
            row['nakshatra'] = key
            if key not in merged:
                merged[key] = {}
            # Only overwrite with non-empty values
            merged[key].update({k: v for k, v in row.items() if v and v.strip()})
    except FileNotFoundError:
        print(f"WARNING: {filepath} not found, skipping")

# Define canonical column order
canonical_order = [
    'nakshatra', 'graha', 'deity', 'element', 'guna', 'gana', 'dosha',
    'yoni_animal', 'yoni_gender', 'symbol', 'shakti', 'themes',
    'tree', 'plant', 'gemstone', 'direction', 'varna', 'nadi',
    'path', 'color_hex', 'glyph', 'emoji', 'attestation_status',
]

# Collect any extra columns not in canonical_order
all_cols_seen = set()
for row in merged.values():
    all_cols_seen.update(row.keys())

extra = [c for c in sorted(all_cols_seen) if c not in canonical_order]
all_cols = canonical_order + extra

# Canonical nakshatra order (1-27)
NAKSHATRA_ORDER = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira',
    'Ardra', 'Punarvasu', 'Pushya', 'Ashlesha', 'Magha',
    'Purva Phalguni', 'Uttara Phalguni', 'Hasta', 'Chitra', 'Swati',
    'Vishakha', 'Anuradha', 'Jyeshtha', 'Mula', 'Purva Ashadha',
    'Uttara Ashadha', 'Shravana', 'Dhanishta', 'Shatabhisha',
    'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati',
]

def sort_key(row):
    name = row.get('nakshatra', '')
    try:
        return NAKSHATRA_ORDER.index(name)
    except ValueError:
        return 999

outpath = os.path.join(ROOT, 'datasets', 'astro', 'nakshatra_canonical.csv')
with open(outpath, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=all_cols, extrasaction='ignore')
    writer.writeheader()
    for row in sorted(merged.values(), key=sort_key):
        writer.writerow(row)

print(f'Written: {len(merged)} nakshatras, {len(all_cols)} columns')
print(f'Columns: {all_cols}')
print(f'Output: {outpath}')
