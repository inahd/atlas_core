"""
yantra_generator.py — Generate Sri Yantra SVG from field state.

Nine interlocking triangles mapped to the current astronomical moment.
Active nakshatra's triangle glows, co-triangulars at medium, others dim.
Tithi maps to petal position. Bindu breathes with coherence (ψ).

All fills solid hex. No rgba. No opacity.
"""

import math
from typing import Dict, List, Tuple

# ── Triangle colors (from VISUAL_STANDARDS graha palette) ────
TRIANGLE_COLORS = {
    "shakti_satya":    "#a0d8f0",  # Candra — silver-blue
    "shakti_treta":    "#d890e0",  # Shukra — rose-violet
    "shakti_dvapara":  "#f0a060",  # Guru — amber
    "shakti_kali":     "#c8a96e",  # Ketu — smoky ochre
    "shiva_satya":     "#FFB300",  # Surya — gold
    "shiva_treta":     "#f0d090",  # Guru — warm gold
    "shiva_dvapara_1": "#80e0b0",  # Budha — jade green
    "shiva_dvapara_2": "#90b0f0",  # Shani — slate blue
    "shiva_kali":      "#e08080",  # Mangala — crimson
}

# Dim versions of the colors (for inactive triangles)
def _dim(hex_color: str) -> str:
    """Darken a hex color to ~20% brightness for dim state."""
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    return f"#{r//5:02x}{g//5:02x}{b//5:02x}"

def _mid(hex_color: str) -> str:
    """Bring a hex color to ~40% brightness for medium state."""
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    return f"#{r*2//5:02x}{g*2//5:02x}{b*2//5:02x}"


# ── Triangle definitions ────────────────────────────────────
# Scale factors for each triangle (fraction of base radius R)
# Shakti triangles point DOWN, Shiva triangles point UP

TRIANGLES = [
    # (name, polarity, scale, yuga)
    ("shakti_satya",    "shakti", 0.95, "Satya"),
    ("shiva_satya",     "shiva",  0.95, "Satya"),
    ("shakti_treta",    "shakti", 0.80, "Treta"),
    ("shiva_treta",     "shiva",  0.75, "Treta"),
    ("shakti_dvapara",  "shakti", 0.65, "Dvapara"),
    ("shiva_dvapara_1", "shiva",  0.60, "Dvapara"),
    ("shiva_dvapara_2", "shiva",  0.45, "Dvapara"),
    ("shakti_kali",     "shakti", 0.50, "Kali"),
    ("shiva_kali",      "shiva",  0.28, "Kali"),
]


def _triangle_points(cx: float, cy: float, scale: float, R: float,
                     polarity: str) -> List[Tuple[float, float]]:
    """Compute 3 vertices of a triangle at given scale."""
    s = scale * R
    if polarity == "shakti":
        # Points down — apex at bottom
        return [
            (cx, cy + s * 0.95),
            (cx - s * 0.82, cy - s * 0.48),
            (cx + s * 0.82, cy - s * 0.48),
        ]
    else:
        # Points up — apex at top
        return [
            (cx, cy - s * 0.95),
            (cx - s * 0.82, cy + s * 0.48),
            (cx + s * 0.82, cy + s * 0.48),
        ]


def _petal_path(cx: float, cy: float, r: float, angle: float,
                petal_r: float) -> str:
    """Generate SVG path for one lotus petal at given angle."""
    # Petal is an ellipse pointing outward from center
    a1 = angle - 0.18
    a2 = angle + 0.18
    x1 = cx + r * math.cos(a1)
    y1 = cy + r * math.sin(a1)
    x2 = cx + r * math.cos(a2)
    y2 = cy + r * math.sin(a2)
    # Tip
    xt = cx + (r + petal_r) * math.cos(angle)
    yt = cy + (r + petal_r) * math.sin(angle)
    return f"M{x1:.1f},{y1:.1f} Q{xt:.1f},{yt:.1f} {x2:.1f},{y2:.1f}"


def generate_yantra(field_state: dict = None, width: int = 280,
                    height: int = 280) -> str:
    """Generate full Sri Yantra SVG from field state.

    Returns SVG string. All fills solid hex.
    """
    fs = field_state or {}
    cx = width / 2
    cy = height / 2
    R = min(width, height) * 0.42

    # Extract field data
    p = fs.get("panchanga", {})
    yantra_data = fs.get("yantra", {})
    active_tri = yantra_data.get("triangle", "")
    co_tris = fs.get("co_triangulars", [])
    # Normalize co-triangular names to yantra IDs
    co_tri_ids = set()
    for ct in co_tris:
        # co_tris might be nakshatra names — map via their triangle
        co_tri_ids.add(ct)  # will match if already a triangle id

    tidx = p.get("tidx", 0)
    active_petal_16 = tidx % 16
    active_petal_8 = tidx % 8
    psi = 0.5
    if isinstance(fs.get("psi"), dict):
        psi = fs["psi"].get("intensity", 0.5)

    # Devi color
    devi = p.get("devi", {})
    devi_color = "#aa77dd"
    if isinstance(devi, dict):
        devi_color = devi.get("color", "#aa77dd")

    svg_parts = []

    # ── 1. Bhupura (outer square with 4 gates) ──
    sq = R * 1.15
    gw = sq * 0.12
    gh = sq * 0.04
    svg_parts.append(
        f'<rect x="{cx-sq:.1f}" y="{cy-sq:.1f}" width="{sq*2:.1f}" height="{sq*2:.1f}" '
        f'fill="none" stroke="#1a2030" stroke-width="0.6"/>')
    # Gates (N, S, E, W)
    for gx, gy in [(cx, cy-sq-gh), (cx, cy+sq), (cx-sq-gh, cy), (cx+sq, cy)]:
        if abs(gx - cx) < 1:  # top/bottom gates
            svg_parts.append(
                f'<rect x="{gx-gw/2:.1f}" y="{gy:.1f}" width="{gw:.1f}" height="{gh:.1f}" fill="#1a2535"/>')
        else:  # left/right gates
            svg_parts.append(
                f'<rect x="{gy:.1f}" y="{gx-gw/2:.1f}" width="{gh:.1f}" height="{gw:.1f}" fill="#1a2535"/>')

    # ── 2. 16-petal lotus ──
    r16 = R * 1.08
    pr16 = R * 0.15
    for i in range(16):
        angle = (i / 16) * math.pi * 2 - math.pi / 2
        is_active = (i == active_petal_16)
        color = TRIANGLE_COLORS.get(active_tri, "#4a3a20") if is_active else "#0d1428"
        path = _petal_path(cx, cy, r16, angle, pr16)
        svg_parts.append(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="{"1.0" if is_active else "0.3"}"/>')

    # ── 3. 8-petal lotus ──
    r8 = R * 0.85
    pr8 = R * 0.12
    for i in range(8):
        angle = (i / 8) * math.pi * 2 - math.pi / 2
        is_devi = (i == active_petal_8)
        color = devi_color if is_devi else "#0a0e18"
        path = _petal_path(cx, cy, r8, angle, pr8)
        svg_parts.append(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="{"0.8" if is_devi else "0.3"}"/>')

    # ── 4-6. Nine triangles ──
    for name, polarity, scale, yuga in TRIANGLES:
        pts = _triangle_points(cx, cy, scale, R, polarity)
        points_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        color = TRIANGLE_COLORS.get(name, "#4a4a5a")

        if name == active_tri:
            # Active — full brightness, thick stroke, glow
            svg_parts.append(
                f'<polygon points="{points_str}" fill="none" '
                f'stroke="{color}" stroke-width="1.2"/>')
            # Outer glow
            glow_pts = _triangle_points(cx, cy, scale * 1.03, R, polarity)
            glow_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in glow_pts)
            svg_parts.append(
                f'<polygon points="{glow_str}" fill="none" '
                f'stroke="{color}" stroke-width="0.4"/>')
        elif name in co_tri_ids:
            # Co-triangular — medium brightness
            svg_parts.append(
                f'<polygon points="{points_str}" fill="none" '
                f'stroke="{_mid(color)}" stroke-width="0.6"/>')
        else:
            # Inactive — dim
            svg_parts.append(
                f'<polygon points="{points_str}" fill="none" '
                f'stroke="{_dim(color)}" stroke-width="0.4"/>')

    # ── 7. Inner circle ──
    svg_parts.append(
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R*0.25:.1f}" '
        f'fill="none" stroke="#2a3040" stroke-width="0.5"/>')

    # ── 8. Bindu ──
    bindu_r = 3 + (psi * 6)
    svg_parts.append(
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{bindu_r+4:.1f}" '
        f'fill="none" stroke="#f0c040" stroke-width="0.5"/>')
    svg_parts.append(
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{bindu_r:.1f}" '
        f'fill="#f0c040"/>')

    inner = "\n  ".join(svg_parts)
    return (f'<svg width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}">\n  {inner}\n</svg>')


def yantra_data_for_field(field_state: dict) -> dict:
    """Extract yantra visualization data from field state.

    Used by /shell/state and /observe to provide visual_data
    for the sri_yantra visual type.
    """
    fs = field_state or {}
    p = fs.get("panchanga", {})
    yantra = fs.get("yantra", {})
    tidx = p.get("tidx", 0)
    psi = 0.5
    if isinstance(fs.get("psi"), dict):
        psi = fs["psi"].get("intensity", 0.5)

    active_tri = yantra.get("triangle", "")
    co_tris = fs.get("co_triangulars", [])

    return {
        "active_triangle": active_tri,
        "co_triangulars": co_tris,
        "triangle_color": TRIANGLE_COLORS.get(active_tri, "#4a4a5a"),
        "vastu_direction": yantra.get("compass", ""),
        "active_tithi_petal": tidx % 16,
        "devi_petal": tidx % 8,
        "psi": psi,
        "polarity": yantra.get("polarity", ""),
        "yuga": yantra.get("yuga", ""),
        # Full color map for shell SVG renderer
        "triangle_colors": TRIANGLE_COLORS,
    }
