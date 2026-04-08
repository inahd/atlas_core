"""
build_field_state.py — The single pipeline entry point for FieldState.

This is the ONLY place that orchestrates:
  toroid → graph → coherence rerank → geometry → lifecycle → psi

No other module may call these components directly for field computation.

Pipeline:
  1. θ, φ from ToroidalField (unchanged 2-axis math)
  2. field_query → geometric entity ranking
  3. enrich entities with metadata (element, guna, name)
  4. relation expansion + relational scoring via GraphEngine
  5. composite rerank via CoherenceEngineV2
  6. extract active_relations among top entities
  7. formation detection via TempleGeometry
  8. lifecycle from arc_phase + formations
  9. ψ and optional embedding modulation
"""

from typing import Any, Dict, List, Optional, Tuple

from .field_state import FieldState


def _enrich_entity(entity: Dict[str, Any],
                   metadata: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Add element, guna, name from entity metadata."""
    eid = entity.get("entity_id", "")
    meta = metadata.get(eid, {})
    attrs = meta.get("attributes", {})

    enriched = dict(entity)

    if "element" not in enriched:
        elem_vals = attrs.get("element", [])
        if isinstance(elem_vals, list) and elem_vals:
            enriched["element"] = elem_vals[0].lower()
        elif isinstance(elem_vals, str) and elem_vals:
            enriched["element"] = elem_vals.lower()
        else:
            enriched["element"] = "ether"

    if "guna" not in enriched:
        guna_vals = attrs.get("guna", [])
        if isinstance(guna_vals, list) and guna_vals:
            enriched["guna"] = guna_vals[0].lower()
        elif isinstance(guna_vals, str) and guna_vals:
            enriched["guna"] = guna_vals.lower()
        else:
            enriched["guna"] = "sattva"

    if "name" not in enriched:
        enriched["name"] = meta.get("name", eid)

    return enriched


def _detect_soft_formations(entities: List[Dict], relations: List[Dict]) -> List[Dict]:
    """Detect soft formations beyond strict geometric symmetry.

    Finds:
      - element clusters: 3+ top entities sharing an element
      - governance triads: entity → deity → graha chains
      - relation chains: 3+ entities connected by the same relation type

    Tags: "cluster", "triad", "chain". Does not invent relations.
    """
    formations = []
    top = entities[:20]
    if len(top) < 3:
        return formations

    # ── Element clusters ──────────────────────────────────
    from collections import Counter
    elem_groups: Dict[str, List[str]] = {}
    for e in top:
        elem = e.get("element", "ether")
        elem_groups.setdefault(elem, []).append(e.get("entity_id", ""))

    for elem, members in elem_groups.items():
        if len(members) >= 3:
            formations.append({
                "name": f"{elem}_cluster",
                "type": "cluster",
                "count": len(members),
                "members": members[:12],
                "symmetry_score": round(min(1.0, len(members) / 10), 3),
                "attestation": "SYNTHESIS",
                "description": f"{len(members)} entities share {elem} element",
            })

    # ── Governance triads: entity → deity/graha ───────────
    GOVERNANCE_RELS = {"nakshatra_associated_deity", "nakshatra_ruling_graha",
                       "ruled_by", "deity", "associated_graha"}
    top_ids = {e.get("entity_id") for e in top}

    # Find entities that share a common governance target
    gov_targets: Dict[str, List[str]] = {}  # target_id → [source_ids]
    for r in relations:
        rel = r.get("relation", "")
        if rel not in GOVERNANCE_RELS:
            continue
        from_id = r.get("from_id", "")
        to_id = r.get("to_id", "")
        if from_id in top_ids:
            gov_targets.setdefault(to_id, []).append(from_id)

    for target, sources in gov_targets.items():
        if len(sources) >= 2:
            members = list(set(sources + [target]))
            formations.append({
                "name": f"triad_{target.split('_')[-1]}" if '_' in target else f"triad_{target}",
                "type": "triad",
                "count": len(members),
                "members": members,
                "symmetry_score": round(min(1.0, len(sources) / 4), 3),
                "attestation": "SYNTHESIS",
                "description": f"{len(sources)} entities governed by {target.replace('_', ' ')}",
            })

    # ── Relation chains: same relation type connecting 3+ ─
    rel_chains: Dict[str, List[str]] = {}  # relation_type → [entity_ids involved]
    NOISE = {"nakshatra_has_pada", "nakshatra_pada_entity", "tithi_in_paksha",
             "tithi_index_in_paksha", "identity_bridge"}
    for r in relations:
        rel = r.get("relation", "")
        if rel in NOISE:
            continue
        from_id = r.get("from_id", "")
        to_id = r.get("to_id", "")
        chain = rel_chains.setdefault(rel, set())
        if from_id in top_ids:
            chain.add(from_id)
        if to_id in top_ids:
            chain.add(to_id)

    for rel, members in rel_chains.items():
        if len(members) >= 3:
            member_list = list(members)
            formations.append({
                "name": f"chain_{rel.replace('_', ' ')[:20]}",
                "type": "chain",
                "count": len(member_list),
                "members": member_list[:12],
                "symmetry_score": round(min(1.0, len(member_list) / 6), 3),
                "attestation": "SYNTHESIS",
                "description": f"{len(member_list)} entities linked by {rel.replace('_', ' ')}",
            })

    return formations


def build_field_state(panchanga: Dict[str, Any],
                      field,              # ToroidalField
                      temple,             # TempleGeometry
                      graph=None,         # GraphEngine (optional)
                      vector_store=None,  # VectorStore (optional, for modulation only)
                      top_n: int = 64) -> FieldState:
    """Build a complete FieldState. Single pipeline entry point.

    With graph=None, behaves like the original (geometric-only ranking).
    With graph provided, adds relational scoring + active relations.
    With vector_store, adds bounded semantic modulation (±0.05).
    """

    # ── 1. Toroidal coordinates (θ=time, φ=quality) ──────────
    theta, phi = field.moment_to_coords(panchanga)

    # ── 2. Geometric entity ranking ──────────────────────────
    raw_entities = field.field_query(panchanga, top_n=top_n)

    # ── 3. Enrich with metadata ──────────────────────────────
    metadata = getattr(field, 'entity_metadata', {})
    entities = [_enrich_entity(e, metadata) for e in raw_entities]

    # ── 4-5. Relational expansion + composite rerank ─────────
    active_relations = []
    if graph is not None:
        from .coherence_engine_v2 import rerank_entities, extract_active_relations
        from .modulation_engine import semantic_modulation

        # Optional semantic modulation
        sem_scores = {}
        if vector_store is not None:
            nak = panchanga.get("nakshatra", "")
            elem = panchanga.get("element", "")
            query = f"{nak} {elem}".strip()
            entity_ids = [e["entity_id"] for e in entities]
            sem_scores = semantic_modulation(entity_ids, query, vector_store)

        entities = rerank_entities(entities, graph,
                                   seed_count=8,
                                   semantic_scores=sem_scores)
        active_relations = extract_active_relations(entities, graph, top_n=10)
    else:
        # No graph — keep geometric order, add placeholder scores
        for ent in entities:
            ent["geometric_score"] = ent.get("score", 0.0)
            ent["composite_score"] = ent.get("score", 0.0)

    # ── 6. Sacred geometry + soft cluster detection ──────────
    formations = temple.detect_formations(entities)
    # Add soft formations: element clusters, relation chains, governance triads
    formations.extend(_detect_soft_formations(entities, active_relations))
    vastu_grid = temple.vastu_grid(entities)

    # ── 6b. Vāstu S4 state (deterministic, S3→S4) ───────────
    from .vastu_engine import derive_vastu_state
    vastu_state = derive_vastu_state(
        panchanga=panchanga,
        entities=entities,
        active_relations=active_relations,
        formations=formations,
        theta=theta,
        phi=phi,
    )

    # ── 7. Arc phase ─────────────────────────────────────────
    arc_phase = panchanga.get("arc_phase", 0.0)
    if not arc_phase:
        tidx = panchanga.get("tithi_num", 1)
        arc_phase = round(tidx / 30.0, 3)

    # ── 8. Lifecycle ─────────────────────────────────────────
    from .lifecycle_engine import compute_lifecycle
    lifecycle = compute_lifecycle(arc_phase, formations)

    # ── 9. ψ expression axis ─────────────────────────────────
    from .modulation_engine import derive_psi
    psi = derive_psi(entities, arc_phase, formations)

    # ── 10. UI layout (interface projection of field state) ──
    from .ui_vastu_engine import derive_ui_layout
    _fs_dict = {
        "panchanga": panchanga,
        "theta": theta, "phi": phi,
        "entities": entities,
        "active_relations": active_relations,
        "formations": formations,
        "vastu_state": vastu_state,
        "lifecycle": lifecycle,
        "arc_phase": arc_phase,
        "psi": psi,
        "sound_state": panchanga,  # pass through for layer weight heuristics
    }
    ui_layout = derive_ui_layout(_fs_dict)

    return FieldState(
        panchanga=panchanga,
        theta=theta,
        phi=phi,
        entities=entities,
        active_relations=active_relations,
        formations=formations,
        vastu_grid=vastu_grid,
        vastu_state=vastu_state,
        ui_layout=ui_layout,
        lifecycle=lifecycle,
        arc_phase=arc_phase,
        psi=psi,
        modulation={},
    )


def apply_modulation(state: FieldState,
                     cluster_engine) -> FieldState:
    """Apply cluster engine modulation. Writes only state.modulation."""
    if not state.entities:
        return state
    top_id = state.top_entity_id()
    if not top_id:
        return state
    profile = cluster_engine.control_profile(top_id, cycle_phase=state.arc_phase)
    state.modulation = profile
    return state


# ── Convenience: unified query function ──────────────────────

def query_field_state(panchanga: Dict[str, Any],
                      top_n: int = 64,
                      depth: int = 2) -> Dict[str, Any]:
    """One-call query: panchanga → full field state as dict.

    Initializes all engines internally. For scripts and testing.
    """
    from .toroidal_field import ToroidalField
    from .temple_geometry import TempleGeometry
    from .graph_engine import GraphEngine

    field = ToroidalField()
    temple = TempleGeometry()
    graph = GraphEngine()

    # Try vector store (optional)
    vs = None
    try:
        from .vector_store import get_vector_store
        vs = get_vector_store()
    except Exception:
        pass

    state = build_field_state(panchanga, field, temple, graph, vs, top_n=top_n)

    return {
        "theta": state.theta,
        "phi": state.phi,
        "entities": state.entities,
        "active_relations": state.active_relations,
        "formations": state.formations,
        "lifecycle": state.lifecycle,
        "arc_phase": state.arc_phase,
        "psi": state.psi,
        "modulation": state.modulation,
        "summary": state.summary(),
    }
