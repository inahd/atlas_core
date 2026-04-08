"""SE · Agni · S6 — Action engine. Ritual, craft, transformation, practice."""
from .base_engine import ZoneEngine

class ActionEngine(ZoneEngine):
    vastu_position = "SE"
    layer = "S6"
    domain = "Action"
    deity = "Agni"
    color = "#f0b060"

    def get_entity(self, fs):
        return ""  # action doesn't have a single entity

    def render_icon(self, fs):
        s6 = self._layers(fs).get("S6", {})
        return {"symbol": "🔥", "color": self.color,
                "entity_id": "",
                "vastu": self.vastu_position,
                "value": s6.get("practice", "")}

    def render_zone(self, fs):
        s6 = self._layers(fs).get("S6", {})
        return {**super().render_zone(fs),
                "title": "Action",
                "visual_type": "vara_arc",
                "rows": [
                    {"label": "practice", "value": s6.get("practice", "")},
                    {"label": "art", "value": s6.get("art", "")},
                ],
                "apps": [{"name": "yantra", "url": "/devi/yantra"}]}
