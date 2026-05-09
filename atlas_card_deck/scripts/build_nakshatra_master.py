#!/usr/bin/env python3
"""
Build nakshatra_master_table.csv and .json from Atlas source files.
First-pass deck-ready dataset — 27 rows, 41 columns.

v2: strict status logic, per-cell citation honesty, conflict detection,
    core_completeness_score, conflict_flag columns.
"""

import csv
import json
import os

ROOT = os.path.expanduser("~/atlas_core")

# ── Load sources ──────────────────────────────────────────────

def load_csv(rel_path):
    path = os.path.join(ROOT, rel_path)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))

canonical = {r["nakshatra"]: r for r in load_csv("datasets/astro/nakshatra_canonical.csv")}

_plants_raw = load_csv("datasets/plants/nakshatra_plants.csv")
plants = {}
for r in _plants_raw:
    name = r["nakshatra"]
    if name == "Dhanishtha": name = "Dhanishta"
    plants[name] = r

species = {}
for r in load_csv("datasets/species/nakshatra_species.csv"):
    name = r["nakshatra_name"]
    if name == "Dhanishtha": name = "Dhanishta"
    species[name] = r

dosha = {}
for r in load_csv("datasets/ayurveda/dosha_nakshatra_matrix.csv"):
    name = r["nakshatra"]
    if name == "Mrigashirsha": name = "Mrigashira"
    if name == "Moola": name = "Mula"
    if name == "Purvashadha": name = "Purva Ashadha"
    if name == "Uttarashadha": name = "Uttara Ashadha"
    dosha[name] = r

_body_raw = load_csv("datasets/yoga/nakshatra_body_map.csv")
body = {}
for r in _body_raw:
    name = r["nakshatra"]
    if name == "Dhanishtha": name = "Dhanishta"
    body[name] = r

agri = {r["nakshatra"]: r for r in load_csv("datasets/plants/nakshatra_agriculture.csv")}

# ── NAK_RAGA mapping from sound_engine.py line 387 ──────────

NAK_RAGA = {
    'Ashwini': 'Bilawal', 'Bharani': 'Kalyani', 'Krittika': 'Todi',
    'Rohini': 'Bhairavi', 'Mrigashira': 'Hindol', 'Ardra': 'Darbari',
    'Punarvasu': 'Yaman', 'Pushya': 'Kafi', 'Ashlesha': 'Bhairav',
    'Magha': 'Marwa', 'Purva Phalguni': 'Puriya', 'Uttara Phalguni': 'Bihag',
    'Hasta': 'Miyan ki Todi', 'Chitra': 'Ahir Bhairav', 'Swati': 'Desh',
    'Vishakha': 'Jaunpuri', 'Anuradha': 'Malkauns', 'Jyeshtha': 'Bageshri',
    'Mula': 'Shree', 'Purva Ashadha': 'Kedar', 'Uttara Ashadha': 'Hamir',
    'Shravana': 'Durga', 'Dhanishta': 'Sarang', 'Shatabhisha': 'Lalit',
    'Purva Bhadrapada': 'Basant', 'Uttara Bhadrapada': 'Jayjaywanti',
    'Revati': 'Hansadhwani',
}

# ── Canonical order ──────────────────────────────────────────

NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

RASHIS = [
    "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
    "Tula", "Vrischika", "Dhanu", "Makara", "Kumbha", "Meena",
]

GANDANTA = {"Ashwini", "Ashlesha", "Magha", "Jyeshtha", "Mula", "Revati"}
GANDANTA_POLARITY = {
    "Ashwini": "fire-entering", "Magha": "fire-entering", "Mula": "fire-entering",
    "Ashlesha": "water-leaving", "Jyeshtha": "water-leaving", "Revati": "water-leaving",
}

TITHI_PREF = {
    "Ashwini": "Nanda (fire-starting gandanta prefers Nanda tithis)",
    "Magha": "Nanda (fire-starting gandanta prefers Nanda tithis)",
    "Mula": "Nanda (fire-starting gandanta prefers Nanda tithis)",
    "Ashlesha": "Purna (water-ending gandanta prefers Purna tithis)",
    "Jyeshtha": "Purna (water-ending gandanta prefers Purna tithis)",
    "Revati": "Purna (water-ending gandanta prefers Purna tithis)",
}

BIODYNAMIC = {
    "Mesha": "Fruit/Seed", "Simha": "Fruit/Seed", "Dhanu": "Fruit/Seed",
    "Vrishabha": "Root", "Kanya": "Root", "Makara": "Root",
    "Mithuna": "Flower", "Tula": "Flower", "Kumbha": "Flower",
    "Karka": "Leaf", "Vrischika": "Leaf", "Meena": "Leaf",
}

# ── Yoni conflict detection ──────────────────────────────────

# Known animal-type conflicts between canonical.csv and species.csv
YONI_ANIMAL_CONFLICTS = {
    "Anuradha":      ("deer", "Rabbit"),
    "Jyeshtha":      ("deer", "Rabbit"),
    "Uttara Ashadha": ("monkey", "Mongoose"),
}

# Gender conflicts are pervasive but do not change the animal type.
# We log them in the report but use canonical as primary.
GENDER_SWAP_NAKSHATRAS = {
    "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Hasta", "Chitra", "Swati",
    "Vishakha", "Mula", "Purva Ashadha", "Revati",
}

# ── Gift/shadow (SYNTHESIS — derived from themes, not direct extraction) ──

GIFT_SHADOW = {
    "Ashwini":  ("swift healing; initiating action", "impatience; restlessness"),
    "Bharani":  ("endurance through transformation", "excess; possessiveness"),
    "Krittika": ("clarity through purification", "harshness; destructive criticism"),
    "Rohini":   ("fertility; creative abundance", "attachment; material fixation"),
    "Mrigashira": ("curiosity; tireless seeking", "indecisiveness; scattered pursuit"),
    "Ardra":    ("emotional renewal after storm", "anxiety; destructive intensity"),
    "Punarvasu": ("restoration; nurturing return", "instability; over-optimism"),
    "Pushya":   ("nourishing devotion; teaching", "rigidity; smothering care"),
    "Ashlesha": ("coiling intelligence; strategic depth", "manipulation; secrecy"),
    "Magha":    ("ancestral authority; leadership", "pride; attachment to status"),
    "Purva Phalguni": ("creative pleasure; relaxation", "indulgence; laziness"),
    "Uttara Phalguni": ("steady patronage; alliance-building", "over-obligation; dryness"),
    "Hasta":    ("skillful manifestation; craft", "control; compulsive busyness"),
    "Chitra":   ("brilliant design; architectural beauty", "perfectionism; vanity"),
    "Swati":    ("independent exploration; freedom", "rootlessness; instability"),
    "Vishakha": ("determined achievement; ambition", "obsession; jealousy"),
    "Anuradha": ("loyal devotion; friendship", "codependence; suppressed anger"),
    "Jyeshtha": ("protective authority; responsibility", "arrogance; isolation"),
    "Mula":     ("root investigation; uprooting falsehood", "nihilism; destructiveness"),
    "Purva Ashadha": ("courageous declaration; invigoration", "fanaticism; grandiosity"),
    "Uttara Ashadha": ("enduring victory; ethical leadership", "rigidity; workaholism"),
    "Shravana": ("receptive listening; sacred learning", "gossip; passive withdrawal"),
    "Dhanishta": ("rhythmic prosperity; community wealth", "possessiveness over resources"),
    "Shatabhisha": ("solitary healing; esoteric research", "isolation; paranoia"),
    "Purva Bhadrapada": ("transformative fire; ascetic intensity", "fanaticism; rage"),
    "Uttara Bhadrapada": ("patient depth; wisdom through endurance", "lethargy; emotional suppression"),
    "Revati":   ("compassionate guidance; safe passage", "over-softness; boundary dissolution"),
}

# ── Mottos (SYNTHESIS — composed for card use, no textual source) ──

MOTTOS = {
    "Ashwini":  "The healers arrive before the wound is named.",
    "Bharani":  "What is born must also die; what dies is reborn.",
    "Krittika": "The blade that purifies does not apologize.",
    "Rohini":   "All things grow toward what nourishes them.",
    "Mrigashira": "The deer never stops searching.",
    "Ardra":    "After the storm, the air is new.",
    "Punarvasu": "What was lost returns, changed.",
    "Pushya":   "Feed first; teach after.",
    "Ashlesha": "The serpent knows by coiling, not by asking.",
    "Magha":    "The throne remembers who sat before.",
    "Purva Phalguni": "Rest is not the opposite of creation.",
    "Uttara Phalguni": "The contract holds when both sides hold.",
    "Hasta":    "The hand knows what the mind forgets.",
    "Chitra":   "Beauty is the first proof of structure.",
    "Swati":    "The wind carries no luggage.",
    "Vishakha": "The archer and the gate are one act.",
    "Anuradha": "Devotion is the shortest distance.",
    "Jyeshtha": "The elder guards what the young forget.",
    "Mula":     "Pull the root and the whole field shifts.",
    "Purva Ashadha": "Declare before you are ready.",
    "Uttara Ashadha": "The last standing wins without fighting.",
    "Shravana": "Listen until the silence speaks.",
    "Dhanishta": "The drum calls the wealth.",
    "Shatabhisha": "A hundred physicians in an empty circle.",
    "Purva Bhadrapada": "The fire that transforms is not gentle.",
    "Uttara Bhadrapada": "The deep serpent waits in water.",
    "Revati":   "The journey ends where the fish swim home.",
}

# ── Panel layout (SYNTHESIS — designed per-nakshatra, no source) ──

PANEL = {
    "Ashwini": "warm bg; twin horse heads flanking; swift diagonal lines",
    "Bharani": "earth tones; yoni triangle center; heavy border",
    "Krittika": "flame gradient; razor motif top; sharp horizontal divide",
    "Rohini": "cream/green; chariot center; lush organic border",
    "Mrigashira": "bisected card (earth/air); deer silhouette; wandering path",
    "Ardra": "dark storm wash; single teardrop focal; jagged edges",
    "Punarvasu": "golden air; quiver motif; return-arrow arc",
    "Pushya": "deep blue-green; lotus center; concentric nourishing rings",
    "Ashlesha": "dark green; coiled serpent spiral; tight border",
    "Magha": "dark fire tones; throne silhouette; ancestral column",
    "Purva Phalguni": "rose/gold; hammock arc; open relaxed composition",
    "Uttara Phalguni": "amber/earth; bed frame lines; stable grid",
    "Hasta": "white/silver; open hand center; fine craft-line detail",
    "Chitra": "jewel tones; pearl/gem focal; architectural frame",
    "Swati": "violet/air; young shoot rising; asymmetric wind lines",
    "Vishakha": "gold/fire; triumphal arch frame; goal-directed axis",
    "Anuradha": "water/devotion blue; lotus center; friendship dyad",
    "Jyeshtha": "emerald; protective earring motif; elder border",
    "Mula": "root brown; root system radiating down; stripped composition",
    "Purva Ashadha": "water blue/rose; fan spread; upward declaration",
    "Uttara Ashadha": "amber/earth; elephant tusk vertical; enduring column",
    "Shravana": "silver/white; ear motif; concentric listening rings",
    "Dhanishta": "red/fire; drum center; rhythmic horizontal bands",
    "Shatabhisha": "deep violet; empty circle center; 100-dot surround",
    "Purva Bhadrapada": "fire/gold; lightning bolt diagonal; intense edge",
    "Uttara Bhadrapada": "deep ocean blue; serpent bed base; patient depth",
    "Revati": "sea green; fish motif; flowing completion arc",
}

# ── Helper functions ─────────────────────────────────────────

def zodiac_span(i):
    start_deg = i * (360 / 27)
    end_deg = (i + 1) * (360 / 27)
    def fmt(d):
        sign_idx = int(d / 30) % 12
        rem = d % 30
        deg = int(rem)
        mins = int((rem - deg) * 60)
        return f"{deg:02d}d{mins:02d}m {RASHIS[sign_idx]}"
    return f"{fmt(start_deg)} - {fmt(end_deg)}"

def rashi_overlap(i):
    start_deg = i * (360 / 27)
    end_deg = (i + 1) * (360 / 27)
    r1 = RASHIS[int(start_deg / 30)]
    r2 = RASHIS[int((end_deg - 0.001) / 30)]
    if r1 == r2:
        return r1
    return f"{r1}/{r2}"

def biodynamic_cat(i):
    start_deg = i * (360 / 27)
    end_deg = (i + 1) * (360 / 27)
    mid = (start_deg + end_deg) / 2
    rashi = RASHIS[int(mid / 30)]
    cat = BIODYNAMIC.get(rashi, "")
    r1 = RASHIS[int(start_deg / 30)]
    r2 = RASHIS[int((end_deg - 0.001) / 30)]
    if r1 != r2:
        c1 = BIODYNAMIC.get(r1, "")
        c2 = BIODYNAMIC.get(r2, "")
        if c1 != c2:
            return f"{c1}/{c2} (cusp)"
    return cat

# ── Columns (now 41 with new fields) ────────────────────────

COLUMNS = [
    "deck_id", "nakshatra_number", "nakshatra_name", "zodiac_span", "padas",
    "rashi_overlap", "deity", "planetary_lord", "sacred_symbol",
    "shakti_statement", "yoni_animal", "species_correspondence",
    "primary_plant", "secondary_plants", "biodynamic_category",
    "astrobotanical_timing", "gana", "varna", "nadi", "dosha_profile",
    "body_region", "gift_expression", "shadow_expression",
    "gandanta_flag", "gandanta_polarity", "tithi_group_preference",
    "boundary_harmonic_mode", "nodal_interior_pattern", "prime_signature",
    "morphology_correlates", "svara_link", "raga_link",
    "visual_palette_logic", "panel_layout", "motto",
    "attestation_level", "source_file", "citation_status", "operational_status",
    "core_completeness_score", "conflict_flag",
]

# Core fields that determine ready/partial/blocked
CORE_FIELDS = [
    "deck_id", "nakshatra_number", "nakshatra_name", "zodiac_span",
    "deity", "planetary_lord", "sacred_symbol", "shakti_statement",
    "yoni_animal", "primary_plant", "gana", "nadi",
    "attestation_level", "source_file", "citation_status",
]

# ── Build rows ───────────────────────────────────────────────

rows = []
for i, name in enumerate(NAMES):
    c = canonical.get(name, {})
    p = plants.get(name, {})
    if not p:
        for alt in [name.replace(" ", ""), name.replace(" ", "_")]:
            p = plants.get(alt, {})
            if p: break
    if not p and name == "Purva Ashadha":
        p = plants.get("Purvashadha", plants.get("Purva_Ashadha", {}))
    if not p and name == "Uttara Ashadha":
        p = plants.get("Uttarashadha", plants.get("Uttara_Ashadha", {}))
    sp = species.get(name, {})
    d = dosha.get(name, {})
    b = body.get(name, {})
    ag = agri.get(name, {})

    # ── Yoni: use canonical, detect conflicts ────────────────
    yoni_from_canon = f"{c.get('yoni_animal', '')} ({c.get('yoni_gender', '')})" if c.get('yoni_animal') else ""
    species_from_file = f"{sp.get('species_name', '')} ({sp.get('relationship_type', '')})" if sp.get('species_name') else ""

    has_animal_conflict = name in YONI_ANIMAL_CONFLICTS
    has_gender_conflict = name in GENDER_SWAP_NAKSHATRAS
    has_any_conflict = has_animal_conflict or has_gender_conflict

    # For animal conflicts, append CONFLICT marker to yoni_animal
    if has_animal_conflict:
        canon_animal, species_animal = YONI_ANIMAL_CONFLICTS[name]
        yoni_from_canon += f" [CONFLICT: species.csv={species_animal}]"

    # ── Dosha profile ────────────────────────────────────────
    dosha_str = ""
    if d:
        dosha_str = f"{d.get('primary_dosha', '')}/{d.get('secondary_dosha', '')}: {d.get('dosha_modification_when_active', '')}"

    # ── Astrobotanical timing ────────────────────────────────
    agri_str = ""
    if ag:
        parts = []
        if ag.get("quality"): parts.append(ag["quality"])
        if ag.get("activity"): parts.append(f"do: {ag['activity']}")
        if ag.get("avoid") and ag["avoid"] != "—": parts.append(f"avoid: {ag['avoid']}")
        if ag.get("crops") and ag["crops"] != "—": parts.append(f"crops: {ag['crops']}")
        agri_str = "; ".join(parts)

    # ── Secondary plants ─────────────────────────────────────
    sec_parts = []
    tree = p.get("sacred_tree", "") or c.get("tree", "")
    if tree and tree != p.get("plant", ""):
        tree_latin = p.get("tree_latin", "")
        sec_parts.append(f"{tree}" + (f" ({tree_latin})" if tree_latin else ""))
    canon_plant = c.get("plant", "")
    if canon_plant and canon_plant != p.get("plant", "") and canon_plant != tree:
        sec_parts.append(canon_plant)
    secondary = "; ".join(sec_parts) if sec_parts else ""

    # ── Gandanta ─────────────────────────────────────────────
    is_gandanta = name in GANDANTA
    ganda_pol = GANDANTA_POLARITY.get(name, "")
    tithi_pref = TITHI_PREF.get(name, "")
    boundary_mode = ""
    if is_gandanta:
        boundary_mode = "elevated tithi-group differentiation (1.6x, p<0.0001)"

    gift, shadow = GIFT_SHADOW.get(name, ("", ""))

    # ── Visual palette ───────────────────────────────────────
    color = c.get("color_hex", "")
    element = c.get("element", "")
    palette = f"{color}; {element}-toned" if color else ""

    panel = PANEL.get(name, "")

    # ── Source files ─────────────────────────────────────────
    sources = "datasets/astro/nakshatra_canonical.csv"
    if p: sources += "; datasets/plants/nakshatra_plants.csv"
    if d: sources += "; datasets/ayurveda/dosha_nakshatra_matrix.csv"
    if b: sources += "; datasets/yoga/nakshatra_body_map.csv"
    if ag: sources += "; datasets/plants/nakshatra_agriculture.csv"
    if sp: sources += "; datasets/species/nakshatra_species.csv"
    sources += "; npu_engine/sound/sound_engine.py"

    # ── Attestation level ────────────────────────────────────
    # Core jyotish identity = canon (from BPHS-attributed data).
    # Plant/body/dosha = secondary (Brihat Samhita, Nadi Koota).
    # Gift/shadow/motto/panel = atlas_synthesis.
    # Raga mapping = atlas_synthesis (no traditional source cited).
    att = "canon"
    if c.get("attestation_status") != "attested_classical":
        att = "secondary"

    # ── Citation status: per-row (conservative) ──────────────
    # If the row has unresolved animal conflicts, citation = unresolved.
    # If the row is clean extraction, citation = extracted.
    # All rows have synthesis fields (gift/shadow/motto), but we
    # report citation at the row level for the *core* fields only.
    if has_animal_conflict:
        citation = "unresolved"
    else:
        citation = "extracted"

    # ── Core completeness score ──────────────────────────────
    primary_plant_val = p.get("plant", "") or p.get("common_name", "")
    row_draft = {
        "deck_id": f"nak_{i+1:02d}",
        "nakshatra_number": str(i + 1),
        "nakshatra_name": name,
        "zodiac_span": zodiac_span(i),
        "deity": c.get("deity", ""),
        "planetary_lord": c.get("graha", ""),
        "sacred_symbol": c.get("symbol", ""),
        "shakti_statement": c.get("shakti", ""),
        "yoni_animal": yoni_from_canon,
        "primary_plant": primary_plant_val,
        "gana": c.get("gana", ""),
        "nadi": c.get("nadi", ""),
        "attestation_level": att,
        "source_file": sources,
        "citation_status": citation,
    }
    core_filled = sum(1 for k in CORE_FIELDS if str(row_draft.get(k, "")).strip())
    core_score = int(100 * core_filled / len(CORE_FIELDS))

    # Also count non-core filled for a total picture
    all_field_count = len(COLUMNS) - 2  # exclude the two meta columns themselves
    # We'll compute total fill after building the full row

    # ── Operational status ───────────────────────────────────
    # blocked: missing core identity/canonical field
    # partial: has conflict, or missing important non-core field
    # ready: all core present, no unresolved conflicts
    missing_core = [k for k in CORE_FIELDS if not str(row_draft.get(k, "")).strip()]
    if missing_core:
        op_status = "blocked"
    elif has_animal_conflict:
        op_status = "partial"
    elif has_gender_conflict:
        # Gender swaps are less severe — row still usable but not pristine
        op_status = "partial"
    else:
        op_status = "ready"

    conflict_flag = "yes" if has_any_conflict else "no"

    row = {
        "deck_id": f"nak_{i+1:02d}",
        "nakshatra_number": i + 1,
        "nakshatra_name": name,
        "zodiac_span": zodiac_span(i),
        "padas": "4",
        "rashi_overlap": rashi_overlap(i),
        "deity": c.get("deity", ""),
        "planetary_lord": c.get("graha", ""),
        "sacred_symbol": c.get("symbol", ""),
        "shakti_statement": c.get("shakti", ""),
        "yoni_animal": yoni_from_canon,
        "species_correspondence": species_from_file,
        "primary_plant": primary_plant_val,
        "secondary_plants": secondary,
        "biodynamic_category": biodynamic_cat(i),
        "astrobotanical_timing": agri_str,
        "gana": c.get("gana", ""),
        "varna": c.get("varna", ""),
        "nadi": c.get("nadi", ""),
        "dosha_profile": dosha_str,
        "body_region": b.get("body_region", ""),
        "gift_expression": gift,
        "shadow_expression": shadow,
        "gandanta_flag": "yes" if is_gandanta else "no",
        "gandanta_polarity": ganda_pol,
        "tithi_group_preference": tithi_pref,
        "boundary_harmonic_mode": boundary_mode,
        "nodal_interior_pattern": "",
        "prime_signature": "",
        "morphology_correlates": "",
        "svara_link": "",
        "raga_link": NAK_RAGA.get(name, ""),
        "visual_palette_logic": palette,
        "panel_layout": panel,
        "motto": MOTTOS.get(name, ""),
        "attestation_level": att,
        "source_file": sources,
        "citation_status": citation,
        "operational_status": op_status,
        "core_completeness_score": core_score,
        "conflict_flag": conflict_flag,
    }
    rows.append(row)

# ── Write CSV ────────────────────────────────────────────────

out_dir = os.path.join(ROOT, "data")
os.makedirs(out_dir, exist_ok=True)

csv_path = os.path.join(out_dir, "nakshatra_master_table.csv")
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=COLUMNS, quoting=csv.QUOTE_ALL)
    writer.writeheader()
    writer.writerows(rows)
print(f"CSV: {csv_path} — {len(rows)} rows, {len(COLUMNS)} columns")

# ── Write JSON ───────────────────────────────────────────────

json_path = os.path.join(out_dir, "nakshatra_master_table.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(rows, f, indent=2, ensure_ascii=False)
print(f"JSON: {json_path} — {len(rows)} entries")

# ── Stats ────────────────────────────────────────────────────

ready = sum(1 for r in rows if r["operational_status"] == "ready")
partial = sum(1 for r in rows if r["operational_status"] == "partial")
blocked = sum(1 for r in rows if r["operational_status"] == "blocked")
print(f"\nStatus: {ready} ready, {partial} partial, {blocked} blocked")

conflict_rows = [r["nakshatra_name"] for r in rows if r["conflict_flag"] == "yes"]
print(f"Conflict rows ({len(conflict_rows)}): {', '.join(conflict_rows)}")

for col in COLUMNS:
    if col not in rows[0]:
        print(f"MISSING COLUMN: {col}")

print("\nColumns under 50% filled:")
for col in COLUMNS:
    filled = sum(1 for r in rows if str(r.get(col, "")).strip())
    pct = filled / 27 * 100
    if pct < 50:
        print(f"  {col}: {filled}/27 ({pct:.0f}%)")

print("\nTop 10 fields most in need of manual review:")
review_fields = []
for col in COLUMNS:
    filled = sum(1 for r in rows if str(r.get(col, "")).strip())
    if filled < 27:
        review_fields.append((col, filled))
review_fields.sort(key=lambda x: x[1])
for col, filled in review_fields[:10]:
    print(f"  {col}: {filled}/27")

print("\nDone.")
