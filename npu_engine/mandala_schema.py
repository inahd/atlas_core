"""
mandala_schema.py — Vastu mandala zone resolver.

Every zone in the 3x3 mandala is resolved from the graph,
not hardcoded in the shell.  The shell becomes a pure renderer.

Three nesting levels:
  1. Main mandala   — 9 zones, one per vastu direction
  2. Sub-mandala    — enter a layer (S0-S6), 9 domain zones
  3. Sub-zone       — enter a zone within a sub-mandala, 9 detail zones

Directional schema (vastu pada):
  NW=Vayu   N=Kubera  NE=Ishana
  W=Varuna  C=Brahma  E=Indra
  SW=Nirriti S=Yama   SE=Agni

Functions:
  resolve_zone()         — single zone content
  resolve_mandala()      — all 9 zones at once (main mandala)
  resolve_sub_mandala()  — 9 zones for a sub-layer (e.g. S5 ecology)
  resolve_sub_zone()     — 9 zones for a zone within a sub-layer (third level)
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional

# ── Vastu direction schema ──────────────────────────────────
# Each direction has element affinity, deity, and domain flavor
MANDALA_SCHEMA = {
    "NW": {"element": "air",   "deity": "Vayu",    "quality": "movement",
            "affinity": ["sound", "transmission", "herb", "shruti"]},
    "N":  {"element": "water", "deity": "Kubera",  "quality": "abundance",
            "affinity": ["calendar", "time", "tithi", "wealth"]},
    "NE": {"element": "ether", "deity": "Ishana",  "quality": "knowledge",
            "affinity": ["archetype", "sacred", "wisdom", "ritual"]},
    "W":  {"element": "water", "deity": "Varuna",  "quality": "depth",
            "affinity": ["ecology", "ocean", "wheel", "cycle"]},
    "C":  {"element": "ether", "deity": "Brahma",  "quality": "source",
            "affinity": ["field", "center", "bindu", "present"]},
    "E":  {"element": "fire",  "deity": "Indra",   "quality": "perception",
            "affinity": ["search", "database", "codex", "vision"]},
    "SW": {"element": "earth", "deity": "Nirriti", "quality": "ancestor",
            "affinity": ["guild", "companion", "root", "foundation"]},
    "S":  {"element": "earth", "deity": "Yama",    "quality": "discipline",
            "affinity": ["body", "marma", "practice", "death"]},
    "SE": {"element": "fire",  "deity": "Agni",    "quality": "transformation",
            "affinity": ["practice", "action", "offering", "dinacharya"]},
}

DIRECTIONS = ["NW", "N", "NE", "W", "C", "E", "SW", "S", "SE"]


# ── 1. Content types — every named type a zone can render ──────

CONTENT_TYPES = {
    "hero": {
        "description": "Primary entity name, large italic",
        "min_font_size": 22,
        "color_rule": "#ffffff",
    },
    "label": {
        "description": "Field label (graha, deity, element etc)",
        "min_font_size": 11,
        "color_rule": "rgba(255,255,255,0.7)",
    },
    "value": {
        "description": "Data value (Hasta, Candra, fire etc)",
        "min_font_size": 14,
        "color_rule": "#ffffff",
    },
    "deity_tag": {
        "description": "Zone guardian deity name",
        "min_font_size": 9,
        "color_rule": "#6a8090",
    },
    "zone_title": {
        "description": "Zone domain name (Sound, Rhythm etc)",
        "min_font_size": 22,
        "color_rule": "#ffffff",
    },
    "portal": {
        "description": "App link (✦ talachakra etc)",
        "min_font_size": 11,
        "color_rule": "#ffffff",
    },
    "passage": {
        "description": "Text corpus excerpt",
        "min_font_size": 14,
        "color_rule": "rgba(255,255,255,0.7)",
    },
    "signal": {
        "description": "S0 field signal text",
        "min_font_size": 14,
        "color_rule": "#ffffff",
    },
    "cosmic": {
        "description": "Yuga/manvantara context",
        "min_font_size": 11,
        "color_rule": "#6a8090",
    },
    "row": {
        "description": "Key-value data row",
        "min_font_size": 14,
        "color_rule": "#ffffff",
    },
}


# ── 2. Zone visuals — which SVG each direction renders ─────────
# These are FIXED. NW always raga_ring. Never invent new types.

ZONE_VISUALS = {
    "NW": "raga_ring",      # 12-semitone ring, active notes lit
    "N":  "tala_cycle",     # beat dots in a ring, sam gold
    "NE": "devi_yantra",    # triangle + circle + square + gates
    "W":  None,             # no visual — data only
    "C":  "moon_phase",     # waxing/waning arc from tidx
    "E":  None,             # no visual — data only
    "SW": "plant_form",     # botanical leaf SVG
    "S":  "body_region",    # human outline, active region highlighted
    "SE": "vara_arc",       # planetary glyph + time-of-day arc
}

# Allowed visual type names — shell renders these and nothing else
VISUAL_TYPES = {
    "raga_ring":    {"description": "12 semitone positions, active notes green, vadi brighter",
                     "data_keys": ["raga_aroha", "raga_avaroha", "raga_vadi"]},
    "tala_cycle":   {"description": "Beat dots in circle, sam gold, bols as labels",
                     "data_keys": ["tala_bols", "tala_beats"]},
    "devi_yantra":  {"description": "Outer square with 4 gates, circle, upward triangle, bindu",
                     "data_keys": []},
    "moon_phase":   {"description": "Circle with illuminated arc, gold stroke, from tidx",
                     "data_keys": ["tidx"]},
    "plant_form":   {"description": "Three bezier leaves on stem, earth greens",
                     "data_keys": []},
    "body_region":  {"description": "Human stick outline, active region highlighted",
                     "data_keys": ["body_region"]},
    "vara_arc":     {"description": "Day planetary glyph + semicircle time arc + position dot",
                     "data_keys": ["vara"]},
    "sri_yantra":   {"description": "Full Sri Yantra — 9 triangles, 2 lotuses, bhupura, bindu",
                     "data_keys": ["active_triangle", "co_triangulars", "triangle_color",
                                   "vastu_direction", "active_tithi_petal", "devi_petal",
                                   "psi", "polarity", "yuga", "triangle_colors"]},
}


# ── Canonical zone colors from VISUAL_STANDARDS.md ───────────
# These are cosmological, not decorative.

ZONE_BG = {
    "NW": "#0d2818", "N":  "#0d1828", "NE": "#1a0d28",
    "W":  "#0d2020", "C":  "#0d1428", "E":  "#280d0d",
    "SW": "#0d2010", "S":  "#1a1408", "SE": "#281808",
}

ZONE_BORDER = {
    "NW": "#5cb87a", "N":  "#8899bb", "NE": "#aa77dd",
    "W":  "#4da8a0", "C":  "#f0c040", "E":  "#d44040",
    "SW": "#5cb87a", "S":  "#a09070", "SE": "#f0b060",
}

ZONE_DEITY_NAME = {
    "NW": "Vayu",    "N":  "Kubera",  "NE": "Ishana",
    "W":  "Varuna",  "C":  "Brahma",  "E":  "Indra",
    "SW": "Nirriti", "S":  "Yama",    "SE": "Agni",
}


# ── 3. Navigation — explicit rules, no invention ──────────────

NAVIGATION = {
    "primary":     "left/right arrow keys cycle S0-S6",
    "enter":       "up arrow enters sub-mandala for current layer",
    "back":        "down arrow or Escape goes up one level",
    "jump":        "number keys 0-6 jump directly to that layer",
    "s0_special":  "S0 shows all layers symbolically — no sub-mandala",
    "observe":     "click entity name → observe panel slides in",
    "portal":      "click ✦ app link → iframe overlay opens",
    "stack_max":   2,
    "levels": [
        "main mandala (S0 view or layer view)",
        "sub-mandala (9 zones within a layer)",
    ],
}


# ── 4. Zone content order — rendering sequence per direction ───
# Shell renders these in this exact order. No reordering.
# Types: visual, deity_tag, zone_title, hero, row, portal

ZONE_CONTENT_ORDER = {
    "NW": ["deity_tag", "zone_title", "visual", "row", "portal"],
    "N":  ["deity_tag", "zone_title", "visual", "row", "portal"],
    "NE": ["deity_tag", "zone_title", "visual", "row", "portal"],
    "W":  ["deity_tag", "zone_title", "row", "portal"],
    "C":  ["deity_tag", "hero", "row", "visual"],
    "E":  ["deity_tag", "zone_title", "row", "portal"],
    "SW": ["deity_tag", "zone_title", "visual", "row", "portal"],
    "S":  ["deity_tag", "zone_title", "visual", "row", "portal"],
    "SE": ["deity_tag", "zone_title", "visual", "row", "portal"],
}

# ── 5. Layer zone content — what each zone shows per layer ──
# type: hero | field_rows | svg_visual | portrait | passage | signal
# visual: override visual_type for this zone in this layer (or None = use default)
# source: which field_layers key(s) provide the data
# title: zone title text
# apps: app portals for this zone
#
# MAIN mandala uses "main" key.
# Sub-mandalas use "S0"-"S6" keys.
# Shell reads layout_map from /shell/state and renders accordingly.

LAYER_ZONE_CONTENT = {
    # ═══════════════════════════════════════════════════════════
    # Directional law (never changes):
    #   NW Vayu/air:     sound, breath, transmission
    #   N  Kubera/water: time, rhythm, calendar
    #   NE Ishana/ether: sacred knowledge, deity, mantra, scripture
    #   W  Varuna/water: depth, ecology, plant, dissolution
    #   C  Brahma/all:   field now, integration, bindu
    #   E  Indra/fire:   perception, codex, text, cognition
    #   SW Nirriti/earth: ancestor, history, seed, root
    #   S  Yama/earth:   body, marma, anatomy, dharma
    #   SE Agni/fire:    action, practice, ritual, transformation
    # ═══════════════════════════════════════════════════════════

    # ── Main mandala — each direction shows its governing layer ──
    "main": {
        "NW": {"title": "Sound",     "type": "svg_visual", "visual": "raga_ring",
               "source": "S2",       "keys": ["raga", "raga_vadi", "tala"],
               "apps": ["/kala"]},
        "N":  {"title": "Rhythm",    "type": "svg_visual", "visual": "tala_cycle",
               "source": "S3",       "keys": ["nakshatra", "tithi", "nak_lord"],
               "apps": ["/agriculture"]},
        "NE": {"title": "Archetype", "type": "svg_visual", "visual": "sri_yantra",
               "source": "S1",       "keys": ["devi", "deity", "graha"],
               "apps": ["/devi/archana"]},
        "W":  {"title": "Ecology",   "type": "field_rows", "visual": "plant_form",
               "source": "S5",       "keys": ["nakshatra_plant", "element", "dosha"],
               "apps": ["/s5"]},
        "C":  {"title": None,        "type": "hero",       "visual": "moon_phase",
               "source": "panchanga","keys": ["nakshatra", "tithi", "vara", "devi"],
               "apps": []},
        "E":  {"title": "Codex",     "type": "field_rows", "visual": None,
               "source": "S6",       "keys": ["practice", "codex_mode", "companion"],
               "apps": ["/codex", "/bandhu"]},
        "SW": {"title": "Plants",    "type": "svg_visual", "visual": "plant_form",
               "source": "S5",       "keys": ["nakshatra_plant"],
               "apps": ["/s5", "/wiki"]},
        "S":  {"title": "Body",      "type": "svg_visual", "visual": "body_region",
               "source": "S5",       "keys": ["body_region", "dosha", "element"],
               "apps": []},
        "SE": {"title": "Action",    "type": "svg_visual", "visual": "vara_arc",
               "source": "S6",       "keys": ["practice", "art"],
               "apps": ["/devi/yantra"]},
    },

    # ── S0 — Metaphysical Source ──
    # NW=primordial sound  N=deep time  NE=sacred text
    # W=akasha  C=bindu  E=revelation
    # SW=ancestry  S=earth  SE=creation/dissolution
    "S0": {
        "NW": {"title": "OM",              "type": "signal",     "visual": None,
               "source": "S0",             "keys": ["signal"],
               "apps": []},
        "N":  {"title": "Yuga",            "type": "signal",     "visual": None,
               "source": "S0",             "keys": ["phase", "arc"],
               "apps": []},
        "NE": {"title": "Ashtakala",       "type": "signal",     "visual": None,
               "source": "S0",             "keys": ["signal"],
               "apps": []},
        "W":  {"title": "Akasha",          "type": "signal",     "visual": None,
               "source": "S0",             "keys": ["element_signal"],
               "apps": []},
        "C":  {"title": None,              "type": "hero",       "visual": None,
               "source": "panchanga",      "keys": ["paksha", "element"],
               "apps": []},
        "E":  {"title": "Veda",            "type": "passage",    "visual": None,
               "source": "S0",             "keys": ["guna_signal"],
               "apps": []},
        "SW": {"title": "Manvantara",      "type": "signal",     "visual": None,
               "source": "S0",             "keys": ["element_signal"],
               "apps": []},
        "S":  {"title": "Earth",           "type": "field_rows", "visual": None,
               "source": "S3",             "keys": ["nakshatra", "vara"],
               "apps": []},
        "SE": {"title": "Srishti",         "type": "signal",     "visual": None,
               "source": "S0",             "keys": ["phase"],
               "apps": []},
    },

    # ── S1 — Archetype / Deity ──
    # NW=devi's sound  N=tithi deity  NE=devi portrait (sacred knowledge)
    # W=devi's herb  C=devi hero  E=passage about her
    # SW=nakshatra deity lineage  S=her body/marma  SE=worship ritual
    "S1": {
        "NW": {"title": "Devi Raga",       "type": "field_rows", "visual": "raga_ring",
               "source": "S2",             "keys": ["raga", "raga_vadi"],
               "apps": ["/kala"]},
        "N":  {"title": "Tithi Deity",     "type": "field_rows", "visual": None,
               "source": "S1",             "keys": ["deity"],
               "apps": []},
        "NE": {"title": "Devi",            "type": "portrait",   "visual": "devi_yantra",
               "source": "S1",             "keys": ["devi", "shakti", "graha", "gana", "symbol"],
               "apps": ["/devi/archana"]},
        "W":  {"title": "Sacred Herb",     "type": "field_rows", "visual": "plant_form",
               "source": "S5",             "keys": ["nakshatra_plant"],
               "apps": ["/s5"]},
        "C":  {"title": None,              "type": "hero",       "visual": "devi_yantra",
               "source": "S1",             "keys": ["devi", "deity", "graha"],
               "apps": []},
        "E":  {"title": "Passage",         "type": "passage",    "visual": None,
               "source": "S1",             "keys": ["themes"],
               "apps": ["/codex"]},
        "SW": {"title": "Nakshatra Deity", "type": "field_rows", "visual": None,
               "source": "S1",             "keys": ["deity", "shakti"],
               "apps": ["/wiki"]},
        "S":  {"title": "Body",            "type": "svg_visual", "visual": "body_region",
               "source": "S5",             "keys": ["body_region"],
               "apps": []},
        "SE": {"title": "Worship",         "type": "field_rows", "visual": None,
               "source": "S1",             "keys": ["symbol", "themes"],
               "apps": ["/devi/archana"]},
    },

    # ── S2 — Sound / Gandharva ──
    # NW=raga (Vayu=sound)  N=tala (Kubera=rhythm)
    # NE=mantra/bija (Ishana=sacred knowledge, NOT devi portrait)
    # W=shruti (Varuna=depth/tuning)  C=raga+tala live
    # E=rasa (Indra=perception/cognition)
    # SW=gandharva texts (Nirriti=ancestry/tradition)
    # S=therapeutic (Yama=body/dharma)
    # SE=phrase/composition (Agni=action/craft)
    "S2": {
        "NW": {"title": "Raga",            "type": "svg_visual", "visual": "raga_ring",
               "source": "S2",
               "keys": ["raga", "raga_aroha", "raga_avaroha", "raga_vadi"],
               "apps": ["/kala"]},
        "N":  {"title": "Tala",            "type": "svg_visual", "visual": "tala_cycle",
               "source": "S2",
               "keys": ["tala", "tala_beats", "tala_bols", "gati"],
               "apps": ["/kala"]},
        "NE": {"title": "Mantra",          "type": "field_rows", "visual": None,
               "source": "S5",
               "keys": ["mantra"],
               "apps": []},
        "W":  {"title": "Shruti",          "type": "field_rows", "visual": None,
               "source": "S2",
               "keys": ["element_frequency", "tuning"],
               "apps": []},
        "C":  {"title": None,              "type": "hero",       "visual": "raga_ring",
               "source": "S2",
               "keys": ["raga", "tala", "raga_vadi", "bpm"],
               "apps": ["/kala"]},
        "E":  {"title": "Rasa",            "type": "field_rows", "visual": None,
               "source": "S2",
               "keys": ["raga_rasa", "raga_time"],
               "apps": ["/codex"]},
        "SW": {"title": "Gandharva",       "type": "passage",    "visual": None,
               "source": "S2",
               "keys": ["raga"],
               "apps": ["/wiki"]},
        "S":  {"title": "Therapeutic",     "type": "field_rows", "visual": "body_region",
               "source": "S5",
               "keys": ["dosha", "body_region"],
               "apps": []},
        "SE": {"title": "Phrase",          "type": "field_rows", "visual": None,
               "source": "S2",
               "keys": ["gati", "bpm"],
               "apps": []},
    },

    # ── S3 — Rhythm / Panchanga ──
    # NW=svara/sound of time (Vayu)  N=tithi (Kubera=time)
    # NE=devi of tithi (Ishana=sacred)  W=dasha (Varuna=depth/cycles)
    # C=nakshatra hero  E=passage (Indra=text/cognition)
    # SW=history (Nirriti=ancestor)  S=body (Yama=anatomy)
    # SE=muhurta (Agni=auspicious action)
    "S3": {
        "NW": {"title": "Vara",            "type": "svg_visual", "visual": "vara_arc",
               "source": "S3",
               "keys": ["vara", "nak_lord"],
               "apps": []},
        "N":  {"title": "Tithi",           "type": "field_rows", "visual": "moon_phase",
               "source": "S3",
               "keys": ["tithi", "paksha", "tithi_num"],
               "apps": []},
        "NE": {"title": "Tithi Devi",      "type": "field_rows", "visual": "devi_yantra",
               "source": "S1",
               "keys": ["devi"],
               "apps": ["/devi/archana"]},
        "W":  {"title": "Dasha",           "type": "field_rows", "visual": None,
               "source": "S3",
               "keys": ["nakshatra", "nak_lord"],
               "apps": []},
        "C":  {"title": None,              "type": "hero",       "visual": None,
               "source": "panchanga",
               "keys": ["nakshatra", "tithi", "vara"],
               "apps": []},
        "E":  {"title": "Passage",         "type": "passage",    "visual": None,
               "source": "S3",
               "keys": ["nakshatra"],
               "apps": ["/codex"]},
        "SW": {"title": "History",         "type": "field_rows", "visual": None,
               "source": "S3",
               "keys": ["nakshatra"],
               "apps": ["/wiki"]},
        "S":  {"title": "Body",            "type": "svg_visual", "visual": "body_region",
               "source": "S3",
               "keys": ["body_region"],
               "apps": []},
        "SE": {"title": "Muhurta",         "type": "field_rows", "visual": None,
               "source": "S3",
               "keys": ["nakshatra", "qualities"],
               "apps": []},
    },

    # ── S4 — Geometry / Vastu ──
    # NW=temple geometry (Vayu=transmission/form)
    # N=mandala/formation (Kubera=structure/time)
    # NE=yantra (Ishana=sacred geometry)
    # W=vastu analyzer (Varuna=spatial depth)
    # C=grid hero  E=mayamata text (Indra=text)
    # SW=brihat samhita (Nirriti=ancestral text)
    # S=compass/alignment (Yama=law/boundary)
    # SE=formation (Agni=active geometry)
    "S4": {
        "NW": {"title": "Temple",          "type": "field_rows", "visual": None,
               "source": "S4",
               "keys": ["active_zone", "zone_deity"],
               "apps": ["/vastu"]},
        "N":  {"title": "Mandala",         "type": "field_rows", "visual": None,
               "source": "S4",
               "keys": ["top_formation", "formation_count"],
               "apps": []},
        "NE": {"title": "Yantra",          "type": "svg_visual", "visual": "devi_yantra",
               "source": "S4",
               "keys": ["entity_count"],
               "apps": ["/devi/yantra"]},
        "W":  {"title": "Vastu",           "type": "field_rows", "visual": None,
               "source": "S4",
               "keys": ["active_zone", "zone_function"],
               "apps": ["/vastu"]},
        "C":  {"title": None,              "type": "hero",       "visual": None,
               "source": "S4",
               "keys": ["active_zone", "element", "guna"],
               "apps": []},
        "E":  {"title": "Mayamata",        "type": "passage",    "visual": None,
               "source": "S4",
               "keys": ["zone_function"],
               "apps": ["/codex"]},
        "SW": {"title": "Brihat Samhita",  "type": "passage",    "visual": None,
               "source": "S4",
               "keys": ["active_zone"],
               "apps": ["/wiki"]},
        "S":  {"title": "Compass",         "type": "field_rows", "visual": None,
               "source": "S4",
               "keys": ["element", "theta", "phi"],
               "apps": []},
        "SE": {"title": "Formation",       "type": "field_rows", "visual": None,
               "source": "S4",
               "keys": ["top_formation", "entity_count"],
               "apps": ["/devi/yantra"]},
    },

    # ── S5 — Ecology / Nature ──
    # NW=herb properties (Vayu=prana/breath/herb)
    # N=agricultural calendar (Kubera=seasonal time)
    # NE=sacred plants (Ishana=ritual/mantra use)
    # W=plant wheel (Varuna=ecology/depth)
    # C=today's plant hero  E=PFAF search (Indra=cognition/lookup)
    # SW=guild/companion (Nirriti=root/seed/foundation)
    # S=body-plant (Yama=marma/anatomy)
    # SE=dinacharya (Agni=daily practice)
    "S5": {
        "NW": {"title": "Herb Study",      "type": "field_rows", "visual": None,
               "source": "S5",
               "keys": ["nakshatra_plant", "dosha", "element"],
               "apps": ["/guild/search"]},
        "N":  {"title": "Calendar",        "type": "field_rows", "visual": None,
               "source": "S5",
               "keys": ["nakshatra_plant", "element"],
               "apps": ["/agriculture"]},
        "NE": {"title": "Sacred Plants",   "type": "field_rows", "visual": None,
               "source": "S5",
               "keys": ["nakshatra_plant", "mantra"],
               "apps": []},
        "W":  {"title": "Plant Wheel",     "type": "field_rows", "visual": "plant_form",
               "source": "S5",
               "keys": ["nakshatra_plant", "element"],
               "apps": ["/s5"]},
        "C":  {"title": None,              "type": "hero",       "visual": None,
               "source": "S5",
               "keys": ["nakshatra_plant", "body_region", "dosha", "element", "guna"],
               "apps": []},
        "E":  {"title": "PFAF Search",     "type": "field_rows", "visual": None,
               "source": "S5",
               "keys": ["nakshatra_plant"],
               "apps": ["/guild/search"]},
        "SW": {"title": "Guild",           "type": "field_rows", "visual": "plant_form",
               "source": "S5",
               "keys": ["nakshatra_plant"],
               "apps": ["/guild/generate"]},
        "S":  {"title": "Body-Plant",      "type": "svg_visual", "visual": "body_region",
               "source": "S5",
               "keys": ["body_region", "dosha"],
               "apps": []},
        "SE": {"title": "Dinacharya",      "type": "field_rows", "visual": None,
               "source": "S6",
               "keys": ["practice", "art"],
               "apps": []},
    },

    # ── S6 — Lila / Human Experience ──
    # NW=expression (Vayu=transmission/journal)
    # N=wiki/time (Kubera=reference/structure)
    # NE=codex (Ishana=sacred study/scripture)
    # W=bandhu (Varuna=depth/companion)
    # C=practice hero  E=research (Indra=perception/inquiry)
    # SW=lila/game (Nirriti=history/play/roots)
    # S=art/form (Yama=discipline/craft)
    # SE=offering (Agni=ritual/transformation)
    "S6": {
        "NW": {"title": "Journal",         "type": "field_rows", "visual": None,
               "source": "S6",
               "keys": ["nakshatra", "vara"],
               "apps": []},
        "N":  {"title": "Wiki",            "type": "field_rows", "visual": None,
               "source": "S3",
               "keys": ["nakshatra"],
               "apps": ["/wiki"]},
        "NE": {"title": "Codex",           "type": "field_rows", "visual": None,
               "source": "S6",
               "keys": ["codex_mode", "practice"],
               "apps": ["/codex"]},
        "W":  {"title": "Bandhu",          "type": "field_rows", "visual": None,
               "source": "S6",
               "keys": ["companion"],
               "apps": ["/bandhu"]},
        "C":  {"title": None,              "type": "hero",       "visual": None,
               "source": "S6",
               "keys": ["practice", "art", "companion"],
               "apps": []},
        "E":  {"title": "Research",        "type": "field_rows", "visual": None,
               "source": "S6",
               "keys": ["codex_mode"],
               "apps": ["/research"]},
        "SW": {"title": "Lila",            "type": "field_rows", "visual": None,
               "source": "S6",
               "keys": ["practice"],
               "apps": ["/lila"]},
        "S":  {"title": "Art",             "type": "field_rows", "visual": None,
               "source": "S6",
               "keys": ["art"],
               "apps": ["/kala"]},
        "SE": {"title": "Offering",        "type": "field_rows", "visual": None,
               "source": "S6",
               "keys": ["practice", "art"],
               "apps": ["/devi/archana"]},
    },
}


def _resolve_layout_zone(layer_key: str, direction: str,
                         panchanga: dict, layers: dict) -> dict:
    """Resolve a single zone's data from LAYER_ZONE_CONTENT.

    Returns the zone's layout definition enriched with resolved data
    values from field_layers.
    """
    lzc = LAYER_ZONE_CONTENT.get(layer_key, {}).get(direction)
    if not lzc:
        return {}

    source_key = lzc.get("source", "")
    keys = lzc.get("keys", [])

    # Get source data dict
    if source_key == "panchanga":
        src = panchanga
    else:
        src = layers.get(source_key, {})

    # Resolve data values
    data = {}
    for k in keys:
        val = src.get(k)
        if val is not None:
            data[k] = val

    return {
        "title": lzc.get("title"),
        "type": lzc["type"],
        "visual": lzc.get("visual"),
        "source": source_key,
        "keys": keys,
        "apps": lzc.get("apps", []),
        "data": data,
    }


def resolve_layout_map(layer_key: str, panchanga: dict,
                       layers: dict) -> dict:
    """Resolve the full layout_map for a layer.

    Returns {direction: {title, type, visual, source, data, apps}}
    for all 9 directions.
    """
    layout = {}
    for d in DIRECTIONS:
        layout[d] = _resolve_layout_zone(layer_key, d, panchanga, layers)
    return layout


# ── S-layer sub-mandala definitions ─────────────────────────
# Each layer defines how its 9 zones are named and what data
# populates them.  The center is always the field moment.
# Zones are keyed by direction → {name, data_key, apps, bg}

SUB_MANDALA_DEFS = {
    "S5": {
        "name": "Ecology",
        "color": "#5cb87a",
        "bg_palette": {
            "NW": "#0d2818", "N": "#0d2015", "NE": "#102818",
            "W":  "#0d2010", "C": "#0d1a10", "E":  "#10200d",
            "SW": "#0d1808", "S": "#1a1408", "SE": "#181a08",
        },
        "zones": {
            "NW": {"name": "Herb Study",     "icon": "herb",
                   "source": "s5_herbs",     "apps": ["/guild/search"]},
            "N":  {"name": "Calendar",       "icon": "calendar",
                   "source": "agriculture",  "apps": ["/agriculture"]},
            "NE": {"name": "Sacred Plants",  "icon": "sacred",
                   "source": "s5_sacred",    "apps": []},
            "W":  {"name": "Plant Wheel",    "icon": "wheel",
                   "source": "s5_wheel",     "apps": ["/s5"]},
            "C":  {"name": "Today",          "icon": "field",
                   "source": "s5_center",    "apps": []},
            "E":  {"name": "PFAF Search",    "icon": "search",
                   "source": "s5_search",    "apps": ["/guild/search"]},
            "SW": {"name": "Guild Mandala",  "icon": "guild",
                   "source": "s5_guild",     "apps": ["/guild/generate"]},
            "S":  {"name": "Body-Plant",     "icon": "body",
                   "source": "s5_body",      "apps": []},
            "SE": {"name": "Practice",       "icon": "practice",
                   "source": "s5_practice",  "apps": []},
        },
    },
    "S1": {
        "name": "Archetype",
        "color": "#A78BFA",
        "bg_palette": {
            "NW": "#1a0d28", "N": "#180d28", "NE": "#200d28",
            "W":  "#150d20", "C": "#100d1a", "E":  "#1a0d20",
            "SW": "#120d18", "S": "#140d1a", "SE": "#180d20",
        },
        "zones": {
            "NW": {"name": "Graha",     "icon": "planet",  "source": "s1_graha",  "apps": []},
            "N":  {"name": "Deity",     "icon": "deity",   "source": "s1_deity",  "apps": []},
            "NE": {"name": "Devi",      "icon": "devi",    "source": "s1_devi",   "apps": ["/devi/archana"]},
            "W":  {"name": "Mantra",    "icon": "mantra",  "source": "s1_mantra", "apps": []},
            "C":  {"name": "Field",     "icon": "field",   "source": "s1_center", "apps": []},
            "E":  {"name": "Yantra",    "icon": "yantra",  "source": "s1_yantra", "apps": ["/devi/yantra"]},
            "SW": {"name": "Vahana",    "icon": "vahana",  "source": "s1_vahana", "apps": []},
            "S":  {"name": "Shakti",    "icon": "shakti",  "source": "s1_shakti", "apps": []},
            "SE": {"name": "Bija",      "icon": "seed",    "source": "s1_bija",   "apps": []},
        },
    },
    "S2": {
        "name": "Sound",
        "color": "#1d9e75",
        "bg_palette": {
            "NW": "#0d2820", "N": "#0d2018", "NE": "#0d2825",
            "W":  "#0d2018", "C": "#0d1a15", "E":  "#0d2020",
            "SW": "#0d1a10", "S": "#0d1815", "SE": "#0d2018",
        },
        "zones": {
            "NW": {"name": "Shruti",      "icon": "shruti",  "source": "s2_shruti",  "apps": []},
            "N":  {"name": "Tala",        "icon": "tala",    "source": "s2_tala",    "apps": []},
            "NE": {"name": "Raga",        "icon": "raga",    "source": "s2_raga",    "apps": []},
            "W":  {"name": "Melody",      "icon": "melody",  "source": "s2_melody",  "apps": []},
            "C":  {"name": "Field",       "icon": "field",   "source": "s2_center",  "apps": []},
            "E":  {"name": "Mantra",      "icon": "mantra",  "source": "s2_mantra",  "apps": []},
            "SW": {"name": "Rhythm",      "icon": "rhythm",  "source": "s2_rhythm",  "apps": []},
            "S":  {"name": "Voice",       "icon": "voice",   "source": "s2_voice",   "apps": []},
            "SE": {"name": "Composition", "icon": "compose",  "source": "s2_compose", "apps": []},
        },
    },
    "S3": {
        "name": "Panchanga",
        "color": "#F0C040",
        "bg_palette": {
            "NW": "#1a1808", "N": "#201a08", "NE": "#1a1a08",
            "W":  "#181408", "C": "#141008", "E":  "#181808",
            "SW": "#141008", "S": "#181208", "SE": "#1a1408",
        },
        "zones": {
            "NW": {"name": "Vara",      "icon": "sun",      "source": "s3_vara",     "apps": []},
            "N":  {"name": "Tithi",     "icon": "moon",     "source": "s3_tithi",    "apps": []},
            "NE": {"name": "Nakshatra", "icon": "star",     "source": "s3_nakshatra","apps": []},
            "W":  {"name": "Muhurta",   "icon": "clock",    "source": "s3_muhurta",  "apps": []},
            "C":  {"name": "Field",     "icon": "field",    "source": "s3_center",   "apps": []},
            "E":  {"name": "Dasha",     "icon": "cycle",    "source": "s3_dasha",    "apps": []},
            "SW": {"name": "Transit",   "icon": "transit",  "source": "s3_transit",  "apps": []},
            "S":  {"name": "Yoga",      "icon": "yoga",     "source": "s3_yoga",     "apps": []},
            "SE": {"name": "Karana",    "icon": "half",     "source": "s3_karana",   "apps": []},
        },
    },
    "S4": {
        "name": "Geometry",
        "color": "#534AB7",
        "bg_palette": {
            "NW": "#0d0d28", "N": "#100d28", "NE": "#0d1028",
            "W":  "#0d0d20", "C": "#0d0d1a", "E":  "#100d20",
            "SW": "#0d0d18", "S": "#0d0d1a", "SE": "#100d1a",
        },
        "zones": {
            "NW": {"name": "Geometry",  "icon": "shape",    "source": "s4_geometry",  "apps": []},
            "N":  {"name": "Vastu",     "icon": "grid",     "source": "s4_vastu",     "apps": ["/vastu"]},
            "NE": {"name": "Yantra",    "icon": "yantra",   "source": "s4_yantra",    "apps": ["/devi/yantra"]},
            "W":  {"name": "Temple",    "icon": "temple",   "source": "s4_temple",    "apps": []},
            "C":  {"name": "Field",     "icon": "field",    "source": "s4_center",    "apps": []},
            "E":  {"name": "Mandala",   "icon": "mandala",  "source": "s4_mandala",   "apps": []},
            "SW": {"name": "Grid",      "icon": "grid",     "source": "s4_grid",      "apps": []},
            "S":  {"name": "Compass",   "icon": "compass",  "source": "s4_compass",   "apps": []},
            "SE": {"name": "Formation", "icon": "form",     "source": "s4_formation", "apps": []},
        },
    },
    "S6": {
        "name": "Lila",
        "color": "#d4943a",
        "bg_palette": {
            "NW": "#1a1008", "N": "#201408", "NE": "#1a1208",
            "W":  "#181008", "C": "#140d08", "E":  "#181208",
            "SW": "#140d08", "S": "#160d08", "SE": "#181008",
        },
        "zones": {
            "NW": {"name": "Wiki",     "icon": "wiki",    "source": "s6_wiki",    "apps": ["/wiki"]},
            "N":  {"name": "Codex",    "icon": "book",    "source": "s6_codex",   "apps": ["/codex"]},
            "NE": {"name": "Practice", "icon": "practice","source": "s6_practice","apps": []},
            "W":  {"name": "Bandhu",   "icon": "chat",    "source": "s6_bandhu",  "apps": ["/bandhu"]},
            "C":  {"name": "Field",    "icon": "field",   "source": "s6_center",  "apps": []},
            "E":  {"name": "Journal",  "icon": "pen",     "source": "s6_journal", "apps": []},
            "SW": {"name": "Lila",     "icon": "play",    "source": "s6_lila",    "apps": []},
            "S":  {"name": "Art",      "icon": "art",     "source": "s6_art",     "apps": []},
            "SE": {"name": "Offering", "icon": "flame",   "source": "s6_offering","apps": []},
        },
    },
}


# ── Sub-zone definitions (third nesting level) ──────────────
# Key: "layer_direction" → 9 inner zones
# Each zone that has an entry here gets has_sub_zone=True
# in the sub-mandala response.

SUB_ZONE_DEFS = {
    # ── S5 Ecology sub-zones ────────────────────────────────
    "S5_SW": {
        "name": "Guild · Companion Planting",
        "color": "#5cb87a",
        "source_key": "guild",
        "zones": {
            "NW": {"name": "Nitrogen Fixers",      "source": "guild_nfix",    "affinity": "N-fix"},
            "N":  {"name": "Timing",               "source": "guild_timing",  "affinity": "calendar"},
            "NE": {"name": "Sacred Species",        "source": "guild_sacred",  "affinity": "ritual"},
            "W":  {"name": "Dynamic Accumulators",  "source": "guild_mineral", "affinity": "mineral"},
            "C":  {"name": "Center Plant",          "source": "guild_center",  "affinity": "hero"},
            "E":  {"name": "PFAF Lookup",           "source": "guild_pfaf",    "affinity": "search"},
            "SW": {"name": "Ground Cover",          "source": "guild_ground",  "affinity": "earth"},
            "S":  {"name": "Medicinal",             "source": "guild_med",     "affinity": "heal"},
            "SE": {"name": "Pollinators",           "source": "guild_poll",    "affinity": "flower"},
        },
    },
    "S5_NE": {
        "name": "Sacred Plant Study",
        "color": "#5cb87a",
        "source_key": "sacred",
        "zones": {
            "NW": {"name": "Ayurveda Use",     "source": "sacred_ayur",    "affinity": "heal"},
            "N":  {"name": "Calendar",          "source": "sacred_cal",     "affinity": "time"},
            "NE": {"name": "Mantra",            "source": "sacred_mantra",  "affinity": "ritual"},
            "W":  {"name": "Taxonomy",          "source": "sacred_taxon",   "affinity": "form"},
            "C":  {"name": "Sacred Plant",      "source": "sacred_center",  "affinity": "hero"},
            "E":  {"name": "Passage",           "source": "sacred_passage", "affinity": "text"},
            "SW": {"name": "History",           "source": "sacred_hist",    "affinity": "past"},
            "S":  {"name": "Body Region",       "source": "sacred_body",    "affinity": "body"},
            "SE": {"name": "Ritual Use",        "source": "sacred_ritual",  "affinity": "fire"},
        },
    },
    "S5_E": {
        "name": "PFAF · Plant Database",
        "color": "#5cb87a",
        "source_key": "pfaf",
        "zones": {
            "NW": {"name": "Edibility",        "source": "pfaf_edible",  "affinity": "food"},
            "N":  {"name": "Habitat",           "source": "pfaf_habitat", "affinity": "place"},
            "NE": {"name": "Cultivation",       "source": "pfaf_cult",    "affinity": "grow"},
            "W":  {"name": "Taxonomy",          "source": "pfaf_taxon",   "affinity": "form"},
            "C":  {"name": "Plant Profile",     "source": "pfaf_center",  "affinity": "hero"},
            "E":  {"name": "Medicinal Use",     "source": "pfaf_med",     "affinity": "heal"},
            "SW": {"name": "Propagation",       "source": "pfaf_prop",    "affinity": "root"},
            "S":  {"name": "Physical",          "source": "pfaf_phys",    "affinity": "body"},
            "SE": {"name": "Companion Plants",  "source": "pfaf_comp",    "affinity": "guild"},
        },
    },

    # ── S1 Archetype sub-zones ──────────────────────────────
    "S1_NE": {
        "name": "Devi Portrait",
        "color": "#A78BFA",
        "source_key": "devi_portrait",
        "zones": {
            "NW": {"name": "Graha",     "source": "devi_graha",   "affinity": "planet"},
            "N":  {"name": "Vahana",    "source": "devi_vahana",  "affinity": "mount"},
            "NE": {"name": "Yantra",    "source": "devi_yantra",  "affinity": "geometry"},
            "W":  {"name": "Mantra",    "source": "devi_mantra",  "affinity": "sound"},
            "C":  {"name": "Devi",      "source": "devi_center",  "affinity": "hero"},
            "E":  {"name": "Passage",   "source": "devi_passage", "affinity": "text"},
            "SW": {"name": "Weapon",    "source": "devi_weapon",  "affinity": "ayudha"},
            "S":  {"name": "Shakti",    "source": "devi_shakti",  "affinity": "power"},
            "SE": {"name": "Ritual",    "source": "devi_ritual",  "affinity": "worship"},
        },
    },
    "S1_N": {
        "name": "Deity Portrait",
        "color": "#A78BFA",
        "source_key": "deity_portrait",
        "zones": {
            "NW": {"name": "Graha",     "source": "deity_graha",   "affinity": "planet"},
            "N":  {"name": "Attributes","source": "deity_attr",    "affinity": "quality"},
            "NE": {"name": "Mythology", "source": "deity_myth",    "affinity": "story"},
            "W":  {"name": "Mantra",    "source": "deity_mantra",  "affinity": "sound"},
            "C":  {"name": "Deity",     "source": "deity_center",  "affinity": "hero"},
            "E":  {"name": "Passage",   "source": "deity_passage", "affinity": "text"},
            "SW": {"name": "Nakshatra", "source": "deity_nak",     "affinity": "star"},
            "S":  {"name": "Form",      "source": "deity_form",    "affinity": "body"},
            "SE": {"name": "Worship",   "source": "deity_worship", "affinity": "fire"},
        },
    },

    # ── S2 Sound sub-zones ──────────────────────────────────
    "S2_NE": {
        "name": "Raga Study",
        "color": "#1d9e75",
        "source_key": "raga_study",
        "zones": {
            "NW": {"name": "Shruti",      "source": "raga_shruti",  "affinity": "tuning"},
            "N":  {"name": "Aroha",        "source": "raga_aroha",   "affinity": "ascent"},
            "NE": {"name": "Rasa",         "source": "raga_rasa",    "affinity": "emotion"},
            "W":  {"name": "Avaroha",      "source": "raga_avaroha", "affinity": "descent"},
            "C":  {"name": "Raga",         "source": "raga_center",  "affinity": "hero"},
            "E":  {"name": "History",      "source": "raga_hist",    "affinity": "text"},
            "SW": {"name": "Chalan",       "source": "raga_chalan",  "affinity": "movement"},
            "S":  {"name": "Therapeutic",  "source": "raga_therapy",  "affinity": "heal"},
            "SE": {"name": "Performance",  "source": "raga_perf",    "affinity": "action"},
        },
    },
    "S2_N": {
        "name": "Tala Study",
        "color": "#1d9e75",
        "source_key": "tala_study",
        "zones": {
            "NW": {"name": "Theka",      "source": "tala_theka",   "affinity": "pattern"},
            "N":  {"name": "Bol Cycle",   "source": "tala_bols",    "affinity": "time"},
            "NE": {"name": "Vibhag",      "source": "tala_vibhag",  "affinity": "section"},
            "W":  {"name": "Layakari",    "source": "tala_laya",    "affinity": "speed"},
            "C":  {"name": "Tala",        "source": "tala_center",  "affinity": "hero"},
            "E":  {"name": "Tihai",       "source": "tala_tihai",   "affinity": "cadence"},
            "SW": {"name": "History",     "source": "tala_hist",    "affinity": "past"},
            "S":  {"name": "Gati",        "source": "tala_gati",    "affinity": "body"},
            "SE": {"name": "Composition", "source": "tala_comp",    "affinity": "form"},
        },
    },

    # ── S4 Geometry sub-zones ───────────────────────────────
    "S4_NE": {
        "name": "Yantra Study",
        "color": "#534AB7",
        "source_key": "yantra_study",
        "zones": {
            "NW": {"name": "Geometry",    "source": "yantra_geom",   "affinity": "shape"},
            "N":  {"name": "Deity",       "source": "yantra_deity",  "affinity": "god"},
            "NE": {"name": "Bija",        "source": "yantra_bija",   "affinity": "seed"},
            "W":  {"name": "Petals",      "source": "yantra_petals", "affinity": "ring"},
            "C":  {"name": "Yantra",      "source": "yantra_center", "affinity": "hero"},
            "E":  {"name": "Meditation",  "source": "yantra_med",    "affinity": "practice"},
            "SW": {"name": "Tradition",   "source": "yantra_trad",   "affinity": "past"},
            "S":  {"name": "Material",    "source": "yantra_mat",    "affinity": "body"},
            "SE": {"name": "Consecration","source": "yantra_cons",   "affinity": "fire"},
        },
    },
    "S4_N": {
        "name": "Vastu Grid",
        "color": "#534AB7",
        "source_key": "vastu_grid",
        "zones": {
            "NW": {"name": "Vayu Zone",   "source": "vastu_nw",  "affinity": "air"},
            "N":  {"name": "Kubera Zone",  "source": "vastu_n",   "affinity": "wealth"},
            "NE": {"name": "Ishana Zone",  "source": "vastu_ne",  "affinity": "sacred"},
            "W":  {"name": "Varuna Zone",  "source": "vastu_w",   "affinity": "water"},
            "C":  {"name": "Brahmasthana", "source": "vastu_c",   "affinity": "center"},
            "E":  {"name": "Indra Zone",   "source": "vastu_e",   "affinity": "king"},
            "SW": {"name": "Nirriti Zone", "source": "vastu_sw",  "affinity": "earth"},
            "S":  {"name": "Yama Zone",    "source": "vastu_s",   "affinity": "law"},
            "SE": {"name": "Agni Zone",    "source": "vastu_se",  "affinity": "fire"},
        },
    },
}


def _has_sub_zone(layer: str, direction: str) -> bool:
    """Check if a zone within a sub-mandala has its own third-level mandala."""
    return f"{layer}_{direction}" in SUB_ZONE_DEFS


# ── Zone resolution ─────────────────────────────────────────

def _entity_to_zone_row(eid: str, meta: dict) -> dict:
    """Convert entity metadata to a zone display row."""
    name = meta.get("name", eid.split("_", 1)[-1].replace("_", " ").title())
    return {
        "id": eid,
        "name": name,
        "element": meta.get("element", ""),
        "category": meta.get("category", ""),
    }


def _top_entities_for(graph, seed_ids: List[str],
                      category_filter: str = "",
                      limit: int = 5) -> List[dict]:
    """Get top entities related to seeds, optionally filtered."""
    if not graph or not seed_ids:
        return []
    expanded = graph.expand_from_entities(seed_ids, depth=1, max_per_node=8)
    scored = graph.score_relations(seed_ids, expanded)
    seen = set()
    results = []
    for edge in scored:
        eid = edge.get("to_id", "")
        if eid in seen or eid in seed_ids:
            continue
        meta = graph.meta(eid)
        if category_filter and meta.get("category", "") != category_filter:
            continue
        seen.add(eid)
        row = _entity_to_zone_row(eid, meta)
        row["score"] = edge.get("_score", 0)
        row["relation"] = edge.get("relation", "")
        results.append(row)
        if len(results) >= limit:
            break
    return results


def _graph_neighbors(graph, eid: str, relation_type: str = None,
                     limit: int = 5) -> List[dict]:
    """Direct neighbors of an entity."""
    if not graph:
        return []
    neighbors = graph.get_neighbors(eid, relation_types=[relation_type] if relation_type else None)
    results = []
    for edge in neighbors[:limit]:
        meta = graph.meta(edge["to_id"])
        row = _entity_to_zone_row(edge["to_id"], meta)
        row["relation"] = edge.get("relation", "")
        row["confidence"] = edge.get("confidence", 0)
        results.append(row)
    return results


# ── Entity symbol + color lookup (cached from datasets) ──────
_ENTITY_SYMBOLS = None  # {slug: {symbol, color}}

def _load_entity_symbols() -> dict:
    """Load symbol and color for entities from canonical CSVs."""
    global _ENTITY_SYMBOLS
    if _ENTITY_SYMBOLS is not None:
        return _ENTITY_SYMBOLS
    import csv
    _ENTITY_SYMBOLS = {}
    root = __import__("pathlib").Path(__file__).parent.parent / "datasets"

    # Grahas — index by both English and Sanskrit names
    _GRAHA_SANSKRIT = {
        "sun": ["surya", "ravi"], "moon": ["chandra", "candra", "soma"],
        "mars": ["mangala", "kuja"], "mercury": ["budha"],
        "jupiter": ["guru", "brihaspati"], "venus": ["shukra", "sukra"],
        "saturn": ["shani", "sani"], "rahu": ["rahu"], "ketu": ["ketu"],
    }
    p = root / "cosmology" / "graha_master.csv"
    if p.exists():
        with p.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                name = r.get("graha", "")
                entry = {"symbol": r.get("symbol", ""), "color": r.get("color_primary", "#ffffff")}
                _ENTITY_SYMBOLS[_slug(name)] = entry
                # Also index by Sanskrit names
                for sn in _GRAHA_SANSKRIT.get(_slug(name), []):
                    _ENTITY_SYMBOLS[sn] = entry
    # Nakshatras
    p = root / "cosmology" / "nakshatra_master.csv"
    if p.exists():
        with p.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                name = r.get("nakshatra", "")
                _ENTITY_SYMBOLS[_slug(name)] = {
                    "symbol": r.get("glyph", "✶"),
                    "color": r.get("color_hex", "#ffffff"),
                }
    # Nitya Devis
    p = root / "nitya_devi_mapping.csv"
    if p.exists():
        with p.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                name = r.get("nitya_devi", "")
                _ENTITY_SYMBOLS[_slug(name)] = {
                    "symbol": "✦",
                    "color": r.get("color_hex", "#aa77dd"),
                }
    return _ENTITY_SYMBOLS


# Category fallback symbols — used when entity not found in datasets
_CAT_SYM = {
    "deity": "✦", "devi": "✦", "graha": "☽", "nakshatra": "✶",
    "raga": "♪", "tala": "○", "plant": "❧", "element": "◉",
    "dosha": "〜", "body_region": "◉", "mantra": "ॐ",
    "yantra": "△", "vastu": "⬡", "metal": "⚙", "ratna": "💎",
}
_CAT_COLOR = {
    "graha": "#c8d8f0", "nakshatra": "#c8d8f0", "devi": "#aa77dd",
    "deity": "#aa77dd", "raga": "#5cb87a", "plant": "#5cb87a",
    "element": "#8899bb", "dosha": "#8899bb",
}


def _entity_sym_color(field_key: str, value: str) -> tuple:
    """Return (symbol, color) for a field value.

    Looks up in dataset CSVs first, then category fallback.
    """
    syms = _load_entity_symbols()
    vslug = _slug(value)

    # Direct lookup by value slug
    entry = syms.get(vslug)
    if entry:
        return entry["symbol"], entry["color"]

    # Category fallback from field key
    sym = _CAT_SYM.get(field_key, "")
    col = _CAT_COLOR.get(field_key, "#ffffff")
    return sym, col


def _build_zone_response(direction: str, layer_key: str,
                         panchanga: dict, layers: dict,
                         weight: float = 1.0,
                         extra_data: dict = None,
                         entities: list = None,
                         has_sub_zone: bool = False,
                         bg_override: str = None) -> dict:
    """Build the canonical zone response per SHELL_STATE_TEMPLATE.md.

    Every visual and typographic decision is made here.
    The shell applies it mechanically — no CSS logic needed.
    """
    is_center = (direction == "C")
    lzc = LAYER_ZONE_CONTENT.get(layer_key, {}).get(direction, {})

    # ── Source data ──
    source_key = lzc.get("source", "")
    data_keys = lzc.get("keys", [])
    src = panchanga if source_key == "panchanga" else layers.get(source_key, {})
    resolved = {}
    for k in data_keys:
        val = src.get(k)
        if val is not None:
            resolved[k] = val
    if extra_data:
        resolved.update(extra_data)

    # ── Zone identity ──
    zone_label = lzc.get("title", "")
    zone_type = lzc.get("type", "field_rows")
    deity = ZONE_DEITY_NAME.get(direction, "Brahma")
    border_color = ZONE_BORDER.get(direction, "#f0c040")

    # ── Title (hero value) ──
    if zone_type == "hero" or is_center:
        title = ""
        for k in data_keys:
            v = resolved.get(k)
            if isinstance(v, dict) and k == "devi":
                title = v.get("name", "")
                if title:
                    break
            elif v and isinstance(v, str):
                title = v
                break
        if not title:
            title = panchanga.get("nakshatra", "Field")
    elif zone_type == "portrait":
        title = str(resolved.get(data_keys[0], "")) if data_keys else ""
    else:
        title = zone_label

    # ── Visual ──
    visual_type = lzc.get("visual") or ZONE_VISUALS.get(direction)
    visual_data = _build_visual_data(visual_type, direction, resolved, src, layers, panchanga)

    # ── Rows: [{label, value, symbol, entity_id, value_color, ...}] ──
    rows = []
    clickable_keys = {"canonical_plant", "plant", "deity", "graha", "nakshatra",
                      "devi", "raga", "tala", "yantra", "nak_lord"}
    _PREFIX = {"graha": "graha_", "nak_lord": "graha_", "deity": "deity_",
               "devi": "devi_", "nakshatra": "nakshatra_", "raga": "raga_",
               "tala": "tala_", "yantra": "yantra_"}

    for k in data_keys:
        val = resolved.get(k)
        if val is None or val == "":
            continue
        # Handle devi dict from panchanga
        if isinstance(val, dict) and k == "devi":
            vs = val.get("name", "")
            if not vs:
                continue
            val = vs  # fall through to normal processing
        elif isinstance(val, (list, dict)):
            continue
        vs = str(val)
        if is_center and vs == title:
            continue
        is_click = k in clickable_keys
        eid = None
        if is_click:
            pfx = _PREFIX.get(k, "plant_")
            slug_val = _slug(vs)
            # Normalize IAST graha names to graph format
            if pfx == "graha_":
                slug_val = {"candra": "chandra", "sukra": "shukra",
                            "sani": "shani"}.get(slug_val, slug_val)
            eid = pfx + slug_val
        sym, vcol = _entity_sym_color(k, vs) if is_click else ("", "#ffffff")
        rows.append({
            "label": k,
            "value": vs,
            "symbol": sym,
            "label_color": "#7a8fa0",
            "value_color": vcol,
            "value_size": 14,
            "clickable": is_click,
            "entity_id": eid,
        })

    # Enrich clickable entities with their key graph relations
    # This makes devi weapons, raga rasas, etc. visible in zones
    _ENRICH_RELS = {
        "devi_weapon", "devi_rasa", "devi_shakti", "devi_mantra",
        "raga_rasa", "raga_devi", "nakshatra_element", "nakshatra_guna",
    }
    if entities is not None:
        # entities param is from _top_entities_for — check clickable rows too
        _enriched_eids = set()
        for row in rows:
            row_eid = row.get("entity_id")
            if not row_eid or row_eid in _enriched_eids:
                continue
            _enriched_eids.add(row_eid)
            # Pull this entity's relations from graph
            try:
                from npu_engine.graph_engine import GraphEngine
                _g = GraphEngine()
                for edge in _g.get_neighbors(row_eid):
                    rel = edge.get("relation", "")
                    if rel not in _ENRICH_RELS:
                        continue
                    target = edge.get("to_id", "")
                    tname = target.replace("_", " ") if "_" in target else target
                    tcat = target.split("_")[0] if "_" in target else ""
                    sym = _CAT_SYM.get(tcat, "")
                    vcol = _CAT_COLOR.get(tcat, "#ffffff")
                    rows.append({
                        "label": rel.replace("devi_","").replace("raga_","").replace("nakshatra_",""),
                        "value": tname,
                        "symbol": sym,
                        "label_color": "#7a8fa0",
                        "value_color": vcol,
                        "value_size": 14,
                        "clickable": True,
                        "entity_id": target,
                    })
            except Exception:
                pass

    # Entity rows from graph — skip internal relations
    _SKIP_RELATIONS = {"nakshatra_has_pada", "nakshatra_pada_entity",
                       "pada_has_navamsa", "inverse_of"}
    for ent in (entities or []):
        rel = ent.get("relation", "")
        if rel in _SKIP_RELATIONS:
            continue
        ent_name = ent.get("name", ent.get("id", ""))
        if not ent_name or ent_name in ("1", "2", "3", "4"):
            continue
        ent_id = ent.get("id", "")
        ent_cat = ent_id.split("_")[0] if "_" in ent_id else ""
        sym = _CAT_SYM.get(ent_cat, "")
        vcol = _CAT_COLOR.get(ent_cat, "#ffffff")
        rows.append({
            "label": rel or ent.get("category", "entity"),
            "value": ent_name,
            "symbol": sym,
            "label_color": "#7a8fa0",
            "value_color": vcol,
            "value_size": 14,
            "clickable": True,
            "entity_id": ent_id,
        })

    # ── Apps: [{name, url, color}] ──
    apps = []
    for url in lzc.get("apps", []):
        name = url.strip("/").split("/")[-1]
        apps.append({"name": name, "url": url, "color": border_color})

    # ── Build response per SHELL_STATE_TEMPLATE.md ──
    zone = {
        "id": direction.lower(),
        "deity": deity,
        "domain": zone_label or direction,
        "layer_ref": source_key,

        "bg": bg_override or ZONE_BG.get(direction, "#0d1428"),
        "border_color": border_color,
        "border_width": "2px" if not is_center else "0",

        "title": title,
        "title_font": "Cormorant Garamond",
        "title_size": 48 if is_center else 22,
        "title_style": "italic",
        "title_color": "#f0c040" if is_center else "#ffffff",

        "deity_color": border_color,
        "deity_size": 9,

        "visual": {
            "type": visual_type,
            "data": visual_data,
        } if visual_type else {"type": None, "data": {}},

        "rows": rows,
        "apps": apps,
        "weight": weight,
        "has_sub_mandala": has_sub_zone,
    }

    # Center gets extra fields per template
    if is_center:
        tithi = panchanga.get("tithi", "")
        vara = panchanga.get("vara", "")
        devi = panchanga.get("devi", "")
        if isinstance(devi, list):
            devi = devi[0] if devi else ""

        zone["hero"] = {
            "text": title,
            "font": "Cormorant Garamond",
            "size": 48,
            "style": "italic",
            "color": "#f0c040",
        }
        zone["sub_hero"] = (tithi + " \u00b7 " + vara).strip(" \u00b7 ")
        zone["sub_hero_color"] = "#c8d8f0"
        zone["sub_hero_size"] = 14
        if isinstance(devi, dict):
            zone["field_signal"] = devi.get("name", "")
        elif isinstance(devi, (list, tuple)):
            zone["field_signal"] = devi[0] if devi else ""
        else:
            zone["field_signal"] = str(devi)
        zone["field_signal_color"] = "#8899aa"
        zone["field_signal_size"] = 13

        tidx = panchanga.get("tidx", 0)
        zone["moon"] = {
            "tidx": tidx,
            "phase": "waxing" if tidx < 15 else "waning",
            "color": "#c8a840",
            "bg_color": "#4a4020",
        }

    # ── Three-depth architecture ──
    # symbol: glyph + name + color (always available)
    # infographic: visual type + data (already in zone["visual"])
    # study: passages for the primary entity
    primary_eid = None
    for r in rows:
        if r.get("entity_id"):
            primary_eid = r["entity_id"]
            break

    zone["active_depth"] = "infographic" if is_center else "symbol"
    zone["symbol_depth"] = {
        "glyph": rows[0].get("symbol", "◉") if rows else "◉",
        "name": title,
        "color": zone.get("title_color", "#ffffff"),
        "label": f"{deity} · {zone_label}" if zone_label else deity,
    }
    zone["study_depth"] = {
        "primary_entity": primary_eid,
        "passages": [],  # filled by caller if needed
    }

    return zone


def _build_visual_data(visual_type: str, direction: str,
                       resolved: dict, src: dict,
                       layers: dict, panchanga: dict) -> dict:
    """Build the complete visual data object for an SVG generator.

    Every color is a solid hex. The shell generator receives this
    and renders mechanically.
    """
    if not visual_type:
        return {}

    s2 = layers.get("S2", {})
    s3 = layers.get("S3", {})
    s5 = layers.get("S5", {})

    if visual_type == "raga_ring":
        aroha = resolved.get("raga_aroha") or s2.get("raga_aroha", [])
        avaroha = resolved.get("raga_avaroha") or s2.get("raga_avaroha", [])
        vadi = resolved.get("raga_vadi") or s2.get("raga_vadi", "")
        # Map swara names to semitone indices
        # Labels are single-letter abbreviations used in the SVG
        LABELS = ["S", "r", "R", "g", "G", "m", "M", "P", "d", "D", "n", "N"]
        # Full swara names map to the same positions
        SWARA_MAP = {
            "Sa": 0, "S": 0,
            "Re": 2, "R": 2, "re": 1, "r": 1,
            "Ga": 4, "G": 4, "ga": 3, "g": 3,
            "Ma": 5, "m": 5, "ma": 6, "M": 6, "Ma_t": 6,
            "Pa": 7, "P": 7,
            "Dha": 9, "D": 9, "dha": 8, "d": 8,
            "Ni": 11, "N": 11, "ni": 10, "n": 10,
        }
        all_notes = aroha + avaroha
        active = sorted(set(SWARA_MAP.get(n, -1) for n in all_notes) - {-1})
        vadi_idx = SWARA_MAP.get(vadi, -1)
        samvadi_idx = -1
        return {
            "notes": LABELS,
            "active": active,
            "vadi": vadi_idx,
            "samvadi": samvadi_idx,
            "active_color": "#3a8050",
            "vadi_color": "#5cb87a",
            "inactive_color": "#2a3548",
            "ring_color": "#2a3548",
        }

    if visual_type == "tala_cycle":
        bols = resolved.get("tala_bols") or s2.get("tala_bols", [])
        beats = len(bols) if bols else (resolved.get("tala_beats") or s2.get("tala_beats", 8))
        return {
            "beats": beats,
            "bols": bols,
            "sam_color": "#f0c040",
            "beat_color": "#4a6080",
            "ring_color": "#2a3548",
        }

    if visual_type == "devi_yantra":
        return {
            "color": "#4a2a6a",
            "gate_color": "#5a3a7a",
            "bindu_color": "#aa77dd",
        }

    if visual_type == "plant_form":
        return {
            "stem_color": "#3a7a48",
            "leaf_color": "#2a5030",
            "leaf_stroke": "#5cb87a",
        }

    if visual_type == "body_region":
        region = resolved.get("body_region") or s5.get("body_region", "")
        return {
            "outline_color": "#3a4a58",
            "active_region": region,
            "active_color": "#a09070",
        }

    if visual_type == "vara_arc":
        vara = resolved.get("vara") or panchanga.get("vara", "")
        # Map vara name to glyph key
        VARA_MAP = {
            "Ravivara": "Sun", "Somavara": "Mon", "Mangalavara": "Tue",
            "Budhavara": "Wed", "Guruvara": "Thu", "Shukravara": "Fri",
            "Shanivara": "Sat",
        }
        import re as _re
        vara_clean = _re.sub(r"[^a-zA-Z]", "", vara)
        glyph_key = VARA_MAP.get(vara_clean, "Sun")
        return {
            "glyph": glyph_key,
            "arc_color": "#4a3010",
            "night_color": "#2a1808",
            "dot_color": "#f0b060",
        }

    if visual_type == "moon_phase":
        return {
            "tidx": resolved.get("tidx") or panchanga.get("tidx", 0),
            "color": "#c8a840",
            "bg_color": "#4a4020",
        }

    if visual_type == "sri_yantra":
        try:
            from npu_engine.yantra_generator import yantra_data_for_field
            from npu_engine.graph_engine import GraphEngine
            from npu_engine.torus_queries import torus_context_for_entity
            _g = GraphEngine()
            nak = panchanga.get("nakshatra", "")
            # Strip IAST diacritics for torus lookup
            import unicodedata as _ud
            nak_ascii = _ud.normalize("NFKD", nak).encode("ascii","ignore").decode("ascii")
            ctx = torus_context_for_entity(nak, _g._metadata, _g) or \
                  torus_context_for_entity(nak_ascii, _g._metadata, _g) or {}
            fs_mini = {
                "panchanga": panchanga,
                "yantra": ctx.get("yantra", {}),
                "co_triangulars": ctx.get("co_triangulars", []),
                "psi": {"intensity": 0.5},
            }
            return yantra_data_for_field(fs_mini)
        except Exception:
            return {}

    return {}


def resolve_zone(direction: str, field_state: dict, graph=None,
                 active_layer: str = None) -> dict:
    """Resolve a single main-mandala zone. Returns canonical zone response."""
    p = field_state.get("panchanga", {})
    layers = field_state.get("layers", {})

    # Entities from graph
    nak_id = "nakshatra_" + _slug(p.get("nakshatra", ""))
    seeds = [nak_id]
    if p.get("nak_lord"):
        seeds.append("graha_" + _slug(p["nak_lord"]))
    entities = _top_entities_for(graph, seeds, limit=5) if graph else []

    # Build zone first with placeholder weight
    zone = _build_zone_response(
        direction=direction,
        layer_key="main",
        panchanga=p,
        layers=layers,
        weight=1.0,
        entities=entities,
    )

    # Compute proper weight from affinity + density
    layer_key = active_layer or "main"
    s4 = layers.get("S4", {})
    ld = layers.get(layer_key, s4) if isinstance(layers.get(layer_key), dict) else s4
    row_count = len(zone.get("rows", []))
    app_count = len(zone.get("apps", []))
    has_visual = bool(zone.get("visual", {}).get("type"))
    zone["weight"] = _compute_zone_weight(
        layer_key, direction, ld if isinstance(ld, dict) else {},
        {}, field_state,
        row_count=row_count, app_count=app_count, has_visual=has_visual)

    return zone


LAYER_BAR = [
    {"id": "S0", "name": "Bindu",     "color": "#a09070"},
    {"id": "S1", "name": "Archetype", "color": "#aa77dd"},
    {"id": "S2", "name": "Sound",     "color": "#5cb87a"},
    {"id": "S3", "name": "Rhythm",    "color": "#c8d8f0"},
    {"id": "S4", "name": "Geometry",  "color": "#8899bb"},
    {"id": "S5", "name": "Nature",    "color": "#5cb87a"},
    {"id": "S6", "name": "Lila",      "color": "#f0b060"},
]


def resolve_mandala(field_state: dict, graph=None,
                    active_layer: str = None) -> dict:
    """Resolve all 9 zones per SHELL_STATE_TEMPLATE.md.

    This is what GET /shell/state returns.
    """
    p = field_state.get("panchanga", {})
    layers = field_state.get("layers", {})
    layer_code = active_layer or "S0"

    zones = {}
    for direction in DIRECTIONS:
        zones[direction.lower()] = resolve_zone(direction, field_state, graph, active_layer)

    # Fill study depth passages for each zone's primary entity
    try:
        from npu_engine.passage_resolver import find_passages
        for zid, zone in zones.items():
            eid = (zone.get("study_depth") or {}).get("primary_entity")
            if eid:
                zone["study_depth"]["passages"] = find_passages(eid, limit=3)
    except Exception:
        pass

    # Grid weights from zones
    cw = [1.0, 1.5, 1.0]
    rw = [1.0, 1.5, 1.0]
    grid_map = [
        {"d": "nw", "c": 0, "r": 0}, {"d": "n", "c": 1, "r": 0}, {"d": "ne", "c": 2, "r": 0},
        {"d": "w",  "c": 0, "r": 1}, {"d": "c", "c": 1, "r": 1}, {"d": "e",  "c": 2, "r": 1},
        {"d": "sw", "c": 0, "r": 2}, {"d": "s", "c": 1, "r": 2}, {"d": "se", "c": 2, "r": 2},
    ]
    for gm in grid_map:
        w = zones.get(gm["d"], {}).get("weight", 1.0)
        if gm["d"] == "c":
            w = max(w, 1.5)
        cw[gm["c"]] = max(cw[gm["c"]], w)
        rw[gm["r"]] = max(rw[gm["r"]], w)

    # Layer bar with active flag
    bar = []
    for lb in LAYER_BAR:
        bar.append({**lb, "active": lb["id"] == layer_code})

    return {
        "layer": layer_code,
        "layer_name": next((lb["name"] for lb in LAYER_BAR if lb["id"] == layer_code), "Bindu"),
        "layer_color": next((lb["color"] for lb in LAYER_BAR if lb["id"] == layer_code), "#a09070"),
        "grid": {
            "cols": " ".join(str(w) + "fr" for w in cw),
            "rows": " ".join(str(w) + "fr" for w in rw),
        },
        "zones": zones,
        "layer_bar": bar,
        "field": {
            "nakshatra": p.get("nakshatra", ""),
            "tithi": p.get("tithi", ""),
            "vara": p.get("vara", ""),
            "paksha": p.get("paksha", ""),
            "element": p.get("element", ""),
            "devi": p.get("devi", ""),
        },
    }


def resolve_sub_mandala(parent_layer: str, field_state: dict,
                        graph=None, s5_data: dict = None) -> dict:
    """
    Resolve a sub-mandala for a specific S-layer.

    The parent layer becomes the CENTER — its 9 domain-specific
    zones fill the mandala, colored and weighted by the layer schema.

    Returns same shape as resolve_mandala() but with sub-zone content.
    """
    layer_def = SUB_MANDALA_DEFS.get(parent_layer)
    if not layer_def:
        return resolve_mandala(field_state, graph, parent_layer)

    p = field_state.get("panchanga", {})
    layers = field_state.get("layers", {})
    layer_data = layers.get(parent_layer, {})
    nak = p.get("nakshatra", "")
    nak_id = "nakshatra_" + _slug(nak)

    # S5-specific data enrichment
    s5 = s5_data or {}

    zones = {}
    for direction in DIRECTIONS:
        zone_def = layer_def["zones"].get(direction, {})

        entities = _resolve_sub_zone_entities(
            parent_layer, direction, zone_def.get("source", ""),
            p, layer_data, graph, s5
        )

        extra_data = _resolve_sub_zone_data(
            parent_layer, direction, zone_def.get("source", ""),
            p, layer_data, layers, s5, field_state
        )

        bg = layer_def["bg_palette"].get(direction, ZONE_BG.get(direction, "#0d1428"))

        zones[direction] = _build_zone_response(
            direction=direction,
            layer_key=parent_layer,
            panchanga=p,
            layers=layers,
            weight=1.0,  # placeholder, computed below
            extra_data=extra_data,
            entities=entities,
            has_sub_zone=_has_sub_zone(parent_layer, direction),
            bg_override=bg,
        )
        # Compute proper weight from affinity + density
        z = zones[direction]
        z["weight"] = _compute_zone_weight(
            parent_layer, direction, layer_data, s5, field_state,
            row_count=len(z.get("rows", [])),
            app_count=len(z.get("apps", [])),
            has_visual=bool((z.get("visual") or {}).get("type")))

    # Lowercase zone keys per template
    zones_lower = {}
    for direction in DIRECTIONS:
        zones_lower[direction.lower()] = zones[direction]

    # Grid weights
    cw = [1.0, 1.5, 1.0]
    rw = [1.0, 1.5, 1.0]
    gm = [
        {"d": "NW", "c": 0, "r": 0}, {"d": "N", "c": 1, "r": 0}, {"d": "NE", "c": 2, "r": 0},
        {"d": "W",  "c": 0, "r": 1}, {"d": "C", "c": 1, "r": 1}, {"d": "E",  "c": 2, "r": 1},
        {"d": "SW", "c": 0, "r": 2}, {"d": "S", "c": 1, "r": 2}, {"d": "SE", "c": 2, "r": 2},
    ]
    for g in gm:
        w = zones.get(g["d"], {}).get("weight", 1.0)
        if g["d"] == "C":
            w = max(w, 1.5)
        cw[g["c"]] = max(cw[g["c"]], w)
        rw[g["r"]] = max(rw[g["r"]], w)

    bar = []
    for lb in LAYER_BAR:
        bar.append({**lb, "active": lb["id"] == parent_layer})

    return {
        "layer": parent_layer,
        "layer_name": layer_def["name"],
        "layer_color": layer_def["color"],
        "grid": {
            "cols": " ".join(str(w) + "fr" for w in cw),
            "rows": " ".join(str(w) + "fr" for w in rw),
        },
        "zones": zones_lower,
        "layer_bar": bar,
        "field": {
            "nakshatra": nak,
            "tithi": p.get("tithi", ""),
            "vara": p.get("vara", ""),
            "paksha": p.get("paksha", ""),
            "element": layer_data.get("element", p.get("element", "")),
            "devi": p.get("devi", ""),
        },
    }


def resolve_sub_zone(parent_layer: str, parent_direction: str,
                     field_state: dict, graph=None,
                     s5_data: dict = None) -> Optional[dict]:
    """
    Resolve a third-level sub-zone mandala.

    Called when a zone within a sub-mandala is clicked and
    has_sub_zone=True.  Returns None if no definition exists.

    Navigation: main → S5 (sub-mandala) → SW (guild sub-zone)
    """
    key = f"{parent_layer}_{parent_direction}"
    sz_def = SUB_ZONE_DEFS.get(key)
    if not sz_def:
        return None

    p = field_state.get("panchanga", {})
    layers = field_state.get("layers", {})
    layer_data = layers.get(parent_layer, {})
    s5 = s5_data or {}

    # Get the parent zone's data for context
    parent_sub_def = SUB_MANDALA_DEFS.get(parent_layer, {})
    parent_zone_def = parent_sub_def.get("zones", {}).get(parent_direction, {})
    parent_source = parent_zone_def.get("source", "")

    # Derive the hero entity for this sub-zone
    hero = _resolve_sub_zone_hero(parent_layer, parent_direction, p, layer_data, s5)

    zones = {}
    for direction in DIRECTIONS:
        inner_def = sz_def["zones"].get(direction, {})
        vastu = MANDALA_SCHEMA.get(direction, MANDALA_SCHEMA["C"])
        inner_source = inner_def.get("source", "")

        data = _resolve_third_level_data(
            key, direction, inner_source, hero,
            p, layer_data, layers, s5, field_state, graph
        )

        entities = _resolve_third_level_entities(
            key, direction, inner_source, hero,
            p, layer_data, graph, s5
        )

        zones[direction] = {
            "direction": direction,
            "name": inner_def.get("name", direction),
            "affinity": inner_def.get("affinity", ""),
            "deity": vastu["deity"],
            "element": vastu["element"],
            "entities": entities,
            "data": data,
            "visual": {
                "color": sz_def.get("color", "#5cb87a"),
                "weight": 1.0,
                "bg": MANDALA_SCHEMA.get(direction, {}).get("element", "ether"),
            },
            "apps": [],
            "has_sub_zone": False,
        }

    # Use parent layer palette for bg, darken slightly for depth
    parent_palette = parent_sub_def.get("bg_palette", {})
    for d in DIRECTIONS:
        base_bg = parent_palette.get(d, _element_bg(zones[d]["element"]))
        zones[d]["visual"]["bg"] = base_bg

    return {
        "mode": "sub_zone",
        "parent_layer": parent_layer,
        "parent_direction": parent_direction,
        "name": sz_def["name"],
        "color": sz_def.get("color", "#5cb87a"),
        "hero": hero,
        "zones": zones,
        "field": {
            "nakshatra": p.get("nakshatra", ""),
            "tithi": p.get("tithi", ""),
            "vara": p.get("vara", ""),
            "paksha": p.get("paksha", ""),
            "element": layer_data.get("element", p.get("element", "")),
            "devi": p.get("devi", ""),
        },
        "layers": layers,
    }


def _resolve_sub_zone_hero(layer: str, direction: str,
                           p: dict, ld: dict, s5: dict) -> str:
    """Get the hero entity name for a sub-zone center."""
    key = f"{layer}_{direction}"

    if key == "S5_SW":
        return s5.get("canonical_plant", ld.get("nakshatra_plant", ""))
    if key == "S5_NE":
        return s5.get("canonical_plant", ld.get("nakshatra_plant", ""))
    if key == "S5_E":
        return s5.get("canonical_plant", ld.get("nakshatra_plant", ""))
    if key == "S1_NE":
        devi = p.get("devi", "")
        return str(devi[0]) if isinstance(devi, list) and devi else str(devi)
    if key == "S1_N":
        return ld.get("deity", "")
    if key == "S2_NE":
        return (ld.get("raga", "") or
                (p.get("layers", {}).get("S2", {}) or {}).get("raga", ""))
    if key == "S2_N":
        return (ld.get("tala", "") or
                (p.get("layers", {}).get("S2", {}) or {}).get("tala", ""))
    if key == "S4_NE":
        return ld.get("yantra_type", "Sri Yantra")
    if key == "S4_N":
        return "Vastu Mandala"

    return ""


def _resolve_third_level_data(key: str, direction: str, source: str,
                              hero: str, p: dict, ld: dict, layers: dict,
                              s5: dict, fs: dict, graph) -> dict:
    """Resolve data for a third-level zone."""

    # ── S5 Guild zones ──
    if key == "S5_SW":
        if source == "guild_center":
            return {"plant": hero, "role": "center/canopy",
                    "element": ld.get("element", ""),
                    "nakshatra": p.get("nakshatra", "")}
        if source == "guild_nfix":
            return {"role": "nitrogen fixer", "examples": "clover, vetch, beans",
                    "function": "fix atmospheric N into soil"}
        if source == "guild_timing":
            return {"day_type": s5.get("day_type", ""),
                    "moon": "waxing" if p.get("tidx", 0) < 15 else "waning",
                    "season": ld.get("season", "")}
        if source == "guild_sacred":
            return {"nakshatra": p.get("nakshatra", ""),
                    "deity": ld.get("deity", ""), "plant": hero}
        if source == "guild_mineral":
            return {"role": "dynamic accumulator",
                    "examples": "comfrey, yarrow, dandelion",
                    "function": "mine deep minerals to surface"}
        if source == "guild_pfaf":
            return {"search": hero, "database": "PFAF 8504 plants"}
        if source == "guild_ground":
            return {"role": "ground cover / living mulch",
                    "examples": "clover, strawberry, ajuga",
                    "function": "suppress weeds, retain moisture"}
        if source == "guild_med":
            return {"role": "medicinal",
                    "dosha": s5.get("dosha_today", ld.get("dosha", "")),
                    "herbs": s5.get("active_herbs", [])[:4]}
        if source == "guild_poll":
            return {"role": "pollinator attractor",
                    "examples": "borage, calendula, lavender",
                    "function": "attract bees, butterflies"}

    # ── S5 Sacred Plant zones ──
    if key == "S5_NE":
        if source == "sacred_center":
            return {"plant": hero, "nakshatra": p.get("nakshatra", ""),
                    "deity": ld.get("deity", ""), "authority": "shastra"}
        if source == "sacred_ayur":
            return {"dosha": s5.get("dosha_today", ""),
                    "body_region": ld.get("body_region", "")}
        if source == "sacred_cal":
            return {"day_type": s5.get("day_type", ""),
                    "harvest": s5.get("harvest_quality", "")}
        if source == "sacred_mantra":
            return {"mantra": ld.get("mantra", ""), "deity": ld.get("deity", "")}
        if source == "sacred_passage":
            return {"source": "shastra", "hint": "Vedic references to " + hero}
        if source == "sacred_body":
            return {"body_region": ld.get("body_region", ""),
                    "marma": ld.get("marma_point", "")}
        if source == "sacred_ritual":
            return {"use": "puja offering", "plant": hero}
        if source in ("sacred_taxon", "sacred_hist"):
            return {"plant": hero}

    # ── S5 PFAF zones ──
    if key == "S5_E":
        if source == "pfaf_center":
            return {"plant": hero, "database": "PFAF"}
        return {"plant": hero, "section": source.replace("pfaf_", "")}

    # ── S1 Devi Portrait zones ──
    if key == "S1_NE":
        if source == "devi_center":
            return {"devi": hero, "nakshatra": p.get("nakshatra", ""),
                    "tithi": p.get("tithi", "")}
        if source == "devi_graha":
            return {"graha": ld.get("graha", p.get("nak_lord", ""))}
        if source == "devi_vahana":
            return {"vahana": ld.get("vahana", "")}
        if source == "devi_yantra":
            return {"yantra": ld.get("yantra_type", "")}
        if source == "devi_mantra":
            return {"mantra": ld.get("mantra", ""), "bija": ld.get("bija", "")}
        if source == "devi_passage":
            return {"source": "Bhagavatam", "hint": "passages mentioning " + hero}
        if source == "devi_weapon":
            return {"weapon": ld.get("weapon", "")}
        if source == "devi_shakti":
            return {"shakti": ld.get("shakti", "")}
        if source == "devi_ritual":
            return {"worship": "puja for " + hero}

    # ── S1 Deity Portrait zones ──
    if key == "S1_N":
        if source == "deity_center":
            return {"deity": hero, "nakshatra": p.get("nakshatra", "")}
        if source == "deity_graha":
            return {"graha": p.get("nak_lord", "")}
        if source == "deity_mantra":
            return {"mantra": ld.get("mantra", "")}
        if source == "deity_passage":
            return {"source": "Purana", "hint": "passages about " + hero}
        if source == "deity_nak":
            return {"nakshatra": p.get("nakshatra", "")}
        return {"deity": hero}

    # ── S2 Raga Study zones ──
    if key == "S2_NE":
        s2 = layers.get("S2", {})
        if source == "raga_center":
            return {"raga": hero, "thaat": s2.get("raga_thaat", ""),
                    "vadi": s2.get("raga_vadi", ""),
                    "samvadi": s2.get("raga_samvadi", "")}
        if source == "raga_aroha":
            return {"aroha": s2.get("raga_aroha", [])}
        if source == "raga_avaroha":
            return {"avaroha": s2.get("raga_avaroha", [])}
        if source == "raga_rasa":
            return {"rasa": s2.get("raga_rasa", ""),
                    "time": s2.get("raga_time", ""),
                    "season": s2.get("raga_season", "")}
        if source == "raga_therapy":
            return {"dosha": s2.get("raga_dosha", ""),
                    "chakra": s2.get("raga_chakra", "")}
        if source == "raga_shruti":
            return {"sa_freq": s2.get("element_frequency", ""),
                    "tuning": s2.get("tuning", "")}
        return {"raga": hero}

    # ── S2 Tala Study zones ──
    if key == "S2_N":
        s2 = layers.get("S2", {})
        if source == "tala_center":
            return {"tala": hero, "beats": s2.get("tala_beats", 8),
                    "jati": s2.get("tala_jati", "")}
        if source == "tala_bols":
            return {"bols": s2.get("tala_bols", [])}
        if source == "tala_laya":
            return {"gati": s2.get("gati", ""), "bpm": s2.get("bpm", 72)}
        return {"tala": hero}

    # ── S4 Yantra Study zones ──
    if key == "S4_NE":
        if source == "yantra_center":
            return {"yantra": hero}
        if source == "yantra_deity":
            return {"deity": ld.get("deity", "")}
        if source == "yantra_bija":
            return {"bija": ld.get("bija", "")}
        return {"yantra": hero}

    # ── S4 Vastu Grid zones ──
    if key == "S4_N":
        vastu_dir = source.replace("vastu_", "").upper()
        vastu_info = MANDALA_SCHEMA.get(vastu_dir, MANDALA_SCHEMA.get(direction, {}))
        return {
            "zone": vastu_dir or direction,
            "deity": vastu_info.get("deity", ""),
            "element": vastu_info.get("element", ""),
            "quality": vastu_info.get("quality", ""),
        }

    return {}


def _resolve_third_level_entities(key: str, direction: str, source: str,
                                  hero: str, p: dict, ld: dict,
                                  graph, s5: dict) -> list:
    """Resolve entities for a third-level zone via graph."""
    if not graph or not hero:
        return []

    # For guild zones, expand from the center plant
    if key.startswith("S5_"):
        plant_id = "plant_" + _slug(hero)
        if source and "center" in source:
            return _graph_neighbors(graph, plant_id, limit=3)
        if source and ("nfix" in source or "ground" in source or
                       "mineral" in source or "poll" in source or
                       "med" in source):
            return _top_entities_for(graph, [plant_id],
                                     category_filter="plant", limit=4)

    # For devi/deity, expand from entity
    if key == "S1_NE":
        devi_id = "devi_" + _slug(hero)
        if source and "center" in source:
            return _graph_neighbors(graph, devi_id, limit=4)
        if source and ("graha" in source or "weapon" in source):
            return _graph_neighbors(graph, devi_id, limit=3)

    if key == "S1_N":
        deity_id = "deity_" + _slug(hero)
        if source and "center" in source:
            return _graph_neighbors(graph, deity_id, limit=4)

    # For raga, expand from raga entity
    if key == "S2_NE":
        raga_id = "raga_" + _slug(hero)
        if source and "center" in source:
            return _graph_neighbors(graph, raga_id, limit=4)

    return []


# ── Sub-zone data resolvers ─────────────────────────────────

def _resolve_sub_zone_entities(layer: str, direction: str, source: str,
                               p: dict, ld: dict, graph, s5: dict) -> list:
    """Return entity list for a sub-zone."""
    if not graph:
        return []

    nak_id = "nakshatra_" + _slug(p.get("nakshatra", ""))

    if layer == "S5":
        if source == "s5_herbs":
            herbs = s5.get("active_herbs", [])
            return [{"id": "plant_" + _slug(h), "name": h} for h in herbs[:6]]
        if source == "s5_sacred":
            return _graph_neighbors(graph, nak_id, "nakshatra_plant", limit=3)
        if source == "s5_guild":
            plant = s5.get("canonical_plant", ld.get("nakshatra_plant", ""))
            if plant:
                return _top_entities_for(graph, ["plant_" + _slug(plant)], limit=5)
        if source == "s5_body":
            region = ld.get("body_region", "")
            if region:
                return _graph_neighbors(graph, "body_region_" + _slug(region), limit=4)

    if layer == "S1":
        if source == "s1_graha":
            lord = p.get("nak_lord", "")
            if lord:
                return _graph_neighbors(graph, "graha_" + _slug(lord), limit=4)
        if source == "s1_devi":
            devi = p.get("devi", "")
            if isinstance(devi, list) and devi:
                devi = devi[0]
            if devi:
                return _graph_neighbors(graph, "devi_" + _slug(str(devi)), limit=4)

    return []


def _resolve_sub_zone_data(layer: str, direction: str, source: str,
                           p: dict, ld: dict, layers: dict,
                           s5: dict, fs: dict) -> dict:
    """Return structured data rows for a sub-zone."""

    if layer == "S5":
        return _resolve_s5_data(direction, source, p, ld, layers, s5, fs)
    if layer == "S1":
        return _resolve_s1_data(direction, source, p, ld, layers, fs)
    if layer == "S2":
        return _resolve_s2_data(direction, source, p, ld, layers, fs)
    if layer == "S3":
        return _resolve_s3_data(direction, source, p, ld, layers, fs)

    # Default: return layer data as-is
    return dict(ld)


def _resolve_s5_data(direction, source, p, ld, layers, s5, fs):
    """S5 ecology sub-zone data."""
    if source == "s5_center":
        return {
            "canonical_plant": s5.get("canonical_plant", ld.get("nakshatra_plant", "")),
            "body_region": ld.get("body_region", ""),
            "dosha": s5.get("dosha_today", ld.get("dosha", "")),
            "element": ld.get("element", ""),
            "guna": ld.get("guna", ""),
            "day_type": s5.get("day_type", ""),
            "nakshatra": p.get("nakshatra", ""),
        }
    if source == "s5_herbs":
        return {
            "herbs": s5.get("active_herbs", [])[:8],
            "dosha": s5.get("dosha_today", ""),
            "search_hint": "Search by name, dosha, or use",
        }
    if source == "agriculture":
        return {
            "day_type": s5.get("day_type", ""),
            "harvest_quality": s5.get("harvest_quality", ""),
            "nakshatra": p.get("nakshatra", ""),
            "element": ld.get("element", ""),
            "moon_phase": "waxing" if (p.get("tidx", 0)) < 15 else "waning",
        }
    if source == "s5_sacred":
        return {
            "plant": s5.get("canonical_plant", ld.get("nakshatra_plant", "")),
            "deity": ld.get("deity", ""),
            "mantra": ld.get("mantra", ""),
            "nakshatra": p.get("nakshatra", ""),
            "ritual_use": "",
        }
    if source == "s5_wheel":
        # Ring counts for the wheel
        return {
            "ring1_count": len(s5.get("ring1", [])),
            "ring2_count": len(s5.get("ring2", [])),
            "ring3_count": len(s5.get("ring3", [])),
            "active_nak_idx": s5.get("active_nak_idx", 0),
        }
    if source == "s5_search":
        return {"search_hint": "PFAF database — full plant profiles"}
    if source == "s5_guild":
        plant = s5.get("canonical_plant", ld.get("nakshatra_plant", ""))
        return {"canonical_plant": plant, "hint": "Generate companion planting guild"}
    if source == "s5_body":
        return {
            "body_region": ld.get("body_region", ""),
            "marma": ld.get("marma_point", ""),
            "dosha": ld.get("dosha", ""),
            "herbs": s5.get("active_herbs", [])[:3],
        }
    if source == "s5_practice":
        s6 = layers.get("S6", {})
        return {
            "practice": s6.get("practice", ""),
            "dinacharya": _dinacharya_for_element(ld.get("element", "")),
            "time": p.get("vara", ""),
        }
    return {}


def _resolve_s1_data(direction, source, p, ld, layers, fs):
    """S1 archetype sub-zone data."""
    if source == "s1_center":
        devi = p.get("devi", "")
        if isinstance(devi, list) and devi:
            devi = devi[0]
        return {
            "devi": str(devi),
            "deity": ld.get("deity", ""),
            "nakshatra": p.get("nakshatra", ""),
            "tithi": p.get("tithi", ""),
            "element": ld.get("element", p.get("element", "")),
        }
    if source == "s1_graha":
        return {"graha": p.get("nak_lord", ""), "hora": ld.get("hora", "")}
    if source == "s1_deity":
        return {"deity": ld.get("deity", ""), "aspect": ld.get("aspect", "")}
    if source == "s1_devi":
        devi = p.get("devi", "")
        if isinstance(devi, list) and devi:
            devi = devi[0]
        return {"devi": str(devi), "shakti": ld.get("shakti", ""), "bija": ""}
    if source == "s1_mantra":
        return {"mantra": ld.get("mantra", ""), "bija": ""}
    if source == "s1_yantra":
        return {"yantra": ld.get("yantra_type", ""), "geometry": ""}
    if source == "s1_vahana":
        return {"vahana": ld.get("vahana", "")}
    if source == "s1_shakti":
        return {"shakti": ld.get("shakti", ""), "direction": ""}
    if source == "s1_bija":
        return {"bija": "", "element": ld.get("element", "")}
    return {}


def _resolve_s2_data(direction, source, p, ld, layers, fs):
    """S2 sound sub-zone data."""
    ss = fs.get("sound_state", {})
    s2 = layers.get("S2", {})
    if source == "s2_center":
        return {"raga": s2.get("raga", ""), "tala": s2.get("tala", ""),
                "vadi": s2.get("raga_vadi", ""), "bpm": s2.get("bpm", 72)}
    if source == "s2_raga":
        return {"raga": s2.get("raga", ""), "thaat": s2.get("raga_thaat", ""),
                "aroha": s2.get("raga_aroha", []), "avaroha": s2.get("raga_avaroha", []),
                "vadi": s2.get("raga_vadi", ""), "samvadi": s2.get("raga_samvadi", "")}
    if source == "s2_tala":
        return {"tala": s2.get("tala", ""), "beats": s2.get("tala_beats", 8),
                "bols": s2.get("tala_bols", []), "gati": s2.get("gati", "")}
    return dict(s2) if s2 else {}


def _resolve_s3_data(direction, source, p, ld, layers, fs):
    """S3 panchanga sub-zone data."""
    s3 = layers.get("S3", {})
    if source == "s3_center":
        return {"nakshatra": p.get("nakshatra", ""), "tithi": p.get("tithi", ""),
                "vara": p.get("vara", ""), "yoga": p.get("yoga", ""),
                "karana": p.get("karana", "")}
    if source == "s3_nakshatra":
        return {"nakshatra": p.get("nakshatra", ""), "lord": p.get("nak_lord", ""),
                "pada": s3.get("pada", ""), "element": ld.get("element", "")}
    if source == "s3_tithi":
        return {"tithi": p.get("tithi", ""), "paksha": p.get("paksha", ""),
                "tidx": p.get("tidx", 0)}
    return dict(s3) if s3 else {}


# ── Zone weight computation ──────────────────────────────────

# ── Layer affinity tables ────────────────────────────────────
# How central is each direction to each layer's domain?
# 1.0 = primary domain, 0.4 = distant

LAYER_AFFINITY = {
    "S0": {  # Bindu — uniform, all equally present at source
        "NW": 0.6, "N": 0.6, "NE": 0.6, "W": 0.6, "C": 1.0,
        "E": 0.6, "SW": 0.6, "S": 0.6, "SE": 0.6,
    },
    "S1": {  # Archetype — NE (Ishana/sacred knowledge) is primary
        "NW": 0.6, "N": 0.7, "NE": 1.0, "W": 0.4, "C": 1.0,
        "E": 0.5, "SW": 0.4, "S": 0.4, "SE": 0.4,
    },
    "S2": {  # Sound — NW (Vayu/sound) is primary
        "NW": 1.0, "N": 0.8, "NE": 0.6, "W": 0.5, "C": 1.0,
        "E": 0.5, "SW": 0.4, "S": 0.4, "SE": 0.5,
    },
    "S3": {  # Rhythm — N (Kubera/time) is primary
        "NW": 0.6, "N": 1.0, "NE": 0.7, "W": 0.5, "C": 1.0,
        "E": 0.5, "SW": 0.4, "S": 0.5, "SE": 0.6,
    },
    "S4": {  # Geometry — all directions equally structural
        "NW": 0.7, "N": 0.7, "NE": 0.8, "W": 0.7, "C": 1.0,
        "E": 0.6, "SW": 0.6, "S": 0.7, "SE": 0.7,
    },
    "S5": {  # Nature — W (Varuna/ecology) and SW (Nirriti/earth) are primary
        "NW": 0.7, "N": 0.6, "NE": 0.5, "W": 1.0, "C": 1.0,
        "E": 0.5, "SW": 0.9, "S": 0.7, "SE": 0.5,
    },
    "S6": {  # Lila — E (Indra/perception) is primary
        "NW": 0.5, "N": 0.5, "NE": 0.6, "W": 0.5, "C": 1.0,
        "E": 1.0, "SW": 0.4, "S": 0.5, "SE": 0.6,
    },
    "main": {  # Main mandala — all zones balanced, center strong
        "NW": 0.7, "N": 0.7, "NE": 0.7, "W": 0.7, "C": 1.0,
        "E": 0.7, "SW": 0.7, "S": 0.7, "SE": 0.7,
    },
}


def _compute_zone_weight(layer: str, direction: str, ld: dict,
                         s5: dict, fs: dict,
                         row_count: int = 0, app_count: int = 0,
                         has_visual: bool = False) -> float:
    """Compute zone weight from layer affinity + data density.

    Weight formula:
      affinity: how central is this direction to the active layer (0.4-1.0)
      density:  how much data this zone has (0.0-1.0)
      weight = (affinity * 0.7) + (density * 0.3)
      scaled to CSS fr range: 0.4 to 2.0

    Center special: derives from field coherence (psi intensity).
    """
    if direction == "C":
        # Center weight from field coherence
        psi = (fs.get("psi") or {}).get("intensity", 0.5) if isinstance(fs.get("psi"), dict) else 0.5
        return round(1.2 + (psi * 1.2), 2)  # range 1.2 to 2.4

    # Layer affinity
    affinities = LAYER_AFFINITY.get(layer, LAYER_AFFINITY["main"])
    affinity = affinities.get(direction, 0.6)

    # Data density
    count = row_count + app_count + (1 if has_visual else 0)
    density = min(count / 8.0, 1.0)

    # S5 bio-cycle boost (preserved from original)
    bio_boost = 0.0
    if layer == "S5":
        day_type = s5.get("day_type", "")
        DAY_TYPE_BOOST = {
            "fruit": {"NE": 0.3, "E": 0.2},
            "root": {"SW": 0.3, "S": 0.2},
            "flower": {"NW": 0.2, "N": 0.15},
            "leaf": {"W": 0.2, "NW": 0.15},
        }
        bio_boost = DAY_TYPE_BOOST.get(day_type, {}).get(direction, 0.0)

    # S4 vastu engine override
    if layer == "S4":
        vastu_w = ld.get("zone_weights", {}).get(direction)
        if vastu_w is not None:
            return round(max(0.4, min(2.0, vastu_w)), 2)

    # Combine
    raw = (affinity * 0.7) + (density * 0.3) + bio_boost
    weight = max(0.4, min(2.0, raw * 2.0))
    return round(weight, 2)


# ── Helpers ──────────────────────────────────────────────────

def _slug(s: str) -> str:
    if not s:
        return ""
    import re
    import unicodedata
    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", "ignore").decode("ascii").lower()
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return s


def _element_color(element: str) -> str:
    return {
        "fire": "#d4943a", "water": "#4878c8", "earth": "#5cb87a",
        "air": "#7bb8c8", "ether": "#d4a84b",
    }.get(element, "#d4a84b")


def _element_bg(element: str) -> str:
    return {
        "fire": "#280d0d", "water": "#0d1828", "earth": "#0d2818",
        "air": "#0d2020", "ether": "#0d1428",
    }.get(element, "#0d1428")


def _dinacharya_for_element(element: str) -> str:
    return {
        "fire": "abhyanga with cooling oil, moderate exercise",
        "water": "warm oil massage, vigorous movement",
        "earth": "dry brushing, stimulating breath",
        "air": "grounding oil massage, slow walking",
        "ether": "meditation, minimal intake",
    }.get(element, "gentle routine appropriate to constitution")
