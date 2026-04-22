"""
nitya_bp.py — Flask blueprint for Nitya Devi routes.

Blueprint: nitya_bp, prefix: /nitya
"""

import io
from flask import Blueprint, jsonify, request, Response

nitya_bp = Blueprint("nitya_bp", __name__, url_prefix="/nitya")


@nitya_bp.route("/devi/today")
def devi_today():
    """Current Nitya Devi from live field state."""
    from npu_engine.nitya.devi_engine import get_current_devi

    # Get field state from kernel
    try:
        import kernel
        fs = kernel.field_state()
    except Exception:
        fs = {'panchanga': {'tidx': 0}}

    devi = get_current_devi(fs)
    return jsonify(devi)


@nitya_bp.route("/devi/<int:tithi>")
def devi_by_tithi(tithi):
    """Specific Nitya Devi by tithi number (1-30)."""
    from npu_engine.nitya.devi_engine import get_devi_by_tithi
    if tithi < 1 or tithi > 30:
        return jsonify({"error": "tithi must be 1-30"}), 400
    return jsonify(get_devi_by_tithi(tithi))


@nitya_bp.route("/field/<int:tithi>")
def devi_field(tithi):
    """Render quasicrystal field for a tithi as JSON intensity array."""
    from npu_engine.nitya.devi_engine import render_devi_field

    k = request.args.get('k', type=float)
    size = request.args.get('size', 256, type=int)
    size = min(size, 1024)  # cap at 1024

    field = render_devi_field(tithi, k=k, size=size)

    # Return as flat list for canvas rendering
    return jsonify({
        "tithi": tithi,
        "size": size,
        "field": field.ravel().tolist(),
    })


@nitya_bp.route("/field/<int:tithi>/png")
def devi_field_png(tithi):
    """Render quasicrystal field as PNG image."""
    from npu_engine.nitya.devi_engine import render_devi_field, get_devi_by_tithi

    k = request.args.get('k', type=float)
    size = request.args.get('size', 512, type=int)
    size = min(size, 1024)

    field = render_devi_field(tithi, k=k, size=size)
    devi = get_devi_by_tithi(tithi)
    color_hex = devi.get('color_hex', '#c8a96e')

    # Convert to PNG via numpy → PIL
    try:
        from PIL import Image
        # Map field to RGB using devi color
        r_base = int(color_hex[1:3], 16) if len(color_hex) >= 7 else 200
        g_base = int(color_hex[3:5], 16) if len(color_hex) >= 7 else 169
        b_base = int(color_hex[5:7], 16) if len(color_hex) >= 7 else 110

        img_array = np.zeros((size, size, 3), dtype=np.uint8)
        img_array[:, :, 0] = (field * r_base).astype(np.uint8)
        img_array[:, :, 1] = (field * g_base).astype(np.uint8)
        img_array[:, :, 2] = (field * b_base).astype(np.uint8)

        img = Image.fromarray(img_array)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return Response(buf.getvalue(), mimetype='image/png')
    except ImportError:
        return jsonify({"error": "PIL not installed for PNG rendering"}), 500


@nitya_bp.route("/srichakra")
def sri_chakra():
    """Full Sri Yantra field — all 15 Nitya contributions superposed."""
    from npu_engine.geometry.cut_and_project import project_sri_yantra

    k = request.args.get('k', 1.0, type=float)
    size = request.args.get('size', 256, type=int)
    size = min(size, 1024)

    field = project_sri_yantra(k=k, size=size)

    return jsonify({
        "size": size,
        "field": field.ravel().tolist(),
    })


# Need numpy for PNG route
try:
    import numpy as np
except ImportError:
    pass
