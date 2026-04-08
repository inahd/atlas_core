"""
graph_seed_data.py — Seeds the graph with vocal-relational data.

All seeded as stability: working, authority: sadhu.
Includes: matrika phonemes, gamaka types, bhava states,
svara-raga-rasa triangles, tala breath positions.
"""

# ──────────────────────────────────────────────────────────────
# MATRIKA PHONEMES — the 50 sound-mothers of Sanskrit
# ──────────────────────────────────────────────────────────────
# Each phoneme is a node in the graph with element, chakra, deity,
# rasa, and formant profile (F1, F2, F3, bw) for SC synthesis.
#
# Formant profiles are for a male-register vocal fundamental (~120Hz).
# F1/F2 positions from Peterson & Barney (1952) adapted to Sanskrit.

MATRIKA_PHONEMES = [
    # Vowels (svara-varna)
    {"syllable": "a",    "element": "ether", "chakra": "vishuddha",  "deity": "brahma",    "rasa": "shanta",    "f1": 800, "f2": 1200, "f3": 2500, "bw": 80},
    {"syllable": "aa",   "element": "ether", "chakra": "vishuddha",  "deity": "brahma",    "rasa": "shanta",    "f1": 850, "f2": 1100, "f3": 2500, "bw": 90},
    {"syllable": "i",    "element": "air",   "chakra": "ajna",       "deity": "saraswati", "rasa": "shringara", "f1": 300, "f2": 2300, "f3": 3100, "bw": 55},
    {"syllable": "ee",   "element": "air",   "chakra": "ajna",       "deity": "saraswati", "rasa": "shringara", "f1": 280, "f2": 2400, "f3": 3200, "bw": 50},
    {"syllable": "u",    "element": "water",  "chakra": "svadhisthana","deity": "vishnu",   "rasa": "karuna",    "f1": 350, "f2": 650,  "f3": 2400, "bw": 60},
    {"syllable": "oo",   "element": "water",  "chakra": "svadhisthana","deity": "vishnu",   "rasa": "karuna",    "f1": 320, "f2": 600,  "f3": 2400, "bw": 65},
    {"syllable": "ri",   "element": "fire",   "chakra": "manipura",   "deity": "agni",     "rasa": "vira",      "f1": 350, "f2": 1800, "f3": 2800, "bw": 60},
    {"syllable": "e",    "element": "air",    "chakra": "anahata",    "deity": "vayu",     "rasa": "adbhuta",   "f1": 500, "f2": 1900, "f3": 2600, "bw": 70},
    {"syllable": "ai",   "element": "fire",   "chakra": "manipura",   "deity": "agni",     "rasa": "raudra",    "f1": 700, "f2": 1800, "f3": 2600, "bw": 75},
    {"syllable": "o",    "element": "water",  "chakra": "svadhisthana","deity": "varuna",   "rasa": "karuna",    "f1": 500, "f2": 800,  "f3": 2400, "bw": 80},
    {"syllable": "au",   "element": "earth",  "chakra": "muladhara",  "deity": "prithvi",  "rasa": "bibhatsa",  "f1": 600, "f2": 900,  "f3": 2400, "bw": 85},
    {"syllable": "am",   "element": "ether",  "chakra": "sahasrara",  "deity": "shiva",    "rasa": "shanta",    "f1": 700, "f2": 1100, "f3": 2600, "bw": 80},
    {"syllable": "ah",   "element": "ether",  "chakra": "sahasrara",  "deity": "shiva",    "rasa": "shanta",    "f1": 800, "f2": 1200, "f3": 2500, "bw": 80},
    # Guttural (kanthya) — ka-varga
    {"syllable": "ka",   "element": "fire",   "chakra": "muladhara",  "deity": "agni",     "rasa": "raudra",    "f1": 750, "f2": 1100, "f3": 2400, "bw": 85},
    {"syllable": "kha",  "element": "fire",   "chakra": "muladhara",  "deity": "agni",     "rasa": "raudra",    "f1": 750, "f2": 1200, "f3": 2500, "bw": 80},
    {"syllable": "ga",   "element": "fire",   "chakra": "muladhara",  "deity": "ganesha",  "rasa": "vira",      "f1": 750, "f2": 1100, "f3": 2400, "bw": 85},
    {"syllable": "gha",  "element": "fire",   "chakra": "muladhara",  "deity": "ganesha",  "rasa": "vira",      "f1": 750, "f2": 1100, "f3": 2500, "bw": 80},
    {"syllable": "nga",  "element": "fire",   "chakra": "muladhara",  "deity": "ganesha",  "rasa": "shanta",    "f1": 650, "f2": 1100, "f3": 2500, "bw": 90},
    # Palatal (talavya) — cha-varga
    {"syllable": "cha",  "element": "air",    "chakra": "svadhisthana","deity": "vayu",     "rasa": "adbhuta",   "f1": 600, "f2": 1800, "f3": 2800, "bw": 70},
    {"syllable": "chha", "element": "air",    "chakra": "svadhisthana","deity": "vayu",     "rasa": "adbhuta",   "f1": 600, "f2": 1900, "f3": 2800, "bw": 65},
    {"syllable": "ja",   "element": "air",    "chakra": "svadhisthana","deity": "indra",    "rasa": "vira",      "f1": 650, "f2": 1700, "f3": 2700, "bw": 75},
    {"syllable": "jha",  "element": "air",    "chakra": "svadhisthana","deity": "indra",    "rasa": "vira",      "f1": 650, "f2": 1700, "f3": 2700, "bw": 75},
    {"syllable": "nya",  "element": "air",    "chakra": "svadhisthana","deity": "indra",    "rasa": "shanta",    "f1": 600, "f2": 1800, "f3": 2700, "bw": 80},
    # Cerebral (murdhanya) — ta-varga (retroflex)
    {"syllable": "ta",   "element": "fire",   "chakra": "manipura",   "deity": "rudra",    "rasa": "raudra",    "f1": 700, "f2": 1200, "f3": 2600, "bw": 80},
    {"syllable": "tha",  "element": "fire",   "chakra": "manipura",   "deity": "rudra",    "rasa": "raudra",    "f1": 700, "f2": 1300, "f3": 2600, "bw": 75},
    {"syllable": "da",   "element": "fire",   "chakra": "manipura",   "deity": "rudra",    "rasa": "vira",      "f1": 700, "f2": 1200, "f3": 2600, "bw": 80},
    {"syllable": "dha",  "element": "fire",   "chakra": "manipura",   "deity": "rudra",    "rasa": "vira",      "f1": 650, "f2": 1200, "f3": 2500, "bw": 85},
    {"syllable": "na",   "element": "earth",  "chakra": "manipura",   "deity": "prithvi",  "rasa": "karuna",    "f1": 650, "f2": 1100, "f3": 2700, "bw": 80},
    # Dental (dantya) — ta-varga
    {"syllable": "tha_d","element": "earth",  "chakra": "anahata",    "deity": "vayu",     "rasa": "shanta",    "f1": 650, "f2": 1400, "f3": 2700, "bw": 75},
    {"syllable": "da_d", "element": "earth",  "chakra": "anahata",    "deity": "vayu",     "rasa": "shanta",    "f1": 650, "f2": 1400, "f3": 2600, "bw": 80},
    {"syllable": "na_d", "element": "earth",  "chakra": "anahata",    "deity": "vayu",     "rasa": "karuna",    "f1": 650, "f2": 1100, "f3": 2600, "bw": 85},
    # Labial (oshthya) — pa-varga
    {"syllable": "pa",   "element": "water",  "chakra": "anahata",    "deity": "vishnu",   "rasa": "hasya",     "f1": 700, "f2": 1000, "f3": 2500, "bw": 85},
    {"syllable": "pha",  "element": "water",  "chakra": "anahata",    "deity": "vishnu",   "rasa": "hasya",     "f1": 700, "f2": 1100, "f3": 2500, "bw": 80},
    {"syllable": "ba",   "element": "water",  "chakra": "anahata",    "deity": "vishnu",   "rasa": "shringara", "f1": 700, "f2": 1000, "f3": 2500, "bw": 90},
    {"syllable": "bha",  "element": "water",  "chakra": "anahata",    "deity": "vishnu",   "rasa": "shringara", "f1": 700, "f2": 1100, "f3": 2500, "bw": 85},
    {"syllable": "ma",   "element": "water",  "chakra": "anahata",    "deity": "vishnu",   "rasa": "karuna",    "f1": 350, "f2": 900,  "f3": 2300, "bw": 90},
    # Semivowels (antahstha)
    {"syllable": "ya",   "element": "air",    "chakra": "anahata",    "deity": "vayu",     "rasa": "shringara", "f1": 350, "f2": 2100, "f3": 2900, "bw": 65},
    {"syllable": "ra",   "element": "fire",   "chakra": "manipura",   "deity": "agni",     "rasa": "vira",      "f1": 500, "f2": 1300, "f3": 2600, "bw": 75},
    {"syllable": "la",   "element": "earth",  "chakra": "muladhara",  "deity": "prithvi",  "rasa": "shanta",    "f1": 600, "f2": 1100, "f3": 2500, "bw": 80},
    {"syllable": "va",   "element": "water",  "chakra": "svadhisthana","deity": "varuna",   "rasa": "shringara", "f1": 600, "f2": 1100, "f3": 2500, "bw": 80},
    # Sibilants (ushman)
    {"syllable": "sha",  "element": "ether",  "chakra": "vishuddha",  "deity": "shiva",    "rasa": "shanta",    "f1": 600, "f2": 1800, "f3": 2800, "bw": 70},
    {"syllable": "sha_r","element": "fire",   "chakra": "ajna",       "deity": "rudra",    "rasa": "raudra",    "f1": 600, "f2": 1900, "f3": 2900, "bw": 65},
    {"syllable": "sa",   "element": "ether",  "chakra": "sahasrara",  "deity": "saraswati","rasa": "shanta",    "f1": 600, "f2": 1700, "f3": 2800, "bw": 70},
    {"syllable": "ha",   "element": "ether",  "chakra": "sahasrara",  "deity": "shiva",    "rasa": "shanta",    "f1": 700, "f2": 1200, "f3": 2500, "bw": 80},
    # Composite bija (from bija_master.csv)
    {"syllable": "om",   "element": "ether",  "chakra": "sahasrara",  "deity": "universal","rasa": "shanta",    "f1": 600, "f2": 1000, "f3": 2400, "bw": 90},
    {"syllable": "hrim", "element": "fire",   "chakra": "anahata",    "deity": "devi",     "rasa": "shringara", "f1": 350, "f2": 2000, "f3": 2900, "bw": 65},
    {"syllable": "shrim","element": "water",  "chakra": "anahata",    "deity": "lakshmi",  "rasa": "shringara", "f1": 400, "f2": 1800, "f3": 2800, "bw": 70},
    {"syllable": "klim", "element": "air",    "chakra": "svadhisthana","deity": "krishna",  "rasa": "shringara", "f1": 300, "f2": 2200, "f3": 3000, "bw": 60},
    {"syllable": "gam",  "element": "earth",  "chakra": "muladhara",  "deity": "ganesha",  "rasa": "shanta",    "f1": 700, "f2": 1100, "f3": 2400, "bw": 90},
    {"syllable": "aim",  "element": "air",    "chakra": "ajna",       "deity": "saraswati","rasa": "shanta",    "f1": 700, "f2": 1800, "f3": 2600, "bw": 75},
]


# ──────────────────────────────────────────────────────────────
# GAMAKA TYPES — ornaments are relational
# ──────────────────────────────────────────────────────────────

GAMAKA_TYPES = {
    "meend": {
        "element": "water",
        "intensity": 0.7,
        "sc_params": {"type": 0, "depth_min": 50, "depth_max": 200, "rate_min": 0.0, "rate_max": 0.0, "dur_min": 0.1, "dur_max": 0.4},
        "characteristic_of": ["Darbari", "Marwa", "Todi", "Bageshri"],
        "used_on": ["g", "d", "n", "r"],  # komal notes primarily
    },
    "andolan": {
        "element": "air",
        "intensity": 0.5,
        "sc_params": {"type": 1, "depth_min": 30, "depth_max": 80, "rate_min": 1.0, "rate_max": 3.0, "dur_min": 0.3, "dur_max": 1.0},
        "characteristic_of": ["Bhairava", "Bhairavi", "Darbari"],
        "used_on": ["g", "d", "G", "r"],
    },
    "murki": {
        "element": "fire",
        "intensity": 0.8,
        "sc_params": {"type": 2, "depth_min": 80, "depth_max": 150, "rate_min": 8.0, "rate_max": 14.0, "dur_min": 0.05, "dur_max": 0.15},
        "characteristic_of": ["Bhimpalasi", "Bageshri", "Yaman"],
        "used_on": ["G", "M", "D", "N"],
    },
    "kan": {
        "element": "ether",
        "intensity": 0.3,
        "sc_params": {"type": 3, "depth_min": 100, "depth_max": 200, "rate_min": 0.0, "rate_max": 0.0, "dur_min": 0.02, "dur_max": 0.04},
        "characteristic_of": ["Yaman", "Bilawal", "Sarang"],
        "used_on": ["G", "N", "D", "R"],
    },
    "gamak": {
        "element": "fire",
        "intensity": 0.9,
        "sc_params": {"type": 4, "depth_min": 80, "depth_max": 150, "rate_min": 5.0, "rate_max": 8.0, "dur_min": 0.1, "dur_max": 0.3},
        "characteristic_of": ["Bhairava", "Darbari", "Marwa"],
        "used_on": ["g", "d", "r", "n"],
    },
    "mind": {
        "element": "water",
        "intensity": 0.6,
        "sc_params": {"type": 5, "depth_min": 200, "depth_max": 700, "rate_min": 0.0, "rate_max": 0.0, "dur_min": 0.3, "dur_max": 0.8},
        "characteristic_of": ["Darbari", "Todi"],
        "used_on": ["g", "d", "n"],
    },
    "sparsh": {
        "element": "ether",
        "intensity": 0.2,
        "sc_params": {"type": 6, "depth_min": 100, "depth_max": 200, "rate_min": 0.0, "rate_max": 0.0, "dur_min": 0.015, "dur_max": 0.025},
        "characteristic_of": ["Yaman", "Bilawal", "Sarang"],
        "used_on": ["G", "N", "D"],
    },
    "khatka": {
        "element": "fire",
        "intensity": 0.7,
        "sc_params": {"type": 7, "depth_min": 100, "depth_max": 200, "rate_min": 10.0, "rate_max": 16.0, "dur_min": 0.03, "dur_max": 0.08},
        "characteristic_of": ["Bhimpalasi", "Bhairavi", "Bageshri"],
        "used_on": ["M", "P", "G", "g"],
    },
    # ── Planetary gamakas — each planet's gaze quality ────────
    "kampita": {
        "element": "fire",
        "intensity": 0.85,
        "sc_params": {"type": 8, "depth_min": 40, "depth_max": 120, "rate_min": 5.0, "rate_max": 9.0, "dur_min": 0.15, "dur_max": 0.5},
        "characteristic_of": [],  # assigned by swara_engine via planet
        "used_on": [],
        "planet": "graha_mangala",
    },
    "pratyahata": {
        "element": "fire",
        "intensity": 0.9,
        "sc_params": {"type": 9, "depth_min": 30, "depth_max": 60, "rate_min": 0.0, "rate_max": 0.0, "dur_min": 0.01, "dur_max": 0.03},
        "characteristic_of": [],
        "used_on": [],
        "planet": "graha_surya",
    },
    "murcchana": {
        "element": "water",
        "intensity": 0.5,
        "sc_params": {"type": 10, "depth_min": 20, "depth_max": 60, "rate_min": 0.0, "rate_max": 0.0, "dur_min": 0.15, "dur_max": 0.4},
        "characteristic_of": [],
        "used_on": [],
        "planet": "graha_shukra",
    },
    "sparsha": {
        "element": "ether",
        "intensity": 0.3,
        "sc_params": {"type": 11, "depth_min": 80, "depth_max": 180, "rate_min": 0.0, "rate_max": 0.0, "dur_min": 0.02, "dur_max": 0.04},
        "characteristic_of": [],
        "used_on": [],
        "planet": "graha_budha",
    },
}

# Gamaka type index for OSC
GAMAKA_INDEX = {name: data["sc_params"]["type"] for name, data in GAMAKA_TYPES.items()}


# ──────────────────────────────────────────────────────────────
# BHAVA STATES — emotional coloring for vocal quality
# ──────────────────────────────────────────────────────────────

BHAVA_STATES = {
    "rati":     {"rasa": "shringara", "brightness": 0.6,  "vib_rate": 5.5, "vib_depth": 0.007, "breathiness": 0.3,  "register": 0,  "arc_min": 0.2, "arc_max": 0.6},
    "utsaha":   {"rasa": "vira",      "brightness": 0.85, "vib_rate": 6.5, "vib_depth": 0.004, "breathiness": 0.05, "register": 0,  "arc_min": 0.3, "arc_max": 0.8},
    "shoka":    {"rasa": "karuna",    "brightness": 0.25, "vib_rate": 4.0, "vib_depth": 0.012, "breathiness": 0.4,  "register": -1, "arc_min": 0.0, "arc_max": 0.4},
    "vismaya":  {"rasa": "adbhuta",   "brightness": 0.75, "vib_rate": 7.0, "vib_depth": 0.009, "breathiness": 0.15, "register": 1,  "arc_min": 0.5, "arc_max": 1.0},
    "bhaya":    {"rasa": "bhayanaka", "brightness": 0.35, "vib_rate": 8.0, "vib_depth": 0.003, "breathiness": 0.5,  "register": 0,  "arc_min": 0.0, "arc_max": 0.3},
    "shanta":   {"rasa": "shanta",    "brightness": 0.45, "vib_rate": 3.5, "vib_depth": 0.005, "breathiness": 0.6,  "register": 0,  "arc_min": 0.0, "arc_max": 1.0},
    "hasya":    {"rasa": "hasya",     "brightness": 0.9,  "vib_rate": 6.0, "vib_depth": 0.006, "breathiness": 0.1,  "register": 1,  "arc_min": 0.4, "arc_max": 0.8},
    "jugupsa":  {"rasa": "bibhatsa",  "brightness": 0.15, "vib_rate": 3.0, "vib_depth": 0.015, "breathiness": 0.7,  "register": -1, "arc_min": 0.0, "arc_max": 0.2},
}

BHAVA_INDEX = {name: i for i, name in enumerate(BHAVA_STATES.keys())}


# ──────────────────────────────────────────────────────────────
# SVARA-RAGA-RASA TRIANGLES
# ──────────────────────────────────────────────────────────────
# Same swara in different ragas evokes different rasa/bhava.

SVARA_RAGA_RASA = [
    {"swara": "g", "raga": "Bhairava",  "rasa": "karuna",    "bhava": "shoka",   "ornament": "andolan"},
    {"swara": "G", "raga": "Yaman",     "rasa": "shringara", "bhava": "rati",    "ornament": "kan"},
    {"swara": "n", "raga": "Darbari",   "rasa": "karuna",    "bhava": "shoka",   "ornament": "meend"},
    {"swara": "N", "raga": "Yaman",     "rasa": "shringara", "bhava": "rati",    "ornament": "kan"},
    {"swara": "r", "raga": "Todi",      "rasa": "bibhatsa",  "bhava": "vismaya", "ornament": "andolan"},
    {"swara": "r", "raga": "Marwa",     "rasa": "vira",      "bhava": "utsaha",  "ornament": "meend"},
    {"swara": "R", "raga": "Darbari",   "rasa": "vira",      "bhava": "utsaha",  "ornament": "gamak"},
    {"swara": "M", "raga": "Bhairavi",  "rasa": "karuna",    "bhava": "shoka",   "ornament": "andolan"},
    {"swara": "M", "raga": "Bhimpalasi","rasa": "shringara", "bhava": "rati",    "ornament": "murki"},
    {"swara": "G", "raga": "Bageshri",  "rasa": "shringara", "bhava": "rati",    "ornament": "murki"},
    {"swara": "D", "raga": "Bilawal",   "rasa": "shanta",    "bhava": "shanta",  "ornament": "kan"},
    {"swara": "d", "raga": "Bhairava",  "rasa": "bhayanaka", "bhava": "bhaya",   "ornament": "andolan"},
    {"swara": "P", "raga": "Sarang",    "rasa": "shanta",    "bhava": "shanta",  "ornament": "sparsh"},
]


# ──────────────────────────────────────────────────────────────
# TALA BREATH POSITIONS
# ──────────────────────────────────────────────────────────────
# Khali beats are natural breath points. Sam is arrival, not breath.

TALA_BREATH = {
    "Teentaal": {"beats": 16, "khali": [8],           "sam": [0],  "phrase_ends": [3, 7, 11, 15]},
    "Rupak":    {"beats": 7,  "khali": [0],           "sam": [0],  "phrase_ends": [2, 4, 6]},
    "Jhaptal":  {"beats": 10, "khali": [4],           "sam": [0],  "phrase_ends": [1, 4, 6, 9]},
    "Adi":      {"beats": 8,  "khali": [4],           "sam": [0],  "phrase_ends": [3, 7]},
    "Dadra":    {"beats": 6,  "khali": [3],           "sam": [0],  "phrase_ends": [2, 5]},
    "Keherwa":  {"beats": 8,  "khali": [4],           "sam": [0],  "phrase_ends": [3, 7]},
    "Chautal":  {"beats": 12, "khali": [4],           "sam": [0],  "phrase_ends": [3, 7, 9, 11]},
}
