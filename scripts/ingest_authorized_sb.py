#!/usr/bin/env python3
"""
ingest_authorized_sb.py — Parse authorized Srimad Bhagavatam RTF/DOC files
into verse-level JSONL chunks for the Atlas text pipeline.

Source files: datasets/sources/gaudiya/sb*.rtf, sb*.RTF, sb*.doc, SB*.doc
Output: datasets/sources/gaudiya/bhagavatam_chunks.jsonl

Usage:
  python3 scripts/ingest_authorized_sb.py              # all cantos
  python3 scripts/ingest_authorized_sb.py --canto 1    # single canto
  python3 scripts/ingest_authorized_sb.py --dry-run    # parse + stats only
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAUDIYA = ROOT / "datasets" / "sources" / "gaudiya"

# Map canto number → filename
CANTO_FILES = {
    1: "sb1b.rtf",
    2: "sb_2_1972.rtf",
    3: "sb_3.doc",
    4: "sb4.rtf",
    5: "sb5.RTF",
    6: "sb6.RTF",
    7: "sb7.RTF",
    8: "sb8.RTF",
    9: "SB.Ninth Canto.doc",
}


def extract_text(filepath: Path) -> str:
    """Extract plain text from RTF or DOC using catdoc."""
    result = subprocess.run(
        ["catdoc", str(filepath)],
        capture_output=True, timeout=60,
    )
    if result.returncode != 0:
        print(f"  catdoc error on {filepath.name}: {result.stderr[:200]}")
        return ""
    # Decode with fallback for non-UTF8 chars
    return result.stdout.decode("utf-8", errors="replace")


# Regex for "SB X.Y.Z" refs (standalone or with inline translation)
_SB_REF = re.compile(
    r'^SB\s+(\d+)\.(\d+)\.(\d+(?:\s*[-–]\s*\d+)?)'
    r'(?:\s*,\s*SB\s+\d+\.\d+\.\d+(?:\s*[-–]\s*\d+)?)*'  # skip combined dupes
    r'(?:\s*[-–—]\s*(.+))?$'  # optional inline translation after dash
)


def parse_canto(text: str, canto: int) -> list:
    """Parse extracted text into verse dicts.

    Handles three formats found across cantos:
      A) CHAPTER X + TEXT N (cantos 1-3)
      B) SB X.Y.Z on its own line + TEXT below (cantos 4,5,7)
      C) SB X.Y.Z - translation inline (cantos 6,8)
    """
    verses = []
    lines = text.split('\n')
    chapter = 0
    i = 0

    def _is_verse_boundary(ln):
        """True if line starts a new verse or chapter."""
        s = ln.strip()
        if re.match(r'^TEXT\s+\d+', s):
            return True
        if re.match(r'^CHAPTER\s+', s, re.IGNORECASE):
            return True
        if _SB_REF.match(s):
            return True
        return False

    def _collect_body(start_i):
        """Collect sanskrit/synonyms/translation/purport from start_i onward."""
        sanskrit, synonyms, translation, purport = [], [], [], []
        section = "sanskrit"
        j = start_i
        while j < len(lines):
            sline = lines[j].strip()
            if _is_verse_boundary(sline):
                break
            sup = sline.upper()
            if sup in ("SYNONYMS", "SYNONYM"):
                section = "synonyms"
                j += 1; continue
            elif sup in ("TRANSLATION", "TRANSLATIONS"):
                section = "translation"
                j += 1; continue
            elif sup in ("PURPORT", "PURPORTS"):
                section = "purport"
                j += 1; continue
            if sline:
                if section == "sanskrit":
                    sanskrit.append(sline)
                elif section == "synonyms":
                    synonyms.append(sline)
                elif section == "translation":
                    translation.append(sline)
                elif section == "purport":
                    purport.append(sline)
            j += 1
        return j, sanskrit, synonyms, translation, purport

    while i < len(lines):
        line = lines[i].strip()

        # --- Format A: CHAPTER header ---
        ch_match = re.match(r'^CHAPTER\s+(\w+[-]?\w*)', line, re.IGNORECASE)
        if ch_match:
            n = _word_to_num(ch_match.group(1))
            if n > 0:
                chapter = n
            i += 1
            continue

        # --- Format A: TEXT N (needs chapter context) ---
        text_match = re.match(r'^TEXT\s+(\d+(?:\s*[-–]\s*\d+)?)\s*$', line)
        if text_match and chapter > 0:
            verse_num = text_match.group(1).replace('–', '-').replace(' ', '')
            ref = f"SB {canto}.{chapter}.{verse_num}"
            i += 1
            i, sanskrit, synonyms, translation, purport = _collect_body(i)
            trans_text = ' '.join(translation).strip()
            purport_text = ' '.join(purport).strip()
            if trans_text or purport_text:
                verses.append({
                    "verse_ref": ref,
                    "sanskrit": '\n'.join(sanskrit).strip()[:1000],
                    "synonyms": ' '.join(synonyms).strip()[:2000],
                    "translation": trans_text[:3000],
                    "purport": purport_text[:8000],
                })
            continue

        # --- Formats B & C: SB X.Y.Z line ---
        sb_match = _SB_REF.match(line)
        if sb_match:
            c, ch, v_raw, inline_trans = sb_match.groups()
            chapter = int(ch)
            verse_num = v_raw.replace('–', '-').replace(' ', '')
            ref = f"SB {c}.{ch}.{verse_num}"

            i += 1
            # Skip duplicate "TEXT N" line if present right after
            if i < len(lines) and re.match(r'^TEXT\s*$', lines[i].strip()):
                i += 1
            elif i < len(lines) and re.match(r'^TEXT\s+\d+', lines[i].strip()):
                i += 1

            i, sanskrit, synonyms, translation, purport = _collect_body(i)

            # Format C: inline translation
            if inline_trans and not translation:
                translation = [inline_trans.strip()]

            trans_text = ' '.join(translation).strip()
            purport_text = ' '.join(purport).strip()
            if trans_text or purport_text:
                verses.append({
                    "verse_ref": ref,
                    "sanskrit": '\n'.join(sanskrit).strip()[:1000],
                    "synonyms": ' '.join(synonyms).strip()[:2000],
                    "translation": trans_text[:3000],
                    "purport": purport_text[:8000],
                })
            continue

        i += 1

    return verses


def _word_to_num(word: str) -> int:
    """Convert chapter word (ONE, TWO, ..., or digit) to int."""
    word = word.upper().strip()
    if word.isdigit():
        return int(word)
    words = {
        "ONE": 1, "TWO": 2, "THREE": 3, "FOUR": 4, "FIVE": 5,
        "SIX": 6, "SEVEN": 7, "EIGHT": 8, "NINE": 9, "TEN": 10,
        "ELEVEN": 11, "TWELVE": 12, "THIRTEEN": 13, "FOURTEEN": 14,
        "FIFTEEN": 15, "SIXTEEN": 16, "SEVENTEEN": 17, "EIGHTEEN": 18,
        "NINETEEN": 19, "TWENTY": 20, "TWENTY-ONE": 21, "TWENTY-TWO": 22,
        "TWENTY-THREE": 23, "TWENTY-FOUR": 24, "TWENTY-FIVE": 25,
        "TWENTY-SIX": 26, "TWENTY-SEVEN": 27, "TWENTY-EIGHT": 28,
        "TWENTY-NINE": 29, "THIRTY": 30, "THIRTY-ONE": 31,
        "THIRTY-TWO": 32, "THIRTY-THREE": 33,
    }
    return words.get(word, 0)


def main():
    parser = argparse.ArgumentParser(description="Ingest authorized SB into JSONL")
    parser.add_argument("--canto", type=int, help="Process only this canto")
    parser.add_argument("--dry-run", action="store_true", help="Parse and show stats only")
    args = parser.parse_args()

    cantos = sorted(CANTO_FILES.keys())
    if args.canto:
        if args.canto not in CANTO_FILES:
            print(f"No file for canto {args.canto}. Available: {cantos}")
            sys.exit(1)
        cantos = [args.canto]

    out_path = GAUDIYA / "bhagavatam_chunks.jsonl"
    all_verses = []
    total_stats = {}

    for canto in cantos:
        fname = CANTO_FILES[canto]
        fpath = GAUDIYA / fname
        if not fpath.exists():
            print(f"  SKIP canto {canto}: {fname} not found")
            continue

        print(f"  Canto {canto}: extracting {fname}...")
        text = extract_text(fpath)
        if not text:
            continue

        verses = parse_canto(text, canto)
        all_verses.extend(verses)

        # Stats
        chapters = set()
        for v in verses:
            m = re.match(r'SB \d+\.(\d+)', v["verse_ref"])
            if m:
                chapters.add(int(m.group(1)))
        total_stats[canto] = {
            "chapters": len(chapters),
            "verses": len(verses),
            "with_purport": sum(1 for v in verses if v["purport"]),
        }
        print(f"    → {len(verses)} verses across {len(chapters)} chapters")

    if args.dry_run:
        print(f"\n✦ Dry run: {len(all_verses)} total verses parsed")
        for c, s in sorted(total_stats.items()):
            print(f"  Canto {c}: {s['chapters']} ch, {s['verses']} verses, "
                  f"{s['with_purport']} with purport")
        return

    # Write JSONL
    print(f"\n  Writing {out_path.name}...")
    with open(out_path, "w", encoding="utf-8") as f:
        for idx, v in enumerate(all_verses):
            text = v["translation"]
            if v["purport"]:
                text += "\n\n" + v["purport"]
            chunk = {
                "id": idx,
                "verse_ref": v["verse_ref"],
                "domain": "gaudiya",
                "authority": "shastra",
                "translator": "AC Bhaktivedanta Swami Prabhupada",
                "source": "authorized_sb",
                "text": text,
                "sanskrit": v["sanskrit"],
                "synonyms": v["synonyms"],
            }
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    print(f"\n✦ Done: {len(all_verses)} verses → {out_path.name}")
    for c, s in sorted(total_stats.items()):
        print(f"  Canto {c}: {s['chapters']} ch, {s['verses']} verses")


if __name__ == "__main__":
    main()
