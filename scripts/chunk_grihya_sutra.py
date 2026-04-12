#!/usr/bin/env python3
"""
chunk_grihya_sutra.py — Parse and chunk the Grihya Sutras from SBE vol. 29
(Oldenberg & Max Müller translation, public domain).

Source: datasets/sources/dharma/grihya_sutra_raw.txt
        (djvu OCR text from archive.org/details/grihyasutras0000unse)

Contains four texts:
  1. Sankhayana Grihya Sutra   (~lines 874–8209)
  2. Asvalayana Grihya Sutra   (~lines 8506–13749)
  3. Paraskara Grihya Sutra    (~lines 13769–19315)
  4. Khadira Grihya Sutra      (~lines 19316–end)

Chunks by sutra number. Each numbered sutra = one chunk.
Commentary paragraphs (footnotes in original) are attached to the
preceding sutra as a 'commentary' field.
"""

import json
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "datasets", "sources", "dharma", "grihya_sutra_raw.txt")
OUTPUT = os.path.join(BASE, "datasets", "sources", "dharma", "grihya_sutra_en_chunks.jsonl")

# --- Text boundaries (approximate line numbers) ---
TEXTS = [
    {"name": "Sankhayana Grihya Sutra", "slug": "sankhayana",
     "start_marker": "SANKHAYANA-GR", "end_marker": "End of the Sankh",
     "start_line": 874, "end_line": 8209},
    {"name": "Asvalayana Grihya Sutra", "slug": "asvalayana",
     "start_marker": "ASVALAYANA-GR", "end_marker": "PARASKARA-GR",
     "start_line": 8506, "end_line": 13749},
    {"name": "Paraskara Grihya Sutra", "slug": "paraskara",
     "start_marker": "PARASKARA-GR", "end_marker": "KHADIRA-GR",
     "start_line": 13850, "end_line": 19315},
    {"name": "Khadira Grihya Sutra", "slug": "khadira",
     "start_marker": "KHADIRA-GR", "end_marker": None,
     "start_line": 19340, "end_line": 23000},
]

# Patterns
ADHYAYA_RE = re.compile(
    r'(?:ADHYAYA|Adhy[aā]ya|ApunyAya)\s+([IVXLC]+)',
    re.IGNORECASE
)
KHANDA_RE = re.compile(
    r'(?:KH[AÂ]NDA|KANDIKA|KawoixA|Kawnp[aA]|Ka[nw][dp]ik[aA]|PATALA)\s+(\d+)',
    re.IGNORECASE
)
# Match numbered sutras at line start: "1. ...", "2. ...", etc.
SUTRA_NUM_RE = re.compile(r'^(\d{1,3})\.\s+(.+)')
# OCR page headers (page numbers + title remnants)
PAGE_HEADER_RE = re.compile(
    r'^\d+\s+[A-Z]*[sS][AaĀ][NnṆ]KH[AaĀ]YANA|'
    r'^\d+\s+A[Ss]V[AaĀ]L[AaĀ]YANA|'
    r'^\d+\s+P[AaĀ]R[AaĀ]SKARA|'
    r'^\d+\s+KH[AaĀ]DIRA|'
    r'^[IVXLC]+\s+ADHYAYA|'
    r'^\d+\s+[A-Z]+-GR',
    re.IGNORECASE
)
# Lines that are just OCR noise (very short, gibberish)
NOISE_RE = re.compile(r'^[^a-zA-Z]*$|^.{0,3}$|^[~#@\*\+\=\{\}]+')
# Commentary marker: lines starting with reference like "1, 1."  or "2."
# that are footnote-style commentary
COMMENTARY_REF_RE = re.compile(r'^(\d+)[,.]?\s')


def load_lines():
    with open(RAW, "r", encoding="utf-8", errors="replace") as f:
        return f.readlines()


def extract_text_section(lines, start_line, end_line):
    """Extract lines for a specific text section."""
    return lines[start_line:end_line]


def find_actual_start(lines, text_info):
    """Find where the actual sutra text begins (after introduction)."""
    slug_upper = text_info["slug"].upper()
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Look for first ADHYAYA marker
        if ADHYAYA_RE.search(stripped) and KHANDA_RE.search(stripped):
            return i
        # Or look for "ADHYAYA I, KANDIKA 1" style
        if re.search(r'ADHYAYA\s+I\b|Adhy[aā]ya\s+I\b|ApunyAya\s+I\b', stripped, re.IGNORECASE):
            return i
    return 0


def is_page_header(line):
    """Check if a line is an OCR page header (running header at top of page)."""
    stripped = line.strip()
    if PAGE_HEADER_RE.match(stripped):
        return True
    # Lines like "160 AsVALAYANA-GRIHYA-SUTRA." or "SANKHAYANA-GR/JHYA-SUTRA."
    if re.match(r'^\d*\s*[A-Za-z]*-GR[/I]', stripped):
        return True
    if re.match(r'^\d+\s+[A-Za-z]*GRIHYA', stripped, re.IGNORECASE):
        return True
    # Running headers: "I ADHYAYA, 2 KANDIKA, 6. 161" or "II ADHYAYA, 8 KAwpIKA, 16, 213"
    if re.match(r'^[IVXLC]+\s+ADHYAYA,\s+\d+\s+K[AaĀ]', stripped, re.IGNORECASE):
        return True
    if re.match(r'^[IVXLC]+\s+ADHYAyA,\s+\d+\s+K', stripped, re.IGNORECASE):
        return True
    if re.match(r'^\d+\s+ADHYAYA,', stripped, re.IGNORECASE):
        return True
    return False


def is_noise(line):
    """Check if line is OCR noise."""
    stripped = line.strip()
    if not stripped:
        return True
    if NOISE_RE.match(stripped):
        return True
    # Very short lines that are just artifacts
    if len(stripped) < 4 and not stripped[0].isdigit():
        return True
    return False


def is_section_header(line):
    """Check if line is an ADHYAYA/KHANDA header."""
    stripped = line.strip()
    if ADHYAYA_RE.search(stripped):
        return True
    # Standalone KHANDA headers
    if re.match(r'^K[Hh][AaĀ][Nn][Dd][AaĀ]\s+\d+', stripped):
        return True
    return False


def parse_sutra_text(section_lines, text_info):
    """Parse sutra text into numbered chunks."""
    chunks = []
    current_adhyaya = 0
    current_khanda = 0
    current_sutra_num = 0
    current_sutra_text = []
    current_commentary = []
    in_commentary = False
    in_introduction = True

    # Find where actual sutras start
    start_idx = find_actual_start(section_lines, text_info)
    working_lines = section_lines[start_idx:]

    for line in working_lines:
        stripped = line.strip()

        # Skip noise and page headers
        if is_noise(stripped):
            if current_sutra_text and not in_commentary:
                # Blank line might separate sutra from commentary
                pass
            continue

        if is_page_header(stripped):
            continue

        # Check for "End of" markers
        if re.match(r'^End of', stripped, re.IGNORECASE):
            in_introduction = False
            continue

        # Track ADHYAYA
        adhyaya_match = ADHYAYA_RE.search(stripped)
        if adhyaya_match:
            roman = adhyaya_match.group(1).upper()
            roman_map = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5,
                         "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10}
            current_adhyaya = roman_map.get(roman, current_adhyaya)
            in_introduction = False

            # Also check for KHANDA in same line
            khanda_match = KHANDA_RE.search(stripped)
            if khanda_match:
                current_khanda = int(khanda_match.group(1))
            continue

        # Track KHANDA
        khanda_match = re.match(
            r'K[Hh][AaĀ][Nn][Dd][AaĀ]\s+(\d+)',
            stripped, re.IGNORECASE
        )
        if khanda_match:
            current_khanda = int(khanda_match.group(1))
            continue

        if in_introduction:
            continue

        # Check for numbered sutra
        sutra_match = SUTRA_NUM_RE.match(stripped)
        if sutra_match:
            new_num = int(sutra_match.group(1))
            sutra_body = sutra_match.group(2).strip()

            # Heuristic: if number is sequential (or 1 for new section),
            # treat as a new sutra. If it's a commentary reference
            # (e.g., "1, 1. The ceremonies..."), check context.
            is_new_sutra = False
            if new_num == current_sutra_num + 1:
                is_new_sutra = True
            elif new_num == 1 and current_sutra_num > 0:
                is_new_sutra = True
            elif new_num == 1 and current_sutra_num == 0:
                is_new_sutra = True
            elif current_sutra_num == 0 and new_num <= 3:
                is_new_sutra = True

            # Commentary lines often start with references like
            # "1, 1. The ceremonies..." or have very long text
            if re.match(r'\d+,\s*\d+\.', stripped):
                # This is likely a commentary reference
                in_commentary = True
                current_commentary.append(stripped)
                continue

            if is_new_sutra:
                # Save previous sutra
                if current_sutra_text and current_sutra_num > 0:
                    text = clean_text(" ".join(current_sutra_text))
                    if len(text) >= 10:
                        commentary = clean_text(" ".join(current_commentary)) if current_commentary else ""
                        chunks.append({
                            "adhyaya": current_adhyaya,
                            "khanda": current_khanda,
                            "sutra": current_sutra_num,
                            "text": text,
                            "commentary": commentary,
                        })

                current_sutra_num = new_num
                current_sutra_text = [sutra_body]
                current_commentary = []
                in_commentary = False
                continue
            else:
                # Probably commentary or non-sequential — treat as commentary
                in_commentary = True
                current_commentary.append(stripped)
                continue

        # Continuation lines
        if in_commentary:
            current_commentary.append(stripped)
        elif current_sutra_num > 0:
            # Check if this looks like commentary (starts with a reference)
            if re.match(r'\d+\.\s+[A-Z]', stripped) and len(stripped) > 80:
                in_commentary = True
                current_commentary.append(stripped)
            else:
                current_sutra_text.append(stripped)

    # Save last sutra
    if current_sutra_text and current_sutra_num > 0:
        text = clean_text(" ".join(current_sutra_text))
        if len(text) >= 10:
            commentary = clean_text(" ".join(current_commentary)) if current_commentary else ""
            chunks.append({
                "adhyaya": current_adhyaya,
                "khanda": current_khanda,
                "sutra": current_sutra_num,
                "text": text,
                "commentary": commentary,
            })

    return chunks


def clean_text(text):
    """Clean OCR artifacts from text."""
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Fix common OCR issues
    text = text.replace('Grzhya', 'Grihya')
    text = text.replace('Grrhya', 'Grihya')
    text = text.replace('GR/HYA', 'GRIHYA')
    text = text.replace('GR/JHYA', 'GRIHYA')
    text = text.replace('/i', 'ri')
    text = text.replace('sitra', 'sutra')
    text = text.replace('Sfitra', 'Sutra')
    text = text.replace('Sitra', 'Sutra')
    text = text.replace('siitra', 'sutra')
    text = text.replace('Azshi', 'Rishi')
    text = text.replace('Azveda', 'Rigveda')
    text = text.replace('PAakayag#as', 'Pakayajnas')
    text = text.replace('Brahmava', 'Brahmana')
    text = text.replace('Aravyaka', 'Aranyaka')
    text = text.replace('Arazyaka', 'Aranyaka')
    text = text.replace('Araxyaka', 'Aranyaka')
    # Remove trailing page numbers
    text = re.sub(r'\s+\d+\s*$', '', text)
    return text


def build_entity_refs(text):
    """Extract entity references from chunk text."""
    refs = set()
    t = text.lower()

    # Deities
    if "agni" in t:
        refs.add("deity:agni")
    if "indra" in t:
        refs.add("deity:indra")
    if "brahm" in t:
        refs.add("deity:brahma")
    if "vishnu" in t or "narayana" in t:
        refs.add("deity:vishnu")
    if "rudra" in t or "shiva" in t:
        refs.add("deity:rudra")
    if "prajapati" in t:
        refs.add("deity:prajapati")
    if "soma" in t:
        refs.add("deity:soma")
    if "vayu" in t:
        refs.add("deity:vayu")
    if "varuna" in t:
        refs.add("deity:varuna")
    if "savitri" in t or "savitr" in t:
        refs.add("deity:savitri")
    if "gayatri" in t:
        refs.add("deity:savitri")
    if "lakshmi" in t or "sri " in t:
        refs.add("deity:lakshmi")
    if "ganesh" in t or "ganapati" in t:
        refs.add("deity:ganesha")

    # Grahas
    if re.search(r'\bsun\b|\bsurya\b|\baditya\b', t):
        refs.add("graha:surya")
    if re.search(r'\bmoon\b|\bchandra\b|\bsoma\b', t):
        refs.add("graha:chandra")

    # Ritual concepts
    if "samskara" in t or "sacrament" in t:
        refs.add("concept:samskara")
    if "vivaha" in t or "marriage" in t or "nuptial" in t or "wedding" in t:
        refs.add("samskara:vivaha")
    if "upanayana" in t or "initiation" in t:
        refs.add("samskara:upanayana")
    if "antyeshti" in t or "funeral" in t or "cremation" in t:
        refs.add("samskara:antyeshti")
    if "namakarana" in t or "naming" in t:
        refs.add("samskara:namakarana")
    if "sraddha" in t or "shr[aā]ddha" in t:
        refs.add("ritual:shraddha")
    if "homa" in t or "oblation" in t:
        refs.add("ritual:homa")
    if "puja" in t or "worship" in t:
        refs.add("ritual:puja")

    # Nakshatras
    if "rohini" in t:
        refs.add("nakshatra:rohini")
    if "pushya" in t:
        refs.add("nakshatra:pushya")
    if "uttara phalguni" in t:
        refs.add("nakshatra:uttara_phalguni")

    # Calendar
    if "new moon" in t or "amavasya" in t:
        refs.add("tithi:amavasya")
    if "full moon" in t or "purnima" in t:
        refs.add("tithi:purnima")

    return sorted(refs)


def main():
    print(f"Reading raw text from {RAW}")
    lines = load_lines()
    print(f"Total lines: {len(lines)}")

    all_chunks = []

    for text_info in TEXTS:
        print(f"\nProcessing {text_info['name']}...")
        section = extract_text_section(
            lines, text_info["start_line"], text_info["end_line"]
        )
        raw_chunks = parse_sutra_text(section, text_info)
        print(f"  Raw chunks extracted: {len(raw_chunks)}")

        for chunk in raw_chunks:
            chunk_id = (
                f"grihya_{text_info['slug']}"
                f"_{chunk['adhyaya']}_{chunk['khanda']}_{chunk['sutra']}"
            )
            text = chunk["text"]
            entity_refs = build_entity_refs(text)

            record = {
                "id": len(all_chunks),
                "chunk_id": chunk_id,
                "text": text,
                "source": text_info["name"],
                "tradition": "vedic_ritual",
                "language": "en",
                "domain": "dharma",
                "book": chunk["adhyaya"],
                "khanda": chunk["khanda"],
                "sutra": chunk["sutra"],
                "authority": "shastra",
                "entity_refs": entity_refs,
            }
            if chunk.get("commentary"):
                record["commentary"] = chunk["commentary"]

            all_chunks.append(record)

    # Write output
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        for record in all_chunks:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"\nWrote {len(all_chunks)} chunks to {OUTPUT}")

    # Summary by text
    from collections import Counter
    by_source = Counter(c["source"] for c in all_chunks)
    for src, count in by_source.most_common():
        print(f"  {src}: {count} chunks")

    # Sample
    if all_chunks:
        print(f"\nSample chunk:")
        print(json.dumps(all_chunks[0], indent=2, ensure_ascii=False)[:500])


if __name__ == "__main__":
    main()
