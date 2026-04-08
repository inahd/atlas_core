"""
reading_engine.py — Unified oracle reading system.

A reading is the intersection of field state, trajectory, natal chart,
altar, intention, and graph coherence — seen through a chosen lens.
Every lens (tarot, jyotish, iching, calendar, bandhu) reads the same
field through a different filter. All lenses are coherent with each other.

Pattern follows ui_vastu_engine.py:
    canonical data → internal helpers → validation → public API
"""

from typing import Any, Dict, List, Optional
import csv
import json
import os
from datetime import datetime

# ══════════════════════════════════════════════════════════
# DATA LOADING
# ══════════════════════════════════════════════════════════

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))

_PATHS = {
    "devi_cards": os.path.join(_ROOT, "datasets", "tarot", "devi_cards.json"),
    "hexagrams": os.path.join(_ROOT, "datasets", "iching", "hexagrams.csv"),
    "hex_nak": os.path.join(_ROOT, "datasets", "iching", "hexagram_nakshatra_resonance.csv"),
    "hex_devi": os.path.join(_ROOT, "datasets", "iching", "hexagram_devi_resonance.csv"),
    "compositions": os.path.join(_ROOT, "datasets", "compositions", "gaudiya_compositions.csv"),
    "navagraha": os.path.join(_ROOT, "datasets", "compositions", "navagraha_kritis.csv"),
    "narottama_padas": os.path.join(_ROOT, "datasets", "compositions", "narottama_padas.csv"),
    "nakshatra_kritis": os.path.join(_ROOT, "datasets", "compositions", "nakshatra_kritis.csv"),
    "chandas": os.path.join(_ROOT, "datasets", "chandas", "metres_forms.csv"),
    "nitya_devi": os.path.join(_ROOT, "datasets", "cosmology", "nitya_devi_master.csv"),
    "graha": os.path.join(_ROOT, "datasets", "cosmology", "graha_master.csv"),
    "natal": os.path.join(_ROOT, "instance", "personal", "natal.json"),
    "altar": os.path.join(_ROOT, "instance", "personal", "altar.json"),
}

_cache: Dict[str, Any] = {}


def _load_json(key: str) -> Any:
    if key in _cache:
        return _cache[key]
    try:
        with open(_PATHS[key], encoding="utf-8") as f:
            data = json.load(f)
        _cache[key] = data
        return data
    except Exception:
        _cache[key] = {} if key in ("natal", "altar") else []
        return _cache[key]


def _load_csv_rows(key: str) -> List[dict]:
    if key in _cache:
        return _cache[key]
    try:
        with open(_PATHS[key], encoding="utf-8") as f:
            # Skip leading blank lines before header
            lines = f.readlines()
            clean = [l for l in lines if l.strip()]
            import io
            rows = list(csv.DictReader(io.StringIO("".join(clean))))
        _cache[key] = rows
        return rows
    except Exception:
        _cache[key] = []
        return []


# ══════════════════════════════════════════════════════════
# READING CONTEXT
# ══════════════════════════════════════════════════════════

def build_reading_context(field_state: dict, intention: str = "",
                          natal: dict = None) -> dict:
    """Build full context before any lens reads it."""
    if natal is None:
        natal = _load_json("natal")
    altar = _load_json("altar")

    # Trajectory
    try:
        from .trajectory_engine import derive_trajectory
        trajectory = derive_trajectory(field_state, natal)
    except Exception:
        trajectory = {}

    # Intention classification
    intention_spec = {}
    if intention:
        try:
            from .intention_engine import classify_intention
            intention_spec = classify_intention(intention)
        except Exception:
            pass

    return {
        "field_state": field_state,
        "trajectory": trajectory,
        "natal": natal,
        "altar": altar,
        "intention": intention,
        "intention_spec": intention_spec,
        "timestamp": datetime.now().isoformat(),
    }


# ══════════════════════════════════════════════════════════
# LENS: TAROT (Devi Cards)
# ══════════════════════════════════════════════════════════

def _lens_tarot(ctx: dict) -> dict:
    cards = _load_json("devi_cards")
    if not isinstance(cards, list) or not cards:
        return _empty_reading("tarot", ctx)

    p5 = ctx["field_state"].get("panchanga", {})
    tidx = int(p5.get("tidx", 0))
    tithi_num = (tidx % 15) + 1
    nak = p5.get("nakshatra", "").lower()
    element = p5.get("element", "").lower()
    altar = ctx.get("altar", {})
    altar_deities = [d for d in altar.get("deities", [])]
    traj = ctx.get("trajectory", {})
    arc = traj.get("now", {}).get("arc_position", 0.5)

    # Score each card
    scored = []
    for card in cards:
        score = 0.0
        # Tithi match
        if card.get("tithi") == tithi_num:
            score += 0.3
        # Element match
        card_elem = card.get("element", "")
        if isinstance(card_elem, list):
            if element in [e.lower() for e in card_elem]:
                score += 0.2
        elif element == str(card_elem).lower():
            score += 0.2
        # Altar presence
        card_id = "devi_" + card.get("id", "").replace("devi_", "")
        if card_id in str(altar_deities):
            score += 0.15
        # Trajectory energy alignment
        card_guna = card.get("guna", "")
        if arc > 0.4 and card_guna == "rajas":
            score += 0.1
        elif arc < 0.2 and card_guna == "tamas":
            score += 0.1
        elif card_guna == "sattva":
            score += 0.05
        scored.append((score, card))

    scored.sort(key=lambda x: x[0], reverse=True)
    primary_card = scored[0][1] if scored else cards[0]
    secondary = [c for _, c in scored[1:3]]

    # Find matching Nitya Devi for raga
    raga = primary_card.get("raga", "Yaman")
    rasa = ""
    for row in _load_csv_rows("nitya_devi"):
        if row.get("name_iast", "").lower() in primary_card.get("name", "").lower():
            rasa = row.get("rasa", "")
            break

    # Find matching pada
    pada = _find_pada(raga, rasa)

    return {
        "lens": "tarot",
        "context": ctx,
        "primary": {
            "entity_id": "devi_" + primary_card.get("id", ""),
            "name": primary_card.get("name", ""),
            "symbol": primary_card.get("emoji", ""),
            "quality": primary_card.get("guna", ""),
            "image_hint": primary_card.get("sk", ""),
        },
        "secondary": [
            {"entity_id": "devi_" + c.get("id", ""), "name": c.get("name", ""),
             "symbol": c.get("emoji", ""), "quality": c.get("guna", "")}
            for c in secondary
        ],
        "passages": [{"text": primary_card.get("reading", ""), "source": "devi_cards"}],
        "interpretation": {
            "now": primary_card.get("process", ""),
            "arc": traj.get("musical_implication", {}).get("energy_arc", ""),
            "personal": f"Altar holds {len(altar_deities)} deities" if altar_deities else "",
            "guidance": primary_card.get("reading", ""),
        },
        "musical_response": {
            "raga": raga, "rasa": rasa,
            "tempo": "vilambit" if arc > 0.7 else "madhya",
            "instrument_emphasis": "tanpura" if arc > 0.8 else "sarangi",
        },
        "pada": pada,
        "attestation": "SYNTHESIS",
    }


# ══════════════════════════════════════════════════════════
# LENS: I CHING
# ══════════════════════════════════════════════════════════

def _lens_iching(ctx: dict) -> dict:
    hexagrams = _load_csv_rows("hexagrams")
    hex_nak = _load_csv_rows("hex_nak")
    hex_devi = _load_csv_rows("hex_devi")

    if not hexagrams:
        return _empty_reading("iching", ctx)

    p5 = ctx["field_state"].get("panchanga", {})
    nak = p5.get("nakshatra", "").lower().replace(" ", "_")
    tidx = int(p5.get("tidx", 0))
    tithi_num = (tidx % 15) + 1
    traj = ctx.get("trajectory", {})

    # Score hexagrams by nakshatra + devi resonance
    scores: Dict[str, float] = {}
    for row in hex_nak:
        hid = row.get("hexagram_id", "")
        nid = row.get("nakshatra_id", "").lower().replace("nakshatra_", "")
        if nak and nid and nak in nid:
            scores[hid] = scores.get(hid, 0) + float(row.get("resonance_score", 0))

    for row in hex_devi:
        hid = row.get("hexagram_id", "")
        alignment = row.get("tithi_alignment", "")
        if alignment == "direct":
            scores[hid] = scores.get(hid, 0) + float(row.get("resonance_score", 0))

    # Find best hexagram
    best_id = max(scores, key=scores.get) if scores else "hexagram_01"
    primary_hex = None
    for h in hexagrams:
        if h.get("entity_id") == best_id:
            primary_hex = h
            break
    if not primary_hex and hexagrams:
        primary_hex = hexagrams[0]

    # Changing lines from trajectory
    paksha = traj.get("now", {}).get("paksha", "")
    if "kri" in paksha.lower() or "kṛṣṇa" in paksha.lower():
        changing_lines = "lines 4-6 (completion phase)"
    else:
        changing_lines = "lines 1-3 (beginning phase)"

    judgment = primary_hex.get("wilhelm_judgment", "") if primary_hex else ""
    name = primary_hex.get("name_english", "") if primary_hex else ""
    number = primary_hex.get("number", "") if primary_hex else ""

    pada = _find_pada(
        primary_hex.get("graha_primary", ""),
        primary_hex.get("rasa_primary", "shanta"))

    return {
        "lens": "iching",
        "context": ctx,
        "primary": {
            "entity_id": best_id,
            "name": f"{number}. {name}" if number else name,
            "symbol": primary_hex.get("symbol", "☰") if primary_hex else "☰",
            "quality": primary_hex.get("field_quality", "") if primary_hex else "",
            "image_hint": primary_hex.get("wilhelm_image", "") if primary_hex else "",
        },
        "secondary": [],
        "passages": [{"text": judgment, "source": "wilhelm"}] if judgment else [],
        "interpretation": {
            "now": judgment[:200] if judgment else "",
            "arc": f"Changing: {changing_lines}",
            "personal": "",
            "guidance": primary_hex.get("longing_quality", "") if primary_hex else "",
        },
        "musical_response": {
            "raga": "",
            "rasa": primary_hex.get("rasa_primary", "shanta") if primary_hex else "shanta",
            "tempo": "vilambit",
            "instrument_emphasis": "tanpura",
        },
        "pada": pada,
        "attestation": "SYNTHESIS",
    }


# ══════════════════════════════════════════════════════════
# LENS: JYOTISH
# ══════════════════════════════════════════════════════════

def _lens_jyotish(ctx: dict) -> dict:
    natal = ctx.get("natal", {})
    p5 = ctx["field_state"].get("panchanga", {})
    traj = ctx.get("trajectory", {})
    dasha = traj.get("dasha_context", {})

    nak = p5.get("nakshatra", "")
    nak_lord = p5.get("nak_lord", "")
    element = p5.get("element", "")

    # Find graha data
    graha_row = {}
    for g in _load_csv_rows("graha"):
        if g.get("graha", "").lower() == nak_lord.lower().replace("ā", "a").replace("ū", "u"):
            graha_row = g
            break

    # Find navagraha kriti for this lord
    kriti = {}
    lord_lower = nak_lord.lower()
    for k in _load_csv_rows("navagraha"):
        if lord_lower in k.get("notes", "").lower() or lord_lower in k.get("composition_name", "").lower():
            kriti = k
            break

    primary_name = f"{nak} · {nak_lord}"
    if dasha.get("current_dasha"):
        primary_name += f" · {dasha['current_dasha']} dasha"

    pada = _find_pada(
        kriti.get("raga", ""),
        graha_row.get("guna", "sattva"))

    return {
        "lens": "jyotish",
        "context": ctx,
        "primary": {
            "entity_id": f"graha_{nak_lord.lower()}" if nak_lord else "",
            "name": primary_name,
            "symbol": graha_row.get("symbol", ""),
            "quality": graha_row.get("guna", ""),
            "image_hint": graha_row.get("color_meaning", ""),
        },
        "secondary": [],
        "passages": [{"text": dasha.get("dasha_musical", ""),
                       "source": "graha_master"}] if dasha.get("dasha_musical") else [],
        "interpretation": {
            "now": f"{nak} under {nak_lord} — {graha_row.get('domain', '')} governs",
            "arc": traj.get("musical_implication", {}).get("energy_arc", ""),
            "personal": dasha.get("dasha_musical", ""),
            "guidance": f"Element {element} active — align with {graha_row.get('domain', 'present moment')}",
        },
        "musical_response": {
            "raga": kriti.get("raga", ""),
            "rasa": graha_row.get("guna", "sattva"),
            "tempo": traj.get("musical_implication", {}).get("tempo_trend", "stable"),
            "instrument_emphasis": "sarangi" if nak_lord.lower() in ("shukra", "chandra") else "tanpura",
        },
        "pada": pada,
        "attestation": "SYNTHESIS",
    }


# ══════════════════════════════════════════════════════════
# LENS: CALENDAR
# ══════════════════════════════════════════════════════════

def _lens_calendar(ctx: dict) -> dict:
    intention = ctx.get("intention", "")
    traj = ctx.get("trajectory", {})
    now = traj.get("now", {})
    moving = traj.get("moving_toward", {})
    musical = traj.get("musical_implication", {})

    # Classify intention
    intention_spec = ctx.get("intention_spec", {})
    int_label = intention_spec.get("label", intention)

    # Get windows if intention classified
    windows_summary = ""
    if intention_spec.get("intention_id"):
        try:
            from .intention_engine import derive_windows
            wins = derive_windows(intention_spec["intention_id"],
                                  ctx["field_state"], days=7)
            windows_summary = wins.get("today_summary", "")
        except Exception:
            pass

    approaching = moving.get("approaching_event", "")
    approaching_days = moving.get("approaching_days", 0)

    return {
        "lens": "calendar",
        "context": ctx,
        "primary": {
            "entity_id": "",
            "name": f"{now.get('tithi', '')} · {now.get('nakshatra', '')}",
            "symbol": "☽" if "shukla" in now.get("paksha", "").lower() else "☾",
            "quality": now.get("tithi_quality", "mixed"),
            "image_hint": f"arc {now.get('arc_position', 0.5):.2f}",
        },
        "secondary": [],
        "passages": [{"text": windows_summary, "source": "intention_engine"}] if windows_summary else [],
        "interpretation": {
            "now": f"{now.get('tithi', '')} — {now.get('tithi_quality', 'mixed')} quality",
            "arc": f"Approaching {approaching} in {approaching_days} days" if approaching else "",
            "personal": int_label,
            "guidance": windows_summary or f"Field {musical.get('energy_arc', '')}",
        },
        "musical_response": {
            "raga": "",
            "rasa": "shanta" if approaching == "ekadashi" and approaching_days < 3 else "",
            "tempo": musical.get("tempo_trend", "stable"),
            "instrument_emphasis": "tanpura" if not musical.get("tabla_active", True) else "tabla",
        },
        "pada": _find_pada("", ""),
        "attestation": "SYNTHESIS",
    }


# ══════════════════════════════════════════════════════════
# LENS: BANDHU (Companion Oracle)
# ══════════════════════════════════════════════════════════

def _lens_bandhu(ctx: dict) -> dict:
    # Find most resonant Gaudiya pada
    p5 = ctx["field_state"].get("panchanga", {})
    traj = ctx.get("trajectory", {})
    now_hour = datetime.now().hour

    # Match ashtakala period to composition — include all sources
    compositions = _load_csv_rows("compositions")
    compositions.extend(_load_csv_rows("narottama_padas"))
    compositions.extend(_load_csv_rows("nakshatra_kritis"))
    if not compositions:
        return _empty_reading("bandhu", ctx)

    # Score compositions by raga/rasa/time match
    scored = []
    for comp in compositions:
        score = 0.0
        # Prefer Narottama Dasa Thakura
        if "narottama" in comp.get("composer", "").lower():
            score += 0.2
        # Check rasa match with field
        notes = comp.get("notes", "").lower()
        element = p5.get("element", "").lower()
        if element in ("water", "earth") and "karuna" in notes:
            score += 0.15
        if element in ("fire", "air") and "vira" in notes:
            score += 0.15
        if "madhurya" in notes or "shringara" in notes:
            score += 0.1
        # Time of day match
        if now_hour < 8 and "dawn" in notes:
            score += 0.2
        elif now_hour >= 18 and ("evening" in notes or "night" in notes):
            score += 0.2
        scored.append((score, comp))

    scored.sort(key=lambda x: x[0], reverse=True)
    best = scored[0][1] if scored else compositions[0]

    pallavi = best.get("pallavi_text", "")
    raga = best.get("raga", "")
    composer = best.get("composer", "")

    # Devi for this tithi
    tidx = int(p5.get("tidx", 0))
    tithi_num = (tidx % 15) + 1
    devi = {}
    for row in _load_csv_rows("nitya_devi"):
        if str(row.get("tithi_num")) == str(tithi_num):
            devi = row
            break

    devi_name = devi.get("name_iast", "")
    energy_arc = traj.get("musical_implication", {}).get("energy_arc", "")
    dasha_musical = traj.get("dasha_context", {}).get("dasha_musical", "")

    return {
        "lens": "bandhu",
        "context": ctx,
        "primary": {
            "entity_id": best.get("entity_id", ""),
            "name": best.get("composition_name", ""),
            "symbol": devi.get("bija", "Om") if devi else "Om",
            "quality": devi.get("guna", ""),
            "image_hint": devi.get("description", ""),
        },
        "secondary": [
            {"entity_id": devi.get("id", ""), "name": devi_name,
             "symbol": devi.get("bija", ""), "quality": devi.get("rasa", "")}
        ] if devi else [],
        "passages": [{"text": pallavi, "source": composer}] if pallavi else [],
        "interpretation": {
            "now": f"{devi_name} presides — {devi.get('description', '')}" if devi else "",
            "arc": energy_arc,
            "personal": dasha_musical,
            "guidance": pallavi[:200] if pallavi else "",
        },
        "musical_response": {
            "raga": raga,
            "rasa": devi.get("rasa", ""),
            "tempo": traj.get("musical_implication", {}).get("tempo_trend", "stable"),
            "instrument_emphasis": "sarangi",
        },
        "pada": {
            "composition_id": best.get("entity_id", ""),
            "composer": composer,
            "opening_line": pallavi.split(",")[0] if pallavi else "",
            "raga": raga,
            "rasa": devi.get("rasa", ""),
        },
        "metre": _metre_for_rasa(devi.get("rasa", "")),
        "attestation": "shastra" if pallavi else "SYNTHESIS",
    }


# ══════════════════════════════════════════════════════════
# SHARED HELPERS
# ══════════════════════════════════════════════════════════

def _metre_for_rasa(rasa: str) -> dict:
    """Select appropriate chandas metre by rasa."""
    metres = _load_csv_rows("chandas")
    if not metres:
        return {}
    # Normalize rasa: strip IAST diacritics for matching
    def _norm(s):
        s = (s or "").lower()
        for a, b in [("ā","a"),("ī","i"),("ū","u"),("ṛ","r"),("ṝ","r"),("ḷ","l"),
                     ("ṃ","m"),("ḥ","h"),("ṅ","ng"),("ñ","n"),("ṭ","t"),("ḍ","d"),
                     ("ṇ","n"),("ś","sh"),("ṣ","sh"),("ṁ","m")]:
            s = s.replace(a, b)
        return s
    rasa_n = _norm(rasa)
    # Primary rasa match (exact or substring — handles IAST transliteration variants)
    for m in metres:
        rp = _norm(m.get("rasa_primary", ""))
        if rp == rasa_n or (len(rasa_n) > 2 and rasa_n[:3] in rp) or (len(rp) > 2 and rp[:3] in rasa_n):
            return {"name": m.get("name_iast", ""), "syllables": m.get("total_syllables", ""),
                    "cadence": m.get("cadence_pattern", ""), "use_case": m.get("use_case", "")}
    # Secondary rasa match
    for m in metres:
        if rasa_n in _norm(m.get("rasa_secondary", "")):
            return {"name": m.get("name_iast", ""), "syllables": m.get("total_syllables", ""),
                    "cadence": m.get("cadence_pattern", ""), "use_case": m.get("use_case", "")}
    # Default: anuṣṭubh
    for m in metres:
        if "anustubh" in _norm(m.get("name_iast", "")):
            return {"name": m.get("name_iast", ""), "syllables": m.get("total_syllables", ""),
                    "cadence": m.get("cadence_pattern", ""), "use_case": m.get("use_case", "")}
    return {}


def _find_pada(raga: str, rasa: str) -> dict:
    """Find a matching Gaudiya pada by raga or rasa."""
    compositions = _load_csv_rows("compositions") + _load_csv_rows("narottama_padas") + _load_csv_rows("nakshatra_kritis")
    raga_l = raga.lower() if raga else ""
    rasa_l = rasa.lower() if rasa else ""

    for comp in compositions:
        comp_raga = comp.get("raga", "").lower()
        comp_notes = comp.get("notes", "").lower()
        if raga_l and raga_l in comp_raga:
            return {
                "composition_id": comp.get("entity_id", ""),
                "composer": comp.get("composer", ""),
                "opening_line": comp.get("pallavi_text", "").split(",")[0],
                "raga": comp.get("raga", ""),
                "rasa": rasa,
            }
        if rasa_l and rasa_l in comp_notes:
            return {
                "composition_id": comp.get("entity_id", ""),
                "composer": comp.get("composer", ""),
                "opening_line": comp.get("pallavi_text", "").split(",")[0],
                "raga": comp.get("raga", ""),
                "rasa": rasa,
            }
    return {"composition_id": "", "composer": "", "opening_line": "",
            "raga": "", "rasa": ""}


def _empty_reading(lens: str, ctx: dict) -> dict:
    return _validate({
        "lens": lens, "context": ctx,
        "primary": {"entity_id": "", "name": "", "symbol": "", "quality": "", "image_hint": ""},
        "secondary": [], "passages": [],
        "interpretation": {"now": "", "arc": "", "personal": "", "guidance": ""},
        "musical_response": {"raga": "", "rasa": "", "tempo": "madhya", "instrument_emphasis": "tanpura"},
        "pada": {"composition_id": "", "composer": "", "opening_line": "", "raga": "", "rasa": ""},
        "attestation": "SYNTHESIS",
    })


# ══════════════════════════════════════════════════════════
# VALIDATION
# ══════════════════════════════════════════════════════════

def _validate(reading: dict) -> dict:
    defaults = {
        "lens": "",
        "primary": {"entity_id": "", "name": "", "symbol": "", "quality": "", "image_hint": ""},
        "secondary": [],
        "passages": [],
        "interpretation": {"now": "", "arc": "", "personal": "", "guidance": ""},
        "musical_response": {"raga": "", "rasa": "", "tempo": "madhya", "instrument_emphasis": "tanpura"},
        "pada": {"composition_id": "", "composer": "", "opening_line": "", "raga": "", "rasa": ""},
        "attestation": "SYNTHESIS",
    }
    for key, default in defaults.items():
        if key == "context":
            continue
        if key not in reading or reading[key] is None:
            reading[key] = default
        elif isinstance(default, dict) and isinstance(reading[key], dict):
            for dk, dv in default.items():
                if dk not in reading[key]:
                    reading[key][dk] = dv
    return reading


# ══════════════════════════════════════════════════════════
# PUBLIC API
# ══════════════════════════════════════════════════════════

_LENSES = {
    "tarot": _lens_tarot,
    "iching": _lens_iching,
    "jyotish": _lens_jyotish,
    "calendar": _lens_calendar,
    "bandhu": _lens_bandhu,
}


def derive_reading(lens: str, field_state: dict, intention: str = "",
                   natal: dict = None, trajectory: dict = None,
                   altar: dict = None) -> dict:
    """Main entry point. Returns validated ReadingSpec. Never raises.

    Args:
        lens: 'tarot'|'jyotish'|'iching'|'calendar'|'bandhu'
        field_state: dict from kernel.py field_state()
        intention: free text describing what is being asked
        natal: from instance/personal/natal.json (auto-loaded if None)
        trajectory: from trajectory_engine (auto-computed if None)
        altar: from instance/personal/altar.json (auto-loaded if None)

    Returns:
        Validated ReadingSpec — all keys guaranteed present.
    """
    try:
        ctx = build_reading_context(field_state, intention, natal)
        if altar:
            ctx["altar"] = altar

        lens_fn = _LENSES.get(lens)
        if lens_fn is None:
            return _empty_reading(lens, ctx)

        reading = lens_fn(ctx)
        # Strip full context from output (too large for JSON response)
        reading.pop("context", None)
        return _validate(reading)

    except Exception:
        return _validate({"lens": lens, "attestation": "SYNTHESIS"})
