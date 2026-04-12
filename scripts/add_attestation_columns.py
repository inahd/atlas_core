#!/usr/bin/env python3
"""Add attestation_status column to CSVs that lack it."""
import csv, glob, os, sys

DOMAIN_DEFAULTS = {
    'astro': 'attested_classical',
    'cosmology': 'attested_classical',
    'ayurveda': 'attested_secondary',
    'carnatic': 'attested_secondary',
    'gandharva': 'attested_secondary',
    'vastu': 'attested_secondary',
    'yoga': 'attested_secondary',
    'iching': 'inferred_coherent',
    'symbols': 'inferred_coherent',
    'plants': 'attested_secondary',
    'game': 'inferred_coherent',
    'geography': 'attested_secondary',
    'species': 'attested_secondary',
    'marma': 'attested_secondary',
    'svarodaya': 'attested_classical',
    'chandas': 'attested_classical',
    'ontology': 'attested_classical',
    'permaculture': 'inferred_coherent',
    'morphogenesis': 'inferred_coherent',
    'entities': 'seed_unverified',
    'ritual': 'attested_secondary',
    'sound': 'attested_secondary',
    'tantra': 'attested_classical',
    'silpa': 'attested_classical',
    'semantics': 'inferred_coherent',
    'sources': 'attested_secondary',
    'views': 'inferred_coherent',
    'system': 'inferred_coherent',
    'layer_mapping.csv': 'inferred_coherent',
}


def add_attestation(filepath, default):
    with open(filepath) as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        if not fieldnames or 'attestation_status' in fieldnames:
            return False
        rows = list(reader)

    if len(rows) <= 3:
        return False

    fieldnames.append('attestation_status')
    for row in rows:
        row['attestation_status'] = default

    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return True


count = 0
for f in sorted(glob.glob('datasets/**/*.csv', recursive=True)):
    if 'relations' in f:
        continue
    # Determine domain from path
    parts = f.split('/')
    if len(parts) >= 2:
        domain = parts[1]
    else:
        domain = 'unknown'
    # Check for top-level files (e.g. datasets/layer_mapping.csv)
    if len(parts) == 2:
        default = DOMAIN_DEFAULTS.get(parts[1], 'seed_unverified')
    else:
        default = DOMAIN_DEFAULTS.get(domain, 'seed_unverified')
    if add_attestation(f, default):
        print(f'Added: {f} ({default})')
        count += 1

print(f'\nTotal updated: {count}')
