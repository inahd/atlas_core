"""
library_kernel.py — The Atlas library system.

The library knows what it has, what it's missing, and what
it needs next. It's the system's own librarian.

Three functions:
1. INVENTORY  — catalog all datasets and their completeness
2. GAPS       — identify what's missing or incomplete
3. GROWTH     — track what's been added, suggest what's next

Writes /tmp/library_state.json. Serves at /library endpoint.
"""

import csv, json, time
from pathlib import Path
from typing import Dict, List, Any

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "datasets"

# ── Known text corpus — what we should have ──────────────────
TEXT_CORPUS = {
    "Brahma_Samhita": {
        "tradition": "Gaudiya", "layer": "S0", "verses_total": 62,
        "priority": 1,
        "notes": "Most technical Goloka description. 5.1-5.5 critical.",
        "key_verses": ["5.1", "5.29", "5.30", "5.37", "5.38"],
    },
    "Sikshashtakam": {
        "tradition": "Gaudiya", "layer": "S0", "verses_total": 8,
        "priority": 1,
        "notes": "8 verses by Mahaprabhu. Complete theology in miniature.",
        "key_verses": ["1", "2", "3", "4", "5", "6", "7", "8"],
    },
    "Bhagavata_Purana": {
        "tradition": "Gaudiya/Vedic", "layer": "S0/S1", "verses_total": 18000,
        "priority": 2,
        "notes": "Key passages: 2.2.24 (cosmos), 5.16-26 (geography), 10.1-90 (Krishna lila)",
        "key_verses": ["2.2.24", "5.16.1", "10.1.1"],
    },
    "Natya_Shastra": {
        "tradition": "Vedic", "layer": "S3", "verses_total": 6000,
        "priority": 2,
        "notes": "Chapters 28-33 on music. Origin of raga from Brahma.",
        "key_verses": ["28.1", "29.1", "33.1"],
    },
    "Sangita_Ratnakara": {
        "tradition": "Classical", "layer": "S3", "verses_total": 1700,
        "priority": 2,
        "notes": "Most comprehensive music text. 7 chapters.",
        "key_verses": ["1.1", "2.1", "4.1"],
    },
    "Saundarya_Lahari": {
        "tradition": "Tantric", "layer": "S1/S2", "verses_total": 100,
        "priority": 2,
        "notes": "100 verses describing Sri Yantra in sound.",
        "key_verses": ["1", "2", "9", "10", "11"],
    },
    "Chaitanya_Charitamrita": {
        "tradition": "Gaudiya", "layer": "S0", "verses_total": 17000,
        "priority": 3,
        "notes": "Life and teachings of Mahaprabhu.",
        "key_verses": ["Adi.1.1", "Madhya.8.70", "Antya.20.12"],
    },
}

# ── Known dataset gaps ────────────────────────────────────────
KNOWN_GAPS = {
    "matrika_50": {
        "description": "50 Sanskrit letters with full cosmological correspondence",
        "layer": "S2", "priority": 1,
        "what_exists": "phoneme formants in vocal/graph_seed_data.py",
        "what_needed": "devanagari, element, deity, bija, nakshatra, yantra position",
        "path": "datasets/sanskrit/matrika_50.csv",
    },
    "sacred_sites_india": {
        "description": "India sacred geography with chakra mapping",
        "layer": "S6", "priority": 2,
        "what_exists": "nothing",
        "what_needed": "GPS coordinates, deity, chakra, nakshatra, ley line connections",
        "path": "datasets/geography/sacred_sites_india.csv",
    },
    "vraja_parikrama": {
        "description": "Vrindavana circumambulation path with lila references",
        "layer": "S0/S6", "priority": 1,
        "what_exists": "vraja_forests.csv (12 forests, no coordinates)",
        "what_needed": "GPS, path sequence, lila at each stop, time/raga/plant",
        "path": "datasets/geography/vraja_parikrama.csv",
    },
    "key_passages": {
        "description": "Critical cosmological text passages",
        "layer": "S0/S1/S2/S3", "priority": 1,
        "what_exists": "passages.csv (1219 entries, unsorted)",
        "what_needed": "Brahma Samhita 5.1, Sikshashtakam all 8, Natya Shastra music origin",
        "path": "datasets/sources/passages.csv",
    },
    "dasha_meanings": {
        "description": "Vimshottari dasha period meanings and practices",
        "layer": "S4", "priority": 2,
        "what_exists": "nothing",
        "what_needed": "9 dasha lords, meanings, ragas, practices, duration",
        "path": "datasets/karma/dasha_meanings.csv",
    },
    "marma_coordinates": {
        "description": "37 marma points with x,y for body SVG",
        "layer": "S6", "priority": 2,
        "what_exists": "marma_master.csv (37 points, no coordinates)",
        "what_needed": "normalized x,y positions on body silhouette",
        "path": "datasets/marma/marma_coordinates.csv",
    },
    "gaudiya_festivals_full": {
        "description": "Complete Vaishnava festival calendar (50+ events)",
        "layer": "S0", "priority": 2,
        "what_exists": "gaudiya_festivals.csv (14 major festivals)",
        "what_needed": "appearance/disappearance days of all acharyas, minor festivals",
        "path": "datasets/cosmology/gaudiya_festivals.csv",
    },
    "raga_graphs_expanded": {
        "description": "Raga phrase graphs for all 30+ ragas in the system",
        "layer": "S2", "priority": 2,
        "what_exists": "raga_graph.py has ~8 ragas",
        "what_needed": "full directed graph for each raga in raga_master_extended",
        "path": "npu_engine/raga_graph.py",
    },
}


def inventory_datasets() -> Dict[str, Any]:
    """Catalog all datasets with row counts and completeness."""
    result = {}
    for f in sorted(DATA.rglob("*.csv")):
        if "_archive" in str(f) or "_inbox" in str(f):
            continue
        try:
            rows = list(csv.DictReader(open(f, encoding="utf-8")))
            rel = str(f.relative_to(ROOT))
            cols = list(rows[0].keys()) if rows else []
            empty = sum(1 for row in rows
                        if any(not v for v in list(row.values())[:3]))
            result[rel] = {
                "rows": len(rows), "cols": cols[:6],
                "empty_rows": empty, "complete": empty == 0,
            }
        except Exception as e:
            result[str(f.relative_to(ROOT))] = {"error": str(e)}
    return result


def inventory_texts() -> Dict[str, Any]:
    """Check which key texts are in the passages database."""
    passages_path = DATA / "sources" / "passages.csv"
    have = {}
    if passages_path.exists():
        for row in csv.DictReader(open(passages_path, encoding="utf-8")):
            src = row.get("source_id", row.get("source", ""))
            if src:
                have[src] = have.get(src, 0) + 1

    result = {}
    for text_id, meta in TEXT_CORPUS.items():
        count = have.get(text_id, 0)
        result[text_id] = {
            **meta,
            "passages_have": count,
            "passages_need": len(meta.get("key_verses", [])),
            "complete": count >= len(meta.get("key_verses", [])),
        }
    return result


def inventory_graph() -> Dict[str, Any]:
    """Check NPU graph node types and counts."""
    try:
        from npu_engine.datasets import load_entity_metadata
        meta = load_entity_metadata()
        types = {}
        for e in meta.values():
            t = e.get("category", "unknown")
            types[t] = types.get(t, 0) + 1
        return {
            "total": len(meta),
            "by_type": dict(sorted(types.items(), key=lambda x: -x[1])),
        }
    except Exception as e:
        return {"error": str(e)}


def detect_gaps(datasets: Dict, texts: Dict) -> List[Dict]:
    """Identify gaps ordered by priority."""
    gaps = []
    for gap_id, gap in KNOWN_GAPS.items():
        path = ROOT / gap["path"]
        exists = path.exists()
        gaps.append({
            "id": gap_id, "description": gap["description"],
            "layer": gap["layer"], "priority": gap["priority"],
            "exists": exists,
            "what_exists": gap["what_exists"],
            "what_needed": gap["what_needed"],
        })
    for text_id, text in texts.items():
        if not text["complete"] and text["priority"] <= 2:
            gaps.append({
                "id": f"text:{text_id}",
                "description": f"{text_id} passages",
                "layer": text["layer"], "priority": text["priority"],
                "exists": text["passages_have"] > 0,
                "what_exists": f"{text['passages_have']} passages",
                "what_needed": f"{text['passages_need']} key passages",
            })
    return sorted(gaps, key=lambda x: x["priority"])


def track_growth() -> Dict[str, Any]:
    try:
        import subprocess
        recent = subprocess.check_output(
            ["git", "-C", str(ROOT), "log",
             "--oneline", "--since=7 days ago", "--", "datasets/"],
            stderr=subprocess.DEVNULL, text=True).strip()
        return {"recent_commits": recent.split("\n") if recent else []}
    except Exception:
        return {"recent_commits": []}


def suggest_next(gaps: List[Dict]) -> List[Dict]:
    return [g for g in gaps if not g.get("exists")][:5]


def build_library_state() -> Dict[str, Any]:
    """Full library inventory."""
    datasets = inventory_datasets()
    texts    = inventory_texts()
    graph    = inventory_graph()
    gaps     = detect_gaps(datasets, texts)
    growth   = track_growth()
    next_up  = suggest_next(gaps)

    state = {
        "timestamp": time.time(),
        "summary": {
            "dataset_files": len(datasets),
            "dataset_rows": sum(d.get("rows", 0) for d in datasets.values()),
            "graph_nodes": graph.get("total", 0),
            "text_gaps": sum(1 for t in texts.values() if not t["complete"]),
            "open_gaps": sum(1 for g in gaps if not g.get("exists")),
        },
        "graph": graph,
        "texts": texts,
        "gaps": gaps,
        "growth": growth,
        "next": next_up,
    }

    Path("/tmp/library_state.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2))
    return state


def print_library_report(state: Dict):
    s = state["summary"]
    print(f"\n✦ ATLAS LIBRARY")
    print(f"  {s['dataset_files']} datasets · "
          f"{s['dataset_rows']:,} rows · "
          f"{s['graph_nodes']:,} graph nodes")
    print(f"  {s['open_gaps']} open gaps · "
          f"{s['text_gaps']} text gaps\n")

    print("NEXT ACQUISITIONS:")
    for item in state["next"]:
        print(f"  [{item['priority']}] {item['description']}")
        print(f"      have: {item['what_exists']}")
        print(f"      need: {item['what_needed']}")

    print(f"\nRECENT ADDITIONS:")
    for commit in state["growth"]["recent_commits"][:5]:
        print(f"  {commit}")


if __name__ == "__main__":
    print("Building library state...")
    state = build_library_state()
    print_library_report(state)
