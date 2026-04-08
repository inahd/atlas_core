#!/usr/bin/env python3
import csv
import json
import logging
import os
import re
import time
from pathlib import Path
from dataclasses import dataclass, field as dc_field
from typing import Dict, List

log = logging.getLogger("coherence_engine")

# ── weights (env-configurable) ─────────────────────────────
_RULE_W = float(os.environ.get("ATLAS_RULE_WEIGHT", "0.5"))
RULE_WEIGHT = max(0.0, min(1.0, _RULE_W))
SEMANTIC_WEIGHT = 1.0 - RULE_WEIGHT

# max possible rule score from score_batch logic: 4+4+2+3 = 13
_MAX_RULE_SCORE = 13.0

# Category weights — cosmological entities boosted, herb catalogues penalized
_CAT_W = {
    "nakshatra": 1.5, "graha": 1.4, "deity": 1.4,
    "tithi": 1.3, "devi": 1.3, "vara": 1.2,
    "raga": 1.3, "tala": 1.2, "svara": 1.2, "bija": 1.2,
    "plant": 1.0, "dosha": 1.0, "element": 1.0, "marma": 0.9,
    "mythic": 0.6, "jyotish": 0.5,
    "amidha": 0.3, "herb": 0.3,
}

def _cat_w(candidate: str) -> float:
    c = candidate.lower()
    if "amidha" in c: return 0.3
    if "herb_spine" in c: return 0.3
    if c.startswith("jyotish"): return 0.5
    if c.startswith("mythic"): return 0.6
    for prefix, w in _CAT_W.items():
        if c.startswith(prefix): return w
    return 0.8

# ── paths ───────────────────────────────────────────────────
_CORE_ROOT = Path(__file__).resolve().parent
_APP_ROOT = _CORE_ROOT.parent
_CACHE_DIR = _APP_ROOT / "data" / "coherence_cache"


@dataclass
class CoherenceScore:
    candidate: str
    score: float
    reasons: list
    node_class: str = "resonance"
    field: dict = dc_field(default_factory=dict)

class CoherenceEngine:
    def __init__(self, data_path):
        self.data_path = Path(data_path)
        self.load_data()
    
    @staticmethod
    def load_csv(filename):
        with open(filename) as f:
            return list(csv.DictReader(f))
    
    def load_data(self):
        base = self.data_path / 'cosmology'
        astro = self.data_path / 'astro'
        plants = self.data_path / 'plants'
        self.tithis = self.load_csv(astro / 'tithi_deities.csv')
        self.tithi_props = self.load_csv(astro / 'tithi_properties.csv')
        self.grahas = self.load_csv(base / 'graha_master.csv')
        self.plants = self.load_csv(plants / 'sacred_plants.csv')
    
    def get_tithi_constraints(self, tithi_num):
        if tithi_num < 1 or tithi_num > len(self.tithi_props):
            return None
        props = self.tithi_props[tithi_num - 1]
        return {
            'tithi_name': props['tithi'],
            'tithi_element': props['element'],
            'tithi_guna': props['guna'],
            'tithi_dosha': props['dosha']
        }
    
    def score_batch(self, tithi_num, limit=10):
        constraints = self.get_tithi_constraints(tithi_num)
        if not constraints:
            return []
        
        results = []
        for plant in self.plants:
            for graha in self.grahas:
                score = 0
                reasons = []
                
                t_e = constraints['tithi_element']
                p_e = plant['element']
                g_e = graha['element']
                
                if p_e == t_e: score += 4; reasons.append("resonance")
                if p_e == g_e: score += 4; reasons.append("chain")
                if graha['guna'] == constraints['tithi_guna']: score += 2; reasons.append("guna")
                if graha['dosha'] != constraints['tithi_dosha']: score += 3; reasons.append("balance")
                
                results.append(CoherenceScore(
                    f"{plant['plant']} + {graha['graha']}",
                    score,
                    reasons
                ))
        
        return sorted(results, key=lambda x: x.score, reverse=True)[:limit]

    # ── hybrid scoring ──────────────────────────────────────

    @staticmethod
    def classify_node(score_float):
        """Map a 0-1 score to a coherence class."""
        if score_float >= 0.75:
            return "coherence"
        if score_float >= 0.50:
            return "resonance"
        if score_float >= 0.25:
            return "void"
        return "rift"

    def _tithi_context_text(self, tithi_num, fs=None):
        """Build a semantic context string for the current tithi."""
        constraints = self.get_tithi_constraints(tithi_num)
        if not constraints:
            return ""
        name = constraints["tithi_name"]
        element = constraints["tithi_element"]
        guna = constraints["tithi_guna"]
        dosha = constraints["tithi_dosha"]
        # devi from tithi_deities
        devi = ""
        if tithi_num <= len(self.tithis):
            devi = self.tithis[tithi_num - 1].get("deity", "")
        return f"{name} · {element} · {guna} · {dosha} · {devi}"

    @staticmethod
    def _slug(value: str) -> str:
        value = (value or "").strip().lower()
        value = value.replace("ṛ", "r").replace("ś", "s").replace("ṣ", "s").replace("ṅ", "n")
        value = value.replace("ñ", "n").replace("ṭ", "t").replace("ḍ", "d").replace("ṃ", "m")
        value = re.sub(r"[^a-z0-9]+", "_", value).strip("_")
        return value

    @staticmethod
    def _graha_key(name: str) -> str:
        aliases = {
            "sun": "surya",
            "surya": "surya",
            "moon": "chandra",
            "chandra": "chandra",
            "candra": "chandra",
            "mars": "mangala",
            "mangala": "mangala",
            "mercury": "budha",
            "budha": "budha",
            "jupiter": "guru",
            "guru": "guru",
            "brihaspati": "guru",
            "venus": "shukra",
            "shukra": "shukra",
            "saturn": "shani",
            "shani": "shani",
            "rahu": "rahu",
            "ketu": "ketu",
        }
        key = CoherenceEngine._slug(name)
        return aliases.get(key, key)

    def _read_cache(self, tithi_num, nakshatra):
        """Read cached hybrid scores if nakshatra matches."""
        cache_file = _CACHE_DIR / f"{tithi_num}_{nakshatra}.json"
        if not cache_file.exists():
            return None
        try:
            data = json.loads(cache_file.read_text())
            if data.get("nakshatra") == nakshatra:
                return data.get("scores")
        except Exception:
            pass
        return None

    def _write_cache(self, tithi_num, nakshatra, scores_data):
        """Write hybrid scores to cache."""
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_file = _CACHE_DIR / f"{tithi_num}_{nakshatra}.json"
        payload = {
            "tithi_num": tithi_num,
            "nakshatra": nakshatra,
            "created": time.time(),
            "scores": scores_data,
        }
        try:
            cache_file.write_text(json.dumps(payload, default=str))
        except Exception as exc:
            log.warning("cache write failed: %s", exc)

    def score_hybrid(self, tithi_num, limit=10, fs=None):
        """Hybrid vector+rule scoring.

        score = (rule_score * RULE_WEIGHT) + (semantic_score * SEMANTIC_WEIGHT)

        Falls back to pure rule scoring if vector store is unavailable.
        """
        # get field state for context
        if fs is None:
            try:
                import kernel
                fs = kernel.field_state()
            except Exception:
                fs = {}

        nakshatra = fs.get("panchanga", {}).get("nakshatra", "unknown")

        # check cache
        cached = self._read_cache(tithi_num, nakshatra)
        if cached is not None:
            results = [
                CoherenceScore(
                    candidate=s["candidate"],
                    score=s["score"],
                    reasons=s["reasons"],
                    node_class=s.get("node_class", "resonance"),
                    field=s.get("field", {}),
                )
                for s in cached[:limit]
            ]
            return results

        # rule scores (existing logic)
        rule_results = self.score_batch(tithi_num, limit=99999)  # get all

        # semantic retrieval over Atlas sources (wiki/datasets/PDFs)
        context_text = self._tithi_context_text(tithi_num, fs=fs)
        query = f"{context_text} · {nakshatra}".strip(" ·")
        semantic_hits: List[dict] = []
        semantic_by_entity: Dict[str, float] = {}
        try:
            from npu_engine.vector_store import get_vector_store
            store = get_vector_store()
            semantic_hits = store.search(query, n=50)
            for hit in semantic_hits:
                eid = str(hit.get("entity_id", "") or "")
                try:
                    score = float(hit.get("score", 0.0) or 0.0)
                except Exception:
                    score = 0.0
                if eid:
                    semantic_by_entity[eid] = max(semantic_by_entity.get(eid, 0.0), score)
        except Exception as exc:
            log.warning("vector store unavailable — falling back to pure rule scoring: %s", exc)
            semantic_hits = []
            semantic_by_entity = {}

        field_snap = {
            "tithi_num": tithi_num,
            "nakshatra": nakshatra,
            "context": query,
            "mode": "hybrid" if semantic_hits else "rule_only",
            "rule_weight": RULE_WEIGHT,
            "semantic_weight": SEMANTIC_WEIGHT,
        }

        hybrid_results = []
        for r in rule_results:
            rule_norm = r.score / _MAX_RULE_SCORE

            # Find best semantic match for this candidate.
            # Candidate format: "plant + graha" (strings from datasets).
            sem_score = 0.0
            parts = [p.strip() for p in r.candidate.split(" + ") if p.strip()]
            if parts:
                plant_name = parts[0]
                plant_id = f"plant_{self._slug(plant_name)}"
                sem_score = max(sem_score, semantic_by_entity.get(plant_id, 0.0))
            if len(parts) > 1:
                graha_name = parts[1]
                graha_id = f"graha_{self._graha_key(graha_name)}"
                sem_score = max(sem_score, semantic_by_entity.get(graha_id, 0.0))
            if sem_score == 0.0 and semantic_hits and parts:
                # Last-resort: substring match against returned snippets.
                for hit in semantic_hits:
                    htext = str(hit.get("text", "")).lower()
                    if any(p.lower() in htext for p in parts):
                        try:
                            sem_score = max(sem_score, float(hit.get("score", 0.0) or 0.0))
                        except Exception:
                            pass
            hybrid = (rule_norm * RULE_WEIGHT) + (sem_score * SEMANTIC_WEIGHT)

            r.score = round(hybrid, 6)
            r.node_class = self.classify_node(hybrid)
            r.field = field_snap
            hybrid_results.append(r)

        # Apply category weights
        for r in hybrid_results:
            r.score = round(r.score * _cat_w(r.candidate), 6)
        hybrid_results.sort(key=lambda x: x.score, reverse=True)

        # cache results
        cache_data = [
            {
                "candidate": r.candidate,
                "score": r.score,
                "reasons": r.reasons,
                "node_class": r.node_class,
                "field": r.field,
            }
            for r in hybrid_results
        ]
        self._write_cache(tithi_num, nakshatra, cache_data)

        return hybrid_results[:limit]


if __name__ == '__main__':
    engine = CoherenceEngine(Path.home() / 'atlas_330' / 'datasets')
    print("COHERENCE ENGINE — All Tithis\n")
    for tithi_num in range(1, 16):
        constraints = engine.get_tithi_constraints(tithi_num)
        results = engine.score_batch(tithi_num, limit=1)
        print(f"Tithi {tithi_num:2d} ({constraints['tithi_name']:12}): ", end="")
        if results:
            print(f"{results[0].candidate} ({results[0].score:.0f})")
