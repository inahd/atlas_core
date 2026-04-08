"""
raga_graph.py — Directed melodic phrase graph for rāga generation.

Each rāga is a directed graph:
  nodes  = swaras (Sa, Re, Ga, Ma, Pa, Dha, Ni + komal/tīvra variants)
  edges  = characteristic phrase transitions with weights
  vādī   = highest-weight node (most edges resolve here)
  samvādī = second-weight node

Traversal = rāga-compliant phrase generation.
NPU coherence scores modulate edge weights in real time.
"""

import random

# Just intonation ratios — physics, shared with relational_synth
JI_RATIOS = {
    "Sa":    1.0,
    "Re_k":  256/243,
    "Re":    9/8,
    "Ga_k":  32/27,
    "Ga":    5/4,
    "Ma":    4/3,
    "Ma_t":  45/32,
    "Pa":    3/2,
    "Dha_k": 128/81,
    "Dha":   5/3,
    "Ni_k":  16/9,
    "Ni":    15/8,
}

# ══════════════════════════════════════════════════════════
# RĀGA GRAPHS — adjacency dicts with edge weights
# ══════════════════════════════════════════════════════════

RAGA_GRAPHS = {
    'Yaman': {
        'nodes': ['Sa', 'Re', 'Ga', 'Ma_t', 'Pa', 'Dha', 'Ni'],
        'vadi': 'Ga',
        'samvadi': 'Ni',
        'nyasa': ['Sa', 'Ga', 'Pa'],
        'aroha_bias': 0.6,
        'edges': {
            'Sa':   {'Re': 0.7, 'Ni': 0.3},
            'Re':   {'Ga': 0.8, 'Sa': 0.2},
            'Ga':   {'Ma_t': 0.5, 'Re': 0.3, 'Pa': 0.2},
            'Ma_t': {'Pa': 0.7, 'Ga': 0.3},
            'Pa':   {'Dha': 0.6, 'Ga': 0.2, 'Ma_t': 0.2},
            'Dha':  {'Ni': 0.6, 'Pa': 0.4},
            'Ni':   {'Sa+': 0.5, 'Dha': 0.3, 'Pa': 0.2},
            'Sa+':  {'Ni': 0.5, 'Dha': 0.5},
        }
    },
    'Bhairava': {
        'nodes': ['Sa', 'Re_k', 'Ga', 'Ma', 'Pa', 'Dha_k', 'Ni'],
        'vadi': 'Dha_k',
        'samvadi': 'Re_k',
        'nyasa': ['Sa', 'Ga', 'Pa'],
        'aroha_bias': 0.5,
        'edges': {
            'Sa':    {'Re_k': 0.8, 'Ni': 0.2},
            'Re_k':  {'Ga': 0.7, 'Sa': 0.3},
            'Ga':    {'Ma': 0.6, 'Re_k': 0.4},
            'Ma':    {'Pa': 0.8, 'Ga': 0.2},
            'Pa':    {'Dha_k': 0.7, 'Ma': 0.3},
            'Dha_k': {'Ni': 0.5, 'Pa': 0.5},
            'Ni':    {'Sa+': 0.6, 'Dha_k': 0.4},
            'Sa+':   {'Ni': 0.6, 'Dha_k': 0.4},
        }
    },
    'Bhimpalasi': {
        'nodes': ['Sa', 'Re', 'Ga_k', 'Ma', 'Pa', 'Dha', 'Ni_k'],
        'vadi': 'Ma',
        'samvadi': 'Sa',
        'nyasa': ['Sa', 'Ma', 'Pa'],
        'aroha_bias': 0.45,
        'edges': {
            'Sa':    {'Ma': 0.5, 'Re': 0.3, 'Ni_k': 0.2},
            'Re':    {'Ga_k': 0.7, 'Sa': 0.3},
            'Ga_k':  {'Ma': 0.8, 'Re': 0.2},
            'Ma':    {'Pa': 0.5, 'Ga_k': 0.3, 'Sa': 0.2},
            'Pa':    {'Ni_k': 0.4, 'Dha': 0.4, 'Ma': 0.2},
            'Dha':   {'Ni_k': 0.6, 'Pa': 0.4},
            'Ni_k':  {'Sa+': 0.6, 'Dha': 0.4},
            'Sa+':   {'Ni_k': 0.5, 'Pa': 0.5},
        }
    },
    'Darbari': {
        'nodes': ['Sa', 'Re', 'Ga_k', 'Ma', 'Pa', 'Dha_k', 'Ni_k'],
        'vadi': 'Re',
        'samvadi': 'Pa',
        'nyasa': ['Sa', 'Re', 'Pa'],
        'aroha_bias': 0.4,
        'andolana': ['Ga_k', 'Dha_k'],
        'edges': {
            'Sa':    {'Re': 0.6, 'Ni_k': 0.4},
            'Re':    {'Ma': 0.4, 'Ga_k': 0.4, 'Sa': 0.2},
            'Ga_k':  {'Ma': 0.5, 'Re': 0.5},
            'Ma':    {'Pa': 0.7, 'Re': 0.3},
            'Pa':    {'Ni_k': 0.3, 'Dha_k': 0.4, 'Ma': 0.3},
            'Dha_k': {'Ni_k': 0.5, 'Pa': 0.5},
            'Ni_k':  {'Sa+': 0.5, 'Dha_k': 0.5},
            'Sa+':   {'Ni_k': 0.6, 'Dha_k': 0.4},
        }
    },
    'Bageshri': {
        'nodes': ['Sa', 'Re', 'Ga_k', 'Ma', 'Pa', 'Dha', 'Ni_k'],
        'vadi': 'Ma',
        'samvadi': 'Sa',
        'nyasa': ['Sa', 'Ma'],
        'aroha_bias': 0.4,
        'edges': {
            'Sa':    {'Ma': 0.5, 'Ga_k': 0.3, 'Re': 0.2},
            'Re':    {'Ga_k': 0.7, 'Sa': 0.3},
            'Ga_k':  {'Ma': 0.8, 'Re': 0.2},
            'Ma':    {'Pa': 0.4, 'Ga_k': 0.4, 'Sa': 0.2},
            'Pa':    {'Ni_k': 0.4, 'Dha': 0.4, 'Ma': 0.2},
            'Dha':   {'Ni_k': 0.6, 'Pa': 0.4},
            'Ni_k':  {'Sa+': 0.5, 'Dha': 0.5},
            'Sa+':   {'Ni_k': 0.6, 'Dha': 0.4},
        }
    },
    'Marva': {
        'nodes': ['Sa', 'Re_k', 'Ga', 'Ma_t', 'Dha', 'Ni'],
        'vadi': 'Re_k',
        'samvadi': 'Dha',
        'nyasa': ['Re_k', 'Dha'],
        'aroha_bias': 0.45,
        'edges': {
            'Sa':    {'Re_k': 0.7, 'Ni': 0.3},
            'Re_k':  {'Ga': 0.6, 'Sa': 0.4},
            'Ga':    {'Ma_t': 0.7, 'Re_k': 0.3},
            'Ma_t':  {'Dha': 0.7, 'Ga': 0.3},
            'Dha':   {'Ni': 0.6, 'Ma_t': 0.4},
            'Ni':    {'Sa+': 0.5, 'Dha': 0.5},
            'Sa+':   {'Ni': 0.6, 'Dha': 0.4},
        }
    },
    'Kafi': {
        'nodes': ['Sa', 'Re', 'Ga_k', 'Ma', 'Pa', 'Dha', 'Ni_k'],
        'vadi': 'Pa',
        'samvadi': 'Sa',
        'nyasa': ['Sa', 'Pa'],
        'aroha_bias': 0.55,
        'edges': {
            'Sa':    {'Re': 0.6, 'Ni_k': 0.4},
            'Re':    {'Ga_k': 0.6, 'Sa': 0.4},
            'Ga_k':  {'Ma': 0.7, 'Re': 0.3},
            'Ma':    {'Pa': 0.7, 'Ga_k': 0.3},
            'Pa':    {'Dha': 0.5, 'Ma': 0.3, 'Sa+': 0.2},
            'Dha':   {'Ni_k': 0.6, 'Pa': 0.4},
            'Ni_k':  {'Sa+': 0.6, 'Dha': 0.4},
            'Sa+':   {'Ni_k': 0.5, 'Pa': 0.5},
        }
    },
}

# Alias map for fuzzy matching
_ALIASES = {
    'yaman_kalyan': 'Yaman', 'yaman': 'Yaman',
    'bhairava': 'Bhairava', 'bhairav': 'Bhairava',
    'bhimpalasi': 'Bhimpalasi', 'bhimpalasī': 'Bhimpalasi', 'bhīmpalāsī': 'Bhimpalasi',
    'darbari': 'Darbari', 'darbārī': 'Darbari', 'darbari_kanada': 'Darbari',
    'bageshri': 'Bageshri', 'bāgeshṛī': 'Bageshri', 'bageshree': 'Bageshri',
    'marva': 'Marva', 'mārvā': 'Marva',
    'kafi': 'Kafi', 'kāfī': 'Kafi',
    'multani': 'Bhimpalasi', 'multānī': 'Bhimpalasi',  # similar structure
    'todi': 'Bhairava', 'tōḍī': 'Bhairava',  # rough fallback
}

# Swara name mapping for svara_weights keys → graph node names.
# Kernel svara_weights use: Sa, re, Re, ga, Ga, ma, Ma, Pa, dha, Dha, ni, Ni
_WEIGHT_TO_NODE = {
    'Sa': 'Sa', 're': 'Re_k', 'Re': 'Re', 'ga': 'Ga_k', 'Ga': 'Ga',
    'ma': 'Ma', 'Ma': 'Ma_t', 'Pa': 'Pa', 'dha': 'Dha_k', 'Dha': 'Dha',
    'ni': 'Ni_k', 'Ni': 'Ni',
    # Also accept node names directly
    'Re_k': 'Re_k', 'Ga_k': 'Ga_k', 'Ma_t': 'Ma_t', 'Dha_k': 'Dha_k', 'Ni_k': 'Ni_k',
}


# ══════════════════════════════════════════════════════════
# AUTO-LOAD RAGAS FROM CSV
# ══════════════════════════════════════════════════════════

def _svara_to_node(s):
    """Convert CSV svara name to graph node name."""
    s = s.strip()
    MAP = {'Ri':'Re','ri':'Re_k','Re':'Re','re':'Re_k',
           'Ga':'Ga','ga':'Ga_k','Ma':'Ma','ma':'Ma',
           'Ma#':'Ma_t','ma#':'Ma_t','Pa':'Pa',
           'Dha':'Dha','dha':'Dha_k','Ni':'Ni','ni':'Ni_k',
           'Sa':'Sa','Sa+':'Sa+','Sa-':'Sa-'}
    return MAP.get(s, s)

def _build_edges_from_aroha(nodes):
    """Generate directed edges from an ordered svara list."""
    edges = {}
    for i, n in enumerate(nodes):
        targets = {}
        if i + 1 < len(nodes):
            targets[nodes[i+1]] = 0.7
        if i > 0:
            targets[nodes[i-1]] = 0.3
        edges[n] = targets
    # Add Sa+ ↔ last node if not present
    if nodes and 'Sa+' not in edges:
        edges['Sa+'] = {nodes[-1]: 0.6}
        if nodes[-1] in edges:
            edges[nodes[-1]]['Sa+'] = 0.4
    return edges

def _load_ragas_from_csv():
    """Load rāga graphs from CSV data files.

    For new ragas: builds full graph from aroha/avaroha.
    For existing handcrafted ragas: injects aroha/avaroha sequences
    so phrase_engine can use them for directional movement.
    """
    from pathlib import Path
    import csv

    csv_path = Path(__file__).resolve().parent.parent / "datasets" / "carnatic" / "raga_master_extended.csv"
    if not csv_path.exists():
        return

    for row in csv.DictReader(open(csv_path, encoding='utf-8-sig')):
        rid = row.get('id', '').replace('raga_', '')
        name = row.get('name_iast', rid)
        aroha_str = row.get('aroha', '')
        avaroha_str = row.get('avaroha', '')
        vadi = row.get('vadi', '')
        samvadi = row.get('samvadi', '')

        # Parse aroha/avaroha into node names
        aroha_raw = [s.strip() for s in aroha_str.replace(',', ' ').split() if s.strip()]
        avaroha_raw = [s.strip() for s in avaroha_str.replace(',', ' ').split() if s.strip()]
        aroha_nodes = [_svara_to_node(s) for s in aroha_raw]
        avaroha_nodes = [_svara_to_node(s) for s in avaroha_raw]

        # If this raga already exists (handcrafted), inject aroha/avaroha sequences
        existing_key = None
        for k in RAGA_GRAPHS:
            if k.lower() == rid.lower() or k.lower() == name.lower().replace(' ', '_'):
                existing_key = k
                break
        if existing_key is None:
            # Check aliases
            alias_key = _ALIASES.get(rid.lower()) or _ALIASES.get(
                name.lower().replace(' ', '_'))
            if alias_key and alias_key in RAGA_GRAPHS:
                existing_key = alias_key

        if existing_key:
            # Enrich existing graph with aroha/avaroha sequences
            if aroha_nodes:
                RAGA_GRAPHS[existing_key]['aroha'] = aroha_nodes
            if avaroha_nodes:
                RAGA_GRAPHS[existing_key]['avaroha'] = avaroha_nodes
            _ALIASES[rid.lower()] = existing_key
            continue

        nodes = list(dict.fromkeys(n for n in aroha_nodes))
        if not nodes:
            continue

        vadi_node = _svara_to_node(vadi) if vadi else nodes[len(nodes)//2]
        samvadi_node = _svara_to_node(samvadi) if samvadi else (nodes[0] if len(nodes) > 1 else 'Sa')

        edges = _build_edges_from_aroha(nodes)

        graph_name = name.split('/')[0].strip().replace(' ', '_')
        RAGA_GRAPHS[graph_name] = {
            'nodes': nodes,
            'vadi': vadi_node,
            'samvadi': samvadi_node,
            'nyasa': ['Sa', vadi_node],
            'aroha_bias': 0.5,
            'aroha': aroha_nodes,
            'avaroha': avaroha_nodes,
            'edges': edges,
        }

        # Add aliases
        _ALIASES[rid.lower()] = graph_name
        _ALIASES[name.lower().replace(' ', '_')] = graph_name
        for c in 'āīūṛṝḷṃḥṅñṭḍṇśṣḻ':
            simple = {'ā':'a','ī':'i','ū':'u','ṛ':'r','ṝ':'r','ḷ':'l','ṃ':'m','ḥ':'h',
                      'ṅ':'n','ñ':'n','ṭ':'t','ḍ':'d','ṇ':'n','ś':'sh','ṣ':'sh','ḻ':'l'}.get(c, c)
            if c in name.lower():
                simplified = name.lower().replace(c, simple).replace(' ', '_')
                _ALIASES[simplified] = graph_name

try:
    _load_ragas_from_csv()
except Exception:
    pass  # CSV not available — use handcrafted graphs only


# ══════════════════════════════════════════════════════════
# PUBLIC API
# ══════════════════════════════════════════════════════════

def get_raga_graph(raga_name: str) -> dict | None:
    """Return graph for named rāga. Case-insensitive, alias-aware."""
    if not raga_name:
        return None
    # Exact match
    if raga_name in RAGA_GRAPHS:
        return RAGA_GRAPHS[raga_name]
    # Alias / fuzzy
    key = raga_name.lower().replace(' ', '_').replace('ā', 'a').replace('ī', 'i').replace('ū', 'u')
    canonical = _ALIASES.get(key)
    if canonical and canonical in RAGA_GRAPHS:
        return RAGA_GRAPHS[canonical]
    # Substring match
    for name in RAGA_GRAPHS:
        if name.lower() in key or key in name.lower():
            return RAGA_GRAPHS[name]
    return None


def generate_phrase(raga_name: str, length: int = 6, start_node: str = None,
                    svara_weights: dict = None) -> list:
    """Random walk on rāga graph, producing a rāga-compliant phrase.

    Args:
        raga_name:     rāga to use
        length:        target phrase length (may extend by up to 3 for nyāsa)
        start_node:    starting swara (None = 50/50 Sa or vādī)
        svara_weights: dict from field state — modulates edge weights

    Returns:
        List of swara name strings. Andolana notes marked with '~' suffix.
    """
    graph = get_raga_graph(raga_name)
    if graph is None:
        # Fallback: basic Sa-Pa-Sa
        return ['Sa', 'Pa', 'Sa']

    edges = graph['edges']
    nyasa = set(graph.get('nyasa', ['Sa']))
    andolana = set(graph.get('andolana', []))

    # Normalize svara_weights to graph node names
    node_weights = {}
    if svara_weights:
        for sw_key, w in svara_weights.items():
            node = _WEIGHT_TO_NODE.get(sw_key, sw_key)
            node_weights[node] = float(w) if isinstance(w, (int, float)) else 0.5

    # Start node
    if start_node and start_node in edges:
        current = start_node
    elif random.random() < 0.5:
        current = 'Sa'
    else:
        current = graph.get('vadi', 'Sa')
        if current not in edges:
            current = 'Sa'

    phrase = [current]

    for _ in range(length - 1 + 3):  # extra room for nyāsa resolution
        if current not in edges:
            break

        targets = edges[current]
        if not targets:
            break

        # Weight modulation: multiply edge weight by svara_weight of target
        weighted = {}
        for target, w in targets.items():
            # Strip octave marker for weight lookup
            base = target.rstrip('+').rstrip('-')
            npu_mod = node_weights.get(base, 0.5)
            weighted[target] = w * (0.5 + npu_mod)

        # Normalize
        total = sum(weighted.values())
        if total <= 0:
            break

        # Weighted random choice
        r = random.random() * total
        cumulative = 0.0
        chosen = list(weighted.keys())[0]
        for target, w in weighted.items():
            cumulative += w
            if r <= cumulative:
                chosen = target
                break

        current = chosen
        phrase.append(current)

        # Check if we've reached desired length and can stop at nyāsa
        base_current = current.rstrip('+').rstrip('-')
        if len(phrase) >= length and base_current in nyasa:
            break

    # Mark andolana notes
    result = []
    for note in phrase:
        base = note.rstrip('+').rstrip('-')
        if base in andolana:
            result.append(note + '~')
        else:
            result.append(note)

    return result


def phrase_to_freqs(phrase: list, sa_hz: float,
                    ji_ratios: dict = None) -> list:
    """Convert swara names to (freq_hz, swara_name) tuples.

    Sa+ = octave above (×2), Sa- = octave below (×0.5).
    Andolana marker '~' is preserved in the name but stripped for lookup.
    """
    if ji_ratios is None:
        ji_ratios = JI_RATIOS

    result = []
    for note in phrase:
        # Strip markers
        clean = note.rstrip('~')
        octave = 1.0
        if clean.endswith('+'):
            clean = clean[:-1]
            octave = 2.0
        elif clean.endswith('-'):
            clean = clean[:-1]
            octave = 0.5

        ratio = ji_ratios.get(clean, 1.0)
        freq = sa_hz * ratio * octave
        result.append((round(freq, 2), note))

    return result
