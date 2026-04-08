"""
coherence_engine_v2.py — Relation-aware coherence ranking.

Combines:
  0.65 * geometric_score    (toroidal proximity — unchanged math)
  0.25 * relational_score   (graph neighborhood support)
  0.10 * authority_weight   (canon > traditional > inference)
  ±0.05 semantic_modulation (optional, bounded, never overrides)

The toroid remains 2-axis (θ=time, φ=quality).
This engine does NOT modify toroidal coordinates or distances.
It re-ranks entities using additional relational context.
"""

from typing import Any, Dict, List, Optional

from .graph_engine import GraphEngine


# Weights — must sum to 1.0 before semantic modulation
W_GEOMETRIC = 0.65
W_RELATIONAL = 0.25
W_AUTHORITY = 0.10
MAX_SEMANTIC_MOD = 0.05   # bounded ±

_CAT_W = {
    "nakshatra": 1.5, "graha": 1.4, "deity": 1.4,
    "tithi": 1.3, "devi": 1.3, "vara": 1.2,
    "raga": 1.3, "tala": 1.2, "svara": 1.2, "bija": 1.2,
    "plant": 1.0, "dosha": 1.0, "element": 1.0, "marma": 0.9,
    "mythic": 0.6, "jyotish": 0.5,
    "amidha": 0.3, "herb": 0.3,
}

def _cat_w(eid: str) -> float:
    if "amidha_herb" in eid: return 0.3
    if "herb_spine" in eid: return 0.3
    if eid.startswith("jyotish_"): return 0.5
    if eid.startswith("mythic_"): return 0.6
# Category priority weights
# amidha_herb (699 entities) and herb_spine (108) flood the field
# Cosmological entities must dominate
_CAT_W = {
    "nakshatra": 2.0, "graha": 1.8, "deity": 1.8,
    "tithi": 1.6, "devi": 1.6, "vara": 1.5,
    "raga": 1.5, "tala": 1.3, "svara": 1.3, "bija": 1.3,
    "plant": 0.7, "dosha": 1.0, "element": 1.0, "marma": 0.8,
    "amidha": 0.1, "herb": 0.1, "jyotish": 0.5,
}

def _cat_w(eid: str) -> float:
    if "amidha_herb" in eid: return 0.1
    if "herb_spine" in eid: return 0.1
    if eid.startswith("jyotish_"): return 0.5
    # Demote indexed matrix/rules entities (svara_activity_matrix_*, svara_tithi_rules_*, etc.)
    if "activity_matrix" in eid or "tithi_rules" in eid or "coherence_rules" in eid: return 0.3
    # Demote unspecified/family aggregates and placeholder entries
    if "unspecified" in eid or "family_" in eid: return 0.4
    if eid == "graha_none": return 0.2
    # Demote tala_families, tala_sollukattu indexed
    if "tala_families" in eid or "tala_sollukattu" in eid: return 0.4
    p = eid.split("_")[0] if "_" in eid else eid
    return _CAT_W.get(p, 0.8)


def rerank_entities(entities: List[Dict[str, Any]],
                    graph: GraphEngine,
                    seed_count: int = 8,
                    semantic_scores: Optional[Dict[str, float]] = None
                    ) -> List[Dict[str, Any]]:
    """Re-rank toroidally-scored entities with relational context.

    Args:
        entities: list from field_query, each has entity_id + score
        graph: GraphEngine with canonical relations
        seed_count: how many top geometric entities seed the expansion
        semantic_scores: optional {entity_id: 0..1} from embeddings

    Returns:
        entities list re-sorted by composite score, each enriched with:
          geometric_score, relational_score, authority_weight,
          semantic_mod, composite_score, attestation
    """
    if not entities:
        return entities

    semantic = semantic_scores or {}

    # Seed entities for relational expansion
    seed_ids = [e["entity_id"] for e in entities[:seed_count]]
    geo_scores = {e["entity_id"]: e.get("score", 0.0) for e in entities}

    # Expand relations from seeds (depth 2)
    expanded = graph.expand_from_entities(seed_ids, depth=2)
    scored_edges = graph.score_relations(seed_ids, expanded, geo_scores)

    # Build relational support map: entity_id → accumulated relational weight
    rel_support = {}
    for edge in scored_edges:
        to_id = edge["to_id"]
        w = edge.get("_score", 0.0)
        rel_support[to_id] = rel_support.get(to_id, 0.0) + w

    # Normalize relational scores to 0..1
    max_rel = max(rel_support.values()) if rel_support else 1.0
    if max_rel > 0:
        for k in rel_support:
            rel_support[k] = min(1.0, rel_support[k] / max_rel)

    # Score each entity
    for ent in entities:
        eid = ent["entity_id"]

        geo = ent.get("score", 0.0)
        rel = rel_support.get(eid, 0.0)
        auth = graph.authority_weight(eid)
        sem = semantic.get(eid, 0.0)

        # Bounded semantic modulation: ±MAX_SEMANTIC_MOD
        sem_mod = (sem - 0.5) * 2 * MAX_SEMANTIC_MOD  # maps 0..1 → -0.05..+0.05

        composite = _cat_w(eid) * (
            W_GEOMETRIC * geo
            + W_RELATIONAL * rel
            + W_AUTHORITY * auth
            + sem_mod
        )
        composite = max(0.0, min(1.0, composite))

        # Enrich entity with scoring breakdown
        ent["geometric_score"] = round(geo, 4)
        ent["relational_score"] = round(rel, 4)
        ent["authority_weight"] = round(auth, 4)
        ent["semantic_mod"] = round(sem_mod, 4)
        ent["composite_score"] = round(composite, 4)

        # Classify attestation from graph
        meta = graph.meta(eid)
        if meta:
            ent["attestation"] = _entity_attestation(meta)

    # Re-sort by composite score
    entities.sort(key=lambda e: e.get("composite_score", 0.0), reverse=True)

    return entities


def _entity_attestation(meta: Dict) -> str:
    """Derive attestation label from entity metadata."""
    sources = " ".join(str(s) for s in list(meta.get("sources", [])) + list(meta.get("authorities", []))).lower()

    if any(k in sources for k in ("canonical", "core", "master", "observed")):
        return "OBSERVED"
    if any(k in sources for k in ("traditional", "sangita", "jyotisha", "natyashastra")):
        return "TRADITIONAL"
    if any(k in sources for k in ("synthesis", "auto", "inference")):
        return "SYNTHESIS"
    return "INTERPRETATION"


def extract_active_relations(entities: List[Dict],
                             graph: GraphEngine,
                             top_n: int = 10) -> List[Dict[str, Any]]:
    """Extract the most active canonical relations among top entities.

    Returns scored relation edges between coherent entities,
    sorted by relevance. Each edge preserves attestation.
    """
    top_ids = [e["entity_id"] for e in entities[:top_n]]
    top_set = set(top_ids)

    active = []
    seen = set()

    for eid in top_ids:
        for edge in graph.get_neighbors(eid, exclude_inverse=True):
            to_id = edge["to_id"]
            key = (edge["from_id"], edge["relation"], to_id)
            if key in seen:
                continue
            seen.add(key)

            enriched = dict(edge)
            enriched["attestation"] = edge.get("attestation",
                                               _edge_attestation(edge))
            # Boost if both endpoints are coherent
            enriched["mutual"] = to_id in top_set
            if enriched["mutual"]:
                enriched["relevance"] = 1.0
            else:
                enriched["relevance"] = 0.5
            active.append(enriched)

    active.sort(key=lambda e: (e.get("mutual", False), e.get("relevance", 0)),
                reverse=True)
    return active[:50]


def _edge_attestation(edge: Dict) -> str:
    """Classify a single edge's attestation."""
    auth = str(edge.get("authority", "")).lower()
    if "canonical" in auth or "observed" in auth:
        return "OBSERVED"
    if "traditional" in auth:
        return "TRADITIONAL"
    if "synthesis" in auth or "auto" in auth:
        return "SYNTHESIS"
    return "INTERPRETATION"
