"""plants_bp.py — Plants and land routes.

Extracted from kernel.py (RTE-005).
"""
import json
import math
import os
import sqlite3
import unicodedata
from typing import Any, Dict, Optional

from flask import Blueprint, Response, jsonify, request, send_file, send_from_directory

plants_bp = Blueprint('plants', __name__)

# ── Kernel-level imports (lazy where possible) ──────────────
from kernel import (
    field_state,
    _json_serial,
    _load_csv,
    _slugify,
    _lookup_plant,
    _DATA,
    _HERE,
    NAKSHATRA_PLANT_DATA,
    _PLANT_BY_NAKSHATRA,
    NAKSHATRAS,
    nak_to_itrans,
    _seasonal_plants,
    _today_plants,
    _VARA_GRAHA_NAME,
)

# ── Module-level path for _here (used by guild_matrix, entity, schema) ──
_here = str(_HERE)

# ── PFAF SQLite helper ─────────────────────────────────
_PFAF_DB = _DATA / "plants" / "pfaf.sqlite"


def _pfaf_query(sql, params=()):
    if not _PFAF_DB.exists():
        return []
    conn = sqlite3.connect(str(_PFAF_DB))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# Element → PFAF growing condition filters
_ELEMENT_PFAF_FILTERS = {
    "fire":  {"shade": ("F",), "moisture": ("D", "DM"), "notes": "drought tolerant, full sun"},
    "water": {"shade": ("S", "SN"), "moisture": ("M", "MW", "W"), "notes": "moisture loving, shade tolerant"},
    "earth": {"shade": ("S", "SN", "F"), "moisture": ("M", "DM"), "notes": "heavy soil, deep rooted"},
    "air":   {"shade": ("F", "SN"), "moisture": ("D", "DM"), "notes": "light soil, aromatic"},
    "ether": {"shade": (), "moisture": (), "notes": "any soil, prioritize medicinal"},
}


# ── PFAF regional plant lookup ──────────────────────

def _pfaf_region_keywords(lat, lon):
    if lon < -115 and lat > 42:
        return ['North America', 'Western N. America', 'Canada', 'Oregon', 'Washington']
    if lon < -105 and lat < 38:
        return ['North America', 'Mexico', 'Southwestern', 'Arizona', 'Texas']
    if lon > -85 and lon < -75 and lat > 35 and lat < 45:
        return ['North America', 'Eastern N. America', 'Appalachian']
    if lon > -105 and lon < -90 and lat > 35 and lat < 50:
        return ['North America', 'Great Plains', 'Central N. America', 'Canada']
    if lat < 33 and lon > -97:
        return ['North America', 'Southeastern', 'S.E. United States', 'Florida']
    if lon > -90 and lat > 35 and lat < 50:
        return ['North America', 'Eastern N. America', 'E. United States', 'Canada']
    return ['North America']


def _pfaf_ecoregion_name(lat, lon):
    if lon < -115 and lat > 42:
        return 'Pacific Northwest'
    if lon < -105 and lat < 38:
        return 'Desert Southwest'
    if lon > -85 and lon < -75 and lat > 35 and lat < 45:
        return 'Appalachian'
    if lon > -105 and lon < -90 and lat > 35 and lat < 50:
        return 'Great Plains'
    if lat < 33 and lon > -97:
        return 'Gulf Coast'
    if lon > -90 and lat > 35 and lat < 50:
        return 'Eastern Woodlands'
    return 'North America'


# ── Mandala helpers ──────────────────────────────────

def _mandala_patch_class_from_type(mandala_type: str) -> str:
    return {
        "orchard": "orchard_support_patch",
        "medicinal": "medicinal_patch",
        "pollinator": "pollinator_patch",
        "food_forest": "food_forest_patch",
        "sacred_grove": "sacred_court",
    }.get((mandala_type or "").strip().lower(), "food_forest_patch")


def _mandala_slug(value: str) -> str:
    import hashlib
    import re

    base = re.sub(r"[^a-z0-9]+", "_", (value or "").strip().lower()).strip("_")
    if base:
        return base
    return hashlib.md5((value or "candidate").encode("utf-8")).hexdigest()[:8]


def _mandala_plant_input(plant: Dict[str, Any], ring_name: str) -> Dict[str, Any]:
    name = (plant.get("name") or plant.get("common_name") or plant.get("latin") or "candidate").strip()
    latin = (plant.get("latin") or "").strip() or None
    ring = (ring_name or "shrub").strip().lower()
    layer = {
        "fruit": "subcanopy",
        "boundary": "shrub",
    }.get(ring, ring if ring in {"canopy", "subcanopy", "shrub", "herb", "groundcover", "vine", "root"} else "shrub")
    habit = {
        "canopy": "upright",
        "subcanopy": "upright",
        "shrub": "branching",
        "groundcover": "spreading",
        "vine": "twining",
        "root": "rosette",
        "boundary": "branching",
    }.get(ring, "branching")
    default_height = {
        "canopy": 8.0,
        "subcanopy": 5.0,
        "shrub": 2.5,
        "groundcover": 0.3,
        "vine": 3.0,
        "root": 0.5,
        "boundary": 3.0,
    }.get(ring, 2.0)
    height = float(plant.get("height", 0) or default_height)
    source_systems = ["PFAF"] if str(plant.get("attestation", "")).startswith("OBSERVED:PFAF") else ["guild_matrix"]
    source_text = " ".join([
        name,
        latin or "",
        str(plant.get("guild_role", "") or ""),
        str(plant.get("edible_uses", "") or ""),
        str(plant.get("medicinal_uses", "") or ""),
    ]).lower()
    medicinal = bool(plant.get("medicinal")) or "medic" in source_text or "tulsi" in source_text
    edible = bool(plant.get("edibility")) or ring in {"fruit", "root"} or "edible" in source_text
    guild_roles = []
    if medicinal:
        guild_roles.append("medicine")
    if edible:
        guild_roles.append("fruit" if ring != "root" else "root_crop")
    if "pollinator" in source_text:
        guild_roles.append("pollinator_support")
    if ring == "boundary":
        guild_roles.append("boundary")
    if not guild_roles:
        guild_roles.append("habitat" if ring in {"boundary", "groundcover"} else "pollinator_support")

    return {
        "plant_id": f"mandala_{_mandala_slug(latin or name)}",
        "common_name": name,
        "latin_name": latin,
        "source_systems": source_systems,
        "canonical_entity_id": None,
        "layer": layer,
        "habit": habit,
        "life_cycle": "perennial",
        "mature_height_m": round(height, 2),
        "canopy_spread_m": round(max(height * 0.7, 0.4), 2),
        "root_architecture": "mixed" if ring == "root" else "fibrous",
        "climbing": ring == "vine",
        "water_relationship": "mesic",
        "light_preference": "full_sun" if ring not in {"groundcover", "root"} else "part_sun",
        "soil_preferences": ["well_drained", "loamy"],
        "ph_range": {"min": 6.0, "max": 7.5},
        "hardiness_zone_min": 7,
        "hardiness_zone_max": 11,
        "native_status": "unknown",
        "guild_roles": guild_roles,
        "nitrogen_fixer": "nitrogen" in source_text,
        "dynamic_accumulator": "accumulator" in source_text,
        "edible": edible,
        "medicinal": medicinal,
        "fodder_roles": [],
        "erosion_control": ring in {"groundcover", "boundary"},
        "wildlife_support": True,
        "allelopathic": False,
        "allelopathy_notes": "",
        "thorny": False,
        "toxic": bool(plant.get("known_hazards")),
        "toxicity_notes": str(plant.get("known_hazards") or ""),
        "aggressive_spread": False,
        "shade_cast": "high" if ring in {"canopy", "subcanopy"} else "low",
        "spacing_sensitivity": "medium",
        "maintenance_burden": "moderate",
        "establishment_difficulty": "medium",
        "pruning_response": "good",
        "propagation_modes": ["seed"],
    }


def _mandala_site_context(payload: Dict[str, Any], mandala: Dict[str, Any], generator: Dict[str, Any]) -> Dict[str, Any]:
    selected_context = payload.get("selected_context") or {}
    hz = mandala.get("hardiness_zone") or []
    temperature_zone = None
    if isinstance(hz, list) and hz:
        try:
            temperature_zone = int(round(sum(float(v) for v in hz) / len(hz)))
        except Exception:
            temperature_zone = None
    elif isinstance(hz, str) and hz.strip():
        try:
            import re
            nums = [int(n) for n in re.findall(r"\d+", hz)]
            if nums:
                temperature_zone = int(round(sum(nums) / len(nums)))
        except Exception:
            temperature_zone = None
    return {
        "object_type": selected_context.get("object_type", "patch"),
        "object_id": selected_context.get("object_id") or f"patch_draft_{_mandala_slug(str(payload.get('lat', '0')) + '_' + str(payload.get('lon', '0')))}",
        "label": selected_context.get("label") or "Mandala draft patch",
        "water_relationship": selected_context.get("water_relationship", "mesic"),
        "light_preference": selected_context.get("light_preference", "full_sun"),
        "soil_preferences": selected_context.get("soil_preferences", ["well_drained", "loamy"]),
        "space_available_m": float(payload.get("radius_m", 50) or 50) * (0.7 if generator.get("density") == "high" else 1.0),
        "temperature_zone": temperature_zone,
        "animal_pressure": selected_context.get("animal_pressure", []),
        "context_flags": selected_context.get("context_flags", []),
        "hard_exclusion": bool(selected_context.get("hard_exclusion", False)),
    }


def _build_land_mandala_recommendation(payload: Dict[str, Any]) -> Dict[str, Any]:
    from atlas.plant_intel.pipeline import run_plant_pipeline
    from npu_engine.field.land_engine import derive_permaculture_mandala

    lat = float(payload.get("lat", 0) or 0)
    lon = float(payload.get("lon", 0) or 0)
    radius_m = float(payload.get("radius_m", 50) or 50)
    generator = dict(payload.get("generator") or {})
    session_controls = dict(payload.get("session_controls") or {})
    situation = session_controls.get("situation") or "generate_medicinal_patch"
    resolution_profile = session_controls.get("resolution_profile") or "medicinal_weighted"
    policy_mode = session_controls.get("policy_mode") or "default"

    mandala = derive_permaculture_mandala(field_state(), lat, lon, radius_m)
    site_context = _mandala_site_context(payload, mandala, generator)
    candidates = []

    for ring_name, ring_plants in (mandala.get("rings") or {}).items():
        for plant in ring_plants[:3]:
            try:
                plant_input = _mandala_plant_input(plant, ring_name)
                bundle = run_plant_pipeline(
                    plant_input,
                    site_context,
                    situation=situation,
                    resolution_profile=resolution_profile,
                    policy_mode=policy_mode,
                    include_astro_bridge=bool(generator.get("include_astro_bridge", True)),
                    include_ayur_bridge=bool(generator.get("include_ayur_bridge", True)),
                )
                ecology = bundle["ecology_profile"]
                site_fit = bundle["site_fit"]
                resolved = bundle["field_resolution"]
                plant_slug = _mandala_slug(ecology.plant_ref.latin_name or ecology.plant_ref.common_name or ecology.plant_ref.plant_id)
                plant_ref = {
                    "object_type": "plant_recommendation",
                    "object_id": f"plant_rec_{plant_slug}",
                    "label": f"{ecology.plant_ref.common_name or ecology.plant_ref.plant_id} recommendation",
                }
                patch_classes = site_fit.placement_guidance.get("recommended_patch_classes") or []
                recommended_patch_class = patch_classes[0].value if patch_classes else _mandala_patch_class_from_type(generator.get("mandala_type", ""))
                fit_summary = site_fit.fit_summary
                site_fit_summary = " · ".join([
                    ecology.site_preferences.get("water_relationship", "unknown"),
                    ecology.site_preferences.get("light_preference", "unknown"),
                    f"{ecology.growth_form.get('layer', ring_name)} layer",
                ])
                candidates.append({
                    "object_ref": plant_ref,
                    "plant_id": ecology.plant_ref.plant_id,
                    "name": ecology.plant_ref.common_name or ecology.plant_ref.plant_id,
                    "latin_name": ecology.plant_ref.latin_name,
                    "ring": ring_name,
                    "layer": ecology.growth_form.get("layer", ring_name),
                    "fit": fit_summary.get("overall_fit", 0.0),
                    "fit_class": fit_summary.get("fit_class", "moderate"),
                    "primary_reason": fit_summary.get("primary_reason", ""),
                    "site_fit_summary": site_fit_summary,
                    "hard_exclusion": resolved.hard_exclusion_applied,
                    "override_applied": resolved.override_applied,
                    "override_reason": resolved.override_reason,
                    "warnings": list(dict.fromkeys(resolved.warnings + ([plant.get("known_hazards")] if plant.get("known_hazards") else []))),
                    "final_recommendation": resolved.final_recommendation,
                    "why": (resolved.explanation[0] if resolved.explanation else fit_summary.get("primary_reason", "")),
                    "recommended_patch_class": recommended_patch_class,
                    "confidence": resolved.confidence.overall if resolved.confidence else 0.0,
                })
            except Exception as e:
                candidates.append({
                    "object_ref": {
                        "object_type": "plant_recommendation",
                        "object_id": f"plant_rec_{_mandala_slug(str(plant.get('name') or ring_name))}",
                        "label": f"{plant.get('name') or ring_name} recommendation",
                    },
                    "plant_id": _mandala_slug(str(plant.get("name") or ring_name)),
                    "name": plant.get("name") or plant.get("latin") or ring_name,
                    "latin_name": plant.get("latin"),
                    "ring": ring_name,
                    "layer": ring_name,
                    "fit": 0.0,
                    "fit_class": "poor",
                    "primary_reason": f"candidate mapping failed: {e}",
                    "site_fit_summary": "unavailable",
                    "hard_exclusion": False,
                    "override_applied": False,
                    "override_reason": None,
                    "warnings": ["candidate mapping failed"],
                    "final_recommendation": "not_recommended",
                    "why": "candidate mapping failed",
                    "recommended_patch_class": _mandala_patch_class_from_type(generator.get("mandala_type", "")),
                    "confidence": 0.0,
                })

    candidates.sort(
        key=lambda c: (
            c["hard_exclusion"],
            0 if c["final_recommendation"] == "recommended" else 1 if c["final_recommendation"] == "recommended_with_override" else 2,
            -float(c["fit"]),
        )
    )
    top_candidates = candidates[:5]
    preview_warnings = []
    if not generator.get("use_ecology_profile", True):
        preview_warnings.append("Ecology profile retained as direct authority for placement.")
    if not generator.get("use_site_fit", True):
        preview_warnings.append("Site fit retained as ecological gate for placement.")
    if generator.get("include_astro_bridge", True) or generator.get("include_ayur_bridge", True):
        preview_warnings.append("Bridge signals remain advisory unless resolved.")
    for candidate in top_candidates:
        preview_warnings.extend(candidate.get("warnings", []))
    preview_warnings = list(dict.fromkeys([w for w in preview_warnings if w]))[:6]
    exclusions = [c["name"] for c in top_candidates if c.get("hard_exclusion")]
    recommended_patch_class = (
        top_candidates[0]["recommended_patch_class"]
        if top_candidates else
        _mandala_patch_class_from_type(generator.get("mandala_type", ""))
    )
    draft_patch_ref = {
        "object_type": "patch",
        "object_id": site_context["object_id"],
        "label": site_context.get("label") or "Mandala draft patch",
    }

    return {
        "ok": True,
        "session_controls": {
            "situation": situation,
            "resolution_profile": resolution_profile,
            "policy_mode": policy_mode,
        },
        "mandala": mandala,
        "preview": {
            "recommended_patch_class": recommended_patch_class,
            "top_candidates": top_candidates,
            "warnings": preview_warnings,
            "exclusions": exclusions,
            "draft_patch_ref": draft_patch_ref,
            "primary_target_ref": draft_patch_ref,
            "primary_recommendation_ref": top_candidates[0]["object_ref"] if top_candidates else None,
            "recommendation_ids": [c["object_ref"]["object_id"] for c in top_candidates],
        },
    }


# ── PFAF row → plant input helper ──────────────────────

def _pfaf_row_to_plant_input(row: Dict[str, Any], plant_id: str) -> Dict[str, Any]:
    habit_text = str(row.get("habit") or "").lower()
    height = float(row.get("height", 0) or 0)
    if "tree" in habit_text and height > 5:
        layer = "canopy"
        habit = "upright"
    elif "shrub" in habit_text or 1 <= height <= 5:
        layer = "shrub"
        habit = "branching"
    elif "vine" in habit_text or "climb" in habit_text:
        layer = "vine"
        habit = "twining"
    elif height and height < 0.5:
        layer = "groundcover"
        habit = "spreading"
    else:
        layer = "herb"
        habit = "upright"
    medicinal = int(row.get("medicinal_rating", 0) or 0) >= 3
    edible = int(row.get("edibility_rating", 0) or 0) >= 3
    guild_roles = []
    if medicinal:
        guild_roles.append("medicine")
    if edible:
        guild_roles.append("fruit" if layer != "root" else "root_crop")
    if not guild_roles:
        guild_roles.append("pollinator_support")
    return {
        "plant_id": plant_id,
        "common_name": row.get("common_name") or row.get("latin_name") or plant_id,
        "latin_name": row.get("latin_name"),
        "source_systems": ["PFAF"],
        "canonical_entity_id": None,
        "layer": layer,
        "habit": habit,
        "life_cycle": "perennial",
        "mature_height_m": max(height, 0.4),
        "canopy_spread_m": round(max(height * 0.6, 0.4), 2),
        "root_architecture": "fibrous",
        "climbing": layer == "vine",
        "water_relationship": "mesic" if str(row.get("moisture") or "").upper() not in {"W"} else "wet",
        "light_preference": "full_sun" if str(row.get("shade") or "").upper() in {"F"} else "part_sun",
        "soil_preferences": ["well_drained", "loamy"],
        "ph_range": {"min": 6.0, "max": 7.5},
        "hardiness_zone_min": 7,
        "hardiness_zone_max": 11,
        "native_status": "unknown",
        "guild_roles": guild_roles,
        "nitrogen_fixer": False,
        "dynamic_accumulator": False,
        "edible": edible,
        "medicinal": medicinal,
        "fodder_roles": [],
        "erosion_control": layer in {"groundcover", "shrub"},
        "wildlife_support": True,
        "allelopathic": False,
        "allelopathy_notes": "",
        "thorny": False,
        "toxic": bool(row.get("known_hazards")),
        "toxicity_notes": str(row.get("known_hazards") or ""),
        "aggressive_spread": False,
        "shade_cast": "high" if layer == "canopy" else "low",
        "spacing_sensitivity": "medium",
        "maintenance_burden": "moderate",
        "establishment_difficulty": "medium",
        "pruning_response": "good",
        "propagation_modes": ["seed"],
    }


def _hexd_site_context(label: str, plant_input: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "object_type": "patch",
        "object_id": f"hexd_patch_{_mandala_slug(label)}",
        "label": label or "HEXD analytical patch",
        "water_relationship": plant_input.get("water_relationship", "mesic"),
        "light_preference": plant_input.get("light_preference", "full_sun"),
        "soil_preferences": plant_input.get("soil_preferences", ["well_drained", "loamy"]),
        "space_available_m": max(float(plant_input.get("canopy_spread_m", 1.2) or 1.2) * 1.5, 1.5),
        "temperature_zone": plant_input.get("hardiness_zone_min", 9),
        "animal_pressure": [],
        "context_flags": [],
        "hard_exclusion": False,
    }


def _lookup_pfaf_row(name: str) -> Optional[Dict[str, Any]]:
    q = (name or "").replace(" recommendation", "").strip()
    if not q:
        return None
    rows = _pfaf_query(
        """
        SELECT p.latin_name, p.common_name, p.habit, p.height,
               p.edibility_rating, p.medicinal_rating, p.shade, p.moisture,
               p.summary, p.edible_uses, p.medicinal_uses, p.known_hazards, p.family
        FROM plants p
        WHERE p.common_name LIKE ? OR p.latin_name LIKE ? OR p.other_names LIKE ? OR p.summary LIKE ?
        ORDER BY (p.medicinal_rating + p.edibility_rating) DESC
        LIMIT 1
        """,
        [f"%{q}%", f"%{q}%", f"%{q}%", f"%{q}%"],
    )
    return rows[0] if rows else None


def _serialize_weighted_candidate(candidate: Any) -> Dict[str, Any]:
    return {
        "value": getattr(candidate, "value", ""),
        "score": getattr(candidate, "score", 0.0),
        "basis": list(getattr(candidate, "basis", []) or []),
    }


def _build_hexd_plant_payload(object_id: str, label: str, session_controls: Dict[str, Any]) -> Dict[str, Any]:
    from atlas.plant_intel.pipeline import run_plant_pipeline

    row = _lookup_pfaf_row(label or object_id) or {
        "common_name": (label or object_id).replace(" recommendation", "").strip() or "Plant candidate",
        "latin_name": "",
        "habit": "shrub",
        "height": 1.2,
        "edibility_rating": 2,
        "medicinal_rating": 4,
        "shade": "F",
        "moisture": "M",
        "known_hazards": "",
        "medicinal_uses": "",
    }
    plant_input = _pfaf_row_to_plant_input(row, f"hexd_{_mandala_slug(label or object_id)}")
    bundle = run_plant_pipeline(
        plant_input,
        _hexd_site_context(label or object_id, plant_input),
        situation=session_controls.get("situation") or "generate_medicinal_patch",
        resolution_profile=session_controls.get("resolution_profile") or "medicinal_weighted",
        policy_mode=session_controls.get("policy_mode") or "default",
    )
    ecology = bundle["ecology_profile"]
    site_fit = bundle["site_fit"]
    astro = bundle["astro_bridge"]
    ayur = bundle["ayur_bridge"]
    resolver = bundle["field_resolution"]
    return {
        "payload_kind": "plant_recommendation",
        "object_ref": {
            "object_type": "plant_recommendation",
            "object_id": object_id,
            "label": label or ecology.plant_ref.common_name or ecology.plant_ref.plant_id,
        },
        "summary": {
            "name": ecology.plant_ref.common_name or ecology.plant_ref.plant_id,
            "latin_name": ecology.plant_ref.latin_name,
            "fit": site_fit.fit_summary.get("overall_fit", 0.0),
            "fit_class": site_fit.fit_summary.get("fit_class", "moderate"),
            "primary_reason": site_fit.fit_summary.get("primary_reason", ""),
            "final_recommendation": resolver.final_recommendation,
            "warnings": resolver.warnings,
            "hard_exclusion": resolver.hard_exclusion_applied,
            "override_applied": resolver.override_applied,
            "override_reason": resolver.override_reason,
        },
        "ecology": {
            "layer": ecology.growth_form.get("layer"),
            "habit": ecology.growth_form.get("habit"),
            "mature_height_m": ecology.growth_form.get("mature_height_m"),
            "water_relationship": ecology.site_preferences.get("water_relationship"),
            "light_preference": ecology.site_preferences.get("light_preference"),
            "guild_roles": ecology.functional_roles.get("guild_roles", []),
        },
        "site_fit": {
            "overall_fit": site_fit.fit_summary.get("overall_fit"),
            "fit_class": site_fit.fit_summary.get("fit_class"),
            "primary_reason": site_fit.fit_summary.get("primary_reason"),
            "hard_exclusion": resolver.hard_exclusion_applied,
            "avoid_contexts": site_fit.placement_guidance.get("avoid_contexts", []),
        },
        "astro_bridge": {
            "graha_affinities": [_serialize_weighted_candidate(c) for c in astro.astro_profile.get("graha_affinities", [])[:2]],
            "element_affinities": [_serialize_weighted_candidate(c) for c in astro.astro_profile.get("element_affinities", [])[:2]],
            "eligible_rings": [_serialize_weighted_candidate(c) for c in astro.mandala_profile.get("eligible_rings", [])[:2]],
            "confidence": astro.confidence.overall,
        },
        "ayur_bridge": {
            "rasa": [_serialize_weighted_candidate(c) for c in ayur.ayur_profile.get("rasa", [])[:2]],
            "virya": [_serialize_weighted_candidate(c) for c in ayur.ayur_profile.get("virya", [])[:1]],
            "dosha_effects": ayur.ayur_profile.get("dosha_effects", [])[:2],
            "confidence": ayur.confidence.overall,
        },
        "resolver": {
            "final_recommendation": resolver.final_recommendation,
            "warnings": resolver.warnings,
            "hard_exclusion": resolver.hard_exclusion_applied,
            "override_applied": resolver.override_applied,
            "override_reason": resolver.override_reason,
            "agreements": resolver.agreements,
            "tensions": resolver.tensions,
            "explanation": resolver.explanation,
        },
        "claims": [],
    }


def _build_hexd_patch_payload(object_id: str, label: str, session_controls: Dict[str, Any]) -> Dict[str, Any]:
    payload = _build_land_mandala_recommendation({
        "lat": 29.6516,
        "lon": -82.3248,
        "radius_m": 30,
        "generator": {
            "mandala_type": "medicinal",
            "density": "medium",
            "ring_count": 7,
            "anchor_plant": "",
            "primary_function": "medicine",
            "use_ecology_profile": True,
            "use_site_fit": True,
            "include_astro_bridge": True,
            "include_ayur_bridge": True,
        },
        "session_controls": session_controls,
        "selected_context": {
            "object_type": "patch",
            "object_id": object_id,
            "label": label or "Patch target",
        },
    })
    preview = payload.get("preview") or {}
    top_candidates = preview.get("top_candidates") or []
    return {
        "payload_kind": "patch",
        "object_ref": {
            "object_type": "patch",
            "object_id": object_id,
            "label": label or "Patch target",
        },
        "summary": {
            "patch_class": preview.get("recommended_patch_class"),
            "plant_count": len(top_candidates),
            "primary_reason": f"Resolver-oriented {preview.get('recommended_patch_class', 'patch')} analysis for the active session.",
            "warnings": preview.get("warnings", []),
            "exclusions": preview.get("exclusions", []),
        },
        "recommendations": top_candidates,
        "resolver": {
            "final_recommendation": "recommended" if top_candidates else "not_recommended",
            "warnings": preview.get("warnings", []),
            "hard_exclusion": bool(preview.get("exclusions")),
            "override_applied": False,
            "override_reason": None,
        },
        "claims": [],
    }


# ═══════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════

@plants_bp.route("/plants/today")
def _plants_today():
    base = _today_plants()
    fs = field_state()
    p5 = fs.get("panchanga", {})
    nd = p5.get("nak_data", {}) or {}

    # ── Fix: read current nakshatra from field_state, convert to
    #    ITRANS, then look up directly in NAKSHATRA_PLANT_DATA ──
    nak_iast = p5.get("nakshatra", "")
    nak_itrans = nak_to_itrans(nak_iast)
    np_ = _PLANT_BY_NAKSHATRA.get(nak_itrans) or _PLANT_BY_NAKSHATRA.get(nak_iast) or \
          base.get("nakshatra_plant") or {}

    # Load agriculture + biodynamic data for today
    agri_rows = _load_csv("plants/nakshatra_agriculture.csv")
    bio_rows = _load_csv("astrobotany/biodynamic_vedic_mapping.csv")
    nak_name = nak_iast

    def _norm(s):
        """Strip diacritics, aspirates, and vowel variations for fuzzy matching."""
        n = unicodedata.normalize("NFD", s.lower().replace(" ", "_").replace("-", ""))
        n = "".join(c for c in n if unicodedata.category(c) != "Mn")
        for a, b in [("sh", "s"), ("th", "t"), ("dh", "d"), ("ch", "c"),
                     ("kh", "k"), ("bh", "b"), ("ph", "p"), ("gh", "g"),
                     ("w", "v"), ("ee", "i"), ("oo", "u")]:
            n = n.replace(a, b)
        # Remove duplicate consonants and non-initial vowels for robust match
        return n

    def _nmatch(a, b):
        """Fuzzy nakshatra name match — handles IAST vs ASCII."""
        na, nb = _norm(a), _norm(b)
        if na == nb:
            return True
        # Consonant skeleton: first char + consonants only, truncated to 5
        def skel(s):
            c = s[0] + "".join(ch for ch in s[1:] if ch not in "aeiou_")
            return c[:5]
        return len(na) > 2 and len(nb) > 2 and skel(na) == skel(nb)

    nak_key = _norm(nak_name)

    agri = {}
    for row in agri_rows:
        if _nmatch(row.get("nakshatra") or "", nak_name):
            agri = row
            break

    bio_type = ""
    for row in bio_rows:
        naks_str = row.get("nakshatra_equivalents_sidereal_major", "")
        for chunk in naks_str.split(";"):
            cn = chunk.strip().split("(")[0].strip()
            if cn and _nmatch(cn, nak_name):
                bio_type = row.get("biodynamic_day_type", "")
                break

    # Week ahead: next 7 nakshatras
    nak_idx = -1
    for i, n in enumerate(NAKSHATRAS):
        if _nmatch(n, nak_name):
            nak_idx = i
            break
    week = []
    for d in range(1, 8):
        ni = (nak_idx + d) % 27 if nak_idx >= 0 else d % 27
        fn = NAKSHATRAS[ni]
        fa = next((r for r in agri_rows if _nmatch(r.get("nakshatra") or "", fn)), {})
        fb = ""
        for row in bio_rows:
            for chunk in (row.get("nakshatra_equivalents_sidereal_major") or "").split(";"):
                cn = chunk.strip().split("(")[0].strip()
                if cn and _nmatch(cn, fn):
                    fb = row.get("biodynamic_day_type", "")
                    break
        week.append({
            "nakshatra": fn,
            "activity": fa.get("activity", ""),
            "avoid": fa.get("avoid", ""),
            "biodynamic": fb,
        })

    tidx_raw = p5.get("tidx", 0)
    tidx = tidx_raw if isinstance(tidx_raw, int) else 0
    payload = {
        "nakshatra": nak_name,
        "tithi": p5.get("tithi", ""),
        "paksha": p5.get("paksha", ""),
        "vara": p5.get("vara", ""),
        "plant": np_.get("plant", ""),
        "common_name": np_.get("common_name", np_.get("plant", "")),
        "sanskrit_name": np_.get("sanskrit_name", ""),
        "deity": nd.get("deity", np_.get("deity", "")),
        "element": nd.get("element", ""),
        "dosha": np_.get("dosha", ""),
        "activity": agri.get("activity", ""),
        "avoid": agri.get("avoid", "\u2014"),
        "crops": agri.get("crops", ""),
        "quality": agri.get("quality", ""),
        "biodynamic_type": bio_type,
        "moon_phase": "waxing" if tidx < 15 else "waning",
        "ayurvedic_use": np_.get("ayurvedic_use", ""),
        "ritual_use": np_.get("ritual_use", ""),
        "growing_notes": np_.get("growing_notes", ""),
        "mantra": np_.get("mantra", ""),
        "body_part": np_.get("body_part", nd.get("body_region", "")),
        "metal": np_.get("metal", ""),
        "season": np_.get("season", ""),
        "week_ahead": week,
        # Keep legacy fields for backward compat
        "plants": base.get("plants", []),
        "dosha_today": base.get("dosha_today", {}),
    }
    return Response(
        json.dumps(payload, default=_json_serial, ensure_ascii=False),
        mimetype="application/json",
    )


@plants_bp.route("/plants/season")
def _plants_season():
    season, items = _seasonal_plants()
    payload = {"season": season, "plants": items}
    return Response(
        json.dumps(payload, default=_json_serial, ensure_ascii=False),
        mimetype="application/json",
    )


@plants_bp.route("/plants/catalog")
def _plants_catalog():
    payload = {"plants": NAKSHATRA_PLANT_DATA}
    return Response(
        json.dumps(payload, default=_json_serial, ensure_ascii=False),
        mimetype="application/json",
    )


@plants_bp.route("/plants/search")
def _plants_search():
    q = request.args.get("q", "").strip()
    element = request.args.get("element", "").strip().lower()
    use = request.args.get("use", "").strip().lower()
    habit = request.args.get("habit", "").strip().lower()
    limit = min(int(request.args.get("limit", 20)), 100)

    clauses, params = [], []
    if q:
        clauses.append("(p.latin_name LIKE ? OR p.common_name LIKE ? OR p.other_names LIKE ? OR p.summary LIKE ?)")
        w = f"%{q}%"
        params.extend([w, w, w, w])
    if habit:
        clauses.append("LOWER(p.habit) LIKE ?")
        params.append(f"%{habit}%")
    if use == "medicinal":
        clauses.append("p.medicinal_rating >= 3")
    elif use == "edible":
        clauses.append("p.edibility_rating >= 3")
    elif use == "sacred":
        pass  # filter after query

    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    sql = f"""
        SELECT p.latin_name, p.common_name, p.habit, p.height,
               p.edibility_rating, p.medicinal_rating, p.other_uses_rating,
               p.shade, p.moisture, p.soil, p.summary,
               p.edible_uses, p.medicinal_uses, p.other_uses,
               p.cultivation_details, p.known_hazards, p.family
        FROM plants p {where}
        ORDER BY (p.medicinal_rating + p.edibility_rating) DESC
        LIMIT ?
    """
    params.append(limit)
    results = _pfaf_query(sql, params)

    # Flag sacred plants — match by plant name, common name, or sanskrit name
    # against PFAF common_name, latin_name, or summary (case-insensitive substring)
    for r in results:
        r["sacred"] = False
        pfaf_names = " ".join(filter(None, [
            r.get("common_name", ""), r.get("latin_name", ""),
            r.get("summary", ""),
        ])).lower()
        for np_row in NAKSHATRA_PLANT_DATA:
            names_to_check = [
                (np_row.get("plant") or "").lower(),
                (np_row.get("common_name") or "").lower(),
                (np_row.get("sanskrit_name") or "").lower(),
            ]
            if any(n and n in pfaf_names for n in names_to_check):
                r["sacred"] = True
                r["nakshatra"] = np_row.get("nakshatra", "")
                r["sanskrit_name"] = np_row.get("sanskrit_name", "")
                r["deity"] = np_row.get("deity", "")
                r["mantra"] = np_row.get("mantra", "")
                break

    if use == "sacred":
        results = [r for r in results if r.get("sacred")]

    # Fallback: if PFAF returned nothing and we have a query,
    # check nakshatra_plants.csv for Sanskrit/common name matches
    if not results and q:
        ql = q.lower()
        for np_row in NAKSHATRA_PLANT_DATA:
            if ql in (np_row.get("plant") or "").lower() or \
               ql in (np_row.get("common_name") or "").lower() or \
               ql in (np_row.get("sanskrit_name") or "").lower():
                results.append({
                    "latin_name": np_row.get("plant", ""),
                    "common_name": np_row.get("common_name", ""),
                    "habit": "",
                    "height": None,
                    "edibility_rating": 0,
                    "medicinal_rating": 0,
                    "other_uses_rating": 0,
                    "shade": "", "moisture": "", "soil": "",
                    "summary": np_row.get("ayurvedic_use", ""),
                    "family": "",
                    "sacred": True,
                    "nakshatra": np_row.get("nakshatra", ""),
                    "sanskrit_name": np_row.get("sanskrit_name", ""),
                    "deity": np_row.get("deity", ""),
                    "mantra": np_row.get("mantra", ""),
                    "ayurvedic_use": np_row.get("ayurvedic_use", ""),
                    "ritual_use": np_row.get("ritual_use", ""),
                    "growing_notes": np_row.get("growing_notes", ""),
                })

    return Response(
        json.dumps(results, default=_json_serial, ensure_ascii=False),
        mimetype="application/json",
    )


@plants_bp.route("/plants/guild/<nakshatra_id>")
def _plants_guild(nakshatra_id):
    # Resolve nakshatra name
    nak_name = nakshatra_id.replace("_", " ").replace("-", " ")
    nak_row = None
    for r in NAKSHATRA_PLANT_DATA:
        if (r.get("nakshatra") or "").lower() == nak_name.lower():
            nak_row = r
            break
    if not nak_row:
        # Try fuzzy
        slug = _slugify(nak_name)
        for r in NAKSHATRA_PLANT_DATA:
            if _slugify(r.get("nakshatra", "")) == slug:
                nak_row = r
                break
    if not nak_row:
        return Response(
            json.dumps({"error": f"nakshatra not found: {nakshatra_id}"}, ensure_ascii=False),
            mimetype="application/json", status=404,
        )

    element = (nak_row.get("element") or "fire").lower()
    filt = _ELEMENT_PFAF_FILTERS.get(element, _ELEMENT_PFAF_FILTERS["fire"])

    def _guild_query(extra_where="", extra_params=(), order="(p.medicinal_rating + p.edibility_rating) DESC", lim=10):
        shade_clause = ""
        params = list(extra_params)
        if filt["shade"] and element != "ether":
            placeholders = ",".join("?" * len(filt["shade"]))
            shade_clause = f"AND p.shade IN ({placeholders})"
            params.extend(filt["shade"])
        moisture_clause = ""
        if filt["moisture"] and element != "ether":
            placeholders = ",".join("?" * len(filt["moisture"]))
            moisture_clause = f"AND p.moisture IN ({placeholders})"
            params.extend(filt["moisture"])
        sql = f"""
            SELECT p.latin_name, p.common_name, p.habit, p.height,
                   p.edibility_rating, p.medicinal_rating, p.other_uses_rating,
                   p.shade, p.moisture
            FROM plants p
            WHERE 1=1 {shade_clause} {moisture_clause} {extra_where}
            ORDER BY {order} LIMIT ?
        """
        params.append(lim)
        return _pfaf_query(sql, params)

    # Canopy: trees > 5m
    canopy = _guild_query("AND LOWER(p.habit) LIKE '%tree%' AND p.height > 5", order="p.height DESC", lim=5)
    # Sub-canopy: shrubs 2-5m
    sub_canopy = _guild_query("AND LOWER(p.habit) LIKE '%shrub%' AND p.height BETWEEN 2 AND 5", lim=5)
    # Shrub layer: shrubs < 2m
    shrub_layer = _guild_query("AND LOWER(p.habit) LIKE '%shrub%' AND p.height < 2 AND p.height > 0", lim=5)
    # Ground cover: < 0.5m
    ground_cover = _guild_query("AND p.height > 0 AND p.height < 0.5", lim=5)
    # Nitrogen fixers
    nitrogen = _pfaf_query("""
        SELECT DISTINCT p.latin_name, p.common_name, p.habit, p.height,
               p.edibility_rating, p.medicinal_rating, p.other_uses_rating
        FROM plants p JOIN plant_uses pu ON pu.plant = p.latin_name
        WHERE pu.name LIKE '%nitrogen%'
        ORDER BY (p.medicinal_rating + p.edibility_rating) DESC LIMIT 5
    """)
    # Medicinal: rating >= 4
    medicinal = _guild_query("AND p.medicinal_rating >= 4", order="p.medicinal_rating DESC", lim=6)

    payload = {
        "nakshatra": nak_row.get("nakshatra"),
        "element": element,
        "deity": nak_row.get("deity", ""),
        "sacred_plant": {
            "name": nak_row.get("plant", ""),
            "common_name": nak_row.get("common_name", ""),
            "sanskrit_name": nak_row.get("sanskrit_name", ""),
            "mantra": nak_row.get("mantra", ""),
            "ritual_use": nak_row.get("ritual_use", ""),
            "ayurvedic_use": nak_row.get("ayurvedic_use", ""),
        },
        "guild": {
            "canopy": canopy,
            "sub_canopy": sub_canopy,
            "shrub": shrub_layer,
            "ground_cover": ground_cover,
            "nitrogen_fixer": nitrogen,
            "medicinal": medicinal,
        },
        "element_notes": filt["notes"],
    }
    return Response(
        json.dumps(payload, default=_json_serial, ensure_ascii=False),
        mimetype="application/json",
    )


@plants_bp.route("/plants/related/<path:entity_id>")
def _plants_related(entity_id):
    """Traverse relation graph from entity, return connected plants."""
    try:
        from npu_engine.graph_engine import GraphEngine
        g = GraphEngine()
    except Exception as e:
        return Response(
            json.dumps({"error": f"GraphEngine unavailable: {e}"}, ensure_ascii=False),
            mimetype="application/json", status=500,
        )

    # Normalize entity_id: accept both colon and underscore format
    canonical = entity_id.replace(":", "_").lower().replace(" ", "_").replace("-", "_")
    depth = int(request.args.get("depth", 2))
    depth = min(depth, 3)

    edges = g.expand_from_entities([canonical], depth=depth, max_per_node=20)
    # Partition into plants vs other categories
    plants, paths, nakshatras, ragas = [], [], [], []
    seen = set()
    for edge in edges:
        to_id = edge.get("to_id", "")
        info = {
            "id": to_id,
            "relation": edge.get("relation", ""),
            "from": edge.get("from_id", ""),
            "confidence": edge.get("confidence", ""),
            "hop": edge.get("hop", 1),
        }
        meta = g.meta(to_id)
        if meta:
            info["name"] = meta.get("aliases", [None])[0] if meta.get("aliases") else to_id
            info["category"] = meta.get("attributes", {}).get("category", [""])[0] if meta.get("attributes", {}).get("category") else ""

        if to_id.startswith("plant_") and to_id not in seen:
            plants.append(info)
            seen.add(to_id)
        elif to_id.startswith("nakshatra_") and to_id not in seen:
            nakshatras.append(info)
            seen.add(to_id)
        elif to_id.startswith("raga_") and to_id not in seen:
            ragas.append(info)
            seen.add(to_id)

        paths.append({"from": edge.get("from_id", ""), "relation": edge.get("relation", ""),
                      "to": to_id, "hop": edge.get("hop", 1)})

    payload = {
        "entity": canonical,
        "plants": plants,
        "paths": paths[:50],
        "related_nakshatras": nakshatras,
        "related_ragas": ragas,
    }
    return Response(
        json.dumps(payload, default=_json_serial, ensure_ascii=False),
        mimetype="application/json",
    )


@plants_bp.route("/plants/guild_matrix")
def _plants_guild_matrix():
    try:
        import csv as _csv_gm
        gm_path = os.path.join(_here, "datasets", "plants", "guild_matrix.csv")
        if not os.path.exists(gm_path):
            return jsonify({"error": "guild_matrix.csv not found"})
        with open(gm_path, newline="", encoding="utf-8") as fp:
            rows = list(_csv_gm.DictReader(fp))
        layer = request.args.get("layer")
        ecoregion = request.args.get("ecoregion")
        n_fixer = request.args.get("nitrogen_fixer")
        if layer:
            rows = [r for r in rows if r.get("layer") == layer]
        if ecoregion:
            rows = [r for r in rows if ecoregion.lower() in (r.get("ecoregion") or "").lower()]
        if n_fixer:
            rows = [r for r in rows if (r.get("nitrogen_fixer") or "").lower() == n_fixer.lower()]
        return jsonify({"plants": rows, "count": len(rows)})
    except Exception as e:
        return jsonify({"error": str(e)})


@plants_bp.route("/plants/region")
def _plants_region():
    try:
        lat = float(request.args.get('lat', 0))
        lon = float(request.args.get('lon', 0))
        limit = int(request.args.get('limit', 20))
        radius_km = float(request.args.get('radius_km', 10))
        from npu_engine.field.region_engine import derive_regional_plants
        return jsonify(derive_regional_plants(lat, lon, radius_km, limit))
    except Exception as e:
        return jsonify({'plants': [], 'error': str(e)})


@plants_bp.route("/plants/<path:plant_key>")
def _plants_lookup(plant_key):
    payload = _lookup_plant(plant_key)
    if not payload:
        return Response(
            json.dumps({"error": f"plant not found: {plant_key}"}, ensure_ascii=False),
            mimetype="application/json",
            status=404,
        )
    return Response(
        json.dumps(payload, default=_json_serial, ensure_ascii=False),
        mimetype="application/json",
    )


# ── Land routes ──────────────────────────────────────

@plants_bp.route("/land")
def _land():
    from npu_engine.field.land_engine import derive_land_layout
    fs = field_state()
    layout = derive_land_layout(fs)
    layout["panchanga"] = fs.get("panchanga", {})
    return jsonify(layout)


@plants_bp.route("/land/plot", methods=["POST"])
def _land_plot():
    from npu_engine.field.land_engine import derive_land_layout
    data = request.get_json(force=True, silent=True) or {}
    plot = {"orientation_degrees": data.get("orientation", 0),
            "area_m2": data.get("area_m2", 0)}
    fs = field_state()
    layout = derive_land_layout(fs, plot=plot)
    layout["panchanga"] = fs.get("panchanga", {})
    return jsonify(layout)


@plants_bp.route("/land/layout")
def _land_layout():
    """GeoJSON vastu mandala projected at lat/lon."""
    from npu_engine.field.land_engine import derive_land_layout
    lat = float(request.args.get("lat", 0))
    lon = float(request.args.get("lon", 0))
    radius_m = float(request.args.get("radius_m", 50))
    fs = field_state()
    layout = derive_land_layout(fs)

    # Generate 9 pie-slice polygons
    zone_order = ["E", "NE", "N", "NW", "W", "SW", "S", "SE", "C"]
    zone_angles = {
        "E": (67.5, 112.5), "NE": (22.5, 67.5), "N": (-22.5, 22.5),
        "NW": (-67.5, -22.5), "W": (-112.5, -67.5), "SW": (-157.5, -112.5),
        "S": (157.5, 202.5), "SE": (112.5, 157.5), "C": (0, 360),
    }
    m_per_deg_lat = 111320.0
    m_per_deg_lon = 111320.0 * math.cos(math.radians(lat)) if lat else 111320.0

    features = []
    for zk in zone_order:
        zdata = layout.get("zones", {}).get(zk, {})
        if zk == "C":
            # Brahmasthana — small circle at center
            r_deg = (radius_m * 0.15) / m_per_deg_lat
            pts = []
            for i in range(17):
                a = math.radians(i * 360 / 16)
                pts.append([round(lon + r_deg * math.cos(a) * m_per_deg_lat / m_per_deg_lon, 7),
                            round(lat + r_deg * math.sin(a), 7)])
            pts.append(pts[0])
        else:
            a1, a2 = zone_angles[zk]
            pts = [[round(lon, 7), round(lat, 7)]]
            for i in range(9):
                a = math.radians(a1 + (a2 - a1) * i / 8)
                dx = radius_m * math.sin(a) / m_per_deg_lon
                dy = radius_m * math.cos(a) / m_per_deg_lat
                pts.append([round(lon + dx, 7), round(lat + dy, 7)])
            pts.append(pts[0])

        features.append({
            "type": "Feature",
            "properties": {
                "zone_id": zk,
                "deity": zdata.get("deity", ""),
                "element": zdata.get("element", ""),
                "land_use": zdata.get("land_use", []),
                "plants": zdata.get("recommended_plants", []),
                "structures": zdata.get("recommended_structures", []),
                "coherence": zdata.get("coherence", 0),
                "activity": zdata.get("activity", ""),
            },
            "geometry": {"type": "Polygon", "coordinates": [pts]}
        })

    p5 = fs.get("panchanga", {})
    return jsonify({
        "type": "FeatureCollection",
        "features": features,
        "properties": {
            "center": [lat, lon],
            "radius_m": radius_m,
            "field_emphasis": layout.get("current_field_emphasis", ""),
            "recommendations": layout.get("recommendations", []),
            "timing": layout.get("timing", {}),
            "panchanga": {
                "nakshatra": p5.get("nakshatra", ""),
                "tithi": p5.get("tithi", ""),
                "vara": p5.get("vara", ""),
            },
            "suggested_gate": "E",
            "suggested_pond": [lat + radius_m * 0.7 / m_per_deg_lat,
                               lon + radius_m * 0.7 / m_per_deg_lon],
            "suggested_hearth": [lat - radius_m * 0.5 / m_per_deg_lat,
                                 lon + radius_m * 0.5 / m_per_deg_lon],
        }
    })


@plants_bp.route("/land/mandala")
def _land_mandala():
    from npu_engine.field.land_engine import derive_permaculture_mandala
    lat = float(request.args.get("lat", 0))
    lon = float(request.args.get("lon", 0))
    radius_m = float(request.args.get("radius_m", 50))
    return jsonify(derive_permaculture_mandala(field_state(), lat, lon, radius_m))


@plants_bp.route("/land/mandala/recommend", methods=["POST"])
def _land_mandala_recommend():
    payload = request.get_json(silent=True) or {}
    return jsonify(_build_land_mandala_recommendation(payload))


# ── Plant field coherence routes ──────────────────────

@plants_bp.route("/plants/field")
def _plants_field():
    from npu_engine.engines.plant_engine import derive_plant_field
    return jsonify(derive_plant_field(field_state()))


@plants_bp.route("/plants/entity/<path:plant_id>")
def _plant_entity(plant_id):
    epath = os.path.join(_here, "datasets", "plants", "entities", plant_id + ".json")
    if os.path.exists(epath):
        return send_file(epath, mimetype="application/json")
    return jsonify({"error": "not found", "plant_id": plant_id}), 404


@plants_bp.route("/plants/schema")
def _plants_schema():
    return send_file(os.path.join(_here, "datasets", "schema", "entity_template.json"),
                     mimetype="application/json")
