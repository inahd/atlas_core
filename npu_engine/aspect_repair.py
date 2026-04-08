"""
aspect_repair.py — Adds directional planetary aspect edges to the NPU graph.

Creates 13 swara entities and connects them to grahas via
directed aspect edges based on Jyotiṣa dṛṣṭi (planetary gaze) rules.

Each planet gazes at specific houses from its position.
Each house maps to a swara position in the octave.
The gaze has force, quality, and duration characteristics.

Rāhu/Ketu have vakra (retrograde) quality — the gaze doubles back.
"""

import csv
from pathlib import Path

# ── Swara entities to create ──────────────────────────────────────

SWARA_ENTITIES = {
    "swara_sa":          {"name": "Sa",          "iast": "Ṣaḍja",       "ratio": 1.0,      "semitone": 0,  "position": 1},
    "swara_komal_re":    {"name": "Komal Re",    "iast": "Komal Ṛṣabha","ratio": 256/243,  "semitone": 1,  "position": 2},
    "swara_shuddha_re":  {"name": "Shuddha Re",  "iast": "Ṛṣabha",     "ratio": 9/8,      "semitone": 2,  "position": 2},
    "swara_komal_ga":    {"name": "Komal Ga",    "iast": "Komal Gāndhāra","ratio": 32/27,  "semitone": 3,  "position": 3},
    "swara_shuddha_ga":  {"name": "Shuddha Ga",  "iast": "Gāndhāra",   "ratio": 5/4,      "semitone": 4,  "position": 3},
    "swara_shuddha_ma":  {"name": "Shuddha Ma",  "iast": "Madhyama",   "ratio": 4/3,      "semitone": 5,  "position": 4},
    "swara_teevra_ma":   {"name": "Teevra Ma",   "iast": "Tīvra Madhyama","ratio": 45/32, "semitone": 6,  "position": 4},
    "swara_pa":          {"name": "Pa",          "iast": "Pañcama",     "ratio": 3/2,      "semitone": 7,  "position": 5},
    "swara_komal_dha":   {"name": "Komal Dha",   "iast": "Komal Dhaivata","ratio": 128/81, "semitone": 8,  "position": 6},
    "swara_shuddha_dha": {"name": "Shuddha Dha", "iast": "Dhaivata",   "ratio": 5/3,      "semitone": 9,  "position": 6},
    "swara_komal_ni":    {"name": "Komal Ni",    "iast": "Komal Niṣāda","ratio": 16/9,     "semitone": 10, "position": 7},
    "swara_shuddha_ni":  {"name": "Shuddha Ni",  "iast": "Niṣāda",    "ratio": 15/8,     "semitone": 11, "position": 7},
    "swara_tara_sa":     {"name": "Tara Sa",     "iast": "Tāra Ṣaḍja", "ratio": 2.0,      "semitone": 12, "position": 8},
}

# ── Planetary aspect rules (Jyotiṣa dṛṣṭi) ──────────────────────

ASPECT_RULES = {
    "graha_mangala": {
        "aspects": [4, 7, 8],
        "force": 1.0,
        "quality": "sharp_precise_fierce",
        "gaze_duration": "insistent",
    },
    "graha_guru": {
        "aspects": [5, 7, 9],
        "force": 0.9,
        "quality": "expansive_generous_wise",
        "gaze_duration": "dwelling",
    },
    "graha_shani": {
        "aspects": [3, 7, 10],
        "force": 0.85,
        "quality": "slow_heavy_austere",
        "gaze_duration": "weighted",
    },
    "graha_surya": {
        "aspects": [7],
        "force": 1.0,
        "quality": "bright_clear_sovereign",
        "gaze_duration": "commanding",
    },
    "graha_chandra": {
        "aspects": [7],
        "force": 0.7,
        "quality": "soft_reflective_fluid",
        "gaze_duration": "touching",
    },
    "graha_shukra": {
        "aspects": [7],
        "force": 0.8,
        "quality": "sweet_aesthetic_attractive",
        "gaze_duration": "caressing",
    },
    "graha_budha": {
        "aspects": [7],
        "force": 0.75,
        "quality": "quick_analytical_communicative",
        "gaze_duration": "darting",
    },
    "graha_rahu": {
        "aspects": [5, 7, 9],
        "force": 0.8,
        "quality": "shadowy_obsessive_amplifying",
        "gaze_duration": "returning",
        "retrograde": True,
    },
    "graha_ketu": {
        "aspects": [5, 7, 9],
        "force": 0.7,
        "quality": "dissolving_releasing_moksha",
        "gaze_duration": "fading",
        "retrograde": True,
    },
}

# ── Canonical planet → swara affinity ─────────────────────────────
# Which swara each planet naturally gazes from its own seat

PLANETARY_SWARA_AFFINITY = {
    "graha_surya":   "swara_sa",
    "graha_chandra": "swara_komal_ni",
    "graha_mangala": "swara_komal_ga",
    "graha_budha":   "swara_shuddha_re",
    "graha_guru":    "swara_shuddha_ma",
    "graha_shukra":  "swara_pa",
    "graha_shani":   "swara_komal_dha",
    "graha_rahu":    "swara_teevra_ma",
    "graha_ketu":    "swara_komal_re",
}

# House position → swara mapping (zodiac → octave)
POSITION_TO_SWARAS = {}
for swara_id, info in SWARA_ENTITIES.items():
    pos = info["position"]
    POSITION_TO_SWARAS.setdefault(pos, []).append(swara_id)


def add_aspect_edges(graph):
    """Add swara entities and planetary aspect edges to a live GraphEngine.

    Returns count of entities and edges added.
    """
    entities_added = 0
    edges_added = 0

    # 1. Create swara entities in graph metadata
    for swara_id, info in SWARA_ENTITIES.items():
        if swara_id not in graph._metadata:
            graph._metadata[swara_id] = {
                "category": "swara",
                "name": info["name"],
                "aliases": [info["iast"]],
                "sources": ["gandharva_veda"],
                "authorities": ["traditional"],
                "attributes": {
                    "ratio": [str(info["ratio"])],
                    "semitone": [str(info["semitone"])],
                    "position": [str(info["position"])],
                    "iast": [info["iast"]],
                },
            }
            entities_added += 1

    # 2. Add canonical affinity edges (planet → its home swara)
    for graha_id, swara_id in PLANETARY_SWARA_AFFINITY.items():
        if graha_id not in graph._metadata:
            continue
        rules = ASPECT_RULES.get(graha_id, {})
        edge = {
            "from_id": graha_id,
            "to_id": swara_id,
            "relation": "canonical_swara_affinity",
            "confidence": "0.90",
            "authority": "traditional",
            "source_file": "aspect_repair",
            "force": str(rules.get("force", 0.5)),
            "quality": rules.get("quality", ""),
            "gaze_duration": rules.get("gaze_duration", ""),
        }
        graph._relations.setdefault(graha_id, []).append(edge)
        edges_added += 1

    # 3. Add directional aspect edges (planet gazes at swara positions)
    for graha_id, rules in ASPECT_RULES.items():
        if graha_id not in graph._metadata:
            continue
        for house_offset in rules["aspects"]:
            # Map house offset to swaras at that position
            target_swaras = POSITION_TO_SWARAS.get(house_offset, [])
            # Also handle positions > 8 by wrapping
            if house_offset > 8:
                wrapped = ((house_offset - 1) % 8) + 1
                target_swaras = POSITION_TO_SWARAS.get(wrapped, [])

            for swara_id in target_swaras:
                edge = {
                    "from_id": graha_id,
                    "to_id": swara_id,
                    "relation": "aspects_with_gaze",
                    "confidence": "0.85",
                    "authority": "traditional",
                    "source_file": "aspect_repair",
                    "force": str(rules["force"]),
                    "quality": rules["quality"],
                    "gaze_duration": rules["gaze_duration"],
                    "tradition": "gandharva_veda",
                    "direction": "one_way",
                }
                graph._relations.setdefault(graha_id, []).append(edge)
                edges_added += 1

                # Vakra (retrograde) — the note double-backs
                if rules.get("retrograde"):
                    vakra_edge = {
                        "from_id": swara_id,
                        "to_id": graha_id,
                        "relation": "received_vakra_gaze",
                        "confidence": "0.80",
                        "authority": "traditional",
                        "source_file": "aspect_repair",
                        "force": str(rules["force"] * 0.7),
                        "quality": rules["quality"],
                        "gaze_duration": rules["gaze_duration"],
                        "tradition": "gandharva_veda",
                    }
                    graph._relations.setdefault(swara_id, []).append(vakra_edge)
                    edges_added += 1

    return entities_added, edges_added


if __name__ == "__main__":
    from npu_engine.graph_engine import GraphEngine
    g = GraphEngine()
    ents, edges = add_aspect_edges(g)
    print(f"✓ Added {ents} swara entities, {edges} aspect edges")

    # Verify
    for graha in ["graha_mangala", "graha_guru", "graha_shani"]:
        aspect_edges = [e for e in g.get_neighbors(graha)
                        if e["relation"] in ("aspects_with_gaze", "canonical_swara_affinity")]
        targets = [e["to_id"] for e in aspect_edges]
        print(f"  {graha}: gazes at {targets}")

    # Check vakra
    vakra = g.get_neighbors("swara_teevra_ma", exclude_inverse=False)
    print(f"  swara_teevra_ma vakra edges: {[e['to_id'] for e in vakra if e['relation']=='received_vakra_gaze']}")
