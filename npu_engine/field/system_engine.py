"""
system_engine.py — Kanjira self-model: hardware, audio routing, capabilities.

This is the single place where system topology is read and audio routes are derived.
start.sh and kernel.py consume the result; they never probe hardware directly.

Hierarchy:
    datasets/system/system_topology.csv  — canonical hardware/software graph
    datasets/system/capability_map.csv   — what kanjira can do now vs planned
    → derive_system_state()              — full snapshot with live process checks
    → derive_audio_route()               — find stable synthesis → output path
    → check_audio_connections()          — verify PipeWire links are live
    → restore_audio_connections()        — fix broken links

Pattern follows ui_vastu_engine.py:
    canonical mappings → internal helpers → validation → public API
"""

from typing import Any, Dict, List, Optional
import csv
import os
import subprocess

# ══════════════════════════════════════════════════════════
# DATA LOADING
# ══════════════════════════════════════════════════════════

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
_TOPOLOGY_PATH = os.path.join(_ROOT, "datasets", "system", "system_topology.csv")
_CAPABILITY_PATH = os.path.join(_ROOT, "datasets", "system", "capability_map.csv")

_topology_cache: Optional[List[dict]] = None
_capability_cache: Optional[List[dict]] = None


def _load_csv(path: str) -> List[dict]:
    rows = []
    try:
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                rows.append(row)
    except Exception:
        pass
    return rows


def _load_topology() -> List[dict]:
    global _topology_cache
    if _topology_cache is None:
        _topology_cache = _load_csv(_TOPOLOGY_PATH)
    return _topology_cache


def _load_capabilities() -> List[dict]:
    global _capability_cache
    if _capability_cache is None:
        _capability_cache = _load_csv(_CAPABILITY_PATH)
    return _capability_cache


def _entity_by_id(entity_id: str) -> dict:
    for row in _load_topology():
        if row.get("entity_id") == entity_id:
            return dict(row)
    return {}


# ══════════════════════════════════════════════════════════
# PROCESS PROBES — all have 3s timeout, never raise
# ══════════════════════════════════════════════════════════

def _run(cmd: List[str], timeout: float = 3.0) -> str:
    """Run a subprocess, return stdout. Empty string on any failure."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except Exception:
        return ""


def _is_process_running(name: str) -> bool:
    return bool(_run(["pgrep", "-x", name]))


def _pid_of(pattern: str) -> str:
    out = _run(["pgrep", "-f", pattern])
    return out.split("\n")[0].strip() if out else ""


def _pw_link_outputs() -> List[str]:
    out = _run(["pw-link", "-o"])
    return [line.strip() for line in out.splitlines() if line.strip()] if out else []


def _pw_link_connections() -> List[tuple]:
    """Parse pw-link -l output into (source, sink) tuples."""
    out = _run(["pw-link", "-l"])
    if not out:
        return []
    connections = []
    current_src = ""
    for line in out.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("|->"):
            sink = stripped[3:].strip()
            if current_src:
                connections.append((current_src, sink))
        elif stripped.startswith("|<-"):
            continue  # reverse direction — skip
        elif ":" in stripped:
            current_src = stripped
    return connections


# ══════════════════════════════════════════════════════════
# AUDIO TOPOLOGY — the known graph of synthesis → output
# ══════════════════════════════════════════════════════════

# Static route definitions derived from system_topology.csv
# Stability ratings from operational experience.
_AUDIO_ROUTES = [
    {
        "id": "om_pwcat_motu",
        "label": "om.py → pw-cat → PipeWire → MOTU M2",
        "steps": ["om_py", "pw_cat", "pipewire", "motu_m2"],
        "connect_commands": [],  # pw-cat --target handles routing
        "stability": "stable",
        "native_pipewire": True,
    },
    {
        "id": "sc_pwlink_motu",
        "label": "SC → pw-link → PipeWire → MOTU M2",
        "steps": ["sc_synthesis", "pw_link", "pipewire", "motu_m2"],
        "connect_commands": [
            ["pw-link", "SuperCollider:out_1",
             "alsa_output.usb-MOTU_M2_M20000063536-00.analog-stereo:playback_FL"],
            ["pw-link", "SuperCollider:out_2",
             "alsa_output.usb-MOTU_M2_M20000063536-00.analog-stereo:playback_FR"],
        ],
        "stability": "broken",  # PW 1.2.6 JACK shim: connections appear, audio silent
        "native_pipewire": False,
    },
    {
        "id": "sc_pwjack_motu",
        "label": "SC → pw-jack → JACK shim → MOTU M2",
        "steps": ["sc_synthesis", "pw_jack", "pipewire", "motu_m2"],
        "connect_commands": [
            ["pw-jack", "jack_connect", "SuperCollider:out_1",
             "M Series Analog Stereo:playback_FL"],
            ["pw-jack", "jack_connect", "SuperCollider:out_2",
             "M Series Analog Stereo:playback_FR"],
        ],
        "stability": "broken",
        "native_pipewire": False,
    },
]

# MOTU M2 PipeWire sink identifiers
_MOTU_SINK = "alsa_output.usb-MOTU_M2_M20000063536-00.analog-stereo"
_MOTU_FL = _MOTU_SINK + ":playback_FL"
_MOTU_FR = _MOTU_SINK + ":playback_FR"


# ══════════════════════════════════════════════════════════
# INTERNAL HELPERS
# ══════════════════════════════════════════════════════════

def _check_compute() -> dict:
    return {
        "cpu": {"status": "active", "name": "Intel Core Ultra (x86)"},
        "npu": {
            "status": "active" if os.path.exists("/dev/accel0") else "unavailable",
            "name": "Intel NPU (Meteor Lake)",
        },
        "igpu": {"status": "active", "name": "Intel Iris Xe"},
        "ram_gb": 16,
    }


def _check_audio_processes() -> dict:
    sc_running = _is_process_running("scsynth")
    sclang_running = _is_process_running("sclang")
    om_pid = _pid_of("python3.*om\\.py")
    pwcat_pid = _pid_of("pw-cat.*playback")
    pw_running = _is_process_running("pipewire")

    return {
        "scsynth": {"running": sc_running, "pid": _pid_of("scsynth") if sc_running else ""},
        "sclang": {"running": sclang_running, "pid": _pid_of("sclang") if sclang_running else ""},
        "om_py": {"running": bool(om_pid), "pid": om_pid},
        "pw_cat": {"running": bool(pwcat_pid), "pid": pwcat_pid},
        "pipewire": {"running": pw_running},
    }


def _check_network() -> dict:
    kernel_pid = _pid_of("python3.*kernel\\.py")
    ngrok_pid = _pid_of("ngrok.*http")
    ngrok_url = ""
    if ngrok_pid:
        try:
            import urllib.request
            import json
            with urllib.request.urlopen("http://127.0.0.1:4040/api/tunnels", timeout=2) as r:
                data = json.loads(r.read())
                tunnels = data.get("tunnels", [])
                if tunnels:
                    ngrok_url = tunnels[0].get("public_url", "")
        except Exception:
            pass

    return {
        "kernel": {"running": bool(kernel_pid), "pid": kernel_pid, "port": 5000},
        "ngrok": {"running": bool(ngrok_pid), "url": ngrok_url},
        "osc_sc": {"port": 57120, "active": _is_process_running("scsynth")},
    }


def _group_capabilities() -> dict:
    caps = _load_capabilities()
    grouped = {"active": [], "ready": [], "planned": [], "blocked": []}
    for cap in caps:
        status = cap.get("status", "planned")
        entry = {
            "id": cap.get("capability_id", ""),
            "name": cap.get("name", ""),
            "entity": cap.get("entity_id", ""),
            "install_time": cap.get("install_time", ""),
            "notes": cap.get("notes", ""),
        }
        if cap.get("blocked_by"):
            entry["blocked_by"] = cap["blocked_by"]
        grouped.get(status, grouped["planned"]).append(entry)
    return grouped


def _build_recommendations(audio: dict, caps: dict) -> List[str]:
    recs = []
    if not audio.get("stable"):
        recs.append("Audio path unstable — run: ./start.sh audio")
    ready = caps.get("ready", [])
    for cap in ready[:3]:
        recs.append(f"Ready to install: {cap['name']} ({cap.get('install_time', '?')})")
    return recs


# ══════════════════════════════════════════════════════════
# VALIDATION
# ══════════════════════════════════════════════════════════

def _validate_system_state(state: dict) -> dict:
    """Ensure all required keys exist. Never returns partial data."""
    defaults = {
        "compute": {"cpu": {}, "npu": {}, "igpu": {}, "ram_gb": 0},
        "audio": {
            "path": "",
            "synthesis": "",
            "stable": False,
            "broken": [],
            "processes": {},
        },
        "network": {"kernel": {}, "ngrok": {}, "osc_sc": {}},
        "capabilities": {"active": [], "ready": [], "planned": [], "blocked": []},
        "recommendations": [],
        "session_summary": "",
        "attestation": "SYNTHESIS",
    }
    for key, default in defaults.items():
        if key not in state or state[key] is None:
            state[key] = default
        elif isinstance(default, dict) and isinstance(state[key], dict):
            for dk, dv in default.items():
                if dk not in state[key]:
                    state[key][dk] = dv
    return state


def _validate_audio_route(route: dict) -> dict:
    defaults = {
        "primary": "",
        "synthesis": "",
        "connect_commands": [],
        "fallback": "",
        "broken": [],
        "attestation": "SYNTHESIS",
    }
    for key, default in defaults.items():
        if key not in route or route[key] is None:
            route[key] = default
    return route


# ══════════════════════════════════════════════════════════
# PUBLIC API
# ══════════════════════════════════════════════════════════

def derive_system_state() -> dict:
    """Full system snapshot: compute, audio, network, capabilities.

    Reads system_topology.csv + capability_map.csv, probes running processes.
    Returns validated dict — all keys guaranteed present.
    """
    compute = _check_compute()
    procs = _check_audio_processes()
    network = _check_network()
    caps = _group_capabilities()

    # Determine current audio path
    om_live = procs["om_py"]["running"] and procs["pw_cat"]["running"]
    sc_live = procs["scsynth"]["running"]

    if om_live:
        audio_path = "om.py → pw-cat → PipeWire → MOTU M2"
        audio_stable = True
    elif sc_live:
        audio_path = "SC → PipeWire (JACK shim — unstable)"
        audio_stable = False
    else:
        audio_path = "no audio output"
        audio_stable = False

    synthesis = "SC → OSC → om.py" if sc_live else "om.py (standalone)"

    audio = {
        "path": audio_path,
        "synthesis": synthesis,
        "stable": audio_stable,
        "broken": ["SC → pw-jack → MOTU (PW 1.2.6 JACK shim silent)"],
        "processes": procs,
    }

    recs = _build_recommendations(audio, caps)

    # Session summary
    parts = []
    if audio_stable:
        parts.append("audio:ok")
    else:
        parts.append("audio:DOWN")
    if network["kernel"]["running"]:
        parts.append(f"kernel:5000")
    if network["ngrok"]["url"]:
        parts.append("ngrok:up")
    active_count = len(caps.get("active", []))
    ready_count = len(caps.get("ready", []))
    parts.append(f"{active_count} active/{ready_count} ready")
    summary = " · ".join(parts)

    state = {
        "compute": compute,
        "audio": audio,
        "network": network,
        "capabilities": caps,
        "recommendations": recs,
        "session_summary": summary,
        "attestation": "SYNTHESIS",
    }
    return _validate_system_state(state)


def derive_audio_route(system_state: dict = None) -> dict:
    """Find stable audio path: synthesis → output.

    Prefers native PipeWire over JACK shim. Returns primary path,
    exact shell commands to establish connections, and fallbacks.

    Args:
        system_state: optional — if None, probes live processes.

    Returns:
        Validated dict with primary, synthesis, connect_commands,
        fallback, broken, attestation. All keys guaranteed.
    """
    procs = (system_state or {}).get("audio", {}).get("processes")
    if procs is None:
        procs = _check_audio_processes()

    om_live = procs.get("om_py", {}).get("running", False)
    sc_live = procs.get("scsynth", {}).get("running", False)

    # Score each route
    primary = None
    fallback = None
    broken = []

    for route in _AUDIO_ROUTES:
        if route["stability"] == "broken":
            broken.append(route["label"])
            continue

        # Check if dependencies are running
        viable = True
        for step in route["steps"]:
            if step == "om_py" and not om_live:
                viable = False
            elif step == "sc_synthesis" and not sc_live:
                viable = False
            elif step == "pipewire" and not procs.get("pipewire", {}).get("running", True):
                viable = False

        if viable and route.get("native_pipewire"):
            primary = route
        elif viable:
            fallback = route

    if primary is None and fallback is not None:
        primary = fallback
        fallback = None

    result = {
        "primary": primary["label"] if primary else "",
        "synthesis": "SC → OSC → om.py" if sc_live else "om.py (standalone)",
        "connect_commands": primary["connect_commands"] if primary else [],
        "fallback": fallback["label"] if fallback else "",
        "broken": broken,
        "attestation": "SYNTHESIS",
    }
    return _validate_audio_route(result)


def check_audio_connections() -> dict:
    """Check current PipeWire connections for audio ports.

    Returns:
        {connected: [(src, sink)], missing: [str], broken: [str]}
    """
    connections = _pw_link_connections()
    outputs = _pw_link_outputs()

    connected = []
    missing = []
    broken = []

    # Check pw-cat → MOTU
    pwcat_fl = False
    pwcat_fr = False
    sc_fl = False
    sc_fr = False

    for src, sink in connections:
        if "pw-cat" in src and "playback_FL" in sink:
            pwcat_fl = True
            connected.append((src, sink))
        elif "pw-cat" in src and "playback_FR" in sink:
            pwcat_fr = True
            connected.append((src, sink))
        elif "SuperCollider" in src and "playback_FL" in sink:
            sc_fl = True
            connected.append((src, sink))
        elif "SuperCollider" in src and "playback_FR" in sink:
            sc_fr = True
            connected.append((src, sink))

    # pw-cat connections
    has_pwcat = any("pw-cat" in o for o in outputs)
    if has_pwcat:
        if not pwcat_fl:
            missing.append("pw-cat:output_FL → MOTU:playback_FL")
        if not pwcat_fr:
            missing.append("pw-cat:output_FR → MOTU:playback_FR")

    # SC connections (broken path, note it)
    has_sc = any("SuperCollider" in o for o in outputs)
    if has_sc and (sc_fl or sc_fr):
        broken.append("SC → MOTU connected but audio silent (PW JACK shim bug)")

    return {
        "connected": [(s, k) for s, k in connected],
        "missing": missing,
        "broken": broken,
    }


def restore_audio_connections() -> bool:
    """Restore audio connections using the best available route.

    Calls derive_audio_route(), runs connect_commands, verifies.
    Returns True if audio path is live.
    """
    route = derive_audio_route()

    # Run connect commands
    for cmd in route.get("connect_commands", []):
        _run(cmd, timeout=5.0)

    # For the primary om.py → pw-cat path, pw-cat --target handles
    # routing automatically. We just need to verify the processes exist.
    procs = _check_audio_processes()
    om_live = procs["om_py"]["running"] and procs["pw_cat"]["running"]
    pw_live = procs["pipewire"]["running"]

    if om_live and pw_live:
        # Verify connections
        status = check_audio_connections()
        return len(status["missing"]) == 0

    return False
