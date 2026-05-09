#!/usr/bin/env python3
"""
Generate v2 image prompts for 27 nakshatra cards from nakshatra_deck.json.
Outputs: prompts/nakshatra_card_prompts.json, docs/nakshatra_prompt_review.md

v2 changes:
- Rajput/Mewar style anchor (strong generator training signal)
- Per-deity canonical iconography (27-entry lookup)
- Per-plant visual cues (27-entry lookup)
- Yoni animal composition role (vahana/companion/ambient/emblematic)
- Natural-language color (no hex in front_image_prompt)
- Expanded negative prompt
"""

import json, os

ROOT = os.path.expanduser("~/atlas_core")

with open(os.path.join(ROOT, "data", "nakshatra_deck.json"), encoding="utf-8") as f:
    deck = json.load(f)

# ── Style anchor ─────────────────────────────────────────────

STYLE = (
    "Rajput miniature painting style, Mewar school, "
    "flat jewel-tone color fields, fine gold leaf detailing, "
    "black outline, vertical portrait composition, ornamental border"
)

NEG = (
    "photorealistic, glossy, generic fantasy, western tarot imagery, "
    "RWS/Rider-Waite imagery, text overlays, watermark, blurry, "
    "extra fingers, deformed, anime, Disney, digital painting style, "
    "modern graphic design, sanskrit text, devanagari script in image"
)

# ── Deity iconography (canonical specifics) ──────────────────

DEITY_ICON = {
    "Ashwini Kumaras": "twin horse-headed physicians side by side, each holding a golden healing vessel, youthful radiant forms",
    "Yama": "dark-skinned lord of death, seated on buffalo vahana, holding noose (pasha) and staff (danda), red garments, stern composure",
    "Agni": "red-skinned fire god, seven tongues of flame rising from crown, multi-armed holding ghee ladle and japa mala, riding a ram",
    "Brahma": "four-headed four-armed creator, seated on lotus, holding Vedas scroll and water vessel (kamandalu), white beard, serene",
    "Soma": "cool blue-skinned moon deity, holding chalice of amrita, crescent moon on brow, seated on antelope, luminous",
    "Rudra": "three-eyed fierce ascetic, tiger-skin garment, holding trident and damaru drum, ash-smeared body, matted locks piled high",
    "Aditi": "maternal cosmic mother, radiant halo of twelve suns around her head, seated in lotus posture, open-palmed blessing gesture",
    "Brihaspati": "golden-skinned guru with chin-beard, holding teaching staff (danda) and rudraksha rosary, seated on lotus, wise expression",
    "Nagas": "multi-hooded serpent deities, jeweled cobra hoods raised, coiled lower bodies, luminous gem in central hood",
    "Pitris": "three elder ancestral figures seated in row, white garments, offerings of rice and water before them, dignified stillness",
    "Bhaga": "red-gold solar deity of fortune, holding lotus in right hand, dawn light behind, regal standing posture",
    "Aryaman": "golden-complexioned friend-god, seated on chariot, holding contract scroll, solar disc behind head",
    "Savitar": "solar-golden deity, two right hands raised in blessing mudra (abhaya and varada), radiating light-lines from palms",
    "Tvashtar": "divine architect-artisan, holding hammer and compass, mandala blueprint visible, creating cosmic forms at a workbench",
    "Vayu": "blue-green wind god, striding forward dynamically, holding banner that streams behind, garments wind-swept, powerful build",
    "Indra-Agni": "dual deity — Indra (right, holding vajra thunderbolt, crowned) and Agni (left, flame-tongued, holding ladle) sharing one throne",
    "Mitra": "solar friend-god, gentle golden complexion, holding lotus and sun disc, seated on chariot, benevolent expression",
    "Indra": "king of devas, crowned with kirita-mukuta, vajra thunderbolt in right hand, seated regally on white elephant Airavata",
    "Nirriti": "dark fierce goddess of dissolution, matted hair, seated on black dog, holding tangled roots and a skull, southwest quarter",
    "Apas": "water nymphs (three flowing feminine forms), holding conch and lotus, turquoise-blue skin, emerging from waves",
    "Vishvadevas": "assembly of ten devas in two rows, each holding different attribute, collective regal composition, sunburst behind group",
    "Vishnu": "dark-blue four-armed preserver, holding conch (shankha), discus (sudarshana), mace (gada), lotus (padma), standing on lotus",
    "Vasus": "eight elemental deities grouped in circle, drums and instruments present, each in distinct color, communal energy",
    "Varuna": "blue-black ocean lord, holding noose (pasha), seated on makara sea-creature, oceanic waves as background, stern gaze",
    "Aja Ekapada": "one-footed goat-headed ascetic deity, fierce expression, single leg planted in fire, lightning around form",
    "Ahirbudhnya": "great serpent of the cosmic depths, coiled massive form, jeweled hood, oceanic underworld setting, patient stillness",
    "Pushan": "gentle golden nourisher, holding goad, soft features, guardian of paths, cow visible nearby, benevolent pastoral setting",
}

# ── Plant visual cues ────────────────────────────────────────

PLANT_CUE = {
    "Ashwagandha": "low shrub with small red-orange berries among oval green leaves in the border",
    "Amla": "round ribbed green gooseberries clustered on feathery pinnate-leafed branches in the border",
    "Fig": "round figs clustered directly on trunk and thick branches, broad lobed leaves framing edges",
    "Jasmine": "white five-petaled star-shaped jasmine flowers with deep green leaves woven as garland",
    "Khadira": "thorny acacia branch with small yellow pom-pom flower clusters and pinnate leaves in border",
    "Agarwood": "dark resinous wood fragments and small white flower clusters in border corners",
    "Bamboo": "tall segmented green bamboo culms with narrow leaves framing the card sides",
    "Peepal": "heart-shaped leaves with elongated drip-tips, fluttering on slender petioles as border motif",
    "Nagakesara": "waxy white four-petaled flowers with golden stamen clusters in the border",
    "Banyan": "broad canopy with descending aerial roots, thick oval leaves as frame elements",
    "Palasha": "brilliant orange-red flame-of-forest flowers on bare branches, trifoliate leaves in border",
    "Rudraksha": "blue-brown ridged rudraksha berries on branch with elliptic leaves in border",
    "Soapnut": "round brown soapnut fruits and pinnate compound leaves in border corners",
    "Bael": "trifoliate bilva leaves (three pointed leaflets) and hard yellow-green fruit in border",
    "Arjuna": "arjuna tree bark strips and small pale flower clusters in border",
    "Wood Apple": "hard round wood apple fruit and compound leaves in border corners",
    "Tulsi": "small dark-green aromatic tulsi leaves with purple stems and tiny flower spikes in border",
    "Silk Cotton": "red silk-cotton flowers on thorny trunk, kapok pods splitting open in border",
    "Sal": "broad sal leaves and small cream-yellow flower clusters in border",
    "Lotus": "open pink lotus blooms and round floating leaves as border and base motif",
    "Jackfruit": "large oblong spiny jackfruit and broad dark leaves in border",
    "Arka": "crown flower with waxy purple-white five-petaled blooms and thick round leaves in border",
    "Shami": "tiny bipinnate leaves and small yellow flower clusters of prosopis in border",
    "Kadamba": "spherical orange kadamba flower-balls and broad round leaves in border",
    "Mango": "broad lance-shaped mango leaves in red-green new-growth colors, small fruit clusters in border",
    "Neem": "pinnate compound neem leaves with small white flower sprays in border",
    "Mahua": "fleshy cream-yellow mahua flowers dropping from branches, broad leaves in border",
}

# ── Yoni animal role & composition ───────────────────────────
# vahana: deity rides/sits on the animal
# companion: animal beside deity at similar scale
# ambient: animal in background/landscape, not foregrounded
# emblematic: animal IS the primary symbol (deity is abstract/group)

YONI_ROLE = {
    "Ashwini":           ("companion", "two golden horses flanking the twin physicians"),
    "Bharani":           ("vahana", "Yama seated on his buffalo, with a tusked elephant standing guard at card base"),
    "Krittika":          ("vahana", "Agni riding his ram, a sheep resting at the base of the flames"),
    "Rohini":            ("ambient", "a serpent coiled peacefully among jasmine vines at the card base"),
    "Mrigashira":        ("ambient", "a serpent coiled in moonlit grass at the deity's feet, deer-head symbol at card top"),
    "Ardra":             ("companion", "a loyal dog sitting beside Rudra in the storm"),
    "Punarvasu":         ("ambient", "a cat resting in bamboo shade at the card base"),
    "Pushya":            ("ambient", "a sheep grazing beneath the peepal tree at the card base"),
    "Ashlesha":          ("emblematic", "the Naga serpent deities ARE the central figures, a small cat curled at base"),
    "Magha":             ("ambient", "a mouse near the offerings at the foot of the throne"),
    "Purva Phalguni":    ("ambient", "a small mouse nestled in the hammock folds"),
    "Uttara Phalguni":   ("companion", "a bull (cow, male) standing steady beside Aryaman's chariot"),
    "Hasta":             ("ambient", "a water buffalo visible in the field behind Savitar"),
    "Chitra":            ("companion", "a tiger seated at Tvashtar's workbench side"),
    "Swati":             ("ambient", "a buffalo silhouette in the wind-swept landscape behind Vayu"),
    "Vishakha":          ("ambient", "a tigress prowling beneath the triumphal arch"),
    "Anuradha":          ("companion", "a hare seated beside Mitra on the lotus platform"),
    "Jyeshtha":          ("ambient", "a hare crouched near the base of Indra's elephant"),
    "Mula":              ("companion", "a dog at the goddess's side, both surrounded by tangled roots"),
    "Purva Ashadha":     ("ambient", "a monkey perched on a branch above the water nymphs"),
    "Uttara Ashadha":    ("ambient", "a mongoose among rocks at the assembly's base"),
    "Shravana":          ("ambient", "a monkey in a listening pose in the background landscape"),
    "Dhanishta":         ("companion", "a lion seated among the eight Vasu deities"),
    "Shatabhisha":       ("ambient", "a mare (female horse) at the ocean shore behind Varuna"),
    "Purva Bhadrapada":  ("companion", "a lioness at the base of the one-footed fire deity"),
    "Uttara Bhadrapada": ("ambient", "a cow resting on the shore above the oceanic depths"),
    "Revati":            ("companion", "a gentle elephant walking beside Pushan on the path"),
}

# ── Hex to natural language color ────────────────────────────

HEX_TO_NATURAL = {
    "#8d784f": "warm bronze-brown",
    "#ffa9dc": "soft mauve-pink",
    "#ffb300": "bright saffron-amber",
    "#e7e7ff": "pale moonlit lavender",
    "#922610": "deep burnt sienna",
    "#4e0d7a": "dark storm-violet",
    "#ffe574": "warm golden-yellow",
    "#4e6175": "deep slate-blue",
    "#0d7a39": "dark emerald-green",
    "#685d48": "aged bronze-earth",
    "#ffbe26": "rich amber-gold",
    "#ffffff": "luminous silver-white",
    "#ffdd43": "bright turmeric-gold",
    "#6500aa": "deep royal-violet",
    "#cc2100": "fierce vermilion-red",
    "#e5c11c": "burning gold",
    "#00c34e": "living sea-green",
}

def natural_color(hex_str):
    """Convert hex to natural language, with fallback."""
    h = hex_str.strip().lower()
    return HEX_TO_NATURAL.get(h, f"muted tone ({h})")

def element_mood(elem):
    """Element to tonal mood descriptor."""
    return {
        "fire": "warm and radiant",
        "earth": "grounded and rich",
        "water": "cool and deep",
        "air": "luminous and open",
    }.get(elem, "balanced")

# ── Build prompts ────────────────────────────────────────────

def build_prompt(r):
    name = r["nakshatra_name"]
    deity = r["deity"]
    symbol = r["sacred_symbol"].replace("_", " ")
    plant = r["primary_plant"]
    layout = r["panel_layout"]

    # Parse hex and element from visual_palette_logic
    parts = r["visual_palette_logic"].split(";")
    hex_val = parts[0].strip() if parts else ""
    elem_tone = parts[1].strip().replace("-toned", "").strip() if len(parts) > 1 else ""
    color_name = natural_color(hex_val)
    mood = element_mood(elem_tone)

    # Deity iconography
    deity_desc = DEITY_ICON.get(deity, f"{deity} in traditional Vedic form")

    # Plant cue
    plant_cue = PLANT_CUE.get(plant, f"{plant.lower()} botanical elements in the border")

    # Yoni role
    yoni_role_type, yoni_desc = YONI_ROLE.get(name, ("ambient", f"{r['yoni_animal'].split(' (')[0].lower()} visible in background"))

    # Front image prompt
    # Fix article: "a" vs "an"
    article = "An" if symbol[0].lower() in "aeiou" else "A"
    front = (
        f"{deity_desc}. "
        f"{article} {symbol} motif is inscribed or integrated into the composition. "
        f"{yoni_desc[0].upper() + yoni_desc[1:]}. "
        f"{plant_cue[0].upper() + plant_cue[1:]}. "
        f"Composition: {layout}. "
        f"Dominant color: {color_name}, overall mood {mood}. "
        f"{STYLE}."
    )

    # Symbol prompt (keep hex for production use)
    sym = (
        f"Isolated symbolic glyph of a {symbol}, "
        f"stylized in fine gold linework on matte {color_name} background. "
        f"No text, no figures. "
        f"{STYLE}."
    )

    # Palette prompt (hex preserved here for print pipeline)
    pal = (
        f"Color swatch: primary {hex_val} ({color_name}), "
        f"mood: {mood}, "
        f"accent: gold leaf. "
        f"Matte, flat, print-ready."
    )

    caption = f"{name} · {deity} · {r['shakti_statement']} · {r['planetary_lord']}"
    short = f"{name} — {r['shakti_statement']}"

    return {
        "deck_id": r["deck_id"],
        "nakshatra_name": name,
        "short_title": short,
        "front_image_prompt": front,
        "back_caption": caption,
        "symbol_prompt": sym,
        "palette_prompt": pal,
        "negative_prompt": NEG,
    }

prompts = [build_prompt(r) for r in deck]

# ── Write JSON ───────────────────────────────────────────────

out_json = os.path.join(ROOT, "prompts", "nakshatra_card_prompts.json")
os.makedirs(os.path.dirname(out_json), exist_ok=True)
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(prompts, f, indent=2, ensure_ascii=False)
print(f"Prompts JSON: {out_json} — {len(prompts)} cards")

# ── Write review doc ─────────────────────────────────────────

lines = [
    "# Nakshatra Card Prompts — Review Document (v2)",
    "",
    "**Generated**: 2026-04-23",
    "**Source**: `data/nakshatra_deck.json`",
    "**Output**: `prompts/nakshatra_card_prompts.json`",
    f"**Style**: {STYLE}",
    "",
    "---",
    "",
]

for p, r in zip(prompts, deck):
    lines.extend([
        f"## {r['nakshatra_number']}. {r['nakshatra_name']}",
        "",
        "### Source fields",
        "",
        f"- **deity**: {r['deity']}",
        f"- **planetary_lord**: {r['planetary_lord']}",
        f"- **sacred_symbol**: {r['sacred_symbol']}",
        f"- **shakti**: {r['shakti_statement']}",
        f"- **yoni_animal**: {r['yoni_animal']}",
        f"- **primary_plant**: {r['primary_plant']}",
        f"- **visual_palette_logic**: {r['visual_palette_logic']}",
        f"- **panel_layout**: {r['panel_layout']}",
        "",
        "### Image prompt",
        "",
        f"> {p['front_image_prompt']}",
        "",
        "### Caption",
        "",
        f"`{p['back_caption']}`",
        "",
        "---",
        "",
    ])

review_path = os.path.join(ROOT, "docs", "nakshatra_prompt_review.md")
with open(review_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"Review doc: {review_path}")

print("Done.")
