#!/usr/bin/env python3
"""
build_entity_registry.py — REL-002
Scans all domain CSVs for entities and produces a canonical entity registry.
Output: datasets/entities/entity_registry.csv
Columns: entity_id, entity_type, name, name_iast, source_file, row_index
"""

import csv
import os
import re
import glob
from collections import OrderedDict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(BASE, 'datasets')
OUTPUT = os.path.join(DATASET_DIR, 'entities', 'entity_registry.csv')

# ---------- entity type from filename ----------

ENTITY_TYPE_MAP = {
    'nakshatra_master': 'nakshatra',
    'nakshatra_core': 'nakshatra',
    'nakshatra_full': 'nakshatra',
    'nakshatra_extended': 'nakshatra',
    'nakshatra_padas': 'nakshatra',
    'nakshatra_syllables': 'nakshatra',
    'nakshatra_num_to_name': 'nakshatra',
    'nakshatra_deities': 'nakshatra',
    'grahas': 'graha',
    'graha_master': 'graha',
    'tithi_master': 'tithi',
    'tithi_core': 'tithi',
    'tithi_list': 'tithi',
    'tithi_deities': 'tithi',
    'tithi_properties': 'tithi',
    'nitya_devi_master': 'devi',
    'nitya_devi_mapping': 'devi',
    'deity_master': 'deity',
    'deity_attributes': 'deity',
    'deity_domains': 'deity',
    'deity_vahana_extended': 'deity',
    'tala_master': 'tala',
    '35_talas': 'tala',
    'raga_master': 'raga',
    'raga_therapeutic': 'raga',
    'marma_master': 'marma',
    'marma_field': 'marma',
    'marma_coordinates': 'marma',
    'chakra_master': 'chakra',
    'pada_topology': 'pada',
    'element_master': 'element',
    'dosha': 'dosha',
    'doshas': 'dosha',
    'sapta_dhatu': 'dhatu',
    'rasa': 'rasa',
    'rasa_siddhanta': 'rasa',
    'guna': 'guna',
    'gunas': 'guna',
    'vipaka': 'vipaka',
    'virya': 'virya',
    'herb_spine_108': 'herb',
    'herb_exemplars': 'herb',
    'sacred_plants': 'plant',
    'nakshatra_plants': 'plant',
    'instruments': 'instrument',
    'hexagrams': 'hexagram',
    'trigrams': 'trigram',
    'sacred_sites_global': 'site',
    'sacred_sites_india': 'site',
    'shakti_pitha_matrix': 'pitha',
    'bhava_types': 'bhava',
    'parampara': 'parampara',
    'vaishnava_tattva': 'tattva',
    'species_entities': 'species',
    'species_plant_matrix': 'species',
    'nakshatra_species': 'species',
    'sura_asura_map': 'being',
    'metre_correspondence_matrix': 'metre',
    'metres_forms': 'metre',
    'vraja_parikrama': 'site',
    'vraja_forests': 'forest',
    'goloka_topology': 'location',
    'ashtakala': 'period',
    'vedic_arts_64': 'art',
    'asana_core': 'asana',
    'pranayama_core': 'pranayama',
    'bandha_core': 'bandha',
    'matrika_50': 'letter',
}

# Files to skip (join tables, render params, non-entity files)
SKIP_FILES = {
    'atlas_glyphs',           # glyph rendering metadata, not entity source
    'hexagram_raga_resonance',     # join table
    'hexagram_nakshatra_resonance', # join table
    'hexagram_devi_resonance',     # join table
    'species_render_params',       # render params, not entity source
    'species_plant_matrix',        # join table
    'nakshatra_species',           # join table
    'dhatu_herb_matrix',           # join table
    'dhatu_render_params',         # render params
    'sura_asura_map',              # game entity, not domain entity
    'capability_map',              # system metadata
    'code_topology',               # system metadata
    'system_topology',             # system metadata
    'concept',                     # YAML stub, not real entities
    'deity',                       # YAML stub (deity_master is the source)
    'jyotish',                     # YAML stub, meta-categories
    'text',                        # YAML stub
    'nakshatra',                   # entities/ stub (master files are authoritative)
    'graha',                       # entities/ stub (master files are authoritative)
    'nitya_devi_mapping',          # mapping table (tithi→devi), not entity source
    'dosha_nakshatra_matrix',      # matrix, not entity source
    'biodynamic_vedic_mapping',    # mapping table
    'navagraha_kritis',            # composition list, not entity source
    'tithi_deities',               # mapping table (tithi→deity)
    'nakshatra_deities',           # mapping table (nakshatra→deity)
    'tithi_properties',            # properties table, tithi_master is authoritative
}

# ---------- ID column strategies ----------

# Standard ID columns
STANDARD_ID_COLS = [
    'id', 'entity_id', 'graha_id', 'nakshatra_id', 'tithi_id', 'deity_id',
    'species_id', 'herb_id', 'site_id', 'chakra_id', 'dhatu_id', 'tala_id',
    'raga_id', 'pitha_id', 'metre_id',
]

# Name columns used as primary key in files without standard ID
NAME_KEY_COLS = [
    'nakshatra', 'graha', 'deity', 'tithi', 'raga', 'plant', 'asana',
    'pranayama', 'bandha', 'name', 'name_iast',
]

# Name / IAST columns for display
IAST_COLS = ['name_iast', 'name_sanskrit', 'sanskrit', 'name_devanagari']
NAME_COLS = ['name', 'name_iast', 'name_english', 'nakshatra', 'graha',
             'deity', 'tithi', 'raga', 'plant', 'asana', 'pranayama',
             'bandha', 'common_name', 'english_name']


# Sanskrit name overrides for grahas (task spec: use Sanskrit, not English)
GRAHA_SANSKRIT = {
    'sun': ('Surya', 'Sūrya'),
    'moon': ('Chandra', 'Candra'),
    'mars': ('Mangala', 'Maṅgala'),
    'mercury': ('Budha', 'Budha'),
    'jupiter': ('Guru', 'Guru'),
    'venus': ('Shukra', 'Śukra'),
    'saturn': ('Shani', 'Śani'),
    'rahu': ('Rahu', 'Rāhu'),
    'ketu': ('Ketu', 'Ketu'),
}


def slugify(name):
    """Convert a name to canonical slug: lowercase, underscores."""
    s = name.strip().lower()
    s = re.sub(r'[āàáâã]', 'a', s)
    s = re.sub(r'[īìíîĩ]', 'i', s)
    s = re.sub(r'[ūùúûũ]', 'u', s)
    s = re.sub(r'[ṛṝ]', 'ri', s)
    s = re.sub(r'[ṣśṡ]', 'sh', s)
    s = re.sub(r'[ṭ]', 't', s)
    s = re.sub(r'[ḍ]', 'd', s)
    s = re.sub(r'[ṇñṅ]', 'n', s)
    s = re.sub(r'[ṃṁ]', 'm', s)
    s = re.sub(r'[ḥ]', 'h', s)
    s = re.sub(r'[ḻ]', 'l', s)
    # Replace spaces, hyphens, dots with underscore
    s = re.sub(r'[\s\-\.]+', '_', s)
    # Strip non-alphanumeric except underscore
    s = re.sub(r'[^a-z0-9_]', '', s)
    # Collapse multiple underscores
    s = re.sub(r'_+', '_', s).strip('_')
    return s


def entity_type_from_file(filepath):
    """Derive entity type from filename using the mapping."""
    basename = os.path.splitext(os.path.basename(filepath))[0]
    return ENTITY_TYPE_MAP.get(basename)


def find_col(fieldnames, candidates):
    """Return the first matching column name from candidates."""
    for c in candidates:
        if c in fieldnames:
            return c
    return None


def get_name_value(row, fieldnames):
    """Get the best human-readable name from the row."""
    for col in NAME_COLS:
        if col in fieldnames and row.get(col, '').strip():
            return row[col].strip()
    return None


def get_iast_value(row, fieldnames):
    """Get IAST name if available."""
    for col in IAST_COLS:
        if col in fieldnames and row.get(col, '').strip():
            return row[col].strip()
    return ''


def process_file_with_id_col(filepath, id_col, entity_type, fieldnames):
    """Process a CSV that has a standard ID column."""
    entities = []
    rel_path = os.path.relpath(filepath, BASE)
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            raw_id = row.get(id_col, '').strip()
            if not raw_id:
                continue

            name = get_name_value(row, fieldnames)
            iast = get_iast_value(row, fieldnames)

            # If the ID already contains a colon, use it as-is
            if ':' in raw_id:
                eid = raw_id
                etype = raw_id.split(':')[0]
                if not name:
                    name = raw_id.split(':')[1].replace('_', ' ').title()
            else:
                # Build canonical ID
                if name:
                    slug = slugify(name)
                else:
                    slug = slugify(raw_id)
                    name = raw_id.replace('_', ' ').title()
                etype = entity_type

                # For tithis with paksha (shukla/krishna), disambiguate
                paksha = row.get('paksha', '').strip().lower()
                if etype == 'tithi' and paksha in ('shukla', 'krishna'):
                    slug = f'{paksha}_{slug}'

                eid = f'{etype}:{slug}'

            if not name:
                name = ''

            entities.append({
                'entity_id': eid,
                'entity_type': etype,
                'name': name,
                'name_iast': iast,
                'source_file': rel_path,
                'row_index': idx,
            })
    return entities


def process_file_with_name_key(filepath, name_col, entity_type, fieldnames):
    """Process a CSV that uses a name column as the primary key."""
    entities = []
    rel_path = os.path.relpath(filepath, BASE)
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            raw_name = row.get(name_col, '').strip()
            if not raw_name:
                continue

            slug = slugify(raw_name)
            eid = f'{entity_type}:{slug}'
            iast = get_iast_value(row, fieldnames)

            # Try to get a better display name
            name = raw_name
            for col in ['name', 'name_english']:
                if col in fieldnames and row.get(col, '').strip():
                    name = row[col].strip()
                    break

            entities.append({
                'entity_id': eid,
                'entity_type': entity_type,
                'name': name,
                'name_iast': iast if iast else '',
                'source_file': rel_path,
                'row_index': idx,
            })
    return entities


def main():
    # entity_id -> best record (first wins per source, but we track all sources)
    registry = OrderedDict()
    seen_keys = {}  # entity_id -> source_file (for dedup)

    csv_files = sorted(glob.glob(os.path.join(DATASET_DIR, '**', '*.csv'), recursive=True))

    for filepath in csv_files:
        rel_path = os.path.relpath(filepath, BASE)

        # Skip relation files, layer mappings, output file, and non-entity files
        if 'relations' in rel_path:
            continue
        if rel_path == 'datasets/entities/entity_registry.csv':
            continue
        if 'layer_mapping' in rel_path:
            continue
        if 'system/' in rel_path:
            continue

        basename_no_ext = os.path.splitext(os.path.basename(filepath))[0]
        if basename_no_ext in SKIP_FILES:
            continue

        entity_type = entity_type_from_file(filepath)

        try:
            with open(filepath, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames or []
        except Exception:
            continue

        if not fieldnames:
            continue

        entities = []

        # Strategy 1: file has a standard ID column
        id_col = find_col(fieldnames, STANDARD_ID_COLS)
        if id_col and entity_type:
            entities = process_file_with_id_col(filepath, id_col, entity_type, fieldnames)
        elif id_col:
            # Has ID col but no type mapping — try to infer type from directory
            parent_dir = os.path.basename(os.path.dirname(filepath))
            basename = os.path.splitext(os.path.basename(filepath))[0]
            # Use parent dir as type hint
            type_guess = basename.replace('_master', '').replace('_core', '')
            entities = process_file_with_id_col(filepath, id_col, type_guess, fieldnames)
        elif entity_type:
            # No standard ID column — look for a name-key column
            # Prefer column matching entity type (e.g., 'tithi' col for tithi type)
            name_col = None
            if entity_type in fieldnames:
                name_col = entity_type
            else:
                name_col = find_col(fieldnames, NAME_KEY_COLS)
            if name_col:
                entities = process_file_with_name_key(filepath, name_col, entity_type, fieldnames)

        # Deduplicate: keep first occurrence, prefer files with IAST names
        for ent in entities:
            eid = ent['entity_id']
            if eid in registry:
                existing = registry[eid]
                # Prefer the version with IAST name
                if not existing['name_iast'] and ent['name_iast']:
                    registry[eid] = ent
            else:
                registry[eid] = ent

    # Post-process: apply Sanskrit names for grahas
    graha_remap = {}
    for eid, ent in list(registry.items()):
        if ent['entity_type'] == 'graha':
            name_lower = ent['name'].lower()
            if name_lower in GRAHA_SANSKRIT:
                skt_name, skt_iast = GRAHA_SANSKRIT[name_lower]
                new_slug = slugify(skt_name)
                new_eid = f'graha:{new_slug}'
                ent['name'] = skt_name
                ent['name_iast'] = skt_iast
                ent['entity_id'] = new_eid
                graha_remap[eid] = new_eid
    # Re-key remapped grahas
    for old_eid, new_eid in graha_remap.items():
        if old_eid in registry:
            ent = registry.pop(old_eid)
            registry[new_eid] = ent

    # Sort by entity_type then entity_id
    sorted_entities = sorted(registry.values(), key=lambda e: (e['entity_type'], e['entity_id']))

    # Write output
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['entity_id', 'entity_type', 'name', 'name_iast', 'source_file', 'row_index'])
        writer.writeheader()
        writer.writerows(sorted_entities)

    # Summary
    type_counts = {}
    for ent in sorted_entities:
        t = ent['entity_type']
        type_counts[t] = type_counts.get(t, 0) + 1

    print(f'Registry written to {OUTPUT}')
    print(f'Total entities: {len(sorted_entities)}')
    print(f'Entity types ({len(type_counts)}):')
    for t in sorted(type_counts, key=lambda x: -type_counts[x]):
        print(f'  {t}: {type_counts[t]}')


if __name__ == '__main__':
    main()
