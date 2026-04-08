"""
codex_interaction.py — Localized Codex generation from selected entities.

Thin bridge: selected entity → local subgraph → Codex artifact.

No freeform prompts. No invented relations. No field recomputation.
"""

from typing import Any, Dict, List, Optional, Tuple

from .codex_engine import generate


def codex_from_entity(state: Dict[str, Any],
                      entity_id: str,
                      mode: str = "brief",
                      config: Optional[Dict] = None) -> str:
    """Generate a Codex artifact from a single entity's neighborhood.

    Filters field_state to the local relational cluster around entity_id,
    then calls the standard Codex engine on the localized state.
    """
    entities = state.get("entities") or []
    relations = state.get("active_relations") or []

    # Find anchor
    anchor = None
    for e in entities:
        if e.get("entity_id") == entity_id:
            anchor = e
            break

    # If not in entities, check if it appears in relation endpoints
    if anchor is None:
        for r in relations:
            if r.get("from_id") == entity_id or r.get("to_id") == entity_id:
                anchor = {"entity_id": entity_id, "score": 0, "composite_score": 0,
                          "element": "ether", "guna": "sattva", "name": entity_id,
                          "attestation": "INTERPRETATION"}
                break

    if anchor is None:
        return f"Entity '{entity_id}' not found in current field state.\n"

    # Local relations: edges touching this entity
    local_rels = [
        r for r in relations
        if r.get("from_id") == entity_id or r.get("to_id") == entity_id
    ]

    # Local entity ids: anchor + all relation endpoints
    local_ids = {entity_id}
    for r in local_rels:
        local_ids.add(r.get("from_id", ""))
        local_ids.add(r.get("to_id", ""))
    local_ids.discard("")

    # Local entities: anchor first, then neighbors from the ranked list
    local_ents = [anchor]
    for e in entities:
        eid = e.get("entity_id")
        if eid in local_ids and eid != entity_id:
            local_ents.append(e)

    # Build localized state (shallow copy, preserve global context)
    local_state = dict(state)
    local_state["entities"] = local_ents
    local_state["active_relations"] = local_rels

    return generate(local_state, mode=mode, config=config or {})


def codex_from_cluster(state: Dict[str, Any],
                       entity_ids: List[str],
                       mode: str = "cluster",
                       config: Optional[Dict] = None) -> str:
    """Generate a Codex artifact from a cluster of entities.

    Selects all matching entities and their mutual relations.
    """
    if not entity_ids:
        return "No entity IDs provided.\n"

    entities = state.get("entities") or []
    relations = state.get("active_relations") or []
    id_set = set(entity_ids)

    # Select matching entities, preserving field order
    local_ents = [e for e in entities if e.get("entity_id") in id_set]

    if not local_ents:
        return f"None of the requested entities found in current field state.\n"

    # Select relations where both endpoints are in the cluster
    # plus relations where at least one endpoint is in the cluster
    local_rels = [
        r for r in relations
        if r.get("from_id") in id_set or r.get("to_id") in id_set
    ]

    local_state = dict(state)
    local_state["entities"] = local_ents
    local_state["active_relations"] = local_rels

    return generate(local_state, mode=mode, config=config or {})


def paths_from_entity(state: Dict[str, Any],
                      entity_id: str,
                      depth: int = 2) -> List[List[Tuple[str, Optional[str], Optional[str]]]]:
    """Find relational paths from an entity through the field graph.

    Uses active_relations from field_state + graph expansion.
    Returns ranked list of paths.
    Each path: [(entity_id, relation, attestation), ...].
    """
    from .path_engine import find_paths, rank_paths
    from .graph_engine import GraphEngine

    relations = list(state.get("active_relations") or [])

    # Expand from graph engine for richer traversal
    try:
        graph = GraphEngine()
        expanded = graph.expand_from_entities([entity_id], depth=depth, max_per_node=20)
        existing = {(r.get("from_id"), r.get("relation"), r.get("to_id")) for r in relations}
        for r in expanded:
            key = (r.get("from_id"), r.get("relation"), r.get("to_id"))
            if key not in existing:
                relations.append(r)
    except Exception:
        pass

    paths = find_paths(relations, entity_id, depth=depth)

    scores = {e.get("entity_id", ""): e.get("composite_score", e.get("score", 0))
              for e in (state.get("entities") or [])}

    return rank_paths(paths, scores)
