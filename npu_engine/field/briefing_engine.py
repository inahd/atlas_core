"""
briefing_engine.py — LLM-arranged field briefing

Gathers Atlas's own Jyotish data and asks a local LLM
to arrange it into readable sentences.

The LLM contributes NO knowledge of its own.
Atlas provides all knowledge from its corpus.
The LLM only arranges what it receives.
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Callable, Dict, Optional
from urllib.request import urlopen, Request
from urllib.error import URLError

_OLLAMA_URL = "http://localhost:11434/api/generate"
_OLLAMA_MODEL = "qwen2.5:1.5b"  # no thinking tokens, fast on CPU
_OLLAMA_TIMEOUT = 120
_CACHE_TTL = 7200  # 2 hours

_briefing_cache: Optional[dict] = None
_briefing_cache_time: float = 0


# ═══════════════════════════════════════════════════════════
# GATHER DATA
# ═══════════════════════════════════════════════════════════

def gather_briefing_data(calc_panchanga: Callable,
                         field_state_fn: Callable) -> dict:
    """
    Gather all data needed for the briefing from Atlas internals.
    calc_panchanga: function(now=None) → panchanga dict
    field_state_fn: function() → full field state dict
    """
    now = datetime.now()
    fs = {}
    try:
        fs = field_state_fn()
    except Exception:
        pass

    # Current panchanga
    current_pa = fs.get("panchanga", {})
    if not current_pa:
        try:
            current_pa = calc_panchanga(now)
        except Exception:
            current_pa = {}

    # Natal
    natal = fs.get("natal", {})

    # Hora
    hora = fs.get("hora", {})
    hora_lord = hora.get("hora_lord", "")
    if isinstance(hora_lord, dict):
        hora_lord = hora_lord.get("name", str(hora_lord))

    # Devi
    devi = current_pa.get("devi", {})
    devi_name = devi.get("name", "") if isinstance(devi, dict) else str(devi)
    devi_id = devi.get("entity_id", "") if isinstance(devi, dict) else ""

    # Upcoming 7 days
    upcoming = []
    natal_moon_nak = ""
    natal_lagna_nak = ""
    if natal:
        moon = natal.get("moon", {})
        natal_moon_nak = moon.get("nak", "") if isinstance(moon, dict) else ""
        natal_lagna_nak = natal.get("lagna_nak", "")

    for day_offset in range(1, 8):
        dt = now + timedelta(days=day_offset)
        try:
            p = calc_panchanga(dt)
        except Exception:
            continue

        tithi = p.get("tithi", "")
        nak = p.get("nakshatra", "")
        paksha = p.get("paksha", "")

        # Flag notable days
        notable = False
        reasons = []
        tithi_lower = tithi.lower()
        if "ekādaśī" in tithi_lower or "ekadashi" in tithi_lower:
            notable = True
            reasons.append("Ekādaśī (Viṣṇu fast)")
        if "paurṇimā" in tithi_lower or "purnima" in tithi_lower:
            notable = True
            reasons.append("Paurṇimā (full moon)")
        if "amāvāsyā" in tithi_lower or "amavasya" in tithi_lower:
            notable = True
            reasons.append("Amāvāsyā (new moon)")
        if natal_moon_nak and natal_moon_nak.lower() in nak.lower():
            notable = True
            reasons.append(f"Moon nakshatra matches natal ({natal_moon_nak})")
        if natal_lagna_nak and natal_lagna_nak.lower().split()[0] in nak.lower():
            notable = True
            reasons.append(f"Nakshatra near natal lagna ({natal_lagna_nak})")

        upcoming.append({
            "date": dt.strftime("%A %B %d"),
            "tithi": tithi,
            "nakshatra": nak,
            "paksha": paksha,
            "notable": notable,
            "reason": "; ".join(reasons) if reasons else "",
        })

    # Observe current nakshatra
    nak_observe = _fetch_observe("nakshatra_" + _slugify(
        current_pa.get("nakshatra", "")))
    devi_observe = _fetch_observe(devi_id) if devi_id else {}

    # Geosolar
    geosolar = {}
    try:
        from npu_engine.field.geosolar_engine import get_geosolar_state
        geosolar = get_geosolar_state()
    except Exception:
        pass

    # Nakshatra qualities from nak_data
    nak_data = current_pa.get("nak_data", {})

    return {
        "current": {
            "nakshatra": current_pa.get("nakshatra", ""),
            "nakshatra_deity": nak_data.get("deity", ""),
            "nakshatra_shakti": nak_data.get("shakti", ""),
            "nakshatra_themes": nak_data.get("themes", ""),
            "nakshatra_guna": nak_data.get("guna", ""),
            "nakshatra_element": nak_data.get("element", ""),
            "tithi": current_pa.get("tithi", ""),
            "paksha": current_pa.get("paksha", ""),
            "tithi_devi": devi_name,
            "hora_lord": hora_lord,
            "vara": current_pa.get("vara", ""),
        },
        "natal": {
            "lagna": natal.get("lagna", ""),
            "lagna_nak": natal.get("lagna_nak", ""),
            "moon_nakshatra": natal_moon_nak,
            "moon_rashi": natal.get("moon", {}).get("rashi", "")
                          if isinstance(natal.get("moon"), dict) else "",
            "dasha_lord": natal.get("dasha", {}).get("lord", ""),
            "dasha_closes": natal.get("dasha", {}).get("closes", ""),
        },
        "upcoming": upcoming,
        "geosolar": {
            "kp": geosolar.get("kp", ""),
            "kp_class": geosolar.get("kp_class", ""),
            "flare_class": geosolar.get("flare_class", ""),
            "solar_wind_speed": geosolar.get("solar_wind_speed", ""),
            "field_modifier": geosolar.get("field_modifier", ""),
        },
        "observe_nakshatra": _extract_observe(nak_observe),
        "observe_devi": _extract_observe(devi_observe),
    }


def _slugify(s: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.lower().replace(" ", "_").strip("_")


def _fetch_observe(entity_id: str) -> dict:
    """Call the local /observe endpoint."""
    if not entity_id:
        return {}
    try:
        req = Request(
            "http://localhost:5000/observe",
            data=json.dumps({"entity": entity_id}).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return {}


_JARGON = {
    "BP_HRV": "blood pressure and heart rate variability",
    "BP": "blood pressure",
    "HRV": "heart rate variability",
    "EEG": "brainwave activity",
    "PEER_REVIEWED": "peer-reviewed",
}


def _clean_jargon(text: str) -> str:
    """Replace technical abbreviations with plain language."""
    for abbr, expansion in _JARGON.items():
        text = text.replace(abbr, expansion)
    return text


def _extract_observe(data: dict) -> dict:
    """Pull useful fields from observe response."""
    domains = data.get("domains", {})
    result = {}

    for domain in ["ayurveda", "marma", "gandharva", "synthesis"]:
        content = domains.get(domain, {}).get("content", {})
        if isinstance(content, str):
            result[domain] = _clean_jargon(content)
        elif isinstance(content, dict):
            parts = []
            for k, v in content.items():
                if k in ("id", "type", "name_key", "attestation",
                         "attestation_status", "data"):
                    continue
                if isinstance(v, str) and v:
                    parts.append(f"{k}: {v}")
                elif isinstance(v, dict):
                    for k2, v2 in v.items():
                        if isinstance(v2, str) and v2:
                            parts.append(f"{k2}: {v2}")
            result[domain] = _clean_jargon(
                "; ".join(parts[:6]) if parts else ""
            )

    return result


# ═══════════════════════════════════════════════════════════
# BUILD PROMPT
# ═══════════════════════════════════════════════════════════

def build_prompt(data: dict) -> str:
    cur = data.get("current", {})
    nat = data.get("natal", {})
    geo = data.get("geosolar", {})
    obs_nak = data.get("observe_nakshatra", {})
    obs_devi = data.get("observe_devi", {})
    upcoming = data.get("upcoming", [])

    lines = []
    lines.append("=== CURRENT FIELD ===")
    lines.append(f"Nakshatra: {cur.get('nakshatra','')} — "
                 f"deity {cur.get('nakshatra_deity','')}, "
                 f"shakti {cur.get('nakshatra_shakti','')}")
    lines.append(f"  Themes: {cur.get('nakshatra_themes','')}")
    lines.append(f"  Element: {cur.get('nakshatra_element','')}, "
                 f"Guna: {cur.get('nakshatra_guna','')}")
    lines.append(f"Tithi: {cur.get('tithi','')} ({cur.get('paksha','')}) "
                 f"— Devi: {cur.get('tithi_devi','')}")
    lines.append(f"Hora lord: {cur.get('hora_lord','')}")
    lines.append(f"Vara: {cur.get('vara','')}")

    if obs_nak.get("ayurveda"):
        lines.append(f"Ayurveda: {obs_nak['ayurveda']}")
    if obs_nak.get("gandharva"):
        lines.append(f"Raga indicated: {obs_nak['gandharva']}")
    if obs_devi.get("synthesis"):
        lines.append(f"Devi quality: {obs_devi['synthesis']}")

    if geo.get("kp"):
        lines.append(f"Geomagnetic: Kp {geo['kp']} ({geo.get('kp_class','')}), "
                     f"wind {geo.get('solar_wind_speed','')} km/s, "
                     f"field modifier {geo.get('field_modifier','')}")

    lines.append("")
    lines.append("=== YOUR NATAL CONTEXT ===")
    lines.append(f"Lagna: {nat.get('lagna','')}, "
                 f"Moon: {nat.get('moon_rashi','')} / "
                 f"{nat.get('moon_nakshatra','')}")
    if nat.get("dasha_lord"):
        lines.append(f"Current dasha: {nat['dasha_lord']} "
                     f"(closes {nat.get('dasha_closes','')})")

    notable = [u for u in upcoming if u.get("notable")]
    if notable:
        lines.append("")
        lines.append("=== APPROACHING THIS WEEK ===")
        for u in notable:
            lines.append(f"{u['date']}: {u['nakshatra']}, {u['tithi']} "
                         f"— {u['reason']}")

    lines.append("")
    lines.append("What is worth noting about this moment "
                 "and the coming days?")

    return "\n".join(lines)


SYSTEM_PROMPT = (
    "You are reading structured Jyotish data from the Coherence Atlas database. "
    "Your task is to arrange observations into 2-3 plain sentences. "
    "Use ONLY the information provided below. "
    "Do not add knowledge not present here. "
    "Name specific entities (nakshatra, devi, graha) rather than generic descriptions. "
    "Do not predict outcomes. "
    "Observe qualities of the current moment and note what is approaching."
)


# ═══════════════════════════════════════════════════════════
# CALL OLLAMA
# ═══════════════════════════════════════════════════════════

def call_ollama(prompt: str) -> Optional[str]:
    """Call local ollama. Returns response text or None."""
    payload = json.dumps({
        "model": _OLLAMA_MODEL,
        "system": SYSTEM_PROMPT,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_predict": 150,
        },
    }).encode()

    try:
        req = Request(
            _OLLAMA_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urlopen(req, timeout=_OLLAMA_TIMEOUT) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result.get("response", "").strip() or None
    except Exception as e:
        print(f"  [briefing] ollama call failed: {e}")
        return None


# ═══════════════════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════════════════

def get_briefing(calc_panchanga: Callable,
                 field_state_fn: Callable) -> dict:
    """
    Return cached briefing if fresh, otherwise generate new one.
    Never blocks longer than ollama timeout.
    """
    global _briefing_cache, _briefing_cache_time

    now = time.time()
    if _briefing_cache and (now - _briefing_cache_time) < _CACHE_TTL:
        return _briefing_cache

    data = gather_briefing_data(calc_panchanga, field_state_fn)
    prompt = build_prompt(data)
    text = call_ollama(prompt)

    pa = data.get("current", {})
    geo = data.get("geosolar", {})

    result = {
        "text": text,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "field_snapshot": {
            "nakshatra": pa.get("nakshatra", ""),
            "tithi": pa.get("tithi", ""),
            "hora": pa.get("hora_lord", ""),
            "kp": geo.get("kp", ""),
        },
        "prompt_used": prompt,
        "upcoming_notable": [
            u for u in data.get("upcoming", []) if u.get("notable")
        ],
    }

    _briefing_cache = result
    _briefing_cache_time = now
    return result
