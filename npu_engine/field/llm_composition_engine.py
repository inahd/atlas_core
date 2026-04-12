"""
llm_composition_engine.py — LLM-driven Vedic composition engine.

Qwen3:8b generates structured verse + melody + rhythm as JSON,
validated against chandas metre grammar and raga scale rules.
"""

import csv
import io
import json
import logging
import os
import re
import time
from typing import Any, Dict, List, Optional, Tuple

import requests

log = logging.getLogger(__name__)

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))

OLLAMA_URL = "http://localhost:11434"
MODEL = "qwen3:8b"

_NAROTTAMA_PATH = os.path.join(_ROOT, "datasets", "compositions", "narottama_padas.csv")

_OUTPUT_SCHEMA = {
    "verse": {
        "lines": ["line 1", "line 2", "line 3", "line 4"],
        "language": "bengali_transliterated",
        "metre": "metre_name",
    },
    "melody": {
        "phrases": [
            {"swaras": ["Sa", "Ga", "Ma", "Pa"], "durations": [1.0, 0.5, 0.5, 1.5]},
            {"swaras": ["Dha", "Ni", "SA", "Ni"], "durations": [0.5, 0.5, 1.0, 1.0]},
        ],
        "raga": "raga_name",
    },
    "rhythm": {
        "tala": "tala_name",
        "tempo": "madhya_laya",
    },
    "rasa": "shrngara",
    "mood": "A sentence about this moment's devotional quality",
}

# ══════════════════════════════════════════════════════════
# DATA HELPERS
# ══════════════════════════════════════════════════════════

_cache: Dict[str, Any] = {}


def _load_narottama_padas() -> List[dict]:
    """Load narottama_padas.csv, cached."""
    if "narottama" in _cache:
        return _cache["narottama"]
    try:
        with open(_NAROTTAMA_PATH, encoding="utf-8") as f:
            lines = [l for l in f.readlines() if l.strip()]
            rows = list(csv.DictReader(io.StringIO("".join(lines))))
        _cache["narottama"] = rows
        return rows
    except Exception:
        _cache["narottama"] = []
        return []


def _gamak_level(field_state: dict) -> str:
    """Derive gamak intensity from coherence score."""
    sv = field_state.get("svarodaya", {})
    coherence = sv.get("coherence_score", 0.5)
    if isinstance(coherence, str):
        try:
            coherence = float(coherence)
        except ValueError:
            coherence = 0.5
    if coherence >= 0.85:
        return "high"
    elif coherence >= 0.5:
        return "medium"
    return "low"


def _match_padas(raga: str, rasa: str, limit: int = 3) -> List[str]:
    """Pick example pallavis from narottama_padas matching raga or rasa mood."""
    padas = _load_narottama_padas()
    if not padas:
        return []

    raga_l = raga.lower() if raga else ""
    rasa_l = rasa.lower() if rasa else ""

    # Rasa keyword mapping for notes field
    rasa_keywords = {
        "shringara": ["madhurya", "sweet", "love", "romantic"],
        "shrngara": ["madhurya", "sweet", "love", "romantic"],
        "karuna": ["lament", "mournful", "grief", "separation", "viraha"],
        "vira": ["hero", "glory", "strength"],
        "shanta": ["peace", "morning", "meditation", "guru"],
        "adbhuta": ["wonder", "transcendental"],
        "dasya": ["mercy", "service", "surrender"],
    }
    rasa_kws = rasa_keywords.get(rasa_l, [])

    scored = []
    for p in padas:
        score = 0.0
        p_raga = (p.get("raga", "") or "").lower()
        p_notes = (p.get("notes", "") or "").lower()
        pallavi = (p.get("pallavi_text", "") or "").strip()
        if not pallavi:
            continue

        # Raga match
        if raga_l and raga_l in p_raga:
            score += 1.0
        # Partial raga match (first word)
        elif raga_l and raga_l.split()[0] in p_raga:
            score += 0.5

        # Rasa/mood match via notes
        for kw in rasa_kws:
            if kw in p_notes:
                score += 0.3
                break

        scored.append((score, pallavi))

    scored.sort(key=lambda x: -x[0])
    return [s[1] for s in scored[:limit]]


# ══════════════════════════════════════════════════════════
# 1. GET FIELD MUSIC CONTEXT
# ══════════════════════════════════════════════════════════

def get_field_music_context(field_state: dict) -> dict:
    """Pull from chandas_engine, raga_engine, and narottama_padas.csv."""
    # Chandas
    metre_data = {}
    try:
        from npu_engine.field.chandas_engine import derive_chandas
        ch = derive_chandas(field_state)
        metre_data = {
            "name": ch.get("primary_metre", "Anustubh"),
            "syllables": ch.get("syllables_per_pada", 8),
            "cadence_pattern": ch.get("cadence_pattern", ""),
        }
    except Exception as e:
        log.warning("chandas_engine unavailable: %s", e)
        metre_data = {"name": "Anustubh", "syllables": 8, "cadence_pattern": ""}

    # Raga
    raga_data = {}
    try:
        from npu_engine.sound.raga_engine import derive_raga_phrase
        rp = derive_raga_phrase(field_state)
        raga_data = {
            "raga": rp.get("raga", "Bihag"),
            "swaras": rp.get("swaras", []),
            "frequencies": rp.get("frequencies", []),
        }
    except Exception as e:
        log.warning("raga_engine unavailable: %s", e)
        raga_data = {"raga": "Bihag", "swaras": ["Sa", "Ga", "Ma", "Pa", "Ni"], "frequencies": []}

    # Rasa from panchanga
    pa = field_state.get("panchanga", {})
    rasa_map = {
        "sattva": "shringara",
        "rajas": "vira",
        "tamas": "karuna",
    }
    guna = pa.get("guna", "sattva") or "sattva"
    rasa = rasa_map.get(guna.lower(), "shringara")

    # Example padas
    examples = _match_padas(raga_data.get("raga", ""), rasa)

    return {
        "raga": raga_data.get("raga", "Bihag"),
        "swaras": raga_data.get("swaras", []),
        "frequencies": raga_data.get("frequencies", []),
        "metre": metre_data,
        "rasa": rasa,
        "examples": examples,
        "gamak_level": _gamak_level(field_state),
    }


# ══════════════════════════════════════════════════════════
# 2. BUILD COMPOSITION PROMPT
# ══════════════════════════════════════════════════════════

def build_composition_prompt(field_state: dict, context: dict) -> Tuple[str, str]:
    """Returns (system_prompt, user_prompt)."""
    system_prompt = (
        "You are a Gaudiya Vaishnava composer in the tradition of "
        "Narottama Das Thakura. You compose devotional verses with "
        "matching melody specifications. Respond ONLY with valid JSON, "
        "no other text."
    )

    pa = field_state.get("panchanga", {})

    def gn(obj):
        if isinstance(obj, dict):
            return obj.get("name", str(obj))
        return str(obj) if obj else ""

    nakshatra = gn(pa.get("nakshatra", ""))
    tithi = gn(pa.get("tithi", ""))
    raga = context.get("raga", "Bihag")
    metre = context.get("metre", {})
    metre_name = metre.get("name", "Anustubh")
    syllables = metre.get("syllables", 8)
    cadence = metre.get("cadence_pattern", "")
    swaras = context.get("swaras", [])
    rasa = context.get("rasa", "shringara")
    examples = context.get("examples", [])

    # Build examples block
    examples_block = ""
    if examples:
        ex_lines = []
        for i, ex in enumerate(examples, 1):
            ex_lines.append(f"  {i}. \"{ex}\"")
        examples_block = "Example pallavis from Narottama Das Thakura:\n" + "\n".join(ex_lines)

    user_prompt = f"""Current field state:
  Nakshatra: {nakshatra}
  Tithi: {tithi}
  Raga: {raga}
  Metre: {metre_name} ({syllables} syllables per pada)
  Cadence pattern: {cadence if cadence else 'not specified'}
  Rasa: {rasa}
  Available swaras: {', '.join(swaras) if swaras else 'Sa Re Ga Ma Pa Dha Ni SA'}

{examples_block}

Compose a 4-line devotional verse in Bengali transliteration with matching melody and rhythm.
Each melody phrase should use only the available swaras listed above.
Each line should aim for approximately {syllables} syllables.

Respond with this exact JSON structure:
{json.dumps(_OUTPUT_SCHEMA, indent=2)}

Replace all placeholder values with your actual composition. JSON only, no commentary."""

    return system_prompt, user_prompt


# ══════════════════════════════════════════════════════════
# 3. CALL QWEN3
# ══════════════════════════════════════════════════════════

def call_qwen3(system: str, prompt: str) -> dict:
    """POST to Ollama /api/chat with think:false. Timeout 90s."""
    try:
        r = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                "stream": False,
                "think": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 512,
                    "top_p": 0.9,
                },
                "keep_alive": "10m",
            },
            timeout=90,
        )

        if r.status_code != 200:
            return {"error": f"Ollama returned {r.status_code}: {r.text[:200]}"}

        data = r.json()
        content = (data.get("message", {}).get("content", "")).strip()

        # Strip thinking tags if present
        if "<think>" in content:
            content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()

        # Extract JSON from content (may have markdown fences)
        json_match = re.search(r"\{[\s\S]*\}", content)
        if not json_match:
            return {"error": "No JSON found in response", "raw": content[:500]}

        parsed = json.loads(json_match.group())

        # Attach timing info
        eval_dur = data.get("eval_duration", 0)
        eval_count = data.get("eval_count", 0)
        parsed["_meta"] = {
            "tokens": eval_count,
            "duration_ms": eval_dur // 1_000_000 if eval_dur else 0,
            "tok_per_sec": round(eval_count / (eval_dur / 1e9), 1) if eval_dur > 0 else 0,
        }
        return parsed

    except requests.Timeout:
        return {"error": "Ollama timeout (90s)"}
    except json.JSONDecodeError as e:
        return {"error": f"JSON parse failed: {e}", "raw": content[:500] if 'content' in dir() else ""}
    except Exception as e:
        return {"error": f"Ollama call failed: {e}"}


# ══════════════════════════════════════════════════════════
# 4. VALIDATE COMPOSITION
# ══════════════════════════════════════════════════════════

def validate_composition(
    composition: dict, metre_data: dict, raga_data: dict
) -> Tuple[bool, List[str]]:
    """Validate composition against metre and raga rules.

    Returns (valid, list_of_errors).
    """
    errors = []

    # Check basic structure
    verse = composition.get("verse", {})
    melody = composition.get("melody", {})

    if not verse.get("lines"):
        errors.append("Missing verse.lines")
    if not melody.get("phrases"):
        errors.append("Missing melody.phrases")

    # Syllable count check
    syllables_target = metre_data.get("syllables", 0)
    if syllables_target and isinstance(syllables_target, (int, float)) and syllables_target > 0:
        lines = verse.get("lines", [])
        for i, line in enumerate(lines):
            # Count syllables: approximate by counting vowel clusters
            vowels = re.findall(r"[aeiouāīūṛṝḷaiauoéè]+", line.lower())
            count = len(vowels)
            target = int(syllables_target)
            # Allow +/- 3 syllable tolerance (transliteration varies)
            if abs(count - target) > 3:
                errors.append(
                    f"Line {i+1}: ~{count} syllables, expected ~{target}"
                )

    # Raga scale check: verify all swaras in melody are in the raga scale
    available_swaras = set(raga_data.get("swaras", []))
    if available_swaras:
        phrases = melody.get("phrases", [])
        for i, phrase in enumerate(phrases):
            phrase_swaras = phrase.get("swaras", [])
            for sw in phrase_swaras:
                if sw not in available_swaras:
                    errors.append(
                        f"Phrase {i+1}: swara '{sw}' not in raga scale "
                        f"{sorted(available_swaras)}"
                    )

    # Check durations exist and match swaras count
    phrases = melody.get("phrases", [])
    for i, phrase in enumerate(phrases):
        sw = phrase.get("swaras", [])
        dur = phrase.get("durations", [])
        if sw and dur and len(sw) != len(dur):
            errors.append(
                f"Phrase {i+1}: {len(sw)} swaras but {len(dur)} durations"
            )

    valid = len(errors) == 0
    return valid, errors


# ══════════════════════════════════════════════════════════
# 5. COMPOSE (main entry point)
# ══════════════════════════════════════════════════════════

def compose(field_state: dict, max_attempts: int = 2) -> dict:
    """LLM-driven composition: build prompt, call Qwen3, validate, retry.

    Returns final composition dict with metadata.
    """
    t0 = time.time()

    # Get context
    context = get_field_music_context(field_state)

    # Build prompt
    system, user_prompt = build_composition_prompt(field_state, context)

    all_errors = []
    composition = {}

    for attempt in range(1, max_attempts + 1):
        # On retry, append validation errors to the prompt
        if attempt > 1 and all_errors:
            error_block = "\n".join(f"- {e}" for e in all_errors)
            user_prompt_with_errors = (
                user_prompt
                + f"\n\nYour previous attempt had these errors:\n{error_block}\n"
                + "Please fix them. Respond with corrected JSON only."
            )
            composition = call_qwen3(system, user_prompt_with_errors)
        else:
            composition = call_qwen3(system, user_prompt)

        # Check for Ollama-level errors
        if "error" in composition and "verse" not in composition:
            all_errors.append(composition["error"])
            continue

        # Validate
        metre_data = context.get("metre", {})
        raga_data = {"swaras": context.get("swaras", [])}
        valid, errors = validate_composition(composition, metre_data, raga_data)

        if valid:
            break

        all_errors.extend(errors)

    # Build final result
    duration_ms = int((time.time() - t0) * 1000)
    meta = composition.pop("_meta", {})

    valid_final, final_errors = validate_composition(
        composition,
        context.get("metre", {}),
        {"swaras": context.get("swaras", [])},
    )

    result = {
        "verse": composition.get("verse", {}),
        "melody": composition.get("melody", {}),
        "rhythm": composition.get("rhythm", {}),
        "rasa": composition.get("rasa", context.get("rasa", "")),
        "mood": composition.get("mood", ""),
        "valid": valid_final,
        "errors": final_errors,
        "model": MODEL,
        "duration_ms": duration_ms,
        "tokens": meta.get("tokens", 0),
        "tok_per_sec": meta.get("tok_per_sec", 0),
        "context": {
            "raga": context.get("raga", ""),
            "metre": context.get("metre", {}).get("name", ""),
            "rasa": context.get("rasa", ""),
            "gamak_level": context.get("gamak_level", ""),
        },
        "status": "ok",
    }
    return result


# ══════════════════════════════════════════════════════════
# 6. EXECUTE COMPOSITION (send to SC via OSC)
# ══════════════════════════════════════════════════════════

def execute_composition(composition: dict) -> dict:
    """Send melody phrases to SuperCollider via OSC.

    Uses /atlas/phrase message format:
      [freq1, freq2, freq3, dur1, dur2, dur3, gamak_rate, gamak_depth, gamak_idx, amp, pan]
    """
    try:
        from pythonosc.udp_client import SimpleUDPClient
    except ImportError:
        return {"sent": False, "error": "python-osc not installed", "phrases": 0}

    try:
        from npu_engine.sound.raga_engine import SWARA_RATIOS
    except ImportError:
        SWARA_RATIOS = {
            'Sa': 1.0, 'Re': 9/8, 're': 16/15, 'Ga': 5/4, 'ga': 6/5,
            'Ma': 4/3, 'ma': 45/32, 'Pa': 3/2, 'Dha': 5/3, 'dha': 8/5,
            'Ni': 15/8, 'ni': 9/5, 'SA': 2.0,
        }

    SA_HZ = 130.81  # default Sa frequency

    melody = composition.get("melody", {})
    phrases = melody.get("phrases", [])
    if not phrases:
        return {"sent": False, "error": "no melody phrases", "phrases": 0}

    # Gamak defaults
    gamak_rate = 3.0
    gamak_depth = 20.0
    gamak_idx = 0
    amp = 0.3
    pan = 0.0

    client = SimpleUDPClient("127.0.0.1", 57120)
    sent_count = 0

    for phrase in phrases:
        swaras = phrase.get("swaras", [])
        durations = phrase.get("durations", [])

        if not swaras:
            continue

        # Convert swaras to frequencies
        freqs = [SA_HZ * SWARA_RATIOS.get(s, 1.0) for s in swaras]

        # Pad/trim to 3 notes per OSC message (send multiple if longer)
        for i in range(0, len(freqs), 3):
            chunk_freqs = freqs[i:i+3]
            chunk_durs = durations[i:i+3] if durations else [1.0] * len(chunk_freqs)

            # Pad to exactly 3
            while len(chunk_freqs) < 3:
                chunk_freqs.append(chunk_freqs[-1])
            while len(chunk_durs) < 3:
                chunk_durs.append(chunk_durs[-1])

            msg = chunk_freqs + chunk_durs + [gamak_rate, gamak_depth, gamak_idx, amp, pan]
            client.send_message("/atlas/phrase", msg)
            sent_count += 1

    return {"sent": True, "phrases": sent_count}
