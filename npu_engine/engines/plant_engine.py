"""SW · Nirriti · S5 — Plant engine. Seed, root, ancestor, history.

Scores plants by 4D coherence with the current field:
  nakshatra match (0.35) + element match (0.25) +
  dosha balance (0.20) + vara match (0.10) + tithi quality (0.10)
"""
import csv
import os
from .base_engine import ZoneEngine

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
_PLANTS_CSV = os.path.join(_ROOT, "datasets", "plants", "nakshatra_plants.csv")

_plants_cache = None

# Nakshatra lord → vara
_LORD_VARA = {
    "sun": "ravivara", "surya": "ravivara",
    "moon": "somavara", "chandra": "somavara", "soma": "somavara",
    "mars": "mangalavara", "mangala": "mangalavara",
    "mercury": "budhavara", "budha": "budhavara",
    "jupiter": "guruvara", "brihaspati": "guruvara", "guru": "guruvara",
    "venus": "shukravara", "shukra": "shukravara",
    "saturn": "shanivara", "shani": "shanivara",
    "rahu": "shanivara", "ketu": "mangalavara",
    # Deity → rough vara mapping for plant deities
    "ashvini kumaras": "ravivara", "yama": "shanivara",
    "agni": "mangalavara", "brahma": "guruvara",
    "vayu": "shanivara", "indra": "guruvara",
    "vishnu": "budhavara", "mitra": "somavara",
    "rudra": "mangalavara", "aditi": "somavara",
    "nagas": "mangalavara", "pitrs": "shanivara",
    "savitar": "ravivara", "vishvakarma": "shukravara",
    "varuna": "shanivara", "pushan": "somavara",
    "nirriti": "shanivara", "apas": "shukravara",
    "vishvadevas": "guruvara", "vasus": "shanivara",
    "indra-agni": "mangalavara", "kartikeya": "mangalavara",
    "aja ekapada": "shanivara", "ahir budhnya": "shanivara",
    "bhaga": "shukravara", "aryaman": "ravivara",
}

# Weekday index → vara name
_WEEKDAY_VARA = {
    0: "somavara", 1: "mangalavara", 2: "budhavara",
    3: "guruvara", 4: "shukravara", 5: "shanivara", 6: "ravivara",
}


def _load_plants():
    global _plants_cache
    if _plants_cache is not None:
        return _plants_cache
    _plants_cache = []
    try:
        with open(_PLANTS_CSV, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                _plants_cache.append(row)
    except Exception:
        pass
    return _plants_cache


def derive_plant_field(field_state):
    """Return plants ordered by 4D coherence with current field.

    Scores each plant by:
      nakshatra match (0.35), element match (0.25),
      dosha balance (0.20), vara match (0.10), tithi quality (0.10)

    Returns top 5 plants with scores and reasons.
    """
    plants = _load_plants()
    if not plants:
        return []

    p5 = field_state.get("panchanga", {})
    nak = p5.get("nakshatra", "").lower().replace(" ", "_").replace("ā", "a").replace("ī", "i")
    element = p5.get("element", "ether").lower()
    guna = p5.get("guna", "sattva").lower()
    tidx = int(p5.get("tidx", 0))
    tithi_num = (tidx % 15) + 1

    # Current vara
    from datetime import datetime
    now = datetime.now()
    current_vara = _WEEKDAY_VARA.get(now.weekday(), "")

    # Tithi quality
    _TITHI_QUALITY = {
        1: "auspicious", 2: "mixed", 3: "mixed", 4: "inauspicious",
        5: "auspicious", 6: "auspicious", 7: "mixed", 8: "mixed",
        9: "inauspicious", 10: "auspicious", 11: "auspicious", 12: "mixed",
        13: "mixed", 14: "inauspicious", 15: "auspicious",
    }
    tithi_quality = _TITHI_QUALITY.get(tithi_num, "mixed")

    # Dosha from guna
    _GUNA_DOSHA = {"sattva": "kapha", "rajas": "pitta", "tamas": "vata"}
    dominant_dosha = _GUNA_DOSHA.get(guna, "vata")

    scored = []
    for plant in plants:
        score = 0.0
        reasons = []

        plant_nak = plant.get("nakshatra", "").lower().replace(" ", "_")
        plant_elem = plant.get("element", "").lower()
        plant_dosha = plant.get("dosha", "").lower()
        plant_deity = plant.get("deity", "").lower()

        # Nakshatra match (0.35)
        if plant_nak and nak and (plant_nak in nak or nak in plant_nak):
            score += 0.35
            reasons.append("nakshatra")

        # Element match (0.25)
        if plant_elem == element:
            score += 0.25
            reasons.append("element")
        elif plant_elem and element:
            # Partial: compatible elements
            _COMPAT = {"fire": ["air"], "water": ["earth"], "air": ["ether"],
                       "earth": ["water"], "ether": ["air"]}
            if plant_elem in _COMPAT.get(element, []):
                score += 0.12
                reasons.append("element_compat")

        # Dosha balance (0.20)
        if plant_dosha == dominant_dosha:
            score += 0.20
            reasons.append("dosha")
        elif plant_dosha:
            score += 0.08  # any dosha data is some coherence

        # Vara match (0.10)
        plant_vara = _LORD_VARA.get(plant_deity, "")
        if plant_vara and plant_vara == current_vara:
            score += 0.10
            reasons.append("vara")

        # Tithi quality (0.10)
        if tithi_quality == "auspicious":
            score += 0.10
            reasons.append("tithi_auspicious")
        elif tithi_quality == "mixed":
            score += 0.05

        scored.append({
            "plant": plant.get("plant", ""),
            "common_name": plant.get("common_name", ""),
            "sanskrit_name": plant.get("sanskrit_name", ""),
            "entity_id": "plant_" + plant.get("plant", "").lower().replace(" ", "_"),
            "nakshatra": plant.get("nakshatra", ""),
            "element": plant_elem,
            "dosha": plant_dosha,
            "score": round(score, 3),
            "reason": " · ".join(reasons) if reasons else "baseline",
            "use": plant.get("use", ""),
            "ritual_use": plant.get("ritual_use", ""),
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:5]


class PlantEngine(ZoneEngine):
    vastu_position = "SW"
    layer = "S5"
    domain = "Plants"
    deity = "Nirriti"
    color = "#5cb87a"

    def get_entity(self, fs):
        plants = derive_plant_field(fs)
        if plants:
            return plants[0]["entity_id"]
        s5 = self._layers(fs).get("S5", {})
        plant = s5.get("nakshatra_plant", "")
        return "plant_" + plant.lower().replace(" ", "_") if plant else ""

    def render_icon(self, fs):
        plants = derive_plant_field(fs)
        top = plants[0] if plants else {}
        return {"symbol": "🌱", "color": self.color,
                "entity_id": top.get("entity_id", self.get_entity(fs)),
                "vastu": self.vastu_position,
                "value": top.get("plant", "")}

    def render_zone(self, fs):
        plants = derive_plant_field(fs)
        s5 = self._layers(fs).get("S5", {})
        rows = []
        for p in plants[:3]:
            rows.append({
                "label": "plant", "value": p["plant"],
                "value_color": self.color if p["score"] > 0.3 else "#7a8fa0",
                "entity_id": p["entity_id"], "clickable": True,
                "symbol": "❧",
            })
            rows.append({
                "label": "score", "value": f"{p['score']:.2f} · {p['reason']}",
                "label_color": "#3a5040",
            })
        if not rows:
            rows = [{"label": "plant", "value": s5.get("nakshatra_plant", ""),
                     "entity_id": self.get_entity(fs), "clickable": True}]
        rows.append({"label": "body", "value": s5.get("body_region", "")})
        return {**super().render_zone(fs),
                "title": plants[0]["plant"] if plants else "Plants",
                "visual_type": "plant_form",
                "rows": rows,
                "apps": [{"name": "s5", "url": "/s5"}, {"name": "agriculture", "url": "/bhumi/agriculture"}]}
