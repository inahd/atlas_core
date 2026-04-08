"""
igpu.py — Atlas iGPU: relational rendering engine.

Converts field_state into renderable spatial/visual state.
Framework-independent — produces data, not pixels.

Does NOT:
  - compute coherence
  - modify entities
  - invent relations

Pipeline:
  field_state → projection → layout → render_mapping → RenderState
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

TAU = math.tau


# ══════════════════════════════════════════════════════════════
# RENDER STATE — the output object
# ══════════════════════════════════════════════════════════════

@dataclass
class RenderNode:
    id: str
    name: str
    x: float
    y: float
    z: float                     # 0 for 2D projections
    size: float                  # 0..1, from composite_score
    color: Tuple[int, int, int]  # RGB from element
    alpha: float                 # opacity from score + attestation
    attestation: str
    element: str
    guna: str
    pinned: bool = False
    group: int = -1              # formation/cluster id, -1 = none
    role: str = "free"           # "center" | "orbit" | "bridge" | "free"
    motion: str = "static"       # "stable" | "orbit" | "oscillate" | "static"


@dataclass
class RenderFlow:
    """2-step relational flow: A → via B → C."""
    source: str
    via: str
    target: str
    relations: Tuple[str, str]
    strength: float              # combined score 0..1
    domains: Tuple[str, str]
    # Spatial: set by resolve_flow_positions after node layout
    sx: float = 0.0             # source x
    sy: float = 0.0             # source y
    vx: float = 0.0             # via x (control point for curve)
    vy: float = 0.0             # via y
    tx: float = 0.0             # target x
    ty: float = 0.0             # target y     # semantic domain labels


@dataclass
class RenderEdge:
    source: str                  # entity_id
    target: str                  # entity_id
    relation: str
    attestation: str
    style: str                   # "solid" | "dashed" | "dotted"
    width: float                 # 0..1
    alpha: float                 # 0..1
    mutual: bool = False


@dataclass
class RenderFormation:
    name: str
    center_x: float
    center_y: float
    radius: float
    member_ids: List[str]
    symmetry: float
    style: str                   # "ring" | "hex" | "grid"


@dataclass
class RenderState:
    """Complete renderable snapshot. Any UI/canvas can consume this."""
    nodes: List[RenderNode]
    edges: List[RenderEdge]
    flows: List[RenderFlow]
    formations: List[RenderFormation]
    lifecycle_phase: str         # birth | formation | dissolution | pralaya
    lifecycle_intensity: float   # 0..1
    psi_intensity: float
    psi_focus: float
    psi_stability: float
    projection: str              # "plane" | "hex" | "toroid"
    bounds: Tuple[float, float, float, float]  # min_x, min_y, max_x, max_y


# ══════════════════════════════════════════════════════════════
# ELEMENT → VISUAL MAPPING (canon-derived, not inferred)
# ══════════════════════════════════════════════════════════════

ELEMENT_RGB = {
    "fire":  (255, 100, 30),
    "water": (30, 100, 255),
    "earth": (139, 100, 20),
    "air":   (0, 200, 255),
    "ether": (200, 169, 110),
}

ATTESTATION_STYLE = {
    "OBSERVED":       {"edge": "solid",  "alpha": 0.85, "width": 0.8},
    "TRADITIONAL":    {"edge": "solid",  "alpha": 0.65, "width": 0.6},
    "SYNTHESIS":      {"edge": "dashed", "alpha": 0.45, "width": 0.5},
    "INTERPRETATION": {"edge": "dotted", "alpha": 0.25, "width": 0.35},
}

FORMATION_STYLE = {
    "chatushkona":       "grid",
    "shatkona":          "hex",
    "ashtadala":         "ring",
    "navagraha":         "ring",
    "shodasha":          "ring",
    "nakshatra_mandala": "ring",
    "vastu_pada":        "grid",
}


# ══════════════════════════════════════════════════════════════
# PROJECTIONS
# ══════════════════════════════════════════════════════════════

def project_plane(theta: float, phi: float,
                  scale: float = 300.0) -> Tuple[float, float, float]:
    """Flat 2D projection. θ → x, φ → y."""
    x = (theta / TAU) * scale * 2 - scale
    y = (phi / TAU) * scale - scale * 0.5
    return (x, y, 0.0)


def project_toroid(theta: float, phi: float,
                   R: float = 250.0, r: float = 90.0) -> Tuple[float, float, float]:
    """3D toroid surface → 2D screen via perspective."""
    # Full 3D coords
    x3 = (R + r * math.cos(phi)) * math.cos(theta)
    y3 = (R + r * math.cos(phi)) * math.sin(theta)
    z3 = r * math.sin(phi)
    # Simple perspective: project onto xz plane with y as depth
    depth = 1.0 / (1.0 + max(0, y3 / (R * 2)))
    sx = x3 * depth
    sy = z3 * depth * 0.8  # slight vertical compression
    return (sx, sy, y3)


def project_hex(theta: float, phi: float,
                width: int = 27, height: int = 21,
                cell_size: float = 24.0) -> Tuple[float, float, float]:
    """Hex grid projection using existing hex_projection math."""
    theta_norm = (theta % TAU) / TAU
    phi_norm = (phi % TAU) / TAU

    # Map to grid coordinates
    gx = theta_norm * width
    gy = phi_norm * height

    # Flat-top axial hex conversion
    q = (2.0 / 3.0) * gx
    r_ax = (-1.0 / 3.0) * gx + (math.sqrt(3.0) / 3.0) * gy

    # Axial to pixel (flat-top)
    px = cell_size * (3.0 / 2.0 * q)
    py = cell_size * (math.sqrt(3.0) * (r_ax + q / 2.0))

    # Center the grid
    cx = cell_size * (3.0 / 2.0 * width / 3.0)
    cy = cell_size * (math.sqrt(3.0) * height / 3.0)

    return (px - cx, py - cy, 0.0)


def project_4d(theta: float, phi: float,
               t: float = 0.0,
               R: float = 250.0, r: float = 90.0) -> Tuple[float, float, float]:
    """4D torus projection — theta rotates with time parameter t.

    At t=0, identical to project_toroid.
    Advancing t rotates the theta axis, revealing the 4th dimension
    as temporal flow through the toroidal field.
    """
    theta_4d = theta + t * TAU
    return project_toroid(theta_4d, phi, R, r)


PROJECTIONS = {
    "plane":  project_plane,
    "toroid": project_toroid,
    "hex":    project_hex,
    "4d":     project_4d,
}


# ══════════════════════════════════════════════════════════════
# LAYOUT ENGINE
# ══════════════════════════════════════════════════════════════

def layout_nodes(entities: List[Dict[str, Any]],
                 projection: str = "plane",
                 formations: Optional[List[Dict]] = None,
                 t: float = 0.0
                 ) -> List[RenderNode]:
    """Position nodes from projection, group by formations."""
    proj_fn = PROJECTIONS.get(projection, project_plane)
    formation_members = {}  # entity_id → formation_index

    if formations:
        for fi, f in enumerate(formations):
            for mid in f.get("members", []):
                formation_members[mid] = fi

    nodes = []
    for e in entities:
        theta = e.get("theta", 0.0)
        phi = e.get("phi", 0.0)
        # 4D projection accepts t parameter
        if projection == "4d":
            x, y, z = proj_fn(theta, phi, t=t)
        else:
            x, y, z = proj_fn(theta, phi)

        comp = e.get("composite_score", e.get("score", 0.0))
        elem = e.get("element", "ether")
        att = e.get("attestation", "INTERPRETATION")
        att_style = ATTESTATION_STYLE.get(att, ATTESTATION_STYLE["INTERPRETATION"])

        nodes.append(RenderNode(
            id=e.get("entity_id", ""),
            name=(e.get("name") or e.get("entity_id", "")).replace("_", " "),
            x=x, y=y, z=z,
            size=max(0.05, min(1.0, comp)),
            color=ELEMENT_RGB.get(elem, ELEMENT_RGB["ether"]),
            alpha=max(0.1, min(1.0, 0.2 + comp * 0.6 + att_style["alpha"] * 0.2)),
            attestation=att,
            element=elem,
            guna=e.get("guna", "sattva"),
            group=formation_members.get(e.get("entity_id"), -1),
        ))

    return nodes


def layout_edges(relations: List[Dict[str, Any]]) -> List[RenderEdge]:
    """Map relations to renderable edges with attestation-based styling."""
    edges = []
    for r in relations:
        att = r.get("attestation", "INTERPRETATION")
        att_style = ATTESTATION_STYLE.get(att, ATTESTATION_STYLE["INTERPRETATION"])

        edges.append(RenderEdge(
            source=r.get("from_id", ""),
            target=r.get("to_id", ""),
            relation=r.get("relation", ""),
            attestation=att,
            style=att_style["edge"],
            width=att_style["width"],
            alpha=att_style["alpha"],
            mutual=bool(r.get("mutual")),
        ))

    return edges


def layout_formations(formations: List[Dict[str, Any]],
                      node_map: Dict[str, RenderNode]
                      ) -> List[RenderFormation]:
    """Compute formation center/radius from member node positions."""
    results = []
    for f in formations:
        members = f.get("members", [])
        if len(members) < 3:
            continue

        # Compute centroid from member positions
        xs, ys = [], []
        for mid in members:
            n = node_map.get(mid)
            if n:
                xs.append(n.x)
                ys.append(n.y)

        if len(xs) < 3:
            continue

        cx = sum(xs) / len(xs)
        cy = sum(ys) / len(ys)
        radius = max(30.0, max(
            math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            for x, y in zip(xs, ys)
        ) * 1.2)

        name = f.get("name", "organic")
        results.append(RenderFormation(
            name=name,
            center_x=cx,
            center_y=cy,
            radius=radius,
            member_ids=members,
            symmetry=f.get("symmetry_score", 0),
            style=FORMATION_STYLE.get(name, "ring"),
        ))

    return results


# ══════════════════════════════════════════════════════════════
# FORMATION SPATIAL ACTIVATION
# ══════════════════════════════════════════════════════════════

# Layout shapes by formation type
_FORMATION_LAYOUTS = {
    "cluster": "circle",
    "triad":   "triangle",
    "chain":   "line",
}


def _arrange_circle(cx: float, cy: float, radius: float,
                    count: int, index: int) -> Tuple[float, float]:
    """Position index-th member on a circle."""
    angle = (index / max(1, count)) * TAU
    return (cx + math.cos(angle) * radius,
            cy + math.sin(angle) * radius)


def _arrange_triangle(cx: float, cy: float, radius: float,
                      count: int, index: int) -> Tuple[float, float]:
    """Position on a triangle (3 vertices + interpolated edges)."""
    # First 3 get vertex positions, rest fill edges
    if count <= 3:
        angle = (index / 3) * TAU - math.pi / 2  # point up
    else:
        edge = index % 3
        pos_on_edge = (index // 3) / max(1, (count // 3))
        a1 = (edge / 3) * TAU - math.pi / 2
        a2 = ((edge + 1) / 3) * TAU - math.pi / 2
        angle = a1 + (a2 - a1) * pos_on_edge
    return (cx + math.cos(angle) * radius,
            cy + math.sin(angle) * radius)


def _arrange_line(cx: float, cy: float, radius: float,
                  count: int, index: int) -> Tuple[float, float]:
    """Position along a horizontal line (for chains)."""
    spread = radius * 2
    x = cx - spread / 2 + (index / max(1, count - 1)) * spread if count > 1 else cx
    return (x, cy)


_ARRANGE_FN = {
    "circle":   _arrange_circle,
    "triangle": _arrange_triangle,
    "line":     _arrange_line,
}


# ══════════════════════════════════════════════════════════════
# NODE ROLES — center / orbit / bridge
# ══════════════════════════════════════════════════════════════

def assign_roles(nodes: List[RenderNode],
                 formations: List[Dict[str, Any]],
                 relations: List[Dict[str, Any]]) -> None:
    """Assign roles to nodes based on formation membership and connectivity.

    center: highest composite_score in its formation
    bridge: belongs to a formation AND has ≥2 edges to nodes outside it
    orbit:  all other formation members
    free:   not in any formation

    Mutates nodes in place (sets .role and .motion).
    """
    node_map = {n.id: n for n in nodes}

    # Build external connection count per node
    external_of: Dict[str, int] = {}  # node_id → count of edges outside own formation

    # Map entity → formation members set
    formation_sets: Dict[int, set] = {}
    node_to_fi: Dict[str, int] = {}
    for fi, f in enumerate(formations):
        members = set(f.get("members", []))
        formation_sets[fi] = members
        for mid in members:
            node_to_fi[mid] = fi

    for r in relations:
        from_id = r.get("from_id", "")
        to_id = r.get("to_id", "")
        for src, dst in [(from_id, to_id), (to_id, from_id)]:
            if src in node_to_fi:
                fi = node_to_fi[src]
                if dst not in formation_sets.get(fi, set()):
                    external_of[src] = external_of.get(src, 0) + 1

    # Assign roles per formation
    for fi, f in enumerate(formations):
        members = f.get("members", [])
        member_nodes = [(mid, node_map[mid]) for mid in members if mid in node_map]
        if not member_nodes:
            continue

        # Center: highest score
        center_id = max(member_nodes, key=lambda x: x[1].size)[0]

        for mid, n in member_nodes:
            if mid == center_id:
                n.role = "center"
                n.motion = "stable"
            elif external_of.get(mid, 0) >= 2:
                n.role = "bridge"
                n.motion = "oscillate"
            else:
                n.role = "orbit"
                n.motion = "orbit"

    # Assign motion to free nodes (not in any formation)
    for n in nodes:
        if n.role == "free":
            if n.size > 0.6:
                n.motion = "orbit"       # high-score free nodes orbit
            elif n.size > 0.3:
                n.motion = "oscillate"   # medium nodes oscillate
            else:
                n.motion = "static"      # low-score nodes stay still


def activate_formations(nodes: List[RenderNode],
                        formations: List[Dict[str, Any]],
                        lifecycle: Dict[str, Any],
                        psi: Dict[str, float],
                        selected_id: Optional[str] = None,
                        pull_strength: float = 0.6) -> List[RenderNode]:
    """Pull formation members toward cluster centroids with shape layout.

    Does NOT detect new formations. Does NOT modify membership.
    Only repositions nodes that belong to detected formations.

    Args:
        nodes: positioned RenderNodes from layout_nodes
        formations: from field_state (NPU-detected)
        lifecycle: {phase, intensity, stability}
        psi: {intensity, focus, stability}
        selected_id: focused entity_id (its formation gets emphasis)
        pull_strength: 0..1 how strongly to pull (0=no effect, 1=full snap)
    """
    if not formations or not nodes:
        return nodes

    node_map = {n.id: n for n in nodes}

    # Lifecycle modulation
    phase = lifecycle.get("phase", "formation")
    lc_intensity = lifecycle.get("intensity", 0.5)
    psi_stability = psi.get("stability", 0.5)

    # Phase → pull modifier
    if phase == "pralaya":
        # Loosening: reduce pull, add outward drift
        phase_pull = pull_strength * 0.3
        drift = 1.4
    elif phase == "birth":
        # Forming: moderate pull, growing
        phase_pull = pull_strength * 0.7
        drift = 1.0
    elif phase == "dissolution":
        # Weakening: pull fading
        phase_pull = pull_strength * 0.5
        drift = 1.2
    else:
        # Formation: strongest pull
        phase_pull = pull_strength
        drift = 1.0

    # Stability dampens jitter
    damping = 0.5 + psi_stability * 0.5  # 0.5..1.0

    # Find which formation the selected entity belongs to
    selected_formation = -1
    if selected_id:
        for fi, f in enumerate(formations):
            if selected_id in f.get("members", []):
                selected_formation = fi
                break

    for fi, f in enumerate(formations):
        members = f.get("members", [])
        f_type = f.get("type", "cluster")
        f_name = f.get("name", "")

        # Resolve member nodes
        member_nodes = [node_map[mid] for mid in members if mid in node_map]
        if len(member_nodes) < 2:
            continue

        # Compute current centroid
        cx = sum(n.x for n in member_nodes) / len(member_nodes)
        cy = sum(n.y for n in member_nodes) / len(member_nodes)

        # Formation radius based on member count
        base_radius = 30 + len(member_nodes) * 8
        radius = base_radius * drift

        # Choose arrangement shape
        shape = _FORMATION_LAYOUTS.get(f_type, "circle")
        # Governance triads use triangle
        if "triad" in f_name:
            shape = "triangle"
        arrange_fn = _ARRANGE_FN.get(shape, _arrange_circle)

        # Focus: is this the selected formation?
        is_focused = (fi == selected_formation)
        focus_boost = 1.15 if is_focused else 1.0

        # Separate by role
        center_nodes = [n for n in member_nodes if n.role == "center"]
        orbit_nodes = [n for n in member_nodes if n.role == "orbit"]
        bridge_nodes = [n for n in member_nodes if n.role == "bridge"]

        # If no roles assigned yet, treat all as orbit
        if not center_nodes and not bridge_nodes:
            if member_nodes:
                center_nodes = [member_nodes[0]]
                orbit_nodes = member_nodes[1:]

        effective_pull = phase_pull * damping

        # ── Center: snap to centroid ──────────────────────
        for n in center_nodes:
            n.x = n.x * (1 - effective_pull) + cx * effective_pull
            n.y = n.y * (1 - effective_pull) + cy * effective_pull
            n.size = min(1.0, n.size * 1.4)  # center is larger

        # ── Orbit: arrange in circle/shape around centroid ──
        orbit_count = len(orbit_nodes)
        for i, n in enumerate(orbit_nodes):
            target_x, target_y = arrange_fn(cx, cy, radius * focus_boost,
                                            orbit_count, i)
            n.x = n.x * (1 - effective_pull) + target_x * effective_pull
            n.y = n.y * (1 - effective_pull) + target_y * effective_pull

        # ── Bridge: place between own centroid and the midpoint outward ──
        for n in bridge_nodes:
            # Bridge extends outward from centroid
            dx = n.x - cx
            dy = n.y - cy
            dist = math.sqrt(dx * dx + dy * dy) + 1e-6
            bridge_r = radius * 1.3 * focus_boost
            target_x = cx + (dx / dist) * bridge_r
            target_y = cy + (dy / dist) * bridge_r
            n.x = n.x * (1 - effective_pull * 0.5) + target_x * (effective_pull * 0.5)
            n.y = n.y * (1 - effective_pull * 0.5) + target_y * (effective_pull * 0.5)
            n.size = min(1.0, n.size * 1.1)

        # ── Focus emphasis / dimming ──────────────────────
        for n in member_nodes:
            if is_focused:
                n.size = min(1.0, n.size * (1.0 + lc_intensity * 0.15))
                n.alpha = min(1.0, n.alpha * 1.12)
            elif selected_formation >= 0:
                n.alpha = max(0.1, n.alpha * 0.75)

    return nodes


# ══════════════════════════════════════════════════════════════
# FLOW VECTORS — 2-step paths as directional render objects
# ══════════════════════════════════════════════════════════════

def _normalize_entity_id(eid: str) -> str:
    """Extract a canonical graph entity_id from a spine composite ID.

    Spine entities often have IDs like 'nakshatra_nakshatra_kritis_13'
    or 'nakshatra_pada_jyeshtha_pada_1' that don't exist in the graph.
    The graph has IDs like 'nakshatra_anuradha', 'deity_agni'.
    """
    # Already a standard category_name form? Check common prefixes.
    _CATS = ("nakshatra_", "graha_", "deity_", "devi_", "plant_", "raga_",
             "tala_", "element_", "dosha_", "marma_", "herb_")
    if any(eid.startswith(c) for c in _CATS):
        # Strip double-prefixes: nakshatra_nakshatra_kritis_13 → nakshatra_kritis_13
        # But prefer known graph forms: nakshatra_anuradha
        parts = eid.split("_")
        if len(parts) >= 3 and parts[0] == parts[1]:
            return "_".join(parts[:1] + parts[2:])
    return eid


def build_flow_vectors(state: Dict[str, Any],
                       entity_scores: Optional[Dict[str, float]] = None,
                       top_n: int = 5) -> List[RenderFlow]:
    """Build renderable flow vectors from path engine output.

    Reads active_relations, finds 2-step meaningful chains,
    returns RenderFlow objects for any canvas to draw.

    Does NOT invent relations — only traces existing edges.
    """
    relations = state.get("active_relations") or []
    entities = state.get("entities") or []
    if not entities:
        return []

    scores = entity_scores or {}
    if not scores:
        for e in entities:
            eid = e.get("entity_id", "")
            sc = e.get("composite_score", e.get("score", 0))
            scores[eid] = sc
            # Also register normalized ID so detect_flows can score via-nodes
            neid = _normalize_entity_id(eid)
            if neid != eid:
                scores[neid] = sc

    # Use path engine's flow detection
    try:
        from .path_engine import detect_flows
    except ImportError:
        return []

    # Expand relations via graph engine for 2-step chains.
    # Spine entity IDs may be composite — normalize them for graph lookup.
    expanded = list(relations)
    try:
        from .graph_engine import GraphEngine
        graph = GraphEngine()
        # Normalize spine entity IDs → graph IDs, then deduplicate
        raw_ids = [e.get("entity_id", "") for e in entities[:10] if e.get("entity_id")]
        seed_ids = list(dict.fromkeys(
            _normalize_entity_id(eid) for eid in raw_ids
        ))
        # Only keep IDs that actually have neighbors in the graph
        seed_ids = [eid for eid in seed_ids if graph.get_neighbors(eid)][:5]

        if seed_ids:
            graph_edges = graph.expand_from_entities(seed_ids, depth=2, max_per_node=15)
            existing = {(r.get("from_id"), r.get("relation"), r.get("to_id")) for r in expanded}
            for r in graph_edges:
                key = (r.get("from_id"), r.get("relation"), r.get("to_id"))
                if key not in existing:
                    expanded.append(r)
                    existing.add(key)
    except Exception:
        pass

    if not expanded:
        return []

    # Detect flows — try both original and normalized IDs
    all_flows = []
    seen = set()
    tried = set()
    for e in entities[:5]:
        eid = e.get("entity_id", "")
        if not eid:
            continue
        for candidate in (eid, _normalize_entity_id(eid)):
            if candidate in tried:
                continue
            tried.add(candidate)
            flows = detect_flows(expanded, candidate, scores, top_n=3)
            for f in flows:
                key = tuple(f["chain"])
                if key not in seen:
                    seen.add(key)
                    all_flows.append(f)

    # Convert to RenderFlow
    render_flows = []
    for f in sorted(all_flows, key=lambda x: -x["score"])[:top_n]:
        chain = f["chain"]
        if len(chain) < 3:
            continue
        render_flows.append(RenderFlow(
            source=chain[0],
            via=chain[1],
            target=chain[2],
            relations=tuple(f["relations"][:2]),
            strength=min(1.0, f["score"] / 3.0),
            domains=tuple(f["domains"][:2]),
        ))

    return render_flows


# ══════════════════════════════════════════════════════════════
# MAIN: field_state → RenderState
# ══════════════════════════════════════════════════════════════

def render_field_state(state: Dict[str, Any],
                       projection: str = "plane",
                       selected_id: Optional[str] = None,
                       t: float = 0.0) -> RenderState:
    """Convert a field_state dict into a complete RenderState.

    This is the iGPU entry point. Any canvas/UI consumes the output.
    Does not modify the input field_state.

    Args:
        state: field_state dict from /spine or build_field_state
        projection: "plane" | "toroid" | "hex" | "4d"
        selected_id: focused entity_id (its formation gets emphasis)
        t: time parameter for 4D projection (0.0=now, ashtakala_phase for eternal)
    """
    entities = state.get("entities") or []
    relations = state.get("active_relations") or []
    formations = state.get("formations") or []
    lifecycle = state.get("lifecycle") or {}
    psi = state.get("psi") or {}

    # Project + layout nodes
    nodes = layout_nodes(entities, projection, formations, t=t)

    # Assign roles before activation (center/orbit/bridge)
    assign_roles(nodes, formations, relations)

    # Activate formations: pull members into role-aware spatial clusters
    nodes = activate_formations(nodes, formations, lifecycle, psi,
                                selected_id=selected_id)

    node_map = {n.id: n for n in nodes}

    # Layout edges
    edges = layout_edges(relations)

    # Build flow vectors (2-step meaningful chains)
    flows = build_flow_vectors(state)

    # Resolve flow positions from laid-out nodes
    for f in flows:
        sn = node_map.get(f.source)
        vn = node_map.get(f.via)
        tn = node_map.get(f.target)
        if sn:
            f.sx, f.sy = sn.x, sn.y
        if vn:
            f.vx, f.vy = vn.x, vn.y
        if tn:
            f.tx, f.ty = tn.x, tn.y

    # Layout formations (compute centroid/radius AFTER activation)
    rendered_formations = layout_formations(formations, node_map)

    # Compute bounds
    if nodes:
        min_x = min(n.x for n in nodes)
        min_y = min(n.y for n in nodes)
        max_x = max(n.x for n in nodes)
        max_y = max(n.y for n in nodes)
        # Add margin
        margin = max(50, (max_x - min_x) * 0.1)
        bounds = (min_x - margin, min_y - margin,
                  max_x + margin, max_y + margin)
    else:
        bounds = (-300, -300, 300, 300)

    return RenderState(
        nodes=nodes,
        edges=edges,
        flows=flows,
        formations=rendered_formations,
        lifecycle_phase=lifecycle.get("phase", "unknown"),
        lifecycle_intensity=lifecycle.get("intensity", 0.0),
        psi_intensity=psi.get("intensity", 0.5),
        psi_focus=psi.get("focus", 0.5),
        psi_stability=psi.get("stability", 0.5),
        projection=projection,
        bounds=bounds,
    )


def render_state_to_dict(rs: RenderState) -> Dict[str, Any]:
    """Serialize RenderState to a plain dict (for JSON/API)."""
    return {
        "nodes": [
            {"id": n.id, "name": n.name, "x": round(n.x, 2), "y": round(n.y, 2),
             "z": round(n.z, 2), "size": round(n.size, 3),
             "color": list(n.color), "alpha": round(n.alpha, 3),
             "attestation": n.attestation, "element": n.element,
             "guna": n.guna, "group": n.group,
             "role": n.role, "motion": n.motion}
            for n in rs.nodes
        ],
        "edges": [
            {"source": e.source, "target": e.target, "relation": e.relation,
             "attestation": e.attestation, "style": e.style,
             "width": round(e.width, 3), "alpha": round(e.alpha, 3),
             "mutual": e.mutual}
            for e in rs.edges
        ],
        "flows": [
            {"source": f.source, "via": f.via, "target": f.target,
             "relations": list(f.relations), "strength": round(f.strength, 3),
             "domains": list(f.domains),
             "curve": {"sx": round(f.sx, 2), "sy": round(f.sy, 2),
                       "vx": round(f.vx, 2), "vy": round(f.vy, 2),
                       "tx": round(f.tx, 2), "ty": round(f.ty, 2)}}
            for f in rs.flows
        ],
        "formations": [
            {"name": f.name, "center_x": round(f.center_x, 2),
             "center_y": round(f.center_y, 2), "radius": round(f.radius, 2),
             "member_ids": f.member_ids, "symmetry": round(f.symmetry, 3),
             "style": f.style}
            for f in rs.formations
        ],
        "lifecycle_phase": rs.lifecycle_phase,
        "lifecycle_intensity": round(rs.lifecycle_intensity, 3),
        "psi": {"intensity": rs.psi_intensity, "focus": rs.psi_focus,
                "stability": rs.psi_stability},
        "projection": rs.projection,
        "bounds": [round(b, 2) for b in rs.bounds],
    }
