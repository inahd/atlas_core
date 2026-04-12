"""
Derive raga-ritual relations from ashtakala.csv, daily_program.csv,
and gaudiya_festivals.csv. Writes to datasets/relations/relations_raga_ritual.csv.
"""

import csv
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / "datasets" / "relations" / "relations_raga_ritual.csv"

HEADER = [
    "from_id", "relation", "to_id", "source_title", "source_locator",
    "excerpt", "tradition", "confidence", "notes"
]


def slugify(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")


def raga_id(name: str) -> str:
    return f"raga:{slugify(name)}"


def load_csv(rel_path: str) -> list[dict]:
    with open(BASE / rel_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    rows = []

    # --- Ashtakala: raga + raga_alt → period ---
    ashtakala = load_csv("datasets/cosmology/ashtakala.csv")
    for r in ashtakala:
        period_slug = slugify(r["name"])
        period_id = f"ashtakala:{period_slug}"

        for raga_col in ("raga", "raga_alt"):
            raga_name = r.get(raga_col, "").strip()
            if not raga_name:
                continue
            rid = raga_id(raga_name)

            # forward: raga → prescribed_for → ashtakala period
            rows.append({
                "from_id": rid,
                "relation": "raga_prescribed_for",
                "to_id": period_id,
                "source_title": "Ashtakala CSV",
                "source_locator": "cosmology/ashtakala.csv",
                "excerpt": "",
                "tradition": "gaudiya_vaishnava",
                "confidence": "0.95",
                "notes": f"{raga_col} for {r['name']} period ({r['time_start']}–{r['time_end']})"
            })

            # inverse: ashtakala period → ashtakala_raga → raga
            rows.append({
                "from_id": period_id,
                "relation": "ashtakala_raga",
                "to_id": rid,
                "source_title": "Ashtakala CSV",
                "source_locator": "cosmology/ashtakala.csv",
                "excerpt": "",
                "tradition": "gaudiya_vaishnava",
                "confidence": "0.95",
                "notes": f"{raga_col} for {r['name']} period"
            })

    # --- Daily Program: raga_appropriate → program activity ---
    daily = load_csv("datasets/cosmology/daily_program.csv")
    for r in daily:
        raga_name = r.get("raga_appropriate", "").strip()
        if not raga_name:
            continue
        rid = raga_id(raga_name)
        prog_slug = slugify(r["name"])
        prog_id = f"program:{prog_slug}"

        rows.append({
            "from_id": rid,
            "relation": "raga_prescribed_for",
            "to_id": prog_id,
            "source_title": "Daily Program CSV",
            "source_locator": "cosmology/daily_program.csv",
            "excerpt": "",
            "tradition": "gaudiya_vaishnava",
            "confidence": "0.90",
            "notes": f"raga for {r['name']} ({r['time']})"
        })

    # --- Gaudiya Festivals: raga → festival ---
    festivals = load_csv("datasets/cosmology/gaudiya_festivals.csv")
    for r in festivals:
        raga_name = r.get("raga", "").strip()
        if not raga_name:
            continue
        rid = raga_id(raga_name)
        fest_slug = slugify(r["name"])
        fest_id = f"festival:{fest_slug}"

        rows.append({
            "from_id": rid,
            "relation": "raga_prescribed_for",
            "to_id": fest_id,
            "source_title": "Gaudiya Festivals CSV",
            "source_locator": "cosmology/gaudiya_festivals.csv",
            "excerpt": "",
            "tradition": "gaudiya_vaishnava",
            "confidence": "0.90",
            "notes": f"raga for {r['name']} ({r['tithi']} {r['month']})"
        })

    # Deduplicate by (from_id, relation, to_id)
    seen = set()
    unique = []
    for r in rows:
        key = (r["from_id"], r["relation"], r["to_id"])
        if key not in seen:
            seen.add(key)
            unique.append(r)

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=HEADER)
        w.writeheader()
        w.writerows(unique)

    print(f"Wrote {len(unique)} rows to {OUT}")


if __name__ == "__main__":
    main()
