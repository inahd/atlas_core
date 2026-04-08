"""NW · Vayu · S2 — Sound engine. Raga, svara, transmission."""
from .base_engine import ZoneEngine

class SoundEngine(ZoneEngine):
    vastu_position = "NW"
    layer = "S2"
    domain = "Sound"
    deity = "Vayu"
    color = "#5cb87a"

    def get_entity(self, fs):
        s2 = self._layers(fs).get("S2", {})
        raga = s2.get("raga", "")
        return "raga_" + raga.lower().replace(" ", "_") if raga else ""

    def render_icon(self, fs):
        s2 = self._layers(fs).get("S2", {})
        return {"symbol": "♪", "color": self.color,
                "entity_id": self.get_entity(fs),
                "vastu": self.vastu_position,
                "value": s2.get("raga", "")}

    def render_zone(self, fs):
        s2 = self._layers(fs).get("S2", {})
        return {**super().render_zone(fs),
                "title": s2.get("raga", "Sound"),
                "visual_type": "raga_ring",
                "rows": [
                    {"label": "raga", "value": s2.get("raga", ""), "entity_id": self.get_entity(fs), "clickable": True, "symbol": "♪"},
                    {"label": "vadi", "value": s2.get("raga_vadi", "")},
                    {"label": "tala", "value": s2.get("tala", "")},
                ]}
