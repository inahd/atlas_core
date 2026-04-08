"""
passage_resolver.py — Find and rank text passages for any entity.

Sources:
  1. datasets/sources/entity_index.json → chunk IDs → JSONL chunks
  2. datasets/sources/passages.csv → tagged passages
  3. datasets/relations/text_entity_relations.csv → chunk→entity links

Ranking:
  1. Tradition weight (bhagavatam > parashara etc)
  2. Confidence score from relation
  3. Tag match quality
"""

import csv
import json
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "datasets" / "sources"

# Tradition → source file patterns
_TRADITION_MAP = {
    "bhagavatam": ["bhagavatam", "sb_", "bhagavata"],
    "gaudiya_commentary": ["bhakti_rasamrita", "brihad_bhagavatamrita", "hari_bhakti"],
    "bhakti_rasamrita": ["bhakti_rasamrita", "nectar_of_devotion"],
    "tantraraja": ["tantraloka", "vijnana_bhairava", "kularnava", "mahanirvana"],
    "parashara": ["brihat_parashara", "parashara"],
    "caraka_sushruta": ["charaka", "sushruta", "ashtanga"],
    "natyashastra": ["natyashastra", "natya"],
    "sangita_ratnakara": ["sangita_ratnakara", "sangita"],
    "brihat_samhita": ["brihat_samhita"],
}

_TRADITION_WEIGHT = {
    "bhagavatam": 1.0, "gaudiya_commentary": 0.95, "bhakti_rasamrita": 0.92,
    "tantraraja": 0.88, "parashara": 0.85, "caraka_sushruta": 0.80,
    "natyashastra": 0.78, "sangita_ratnakara": 0.75, "brihat_samhita": 0.72,
}

# Cached data
_entity_index: Optional[Dict] = None
_passages_by_tag: Optional[Dict[str, List]] = None


def _load_entity_index() -> dict:
    global _entity_index
    if _entity_index is not None:
        return _entity_index
    idx_path = SOURCES / "entity_index.json"
    if idx_path.exists():
        _entity_index = json.loads(idx_path.read_text())
    else:
        _entity_index = {}
    return _entity_index


def _load_passages_by_tag() -> dict:
    global _passages_by_tag
    if _passages_by_tag is not None:
        return _passages_by_tag
    _passages_by_tag = {}
    pc = SOURCES / "passages.csv"
    if not pc.exists():
        return _passages_by_tag
    with pc.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            tags = row.get("tags", "")
            if not tags:
                continue
            for tag in tags.split(";"):
                tag = tag.strip()
                if ":" in tag:
                    _passages_by_tag.setdefault(tag, []).append(row)
    return _passages_by_tag


def _guess_tradition(source: str) -> str:
    """Guess tradition from source/filename."""
    sl = source.lower()
    for tradition, patterns in _TRADITION_MAP.items():
        for pat in patterns:
            if pat in sl:
                return tradition
    return "modern_practice"


def _extract_entity_ids(text: str, entity_id: str) -> list:
    """Find entity IDs mentioned in passage text."""
    # Simple: return the primary entity
    ids = [entity_id]
    # Check for common entity patterns in text
    import re
    # Look for IAST names that might be entities
    for pat, prefix in [
        (r"\b(Kāmeśvarī|Bhagamālinī|Nityaklinnā|Bheruṇḍā|Vahnivāsinī)", "devi_"),
        (r"\b(Yaman|Bhairavī|Bhairav|Tōḍī|Mārvā|Darbārī)", "raga_"),
    ]:
        for m in re.finditer(pat, text):
            name = m.group(1).lower().replace("ā","a").replace("ī","i").replace("ū","u")
            name = re.sub(r"[^a-z]", "", name)
            ids.append(prefix + name)
    return list(set(ids))


def find_passages(entity_id: str, limit: int = 5) -> list:
    """Find passages mentioning an entity, ranked by tradition weight."""
    results = []

    # 1. From entity_index.json → JSONL chunks
    idx = _load_entity_index()
    chunk_ids = idx.get(entity_id, [])[:limit * 2]
    for cid in chunk_ids:
        parts = cid.split(":", 1)
        if len(parts) != 2:
            continue
        src, num = parts
        for jf in SOURCES.rglob(f"{src}_chunks.jsonl"):
            try:
                with jf.open() as f:
                    for line in f:
                        ch = json.loads(line)
                        if str(ch.get("id")) == num:
                            text = ch.get("text", "")[:500]
                            tradition = _guess_tradition(src)
                            results.append({
                                "text": text,
                                "source": src,
                                "verse_ref": ch.get("verse_ref", ""),
                                "domain": ch.get("domain", jf.parent.name),
                                "tradition": tradition,
                                "confidence": _TRADITION_WEIGHT.get(tradition, 0.5),
                                "entity_ids": _extract_entity_ids(text, entity_id),
                                "gaudiya_aligned": tradition in (
                                    "bhagavatam", "gaudiya_commentary",
                                    "bhakti_rasamrita", "tantraraja"),
                            })
                            break
            except Exception:
                pass
            break

    # 2. From passages.csv tags
    tag_index = _load_passages_by_tag()
    # Try entity_id as tag (e.g. "nakshatra:Hasta")
    tag_formats = [
        entity_id,
        entity_id.replace("_", ":"),
        entity_id.split("_", 1)[0] + ":" + entity_id.split("_", 1)[-1].title() if "_" in entity_id else "",
    ]
    seen_texts = {r["text"][:50] for r in results}
    for tag in tag_formats:
        for passage in tag_index.get(tag, []):
            text = passage.get("excerpt", "")[:500]
            if text[:50] in seen_texts:
                continue
            seen_texts.add(text[:50])
            source = passage.get("source_id", "")
            tradition = _guess_tradition(source)
            results.append({
                "text": text,
                "source": source,
                "verse_ref": passage.get("locator", ""),
                "domain": "",
                "tradition": tradition,
                "confidence": _TRADITION_WEIGHT.get(tradition, 0.5),
                "entity_ids": [entity_id],
                "gaudiya_aligned": tradition in (
                    "bhagavatam", "gaudiya_commentary",
                    "bhakti_rasamrita", "tantraraja"),
            })

    # Sort by tradition weight descending
    results.sort(key=lambda r: -r.get("confidence", 0))
    return results[:limit]
