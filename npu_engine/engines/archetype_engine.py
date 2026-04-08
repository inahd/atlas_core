"""NE · Ishana · S1 — Archetype engine. Devi, deity, mantra, sacred knowledge."""
from .base_engine import ZoneEngine

class ArchetypeEngine(ZoneEngine):
    vastu_position = "NE"
    layer = "S1"
    domain = "Archetype"
    deity = "Ishana"
    color = "#aa77dd"

    def get_entity(self, fs):
        s1 = self._layers(fs).get("S1", {})
        devi = s1.get("devi", "")
        return "devi_" + devi.lower().replace(" ", "_") if devi else ""

    def render_icon(self, fs):
        s1 = self._layers(fs).get("S1", {})
        return {"symbol": "✦", "color": self.color,
                "entity_id": self.get_entity(fs),
                "vastu": self.vastu_position,
                "value": s1.get("devi", "")}

    def render_zone(self, fs):
        s1 = self._layers(fs).get("S1", {})
        devi = s1.get("devi", "")
        deity = s1.get("deity", "")
        graha = s1.get("graha", "")
        return {**super().render_zone(fs),
                "title": devi or "Archetype",
                "visual_type": "sri_yantra",
                "rows": [
                    {"label": "devi", "value": devi, "entity_id": self.get_entity(fs), "clickable": True, "symbol": "✦"},
                    {"label": "deity", "value": deity, "entity_id": "deity_" + deity.lower().replace(" ","_") if deity else "", "clickable": bool(deity), "symbol": "✦"},
                    {"label": "graha", "value": graha, "entity_id": "graha_" + graha.lower().replace(" ","_") if graha else "", "clickable": bool(graha), "symbol": "☽"},
                ]}
