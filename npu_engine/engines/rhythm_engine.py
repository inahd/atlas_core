"""N · Kubera · S3 — Rhythm engine. Tithi, nakshatra, tala, calendar."""
from .base_engine import ZoneEngine

class RhythmEngine(ZoneEngine):
    vastu_position = "N"
    layer = "S3"
    domain = "Rhythm"
    deity = "Kubera"
    color = "#8899bb"

    def get_entity(self, fs):
        p = self._panchanga(fs)
        nak = p.get("nakshatra", "")
        return "nakshatra_" + nak.lower().replace(" ", "_") if nak else ""

    def render_icon(self, fs):
        p = self._panchanga(fs)
        return {"symbol": "✶", "color": self.color,
                "entity_id": self.get_entity(fs),
                "vastu": self.vastu_position,
                "value": p.get("nakshatra", "")}

    def render_zone(self, fs):
        p = self._panchanga(fs)
        s3 = self._layers(fs).get("S3", {})
        nak = p.get("nakshatra", "")
        lord = p.get("nak_lord", "")
        return {**super().render_zone(fs),
                "title": nak or "Rhythm",
                "visual_type": "tala_cycle",
                "rows": [
                    {"label": "nakshatra", "value": nak, "entity_id": self.get_entity(fs), "clickable": True, "symbol": "✶"},
                    {"label": "tithi", "value": p.get("tithi", "")},
                    {"label": "nak_lord", "value": lord, "entity_id": "graha_" + lord.lower().replace(" ","_") if lord else "", "clickable": bool(lord), "symbol": "☽" if lord else ""},
                    {"label": "dosha", "value": s3.get("dosha", "")},
                ]}
