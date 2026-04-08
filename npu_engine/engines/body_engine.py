"""S · Yama · S5 — Body engine. Marma, anatomy, dharma, boundary.

Connects to:
    datasets/marma/body_region_marma.csv  — body region → marma names
    datasets/marma/marma_field.csv        — full marma details (element, dosha, herb, raga)
"""
import csv
import os
from .base_engine import ZoneEngine

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
_BODY_MARMA_CSV = os.path.join(_ROOT, "datasets", "marma", "body_region_marma.csv")
_MARMA_FIELD_CSV = os.path.join(_ROOT, "datasets", "marma", "marma_field.csv")

_marma_by_region = None
_marma_by_element = None


def _load_marma():
    global _marma_by_region, _marma_by_element
    if _marma_by_region is not None:
        return
    _marma_by_region = {}
    _marma_by_element = {}
    try:
        with open(_BODY_MARMA_CSV, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                region = row.get("body_region", "").lower()
                _marma_by_region.setdefault(region, []).append(row)
    except Exception:
        pass
    try:
        with open(_MARMA_FIELD_CSV, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                elem = row.get("element", "").lower()
                _marma_by_element.setdefault(elem, []).append(row)
    except Exception:
        pass


class BodyEngine(ZoneEngine):
    vastu_position = "S"
    layer = "S5"
    domain = "Body"
    deity = "Yama"
    color = "#a09070"

    def get_entity(self, fs):
        s5 = self._layers(fs).get("S5", {})
        region = s5.get("body_region", "")
        return "body_" + region.lower().replace(" ", "_") if region else ""

    def render_icon(self, fs):
        s5 = self._layers(fs).get("S5", {})
        return {"symbol": "◉", "color": self.color,
                "entity_id": self.get_entity(fs),
                "vastu": self.vastu_position,
                "value": s5.get("body_region", "")}

    def render_zone(self, fs):
        s5 = self._layers(fs).get("S5", {})
        p5 = fs.get("panchanga", {})
        element = p5.get("element", "ether").lower()
        region = s5.get("body_region", "")

        _load_marma()

        # Find marma by body region first, then by element
        marma_name = ""
        marma_treatment = ""
        marma_herb = ""
        marma_raga = ""
        region_matches = _marma_by_region.get(region.lower(), []) if region else []
        if region_matches:
            m = region_matches[0]
            marma_name = m.get("marma_name", "")
            marma_treatment = m.get("therapeutic_action", "")
        # Enrich from marma_field.csv by element
        elem_matches = _marma_by_element.get(element, [])
        if elem_matches:
            mf = elem_matches[0]
            if not marma_name:
                marma_name = mf.get("name_iast", "")
            marma_herb = mf.get("herb_primary", "")
            marma_raga = mf.get("raga_therapeutic", "")
            marma_treatment = marma_treatment or mf.get("treatment_approach", "")

        rows = [
            {"label": "body_region", "value": region},
            {"label": "dosha", "value": s5.get("dosha", "")},
            {"label": "element", "value": s5.get("element", "")},
        ]
        if marma_name:
            rows.append({"label": "marma", "value": marma_name})
        if marma_herb:
            rows.append({"label": "herb", "value": marma_herb})
        if marma_raga:
            rows.append({"label": "raga", "value": marma_raga})

        return {**super().render_zone(fs),
                "title": region or "Body",
                "visual_type": "body_region",
                "rows": rows}
