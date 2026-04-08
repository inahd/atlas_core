"""
yantra_engine.py — Sacred geometry generation from field state.

Generates yantra geometry from the current panchanga/spine.
The yantra is the score: geometric primitives map to beat positions,
element shapes map to tonal qualities, and tala beats distribute
as Euclidean rhythm points around the perimeter.

Element → geometry:
  fire    = triangle (upward, Agni)
  water   = circle (flow, Varuna)
  earth   = square (stability, Prithvi)
  air     = hexagon (movement, Vayu)
  ether   = bindu + lotus petals (Akasha)
"""

import math
from typing import Dict, List, Optional


# ── Element geometry definitions ─────────────────────────
_ELEM_SHAPE = {
    "fire":  "triangle",
    "water": "circle",
    "earth": "square",
    "air":   "hexagon",
    "ether": "lotus",
}

# Element → yantra radii (nested layers from center outward)
_ELEM_RADII = {
    "fire":  [0.25, 0.55],
    "water": [0.3, 0.6],
    "earth": [0.2, 0.5, 0.75],
    "air":   [0.35, 0.65],
    "ether": [0.15, 0.4, 0.7],
}

# Guna → rotation offset and number of sub-shapes
_GUNA_MOD = {
    "sattva": {"rotation": 0,           "layers": 3, "petal_count": 8},
    "rajas":  {"rotation": math.pi / 6, "layers": 2, "petal_count": 6},
    "tamas":  {"rotation": math.pi / 4, "layers": 2, "petal_count": 4},
}


def _euclidean_rhythm(beats, pulses):
    """Bjorklund's Euclidean rhythm: distribute `pulses` hits across `beats` slots.

    Returns list of beat indices that are active.
    E.g. euclidean(8, 3) → [0, 3, 6] — tresillo.
    """
    if pulses <= 0:
        return []
    if pulses >= beats:
        return list(range(beats))

    # Bjorklund algorithm
    pattern = []
    counts = [1] * pulses + [0] * (beats - pulses)
    remainders = [pulses, beats - pulses]

    level = 0
    while remainders[-1] > 1:
        steps = remainders[-2]
        remainder = remainders[-1]
        new_steps = min(steps, remainder)
        new_remainder = abs(steps - remainder)
        remainders = [new_steps, new_remainder] if new_remainder > 0 else [new_steps]
        level += 1

    # Build from counts — simplified: just distribute evenly
    result = []
    acc = 0
    for i in range(pulses):
        result.append(round(acc))
        acc += beats / pulses
    return sorted(set(r % beats for r in result))


def _polygon_points(cx, cy, r, sides, rotation=0):
    """Generate vertices of a regular polygon."""
    points = []
    for i in range(sides):
        angle = rotation + (i / sides) * math.pi * 2 - math.pi / 2
        points.append({
            "x": round(cx + r * math.cos(angle), 2),
            "y": round(cy + r * math.sin(angle), 2),
        })
    return points


def _lotus_petals(cx, cy, r, count, rotation=0):
    """Generate lotus petal paths (elliptical arcs around center)."""
    petals = []
    for i in range(count):
        angle = rotation + (i / count) * math.pi * 2 - math.pi / 2
        tip_x = cx + r * math.cos(angle)
        tip_y = cy + r * math.sin(angle)
        # Petal is a narrow ellipse from center toward tip
        mid_r = r * 0.6
        width = r * 0.18
        left_a = angle - 0.15
        right_a = angle + 0.15
        petals.append({
            "type": "petal",
            "cx": round(cx + mid_r * math.cos(angle), 2),
            "cy": round(cy + mid_r * math.sin(angle), 2),
            "tip_x": round(tip_x, 2),
            "tip_y": round(tip_y, 2),
            "left_x": round(cx + width * math.cos(left_a), 2),
            "left_y": round(cy + width * math.sin(left_a), 2),
            "right_x": round(cx + width * math.cos(right_a), 2),
            "right_y": round(cy + width * math.sin(right_a), 2),
            "index": i,
        })
    return petals


def generate_yantra(spine_data):
    """Generate yantra geometry from spine/field state.

    Args:
        spine_data: dict from /spine endpoint

    Returns:
        dict with:
          - element: str
          - guna: str
          - shapes: list[dict] — geometric primitives
          - beat_points: list[dict] — tala intersection points
          - connections: list[dict] — lines connecting beat points
    """
    p = spine_data.get("panchanga", {})
    ss = spine_data.get("sound_state", {})

    element = (p.get("element") or ss.get("element") or "ether").lower()
    guna = (p.get("guna") or "sattva").lower()
    nakshatra = p.get("nakshatra", "")
    tala_beats = ss.get("tala_beats") or 8
    tala_name = ss.get("tala", "Adi")

    shape_type = _ELEM_SHAPE.get(element, "circle")
    radii = _ELEM_RADII.get(element, [0.3, 0.6])
    guna_mod = _GUNA_MOD.get(guna, _GUNA_MOD["sattva"])
    rotation = guna_mod["rotation"]
    petal_count = guna_mod["petal_count"]

    # Scale factor: yantra fits within S4 geometry ring (r=158)
    # All coords relative to SVG center (0,0), scale=150
    S = 150

    shapes = []

    # ── Central bindu ────────────────────────────────
    shapes.append({
        "type": "circle",
        "cx": 0, "cy": 0, "r": 3,
        "layer": "bindu",
        "source_layer": "S0",
        "tattva": "tattva_svayam_bhagavan",
        "rasa": "madhurya",
    })

    # ── Element shapes at each radius layer ──────────
    for li, frac in enumerate(radii):
        r = frac * S

        if shape_type == "triangle":
            pts = _polygon_points(0, 0, r, 3, rotation + li * math.pi / 3)
            shapes.append({
                "type": "polygon",
                "points": pts,
                "sides": 3,
                "r": round(r, 1),
                "element": element,
                "layer": f"ring_{li}",
            })
            # Inverted triangle on alternate layers
            if li > 0:
                pts2 = _polygon_points(0, 0, r * 0.85, 3, rotation + math.pi + li * math.pi / 3)
                shapes.append({
                    "type": "polygon",
                    "points": pts2,
                    "sides": 3,
                    "r": round(r * 0.85, 1),
                    "element": element,
                    "layer": f"ring_{li}_inv",
                })

        elif shape_type == "square":
            pts = _polygon_points(0, 0, r, 4, rotation + li * math.pi / 8)
            shapes.append({
                "type": "polygon",
                "points": pts,
                "sides": 4,
                "r": round(r, 1),
                "element": element,
                "layer": f"ring_{li}",
            })

        elif shape_type == "hexagon":
            pts = _polygon_points(0, 0, r, 6, rotation + li * math.pi / 12)
            shapes.append({
                "type": "polygon",
                "points": pts,
                "sides": 6,
                "r": round(r, 1),
                "element": element,
                "layer": f"ring_{li}",
            })

        elif shape_type == "lotus":
            # Concentric circles + lotus petals
            shapes.append({
                "type": "circle",
                "cx": 0, "cy": 0, "r": round(r, 1),
                "element": element,
                "layer": f"ring_{li}",
            })
            if li == len(radii) - 1:
                petals = _lotus_petals(0, 0, r, petal_count, rotation)
                for pet in petals:
                    pet["element"] = element
                    pet["layer"] = "petals"
                    shapes.append(pet)

        else:  # circle (water)
            shapes.append({
                "type": "circle",
                "cx": 0, "cy": 0, "r": round(r, 1),
                "element": element,
                "layer": f"ring_{li}",
            })

    # ── Beat points — Euclidean distribution on perimeter ──
    # Use outermost radius for beat placement
    beat_r = max(radii) * S
    # Euclidean pulses: accent beats distributed evenly
    # Number of accents = floor(beats/2) + 1 for interesting patterns
    n_accents = max(2, tala_beats // 2 + 1)
    accent_beats = set(_euclidean_rhythm(tala_beats, n_accents))

    beat_points = []
    for i in range(tala_beats):
        angle = rotation + (i / tala_beats) * math.pi * 2 - math.pi / 2
        bx = round(beat_r * math.cos(angle), 2)
        by = round(beat_r * math.sin(angle), 2)

        beat_points.append({
            "beat_index": i,
            "x": bx,
            "y": by,
            "angle": round(angle, 4),
            "accent": i in accent_beats,
            "sam": i == 0,
            "element": element,
        })

    # ── Connections — lines between adjacent beat points + star pattern ──
    connections = []
    for i in range(tala_beats):
        j = (i + 1) % tala_beats
        connections.append({
            "from": i, "to": j,
            "type": "perimeter",
        })

    # Star connections: connect accent beats to each other
    accent_list = sorted(accent_beats)
    for i in range(len(accent_list)):
        for j in range(i + 1, len(accent_list)):
            connections.append({
                "from": accent_list[i], "to": accent_list[j],
                "type": "star",
            })

    # Connect beat points to center (spoke lines for sam and accents)
    for i in accent_list:
        connections.append({
            "from": i, "to": -1,  # -1 = center
            "type": "spoke",
        })

    return {
        "element": element,
        "guna": guna,
        "nakshatra": nakshatra,
        "tala": tala_name,
        "tala_beats": tala_beats,
        "shape_type": shape_type,
        "shapes": shapes,
        "beat_points": beat_points,
        "connections": connections,
    }
