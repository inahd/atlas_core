"""
base_engine.py — Base class for vastu zone engines.

Each zone engine owns its domain. It knows:
  - which entity is primary right now
  - how to render its icon for the center
  - how to render its full zone data
  - how to produce its SVG visual

The shell renders what engines produce. Nothing hardcoded.
"""

from typing import Any, Dict, Optional


# Vastu angles for icon positioning on center zone border
VASTU_ANGLES = {
    "NW": 315, "N": 0, "NE": 45,
    "W": 270, "C": None, "E": 90,
    "SW": 225, "S": 180, "SE": 135,
}


class ZoneEngine:
    """Base class for all zone engines."""

    vastu_position: str = ""   # NW, N, NE, W, C, E, SW, S, SE
    layer: str = ""            # S0-S6
    domain: str = ""           # sound, rhythm, archetype etc
    deity: str = ""            # Vayu, Kubera, Ishana etc
    color: str = "#ffffff"     # zone accent color

    def get_entity(self, field_state: dict) -> str:
        """Primary entity_id for this zone right now."""
        raise NotImplementedError

    def render_icon(self, field_state: dict) -> dict:
        """Small contribution to center field.
        Returns: {symbol, color, entity_id, vastu}"""
        eid = self.get_entity(field_state)
        return {
            "symbol": "◉",
            "color": self.color,
            "entity_id": eid,
            "vastu": self.vastu_position,
        }

    def render_zone(self, field_state: dict) -> dict:
        """Full zone data for /shell/state.
        Override in subclasses for domain-specific rendering."""
        return {
            "deity": self.deity,
            "domain": self.domain,
            "layer_ref": self.layer,
            "title": self.domain,
        }

    def render_visual(self, field_state: dict) -> Optional[str]:
        """SVG string for this zone's visual. Override in subclasses."""
        return None

    def _layers(self, fs: dict) -> dict:
        return fs.get("layers", {})

    def _panchanga(self, fs: dict) -> dict:
        return fs.get("panchanga", {})

    def _sound(self, fs: dict) -> dict:
        return fs.get("sound_state", {}) or self._layers(fs).get("S2", {})
