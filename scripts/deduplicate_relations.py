#!/usr/bin/env python3
"""Remove exact duplicate relations across all relation CSVs.

Policy:
- Exact duplicates: keep the first occurrence, remove subsequent ones
- Canon file (relations_resolved_canon.csv): never touched
- Inverse pairs: kept (they serve different traversal directions), logged
- Same subject+object with different predicate: kept (different relations)
"""
import csv
import glob
import os

RELATIONS_DIR = os.path.join(os.path.dirname(__file__), '..', 'datasets', 'relations')
AUDIT_DIR = os.path.join(os.path.dirname(__file__), '..', 'docs', 'audit')

# Inverse predicate pairs — logged but not removed
INVERSE_PAIRS = {
    'nakshatra_ruling_graha': 'graha_rules_nakshatra',
    'nakshatra_associated_deity': 'deity_presides_nakshatra',
    'composed_by': 'composer_of',
    'element': 'has_element',
    'dosha': 'associated_dosha',
    'ruling_graha': 'rules_nakshatra',
    'presiding_deity': 'presides_over',
}

def main():
    seen = set()
    dedup_log = []
    inverse_log = []
    total_removed = 0

    # Process files in sorted order for deterministic results
    # Canon file is processed first so its triples claim the "seen" slots
    files = sorted(glob.glob(os.path.join(RELATIONS_DIR, '*.csv')))
    canon_files = [f for f in files if 'canon' in os.path.basename(f)]
    other_files = [f for f in files if 'canon' not in os.path.basename(f)]
    ordered_files = canon_files + other_files

    for filepath in ordered_files:
        basename = os.path.basename(filepath)
        is_canon = 'canon' in basename

        try:
            with open(filepath, newline='') as fh:
                rows = list(csv.DictReader(fh))
        except Exception as e:
            print(f'Error reading {basename}: {e}')
            continue

        if not rows:
            continue

        clean = []
        file_removed = 0
        for row in rows:
            key = (row.get('from_id', ''), row.get('relation', ''), row.get('to_id', ''))
            if not all(key):
                clean.append(row)  # keep rows with missing fields (don't drop data)
                continue

            if key in seen:
                if is_canon:
                    clean.append(row)  # never remove from canon
                else:
                    dedup_log.append({
                        'file': basename,
                        'from_id': key[0],
                        'relation': key[1],
                        'to_id': key[2],
                    })
                    file_removed += 1
            else:
                seen.add(key)
                clean.append(row)

        if file_removed > 0:
            print(f'Removed {file_removed} duplicates from {basename}')
            total_removed += file_removed
            with open(filepath, 'w', newline='') as fh:
                writer = csv.DictWriter(fh, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(clean)

    # Scan for inverse pairs (log only, do not remove)
    all_triples = set()
    for filepath in ordered_files:
        try:
            for row in csv.DictReader(open(filepath, newline='')):
                t = (row.get('from_id', ''), row.get('relation', ''), row.get('to_id', ''))
                if all(t):
                    all_triples.add(t)
        except:
            pass

    for subj, pred, obj in all_triples:
        inv_pred = INVERSE_PAIRS.get(pred)
        if inv_pred and (obj, inv_pred, subj) in all_triples:
            inverse_log.append({
                'from_id': subj,
                'relation': pred,
                'to_id': obj,
                'inverse_relation': inv_pred,
            })

    print(f'\nTotal duplicates removed: {total_removed}')
    print(f'Inverse pairs logged (kept): {len(inverse_log)}')

    # Write dedup log
    os.makedirs(AUDIT_DIR, exist_ok=True)
    log_path = os.path.join(AUDIT_DIR, 'dedup_log.csv')
    with open(log_path, 'w', newline='') as fh:
        fields = ['file', 'from_id', 'relation', 'to_id']
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(dedup_log)
    print(f'Dedup log written to {log_path} ({len(dedup_log)} entries)')

    # Write inverse log if any
    if inverse_log:
        inv_path = os.path.join(AUDIT_DIR, 'inverse_pairs_log.csv')
        with open(inv_path, 'w', newline='') as fh:
            fields = ['from_id', 'relation', 'to_id', 'inverse_relation']
            writer = csv.DictWriter(fh, fieldnames=fields)
            writer.writeheader()
            writer.writerows(inverse_log)
        print(f'Inverse pairs log written to {inv_path} ({len(inverse_log)} entries)')


if __name__ == '__main__':
    main()
