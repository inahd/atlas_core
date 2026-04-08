"""
natal_musician.py — Natal-aware sound interpretation layer.

Sits between raw field law and what SuperCollider plays.
Takes the natal chart (/natal) and current field (/spine)
and derives a musician reading: raga coloring, gamak emphasis,
tempo feel, rest density, phrase arc, field tensions,
rhythmic tensions — all from jyotish.
"""

# ── All 12 swaras (for tension detection) ────────────
_ALL_SWARAS = ["Sa", "re", "Re", "ga", "Ga", "ma", "Ma", "Pa", "dha", "Dha", "ni", "Ni"]
_SEMI_TO_SWARA = {i: s for i, s in enumerate(_ALL_SWARAS)}

# ── Raga scales (semitones) for secondary raga comparison ──
# Mirrors kernel.py RAGAS — just the scales we reference as secondary
_RAGA_SCALES = {
    "Bhairavī":       {0, 1, 3, 5, 7, 8, 10},
    "Darbari Kanada":  {0, 2, 3, 5, 7, 8, 10},
    "Yaman Kalyan":    {0, 2, 4, 6, 7, 9, 11},
    "Mārwā":          {0, 1, 4, 6, 7, 9, 11},
    "Bāgeshri":       {0, 2, 3, 5, 7, 9, 10},
    "Malhār":         {0, 2, 3, 5, 7, 9, 10},
    "Shree":          {0, 1, 4, 6, 7, 8, 11},
    "Pūriyā":         {0, 1, 4, 6, 7, 9, 11},
    "Bihāg":          {0, 2, 4, 5, 7, 9, 11},
    "Toḍī":           {0, 1, 3, 6, 7, 8, 11},
    "Yaman":           {0, 2, 4, 6, 7, 9, 11},
}

# ── Natal nakshatra → raga affinities ────────────────
# Each natal graha's nakshatra colors a raga tendency.
_NAK_RAGA = {
    "Rohiṇī":      "Bhairavī",       # earth, Venus — morning tenderness
    "Punarvasu":    "Darbari Kanada",  # air, Jupiter — expansive depth
    "Śravaṇa":     "Yaman Kalyan",    # air, Moon — evening listening
    "Svātī":        "Mārwā",          # air, Rahu — weightless precision
    "Anurādhā":     "Bāgeshri",       # water, Saturn — devotional intimacy
    "Ārdrā":        "Malhār",         # water, Rahu — storm, dissolution
    "Śatabhiṣā":    "Shree",          # ether, Rahu — solitude
    "Pūrvāṣāḍhā":  "Pūriyā",        # water, Venus — invincibility
    "Dhaniṣṭhā":    "Bihāg",         # ether, Mars — celebration
    "Mūla":         "Toḍī",           # fire, Ketu — uprooting
}

# Graha → swara emphasis (for gamak)
_GRAHA_SWARA = {
    "Surya":  "Re",   # Sun — clarity
    "Candra": "Sa",   # Moon — home
    "Mangala": "Pa",  # Mars — force
    "Budha":  "Ma",   # Mercury — pivot
    "Guru":   "Dha",  # Jupiter — grace
    "Sukra":  "Ga",   # Venus — beauty
    "Sani":   "Ni",   # Saturn — boundary
    "Rahu":   "Ma",   # Rahu — tivra Ma, tension
    "Ketu":   "Sa",   # Ketu — dissolution to root
}

# Graha name mapping (NATAL keys → display names)
_GRAHA_MAP = {
    "sun": "Surya", "moon": "Candra", "mars": "Mangala",
    "mercury": "Budha", "jupiter": "Guru", "venus": "Sukra",
    "saturn": "Sani", "rahu": "Rahu", "ketu": "Ketu",
}

# Nakshatra → tempo quality
_NAK_QUALITY = {
    "Rohiṇī":      "devotional",   # fixed, fertile
    "Punarvasu":    "expansive",    # return, renewal
    "Śravaṇa":     "precise",      # listening, knowledge
    "Svātī":        "precise",      # independence, detachment
    "Anurādhā":     "devotional",   # friendship, devotion
    "Ārdrā":        "stormy",       # storm, Rudra
    "Śatabhiṣā":    "precise",     # hundred healers
    "Pūrvāṣāḍhā":  "expansive",   # invincibility
    "Dhaniṣṭhā":    "expansive",   # wealth, rhythm
    "Mūla":         "stormy",       # uprooting
}


def _natal_nakshatras(natal):
    """Extract set of nakshatra names from natal chart."""
    naks = set()
    if natal.get("lagna_nak"):
        naks.add(natal["lagna_nak"].split(" pada")[0].strip())
    for graha in _GRAHA_MAP:
        g = natal.get(graha)
        if isinstance(g, dict) and g.get("nak"):
            naks.add(g["nak"].split(" pada")[0].strip())
    return naks


def _current_nakshatra(spine):
    """Get current nakshatra name from spine panchanga."""
    p = spine.get("panchanga", {})
    return p.get("nakshatra", "")


def _match_natal_nak(current_nak, natal_naks):
    """Check if current nakshatra matches any natal nakshatra (substring)."""
    for nn in natal_naks:
        if nn.lower() in current_nak.lower() or current_nak.lower() in nn.lower():
            return nn
    return None


def _dasha_lord(natal):
    """Get current dasha lord graha name."""
    d = natal.get("dasha", {})
    return d.get("lord", "Budha")


def _derive_field_tensions(natal, spine, ss, current_nak, natal_naks, raga_blend):
    """Find swaras cosmically present but outside the current raga.

    These are "off notes" the musician hears — not errors but the field
    speaking in a different language. Each tension carries a gesture
    suggestion for how to reference it without breaking the raga.
    """
    # Current raga's scale (swara names from sound_state)
    raga_notes = set(ss.get("raga_notes", []))
    if not raga_notes:
        return []

    # Secondary raga scale (from natal lagna nakshatra)
    lagna_nak = (natal.get("lagna_nak") or "Rohiṇī pada 1").split(" pada")[0].strip()
    secondary = _NAK_RAGA.get(lagna_nak, "Bhairavī")
    sec_semis = _RAGA_SCALES.get(secondary, set())

    # Graha nakshatras that are active → their swaras
    # Each graha in the natal chart has a swara; if its nakshatra
    # is close to the current field nakshatra, that swara "calls"
    tensions = []
    seen_swaras = set()

    # 1. Secondary raga notes not in primary raga
    for semi in sec_semis:
        swara = _SEMI_TO_SWARA.get(semi, "")
        if swara and swara not in raga_notes and swara not in seen_swaras:
            pull = 0.3 * raga_blend  # stronger when natal is active
            # Komal/tivra variants are grace notes; others passing tones
            gesture = "grace_note" if swara[0].islower() else "passing_tone"
            tensions.append({
                "swara": swara,
                "source": f"{secondary} ({lagna_nak} lagna)",
                "pull": round(min(pull, 1.0), 2),
                "gesture": gesture,
            })
            seen_swaras.add(swara)

    # 2. Natal graha swaras not in current raga
    for graha_key, graha_name in _GRAHA_MAP.items():
        g = natal.get(graha_key)
        if not isinstance(g, dict):
            continue
        g_nak = g.get("nak", "").split(" pada")[0].strip()
        swara = _GRAHA_SWARA.get(graha_name, "")
        if not swara or swara in raga_notes or swara in seen_swaras:
            continue

        # Pull is stronger if this graha's nakshatra is close to current
        pull = 0.15
        if _match_natal_nak(current_nak, {g_nak}):
            pull = 0.7  # graha's nakshatra is active right now
        elif g.get("exalted"):
            pull = 0.4  # exalted graha always audible

        # Gesture depends on graha nature
        if graha_name in ("Sani", "Ketu"):
            gesture = "silence_before"  # Saturn/Ketu = space
        elif graha_name in ("Rahu",):
            gesture = "rhythmic_echo"   # Rahu = obsessive return
        elif graha_name in ("Guru", "Sukra"):
            gesture = "phrase_end"      # benevolics = resolution
        else:
            gesture = "passing_tone"

        tensions.append({
            "swara": swara,
            "source": f"{graha_name} in {g_nak}",
            "pull": round(min(pull, 1.0), 2),
            "gesture": gesture,
        })
        seen_swaras.add(swara)

    # 3. Element-adjacent swaras from field entities
    # Entities with elements different from raga element can pull swaras
    raga_element = ss.get("element", "ether")
    _ELEMENT_SWARA = {
        "fire": "Re", "water": "ga", "earth": "Sa",
        "air": "Dha", "ether": "Pa",
    }
    for ent in spine.get("entities", [])[:16]:
        ent_elem = ent.get("element", "")
        if ent_elem and ent_elem != raga_element:
            swara = _ELEMENT_SWARA.get(ent_elem, "")
            if swara and swara not in raga_notes and swara not in seen_swaras:
                tensions.append({
                    "swara": swara,
                    "source": f"{ent.get('name', ent.get('id', '?'))} ({ent_elem})",
                    "pull": round(ent.get("coherence", 0.3) * 0.5, 2),
                    "gesture": "grace_note",
                })
                seen_swaras.add(swara)

    # Sort by pull strength, descending
    tensions.sort(key=lambda t: t["pull"], reverse=True)
    return tensions[:6]  # cap at 6 tensions


# ── Rhythmic tensions ────────────────────────────────
# Tala beat counts in the system
_TALA_BEATS = {
    "Adi": 8, "Rupak": 7, "Jhaptal": 10,
    "Dadra": 6, "Chautal": 12, "Keherwa": 8,
}

# Element → rhythmic tendency (felt cross-rhythm)
_ELEMENT_RHYTHM = {
    "fire": 3,    # fire wants triads
    "water": 5,   # water wants khanda
    "earth": 4,   # earth wants chatusra
    "air": 7,     # air wants misra
    "ether": 5,   # ether wants space, khanda
}

# Guna → rhythmic expression preference
_GUNA_EXPRESSION = {
    "sattva": "breath",
    "rajas": "polyrhythm",
    "tamas": "phrase_boundary",
}


def _derive_rhythmic_tensions(natal, spine, tala_beats):
    """Find alternative rhythmic cycles felt within the current tala.

    A musician in Rupak 7 might feel a 5-beat cycle pulling,
    or a 3-beat cycle nested. These are creative material.
    """
    p = spine.get("panchanga", {})
    tensions = []
    seen_cycles = set()

    # 1. Natal graha element pulls a different cycle
    for graha_key, graha_name in _GRAHA_MAP.items():
        g = natal.get(graha_key)
        if not isinstance(g, dict):
            continue
        # Only consider grahas with strong natal positions
        if not (g.get("exalted") or g.get("retrograde") or
                graha_key in ("moon", "saturn", "jupiter")):
            continue

        g_nak = g.get("nak", "").split(" pada")[0].strip()
        g_quality = _NAK_QUALITY.get(g_nak, "")
        felt_cycle = _ELEMENT_RHYTHM.get(
            p.get("element", "ether"), 5)

        # Retrograde grahas pull against the current direction
        if g.get("retrograde"):
            # Retrograde = contra-cycle, use complement
            felt_cycle = tala_beats - felt_cycle if felt_cycle < tala_beats else 3

        if felt_cycle == tala_beats or felt_cycle in seen_cycles or felt_cycle < 2:
            continue

        # Expression based on graha nature
        if graha_name == "Sani":
            expression = "phrase_boundary"
        elif graha_name in ("Rahu", "Ketu"):
            expression = "tihai"
        elif g_quality == "devotional":
            expression = "breath"
        else:
            expression = "polyrhythm"

        tensions.append({
            "cycle": felt_cycle,
            "source": f"{graha_name} in {g_nak}" +
                      (" (retrograde)" if g.get("retrograde") else "") +
                      (" (exalted)" if g.get("exalted") else ""),
            "expression": expression,
        })
        seen_cycles.add(felt_cycle)

    # 2. Guna-driven cross-rhythm
    guna = p.get("guna", "sattva").lower()
    guna_cycle = {"sattva": 3, "rajas": 5, "tamas": 4}.get(guna, 3)
    if guna_cycle != tala_beats and guna_cycle not in seen_cycles:
        tensions.append({
            "cycle": guna_cycle,
            "source": f"guna ({guna})",
            "expression": _GUNA_EXPRESSION.get(guna, "breath"),
        })
        seen_cycles.add(guna_cycle)

    # 3. Tithi-derived inner cycle
    # Tithi number (1-30) mod small primes gives a felt sub-cycle
    tidx = p.get("tidx", 0)
    tithi_cycle = (tidx % 5) + 2  # 2-6 range
    if tithi_cycle != tala_beats and tithi_cycle not in seen_cycles:
        tensions.append({
            "cycle": tithi_cycle,
            "source": f"tithi phase ({tidx})",
            "expression": "phrase_boundary",
        })
        seen_cycles.add(tithi_cycle)

    # Sort by how different the cycle is from current tala (more different = more tension)
    tensions.sort(key=lambda t: abs(t["cycle"] - tala_beats), reverse=True)
    return tensions[:4]  # cap at 4


# ── Bhajan form selection ─────────────────────────────
# Nakshatra deity → invocation mantra
_NAK_DEITY_MANTRA = {
    "Ashwini":    ("Aśvinau", "Om Aśvinau namaḥ"),
    "Bharani":    ("Yama", "Om Yamāya namaḥ"),
    "Krittika":   ("Agni", "Om Agnaye namaḥ"),
    "Rohini":     ("Brahmā", "Om Brahmāya namaḥ"),
    "Mrigashira": ("Soma", "Om Somāya namaḥ"),
    "Ardra":      ("Rudra", "Om Rudrāya namaḥ"),
    "Punarvasu":  ("Bṛhaspati", "Om Bṛhaspataye namaḥ"),
    "Pushya":     ("Bṛhaspati", "Om Bṛhaspataye namaḥ"),
    "Ashlesha":   ("Sarpa", "Om Sarpebhyo namaḥ"),
    "Magha":      ("Pitṛ", "Om Pitṛbhyo namaḥ"),
    "Purva Phalguni":  ("Bhaga", "Om Bhagāya namaḥ"),
    "Uttara Phalguni": ("Aryaman", "Om Aryamṇe namaḥ"),
    "Hasta":      ("Savitṛ", "Om Savitre namaḥ"),
    "Chitra":     ("Tvaṣṭṛ", "Om Tvaṣṭre namaḥ"),
    "Swati":      ("Vāyu", "Om Vāyave namaḥ"),
    "Vishakha":   ("Indrāgni", "Om Indrāgnibhyāṃ namaḥ"),
    "Anuradha":   ("Mitra", "Om Mitrāya namaḥ"),
    "Jyeshtha":   ("Indra", "Om Indrāya namaḥ"),
    "Mula":       ("Nirṛti", "Om Nirṛtaye namaḥ"),
    "Purva Ashadha":   ("Āpaḥ", "Om Apāṃ namaḥ"),
    "Uttara Ashadha":  ("Viśvedeva", "Om Viśvedevebhyo namaḥ"),
    "Shravana":   ("Viṣṇu", "Om Viṣṇave namaḥ"),
    "Dhanishta":  ("Vasu", "Om Vasubhyo namaḥ"),
    "Shatabhisha": ("Varuṇa", "Om Varuṇāya namaḥ"),
    "Purva Bhadrapada":  ("Ajaikapād", "Om Ajaikapāde namaḥ"),
    "Uttara Bhadrapada": ("Ahirbudhnya", "Om Ahirbudhnyāya namaḥ"),
    "Revati":     ("Pūṣan", "Om Pūṣṇe namaḥ"),
}

# Poetic meters used in bhajan forms
_METERS = {
    "chaupai":   {"syllables": 16, "pattern": "4×4 mātrā"},
    "doha":      {"syllables": 24, "pattern": "13+11 mātrā"},
    "soratha":   {"syllables": 24, "pattern": "11+13 mātrā"},
    "chhand":    {"syllables": 28, "pattern": "16+12 mātrā"},
    "shloka":    {"syllables": 32, "pattern": "8×4 akṣara"},
    "arya":      {"syllables": 30, "pattern": "12+18 mātrā"},
    "kavitt":    {"syllables": 31, "pattern": "8+8+8+7 mātrā"},
}

# Vara (weekday) name fragments for matching
_VARA_FORM = {
    "guruvāra":   ("dhrupad", "Chautal", 12, "sanskrit"),
    "guru":       ("dhrupad", "Chautal", 12, "sanskrit"),
    "śukravāra":  ("thumri", "Dadra", 6, "brajbhasha"),
    "śukra":      ("thumri", "Dadra", 6, "brajbhasha"),
    "ravivāra":   ("khayal", "Adi", 8, "hindi"),
    "ravi":       ("khayal", "Adi", 8, "hindi"),
    "somavāra":   ("kirtan", "Keherwa", 8, "brajbhasha"),
    "soma":       ("kirtan", "Keherwa", 8, "brajbhasha"),
    "maṅgalavāra": ("dhrupad", "Jhaptal", 10, "sanskrit"),
    "maṅgala":    ("dhrupad", "Jhaptal", 10, "sanskrit"),
    "budhavāra":  ("khayal", "Rupak", 7, "hindi"),
    "budha":      ("khayal", "Rupak", 7, "hindi"),
    "śanivāra":   ("doha", "Adi", 8, "hindi"),
    "śani":       ("doha", "Adi", 8, "hindi"),
}


def select_bhajan_form(panchanga, natal):
    """Select bhajan form from panchanga moment + natal chart.

    Args:
        panchanga: dict with vara, nakshatra, paksha, tithi, etc.
        natal: dict from /natal (NATAL constant)

    Returns:
        dict with form, tala, meter, language, deity_invocation,
        antara_length, sthayi_refrain
    """
    vara = (panchanga.get("vara") or "").lower()
    paksha = (panchanga.get("paksha") or "shukla").lower()
    nakshatra = panchanga.get("nakshatra", "")
    lagna_nak = (natal.get("lagna_nak") or "Rohiṇī pada 1").split(" pada")[0].strip()

    # ── Normalize nakshatra for lookup ──
    nak_key = nakshatra
    for k in _NAK_DEITY_MANTRA:
        if k.lower() in nakshatra.lower() or nakshatra.lower() in k.lower():
            nak_key = k
            break

    # ── Deity invocation from current nakshatra ──
    deity_name, deity_mantra = _NAK_DEITY_MANTRA.get(nak_key, ("", "Om namaḥ"))

    # ── Form selection: vara drives primary choice ──
    form = "khayal"
    tala = "Adi"
    tala_beats = 8
    language = "hindi"

    for vara_frag, (f, t, b, l) in _VARA_FORM.items():
        if vara_frag in vara:
            form, tala, tala_beats, language = f, t, b, l
            break

    # ── Paksha modulates form ──
    # Krishna paksha → quieter, more introspective forms
    if paksha.startswith("kr"):
        if form == "kirtan":
            form = "doha"      # quieter than full kirtan
            language = "hindi"
        elif form == "khayal":
            form = "khayal"    # khayal works in both pakshas
        # doha and dhrupad stay
    else:
        # Shukla paksha → full forms allowed
        if form == "doha":
            form = "kirtan"    # upgrade doha → kirtan in shukla
            language = "brajbhasha"

    # ── Rohiṇī (natal lagna) always available as secondary ──
    # If current nakshatra is Rohini, shift toward Bhairavī/thumri color
    rohini_active = "rohi" in nakshatra.lower()

    # ── Meter selection by form ──
    meter_map = {
        "dhrupad": "shloka",
        "khayal":  "chaupai",
        "kirtan":  "chaupai",
        "thumri":  "doha",
        "doha":    "doha",
        "sloka":   "shloka",
    }
    meter_name = meter_map.get(form, "chaupai")
    meter = _METERS.get(meter_name, _METERS["chaupai"])

    # ── Antara length: 2 for doha, 3-4 for dhrupad/khayal ──
    antara_map = {"doha": 2, "thumri": 2, "kirtan": 3, "khayal": 3, "dhrupad": 4, "sloka": 4}
    antara_length = antara_map.get(form, 3)

    # ── Sthayi refrain: nakshatra deity mantra as the returning phrase ──
    sthayi_refrain = deity_mantra

    return {
        "form": form,
        "tala": tala,
        "tala_beats": tala_beats,
        "meter": meter_name,
        "meter_syllables": meter["syllables"],
        "meter_pattern": meter["pattern"],
        "language": language,
        "deity": deity_name,
        "deity_invocation": deity_mantra,
        "antara_length": antara_length,
        "sthayi_refrain": sthayi_refrain,
        "rohini_secondary": rohini_active,
        "paksha": paksha,
    }


def derive_musician_reading(natal, spine):
    """Derive natal-aware sound interpretation from chart + field.

    Args:
        natal: dict from /natal endpoint (NATAL constant)
        spine: dict from /spine endpoint (full field state)

    Returns:
        dict with musician reading keys
    """
    ss = spine.get("sound_state", {})
    p = spine.get("panchanga", {})
    paksha = p.get("paksha", "shukla")

    # ── Natal nakshatras ─────────────────────────────
    natal_naks = _natal_nakshatras(natal)
    current_nak = _current_nakshatra(spine)
    lagna_nak = (natal.get("lagna_nak") or "Rohiṇī pada 1").split(" pada")[0].strip()
    moon_nak = natal.get("moon", {}).get("nak", "Punarvasu").split(" pada")[0].strip()

    # ── Primary raga: from spine, modified by natal ──
    primary_raga = ss.get("raga", "Yaman")

    # ── Secondary raga: lagna nakshatra color ────────
    secondary_raga = _NAK_RAGA.get(lagna_nak, "Bhairavī")

    # ── Raga blend: how much natal colors the cosmic ─
    # Base blend: natal always has some presence
    raga_blend = 0.15

    # If current nakshatra matches a natal graha nakshatra, increase
    matched_nak = _match_natal_nak(current_nak, natal_naks)
    if matched_nak:
        raga_blend += 0.35

    # Moon nakshatra match gets extra weight
    if moon_nak.lower() in current_nak.lower():
        raga_blend += 0.2

    # Lagna nakshatra match
    if lagna_nak.lower() in current_nak.lower():
        raga_blend += 0.15

    raga_blend = min(raga_blend, 1.0)

    # ── Gamak emphasis: dasha lord + natal graha ─────
    dasha = _dasha_lord(natal)
    gamak_emphasis = []

    # Dasha lord swara gets primary gamak
    dasha_swara = _GRAHA_SWARA.get(dasha, "Ma")
    gamak_emphasis.append(dasha_swara)

    # Lagna lord (Venus for Vṛṣabha)
    gamak_emphasis.append(_GRAHA_SWARA.get("Sukra", "Ga"))

    # Moon lord swara
    gamak_emphasis.append(_GRAHA_SWARA.get("Guru", "Dha"))

    # Deduplicate preserving order
    seen = set()
    gamak_emphasis = [s for s in gamak_emphasis if not (s in seen or seen.add(s))]

    # ── Vadi emphasis: weighted by natal + cosmic ────
    cosmic_vadi = ss.get("raga_vadi", "Ga")
    # If dasha lord swara matches cosmic vadi, strong emphasis
    if dasha_swara == cosmic_vadi:
        vadi_emphasis = cosmic_vadi
    else:
        # Natal lagna lord (Venus=Ga) pulls toward Ga
        vadi_emphasis = cosmic_vadi  # cosmic wins, but gamak ornaments natal

    # ── Tempo feel ───────────────────────────────────
    # Saturn exalted → precision; check natal Saturn
    saturn = natal.get("saturn", {})
    saturn_exalted = saturn.get("exalted", False)

    # Start from field quality, then natal modifies
    tempo_feel = "expansive"  # default

    if saturn_exalted:
        tempo_feel = "precise"

    # Rahu in Ārdrā → stormy when Ārdrā active
    rahu = natal.get("rahu", {})
    rahu_nak = rahu.get("nak", "").split(" pada")[0].strip()
    if rahu_nak and rahu_nak.lower() in current_nak.lower():
        tempo_feel = "stormy"

    # Jupiter nakshatras → devotional
    jupiter = natal.get("jupiter", {})
    jup_nak = jupiter.get("nak", "").split(" pada")[0].strip()
    if jup_nak and jup_nak.lower() in current_nak.lower():
        tempo_feel = "devotional"

    # ── Rest density ─────────────────────────────────
    # Saturn exalted = more space; base from arc_phase
    arc = float(ss.get("arc_phase") or p.get("arc_phase") or 0.5)
    rest_density = 0.3  # base

    if saturn_exalted:
        rest_density = 0.55  # Saturn gives space

    # Waning moon (krishna paksha) → more silence
    if paksha.lower().startswith("kr"):
        rest_density += 0.1

    # Late arc → less rest (jhala energy)
    if arc > 0.75:
        rest_density = max(0.15, rest_density - 0.2)

    rest_density = max(0.0, min(1.0, rest_density))

    # ── Phrase arc ───────────────────────────────────
    if paksha.lower().startswith("sh"):
        # Shukla (waxing) → ascent, wave
        phrase_arc = "ascent" if arc < 0.5 else "wave"
    else:
        # Krishna (waning) → descent, circle
        phrase_arc = "descent" if arc < 0.5 else "circle"

    # Natal moon in Punarvasu (return) → circle tendency
    if moon_nak == "Punarvasu":
        if phrase_arc in ("ascent", "descent"):
            phrase_arc = "wave"  # Punarvasu = return = cyclical

    # ── Resonance nodes ──────────────────────────────
    resonance_nodes = []

    # Moon nakshatra always resonant
    resonance_nodes.append(f"nakshatra:{moon_nak.lower().replace('ā', 'a').replace('ī', 'i').replace('ṇ', 'n').replace('ū', 'u')}")

    # Lagna nakshatra
    lagna_id = f"nakshatra:{lagna_nak.lower().replace('ā', 'a').replace('ī', 'i').replace('ṇ', 'n').replace('ū', 'u')}"
    if lagna_id not in resonance_nodes:
        resonance_nodes.append(lagna_id)

    # Any natal graha nakshatra matching current field entities
    entities = spine.get("entities", [])
    for ent in entities[:32]:
        eid = ent.get("id", "")
        for nn in natal_naks:
            nn_slug = nn.lower().replace("ā", "a").replace("ī", "i").replace("ṇ", "n").replace("ū", "u").replace("ṣ", "s").replace("ḍ", "d")
            if nn_slug in eid:
                if eid not in resonance_nodes:
                    resonance_nodes.append(eid)

    # ── Field tensions ──────────────────────────────
    # Swaras cosmically present but outside the current raga.
    # The musician hears these as calls from the field.
    field_tensions = _derive_field_tensions(
        natal, spine, ss, current_nak, natal_naks, raga_blend)

    # ── Rhythmic tensions ────────────────────────────
    # Alternative cycles felt within the current tala.
    tala_beats = ss.get("tala_beats", 8)
    rhythmic_tensions = _derive_rhythmic_tensions(
        natal, spine, tala_beats)

    # ── Musician note ────────────────────────────────
    parts = []
    if matched_nak:
        parts.append(f"{matched_nak} active — natal resonance high")
    if saturn_exalted:
        parts.append("Saturn exalted gives space between phrases")
    parts.append(f"{primary_raga} colored by {secondary_raga} ({lagna_nak} lagna)")
    if tempo_feel == "stormy":
        parts.append("Ārdrā storm energy present")
    if field_tensions:
        t_swaras = ", ".join(t["swara"] for t in field_tensions[:3])
        parts.append(f"field calling {t_swaras}")
    musician_note = "; ".join(parts) + "."

    return {
        "primary_raga": primary_raga,
        "secondary_raga": secondary_raga,
        "raga_blend": round(raga_blend, 2),
        "gamak_emphasis": gamak_emphasis,
        "vadi_emphasis": vadi_emphasis,
        "tempo_feel": tempo_feel,
        "rest_density": round(rest_density, 2),
        "phrase_arc": phrase_arc,
        "resonance_nodes": resonance_nodes,
        "field_tensions": field_tensions,
        "rhythmic_tensions": rhythmic_tensions,
        "musician_note": musician_note,
    }
