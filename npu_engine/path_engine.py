"""
path_engine.py — Meaningful relational path traversal for Atlas.

Filters out structural noise (pada indexing, schema plumbing).
Prioritizes semantic relations (deity, element, guna, dosha).
Paths should read like insight, not schema traversal.
"""

from collections import defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple


# ── Relation filtering ────────────────────────────────────
# Structural/indexing relations — low insight value
NOISE_RELATIONS = {
    "nakshatra_has_pada", "nakshatra_pada_entity",
    "tithi_in_paksha", "tithi_index_in_paksha",
    "identity_bridge", "index_entry",
}
NOISE_PREFIXES = ("has_pada", "pada_entity", "index_")

# High-value semantic relations
MEANINGFUL_RELATIONS = {
    "nakshatra_associated_deity": 1.0,
    "nakshatra_ruling_graha": 1.0,
    "ruled_by": 0.9,
    "deity": 0.9,
    "element": 0.8,
    "guna": 0.7,
    "dosha": 0.7,
    "raga": 0.8,
    "therapeutic": 0.7,
    "body_region": 0.6,
    "vahana": 0.6,
    "weapon": 0.5,
    "associated_graha": 0.8,
    "balances": 0.7,
    "opposes": 0.7,
    "conflicts": 0.6,
}


def _is_noise(relation: str) -> bool:
    """Is this relation structural noise?"""
    if relation in NOISE_RELATIONS:
        return True
    for prefix in NOISE_PREFIXES:
        if relation.startswith(prefix) or relation.endswith(prefix):
            return True
    return False


def _relation_value(relation: str) -> float:
    """Semantic importance of a relation type. 0 = noise, 1 = high value."""
    if _is_noise(relation):
        return 0.0
    # Check exact match
    if relation in MEANINGFUL_RELATIONS:
        return MEANINGFUL_RELATIONS[relation]
    # Check partial match
    for key, val in MEANINGFUL_RELATIONS.items():
        if key in relation or relation in key:
            return val * 0.8
    return 0.3  # unknown relation — modest default


def find_paths(relations: List[Dict[str, Any]],
               start: str,
               depth: int = 2,
               max_paths: int = 30,
               filter_noise: bool = True) -> List[List[Tuple[str, Optional[str], Optional[str]]]]:
    """Find meaningful paths from start entity.

    Filters out structural noise by default. Only traverses
    edges with semantic value.
    """
    # Build adjacency, filtering noise
    adj: Dict[str, List[Tuple[str, str, str, float]]] = defaultdict(list)
    for r in relations:
        from_id = r.get("from_id", "")
        to_id = r.get("to_id", "")
        rel = r.get("relation", "")
        att = r.get("attestation", "INTERPRETATION")
        if not from_id or not to_id:
            continue
        if filter_noise and _is_noise(rel):
            continue
        value = _relation_value(rel)
        adj[from_id].append((to_id, rel, att, value))

    # DFS — prefer high-value edges
    results = []

    def _dfs(node, path, visited, d):
        if len(results) >= max_paths or d == 0:
            return

        # Sort neighbors by relation value (best first)
        neighbors = sorted(adj.get(node, []), key=lambda x: -x[3])

        for neighbor, rel, att, val in neighbors:
            if neighbor in visited:
                continue
            path.append((neighbor, rel, att))
            visited.add(neighbor)

            if len(path) > 1:
                results.append(list(path))
                if len(results) >= max_paths:
                    path.pop()
                    visited.discard(neighbor)
                    return

            _dfs(neighbor, path, visited, d - 1)
            path.pop()
            visited.discard(neighbor)

    _dfs(start, [(start, None, None)], {start}, depth)

    # Deduplicate
    seen = set()
    unique = []
    for p in results:
        key = tuple(step[0] for step in p)
        if key not in seen:
            seen.add(key)
            unique.append(p)

    return unique


def rank_paths(paths: List[List[Tuple]],
               entity_scores: Optional[Dict[str, float]] = None,
               top_n: int = 5) -> List[List[Tuple]]:
    """Rank paths by semantic importance, diversity, and coherence.

    Returns top_n most meaningful paths.
    """
    scores = entity_scores or {}

    def _path_score(path):
        if len(path) < 2:
            return 0

        # Semantic value of relations used
        rel_value = sum(
            _relation_value(step[1]) if step[1] else 0
            for step in path[1:]
        )

        # Relation diversity bonus
        rels_used = {step[1] for step in path[1:] if step[1]}
        diversity = len(rels_used) * 0.3

        # Endpoint coherence
        endpoint = path[-1][0]
        endpoint_score = scores.get(endpoint, 0.0)

        # Attestation quality
        att_score = sum(
            0.4 if step[2] == "OBSERVED" else
            0.3 if step[2] == "TRADITIONAL" else
            0.1
            for step in path[1:]
        )

        # Path length bonus (longer meaningful paths are more insightful)
        length_bonus = min(1.5, len(path) * 0.3)

        return rel_value + diversity + endpoint_score + att_score + length_bonus

    ranked = sorted(paths, key=_path_score, reverse=True)
    return ranked[:top_n]


def format_path(path: List[Tuple[str, Optional[str], Optional[str]]]) -> str:
    """Format a path for display. Cleans up entity names."""
    parts = []
    for i, (eid, rel, att) in enumerate(path):
        name = eid.split("_", 1)[-1].replace("_", " ") if "_" in eid else eid
        if i == 0:
            parts.append(name)
        else:
            rel_clean = (rel or "").replace("_", " ").replace("nakshatra ", "")
            att_tag = f"[{att}]" if att else ""
            parts.append(f"—({rel_clean})→ {name} {att_tag}")
    return " ".join(parts)


# ══════════════════════════════════════════════════════════════
# FLOW DETECTION — 2-step meaningful chains (A → B → C)
# ══════════════════════════════════════════════════════════════

# What B connects to conceptually (relation → domain label)
_FLOW_DOMAINS = {
    "nakshatra_associated_deity": "governance",
    "nakshatra_ruling_graha": "planetary",
    "ruled_by": "authority",
    "deity": "divine",
    "associated_graha": "planetary",
    "element": "elemental",
    "dosha": "constitutional",
    "guna": "quality",
    "raga": "sonic",
    "therapeutic": "healing",
    "balances": "balance",
    "opposes": "tension",
}


def detect_flows(relations: List[Dict[str, Any]],
                 start: str,
                 entity_scores: Optional[Dict[str, float]] = None,
                 top_n: int = 3) -> List[Dict[str, Any]]:
    """Detect meaningful 2-step flows: A → B → C.

    Prefers chains where B is high-coherence and both relations
    are semantically meaningful. Returns formatted flow dicts.

    Args:
        relations: edge list
        start: starting entity_id
        entity_scores: {entity_id: coherence_score} for ranking
        top_n: max flows returned

    Returns:
        [{"chain": [A, B, C], "relations": [rel1, rel2],
          "domains": [d1, d2], "score": float, "text": str}, ...]
    """
    scores = entity_scores or {}

    # Build bidirectional adjacency (meaningful only)
    adj: Dict[str, List[Tuple[str, str, str]]] = defaultdict(list)
    for r in relations:
        rel = r.get("relation", "")
        if _is_noise(rel):
            continue
        from_id = r.get("from_id", "")
        to_id = r.get("to_id", "")
        att = r.get("attestation", "INTERPRETATION")
        if from_id and to_id:
            adj[from_id].append((to_id, rel, att))
            # Reverse edge: B can reach back toward siblings via shared governance
            if not r.get("inverse"):
                adj[to_id].append((from_id, f"inv_{rel}", att))

    # Also try entity attributes as implicit semantic links
    # (deity_varuna → "water" via element attribute)
    try:
        from .graph_engine import GraphEngine
        _g = GraphEngine()
        # For each node reachable from start in 1 hop, add attribute edges
        for b_id, _, _ in adj.get(start, []):
            meta = _g.meta(b_id)
            attrs = meta.get("attributes", {})
            for attr_key in ("element", "dosha", "domain"):
                vals = attrs.get(attr_key, [])
                if isinstance(vals, list) and vals:
                    val = str(vals[0]).lower()
                elif isinstance(vals, str) and vals:
                    val = vals.lower()
                else:
                    continue
                adj[b_id].append((val, attr_key, "SYNTHESIS"))
    except Exception:
        pass

    # Find all 2-step chains from start
    flows = []
    for b_id, rel1, att1 in adj.get(start, []):
        if rel1.startswith("inv_"):
            continue  # don't start flows on inverse edges
        val1 = _relation_value(rel1)
        if val1 < 0.3:
            continue

        for c_id, rel2, att2 in adj.get(b_id, []):
            if c_id == start:
                continue  # no boomerangs
            if rel2.startswith("inv_") and c_id == start:
                continue
            val2 = _relation_value(rel2) if not rel2.startswith("inv_") else _relation_value(rel2[4:]) * 0.6
            if val2 < 0.2:
                continue

            # Score: relation value + B coherence + diversity
            b_score = scores.get(b_id, 0.0)
            c_score = scores.get(c_id, 0.0)
            domain1 = _FLOW_DOMAINS.get(rel1, "")
            domain2 = _FLOW_DOMAINS.get(rel2, "")
            diversity = 0.3 if domain1 != domain2 else 0.0

            flow_score = val1 + val2 + b_score * 0.5 + c_score * 0.3 + diversity

            # Format names
            a_name = _eid_name(start)
            b_name = _eid_name(b_id)
            c_name = _eid_name(c_id)
            text = f"{a_name} → {b_name} → {c_name}"

            flows.append({
                "chain": [start, b_id, c_id],
                "relations": [rel1, rel2],
                "domains": [domain1, domain2],
                "score": round(flow_score, 3),
                "text": text,
            })

    # Deduplicate by chain
    seen = set()
    unique = []
    for f in flows:
        key = tuple(f["chain"])
        if key not in seen:
            seen.add(key)
            unique.append(f)

    unique.sort(key=lambda f: f["score"], reverse=True)
    return unique[:top_n]


def _eid_name(eid: str) -> str:
    """Short display name from entity_id."""
    if "_" in eid:
        return eid.split("_", 1)[-1].replace("_", " ")
    return eid


# ══════════════════════════════════════════════════════════════
# RELATION PRIORITY — limit governance to readable counts
# ══════════════════════════════════════════════════════════════

def prioritize_relations(relations: List[Dict[str, Any]],
                         entity_scores: Optional[Dict[str, float]] = None
                         ) -> Dict[str, List[Dict]]:
    """Group and limit relations to prevent information overload.

    Returns:
        {
          "primary_deity": [max 2],
          "ruling_graha": [max 1],
          "element": [max 1],
          "secondary": [rest],
        }
    """
    scores = entity_scores or {}

    deity_rels = []
    graha_rels = []
    element_rels = []
    secondary = []

    DEITY_TYPES = {"nakshatra_associated_deity", "deity"}
    GRAHA_TYPES = {"nakshatra_ruling_graha", "ruling_graha", "associated_graha", "ruled_by"}
    ELEMENT_TYPES = {"element", "dosha", "guna"}

    for r in relations:
        rel = r.get("relation", "")
        if _is_noise(rel):
            continue

        # Score for sorting: target coherence + relation value
        target = r.get("to_id", "")
        sort_score = scores.get(target, 0) + _relation_value(rel)
        r["_priority_score"] = sort_score

        if rel in DEITY_TYPES:
            deity_rels.append(r)
        elif rel in GRAHA_TYPES:
            graha_rels.append(r)
        elif rel in ELEMENT_TYPES:
            element_rels.append(r)
        else:
            secondary.append(r)

    # Sort each group by priority
    deity_rels.sort(key=lambda r: r.get("_priority_score", 0), reverse=True)
    graha_rels.sort(key=lambda r: r.get("_priority_score", 0), reverse=True)
    element_rels.sort(key=lambda r: r.get("_priority_score", 0), reverse=True)
    secondary.sort(key=lambda r: r.get("_priority_score", 0), reverse=True)

    return {
        "primary_deity": deity_rels[:2],
        "ruling_graha": graha_rels[:1],
        "element": element_rels[:1],
        "secondary": secondary[:5],
    }
