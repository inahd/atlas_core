"""
region_engine.py — Multi-source regional plant lookup.

Merges iNaturalist observations, USDA PLANTS data, and PFAF database
into a ranked list of plants for a given location.

Sources:
    iNaturalist API — actually observed species at lat/lon (OBSERVED:INATURALIST)
    USDA PLANTS API — native status + growth habit (OBSERVED:USDA)
    PFAF sqlite     — edibility, medicinal, cultivation (OBSERVED:PFAF)

Pattern follows derive_*(): never raises, all keys guaranteed.
"""
import logging
import os
import re
import sqlite3

log = logging.getLogger(__name__)

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
_PFAF_DB = os.path.join(_ROOT, "datasets", "plants", "pfaf.sqlite")

# Lazy import requests — not available at module level in all contexts
_requests = None


def _get_requests():
    global _requests
    if _requests is None:
        try:
            import requests as _r
            _requests = _r
        except ImportError:
            _requests = False
    return _requests if _requests else None


# ══════════════════════════════════════════════════════════
# ECOREGION + HARDINESS
# ══════════════════════════════════════════════════════════

def _ecoregion_name(lat, lon):
    if lon < -115 and lat > 42:
        return "Pacific Northwest"
    if lon < -105 and lat < 38:
        return "Desert Southwest"
    if lon > -85 and lon < -75 and lat > 35 and lat < 45:
        return "Appalachian"
    if lon > -105 and lon < -90 and lat > 35 and lat < 50:
        return "Great Plains"
    if lat < 33 and lon > -97:
        return "Gulf Coast"
    if lon > -90 and lat > 35 and lat < 50:
        return "Eastern Woodlands"
    return "North America"


def _hardiness_zone(lat):
    if lat > 47:
        return "3-4"
    if lat > 43:
        return "4-5"
    if lat > 39:
        return "5-6"
    if lat > 35:
        return "6-7"
    if lat > 31:
        return "7-8"
    if lat > 27:
        return "8-9"
    return "9-11"


def _hardiness_range(lat):
    if lat > 47:
        return (3, 4)
    if lat > 43:
        return (4, 5)
    if lat > 39:
        return (5, 6)
    if lat > 35:
        return (6, 7)
    if lat > 31:
        return (7, 8)
    if lat > 27:
        return (8, 9)
    return (9, 11)


# ══════════════════════════════════════════════════════════
# iNATURALIST — species observed at location
# ══════════════════════════════════════════════════════════

INAT_API = "https://api.inaturalist.org/v1"


def _fetch_inaturalist(lat, lon, radius_km=10, limit=30):
    """Fetch plant species observed near lat/lon from iNaturalist."""
    req = _get_requests()
    if not req:
        return []
    try:
        r = req.get(
            f"{INAT_API}/observations/species_counts",
            params={
                "lat": lat,
                "lng": lon,
                "radius": radius_km,
                "iconic_taxa": "Plantae",
                "quality_grade": "research",
                "per_page": min(limit * 2, 50),
            },
            timeout=8,
        )
        if not r.ok:
            log.warning("iNat API returned %d", r.status_code)
            return []
        data = r.json()
        results = []
        for item in data.get("results", []):
            taxon = item.get("taxon", {})
            name = taxon.get("name", "")
            rank = taxon.get("rank", "")
            if not name or rank not in ("species", "subspecies", "variety"):
                continue
            results.append({
                "latin_name": name,
                "common_name": taxon.get("preferred_common_name", ""),
                "family": (taxon.get("ancestry", "").split("/")[-2:]
                           if taxon.get("ancestry") else [""])[0] if False else "",
                "observation_count": item.get("count", 0),
                "iconic_taxon": taxon.get("iconic_taxon_name", ""),
                "rank": rank,
                "inat_id": taxon.get("id"),
                "source": "iNaturalist",
                "attestation": "OBSERVED:INATURALIST",
            })
        log.info("iNat returned %d species for %.2f,%.2f r=%dkm",
                 len(results), lat, lon, radius_km)
        return results
    except Exception as e:
        log.warning("iNat fetch failed: %s", e)
        return []


# ══════════════════════════════════════════════════════════
# USDA PLANTS — native status + growth habit for individual species
# ══════════════════════════════════════════════════════════

USDA_API = "https://plantsservices.sc.egov.usda.gov/api"


def _usda_lookup(latin_name):
    """Look up a single species in USDA PLANTS by symbol guess."""
    req = _get_requests()
    if not req or not latin_name:
        return None
    # Generate USDA symbol from genus + species initials
    parts = latin_name.split()
    if len(parts) < 2:
        return None
    symbol = (parts[0][:2] + parts[1][:2]).upper()
    try:
        r = req.get(
            f"{USDA_API}/PlantProfile",
            params={"symbol": symbol},
            timeout=5,
        )
        if not r.ok:
            return None
        data = r.json()
        if not data.get("CommonName"):
            return None
        return {
            "usda_symbol": data.get("Symbol", symbol),
            "growth_habit": (data.get("GrowthHabits") or [""])[0] if data.get("GrowthHabits") else "",
            "duration": (data.get("Durations") or [""])[0] if data.get("Durations") else "",
            "native_status": "native" if any(
                ns.get("Status") == "N"
                for ns in (data.get("NativeStatuses") or [])
            ) else "introduced",
            "source": "USDA",
            "attestation": "OBSERVED:USDA",
        }
    except Exception:
        return None


def _enrich_with_usda(plants, max_lookups=8):
    """Enrich top N plants with USDA data. Slow — limited lookups."""
    req = _get_requests()
    if not req:
        return
    enriched = 0
    for p in plants:
        if enriched >= max_lookups:
            break
        latin = p.get("latin_name", "")
        if not latin:
            continue
        usda = _usda_lookup(latin)
        if usda:
            p["usda_symbol"] = usda.get("usda_symbol", "")
            p["growth_habit"] = p.get("growth_habit") or usda.get("growth_habit", "")
            p["duration"] = p.get("duration") or usda.get("duration", "")
            p["native_status"] = usda.get("native_status", "")
            if "USDA" not in p.get("sources", []):
                p.setdefault("sources", []).append("USDA")
            enriched += 1


# ══════════════════════════════════════════════════════════
# PFAF — edibility, medicinal, cultivation
# ══════════════════════════════════════════════════════════

_PFAF_REGION_KEYWORDS = {
    "Pacific Northwest": ["North America", "Western N. America", "Oregon", "Washington"],
    "Desert Southwest": ["North America", "Mexico", "Southwestern", "Arizona", "Texas"],
    "Great Plains": ["North America", "Great Plains", "Central N. America"],
    "Gulf Coast": ["North America", "Southeastern", "S.E. United States", "Florida"],
    "Eastern Woodlands": ["North America", "Eastern N. America", "E. United States"],
    "Appalachian": ["North America", "Eastern N. America", "Appalachian"],
}


def _fetch_pfaf(lat, lon, limit=30):
    """Query PFAF sqlite for regional plants."""
    if not os.path.exists(_PFAF_DB):
        return []
    eco = _ecoregion_name(lat, lon)
    keywords = _PFAF_REGION_KEYWORDS.get(eco, ["North America"])
    try:
        conn = sqlite3.connect(_PFAF_DB)
        conn.row_factory = sqlite3.Row
        clauses = " OR ".join(["found_in LIKE ? OR range LIKE ?" for _ in keywords])
        params = []
        for kw in keywords:
            params += [f"%{kw}%", f"%{kw}%"]
        params.append(limit * 2)
        rows = conn.execute(
            f"SELECT latin_name, common_name, family, habit, height, "
            f"edibility_rating, medicinal_rating, other_uses_rating, "
            f"range, found_in, edible_uses, medicinal_uses, known_hazards, summary "
            f"FROM plants WHERE ({clauses}) "
            f"ORDER BY edibility_rating DESC, medicinal_rating DESC LIMIT ?",
            params,
        ).fetchall()
        conn.close()
        results = []
        hz = _hardiness_range(lat)
        for r in rows:
            # Hardiness filter
            h_str = ""  # PFAF schema doesn't have hardiness in this query
            p = dict(r)
            p["source"] = "PFAF"
            p["attestation"] = "OBSERVED:PFAF"
            results.append(p)
        return results[:limit]
    except Exception as e:
        log.warning("PFAF query failed: %s", e)
        return []


# ══════════════════════════════════════════════════════════
# MERGE + RANK
# ══════════════════════════════════════════════════════════

def _merge_sources(inat, pfaf):
    """Merge iNaturalist and PFAF by latin_name, then genus-level fuzzy match."""
    merged = {}

    # iNat plants first — actually observed nearby
    for p in inat:
        key = p["latin_name"].lower()
        merged[key] = {
            **p,
            "score": 1.0,
            "sources": ["iNaturalist"],
        }

    # Build PFAF genus index for fuzzy matching
    pfaf_by_genus = {}
    for p in pfaf:
        latin = (p.get("latin_name") or "").strip()
        if not latin:
            continue
        genus = latin.split()[0].lower() if latin else ""
        if genus:
            pfaf_by_genus.setdefault(genus, []).append(p)

    # PFAF exact match pass
    for p in pfaf:
        key = (p.get("latin_name") or "").lower()
        if not key:
            continue
        if key in merged:
            merged[key]["score"] += 0.8
            merged[key]["sources"].append("PFAF")
            for k, v in p.items():
                if k not in merged[key] or not merged[key][k]:
                    merged[key][k] = v
        else:
            merged[key] = {
                **p,
                "score": 0.6,
                "sources": ["PFAF"],
            }

    # Genus-level fuzzy match: iNat plants not yet matched to PFAF
    for key, plant in list(merged.items()):
        if "PFAF" in plant.get("sources", []):
            continue  # already has exact PFAF match
        if "iNaturalist" not in plant.get("sources", []):
            continue  # only fuzzy-match iNat plants
        latin = plant.get("latin_name", "")
        genus = latin.split()[0].lower() if latin else ""
        if not genus:
            continue
        genus_matches = pfaf_by_genus.get(genus, [])
        if not genus_matches:
            continue
        # Pick the best PFAF match in same genus (highest edibility + medicinal)
        best = max(genus_matches, key=lambda p: int(p.get("edibility_rating") or 0) + int(p.get("medicinal_rating") or 0))
        # Inherit PFAF data with lower confidence
        for k in ("edibility_rating", "medicinal_rating", "other_uses_rating",
                   "family", "habit", "edible_uses", "medicinal_uses", "known_hazards"):
            if k not in plant or not plant[k]:
                plant[k] = best.get(k, "")
        plant["score"] += 0.4  # less than exact match (0.8)
        plant["sources"].append("PFAF")
        plant["pfaf_genus_match"] = best.get("latin_name", "")
        plant["attestation"] = "OBSERVED:INATURALIST+PFAF:genus_match"

    return list(merged.values())


def _rank(plants, lat, lon):
    """Score and sort plants by permaculture relevance."""
    for p in plants:
        s = p.get("score", 0)
        ed = int(p.get("edibility_rating") or 0)
        med = int(p.get("medicinal_rating") or 0)
        if ed >= 3:
            s += 0.4
        if med >= 3:
            s += 0.3
        if p.get("native_status") == "native":
            s += 0.2
        if "iNaturalist" in p.get("sources", []):
            s += 0.2  # actually observed nearby
        p["score"] = round(s, 2)
    plants.sort(key=lambda x: x.get("score", 0), reverse=True)
    return plants


# ══════════════════════════════════════════════════════════
# PUBLIC API
# ══════════════════════════════════════════════════════════

def derive_regional_plants(lat, lon, radius_km=10, limit=30):
    """Multi-source regional plant lookup. Never raises.

    Merges iNaturalist (observed nearby), PFAF (edibility/medicinal),
    and enriches top results with USDA native status.

    Returns dict with all keys guaranteed.
    """
    try:
        inat = _fetch_inaturalist(lat, lon, radius_km, limit)
        pfaf = _fetch_pfaf(lat, lon, limit)
        merged = _merge_sources(inat, pfaf)
        ranked = _rank(merged, lat, lon)

        # Enrich top results with USDA (slow — max 8 lookups)
        _enrich_with_usda(ranked[:8], max_lookups=8)

        # Trim to limit
        plants = ranked[:limit]

        return {
            "plants": plants,
            "ecoregion": _ecoregion_name(lat, lon),
            "hardiness_zone": _hardiness_zone(lat),
            "inat_count": len(inat),
            "pfaf_count": len(pfaf),
            "total_merged": len(merged),
            "count": len(plants),
            "sources": ["iNaturalist", "PFAF", "USDA"],
            "attestation": "SYNTHESIS",
        }
    except Exception as e:
        log.error("derive_regional_plants failed: %s", e)
        return {
            "plants": [],
            "ecoregion": _ecoregion_name(lat, lon),
            "hardiness_zone": _hardiness_zone(lat),
            "inat_count": 0,
            "pfaf_count": 0,
            "total_merged": 0,
            "count": 0,
            "sources": [],
            "error": str(e),
            "attestation": "SYNTHESIS",
        }
