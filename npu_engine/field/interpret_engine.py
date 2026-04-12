"""
interpret_engine.py — Atlas Field Interpretation via Qwen3 + Corpus

Wires Ollama (Qwen3) to field state + Gaudiya corpus
for real-time cosmological field interpretation.

The system prompt grounds responses in the tradition of
Rupa Gosvami, Narottama Das Thakura, and Srila Prabhupada.
"""

import logging
import re
import requests
from typing import Dict, Optional

log = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434"
DEFAULT_MODEL = "qwen3:1.5b"

SYSTEM_PROMPT = """You are a Gaudiya Vaishnava scholar speaking from
the tradition of Rupa Gosvami, Narottama Das Thakura, and Srila Prabhupada.
You interpret cosmological field states through the lens of bhakti and lila.

Respond in 2-3 sentences. Be specific to this exact moment.
Ground your response in the scripture provided.
Do not speak generically — speak from the tradition.
Do not use markdown formatting. Plain text only."""


def get_available_model() -> str:
    """Find fastest available Qwen model."""
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        models = [m["name"] for m in r.json().get("models", [])]
        for preferred in ["qwen3:1.5b", "qwen3:0.5b", "qwen3:8b"]:
            if preferred in models:
                return preferred
        for m in models:
            if "qwen" in m.lower():
                return m
    except Exception:
        pass
    return DEFAULT_MODEL


def get_corpus_context(field_state: dict, limit: int = 3) -> str:
    """Pull relevant scripture — semantic search first, keyword fallback."""
    pa = field_state.get("panchanga", {})
    nak = pa.get("nakshatra", "")
    if isinstance(nak, dict):
        nak = nak.get("name", "")
    tithi = pa.get("tithi", "")
    if isinstance(tithi, dict):
        tithi = tithi.get("name", "")

    query = f"{nak} {tithi} devotion practice"

    # Try semantic search (NPU-powered) first
    try:
        from npu_engine.field.semantic_engine import semantic_search
        results = semantic_search(query, limit=limit, tradition="gaudiya")
        if results:
            passages = []
            for res in results[:limit]:
                source = res.get("source", "")
                text = res.get("text", "")[:250]
                if text:
                    passages.append(f"[{source}]: {text}")
            if passages:
                return "\n\n".join(passages)
    except Exception:
        pass

    # Fallback: keyword search via corpus API
    try:
        r = requests.get(
            "http://localhost:5000/corpus/search",
            params={"q": query, "limit": limit},
            timeout=3,
        )
        if r.status_code == 200:
            results = r.json().get("results", r.json().get("passages", []))
            passages = []
            for res in results[:limit]:
                source = res.get("source", res.get("text_id", ""))
                text = res.get("text", res.get("passage", res.get("excerpt", "")))[:250]
                if text:
                    passages.append(f"[{source}]: {text}")
            return "\n\n".join(passages)
    except Exception:
        pass
    return ""


def build_field_prompt(field_state: dict) -> str:
    """Build the field state description for the prompt."""
    pa = field_state.get("panchanga", {})

    def gn(obj):
        if isinstance(obj, dict):
            return obj.get("name", str(obj))
        return str(obj) if obj else "—"

    lines = [
        f"Nakshatra: {gn(pa.get('nakshatra', '—'))}",
        f"Tithi: {gn(pa.get('tithi', '—'))}",
        f"Vara: {pa.get('vara', '—')}",
        f"Nitya Devi: {gn(pa.get('devi', '—'))}",
        f"Element: {pa.get('element', '—')} · Guna: {pa.get('guna', '—')}",
    ]

    ss = field_state.get("sound_state", {})
    if ss.get("raga"):
        lines.append(f"Raga: {ss['raga']}")

    da = field_state.get("dasha", {})
    if da.get("lord"):
        lines.append(f"Dasha: {da['lord']} mahadasha")

    return "\n".join(lines)


def interpret_field(
    field_state: dict,
    query: str = "What does this moment call for?",
    model: Optional[str] = None,
) -> dict:
    """Generate a field interpretation using Qwen3 via Ollama.

    Uses /api/chat (not /api/generate) so Qwen3's /nothink flag
    is handled correctly — disabling the thinking chain that otherwise
    consumes the entire token budget.
    """
    if model is None:
        model = get_available_model()

    field_desc = build_field_prompt(field_state)
    scripture = get_corpus_context(field_state)

    user_message = f"""Current field state:
{field_desc}

Relevant scripture:
{scripture if scripture else "(corpus offline)"}

Question: {query}"""

    try:
        r = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                "stream": False,
                "think": False,  # disable Qwen3 thinking chain
                "options": {
                    "temperature": 0.7,
                    "num_predict": 120,
                    "top_p": 0.9,
                },
                "keep_alive": "10m",
            },
            timeout=90,
        )

        if r.status_code == 200:
            data = r.json()
            response = (data.get("message", {}).get("content", "")).strip()

            # Strip Qwen3 thinking tags if they still appear
            if "<think>" in response:
                response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL).strip()

            eval_dur = data.get("eval_duration", 0)
            eval_count = data.get("eval_count", 0)
            tok_per_sec = round(eval_count / (eval_dur / 1e9), 1) if eval_dur > 0 else 0

            return {
                "interpretation": response,
                "model": model,
                "field_summary": field_desc.split("\n")[0],
                "scripture_used": bool(scripture),
                "tokens_generated": eval_count,
                "duration_ms": eval_dur // 1_000_000 if eval_dur else 0,
                "tokens_per_second": tok_per_sec,
                "status": "ok",
            }
    except requests.Timeout:
        return {"interpretation": "", "status": "timeout", "model": model}
    except Exception as e:
        return {"interpretation": "", "status": f"error: {str(e)}", "model": model}
