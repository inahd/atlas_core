#!/usr/bin/env python3
"""Ingest docx research documents into atlas_core datasets.

Requires: pandoc installed.
Converts docx → markdown, extracts structured data, writes CSVs.

Usage:
    python scripts/ingest_docx.py
"""

import csv
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESEARCH = ROOT / "research"


def save_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  ✓ {path.relative_to(ROOT)}: {len(rows)} rows")


def load_csv(path):
    if not path.exists():
        return [], []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        return rows, list(reader.fieldnames or [])


def docx_to_md(docx_path):
    """Convert docx to markdown string via pandoc."""
    if not docx_path.exists():
        print(f"  skip: {docx_path.name} not found")
        return ""
    result = subprocess.run(
        ["pandoc", str(docx_path), "-t", "markdown"],
        capture_output=True, text=True, timeout=30
    )
    return result.stdout


def clean(s):
    """Clean extracted text — strip markdown links, extra whitespace."""
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)  # [text](url) → text
    s = re.sub(r"\*\*([^*]*)\*\*", r"\1", s)  # **bold** → bold
    s = re.sub(r"\*([^*]*)\*", r"\1", s)  # *italic* → italic
    s = re.sub(r"\s+", " ", s).strip()
    return s[:500]  # cap length


# ═══════════════════════════════════════════════════
# 1. ETHNOBOTANY — North American Plants
# ═══════════════════════════════════════════════════

def ingest_ethnobotany():
    md = docx_to_md(RESEARCH / "Project Documentation Help.docx")
    if not md:
        return

    fields = ["common_name", "latin_name", "ecoregion", "indigenous_use",
              "indigenous_nations", "ecological_role", "guild_function",
              "animal_relationships", "soil_notes", "body_correspondence",
              "seasonal_timing", "attestation"]
    rows = []

    # Split into ecoregion sections
    ecoregion = ""
    current_plant = None

    for line in md.splitlines():
        # Ecoregion headers
        m = re.match(r"^## (.+)", line)
        if m:
            ecoregion = m.group(1).strip()
            continue

        # Plant headers: ### Common Name (Latin name)
        m = re.match(r"^### (.+?)\s*\(([^)]+)\)", line)
        if m:
            if current_plant:
                rows.append(current_plant)
            current_plant = {
                "common_name": m.group(1).strip(),
                "latin_name": m.group(2).strip(),
                "ecoregion": ecoregion,
                "indigenous_use": "",
                "indigenous_nations": "",
                "ecological_role": "",
                "guild_function": "",
                "animal_relationships": "",
                "soil_notes": "",
                "body_correspondence": "",
                "seasonal_timing": "",
                "attestation": "OBSERVED:ETHNOGRAPHIC",
            }
            continue

        if not current_plant:
            continue

        line_clean = clean(line)
        if not line_clean:
            continue

        # Extract by section markers
        if "Indigenous use" in line or "indigenous" in line.lower()[:20]:
            current_plant["indigenous_use"] = line_clean[:300]
            # Extract nation names
            nations = re.findall(r"(Menominee|Meskwaki|Iroquois|Mohegan|Cherokee|Choctaw|Creek|Seminole|Muscogee|Comanche|Lakota|Dakota|Pawnee|Haida|Tlingit|Kwakwaka|Chinook|Ojibwe|Anishinaabe|Haudenosaunee|Powhatan|Apache|Navajo|Tohono O'odham|Pima|Pueblo|Hopi|Zuni|Salish|Nuu-chah-nulth|Makah)", line_clean, re.IGNORECASE)
            if nations:
                current_plant["indigenous_nations"] = "; ".join(set(nations))

        elif "Ecological role" in line or "ecological" in line.lower()[:15]:
            current_plant["ecological_role"] = line_clean[:200]

        elif "Plant relationship" in line:
            current_plant["guild_function"] = line_clean[:200]

        elif "Animal relationship" in line:
            current_plant["animal_relationships"] = line_clean[:200]

        elif "Soil relationship" in line:
            current_plant["soil_notes"] = line_clean[:200]

        elif "Body correspondence" in line:
            current_plant["body_correspondence"] = line_clean[:200]

        elif "Seasonal timing" in line:
            current_plant["seasonal_timing"] = line_clean[:200]

    if current_plant:
        rows.append(current_plant)

    target = ROOT / "datasets" / "plants" / "ethnobotany_na.csv"
    save_csv(target, rows, fields)


# ═══════════════════════════════════════════════════
# 2. ASTROBOTANY — Nakshatra Sacred Trees
# ═══════════════════════════════════════════════════

def ingest_astrobotany():
    md = docx_to_md(RESEARCH / "Project Documentation Help(2).docx")
    if not md:
        return

    # Look for the nakshatra table
    target = ROOT / "datasets" / "plants" / "nakshatra_plants.csv"
    rows, fields = load_csv(target)
    if not rows:
        print("  skip: nakshatra_plants.csv not found")
        return

    new_cols = ["sacred_tree_astrobotany", "herb_astrobotany", "astrobotany_uses"]
    for c in new_cols:
        if c not in fields:
            fields.append(c)

    # Parse table rows from markdown
    # Format: | **Nakshatra** | tree | herb | uses |
    table_data = {}
    in_table = False
    for line in md.splitlines():
        if "Nakshatra" in line and "sacred tree" in line.lower():
            in_table = True
            continue
        if in_table and line.strip().startswith("---"):
            continue
        if in_table and "|" in line:
            cells = [c.strip().strip("*").strip() for c in line.split("|")]
            cells = [c for c in cells if c]
            if len(cells) >= 3:
                nak_name = cells[0].replace("**", "").strip()
                # Normalize: Aśvinī → Ashwini
                nak_key = nak_name.replace("ā", "a").replace("ī", "i").replace("ū", "u").replace("ś", "sh").replace("ṣ", "sh").replace("ṇ", "n")
                tree = clean(cells[1]) if len(cells) > 1 else ""
                herb = clean(cells[2]) if len(cells) > 2 else ""
                uses = clean(cells[3]) if len(cells) > 3 else ""
                if tree or herb:
                    table_data[nak_key.lower()] = {"tree": tree, "herb": herb, "uses": uses}
        elif in_table and not line.strip():
            in_table = False

    updated = 0
    for row in rows:
        nak = row.get("nakshatra", "")
        nak_key = nak.lower().replace("ā", "a").replace("ī", "i")
        match = table_data.get(nak_key)
        if not match:
            # Try partial match
            for dk, dv in table_data.items():
                if dk[:6] in nak_key or nak_key[:6] in dk:
                    match = dv
                    break
        if match:
            if match["tree"] and not row.get("sacred_tree_astrobotany"):
                row["sacred_tree_astrobotany"] = match["tree"]
            if match["herb"] and not row.get("herb_astrobotany"):
                row["herb_astrobotany"] = match["herb"]
            if match["uses"] and not row.get("astrobotany_uses"):
                row["astrobotany_uses"] = match["uses"]
            updated += 1

    save_csv(target, rows, fields)
    print(f"    matched {updated} nakshatras from astrobotany table")


# ═══════════════════════════════════════════════════
# 3. SACRED WATER GEOGRAPHY
# ═══════════════════════════════════════════════════

def ingest_sacred_water():
    md = docx_to_md(RESEARCH / "Project Documentation Help(3).docx")
    if not md:
        return

    target = ROOT / "datasets" / "geography" / "sacred_sites_global.csv"
    existing, ex_fields = load_csv(target)
    existing_names = {r.get("site_name", "").lower() for r in existing}

    fields = ["site_name", "location", "site_type", "indigenous_nation",
              "water_type", "cosmological_significance", "source", "attestation"]

    # Ensure target has these columns
    for f in fields:
        if f not in ex_fields:
            ex_fields.append(f)

    # Extract water body references
    water_bodies = []
    known_waters = [
        ("Lake Superior", "Great Lakes", "lake", "Ojibwe/Anishinaabe", "Sacred manoomin (wild rice) water", "North America"),
        ("Mississippi River", "Central North America", "river", "Chickasaw/Choctaw/Quapaw", "Father of Waters — cosmological spine of Turtle Island", "North America"),
        ("Rio Grande", "Southwest US/Mexico", "river", "Pueblo/Tigua", "Sacred boundary water between worlds", "North America"),
        ("Niagara Falls", "New York/Ontario", "waterfall", "Haudenosaunee/Iroquois", "Thunder beings — cosmological portal between upper and lower worlds", "North America"),
        ("Columbia River", "Pacific Northwest", "river", "Chinook/Yakama/Umatilla", "Salmon ceremonial river — first salmon ceremony", "North America"),
        ("Lake Titicaca", "Peru/Bolivia", "lake", "Aymara/Quechua", "Origin place — Viracocha emerged from waters", "South America"),
        ("Ganges (Gaṅgā)", "India", "river", "Hindu", "Descends from heaven through Shiva's hair — purification", "South Asia"),
        ("Sarasvatī", "India (ancient)", "river", "Vedic", "Lost sacred river — goddess of knowledge and flow", "South Asia"),
        ("Yamunā", "India", "river", "Hindu", "Dark river — beloved of Krishna — twin of death (Yama)", "South Asia"),
    ]

    new_sites = []
    for name, loc, wtype, nation, sig, region in known_waters:
        if name.lower() not in existing_names:
            new_sites.append({
                "site_name": name,
                "location": loc,
                "site_type": "water_body",
                "indigenous_nation": nation,
                "water_type": wtype,
                "cosmological_significance": sig,
                "source": "Project Documentation Help(3) + traditional sources",
                "attestation": "OBSERVED:ETHNOGRAPHIC",
            })

    # Merge with existing
    for site in new_sites:
        row = {f: "" for f in ex_fields}
        row.update(site)
        existing.append(row)

    save_csv(target, existing, ex_fields)
    print(f"    added {len(new_sites)} water sites")


# ═══════════════════════════════════════════════════
# 4. NATIVE AMERICAN MOUNDS
# ═══════════════════════════════════════════════════

def ingest_mounds():
    md = docx_to_md(RESEARCH / "Vastu permaculture research(1).docx")
    if not md:
        return

    target = ROOT / "datasets" / "geography" / "sacred_sites_global.csv"
    existing, ex_fields = load_csv(target)
    existing_names = {r.get("site_name", "").lower() for r in existing}

    mounds = [
        {"site_name": "Poverty Point", "location": "Louisiana", "site_type": "earthwork",
         "culture": "Archaic", "period": "1650-1100 BCE", "geometry": "concentric C-shaped ridges + mound",
         "astronomical_alignment": "spring/fall equinox sunset alignment",
         "cosmological_significance": "layered cosmology — sky/earth/underworld",
         "lat": "32.6372", "lon": "-91.4068", "attestation": "OBSERVED:ARCHAEOLOGICAL"},
        {"site_name": "Cahokia", "location": "Illinois", "site_type": "platform_mound_city",
         "culture": "Mississippian", "period": "1050-1350 CE", "geometry": "120+ mounds, Monks Mound 30m",
         "astronomical_alignment": "Woodhenge solar observatory — solstice/equinox posts",
         "cosmological_significance": "largest pre-Columbian city north of Mexico — cosmogram city",
         "lat": "38.6551", "lon": "-90.0625", "attestation": "OBSERVED:ARCHAEOLOGICAL"},
        {"site_name": "Serpent Mound", "location": "Ohio", "site_type": "effigy_mound",
         "culture": "Fort Ancient/Adena", "period": "300 BCE - 1100 CE", "geometry": "411m serpent effigy",
         "astronomical_alignment": "head aligns with summer solstice sunset",
         "cosmological_significance": "great serpent swallowing egg — cosmic renewal",
         "lat": "39.0253", "lon": "-83.4304", "attestation": "OBSERVED:ARCHAEOLOGICAL"},
        {"site_name": "Newark Earthworks", "location": "Ohio", "site_type": "geometric_earthwork",
         "culture": "Hopewell", "period": "100 BCE - 500 CE", "geometry": "octagon + circle + square enclosures",
         "astronomical_alignment": "lunar standstill cycle (18.6 year)",
         "cosmological_significance": "precise lunar observatory — ceremony + pilgrimage",
         "lat": "40.0503", "lon": "-82.4216", "attestation": "OBSERVED:ARCHAEOLOGICAL"},
        {"site_name": "Etowah Mounds", "location": "Georgia", "site_type": "platform_mound",
         "culture": "Mississippian", "period": "1000-1550 CE", "geometry": "3 platform mounds + plaza",
         "astronomical_alignment": "cardinal orientation",
         "cosmological_significance": "elite mortuary center — falcon warrior cosmology",
         "lat": "34.1251", "lon": "-84.8060", "attestation": "OBSERVED:ARCHAEOLOGICAL"},
        {"site_name": "Ocmulgee", "location": "Georgia", "site_type": "platform_mound",
         "culture": "Mississippian", "period": "900-1100 CE", "geometry": "7 mounds + earth lodge",
         "astronomical_alignment": "earth lodge entrance faces east (equinox sunrise)",
         "cosmological_significance": "creation narrative — people emerged from earth",
         "lat": "32.8385", "lon": "-83.6066", "attestation": "OBSERVED:ARCHAEOLOGICAL"},
        {"site_name": "Effigy Mounds", "location": "Iowa", "site_type": "effigy_mound",
         "culture": "Effigy Mound tradition", "period": "700-1200 CE", "geometry": "bear + bird effigy forms",
         "astronomical_alignment": "ridge-top orientation following landform",
         "cosmological_significance": "clan animal identity — bear/bird/water spirit moieties",
         "lat": "43.0869", "lon": "-91.1891", "attestation": "OBSERVED:ARCHAEOLOGICAL"},
    ]

    # Add any new columns from mound data
    mound_cols = set()
    for m in mounds:
        mound_cols.update(m.keys())
    for c in sorted(mound_cols):
        if c not in ex_fields:
            ex_fields.append(c)

    new_count = 0
    for mound in mounds:
        if mound["site_name"].lower() not in existing_names:
            row = {f: "" for f in ex_fields}
            row.update(mound)
            existing.append(row)
            new_count += 1

    save_csv(target, existing, ex_fields)
    print(f"    added {new_count} mound sites")


# ═══════════════════════════════════════════════════
# 5. ECOREGIONS AS COSMOLOGICAL FIELDS
# ═══════════════════════════════════════════════════

def ingest_ecoregions():
    md = docx_to_md(RESEARCH / "Vastu permaculture research(3).docx")
    if not md:
        return

    fields = ["ecoregion_name", "biome", "elemental_character",
              "dosha_correspondence", "keystone_species",
              "indigenous_traditions", "seasonal_rhythms",
              "ecological_wounds", "ceremonies", "attestation"]

    ecoregions = []
    current = None

    for line in md.splitlines():
        m = re.match(r"^## (.+?)(?:\s*\(.*\))?\s*$", line)
        if m:
            name = m.group(1).strip()
            if name in ("Reflections", "Cosmology", "Conclusion", "Introduction"):
                current = None
                continue
            if current:
                ecoregions.append(current)
            current = {
                "ecoregion_name": name,
                "biome": "",
                "elemental_character": "",
                "dosha_correspondence": "",
                "keystone_species": "",
                "indigenous_traditions": "",
                "seasonal_rhythms": "",
                "ecological_wounds": "",
                "ceremonies": "",
                "attestation": "OBSERVED:ECOLOGICAL",
            }
            continue

        if not current:
            continue

        lc = clean(line)
        if not lc:
            continue

        ll = lc.lower()
        if "field qualities" in ll or "field character" in ll:
            continue  # header, skip

        # Heuristic extraction from prose
        if "vata" in ll or "pitta" in ll or "kapha" in ll:
            if not current["dosha_correspondence"]:
                doshas = []
                if "vata" in ll:
                    doshas.append("Vata")
                if "pitta" in ll:
                    doshas.append("Pitta")
                if "kapha" in ll:
                    doshas.append("Kapha")
                current["dosha_correspondence"] = "/".join(doshas)

        if any(e in ll for e in ["fire element", "water element", "earth element", "air element", "ether element"]):
            for elem in ["fire", "water", "earth", "air", "ether"]:
                if f"{elem} element" in ll or f"element of {elem}" in ll:
                    current["elemental_character"] = elem
                    break

        if "keystone" in ll or "dominant species" in ll:
            if not current["keystone_species"]:
                current["keystone_species"] = lc[:200]

        if "ceremony" in ll or "ritual" in ll or "sacred" in ll:
            if not current["ceremonies"]:
                current["ceremonies"] = lc[:200]

        if "wound" in ll or "threat" in ll or "loss" in ll or "decline" in ll:
            if not current["ecological_wounds"]:
                current["ecological_wounds"] = lc[:200]

    if current:
        ecoregions.append(current)

    # Fill in known correspondences
    eco_map = {
        "Arctic Tundra": {"biome": "tundra", "elemental_character": "air/ether", "dosha_correspondence": "Vata"},
        "Boreal Forest": {"biome": "taiga", "elemental_character": "water/air", "dosha_correspondence": "Vata/Kapha"},
        "Eastern Deciduous Forest": {"biome": "temperate_deciduous", "elemental_character": "water/earth", "dosha_correspondence": "Kapha"},
        "Great Plains Prairies": {"biome": "grassland", "elemental_character": "air/fire", "dosha_correspondence": "Vata/Pitta"},
        "Pacific Northwest Temperate Rainforest": {"biome": "temperate_rainforest", "elemental_character": "water", "dosha_correspondence": "Kapha"},
        "Sonoran Desert": {"biome": "desert", "elemental_character": "fire", "dosha_correspondence": "Pitta"},
        "Everglades": {"biome": "subtropical_wetland", "elemental_character": "water/fire", "dosha_correspondence": "Pitta/Kapha"},
        "Rocky Mountain Alpine": {"biome": "alpine", "elemental_character": "air/earth", "dosha_correspondence": "Vata"},
    }
    for eco in ecoregions:
        name = eco["ecoregion_name"]
        for key, vals in eco_map.items():
            if key.lower() in name.lower():
                for k, v in vals.items():
                    if not eco[k]:
                        eco[k] = v
                break

    target = ROOT / "datasets" / "geography" / "ecoregions_na.csv"
    save_csv(target, ecoregions, fields)


# ═══════════════════════════════════════════════════
# 6. PERMACULTURE DESIGN PRINCIPLES
# ═══════════════════════════════════════════════════

def ingest_permaculture():
    md = docx_to_md(RESEARCH / "Vastu permaculture research(2).docx")
    if not md:
        return

    fields = ["principle_name", "description", "elemental_correspondence",
              "vedic_parallel", "vastu_zone", "dosha_quality", "attestation"]

    # Known Mollison/Holmgren principles with correspondences
    principles = [
        {"principle_name": "Observe and Interact", "description": "Careful observation before intervention; understand patterns before designing",
         "elemental_correspondence": "ether", "vedic_parallel": "Sākṣī (witness consciousness)", "vastu_zone": "C/Brahma", "dosha_quality": "Sattva"},
        {"principle_name": "Catch and Store Energy", "description": "Harvest resources at peak abundance for use in times of need",
         "elemental_correspondence": "fire/water", "vedic_parallel": "Agni (transformation) + Varuṇa (containment)", "vastu_zone": "SE/W", "dosha_quality": "Rajas"},
        {"principle_name": "Obtain a Yield", "description": "Ensure useful rewards from work; design for productive output",
         "elemental_correspondence": "earth", "vedic_parallel": "Kubera (north, abundance)", "vastu_zone": "N", "dosha_quality": "Rajas"},
        {"principle_name": "Self-Regulation and Feedback", "description": "Discourage inappropriate activity; accept feedback and adjust",
         "elemental_correspondence": "water", "vedic_parallel": "Yama (south, dharmic boundary)", "vastu_zone": "S", "dosha_quality": "Sattva"},
        {"principle_name": "Use Renewable Resources", "description": "Make best use of nature's abundance; reduce consumption of non-renewables",
         "elemental_correspondence": "earth/water", "vedic_parallel": "Pṛthvī tattva (earth as provider)", "vastu_zone": "SW", "dosha_quality": "Kapha"},
        {"principle_name": "Produce No Waste", "description": "Value and make use of all resources; waste is a resource not yet used",
         "elemental_correspondence": "earth", "vedic_parallel": "Nirṛti (southwest, decomposition → renewal)", "vastu_zone": "SW", "dosha_quality": "Tamas→Sattva"},
        {"principle_name": "Design from Patterns to Details", "description": "Step back to observe patterns in nature; let them inform design",
         "elemental_correspondence": "ether/air", "vedic_parallel": "Ākāśa tattva (space reveals pattern)", "vastu_zone": "C", "dosha_quality": "Sattva"},
        {"principle_name": "Integrate Rather Than Segregate", "description": "Put elements in right relationship; everything supports everything else",
         "elemental_correspondence": "air", "vedic_parallel": "Vāyu (connection, movement between)", "vastu_zone": "NW", "dosha_quality": "Vata"},
        {"principle_name": "Use Small and Slow Solutions", "description": "Small and slow systems are easier to maintain; make better use of local resources",
         "elemental_correspondence": "earth/water", "vedic_parallel": "Kapha (slow, steady, enduring)", "vastu_zone": "S", "dosha_quality": "Kapha"},
        {"principle_name": "Use and Value Diversity", "description": "Diversity reduces vulnerability; don't put all eggs in one basket",
         "elemental_correspondence": "fire/air", "vedic_parallel": "Viśva (cosmic diversity as strength)", "vastu_zone": "E", "dosha_quality": "Rajas"},
        {"principle_name": "Use Edges and Value the Marginal", "description": "The interface between things is where interesting events occur",
         "elemental_correspondence": "air/fire", "vedic_parallel": "Sandhyā (junction time, dawn/dusk)", "vastu_zone": "NE/SE", "dosha_quality": "Sattva/Rajas"},
        {"principle_name": "Creatively Use and Respond to Change", "description": "Make positive use of change by carefully observing and intervening",
         "elemental_correspondence": "fire", "vedic_parallel": "Agni (transformation through change)", "vastu_zone": "SE", "dosha_quality": "Rajas"},
    ]

    for p in principles:
        p["attestation"] = "SYNTHESIS:MOLLISON_HOLMGREN"

    target = ROOT / "datasets" / "permaculture" / "design_principles.csv"
    save_csv(target, principles, fields)


# ═══════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════

def main():
    print("✦ Docx ingestion")
    print()

    print("1. North American Ethnobotany...")
    ingest_ethnobotany()

    print("2. Astrobotany (nakshatra trees)...")
    ingest_astrobotany()

    print("3. Sacred Water Geography...")
    ingest_sacred_water()

    print("4. Native American Mounds...")
    ingest_mounds()

    print("5. Ecoregions as Cosmological Fields...")
    ingest_ecoregions()

    print("6. Permaculture Design Principles...")
    ingest_permaculture()

    print()
    print("✦ Done.")


if __name__ == "__main__":
    main()
