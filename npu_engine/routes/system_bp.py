"""system_bp.py — Health, system, snapshot, and dashboard routes.

Extracted from kernel.py (RTE-005).
"""
import json
import os
import time

from flask import Blueprint, Response, current_app, jsonify, request
from pathlib import Path

system_bp = Blueprint('system', __name__)


# ── Health ─────────────────────────────

@system_bp.route("/health")
def _health():
    from kernel import calc_panchanga, START_TIME
    health = {"status": "ok", "timestamp": time.time(), "uptime": time.time() - START_TIME}
    try:
        p = calc_panchanga()
        health["field"] = "ok"
        health["nakshatra"] = p.get("nakshatra")
    except Exception as e:
        health["field"] = f"error: {e}"
        health["status"] = "degraded"
    return jsonify(health)


# ── System state ─────────────────────────────

@system_bp.route("/system/state")
def _system_state():
    from npu_engine.field.system_engine import derive_system_state
    return jsonify(derive_system_state())


@system_bp.route("/system/audio")
def _system_audio():
    from npu_engine.field.system_engine import derive_audio_route, check_audio_connections
    route = derive_audio_route()
    connections = check_audio_connections()
    return jsonify({"route": route, "connections": connections})


@system_bp.route("/system/audio/restore", methods=["POST"])
def _system_audio_restore():
    from npu_engine.field.system_engine import restore_audio_connections
    ok = restore_audio_connections()
    return jsonify({"restored": ok})


@system_bp.route("/system/services")
def _system_services():
    import subprocess
    units = ["atlas-sc", "atlas-sclang", "atlas-porter",
             "atlas-om", "atlas-kernel", "atlas-ngrok"]
    result = {}
    for unit in units:
        try:
            r = subprocess.run(
                ["systemctl", "--user", "is-active", f"{unit}.service"],
                capture_output=True, text=True, timeout=3)
            result[unit] = r.stdout.strip() or "unknown"
        except Exception:
            result[unit] = "unknown"
    return jsonify(result)


# ── Snapshots ─────────────────────────────

@system_bp.route('/snapshot', methods=['POST'])
def _snapshot():
    data = request.json or {}
    url = data.get('url', 'http://localhost:5000/s4')
    filename = data.get('filename', 'snapshot.png')
    folder = data.get('folder', 'research/snapshots')
    wait_ms = data.get('wait_ms', 2000)
    vp = data.get('viewport', {'width': 1400, 'height': 900})
    path = os.path.join(folder, filename)
    os.makedirs(folder, exist_ok=True)
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page(viewport=vp)
            page.goto(url)
            page.wait_for_timeout(wait_ms)
            page.screenshot(path=path)
            browser.close()
        return jsonify({'path': path, 'filename': filename})
    except ImportError:
        return jsonify({'error': 'playwright not installed — pip install playwright && playwright install chromium'}), 501
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ── Dashboard health ─────────────────────────────

@system_bp.route('/dashboard/health')
def _dashboard_health():
    """Single-call system health and state summary for home.html."""
    from kernel import calc_panchanga, _load_full_corpus_registry
    out = {"timestamp": time.time(), "routes": {}, "corpus": {}, "graph": {}, "field": {}}

    # Field state (most important)
    try:
        p = calc_panchanga()
        out["field"] = {
            "tithi": p.get("tithi"),
            "nakshatra": p.get("nakshatra"),
            "devi": p.get("devi", {}).get("name") if isinstance(p.get("devi"), dict) else (p.get("devi")[0] if isinstance(p.get("devi"), (list, tuple)) else p.get("devi")),
            "vara": p.get("vara"),
        }
        out["routes"]["field"] = "ok"
    except Exception as e:
        out["routes"]["field"] = f"error: {e}"

    # Corpus stats
    try:
        registry = _load_full_corpus_registry()
        total_chunks = sum(e.get("chunks", 0) for e in registry)
        out["corpus"] = {"files": len(registry), "chunks": total_chunks}
        out["routes"]["corpus"] = "ok"
    except Exception as e:
        out["routes"]["corpus"] = f"error: {e}"

    # Graph stats
    try:
        from npu_engine.graph_engine import GraphEngine
        g = GraphEngine()
        out["graph"] = {"entities": g.node_count, "edges": g.edge_count}
        out["routes"]["graph"] = "ok"
    except Exception as e:
        out["routes"]["graph"] = f"error: {e}"

    # Quick probe of key routes
    probe_routes = ["/goloka", "/helix", "/trajectory", "/rings", "/yantra",
                    "/guild/state", "/sound/spec", "/layers"]
    for route in probe_routes:
        try:
            current_app.url_map.bind("").match(route, method="GET")
            out["routes"][route] = "registered"
        except Exception:
            out["routes"][route] = "not_found"

    out["health"] = "ok" if out["routes"].get("field") == "ok" else "degraded"
    return jsonify(out)


@system_bp.route('/dashboard/status')
def _dashboard_status():
    """JSON system status for home.html status panel."""
    from kernel import calc_panchanga, field_state, _load_full_corpus_registry, START_TIME
    out = {"health": "ok", "uptime": round(time.time() - START_TIME)}

    # Corpus stats
    try:
        registry = _load_full_corpus_registry()
        total_chunks = sum(e.get("chunks", 0) for e in registry)
        out["corpus"] = {"texts": len(registry), "chunks": total_chunks}
    except Exception:
        out["corpus"] = {"texts": 0, "chunks": 0}

    # Graph stats
    try:
        from npu_engine.datasets import load_all_entities, load_relations
        ents = load_all_entities()
        rels = load_relations()
        rel_count = sum(len(v) for v in rels.values()) if isinstance(rels, dict) else len(rels)
        out["graph"] = {"entities": len(ents), "relations": rel_count}
    except Exception:
        out["graph"] = {"entities": 0, "relations": 0}

    # Field probe
    try:
        calc_panchanga()
        out["field"] = "ok"
    except Exception:
        out["field"] = "error"

    # Engine probes
    probe = {}
    fs = None
    try:
        fs = field_state()
    except Exception:
        pass

    engine_checks = [
        ("goloka", "npu_engine.field.goloka_engine", "derive_goloka"),
        ("trajectory", "npu_engine.time.trajectory_engine", "derive_trajectory"),
        ("svarodaya", "npu_engine.field.svarodaya_engine", "derive_svarodaya"),
        ("dinacharya", "npu_engine.field.dinacharya_engine", "derive_dinacharya"),
        ("astrobotany", "npu_engine.field.astrobotany_engine", "derive_astrobotany"),
    ]
    for name, mod_path, fn_name in engine_checks:
        try:
            mod = __import__(mod_path, fromlist=[fn_name])
            fn = getattr(mod, fn_name)
            fn(fs)
            probe[name] = "ok"
        except Exception:
            probe[name] = "error"

    # Sound probe
    try:
        from npu_engine.field.system_engine import derive_audio_route
        route = derive_audio_route()
        probe["sound"] = "ok" if route.get("available") else "no_device"
    except Exception:
        probe["sound"] = "error"

    out["probe"] = probe
    return jsonify(out)


@system_bp.route("/resonance")
def _resonance():
    """Cosmological resonance — what in the living world matches the current field."""
    from kernel import field_state
    try:
        from npu_engine.field.resonance_engine import derive_resonance
        return jsonify(derive_resonance(field_state()))
    except Exception as e:
        return jsonify({"error": str(e), "temples": [], "deity_images": [], "raga_recordings": []})
