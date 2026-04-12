#!/usr/bin/env python3
"""
chunk_bg.py — Extract Bhagavad Gita from Mahabharata (Ganguli translation)
and produce bg_chunks.jsonl matching gaudiya corpus schema.

Source: datasets/sources/epics/mahabharata_en.txt (public domain, Ganguli/Hare)
The BG is embedded in the Bhishma Parva, marked with "(Bhagavad Gita Chapter X)" headers.
"""

import json
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAHABHARATA = os.path.join(BASE, "datasets", "sources", "epics", "mahabharata_en.txt")
OUTPUT = os.path.join(BASE, "datasets", "sources", "gaudiya", "bg_chunks.jsonl")

CHAPTER_RE = re.compile(r"^\(Bhagavad Gita[,]?\s+Chapter\s+([IVXLC]+)\)$", re.IGNORECASE)
SECTION_RE = re.compile(r"^Section\s+\d+", re.IGNORECASE)
FOOTNOTE_RE = re.compile(r"^Footnotes?\s*$", re.IGNORECASE)
LESSON_END_RE = re.compile(r"^\[Here ends the .* lesson")

ROMAN = {
    "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7,
    "VIII": 8, "IX": 9, "X": 10, "XI": 11, "XII": 12, "XIII": 13,
    "XIV": 14, "XV": 15, "XVI": 16, "XVII": 17, "XVIII": 18,
}


def extract_bg_chapters(path: str) -> dict[int, str]:
    """Extract BG text from Mahabharata, split by chapter."""
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    chapters = {}
    current_chapter = None
    current_lines = []
    in_footnotes = False
    bg_started = False

    for line in lines:
        stripped = line.strip()

        # Check for chapter header
        m = CHAPTER_RE.match(stripped)
        if m:
            # Save previous chapter (only if we have unsaved lines)
            if current_chapter is not None and current_lines:
                chapters[current_chapter] = "\n".join(current_lines).strip()
            roman = m.group(1).upper()
            current_chapter = ROMAN.get(roman)
            current_lines = []
            in_footnotes = False
            bg_started = True
            continue

        if not bg_started:
            continue

        # Section markers appear BEFORE chapter headers in this text.
        # When we're in a chapter collecting text, a Section marker means
        # we've hit the inter-chapter zone (footnotes etc.) — stop collecting
        # until the next chapter header resets us.
        if SECTION_RE.match(stripped):
            if current_chapter is not None and current_lines:
                chapters[current_chapter] = "\n".join(current_lines).strip()
                current_lines = []
            in_footnotes = True
            continue

        if in_footnotes:
            continue

        # Skip editorial notes at very start
        if stripped.startswith("(This where is"):
            continue
        if stripped.startswith("headings to aid"):
            continue
        if stripped.startswith("the original Ganguli"):
            continue

        # Skip footnote sections within a chapter
        if FOOTNOTE_RE.match(stripped):
            in_footnotes = True
            continue

        # Skip lesson-end markers
        if LESSON_END_RE.match(stripped):
            continue

        if current_chapter is not None:
            current_lines.append(line.rstrip())

    # Save last chapter
    if current_chapter is not None and current_lines:
        chapters[current_chapter] = "\n".join(current_lines).strip()

    return chapters


def split_long_paragraph(text: str, max_chars: int = 600) -> list[str]:
    """Split a long paragraph into sentence-level sub-chunks."""
    if len(text) <= max_chars:
        return [text]

    # Split on sentence boundaries: period/question/exclamation followed by space+capital
    # or on speaker changes ("X said,")
    sentences = re.split(r'(?<=[.?!])\s+(?=[A-Z"\'])', text)

    sub_chunks = []
    current = ""
    for sent in sentences:
        if current and len(current) + len(sent) + 1 > max_chars:
            sub_chunks.append(current.strip())
            current = sent
        else:
            current = (current + " " + sent).strip() if current else sent

    if current.strip():
        sub_chunks.append(current.strip())

    return [s for s in sub_chunks if len(s) >= 20]


def chunk_chapter(chapter_num: int, text: str) -> list[dict]:
    """Split chapter text into verse-sized chunks by paragraph breaks,
    then sub-split large paragraphs on sentence boundaries."""
    # Split on double newlines (paragraph boundaries)
    raw_paragraphs = re.split(r"\n\s*\n", text)

    chunks = []
    verse_num = 0

    for para in raw_paragraphs:
        para = para.strip()
        if len(para) < 10:
            continue

        # Merge consecutive short lines (line-wrap artifacts)
        para = re.sub(r"\n(?!\n)", " ", para)
        para = re.sub(r"\s+", " ", para).strip()

        if len(para) < 10:
            continue

        # Sub-split large paragraphs
        sub_chunks = split_long_paragraph(para)
        for sub in sub_chunks:
            verse_num += 1
            chunks.append({
                "chapter": chapter_num,
                "verse": verse_num,
                "text": sub,
            })

    return chunks


def build_entity_refs(text: str) -> list[str]:
    """Extract basic entity references from chunk text."""
    refs = set()
    text_lower = text.lower()

    # Key figures
    if "krishna" in text_lower or "vasudeva" in text_lower or "hrishikesha" in text_lower:
        refs.add("deity:krishna")
    if "arjuna" in text_lower or "dhananjaya" in text_lower or "partha" in text_lower:
        refs.add("deity:arjuna")
    if "brahm" in text_lower:
        refs.add("deity:brahma")
    if "vishnu" in text_lower or "narayana" in text_lower:
        refs.add("deity:vishnu")
    if "shiva" in text_lower or "siva" in text_lower or "mahadeva" in text_lower:
        refs.add("deity:shiva")
    if "indra" in text_lower:
        refs.add("deity:indra")

    # Grahas
    if re.search(r"\bsun\b|\bsurya\b|\baditya\b", text_lower):
        refs.add("graha:surya")
    if re.search(r"\bmoon\b|\bchandra\b|\bsoma\b", text_lower):
        refs.add("graha:chandra")

    # Gunas
    if "sattwa" in text_lower or "sattva" in text_lower or "goodness" in text_lower:
        refs.add("guna:sattva")
    if "rajas" in text_lower or "passion" in text_lower:
        refs.add("guna:rajas")
    if "tamas" in text_lower or "darkness" in text_lower or "ignorance" in text_lower:
        refs.add("guna:tamas")

    return sorted(refs)


def main():
    print(f"Reading Mahabharata from {MAHABHARATA}")
    chapters = extract_bg_chapters(MAHABHARATA)
    print(f"Extracted {len(chapters)} chapters: {sorted(chapters.keys())}")

    all_chunks = []
    char_offset = 0

    for ch_num in sorted(chapters.keys()):
        ch_text = chapters[ch_num]
        ch_chunks = chunk_chapter(ch_num, ch_text)
        print(f"  Chapter {ch_num:2d}: {len(ch_chunks)} chunks, {len(ch_text)} chars")

        for chunk in ch_chunks:
            chunk_id = f"bg_{ch_num:02d}_{chunk['verse']:02d}"
            text = chunk["text"]
            entity_refs = build_entity_refs(text)

            record = {
                "id": len(all_chunks),
                "chunk_id": chunk_id,
                "char_start": char_offset,
                "char_end": char_offset + len(text),
                "verse_ref": f"BG {ch_num}.{chunk['verse']}",
                "text": text,
                "source": "Bhagavad Gita (Ganguli translation)",
                "domain": "gaudiya",
                "tradition": "gaudiya_vaishnava",
                "language": "en",
                "chapter": ch_num,
                "verse": chunk["verse"],
                "authority": "shastra",
                "entity_refs": entity_refs,
            }
            all_chunks.append(record)
            char_offset += len(text)

    # Write output
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        for record in all_chunks:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"\nWrote {len(all_chunks)} chunks to {OUTPUT}")
    print(f"Chapters covered: {sorted(chapters.keys())}")

    # Verify
    missing = [ch for ch in range(1, 19) if ch not in chapters]
    if missing:
        print(f"WARNING: Missing chapters: {missing}")


if __name__ == "__main__":
    main()
