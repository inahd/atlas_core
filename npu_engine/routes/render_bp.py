"""render_bp.py — Render, yantra, and visualization routes.

Extracted from kernel.py (RTE-005).
Routes that depend on _spine() remain in kernel.py.
"""
import json
import os
from pathlib import Path

from flask import Blueprint, Response, jsonify, request, send_file

render_bp = Blueprint('render', __name__)

# Supabase config (anon key — safe to include)
_SUPA_URL = "https://oxskujpofiipoeifcfnm.supabase.co"
_SUPA_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im94c2t1anBvZmlpcG9laWZjZm5tIiwi"
    "cm9sZSI6ImFub24iLCJpYXQiOjE3NzQyODQyMDUsImV4cCI6MjA4OTg2MDIwNX0."
    "264z-yp79z3J9IGiHn3wSZs0kOSozQFvxNxwL822eok"
)


def _enrich_fs_yantra(fs):
    """Add yantra + co-triangular data to field state."""
    try:
        from npu_engine.graph_engine import GraphEngine as _YGE
        from npu_engine.torus_queries import torus_context_for_entity
        import unicodedata
        _yg = _YGE()
        nak = fs.get("panchanga", {}).get("nakshatra", "")
        nak_ascii = unicodedata.normalize("NFKD", nak).encode("ascii", "ignore").decode("ascii")
        ctx = torus_context_for_entity(nak, _yg._metadata, _yg) or \
              torus_context_for_entity(nak_ascii, _yg._metadata, _yg) or {}
        fs["yantra"] = ctx.get("yantra", {})
        fs["co_triangulars"] = ctx.get("co_triangulars", [])
    except Exception:
        pass
    return fs


# ── Render toroid ─────────────────────────────

@render_bp.route("/render/toroid", methods=["POST", "GET"])
def _render_toroid():
    """Render toroidal field via Blender headless."""
    import subprocess
    from kernel import _HERE, _json_serial, field_state
    fs = field_state()
    field_data = {
        "panchanga": fs.get("panchanga", {}),
        "sound_state": fs.get("sound_state", {}),
        "entities": (fs.get("entities") or [])[:20],
        "theta": fs.get("theta", 0.0),
        "phi": fs.get("phi", 1.57),
    }
    Path("/tmp/atlas_field.json").write_text(json.dumps(field_data, default=_json_serial))
    try:
        result = subprocess.run(
            ["blender", "--background", "--python",
             str(_HERE / "blender" / "render_toroid.py")],
            capture_output=True, text=True, timeout=60)
        if Path("/tmp/atlas_render.png").exists():
            return send_file("/tmp/atlas_render.png", mimetype="image/png")
        return Response(json.dumps({"error": result.stderr[-300:]}), mimetype="application/json", status=500)
    except subprocess.TimeoutExpired:
        return Response(json.dumps({"error": "render timeout"}), mimetype="application/json", status=504)
    except FileNotFoundError:
        return Response(json.dumps({"error": "blender not installed"}), mimetype="application/json", status=503)


# ── Render eternal ─────────────────────────────

@render_bp.route("/render/eternal")
def _render_eternal():
    """Eternal cosmology render — canonical entity positions, not field-weighted."""
    from kernel import _json_serial
    proj = request.args.get("projection", "toroid")
    t_param = float(request.args.get("t", 0.0))
    try:
        from npu_engine.igpu import render_field_state, render_state_to_dict
        from npu_engine.datasets import load_all_entities, load_entity_metadata

        coords = load_all_entities()
        metadata = load_entity_metadata()
        entities = []
        for eid, (theta, phi) in list(coords.items())[:64]:
            meta = metadata.get(eid, {})
            entities.append({
                "entity_id": eid,
                "name": meta.get("name", eid.replace("_", " ")),
                "theta": theta,
                "phi": phi,
                "composite_score": 0.5,
                "element": meta.get("element", "ether"),
                "guna": meta.get("guna", "sattva"),
                "attestation": "OBSERVED",
            })

        state = {"entities": entities, "active_relations": [], "formations": [],
                 "lifecycle": {"phase": "formation", "intensity": 0.7},
                 "psi": {"intensity": 0.6, "focus": 0.5, "stability": 0.8}}

        rs = render_field_state(state, projection=proj, t=t_param)
        payload = render_state_to_dict(rs)
    except Exception as exc:
        payload = {"error": str(exc)}
    return Response(
        json.dumps(payload, default=_json_serial, ensure_ascii=False),
        mimetype="application/json",
    )


# ── Render bandhu / species / shrine ─────────────────────────────

@render_bp.route("/render/bandhu")
def _render_bandhu():
    from kernel import field_state
    from npu_engine.renderers.figure_renderer import render_bandhu_full
    pose = request.args.get("pose", "idle")
    raw_scale = float(request.args.get("scale", 1.0))
    layers = request.args.get("layers", "skin")
    dhatu = request.args.get("dhatu", "")
    zoom = float(request.args.get("zoom", 1.0))
    scale = raw_scale
    g_svg = render_bandhu_full(field_state(), pose, 0, 0, scale,
                               layers=layers, dhatu=dhatu,
                               zoom_level=zoom)
    full_svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' "
        "width='400' height='600' "
        "viewBox='-200 -200 400 600' "
        "style='background:#060c0a'>"
        f"{g_svg}</svg>"
    )
    return Response(full_svg, mimetype="image/svg+xml")


@render_bp.route("/render/species/<species_id>")
def _render_species(species_id):
    from kernel import field_state
    from npu_engine.renderers.species_renderer import render_species_svg
    scale = float(request.args.get("scale", 1.0))
    g_svg = render_species_svg(species_id, field_state(), 0, 0, scale)
    full_svg = (
        f"<svg xmlns='http://www.w3.org/2000/svg' "
        f"width='200' height='200' viewBox='-100 -100 200 200' "
        f"style='background:#060c0a'>{g_svg}</svg>"
    )
    return Response(full_svg, mimetype="image/svg+xml")


@render_bp.route("/render/shrine")
def _render_shrine():
    from kernel import field_state
    from npu_engine.renderers.figure_renderer import render_bandhu_svg
    from npu_engine.renderers.species_renderer import render_species_svg, get_top_species
    fs = field_state()
    bandhu = render_bandhu_svg(fs, "seated", 0, 0, 1.0)
    top = get_top_species(fs, n=5)
    species = []
    positions = [(-80, -30), (80, -30), (-60, 40), (60, 40), (0, -60)]
    for i, s in enumerate(top):
        pos = positions[i] if i < len(positions) else (0, 0)
        svg = render_species_svg(s["id"], fs, pos[0], pos[1], 0.6)
        species.append({"id": s["id"], "svg": svg,
                        "presence_score": s["presence_score"],
                        "position_hint": {"x": pos[0], "y": pos[1]}})
    p5 = fs.get("panchanga", {})
    return jsonify({
        "bandhu": bandhu,
        "species": species,
        "field": {"nakshatra": p5.get("nakshatra", ""),
                  "tithi": p5.get("tithi", ""),
                  "element": p5.get("element", "")},
    })


# ── Yantra SVG / data ─────────────────────────────

@render_bp.route("/yantra/svg")
def _yantra_svg():
    """Generate Sri Yantra SVG from current field state."""
    from kernel import field_state
    from npu_engine.yantra_generator import generate_yantra
    fs = _enrich_fs_yantra(field_state())
    w = int(request.args.get("w", "280"))
    h = int(request.args.get("h", "280"))
    svg = generate_yantra(fs, width=w, height=h)
    return Response(svg, mimetype="image/svg+xml")


@render_bp.route("/yantra/data")
def _yantra_field_data():
    """Return yantra visualization data for current field state."""
    from kernel import _json_serial, field_state
    from npu_engine.yantra_generator import yantra_data_for_field
    fs = _enrich_fs_yantra(field_state())
    data = yantra_data_for_field(fs)
    return Response(
        json.dumps(data, default=_json_serial, ensure_ascii=False),
        mimetype="application/json")


@render_bp.route("/yantra-data")
def _yantra_data():
    """Yantra geometry data — element-driven sides, rings, speed, colors."""
    from kernel import _devi_field, _json_serial, field_state
    fs = field_state()
    p5 = fs["panchanga"]
    nak = p5.get("nak_data") or {}
    mu = fs.get("muhurta") or {}
    raga_name = fs.get("devi_raga", "Yaman")
    raga_def = fs.get("devi_raga_def") or {}
    element = (nak.get("element") or "ether").lower()
    geometry = {
        "fire": {"sides": 3, "rings": 4, "speed": 1.2, "vibe_intensity": 0.82, "colors": {"primary": "#FF8A3A", "glow": "#FFD36E", "bg": "#140804"}},
        "water": {"sides": 6, "rings": 5, "speed": 0.78, "vibe_intensity": 0.56, "colors": {"primary": "#5DA7D1", "glow": "#B4E7FF", "bg": "#050A12"}},
        "earth": {"sides": 4, "rings": 4, "speed": 0.7, "vibe_intensity": 0.48, "colors": {"primary": "#9F7B54", "glow": "#E2C49D", "bg": "#0C0906"}},
        "air": {"sides": 8, "rings": 6, "speed": 1.08, "vibe_intensity": 0.68, "colors": {"primary": "#7BA7C8", "glow": "#D6F3FF", "bg": "#070C11"}},
        "ether": {"sides": 12, "rings": 6, "speed": 0.94, "vibe_intensity": 0.62, "colors": {"primary": "#C8A96E", "glow": "#F5E6C8", "bg": "#1A1508"}},
    }.get(element, {
        "sides": 12, "rings": 5, "speed": 0.9, "vibe_intensity": 0.5,
        "colors": {"primary": "#C8A96E", "glow": "#F5E6C8", "bg": "#1A1508"},
    })
    payload = {
        **geometry,
        "devi_name": _devi_field(p5["devi"], 0),
        "devi_emoji": _devi_field(p5["devi"], 1),
        "nakshatra": p5["nakshatra"],
        "nak_symbol": nak.get("symbol", "\u2014"),
        "nak_deity": nak.get("deity", "\u2014"),
        "nak_shakti": nak.get("shakti", "\u2014"),
        "guna": nak.get("guna", "\u2014"),
        "element": element,
        "raga": raga_name,
        "raga_rasa": raga_def.get("rasa", ""),
        "tithi": p5["tithi"],
        "paksha": p5["paksha"],
        "vara": p5["vara"],
        "muhurta": mu.get("name", "\u2014"),
    }
    return Response(
        json.dumps(payload, default=_json_serial, ensure_ascii=False),
        mimetype="application/json",
    )


# ── Yantra Supabase persistence ─────────────────────────────

@render_bp.route("/yantra/deposit", methods=["POST"])
def _yantra_deposit():
    """Persist yantra field lines to Supabase."""
    import urllib.request
    lines = request.get_json(silent=True)
    if not lines or not isinstance(lines, list):
        return jsonify({"error": "expected array of lines"}), 400
    payload = json.dumps(lines, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        f"{_SUPA_URL}/rest/v1/yantra_field",
        data=payload,
        headers={
            "apikey": _SUPA_KEY,
            "Authorization": f"Bearer {_SUPA_KEY}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return jsonify({"inserted": len(lines), "status": resp.status})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@render_bp.route("/yantra/field")
def _yantra_field():
    """Fetch existing yantra field lines from Supabase."""
    import urllib.request
    url = f"{_SUPA_URL}/rest/v1/yantra_field?select=*&order=created_at.desc&limit=500"
    req = urllib.request.Request(url, headers={
        "apikey": _SUPA_KEY,
        "Authorization": f"Bearer {_SUPA_KEY}",
    })
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            return Response(
                json.dumps(data, ensure_ascii=False),
                mimetype="application/json",
            )
    except Exception as exc:
        return jsonify({"error": str(exc), "lines": []}), 200
