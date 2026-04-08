"""
composition_engine.py — Field-revealed tradition composer.

The field is the query. The tradition is the answer.
Metre shapes the response. The voice carries it.

Attestation hierarchy (never invent doctrine):
  OBSERVED:PRIMARY_TEXT  → weight 1.0
  OBSERVED:TRADITIONAL   → weight 0.8
  SYNTHESIS              → weight 0.4

Pattern follows ui_vastu_engine.py:
    canonical data → internal helpers → validation → public API
"""

from typing import Any, Dict, List, Optional
import csv
import io
import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path

log = logging.getLogger(__name__)

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))

_PATHS = {
    "compositions": os.path.join(_ROOT, "datasets", "compositions", "gaudiya_compositions.csv"),
    "narottama": os.path.join(_ROOT, "datasets", "compositions", "narottama_padas.csv"),
    "metres": os.path.join(_ROOT, "datasets", "chandas", "metres_forms.csv"),
    "natal": os.path.join(_ROOT, "instance", "personal", "natal.json"),
}
_SOURCES_DIR = os.path.join(_ROOT, "datasets", "sources", "gaudiya")

_cache: Dict[str, Any] = {}


# ══════════════════════════════════════════════════════════
# DATA LOADING
# ══════════════════════════════════════════════════════════

def _load_csv(key: str) -> List[dict]:
    if key in _cache:
        return _cache[key]
    try:
        with open(_PATHS[key], encoding="utf-8") as f:
            lines = [l for l in f.readlines() if l.strip()]
            rows = list(csv.DictReader(io.StringIO("".join(lines))))
        _cache[key] = rows
        return rows
    except Exception:
        _cache[key] = []
        return []


def _load_natal() -> dict:
    if "natal" in _cache:
        return _cache["natal"]
    try:
        with open(_PATHS["natal"], encoding="utf-8") as f:
            data = json.load(f)
        _cache["natal"] = data
        return data
    except Exception:
        _cache["natal"] = {}
        return {}


def _all_compositions() -> List[dict]:
    return _load_csv("compositions") + _load_csv("narottama")


# ══════════════════════════════════════════════════════════
# MESSAGE CLASSIFICATION
# ══════════════════════════════════════════════════════════

_INTENTION_KEYWORDS = {
    "viraha":    ["dissolv", "end", "releas", "letting go", "grief", "loss",
                  "separation", "viraha", "goodbye", "death", "leaving"],
    "srishti":   ["begin", "start", "plant", "creat", "build", "new",
                  "birth", "initiat", "open", "launch"],
    "abhyasa":   ["practice", "yoga", "medit", "sadhana", "japa",
                  "chant", "mantra", "routine", "discipline"],
    "madhurya":  ["love", "devot", "bhakti", "heart", "beauty",
                  "radha", "krishna", "prema", "sweetness"],
    "dasya":     ["serve", "service", "seva", "surrender", "offer",
                  "guru", "master", "humil"],
    "jyotish":   ["guid", "what should", "direction", "timing",
                  "when", "auspicious", "plan", "decide"],
    "archetype": ["who am", "self", "atma", "identity", "purpose",
                  "why", "meaning", "nature"],
}

_RASA_FROM_INTENTION = {
    "viraha":    "karuna",
    "srishti":   "vira",
    "abhyasa":   "shanta",
    "madhurya":  "shringara",
    "dasya":     "dasya",
    "jyotish":   "shanta",
    "archetype": "adbhuta",
    "bandhu":    "shanta",
}


def _classify_message(message: str) -> str:
    msg = message.lower()
    for intention, keywords in _INTENTION_KEYWORDS.items():
        if any(k in msg for k in keywords):
            return intention
    return "bandhu"


# ══════════════════════════════════════════════════════════
# PADA SELECTION
# ══════════════════════════════════════════════════════════

def _select_pada(field_state: dict, intention: str) -> dict:
    """Select most resonant pada from corpus."""
    compositions = _all_compositions()
    if not compositions:
        return {}

    p5 = field_state.get("panchanga", {})
    target_rasa = _RASA_FROM_INTENTION.get(intention, "shanta")
    now_hour = datetime.now().hour

    scored = []
    for comp in compositions:
        score = 0.0
        notes = (comp.get("notes", "") or "").lower()
        raga = (comp.get("raga", "") or "").lower()

        # Rasa match (0.3)
        if target_rasa in notes:
            score += 0.3
        elif "shanta" in notes and target_rasa in ("abhyasa", "jyotish"):
            score += 0.2
        elif "madhurya" in notes and target_rasa == "shringara":
            score += 0.3

        # Time-of-day match via raga notes (0.25)
        if now_hour < 8 and ("dawn" in notes or "morning" in notes or "bhairav" in raga):
            score += 0.25
        elif now_hour >= 18 and ("evening" in notes or "night" in notes or "kafi" in raga or "khamaj" in raga):
            score += 0.25
        elif 10 <= now_hour < 16 and ("midday" in notes or "any time" in notes):
            score += 0.15

        # Prefer Narottama (0.15)
        if "narottama" in (comp.get("composer", "") or "").lower():
            score += 0.15

        # Intention keyword in notes (0.15)
        for kw in _INTENTION_KEYWORDS.get(intention, []):
            if kw in notes:
                score += 0.15
                break

        # Has pallavi text (0.1)
        if comp.get("pallavi_text", "").strip():
            score += 0.1

        scored.append((score, comp))

    scored.sort(key=lambda x: -x[0])
    best = scored[0][1] if scored else {}

    pallavi = best.get("pallavi_text", "")
    return {
        "opening_line": pallavi.split(",")[0].strip() if pallavi else "",
        "full_text": pallavi,
        "composer": best.get("composer", ""),
        "raga": best.get("raga", ""),
        "rasa": target_rasa,
        "language": best.get("language", ""),
        "entity_id": best.get("entity_id", ""),
        "attestation": "OBSERVED:TRADITIONAL" if pallavi else "SYNTHESIS",
    }


# ══════════════════════════════════════════════════════════
# PASSAGE SEARCH
# ══════════════════════════════════════════════════════════

_ATTESTATION_WEIGHT = {
    "OBSERVED:PRIMARY_TEXT": 1.0,
    "OBSERVED:TRADITIONAL": 0.8,
    "SYNTHESIS": 0.4,
}


def _search_passage(message: str, field_state: dict) -> dict:
    """Find relevant passage from shastra sources."""
    # Try vector store first
    try:
        from npu_engine.vector_store import get_vector_store
        vs = get_vector_store()
        if vs:
            p5 = field_state.get("panchanga", {})
            query = f"{message} {p5.get('nakshatra', '')} {p5.get('element', '')}"
            results = vs.search(query, top_k=3)
            if results:
                best = results[0]
                return {
                    "text": best.get("text", "")[:300],
                    "source": best.get("source", ""),
                    "chapter_verse": best.get("verse_ref", best.get("id", "")),
                    "attestation": "OBSERVED:PRIMARY_TEXT",
                    "coherence_score": round(best.get("score", 0.0), 3),
                }
    except Exception:
        pass

    # Fallback: keyword search JSONL files
    return _keyword_search_jsonl(message, field_state)


def _keyword_search_jsonl(message: str, field_state: dict) -> dict:
    """Direct keyword search across JSONL source files."""
    keywords = set(re.split(r"[^a-zA-Z]+", message.lower()))
    keywords = {w for w in keywords if len(w) >= 4}
    if not keywords:
        keywords = {"krishna", "devotion"}

    best_text = ""
    best_source = ""
    best_score = 0.0

    sources = [
        "brahma_samhita_chunks.jsonl",
        "sikshashtakam_chunks.jsonl",
        "bhakti_rasamrita_sindhu_en_1_chunks.jsonl",
    ]

    for src_file in sources:
        src_path = os.path.join(_SOURCES_DIR, src_file)
        if not os.path.exists(src_path):
            continue
        try:
            with open(src_path, encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        chunk = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    text = chunk.get("text", "").lower()
                    score = sum(1 for kw in keywords if kw in text)
                    if score > best_score and len(chunk.get("text", "")) > 20:
                        best_score = score
                        best_text = chunk.get("text", "")[:300]
                        best_source = chunk.get("source", src_file.replace("_chunks.jsonl", ""))
        except Exception:
            continue

    if best_text:
        return {
            "text": best_text,
            "source": best_source,
            "chapter_verse": "",
            "attestation": "OBSERVED:PRIMARY_TEXT",
            "coherence_score": round(min(1.0, best_score / max(len(keywords), 1)), 3),
        }

    # Final fallback: field description
    p5 = field_state.get("panchanga", {})
    return {
        "text": "",
        "source": "field",
        "chapter_verse": "",
        "attestation": "SYNTHESIS",
        "coherence_score": 0.0,
    }


# ══════════════════════════════════════════════════════════
# METRE SELECTION
# ══════════════════════════════════════════════════════════

_RASA_METRE_MAP = {
    "shringara": "mandakranta",
    "karuna": "anustubh",
    "vira": "shardulvikridita",
    "shanta": "anustubh",
    "adbhuta": "shikhirini",
    "dasya": "anustubh",
    "madhurya": "vasantatilaka",
    "raudra": "shardulvikridita",
    "hasya": "arya",
    "bhayanaka": "anustubh",
}


def _select_metre(rasa: str) -> dict:
    """Select chandas metre by rasa affinity."""
    metres = _load_csv("metres") if "metres" not in _cache else _cache["metres"]
    if not metres:
        # Load fresh
        try:
            with open(_PATHS["metres"], encoding="utf-8") as f:
                lines = [l for l in f.readlines() if l.strip()]
                metres = list(csv.DictReader(io.StringIO("".join(lines))))
            _cache["metres"] = metres
        except Exception:
            metres = []

    target_name = _RASA_METRE_MAP.get(rasa, "anustubh")

    for m in metres:
        name = m.get("name_iast", "").lower()
        if target_name in name.replace("ā", "a").replace("ī", "i").replace("ṛ", "r").replace("ṣ", "sh").replace("ś", "sh"):
            return {
                "name": m.get("name_iast", ""),
                "syllables_per_pada": m.get("syllables_per_pada", ""),
                "rasa_affinity": m.get("rasa_primary", ""),
                "use_case": m.get("use_case", ""),
            }

    return {"name": "Anuṣṭubh", "syllables_per_pada": "8", "rasa_affinity": "śānta", "use_case": ""}


# ══════════════════════════════════════════════════════════
# RESPONSE COMPOSITION
# ══════════════════════════════════════════════════════════

def _llm_connector(pada: dict, passage: dict, field_state: dict,
                    metre: dict) -> Optional[str]:
    """Ask Qwen3:8b for ONE connecting sentence. Never raises."""
    opening = pada.get("opening_line", "")
    passage_text = passage.get("text", "")
    if not opening or not passage_text:
        return None

    p5 = field_state.get("panchanga", {})
    rasa = pada.get("rasa", "shanta")
    nak = p5.get("nakshatra", "")

    elem = p5.get("element", "")

    system = (
        "You are connecting two sacred texts. "
        "Write exactly ONE sentence under 25 words. "
        "Do not invent doctrine or spiritual claims. "
        "Only connect these two passages with a transitional thought. "
        "Write in present tense. No commentary."
    )
    prompt = (
        f"Passage 1: {opening}\n"
        f"Passage 2: {passage_text[:200]}\n"
        f"Field: {nak} \u00b7 {elem} \u00b7 {rasa}\n"
        f"One connecting sentence:"
    )

    try:
        import urllib.request
        req = urllib.request.Request(
            "http://localhost:11434/api/generate",
            data=json.dumps({
                "model": "qwen3:8b",
                "prompt": prompt + "\n/no_think",
                "system": system,
                "stream": False,
                "options": {"temperature": 0.3, "num_predict": 80},
            }).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
        text = result.get("response", "").strip()

        # Qwen3 may put output in 'thinking' field instead of 'response'
        if not text:
            text = result.get("thinking", "").strip()

        # Strip <think>...</think> tags (Qwen3 thinks out loud)
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

        # Take only the first sentence
        for delim in [".", "।", "\n"]:
            if delim in text:
                text = text[:text.index(delim) + 1]
                break

        # Reject if too long or empty
        if not text or len(text.split()) > 25:
            return None

        log.info("llm connector: %s", text[:80])
        return text

    except Exception as e:
        log.warning("llm connector failed: %s", e)
        return None


def _compose_with_llm(pada: dict, passage: dict, field_state: dict,
                      metre: dict) -> str:
    """Build response text with LLM connector sentence between pada and passage."""
    connector = _llm_connector(pada, passage, field_state, metre)

    parts = []
    opening = pada.get("opening_line", "")
    if opening:
        parts.append(opening)

    if connector:
        parts.append(connector)

    passage_text = passage.get("text", "")
    if passage_text and passage_text != opening:
        parts.append(passage_text[:250])

    # Attribution
    composer = pada.get("composer", "")
    raga = pada.get("raga", "")
    rasa = pada.get("rasa", "")
    attr_parts = []
    if composer:
        attr_parts.append(composer)
    if raga:
        attr_parts.append(raga)
    if rasa:
        attr_parts.append(rasa)
    if metre.get("name"):
        attr_parts.append(metre["name"])
    if attr_parts:
        parts.append("\u2014 " + " \u00b7 ".join(attr_parts))

    return "\n\n".join(p for p in parts if p), connector


def _compose_without_llm(pada: dict, passage: dict, field_state: dict,
                         metre: dict) -> str:
    """Build response text from tradition parts. No LLM."""
    parts = []

    opening = pada.get("opening_line", "")
    if opening:
        parts.append(opening)

    passage_text = passage.get("text", "")
    if passage_text and passage_text != opening:
        parts.append(passage_text[:250])

    # Attribution
    composer = pada.get("composer", "")
    raga = pada.get("raga", "")
    rasa = pada.get("rasa", "")
    attr_parts = []
    if composer:
        attr_parts.append(composer)
    if raga:
        attr_parts.append(raga)
    if rasa:
        attr_parts.append(rasa)
    if metre.get("name"):
        attr_parts.append(metre["name"])
    if attr_parts:
        parts.append("\u2014 " + " \u00b7 ".join(attr_parts))

    # Field moment
    p5 = field_state.get("panchanga", {})
    nak = p5.get("nakshatra", "")
    tithi = p5.get("tithi", "")
    elem = p5.get("element", "")
    if nak:
        parts.append(f"{nak} \u00b7 {tithi} \u00b7 {elem}")

    return "\n\n".join(p for p in parts if p)


def _speak_response(pada: dict, field_state: dict, natal: dict) -> bool:
    """Try to speak the pada via vocal_kernel. Never raises."""
    try:
        from npu_engine.vocal.vocal_kernel import VocalKernel
        # Check if vocal kernel is available and wired
        return False  # Not yet wired — return False for now
    except Exception:
        return False


def _derive_musical_response(pada: dict, field_state: dict) -> dict:
    """Musical response from pada."""
    try:
        from .trajectory_engine import derive_trajectory
        traj = derive_trajectory(field_state)
        tempo = traj.get("musical_implication", {}).get("tempo_trend", "stable")
    except Exception:
        tempo = "stable"

    return {
        "raga": pada.get("raga", ""),
        "rasa": pada.get("rasa", ""),
        "tempo": tempo,
        "instrument_emphasis": "sarangi" if pada.get("rasa") in ("karuna", "shringara") else "tanpura",
    }


# ══════════════════════════════════════════════════════════
# VALIDATION
# ══════════════════════════════════════════════════════════

def _validate(spec: dict) -> dict:
    defaults = {
        "pada": {"opening_line": "", "composer": "", "raga": "", "rasa": "",
                 "language": "", "attestation": ""},
        "passage": {"text": "", "source": "", "chapter_verse": "",
                    "attestation": "", "coherence_score": 0.0},
        "connector": None,
        "metre": {"name": "", "syllables_per_pada": "", "rasa_affinity": ""},
        "response_text": "",
        "rasa": "",
        "spoken": False,
        "musical_response": {"raga": "", "rasa": "", "tempo": "stable",
                             "instrument_emphasis": "tanpura"},
        "attestation": "SYNTHESIS",
    }
    for key, default in defaults.items():
        if key not in spec or spec[key] is None:
            spec[key] = default
        elif isinstance(default, dict) and isinstance(spec[key], dict):
            for dk, dv in default.items():
                if dk not in spec[key]:
                    spec[key][dk] = dv
    return spec


# ══════════════════════════════════════════════════════════
# PUBLIC API
# ══════════════════════════════════════════════════════════

def compose_response(message: str, field_state: dict,
                     natal: dict = None, speak: bool = False,
                     use_llm: bool = False) -> dict:
    """Field-revealed tradition composition. Never raises.

    Args:
        message: user's inquiry
        field_state: from kernel field_state()
        natal: from natal.json (auto-loaded if None)
        speak: whether to fire vocal_kernel
        use_llm: whether to use LLM connector (future)

    Returns validated CompositionSpec — all keys guaranteed.
    """
    try:
        if natal is None:
            natal = _load_natal()

        # 1. Classify
        intention = _classify_message(message)
        rasa = _RASA_FROM_INTENTION.get(intention, "shanta")
        log.info("compose: intention=%s rasa=%s", intention, rasa)

        # 2. Select pada
        pada = _select_pada(field_state, intention)
        log.info("compose: pada=%s · %s", pada.get("composer", "?"), pada.get("rasa", "?"))

        # 3. Search passage
        passage = _search_passage(message, field_state)
        log.info("compose: passage=%s score=%.2f",
                 passage.get("source", "?"), passage.get("coherence_score", 0))

        # 4. Select metre
        metre = _select_metre(rasa)

        # 5. Compose
        connector = None
        if use_llm:
            response_text, connector = _compose_with_llm(pada, passage, field_state, metre)
        else:
            response_text = _compose_without_llm(pada, passage, field_state, metre)

        # 6. Speak
        spoken = False
        if speak:
            spoken = _speak_response(pada, field_state, natal)

        # 7. Musical response
        musical = _derive_musical_response(pada, field_state)

        # Determine overall attestation
        att_levels = [
            pada.get("attestation", "SYNTHESIS"),
            passage.get("attestation", "SYNTHESIS"),
        ]
        if any("PRIMARY_TEXT" in a for a in att_levels):
            attestation = "OBSERVED:PRIMARY_TEXT"
        elif any("TRADITIONAL" in a for a in att_levels):
            attestation = "OBSERVED:TRADITIONAL"
        else:
            attestation = "SYNTHESIS"

        spec = {
            "pada": pada,
            "passage": passage,
            "connector": connector,
            "metre": metre,
            "response_text": response_text,
            "rasa": rasa,
            "spoken": spoken,
            "musical_response": musical,
            "attestation": attestation,
        }
        return _validate(spec)

    except Exception as e:
        log.warning("compose_response failed: %s", e)
        return _validate({"attestation": "SYNTHESIS"})
