"""
graph_seed_data.py — Seeds all mix-relational data.

Rasa-layer weights, element biases, deity biases, guna characters,
arc-mix transitions. All stability: working, authority: sadhu.
"""

# ──────────────────────────────────────────────────────────────
# LAYERS — canonical ordering
# ──────────────────────────────────────────────────────────────

LAYERS = [
    "tanpura", "mantra_drone", "vocal_pad",     # foundation
    "tabla", "konnakol", "bol",                  # rhythm
    "melody", "vocal_line",                      # expressive
    "pad", "electronic",                         # atmosphere
    "bija",                                      # transition
]

# ──────────────────────────────────────────────────────────────
# RASA → LAYER WEIGHTS (9 rasas × 11 layers)
# ──────────────────────────────────────────────────────────────
# Values are relative weights 0-1. Mix kernel normalizes.

RASA_LAYER_WEIGHTS = {
    "shringara": {
        "tanpura": 0.8, "mantra_drone": 0.6, "vocal_pad": 0.5,
        "tabla": 0.7, "konnakol": 0.4, "bol": 0.5,
        "melody": 0.9, "vocal_line": 0.8,
        "pad": 0.7, "electronic": 0.3, "bija": 0.4,
    },
    "karuna": {
        "tanpura": 0.9, "mantra_drone": 0.8, "vocal_pad": 0.7,
        "tabla": 0.4, "konnakol": 0.2, "bol": 0.3,
        "melody": 0.8, "vocal_line": 0.9,
        "pad": 0.8, "electronic": 0.2, "bija": 0.5,
    },
    "vira": {
        "tanpura": 0.6, "mantra_drone": 0.3, "vocal_pad": 0.2,
        "tabla": 0.9, "konnakol": 0.8, "bol": 0.7,
        "melody": 0.7, "vocal_line": 0.6,
        "pad": 0.3, "electronic": 0.7, "bija": 0.3,
    },
    "raudra": {
        "tanpura": 0.5, "mantra_drone": 0.2, "vocal_pad": 0.1,
        "tabla": 1.0, "konnakol": 0.9, "bol": 0.8,
        "melody": 0.5, "vocal_line": 0.4,
        "pad": 0.2, "electronic": 0.8, "bija": 0.2,
    },
    "hasya": {
        "tanpura": 0.6, "mantra_drone": 0.4, "vocal_pad": 0.3,
        "tabla": 0.7, "konnakol": 0.7, "bol": 0.6,
        "melody": 0.8, "vocal_line": 0.7,
        "pad": 0.4, "electronic": 0.5, "bija": 0.3,
    },
    "bhayanaka": {
        "tanpura": 0.7, "mantra_drone": 0.8, "vocal_pad": 0.6,
        "tabla": 0.3, "konnakol": 0.2, "bol": 0.2,
        "melody": 0.4, "vocal_line": 0.5,
        "pad": 0.9, "electronic": 0.6, "bija": 0.6,
    },
    "bibhatsa": {
        "tanpura": 0.6, "mantra_drone": 0.7, "vocal_pad": 0.5,
        "tabla": 0.3, "konnakol": 0.1, "bol": 0.2,
        "melody": 0.3, "vocal_line": 0.4,
        "pad": 0.7, "electronic": 0.8, "bija": 0.5,
    },
    "adbhuta": {
        "tanpura": 0.7, "mantra_drone": 0.6, "vocal_pad": 0.5,
        "tabla": 0.5, "konnakol": 0.5, "bol": 0.4,
        "melody": 0.7, "vocal_line": 0.7,
        "pad": 0.8, "electronic": 0.7, "bija": 0.6,
    },
    "shanta": {
        "tanpura": 1.0, "mantra_drone": 0.9, "vocal_pad": 0.7,
        "tabla": 0.3, "konnakol": 0.2, "bol": 0.2,
        "melody": 0.6, "vocal_line": 0.7,
        "pad": 0.8, "electronic": 0.2, "bija": 0.7,
    },
}

# ──────────────────────────────────────────────────────────────
# ELEMENT → MIX BIAS
# ──────────────────────────────────────────────────────────────

ELEMENT_MIX_BIAS = {
    "fire":  {"tabla": 0.15, "electronic": 0.1, "brightness": 0.1, "melody": 0.05},
    "water": {"mantra_drone": 0.1, "vocal_line": 0.1, "reverb_depth": 0.15, "pad": 0.08},
    "earth": {"tanpura": 0.08, "tabla": 0.05, "sub": 0.15, "attack": -0.1},
    "air":   {"melody": 0.1, "konnakol": 0.08, "attack": 0.05, "vocal_line": 0.05},
    "ether": {"mantra_drone": 0.12, "pad": 0.1, "vocal_pad": 0.1, "stereo_width": 0.15},
}

# ──────────────────────────────────────────────────────────────
# DEITY → MIX BIAS
# ──────────────────────────────────────────────────────────────

DEITY_MIX_BIAS = {
    "Agni":       {"tabla": 0.15, "electronic": 0.1, "brightness": 0.15},
    "Varuna":     {"mantra_drone": 0.12, "reverb_depth": 0.2, "electronic": -0.05},
    "Saraswati":  {"vocal_line": 0.15, "melody": 0.1, "tabla": -0.05},
    "Shiva":      {"mantra_drone": 0.15, "sub": 0.2, "konnakol": 0.1},
    "Brahma":     {},  # balanced — creation holds all
    "Indra":      {"tabla": 0.12, "electronic": 0.08, "konnakol": 0.05},
    "Soma":       {"vocal_pad": 0.12, "mantra_drone": 0.1, "reverb_depth": 0.1},
    "Vishnu":     {"tanpura": 0.08, "melody": 0.08, "pad": 0.05},
}

# ──────────────────────────────────────────────────────────────
# GUNA → TIMBRAL CHARACTER
# ──────────────────────────────────────────────────────────────

GUNA_CHARACTER = {
    "sattva": {"brightness": 0.1,  "reverb": 0.15, "compression": -0.1, "sub": 0.0},
    "rajas":  {"brightness": 0.0,  "reverb": 0.0,  "compression": 0.0,  "sub": 0.0,
               "drive": 0.15, "mid_presence": 0.2, "attack": 0.1},
    "tamas":  {"brightness": -0.2, "reverb": 0.0,  "compression": 0.0,  "sub": 0.25,
               "reverb_decay": 0.4},
}

# ──────────────────────────────────────────────────────────────
# ARC → MIX DENSITY CURVE
# ──────────────────────────────────────────────────────────────
# 8 arc zones (0.0-1.0), each with a density multiplier
# Sparse at 0.0 (tanpura only), full at 0.8, dissolving at 1.0

ARC_DENSITY = [
    (0.0, 0.15, 0.3),   # (arc_start, arc_end, density_mult)
    (0.15, 0.3, 0.5),
    (0.3, 0.45, 0.7),
    (0.45, 0.6, 0.85),
    (0.6, 0.7, 0.95),
    (0.7, 0.85, 1.0),   # climax zone
    (0.85, 0.95, 0.8),  # beginning to dissolve
    (0.95, 1.0, 0.4),   # dissolution
]

# Mode overrides
MODE_OVERRIDES = {
    "alap":  {"tabla": 0, "konnakol": 0, "bol": 0, "electronic": 0.3},
    "jod":   {"konnakol": 0.3, "electronic": 0.2},
    "gat":   {},  # no overrides
    "taan":  {"pad": 0.3, "vocal_pad": 0.2},
    "jhala": {"electronic": 0.5, "pad": 0.2, "vocal_pad": 0.1},
}
