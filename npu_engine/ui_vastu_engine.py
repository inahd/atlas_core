"""
ui_vastu_engine.py — Interface layout derived from field state + Vāstu spatial law.

This is the single place where UI layout is computed.
Renderers (atlas.html, igpu.py) consume the result; they never recompute it.

Hierarchy:
    kernel / build_field_state
        → field_state
        → vastu_state  (S4 spatial law)
        → ui_layout    (this module)
        → atlas.html / igpu / clients

Three spatial bands:
    A. Center (Brahmasthāna)  — dominant entity, primary focus
    B. Layer ring (S0–S6)     — stable concentric ring, emphasis from field
    C. Zone regions (8 dirs)  — action clusters, activated by zone_weights
"""

from typing import Any, Dict, List
import math


# ══════════════════════════════════════════════════════════
# CANONICAL MAPPINGS — stable configuration, not scattered HTML
# ══════════════════════════════════════════════════════════

# S-layer canonical ring: fixed order, stable positions.
# angle=0 is North (top), clockwise.
_LAYER_RING = [
    {"id": "S0", "label": "Bindu · Source",    "angle_deg":   0},
    {"id": "S1", "label": "Archetype · Devī",  "angle_deg":  51},
    {"id": "S2", "label": "Sound · Rāga",      "angle_deg": 103},
    {"id": "S3", "label": "Rhythm · Kāla",     "angle_deg": 154},
    {"id": "S4", "label": "Geometry · Vāstu",   "angle_deg": 206},
    {"id": "S5", "label": "Nature · Āyurveda",  "angle_deg": 257},
    {"id": "S6", "label": "Līlā · Practice",    "angle_deg": 309},
]

# Directional zones → semantic action groups.
# Each zone has a stable label, position, and action palette.
# attestation: SYNTHESIS — these mappings are design decisions, not śāstra.
_ZONE_ACTIONS = {
    "NE": {
        "label": "Insight",
        "x": 0.80, "y": 0.20,
        "actions": [
            {"id": "inspect",    "label": "Inspect",    "priority": 1},
            {"id": "commentary", "label": "Commentary", "priority": 2},
            {"id": "codex",      "label": "Codex",      "priority": 3},
        ],
    },
    "E": {
        "label": "Reveal",
        "x": 0.92, "y": 0.50,
        "actions": [
            {"id": "display", "label": "Display", "priority": 1},
            {"id": "unfold",  "label": "Unfold",  "priority": 2},
        ],
    },
    "SE": {
        "label": "Build",
        "x": 0.80, "y": 0.80,
        "actions": [
            {"id": "build",   "label": "Build",   "priority": 1},
            {"id": "compose", "label": "Compose", "priority": 2},
            {"id": "render",  "label": "Render",  "priority": 3},
        ],
    },
    "S": {
        "label": "Transform",
        "x": 0.50, "y": 0.92,
        "actions": [
            {"id": "commit",    "label": "Commit",    "priority": 1},
            {"id": "transform", "label": "Transform", "priority": 2},
        ],
    },
    "SW": {
        "label": "Dissolve",
        "x": 0.20, "y": 0.80,
        "actions": [
            {"id": "clear",   "label": "Clear",   "priority": 1},
            {"id": "archive", "label": "Archive", "priority": 2},
            {"id": "prune",   "label": "Prune",   "priority": 3},
        ],
    },
    "W": {
        "label": "Memory",
        "x": 0.08, "y": 0.50,
        "actions": [
            {"id": "history",   "label": "History",   "priority": 1},
            {"id": "retrieval", "label": "Retrieval", "priority": 2},
        ],
    },
    "NW": {
        "label": "Navigate",
        "x": 0.20, "y": 0.20,
        "actions": [
            {"id": "navigate", "label": "Navigate", "priority": 1},
            {"id": "explore",  "label": "Explore",  "priority": 2},
            {"id": "graph",    "label": "Graph",    "priority": 3},
        ],
    },
    "N": {
        "label": "Synthesize",
        "x": 0.50, "y": 0.08,
        "actions": [
            {"id": "overview",    "label": "Overview",    "priority": 1},
            {"id": "synthesize",  "label": "Synthesize",  "priority": 2},
        ],
    },
    "Center": {
        "label": "Focus",
        "x": 0.50, "y": 0.50,
        "actions": [
            {"id": "focus", "label": "Focus", "priority": 1},
            {"id": "bind",  "label": "Bind",  "priority": 2},
        ],
    },
}

# Layer relevance heuristics: which field properties boost each layer.
# Used to compute layer_ring weight. Not truth — display emphasis only.
_LAYER_WEIGHT_KEYS = {
    "S0": lambda s: 0.5 + 0.5 * s.get("psi", {}).get("intensity", 0.5),
    "S1": lambda s: min(1.0, len([e for e in s.get("entities", [])[:10]
                                   if "deity" in e.get("entity_id", "")]) / 3.0 + 0.3),
    "S2": lambda s: 0.7 if s.get("sound_state", s).get("raga") else 0.3,
    "S3": lambda s: 0.6 + 0.4 * s.get("arc_phase", 0.5),
    "S4": lambda s: 0.5 + 0.5 * max(
        s.get("vastu_state", {}).get("zone_weights", {}).values() or [0]),
    "S5": lambda s: min(1.0, len([e for e in s.get("entities", [])[:20]
                                   if "plant" in e.get("entity_id", "")]) / 2.0 + 0.2),
    "S6": lambda s: 0.4 + 0.3 * s.get("psi", {}).get("stability", 0.5),
}


# ══════════════════════════════════════════════════════════
# INTERNAL HELPERS
# ══════════════════════════════════════════════════════════

def _ring_xy(angle_deg: float, radius: float = 0.35,
             cx: float = 0.5, cy: float = 0.5):
    """Convert angle (0=N, clockwise) + radius to normalized x,y."""
    rad = math.radians(angle_deg - 90)  # CSS: 0°=right, we want 0°=top
    return (
        round(cx + radius * math.cos(rad), 4),
        round(cy + radius * math.sin(rad), 4),
    )


def _compute_center_focus(vastu_state: dict, entities: list) -> dict:
    """Brahmasthāna → center focus node."""
    brahma = vastu_state.get("brahmasthana", {})
    eid = brahma.get("entity_id", "")
    reason = brahma.get("reason", "brahmasthana")

    # Find the entity metadata
    label = eid.replace("_", " ") if eid else "field"
    for e in entities[:8]:
        if e.get("entity_id") == eid:
            label = e.get("name", label)
            break

    return {
        "entity_id": eid,
        "label": label,
        "zone": "Center",
        "x": 0.5,
        "y": 0.5,
        "size": 1.0,
        "reason": reason,
    }


def _compute_layer_ring(field_state: dict) -> list:
    """S0–S6 ring with positions + field-derived weights."""
    ring = []
    for layer in _LAYER_RING:
        lid = layer["id"]
        weight_fn = _LAYER_WEIGHT_KEYS.get(lid)
        try:
            weight = round(weight_fn(field_state), 3) if weight_fn else 0.5
        except Exception:
            weight = 0.5

        x, y = _ring_xy(layer["angle_deg"])
        ring.append({
            "id": lid,
            "label": layer["label"],
            "x": x,
            "y": y,
            "size": round(0.4 + 0.6 * weight, 3),
            "weight": weight,
            "active": weight > 0.45,
            "zone": _angle_to_zone(layer["angle_deg"]),
        })
    return ring


def _angle_to_zone(deg: float) -> str:
    """Map ring angle to nearest Vāstu zone."""
    # N=0, NE=45, E=90, SE=135, S=180, SW=225, W=270, NW=315
    zones = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    idx = round(deg / 45) % 8
    return zones[idx]


def _compute_zone_regions(vastu_state: dict, lifecycle: dict, psi: dict) -> dict:
    """Zone regions with weights and dominance from vastu_state."""
    zone_weights = vastu_state.get("zone_weights", {})
    dominant = vastu_state.get("activation_summary", {}).get("dominant_zone", "Center")

    regions = {}
    for zone_id, zone_def in _ZONE_ACTIONS.items():
        w = zone_weights.get(zone_id, 0.1)
        regions[zone_id] = {
            "label": zone_def["label"],
            "weight": round(w, 4),
            "dominant": zone_id == dominant,
            "x": zone_def["x"],
            "y": zone_def["y"],
        }
    return regions


def _compute_zone_action_state(vastu_state: dict, lifecycle: dict) -> dict:
    """Zone actions with activation state from field."""
    zone_weights = vastu_state.get("zone_weights", {})
    phase = lifecycle.get("phase", "formation")
    intensity = lifecycle.get("intensity", 0.7)

    result = {}
    for zone_id, zone_def in _ZONE_ACTIONS.items():
        w = zone_weights.get(zone_id, 0.1)
        actions = []
        for act in zone_def["actions"]:
            # Active if zone weight > 0.12 and lifecycle allows it
            active = w > 0.12 and intensity > 0.15
            # In pralaya, only archive/clear/dissolve stay active
            if phase == "pralaya" and act["id"] not in ("clear", "archive", "prune", "focus"):
                active = False
            actions.append({
                "id": act["id"],
                "label": act["label"],
                "active": active,
                "priority": act["priority"],
            })
        result[zone_id] = actions
    return result


def _compute_entity_nodes(vastu_state: dict, entities: list,
                          formations: list) -> list:
    """Entity placement nodes from vastu_state.cell_occupancy."""
    occupancy = vastu_state.get("cell_occupancy", {})
    formation_members = set()
    for f in formations:
        for m in f.get("members", []):
            formation_members.add(m)

    nodes = []
    for eid, cell_info in occupancy.items():
        # Find entity metadata
        label = eid.replace("_", " ")
        score = 0.0
        for e in entities:
            if e.get("entity_id") == eid:
                label = e.get("name", label)
                score = e.get("composite_score", e.get("score", 0))
                break

        nodes.append({
            "entity_id": eid,
            "label": label,
            "zone": cell_info.get("zone", "Center"),
            "cell_id": cell_info.get("cell_id", ""),
            "x": cell_info.get("x", 0.5),
            "y": cell_info.get("y", 0.5),
            "size": round(min(1.0, 0.3 + score * 0.5), 3),
            "active": score > 0.3,
            "formation_member": eid in formation_members,
        })

    # Sort by formation membership first, then score — stable ordering
    nodes.sort(key=lambda n: (n.get("formation_member", False), n["size"]), reverse=True)
    # Cap at 24 visible nodes to limit visual noise
    return nodes[:24]


def _compute_nav_paths(layer_ring: list, vastu_state: dict) -> list:
    """Navigation paths: center ↔ active layers, center ↔ dominant zone."""
    paths = []
    dominant = vastu_state.get("activation_summary", {}).get("dominant_zone", "Center")

    # Center → dominant zone
    if dominant != "Center":
        paths.append({"from": "Center", "to": dominant, "kind": "zone_focus"})

    # Center → most active layer
    if layer_ring:
        top_layer = max(layer_ring, key=lambda l: l["weight"])
        if top_layer["weight"] > 0.6:
            paths.append({"from": "Center", "to": top_layer["id"], "kind": "layer_focus"})

    return paths


# ══════════════════════════════════════════════════════════
# HARDENING HELPERS
# ══════════════════════════════════════════════════════════

def _clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, float(v)))


def _clamp_xy(d: dict) -> dict:
    """Clamp x,y coordinates to [0,1]."""
    if "x" in d:
        d["x"] = round(_clamp(d["x"]), 4)
    if "y" in d:
        d["y"] = round(_clamp(d["y"]), 4)
    return d


def _smooth_xy(new: dict, prev: dict, alpha: float = 0.2) -> dict:
    """Blend new position toward previous (reduces jitter). alpha=weight of new."""
    if prev and "x" in prev and "y" in prev:
        new["x"] = round(alpha * new.get("x", 0.5) + (1 - alpha) * prev["x"], 4)
        new["y"] = round(alpha * new.get("y", 0.5) + (1 - alpha) * prev["y"], 4)
    return new


def _validate_layout(layout: dict) -> dict:
    """Ensure all required keys exist with correct types. Never returns partial data."""
    defaults = {
        "layout_version": 1,
        "mode": "vastu_mandala",
        "center_focus": {"entity_id": "", "label": "field", "zone": "Center",
                         "x": 0.5, "y": 0.5, "size": 1.0, "reason": "default"},
        "layer_ring": [],
        "zone_regions": {},
        "zone_actions": {},
        "entity_nodes": [],
        "navigation_paths": [],
        "status": {
            "active_zone": "Center",
            "dominant_element": "ether",
            "top_formation": "",
            "formation_count": 0,
            "lifecycle_phase": "idle",
        },
        "style_hints": {
            "ring_rotation_deg": 0.0,
            "glow_intensity": 0.5,
            "stability": 0.5,
        },
        "attestation": "SYNTHESIS",
    }
    for key, default in defaults.items():
        if key not in layout or layout[key] is None:
            layout[key] = default
        elif isinstance(default, dict) and isinstance(layout[key], dict):
            for dk, dv in default.items():
                if dk not in layout[key]:
                    layout[key][dk] = dv
        elif isinstance(default, list) and not isinstance(layout[key], list):
            layout[key] = default

    # Clamp all coordinates
    _clamp_xy(layout["center_focus"])
    for node in layout.get("layer_ring", []):
        _clamp_xy(node)
    for node in layout.get("entity_nodes", []):
        _clamp_xy(node)
    for region in layout.get("zone_regions", {}).values():
        if isinstance(region, dict):
            _clamp_xy(region)

    # Clamp style hints
    sh = layout["style_hints"]
    sh["glow_intensity"] = round(_clamp(sh.get("glow_intensity", 0.5), 0.2, 1.0), 3)
    sh["stability"] = round(_clamp(sh.get("stability", 0.5), 0.0, 1.0), 3)

    # Cap zone_actions: max 3 per zone, sorted by priority
    for zone_id, actions in layout.get("zone_actions", {}).items():
        if isinstance(actions, list):
            actions.sort(key=lambda a: a.get("priority", 99))
            layout["zone_actions"][zone_id] = actions[:3]

    return layout


# ══════════════════════════════════════════════════════════
# PUBLIC API
# ══════════════════════════════════════════════════════════

def derive_ui_layout(field_state: dict) -> dict:
    """Derive complete UI layout from field state + Vāstu spatial law.

    Single function for interface layout computation.
    Renderers consume the result; they never recompute it.

    Args:
        field_state: dict with vastu_state, entities, formations,
                     active_relations, lifecycle, psi, panchanga.
                     Optional: _prev_ui_layout for position smoothing.

    Returns:
        Validated, app-consumable layout object. All coordinates in [0,1].
        All required keys guaranteed present. Safe to render without checks.

    Zone→action mapping is SYNTHESIS (design decisions, not śāstra).
    Layer weights are display emphasis, not truth.
    Smoothing is optional — degrades gracefully without _prev_ui_layout.
    """
    vastu_state = field_state.get("vastu_state", {})
    entities = field_state.get("entities", [])
    formations = field_state.get("formations", [])
    lifecycle = field_state.get("lifecycle", {})
    psi = field_state.get("psi", {})
    prev = field_state.get("_prev_ui_layout")

    # A. Center focus — from Brahmasthāna
    center_focus = _compute_center_focus(vastu_state, entities)

    # B. Layer ring — S0–S6 (fixed canonical order)
    layer_ring = _compute_layer_ring(field_state)

    # C. Zone regions and actions
    zone_regions = _compute_zone_regions(vastu_state, lifecycle, psi)
    zone_actions = _compute_zone_action_state(vastu_state, lifecycle)

    # Entity nodes from Vāstu cell placement
    entity_nodes = _compute_entity_nodes(vastu_state, entities, formations)

    # Navigation paths
    nav_paths = _compute_nav_paths(layer_ring, vastu_state)

    # Status summary — guaranteed complete
    vs_summary = vastu_state.get("activation_summary", {})
    status = {
        "active_zone": str(vs_summary.get("dominant_zone", "Center")),
        "dominant_element": str(vs_summary.get("dominant_element", "ether")),
        "top_formation": str(vs_summary.get("top_formation", "")),
        "formation_count": int(vs_summary.get("formation_count", 0)),
        "lifecycle_phase": str(lifecycle.get("phase", "idle")),
    }

    # Style hints — clamped, stable
    orientation = vastu_state.get("orientation", {})
    raw_rotation = float(orientation.get("effective_rotation_deg", 0.0))
    # Dampen rotation jitter: if prev exists, blend
    if prev and "style_hints" in prev:
        prev_rot = prev["style_hints"].get("ring_rotation_deg", 0.0)
        if abs(raw_rotation - prev_rot) < 2.0:
            raw_rotation = prev_rot  # suppress sub-2° jitter

    n_active = len([n for n in entity_nodes if n.get("active")])
    sym_scores = [f.get("symmetry_score", 0) for f in formations if "symmetry_score" in f]
    avg_sym = sum(sym_scores) / max(len(sym_scores), 1) if sym_scores else 0.3
    derived_stability = _clamp(0.3 + 0.3 * (n_active / max(len(entity_nodes), 1)) + 0.4 * avg_sym)

    style_hints = {
        "ring_rotation_deg": round(raw_rotation, 2),
        "glow_intensity": round(_clamp(psi.get("intensity", 0.5), 0.2, 1.0), 3),
        "stability": round(derived_stability, 3),
    }

    # Optional position smoothing from previous layout
    if prev:
        prev_center = prev.get("center_focus")
        if prev_center:
            _smooth_xy(center_focus, prev_center, alpha=0.2)
        for node in layer_ring:
            prev_nodes = {n["id"]: n for n in prev.get("layer_ring", [])}
            p = prev_nodes.get(node["id"])
            if p:
                _smooth_xy(node, p, alpha=0.2)

    layout = {
        "layout_version": 1,
        "mode": "vastu_mandala",
        "center_focus": center_focus,
        "layer_ring": layer_ring,
        "zone_regions": zone_regions,
        "zone_actions": zone_actions,
        "entity_nodes": entity_nodes,
        "navigation_paths": nav_paths,
        "status": status,
        "style_hints": style_hints,
        "attestation": "SYNTHESIS",
    }

    return _validate_layout(layout)
