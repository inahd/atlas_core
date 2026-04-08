"""
site_engine.py — Terrain intelligence spine for lila-streams.

Fetches elevation from USGS 3DEP, computes slope/aspect/hydrology,
generates swale/pond candidates and suitability scores.

Pattern: derive_*() — never raises, all keys guaranteed.

Elevation source: USGS 3DEP (https://epqs.nationalmap.gov/v1/json)
  Free, no API key, 1m resolution for USA.
  Fallback: flat terrain assumption if fetch fails.
"""
import json
import logging
import math
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

log = logging.getLogger(__name__)

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
_CACHE_DIR = os.path.join(_ROOT, "instance", "cache", "terrain")

USGS_URL = "https://epqs.nationalmap.gov/v1/json"

# Lazy imports
_np = None
_requests = None


def _get_np():
    global _np
    if _np is None:
        try:
            import numpy
            _np = numpy
        except ImportError:
            _np = False
    return _np if _np else None


def _get_requests():
    global _requests
    if _requests is None:
        try:
            import requests
            _requests = requests
        except ImportError:
            _requests = False
    return _requests if _requests else None


# ══════════════════════════════════════════════════════════
# ELEVATION FETCH
# ══════════════════════════════════════════════════════════

def _fetch_elevation_point(lat, lon):
    """Fetch single point elevation from USGS 3DEP."""
    req = _get_requests()
    if not req:
        return None
    try:
        r = req.get(USGS_URL, params={
            "x": lon, "y": lat, "wkid": 4326,
            "units": "Meters", "includeDate": "false",
        }, timeout=8)
        if r.ok:
            return float(r.json().get("value", 0))
    except Exception:
        pass
    return None


def _fetch_elevation_grid(lat, lon, radius_m, grid_size=7):
    """Fetch NxN elevation grid centered on lat/lon. Uses concurrent requests."""
    req = _get_requests()
    np = _get_np()
    if not req or not np:
        return None, 0

    m_per_deg_lat = 111320.0
    m_per_deg_lon = 111320.0 * math.cos(math.radians(lat))
    half = radius_m
    cell_size_m = (2 * half) / max(grid_size - 1, 1)

    points = []
    for r in range(grid_size):
        for c in range(grid_size):
            py = lat + (half - r * cell_size_m) / m_per_deg_lat
            px = lon + (-half + c * cell_size_m) / m_per_deg_lon
            points.append((r, c, py, px))

    grid = np.zeros((grid_size, grid_size))

    def fetch_one(pt):
        r, c, py, px = pt
        try:
            resp = req.get(USGS_URL, params={
                "x": px, "y": py, "wkid": 4326,
                "units": "Meters", "includeDate": "false",
            }, timeout=8)
            if resp.ok:
                return r, c, float(resp.json().get("value", 0))
        except Exception:
            pass
        return r, c, None

    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = [pool.submit(fetch_one, pt) for pt in points]
        for f in as_completed(futures):
            r, c, val = f.result()
            if val is not None:
                grid[r, c] = val

    # Fill any zeros with neighbor mean
    for r in range(grid_size):
        for c in range(grid_size):
            if grid[r, c] == 0:
                neighbors = []
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < grid_size and 0 <= nc < grid_size and grid[nr, nc] != 0:
                            neighbors.append(grid[nr, nc])
                if neighbors:
                    grid[r, c] = sum(neighbors) / len(neighbors)

    return grid, cell_size_m


# ══════════════════════════════════════════════════════════
# CACHE
# ══════════════════════════════════════════════════════════

def _cache_key(lat, lon, radius_m):
    return f"{lat:.4f}_{lon:.4f}_{int(radius_m)}"


def _load_cache(lat, lon, radius_m):
    key = _cache_key(lat, lon, radius_m)
    path = os.path.join(_CACHE_DIR, key + ".json")
    try:
        if os.path.exists(path):
            with open(path) as f:
                data = json.load(f)
            return data
    except Exception:
        pass
    return None


def _save_cache(lat, lon, radius_m, data):
    try:
        os.makedirs(_CACHE_DIR, exist_ok=True)
        key = _cache_key(lat, lon, radius_m)
        path = os.path.join(_CACHE_DIR, key + ".json")
        with open(path, "w") as f:
            json.dump(data, f)
    except Exception:
        pass


# ══════════════════════════════════════════════════════════
# TERRAIN ANALYSIS
# ══════════════════════════════════════════════════════════

def _compute_slope(grid, cell_size_m):
    """Horn's method slope in percent."""
    np = _get_np()
    if np is None or grid is None:
        return None
    g = np.array(grid)
    rows, cols = g.shape
    slope = np.zeros_like(g)
    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            dz_dx = ((g[r-1, c+1] + 2*g[r, c+1] + g[r+1, c+1]) -
                     (g[r-1, c-1] + 2*g[r, c-1] + g[r+1, c-1])) / (8 * cell_size_m)
            dz_dy = ((g[r+1, c-1] + 2*g[r+1, c] + g[r+1, c+1]) -
                     (g[r-1, c-1] + 2*g[r-1, c] + g[r-1, c+1])) / (8 * cell_size_m)
            slope[r, c] = math.sqrt(dz_dx**2 + dz_dy**2) * 100
    return slope


def _compute_aspect(grid, cell_size_m):
    """Aspect in degrees (0=N, 90=E, 180=S, 270=W)."""
    np = _get_np()
    if np is None or grid is None:
        return None
    g = np.array(grid)
    rows, cols = g.shape
    aspect = np.full_like(g, -1.0)
    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            dz_dx = ((g[r-1, c+1] + 2*g[r, c+1] + g[r+1, c+1]) -
                     (g[r-1, c-1] + 2*g[r, c-1] + g[r+1, c-1])) / (8 * cell_size_m)
            dz_dy = ((g[r+1, c-1] + 2*g[r+1, c] + g[r+1, c+1]) -
                     (g[r-1, c-1] + 2*g[r-1, c] + g[r-1, c+1])) / (8 * cell_size_m)
            a = math.degrees(math.atan2(dz_dy, -dz_dx))
            aspect[r, c] = (a + 360) % 360
    return aspect


def _compute_flow_direction(grid):
    """D8 flow direction. Returns grid of direction codes."""
    np = _get_np()
    if np is None or grid is None:
        return None
    g = np.array(grid)
    rows, cols = g.shape
    dirs = np.zeros((rows, cols), dtype=int)
    # D8 neighbors: E=1, SE=2, S=4, SW=8, W=16, NW=32, N=64, NE=128
    dr = [0, 1, 1, 1, 0, -1, -1, -1]
    dc = [1, 1, 0, -1, -1, -1, 0, 1]
    codes = [1, 2, 4, 8, 16, 32, 64, 128]
    dist = [1, 1.414, 1, 1.414, 1, 1.414, 1, 1.414]
    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            max_drop = 0
            max_dir = 0
            for i in range(8):
                nr, nc = r + dr[i], c + dc[i]
                drop = (g[r, c] - g[nr, nc]) / dist[i]
                if drop > max_drop:
                    max_drop = drop
                    max_dir = codes[i]
            dirs[r, c] = max_dir
    return dirs


def _compute_flow_accumulation(flow_dir):
    """Simple flow accumulation from D8 directions."""
    np = _get_np()
    if np is None or flow_dir is None:
        return None
    rows, cols = flow_dir.shape
    acc = np.ones((rows, cols))
    # Iterative propagation (simplified — not full recursive)
    for _ in range(max(rows, cols)):
        changed = False
        for r in range(1, rows - 1):
            for c in range(1, cols - 1):
                # Check all neighbors that flow INTO this cell
                dr = [0, 1, 1, 1, 0, -1, -1, -1]
                dc = [1, 1, 0, -1, -1, -1, 0, 1]
                inflow_codes = [16, 32, 64, 128, 1, 2, 4, 8]  # opposite directions
                total = 1.0
                for i in range(8):
                    nr, nc = r + dr[i], c + dc[i]
                    if 0 <= nr < rows and 0 <= nc < cols:
                        if flow_dir[nr, nc] == inflow_codes[i]:
                            total += acc[nr, nc]
                if total != acc[r, c]:
                    acc[r, c] = total
                    changed = True
        if not changed:
            break
    return acc


def _terrain_class(slope_pct):
    if slope_pct < 2:
        return "flat"
    if slope_pct < 5:
        return "gentle"
    if slope_pct < 15:
        return "moderate"
    return "steep"


def _find_swale_candidates(lat, lon, radius_m, elev_grid, slope_grid, flow_acc, cell_size_m):
    """Find contour-following swale positions."""
    np = _get_np()
    if np is None or elev_grid is None:
        return []
    rows, cols = elev_grid.shape
    m_lat = 111320.0
    m_lon = 111320.0 * math.cos(math.radians(lat))
    candidates = []

    for r in range(2, rows - 2):
        for c in range(2, cols - 2):
            sl = slope_grid[r, c] if slope_grid is not None else 0
            fa = flow_acc[r, c] if flow_acc is not None else 0
            # Good swale: slope 1-8%, moderate flow accumulation
            if 1 < sl < 8 and fa > 3:
                cy = lat + (radius_m - r * cell_size_m) / m_lat
                cx = lon + (-radius_m + c * cell_size_m) / m_lon
                # Extend contour line E-W through this point
                el = elev_grid[r, c]
                line = [[cy, cx - radius_m * 0.3 / m_lon], [cy, cx + radius_m * 0.3 / m_lon]]
                quality = "good" if sl < 5 and fa > 5 else "marginal" if fa > 2 else "poor"
                zone = _vastu_zone_for_point(cy, cx, lat, lon)
                candidates.append({
                    "geojson": {"type": "LineString", "coordinates": [[p[1], p[0]] for p in line]},
                    "elevation_m": round(el, 1),
                    "slope_pct": round(sl, 1),
                    "catchment_area_m2": round(fa * cell_size_m * cell_size_m, 0),
                    "vastu_zone": zone,
                    "quality": quality,
                })
    # Deduplicate: keep best per ~20m vertical band
    candidates.sort(key=lambda x: -x["catchment_area_m2"])
    return candidates[:5]


def _find_pond_candidates(lat, lon, radius_m, elev_grid, flow_acc, cell_size_m):
    """Find natural depression / high-accumulation pond sites."""
    np = _get_np()
    if np is None or elev_grid is None:
        return []
    rows, cols = elev_grid.shape
    m_lat = 111320.0
    m_lon = 111320.0 * math.cos(math.radians(lat))
    candidates = []

    if flow_acc is None:
        return []

    # Find top accumulation points
    flat = flow_acc.flatten()
    threshold = max(flat.mean() + flat.std(), 5)

    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            if flow_acc[r, c] >= threshold:
                cy = lat + (radius_m - r * cell_size_m) / m_lat
                cx = lon + (-radius_m + c * cell_size_m) / m_lon
                zone = _vastu_zone_for_point(cy, cx, lat, lon)
                ca = flow_acc[r, c] * cell_size_m * cell_size_m
                quality = "good" if zone in ("NE", "N") else "marginal"
                candidates.append({
                    "lat": round(cy, 6),
                    "lon": round(cx, 6),
                    "catchment_area_m2": round(ca, 0),
                    "vastu_zone": zone,
                    "quality": quality,
                })
    candidates.sort(key=lambda x: -x["catchment_area_m2"])
    return candidates[:3]


def _vastu_zone_for_point(py, px, center_lat, center_lon):
    """Determine vastu zone for a point relative to center."""
    dy = py - center_lat
    dx = px - center_lon
    angle = math.degrees(math.atan2(dx, dy)) % 360
    if angle < 22.5 or angle >= 337.5:
        return "N"
    if angle < 67.5:
        return "NE"
    if angle < 112.5:
        return "E"
    if angle < 157.5:
        return "SE"
    if angle < 202.5:
        return "S"
    if angle < 247.5:
        return "SW"
    if angle < 292.5:
        return "W"
    return "NW"


# ══════════════════════════════════════════════════════════
# SOLAR
# ══════════════════════════════════════════════════════════

def _compute_solar(lat, lon, house_lat=None, house_lon=None):
    hemisphere = "N" if lat >= 0 else "S"
    abs_lat = abs(lat)
    summer = min(90, 90 - abs_lat + 23.5)
    winter = max(0, 90 - abs_lat - 23.5)

    aspect_quality = {}
    if hemisphere == "N":
        aspect_quality = {"N": "poor", "NE": "marginal", "E": "good", "SE": "excellent",
                          "S": "excellent", "SW": "good", "W": "marginal", "NW": "poor"}
        optimal = "S"
    else:
        aspect_quality = {"N": "excellent", "NE": "good", "E": "good", "SE": "marginal",
                          "S": "poor", "SW": "marginal", "W": "good", "NW": "good"}
        optimal = "N"

    house_shadow_radius = 0
    house_shadow_bearing = ""
    if house_lat is not None and winter > 0:
        house_h = 5.0  # estimate
        house_shadow_radius = round(house_h / math.tan(math.radians(winter)), 1)
        house_shadow_bearing = "N" if hemisphere == "N" else "S"

    frost_risk = abs_lat > 35

    return {
        "latitude": lat,
        "hemisphere": hemisphere,
        "sun_angle_summer_solstice": round(summer, 1),
        "sun_angle_winter_solstice": round(winter, 1),
        "optimal_food_forest_aspect": optimal,
        "aspect_quality": aspect_quality,
        "house_shadow_radius_m": house_shadow_radius,
        "house_shadow_bearing": house_shadow_bearing,
        "frost_pocket_risk": frost_risk,
    }


# ══════════════════════════════════════════════════════════
# VASTU ZONES
# ══════════════════════════════════════════════════════════

ZONE_SUITABILITY = {
    "C":  {"food_forest": 0.9, "annual": 0.4, "sacred": 0.8, "pond": 0.2, "windbreak": 0.1, "pasture": 0.2},
    "NE": {"food_forest": 0.6, "annual": 0.3, "sacred": 1.0, "pond": 0.9, "windbreak": 0.2, "pasture": 0.1},
    "E":  {"food_forest": 0.7, "annual": 0.9, "sacred": 0.4, "pond": 0.3, "windbreak": 0.2, "pasture": 0.4},
    "SE": {"food_forest": 0.6, "annual": 0.8, "sacred": 0.3, "pond": 0.2, "windbreak": 0.3, "pasture": 0.5},
    "S":  {"food_forest": 0.5, "annual": 0.5, "sacred": 0.2, "pond": 0.2, "windbreak": 0.9, "pasture": 0.7},
    "SW": {"food_forest": 0.4, "annual": 0.3, "sacred": 0.2, "pond": 0.3, "windbreak": 0.8, "pasture": 0.6},
    "W":  {"food_forest": 0.5, "annual": 0.4, "sacred": 0.4, "pond": 0.6, "windbreak": 0.5, "pasture": 0.5},
    "NW": {"food_forest": 0.4, "annual": 0.3, "sacred": 0.3, "pond": 0.4, "windbreak": 0.7, "pasture": 0.6},
    "N":  {"food_forest": 0.3, "annual": 0.2, "sacred": 0.5, "pond": 0.8, "windbreak": 0.6, "pasture": 0.4},
}


def _compute_suitability(terrain, solar, lat, lon, radius_m, house_lat=None, house_lon=None):
    """Score suitability per use type per vastu zone."""
    zones = ["C", "NE", "E", "SE", "S", "SW", "W", "NW", "N"]
    m_lat = 111320.0
    m_lon = 111320.0 * math.cos(math.radians(lat))
    result = {}

    for use in ("food_forest", "annual", "pond", "windbreak", "sacred", "pasture"):
        best_zone = max(zones, key=lambda z: ZONE_SUITABILITY.get(z, {}).get(use, 0))
        best_score = ZONE_SUITABILITY.get(best_zone, {}).get(use, 0)

        # Terrain adjustment
        slope = terrain.get("slope_pct", 0)
        if use in ("food_forest", "annual", "pond") and slope > 10:
            best_score *= 0.5
        if use == "windbreak" and slope < 1:
            best_score *= 0.8

        # Solar adjustment for food production
        if use in ("food_forest", "annual"):
            aq = solar.get("aspect_quality", {}).get(best_zone, "marginal")
            if aq == "excellent":
                best_score = min(1, best_score + 0.1)
            elif aq == "poor":
                best_score *= 0.7

        # Zone center coordinates
        offsets = {"C": (0, 0), "NE": (0.5, 0.5), "E": (0, 0.6), "SE": (-0.5, 0.5),
                   "S": (-0.6, 0), "SW": (-0.5, -0.5), "W": (0, -0.6), "NW": (0.5, -0.5), "N": (0.6, 0)}
        off = offsets.get(best_zone, (0, 0))
        blat = lat + off[0] * radius_m / m_lat
        blon = lon + off[1] * radius_m / m_lon

        result[use] = {
            "best_zone": best_zone,
            "score": round(best_score, 2),
            "lat": round(blat, 6),
            "lon": round(blon, 6),
        }
    return result


# ══════════════════════════════════════════════════════════
# RECOMMENDATIONS
# ══════════════════════════════════════════════════════════

def _generate_recommendations(suitability, hydrology, solar, terrain):
    recs = []
    priority = 1

    # Water first
    ponds = hydrology.get("pond_candidates", [])
    if ponds:
        p = ponds[0]
        recs.append({
            "priority": priority, "element": "pond",
            "location": {"lat": p["lat"], "lon": p["lon"]},
            "vastu_zone": p["vastu_zone"],
            "rationale": f"Natural catchment {p['catchment_area_m2']:.0f}m\u00b2 \u2014 {p['quality']} site",
            "terrain_fit": f"Flow accumulation peak in {p['vastu_zone']} zone",
        })
        priority += 1

    swales = hydrology.get("swale_candidates", [])
    for s in swales[:2]:
        recs.append({
            "priority": priority, "element": "swale",
            "location": {"lat": s["geojson"]["coordinates"][0][1], "lon": s["geojson"]["coordinates"][0][0]},
            "vastu_zone": s["vastu_zone"],
            "rationale": f"Slope {s['slope_pct']}% \xb7 {s['quality']} \xb7 {s['elevation_m']}m",
            "terrain_fit": f"Contour-following at {s['slope_pct']}% in {s['vastu_zone']}",
        })
        priority += 1

    # Food forest
    ff = suitability.get("food_forest", {})
    if ff.get("score", 0) > 0.5:
        recs.append({
            "priority": priority, "element": "food_forest",
            "location": {"lat": ff["lat"], "lon": ff["lon"]},
            "vastu_zone": ff["best_zone"],
            "rationale": f"Score {ff['score']} \xb7 {solar.get('optimal_food_forest_aspect', 'S')}-facing preferred",
            "terrain_fit": f"{terrain.get('terrain_class', 'flat')} terrain in {ff['best_zone']}",
        })
        priority += 1

    # Annual garden
    ag = suitability.get("annual", {})
    if ag.get("score", 0) > 0.5:
        recs.append({
            "priority": priority, "element": "annual_garden",
            "location": {"lat": ag["lat"], "lon": ag["lon"]},
            "vastu_zone": ag["best_zone"],
            "rationale": f"Full sun zone \xb7 score {ag['score']}",
            "terrain_fit": f"Near access in {ag['best_zone']}",
        })
        priority += 1

    # Windbreak
    wb = suitability.get("windbreak", {})
    if wb.get("score", 0) > 0.5:
        recs.append({
            "priority": priority, "element": "windbreak",
            "location": {"lat": wb["lat"], "lon": wb["lon"]},
            "vastu_zone": wb["best_zone"],
            "rationale": f"S/SW boundary protection \xb7 score {wb['score']}",
            "terrain_fit": f"Exposed {wb['best_zone']} boundary",
        })

    return recs


# ══════════════════════════════════════════════════════════
# ECOREGION + HARDINESS (shared with region_engine)
# ══════════════════════════════════════════════════════════

def _ecoregion(lat, lon):
    if lon < -115 and lat > 42:
        return "Pacific Northwest"
    if lon < -105 and lat < 38:
        return "Desert Southwest"
    if lon > -105 and lon < -90 and lat > 35:
        return "Great Plains"
    if lat < 33 and lon > -97:
        return "Gulf Coast"
    if lon > -90 and lat > 35:
        return "Eastern Woodlands"
    return "North America"


def _hardiness(lat):
    if lat > 47: return "3-4"
    if lat > 43: return "4-5"
    if lat > 39: return "5-6"
    if lat > 35: return "6-7"
    if lat > 31: return "7-8"
    if lat > 27: return "8-9"
    return "9-11"


def _scale_label(radius_m):
    if radius_m <= 15: return "kitchen"
    if radius_m <= 50: return "garden"
    if radius_m <= 200: return "farm"
    return "landscape"


# ══════════════════════════════════════════════════════════
# PUBLIC API
# ══════════════════════════════════════════════════════════

def derive_site_state(lat, lon, radius_m=100,
                      house_lat=None, house_lon=None,
                      boundary=None, field_state=None):
    """Complete site terrain intelligence. Never raises.

    Fetches elevation from USGS 3DEP, computes slope/aspect/hydrology,
    scores suitability per land use type, generates prioritized
    design recommendations.

    Returns dict with all keys guaranteed present.
    """
    np = _get_np()

    # Defaults for error/offline case
    _empty = {
        "center": {"lat": lat, "lon": lon},
        "radius_m": radius_m,
        "hemisphere": "N" if lat >= 0 else "S",
        "terrain": {"elevation_m": 0, "slope_pct": 0, "aspect_degrees": 0,
                     "relief_m": 0, "terrain_class": "flat", "contours": [],
                     "ridges": [], "valleys": []},
        "hydrology": {"swale_candidates": [], "pond_candidates": [],
                       "overflow_paths": [], "high_water_table_risk": lat < 32 or False},
        "solar": _compute_solar(lat, lon, house_lat, house_lon),
        "vastu": {"zone_suitability": ZONE_SUITABILITY},
        "suitability": {},
        "constraints": {},
        "design_recommendations": [],
        "site_brief": {
            "area_m2": round(math.pi * radius_m ** 2, 0),
            "area_ha": round(math.pi * radius_m ** 2 / 10000, 2),
            "ecoregion": _ecoregion(lat, lon),
            "hardiness_zone": _hardiness(lat),
            "terrain_class": "unknown",
            "design_scale": _scale_label(radius_m),
        },
        "elevation_source": "none",
        "cached": False,
        "attestation": "SYNTHESIS",
        "error": None,
    }

    try:
        # Check cache
        cached = _load_cache(lat, lon, radius_m)
        if cached:
            cached["cached"] = True
            return cached

        # Grid size: smaller for small radius, bigger for large
        grid_size = min(9, max(5, int(radius_m / 20)))

        # Fetch elevation grid
        elev_grid, cell_size_m = _fetch_elevation_grid(lat, lon, radius_m, grid_size)

        if elev_grid is None or not np:
            _empty["error"] = "elevation fetch failed or numpy unavailable"
            return _empty

        center_elev = float(elev_grid[grid_size // 2, grid_size // 2])
        relief = float(elev_grid.max() - elev_grid.min())

        # Compute terrain derivatives
        slope_grid = _compute_slope(elev_grid, cell_size_m)
        aspect_grid = _compute_aspect(elev_grid, cell_size_m)
        flow_dir = _compute_flow_direction(elev_grid)
        flow_acc = _compute_flow_accumulation(flow_dir)

        avg_slope = float(slope_grid[1:-1, 1:-1].mean()) if slope_grid is not None else 0
        dominant_aspect = float(aspect_grid[grid_size // 2, grid_size // 2]) if aspect_grid is not None else 0

        # Hydrology
        swale_cands = _find_swale_candidates(lat, lon, radius_m, elev_grid, slope_grid, flow_acc, cell_size_m)
        pond_cands = _find_pond_candidates(lat, lon, radius_m, elev_grid, flow_acc, cell_size_m)

        terrain = {
            "elevation_m": round(center_elev, 1),
            "slope_pct": round(avg_slope, 1),
            "aspect_degrees": round(dominant_aspect, 0),
            "relief_m": round(relief, 1),
            "terrain_class": _terrain_class(avg_slope),
            "grid_size": grid_size,
            "cell_size_m": round(cell_size_m, 1),
            "elevation_grid": elev_grid.tolist(),
            "contours": [],
            "ridges": [],
            "valleys": [],
        }

        hydrology = {
            "swale_candidates": swale_cands,
            "pond_candidates": pond_cands,
            "overflow_paths": [],
            "high_water_table_risk": lat < 32 or center_elev < 10,
        }

        solar = _compute_solar(lat, lon, house_lat, house_lon)
        suitability = _compute_suitability(terrain, solar, lat, lon, radius_m, house_lat, house_lon)
        recommendations = _generate_recommendations(suitability, hydrology, solar, terrain)

        result = {
            "center": {"lat": lat, "lon": lon},
            "radius_m": radius_m,
            "hemisphere": "N" if lat >= 0 else "S",
            "terrain": terrain,
            "hydrology": hydrology,
            "solar": solar,
            "vastu": {"zone_suitability": ZONE_SUITABILITY},
            "suitability": suitability,
            "constraints": {
                "steep_slope_mask": (slope_grid > 15).tolist() if slope_grid is not None else [],
            },
            "design_recommendations": recommendations,
            "site_brief": {
                "area_m2": round(math.pi * radius_m ** 2, 0),
                "area_ha": round(math.pi * radius_m ** 2 / 10000, 2),
                "ecoregion": _ecoregion(lat, lon),
                "hardiness_zone": _hardiness(lat),
                "terrain_class": _terrain_class(avg_slope),
                "design_scale": _scale_label(radius_m),
                "key_opportunities": [r["rationale"] for r in recommendations[:3]],
                "key_constraints": ["high water table risk"] if hydrology["high_water_table_risk"] else [],
            },
            "elevation_source": "USGS 3DEP",
            "cached": False,
            "attestation": "OBSERVED:USGS",
            "error": None,
        }

        _save_cache(lat, lon, radius_m, result)
        return result

    except Exception as e:
        log.error("derive_site_state failed: %s", e)
        _empty["error"] = str(e)
        return _empty
