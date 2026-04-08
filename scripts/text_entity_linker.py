#!/usr/bin/env python3
"""
text_entity_linker.py — Scan text chunks, find entity mentions, write relation edges.

Disambiguation by resonance: when a name matches multiple entities
(e.g. "arjuna" → plant_arjuna AND deity_arjuna), score each candidate
by relational coherence with other entities in the same chunk.

Reads: datasets/sources/**/*_chunks.jsonl
Writes: datasets/relations/text_entity_relations.csv
        datasets/sources/entity_index.json

Usage: python3 scripts/text_entity_linker.py
"""

import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

SOURCES = ROOT / "datasets" / "sources"
REL_OUT = ROOT / "datasets" / "relations" / "text_entity_relations.csv"
IDX_OUT = SOURCES / "entity_index.json"


# Domain bias: when no graph context, prefer these categories per source domain
DOMAIN_BIAS = {
    "gaudiya":   {"deity": 0.4, "devi": 0.3, "parampara": 0.2},
    "cosmology":  {"deity": 0.3, "nakshatra": 0.2, "graha": 0.2},
    "ayurveda":   {"plant": 0.4, "dosha": 0.3, "marma": 0.2},
    "jyotish":    {"graha": 0.4, "nakshatra": 0.3, "deity": 0.1},
    "yoga":       {"chakra": 0.3, "deity": 0.2, "element": 0.2},
}


# ── Build entity name lookup ──────────────────────────────────

def build_name_lookup() -> dict:
    """Build normalized_name → [entity_ids] lookup from NPU graph metadata.

    Returns dict where each key maps to a list of candidate entity IDs,
    enabling disambiguation when names are ambiguous.
    """
    from npu_engine.datasets import load_entity_metadata
    meta = load_entity_metadata()

    lookup = defaultdict(list)  # lowercase name → [entity_ids]

    MATCH_CATS = {
        "nakshatra", "graha", "deity", "devi", "raga", "tala",
        "element", "guna", "dosha", "rasa", "plant", "marma",
        "chakra", "bija", "tattva", "bhava", "ratna", "yantra",
        "body_region", "vastu_deity", "parampara", "deity_attr",
    }

    # Manual aliases — maps name → single entity_id
    EXTRA = {
        # Nakshatras
        "ashvini": "nakshatra_ashwini", "asvini": "nakshatra_ashwini",
        "bharani": "nakshatra_bharani", "krttika": "nakshatra_krittika",
        "kritika": "nakshatra_krittika", "rohini": "nakshatra_rohini",
        "mrgasira": "nakshatra_mrigashira", "mrigashirsha": "nakshatra_mrigashira",
        "ardra": "nakshatra_ardra", "punarvasu": "nakshatra_punarvasu",
        "pushya": "nakshatra_pushya", "pusya": "nakshatra_pushya",
        "ashlesha": "nakshatra_ashlesha", "aslesa": "nakshatra_ashlesha",
        "magha": "nakshatra_magha", "phalguni": "nakshatra_purva_phalguni",
        "hasta": "nakshatra_hasta", "chitra": "nakshatra_chitra",
        "citra": "nakshatra_chitra", "svati": "nakshatra_swati",
        "swati": "nakshatra_swati", "vishakha": "nakshatra_vishakha",
        "visakha": "nakshatra_vishakha", "anuradha": "nakshatra_anuradha",
        "jyeshtha": "nakshatra_jyeshtha", "jyestha": "nakshatra_jyeshtha",
        "mula": "nakshatra_mula", "ashadha": "nakshatra_purva_ashadha",
        "shravana": "nakshatra_shravana", "sravana": "nakshatra_shravana",
        "dhanishtha": "nakshatra_dhanishtha", "shatabhisha": "nakshatra_shatabhisha",
        "revati": "nakshatra_revati",
        # Grahas
        "surya": "graha_surya", "candra": "graha_chandra",
        "chandra": "graha_chandra", "mangala": "graha_mangala",
        "kuja": "graha_mangala", "budha": "graha_budha",
        "guru": "graha_guru", "brhaspati": "graha_guru",
        "brihaspati": "graha_guru", "shukra": "graha_shukra",
        "sukra": "graha_shukra", "shani": "graha_shani",
        "sani": "graha_shani", "rahu": "graha_rahu", "ketu": "graha_ketu",
        # Deities
        "vishnu": "deity_vishnu", "visnu": "deity_vishnu",
        "shiva": "deity_shiva", "siva": "deity_shiva", "rudra": "deity_rudra",
        "brahma": "deity_brahma", "indra": "deity_indra",
        "agni": "deity_agni", "vayu": "deity_vayu", "varuna": "deity_varuna",
        "krishna": "deity_krishna", "krsna": "deity_krishna",
        "rama": "deity_rama", "hanuman": "deity_hanuman",
        "lakshmi": "deity_lakshmi", "sarasvati": "deity_saraswati",
        "saraswati": "deity_saraswati", "durga": "deity_durga",
        "parvati": "deity_parvati", "ganesa": "deity_ganesha",
        "ganesha": "deity_ganesha",
        # Elements
        "prthivi": "element_earth", "prithvi": "element_earth",
        "apas": "element_water", "jala": "element_water",
        "tejas": "element_fire", "agni_element": "element_fire",
        "vayu_element": "element_air", "akasha": "element_ether",
        "akasa": "element_ether",
        # Gunas
        "sattva": "guna_sattva", "rajas": "guna_rajas", "tamas": "guna_tamas",
        # Doshas
        "vata": "dosha_vata", "pitta": "dosha_pitta", "kapha": "dosha_kapha",
        # Rasas
        "madhura": "rasa_madhura", "amla": "rasa_amla", "lavana": "rasa_lavana",
        "katu": "rasa_katu", "tikta": "rasa_tikta", "kashaya": "rasa_kashaya",
        # Chakras
        "muladhara": "chakra_muladhara", "svadhisthana": "chakra_svadhishthana",
        "manipura": "chakra_manipura", "anahata": "chakra_anahata",
        "vishuddha": "chakra_vishuddha", "ajna": "chakra_ajna",
        "sahasrara": "chakra_sahasrara",
    }

    for eid, m in meta.items():
        cat = m.get("category", "")
        if cat not in MATCH_CATS:
            continue
        name = m.get("name", "")
        if name and len(name) >= 3:
            key = name.lower()
            if eid not in lookup[key]:
                lookup[key].append(eid)
        for alias in m.get("aliases", []):
            if alias and len(alias) >= 3:
                key = alias.lower()
                if eid not in lookup[key]:
                    lookup[key].append(eid)

    # Add manual aliases (these are unambiguous, so just ensure they're in the list)
    for name, eid in EXTRA.items():
        if eid not in lookup[name]:
            lookup[name].append(eid)

    # Remove very short/common words that cause false matches
    for bad in ["sun", "ram", "art", "arm", "air", "son", "one",
                "man", "van", "all", "has", "red", "old"]:
        lookup.pop(bad, None)

    return dict(lookup)


# ── Graph-based disambiguation ───────────────────────────────

def _build_neighbor_index(graph):
    """Pre-build neighbor sets for fast lookup during disambiguation.

    Returns: {entity_id: {neighbor_id: max_confidence}}
    """
    index = {}
    for eid in graph._relations:
        neighbors = {}
        for edge in graph.get_neighbors(eid, exclude_inverse=False):
            to_id = edge.get("to_id", "")
            conf = _safe_float(edge.get("confidence"), 0.5)
            # Keep the highest confidence if multiple edges to same neighbor
            if to_id not in neighbors or conf > neighbors[to_id]:
                neighbors[to_id] = conf
        index[eid] = neighbors
    return index


def disambiguate(candidates, chunk_entities, neighbor_index, domain=""):
    """Choose the best entity from candidates using graph coherence.

    Score each candidate by how many already-detected entities in this
    chunk are its graph neighbors. The entity that resonates most with
    its context wins.

    Falls back to domain bias when no graph signal.
    """
    if len(candidates) == 1:
        return candidates[0]

    scores = {}
    for candidate in candidates:
        score = 0.0
        neighbors = neighbor_index.get(candidate, {})
        for detected in chunk_entities:
            if detected in neighbors:
                score += neighbors[detected]
        scores[candidate] = score

    best_score = max(scores.values())

    # If graph gives a clear winner, use it
    if best_score > 0:
        winners = [c for c, s in scores.items() if s == best_score]
        if len(winners) == 1:
            return winners[0]
        # Tie among graph-connected candidates — use domain bias to break
        candidates = winners

    # Fallback: domain bias
    bias = DOMAIN_BIAS.get(domain, {})
    if bias:
        best_bias = -1.0
        best_candidate = candidates[0]
        for c in candidates:
            cat = c.split("_")[0] if "_" in c else ""
            b = bias.get(cat, 0.0)
            if b > best_bias:
                best_bias = b
                best_candidate = c
        return best_candidate

    # No domain bias either — prefer deity > nakshatra > plant > first
    CAT_ORDER = {"deity": 5, "devi": 4, "nakshatra": 3, "graha": 3,
                 "plant": 2, "raga": 2}
    return max(candidates,
               key=lambda c: CAT_ORDER.get(c.split("_")[0], 1))


def _safe_float(v, default=0.5):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


# ── Scan chunks ───────────────────────────────────────────────

def scan_chunks(lookup: dict, neighbor_index: dict):
    """Scan all chunks for entity mentions with graph-based disambiguation.

    Two-pass per chunk:
      1. Find all name matches → collect candidate sets
      2. Disambiguate ambiguous names using already-resolved entities as context
    """
    relations = []
    entity_index = defaultdict(list)

    names = sorted(lookup.keys(), key=len, reverse=True)
    pattern = re.compile(
        r'\b(' + '|'.join(re.escape(n) for n in names if len(n) >= 4) + r')\b',
        re.IGNORECASE
    )

    chunk_files = sorted(SOURCES.rglob("*_chunks.jsonl"))
    total_chunks = 0
    total_matches = 0
    disambig_count = 0

    for jf in chunk_files:
        source = jf.stem.replace("_chunks", "")
        domain = jf.parent.name

        with open(jf, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    chunk = json.loads(line)
                except json.JSONDecodeError:
                    continue

                total_chunks += 1
                text = chunk.get("text", "")
                chunk_id = f"{source}:{chunk.get('id', 0)}"

                # Pass 1: collect all name matches with their candidate lists
                matches = []  # [(name, [candidate_eids])]
                seen_names = set()
                for match in pattern.finditer(text):
                    name = match.group(1).lower()
                    if name in seen_names:
                        continue
                    seen_names.add(name)
                    candidates = lookup.get(name, [])
                    if candidates:
                        matches.append((name, candidates))

                if not matches:
                    continue

                # Pass 2: resolve unambiguous first, then disambiguate
                resolved = {}   # name → entity_id
                unresolved = []  # [(name, [candidates])]

                for name, candidates in matches:
                    if len(candidates) == 1:
                        resolved[name] = candidates[0]
                    else:
                        unresolved.append((name, candidates))

                # Context for disambiguation: already-resolved entities
                chunk_entities = set(resolved.values())

                # Disambiguate ambiguous names using graph coherence
                for name, candidates in unresolved:
                    winner = disambiguate(candidates, chunk_entities,
                                          neighbor_index, domain)
                    resolved[name] = winner
                    chunk_entities.add(winner)
                    disambig_count += 1

                # Write resolved entities
                for name, eid in resolved.items():
                    relations.append({
                        "from_id": f"chunk:{chunk_id}",
                        "relation": "mentions",
                        "to_id": eid,
                        "source_title": source,
                        "source_locator": str(chunk.get("id", "")),
                        "excerpt": text[:120],
                        "tradition": domain,
                        "confidence": "0.7",
                        "notes": f"auto-linked from {source}",
                    })
                    entity_index[eid].append(chunk_id)
                    total_matches += 1

    return relations, dict(entity_index), total_chunks, total_matches, disambig_count


# ── Write output ──────────────────────────────────────────────

def write_relations(relations: list):
    REL_OUT.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["from_id", "relation", "to_id", "source_title",
                  "source_locator", "excerpt", "tradition", "confidence", "notes"]
    with open(REL_OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(relations)


def write_index(entity_index: dict):
    IDX_OUT.write_text(
        json.dumps(entity_index, indent=2, ensure_ascii=False),
        encoding="utf-8")


# ── Main ──────────────────────────────────────────────────────

def main():
    print("✦ Text entity linker (graph-coherence disambiguation)")
    print("  Building name lookup...")

    lookup = build_name_lookup()
    # Count ambiguous names
    ambig = sum(1 for v in lookup.values() if len(v) > 1)
    print(f"  {len(lookup)} matchable names ({ambig} ambiguous)")

    print("  Loading graph for disambiguation...")
    from npu_engine.graph_engine import GraphEngine
    graph = GraphEngine()
    neighbor_index = _build_neighbor_index(graph)
    print(f"  {graph.node_count} nodes, {graph.edge_count} edges")

    print("  Scanning chunks...")
    relations, entity_index, total_chunks, total_matches, disambig_count = \
        scan_chunks(lookup, neighbor_index)

    print(f"  {total_chunks} chunks scanned")
    print(f"  {total_matches} relations found")
    print(f"  {disambig_count} ambiguous names resolved by graph coherence")
    print(f"  {len(entity_index)} unique entities mentioned")

    write_relations(relations)
    print(f"  → {REL_OUT.relative_to(ROOT)}")

    write_index(entity_index)
    print(f"  → {IDX_OUT.relative_to(ROOT)}")

    # Top entities by mention count
    print("\n  Top 15 entities by mentions:")
    counts = Counter()
    for eid, chunks in entity_index.items():
        counts[eid] = len(chunks)
    for eid, n in counts.most_common(15):
        print(f"    {n:4d}  {eid}")


if __name__ == "__main__":
    main()
