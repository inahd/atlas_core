"""
query_engine.py — Structured field query with focus, domain filter, and depth expansion.

Does NOT compute coherence or modify the source field_state.
Reads entities + relations, filters, boosts, expands, returns.

Usage:
    result = query(state, focus="nakshatra_rohini", domain="deity", depth=2)
"""

from typing import Any, Dict, List, Optional, Set

from .graph_engine import GraphEngine


# Lazy singleton
_graph: Optional[GraphEngine] = None


def _get_graph() -> GraphEngine:
    global _graph
    if _graph is None:
        _graph = GraphEngine()
    return _graph


def query(field_state: Dict[str, Any],
          focus: Optional[str] = None,
          domain: Optional[str] = None,
          depth: int = 1,
          top_n: int = 20,
          boost_weight: float = 0.15) -> Dict[str, Any]:
    """Query the field with optional focus entity, domain filter, and relation depth.

    Args:
        field_state:   dict from /spine or build_field_state
        focus:         entity_id to boost neighborhood of (optional)
        domain:        category prefix to filter by, e.g. "nakshatra", "deity", "raga" (optional)
        depth:         relation expansion hops (1 or 2)
        top_n:         max entities returned
        boost_weight:  how much relational proximity to focus boosts score (0..1)

    Returns:
        {
            "entities":   [...],   # filtered, boosted, sorted
            "relations":  [...],   # relevant edges
            "focus":      str or None,
            "domain":     str or None,
            "depth":      int,
            "count":      int,
        }
    """
    entities = list(field_state.get("entities") or [])
    relations = list(field_state.get("active_relations") or [])
    graph = _get_graph()

    # ── Domain filter ─────────────────────────────────────
    if domain:
        d = domain.lower().rstrip("s")  # "deities" → "deity"
        entities = [e for e in entities if _entity_domain(e) == d]
        relations = [r for r in relations
                     if _id_domain(r.get("from_id", "")) == d
                     or _id_domain(r.get("to_id", "")) == d]

    # ── Focus boost + expansion ───────────────────────────
    focus_ids: Set[str] = set()
    expanded_relations: List[Dict] = []

    if focus:
        # Expand neighborhood from focus entity
        neighbors = graph.expand_from_entities([focus], depth=depth, max_per_node=30)
        expanded_relations = neighbors

        # Collect all IDs in the focus neighborhood
        focus_ids.add(focus)
        for edge in neighbors:
            focus_ids.add(edge.get("from_id", ""))
            focus_ids.add(edge.get("to_id", ""))
        focus_ids.discard("")

        # Boost entities that are in the focus neighborhood
        for e in entities:
            eid = e.get("entity_id", "")
            base = e.get("composite_score", e.get("score", 0.0))

            if eid == focus:
                e["query_score"] = min(1.0, base + boost_weight * 2)
                e["focus_relation"] = "self"
            elif eid in focus_ids:
                # Find the relation connecting this entity to focus
                rel_type = _find_relation(eid, focus, neighbors)
                hop = _find_hop(eid, neighbors)
                decay = 1.0 / (hop + 1) if hop > 0 else 1.0
                e["query_score"] = min(1.0, base + boost_weight * decay)
                e["focus_relation"] = rel_type
            else:
                e["query_score"] = base
                e["focus_relation"] = None

        # Add entities from expansion that aren't in the current list
        existing_ids = {e.get("entity_id") for e in entities}
        for eid in focus_ids:
            if eid not in existing_ids:
                meta = graph.meta(eid)
                if meta:
                    entities.append({
                        "entity_id": eid,
                        "name": meta.get("name", eid),
                        "element": _first_attr(meta, "element", "ether"),
                        "guna": _first_attr(meta, "guna", "sattva"),
                        "attestation": _meta_attestation(meta),
                        "score": 0.0,
                        "composite_score": 0.0,
                        "query_score": boost_weight * 0.5,
                        "focus_relation": _find_relation(eid, focus, neighbors),
                        "expanded": True,
                    })

        # Sort by query_score
        entities.sort(key=lambda e: e.get("query_score", 0), reverse=True)

        # Merge expanded relations into output
        relation_set = {(r.get("from_id"), r.get("relation"), r.get("to_id"))
                        for r in relations}
        for r in expanded_relations:
            key = (r.get("from_id"), r.get("relation"), r.get("to_id"))
            if key not in relation_set:
                relations.append(r)
                relation_set.add(key)
    else:
        # No focus — just use composite_score as query_score
        for e in entities:
            e["query_score"] = e.get("composite_score", e.get("score", 0.0))
            e["focus_relation"] = None

    # ── Trim ──────────────────────────────────────────────
    entities = entities[:top_n]
    result_ids = {e.get("entity_id") for e in entities}
    relations = [r for r in relations
                 if r.get("from_id") in result_ids or r.get("to_id") in result_ids]

    # Preserve all original state fields, override entities + relations
    result = dict(field_state)
    result["entities"] = entities
    result["active_relations"] = relations
    result["relations"] = relations  # alias for compatibility
    result["_query"] = {"focus": focus, "domain": domain, "depth": depth}
    result["count"] = len(entities)
    return result


# ── Helpers ───────────────────────────────────────────────

def _entity_domain(entity: Dict) -> str:
    """Extract domain/category from entity_id prefix."""
    eid = entity.get("entity_id", "")
    return _id_domain(eid)


def _id_domain(entity_id: str) -> str:
    """nakshatra_rohini → nakshatra, deity_varuna → deity."""
    parts = entity_id.split("_")
    if len(parts) >= 2:
        prefix = parts[0]
        # Handle multi-word prefixes
        if prefix in ("nakshatra", "graha", "deity", "devi", "raga", "tala",
                       "plant", "marma", "dosha", "bija", "art", "vastu",
                       "svara", "concept", "amidha"):
            return prefix
        if entity_id.startswith("nakshatra_pada"):
            return "nakshatra_pada"
    return parts[0] if parts else ""


def _find_relation(entity_id: str, focus: str,
                   edges: List[Dict]) -> Optional[str]:
    """Find the relation type connecting entity_id to focus."""
    for e in edges:
        if (e.get("from_id") == focus and e.get("to_id") == entity_id) or \
           (e.get("to_id") == focus and e.get("from_id") == entity_id):
            return e.get("relation", "related")
    return None


def _find_hop(entity_id: str, edges: List[Dict]) -> int:
    """Find the hop distance of entity_id in expanded edges."""
    for e in edges:
        if e.get("to_id") == entity_id or e.get("from_id") == entity_id:
            return e.get("hop", 1)
    return 99


def _first_attr(meta: Dict, key: str, default: str) -> str:
    """Get first value from metadata attributes list."""
    attrs = meta.get("attributes", {})
    vals = attrs.get(key, [])
    if isinstance(vals, list) and vals:
        return str(vals[0]).lower()
    if isinstance(vals, str) and vals:
        return vals.lower()
    return default


def _meta_attestation(meta: Dict) -> str:
    """Derive attestation from metadata sources."""
    sources = " ".join(str(s) for s in list(meta.get("sources", [])) + list(meta.get("authorities", []))).lower()
    if "canonical" in sources or "core" in sources or "master" in sources:
        return "OBSERVED"
    if "traditional" in sources:
        return "TRADITIONAL"
    return "INTERPRETATION"
