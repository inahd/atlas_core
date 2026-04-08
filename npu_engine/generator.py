"""
npu_engine/generator.py — Relational content generator.

Final step in NPU pipeline. No API calls. No external processes.
Pure graph traversal → structured artifacts.

On field change:
  nakshatra transition → brief, practice, paths, sound context, card spread
  tithi transition → devi reading
  muhurta change → alert

Usage:
  from npu_engine.generator import get_generator
  gen = get_generator()
  artifacts = gen.process(field_state_dict)
"""

import json
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional

from .graph_engine import GraphEngine
from .path_engine import find_paths, format_path, detect_flows
from .layer_engine import entity_layer

# ── Helpers ───────────────────────────────────────

def _slug(name):
    n = unicodedata.normalize("NFKD", str(name or ""))
    n = n.encode("ascii", "ignore").decode("ascii")
    return n.lower().strip().replace(" ", "_").replace("-", "_")


def _first_attr(meta, key, default=""):
    attrs = meta.get("attributes", {})
    vals = attrs.get(key, [])
    return vals[0] if vals else default


TALA_BOLS = {
    "Adi": ["dha", "dhin", "dhin", "dha", "dha", "tin", "tin", "ta"],
    "Rupak": ["tin", "tin", "na", "dhin", "na", "dhin", "na"],
    "Jhaptal": ["dhi", "na", "dhi", "dhi", "na", "tin", "na", "dhi", "dhi", "na"],
    "Dadra": ["dha", "dhin", "na", "dha", "tin", "na"],
    "Keherwa": ["dha", "ge", "na", "tin", "na", "ke", "dhin", "na"],
}
TALA_BEATS = {k: len(v) for k, v in TALA_BOLS.items()}


# ── FieldGenerator ────────────────────────────────

class FieldGenerator:
    def __init__(self):
        self._graph = GraphEngine()
        self._last_p = {}
        self._generated = {}

    def process(self, fs: Dict) -> Dict[str, Any]:
        """Called when field_state changes. Returns all generated artifacts."""
        changes = self._detect_changes(fs)
        if not changes:
            return self._generated

        for ctype, old_val, new_val in changes:
            arts = self._dispatch(ctype, new_val, fs)
            self._generated.update(arts)

        self._persist(self._generated)
        return self._generated

    def get(self, key):
        return self._generated.get(key)

    def all_keys(self):
        return list(self._generated.keys())

    # ── Change detection ──────────────────────────

    def _detect_changes(self, fs):
        p = fs.get("panchanga", {})
        mu = fs.get("muhurta", {})
        changes = []

        # Nakshatra — use IAST display name for change detection
        new_nak = p.get("nakshatra", "")
        old_nak = self._last_p.get("nakshatra", "")
        if new_nak and new_nak != old_nak:
            changes.append(("nakshatra", old_nak, new_nak))
            self._last_p["nakshatra"] = new_nak

        # Tithi
        new_tithi = p.get("tithi", "")
        old_tithi = self._last_p.get("tithi", "")
        if new_tithi and new_tithi != old_tithi:
            changes.append(("tithi", old_tithi, new_tithi))
            self._last_p["tithi"] = new_tithi

        # Muhurta
        new_mu = mu.get("name", "")
        old_mu = self._last_p.get("muhurta", "")
        if new_mu and new_mu != old_mu:
            changes.append(("muhurta", old_mu, new_mu))
            self._last_p["muhurta"] = new_mu

        return changes

    def _dispatch(self, ctype, new_val, fs):
        if ctype == "nakshatra":
            return self._gen_nakshatra(new_val, fs)
        elif ctype == "tithi":
            return self._gen_tithi(new_val, fs)
        elif ctype == "muhurta":
            return self._gen_muhurta(new_val, fs)
        return {}

    # ── Nakshatra generation ──────────────────────

    def _gen_nakshatra(self, nak, fs):
        g = self._graph
        # Use ITRANS name_key from nak_data (reliable), fallback to slug
        nd = fs.get("panchanga", {}).get("nak_data", {}) or {}
        itrans = nd.get("name_key", "")
        nak_id = f"nakshatra_{_slug(itrans)}" if itrans else f"nakshatra_{_slug(nak)}"
        arts = {}

        # 1. Brief
        try:
            from .codex_interaction import codex_from_entity
            arts["nakshatra_brief"] = codex_from_entity(fs, nak_id, mode="brief")
        except Exception:
            arts["nakshatra_brief"] = ""

        # 2. Practice
        try:
            from .codex_interaction import codex_from_entity
            arts["practice_today"] = codex_from_entity(fs, nak_id, mode="practice")
        except Exception:
            arts["practice_today"] = ""

        # 3. Paths
        try:
            from .codex_interaction import paths_from_entity
            paths = paths_from_entity(fs, nak_id, depth=2)
            arts["nakshatra_paths"] = "\n".join(format_path(p) for p in paths[:5])
        except Exception:
            arts["nakshatra_paths"] = ""

        # 4. Sound context — nakshatra → graha → raga
        graha_edges = g.get_neighbors(nak_id, relation_types=["nakshatra_ruling_graha"])
        graha_id = graha_edges[0]["to_id"] if graha_edges else ""
        raga_edges = g.get_neighbors(graha_id, relation_types=["primary_raga"]) if graha_id else []
        arts["sound_context"] = {
            "graha": graha_id, "raga": raga_edges[0]["to_id"] if raga_edges else "",
        }

        # 5. Plant
        plant_edges = g.get_neighbors(nak_id, relation_types=["nakshatra_sacred_plant"])
        arts["plant_today"] = plant_edges[0]["to_id"] if plant_edges else ""

        # 6. Dosha
        dosha_edges = g.get_neighbors(nak_id, relation_types=["dosha"])
        arts["dosha_today"] = dosha_edges[0]["to_id"] if dosha_edges else ""

        # 7. Flows
        rels = fs.get("active_relations", [])
        try:
            flows = detect_flows(rels, nak_id, top_n=3) if rels else []
            arts["flows_today"] = [f.get("text", "") for f in flows]
        except Exception:
            arts["flows_today"] = []

        # 8. Card spread
        arts["card_spread"] = self._gen_card_spread(nak_id, fs)

        # 9. Mandala
        arts["mandala_layout"] = self._gen_mandala(nak_id, fs)

        # 10. Tala pattern
        arts["tala_pattern"] = self._gen_tala(fs)

        return arts

    def _gen_tithi(self, tithi, fs):
        p = fs.get("panchanga", {})
        devi = p.get("devi", [])
        devi_name = devi[0] if isinstance(devi, list) and devi else ""
        arts = {}
        if devi_name:
            try:
                from .codex_interaction import codex_from_entity
                devi_id = f"deity_{_slug(devi_name)}"
                arts["devi_brief"] = codex_from_entity(fs, devi_id, mode="brief")
            except Exception:
                pass
        return arts

    def _gen_muhurta(self, muhurta, fs):
        AUSPICIOUS = ["Abhijit", "Brahma", "Vijaya"]
        is_ausp = any(a.lower() in (muhurta or "").lower() for a in AUSPICIOUS)
        return {"muhurta_alert": f"{'✦' if is_ausp else '○'} {muhurta}"}

    # ── Card spread ───────────────────────────────

    def _gen_card_spread(self, entity_id, fs):
        g = self._graph
        cards = []

        # Center
        meta = g.meta(entity_id)
        cards.append({
            "position": "center", "angle": 0, "entity_id": entity_id,
            "name": (meta.get("aliases") or [entity_id])[0] if meta.get("aliases") else entity_id.replace("_", " "),
            "relation": "self",
            "element": _first_attr(meta, "element", "ether"),
            "s_layer": entity_layer(entity_id) or "S3",
        })

        POSITIONS = [
            ("above", 90, ["nakshatra_associated_deity"]),
            ("right", 0, ["nakshatra_ruling_graha"]),
            ("below", 270, ["element", "dosha"]),
            ("left", 180, ["primary_raga"]),
            ("ne", 45, ["body_region"]),
            ("se", 315, ["nakshatra_sacred_plant"]),
            ("sw", 225, ["therapeutic_target"]),
            ("nw", 135, ["bija"]),
        ]

        for pos_name, angle, rel_types in POSITIONS:
            edges = g.get_neighbors(entity_id, relation_types=rel_types)
            if not edges:
                # Try via graha (for raga, bija, ratna)
                graha = g.get_neighbors(entity_id, relation_types=["nakshatra_ruling_graha"])
                if graha:
                    edges = g.get_neighbors(graha[0]["to_id"], relation_types=rel_types)
            if edges:
                e = edges[0]
                to_meta = g.meta(e["to_id"])
                name = (to_meta.get("aliases") or [e["to_id"]])[0] if to_meta.get("aliases") else e["to_id"].replace("_", " ")
                cards.append({
                    "position": pos_name, "angle": angle,
                    "entity_id": e["to_id"], "name": name,
                    "relation": e.get("relation", ""),
                    "element": _first_attr(to_meta, "element", "ether"),
                    "s_layer": entity_layer(e["to_id"]) or "S1",
                })

        return cards

    # ── Mandala ───────────────────────────────────

    def _gen_mandala(self, entity_id, fs):
        g = self._graph
        p = fs.get("panchanga", {})
        ss = fs.get("sound_state", {})
        rings = [[], [], [], [], []]

        # Ring 0 — center
        meta = g.meta(entity_id)
        rings[0].append({
            "entity_id": entity_id,
            "name": (meta.get("aliases") or [entity_id])[0] if meta.get("aliases") else entity_id.replace("_", " "),
            "angle": 0, "ring": 0, "size": 1.0,
            "element": _first_attr(meta, "element", "ether"),
            "active": True, "relation": "center",
        })

        # Ring 1 — direct neighbors
        neighbors = g.get_neighbors(entity_id, exclude_inverse=True)
        for i, e in enumerate(neighbors[:8]):
            to_meta = g.meta(e["to_id"])
            rings[1].append({
                "entity_id": e["to_id"],
                "name": (to_meta.get("aliases") or [e["to_id"]])[0] if to_meta.get("aliases") else e["to_id"].split("_")[-1],
                "angle": (i / max(len(neighbors[:8]), 1)) * 360,
                "ring": 1, "size": 0.8,
                "element": _first_attr(to_meta, "element", "ether"),
                "active": True, "relation": e.get("relation", ""),
            })

        # Ring 2 — depth-2 expansion
        expanded = g.expand_from_entities([entity_id], depth=2, max_per_node=8)
        hop2 = [e for e in expanded if e.get("hop") == 2]
        seen = {entity_id} | {e["to_id"] for e in neighbors[:8]}
        for i, e in enumerate(hop2):
            if e["to_id"] in seen:
                continue
            seen.add(e["to_id"])
            to_meta = g.meta(e["to_id"])
            rings[2].append({
                "entity_id": e["to_id"],
                "name": e["to_id"].split("_")[-1],
                "angle": (len(rings[2]) / 12) * 360,
                "ring": 2, "size": 0.6,
                "element": _first_attr(to_meta, "element", "ether"),
                "active": False, "relation": e.get("relation", ""),
            })
            if len(rings[2]) >= 12:
                break

        # Ring 3 — tala beats
        tala = ss.get("tala", "Adi")
        bols = TALA_BOLS.get(tala, TALA_BOLS.get("Adi", []))
        for i, bol in enumerate(bols):
            rings[3].append({
                "entity_id": f"beat:{i}", "name": bol,
                "angle": (i / max(len(bols), 1)) * 360,
                "ring": 3, "size": 1.0 if i == 0 else 0.5,
                "element": "fire" if i == 0 else "air",
                "active": False, "relation": "tala_beat",
            })

        # Ring 4 — 27 nakshatras
        current = p.get("nakshatra", "")
        from .datasets import load_entity_metadata
        metadata = load_entity_metadata()
        nak_ids = sorted([k for k in metadata if k.startswith("nakshatra_") and "pada" not in k])[:27]
        for i, nid in enumerate(nak_ids):
            nm = metadata[nid]
            name = (nm.get("aliases") or [nid])[0] if nm.get("aliases") else nid.replace("nakshatra_", "")
            rings[4].append({
                "entity_id": nid, "name": name,
                "angle": (i / 27) * 360,
                "ring": 4, "size": 0.4,
                "element": _first_attr(nm, "element", "ether"),
                "active": _slug(current) in nid,
                "relation": "nakshatra_wheel",
            })

        return {"rings": rings, "entity": entity_id}

    # ── Tala pattern ──────────────────────────────

    def _gen_tala(self, fs):
        ss = fs.get("sound_state", {})
        tala = ss.get("tala", "Adi")
        beats = TALA_BEATS.get(tala, 8)
        density = 0.5

        dayan = [0] * beats
        dayan[0] = 3
        if beats > 4:
            dayan[beats // 2] = 2
        if beats > 6:
            dayan[beats // 4] = 1
            dayan[beats * 3 // 4] = 1

        bayan = [0] * beats
        bayan[0] = 2
        if beats > 4:
            bayan[beats // 2] = 2

        raga_ring = [0] * 7
        raga_ring[0] = 2
        raga_ring[2] = 1
        raga_ring[4] = 1

        return {
            "tala": tala, "beats": beats, "bpm": ss.get("bpm", 72),
            "rings": [
                {"voice": "dayan", "steps": beats, "active": dayan, "phase": 0},
                {"voice": "bayan", "steps": beats, "active": bayan, "phase": 0},
                {"voice": "raga", "steps": 7, "active": raga_ring, "phase": 0, "isRaga": True},
            ],
        }

    # ── Persist ───────────────────────────────────

    def _persist(self, artifacts):
        p = Path("generated")
        p.mkdir(exist_ok=True)
        for key, val in artifacts.items():
            try:
                if isinstance(val, str):
                    (p / f"{key}.md").write_text(val, encoding="utf-8")
                elif isinstance(val, (dict, list)):
                    (p / f"{key}.json").write_text(
                        json.dumps(val, ensure_ascii=False, indent=2), encoding="utf-8")
            except Exception:
                pass


# ── Singleton ─────────────────────────────────────

_instance = None

def get_generator():
    global _instance
    if _instance is None:
        _instance = FieldGenerator()
    return _instance
