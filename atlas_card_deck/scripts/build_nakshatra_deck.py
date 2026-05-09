#!/usr/bin/env python3
"""
Build lean nakshatra deck dataset — 27 rows, 20 columns.
Yoni resolved from species_relations.csv (BPHS-grounded).
"""

import csv, json, os

ROOT = os.path.expanduser("~/atlas_core")

def load_csv(rel):
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p): return []
    with open(p, encoding="utf-8") as f: return list(csv.DictReader(f))

# ── Sources ──────────────────────────────────────────────────

canonical = {r["nakshatra"]: r for r in load_csv("datasets/astro/nakshatra_canonical.csv")}

# BPHS yoni from species_relations.csv (lines 90-116)
SPECIES_ID_TO_NAME = {
    "ashva": "Horse", "gaja": "Elephant", "mesha": "Sheep",
    "sarpa": "Serpent", "shvan": "Dog", "marjara": "Cat",
    "mushaka": "Mouse", "go": "Cow", "mahisha": "Buffalo",
    "vyaghra": "Tiger", "shasha": "Hare", "vanara": "Monkey",
    "nakula": "Mongoose", "simha": "Lion",
}

bphs_yoni = {}  # name -> "Animal (gender)"
for r in load_csv("datasets/relations/species_relations.csv"):
    if r["relation"] != "nakshatra_yoni": continue
    nak_raw = r["from_id"].replace("nakshatra:", "")
    # Normalize to title case with spaces
    nak = nak_raw.replace("_", " ").title()
    nak = nak.replace("Dhanishtha", "Dhanishta")
    animal_id = r["to_id"].replace("species:", "")
    animal = SPECIES_ID_TO_NAME.get(animal_id, animal_id)
    gender = "male" if "yoni_male" in r["notes"] else "female"
    bphs_yoni[nak] = f"{animal} ({gender})"

plants_raw = load_csv("datasets/plants/nakshatra_plants.csv")
plants = {}
for r in plants_raw:
    n = r["nakshatra"]
    if n == "Dhanishtha": n = "Dhanishta"
    if n == "Purvashadha": n = "Purva Ashadha"
    if n == "Uttarashadha": n = "Uttara Ashadha"
    plants[n] = r

# ── Constants ────────────────────────────────────────────────

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

def zodiac_span(i):
    s = i * (360/27); e = (i+1) * (360/27)
    def fmt(d):
        si = int(d/30) % 12; rem = d % 30
        return f"{int(rem):02d}d{int((rem-int(rem))*60):02d}m {RASHIS[si]}"
    return f"{fmt(s)} - {fmt(e)}"

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

PANEL = {
    "Ashwini": "warm bg; twin horse heads flanking; swift diagonal lines",
    "Bharani": "earth tones; yoni triangle center; heavy border",
    "Krittika": "flame gradient; razor motif top; sharp horizontal divide",
    "Rohini": "cream/green; chariot center; lush organic border",
    "Mrigashira": "bisected earth/air; deer silhouette; wandering path",
    "Ardra": "dark storm wash; single teardrop focal; jagged edges",
    "Punarvasu": "golden air; quiver motif; return-arrow arc",
    "Pushya": "deep blue-green; lotus center; concentric rings",
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

# ── Build ────────────────────────────────────────────────────

COLS = [
    "deck_id", "nakshatra_number", "nakshatra_name", "zodiac_span",
    "deity", "planetary_lord", "sacred_symbol", "shakti_statement",
    "yoni_animal", "primary_plant", "gana", "nadi",
    "gift_expression", "shadow_expression",
    "visual_palette_logic", "panel_layout",
    "attestation_level", "source_file", "citation_status", "operational_status",
]

CORE = {"deck_id", "nakshatra_number", "nakshatra_name", "zodiac_span",
        "deity", "planetary_lord", "sacred_symbol", "shakti_statement",
        "yoni_animal", "primary_plant", "gana", "nadi",
        "attestation_level", "source_file", "citation_status"}

rows = []
for i, name in enumerate(NAMES):
    c = canonical.get(name, {})
    p = plants.get(name, {})

    yoni = bphs_yoni.get(name, "")
    plant = p.get("plant", "") or p.get("common_name", "")
    gift, shadow = GIFT_SHADOW.get(name, ("", ""))
    color = c.get("color_hex", "")
    element = c.get("element", "")
    palette = f"{color}; {element}-toned" if color else ""
    panel = PANEL.get(name, "")

    sources = "datasets/astro/nakshatra_canonical.csv; datasets/relations/species_relations.csv"
    if p: sources += "; datasets/plants/nakshatra_plants.csv"

    # All core fields present for every row; yoni resolved from BPHS source
    citation = "extracted"
    op = "ready"

    # Check core completeness
    row = {
        "deck_id": f"nak_{i+1:02d}",
        "nakshatra_number": i + 1,
        "nakshatra_name": name,
        "zodiac_span": zodiac_span(i),
        "deity": c.get("deity", ""),
        "planetary_lord": c.get("graha", ""),
        "sacred_symbol": c.get("symbol", ""),
        "shakti_statement": c.get("shakti", ""),
        "yoni_animal": yoni,
        "primary_plant": plant,
        "gana": c.get("gana", ""),
        "nadi": c.get("nadi", ""),
        "gift_expression": gift,
        "shadow_expression": shadow,
        "visual_palette_logic": palette,
        "panel_layout": panel,
        "attestation_level": "canon",
        "source_file": sources,
        "citation_status": citation,
        "operational_status": op,
    }

    # Verify no missing core fields
    missing = [k for k in CORE if not str(row.get(k, "")).strip()]
    if missing:
        row["operational_status"] = "partial"
        row["citation_status"] = "inferred"

    rows.append(row)

# ── Write ────────────────────────────────────────────────────

out = os.path.join(ROOT, "data")
os.makedirs(out, exist_ok=True)

csv_path = os.path.join(out, "nakshatra_deck.csv")
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
    w.writeheader()
    w.writerows(rows)

json_path = os.path.join(out, "nakshatra_deck.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(rows, f, indent=2, ensure_ascii=False)

# ── Report ───────────────────────────────────────────────────

ready = sum(1 for r in rows if r["operational_status"] == "ready")
partial = sum(1 for r in rows if r["operational_status"] == "partial")
blocked = sum(1 for r in rows if r["operational_status"] == "blocked")

print(f"CSV:  {csv_path} — {len(rows)} rows, {len(COLS)} columns")
print(f"JSON: {json_path}")
print(f"Status: {ready} ready / {partial} partial / {blocked} blocked")

# Check fill
for col in COLS:
    filled = sum(1 for r in rows if str(r.get(col, "")).strip())
    if filled < 27:
        print(f"  {col}: {filled}/27")

if ready == 27:
    print("All 27 rows deck-ready.")
