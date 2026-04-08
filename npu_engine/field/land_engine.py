"""
land_engine.py — Vastu mandala projected onto physical space.

Projects the 9-zone vastu mandala onto land use recommendations.
Without plot data: abstract zone guidance.
With plot data: spatially positioned zones.

Pattern follows ui_vastu_engine.py:
    canonical data → internal helpers → validation → public API
"""

from typing import Any, Dict, List, Optional
import csv
import math
import os
import sqlite3

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
_ZONES_CSV = os.path.join(_ROOT, "datasets", "cosmology", "vastu_zones.csv")
_DIRS_CSV = os.path.join(_ROOT, "datasets", "cosmology", "vastu_directions.csv")

# ══════════════════════════════════════════════════════════
# CANONICAL ZONE PRESCRIPTIONS — from vastu tradition
# ══════════════════════════════════════════════════════════

_ZONE_LAND_USE = {
    "NW": {
        "land_use": ["granary", "livestock", "guest room", "movement paths"],
        "structures": ["grain store", "animal shelter", "guest cottage"],
        "plants": ["wind-tolerant trees", "grasses", "bamboo"],
    },
    "N": {
        "land_use": ["treasury", "water feature", "underground storage"],
        "structures": ["well", "underground cistern", "safe room"],
        "plants": ["shade trees", "water-loving herbs"],
    },
    "NE": {
        "land_use": ["prayer", "well", "sacred plants", "sunrise viewing"],
        "structures": ["altar", "meditation seat", "sacred well"],
        "plants": ["tulsi", "sacred fig", "lotus pond"],
    },
    "E": {
        "land_use": ["entrance", "living space", "solar gain"],
        "structures": ["main door", "veranda", "sun room"],
        "plants": ["flowering entrance plants", "fragrant shrubs"],
    },
    "SE": {
        "land_use": ["kitchen", "fire", "transformation", "composting"],
        "structures": ["kitchen", "fire pit", "compost bay"],
        "plants": ["culinary herbs", "hot peppers", "aromatics"],
    },
    "S": {
        "land_use": ["bedroom", "heavy storage", "boundary hedge"],
        "structures": ["storage shed", "boundary wall", "bedroom"],
        "plants": ["dense hedge", "thorny barrier", "shade trees"],
    },
    "SW": {
        "land_use": ["anchor trees", "guild center", "root cellar"],
        "structures": ["root cellar", "tool shed", "main tree"],
        "plants": ["banyan", "anchor species", "deep-rooted trees"],
    },
    "W": {
        "land_use": ["bathroom", "water storage", "evening garden"],
        "structures": ["bathroom", "water tank", "evening pavilion"],
        "plants": ["evening-fragrant flowers", "water plants"],
    },
    "C": {
        "land_use": ["open space", "central axis", "unobstructed sky"],
        "structures": [],
        "plants": [],
    },
}

_zones_cache = None
_dirs_cache = None


def _load_zones():
    global _zones_cache
    if _zones_cache is not None:
        return _zones_cache
    _zones_cache = {}
    try:
        with open(_ZONES_CSV, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                d = row.get("direction", "")
                _zones_cache[d] = row
    except Exception:
        pass
    return _zones_cache


def _load_dirs():
    global _dirs_cache
    if _dirs_cache is not None:
        return _dirs_cache
    _dirs_cache = {}
    try:
        with open(_DIRS_CSV, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                d = row.get("direction", "")
                # Normalize to 2-letter code
                _DIR_MAP = {
                    "East": "E", "SouthEast": "SE", "South": "S",
                    "SouthWest": "SW", "West": "W", "NorthWest": "NW",
                    "North": "N", "NorthEast": "NE", "Center": "C",
                }
                key = _DIR_MAP.get(d, d)
                _dirs_cache[key] = row
    except Exception:
        pass
    return _dirs_cache


# ══════════════════════════════════════════════════════════
# VALIDATION
# ══════════════════════════════════════════════════════════

def _validate(layout: dict) -> dict:
    defaults = {
        "zones": {},
        "brahmasthana": {
            "prescription": "unobstructed · open sky",
            "radius_fraction": 0.1,
            "suitable_for": ["well", "open_lawn", "meditation"],
        },
        "current_field_emphasis": "",
        "recommendations": [],
        "timing": {"activity": "", "next_auspicious": ""},
        "attestation": "SYNTHESIS",
    }
    for key, default in defaults.items():
        if key not in layout or layout[key] is None:
            layout[key] = default
        elif isinstance(default, dict) and isinstance(layout[key], dict):
            for dk, dv in default.items():
                if dk not in layout[key]:
                    layout[key][dk] = dv
    return layout


# ══════════════════════════════════════════════════════════
# PUBLIC API
# ══════════════════════════════════════════════════════════

def derive_land_layout(field_state: dict, plot: dict = None) -> dict:
    """Project vastu mandala onto physical space.

    Args:
        field_state: from kernel field_state()
        plot: optional {orientation_degrees, area_m2}

    Returns validated dict — all keys guaranteed. Never raises.
    """
    try:
        zones_data = _load_zones()
        dirs_data = _load_dirs()
        p5 = field_state.get("panchanga", {})
        element = p5.get("element", "ether").lower()
        guna = p5.get("guna", "sattva").lower()
        tidx = int(p5.get("tidx", 0))

        # Guild data for plant recommendations
        try:
            from npu_engine.engines.guild_engine import derive_guild, _moon_phase
            guild = derive_guild(field_state)
            phase, activity = _moon_phase(tidx)
        except Exception:
            guild = {}
            phase, activity = "unknown", ""

        zones = {}
        field_emphasis = ""
        max_coherence = 0.0

        for zone_key in ["NW", "N", "NE", "E", "SE", "S", "SW", "W", "C"]:
            z_data = zones_data.get(zone_key, {})
            d_data = dirs_data.get(zone_key, {})
            land = _ZONE_LAND_USE.get(zone_key, {})

            z_elem = (z_data.get("element", "") or d_data.get("element", "")).lower()
            z_deity = z_data.get("deity", "") or d_data.get("deity", "")
            z_guna = d_data.get("guna", "")

            # Coherence: how much the current field aligns with this zone
            coherence = 0.0
            if z_elem == element:
                coherence += 0.5
            if z_guna == guna:
                coherence += 0.3
            coherence += 0.2  # baseline

            if coherence > max_coherence:
                max_coherence = coherence
                field_emphasis = zone_key

            # Recommended plants: guild companions for matching element zones
            rec_plants = list(land.get("plants", []))
            if zone_key == "SW" and guild.get("anchor"):
                rec_plants.insert(0, guild["anchor"])
            if zone_key == "NE":
                rec_plants = ["tulsi", "sacred plants"]

            zones[zone_key] = {
                "deity": z_deity,
                "element": z_elem or "ether",
                "guna": z_guna,
                "land_use": land.get("land_use", []),
                "recommended_plants": rec_plants[:5],
                "recommended_structures": land.get("structures", []),
                "activity": d_data.get("zone_activity", ""),
                "coherence": round(min(1.0, coherence), 2),
            }

        # Recommendations
        recs = []
        if field_emphasis:
            z = zones[field_emphasis]
            if z["land_use"]:
                recs.append(f"{field_emphasis} zone ({z['deity']}): {z['land_use'][0]}")
        recs.append(f"Moon: {phase.replace('_',' ')} · {activity}")
        if guild.get("anchor"):
            recs.append(f"Guild anchor: {guild['anchor']} ({guild.get('nakshatra', '')})")

        layout = {
            "zones": zones,
            "brahmasthana": {
                "prescription": "unobstructed · open sky",
                "radius_fraction": 0.1,
                "suitable_for": ["well", "open_lawn", "meditation"],
            },
            "current_field_emphasis": field_emphasis,
            "recommendations": recs[:5],
            "timing": {
                "activity": activity,
                "moon_phase": phase,
                "next_auspicious": "",
            },
            "attestation": "SYNTHESIS",
        }

        return _validate(layout)

    except Exception:
        return _validate({"attestation": "SYNTHESIS"})


# ══════════════════════════════════════════════════════════
# PERMACULTURE MANDALA — concentric ring ecosystem design
# ══════════════════════════════════════════════════════════

_PFAF_DB = os.path.join(_ROOT, "datasets", "plants", "pfaf.sqlite")

_HABIT_RING = {
    "tree": "canopy",
    "deciduous tree": "canopy",
    "evergreen tree": "canopy",
    "bamboo": "canopy",
    "shrub": "shrub",
    "deciduous shrub": "shrub",
    "evergreen shrub": "shrub",
    "perennial": "groundcover",
    "annual": "groundcover",
    "biennial": "groundcover",
    "fern": "groundcover",
    "grass": "groundcover",
    "climber": "vine",
    "perennial climber": "vine",
    "annual climber": "vine",
    "bulb": "root",
    "aquatic": "groundcover",
}

_RING_CAPS = {
    "canopy": 3, "fruit": 5, "shrub": 8,
    "groundcover": 12, "vine": 5, "root": 6, "boundary": 4,
}

_RING_RADII = {
    "canopy": 0.15, "fruit": 0.28, "shrub": 0.42,
    "groundcover": 0.57, "vine": 0.68, "root": 0.78, "boundary": 1.0,
}

_REGION_KEYWORDS = {
    "pacific_nw": ["North America", "Western N. America", "Canada", "Oregon", "Washington"],
    "desert_sw": ["North America", "Mexico", "Southwestern", "Arizona", "Texas"],
    "great_plains": ["North America", "Great Plains", "Central N. America"],
    "gulf_coast": ["North America", "Southeastern", "S.E. United States", "Florida"],
    "eastern_woodlands": ["North America", "Eastern N. America", "E. United States"],
    "appalachian": ["North America", "Eastern N. America", "Appalachian"],
    "rocky_mountain": ["North America", "Western N. America", "Rocky"],
    "great_basin": ["North America", "Western N. America", "Great Basin"],
}

_ECOREGION_NAMES = {
    "pacific_nw": "Pacific Northwest",
    "desert_sw": "Desert Southwest",
    "great_plains": "Great Plains",
    "gulf_coast": "Gulf Coast",
    "eastern_woodlands": "Eastern Woodlands",
    "appalachian": "Appalachian",
    "rocky_mountain": "Rocky Mountain",
    "great_basin": "Great Basin",
}

_DESIGN_PRINCIPLES = {
    "kitchen": [
        "Intensive edge — spiral and keyhole geometry maximise growing surface",
        "Zone 0–1 proximity — highest-need plants closest to kitchen",
        "Vertical stacking — trellis, spiral, hanging baskets",
    ],
    "garden": [
        "7-layer food forest — canopy to root, all vertical niches filled",
        "Guild planting — every tree surrounded by support species",
        "Water harvesting — swale on contour captures and distributes rainfall",
    ],
    "farm": [
        "Keyline design — water from ridge to valley along keyline contours",
        "Sector analysis — wind, sun, water flow mapped to planting strategy",
        "Zone placement — frequency of visit determines distance from center",
    ],
    "landscape": [
        "Broadscale revegetation — windbreak corridors and woodland patches",
        "Keyline plowing — parallel to keyline for even water distribution",
        "Succession planting — pioneer → climax over 20-year timeline",
    ],
}


def _detect_ecoregion(lat: float, lon: float) -> str:
    if lon < -115 and lat > 42:
        return "pacific_nw"
    if lon < -105 and lat < 38:
        return "desert_sw"
    if lon > -85 and lon < -75 and lat > 35 and lat < 45:
        return "appalachian"
    if lon > -105 and lon < -90 and lat > 35 and lat < 50:
        return "great_plains"
    if lat < 33 and lon > -97:
        return "gulf_coast"
    if lon > -90 and lat > 35 and lat < 50:
        return "eastern_woodlands"
    return "eastern_woodlands"


def _hardiness_zone(lat: float) -> tuple:
    if lat > 45:
        return (4, 5)
    if lat > 40:
        return (5, 6)
    if lat > 35:
        return (6, 7)
    if lat > 30:
        return (7, 9)
    return (9, 11)


def _parse_hardiness(h) -> tuple:
    if not h:
        return (0, 12)
    import re
    m = re.findall(r"\d+", str(h))
    if not m:
        return (0, 12)
    return (int(m[0]), int(m[-1])) if len(m) >= 2 else (int(m[0]), int(m[0]) + 2)


def _assign_ring(habit: str, height: float) -> str:
    h = (habit or "").lower().strip()
    if "tree" in h:
        return "canopy" if height >= 8 else "fruit"
    if "shrub" in h:
        return "shrub"
    if any(token in h for token in ("perennial", "annual", "forb", "fern", "grass", "herb")):
        return "groundcover"
    if any(token in h for token in ("climber", "climb", "vine", "twining")):
        return "vine"
    if any(token in h for token in ("bulb", "tuber", "rhizome", "root crop")):
        return "root"
    ring = _HABIT_RING.get(h)
    if ring:
        return "canopy" if ring == "canopy" and height >= 8 else ("fruit" if ring == "canopy" else ring)
    if height >= 8:
        return "canopy"
    if height >= 4:
        return "fruit"
    if height >= 1.25:
        return "shrub"
    return "groundcover"


_ZONE_SEQUENCE = {
    "canopy": ["SW", "W", "NW", "N", "C"],
    "fruit": ["E", "SE", "S", "W", "N"],
    "shrub": ["NE", "E", "SE", "S", "SW", "W", "NW", "N"],
    "groundcover": ["N", "NE", "E", "SE", "S", "SW", "W", "NW"],
    "vine": ["E", "SE", "S", "SW", "W"],
    "root": ["N", "NE", "E", "SE", "S", "SW"],
    "boundary": ["E", "SE", "S", "SW", "W", "NW", "N", "NE"],
}

_ZONE_ANGLE = {
    "N": 0.0,
    "NE": 45.0,
    "E": 90.0,
    "SE": 135.0,
    "S": 180.0,
    "SW": 225.0,
    "W": 270.0,
    "NW": 315.0,
    "C": 0.0,
}

_ZONE_GRAHA = {
    "NE": "guru",
    "E": "surya",
    "SE": "mangal",
    "S": "shukra",
    "SW": "shani",
    "W": "shukra",
    "NW": "chandra",
    "N": "budha",
    "C": "guru",
}


def _zone_for_candidate(plant: dict, ring_name: str, index: int) -> str:
    zone = (plant.get("vastu_zone") or plant.get("zone") or "").strip().upper()
    if zone in _ZONE_ANGLE:
        return zone
    sequence = _ZONE_SEQUENCE.get(ring_name, _ZONE_SEQUENCE["groundcover"])
    if plant.get("medicinal_rating") and int(plant.get("medicinal_rating") or 0) >= 4:
        return "NE"
    if plant.get("edibility_rating") and int(plant.get("edibility_rating") or 0) >= 4:
        return "E" if ring_name in {"fruit", "groundcover", "root"} else "SE"
    return sequence[index % len(sequence)]


def _position_for_zone_arc(center_lat: float, center_lon: float, ring_radius_m: float, zone: str, offset_index: int, offset_count: int):
    base_deg = _ZONE_ANGLE.get(zone, 0.0)
    arc_span = 30.0 if zone != "C" else 360.0
    if zone == "C":
        angle_deg = base_deg
    else:
        slot_count = max(offset_count, 1)
        local = ((offset_index + 0.5) / slot_count) - 0.5
        angle_deg = base_deg + local * arc_span
    angle = math.radians(angle_deg - 90.0)
    m_lat = 111320.0
    m_lon = 111320.0 * math.cos(math.radians(center_lat)) if center_lat else 111320.0
    lat = center_lat + ring_radius_m * math.cos(angle) / m_lat
    lon = center_lon + ring_radius_m * math.sin(angle) / m_lon
    return round(lat, 6), round(lon, 6), round(angle_deg % 360.0, 1)


def _compact_sources(plant: dict) -> List[str]:
    sources = plant.get("sources") or []
    if isinstance(sources, str):
        sources = [sources]
    compact = []
    for source in sources:
        label = str(source).strip()
        if not label:
            continue
        compact.append(label)
    att = str(plant.get("attestation") or "")
    if "PFAF" in att and "PFAF" not in compact:
        compact.append("PFAF")
    if "INATURALIST" in att and "iNaturalist" not in compact:
        compact.append("iNaturalist")
    if "USDA" in att and "USDA" not in compact:
        compact.append("USDA")
    return compact


def _plant_payload(plant: dict, ring_name: str, zone: str) -> dict:
    name = plant.get("common_name") or plant.get("name") or plant.get("latin_name") or plant.get("latin") or ""
    latin = plant.get("latin_name") or plant.get("latin") or ""
    height = float(plant.get("height", 0) or plant.get("mature_height_m", 0) or 0)
    spread = float(plant.get("canopy_spread_m", 0) or max(height * 0.6, 0.5))
    edibility = int(plant.get("edibility_rating", plant.get("edibility", 0)) or 0)
    medicinal = int(plant.get("medicinal_rating", plant.get("medicinal", 0)) or 0)
    return {
        "name": name,
        "latin": latin,
        "common_name": name,
        "family": plant.get("family", ""),
        "habit": plant.get("growth_habit") or plant.get("habit") or "",
        "height": round(height, 2),
        "canopy_spread_m": round(spread, 2),
        "graha": plant.get("graha") or _ZONE_GRAHA.get(zone, "budha"),
        "zone": zone,
        "edibility": edibility,
        "medicinal": medicinal,
        "edible_uses": (plant.get("edible_uses") or "")[:200],
        "medicinal_uses": (plant.get("medicinal_uses") or "")[:200],
        "known_hazards": (plant.get("known_hazards") or "")[:120],
        "sources": _compact_sources(plant),
        "attestation": plant.get("attestation", "SYNTHESIS"),
        "guild_role": plant.get("guild_role", ring_name),
        "native_status": plant.get("native_status", ""),
    }


def _query_pfaf_regional(lat: float, lon: float, hz: tuple, limit: int = 40) -> list:
    if not os.path.exists(_PFAF_DB):
        return []
    eco = _detect_ecoregion(lat, lon)
    keywords = _REGION_KEYWORDS.get(eco, ["North America"])
    try:
        conn = sqlite3.connect(_PFAF_DB)
        conn.row_factory = sqlite3.Row
        clauses = " OR ".join(["found_in LIKE ? OR range LIKE ?" for _ in keywords])
        params = []
        for kw in keywords:
            params += [f"%{kw}%", f"%{kw}%"]
        params.append(limit * 3)  # fetch extra, filter after
        rows = conn.execute(
            f"SELECT latin_name, common_name, family, habit, height, "
            f"hardiness, edibility_rating, medicinal_rating, other_uses_rating, "
            f"range, found_in, edible_uses, medicinal_uses, known_hazards "
            f"FROM plants WHERE ({clauses}) "
            f"ORDER BY edibility_rating DESC, medicinal_rating DESC LIMIT ?",
            params,
        ).fetchall()
        conn.close()
        plants = []
        for r in rows:
            ph = _parse_hardiness(r["hardiness"])
            if ph[0] > hz[1] or ph[1] < hz[0]:
                continue
            utility = (r["edibility_rating"] or 0) + (r["medicinal_rating"] or 0) + (r["other_uses_rating"] or 0)
            if utility <= 0:
                continue
            plants.append(dict(r))
            if len(plants) >= limit:
                break
        return plants
    except Exception:
        return []


def _place_in_arc(center_lat, center_lon, ring_radius_m, index, count):
    """Place item at angular position within a ring."""
    angle = (index / max(count, 1)) * math.pi * 2 - math.pi / 2
    m_lat = 111320.0
    m_lon = 111320.0 * math.cos(math.radians(center_lat)) if center_lat else 111320.0
    lat = center_lat + ring_radius_m * math.cos(angle) / m_lat
    lon = center_lon + ring_radius_m * math.sin(angle) / m_lon
    return lat, lon, math.degrees(angle) % 360


def _scale_label(radius_m: float) -> str:
    if radius_m <= 15:
        return "kitchen"
    if radius_m <= 50:
        return "garden"
    if radius_m <= 200:
        return "farm"
    return "landscape"


def derive_permaculture_mandala(
    field_state: dict, lat: float, lon: float, radius_m: float = 50
) -> dict:
    """Generate a complete permaculture mandala design for a site.

    Merges guild engine data, PFAF regional plants, and vastu zone prescriptions
    into a concentric ring design with features and keyhole paths.

    Returns validated dict — all keys guaranteed. Never raises.
    """
    try:
        scale = _scale_label(radius_m)
        eco_name = "North America"
        hz_display = ""
        m_lat = 111320.0
        m_lon = 111320.0 * math.cos(math.radians(lat)) if lat else 111320.0

        guild_data = {}
        try:
            from npu_engine.engines.guild_engine import derive_guild_state  # type: ignore
            guild_data = derive_guild_state(field_state)
        except Exception:
            try:
                from npu_engine.engines.guild_engine import derive_guild
                guild_data = derive_guild(field_state)
            except Exception:
                guild_data = {}

        regional = {}
        try:
            from npu_engine.field.region_engine import derive_regional_plants
            regional = derive_regional_plants(lat, lon, radius_km=max(radius_m / 1000.0, 8.0), limit=60)
            eco_name = regional.get("ecoregion") or eco_name
            hz_display = str(regional.get("hardiness_zone") or "")
        except Exception:
            regional = {"plants": []}
            eco = _detect_ecoregion(lat, lon)
            eco_name = _ECOREGION_NAMES.get(eco, "North America")
            hz_range = _hardiness_zone(lat)
            hz_display = f"{hz_range[0]}-{hz_range[1]}"

        rings = {k: [] for k in ["canopy", "fruit", "shrub", "groundcover", "vine", "root", "boundary"]}

        seen = set()
        regional_plants = list(regional.get("plants") or [])
        for idx, plant in enumerate(regional_plants):
            habit = plant.get("growth_habit") or plant.get("habit") or ""
            height = float(plant.get("height", 0) or plant.get("mature_height_m", 0) or 0)
            ring = _assign_ring(habit, height)
            if len(rings[ring]) >= _RING_CAPS.get(ring, 8):
                continue
            key = (plant.get("latin_name") or plant.get("common_name") or "").strip().lower()
            if not key or key in seen:
                continue
            seen.add(key)
            zone = _zone_for_candidate(plant, ring, idx)
            rings[ring].append(_plant_payload(plant, ring, zone))

        anchor_name = guild_data.get("anchor", "")
        anchor_zone = str(guild_data.get("vastu_zone") or "SW").upper() or "SW"
        if anchor_name:
            for ring_name in ["shrub", "fruit", "canopy"]:
                if len(rings[ring_name]) < _RING_CAPS.get(ring_name, 8):
                    rings[ring_name].insert(0, {
                        "name": anchor_name,
                        "latin": "",
                        "common_name": anchor_name,
                        "family": "",
                        "habit": "Guild anchor",
                        "height": 0.0,
                        "canopy_spread_m": 1.0,
                        "graha": _ZONE_GRAHA.get(anchor_zone, "guru"),
                        "zone": anchor_zone,
                        "edibility": 0,
                        "medicinal": 0,
                        "edible_uses": "",
                        "medicinal_uses": "",
                        "known_hazards": "",
                        "sources": ["Guild"],
                        "attestation": "SYNTHESIS",
                        "guild_role": "anchor",
                    })
                    break

        for companion in (guild_data.get("companions") or []):
            if isinstance(companion, dict):
                cname = companion.get("plant") or companion.get("name") or ""
                crole = companion.get("guild_function", "companion")
                zone = str(companion.get("vastu_zone") or "SW").upper()
            else:
                cname = str(companion)
                crole = "companion"
                zone = "SW"
            if not cname:
                continue
            ring = "shrub" if crole in ("nitrogen_fixer", "dynamic_accumulator", "pollinator_attractor", "ground_cover") else "fruit"
            if len(rings[ring]) >= _RING_CAPS.get(ring, 8):
                continue
            key = cname.strip().lower()
            if key in seen:
                continue
            seen.add(key)
            rings[ring].append({
                "name": cname,
                "latin": "",
                "common_name": cname,
                "family": "",
                "habit": crole.replace("_", " "),
                "height": 0.0,
                "canopy_spread_m": 0.8,
                "graha": _ZONE_GRAHA.get(zone, "budha"),
                "zone": zone,
                "edibility": 0,
                "medicinal": 0,
                "edible_uses": "",
                "medicinal_uses": "",
                "known_hazards": "",
                "sources": ["Guild"],
                "attestation": "SYNTHESIS",
                "guild_role": crole,
            })

        for ring_name, ring_plants in rings.items():
            ring_r = _RING_RADII.get(ring_name, 0.5) * radius_m
            zone_buckets = {}
            for plant in ring_plants:
                zone_buckets.setdefault(plant.get("zone") or "N", []).append(plant)
            for zone, plants in zone_buckets.items():
                for offset_index, plant in enumerate(plants):
                    plat, plon, arc_deg = _position_for_zone_arc(lat, lon, ring_r, zone, offset_index, len(plants))
                    plant["lat"] = plat
                    plant["lon"] = plon
                    plant["arc_deg"] = arc_deg
                    plant["radius_m"] = round(ring_r, 1)

        # ── Features ──
        features = {
            "pond": {
                "lat": round(lat + radius_m * 0.55 / m_lat, 6),
                "lon": round(lon + radius_m * 0.55 / m_lon, 6),
                "radius_m": round(radius_m * 0.08, 1),
                "zone": "NE",
            },
            "compost": {
                "lat": round(lat - radius_m * 0.5 / m_lat, 6),
                "lon": round(lon - radius_m * 0.5 / m_lon, 6),
                "zone": "SW",
            },
            "hearth": {
                "lat": round(lat - radius_m * 0.5 / m_lat, 6),
                "lon": round(lon + radius_m * 0.5 / m_lon, 6),
                "zone": "SE",
            },
            "well": {
                "lat": round(lat + radius_m * 0.6 / m_lat, 6),
                "lon": round(lon, 6),
                "zone": "N",
            },
            "gate": {
                "lat": round(lat, 6),
                "lon": round(lon + radius_m * 0.95 / m_lon, 6),
                "bearing": 90,
                "zone": "E",
            },
            "swales": [
                {
                    "lat": round(lat + radius_m * 0.4 / m_lat, 6),
                    "lon": round(lon, 6),
                    "bearing": 90,
                    "length_m": round(radius_m * 1.5, 1),
                    "zone": "N",
                },
                {
                    "lat": round(lat, 6),
                    "lon": round(lon - radius_m * 0.5 / m_lon, 6),
                    "bearing": 90,
                    "length_m": round(radius_m * 1.2, 1),
                    "zone": "W",
                },
            ],
            "paths": [
                {"bearing": 90, "label": "E \xb7 gate"},
                {"bearing": 0, "label": "N \xb7 water"},
                {"bearing": 225, "label": "SW \xb7 compost"},
                {"bearing": 315, "label": "NW \xb7 tools"},
            ],
        }

        # ── Guild summary ──
        companion_names = []
        for companion in (guild_data.get("companions") or []):
            if isinstance(companion, dict):
                companion_names.append(companion.get("plant") or companion.get("name") or "")
            else:
                companion_names.append(str(companion))

        guild_summary = {
            "anchor": guild_data.get("anchor", ""),
            "companions": [c for c in companion_names if c],
            "moon_phase": guild_data.get("moon_phase", ""),
            "activity": guild_data.get("recommended_activity", ""),
            "timing_quality": guild_data.get("timing_quality", ""),
            "nakshatra": guild_data.get("nakshatra", ""),
        }

        return {
            "rings": rings,
            "features": features,
            "guild": guild_summary,
            "center": {"lat": lat, "lon": lon, "radius_m": radius_m},
            "scale": scale,
            "ecoregion": eco_name,
            "hardiness_zone": hz_display,
            "design_principles": _DESIGN_PRINCIPLES.get(scale, []),
            "plant_count": sum(len(v) for v in rings.values()),
            "attestation": "SYNTHESIS",
        }

    except Exception as e:
        return {
            "rings": {k: [] for k in ["canopy", "fruit", "shrub", "groundcover", "vine", "root", "boundary"]},
            "features": {"pond": {}, "compost": {}, "hearth": {}, "well": {}, "gate": {}, "swales": [], "paths": []},
            "guild": {"anchor": "", "companions": [], "moon_phase": "", "activity": ""},
            "center": {"lat": lat, "lon": lon, "radius_m": radius_m},
            "scale": _scale_label(radius_m),
            "ecoregion": "",
            "hardiness_zone": [],
            "design_principles": [],
            "plant_count": 0,
            "error": str(e),
            "attestation": "SYNTHESIS",
        }
