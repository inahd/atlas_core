"""
species_renderer.py — Species SVG rendering from render_params.

Loads species_render_params.csv for geometric primitives.
Uses nakshatra_species.csv for field-presence scoring.

Pattern follows ui_vastu_engine.py.
"""

import csv
import io
import math
import os
from typing import Dict, List

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
_RENDER_CSV = os.path.join(_ROOT, "datasets", "species", "species_render_params.csv")
_NAK_SPECIES_CSV = os.path.join(_ROOT, "datasets", "species", "nakshatra_species.csv")
_ENTITIES_CSV = os.path.join(_ROOT, "datasets", "species", "species_entities.csv")

_render_cache = None
_nak_species_cache = None
_entities_cache = None


def _load(path):
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read().lstrip()
        return list(csv.DictReader(io.StringIO(text)))
    except Exception:
        return []


def _render_params():
    global _render_cache
    if _render_cache is None:
        _render_cache = {r["species_id"]: r for r in _load(_RENDER_CSV) if r.get("species_id")}
    return _render_cache


def _nak_species():
    global _nak_species_cache
    if _nak_species_cache is None:
        _nak_species_cache = _load(_NAK_SPECIES_CSV)
    return _nak_species_cache


def _entities():
    global _entities_cache
    if _entities_cache is None:
        _entities_cache = {r["entity_id"]: r for r in _load(_ENTITIES_CSV) if r.get("entity_id")}
    return _entities_cache


def _presence_score(species_id, field_state):
    """How present is this species in the current field?"""
    p5 = field_state.get("panchanga", {})
    nak = p5.get("nakshatra", "").lower().replace(" ", "_")
    tidx = int(p5.get("tidx", 15))
    # Purnima = fully active, amavasya = resting
    activity = 0.5 + 0.5 * (1 - abs(tidx - 15) / 15)

    # Check nakshatra-species yoni match
    for row in _nak_species():
        if row.get("species_id") == species_id:
            row_nak = row.get("nakshatra_name", "").lower().replace(" ", "_")
            if row_nak and (row_nak in nak or nak in row_nak):
                return min(1.0, activity + 0.3)
    return activity * 0.3  # baseline low if no match


def _validate(spec):
    defaults = {
        "body_form": "", "geometric_primitive": "",
        "proportions": {"head": 0.12, "body": 0.5, "limbs": 0.25, "tail": 0.13},
        "color_primary": "#808080", "color_secondary": "#606060",
        "line_weight": 1.5, "motion_vector": "static", "dominant_curve": "linear",
        "animation": {"cycle_ms": 3000, "amplitude": 0.5, "direction": "static"},
        "presence_score": 0.0, "attestation": "OBSERVED:TRADITIONAL",
    }
    for k, v in defaults.items():
        if k not in spec or spec[k] is None:
            spec[k] = v
    return spec


def derive_species_geometry(species_id: str, field_state: dict) -> dict:
    """Derive species geometry from render params + field state. Never raises."""
    try:
        params = _render_params().get(species_id, {})
        if not params:
            return _validate({"presence_score": 0.0})

        entity = _entities().get(species_id, {})
        presence = _presence_score(species_id, field_state)
        lifecycle = field_state.get("lifecycle", {})
        intensity = lifecycle.get("intensity", 0.5)

        return _validate({
            "body_form": params.get("body_form_primary", ""),
            "geometric_primitive": params.get("geometric_equivalent", ""),
            "proportions": {
                "head": float(params.get("proportion_head", 0.12)),
                "body": float(params.get("proportion_body", 0.5)),
                "limbs": float(params.get("proportion_limbs", 0.25)),
                "tail": float(params.get("proportion_tail", 0.13)),
            },
            "color_primary": params.get("color_primary_hex", "#808080"),
            "color_secondary": params.get("color_secondary_hex", "#606060"),
            "line_weight": float(params.get("line_weight", 1.5)),
            "motion_vector": params.get("motion_vector", "static"),
            "dominant_curve": params.get("dominant_curve", "linear"),
            "animation": {
                "cycle_ms": 3000,
                "amplitude": intensity * presence,
                "direction": params.get("motion_vector", "static"),
            },
            "presence_score": round(presence, 3),
            "attestation": "OBSERVED:TRADITIONAL",
        })
    except Exception:
        return _validate({})


def render_species_svg(species_id: str, field_state: dict,
                       cx: float = 0, cy: float = 0, scale: float = 1.0) -> str:
    """Render species as SVG <g> element. Never raises."""
    try:
        g = derive_species_geometry(species_id, field_state)
        prim = g["geometric_primitive"]
        c1 = g["color_primary"]
        c2 = g["color_secondary"]
        lw = g["line_weight"] * scale
        props = g["proportions"]
        body_h = 40 * scale * props["body"]
        head_h = 40 * scale * props["head"]
        opacity = max(0.2, g["presence_score"])

        svg = f'<g transform="translate({cx},{cy})" opacity="{opacity}">'

        if prim == "circle":
            # Round-bodied animals (elephant, cow, owl)
            svg += f'<ellipse cx="0" cy="0" rx="{body_h}" ry="{body_h*0.7}" fill="none" stroke="{c1}" stroke-width="{lw}"/>'
            svg += f'<ellipse cx="{body_h*0.8}" cy="{-body_h*0.4}" rx="{head_h*2}" ry="{head_h*1.5}" fill="none" stroke="{c1}" stroke-width="{lw}"/>'
            # Legs
            for lx in [-body_h*0.5, -body_h*0.2, body_h*0.2, body_h*0.5]:
                svg += f'<line x1="{lx}" y1="{body_h*0.6}" x2="{lx}" y2="{body_h*1.2}" stroke="{c1}" stroke-width="{lw}"/>'

        elif prim == "triangle":
            # Angular animals (horse, lion, dog)
            svg += f'<polygon points="0,{-body_h} {-body_h*0.8},{body_h*0.5} {body_h*0.8},{body_h*0.5}" fill="none" stroke="{c1}" stroke-width="{lw}"/>'
            svg += f'<ellipse cx="0" cy="{-body_h*0.9}" rx="{head_h*2}" ry="{head_h*1.5}" fill="none" stroke="{c1}" stroke-width="{lw}"/>'

        elif prim in ("spiral", "sinusoidal"):
            # Serpentine/wave animals
            amp = body_h * 0.4
            points = []
            for i in range(20):
                t = i / 19
                x = (t - 0.5) * body_h * 3
                y = math.sin(t * math.pi * 2) * amp
                points.append(f"{x:.1f},{y:.1f}")
            svg += f'<polyline points="{" ".join(points)}" fill="none" stroke="{c1}" stroke-width="{lw*1.5}"/>'
            # Head at end
            svg += f'<ellipse cx="{body_h*1.5}" cy="0" rx="{head_h*2}" ry="{head_h}" fill="none" stroke="{c1}" stroke-width="{lw}"/>'

        elif prim == "vesica":
            # Two overlapping ellipses (cat, rabbit)
            svg += f'<ellipse cx="{-body_h*0.2}" cy="0" rx="{body_h*0.6}" ry="{body_h*0.4}" fill="none" stroke="{c1}" stroke-width="{lw}"/>'
            svg += f'<ellipse cx="{body_h*0.2}" cy="0" rx="{body_h*0.6}" ry="{body_h*0.4}" fill="none" stroke="{c2}" stroke-width="{lw*0.8}"/>'
            svg += f'<ellipse cx="{body_h*0.6}" cy="{-body_h*0.3}" rx="{head_h*2}" ry="{head_h*1.2}" fill="none" stroke="{c1}" stroke-width="{lw}"/>'

        elif prim == "mandala":
            # Radial fan (peacock)
            for i in range(12):
                a = (i / 12) * math.pi - math.pi / 2
                x2 = math.cos(a) * body_h * 1.5
                y2 = math.sin(a) * body_h * 1.5
                col = c1 if i % 2 == 0 else c2
                svg += f'<line x1="0" y1="0" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{lw*0.8}"/>'
            svg += f'<ellipse cx="0" cy="{body_h*0.5}" rx="{head_h*2}" ry="{body_h*0.3}" fill="none" stroke="{c1}" stroke-width="{lw}"/>'

        else:
            # Parabolic/default (swan, parrot, monkey)
            svg += f'<path d="M{-body_h*0.5},0 Q0,{-body_h*0.8} {body_h*0.5},0" fill="none" stroke="{c1}" stroke-width="{lw}"/>'
            svg += f'<ellipse cx="{body_h*0.5}" cy="{-body_h*0.3}" rx="{head_h*2}" ry="{head_h*1.5}" fill="none" stroke="{c1}" stroke-width="{lw}"/>'

        svg += '</g>'
        return svg

    except Exception:
        return f'<g><circle cx="{cx}" cy="{cy}" r="3" fill="#808080"/></g>'


def get_top_species(field_state: dict, n: int = 5) -> list:
    """Return top N species by presence score for current field."""
    results = []
    for sid in _render_params():
        score = _presence_score(sid, field_state)
        results.append({"id": sid, "presence_score": round(score, 3)})
    results.sort(key=lambda x: -x["presence_score"])
    return results[:n]
