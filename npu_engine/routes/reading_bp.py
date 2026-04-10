"""reading_bp.py — Card and reading routes.

Extracted from kernel.py (RTE-005).
"""
from flask import Blueprint, jsonify, request

reading_bp = Blueprint('reading', __name__)


# ── Card routes ─────────────────────────────

@reading_bp.route("/card/draw", methods=["POST"])
def _card_draw():
    from kernel import field_state
    from npu_engine.card_engine import CardEngine
    data = request.get_json(silent=True) or {}
    engine = CardEngine()
    cards = engine.draw_spread(
        n=int(data.get("n", 3)),
        deck=data.get("deck", "mixed"),
        field_state=field_state(),
        natal=data.get("natal"),
    )
    return jsonify({"cards": [c.to_dict() for c in cards]})


@reading_bp.route("/card/spread", methods=["POST"])
def _card_spread_post():
    from kernel import field_state
    from npu_engine.card_engine import CardEngine
    data = request.get_json(silent=True) or {}
    engine = CardEngine()
    spread = engine.resonance_spread(
        field_state=field_state(),
        natal=data.get("natal"),
        intention=data.get("intention", ""),
    )
    result = engine.apply_approach(spread, data.get("approach", "jijnasu"))
    return jsonify(result)


@reading_bp.route("/card/deck/<deck>")
def _card_deck(deck):
    from npu_engine.card_engine import CardEngine
    engine = CardEngine()
    return jsonify({"deck": deck, "cards": engine.get_deck(deck)})


# ── Reading routes ─────────────────────────────

@reading_bp.route("/reading", methods=["POST"])
def _reading():
    from kernel import field_state
    from npu_engine.field.reading_engine import derive_reading
    data = request.get_json(force=True, silent=True) or {}
    lens = data.get("lens", "bandhu")
    intention = data.get("intention", "")
    fs = field_state()
    return jsonify(derive_reading(lens, fs, intention=intention))


@reading_bp.route("/reading/tarot")
def _reading_tarot():
    from kernel import field_state
    from npu_engine.field.reading_engine import derive_reading
    return jsonify(derive_reading("tarot", field_state()))


@reading_bp.route("/reading/iching")
def _reading_iching():
    from kernel import field_state
    from npu_engine.field.reading_engine import derive_reading
    return jsonify(derive_reading("iching", field_state()))


@reading_bp.route("/reading/bandhu")
def _reading_bandhu():
    from kernel import field_state
    from npu_engine.field.reading_engine import derive_reading
    intention = request.args.get("intention", "")
    return jsonify(derive_reading("bandhu", field_state(), intention=intention))


@reading_bp.route("/reading/context")
def _reading_context():
    from kernel import field_state
    from npu_engine.field.reading_engine import build_reading_context
    ctx = build_reading_context(field_state())
    ctx.pop("field_state", None)  # too large for debug response
    return jsonify(ctx)
