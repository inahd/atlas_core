"""
parse_pfaf.py — Extract structured fields from PFAF free-text data.

Reads: datasets/plants/pfaf.sqlite (North American plants)
Writes: datasets/plants/pfaf_structured.csv

Parses cultivation_details, habitats, other_uses, known_hazards
into structured columns: layer, guild_function, succession_role,
nitrogen_fixer, allelopathic, water_relationship, root_architecture,
fodder suitability per animal.

Attestation: OBSERVED:PFAF (structured extraction from PFAF source)
"""
import csv
import re
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "datasets/plants/pfaf.sqlite"
OUT = Path(__file__).resolve().parent.parent / "datasets/plants/pfaf_structured.csv"


def parse_height(row):
    """Extract mature height in meters."""
    h = row.get("height")
    if h and h != "0.0":
        try:
            return float(h)
        except (ValueError, TypeError):
            pass
    for field in ("physical_characteristics", "cultivation_details"):
        text = row.get(field) or ""
        m = re.search(r"(\d+\.?\d*)\s*(?:to|-)\s*(\d+\.?\d*)\s*m", text, re.I)
        if m:
            return (float(m.group(1)) + float(m.group(2))) / 2
        m = re.search(r"(\d+\.?\d*)\s*m", text, re.I)
        if m:
            return float(m.group(1))
    return None


def parse_spread(text):
    if not text:
        return None
    m = re.search(r"spread[s]?\s+(?:of\s+)?(\d+\.?\d*)\s*(?:to\s*(\d+\.?\d*))?\s*m", text, re.I)
    if m:
        return (float(m.group(1)) + float(m.group(2))) / 2 if m.group(2) else float(m.group(1))
    return None


def parse_nitrogen_fixer(row):
    text = " ".join(filter(None, [row.get("other_uses"), row.get("cultivation_details")]))
    keywords = ["nitrogen fix", "fixes nitrogen", "nodules", "rhizobium",
                "nitrogen-fix", "n-fix", "symbiotic relationship with certain soil bacteria"]
    return any(k in text.lower() for k in keywords)


def parse_water(row):
    text = " ".join(filter(None, [row.get("cultivation_details"), row.get("habitats")])).lower()
    if any(k in text for k in ["bog", "wetland", "swamp", "aquatic", "submerged"]):
        return "wetland"
    if any(k in text for k in ["pond margin", "stream bank", "waterside", "moisture retentive"]):
        return "moisture_loving"
    if any(k in text for k in ["drought", "dry", "xeric", "arid"]):
        return "drought_tolerant"
    return "mesic"


def parse_layer(habit, height):
    h = (habit or "").lower()
    if "climber" in h or "vine" in h:
        return "vine"
    if "bulb" in h or "tuber" in h or "rhizome" in h:
        return "root"
    if "tree" in h:
        return "canopy" if height and height > 8 else "understory"
    if "bamboo" in h:
        return "canopy"
    if "shrub" in h:
        return "shrub"
    return "groundcover"


def parse_allelopathy(hazards):
    if not hazards:
        return False
    keywords = ["allelopathic", "inhibit", "juglone", "suppress other", "toxic to other plants"]
    return any(k in hazards.lower() for k in keywords)


def parse_fodder(row):
    text = " ".join(filter(None, [row.get("other_uses"), row.get("edible_uses")])).lower()
    result = {}
    for animal in ["cattle", "sheep", "goat", "pig", "chicken", "duck"]:
        result[animal] = animal in text or "livestock" in text or "fodder" in text
    if "poultry" in text:
        result["chicken"] = True
        result["duck"] = True
    return result


def parse_succession(row):
    text = " ".join(filter(None, [row.get("habitats"), row.get("cultivation_details")])).lower()
    if any(k in text for k in ["pioneer", "colonizer", "disturbed ground", "waste ground", "quick to mature"]):
        return "pioneer"
    if any(k in text for k in ["climax", "old growth", "ancient woodland"]):
        return "climax"
    if any(k in text for k in ["woodland edge", "scrub", "hedgerow", "hedge"]):
        return "early_successional"
    return "mid_successional"


def parse_root_arch(row):
    text = " ".join(filter(None, [row.get("cultivation_details"), row.get("habitats")])).lower()
    if "taproot" in text or "deep root" in text:
        return "deep_taproot"
    if "rhizome" in text or "spreading root" in text:
        return "rhizomatous"
    if "bulb" in text:
        return "bulb"
    if "tuber" in text:
        return "tuber"
    if "superficial" in text or "shallow root" in text:
        return "fibrous_shallow"
    return "fibrous_shallow"


def parse_guild_function(row, nitrogen_fixer, layer):
    text = " ".join(filter(None, [row.get("other_uses"), row.get("habitats")])).lower()
    if nitrogen_fixer:
        return "nitrogen_fixer"
    if any(k in text for k in ["dynamic accumulator", "mineral accumulator"]):
        return "dynamic_accumulator"
    if any(k in text for k in ["attract", "pollinator", "bee plant", "butterfly"]):
        return "pollinator_attractor"
    if any(k in text for k in ["repel", "deter", "pest", "insecticid"]):
        return "pest_confuser"
    if any(k in text for k in ["ground cover", "groundcover", "weed suppress"]):
        return "groundcover"
    if any(k in text for k in ["windbreak", "shelter", "hedge"]):
        return "windbreak"
    if layer == "canopy":
        return "canopy"
    if layer == "vine":
        return "climber"
    return "support"


def parse_hardiness(h):
    if not h:
        return None, None
    nums = re.findall(r"\d+", str(h))
    if len(nums) >= 2:
        return int(nums[0]), int(nums[-1])
    if len(nums) == 1:
        return int(nums[0]), int(nums[0])
    return None, None


FIELDNAMES = [
    "latin_name", "common_name", "family", "habit",
    "mature_height_m", "canopy_spread_m", "hardiness_zone_min", "hardiness_zone_max",
    "layer", "succession_role", "root_architecture", "water_relationship",
    "nitrogen_fixer", "guild_function_primary",
    "allelopathic", "fodder_cattle", "fodder_sheep", "fodder_goat",
    "fodder_pig", "fodder_chicken", "fodder_duck",
    "edibility_rating", "medicinal_rating", "other_uses_rating",
    "soil", "shade", "moisture", "range", "found_in",
    "known_hazards", "summary",
    "attestation", "source",
]


def run():
    if not DB.exists():
        print(f"PFAF database not found at {DB}")
        return

    conn = sqlite3.connect(str(DB))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM plants WHERE found_in LIKE ? OR found_in LIKE ? OR range LIKE ?",
        ("%North America%", "%United States%", "%N. America%"),
    ).fetchall()
    conn.close()

    print(f"Processing {len(rows)} North American plants...")

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()

        for row in rows:
            r = dict(row)
            height = parse_height(r)
            spread = parse_spread(r.get("cultivation_details") or "")
            nitrogen = parse_nitrogen_fixer(r)
            water = parse_water(r)
            layer = parse_layer(r.get("habit"), height)
            allelopathic = parse_allelopathy(r.get("known_hazards"))
            fodder = parse_fodder(r)
            succession = parse_succession(r)
            root_arch = parse_root_arch(r)
            guild_fn = parse_guild_function(r, nitrogen, layer)
            hz_min, hz_max = parse_hardiness(r.get("hardiness"))

            writer.writerow({
                "latin_name": r.get("latin_name", ""),
                "common_name": r.get("common_name", ""),
                "family": r.get("family") or "",
                "habit": r.get("habit") or "",
                "mature_height_m": round(height, 1) if height else "",
                "canopy_spread_m": round(spread, 1) if spread else "",
                "hardiness_zone_min": hz_min or "",
                "hardiness_zone_max": hz_max or "",
                "layer": layer,
                "succession_role": succession,
                "root_architecture": root_arch,
                "water_relationship": water,
                "nitrogen_fixer": "yes" if nitrogen else "no",
                "guild_function_primary": guild_fn,
                "allelopathic": "yes" if allelopathic else "no",
                "fodder_cattle": "yes" if fodder.get("cattle") else "no",
                "fodder_sheep": "yes" if fodder.get("sheep") else "no",
                "fodder_goat": "yes" if fodder.get("goat") else "no",
                "fodder_pig": "yes" if fodder.get("pig") else "no",
                "fodder_chicken": "yes" if fodder.get("chicken") else "no",
                "fodder_duck": "yes" if fodder.get("duck") else "no",
                "edibility_rating": r.get("edibility_rating") or 0,
                "medicinal_rating": r.get("medicinal_rating") or 0,
                "other_uses_rating": r.get("other_uses_rating") or 0,
                "soil": r.get("soil") or "",
                "shade": r.get("shade") or "",
                "moisture": r.get("moisture") or "",
                "range": (r.get("range") or "")[:200],
                "found_in": (r.get("found_in") or "")[:200],
                "known_hazards": (r.get("known_hazards") or "")[:300],
                "summary": (r.get("summary") or "")[:300],
                "attestation": "OBSERVED:PFAF",
                "source": "pfaf.org database",
            })

    print(f"Written to {OUT}")

    # Stats
    layers = {}
    guild_fns = {}
    n_fix = 0
    allelo = 0
    with open(OUT, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            l = row.get("layer", "unknown")
            layers[l] = layers.get(l, 0) + 1
            gf = row.get("guild_function_primary", "")
            guild_fns[gf] = guild_fns.get(gf, 0) + 1
            if row.get("nitrogen_fixer") == "yes":
                n_fix += 1
            if row.get("allelopathic") == "yes":
                allelo += 1

    print(f"Total rows: {sum(layers.values())}")
    print(f"Nitrogen fixers: {n_fix}")
    print(f"Allelopathic: {allelo}")
    print("Layer distribution:")
    for l, c in sorted(layers.items(), key=lambda x: -x[1]):
        print(f"  {l}: {c}")
    print("Guild functions:")
    for g, c in sorted(guild_fns.items(), key=lambda x: -x[1])[:10]:
        print(f"  {g}: {c}")


if __name__ == "__main__":
    run()
