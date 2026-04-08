"""
field_state.py — Unified FieldState spine for the Atlas NPU system.

Every downstream module consumes this single object.
No module may derive state independently.

Pipeline:
  panchanga → θ,φ → field_query → relation expansion → rerank
           → geometry → lifecycle → psi/modulation → expression
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple


@dataclass
class FieldState:
    """Complete snapshot of the NPU field at one moment."""

    # ── Input ─────────────────────────────────────────────────
    panchanga: Dict[str, Any]

    # ── Toroidal coordinates (2-axis only: θ=time, φ=quality) ─
    theta: float
    phi: float

    # ── Entities sorted by composite coherence ────────────────
    # Each dict: {entity_id, score, composite_score, geometric_score,
    #   relational_score, authority_weight, semantic_mod, theta, phi,
    #   element, guna, name, attestation}
    entities: List[Dict[str, Any]]

    # ── Active relations among coherent entities ──────────────
    # Each: {from_id, to_id, relation, confidence, attestation, mutual, hop}
    active_relations: List[Dict[str, Any]] = field(default_factory=list)

    # ── Sacred geometry ───────────────────────────────────────
    formations: List[Dict[str, Any]] = field(default_factory=list)
    vastu_grid: Dict[str, Tuple[float, float, str]] = field(default_factory=dict)

    # ── Vāstu S4 state (from vastu_engine, deterministic) ────
    vastu_state: Dict[str, Any] = field(default_factory=dict)

    # ── UI layout (from ui_vastu_engine, interface projection) ─
    ui_layout: Dict[str, Any] = field(default_factory=dict)

    # ── Lifecycle ─────────────────────────────────────────────
    # {phase, intensity, stability, strongest_formation, formation_count}
    lifecycle: Dict[str, Any] = field(default_factory=dict)

    # ── Cycle position ────────────────────────────────────────
    arc_phase: float = 0.0

    # ── ψ expression axis (downstream, never touches θ/φ) ────
    psi: Dict[str, float] = field(default_factory=lambda: {
        "intensity": 0.5, "focus": 0.5, "stability": 0.5,
    })

    # ── Modulation (cluster/embedding, never overrides canon) ─
    modulation: Dict[str, float] = field(default_factory=dict)

    # ── Helpers ───────────────────────────────────────────────

    def dominant_element(self) -> str:
        top = self.entities[:5]
        if not top:
            return "ether"
        elements = [e.get("element", "ether") for e in top]
        return max(set(elements), key=elements.count)

    def dominant_guna(self) -> str:
        top = self.entities[:5]
        if not top:
            return "sattva"
        gunas = [e.get("guna", "sattva") for e in top]
        return max(set(gunas), key=gunas.count)

    def top_entity_id(self) -> str:
        if self.entities:
            return self.entities[0].get("entity_id", "")
        return ""

    def avg_coherence(self, n: int = 5) -> float:
        top = self.entities[:n]
        if not top:
            return 0.0
        return sum(e.get("composite_score", e.get("score", 0.0)) for e in top) / len(top)

    def summary(self) -> str:
        nak = self.panchanga.get("nakshatra", "?")
        n_ent = len(self.entities)
        n_rel = len(self.active_relations)
        n_form = len(self.formations)
        top = self.top_entity_id() or "none"
        el = self.dominant_element()
        phase = self.lifecycle.get("phase", "?")
        psi_s = "/".join(f"{v:.2f}" for v in self.psi.values())
        return (f"θ={self.theta:.3f} φ={self.phi:.3f} "
                f"nak={nak} ent={n_ent} rel={n_rel} form={n_form} "
                f"top={top} elem={el} phase={phase} "
                f"arc={self.arc_phase:.3f} ψ={psi_s}")
