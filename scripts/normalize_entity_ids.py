#!/usr/bin/env python3
"""
REL-001: Normalize entity IDs in relation CSVs.

Canonical format: category:slug (lowercase, underscores in slug).
Loads authoritative entity data from multiple sources to build lookup tables,
then repairs from_id and to_id columns in relation CSVs.

Usage:
    python scripts/normalize_entity_ids.py                          # all files
    python scripts/normalize_entity_ids.py --file path/to/file.csv  # single file
    python scripts/normalize_entity_ids.py --file path/to/file.csv --dry-run
"""

import argparse
import csv
import glob
import os
import re
import sys
from collections import defaultdict

RELATIONS_DIR = "datasets/relations"
CANON_FILE = "relations_resolved_canon.csv"
AUDIT_LOG = "docs/audit/id_repair_log.csv"


def build_entity_registry():
    """Build {entity_id: name} from authoritative sources."""
    entities = {}

    # 1. Entity CSVs
    skip_names = {'nodes', 'edges', 'texts', 'concepts', 'schools',
                  'graha', 'nakshatra', 'rashi', 'vedanta_schools'}
    for f in sorted(glob.glob('datasets/entities/*.csv')):
        try:
            with open(f) as fh:
                for row in csv.DictReader(fh):
                    eid = row.get('id', '').strip()
                    name = row.get('name', '').strip()
                    if eid and name and name not in skip_names:
                        entities[eid] = name
        except Exception:
            pass

    # 2. Nakshatra number mapping
    try:
        with open('datasets/astro/nakshatra_num_to_name.csv') as f:
            for row in csv.DictReader(f):
                num = row.get('num', '').strip()
                name = row.get('name', '').strip()
                if num and name:
                    canonical = f'nakshatra:{name.lower()}'
                    if canonical not in entities:
                        entities[canonical] = name
    except Exception:
        pass

    # 3. Graha master
    try:
        with open('datasets/cosmology/graha_master.csv') as f:
            for row in csv.DictReader(f):
                name = row.get('graha', '').strip()
                if name:
                    eid = f'graha:{name.lower()}'
                    if eid not in entities:
                        entities[eid] = name
    except Exception:
        pass

    # 4. Deity master
    try:
        with open('datasets/cosmology/deity_master.csv') as f:
            for row in csv.DictReader(f):
                name = row.get('deity', '').strip()
                if name:
                    eid = f'deity:{name.lower()}'
                    if eid not in entities:
                        entities[eid] = name
    except Exception:
        pass

    # 5. Nitya devi master
    try:
        with open('datasets/cosmology/nitya_devi_master.csv') as f:
            for row in csv.DictReader(f):
                eid_raw = row.get('id', '').strip()
                name = row.get('name_iast', '').strip()
                if eid_raw and name:
                    if '_' in eid_raw:
                        parts = eid_raw.split('_', 1)
                        eid = f'{parts[0]}:{parts[1]}'
                    else:
                        eid = f'devi:{eid_raw}'
                    if eid not in entities:
                        entities[eid] = name
    except Exception:
        pass

    # 6. Dosha
    try:
        with open('datasets/ayurveda/dosha.csv') as f:
            for row in csv.DictReader(f):
                name = row.get('name', '').strip() or row.get('dosha', '').strip()
                if name:
                    eid = f'dosha:{name.lower()}'
                    if eid not in entities:
                        entities[eid] = name
    except Exception:
        pass

    # 7. Well-known fixed entities
    for elem in ['fire', 'water', 'earth', 'air', 'ether']:
        eid = f'element:{elem}'
        if eid not in entities:
            entities[eid] = elem.capitalize()

    # 8. Rasa
    try:
        with open('datasets/ayurveda/rasa.csv') as f:
            for row in csv.DictReader(f):
                name = row.get('name', '').strip()
                rid = row.get('id', '').strip()
                if rid:
                    eid = f'rasa:{rid}'
                    if eid not in entities:
                        entities[eid] = name or rid
    except Exception:
        pass

    # 9. Vara
    for vara in ['ravivara', 'somavara', 'mangalavara', 'budhavara',
                 'guruvara', 'shukravara', 'shanivara']:
        eid = f'vara:{vara}'
        if eid not in entities:
            entities[eid] = vara.capitalize()

    # 10. Ashtakala
    try:
        with open('datasets/cosmology/ashtakala.csv') as f:
            for row in csv.DictReader(f):
                name = row.get('id', '').strip() or row.get('name', '').strip()
                if name:
                    eid = f'ashtakala:{name.lower()}'
                    if eid not in entities:
                        entities[eid] = name
    except Exception:
        pass

    return entities


def build_nakshatra_num_map():
    """Build {num_str: name} for nakshatra numeric IDs."""
    num_map = {}
    try:
        with open('datasets/astro/nakshatra_num_to_name.csv') as f:
            for row in csv.DictReader(f):
                num = row.get('num', '').strip()
                name = row.get('name', '').strip()
                if num and name:
                    num_map[num] = name.lower()
    except Exception:
        pass
    return num_map


def build_lookup(entities, nakshatra_nums):
    """
    Build a multi-key lookup: {variant: canonical_id}.
    Handles: case variants, underscore-to-colon, numeric nakshatras, bare slugs.
    """
    lookup = {}
    canonical_set = set(entities.keys())

    for eid, name in entities.items():
        # The canonical ID itself
        lookup[eid] = eid

        # Capitalized variant: deity:Shiva -> deity:shiva
        if ':' in eid:
            cat, slug = eid.split(':', 1)
            cap_variant = f'{cat}:{name}'
            lookup[cap_variant] = eid
            lookup[cap_variant.lower()] = eid
            # Title case: deity:Agni
            lookup[f'{cat}:{slug.title()}'] = eid
            lookup[f'{cat}:{slug.capitalize()}'] = eid
            # Underscore variant: nakshatra_ashwini -> nakshatra:ashwini
            lookup[f'{cat}_{slug}'] = eid
            lookup[f'{cat}_{name}'] = eid
            lookup[f'{cat}_{name.lower()}'] = eid

    # Nakshatra numeric: nakshatra:1 -> nakshatra:ashwini
    for num, name in nakshatra_nums.items():
        canonical = f'nakshatra:{name}'
        if canonical in canonical_set:
            lookup[f'nakshatra:{num}'] = canonical

    # Ayurveda doshas with capitalization
    for dosha in ['vata', 'pitta', 'kapha']:
        canonical = f'dosha:{dosha}'
        lookup[f'ayurveda:{dosha.capitalize()}'] = canonical
        lookup[f'ayurveda:{dosha}'] = canonical

    return lookup


def normalize_id(raw_id, lookup, canonical_set):
    """
    Normalize a single ID. Returns (canonical_id, status).
    Status: 'already_canonical', 'repaired', 'format_fixed', 'unresolved'
    """
    raw_id = raw_id.strip()
    if not raw_id:
        return raw_id, 'empty'

    # Already canonical
    if raw_id in canonical_set:
        return raw_id, 'already_canonical'

    # Direct lookup hit
    if raw_id in lookup:
        return lookup[raw_id], 'repaired'

    # Try lowercase
    lower = raw_id.lower()
    if lower in lookup:
        return lookup[lower], 'repaired'

    # Underscore-to-colon conversion: category_slug -> category:slug
    if '_' in raw_id and ':' not in raw_id:
        # Try first underscore as separator
        parts = raw_id.split('_', 1)
        colon_form = f'{parts[0].lower()}:{parts[1].lower()}'
        if colon_form in lookup:
            return lookup[colon_form], 'repaired'
        if colon_form in canonical_set:
            return colon_form, 'repaired'
        # This is a valid category:slug format, just needs the colon
        # If the prefix is a known category, convert it
        colon_form_clean = re.sub(r'[^a-z0-9_:]', '_', colon_form)
        return colon_form_clean, 'format_fixed'

    # Already has colon — just lowercase it
    if ':' in raw_id:
        parts = raw_id.split(':', 1)
        lowered = f'{parts[0].lower()}:{parts[1].lower()}'
        # Replace spaces with underscores in slug
        lowered = re.sub(r'\s+', '_', lowered)
        # Remove non-canonical chars
        lowered = re.sub(r'[^a-z0-9_:]', '_', lowered)
        # Clean up double underscores
        lowered = re.sub(r'_+', '_', lowered).strip('_')
        cat, slug = lowered.split(':', 1)
        slug = slug.strip('_')
        result = f'{cat}:{slug}'
        if result in canonical_set:
            return result, 'repaired'
        if result in lookup:
            return lookup[result], 'repaired'
        # Even if not in registry, the format is now canonical
        return result, 'format_fixed'

    # Bare word with no prefix and no underscore — unresolved
    return raw_id, 'unresolved'


def process_file(filepath, lookup, canonical_set, dry_run=False):
    """Process a single relation CSV. Returns list of log entries."""
    log_entries = []
    basename = os.path.basename(filepath)

    try:
        with open(filepath, newline='') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            if not fieldnames:
                return log_entries
            rows = list(reader)
    except Exception as e:
        print(f"  ERROR reading {filepath}: {e}")
        return log_entries

    modified = False
    for row in rows:
        for col in ['from_id', 'to_id']:
            if col not in row:
                continue
            original = row[col].strip() if row[col] else ''
            if not original:
                continue

            canonical, status = normalize_id(original, lookup, canonical_set)

            if status in ('repaired', 'format_fixed') and canonical != original:
                modified = True
                if not dry_run:
                    row[col] = canonical
                log_entries.append({
                    'file': basename,
                    'column': col,
                    'original_id': original,
                    'status': 'repaired',
                    'canonical_id': canonical
                })
            elif status == 'unresolved':
                log_entries.append({
                    'file': basename,
                    'column': col,
                    'original_id': original,
                    'status': 'unresolved',
                    'canonical_id': ''
                })

    if modified and not dry_run:
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    return log_entries


def main():
    parser = argparse.ArgumentParser(description='Normalize entity IDs in relation CSVs')
    parser.add_argument('--file', help='Process a single file instead of all')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would change without writing')
    args = parser.parse_args()

    print("Building entity registry...")
    entities = build_entity_registry()
    print(f"  {len(entities)} entities from authoritative sources")

    nakshatra_nums = build_nakshatra_num_map()
    print(f"  {len(nakshatra_nums)} nakshatra number mappings")

    lookup = build_lookup(entities, nakshatra_nums)
    print(f"  {len(lookup)} lookup keys built")

    canonical_set = set(entities.keys())

    if args.file:
        files = [args.file]
    else:
        files = sorted(glob.glob(f'{RELATIONS_DIR}/*.csv'))

    all_log = []
    for filepath in files:
        basename = os.path.basename(filepath)
        if CANON_FILE in basename:
            print(f"  SKIP (canonical): {basename}")
            continue

        print(f"  Processing: {basename}")
        log = process_file(filepath, lookup, canonical_set, dry_run=args.dry_run)
        all_log.extend(log)

        repaired = sum(1 for e in log if e['status'] == 'repaired')
        unresolved = sum(1 for e in log if e['status'] == 'unresolved')
        if repaired or unresolved:
            print(f"    repaired={repaired}, unresolved={unresolved}")

    # Write audit log
    if all_log and not args.dry_run:
        os.makedirs(os.path.dirname(AUDIT_LOG), exist_ok=True)
        with open(AUDIT_LOG, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['file', 'column', 'original_id', 'status', 'canonical_id'])
            writer.writeheader()
            writer.writerows(all_log)
        print(f"\nAudit log written to {AUDIT_LOG}")

    total_repaired = sum(1 for e in all_log if e['status'] == 'repaired')
    total_unresolved = sum(1 for e in all_log if e['status'] == 'unresolved')
    print(f"\nSummary: repaired={total_repaired}, unresolved={total_unresolved}")

    if args.dry_run:
        print("(dry-run — no files modified)")


if __name__ == '__main__':
    main()
