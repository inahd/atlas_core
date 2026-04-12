#!/usr/bin/env python3
"""
derive_composition_relations.py — REL-006

Reads composition CSVs and derives relation triples:
  composition → raga, tala, ashtakala, deity, composer, vraja_forest

Outputs: datasets/relations/composition_relations.csv
"""

import csv
import os
import re

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

COMPOSITION_FILES = [
    os.path.join(_ROOT, "datasets", "compositions", "narottama_padas.csv"),
    os.path.join(_ROOT, "datasets", "compositions", "gaudiya_compositions.csv"),
    os.path.join(_ROOT, "datasets", "compositions", "nakshatra_kritis.csv"),
]

ASHTAKALA_CSV = os.path.join(_ROOT, "datasets", "cosmology", "ashtakala.csv")
VRAJA_CSV = os.path.join(_ROOT, "datasets", "cosmology", "vraja_forests.csv")
OUTPUT = os.path.join(_ROOT, "datasets", "relations", "composition_relations.csv")


def slugify(s: str) -> str:
    """Lowercase, strip diacritics roughly, replace spaces with underscores."""
    s = s.strip().lower()
    s = (s.replace("ā", "a").replace("ī", "i").replace("ū", "u")
          .replace("ṛ", "r").replace("ṣ", "sh").replace("ś", "sh")
          .replace("ṇ", "n").replace("ṅ", "n").replace("ṭ", "t")
          .replace("ḍ", "d").replace("ñ", "n").replace("ḥ", "h")
          .replace("ṃ", "m").replace("ö", "o").replace("ü", "u")
          .replace("é", "e"))
    s = re.sub(r"[''‑\-/().,;:!?\"]+", " ", s)
    s = re.sub(r"\s+", "_", s.strip())
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def load_csv(path: str) -> list:
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        # Skip blank leading lines
        lines = f.readlines()
        content = "".join(l for l in lines if l.strip())
        reader = csv.DictReader(content.splitlines())
        return list(reader)


def load_ashtakala_map() -> dict:
    """Return {period_number: {name, forest, raga, ...}}"""
    rows = load_csv(ASHTAKALA_CSV)
    m = {}
    for r in rows:
        period = r.get("period", "").strip()
        if period:
            m[int(period)] = r
    return m


def load_vraja_forest_map() -> dict:
    """Return {ashtakala_period_str: [forest_name, ...]}"""
    rows = load_csv(VRAJA_CSV)
    m = {}
    for r in rows:
        ap = r.get("ashtakala_period", "").strip()
        name = r.get("name", "").strip()
        if not ap or not name:
            continue
        # ashtakala_period can be "1", "1_and_8", "1-8", etc.
        periods = re.findall(r"\d+", ap)
        for p in periods:
            m.setdefault(p, []).append(name)
    return m


# Map raga keywords to ashtakala period numbers
RAGA_ASHTAKALA_MAP = {
    "bhairav": 1, "bhairavi": 1, "ahir_bhairav": 1, "sindhu_bhairavi": 1,
    "lalit": 1, "bairagi": 1,
    "todi": 2, "gujari_todi": 2, "gurjari_todi": 2,
    "bilaval": 3, "deshkar": 3, "maand": 3,
    "bhimpalasi": 4, "multani": 4,
    "puriya_dhanashri": 5, "marwa": 5,
    "yaman": 6, "kedar": 6, "kamod": 6,
    "bageshri": 7, "khamaj": 7, "mishra_khamaj": 7, "misra_khamaj": 7,
    "des": 7,
    "darbari": 8, "darbari_kanada": 8, "jaunpuri": 8,
    "misra_kafi": 8, "mishra_kafi": 8, "kafi": 8,
    "jhinjhoti": 4,
    "misra_gara": None,  # any time
    "saurastram": None, "asaveri": None, "surati": None,
    "nata_kuranji": None, "athana": None, "pharaju": None,
    "yadukulakambhoji": None, "ramapriya": None, "shanmukhapriya": None,
    "revagupti": None,
}

# Deity mappings for Narottama padas (from composition name / notes)
COMPOSITION_DEITY_MAP = {
    "narottama_gauranga_karuna": ["deity:gauranga"],
    "narottama_sri_guru_carana": ["deity:guru"],
    "narottama_sri_krsna_caitanya": ["deity:gauranga", "deity:nityananda"],
    "narottama_radha_krsna_prana": ["deity:radha", "deity:krishna"],
    "narottama_gaurangera_duti_pada": ["deity:gauranga"],
    "narottama_hari_haraye": ["deity:krishna"],
    "narottama_je_anilo_prema": ["deity:gauranga"],
    "narottama_vrndavana_ramya": ["deity:radha", "deity:krishna"],
    "NDT001": ["deity:gauranga"],
    "NDT002": ["deity:guru"],
    "NDT003": ["deity:gauranga", "deity:nityananda"],
    "NDT004": ["deity:radha", "deity:krishna"],
    "NDT005": ["deity:gauranga"],
    "NDT006": ["deity:krishna"],
    "NDT007": ["deity:gauranga"],
    "NDT008": ["deity:radha", "deity:krishna"],
}

# Navagraha kritis → graha deity
NAVAGRAHA_DEITY = {
    "navagraha_surya": "deity:surya",
    "navagraha_chandra": "deity:chandra",
    "navagraha_mars": "deity:mangala",
    "navagraha_mercury": "deity:budha",
    "navagraha_jupiter": "deity:brihaspati",
    "navagraha_venus": "deity:shukra",
    "navagraha_saturn": "deity:shani",
    "navagraha_rahu": "deity:rahu",
    "navagraha_ketu": "deity:ketu",
}


def derive_ashtakala_from_notes(notes: str) -> str | None:
    """Parse 'Ashtakala: dawn' style hints from notes."""
    notes_l = notes.lower()
    if "ashtakala:" in notes_l:
        after = notes_l.split("ashtakala:")[1].strip().split(";")[0].split("(")[0].strip()
        keyword_map = {
            "dawn": "nisanta", "pre-dawn": "nisanta", "early morning": "pratah",
            "morning": "pratah", "midday": "madhyahna", "afternoon": "aparahna",
            "twilight": "sayahna", "evening": "sayahna", "night": "ratri",
            "midnight": "ratri",
        }
        for kw, period in keyword_map.items():
            if kw in after:
                return period
    return None


def raga_to_ashtakala_period(raga: str) -> int | None:
    """Map raga name to ashtakala period number."""
    slug = slugify(raga)
    # Try exact match first
    if slug in RAGA_ASHTAKALA_MAP:
        return RAGA_ASHTAKALA_MAP[slug]
    # Try partial match
    for key, period in RAGA_ASHTAKALA_MAP.items():
        if key in slug or slug in key:
            return period
    return None


def main():
    ashtakala_map = load_ashtakala_map()
    forest_map = load_vraja_forest_map()

    # Build period_name → period_number lookup
    name_to_period = {}
    for num, info in ashtakala_map.items():
        name_to_period[slugify(info.get("name", ""))] = num

    relations = []
    seen = set()
    seen_entity_ids = set()

    for fpath in COMPOSITION_FILES:
        rows = load_csv(fpath)
        for row in rows:
            eid = row.get("entity_id", "").strip()
            etype = row.get("entity_type", "").strip()

            # Skip non-composition rows (ashtakala_period, rasa, statement)
            if etype in ("ashtakala_period", "rasa", "statement", ""):
                continue
            if not eid:
                continue

            # Dedup across files (narottama padas appear in both files)
            if eid in seen_entity_ids:
                continue
            seen_entity_ids.add(eid)

            from_id = f"composition:{eid}"
            composer = row.get("composer", "").strip()
            raga = row.get("raga", "").strip()
            tala = row.get("tala", "").strip()
            notes = row.get("notes", "")

            def add(relation, to_id, confidence="0.9", attestation="attested_classical"):
                key = (from_id, relation, to_id)
                if key not in seen:
                    seen.add(key)
                    relations.append({
                        "from_id": from_id,
                        "relation": relation,
                        "to_id": to_id,
                        "confidence": confidence,
                        "attestation_status": attestation,
                    })

            # ── Raga ──
            if raga and raga != "–":
                # Handle "Khamaj / Des" or "Khamaj or Des" style
                raga_parts = re.split(r"\s*/\s*|\s+or\s+", raga)
                for rp in raga_parts:
                    rp = rp.strip()
                    if rp and rp != "–":
                        raga_slug = slugify(rp)
                        add("composition_raga", f"raga:{raga_slug}")

            # ── Tala ──
            if tala and tala != "–":
                tala_parts = re.split(r"\s*/\s*|\s+or\s+", tala)
                for tp in tala_parts:
                    tp = tp.strip()
                    if tp and tp != "–":
                        tala_slug = slugify(tp)
                        add("composition_tala", f"tala:{tala_slug}")

            # ── Composer ──
            if composer and composer != "–":
                composer_slug = slugify(composer)
                add("composed_by", f"composer:{composer_slug}")

            # ── Deity ──
            if eid in COMPOSITION_DEITY_MAP:
                for deity_id in COMPOSITION_DEITY_MAP[eid]:
                    add("composition_deity", deity_id)
            if eid in NAVAGRAHA_DEITY:
                add("composition_deity", NAVAGRAHA_DEITY[eid])

            # ── Ashtakala ──
            # Try notes first, then raga mapping
            ashtakala_name = derive_ashtakala_from_notes(notes)
            if ashtakala_name:
                add("composition_ashtakala", f"ashtakala:{ashtakala_name}")
                period_num = name_to_period.get(ashtakala_name)
            else:
                # Derive from raga
                period_num = None
                if raga and raga != "–":
                    first_raga = re.split(r"\s*/\s*|\s+or\s+", raga)[0].strip()
                    period_num = raga_to_ashtakala_period(first_raga)
                if period_num and period_num in ashtakala_map:
                    ak_name = slugify(ashtakala_map[period_num]["name"])
                    add("composition_ashtakala", f"ashtakala:{ak_name}",
                        confidence="0.7", attestation="derived_raga_time")

            # ── Vraja forest (Narottama padas only) ──
            is_narottama = "narottama" in composer.lower() if composer else False
            if is_narottama and period_num:
                forests = forest_map.get(str(period_num), [])
                for forest_name in forests:
                    forest_slug = slugify(forest_name)
                    add("evokes_vraja_forest", f"vraja_forest:{forest_slug}",
                        confidence="0.7", attestation="derived_ashtakala_topology")

    # Write output
    relations.sort(key=lambda r: (r["from_id"], r["relation"], r["to_id"]))

    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "from_id", "relation", "to_id", "confidence", "attestation_status"
        ])
        writer.writeheader()
        writer.writerows(relations)

    # Summary
    preds = set(r["relation"] for r in relations)
    print(f"✦ composition_relations.csv: {len(relations)} rows")
    print(f"  predicates: {sorted(preds)}")
    print(f"  unique compositions: {len(seen_entity_ids)}")


if __name__ == "__main__":
    main()
