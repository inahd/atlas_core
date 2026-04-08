"""W · Varuna · S5 — Ecology engine. Plant, herb, dissolution, depth."""
from .base_engine import ZoneEngine

class EcologyEngine(ZoneEngine):
    vastu_position = "W"
    layer = "S5"
    domain = "Ecology"
    deity = "Varuna"
    color = "#4da8a0"

    def get_entity(self, fs):
        s5 = self._layers(fs).get("S5", {})
        plant = s5.get("nakshatra_plant", "")
        return "plant_" + plant.lower().replace(" ", "_") if plant else ""

    def render_icon(self, fs):
        s5 = self._layers(fs).get("S5", {})
        return {"symbol": "❧", "color": self.color,
                "entity_id": self.get_entity(fs),
                "vastu": self.vastu_position,
                "value": s5.get("nakshatra_plant", "")}

    def render_zone(self, fs):
        s5 = self._layers(fs).get("S5", {})
        return {**super().render_zone(fs),
                "title": s5.get("nakshatra_plant", "") or "Ecology",
                "visual_type": "plant_form",
                "rows": [
                    {"label": "plant", "value": s5.get("nakshatra_plant", ""), "entity_id": self.get_entity(fs), "clickable": True, "symbol": "❧"},
                    {"label": "element", "value": s5.get("element", "")},
                    {"label": "dosha", "value": s5.get("dosha", "")},
                ]}
