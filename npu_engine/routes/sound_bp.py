"""sound_bp.py — Sound, bija, and OSC control routes.

Extracted from kernel.py (RTE-005).
Mutable state (_sound_mode, _perform_mode) lives in _sound_state.py.
"""
import json
import os
from datetime import datetime
from pathlib import Path

from flask import Blueprint, Response, jsonify, request, send_file

from npu_engine.routes._sound_state import send_osc
import npu_engine.routes._sound_state as _ss

sound_bp = Blueprint('sound', __name__)


# ── Sound spec ─────────────────────────────

@sound_bp.route("/sound/spec")
def _sound_spec():
    """Graph-computed sound specification. The descent: eternal -> material."""
    from kernel import _json_serial, field_state
    try:
        from npu_engine.graph_engine import GraphEngine
        g = GraphEngine()
        fs = field_state()
        spec = g.get_soundspec(fs)
        try:
            from npu_engine.field.chandas_engine import derive_chandas
            spec['chandas'] = derive_chandas(fs)
        except Exception:
            pass
        try:
            from npu_engine.tanpura_field import derive_tanpura_params
            spec['tanpura'] = derive_tanpura_params(fs)
        except Exception:
            pass
        return Response(
            json.dumps(spec, default=_json_serial, ensure_ascii=False),
            mimetype="application/json",
        )
    except Exception as exc:
        return Response(
            json.dumps({"error": str(exc)}), mimetype="application/json",
        )


# ── Bija playback ─────────────────────────────

def _play_bija_async(bija_id, dur=3.0):
    """Play bija through sounddevice in a background thread."""
    import threading
    def _play():
        try:
            import sounddevice as sd
            from kernel import field_state
            from npu_engine.bija_synth import synthesize_bija
            fs = field_state()
            audio = synthesize_bija(bija_id, fs, duration_s=dur)
            sd.play(audio, 48000)
        except Exception as e:
            print(f"  bija play error: {e}")
    threading.Thread(target=_play, daemon=True).start()


@sound_bp.route("/bija/<bija_id>/play", methods=["POST", "GET"])
def _bija_play(bija_id):
    """Play bija through server speakers (M2). Returns immediately."""
    dur = float(request.args.get("duration", 3.0))
    _play_bija_async(bija_id, dur)
    return Response(
        json.dumps({"playing": True, "bija": bija_id, "duration": dur}),
        mimetype="application/json",
    )


@sound_bp.route("/bija/<bija_id>/synthesize", methods=["POST", "GET"])
def _bija_synthesize(bija_id):
    """Synthesize a bija mantra. Returns audio/wav OR plays server-side."""
    from kernel import field_state
    mode = request.args.get("mode", "wav")
    if mode == "play":
        dur = float(request.args.get("duration", 3.0))
        _play_bija_async(bija_id, dur)
        return Response(
            json.dumps({"playing": True, "bija": bija_id}),
            mimetype="application/json",
        )
    try:
        import io, wave, numpy as np
        from npu_engine.bija_synth import synthesize_bija
        fs = field_state()
        dur = float(request.args.get("duration", 3.0))
        audio = synthesize_bija(bija_id, fs, duration_s=dur)
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(48000)
            wf.writeframes((audio * 32767).astype(np.int16).tobytes())
        buf.seek(0)
        return send_file(buf, mimetype='audio/wav',
                         download_name=f'{bija_id}.wav')
    except Exception as exc:
        return Response(
            json.dumps({"error": str(exc)}), mimetype="application/json",
        )


# ── Volume ─────────────────────────────

@sound_bp.route("/sound/volume", methods=["GET", "POST"])
def _sound_volume():
    """Master volume control. Reads/writes /tmp/om_volume.json."""
    vol_path = Path("/tmp/om_volume.json")
    max_vol = 0.75
    if request.method == "GET":
        vol = 0.0
        try:
            if vol_path.exists():
                vol = float(json.loads(vol_path.read_text()).get("volume", 0))
        except Exception:
            pass
        return jsonify({"volume": round(vol, 3), "max": max_vol})
    data = request.get_json(force=True) if request.data else {}
    v = max(0.0, min(max_vol, float(data.get("volume", 0))))
    try:
        vol_path.write_text(json.dumps({"volume": round(v, 3)}))
    except Exception:
        pass
    return jsonify({"volume": round(v, 3)})


# ── Sound state ─────────────────────────────

@sound_bp.route("/sound/sc_ready", methods=["POST", "GET"])
def _sound_sc_ready():
    """SuperCollider readiness endpoint. POST from start_atlas.sh, GET to query."""
    if request.method == "POST":
        _ss.sc_state.update(request.get_json(force=True) or {})
        return jsonify({"ok": True, "state": _ss.sc_state})
    return jsonify(_ss.sc_state)


@sound_bp.route("/sound/sc_boot", methods=["POST"])
def _sound_sc_boot():
    """Send initial field tanpura params to running SC engine via OSC.

    Instantiates/updates the tanpura Synth with current field Sa frequency.
    Call after start_sc.sh has booted scsynth + sclang.
    """
    from kernel import field_state
    try:
        fs = field_state()
        ss = fs.get("sound_state", {})
        sa_hz = ss.get("sa_hz", 130.81)
        if isinstance(sa_hz, str):
            try:
                sa_hz = float(sa_hz)
            except ValueError:
                sa_hz = 130.81

        # Send field params to SC via OSC
        send_osc("/atlas/tanpura/sa", [sa_hz])
        send_osc("/atlas/tanpura/jivari", [0.40])
        send_osc("/atlas/tanpura/amp", [1.0])

        # Update SC state
        _ss.sc_state["status"] = "booted"
        _ss.sc_state["sa_hz"] = sa_hz

        return jsonify({"booted": True, "sa_hz": sa_hz, "osc_port": 57120})
    except Exception as e:
        return jsonify({"booted": False, "error": str(e)}), 500


@sound_bp.route("/sound/state")
def _sound_state():
    """Current sound engine state via derive_sound_spec."""
    from kernel import _derive_sound_state, _json_serial, field_state
    fs = field_state()
    try:
        from npu_engine.sound.sound_engine import derive_sound_spec
        spec = derive_sound_spec(fs, _ss.sound_mode)
        inline = _derive_sound_state(fs)
        spec["raga_detail"] = {
            "notes": inline.get("raga_notes", []),
            "aroha": inline.get("raga_aroha", []),
            "avaroha": inline.get("raga_avaroha", []),
            "vadi": inline.get("raga_vadi", ""),
            "samvadi": inline.get("raga_samvadi", ""),
        }
        spec["tala_detail"] = {
            "name": inline.get("tala", ""),
            "beats": inline.get("tala_beats", 8),
            "bols": inline.get("tala_bols", []),
        }
        payload = spec
    except Exception:
        payload = fs.get("sound_state", _derive_sound_state(fs))
    payload["sc"] = _ss.sc_state
    return Response(
        json.dumps(payload, default=_json_serial, ensure_ascii=False),
        mimetype="application/json",
    )


# ── Relational sound ─────────────────────────────

@sound_bp.route("/sound/relational")
def _sound_relational():
    """Relational sound law. Delegated to RelationalEngine."""
    from kernel import _json_serial, _relational, field_state
    fs = field_state()
    if _relational:
        payload = _relational.sound_state(fs)
    else:
        payload = {"error": "RelationalEngine not available"}
    return Response(
        json.dumps(payload, default=_json_serial, ensure_ascii=False),
        mimetype="application/json",
    )


# ── OSC control endpoints ─────────────────────────────

@sound_bp.route("/sound/raga", methods=["POST"])
def _sound_raga():
    """Set active raga — compute full sound spec and send via OSC bridge."""
    from kernel import _json_serial, field_state
    data = request.get_json(force=True) if request.data else {}
    raga = data.get("raga", "Yaman")
    duration = float(data.get("duration", 0))
    try:
        from npu_engine.sound.sound_engine import derive_sound_spec
        from npu_engine.sound.osc_bridge import send_sound_spec
        fs = field_state()
        spec = derive_sound_spec(fs, _ss.sound_mode)
        spec["raga"] = raga
        osc_ok = send_sound_spec(spec)
        return Response(
            json.dumps({
                "sent": osc_ok, "raga": raga,
                "sa_hz": spec.get("sa_hz"),
                "mode": spec.get("mode"),
                "layers": spec.get("layers"),
                "master": spec.get("master"),
            }, default=_json_serial, ensure_ascii=False),
            mimetype="application/json",
        )
    except Exception:
        semis = data.get("semis", [0, 2, 4, 6, 7, 9, 11])
        send_osc("/atlas/raga", [raga] + [int(s) for s in semis])
        return Response(
            json.dumps({"sent": True, "raga": raga, "fallback": True}, ensure_ascii=False),
            mimetype="application/json",
        )


@sound_bp.route("/sound/play_note", methods=["POST"])
def _sound_play_note():
    data = request.get_json(force=True)
    semi = int(data.get("semi", 0))
    octave = int(data.get("octave", 0))
    vel = float(data.get("vel", 0.7))
    dur = float(data.get("dur", 0.5))
    sa = 261.63 * (2 ** octave)
    freq = sa * (2 ** (semi / 12))
    send_osc("/melody", [freq, dur, vel, 0.0])
    return Response(
        json.dumps({"freq": freq, "sent": True}, ensure_ascii=False),
        mimetype="application/json",
    )


@sound_bp.route("/sound/voice", methods=["POST"])
def _sound_voice():
    data = request.get_json(force=True)
    vtype = data.get("type", "konnakol")
    syllable = data.get("syllable", "ta")
    if vtype == "konnakol":
        send_osc("/voice", [syllable.lower(), 0.0, 0.3])
    elif vtype == "bol":
        send_osc("/atlas/rhythm/bol", [syllable, 0.8, 0])
    elif vtype == "mantra":
        send_osc("/atlas/bija", ["aum", "aum", "aum"])
    return Response(
        json.dumps({"sent": True}, ensure_ascii=False),
        mimetype="application/json",
    )


@sound_bp.route("/sound/mantra", methods=["POST"])
def _sound_mantra():
    """Bija mantra synthesis — returns formant decomposition and sends OSC."""
    from kernel import _json_serial, field_state
    data = request.get_json(force=True) if request.data else {}
    action = data.get("action", "start")
    if action == "stop":
        send_osc("/atlas/stop", [])
        return Response(
            json.dumps({"action": "stop", "sent": True}, ensure_ascii=False),
            mimetype="application/json",
        )
    try:
        from npu_engine.bija_synth import BIJA_PATH, VARNA
        from npu_engine.field_to_sound import field_to_sound
        fs = field_state()
        fts = field_to_sound(fs)
        bija = data.get("bija", fts.get("bija", "om"))
        sa_hz = fts.get("sa_hz", 261.63)
        path = BIJA_PATH.get(bija.lower(), [(ch.upper(), 1.0) for ch in bija.lower()])
        varnas = []
        for varna_key, weight in path:
            v = VARNA.get(varna_key, VARNA.get("A", {}))
            varnas.append({
                "varna": varna_key, "weight": weight,
                "f1_hz": v.get("f1", 700), "f2_hz": v.get("f2", 1100),
                "f3_hz": v.get("f3", 2800), "source_type": v.get("src", "vowel"),
            })
        send_osc("/atlas/field", [sa_hz, 72, 0, 0, 1.125, 1])
        return Response(
            json.dumps({
                "bija": bija, "sa_hz": sa_hz,
                "element": fts.get("element", "ether"),
                "guna": fts.get("guna", "sattva"),
                "varnas": varnas, "osc_sent": True,
            }, default=_json_serial, ensure_ascii=False),
            mimetype="application/json",
        )
    except Exception:
        send_osc("/atlas/field", [261.63, 72, 0, 0, 1.125, 1])
        return Response(
            json.dumps({"sent": True, "fallback": True}, ensure_ascii=False),
            mimetype="application/json",
        )


@sound_bp.route("/sound/bols", methods=["POST"])
def _sound_bols():
    """Tabla bols for current tala — wired to tabla_sampler."""
    from kernel import _derive_sound_state, field_state
    data = request.get_json(force=True) if request.data else {}
    try:
        from npu_engine.tabla_sampler import _BOL_SAMPLE, _ensure_synth_samples
        fs = field_state()
        ss = fs.get("sound_state", _derive_sound_state(fs))
        bpm = int(data.get("bpm", ss.get("bpm", 72)))
        tala_bols = data.get("bols") or ss.get("tala_bols", [])
        beat_index = int(data.get("beat", 0))
        samples = _ensure_synth_samples()
        bol_str = tala_bols[beat_index % len(tala_bols)] if tala_bols else "\u2014"
        sample_key = _BOL_SAMPLE.get(bol_str.lower())
        beat_dur = 60.0 / max(bpm, 30)
        for i, bol in enumerate(tala_bols):
            send_osc("/atlas/rhythm/bol", [bol, i * beat_dur, 0.7])
        return Response(
            json.dumps({
                "tala_bols": tala_bols, "beat_index": beat_index,
                "current_bol": bol_str, "sample_key": sample_key,
                "bpm": bpm, "beat_duration": round(beat_dur, 3),
                "samples_available": sorted(samples.keys()),
                "osc_sent": len(tala_bols),
            }, ensure_ascii=False),
            mimetype="application/json",
        )
    except Exception:
        bols = data.get("bols", [])
        bpm_val = float(data.get("bpm", 72))
        beat_dur = 60.0 / bpm_val
        for i, bol in enumerate(bols):
            send_osc("/atlas/rhythm/bol", [bol, i * beat_dur, 0.7])
        return Response(
            json.dumps({"sent": len(bols), "fallback": True}, ensure_ascii=False),
            mimetype="application/json",
        )


# ── Perform mode ─────────────────────────────

@sound_bp.route("/sound/perform_mode", methods=["POST"])
def _sound_perform_mode():
    data = request.get_json(force=True)
    _ss.perform_mode = data.get("active", False)
    if _ss.perform_mode:
        send_osc("/atlas/field", [261.63, 72, 0, 0, 1.125, 0])
    else:
        send_osc("/atlas/field", [261.63, 72, 0, 0, 1.125, 1])
    return Response(
        json.dumps({"perform_mode": _ss.perform_mode}, ensure_ascii=False),
        mimetype="application/json",
    )


@sound_bp.route("/sound/perform_mode")
def _get_perform_mode():
    return Response(
        json.dumps({"perform_mode": _ss.perform_mode}, ensure_ascii=False),
        mimetype="application/json",
    )


@sound_bp.route("/sound/stop", methods=["POST"])
def _sound_stop():
    send_osc("/atlas/stop", [])
    return Response(
        json.dumps({"stopped": True}, ensure_ascii=False),
        mimetype="application/json",
    )


# ── Sound mode ─────────────────────────────

@sound_bp.route("/sound/mode", methods=["GET", "POST"])
def _sound_mode_endpoint():
    from kernel import field_state
    if request.method == "POST":
        data = request.get_json(force=True)
        new_mode = data.get("mode", "field")
        from npu_engine.sound.sound_engine import VALID_MODES
        if new_mode not in VALID_MODES:
            return Response(
                json.dumps({"error": f"invalid mode, use: {sorted(VALID_MODES)}"}),
                mimetype="application/json", status=400,
            )
        _ss.sound_mode = new_mode
        try:
            from npu_engine.sound.sound_engine import derive_sound_spec
            from npu_engine.sound.osc_bridge import send_sound_spec
            spec = derive_sound_spec(field_state(), mode=_ss.sound_mode)
            send_sound_spec(spec)
        except Exception as exc:
            return Response(
                json.dumps({"mode": _ss.sound_mode, "osc_sent": False, "error": str(exc)}),
                mimetype="application/json",
            )
        return Response(
            json.dumps({"mode": _ss.sound_mode, "osc_sent": True}),
            mimetype="application/json",
        )
    return Response(
        json.dumps({"mode": _ss.sound_mode}),
        mimetype="application/json",
    )


# ── Mix state ─────────────────────────────

@sound_bp.route("/sound/mix/state")
def _sound_mix_state():
    """Current mix layer weights for visualization."""
    from kernel import _derive_sound_state, _json_serial, field_state
    fs = field_state()
    p5 = fs.get("panchanga", {})
    ss = fs.get("sound_state") or _derive_sound_state(fs)
    nd = p5.get("nak_data", {}) or {}
    try:
        from npu_engine.mix.layer_graph import get_layer_weights
        weights = get_layer_weights(
            ss.get("rasa_primary", "shanta"),
            ss.get("arc_phase", 0.5),
            ss.get("mode", "gat"),
        )
    except Exception:
        weights = {}
    return Response(
        json.dumps({
            "layers": weights,
            "rasa": ss.get("rasa_primary", "shanta"),
            "arc": ss.get("arc_phase", 0.5),
            "element": nd.get("element", "ether"),
            "guna": nd.get("guna", "sattva"),
        }, default=_json_serial, ensure_ascii=False),
        mimetype="application/json",
    )


# ── Sound recommend ─────────────────────────────

@sound_bp.route("/sound/recommend")
def _sound_recommend():
    """Graph-traversal raga recommendation from vara, dosha, time of day."""
    from kernel import _VARA_GRAHA_NAME, _derive_sound_state, _json_serial, field_state
    fs = field_state()
    p5 = fs.get("panchanga", {})
    nd = p5.get("nak_data", {}) or {}
    ss = fs.get("sound_state") or _derive_sound_state(fs)

    h = datetime.now().hour
    if h < 6:
        samaya = "predawn"
    elif h < 10:
        samaya = "morning"
    elif h < 14:
        samaya = "afternoon"
    elif h < 18:
        samaya = "evening"
    elif h < 22:
        samaya = "night"
    else:
        samaya = "late_night"

    _graha_slug = {
        "S\u016brya": "sun", "Candra": "moon", "Ma\u1e45gala": "mars",
        "Budha": "mercury", "Guru": "jupiter", "\u015aukra": "venus", "\u015aani": "saturn",
    }
    vara_iast = _VARA_GRAHA_NAME.get(datetime.now().weekday(), "Budha")
    vara_slug = _graha_slug.get(vara_iast, "mercury")

    try:
        from npu_engine.graph_engine import GraphEngine
        g = GraphEngine()
        raga_edges = g.get_neighbors(f"graha_{vara_slug}",
                                      relation_types=["primary_raga"])
        recommended = raga_edges[0]["to_id"] if raga_edges else None

        dosha = nd.get("dosha", "vata").lower()
        therapeutic = None
        dosha_eid = f"dosha_{dosha}"
        dosha_n = g.get_neighbors(dosha_eid, exclude_inverse=False)
        ther = [e for e in dosha_n if e.get("relation") == "therapeutic_target" and e.get("inverse")]
        if ther:
            therapeutic = ther[0]["to_id"]

        time_n = g.get_neighbors(f"time_{samaya}", exclude_inverse=False)
        chandas_match = [e for e in time_n if "chandas" in e.get("to_id", "") or "chandas" in e.get("from_id", "")]

    except Exception:
        recommended = None
        therapeutic = None
        chandas_match = []

    def _clean(eid):
        return (eid or "").replace("raga_", "").replace("_", " ").title() if eid else None

    element = nd.get("element", "ether")
    guna = nd.get("guna", "sattva")
    try:
        from npu_engine.field_to_sound import get_treatment_vector
        treatment = get_treatment_vector(element, guna)
    except Exception:
        treatment = "maintain"

    payload = {
        "recommended_raga": _clean(recommended) or ss.get("raga", fs.get("devi_raga")),
        "therapeutic_raga": _clean(therapeutic),
        "current_raga": fs.get("devi_raga"),
        "time_of_day": samaya,
        "element": element,
        "dosha": nd.get("dosha", "vata"),
        "guna": guna,
        "treatment_vector": treatment,
        "vara_graha": vara_iast,
        "chandas": [e.get("to_id", e.get("from_id", "")) for e in chandas_match[:3]],
        "rationale": f"{vara_iast} day \u00b7 {nd.get('element', 'ether')} element \u00b7 {samaya} \u00b7 {nd.get('dosha', 'vata')} dosha",
    }
    return Response(
        json.dumps(payload, default=_json_serial, ensure_ascii=False),
        mimetype="application/json",
    )


@sound_bp.route("/sound/tanpura")
def _sound_tanpura():
    """Compute tanpura parameters from current field state and send to SC."""
    from kernel import _json_serial, field_state
    from npu_engine.tanpura_field import derive_tanpura_params
    fs = field_state()
    params = derive_tanpura_params(fs)

    # Build OSC messages for SuperCollider
    osc_spec = {
        "osc_messages": [
            ["/atlas/tanpura/sa", [params["sa_hz"]]],
            ["/atlas/tanpura/strings", params["string_ratios"]],
            ["/atlas/tanpura/weights", params["string_weights"]],
            ["/atlas/tanpura/cycle", [params["cycle_gap_ms"]]],
            ["/atlas/tanpura/bright", [params["bright_partial"]]],
        ]
    }

    try:
        from npu_engine.sound.osc_bridge import send_sound_spec
        osc_ok = send_sound_spec(osc_spec)
        params["osc_sent"] = osc_ok
    except Exception as e:
        params["osc_sent"] = False
        params["osc_error"] = str(e)

    return Response(
        json.dumps(params, default=_json_serial, ensure_ascii=False),
        mimetype="application/json",
    )


@sound_bp.route("/sound/freesound-key")
def _sound_freesound_key():
    key = os.environ.get("FREESOUND_API_KEY", "")
    return Response(
        json.dumps({"key": key}, ensure_ascii=False),
        mimetype="application/json",
    )
