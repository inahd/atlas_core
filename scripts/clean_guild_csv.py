"""
clean_guild_csv.py — Clean URL noise from guild relations CSV.

Reads:  datasets/plants/guild_relations.csv (or guild_matrix_raw.csv if present)
Writes: cleaned version back to same file (guild_relations.csv)
        or to guild_matrix.csv if processing guild_matrix_raw.csv

The source, notes, and other fields in guild_relations.csv contain
embedded URLs, footnote markers [1-4], and percentage-encoded text
from web scraping. This script strips all that.

Attestation unchanged — preserves original attestation field.
"""
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "datasets" / "plants"
GUILD_REL = ROOT / "guild_relations.csv"
GUILD_RAW = ROOT / "guild_matrix_raw.csv"
GUILD_CLEAN = ROOT / "guild_matrix.csv"


def clean_field(value):
    if not value:
        return ""
    if not isinstance(value, str):
        value = str(value)
    # Strip URLs
    value = re.sub(r"https?://\S+", "", value)
    # Strip footnote markers [1] [2] [1-4] etc
    value = re.sub(r"\[\d+(?:[,-]\s*\d+)*\]", "", value)
    # Strip anchor text patterns #:~:text=...
    value = re.sub(r"#:~:text=\S+", "", value)
    # Strip % encoded chars
    value = re.sub(r"%[0-9A-Fa-f]{2}", " ", value)
    # Strip bare % followed by word chars
    value = re.sub(r"%\w+", "", value)
    # Collapse multiple spaces
    value = re.sub(r"  +", " ", value)
    # Collapse multiple semicolons/commas
    value = re.sub(r";(\s*;)+", ";", value)
    value = re.sub(r",(\s*,)+", ",", value)
    # Strip leading/trailing whitespace and punctuation
    value = value.strip(" ;,.")
    return value


def clean_csv(inpath, outpath):
    if not inpath.exists():
        return None

    with open(inpath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        if not fieldnames:
            print(f"No header found in {inpath}")
            return None
        rows = []
        for row in reader:
            cleaned = {k: clean_field(v) for k, v in row.items() if k is not None and k in fieldnames}
            rows.append(cleaned)

    with open(outpath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return rows


def run():
    cleaned_count = 0

    # Clean guild_relations.csv (always)
    if GUILD_REL.exists():
        print(f"Cleaning {GUILD_REL}...")
        rows = clean_csv(GUILD_REL, GUILD_REL)
        if rows:
            cleaned_count += len(rows)
            print(f"  Cleaned {len(rows)} rows")

            # Sample
            for row in rows[:3]:
                anchor = row.get("anchor_plant", "?")
                companion = row.get("companion_plant", "?")
                fn = row.get("guild_function", "?")
                notes = (row.get("notes") or "")[:60]
                print(f"  {anchor} + {companion} ({fn})")
                print(f"    notes: {notes}")
            print()

            # Stats
            n_fix = sum(1 for r in rows if "nitrogen" in (r.get("guild_function") or "").lower())
            conflict = sum(1 for r in rows if r.get("relationship_type") == "conflict")
            anchors = len(set(r.get("anchor_plant", "") for r in rows))
            print(f"  Anchors: {anchors}")
            print(f"  Nitrogen fixers: {n_fix}")
            print(f"  Conflicts: {conflict}")

    # Clean guild_matrix_raw.csv if present
    if GUILD_RAW.exists():
        print(f"\nCleaning {GUILD_RAW} → {GUILD_CLEAN}...")
        rows = clean_csv(GUILD_RAW, GUILD_CLEAN)
        if rows:
            cleaned_count += len(rows)
            print(f"  Cleaned {len(rows)} rows → {GUILD_CLEAN}")

    if cleaned_count == 0:
        print("No files to clean.")
        if not GUILD_REL.exists():
            print(f"  Missing: {GUILD_REL}")
        if not GUILD_RAW.exists():
            print(f"  Missing: {GUILD_RAW} (optional)")

    return cleaned_count


if __name__ == "__main__":
    run()
