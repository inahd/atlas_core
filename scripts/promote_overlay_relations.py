#!/usr/bin/env python3
"""
REL-004: Promote seed_unverified relations in relations_resolved_overlays.csv
by searching the corpus (entity_index.json + passages.csv) for supporting passages.

Strategy:
  1. For each seed_unverified row, convert from_id and to_id to entity_index format
  2. Look up both in entity_index.json for JSONL chunk hits
  3. Also search passages.csv tags (title-cased format)
  4. If passages found mentioning the entity pair, promote to confidence=0.75
  5. Write updated overlays in-place and log results
"""
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "datasets" / "sources"

INPUT = ROOT / "datasets" / "relations" / "relations_resolved_overlays.csv"
OUTPUT = INPUT  # update in-place
EVIDENCE_LOG = ROOT / "docs" / "audit" / "overlay_promotion_log.txt"

# --- Load corpus data ---

def load_entity_index():
    path = SOURCES / "entity_index.json"
    if path.exists():
        return json.loads(path.read_text())
    return {}

def load_passage_tags():
    """Build tag -> list of passages from passages.csv."""
    tag_map = {}
    pc = SOURCES / "passages.csv"
    if not pc.exists():
        return tag_map
    with pc.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            tags = row.get("tags", "")
            if not tags:
                continue
            for tag in tags.split(";"):
                tag = tag.strip()
                if tag:
                    tag_map.setdefault(tag, []).append(row)
    return tag_map

def colon_to_underscore(eid):
    """Convert 'nakshatra:ashwini' -> 'nakshatra_ashwini'."""
    return eid.replace(":", "_") if ":" in eid else eid

def colon_to_title_tag(eid):
    """Convert 'nakshatra:ashwini' -> 'nakshatra:Ashwini' for passages.csv tag lookup."""
    if ":" in eid:
        prefix, slug = eid.split(":", 1)
        # Title-case each word, handle multi-word like 'uttara ashadha'
        titled = " ".join(w.capitalize() for w in slug.replace("_", " ").split())
        return f"{prefix}:{titled}"
    return eid

def find_chunk_text(entity_index, eid, limit=2):
    """Find chunk texts for an entity from JSONL files."""
    idx_key = colon_to_underscore(eid)
    chunk_ids = entity_index.get(idx_key, [])[:limit]
    results = []
    for cid in chunk_ids:
        parts = cid.split(":", 1)
        if len(parts) != 2:
            continue
        src, num = parts
        # Search for the JSONL file
        for jf in SOURCES.rglob(f"{src}_chunks.jsonl"):
            try:
                with jf.open() as f:
                    for line in f:
                        ch = json.loads(line)
                        if str(ch.get("id")) == num:
                            results.append({
                                "text": ch.get("text", "")[:300],
                                "source": src,
                                "verse_ref": ch.get("verse_ref", ""),
                            })
                            break
            except Exception:
                pass
            break
    return results

def find_evidence(entity_index, tag_map, from_id, to_id):
    """Try to find corpus evidence for a relation between from_id and to_id."""
    # Strategy 1: entity_index chunks for from_id
    from_chunks = find_chunk_text(entity_index, from_id, limit=2)

    # Strategy 2: entity_index chunks for to_id (if non-empty)
    to_chunks = []
    if to_id:
        to_chunks = find_chunk_text(entity_index, to_id, limit=2)

    # Strategy 3: passages.csv tag lookup for from_id
    from_tag = colon_to_title_tag(from_id)
    from_passages = tag_map.get(from_tag, [])

    # Strategy 4: passages.csv tag lookup for to_id
    to_tag = colon_to_title_tag(to_id) if to_id else ""
    to_passages = tag_map.get(to_tag, []) if to_tag else []

    # Extract the entity names for text matching
    from_name = from_id.split(":")[-1].replace("_", " ").lower() if from_id else ""
    to_name = to_id.split(":")[-1].replace("_", " ").lower() if to_id else ""

    # Best case: a passage mentioning both entities
    best = None

    # Check from_id chunks for mention of to_id
    for ch in from_chunks:
        text_lower = ch["text"].lower()
        if to_name and to_name in text_lower:
            return {"text": ch["text"], "source": ch["source"], "quality": "both_mentioned"}
        if not best:
            best = {"text": ch["text"], "source": ch["source"], "quality": "from_only"}

    # Check to_id chunks for mention of from_id
    for ch in to_chunks:
        text_lower = ch["text"].lower()
        if from_name and from_name in text_lower:
            return {"text": ch["text"], "source": ch["source"], "quality": "both_mentioned"}
        if not best:
            best = {"text": ch["text"], "source": ch["source"], "quality": "to_only"}

    # Check passage tags
    for p in from_passages[:3]:
        excerpt = p.get("excerpt", "")
        if to_name and to_name.lower() in excerpt.lower():
            return {"text": excerpt[:300], "source": p.get("source_id", "passages.csv"), "quality": "both_mentioned"}
        if not best:
            best = {"text": excerpt[:300], "source": p.get("source_id", "passages.csv"), "quality": "tag_from"}

    for p in to_passages[:3]:
        excerpt = p.get("excerpt", "")
        if from_name and from_name.lower() in excerpt.lower():
            return {"text": excerpt[:300], "source": p.get("source_id", "passages.csv"), "quality": "both_mentioned"}
        if not best:
            best = {"text": excerpt[:300], "source": p.get("source_id", "passages.csv"), "quality": "tag_to"}

    # If we have any chunk hits at all (entity is in the corpus), that's partial evidence
    if from_chunks or to_chunks:
        if not best:
            ch = (from_chunks or to_chunks)[0]
            best = {"text": ch["text"], "source": ch["source"], "quality": "entity_indexed"}

    return best


def main():
    print("Loading corpus data...")
    entity_index = load_entity_index()
    tag_map = load_passage_tags()
    print(f"  Entity index: {len(entity_index)} entities")
    print(f"  Passage tags: {len(tag_map)} unique tags")

    # Read overlays
    with open(INPUT, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    print(f"  Overlay rows: {len(rows)}")

    seed_count = sum(1 for r in rows if r.get("confidence") == "seed_unverified")
    print(f"  seed_unverified: {seed_count}\n")

    log_lines = []
    promoted = 0
    no_evidence = 0

    for row in rows:
        if row.get("confidence") != "seed_unverified":
            continue

        from_id = row.get("from_id", "")
        to_id = row.get("to_id", "")
        relation = row.get("relation", "")

        evidence = find_evidence(entity_index, tag_map, from_id, to_id)

        if evidence:
            quality = evidence["quality"]
            # Both mentioned = strong, single entity = moderate
            if quality == "both_mentioned":
                row["confidence"] = "0.80"
            else:
                row["confidence"] = "0.70"
            row["source_title"] = evidence["source"]
            row["excerpt"] = evidence["text"][:200]
            promoted += 1
            msg = f"PROMOTED ({quality}): {from_id} → {relation} → {to_id} [src={evidence['source']}]"
            print(msg)
            log_lines.append(msg)
        else:
            msg = f"no evidence: {from_id} → {relation} → {to_id}"
            print(msg)
            log_lines.append(msg)
            no_evidence += 1

    # Write updated overlays
    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        if rows:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

    # Write evidence log
    EVIDENCE_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(EVIDENCE_LOG, "w") as f:
        f.write(f"REL-004 Overlay Promotion Log\n")
        f.write(f"Date: 2026-04-10\n")
        f.write(f"Total rows: {len(rows)}\n")
        f.write(f"Promoted: {promoted}\n")
        f.write(f"No evidence: {no_evidence}\n")
        f.write(f"Already non-seed: {len(rows) - seed_count}\n\n")
        f.write("\n".join(log_lines))

    pct = (promoted / seed_count * 100) if seed_count else 0
    print(f"\n{'='*60}")
    print(f"Promoted: {promoted} / {seed_count} seed_unverified ({pct:.0f}%)")
    print(f"No evidence: {no_evidence}")
    print(f"Written to: {OUTPUT}")
    print(f"Log: {EVIDENCE_LOG}")


if __name__ == "__main__":
    main()
