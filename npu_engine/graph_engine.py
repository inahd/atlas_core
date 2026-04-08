"""
graph_engine.py — Canonical relation graph for the NPU.

Wraps datasets.load_relations() and load_entity_metadata() into
a query-able graph with neighbor expansion, chain scoring, and
provenance tracking.

Embeddings are NOT used here. This is canon-only.
"""

from collections import defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple

from .datasets import load_relations, load_entity_metadata


class GraphEngine:
    """Canonical relation graph — truth layer, not inference."""

    def __init__(self):
        self._relations = load_relations()      # {entity_id: [edges]}
        self._metadata = load_entity_metadata()  # {entity_id: meta}

    @property
    def node_count(self) -> int:
        return len(self._metadata)

    @property
    def edge_count(self) -> int:
        return sum(len(v) for v in self._relations.values())

    def meta(self, entity_id: str) -> Dict[str, Any]:
        """Return metadata for an entity, or empty dict."""
        return self._metadata.get(entity_id, {})

    def has_relations(self, entity_id: str) -> bool:
        return entity_id in self._relations

    def get_neighbors(self, entity_id: str,
                      relation_types: Optional[List[str]] = None,
                      exclude_inverse: bool = True) -> List[Dict[str, Any]]:
        """Return direct neighbors of an entity.

        Each result: {to_id, relation, confidence, authority, source_file, inverse}
        """
        edges = self._relations.get(entity_id, [])
        results = []
        for edge in edges:
            if exclude_inverse and edge.get("inverse"):
                continue
            if relation_types and edge.get("relation") not in relation_types:
                continue
            results.append(edge)
        return results

    def expand_from_entities(self, entity_ids: List[str],
                             depth: int = 1,
                             max_per_node: int = 10) -> List[Dict[str, Any]]:
        """Expand relational neighborhood from a set of seed entities.

        Returns deduplicated edges up to `depth` hops.
        Deeper hops inherit decayed provenance.
        """
        seen_edges: Set[Tuple[str, str, str]] = set()
        results = []
        frontier = list(entity_ids)

        for hop in range(depth):
            next_frontier = []
            for eid in frontier:
                for edge in self.get_neighbors(eid, exclude_inverse=True):
                    key = (edge["from_id"], edge["relation"], edge["to_id"])
                    if key in seen_edges:
                        continue
                    seen_edges.add(key)

                    enriched = dict(edge)
                    enriched["hop"] = hop + 1
                    # Confidence decays with hop distance
                    base_conf = _safe_float(edge.get("confidence"), 0.8)
                    enriched["confidence"] = round(base_conf * (0.8 ** hop), 4)
                    enriched["attestation"] = _classify_authority(edge)
                    results.append(enriched)

                    next_frontier.append(edge["to_id"])

                    if len(results) >= max_per_node * len(entity_ids):
                        break

            frontier = next_frontier[:200]  # bound expansion

        return results

    def score_relations(self, seed_ids: List[str],
                        expanded: List[Dict],
                        coherence_scores: Optional[Dict[str, float]] = None
                        ) -> List[Dict[str, Any]]:
        """Score expanded relations by support from coherent seeds.

        Scoring:
          - Direct canonical edge from a seed: base weight
          - Edge endpoint is also coherent: boosted
          - Repeated support from multiple seeds: boosted
          - Decay by hop distance

        Returns sorted list of scored relation edges.
        """
        scores = coherence_scores or {}
        seed_set = set(seed_ids)

        # Count how many seeds support each target
        target_support: Dict[str, float] = defaultdict(float)

        for edge in expanded:
            from_id = edge["from_id"]
            to_id = edge["to_id"]
            conf = edge.get("confidence", 0.5)
            hop = edge.get("hop", 1)

            # Base relation weight
            weight = conf

            # Boost if from_id is a coherent seed
            if from_id in seed_set:
                weight *= 1.3

            # Boost if to_id is itself coherent
            if to_id in scores:
                weight *= (0.8 + 0.4 * scores[to_id])

            target_support[to_id] += weight
            edge["_score"] = round(weight, 4)

        # Sort by accumulated score
        expanded.sort(key=lambda e: e.get("_score", 0), reverse=True)
        return expanded

    def coherent_paths(self, entity_id: str,
                       depth: int = 2,
                       max_paths: int = 8) -> List[List[Dict]]:
        """Find short relation paths from an entity.

        Returns list of paths, each path is [edge1, edge2, ...].
        """
        paths = []
        for edge1 in self.get_neighbors(entity_id, exclude_inverse=True):
            path = [edge1]
            if depth >= 2:
                for edge2 in self.get_neighbors(edge1["to_id"], exclude_inverse=True)[:5]:
                    if edge2["to_id"] != entity_id:  # no trivial loops
                        paths.append([edge1, edge2])
            else:
                paths.append(path)
            if len(paths) >= max_paths:
                break
        return paths

    # ── Soundspec: graph-computed sound parameters ─────────

    _soundspec_cache: Dict[str, Any] = {}
    _soundspec_key: str = ""

    def get_soundspec(self, field_state: dict = None) -> Dict[str, Any]:
        """Return the soundspec_current node — recomputes if field changed.

        The graph computes sound parameters by traversal:
          nakshatra → graha → raga (graha_raga)
          tithi → nitya_devi → bija (devi_bija)
          element → sa_hz
          guna → character
          bija → varna path (formant data)

        Returns soundspec dict. Cached until field_state changes.
        """
        if field_state is None:
            return self._soundspec_cache or {}

        p = field_state.get("panchanga", {})
        # Cache key: nakshatra + tidx (changes = recompute)
        key = f"{p.get('nakshatra','')}__{p.get('tidx',0)}"
        if key == self._soundspec_key and self._soundspec_cache:
            return self._soundspec_cache

        from .field_to_sound import field_to_sound, _slugify
        spec = field_to_sound(field_state)

        # Store as a virtual entity in the graph
        sid = "soundspec_current"
        self._metadata[sid] = {
            "category": "soundspec",
            "name": "Current Sound Specification",
            "aliases": [],
            "sources": ["field_to_sound"],
            "authorities": ["derived"],
            "attributes": {
                "sa_hz": [str(spec["sa_hz"])],
                "raga": [spec["raga"]],
                "bija": [spec["bija"]],
                "element": [spec["element"]],
                "guna": [spec["guna"]],
                "register": [spec["character"]["register"]],
                "breathiness": [str(spec["character"]["breathiness"])],
                "brightness": [str(spec["character"]["brightness"])],
                "vibrato": [str(spec["character"]["vibrato"])],
            },
        }

        # Create edges from soundspec to its sources
        edges = []
        for rel, tid in [("soundspec_graha", spec["graha"]),
                         ("soundspec_raga", spec["raga"]),
                         ("soundspec_devi", spec["devi"]),
                         ("soundspec_chakra", spec["chakra"]),
                         ("soundspec_nakshatra", spec["nakshatra"])]:
            if tid:
                edge = {"from_id": sid, "to_id": tid, "relation": rel,
                        "source_file": "field_to_sound", "confidence": "derived",
                        "authority": "derived"}
                edges.append(edge)
        self._relations[sid] = edges

        spec["id"] = sid
        spec["bija_path"] = spec.get("bija_path", [])
        self._soundspec_cache = spec
        self._soundspec_key = key
        return spec

    def authority_weight(self, entity_id: str) -> float:
        """Return authority weight 0..1 for an entity.

        Based on source quality:
          canonical/observed datasets → high
          traditional texts → medium
          inference/synthesis → low
        """
        meta = self.meta(entity_id)
        authorities = meta.get("authorities", [])
        sources = meta.get("sources", [])

        if not authorities and not sources:
            return 0.3  # unknown provenance

        # Check for strong provenance markers
        all_sources = " ".join(str(s) for s in list(authorities) + list(sources)).lower()

        if any(k in all_sources for k in ("canonical", "observed", "core", "master")):
            return 0.95
        if any(k in all_sources for k in ("traditional", "sangita", "natyashastra", "jyotisha")):
            return 0.8
        if any(k in all_sources for k in ("inference", "auto", "synthesis")):
            return 0.4

        return 0.6  # default: attested but unclassified


def _safe_float(val, default: float) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def _classify_authority(edge: Dict) -> str:
    """Classify edge attestation from its metadata."""
    auth = str(edge.get("authority", "")).lower()
    conf = _safe_float(edge.get("confidence"), 0.5)

    if conf >= 0.9 or "canonical" in auth or "observed" in auth:
        return "OBSERVED"
    if "traditional" in auth or "sangita" in auth:
        return "TRADITIONAL"
    if "synthesis" in auth or "auto" in auth:
        return "SYNTHESIS"
    if conf >= 0.7:
        return "TRADITIONAL"
    return "INTERPRETATION"
