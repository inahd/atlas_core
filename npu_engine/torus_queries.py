"""
torus_queries.py — Spatial queries on the 108-pada torus knot (2,3).

Distances, cross-ribbon neighbors, triangle scoring.
All geometry comes from the graph (pada entities with knot_x/y/z).
"""

import math
from typing import Dict, List, Optional, Tuple


def _knot_pos(attrs: dict) -> Tuple[float, float, float]:
    """Extract (x, y, z) from entity attributes."""
    x = float((attrs.get("knot_x", ["0"]))[0])
    y = float((attrs.get("knot_y", ["0"]))[0])
    z = float((attrs.get("knot_z", ["0"]))[0])
    return x, y, z


def torus_knot_distance(pada_a: str, pada_b: str, metadata: dict) -> float:
    """Euclidean distance between two padas in torus knot space."""
    a = metadata.get(pada_a, {}).get("attributes", {})
    b = metadata.get(pada_b, {}).get("attributes", {})
    ax, ay, az = _knot_pos(a)
    bx, by, bz = _knot_pos(b)
    return math.sqrt((ax - bx)**2 + (ay - by)**2 + (az - bz)**2)


def find_pada_for_nakshatra(nakshatra: str, metadata: dict, pada_n: int = 1) -> str:
    """Find the pada entity_id for a given nakshatra and pada number."""
    pada_n_str = str(pada_n)
    for eid, meta in metadata.items():
        if not eid.startswith("pada_"):
            continue
        attrs = meta.get("attributes", {})
        if nakshatra in attrs.get("nakshatra", []) and pada_n_str in attrs.get("pada_n", []):
            return eid
    return ""


def nearest_padas_cross_ribbon(nakshatra: str, metadata: dict, k: int = 5) -> List[Dict]:
    """Find k nearest padas on the OPPOSITE ribbon, sorted by torus distance.

    Returns list of {pada_id, nakshatra, pada_n, distance, element}.
    """
    source_pada = find_pada_for_nakshatra(nakshatra, metadata)
    if not source_pada:
        return []

    source_attrs = metadata[source_pada].get("attributes", {})
    source_ribbon = (source_attrs.get("ribbon", ["matter"]))[0]

    candidates = []
    for eid, meta in metadata.items():
        if not eid.startswith("pada_"):
            continue
        attrs = meta.get("attributes", {})
        ribbon = (attrs.get("ribbon", [""]))[0]
        if ribbon == source_ribbon:
            continue
        dist = torus_knot_distance(source_pada, eid, metadata)
        candidates.append({
            "pada_id": eid,
            "nakshatra": (attrs.get("nakshatra", [""]))[0],
            "pada_n": int((attrs.get("pada_n", ["1"]))[0]),
            "distance": round(dist, 4),
            "element": (attrs.get("element", [""]))[0],
        })

    candidates.sort(key=lambda x: x["distance"])
    return candidates[:k]


def score_entity_against_triangle(entity_id: str, triangle_id: str, metadata: dict, graph) -> float:
    """Score how coherent an entity is with a yantra triangle (0.0-1.0).

    Checks:
    - Is the entity's nakshatra a vertex of the triangle? (+0.5)
    - Does the entity's element match the triangle's dominant element? (+0.3)
    - Is the entity on the same ribbon polarity? (+0.2)
    """
    score = 0.0
    yt_id = f"yantra_{triangle_id}" if not triangle_id.startswith("yantra_") else triangle_id

    # Get triangle vertex nakshatras
    tri_naks = set()
    for edge in graph.get_neighbors(yt_id):
        if edge["relation"] == "triangle_vertex":
            to_meta = metadata.get(edge["to_id"], {})
            tri_naks.add(to_meta.get("name", ""))

    # Get entity's nakshatra
    ent_meta = metadata.get(entity_id, {})
    ent_attrs = ent_meta.get("attributes", {})
    ent_nak = (ent_attrs.get("nakshatra", [""]))[0]
    if not ent_nak:
        ent_nak = ent_meta.get("name", "")

    if ent_nak in tri_naks:
        score += 0.5

    # Element alignment
    ent_elem = (ent_attrs.get("element", [""]))[0]
    if ent_elem:
        # Check if any vertex pada shares this element
        for eid, meta in metadata.items():
            if not eid.startswith("pada_"):
                continue
            a = meta.get("attributes", {})
            if (a.get("yantra_triangle_id", [""]))[0] == triangle_id:
                if (a.get("element", [""]))[0] == ent_elem:
                    score += 0.3
                    break

    # Polarity alignment
    yt_meta = metadata.get(yt_id, {})
    yt_polarity = (yt_meta.get("attributes", {}).get("polarity", [""]))[0]
    ent_polarity = (ent_attrs.get("yantra_polarity", [""]))[0]
    if ent_polarity and ent_polarity == yt_polarity:
        score += 0.2

    return min(score, 1.0)


def torus_context_for_entity(nakshatra: str, metadata: dict, graph) -> dict:
    """Full torus context for an entity: position, yantra, cross-ribbon, co-triangulars."""
    pada_id = find_pada_for_nakshatra(nakshatra, metadata)
    if not pada_id:
        return {}

    attrs = metadata[pada_id].get("attributes", {})
    x, y, z = _knot_pos(attrs)
    triangle_id = (attrs.get("yantra_triangle_id", [""]))[0]
    ribbon = (attrs.get("ribbon", [""]))[0]
    polarity = (attrs.get("yantra_polarity", [""]))[0]
    yuga = (attrs.get("yantra_yuga", [""]))[0]

    # Co-triangulars
    co_naks = []
    if triangle_id:
        yt_id = f"yantra_{triangle_id}"
        for edge in graph.get_neighbors(yt_id):
            if edge["relation"] == "triangle_vertex":
                to_name = metadata.get(edge["to_id"], {}).get("name", "")
                if to_name and to_name != nakshatra:
                    co_naks.append(to_name)

    # Diameter pair
    opp_pada = (attrs.get("opposite_pada", [""]))[0]
    opp_nak = ""
    if opp_pada:
        opp_attrs = metadata.get(opp_pada, {}).get("attributes", {})
        opp_nak = (opp_attrs.get("nakshatra", [""]))[0]

    # Cross-ribbon nearest
    cross = nearest_padas_cross_ribbon(nakshatra, metadata, k=3)

    from .field_to_sound import VASTU_COMPASS
    compass = VASTU_COMPASS.get(triangle_id, "")

    return {
        "torus_position": {"x": x, "y": y, "z": z, "knot_y": y, "ribbon": ribbon},
        "yantra": {
            "triangle": triangle_id,
            "polarity": polarity,
            "yuga": yuga,
            "compass": compass,
        },
        "co_triangulars": co_naks,
        "diameter_pair": opp_nak,
        "nearest_cross_ribbon": [
            {"nakshatra": c["nakshatra"], "distance": c["distance"], "element": c["element"]}
            for c in cross
        ],
    }
