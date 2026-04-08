"""SW · Nirriti · S5 — Guild engine. Plant guilds from field state.

A guild is a group of plants that support each other:
  anchor (nakshatra plant) + companions from guild_relations.csv.

Data sources:
    datasets/plants/nakshatra_plants.csv    — nakshatra → anchor plant
    datasets/plants/guild_relations.csv     — anchor → companions + conflicts
    datasets/plants/guild_principles.csv    — permaculture/vedic principles
"""
import csv
import io
import os
import logging
from .base_engine import ZoneEngine

log = logging.getLogger(__name__)

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
_PLANTS_CSV = os.path.join(_ROOT, "datasets", "plants", "nakshatra_plants.csv")
_GUILD_REL_CSV = os.path.join(_ROOT, "datasets", "plants", "guild_relations.csv")
_GUILD_PRINC_CSV = os.path.join(_ROOT, "datasets", "plants", "guild_principles.csv")
_PFAF_STRUCT_CSV = os.path.join(_ROOT, "datasets", "plants", "pfaf_structured.csv")
_GUILD_MATRIX_CSV = os.path.join(_ROOT, "datasets", "plants", "guild_matrix.csv")

_plants_cache = None
_guild_by_anchor = None
_principles_cache = None
_pfaf_cache = None
_matrix_cache = None

# Guild function priority order (soil foundation first)
_FUNCTION_PRIORITY = {
    "nitrogen_fixer": 0,
    "dynamic_accumulator": 1,
    "pest_repellent": 2,
    "pollinator_attractor": 3,
    "ground_cover": 4,
    "climber": 5,
    "root_crop": 6,
}


def _load_plants():
    global _plants_cache
    if _plants_cache is not None:
        return _plants_cache
    _plants_cache = []
    try:
        with open(_PLANTS_CSV, newline="", encoding="utf-8") as f:
            _plants_cache = list(csv.DictReader(f))
        log.info("loaded %d plants from nakshatra_plants.csv", len(_plants_cache))
    except Exception:
        pass
    return _plants_cache


def _load_guild_relations():
    global _guild_by_anchor
    if _guild_by_anchor is not None:
        return _guild_by_anchor
    _guild_by_anchor = {}
    try:
        with open(_GUILD_REL_CSV, encoding="utf-8") as f:
            text = f.read().lstrip()
        rows = list(csv.DictReader(io.StringIO(text)))
        for row in rows:
            anchor = row.get("anchor_plant", "").strip()
            if anchor:
                _guild_by_anchor.setdefault(anchor, []).append(row)
        log.info("loaded %d guild relations for %d anchors",
                 len(rows), len(_guild_by_anchor))
    except Exception as e:
        log.warning("guild_relations.csv load failed: %s", e)
    return _guild_by_anchor


def _load_principles():
    global _principles_cache
    if _principles_cache is not None:
        return _principles_cache
    _principles_cache = []
    try:
        with open(_GUILD_PRINC_CSV, newline="", encoding="utf-8") as f:
            _principles_cache = list(csv.DictReader(f))
        log.info("loaded %d guild principles", len(_principles_cache))
    except Exception:
        pass
    return _principles_cache


def _load_pfaf_structured():
    """Load PFAF structured data if available. Graceful skip if missing."""
    global _pfaf_cache
    if _pfaf_cache is not None:
        return _pfaf_cache
    _pfaf_cache = {}
    try:
        if not os.path.exists(_PFAF_STRUCT_CSV):
            return _pfaf_cache
        with open(_PFAF_STRUCT_CSV, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                latin = row.get("latin_name", "").strip()
                common = row.get("common_name", "").strip().lower()
                if latin:
                    _pfaf_cache[latin.lower()] = row
                if common:
                    _pfaf_cache[common] = row
        log.info("loaded %d PFAF structured entries", len(_pfaf_cache) // 2)
    except Exception as e:
        log.warning("pfaf_structured.csv load failed: %s", e)
    return _pfaf_cache


def _pfaf_lookup(plant_name):
    """Look up a plant in PFAF structured data by common or latin name."""
    pfaf = _load_pfaf_structured()
    if not pfaf or not plant_name:
        return None
    key = plant_name.strip().lower()
    if key in pfaf:
        return pfaf[key]
    # Fuzzy: try first word match
    first = key.split()[0] if key else ""
    for k, v in pfaf.items():
        if first and first in k:
            return v
    return None


def _load_guild_matrix():
    """Load guild_matrix.csv with companion/conflict indexes."""
    global _matrix_cache
    if _matrix_cache is not None:
        return _matrix_cache
    _matrix_cache = {
        "plants": {},           # latin_name_lower → row
        "companion_index": {},  # plant_name_lower → [rows that list it as companion]
        "conflict_index": {},   # plant_name_lower → [rows that conflict with it]
        "by_layer": {},         # layer → [rows]
        "n_fixers": [],         # rows where nitrogen_fixer == yes
    }
    try:
        if not os.path.exists(_GUILD_MATRIX_CSV):
            return _matrix_cache
        with open(_GUILD_MATRIX_CSV, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                latin = (row.get("latin_name") or "").strip().lower()
                common = (row.get("common_name") or "").strip().lower()
                if latin:
                    _matrix_cache["plants"][latin] = row
                if common:
                    _matrix_cache["plants"][common] = row
                # Layer index
                layer = row.get("layer", "")
                _matrix_cache["by_layer"].setdefault(layer, []).append(row)
                # N-fixer index
                if row.get("nitrogen_fixer") == "yes":
                    _matrix_cache["n_fixers"].append(row)
                # Companion index
                for comp in (row.get("good_companions") or "").split(";"):
                    comp = comp.strip().lower()
                    if comp:
                        _matrix_cache["companion_index"].setdefault(comp, []).append(row)
                # Conflict index
                for conf in (row.get("conflict_plants") or "").split(";"):
                    conf = conf.strip().lower()
                    if conf:
                        _matrix_cache["conflict_index"].setdefault(conf, []).append(row)
        plant_count = len(set(r.get("plant_id") for r in _matrix_cache["plants"].values()))
        log.info("loaded %d guild_matrix entries, %d N-fixers",
                 plant_count, len(_matrix_cache["n_fixers"]))
    except Exception as e:
        log.warning("guild_matrix.csv load failed: %s", e)
    return _matrix_cache


def _matrix_lookup(plant_name):
    """Look up plant in guild matrix by common or latin name."""
    m = _load_guild_matrix()
    if not m["plants"] or not plant_name:
        return None
    return m["plants"].get(plant_name.strip().lower())


def _norm(s):
    """Normalize nakshatra name for matching."""
    s = s.lower().replace(" ", "").replace("_", "")
    for a, b in [("ā","a"),("ī","i"),("ū","u"),("ṛ","r"),("ṣ","sh"),
                 ("ś","sh"),("ṇ","n"),("ṭ","t"),("ḍ","d")]:
        s = s.replace(a, b)
    return s


def _find_nakshatra_plant(nak_name):
    """Find plant row for a nakshatra name."""
    plants = _load_plants()
    nak_n = _norm(nak_name)
    for p in plants:
        p_nak = _norm(p.get("nakshatra", ""))
        if p_nak and (p_nak in nak_n or nak_n in p_nak):
            return p
    return {}


def _moon_phase(tidx):
    """Moon phase and recommended activity from tithi index."""
    if tidx <= 7:
        return "waxing_crescent", "observe · root work"
    elif tidx <= 14:
        return "waxing_gibbous", "plant · leaf harvest"
    elif tidx == 15:
        return "full_moon", "fruit harvest · peak"
    elif tidx <= 22:
        return "waning_gibbous", "flower harvest · preserve"
    else:
        return "waning_crescent", "prune · compost · root crops"


def derive_guild_timing(field_state, days=14):
    """Moon phase activity for next N days."""
    p5 = field_state.get("panchanga", {})
    tidx = int(p5.get("tidx", 0))
    schedule = []
    for d in range(days):
        t = (tidx + d) % 30
        phase, activity = _moon_phase(t)
        schedule.append({
            "day": d, "tidx": t,
            "moon_phase": phase,
            "recommended_activity": activity,
        })
    return schedule


def derive_guild(field_state):
    """Given current field, return the active plant guild.

    Uses guild_relations.csv for companion/conflict data.
    Companions sorted by guild_function priority.
    """
    p5 = field_state.get("panchanga", {})
    nak = p5.get("nakshatra", "Rohini")
    element = p5.get("element", "earth").lower()
    guna = p5.get("guna", "sattva").lower()
    tidx = int(p5.get("tidx", 0))
    phase, activity = _moon_phase(tidx)

    anchor_row = _find_nakshatra_plant(nak)
    if not anchor_row:
        return {
            "anchor": "", "anchor_entity_id": "", "anchor_sanskrit": "",
            "nakshatra": nak, "companions": [], "conflict": {},
            "guild_function": "", "vastu_zone": "SW",
            "element": element, "moon_phase": phase,
            "recommended_activity": activity,
            "timing": {}, "guild_principles": [],
            "vastu_placement": {},
            "attestation": "SYNTHESIS",
        }

    anchor_name = anchor_row.get("plant", "")
    anchor_eid = "plant_" + anchor_name.lower().replace(" ", "_")

    # Look up guild relations — try exact match, then fuzzy
    guild_data = _load_guild_relations()
    relations = guild_data.get(anchor_name, [])
    if not relations:
        # Fuzzy match: try substring matching against guild anchors
        anchor_lower = anchor_name.lower()
        for guild_anchor in guild_data:
            ga_lower = guild_anchor.lower()
            if (anchor_lower in ga_lower or ga_lower in anchor_lower or
                    anchor_lower.split()[0] in ga_lower):
                relations = guild_data[guild_anchor]
                break

    # Split companions and conflicts
    companions = []
    conflict = {}
    for rel in relations:
        rtype = rel.get("relationship_type", "")
        if rtype == "companion":
            companions.append({
                "plant": rel.get("companion_plant", ""),
                "guild_function": rel.get("guild_function", ""),
                "vastu_zone": rel.get("vastu_zone", ""),
                "element": rel.get("element", ""),
                "graha": rel.get("graha_companion", ""),
                "ayurvedic_synergy": rel.get("ayurvedic_synergy", ""),
                "planting_nakshatra": rel.get("planting_nakshatra", ""),
                "planting_phase": rel.get("planting_phase", ""),
                "planting_vara": rel.get("planting_vara", ""),
            })
        elif rtype == "conflict":
            # Notes field may have URL noise — use clean reason
            plant = rel.get("companion_plant", "")
            reason = "allelopathic — inhibits growth of neighbors"
            if "walnut" in plant.lower():
                reason = "juglone allelopathy — toxic to most companions"
            conflict = {"plant": plant, "reason": reason}

    # Sort companions by guild_function priority
    companions.sort(key=lambda c: _FUNCTION_PRIORITY.get(
        c.get("guild_function", ""), 99))

    # Enrich companions with PFAF structured data
    for c in companions:
        pfaf = _pfaf_lookup(c.get("plant", ""))
        if pfaf:
            c["pfaf_layer"] = pfaf.get("layer", "")
            c["pfaf_guild_fn"] = pfaf.get("guild_function_primary", "")
            c["pfaf_nitrogen"] = pfaf.get("nitrogen_fixer", "") == "yes"
            c["pfaf_water"] = pfaf.get("water_relationship", "")
            c["pfaf_succession"] = pfaf.get("succession_role", "")
            c["pfaf_allelopathic"] = pfaf.get("allelopathic", "") == "yes"

    # Ensure at least one nitrogen fixer in companions
    has_nfixer = any(
        c.get("guild_function") == "nitrogen_fixer" or c.get("pfaf_nitrogen")
        for c in companions
    )
    if not has_nfixer and companions:
        # Check PFAF for N-fixers that match the anchor's element
        pfaf_data = _load_pfaf_structured()
        for key, p in pfaf_data.items():
            if (p.get("nitrogen_fixer") == "yes" and
                    p.get("layer") in ("shrub", "groundcover") and
                    not any(c.get("plant", "").lower() == key for c in companions)):
                companions.append({
                    "plant": p.get("common_name") or p.get("latin_name", ""),
                    "guild_function": "nitrogen_fixer",
                    "vastu_zone": "SW",
                    "element": p.get("element") or element,
                    "pfaf_nitrogen": True,
                    "pfaf_layer": p.get("layer", ""),
                    "source": "PFAF",
                })
                break

    # Warn about allelopathic conflicts
    allelopathic_warnings = []
    for c in companions:
        if c.get("pfaf_allelopathic"):
            allelopathic_warnings.append(
                f"{c.get('plant', '?')} is allelopathic — may inhibit neighbors"
            )

    # Timing from first companion's planting data or anchor
    timing = {}
    if companions:
        first = companions[0]
        timing = {
            "planting_nakshatra": first.get("planting_nakshatra", nak),
            "planting_phase": first.get("planting_phase", "waxing"),
            "planting_vara": first.get("planting_vara", ""),
            "moon_activity": activity,
        }
    else:
        timing = {
            "planting_nakshatra": nak,
            "planting_phase": "waxing" if tidx < 15 else "waning",
            "planting_vara": "",
            "moon_activity": activity,
        }

    # Vastu placement: map guild_function → vastu zone from data
    vastu_placement = {}
    for c in companions:
        vz = c.get("vastu_zone", "")
        if vz and vz not in vastu_placement:
            vastu_placement[vz] = c["plant"]

    # Guild principles
    principles = []
    for p in _load_principles():
        principles.append({
            "principle": p.get("permaculture_principle", ""),
            "vedic": p.get("vedic_equivalent", ""),
            "zone": p.get("vastu_zone", ""),
            "element": p.get("element", ""),
        })

    timing_quality = "favorable" if guna == "sattva" else "active" if guna == "rajas" else "quiet"

    # Layer coverage from companions
    layers_present = set()
    for c in companions:
        pl = c.get("pfaf_layer") or ""
        if pl:
            layers_present.add(pl)
    # Check anchor layer
    anchor_matrix = _matrix_lookup(anchor_name)
    if anchor_matrix:
        layers_present.add(anchor_matrix.get("layer", ""))

    # Nitrogen fixers in guild
    n_fixers = [
        c.get("plant", "") for c in companions
        if c.get("guild_function") == "nitrogen_fixer" or c.get("pfaf_nitrogen")
    ]

    # Fodder plants from matrix
    fodder_plants = []
    matrix = _load_guild_matrix()
    for c in companions:
        mr = _matrix_lookup(c.get("plant", ""))
        if mr and any(mr.get(f"fodder_{a}") == "yes" for a in ("cattle", "sheep", "goat", "pig", "chicken", "duck")):
            animals = [a for a in ("cattle", "sheep", "goat", "pig", "chicken", "duck") if mr.get(f"fodder_{a}") == "yes"]
            fodder_plants.append({"plant": c.get("plant", ""), "animals": animals})

    return {
        "anchor": anchor_name,
        "anchor_sanskrit": anchor_row.get("sanskrit_name", ""),
        "anchor_entity_id": anchor_eid,
        "nakshatra": nak,
        "companions": companions,
        "conflict": conflict,
        "guild_function": anchor_row.get("use", ""),
        "vastu_zone": "SW",
        "element": anchor_row.get("element", element).lower(),
        "timing_quality": timing_quality,
        "moon_phase": phase,
        "recommended_activity": activity,
        "timing": timing,
        "guild_principles": principles,
        "vastu_placement": vastu_placement,
        "allelopathic_warnings": allelopathic_warnings,
        "nitrogen_fixers": n_fixers,
        "fodder_plants": fodder_plants,
        "layer_coverage": sorted(layers_present),
        "guild_matrix_loaded": len(matrix.get("plants", {})) > 0,
        "attestation": "SYNTHESIS",
    }


class GuildEngine(ZoneEngine):
    vastu_position = "SW"
    layer = "S5"
    domain = "Guild"
    deity = "Nirriti"
    color = "#5cb87a"

    def get_entity(self, fs):
        guild = derive_guild(fs)
        return guild.get("anchor_entity_id", "")

    def render_icon(self, fs):
        guild = derive_guild(fs)
        return {"symbol": "🌿", "color": self.color,
                "entity_id": guild.get("anchor_entity_id", ""),
                "vastu": self.vastu_position,
                "value": guild.get("anchor", "")}

    def render_zone(self, fs):
        guild = derive_guild(fs)
        rows = [
            {"label": "anchor", "value": guild.get("anchor", ""),
             "entity_id": guild.get("anchor_entity_id", ""),
             "clickable": True, "symbol": "❧",
             "value_color": self.color},
            {"label": "moon", "value": guild.get("moon_phase", "").replace("_", " ")},
            {"label": "activity", "value": guild.get("recommended_activity", "")},
        ]
        # Top 3 companions with guild function
        for c in guild.get("companions", [])[:3]:
            fn = c.get("guild_function", "").replace("_", " ")
            rows.append({
                "label": fn or "companion",
                "value": c.get("plant", ""),
                "entity_id": "plant_" + c.get("plant", "").lower().replace(" ", "_"),
                "clickable": True, "label_color": "#3a5040",
            })
        # Conflict with warning
        conflict = guild.get("conflict", {})
        if conflict.get("plant"):
            rows.append({
                "label": "✗ conflict",
                "value": conflict["plant"],
                "label_color": "#8a3030",
                "value_color": "#8a3030",
            })
        # Timing
        timing = guild.get("timing", {})
        if timing.get("planting_nakshatra"):
            timing_str = " · ".join(filter(None, [
                timing.get("planting_nakshatra", ""),
                timing.get("planting_phase", ""),
                timing.get("planting_vara", ""),
            ]))
            rows.append({"label": "timing", "value": timing_str,
                         "label_color": "#4a6040"})
        # Vastu hint
        vp = guild.get("vastu_placement", {})
        if vp:
            first_zone = next(iter(vp))
            rows.append({"label": first_zone, "value": vp[first_zone],
                         "label_color": "#4a5060"})

        return {**super().render_zone(fs),
                "title": guild.get("anchor", "") or "Guild",
                "visual_type": "plant_form",
                "rows": rows,
                "apps": [{"name": "guild", "url": "/bhumi/guild"},
                         {"name": "agriculture", "url": "/bhumi/agriculture"}]}
