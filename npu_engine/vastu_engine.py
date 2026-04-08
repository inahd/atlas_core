"""
vastu_engine.py — Deterministic S4 spatial geometry derived from S3 time-state.

Vāstu is a 2D slice of the toroidal field: the 8×8 Manduka pada grid
activated by current pañcāṅga and entity coherence.

S3 (time) drives S4 (space):
  - tithi arc_phase → grid orientation + intensity
  - nakṣatra/pada  → cell activation seed
  - element/guṇa   → zone weights
  - entity coherence → cell occupancy (highest → Brahmasthāna)
  - graph relations → adjacency preference

This module computes state only. It does not render.
Consumers (igpu, atlas, om) read the result; they never recompute it.

Grid reference: Manduka 64-pada (8×8), canonical Vāstu Śāstra layout.
Perimeter deities from Bṛhat Saṃhitā ch. 53; inner deities from Mayamata.
"""

from typing import Any, Dict, List, Tuple
import math

# ══════════════════════════════════════════════════════════
# CANONICAL 8×8 MANDUKA GRID — 64 PADAS
# ══════════════════════════════════════════════════════════

# Zone classification for each cell.
# 8×8 grid, row 0 = South, row 7 = North, col 0 = West, col 7 = East.
# Brahmasthāna = central 2×2 (rows 3-4, cols 3-4).
_ZONE_MAP = [
    ["SW", "S",  "S",  "S",  "S",  "S",  "S",  "SE"],
    ["W",  "SW", "S",  "S",  "S",  "S",  "SE", "E" ],
    ["W",  "W",  "SW", "S",  "S",  "SE", "E",  "E" ],
    ["W",  "W",  "W",  "Center", "Center", "E",  "E",  "E" ],
    ["W",  "W",  "W",  "Center", "Center", "E",  "E",  "E" ],
    ["W",  "W",  "NW", "N",  "N",  "NE", "E",  "E" ],
    ["W",  "NW", "N",  "N",  "N",  "N",  "NE", "E" ],
    ["NW", "N",  "N",  "N",  "N",  "N",  "N",  "NE"],
]

# Canonical perimeter + inner deities for each pada.
# 32 perimeter deities (Bṛhat Saṃhitā) + Brahmasthāna deities.
# Row-major, [row][col]. Where no canonical name exists, zone deity is used.
_DEITY_MAP = [
    ["Nirṛti",  "Mṛga",    "Pitṛ",    "Dauvarika","Sugrīva", "Puṣpadanta","Agni(var)","Agni"   ],
    ["Aśeṣa",   "Pāpayakṣmā","Rudra",  "Rudrajit", "Āpa",    "Āpavasta",  "Savitṛ",  "Savitar" ],
    ["Roga",     "Nāga",    "Mukhya",  "Bhallāṭa", "Soma",   "Aditi",     "Diti",    "Sūrya"  ],
    ["Śoṣa",    "Asura",   "Varuṇa",  "Brahmā",   "Brahmā", "Mitra",     "Indra",   "Jayanta" ],
    ["Dauvarīka","Sugr.",   "Puṣpad.", "Brahmā",   "Brahmā", "Vivasm.",   "Indra",   "Mahendra"],
    ["Piśāca",   "Pilipañj.","Kubera", "Marīci",   "Vivasvat","Savitṛ",   "Āpavats.","Āditya"  ],
    ["Bhṛṅga",  "Gand.",   "Yama",    "Gṛharakṣ.","Viśvadeva","Puṣan",   "Bṛhaspati","Aṣṭaha."],
    ["Vāyu",    "Mukhya",  "Bhr̥śa",   "Antarikṣa","Aryaman", "Savitṛ",   "Āditya",  "Īśāna"  ],
]

# Element affinity per zone (from vastu_zones.csv + Bṛhat Saṃhitā)
ZONE_ELEMENT = {
    "NE":     "ether",
    "E":      "fire",
    "SE":     "fire",
    "S":      "earth",
    "SW":     "earth",
    "W":      "water",
    "NW":     "air",
    "N":      "water",
    "Center": "ether",
}

# Zone canonical deity (guardian)
ZONE_DEITY = {
    "NE":     "Īśāna",
    "E":      "Indra",
    "SE":     "Agni",
    "S":      "Yama",
    "SW":     "Nirṛti",
    "W":      "Varuṇa",
    "NW":     "Vāyu",
    "N":      "Kubera",
    "Center": "Brahmā",
}

# Element → preferred zone for entity placement
ELEMENT_ZONE_PREF = {
    "fire":  "SE",
    "water": "NE",
    "earth": "SW",
    "air":   "NW",
    "ether": "Center",
}

# Priority order for cell filling within a zone (center-out spiral)
# Higher priority cells get filled first
_ZONE_PRIORITY = {}  # populated by _build_grid()


def _build_grid() -> List[Dict[str, Any]]:
    """Build the canonical 64-cell grid with stable IDs and metadata."""
    cells = []
    for row in range(8):
        for col in range(8):
            cell_id = f"r{row}c{col}"
            zone = _ZONE_MAP[row][col]
            deity = _DEITY_MAP[row][col]
            element = ZONE_ELEMENT.get(zone, "ether")
            is_brahma = (zone == "Center")

            # Distance from center (3.5, 3.5) for priority
            dx = col - 3.5
            dy = row - 3.5
            dist = math.sqrt(dx*dx + dy*dy)

            cells.append({
                "cell_id": cell_id,
                "row": row,
                "col": col,
                "zone": zone,
                "deity": deity,
                "element": element,
                "is_brahmasthana": is_brahma,
                "center_dist": round(dist, 3),
                "x": round(col / 7.0, 4),  # normalized 0..1
                "y": round(row / 7.0, 4),
                "attestation": "TRADITIONAL",
            })

    # Sort by distance from center (Brahmasthāna fills first)
    cells.sort(key=lambda c: c["center_dist"])
    for i, c in enumerate(cells):
        c["priority"] = i
        _ZONE_PRIORITY[c["cell_id"]] = i

    return cells


# Build once at import
GRID_64 = _build_grid()
_CELL_BY_ID = {c["cell_id"]: c for c in GRID_64}
_CELLS_BY_ZONE = {}
for c in GRID_64:
    _CELLS_BY_ZONE.setdefault(c["zone"], []).append(c)


# ══════════════════════════════════════════════════════════
# S3 → S4: TIME DRIVES SPACE
# ══════════════════════════════════════════════════════════

def _zone_weights_from_panchanga(panchanga: dict) -> Dict[str, float]:
    """Compute zone activation weights from current time-state.

    Element of current nakṣatra biases its preferred zone.
    Guṇa modulates adjacent zones.
    Arc phase (tithi position) modulates overall intensity.
    """
    element = (panchanga.get("element") or "ether").lower()
    guna = (panchanga.get("guna") or "sattva").lower()
    tidx = panchanga.get("tidx", 0)
    arc = tidx / 30.0

    # Base: all zones at 0.2
    weights = {z: 0.2 for z in ZONE_DEITY}

    # Element → preferred zone gets boosted
    pref = ELEMENT_ZONE_PREF.get(element, "Center")
    weights[pref] += 0.4

    # Adjacent zones get partial boost
    _ADJ = {
        "NE": ["N", "E", "Center"], "E": ["NE", "SE"],
        "SE": ["E", "S"],           "S": ["SE", "SW"],
        "SW": ["S", "W"],           "W": ["SW", "NW"],
        "NW": ["W", "N"],           "N": ["NW", "NE"],
        "Center": ["NE", "E", "SE", "S", "SW", "W", "NW", "N"],
    }
    for adj in _ADJ.get(pref, []):
        weights[adj] += 0.1

    # Guṇa modulation
    if guna == "sattva":
        weights["NE"] += 0.15
        weights["Center"] += 0.1
    elif guna == "rajas":
        weights["E"] += 0.1
        weights["SE"] += 0.1
    elif guna == "tamas":
        weights["SW"] += 0.1
        weights["W"] += 0.1

    # Arc phase: Śukla intensifies NE/E (growth), Kṛṣṇa intensifies SW/W (contraction)
    if arc < 0.5:
        intensity = arc / 0.5
        weights["NE"] += 0.1 * intensity
        weights["E"]  += 0.05 * intensity
    else:
        intensity = (arc - 0.5) / 0.5
        weights["SW"] += 0.1 * intensity
        weights["W"]  += 0.05 * intensity

    # Normalize to sum=1
    total = sum(weights.values())
    if total > 0:
        weights = {k: round(v / total, 4) for k, v in weights.items()}

    return weights


def _seasonal_rotation(panchanga: dict) -> float:
    """Compute seasonal orientation bias from solar month (māsa).

    In Vedic Vāstu, the entrance orientation shifts with season.
    Māsa 0-2 (spring/Caitra-Jyeṣṭha) → East emphasis (0°)
    Māsa 3-5 (summer/Āṣāḍha-Āśvina) → South (90°)
    Māsa 6-8 (autumn/Kārtika-Māgha) → West (180°)
    Māsa 9-11 (winter/Pauṣa-Phālguna) → North (270°)
    """
    masa = panchanga.get("masa_num", panchanga.get("masa", 0))
    if not isinstance(masa, (int, float)):
        masa = 0
    return (int(masa) // 3) * 90.0


def _place_entities(entities: list, active_relations: list,
                    zone_weights: Dict[str, float]) -> Tuple[dict, list, dict]:
    """Deterministic entity → cell placement.

    Rules:
      1. Top composite-score entity → Brahmasthāna center cell
      2. Next 3 highest → remaining Brahmasthāna cells
      3. Remaining entities → zone by element affinity, prioritized by zone weight
      4. Graph-related entities prefer adjacent cells

    Returns: (brahmasthana_info, active_cells, cell_occupancy)
    """
    brahma_cells = [c for c in GRID_64 if c["is_brahmasthana"]]
    other_cells_by_zone = {z: list(cells) for z, cells in _CELLS_BY_ZONE.items() if z != "Center"}

    # Track which cells are filled
    occupied = {}       # cell_id → entity_id
    occupancy = {}      # entity_id → cell info
    active_cells = []

    # Build relation adjacency lookup
    rel_neighbors = {}  # entity_id → set of related entity_ids
    for r in active_relations:
        fid = r.get("from_id", "")
        tid = r.get("to_id", "")
        rel_neighbors.setdefault(fid, set()).add(tid)
        rel_neighbors.setdefault(tid, set()).add(fid)

    sorted_ents = sorted(entities, key=lambda e: e.get("composite_score", e.get("score", 0)), reverse=True)

    # ── Brahmasthāna: top 4 ──
    brahma_reason = ""
    for i, ent in enumerate(sorted_ents[:min(4, len(sorted_ents))]):
        if i >= len(brahma_cells):
            break
        eid = ent.get("entity_id", "")
        cell = brahma_cells[i]
        cid = cell["cell_id"]
        occupied[cid] = eid
        score = ent.get("composite_score", ent.get("score", 0))
        info = {
            "cell_id": cid,
            "zone": "Center",
            "deity": cell["deity"],
            "element": ent.get("element", "ether"),
            "weight": round(score, 4),
            "entity_id": eid,
            "x": cell["x"],
            "y": cell["y"],
        }
        active_cells.append(info)
        occupancy[eid] = info
        if i == 0:
            brahma_reason = f"top composite coherence ({score:.3f})"

    brahmasthana = {
        "cell_ids": [c["cell_id"] for c in brahma_cells],
        "entity_id": sorted_ents[0].get("entity_id", "") if sorted_ents else "",
        "reason": brahma_reason,
    }

    # ── Remaining entities: zone by element, weighted by zone_weights ──
    remaining = sorted_ents[min(4, len(sorted_ents)):64]

    # Sort zones by weight (highest first) for preferred filling
    zone_order = sorted(zone_weights.keys(), key=lambda z: zone_weights.get(z, 0), reverse=True)

    for ent in remaining:
        eid = ent.get("entity_id", "")
        element = ent.get("element", "ether")
        score = ent.get("composite_score", ent.get("score", 0))

        # Preferred zone from element
        pref_zone = ELEMENT_ZONE_PREF.get(element, "Center")
        if pref_zone == "Center":
            pref_zone = zone_order[0]  # Center is full, use highest-weighted

        # Try: preferred zone → adjacent zones → any zone with space
        candidate_zones = [pref_zone]
        # Add zones where related entities already placed
        for neighbor_eid in rel_neighbors.get(eid, set()):
            if neighbor_eid in occupancy:
                candidate_zones.append(occupancy[neighbor_eid]["zone"])

        # Fallback to all zones by weight
        candidate_zones.extend(zone_order)
        # Deduplicate preserving order
        seen = set()
        ordered_zones = []
        for z in candidate_zones:
            if z not in seen and z != "Center":
                seen.add(z)
                ordered_zones.append(z)

        placed = False
        for zone in ordered_zones:
            zone_cells = other_cells_by_zone.get(zone, [])
            for cell in zone_cells:
                cid = cell["cell_id"]
                if cid not in occupied:
                    occupied[cid] = eid
                    info = {
                        "cell_id": cid,
                        "zone": zone,
                        "deity": cell["deity"],
                        "element": element,
                        "weight": round(score, 4),
                        "entity_id": eid,
                        "x": cell["x"],
                        "y": cell["y"],
                    }
                    active_cells.append(info)
                    occupancy[eid] = info
                    placed = True
                    break
            if placed:
                break

    return brahmasthana, active_cells, occupancy


# ══════════════════════════════════════════════════════════
# PUBLIC API
# ══════════════════════════════════════════════════════════

def derive_vastu_state(panchanga: dict,
                       entities: list,
                       active_relations: list,
                       formations: list,
                       theta: float,
                       phi: float) -> dict:
    """Compute deterministic S4 Vāstu state from S3 time-state + entity coherence.

    Args:
        panchanga:        current pañcāṅga dict (tithi, nakshatra, element, guna, etc.)
        entities:         coherence-ranked entity list from pipeline
        active_relations: extracted relations among top entities
        formations:       detected sacred geometry formations
        theta:            toroidal θ (time axis)
        phi:              toroidal φ (quality axis)

    Returns:
        Complete Vāstu state dict consumed by field_layers, igpu, and renderers.
    """
    # ── S3 → zone weights ──
    zone_weights = _zone_weights_from_panchanga(panchanga)

    # ── Orientation ──
    seasonal = _seasonal_rotation(panchanga)
    orientation = {
        "base_rotation_deg": 0.0,
        "seasonal_rotation_deg": seasonal,
        "effective_rotation_deg": seasonal,
    }

    # ── Entity placement ──
    brahmasthana, active_cells, cell_occupancy = _place_entities(
        entities, active_relations, zone_weights)

    # ── Activation summary ──
    dominant_zone = max(zone_weights, key=zone_weights.get) if zone_weights else "Center"
    dominant_element = ZONE_ELEMENT.get(dominant_zone, "ether")

    top_formation = ""
    formation_count = len(formations)
    if formations:
        top_formation = formations[0].get("name", "")

    summary = {
        "dominant_zone": dominant_zone,
        "dominant_element": dominant_element,
        "top_formation": top_formation,
        "formation_count": formation_count,
    }

    return {
        "grid_type": "manduka_64",
        "orientation": orientation,
        "brahmasthana": brahmasthana,
        "zone_weights": zone_weights,
        "active_cells": active_cells,
        "cell_occupancy": {k: v for k, v in cell_occupancy.items()},
        "activation_summary": summary,
        "attestation": "SYNTHESIS",
    }
