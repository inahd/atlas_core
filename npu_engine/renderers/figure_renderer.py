"""
figure_renderer.py — Bandhu figure geometry from Shilpa Shastra.

Loads bandhu_geometry.csv (Uttama Dasatala proportions).
Derives colors/animation from field state.
Returns SVG group element.

Pattern follows ui_vastu_engine.py.
"""

import csv
import math
import os
from typing import Dict

import io

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
_GEOM_CSV = os.path.join(_ROOT, "datasets", "silpa", "bandhu_geometry.csv")
_ARCHETYPE_CSV = os.path.join(_ROOT, "datasets", "morphogenesis", "body_archetype_map.csv")
_SIGNATURE_CSV = os.path.join(_ROOT, "datasets", "morphogenesis", "doctrine_of_signatures.csv")

_geom_cache = None
_archetype_cache = None
_signature_cache = None

_GRAHA_COLORS = {
    "surya": "#FFB300", "chandra": "#E8E8FF", "mangala": "#CC2200",
    "budha": "#00AA44", "guru": "#FFDD44", "shukra": "#FFAADD",
    "shani": "#445566", "rahu": "#6600AA", "ketu": "#887755",
}


def _load_archetypes():
    global _archetype_cache
    if _archetype_cache is not None:
        return _archetype_cache
    _archetype_cache = []
    try:
        with open(_ARCHETYPE_CSV, encoding="utf-8") as f:
            _archetype_cache = list(csv.DictReader(io.StringIO(f.read().lstrip())))
    except Exception:
        pass
    return _archetype_cache

# ══════════════════════════════════════════════════════════
# TOROIDAL BREATH
# ══════════════════════════════════════════════════════════

def toroidal_breath_params(t_ms: float, breath_cycle_ms: float = 4000) -> dict:
    """Compute toroidal breath expansion at time t_ms.

    Three torus components at 120° phase offsets.
    Four breath phases: inhale (0-0.25), kumbhaka (0.25-0.5),
                        exhale (0.5-0.75), bahya (0.75-1.0).

    Returns dict with expansion values for body animation.
    """
    tau = math.pi * 2
    phase = (t_ms % breath_cycle_ms) / breath_cycle_ms  # 0..1

    # Three torus components at 120° offsets
    t1 = phase                    # primary breath
    t2 = (phase + 1 / 3) % 1.0   # lateral wave
    t3 = (phase + 2 / 3) % 1.0   # rotational micro

    # Breath envelope: smooth four-phase with easing
    # inhale rises, kumbhaka holds, exhale falls, bahya holds low
    if phase < 0.25:
        # Inhale: 0→1 (ease-in-out)
        p = phase / 0.25
        envelope = 0.5 - 0.5 * math.cos(p * math.pi)
    elif phase < 0.5:
        # Kumbhaka (retention): hold near 1.0, gentle pulse
        p = (phase - 0.25) / 0.25
        envelope = 1.0 - 0.05 * math.sin(p * math.pi)
    elif phase < 0.75:
        # Exhale: 1→0
        p = (phase - 0.5) / 0.25
        envelope = 0.5 + 0.5 * math.cos(p * math.pi)
    else:
        # Bahya kumbhaka (empty hold): near 0, gentle pulse
        p = (phase - 0.75) / 0.25
        envelope = 0.05 * math.sin(p * math.pi)

    return {
        "phase": phase,
        "envelope": envelope,         # 0..1 primary breath
        "torus_1_phase": t1,          # primary
        "torus_2_phase": t2,          # lateral sway
        "torus_3_phase": t3,          # micro-rotation
        "arm_angle": envelope * 6.0,              # degrees spread
        "hip_width": envelope * 0.8,              # base_unit multiplier
        "chest_rx": 1.0 + envelope * 0.08,        # torso rx multiplier
        "crown_lift": envelope * 1.5,             # px upward
        "spine_stretch": 1.0 + envelope * 0.02,   # torso ry multiplier
        "lateral_sway": math.sin(t2 * tau) * 0.3, # base_unit multiplier
        "micro_rot": math.sin(t3 * tau) * 1.5,    # degrees
    }


def _breath_keyframes(s: float, breath_ms: int = 4000) -> str:
    """Generate CSS @keyframes for toroidal breath animation.

    Returns <style> block with keyframes for body, chest, crown, arms, hips.
    s = base_unit (2.8).
    """
    steps = 11  # 0%, 10%, 20% ... 100%
    # Collect per-step values
    body_kf = []   # translateX, rotate
    chest_kf = []  # scaleX
    crown_kf = []  # translateY
    arm_l_kf = []  # rotate
    arm_r_kf = []  # rotate
    hip_kf = []    # scaleX

    for i in range(steps):
        pct = i * 10
        t_ms = (pct / 100.0) * breath_ms
        bp = toroidal_breath_params(t_ms, breath_ms)

        sway_px = bp["lateral_sway"] * s
        rot = bp["micro_rot"]
        body_kf.append(f"{pct}%{{transform:translate({sway_px:.2f}px,0) rotate({rot:.2f}deg)}}")

        chest_kf.append(f"{pct}%{{transform:scaleX({bp['chest_rx']:.4f}) scaleY({bp['spine_stretch']:.4f})}}")

        crown_kf.append(f"{pct}%{{transform:translateY({-bp['crown_lift']:.2f}px)}}")

        arm_l_kf.append(f"{pct}%{{transform:rotate({-bp['arm_angle']:.2f}deg)}}")
        arm_r_kf.append(f"{pct}%{{transform:rotate({bp['arm_angle']:.2f}deg)}}")

        hip_kf.append(f"{pct}%{{transform:scaleX({1.0 + bp['hip_width'] * 0.06:.4f})}}")

    dur = f"{breath_ms / 1000:.1f}s"
    ease = "ease-in-out"
    inf = "infinite"

    style = "<style>\n"
    style += f"@keyframes bnd-body{{{' '.join(body_kf)}}}\n"
    style += f"@keyframes bnd-chest{{{' '.join(chest_kf)}}}\n"
    style += f"@keyframes bnd-crown{{{' '.join(crown_kf)}}}\n"
    style += f"@keyframes bnd-arm-l{{{' '.join(arm_l_kf)}}}\n"
    style += f"@keyframes bnd-arm-r{{{' '.join(arm_r_kf)}}}\n"
    style += f"@keyframes bnd-hip{{{' '.join(hip_kf)}}}\n"
    style += f".bnd-body{{animation:bnd-body {dur} {ease} {inf};transform-origin:center center}}\n"
    style += f".bnd-chest{{animation:bnd-chest {dur} {ease} {inf};transform-origin:center center}}\n"
    style += f".bnd-crown{{animation:bnd-crown {dur} {ease} {inf};transform-origin:center center}}\n"
    style += f".bnd-arm-l{{animation:bnd-arm-l {dur} {ease} {inf}}}\n"
    style += f".bnd-arm-r{{animation:bnd-arm-r {dur} {ease} {inf}}}\n"
    style += f".bnd-hip{{animation:bnd-hip {dur} {ease} {inf};transform-origin:center center}}\n"
    style += "</style>\n"
    return style


_ELEM_LINE = {"earth": 2.0, "water": 1.5, "air": 1.0, "fire": 1.8, "ether": 1.3}
_GUNA_SPEED = {"rajas": 1.0, "sattva": 0.7, "tamas": 1.3}
_PHASE_POSE = {"birth": "standing", "formation": "walking", "dissolution": "seated", "pralaya": "bowing"}


def _load_geom():
    global _geom_cache
    if _geom_cache is not None:
        return _geom_cache
    _geom_cache = {}
    try:
        with open(_GEOM_CSV, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                _geom_cache[row.get("measure", "")] = row
    except Exception:
        pass
    return _geom_cache


def _val(key, default=0.0):
    g = _load_geom()
    try:
        return float(g.get(key, {}).get("parts", default))
    except (ValueError, TypeError):
        return default


def _validate(spec):
    defaults = {
        "scale_unit": 1.0,
        "segments": {},
        "colors": {"skin": "#c8a06e", "cloth": "#2a5a4a", "accent": "#c8c8d8", "tilaka": "#c8a96e"},
        "line_weight": 1.5,
        "animation": {"speed": 1.0, "breath_amplitude": 2.0, "walk_cycle_ms": 2000},
        "pose": "idle",
        "attestation": "OBSERVED:PRIMARY_TEXT",
    }
    for k, v in defaults.items():
        if k not in spec or spec[k] is None:
            spec[k] = v
    return spec


def derive_bandhu_geometry(field_state: dict, pose: str = "idle") -> dict:
    """Derive Bandhu figure geometry from Shilpa proportions + field state. Never raises."""
    try:
        total = _val("total_height", 124)
        face = _val("face", 13)
        arm = _val("arm", 17)
        thigh = _val("thigh", 27)
        lower_leg = _val("lower_leg", 27)
        neck = _val("neck", 4.5)
        torso = total - face - neck - thigh - lower_leg - 4  # remainder

        p5 = field_state.get("panchanga", {})
        element = p5.get("element", "ether").lower()
        guna = p5.get("guna", "sattva").lower()
        lifecycle = field_state.get("lifecycle", {})
        phase = lifecycle.get("phase", "formation")

        # Override pose from lifecycle
        if pose == "idle":
            pose = _PHASE_POSE.get(phase, "standing")

        # Scale: 1 tala = face height in pixels (adapt to canvas later)
        scale_unit = face

        segments = {
            "head": {"h": face, "w": face * 0.85},
            "neck": {"h": neck, "w": face * 0.35},
            "torso": {"h": torso, "w": face * 1.1},
            "upper_arm_l": {"h": arm, "w": face * 0.25},
            "upper_arm_r": {"h": arm, "w": face * 0.25},
            "lower_arm_l": {"h": arm, "w": face * 0.22},
            "lower_arm_r": {"h": arm, "w": face * 0.22},
            "thigh_l": {"h": thigh, "w": face * 0.35},
            "thigh_r": {"h": thigh, "w": face * 0.35},
            "lower_leg_l": {"h": lower_leg, "w": face * 0.28},
            "lower_leg_r": {"h": lower_leg, "w": face * 0.28},
        }

        return _validate({
            "scale_unit": scale_unit,
            "segments": segments,
            "colors": {"skin": "#c8a06e", "cloth": "#2a5a4a", "accent": "#c8c8d8", "tilaka": "#c8a96e"},
            "line_weight": _ELEM_LINE.get(element, 1.5),
            "animation": {
                "speed": _GUNA_SPEED.get(guna, 1.0),
                "breath_amplitude": 2.0,
                "walk_cycle_ms": 2000,
            },
            "pose": pose,
            "attestation": "OBSERVED:PRIMARY_TEXT",
        })
    except Exception:
        return _validate({})


def _limb(cx, cy, rx, ry, angle, fill, stroke, lw):
    """SVG ellipse rotated around its center."""
    return (f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{lw:.1f}" '
            f'transform="rotate({angle:.1f},{cx:.1f},{cy:.1f})"/>')


def render_bandhu_svg(field_state: dict, pose: str = "idle",
                      cx: float = 0, cy: float = 0, scale: float = 1.0) -> str:
    """Render Bandhu as volumetric SVG figure. Never raises.

    Rebuilt from exact Shilpa Shastra Uttama Dasatala measurements.
    base_unit = 2.8px per talamana unit. Total height ≈ 347px.
    All coordinates hardcoded from bandhu_geometry.csv × 2.8.
    """
    try:
        # ── COLORS ──
        skin = "#c8a06e"
        skin_sh = "#c0986a"   # shoulders — slightly darker for depth
        skin_limb = "#b8906a" # arms/legs — darker still
        dhoti_c = "#2a5a4a"
        hair = "#1a0e05"
        eyes_c = "#3a2010"
        tilaka_c = "#c8a96e"
        lw = 0.8  # base line weight

        # ── POSE ANGLES ──
        arm_l_rot = -12     # degrees from shoulder
        arm_r_rot = 12
        leg_l_rot = 3
        leg_r_rot = -3
        torso_rot = 0
        head_dy = 0         # crown lift (breath)
        arms_joined = False

        if pose == "walk":
            arm_l_rot = -25
            arm_r_rot = 25
            leg_l_rot = 20
            leg_r_rot = -20
        elif pose == "bow":
            torso_rot = 30
            arms_joined = True
            head_dy = 5
        elif pose == "seated":
            pass  # handled separately

        # ── BREATH KEYFRAMES ──
        svg = _breath_keyframes(2.8)

        # ── OUTER GROUP with body sway animation ──
        svg += f'<g transform="translate({cx:.1f},{cy:.1f})" class="bnd-body">'

        # ── SUSHUMNA NADI — central gold axis (behind all) ──
        svg += '<line x1="0" y1="-173" x2="0" y2="135" stroke="#c8a96e" stroke-width="0.8" opacity="0.35"/>'

        if pose == "seated":
            # ══ SEATED POSE ══
            # Dhoti pad
            svg += f'<ellipse cx="0" cy="-30" rx="30" ry="12" fill="{dhoti_c}"/>'
            # Crossed thighs
            svg += f'<ellipse cx="-18" cy="-15" rx="30" ry="8" fill="{skin_limb}" transform="rotate(-15,-18,-15)"/>'
            svg += f'<ellipse cx="18" cy="-15" rx="30" ry="8" fill="{skin_limb}" transform="rotate(15,18,-15)"/>'
            # Lower legs folded
            svg += f'<ellipse cx="-22" cy="0" rx="6" ry="25" fill="{skin_limb}" transform="rotate(70,-22,0)"/>'
            svg += f'<ellipse cx="22" cy="0" rx="6" ry="25" fill="{skin_limb}" transform="rotate(-70,22,0)"/>'
            # Feet tucked
            svg += f'<ellipse cx="-10" cy="8" rx="8" ry="4" fill="{skin_limb}" opacity="0.8"/>'
            svg += f'<ellipse cx="10" cy="8" rx="8" ry="4" fill="{skin_limb}" opacity="0.8"/>'
            # Torso
            svg += f'<g class="bnd-chest" style="transform-origin:0px -85px">'
            svg += f'<ellipse cx="0" cy="-85" rx="22" ry="38" fill="{skin}"/>'
            svg += '</g>'
            # Hips
            svg += f'<ellipse cx="-18" cy="-30" rx="12" ry="8" fill="{skin}"/>'
            svg += f'<ellipse cx="18" cy="-30" rx="12" ry="8" fill="{skin}"/>'
            # Shoulders
            svg += f'<ellipse cx="-28" cy="-118" rx="14" ry="10" fill="{skin_sh}"/>'
            svg += f'<ellipse cx="28" cy="-118" rx="14" ry="10" fill="{skin_sh}"/>'
            # Arms resting on knees
            svg += f'<g class="bnd-arm-l" style="transform-origin:-28px -118px">'
            svg += f'<ellipse cx="-32" cy="-80" rx="7" ry="20" fill="{skin_limb}" transform="rotate(-25,-32,-80)"/>'
            svg += f'<ellipse cx="-30" cy="-45" rx="5" ry="18" fill="{skin_limb}" transform="rotate(-35,-30,-45)"/>'
            svg += f'<circle cx="-28" cy="-25" r="5" fill="{skin_limb}"/>'
            svg += '</g>'
            svg += f'<g class="bnd-arm-r" style="transform-origin:28px -118px">'
            svg += f'<ellipse cx="32" cy="-80" rx="7" ry="20" fill="{skin_limb}" transform="rotate(25,32,-80)"/>'
            svg += f'<ellipse cx="30" cy="-45" rx="5" ry="18" fill="{skin_limb}" transform="rotate(35,30,-45)"/>'
            svg += f'<circle cx="28" cy="-25" r="5" fill="{skin_limb}"/>'
            svg += '</g>'
        else:
            # ══ STANDING / WALK / BOW POSES ══
            # Draw order: back-to-front

            # 1. DHOTI (behind legs) — solid garment
            svg += (f'<polygon points="-18,-60 18,-60 22,-20 14,20 -14,20 -22,-20" '
                    f'fill="{dhoti_c}" stroke="{dhoti_c}" stroke-width="0.5"/>')
            # Dhoti fold lines
            for i in range(4):
                fx = -10 + i * 7
                svg += f'<line x1="{fx}" y1="-58" x2="{fx-1}" y2="18" stroke="#1e4a3e" stroke-width="0.4" opacity="0.3"/>'

            # 2. THIGHS — animated hip group
            svg += f'<g class="bnd-hip" style="transform-origin:0px -30px">'
            svg += f'<ellipse cx="-12" cy="20" rx="8" ry="36" fill="{skin_limb}" transform="rotate({leg_l_rot},-12,20)"/>'
            svg += f'<ellipse cx="12" cy="20" rx="8" ry="36" fill="{skin_limb}" transform="rotate({leg_r_rot},12,20)"/>'

            # 3. LOWER LEGS
            ll_l_x = -10 + math.sin(math.radians(leg_l_rot)) * 36
            ll_r_x = 10 + math.sin(math.radians(leg_r_rot)) * 36
            svg += f'<ellipse cx="{ll_l_x:.1f}" cy="90" rx="6" ry="36" fill="{skin_limb}" transform="rotate({leg_l_rot*0.5:.1f},{ll_l_x:.1f},90)"/>'
            svg += f'<ellipse cx="{ll_r_x:.1f}" cy="90" rx="6" ry="36" fill="{skin_limb}" transform="rotate({leg_r_rot*0.5:.1f},{ll_r_x:.1f},90)"/>'

            # 4. FEET — pada, planted and solid
            # Left foot
            lf_cx = ll_l_x - 2
            svg += f'<ellipse cx="{lf_cx:.1f}" cy="132" rx="12" ry="5" fill="{skin_limb}"/>'
            svg += f'<ellipse cx="{lf_cx - 2:.1f}" cy="132" rx="5" ry="4" fill="#a07858"/>'
            svg += f'<circle cx="{lf_cx + 6:.1f}" cy="130" r="2" fill="#a07858"/>'
            svg += f'<circle cx="{lf_cx + 4:.1f}" cy="129" r="2" fill="#a07858"/>'
            svg += f'<circle cx="{lf_cx + 2:.1f}" cy="129" r="2" fill="#a07858"/>'
            # Right foot
            rf_cx = ll_r_x + 2
            svg += f'<ellipse cx="{rf_cx:.1f}" cy="132" rx="12" ry="5" fill="{skin_limb}"/>'
            svg += f'<ellipse cx="{rf_cx + 2:.1f}" cy="132" rx="5" ry="4" fill="#a07858"/>'
            svg += f'<circle cx="{rf_cx - 6:.1f}" cy="130" r="2" fill="#a07858"/>'
            svg += f'<circle cx="{rf_cx - 4:.1f}" cy="129" r="2" fill="#a07858"/>'
            svg += f'<circle cx="{rf_cx - 2:.1f}" cy="129" r="2" fill="#a07858"/>'
            svg += '</g>'  # close bnd-hip

            # 5. TORSO — animated chest expansion
            svg += f'<g class="bnd-chest" style="transform-origin:0px -85px">'
            svg += f'<ellipse cx="0" cy="-85" rx="22" ry="38" fill="{skin}"/>'
            svg += '</g>'

            # 6. HIPS
            svg += f'<ellipse cx="-18" cy="-30" rx="12" ry="8" fill="{skin}"/>'
            svg += f'<ellipse cx="18" cy="-30" rx="12" ry="8" fill="{skin}"/>'

            # 7-9. UPPER ARMS, LOWER ARMS, HANDS
            if arms_joined:
                # Pranama — hands together at chest
                svg += f'<ellipse cx="-30" cy="-88" rx="7" ry="24" fill="{skin_limb}" transform="rotate(30,-30,-88)"/>'
                svg += f'<ellipse cx="30" cy="-88" rx="7" ry="24" fill="{skin_limb}" transform="rotate(-30,30,-88)"/>'
                svg += f'<ellipse cx="0" cy="-80" rx="8" ry="5" fill="{skin_limb}"/>'
            else:
                # Left arm group — animated
                svg += f'<g class="bnd-arm-l" style="transform-origin:-28px -118px">'
                svg += f'<ellipse cx="-38" cy="-88" rx="7" ry="24" fill="{skin_limb}" transform="rotate({arm_l_rot},-38,-88)"/>'
                la_l_x = -34 + math.sin(math.radians(arm_l_rot)) * 10
                svg += f'<ellipse cx="{la_l_x:.1f}" cy="-48" rx="5" ry="20" fill="{skin_limb}" transform="rotate({arm_l_rot*0.6:.1f},{la_l_x:.1f},-48)"/>'
                h_l_x = -32 + math.sin(math.radians(arm_l_rot)) * 8
                svg += f'<circle cx="{h_l_x:.1f}" cy="-30" r="5" fill="{skin_limb}"/>'
                svg += '</g>'
                # Right arm group — animated
                svg += f'<g class="bnd-arm-r" style="transform-origin:28px -118px">'
                svg += f'<ellipse cx="38" cy="-88" rx="7" ry="24" fill="{skin_limb}" transform="rotate({arm_r_rot},38,-88)"/>'
                la_r_x = 34 + math.sin(math.radians(arm_r_rot)) * 10
                svg += f'<ellipse cx="{la_r_x:.1f}" cy="-48" rx="5" ry="20" fill="{skin_limb}" transform="rotate({arm_r_rot*0.6:.1f},{la_r_x:.1f},-48)"/>'
                h_r_x = 32 + math.sin(math.radians(arm_r_rot)) * 8
                svg += f'<circle cx="{h_r_x:.1f}" cy="-30" r="5" fill="{skin_limb}"/>'
                svg += '</g>'

            # 10. SHOULDERS — on top of torso/arm junction
            svg += f'<ellipse cx="-28" cy="-118" rx="14" ry="10" fill="{skin_sh}"/>'
            svg += f'<ellipse cx="28" cy="-118" rx="14" ry="10" fill="{skin_sh}"/>'

        # ══ HEAD GROUP (all poses) — animated crown lift ══
        svg += f'<g class="bnd-crown" style="transform-origin:0px -155px">'

        # 11. NECK
        svg += f'<ellipse cx="0" cy="-128" rx="6" ry="9" fill="{skin}"/>'

        # 12. HEAD
        svg += f'<circle cx="0" cy="-155" r="18" fill="{skin}"/>'

        # 13. HAIR CAP
        svg += f'<ellipse cx="0" cy="-162" rx="17" ry="12" fill="{hair}" opacity="0.7"/>'

        # 14. EYES
        svg += f'<ellipse cx="-6" cy="-153" rx="2.2" ry="1.2" fill="{eyes_c}"/>'
        svg += f'<ellipse cx="6" cy="-153" rx="2.2" ry="1.2" fill="{eyes_c}"/>'

        # 15. TILAKA
        svg += f'<circle cx="0" cy="-158" r="2" fill="{tilaka_c}"/>'

        # Ear ornaments
        svg += f'<circle cx="-17" cy="-153" r="1.5" fill="{tilaka_c}" opacity="0.6"/>'
        svg += f'<circle cx="17" cy="-153" r="1.5" fill="{tilaka_c}" opacity="0.6"/>'

        svg += '</g>'  # close bnd-crown

        # ── CHAKRA POINTS — seven stations on sushumna ──
        _chakras = [
            (-173, 2.0, "#c8a96e"),  # Sahasrara — crown
            (-160, 1.5, "#9060c0"),  # Ajna — third eye
            (-128, 1.5, "#4080c0"),  # Vishuddha — throat
            (-95,  2.0, "#40c080"),  # Anahata — heart
            (-70,  1.5, "#e8c86a"),  # Manipura — navel
            (-40,  1.5, "#e8a0c0"),  # Swadhisthana — sacrum
            (-15,  2.0, "#c84040"),  # Muladhara — root
        ]
        for ch_y, ch_r, ch_col in _chakras:
            svg += f'<circle cx="0" cy="{ch_y}" r="{ch_r}" fill="{ch_col}" opacity="0.50"/>'

        svg += '</g>'  # close bnd-body
        return svg

    except Exception:
        return f'<g><circle cx="{cx}" cy="{cy}" r="5" fill="#c8a96e"/></g>'


# ══════════════════════════════════════════════════════════
# DHATU LAYER RENDERING
# ══════════════════════════════════════════════════════════

# Body region → approximate SVG position (relative to figure center)
_REGION_POS = {
    "skull_vault": (0, -0.92, 0.15), "eye_socket": (0, -0.88, 0.06),
    "eye_lens": (0, -0.88, 0.03), "iris": (0, -0.88, 0.02),
    "cochlea": (0.08, -0.85, 0.03), "nasal_cavity": (0, -0.82, 0.05),
    "jaw_masseter": (0, -0.75, 0.08), "cervical_spine": (0, -0.68, 0.04),
    "thoracic_spine": (0, -0.45, 0.05), "lumbar_spine": (0, -0.15, 0.04),
    "sternum": (0, -0.40, 0.06), "ribs": (0, -0.35, 0.20),
    "clavicle": (0, -0.55, 0.18), "scapula": (0, -0.48, 0.15),
    "humerus": (0.22, -0.40, 0.05), "radius_ulna": (0.25, -0.18, 0.04),
    "carpals": (0.27, 0.0, 0.03), "phalanges": (0.28, 0.05, 0.04),
    "pelvis": (0, 0.05, 0.15), "femur": (0.06, 0.25, 0.05),
    "tibia_fibula": (0.06, 0.50, 0.04), "tarsals": (0.06, 0.72, 0.06),
    "lung_bronchial": (0.08, -0.38, 0.12), "heart_muscle": (-0.03, -0.35, 0.06),
    "fascia_network": (0, -0.20, 0.35), "skin_surface": (0, -0.20, 0.40),
}


def render_dhatu_layer(field_state: dict, cx: float = 0, cy: float = 0,
                       scale: float = 1.0, dhatu_filter: str = "",
                       opacity: float = 0.2) -> str:
    """Render dhatu archetype geometry as SVG layer. Never raises.

    Args:
        dhatu_filter: empty=all, or 'D001'-'D007' for specific dhatu
        opacity: base opacity for the layer (0.15-0.25 typical)
    """
    try:
        archetypes = _load_archetypes()
        if not archetypes:
            return ""

        g = derive_bandhu_geometry(field_state)
        total_h = sum(seg["h"] for seg in g["segments"].values()) * scale
        s = scale

        svg = f'<g transform="translate({cx:.1f},{cy:.1f})" opacity="{opacity}">'

        for arch in archetypes:
            # Filter by dhatu if requested
            if dhatu_filter and arch.get("dhatu", "") != dhatu_filter:
                continue

            region = arch.get("body_region", "")
            pos = _REGION_POS.get(region)
            if not pos:
                continue

            rx, ry, rsize = pos
            px = rx * total_h * 0.5
            py = ry * total_h * 0.5
            sz = rsize * total_h

            # Clamp geometry to body bounds
            max_sz = total_h * 0.55  # no single element > half body
            shoulder_w = total_h * 0.25  # approximate shoulder half-width
            sz = min(sz, max_sz)
            # Clamp horizontal extent
            if abs(px) + sz > shoulder_w * 2:
                sz = max(2.0, shoulder_w * 2 - abs(px))
            # Clamp vertical: keep within -total_h/2 .. total_h/2
            half_h = total_h * 0.55
            if py - sz < -half_h:
                sz = min(sz, py + half_h)
            if py + sz > half_h:
                sz = min(sz, half_h - py)

            color = arch.get("color_primary", "#d4a84b")
            anim = arch.get("animation_pattern", "")
            geom = arch.get("archetype", "")

            if geom == "radial":
                # Radial lines from center
                for i in range(8):
                    a = i * math.pi / 4
                    x2 = px + math.cos(a) * sz
                    y2 = py + math.sin(a) * sz
                    svg += f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="0.5"/>'

            elif geom == "sinusoidal":
                # Sine wave pulse
                pts = []
                for i in range(20):
                    t = i / 19
                    x = px - sz + t * sz * 2
                    y = py + math.sin(t * math.pi * 4) * sz * 0.3
                    pts.append(f"{x:.1f},{y:.1f}")
                svg += f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="0.8"/>'

            elif geom == "branching":
                # Simple L-system branching
                def branch_svg(bx, by, angle, length, depth):
                    if depth == 0 or length < 2:
                        return ""
                    ex = bx + math.cos(angle) * length
                    ey = by + math.sin(angle) * length
                    s = f'<line x1="{bx:.1f}" y1="{by:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{color}" stroke-width="{0.3 + depth * 0.2:.1f}"/>'
                    s += branch_svg(ex, ey, angle - 0.5, length * 0.65, depth - 1)
                    s += branch_svg(ex, ey, angle + 0.5, length * 0.65, depth - 1)
                    return s
                svg += branch_svg(px, py, -math.pi / 2, sz * 0.8, 3)

            elif geom == "tensegrity":
                # Triangle mesh micro-grid
                for i in range(4):
                    for j in range(3):
                        ox = px - sz + i * sz * 0.5
                        oy = py - sz * 0.3 + j * sz * 0.3
                        svg += f'<polygon points="{ox:.1f},{oy:.1f} {ox+sz*0.25:.1f},{oy-sz*0.15:.1f} {ox+sz*0.5:.1f},{oy:.1f}" fill="none" stroke="{color}" stroke-width="0.3"/>'

            elif geom == "spiral":
                # Logarithmic spiral
                pts = []
                for i in range(30):
                    t = i / 29 * math.pi * 3
                    r = sz * 0.1 * math.exp(0.15 * t)
                    x = px + r * math.cos(t)
                    y = py + r * math.sin(t)
                    pts.append(f"{x:.1f},{y:.1f}")
                svg += f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="0.6"/>'

            elif geom == "parabolic":
                # Bilateral parabolic arcs
                pts_l = []
                pts_r = []
                for i in range(10):
                    t = i / 9
                    x = t * sz
                    y = py + (t - 0.5) ** 2 * sz * 2
                    pts_l.append(f"{px - x:.1f},{y:.1f}")
                    pts_r.append(f"{px + x:.1f},{y:.1f}")
                svg += f'<polyline points="{" ".join(pts_l)}" fill="none" stroke="{color}" stroke-width="0.6"/>'
                svg += f'<polyline points="{" ".join(pts_r)}" fill="none" stroke="{color}" stroke-width="0.6"/>'

            elif geom == "vesica":
                # Two overlapping ellipses
                svg += f'<ellipse cx="{px - sz * 0.2:.1f}" cy="{py:.1f}" rx="{sz * 0.5:.1f}" ry="{sz * 0.3:.1f}" fill="none" stroke="{color}" stroke-width="0.5"/>'
                svg += f'<ellipse cx="{px + sz * 0.2:.1f}" cy="{py:.1f}" rx="{sz * 0.5:.1f}" ry="{sz * 0.3:.1f}" fill="none" stroke="{color}" stroke-width="0.5"/>'

            elif geom == "concentric":
                # Nested ellipses
                for i in range(3):
                    r = sz * (0.4 + i * 0.2)
                    svg += f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="{r:.1f}" ry="{r * 0.6:.1f}" fill="none" stroke="{color}" stroke-width="0.4"/>'

            elif geom == "tidal":
                # Whole-body glow pulse
                svg += f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="{sz:.1f}" ry="{sz * 1.5:.1f}" fill="{color}" opacity="0.08"/>'

        svg += '</g>'
        return svg

    except Exception:
        return ""


# ══════════════════════════════════════════════════════════
# DOCTRINE OF SIGNATURES LAYER
# ══════════════════════════════════════════════════════════

def _load_signatures():
    global _signature_cache
    if _signature_cache is not None:
        return _signature_cache
    _signature_cache = []
    try:
        with open(_SIGNATURE_CSV, encoding="utf-8") as f:
            _signature_cache = list(csv.DictReader(io.StringIO(f.read().lstrip())))
    except Exception:
        pass
    return _signature_cache


# Map body_target values to _REGION_POS keys (signatures use body_archetype_map names)
_TARGET_TO_REGION = {
    "skull_vault": "skull_vault", "eye_socket": "eye_socket", "iris": "iris",
    "eye_lens": "eye_lens", "cochlea": "cochlea", "nasal_cavity": "nasal_cavity",
    "jaw_masseter": "jaw_masseter", "cervical_spine": "cervical_spine",
    "thoracic_spine": "thoracic_spine", "lumbar_spine": "lumbar_spine",
    "sternum": "sternum", "ribs": "ribs", "clavicle": "clavicle",
    "scapula": "scapula", "humerus": "humerus", "radius_ulna": "radius_ulna",
    "carpals": "carpals", "phalanges": "phalanges", "pelvis": "pelvis",
    "femur": "femur", "tibia_fibula": "tibia_fibula", "tarsals": "tarsals",
    "lung_bronchial": "lung_bronchial", "heart_muscle": "heart_muscle",
    "fascia_network": "fascia_network", "skin_surface": "skin_surface",
}


def _sig_plant_glyph(archetype: str, px: float, py: float, sz: float,
                      color: str, zoom: float) -> str:
    """Render a plant-form glyph for a given archetype at a body position."""
    svg = ""
    r = sz * min(zoom * 0.4, 1.5)  # scale with zoom but cap

    if archetype in ("circular", "radial"):
        # Seed pod / iris pattern: radial lines + central circle
        svg += f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r * 0.3:.1f}" fill="none" stroke="{color}" stroke-width="0.4"/>'
        n = 6 if zoom < 2.0 else 12
        for i in range(n):
            a = i * math.pi * 2 / n
            x2 = px + math.cos(a) * r
            y2 = py + math.sin(a) * r
            svg += f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="0.3" opacity="0.6"/>'
        if zoom >= 2.0:
            # Inner seed holes (lotus pod)
            for i in range(5):
                a = i * math.pi * 2 / 5
                cx2 = px + math.cos(a) * r * 0.5
                cy2 = py + math.sin(a) * r * 0.5
                svg += f'<circle cx="{cx2:.1f}" cy="{cy2:.1f}" r="{r * 0.08:.1f}" fill="{color}" opacity="0.4"/>'

    elif archetype in ("parabolic", "dome"):
        # Fig dome / skull cap arc
        svg += (f'<path d="M{px - r:.1f},{py:.1f} '
                f'Q{px:.1f},{py - r * 1.4:.1f} {px + r:.1f},{py:.1f}" '
                f'fill="none" stroke="{color}" stroke-width="0.5"/>')
        if zoom >= 2.0:
            # Interior fold lines
            for i in range(3):
                off = (i - 1) * r * 0.3
                svg += (f'<path d="M{px + off - r * 0.2:.1f},{py - r * 0.3:.1f} '
                        f'Q{px + off:.1f},{py - r * 0.8:.1f} {px + off + r * 0.2:.1f},{py - r * 0.3:.1f}" '
                        f'fill="none" stroke="{color}" stroke-width="0.3" opacity="0.5"/>')

    elif archetype in ("branching", "folded"):
        # L-system branch (nerve tree / lung tree / leaf vein)
        def _branch(bx, by, angle, length, depth):
            if depth == 0 or length < 1:
                return ""
            ex = bx + math.cos(angle) * length
            ey = by + math.sin(angle) * length
            s = f'<line x1="{bx:.1f}" y1="{by:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{color}" stroke-width="{0.2 + depth * 0.15:.1f}" opacity="0.7"/>'
            s += _branch(ex, ey, angle - 0.5, length * 0.6, depth - 1)
            s += _branch(ex, ey, angle + 0.5, length * 0.6, depth - 1)
            return s
        max_d = 3 if zoom < 2.0 else 4
        svg += _branch(px, py, -math.pi / 2, r * 0.7, max_d)

    elif archetype in ("tensegrity", "vertical"):
        # Bamboo segments: horizontal node lines on vertical axis
        n_seg = 4 if zoom < 2.0 else 7
        seg_h = r * 2 / n_seg
        top_y = py - r
        svg += f'<line x1="{px:.1f}" y1="{top_y:.1f}" x2="{px:.1f}" y2="{py + r:.1f}" stroke="{color}" stroke-width="0.4" opacity="0.6"/>'
        for i in range(n_seg + 1):
            ny = top_y + i * seg_h
            hw = r * 0.3 * (1.0 + 0.2 * math.sin(i * 0.8))
            svg += f'<line x1="{px - hw:.1f}" y1="{ny:.1f}" x2="{px + hw:.1f}" y2="{ny:.1f}" stroke="{color}" stroke-width="0.5"/>'
        if zoom >= 2.0:
            # Hollow channel
            svg += f'<line x1="{px:.1f}" y1="{top_y + seg_h * 0.3:.1f}" x2="{px:.1f}" y2="{py + r - seg_h * 0.3:.1f}" stroke="{color}" stroke-width="0.2" stroke-dasharray="1,1.5" opacity="0.4"/>'

    elif archetype in ("vesica", "oval"):
        # Paired kidney/almond/walnut shapes
        svg += f'<ellipse cx="{px - r * 0.35:.1f}" cy="{py:.1f}" rx="{r * 0.4:.1f}" ry="{r * 0.6:.1f}" fill="none" stroke="{color}" stroke-width="0.4"/>'
        svg += f'<ellipse cx="{px + r * 0.35:.1f}" cy="{py:.1f}" rx="{r * 0.4:.1f}" ry="{r * 0.6:.1f}" fill="none" stroke="{color}" stroke-width="0.4"/>'

    elif archetype in ("sinusoidal",):
        # Ginger / rhizome undulation
        pts = []
        for i in range(16):
            t = i / 15
            x = px - r + t * r * 2
            y = py + math.sin(t * math.pi * 3) * r * 0.3
            pts.append(f"{x:.1f},{y:.1f}")
        svg += f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="0.5" opacity="0.7"/>'

    elif archetype in ("circular;concentric", "concentric"):
        # Onion layers / arjuna rings
        for i in range(4):
            ri = r * (0.25 + i * 0.2)
            svg += f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{ri:.1f}" fill="none" stroke="{color}" stroke-width="0.3" opacity="{0.4 + i * 0.1:.1f}"/>'

    elif archetype == "tidal":
        # Whole-body glow (CSF / latex flow)
        svg += f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="{r * 0.6:.1f}" ry="{r:.1f}" fill="{color}" opacity="0.06"/>'

    elif archetype in ("spiral",):
        # Golden spiral (reproductive / cochlea)
        pts = []
        for i in range(24):
            t = i / 23 * math.pi * 2.5
            ri = r * 0.1 * math.exp(0.12 * t)
            x = px + ri * math.cos(t)
            y = py + ri * math.sin(t)
            pts.append(f"{x:.1f},{y:.1f}")
        svg += f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="0.4" opacity="0.7"/>'

    else:
        # Fallback: simple circle marker
        svg += f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r * 0.3:.1f}" fill="none" stroke="{color}" stroke-width="0.3" opacity="0.5"/>'

    return svg


# Zoom detail thresholds: what archetypes render at each level
_ZOOM_1_ARCHETYPES = {"circular", "radial", "parabolic", "dome", "tensegrity",
                       "vertical", "vesica", "oval"}
_ZOOM_2_ARCHETYPES = _ZOOM_1_ARCHETYPES | {"branching", "folded", "sinusoidal",
                                             "concentric", "circular;concentric",
                                             "spiral", "tidal"}
_ZOOM_4_ARCHETYPES = _ZOOM_2_ARCHETYPES  # all render at max zoom


def render_signature_layer(field_state: dict, cx: float = 0, cy: float = 0,
                           scale: float = 1.0, zoom_level: float = 1.0,
                           opacity: float = 0.20) -> str:
    """Render doctrine of signatures plant-body overlay. Never raises.

    zoom_level controls detail:
        1.0 — major structural: fig dome on skull, bamboo nodes on spine,
               lotus pod on heart, arjuna rings on pelvis
        2.0 — full plant morphology per region: interior folds, hollow channels,
               walnut bilateral halves
        4.0 — cellular level: onion membrane on skin, grape cluster on lung,
               carrot radial on eye
    """
    try:
        sigs = _load_signatures()
        if not sigs:
            return ""

        g = derive_bandhu_geometry(field_state)
        total_h = sum(seg["h"] for seg in g["segments"].values()) * scale

        # Choose archetype set by zoom
        if zoom_level >= 4.0:
            allowed = _ZOOM_4_ARCHETYPES
        elif zoom_level >= 2.0:
            allowed = _ZOOM_2_ARCHETYPES
        else:
            allowed = _ZOOM_1_ARCHETYPES

        svg = f'<g transform="translate({cx:.1f},{cy:.1f})" opacity="{opacity}">'

        for sig in sigs:
            # Parse archetype_shared (may be semicolon-separated)
            archetypes_raw = sig.get("archetype_shared", "")
            arch_list = [a.strip() for a in archetypes_raw.split(";") if a.strip()]
            if not arch_list:
                continue

            # Use first archetype that's in allowed set; else skip
            chosen_arch = None
            for a in arch_list:
                if a in allowed:
                    chosen_arch = a
                    break
            if not chosen_arch:
                continue

            # Resolve body position(s) — body_target may be semicolon-separated
            targets = [t.strip() for t in sig.get("body_target", "").split(";") if t.strip()]
            # Get graha color
            graha_raw = sig.get("graha_correspondence", "")
            graha_first = graha_raw.split(";")[0].strip() if graha_raw else ""
            color = _GRAHA_COLORS.get(graha_first, "#d4a84b")

            for target in targets:
                region_key = _TARGET_TO_REGION.get(target)
                if not region_key:
                    continue
                pos = _REGION_POS.get(region_key)
                if not pos:
                    continue

                rx, ry, rsize = pos
                px = rx * total_h * 0.5
                py = ry * total_h * 0.5
                sz = rsize * total_h

                # Clamp to body bounds (same as dhatu layer)
                max_sz = total_h * 0.55
                shoulder_w = total_h * 0.25
                sz = min(sz, max_sz)
                if abs(px) + sz > shoulder_w * 2:
                    sz = max(2.0, shoulder_w * 2 - abs(px))
                half_h = total_h * 0.55
                if py - sz < -half_h:
                    sz = min(sz, py + half_h)
                if py + sz > half_h:
                    sz = min(sz, half_h - py)

                svg += _sig_plant_glyph(chosen_arch, px, py, sz, color, zoom_level)

        svg += '</g>'
        return svg

    except Exception:
        return ""


# ══════════════════════════════════════════════════════════
# SKELETON LAYER — Asthi (D005) architecture
# ══════════════════════════════════════════════════════════

# Colors from graha-dhatu mapping
_BONE_GOLD = "#e8c86a"      # Surya/Asthi — warm gold (skull, spine, right ribs, sternum)
_BONE_SILVER = "#c8d8e8"    # Chandra/ida — lunar silver (left ribs)
_BONE_EARTH = "#b8906a"     # Prithvi/Asthi — earth tone (long bones)
_BONE_PELVIS = "#8090a8"    # Shani/boundary — steel blue (pelvis)


def render_skeleton_layer(field_state: dict, cx: float = 0, cy: float = 0,
                          scale: float = 1.0, opacity: float = 0.25) -> str:
    """Render anatomical skeleton as SVG layer. Never raises.

    Uses the exact coordinate system from render_bandhu_svg:
    head at cy=-155, feet at cy=+130.
    Ida (left/lunar/silver) and Pingala (right/solar/gold)
    visible in rib color asymmetry.
    """
    try:
        svg = f'<g transform="translate({cx:.1f},{cy:.1f})" opacity="{opacity}">'

        # ── SKULL ──
        # Cranial dome
        svg += f'<ellipse cx="0" cy="-158" rx="17" ry="19" fill="none" stroke="{_BONE_GOLD}" stroke-width="0.8"/>'
        # Jaw arc
        svg += f'<path d="M-10,-137 Q0,-128 10,-137" fill="none" stroke="{_BONE_GOLD}" stroke-width="0.7"/>'
        # Orbital ridges
        svg += f'<path d="M-9,-152 Q-6,-154 -3,-152" fill="none" stroke="{_BONE_GOLD}" stroke-width="0.5"/>'
        svg += f'<path d="M3,-152 Q6,-154 9,-152" fill="none" stroke="{_BONE_GOLD}" stroke-width="0.5"/>'
        # Nasal bone
        svg += f'<line x1="0" y1="-150" x2="0" y2="-143" stroke="{_BONE_GOLD}" stroke-width="0.5"/>'

        # ── CERVICAL SPINE — 7 vertebrae ──
        for i in range(7):
            vy = -128 + i * 2.5
            svg += f'<rect x="-3" y="{vy - 0.75:.1f}" width="6" height="1.5" rx="0.5" fill="none" stroke="{_BONE_GOLD}" stroke-width="0.5"/>'

        # ── THORACIC SPINE — 12 vertebrae ──
        thoracic_ys = []
        for i in range(12):
            vy = -112 + i * 5
            thoracic_ys.append(vy)
            svg += f'<rect x="-4" y="{vy - 0.75:.1f}" width="8" height="1.5" rx="0.5" fill="none" stroke="{_BONE_GOLD}" stroke-width="0.5"/>'

        # ── LUMBAR SPINE — 5 vertebrae ──
        for i in range(5):
            vy = -52 + i * 5
            svg += f'<rect x="-5" y="{vy - 1:.1f}" width="10" height="2" rx="0.5" fill="none" stroke="{_BONE_GOLD}" stroke-width="0.6"/>'

        # ── RIBS — 12 pairs ──
        # Left ribs: Chandra/ida (silver), Right ribs: Surya/pingala (gold)
        for i, ty in enumerate(thoracic_ys):
            # Rib width decreases for lower ribs
            if i < 7:
                w = 18 + i * 0.5   # true ribs widen slightly
            elif i < 10:
                w = 20 - (i - 7) * 2  # false ribs narrow
            else:
                w = 12 - (i - 10) * 3  # floating ribs short

            drop = 6 + i * 0.8  # lower ribs drop more

            # Left rib (ida / silver)
            svg += (f'<path d="M0,{ty:.1f} Q{-w * 0.6:.1f},{ty - 2:.1f} '
                    f'{-w:.1f},{ty + drop * 0.5:.1f} Q{-w * 0.8:.1f},{ty + drop:.1f} '
                    f'{-w * 0.3:.1f},{ty + drop:.1f}" '
                    f'fill="none" stroke="{_BONE_SILVER}" stroke-width="0.6" opacity="0.8"/>')
            # Right rib (pingala / gold)
            svg += (f'<path d="M0,{ty:.1f} Q{w * 0.6:.1f},{ty - 2:.1f} '
                    f'{w:.1f},{ty + drop * 0.5:.1f} Q{w * 0.8:.1f},{ty + drop:.1f} '
                    f'{w * 0.3:.1f},{ty + drop:.1f}" '
                    f'fill="none" stroke="{_BONE_GOLD}" stroke-width="0.6" opacity="0.8"/>')

        # ── STERNUM ──
        svg += f'<rect x="-3" y="-110" width="6" height="50" rx="1.5" fill="none" stroke="{_BONE_GOLD}" stroke-width="0.7"/>'

        # ── CLAVICLES ──
        svg += f'<line x1="0" y1="-112" x2="-28" y2="-118" stroke="{_BONE_GOLD}" stroke-width="1.0"/>'
        svg += f'<line x1="0" y1="-112" x2="28" y2="-118" stroke="{_BONE_GOLD}" stroke-width="1.0"/>'

        # ── SCAPULAE (behind — dimmer) ──
        svg += f'<path d="M-20,-112 L-32,-118 L-28,-90 Z" fill="none" stroke="#c8a96e" stroke-width="0.5" opacity="0.4"/>'
        svg += f'<path d="M20,-112 L32,-118 L28,-90 Z" fill="none" stroke="#c8a96e" stroke-width="0.5" opacity="0.4"/>'

        # ── PELVIS ──
        # Main basin
        svg += f'<ellipse cx="0" cy="-20" rx="20" ry="14" fill="none" stroke="{_BONE_PELVIS}" stroke-width="1.0"/>'
        # Iliac crests
        svg += f'<path d="M-8,-32 Q-16,-28 -20,-20" fill="none" stroke="{_BONE_PELVIS}" stroke-width="0.8"/>'
        svg += f'<path d="M8,-32 Q16,-28 20,-20" fill="none" stroke="{_BONE_PELVIS}" stroke-width="0.8"/>'
        # Sacrum — downward pointing triangle (Shakti yantra)
        svg += f'<path d="M-6,-28 L0,-18 L6,-28 Z" fill="none" stroke="{_BONE_PELVIS}" stroke-width="0.7"/>'

        # ── HUMERUS (upper arm bones) ──
        svg += f'<line x1="-38" y1="-112" x2="-38" y2="-72" stroke="{_BONE_EARTH}" stroke-width="1.5"/>'
        svg += f'<line x1="38" y1="-112" x2="38" y2="-72" stroke="{_BONE_EARTH}" stroke-width="1.5"/>'

        # ── RADIUS / ULNA (forearm — two parallel lines) ──
        # Left
        svg += f'<line x1="-36" y1="-68" x2="-34" y2="-35" stroke="{_BONE_EARTH}" stroke-width="0.8"/>'
        svg += f'<line x1="-38" y1="-68" x2="-36" y2="-35" stroke="{_BONE_EARTH}" stroke-width="0.6"/>'
        # Right
        svg += f'<line x1="36" y1="-68" x2="34" y2="-35" stroke="{_BONE_EARTH}" stroke-width="0.8"/>'
        svg += f'<line x1="38" y1="-68" x2="36" y2="-35" stroke="{_BONE_EARTH}" stroke-width="0.6"/>'

        # ── FEMUR (thigh — longest bone, moringa drumstick) ──
        svg += f'<line x1="-12" y1="-18" x2="-12" y2="52" stroke="{_BONE_EARTH}" stroke-width="2.0"/>'
        svg += f'<line x1="12" y1="-18" x2="12" y2="52" stroke="{_BONE_EARTH}" stroke-width="2.0"/>'

        # ── TIBIA / FIBULA ──
        # Left
        svg += f'<line x1="-11" y1="56" x2="-11" y2="125" stroke="{_BONE_EARTH}" stroke-width="1.0"/>'
        svg += f'<line x1="-13" y1="56" x2="-13" y2="125" stroke="{_BONE_EARTH}" stroke-width="0.6"/>'
        # Right
        svg += f'<line x1="11" y1="56" x2="11" y2="125" stroke="{_BONE_EARTH}" stroke-width="1.0"/>'
        svg += f'<line x1="13" y1="56" x2="13" y2="125" stroke="{_BONE_EARTH}" stroke-width="0.6"/>'

        # ── FEET (metatarsals fanning) ──
        for side in (-1, 1):
            bx = side * 12
            for j in range(3):
                angle = -0.3 + j * 0.3  # fan from heel
                tx = bx + math.cos(angle) * 12 * side
                ty = 126 + math.sin(abs(angle) + 0.8) * 6
                svg += f'<line x1="{bx}" y1="126" x2="{tx:.1f}" y2="{ty:.1f}" stroke="{_BONE_EARTH}" stroke-width="0.5"/>'

        # ── HAND BONES (carpals + metacarpals) ──
        for side in (-1, 1):
            bx = side * 34
            # Wrist block
            svg += f'<rect x="{bx - 3}" y="-34" width="6" height="3" rx="1" fill="none" stroke="{_BONE_EARTH}" stroke-width="0.4"/>'
            # Five metacarpal/finger lines
            for j in range(5):
                angle = -0.4 + j * 0.2
                fx = bx + math.sin(angle) * 10 * side
                fy = -31 + abs(math.cos(angle)) * 2
                svg += f'<line x1="{bx}" y1="-31" x2="{fx:.1f}" y2="{fy + 10:.1f}" stroke="{_BONE_EARTH}" stroke-width="0.3"/>'

        svg += '</g>'
        return svg

    except Exception:
        return ""


# ══════════════════════════════════════════════════════════
# FLUID DYNAMICS LAYER — Rasa (D001) / plasma / lymph
# ══════════════════════════════════════════════════════════

_FLUID_PLASMA = "#c8d8e8"   # Chandra/Moon — plasma/lymph
_FLUID_VENOUS = "#8090c8"   # blue-silver — venous return
_FLUID_ARTERIAL = "#c8906a" # warm/Mars — arterial flow
_FLUID_CSF = "#e8e8f0"      # pure/Majja boundary — cerebrospinal


def _fluid_style() -> str:
    """CSS animations for fluid dynamics: flow, pulse, breathe."""
    return """<style>
@keyframes fl-plasma{0%{transform:scale(1.0)}50%{transform:scale(1.03)}100%{transform:scale(1.0)}}
@keyframes fl-flow-down{0%{stroke-dashoffset:0}100%{stroke-dashoffset:-30}}
@keyframes fl-flow-up{0%{stroke-dashoffset:0}100%{stroke-dashoffset:30}}
@keyframes fl-lymph{0%{stroke-dashoffset:0}100%{stroke-dashoffset:-18}}
@keyframes fl-pulse{0%{opacity:0.15}50%{opacity:0.35}100%{opacity:0.15}}
.fl-plasma{animation:fl-plasma 4s ease-in-out infinite;transform-origin:0px -20px}
.fl-down{animation:fl-flow-down 3s linear infinite}
.fl-up{animation:fl-flow-up 3s linear infinite}
.fl-lymph{animation:fl-lymph 3s linear infinite}
.fl-pulse{animation:fl-pulse 3s ease-in-out infinite}
</style>
"""


def render_fluid_layer(field_state: dict, cx: float = 0, cy: float = 0,
                       scale: float = 1.0, opacity: float = 0.18) -> str:
    """Render Rasa/plasma fluid dynamics as SVG layer. Never raises.

    Plasma field, lymph channels, venous return, arterial flow,
    synovial joint fluid, cerebrospinal fluid.
    Uses exact coordinate system: head cy=-155, feet cy=+130.
    """
    try:
        svg = _fluid_style()
        svg += f'<g transform="translate({cx:.1f},{cy:.1f})" opacity="{opacity}">'

        # ── PLASMA FIELD — overall fluid envelope ──
        svg += (f'<ellipse cx="0" cy="-20" rx="35" ry="95" '
                f'fill="none" stroke="{_FLUID_PLASMA}" stroke-width="0.4" '
                f'opacity="0.15" class="fl-plasma"/>')

        # ── CEREBROSPINAL FLUID — fig latex inside skull ──
        svg += (f'<ellipse cx="0" cy="-158" rx="14" ry="15" '
                f'fill="{_FLUID_CSF}" opacity="0.12"/>')

        # ── LYMPH CHANNELS — flowing paths ──
        # Cervical lymph: throat down both sides of neck
        svg += (f'<path d="M-6,-125 Q-12,-110 -20,-90" fill="none" '
                f'stroke="{_FLUID_PLASMA}" stroke-width="0.6" '
                f'stroke-dasharray="3,3" class="fl-lymph"/>')
        svg += (f'<path d="M6,-125 Q12,-110 20,-90" fill="none" '
                f'stroke="{_FLUID_PLASMA}" stroke-width="0.6" '
                f'stroke-dasharray="3,3" class="fl-lymph"/>')

        # Axillary (armpit) pools
        svg += (f'<ellipse cx="-30" cy="-95" rx="5" ry="3" '
                f'fill="{_FLUID_PLASMA}" opacity="0.20" class="fl-pulse"/>')
        svg += (f'<ellipse cx="30" cy="-95" rx="5" ry="3" '
                f'fill="{_FLUID_PLASMA}" opacity="0.20" class="fl-pulse"/>')

        # Abdominal channels: vertical flow flanking spine
        svg += (f'<line x1="-5" y1="-100" x2="-5" y2="-30" '
                f'stroke="{_FLUID_PLASMA}" stroke-width="0.5" '
                f'stroke-dasharray="3,3" class="fl-lymph"/>')
        svg += (f'<line x1="5" y1="-100" x2="5" y2="-30" '
                f'stroke="{_FLUID_PLASMA}" stroke-width="0.5" '
                f'stroke-dasharray="3,3" class="fl-lymph"/>')

        # Inguinal (groin) pools
        svg += (f'<ellipse cx="-15" cy="-25" rx="4" ry="3" '
                f'fill="{_FLUID_PLASMA}" opacity="0.18" class="fl-pulse"/>')
        svg += (f'<ellipse cx="15" cy="-25" rx="4" ry="3" '
                f'fill="{_FLUID_PLASMA}" opacity="0.18" class="fl-pulse"/>')

        # ── VENOUS RETURN — upward flow (blue-silver) ──
        svg += (f'<line x1="-1" y1="120" x2="-1" y2="-150" '
                f'stroke="{_FLUID_VENOUS}" stroke-width="0.8" '
                f'stroke-dasharray="2,4" class="fl-up"/>')

        # ── ARTERIAL FLOW — downward (warm) ──
        svg += (f'<line x1="2" y1="-100" x2="2" y2="120" '
                f'stroke="{_FLUID_ARTERIAL}" stroke-width="0.6" '
                f'stroke-dasharray="2,4" class="fl-down"/>')

        # ── SYNOVIAL JOINT FLUID — guggul resin glow ──
        _joints = [
            (-28, -115, 6, 4),   # left shoulder
            (28, -115, 6, 4),    # right shoulder
            (-18, -22, 5, 4),    # left hip
            (18, -22, 5, 4),     # right hip
            (-11, 55, 4, 3),     # left knee
            (11, 55, 4, 3),      # right knee
            (-11, 120, 3, 2),    # left ankle
            (11, 120, 3, 2),     # right ankle
        ]
        for jx, jy, jrx, jry in _joints:
            svg += (f'<ellipse cx="{jx}" cy="{jy}" rx="{jrx}" ry="{jry}" '
                    f'fill="{_FLUID_PLASMA}" opacity="0.25" class="fl-pulse"/>')

        svg += '</g>'
        return svg

    except Exception:
        return ""


def render_bandhu_full(field_state: dict, pose: str = "idle",
                       cx: float = 0, cy: float = 0, scale: float = 1.0,
                       layers: str = "all", dhatu: str = "",
                       zoom_level: float = 1.0) -> str:
    """Render Bandhu with optional layers. Never raises.

    Args:
        layers: 'all', 'skin', 'dhatu', 'signature', 'skeleton', 'fluid'
        dhatu: specific dhatu ID (e.g. 'D005' bone, 'D001' plasma)
        zoom_level: 1.0=structural, 2.0=morphological, 4.0=cellular
    """
    parts = []

    # Body silhouette clipPath
    clip_id = "body-clip"
    clip_def = (
        f'<defs><clipPath id="{clip_id}">'
        f'<ellipse cx="{cx:.1f}" cy="{cy - 20:.1f}" rx="45" ry="165"/>'
        f'</clipPath></defs>'
    )
    clip_emitted = False

    def _clip(svg_content):
        nonlocal clip_emitted
        if not clip_emitted:
            parts.append(clip_def)
            clip_emitted = True
        parts.append(f'<g clip-path="url(#{clip_id})">{svg_content}</g>')

    # Layer order (back to front):
    # skeleton → fluid → dhatu → signature → skin

    if layers in ("all", "skeleton") or dhatu == "D005":
        skel_opacity = 0.65 if dhatu == "D005" else (0.85 if layers == "skeleton" else 0.18)
        _clip(render_skeleton_layer(field_state, cx, cy, scale, opacity=skel_opacity))

    if layers in ("all", "fluid") or dhatu == "D001":
        fluid_opacity = 0.40 if dhatu == "D001" else (0.30 if layers == "fluid" else 0.15)
        _clip(render_fluid_layer(field_state, cx, cy, scale, opacity=fluid_opacity))

    if layers in ("all", "dhatu"):
        dhatu_opacity = 0.40 if layers == "dhatu" else 0.18
        _clip(render_dhatu_layer(field_state, cx, cy, scale,
                                 dhatu_filter=dhatu, opacity=dhatu_opacity))

    if layers in ("all", "signature"):
        sig_opacity = 0.20 if layers == "signature" else 0.10
        _clip(render_signature_layer(field_state, cx, cy, scale,
                                     zoom_level=zoom_level, opacity=sig_opacity))

    if layers in ("all", "skin"):
        skin_opacity = "0.55" if layers == "all" else "1.0"
        skin_svg = render_bandhu_svg(field_state, pose, cx, cy, scale)
        if skin_opacity != "1.0":
            skin_svg = skin_svg.replace('<g transform=', f'<g opacity="{skin_opacity}" transform=', 1)
        parts.append(skin_svg)

    return "\n".join(parts)
