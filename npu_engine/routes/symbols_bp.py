"""symbols_bp.py — Symbol, glyph, and ring routes.

Extracted from kernel.py as the first blueprint (RTE-005).
"""
from flask import Blueprint, jsonify, request

symbols_bp = Blueprint('symbols', __name__)


# ── Symbol engine routes ─────────────────────────────

@symbols_bp.route("/symbol/<path:symbol>")
def _symbol_lookup(symbol):
    from npu_engine.field.symbol_engine import lookup_symbol
    result = lookup_symbol(symbol)
    if result:
        return jsonify(result)
    return jsonify({"error": "not found", "symbol": symbol}), 404


@symbols_bp.route("/symbols/field")
def _symbols_field():
    from kernel import field_state
    from npu_engine.field.symbol_engine import field_symbols
    return jsonify(field_symbols(field_state()))


@symbols_bp.route("/symbols/stats")
def _symbols_stats():
    from npu_engine.field.symbol_engine import stats
    return jsonify(stats())


# ── Canonical Glyphs ─────────────────────────────

@symbols_bp.route("/glyphs/field")
def _glyphs_field():
    from kernel import field_state
    from npu_engine.field.symbol_engine import field_glyphs
    return jsonify(field_glyphs(field_state()))


@symbols_bp.route("/glyphs/all")
def _glyphs_all():
    from npu_engine.field.symbol_engine import get_all_glyphs
    return jsonify(get_all_glyphs())


@symbols_bp.route("/glyphs/<path:entity_id>")
def _glyph_lookup(entity_id):
    from npu_engine.field.symbol_engine import get_glyph
    return jsonify(get_glyph(entity_id))


# ── Rings ─────────────────────────────

@symbols_bp.route('/rings')
def rings():
    try:
        from kernel import field_state
        from npu_engine.field.ring_engine import derive_all_rings
        fs = field_state()
        return jsonify(derive_all_rings(fs))
    except Exception as e:
        return jsonify({'error': str(e)})


@symbols_bp.route('/ring/<ring_id>')
def ring(ring_id):
    try:
        from kernel import field_state
        from npu_engine.field.ring_engine import derive_ring_spec
        fs = field_state()
        return jsonify(derive_ring_spec(ring_id, fs))
    except Exception as e:
        return jsonify({'error': str(e)})
