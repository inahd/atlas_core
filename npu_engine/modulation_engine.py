"""
modulation_engine.py — Bounded embedding modulation for the NPU.

This is where embeddings live safely. They NEVER overwrite canon:
  - Cannot introduce canonical relations
  - Cannot replace graph authority
  - Can only modulate near-ties (±0.05 max on composite score)
  - Can inform study-path hints and retrieval ranking

Provenance: anything derived here is labeled SYNTHESIS or INTERPRETATION.
"""

import math
from typing import Any, Dict, List, Optional


def semantic_modulation(entity_ids: List[str],
                        query_context: str = "",
                        vector_store=None) -> Dict[str, float]:
    """Compute bounded semantic affinity scores for entities.

    Uses vector_store (BM25/embeddings) if available.
    Returns {entity_id: 0..1} — raw affinity, not final score.
    The coherence engine maps this to ±0.05 modulation.

    If vector_store is None, returns empty dict (no modulation).
    """
    if vector_store is None or not entity_ids or not query_context:
        return {}

    try:
        results = vector_store.search(query_context, n=50)
    except Exception:
        return {}

    # Build affinity map from search results
    affinity = {}
    if not results:
        return affinity

    top_score = max(r.get("score", 0.0) for r in results) or 1.0

    for result in results:
        eid = result.get("entity_id", "")
        if eid and eid in set(entity_ids):
            # Normalize to 0..1 relative to top result
            raw = result.get("score", 0.0) / top_score
            affinity[eid] = round(max(0.0, min(1.0, raw)), 4)

    return affinity


def derive_psi(entities: List[Dict],
               arc_phase: float,
               formations: List[Dict]) -> Dict[str, float]:
    """Derive ψ expression axis from downstream field structure.

    ψ is NOT geometric. It reads field RESULTS and derives expression hints.
    All values bounded 0..1.

    Returns: {"intensity": .., "focus": .., "stability": ..}
    """
    intensity = 0.5
    focus = 0.5
    stability = 0.5

    # intensity: from coherence concentration + formation strength
    if entities:
        top_scores = [e.get("composite_score", e.get("score", 0.0))
                      for e in entities[:8]]
        intensity = sum(top_scores) / len(top_scores)

    if formations:
        best_sym = max(f.get("symmetry_score", 0.0) for f in formations)
        intensity = intensity * 0.7 + best_sym * 0.3

    # focus: score concentration (sharp peak = high focus)
    if len(entities) >= 6:
        top3 = [e.get("composite_score", e.get("score", 0.0))
                for e in entities[:3]]
        tail3 = [e.get("composite_score", e.get("score", 0.0))
                 for e in entities[-3:]]
        spread = (sum(top3) / 3) - (sum(tail3) / 3)
        focus = min(1.0, spread * 2)
    elif entities:
        focus = 0.8

    # stability: from arc_phase lifecycle position
    arc = max(0.0, min(1.0, arc_phase))
    if 0.2 <= arc <= 0.6:
        stability = 0.7 + 0.3 * (1.0 - abs(arc - 0.4) / 0.2)
    elif arc < 0.2:
        stability = 0.3 + arc * 2.0
    else:
        stability = max(0.1, 1.0 - (arc - 0.6) * 2.5)

    return {
        "intensity": round(max(0.0, min(1.0, intensity)), 4),
        "focus": round(max(0.0, min(1.0, focus)), 4),
        "stability": round(max(0.0, min(1.0, stability)), 4),
    }
