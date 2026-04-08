"""E · Indra · S6 — Codex engine. Perception, text, study, cognition."""
from .base_engine import ZoneEngine

class CodexEngine(ZoneEngine):
    vastu_position = "E"
    layer = "S6"
    domain = "Codex"
    deity = "Indra"
    color = "#d44040"

    def get_entity(self, fs):
        return ""  # codex doesn't have a single primary entity

    def render_icon(self, fs):
        s6 = self._layers(fs).get("S6", {})
        return {"symbol": "📜", "color": self.color,
                "entity_id": "",
                "vastu": self.vastu_position,
                "value": s6.get("practice", "")}

    def render_zone(self, fs):
        s6 = self._layers(fs).get("S6", {})
        return {**super().render_zone(fs),
                "title": "Codex",
                "rows": [
                    {"label": "practice", "value": s6.get("practice", "")},
                    {"label": "codex_mode", "value": s6.get("codex_mode", "")},
                    {"label": "companion", "value": s6.get("companion", "")},
                ],
                "apps": [{"name": "codex", "url": "/codex"}, {"name": "bandhu", "url": "/bandhu"}]}
