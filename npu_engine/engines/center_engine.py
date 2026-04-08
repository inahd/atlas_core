"""C · Brahma · S0 — Center engine. Assembles field from all zone engines."""
from .base_engine import ZoneEngine, VASTU_ANGLES


class CenterEngine(ZoneEngine):
    vastu_position = "C"
    layer = "S0"
    domain = "Field"
    deity = "Brahma"
    color = "#f0c040"

    def __init__(self, engines):
        self.engines = engines

    def get_entity(self, fs):
        p = self._panchanga(fs)
        nak = p.get("nakshatra", "")
        return "nakshatra_" + nak.lower().replace(" ", "_") if nak else ""

    def render_icon(self, fs):
        return {"symbol": "◉", "color": self.color,
                "entity_id": self.get_entity(fs),
                "vastu": "C", "value": "bindu"}

    def render_zone(self, fs):
        p = self._panchanga(fs)
        nak = p.get("nakshatra", "")
        tithi = p.get("tithi", "")
        vara = p.get("vara", "")
        tidx = p.get("tidx", 0)

        # Devi — handle both dict and string format
        devi = p.get("devi", "")
        if isinstance(devi, dict):
            devi_name = devi.get("name", "")
        elif isinstance(devi, (list, tuple)):
            devi_name = devi[0] if devi else ""
        else:
            devi_name = str(devi)

        # Collect icon contributions from all engines
        icons = []
        for engine in self.engines:
            try:
                icon = engine.render_icon(fs)
                icon["angle"] = VASTU_ANGLES.get(engine.vastu_position, 0)
                icon["layer"] = engine.layer
                icon["engine"] = engine.domain
                icons.append(icon)
            except Exception:
                pass

        return {
            "deity": self.deity,
            "domain": self.domain,
            "layer_ref": self.layer,
            "title": nak,
            "title_color": "#f0c040",
            "title_size": 48,
            "hero": {
                "text": nak,
                "font": "Cormorant Garamond",
                "size": 48,
                "style": "italic",
                "color": "#f0c040",
            },
            "sub_hero": f"{tithi} \u00b7 {vara}".strip(" \u00b7 "),
            "sub_hero_color": "#c8d8f0",
            "field_signal": devi_name,
            "field_signal_color": "#8899aa",
            "moon": {
                "tidx": tidx,
                "phase": "waxing" if tidx < 15 else "waning",
                "color": "#c8a840",
                "bg_color": "#4a4020",
            },
            "icons": icons,
            "visual_type": "moon_phase",
            "rows": [
                {"label": "tithi", "value": tithi},
                {"label": "vara", "value": vara},
                {"label": "devi", "value": devi_name, "entity_id": "devi_" + devi_name.lower().replace(" ","_") if devi_name else "", "clickable": bool(devi_name), "symbol": "✦"},
            ],
        }
