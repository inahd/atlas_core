"""
kernel.py
=========
Coherence Atlas — single data spine.

Pañcāṅga · Rāga · S0–S6 layers · field state.
Every front-end (TUI, HTML, API) imports from here.

Run directly to serve the HTTP API:
    python kernel.py            # port 5000
    python kernel.py 8080       # custom port
"""

import csv
import json
import os
import re as _re
import shutil
import sqlite3
import sys
import time
import unicodedata
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

START_TIME = time.time()

# ══════════════════════════════════════════════════════════════
# COHERENCE ENGINE — relational validation
# ══════════════════════════════════════════════════════════════
try:
    from core.coherence_engine import CoherenceEngine
    _coherence = CoherenceEngine(Path(__file__).resolve().parent / "datasets")
    print("✓ CoherenceEngine loaded")
except Exception as e:
    print(f"⚠ CoherenceEngine not loaded: {e}")
    _coherence = None

try:
    from npu_engine.toroidal_field import ToroidalField
    from npu_engine.datasets import load_all_entities
    print("✓ ToroidalField loaded")
except Exception as e:
    print(f"⚠ ToroidalField not loaded: {e}")
    ToroidalField = None
    load_all_entities = None

_toroid = None

try:
    from npu_engine.relational_engine import RelationalEngine
    _relational = RelationalEngine(derive_sound_fn=None)  # wired after _derive_sound_state defined
    print("✓ RelationalEngine loaded")
except Exception as e:
    print(f"⚠ RelationalEngine not loaded: {e}")
    _relational = None

try:
    from npu_engine.temple_geometry import TempleGeometry
    _temple = TempleGeometry()
    print("✓ TempleGeometry loaded")
except Exception as e:
    print(f"⚠ TempleGeometry not loaded: {e}")
    _temple = None

# ══════════════════════════════════════════════════════════════
# SEMITONE CONSTANTS — Ṣaḍja-grāma chromatic
# ══════════════════════════════════════════════════════════════

S   = 0    # Sa
re  = 1    # komal Re
Re  = 2    # śuddha Re
ga  = 3    # komal Ga
Ga  = 4    # śuddha Ga
ma  = 5    # śuddha ma
Ma  = 6    # tīvra Ma
Pa  = 7    # Pa
dha = 8    # komal Dha
Dha = 9    # śuddha Dha
ni  = 10   # komal Ni
Ni  = 11   # śuddha Ni

BASE_FREQ = 130.81   # Sa = C3

# Reverse map: semitone number → swara name (for sound_state derivation)
_SEMI_TO_SWARA = {
    0: "Sa", 1: "re", 2: "Re", 3: "ga", 4: "Ga", 5: "ma",
    6: "Ma", 7: "Pa", 8: "dha", 9: "Dha", 10: "ni", 11: "Ni",
}

# Element root frequencies (for sound surfaces)
_ELEMENT_FREQ = {
    "fire": 440.0, "earth": 261.63, "air": 293.66,
    "water": 392.0, "ether": 329.63,
}

# Element RGB (canonical, per RENDERING_STANDARDS.md)
_ELEMENT_RGB = {
    "air": [0, 200, 255], "fire": [255, 100, 30], "water": [30, 100, 255],
    "earth": [139, 100, 20], "ether": [200, 169, 110],
}
_GUNA_ALPHA = {"sattva": 0.9, "rajas": 0.7, "tamas": 0.5}

def _phi_to_element(phi):
    """Derive element from φ coordinate (TWO_AXIS_FIELD_SPEC encoding)."""
    import math
    phi = phi % (2 * math.pi)
    norm = phi / (2 * math.pi)  # 0-1
    if norm < 0.1: return "ether"
    if norm < 0.3: return "air"
    if norm < 0.5: return "water"
    if norm < 0.7: return "fire"
    if norm < 0.9: return "earth"
    return "ether"

# Tāla bol patterns (module-level, used by sound_state + generate_composition)
_TALA_BOLS = {
    "Adi": ["dha", "dhin", "dhin", "dha", "dha", "tin", "tin", "ta"],
    "Rupak": ["tin", "tin", "na", "dhin", "dhin", "na", "na"],
    "Jhaptal": ["dhi", "na", "dhi", "dhi", "na", "ti", "na", "dhi", "dhi", "na"],
    "Dadra": ["dha", "dhin", "na", "dha", "tin", "na"],
    "Chautal": ["dha", "dha", "din", "ta", "kite", "dha", "dhin", "na", "kat", "ta", "trkt", "dhin"],
    "Keherwa": ["dha", "ge", "na", "ti", "na", "ke", "dhin", "na"],
}

def semi_to_freq(semi, octave=1):
    """Semitone + octave → Hz."""
    return BASE_FREQ * (2 ** (semi / 12 + octave))


# ══════════════════════════════════════════════════════════════
# RĀGA DATABASE
# ══════════════════════════════════════════════════════════════
# Each rāga: scale (semitones), ārōha/avarōha phrases,
# time window, rasa, vādī/samvādī.

RAGAS = {
    "Yaman": {
        "scale":    [S, Re, Ga, Ma, Pa, Dha, Ni],
        "aroha":    [Ni, Re, Ga, Ma, Dha, Ni],
        "avaroha":  [Ni, Dha, Pa, Ma, Ga, Re, S],
        "vadi": Ga, "samvadi": Ni,
        "time":     "evening · 1st prahar",
        "rasa":     "śṛṅgāra · devotional longing",
        "prahar":   1,
    },
    "Bhairavī": {
        "scale":    [S, re, ga, ma, Pa, dha, ni],
        "aroha":    [S, re, ga, ma, Pa, dha, ni],
        "avaroha":  [ni, dha, Pa, ma, ga, re, S],
        "vadi": ma, "samvadi": S,
        "time":     "morning · conclusion rāga",
        "rasa":     "karuṇa · compassionate surrender",
        "prahar":   8,
    },
    "Tōḍī": {
        "scale":    [S, re, ga, Ma, Pa, dha, Ni],
        "aroha":    [S, re, ga, Ma, Pa, dha, Ni],
        "avaroha":  [Ni, dha, Pa, Ma, ga, re, S],
        "vadi": dha, "samvadi": ga,
        "time":     "late morning",
        "rasa":     "karuṇa · viraha · pathos",
        "prahar":   3,
    },
    "Bhairava": {
        "scale":    [S, re, Ga, ma, Pa, dha, Ni],
        "aroha":    [S, re, Ga, ma, Pa, dha, Ni],
        "avaroha":  [Ni, dha, Pa, ma, Ga, re, S],
        "vadi": dha, "samvadi": re,
        "time":     "dawn · Brahma muhūrta",
        "rasa":     "śānta · bhayānaka · Śiva's hour",
        "prahar":   8,
    },
    "Mārvā": {
        "scale":    [S, re, Ga, Ma, Pa, Dha, Ni],
        "aroha":    [S, re, Ga, Ma, Dha, Ni],
        "avaroha":  [Ni, Dha, Ma, Ga, re, S],
        "vadi": Re, "samvadi": Dha,
        "time":     "sunset sandhyā",
        "rasa":     "vīra · gravity at the edge of night",
        "prahar":   1,
    },
    "Darbārī": {
        "scale":    [S, Re, ga, ma, Pa, dha, ni],
        "aroha":    [S, Re, ga, ma, Pa, dha, ni],
        "avaroha":  [ni, dha, Pa, ma, ga, Re, S],
        "vadi": Re, "samvadi": Pa,
        "time":     "midnight · 3rd prahar",
        "rasa":     "vīra · gāmbhīrya · midnight gravity",
        "prahar":   3,
    },
    "Bāgeshṛī": {
        "scale":    [S, Re, ga, ma, Pa, Dha, ni],
        "aroha":    [S, Re, ga, ma, Dha, ni],
        "avaroha":  [ni, Dha, Pa, ma, ga, Re, S],
        "vadi": Dha, "samvadi": ga,
        "time":     "night · 2nd prahar",
        "rasa":     "śṛṅgāra · viraha · tender night",
        "prahar":   2,
    },
    "Bihāg": {
        "scale":    [S, Re, Ga, ma, Pa, Dha, Ni],
        "aroha":    [S, Ga, ma, Pa, Ni],
        "avaroha":  [Ni, Dha, Pa, ma, Ga, Re, S],
        "vadi": Ga, "samvadi": Pa,
        "time":     "late night · 3rd prahar",
        "rasa":     "śṛṅgāra · romantic luminosity",
        "prahar":   3,
    },
    "Kāfī": {
        "scale":    [S, Re, ga, ma, Pa, Dha, ni],
        "aroha":    [S, Re, ga, ma, Pa, Dha, ni],
        "avaroha":  [ni, Dha, Pa, ma, ga, Re, S],
        "vadi": Pa, "samvadi": Re,
        "time":     "late night",
        "rasa":     "śṛṅgāra · hāsya · playful devotion",
        "prahar":   3,
    },
    "Multānī": {
        "scale":    [S, re, ga, Ma, Pa, dha, Ni],
        "aroha":    [S, re, ga, Ma, Pa, dha, Ni],
        "avaroha":  [Ni, dha, Pa, Ma, ga, re, S],
        "vadi": Pa, "samvadi": S,
        "time":     "afternoon",
        "rasa":     "karuṇa · deep afternoon stillness",
        "prahar":   5,
    },
    "Bhimpalasī": {
        "scale":    [S, Re, ga, ma, Pa, Dha, ni],
        "aroha":    [S, Re, ga, ma, Pa, Dha, ni],
        "avaroha":  [ni, Dha, Pa, ma, ga, Re, S],
        "vadi": ga, "samvadi": ma,
        "time":     "afternoon · abhijit",
        "rasa":     "karuṇa · śṛṅgāra · afternoon gravity",
        "prahar":   5,
    },
    "Khamāj": {
        "scale":    [S, Re, Ga, ma, Pa, Dha, ni],
        "aroha":    [S, Re, Ga, ma, Pa, Dha, ni],
        "avaroha":  [ni, Dha, Pa, ma, Ga, Re, S],
        "vadi": Ga, "samvadi": ni,
        "time":     "evening · 2nd prahar",
        "rasa":     "śṛṅgāra · hāsya · light evening",
        "prahar":   2,
    },
    "Śankara": {
        "scale":    [S, Re, Ga, Ma, Pa, Dha, Ni],
        "aroha":    [S, Ga, Ma, Pa, Dha, Ni],
        "avaroha":  [Ni, Dha, Pa, Ma, Ga, Re, S],
        "vadi": Pa, "samvadi": Re,
        "time":     "evening",
        "rasa":     "vīra · śānta · ascendant",
        "prahar":   1,
    },
    "all rāgas": {
        "scale":    [S, Re, Ga, Ma, Pa, Dha, Ni],
        "aroha":    [S, Re, Ga, Ma, Pa, Dha, Ni],
        "avaroha":  [Ni, Dha, Pa, Ma, Ga, Re, S],
        "vadi": Ga, "samvadi": Ni,
        "time":     "all times · Citrā · māyā as full display",
        "rasa":     "all rasas",
        "prahar":   0,
    },
}

# Convenience: scale-only lookup (matches JS RAGA_FREQS)
RAGA_SCALES = {name: r["scale"] for name, r in RAGAS.items()}


# ══════════════════════════════════════════════════════════════
# 15 NITYA DEVĪS
# ══════════════════════════════════════════════════════════════
# (name, emoji, process, rāga)

NITYA_DEVIS = [
    ("Kāmeśvarī",      "✦", "the will that initiates · creative impulse · Sṛṣṭi's first breath",    "Yaman"),
    ("Bhagamālinī",    "☀", "solar manifestation chain · luminaries as garland · sequential unfoldment","Bhairavī"),
    ("Nityāklinā",     "🌊","ever-wet · Soma current perpetual · dissolution of dryness",              "Tōḍī"),
    ("Bheruṇḍā",       "⚡","the terrible pair · dual-force held · productive tension",                "Bhairava"),
    ("Vahnivasini",    "🔥","dwelling in fire · Agni as home · purification as natural state",         "Mārvā"),
    ("Mahāvajreśvarī", "💎","diamond sovereignty · indestructible will · Vajra pervades all",          "Śankara"),
    ("Śivadūtī",       "🕊","S0→S1 bridge · messenger across the boundary · descent made personal",   "Bhimpalasī"),
    ("Tvaritā",        "⚡","the swift one · time compression · years complete in days",               "Darbārī"),
    ("Kulasundarī",    "🌸","lineage transmission · tradition as living form · kula beauty",           "Bāgeshṛī"),
    ("Nityā",          "∞", "the eternal itself · S0 brushing S3 · pure permanence operative",         "Bihāg"),
    ("Nīlapatākā",     "🏴","blue banner raised · direction established · victory standard",           "Kāfī"),
    ("Vijayā",         "🏆","complete victory · dharmic culmination · field at resolution",            "Khamāj"),
    ("Sarvamangalā",   "🌺","all-auspiciousness · total benediction · coherence as grace",            "Multānī"),
    ("Jvālāmālinī",    "🔥","fire-garlanded · transformation ring · destruction as beauty ★",         "Bhairava"),
    ("Citrā",          "🌈","the variegated · māyā as full display · all colors present",             "all rāgas"),
]


def _devi_dict(didx):
    """Convert NITYA_DEVIS tuple to a dict for the panchanga response."""
    name, symbol, desc, raga = NITYA_DEVIS[didx]
    slug = name.lower()
    for a, b in [("ā","a"),("ī","i"),("ū","u"),("ṛ","r"),("ṃ","m"),("ḥ","h"),
                 ("ś","s"),("ṣ","s"),("ṅ","n"),("ñ","n"),("ṭ","t"),("ḍ","d"),("ṇ","n")]:
        slug = slug.replace(a, b)
    slug = slug.replace(" ", "_")
    import re
    slug = re.sub(r"[^a-z0-9_]", "", slug)
    return {
        "name": name,
        "symbol": symbol,
        "description": desc,
        "raga": raga,
        "entity_id": "devi_" + slug,
        "tithi_position": didx + 1,
    }


def _devi_field(devi, field):
    """Read a field from devi whether it's a dict or legacy tuple.

    Supports both old format (name, symbol, desc, raga) and new dict format.
    """
    if isinstance(devi, dict):
        _MAP = {0: "name", 1: "symbol", 2: "description", 3: "raga"}
        if isinstance(field, int):
            return devi.get(_MAP.get(field, ""), "")
        return devi.get(field, "")
    if isinstance(devi, (list, tuple)):
        if isinstance(field, int):
            return devi[field] if field < len(devi) else ""
        _RMAP = {"name": 0, "symbol": 1, "description": 2, "raga": 3}
        idx = _RMAP.get(field)
        if idx is not None and idx < len(devi):
            return devi[idx]
        return ""
    return str(devi)


# ══════════════════════════════════════════════════════════════
# S0 – S6 LAYERS
# ══════════════════════════════════════════════════════════════
# (code, emoji, short_name, description, bullets)

LAYERS = [
    ("S0", "✦", "Bindu",     "Goloka Vṛndāvana · acintya · read-only · source of polarity",
     ["• ALPHA_SOURCE = 0.15  ← non-tunable S0 reference",
      "• AcintyaViolation raised on any S0 write attempt",
      "• s0_reference() is the ONLY permitted S0 operation",
      "• The field has a direction it did not give itself",
      "• acintya-bhedābheda-tattva — unity AND difference",
      "• Never computed. Never simulated. Only inferred toward."]),

    ("S1", "🔱","Archetype",  "15 Nitya Devīs · 64 Śaktis · Navagraha · governance devatās · 4 Varṇas",
     ["• 15 Nitya Devīs — tithi as living process (see Devī screen)",
      "• 64 Śaktis — 8 directions × 8 powers — field resonance modes",
      "• Navagraha — 9 planetary intelligences — TIME_COORD lords",
      "• Pipeline: Gaṇeśa→Varuṇa→Agni→Viṣṇu→Render",
      "• 4 Varṇas as emergent function — not caste — Guṇa ratio",
      "• Brāhmaṇa·Kṣatriya·Vaiśya·Śūdra — each a system role"]),

    ("S2", "♫", "Sound",     "64 Kalās · Rāga grammar · Tāla clock · Bhakti-rasāmṛta-sindhu",
     ["• 64 Kalās — Vedic arts as rasa-expressions (BRS)",
      "• Rāga = symmetry order n in the field (Bhairavī=3, Yaman=6)",
      "• Tāla = S3 time made physical — shared with dance petal",
      "• BRS balance point: technique vs rasa — Bhaktisiddhānta's warning",
      "• Three stability ladders: epistemic · devotional · formal",
      "• Talachakra Studio — working generative music system ✓"]),

    ("S3", "☽", "Rhythm",    "Pañcāṅga · TIME_COORD KEY · Kalpa · Yuga · Manvantara",
     ["• Pañcāṅga = the KEY that sets the entire Atlas in motion",
      "• Tithi→Devī→Yantra→Field slice→Vāstu/Garden/Game",
      "• Nakṣatra→Deity→Rāga→Doṣa→Social group",
      "• Vara→Graha→Element→Practice→Market window",
      "• Kali Yuga NOW — α=1.0 — void nodes dominant",
      "• Budha/Budha daśā — window closes October 2027 — BUILD"]),

    ("S4", "⬡", "Geometry",  "3-toroid Brahmāṇḍa · yantra emergence · Vāstu · garden maṇḍala",
     ["• Three toroids: Sṛṣṭi(A) · Sthiti(B) · Saṃhāra(C) at 120°",
      "• Polar flip at Pralāya — new egg born inverted",
      "• 4 node classes: coherence · resonance · void · rift",
      "• Vāstu = 2D field slice — Īśāna(NE)=coherence Nirṛti(SW)=void",
      "• Garden maṇḍala = planting zones from coherence nodes",
      "• Game world physics = field amplitude as coherence score"]),

    ("S5", "🌿","Nature",     "Ayurveda · Doṣa · plant graph · soil resonance · mycelium",
     ["• Vāta·Pitta·Kapha — morphogenesis in the game organisms",
      "• Sacred plants dataset — 71 CSVs including plants→graha",
      "• Paramagnetic soil = planetary resonance interface",
      "• Mycelial networks = distributed field substrate",
      "• Doṣa zones map to coherence/void/rift node types",
      "• Kṛṣi-Parāśara — garden timing from TIME_COORD"]),

    ("S6", "🎮","Līlā",       "HURDsman · game · social · wiki · market · federation",
     ["• HURDsman = seed planter · shapes pressure fields · YOU",
      "• Līlā engine: humor · errors · eternal incalculable",
      "• Resonance nodes = Manvantara gates — witnessed never explained",
      "• Śukrācārya: UX · token economy · Sañjīvanī recovery",
      "• Samudra Manthan: altar nodes(Devas) · dirty servers(Asuras)",
      "• leelamaps.com — S5→S6 bridge — community on actual territory"]),
]

# Layer → default rāga (S1 uses tithi devī rāga instead)
LAYER_RAGAS = ["Yaman", "", "Bhairavī", "Tōḍī", "Darbārī", "Bāgeshṛī", "Kāfī"]


# ══════════════════════════════════════════════════════════════
# DATASET LOADING
# ══════════════════════════════════════════════════════════════
# Canonical data loaded from datasets/ CSV/JSON files.
# IAST display names map from ITRANS dataset keys so the UI
# stays beautiful while the data comes from files.

_HERE = Path(__file__).resolve().parent
_DATA = _HERE / "datasets"

LOCAL_TEXT_CORPORA = {
    "bg": {
        "label": "Bhagavad Gita",
        "kind": "bg",
        "chunk_path": _HERE / "datasets" / "sources" / "gaudiya" / "bg_chunks.jsonl",
        "verse_dir": _HERE / "datasets" / "sources" / "gaudiya" / "bg_verses",
    },
    "bhagavatam": {
        "label": "Bhagavatam",
        "kind": "jsonl",
        "chunk_path": _HERE / "datasets" / "sources" / "gaudiya" / "bhagavatam_chunks.jsonl",
    },
    "sikshashtakam": {
        "label": "Sikshashtakam",
        "kind": "jsonl",
        "chunk_path": _HERE / "datasets" / "sources" / "gaudiya" / "sikshashtakam_chunks.jsonl",
    },
}


def _available_local_corpora():
    items = []
    for corpus_id, meta in LOCAL_TEXT_CORPORA.items():
        available = False
        if meta.get("kind") == "bg" and meta.get("verse_dir") and Path(meta["verse_dir"]).exists():
            available = True
        if meta.get("chunk_path") and Path(meta["chunk_path"]).exists():
            available = True
        if available:
            items.append({
                "id": corpus_id,
                "corpus_id": corpus_id,
                "label": meta["label"],
            })
    return items


def _iter_jsonl_records(path: Path):
    if not path.exists():
        return
    with path.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except Exception:
                continue


def _normalize_corpus_ref(corpus_id: str, ref: str) -> str:
    value = str(ref or "").strip()
    if not value:
        return ""
    upper = value.upper().replace("_", " ").replace("-", " ")
    upper = _re.sub(r"\s+", " ", upper).strip()
    if corpus_id == "bg":
        match = _re.search(r"(\d+)\.(\d+(?:\s*-\s*\d+)?)", upper)
        if match:
            return f"BG {int(match.group(1))}.{match.group(2).replace(' ', '')}"
    if corpus_id == "bhagavatam":
        match = _re.search(r"(\d+)\.(\d+)\.(\d+)", upper)
        if match:
            return f"SB {int(match.group(1))}.{int(match.group(2))}.{int(match.group(3))}"
    if corpus_id == "sikshashtakam":
        match = _re.search(r"VERSE\s*(\d+)", upper)
        if match:
            return f"verse {int(match.group(1))}"
    return value


def _build_bg_json_path(ref: str) -> Optional[Path]:
    match = _re.search(r"BG\s+(\d+)\.(\d+(?:-\d+)?)", str(ref or "").upper())
    if not match:
        return None
    chapter = int(match.group(1))
    verse = match.group(2)
    return LOCAL_TEXT_CORPORA["bg"]["verse_dir"] / f"{chapter}_{verse}.json"


def _record_text(record: Dict[str, Any]) -> str:
    return "\n\n".join(
        str(record.get(key, "")).strip()
        for key in ("text", "translation", "purport", "sanskrit", "iast", "synonyms")
        if str(record.get(key, "")).strip()
    ).strip()


def _read_local_corpus_passage(corpus_id: str, ref: str) -> Dict[str, Any]:
    meta = LOCAL_TEXT_CORPORA.get(corpus_id)
    if not meta:
        raise FileNotFoundError("unknown corpus")
    normalized_ref = _normalize_corpus_ref(corpus_id, ref)
    if not normalized_ref:
        raise FileNotFoundError("missing ref")

    if corpus_id == "bg":
        bg_path = _build_bg_json_path(normalized_ref)
        if bg_path and bg_path.exists():
            record = json.loads(bg_path.read_text(encoding="utf-8", errors="replace"))
            text = _record_text(record)
            if text:
                return {
                    "corpus_id": corpus_id,
                    "label": meta["label"],
                    "reference": record.get("verse_ref") or normalized_ref,
                    "text": text,
                    "source_path": str(bg_path.relative_to(_HERE)),
                }

    chunk_path = meta.get("chunk_path")
    if chunk_path and Path(chunk_path).exists():
        for record in _iter_jsonl_records(Path(chunk_path)):
            verse_ref = str(record.get("verse_ref", "")).strip()
            text = _record_text(record)
            if verse_ref and verse_ref.upper() == normalized_ref.upper():
                return {
                    "corpus_id": corpus_id,
                    "label": meta["label"],
                    "reference": verse_ref,
                    "text": text or verse_ref,
                    "source_path": str(Path(chunk_path).relative_to(_HERE)),
                }
            if corpus_id == "sikshashtakam" and normalized_ref.lower() in str(record.get("text", "")).lower():
                return {
                    "corpus_id": corpus_id,
                    "label": meta["label"],
                    "reference": normalized_ref,
                    "text": text or str(record.get("text", "")).strip(),
                    "source_path": str(Path(chunk_path).relative_to(_HERE)),
                }
    raise FileNotFoundError("passage not found")


def _search_local_corpus(corpus_id: str, query: str, limit: int = 8) -> list[Dict[str, Any]]:
    meta = LOCAL_TEXT_CORPORA.get(corpus_id)
    if not meta:
        return []
    q = str(query or "").strip().lower()
    if not q:
        return []
    results = []
    chunk_path = meta.get("chunk_path")
    if not chunk_path or not Path(chunk_path).exists():
        return results
    for record in _iter_jsonl_records(Path(chunk_path)):
        hay = "\n".join(
            str(record.get(key, "")).strip()
            for key in ("verse_ref", "text", "translation", "purport", "sanskrit", "iast", "synonyms")
            if str(record.get(key, "")).strip()
        )
        if q not in hay.lower():
            continue
        snippet = ""
        pos = hay.lower().find(q)
        if pos >= 0:
            start = max(0, pos - 80)
            end = min(len(hay), pos + 160)
            snippet = hay[start:end].replace("\n", " ").strip()
        results.append({
            "corpus_id": corpus_id,
            "label": meta["label"],
            "reference": record.get("verse_ref") or record.get("id") or "",
            "snippet": snippet or hay[:220],
            "source_path": str(Path(chunk_path).relative_to(_HERE)),
        })
        if len(results) >= limit:
            break
    return results


def _load_csv(relpath):
    """Load a CSV file from datasets/ into a list of dicts."""
    p = _DATA / relpath
    if not p.exists():
        return []
    with open(p, encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ── Full corpus registry + cross-corpus search ──────────────
_full_corpus_registry: Optional[list] = None
_full_corpus_registry_mtime: float = 0.0


def _load_full_corpus_registry() -> list:
    """Load the corpus registry from corpus_registry.json (auto-reloads on file change)."""
    global _full_corpus_registry, _full_corpus_registry_mtime
    reg_path = _HERE / "datasets" / "sources" / "corpus_registry.json"
    if reg_path.exists():
        mtime = reg_path.stat().st_mtime
        if _full_corpus_registry is not None and mtime == _full_corpus_registry_mtime:
            return _full_corpus_registry
        _full_corpus_registry = json.loads(reg_path.read_text(encoding="utf-8"))
        _full_corpus_registry_mtime = mtime
    else:
        _full_corpus_registry = []
    return _full_corpus_registry


_text_entity_relations: Optional[list] = None


def _load_text_entity_relations() -> list:
    """Load text_entity_relations.csv for entity-linked corpus search."""
    global _text_entity_relations
    if _text_entity_relations is not None:
        return _text_entity_relations
    p = _DATA / "relations" / "text_entity_relations.csv"
    if p.exists():
        with p.open(encoding="utf-8") as f:
            _text_entity_relations = list(csv.DictReader(f))
    else:
        _text_entity_relations = []
    return _text_entity_relations


def _fold_diacritics(s: str) -> str:
    """Fold diacritics for search: Rāma→rama, Śrī→sri, å→a, ∂→i."""
    import unicodedata
    # NFKD decomposition separates base chars from combining marks
    nfkd = unicodedata.normalize("NFKD", s)
    folded = "".join(c for c in nfkd if unicodedata.category(c) != "Mn")
    # Additional replacements for characters NFKD doesn't decompose
    folded = folded.replace("å", "a").replace("∂", "i").replace("ƒ", "n")
    folded = folded.replace("¡", "n").replace("¶", "sh").replace("∫", "n")
    folded = folded.replace("≈", "m").replace("¢", "n").replace("¶", "sh")
    folded = folded.replace("›", "S").replace("Œ", "d").replace("∆", "n")
    return folded.lower()


def _search_full_corpus(query: str, tradition: str = "",
                        limit: int = 10) -> list:
    """Search across all corpus JSONL files. Returns ranked results.
    Folds diacritics for matching but returns original text."""
    q = _fold_diacritics(str(query or "").strip())
    if not q:
        return []
    registry = _load_full_corpus_registry()
    results = []
    terms = q.split()
    for entry in registry:
        if tradition and entry.get("tradition", "") != tradition:
            continue
        cp = entry.get("chunks_path", "")
        chunk_path = _HERE / cp if cp else None
        if not chunk_path or not chunk_path.exists():
            continue
        for record in _iter_jsonl_records(chunk_path):
            # Build original text for display
            original = " ".join(
                str(record.get(k, "")).strip()
                for k in ("verse_ref", "text", "translation", "purport",
                           "sanskrit", "iast", "synonyms")
                if str(record.get(k, "")).strip()
            )
            # Fold diacritics for matching
            hay = _fold_diacritics(original)
            if not all(t in hay for t in terms):
                continue
            # Build snippet from ORIGINAL text (preserves diacritics)
            pos = hay.find(terms[0])
            start = max(0, pos - 80)
            end = min(len(hay), pos + 200)
            # Map positions back to original (same length after folding)
            snippet = original[start:end].strip()
            results.append({
                "corpus_id": entry.get("id", ""),
                "title": entry.get("title", entry.get("name", "")),
                "tradition": entry.get("tradition", ""),
                "reference": record.get("verse_ref", "") or str(record.get("id", "")),
                "text": snippet or original[:280],
                "domain": record.get("domain", entry.get("domain", "")),
                "authority": entry.get("authority", 0.5),
            })
            if len(results) >= limit:
                break
        if len(results) >= limit:
            break
    results.sort(key=lambda r: -r.get("authority", 0))
    return results[:limit]


def _entity_corpus_search(entity_id: str, limit: int = 10) -> list:
    """Find corpus chunks linked to a specific entity via text_entity_relations."""
    rels = _load_text_entity_relations()
    registry = _load_full_corpus_registry()
    reg_by_id = {e["id"]: e for e in registry}

    # Normalize entity_id: accept both nakshatra:rohini and nakshatra_rohini
    entity_norm = entity_id.replace(":", "_").lower()
    entity_colon = entity_id.replace("_", ":", 1).lower() if "_" in entity_id else entity_id.lower()

    # Find matching relations
    matched_chunks = []
    for row in rels:
        to_id = str(row.get("to_id", "")).lower()
        if to_id != entity_norm and to_id != entity_colon:
            continue
        from_id = row.get("from_id", "")
        # from_id format: chunk:source_name:chunk_num
        parts = from_id.split(":")
        if len(parts) < 3 or parts[0] != "chunk":
            continue
        source_name = parts[1]
        chunk_num = parts[2]
        matched_chunks.append({
            "source": source_name,
            "chunk_num": chunk_num,
            "confidence": float(row.get("confidence", 0.5)),
            "excerpt": row.get("excerpt", "")[:300],
            "tradition": row.get("tradition", ""),
        })
        if len(matched_chunks) >= limit * 3:
            break

    # Resolve chunks to full text
    results = []
    for mc in sorted(matched_chunks, key=lambda r: -r["confidence"]):
        source = mc["source"]
        reg_entry = reg_by_id.get(source, {})
        cp = reg_entry.get("chunks_path", "")
        chunk_path = _HERE / cp if cp else None
        if not chunk_path or not chunk_path.exists():
            # Try finding the JSONL by glob
            candidates = list((_HERE / "datasets" / "sources").rglob(
                f"{source}_chunks.jsonl"))
            if candidates:
                chunk_path = candidates[0]
            else:
                results.append({
                    "corpus_id": source,
                    "title": reg_entry.get("title", source),
                    "tradition": mc["tradition"],
                    "reference": f"chunk {mc['chunk_num']}",
                    "text": mc["excerpt"],
                    "entity_id": entity_id,
                    "confidence": mc["confidence"],
                })
                if len(results) >= limit:
                    break
                continue
        target_id = mc["chunk_num"]
        for record in _iter_jsonl_records(chunk_path):
            if str(record.get("id", "")) == target_id:
                text = " ".join(
                    str(record.get(k, "")).strip()
                    for k in ("text", "translation", "purport")
                    if str(record.get(k, "")).strip()
                )[:400]
                results.append({
                    "corpus_id": source,
                    "title": reg_entry.get("title", source),
                    "tradition": mc["tradition"] or reg_entry.get("tradition", ""),
                    "reference": record.get("verse_ref", "") or target_id,
                    "text": text or mc["excerpt"],
                    "entity_id": entity_id,
                    "confidence": mc["confidence"],
                })
                break
        if len(results) >= limit:
            break
    return results[:limit]


def _load_json(relpath):
    """Load a JSON file from datasets/."""
    p = _DATA / relpath
    if not p.exists():
        return {}
    with open(p, encoding="utf-8") as f:
        return json.load(f)


# ── Nakṣatras (full 27) from astro/nakshatra_full.csv ───────
_nak_raw = _load_csv("astro/nakshatra_full.csv")

# ITRANS→IAST display name mapping (datasets use ITRANS)
_NAK_IAST = {
    "Ashwini": "Aśvinī", "Bharani": "Bharaṇī", "Krittika": "Kṛttikā",
    "Rohini": "Rohiṇī", "Mrigashira": "Mṛgaśīrṣa", "Ardra": "Ārdrā",
    "Punarvasu": "Punarvasu", "Pushya": "Puṣya", "Ashlesha": "Āśleṣā",
    "Magha": "Maghā", "Purva Phalguni": "Pūrva Phālgunī",
    "Uttara Phalguni": "Uttara Phālgunī", "Hasta": "Hasta",
    "Chitra": "Citrā", "Swati": "Svātī", "Vishakha": "Viśākhā",
    "Anuradha": "Anurādhā", "Jyeshtha": "Jyeṣṭhā", "Mula": "Mūla",
    "Purva Ashadha": "Pūrvāṣāḍhā", "Uttara Ashadha": "Uttarāṣāḍhā",
    "Shravana": "Śravaṇa", "Dhanishta": "Dhaniṣṭhā",
    "Shatabhisha": "Śatabhiṣā", "Purva Bhadrapada": "Pūrva Bhādrapadā",
    "Uttara Bhadrapada": "Uttara Bhādrapadā", "Revati": "Revatī",
}

# Reverse map: IAST → ITRANS (for CSV lookups from kernel output)
_NAK_ITRANS = {v: k for k, v in _NAK_IAST.items()}

_nak_body_map_raw = _load_csv("yoga/nakshatra_body_map.csv")
NAKSHATRA_BODY_MAP = {row.get("nakshatra", ""): row.get("body_region", "") for row in _nak_body_map_raw if row.get("nakshatra")}

def nak_to_itrans(iast_name):
    """Convert IAST nakshatra name to ITRANS for CSV lookup."""
    return _NAK_ITRANS.get(iast_name, iast_name)

def nak_to_iast(itrans_name):
    """Convert ITRANS nakshatra name to IAST for display."""
    return _NAK_IAST.get(itrans_name, itrans_name)

_GRAHA_IAST = {
    "Sun": "Sūrya", "Moon": "Candra", "Mars": "Maṅgala",
    "Mercury": "Budha", "Jupiter": "Guru", "Venus": "Śukra",
    "Saturn": "Śani", "Rahu": "Rāhu", "Ketu": "Ketu",
    # also accept Sanskrit forms from graha_master.csv
    "Surya": "Sūrya", "Chandra": "Candra", "Mangala": "Maṅgala",
    "Budha": "Budha", "Guru": "Guru", "Shukra": "Śukra",
    "Shani": "Śani",
}

# Build the full nakshatra records — one dict per nakshatra
NAKSHATRA_DATA = []
for row in _nak_raw:
    name_itrans = row.get("nakshatra", "")
    NAKSHATRA_DATA.append({
        "name":     _NAK_IAST.get(name_itrans, name_itrans),
        "name_key": name_itrans,
        "graha":    _GRAHA_IAST.get(row.get("graha", ""), row.get("graha", "")),
        "deity":    row.get("deity", ""),
        "symbol":   row.get("symbol", ""),
        "shakti":   row.get("shakti", ""),
        "guna":     row.get("guna", ""),
        "element":  row.get("element", ""),
        "themes":   row.get("themes", ""),
        "body_region": NAKSHATRA_BODY_MAP.get(name_itrans, ""),
    })

# Flat lists for backward compat (TUI, HTML still index by position)
NAKSHATRAS = [n["name"] for n in NAKSHATRA_DATA]
NAK_LORDS  = [n["graha"] for n in NAKSHATRA_DATA]

# ── Grahas from cosmology/graha_master.csv ───────────────────
_graha_raw = _load_csv("cosmology/graha_master.csv")

GRAHA_DATA = []
for row in _graha_raw:
    eng = row.get("graha", "")
    GRAHA_DATA.append({
        "name":     _GRAHA_IAST.get(eng, eng),
        "name_key": eng,
        "category": row.get("category", ""),
        "element":  row.get("element", ""),
        "guna":     row.get("guna", ""),
        "dosha":    row.get("dosha", ""),
        "vehicle":  row.get("vehicle", ""),
        "weapon":   row.get("weapon", ""),
        "domain":   row.get("domain", ""),
    })

# ── Sacred plants from cosmology/sacred_plants.csv ───────────
_plant_raw = _load_csv("plants/sacred_plants.csv")

PLANT_DATA = []
for row in _plant_raw:
    PLANT_DATA.append({
        "name":    row.get("plant", ""),
        "deity":   row.get("deity", ""),
        "element": row.get("element", ""),
        "use":     row.get("use", ""),
    })

_nakshatra_plant_raw = _load_csv("plants/nakshatra_plants.csv")
NAKSHATRA_PLANT_DATA = []
for row in _nakshatra_plant_raw:
    rec = {
        "nakshatra": row.get("nakshatra", ""),
        "plant": row.get("plant", ""),
        "common_name": row.get("common_name", ""),
        "sanskrit_name": row.get("sanskrit_name", ""),
        "deity": row.get("deity", ""),
        "element": row.get("element", ""),
        "dosha": row.get("dosha", ""),
        "use": row.get("use", ""),
        "mantra": row.get("mantra", ""),
        "body_part": row.get("body_part", ""),
        "metal": row.get("metal", ""),
        "season": row.get("season", ""),
        "growing_notes": row.get("growing_notes", ""),
        "ritual_use": row.get("ritual_use", ""),
        "ayurvedic_use": row.get("ayurvedic_use", ""),
    }
    NAKSHATRA_PLANT_DATA.append(rec)

# ── Tithi deities from astro/tithi_core.csv ──────────────────
_tithi_raw = _load_csv("astro/tithi_core.csv")

# tithi IAST display names (dataset has ITRANS)
_TITHI_IAST = {
    "Pratipada": "Pratipadā", "Dvitiya": "Dvitīyā", "Tritiya": "Tṛtīyā",
    "Chaturthi": "Caturthī", "Panchami": "Pañcamī", "Shashthi": "Ṣaṣṭhī",
    "Saptami": "Saptamī", "Ashtami": "Aṣṭamī", "Navami": "Navamī",
    "Dashami": "Daśamī", "Ekadashi": "Ekādaśī", "Dvadashi": "Dvādaśī",
    "Trayodashi": "Trayodaśī", "Chaturdashi": "Caturdaśī",
    "Purnima": "Pūrṇimā", "Amavasya": "Amāvāsyā",
}

TITHI_DATA = []
for row in _tithi_raw:
    name_itrans = row.get("tithi", "")
    TITHI_DATA.append({
        "name":    _TITHI_IAST.get(name_itrans, name_itrans),
        "deity":   row.get("deity", ""),
    })

# ── Tithi qualities from cosmology/tithi_deities.csv ─────────
_tithi_qual_raw = _load_csv("astro/tithi_deities.csv")
_TITHI_QUALITY = {}
for row in _tithi_qual_raw:
    key = _TITHI_IAST.get(row.get("tithi", ""), row.get("tithi", ""))
    _TITHI_QUALITY[key] = row.get("quality", "")
for td in TITHI_DATA:
    td["quality"] = _TITHI_QUALITY.get(td["name"], "")

# ── Nakṣatra master (gana, dosha, yoni) from cosmology ──────
_nak_master_raw = _load_csv("astro/nakshatra_master.csv")
_NAK_MASTER = {}
for row in _nak_master_raw:
    # key normalization: "Purva_Phalguni" → "Purva Phalguni"
    key = row.get("nakshatra", "").replace("_", " ")
    _NAK_MASTER[key] = {
        "gana":        row.get("gana", ""),
        "dosha":       row.get("dosha", ""),
        "yoni_animal": row.get("yoni_animal", ""),
        "yoni_gender": row.get("yoni_gender", ""),
    }
# merge into NAKSHATRA_DATA
for nd in NAKSHATRA_DATA:
    master = _NAK_MASTER.get(nd["name_key"], {})
    nd["gana"]  = master.get("gana", "")
    nd["dosha"] = master.get("dosha", "")
    nd["yoni"]  = master.get("yoni_animal", "")

# ── Nakṣatra qualities (from /opt/atlas seed) ────────────────
_NAK_QUALITIES = {
    "Ashwini":  ["healing", "speed", "beginnings"],
    "Bharani":  ["transformation", "discipline", "restraint"],
    "Krittika": ["fire", "purification", "cutting"],
    "Rohini":   ["growth", "fertility", "beauty"],
    "Mrigashira":["seeking", "curiosity", "wandering"],
    "Ardra":    ["storm", "intensity", "change"],
    "Punarvasu":["renewal", "return", "restoration"],
    "Pushya":   ["nourishment", "support", "prosperity"],
    "Ashlesha": ["serpent", "coiling", "mystery"],
    "Magha":    ["ancestors", "authority", "heritage"],
    "Purva Phalguni":  ["pleasure", "creativity", "union"],
    "Uttara Phalguni": ["contracts", "friendship", "stability"],
    "Hasta":    ["craft", "skill", "hands"],
    "Chitra":   ["beauty", "design", "architecture"],
    "Swati":    ["wind", "independence", "movement"],
    "Vishakha": ["focus", "achievement", "duality"],
    "Anuradha": ["friendship", "devotion", "cooperation"],
    "Jyeshtha": ["power", "seniority", "protection"],
    "Mula":     ["roots", "destruction", "investigation"],
    "Purva Ashadha":  ["invincibility", "water", "purification"],
    "Uttara Ashadha": ["victory", "truth", "endurance"],
    "Shravana": ["listening", "learning", "transmission"],
    "Dhanishta":["rhythm", "music", "prosperity"],
    "Shatabhisha":    ["healing", "mystery", "seclusion"],
    "Purva Bhadrapada":  ["intensity", "vision", "asceticism"],
    "Uttara Bhadrapada": ["depth", "stability", "patience"],
    "Revati":   ["prosperity", "nurturing", "travel"],
}
for nd in NAKSHATRA_DATA:
    nd["qualities"] = _NAK_QUALITIES.get(nd["name_key"], [])

# ── Graha qualities (from /opt/atlas graha.yaml seed) ────────
_GRAHA_QUALITIES = {
    "Sūrya":   ["authority", "vitality"],
    "Candra":  ["mind", "emotion"],
    "Maṅgala": ["energy", "conflict"],
    "Budha":   ["intellect", "speech"],
    "Guru":    ["wisdom", "expansion"],
    "Śukra":   ["beauty", "pleasure"],
    "Śani":    ["discipline", "restriction"],
    "Rāhu":    ["disruption", "obsession"],
    "Ketu":    ["detachment", "liberation"],
}
for gd in GRAHA_DATA:
    gd["qualities"] = _GRAHA_QUALITIES.get(gd["name"], [])

# ── Vimśottarī Daśā sequence ────────────────────────────────
DASHA_SEQUENCE = [
    ("Ketu", 7), ("Śukra", 20), ("Sūrya", 6), ("Candra", 10),
    ("Maṅgala", 7), ("Rāhu", 18), ("Guru", 16), ("Śani", 19),
    ("Budha", 17),
]
DASHA_TOTAL = 120  # sum of all mahādaśā years


# ══════════════════════════════════════════════════════════════
# JYOTIṢA — natal, transits, daśā, muhūrta quality
# Falls back to mean-motion estimates when no ephemeris is installed.
# ══════════════════════════════════════════════════════════════

JYOTISHA_BIRTH = {
    "birth_date": "1983-01-27",
    "birth_time": "11:57",
    "birth_place": "Montreal, Quebec, Canada",
    "lat": 45.5017,
    "lon": -73.5673,
}

NATAL = {
    "lagna": "Vṛṣabha",
    "lagna_nak": "Rohiṇī pada 1",
    "sun": {"rashi": "Makara", "nak": "Śravaṇa", "pada": 2},
    "moon": {"rashi": "Mithuna", "nak": "Punarvasu", "pada": 2},
    "mars": {"rashi": "Kumbha", "nak": "Śatabhiṣā", "pada": 3},
    "mercury": {"rashi": "Dhanu", "nak": "Pūrvāṣāḍhā", "pada": 3, "combust": True},
    "jupiter": {"rashi": "Vṛścika", "nak": "Anurādhā", "pada": 3},
    "venus": {"rashi": "Kumbha", "nak": "Dhaniṣṭhā", "pada": 4},
    "saturn": {"rashi": "Tulā", "nak": "Svātī", "pada": 2, "exalted": True},
    "rahu": {"rashi": "Mithuna", "nak": "Ārdrā", "pada": 1, "retrograde": True},
    "ketu": {"rashi": "Dhanu", "nak": "Mūla", "pada": 3, "retrograde": True},
    "dasha": {"lord": "Budha", "balance_years": 1.58, "closes": "2027-10"},
}

_GRAHA_KEYS = ("sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu")
_GRAHA_LABELS = {
    "sun": "Sūrya",
    "moon": "Candra",
    "mars": "Maṅgala",
    "mercury": "Budha",
    "jupiter": "Guru",
    "venus": "Śukra",
    "saturn": "Śani",
    "rahu": "Rāhu",
    "ketu": "Ketu",
}
_LORD_TO_KEY = {v: k for k, v in _GRAHA_LABELS.items()}
_EXALTATION_SIGNS = {
    "sun": "Meṣa",
    "moon": "Vṛṣabha",
    "mars": "Makara",
    "mercury": "Kanyā",
    "jupiter": "Karka",
    "venus": "Mīna",
    "saturn": "Tulā",
}
_FALLBACK_GRAHA_MOTION = {
    "sun": {"base_lon": 280.0, "deg_per_day": 0.9856},
    "moon": {"base_lon": 0.0, "deg_per_day": 13.1764},
    "mars": {"base_lon": 110.0, "deg_per_day": 0.5240},
    "mercury": {"base_lon": 250.0, "deg_per_day": 1.6100},
    "jupiter": {"base_lon": 208.0, "deg_per_day": 0.0831},
    "venus": {"base_lon": 200.0, "deg_per_day": 1.1800},
    "saturn": {"base_lon": 183.0, "deg_per_day": 0.0334},
    "rahu": {"base_lon": 80.0, "deg_per_day": -0.05295},
}
_TRANSIT_REFERENCE = datetime(2025, 1, 13, 0, 0)
_NAK_SIZE = 360.0 / 27.0
_PADA_SIZE = _NAK_SIZE / 4.0


def _normalize_lon(lon):
    return lon % 360.0


def _rashi_from_lon(lon):
    return RASHIS[int(_normalize_lon(lon) // 30.0) % 12]


def _nak_from_lon(lon):
    return NAKSHATRAS[int(_normalize_lon(lon) // _NAK_SIZE) % 27]


def _pada_from_lon(lon):
    return int((_normalize_lon(lon) % _NAK_SIZE) // _PADA_SIZE) + 1


def _longitude_from_nak_pada(nak_name, pada):
    nak_idx = NAKSHATRAS.index(nak_name)
    return _normalize_lon(nak_idx * _NAK_SIZE + (max(1, min(4, int(pada))) - 1) * _PADA_SIZE + (_PADA_SIZE / 2.0))


def _parse_lagna_nak(text):
    m = _re.match(r"(.+?)\s+pada\s+(\d+)", str(text))
    if not m:
        return {"nak": str(text), "pada": None}
    return {"nak": m.group(1).strip(), "pada": int(m.group(2))}


def _natal_points():
    lagna = _parse_lagna_nak(NATAL.get("lagna_nak", ""))
    points = {
        "lagna": {
            "rashi": NATAL.get("lagna"),
            "nak": lagna.get("nak"),
            "pada": lagna.get("pada"),
        }
    }
    for key in _GRAHA_KEYS:
        points[key] = dict(NATAL.get(key, {}))
    return points


def _enrich_graha_position(key, lon, speed):
    rashi = _rashi_from_lon(lon)
    nak = _nak_from_lon(lon)
    pada = _pada_from_lon(lon)
    rec = {
        "graha": _GRAHA_LABELS.get(key, key.title()),
        "longitude": round(_normalize_lon(lon), 2),
        "speed_deg_per_day": round(speed, 4),
        "rashi": rashi,
        "nak": nak,
        "pada": pada,
        "retrograde": speed < 0,
    }
    if key in _EXALTATION_SIGNS:
        rec["exalted"] = (rashi == _EXALTATION_SIGNS[key])
    return rec


def _mean_motion_transits(now=None):
    if now is None:
        now = datetime.now()
    days = (now - _TRANSIT_REFERENCE).total_seconds() / 86400.0
    transits = {}
    for key, spec in _FALLBACK_GRAHA_MOTION.items():
        lon = _normalize_lon(spec["base_lon"] + spec["deg_per_day"] * days)
        transits[key] = _enrich_graha_position(key, lon, spec["deg_per_day"])
    ketu_lon = _normalize_lon(transits["rahu"]["longitude"] + 180.0)
    transits["ketu"] = _enrich_graha_position("ketu", ketu_lon, -_FALLBACK_GRAHA_MOTION["rahu"]["deg_per_day"])
    return transits


def _natal_longitude(key):
    point = _natal_points()[key]
    return _longitude_from_nak_pada(point["nak"], point["pada"])


def _aspect_name(delta):
    if delta <= 8:
        return "conjunction"
    if abs(delta - 180) <= 8:
        return "opposition"
    if abs(delta - 120) <= 7:
        return "trine"
    if abs(delta - 90) <= 6:
        return "square"
    if abs(delta - 60) <= 5:
        return "sextile"
    return None


def _format_transit_hit(transit_key, natal_key, aspect, orb, transit_rec, natal_rec):
    graha_label = _GRAHA_LABELS.get(transit_key, transit_key.title())
    natal_label = "Lagna" if natal_key == "lagna" else _GRAHA_LABELS.get(natal_key, natal_key.title())
    pieces = [f"{graha_label} {aspect} natal {natal_label}"]
    pieces.append(f"{transit_rec['rashi']} → {natal_rec['rashi']}")
    if transit_rec["nak"] == natal_rec["nak"]:
        pieces.append(f"same nakṣatra {transit_rec['nak']}")
    pieces.append(f"orb {orb:.1f}°")
    return " · ".join(pieces)


def get_transit_data(now=None):
    if now is None:
        now = datetime.now()
    provider = "fallback: mean-motion"
    transits = _mean_motion_transits(now)
    natal_points = _natal_points()
    hits = []
    for transit_key, transit_rec in transits.items():
        transit_lon = transit_rec["longitude"]
        for natal_key, natal_rec in natal_points.items():
            natal_lon = _natal_longitude(natal_key)
            diff = abs(_normalize_lon(transit_lon - natal_lon))
            delta = min(diff, 360.0 - diff)
            aspect = _aspect_name(delta)
            if not aspect:
                continue
            hit = {
                "transit": transit_key,
                "transit_graha": transit_rec["graha"],
                "natal_point": natal_key,
                "aspect": aspect,
                "orb": round(delta if aspect == "conjunction" else abs(delta - {"opposition": 180, "trine": 120, "square": 90, "sextile": 60}.get(aspect, 0)), 2),
                "transit_rashi": transit_rec["rashi"],
                "natal_rashi": natal_rec["rashi"],
                "transit_nak": transit_rec["nak"],
                "natal_nak": natal_rec["nak"],
            }
            hit["summary"] = _format_transit_hit(
                transit_key,
                natal_key,
                aspect,
                hit["orb"],
                transit_rec,
                natal_rec,
            )
            score = {"conjunction": 5, "opposition": 4, "trine": 3, "square": 3, "sextile": 2}.get(aspect, 1)
            if transit_rec["nak"] == natal_rec["nak"]:
                score += 1
            hit["score"] = score
            hits.append(hit)
    hits.sort(key=lambda item: (-item["score"], item["orb"], item["transit_graha"], item["natal_point"]))
    return {
        "provider": provider,
        "timestamp": now.isoformat(),
        "birth": dict(JYOTISHA_BIRTH),
        "natal": NATAL,
        "positions": transits,
        "hits": hits,
    }


def get_current_dasha(now=None):
    if now is None:
        now = datetime.now()
    anchor = NATAL.get("dasha", {})
    anchor_lord = anchor.get("lord", "Budha")
    anchor_close = datetime.strptime(f"{anchor.get('closes', '2027-10')}-01", "%Y-%m-%d")
    idx = [lord for lord, _ in DASHA_SEQUENCE].index(anchor_lord)
    years = DASHA_SEQUENCE[idx][1]
    start = anchor_close - timedelta(days=years * 365.2425)
    end = anchor_close
    while now >= end:
        idx = (idx + 1) % len(DASHA_SEQUENCE)
        start = end
        years = DASHA_SEQUENCE[idx][1]
        end = start + timedelta(days=years * 365.2425)
    while now < start:
        idx = (idx - 1) % len(DASHA_SEQUENCE)
        end = start
        years = DASHA_SEQUENCE[idx][1]
        start = end - timedelta(days=years * 365.2425)
    maha_lord = DASHA_SEQUENCE[idx][0]
    balance_years = max(0.0, (end - now).total_seconds() / (365.2425 * 86400.0))
    sub_idx = idx
    sub_start = start
    antardasha_lord = maha_lord
    antardasha_end = end
    for step in range(len(DASHA_SEQUENCE)):
        lord, sub_years = DASHA_SEQUENCE[(idx + step) % len(DASHA_SEQUENCE)]
        sub_duration = years * sub_years / DASHA_TOTAL
        candidate_end = sub_start + timedelta(days=sub_duration * 365.2425)
        if now < candidate_end or step == len(DASHA_SEQUENCE) - 1:
            sub_idx = (idx + step) % len(DASHA_SEQUENCE)
            antardasha_lord = lord
            antardasha_end = candidate_end
            break
        sub_start = candidate_end
    antardasha_balance = max(0.0, (antardasha_end - now).total_seconds() / (365.2425 * 86400.0))
    return {
        "provider": "natal anchor",
        "lord": maha_lord,
        "mahadasha": maha_lord,
        "antardasha": DASHA_SEQUENCE[sub_idx][0],
        "balance": round(balance_years, 2),
        "balance_years": round(balance_years, 2),
        "closes": end.strftime("%Y-%m"),
        "started": start.strftime("%Y-%m"),
        "antardasha_closes": antardasha_end.strftime("%Y-%m"),
        "antardasha_balance_years": round(antardasha_balance, 2),
    }


def get_muhurta_quality(now=None):
    if now is None:
        now = datetime.now()
    fs = field_state(now)
    dasha = get_current_dasha(now)
    transit_data = get_transit_data(now)
    mu = fs["muhurta"]
    score = 50
    reasons = []
    if mu["name"] == "Brahma Muhūrta":
        score += 18
        reasons.append("Brahma Muhūrta strongly supports sādhana and clear judgment")
    elif mu["name"] == "Abhijit":
        score += 14
        reasons.append("Abhijit supports decisive work and clean execution")
    elif mu["name"] == "Sāyaṃ Sandhyā":
        score += 10
        reasons.append("Sandhyā favors alignment, prayer, and course correction")
    top_hits = transit_data["hits"][:3]
    if top_hits:
        score += min(15, sum(hit["score"] for hit in top_hits))
        reasons.extend(hit["summary"] for hit in top_hits[:2])
    if dasha["lord"] == "Budha":
        score += 8
        reasons.append("Budha mahādaśā rewards study, writing, systems work, and synthesis")
    score = max(0, min(100, score))
    quality = "excellent" if score >= 78 else "strong" if score >= 64 else "mixed" if score >= 46 else "difficult"
    return {
        "score": score,
        "quality": quality,
        "muhurta": mu,
        "dasha": dasha,
        "transit_hits": top_hits,
        "reasons": reasons,
    }

# Build 30-tithi cycle: Śukla 1-15 then Kṛṣṇa 1-15
# tithi_core.csv has 15 tithis + Pūrṇimā + Amāvāsyā (17 entries)
# Map to the 30-beat cycle used by calc_panchanga
_tithi_names_15 = [td["name"] for td in TITHI_DATA[:15]]
_tithi_deities_15 = [td["deity"] for td in TITHI_DATA[:15]]
# Amāvāsyā is the last entry
_amavasya = TITHI_DATA[-1] if TITHI_DATA else {"name": "Amāvāsyā", "deity": "Pitris"}

TITHIS = _tithi_names_15 + _tithi_names_15[:14] + [_amavasya["name"]]
TITHI_DEITIES = _tithi_deities_15 + _tithi_deities_15[:14] + [_amavasya["deity"]]

# ── Vedic concepts from vedic_concepts.yaml (read as text) ───
# (yaml is optional — avoid hard dep; parse the simple structure)
_vedic_path = _DATA / "vedic_concepts.yaml"
VEDIC_SCHOOLS = []
if _vedic_path.exists():
    _section = None
    _current = None
    for line in _vedic_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("schools:"):
            _section = "schools"
        elif stripped.startswith("concepts:"):
            _section = "concepts"
        elif _section == "schools" and stripped.startswith("- name:"):
            if _current:
                VEDIC_SCHOOLS.append(_current)
            _current = {"name": stripped.split(":", 1)[1].strip()}
        elif _current and stripped.startswith("founder:"):
            _current["founder"] = stripped.split(":", 1)[1].strip()
        elif _current and stripped.startswith("core_idea:"):
            _current["core_idea"] = stripped.split(":", 1)[1].strip()
        elif _current and stripped.startswith("oneness:"):
            _current["oneness"] = float(stripped.split(":", 1)[1].strip())
        elif _current and stripped.startswith("difference:"):
            _current["difference"] = float(stripped.split(":", 1)[1].strip())
    if _current:
        VEDIC_SCHOOLS.append(_current)


# ══════════════════════════════════════════════════════════════
# ENTITY INDEXING — normalize graph entities for apps/APIs
# ══════════════════════════════════════════════════════════════

_GRAHA_BIJA = {
    row.get("graha", ""): row.get("bija", "")
    for row in _load_csv("gandharva/graha_bija.csv")
}

_NAKSHATRA_SYLLABLES = {}
for row in _load_csv("astro/nakshatra_syllables.csv"):
    key = row.get("nakshatra", "")
    _NAKSHATRA_SYLLABLES.setdefault(key, []).append(row.get("sound", ""))

_NAKSHATRA_PLANTS = {
    "Ashwini": "Kuchala / Kanjiram",
    "Bharani": "Amalaki",
    "Krittika": "Udumbara",
    "Rohini": "Jambu / Jamun",
    "Mrigashira": "Khadira / Khair",
    "Ardra": "Agaru / Aguru",
    "Punarvasu": "Bamboo",
    "Pushya": "Ashvattha / Pipal",
    "Ashlesha": "Nagakeshara",
    "Magha": "Vata / Banyan",
    "Purva Phalguni": "Palasha",
    "Uttara Phalguni": "Rudraksha",
    "Hasta": "Arishta / Reetha",
    "Chitra": "Bilva / Bael",
    "Swati": "Arjuna",
    "Vishakha": "Kapittha / Wood-apple",
    "Anuradha": "Bakula / Maulsari",
    "Jyeshtha": "Shalmali / Silk-cotton",
    "Mula": "Sala / Sal",
    "Purva Ashadha": "Vetas / Vañjula",
    "Uttara Ashadha": "Panasa / Jackfruit",
    "Shravana": "Arka",
    "Dhanishta": "Shami / Khejri",
    "Shatabhisha": "Kadamba",
    "Purva Bhadrapada": "Mango",
    "Uttara Bhadrapada": "Nimba / Neem",
    "Revati": "Madhu / Mahua",
}

_GRAHA_BODY_PARTS = {
    "Sūrya": ["eyes", "heart", "vitality"],
    "Candra": ["mind", "chest", "fluids"],
    "Maṅgala": ["blood", "muscles", "adrenals"],
    "Budha": ["nervous system", "skin", "speech"],
    "Guru": ["liver", "fat tissue", "wisdom channels"],
    "Śukra": ["reproductive system", "kidneys", "ojas"],
    "Śani": ["bones", "teeth", "legs"],
    "Rāhu": ["breath", "nerves", "toxicity thresholds"],
    "Ketu": ["spine", "subtle channels", "detachment reflex"],
}

_ELEMENT_BODY_PARTS = {
    "fire": ["eyes", "digestion", "metabolic heat"],
    "earth": ["bones", "muscle tone", "structural tissue"],
    "water": ["blood", "reproductive tissue", "lymph"],
    "air": ["lungs", "nerves", "circulation"],
    "ether": ["throat", "ears", "subtle channels"],
}

_TITHI_SWARAS = {
    1: "aṁ",
    2: "āṁ",
    3: "iṁ",
    4: "īṁ",
    5: "uṁ",
    6: "ūṁ",
    7: "ṛṁ",
    8: "ṝṁ",
    9: "ḷṁ",
    10: "ḹṁ",
    11: "eṁ",
    12: "aiṁ",
    13: "oṁ",
    14: "auṁ",
    15: "aḥ",
}

_TITHI_ELEMENT_CYCLE = {
    1: "fire",
    2: "earth",
    3: "ether",
    4: "water",
    5: "air",
}

_TITHI_GUNA_CYCLE = {
    1: "rajas",
    2: "rajas",
    3: "rajas",
    4: "rajas",
    5: "rajas",
    6: "tamas",
    7: "tamas",
    8: "tamas",
    9: "tamas",
    10: "tamas",
    11: "sattva",
    12: "sattva",
    13: "sattva",
    14: "sattva",
    15: "sattva",
}

COMPANIONS = {
    "bandhu_bhai": {
        "name": "Bandhu Bhai",
        "role": "system awareness companion",
        "mode": "reads the field",
    },
    "shilpi_bhai": {
        "name": "Shilpi Bhai",
        "role": "artifact builder companion",
        "mode": "builds from the field",
    },
}


def _slugify(text):
    """ASCII slug for fuzzy entity lookup across APIs/apps."""
    text = unicodedata.normalize("NFKD", str(text or ""))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower().replace("&", " and ")
    text = _re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


for _plant in NAKSHATRA_PLANT_DATA:
    _plant["id"] = f"plant:{_slugify(_plant.get('plant') or _plant.get('nakshatra'))}"


_PLANT_BY_NAKSHATRA = {row["nakshatra"]: row for row in NAKSHATRA_PLANT_DATA if row.get("nakshatra")}
_PLANT_BY_SLUG = {}
_NAKSHATRA_NAME_ALIASES = {}
for _nak in NAKSHATRA_DATA:
    if _nak.get("name"):
        _NAKSHATRA_NAME_ALIASES[_slugify(_nak["name"])] = _nak.get("name_key", "").replace("_", " ")
    if _nak.get("name_key"):
        _NAKSHATRA_NAME_ALIASES[_slugify(_nak["name_key"])] = _nak.get("name_key", "").replace("_", " ")
for _plant in NAKSHATRA_PLANT_DATA:
    for _key in (
        _plant.get("plant", ""),
        _plant.get("common_name", ""),
        _plant.get("sanskrit_name", ""),
        _plant.get("nakshatra", ""),
        _plant.get("id", ""),
    ):
        if _key:
            _PLANT_BY_SLUG[_slugify(_key)] = _plant

_VARA_GRAHA_NAME = {
    0: "Candra",
    1: "Maṅgala",
    2: "Budha",
    3: "Guru",
    4: "Śukra",
    5: "Śani",
    6: "Sūrya",
}
_VARA_PLANTS = {
    "Sūrya": {
        "plant": "Arka",
        "common_name": "Crown flower",
        "deity": "Sūrya",
        "element": "Fire",
        "dosha": "Pitta",
        "use": "ritual",
        "guidance": "Offer red or orange flowers at sunrise.",
    },
    "Candra": {
        "plant": "Lotus",
        "common_name": "Lotus",
        "deity": "Candra",
        "element": "Water",
        "dosha": "Pitta",
        "use": "cooling",
        "guidance": "Use white flowers and gentle watering practices.",
    },
    "Maṅgala": {
        "plant": "Khadira",
        "common_name": "Cutch tree",
        "deity": "Maṅgala",
        "element": "Fire",
        "dosha": "Vata",
        "use": "strength",
        "guidance": "Channel surplus heat into pruning or repair work.",
    },
    "Budha": {
        "plant": "Tulsi",
        "common_name": "Holy basil",
        "deity": "Budha",
        "element": "Air",
        "dosha": "Kapha",
        "use": "clarity",
        "guidance": "Harvest lightly and use for study or writing practice.",
    },
    "Guru": {
        "plant": "Banana",
        "common_name": "Banana",
        "deity": "Bṛhaspati",
        "element": "Earth",
        "dosha": "Kapha",
        "use": "ritual",
        "guidance": "Eat banana and offer yellow flowers.",
    },
    "Śukra": {
        "plant": "Jasmine",
        "common_name": "Jasmine",
        "deity": "Śukra",
        "element": "Water",
        "dosha": "Kapha",
        "use": "beauty",
        "guidance": "Favor fragrance, beauty, and gentle pleasure in offerings.",
    },
    "Śani": {
        "plant": "Neem",
        "common_name": "Neem",
        "deity": "Śani",
        "element": "Air",
        "dosha": "Pitta",
        "use": "discipline",
        "guidance": "Choose bitter, cleansing support and boundary care.",
    },
}
_TITHI_PLANTS = {
    "Pratipadā": {"plant": "Tulsi", "deity": "Lakshmi", "element": "Water", "use": "auspicious_start", "guidance": "Light a lamp and begin cleanly."},
    "Dvitīyā": {"plant": "Amla", "deity": "Brahma", "element": "Earth", "use": "renewal", "guidance": "Favor nourishing food and stabilizing routines."},
    "Tṛtīyā": {"plant": "Jasmine", "deity": "Gauri", "element": "Water", "use": "beauty", "guidance": "Offer fragrant flowers and cultivate softness."},
    "Caturthī": {"plant": "Durva grass", "deity": "Gaṇeśa", "element": "Earth", "use": "ritual", "guidance": "Offer 21 blades to Gaṇeśa today."},
    "Pañcamī": {"plant": "Neem", "deity": "Nāgas", "element": "Air", "use": "protection", "guidance": "Use protective herbs and clear pests or toxins."},
    "Ṣaṣṭhī": {"plant": "Bilva", "deity": "Skanda", "element": "Fire", "use": "strength", "guidance": "Make disciplined offerings and finish what is pending."},
    "Saptamī": {"plant": "Arka", "deity": "Sūrya", "element": "Fire", "use": "solar", "guidance": "Perform sunrise water offering and face the east."},
    "Aṣṭamī": {"plant": "Neem", "deity": "Durga", "element": "Air", "use": "healing", "guidance": "Choose bitter-cleansing support and protection work."},
    "Navamī": {"plant": "Ashoka", "deity": "Durga", "element": "Fire", "use": "courage", "guidance": "Use flowers in protective worship and clean action."},
    "Daśamī": {"plant": "Shami", "deity": "Vijaya", "element": "Air", "use": "victory", "guidance": "Honor tools, weapons, and work instruments."},
    "Ekādaśī": {"plant": "Tulsi", "deity": "Viṣṇu", "element": "Water", "use": "fasting", "guidance": "Fast lightly and offer Tulsi leaves to Viṣṇu."},
    "Dvādaśī": {"plant": "Banana", "deity": "Viṣṇu", "element": "Earth", "use": "restoration", "guidance": "Break fast gently and offer yellow or white flowers."},
    "Trayodaśī": {"plant": "Bilva", "deity": "Śiva", "element": "Earth", "use": "ritual", "guidance": "Offer bilva leaves and simplify the mind."},
    "Caturdaśī": {"plant": "Darbha grass", "deity": "Śiva", "element": "Fire", "use": "purification", "guidance": "Favor austerity, clearing, and consecration."},
    "Pūrṇimā": {"plant": "Lotus", "deity": "Candra", "element": "Water", "use": "soma", "guidance": "Moon rituals and cooling flowers are favored."},
    "Amāvāsyā": {"plant": "Peepal", "deity": "Pitṛs", "element": "Earth", "use": "ancestral", "guidance": "Ancestor offerings and sesame oil lamps are favored."},
}
_DOSHA_RECOMMENDATIONS = {
    "vata": {
        "recommended": "warm, grounding, oily",
        "avoid": "cold, raw, dry",
        "herbs": ["Ashwagandha", "Sesame", "Triphala"],
    },
    "pitta": {
        "recommended": "cooling, sweet, bitter",
        "avoid": "fried, sour, overheated",
        "herbs": ["Amalaki", "Brahmi", "Coriander"],
    },
    "kapha": {
        "recommended": "light, warming, stimulating",
        "avoid": "heavy, cold, overly sweet",
        "herbs": ["Tulsi", "Ginger", "Trikatu"],
    },
}

_SYMBOL_MEANINGS = {
    "horse_head": "swift medicine, threshold passage, and instinctive movement",
    "yoni": "containment, gestation, and the power to bear karma into form",
    "razor": "purification by cutting away what no longer belongs",
    "chariot": "fertility, beauty, and creation moving into embodied form",
    "deer_head": "searching mind, tenderness, and subtle pursuit",
    "teardrop": "storm, grief, and the release that opens renewal",
    "quiver": "returning resources, stored force, and second beginnings",
    "lotus": "nourishment, unfoldment, and spiritual prosperity",
}
_NAKSHATRA_MANTRAS = {
    "Aśvinī": "ॐ अश्विन्यै नमः",
    "Bharaṇī": "ॐ भरण्यै नमः",
    "Kṛttikā": "ॐ कृत्तिकायै नमः",
    "Rohiṇī": "ॐ रोहिण्यै नमः",
    "Mṛgaśīrṣa": "ॐ मृगशीर्षाय नमः",
    "Ārdrā": "ॐ आर्द्रायै नमः",
    "Punarvasu": "ॐ पुनर्वसवे नमः",
    "Puṣya": "ॐ पुष्याय नमः",
    "Āśleṣā": "ॐ आश्लेषायै नमः",
    "Maghā": "ॐ मघायै नमः",
    "Pūrva Phālgunī": "ॐ पूर्वफल्गुन्यै नमः",
    "Uttara Phālgunī": "ॐ उत्तरफल्गुन्यै नमः",
    "Hasta": "ॐ हस्ताय नमः",
    "Citrā": "ॐ चित्रायै नमः",
    "Svātī": "ॐ स्वात्यै नमः",
    "Viśākhā": "ॐ विशाखायै नमः",
    "Anurādhā": "ॐ अनुराधायै नमः",
    "Jyeṣṭhā": "ॐ ज्येष्ठायै नमः",
    "Mūla": "ॐ मूलाय नमः",
    "Pūrvāṣāḍhā": "ॐ पूर्वाषाढायै नमः",
    "Uttarāṣāḍhā": "ॐ उत्तराषाढायै नमः",
    "Śravaṇa": "ॐ श्रवणाय नमः",
    "Dhaniṣṭhā": "ॐ धनिष्ठायै नमः",
    "Śatabhiṣā": "ॐ शतभिषाय नमः",
    "Pūrva Bhādra": "ॐ पूर्वभाद्रपदायै नमः",
    "Uttara Bhādra": "ॐ उत्तरभाद्रपदायै नमः",
    "Revatī": "ॐ रेवत्यै नमः",
}
_GRAHA_PROFILE = {
    "Sūrya": {"body_part": "eyes", "metal": "gold", "gem": "ruby", "color": "deep red", "weekday": "Ravivāra", "friends": ["Candra", "Maṅgala", "Guru"], "enemies": ["Śukra", "Śani"], "exaltation": "Meṣa", "debilitation": "Tulā", "yantra": "solar square", "mantra": "ॐ सूर्याय नमः"},
    "Candra": {"body_part": "mind", "metal": "silver", "gem": "pearl", "color": "white", "weekday": "Somavāra", "friends": ["Sūrya", "Budha"], "enemies": [], "exaltation": "Vṛṣabha", "debilitation": "Vṛścika", "yantra": "lunar circle", "mantra": "ॐ चन्द्राय नमः"},
    "Maṅgala": {"body_part": "blood", "metal": "copper", "gem": "red coral", "color": "vermilion", "weekday": "Maṅgalavāra", "friends": ["Sūrya", "Candra", "Guru"], "enemies": ["Budha"], "exaltation": "Makara", "debilitation": "Karka", "yantra": "triangular spear grid", "mantra": "ॐ मङ्गलाय नमः"},
    "Budha": {"body_part": "skin", "metal": "bronze", "gem": "emerald", "color": "green", "weekday": "Budhavāra", "friends": ["Sūrya", "Śukra"], "enemies": ["Candra"], "exaltation": "Kanyā", "debilitation": "Mīna", "yantra": "mercurial octagon", "mantra": "ॐ बुधाय नमः"},
    "Guru": {"body_part": "liver", "metal": "gold", "gem": "yellow sapphire", "color": "yellow", "weekday": "Guruvāra", "friends": ["Sūrya", "Candra", "Maṅgala"], "enemies": ["Budha", "Śukra"], "exaltation": "Karka", "debilitation": "Makara", "yantra": "teacher’s mandala", "mantra": "ॐ बृहस्पतये नमः"},
    "Śukra": {"body_part": "reproductive system", "metal": "silver", "gem": "diamond", "color": "clear white", "weekday": "Śukravāra", "friends": ["Budha", "Śani"], "enemies": ["Sūrya", "Candra"], "exaltation": "Mīna", "debilitation": "Kanyā", "yantra": "lotus hexagon", "mantra": "ॐ शुक्राय नमः"},
    "Śani": {"body_part": "bones", "metal": "iron", "gem": "blue sapphire", "color": "indigo", "weekday": "Śanivāra", "friends": ["Budha", "Śukra"], "enemies": ["Sūrya", "Candra", "Maṅgala"], "exaltation": "Tulā", "debilitation": "Meṣa", "yantra": "saturnine lattice", "mantra": "ॐ शनैश्चराय नमः"},
    "Rāhu": {"body_part": "breath", "metal": "lead", "gem": "hessonite", "color": "smoke", "weekday": "shadow", "friends": ["Śukra", "Śani"], "enemies": ["Sūrya", "Candra"], "exaltation": "Vṛṣabha", "debilitation": "Vṛścika", "yantra": "eclipse vortex", "mantra": "ॐ राहवे नमः"},
    "Ketu": {"body_part": "spine", "metal": "mixed alloy", "gem": "cat's eye", "color": "ashen red", "weekday": "shadow", "friends": ["Maṅgala", "Guru"], "enemies": ["Sūrya", "Candra"], "exaltation": "Vṛścika", "debilitation": "Vṛṣabha", "yantra": "moksha blade", "mantra": "ॐ केतवे नमः"},
}
_DEVI_YANTRAS = {
    "Kāmeśvarī": "bindu with opening triangle",
    "Bhagamālinī": "solar garland mandala",
    "Nityāklinā": "soma crescent triangle",
    "Bheruṇḍā": "double thunderbolt yantra",
    "Vahnivasini": "agni triangle wheel",
    "Mahāvajreśvarī": "vajra diamond lattice",
    "Śivadūtī": "messenger bridge yantra",
    "Tvaritā": "swift spiral yantra",
    "Kulasundarī": "lineage lotus yantra",
    "Nityā": "eternal bindu wheel",
    "Nīlapatākā": "banner and axis yantra",
    "Vijayā": "victory gate yantra",
    "Sarvamangalā": "auspicious lotus field",
    "Jvālāmālinī": "fire garland ring",
    "Citrā": "full spectrum mandala",
}


def _today_anchor(fs):
    p5 = fs["panchanga"]
    return {
        "devi": _devi_field(p5["devi"], 0),
        "nakshatra": p5["nakshatra"],
        "nak_lord": p5["nak_lord"],
        "tithi": p5["tithi"],
        "element": (p5.get("nak_data") or {}).get("element", "").lower(),
        "guna": (p5.get("nak_data") or {}).get("guna", "").lower(),
        "raga": fs.get("devi_raga", ""),
        "muhurta_raga": fs.get("muhurta_raga", ""),
    }


def _devi_records():
    records = []
    for idx, (name, emoji, process, raga) in enumerate(NITYA_DEVIS, start=1):
        element = _TITHI_ELEMENT_CYCLE[((idx - 1) % 5) + 1]
        records.append({
            "id": f"devi:{_slugify(name)}",
            "slug": _slugify(name),
            "type": "devi",
            "name": name,
            "emoji": emoji,
            "process": process,
            "raga": raga,
            "tithi_number": idx,
            "tithi_name": TITHIS[idx - 1] if idx - 1 < len(TITHIS) else "",
            "paksha": "Śukla",
            "element": element,
            "guna": _TITHI_GUNA_CYCLE[idx],
            "body_parts": _ELEMENT_BODY_PARTS.get(element, []),
            "mantra": f"oṁ aiṁ hrīṁ śrīṁ {_TITHI_SWARAS.get(idx, 'aiṁ')} {_slugify(name).replace('-', '')}yai namaḥ",
        })
    return records


DEVI_DATA = _devi_records()


def _entity_indexes():
    by_slug = {}
    def _add(keys, payload):
        for key in keys:
            if not key:
                continue
            slug = _slugify(key)
            by_slug[slug] = payload
            by_slug[slug.replace("-", "")] = payload
    for row in NAKSHATRA_DATA:
        keys = {
            row["name"],
            row.get("name_key", ""),
            f"nakshatra:{row.get('name_key', '')}",
            f"nakshatra:{row['name']}",
        }
        _add(keys, ("nakshatra", row))
    for row in GRAHA_DATA:
        keys = {
            row["name"],
            row.get("name_key", ""),
            f"graha:{row.get('name_key', '')}",
            f"graha:{row['name']}",
        }
        sanskrit_aliases = {
            "Sūrya": "surya",
            "Candra": "chandra",
            "Maṅgala": "mangala",
            "Budha": "budha",
            "Guru": "guru",
            "Śukra": "shukra",
            "Śani": "shani",
            "Rāhu": "rahu",
            "Ketu": "ketu",
        }
        alias = sanskrit_aliases.get(row["name"])
        if alias:
            keys.add(alias)
            keys.add(f"graha:{alias}")
        _add(keys, ("graha", row))
    for row in DEVI_DATA:
        keys = {row["name"], row["id"], row["slug"]}
        if "sv" in row["slug"]:
            keys.add(row["slug"].replace("sv", "shv"))
            keys.add(row["id"].replace("sv", "shv"))
        _add(keys, ("devi", row))
    for row in NAKSHATRA_PLANT_DATA:
        keys = {
            row.get("plant", ""),
            row.get("common_name", ""),
            row.get("sanskrit_name", ""),
            row.get("nakshatra", ""),
            row.get("id", ""),
            f"plant:{row.get('plant', '')}",
        }
        _add(keys, ("plant", row))
    return by_slug


ENTITY_INDEX = _entity_indexes()


def _element_matched_plants(element, limit=3):
    element = (element or "").lower()
    matches = [pl["name"] for pl in PLANT_DATA if pl.get("element", "").lower() == element]
    return matches[:limit]


def _florida_season(now=None):
    now = now or datetime.now()
    month = now.month
    if month in (12, 1, 2):
        return "winter"
    if month in (3, 4, 5):
        return "spring"
    if month in (6, 7, 8):
        return "summer"
    return "autumn"


def _seasonal_plants(now=None):
    season = _florida_season(now)
    season_map = {
        "winter": ["Tulsi", "Neem", "Amla", "Banyan", "Peepal"],
        "spring": ["Ashwagandha", "Jasmine", "Arka", "Mango", "Neem"],
        "summer": ["Banana", "Lotus", "Tulsi", "Jackfruit", "Kadamba"],
        "autumn": ["Bilva", "Shami", "Bamboo", "Arjuna", "Wood Apple"],
    }
    names = season_map.get(season, [])
    items = []
    for name in names:
        plant = _PLANT_BY_SLUG.get(_slugify(name))
        if plant:
            items.append(plant)
    return season, items


def _lookup_plant(value):
    if not value:
        return None
    slug = _slugify(value)
    alias = _NAKSHATRA_NAME_ALIASES.get(slug)
    # Try IAST→ITRANS conversion for nakshatra lookup (fixes /plants/today bug)
    itrans = _NAK_ITRANS.get(value, value)
    return (_PLANT_BY_NAKSHATRA.get(value) or
            _PLANT_BY_NAKSHATRA.get(itrans) or
            (alias and _PLANT_BY_NAKSHATRA.get(alias)) or
            _PLANT_BY_SLUG.get(slug))


def _today_plants(now=None):
    now = now or datetime.now()
    fs = field_state(now)
    interp = interpret_field(now)
    p5 = fs["panchanga"]
    nak_plant = dict(_lookup_plant(p5["nakshatra"]) or {})
    if nak_plant:
        nak_plant.update({
            "source": "nakshatra",
            "anchor": p5["nakshatra"],
            "guidance": (nak_plant.get("ritual_use") or "Place at entrance · water at dawn"),
        })
    tithi_plant = dict(_TITHI_PLANTS.get(p5["tithi"], {}))
    if tithi_plant:
        tithi_plant.update({
            "source": "tithi",
            "anchor": p5["tithi"],
            "common_name": tithi_plant.get("plant", ""),
            "sanskrit_name": tithi_plant.get("plant", ""),
            "season": _florida_season(now),
            "growing_notes": "ritual anchor rather than seasonal crop guidance",
            "ritual_use": tithi_plant.get("guidance", ""),
            "ayurvedic_use": tithi_plant.get("use", ""),
        })
    vara_lord = _VARA_GRAHA_NAME[now.weekday()]
    vara_plant = dict(_VARA_PLANTS.get(vara_lord, {}))
    if vara_plant:
        vara_plant.update({
            "source": "vara",
            "anchor": vara_lord,
            "sanskrit_name": vara_plant.get("plant", ""),
            "season": _florida_season(now),
            "growing_notes": "favorable as a weekday altar or food offering",
            "ritual_use": vara_plant.get("guidance", ""),
            "ayurvedic_use": vara_plant.get("use", ""),
        })
    dosha_key = (p5["nak_data"].get("dosha") or "vata").lower()
    dosha = _DOSHA_RECOMMENDATIONS.get(dosha_key, _DOSHA_RECOMMENDATIONS["vata"])
    season, seasonal = _seasonal_plants(now)
    return {
        "nakshatra_plant": nak_plant,
        "tithi_plant": tithi_plant,
        "vara_plant": vara_plant,
        "plants": [p for p in (nak_plant, tithi_plant, vara_plant) if p],
        "dosha_today": {
            "name": dosha_key.capitalize(),
            "recommended": dosha["recommended"],
            "avoid": dosha["avoid"],
            "herbs": dosha["herbs"],
        },
        "season": season,
        "seasonal_plants": seasonal,
        "practice": interp.get("practice", ""),
    }


def _same_tattva_guna_nakshatras(element, guna, exclude_name=None):
    matches = []
    for row in NAKSHATRA_DATA:
        if row.get("element", "").lower() == (element or "").lower() and row.get("guna", "").lower() == (guna or "").lower():
            if row["name"] != exclude_name:
                matches.append(row["name"])
    return matches


def _adjacent_nakshatras(name):
    if name not in NAKSHATRAS:
        return []
    idx = NAKSHATRAS.index(name)
    return [NAKSHATRAS[(idx - 1) % len(NAKSHATRAS)], NAKSHATRAS[(idx + 1) % len(NAKSHATRAS)]]


def _same_deity_group(name):
    row = next((item for item in NAKSHATRA_DATA if item["name"] == name), None)
    if not row:
        return []
    deity = row.get("deity", "")
    if not deity:
        return []
    return [item["name"] for item in NAKSHATRA_DATA if item["name"] != name and item.get("deity", "") == deity][:4]


def _pada_navamsa_details(name):
    if name not in NAKSHATRAS:
        return []
    idx = NAKSHATRAS.index(name)
    details = []
    for pada in range(1, 5):
        details.append({
            "pada": pada,
            "navamsa": _navamsa_rashi(idx, pada),
        })
    return details


def _graha_rulerships(graha_name):
    return [row["name"] for row in NAKSHATRA_DATA if row.get("graha") == graha_name]


def _field_resonance(entity, fs):
    anchor = _today_anchor(fs)
    score = 0.2
    reasons = []
    if entity["type"] == "nakshatra" and entity["name"] == anchor["nakshatra"]:
        score += 0.45
        reasons.append("today's active nakshatra")
    if entity["type"] == "graha" and entity["name"] in {anchor["nak_lord"], (fs.get("vara_graha") or {}).get("name", "")}:
        score += 0.4
        reasons.append("active graha in today's field")
    if entity["type"] == "devi" and entity["name"] == anchor["devi"]:
        score += 0.45
        reasons.append("today's active nitya devi")
    if entity["type"] == "plant":
        ecology = _today_plants(fs["panchanga"]["now"])
        active_names = {p.get("plant", "") for p in ecology.get("plants", [])}
        if entity["name"] in active_names:
            score += 0.45
            reasons.append("today's active ecology plant")
    if entity.get("element", "").lower() and entity.get("element", "").lower() == anchor["element"]:
        score += 0.15
        reasons.append("elemental match")
    if entity.get("guna", "").lower() and entity.get("guna", "").lower() == anchor["guna"]:
        score += 0.1
        reasons.append("guna match")
    if entity.get("raga") and entity.get("raga") in {anchor["raga"], anchor["muhurta_raga"]}:
        score += 0.1
        reasons.append("raga match")
    return {
        "score": round(min(score, 1.0), 3),
        "reasons": reasons or ["ambient field relation"],
    }


def _build_entity_payload(entity_type, row, fs):
    anchor = _today_anchor(fs)
    if entity_type == "nakshatra":
        plant = _lookup_plant(row["name"]) or {}
        symbol = row.get("symbol", "")
        relation_rows = [
            {"type": "ruling_graha", "value": row.get("graha", "")},
            {"type": "presiding_deity", "value": row.get("deity", "")},
            {"type": "paired_nitya", "value": DEVI_DATA[(NAKSHATRAS.index(row["name"]) % len(DEVI_DATA))]["name"]},
        ]
        enriched = dict(row)
        enriched.update({
            "body_part": plant.get("body_part") or (_ELEMENT_BODY_PARTS.get(row.get("element", "").lower(), [""])[0] if _ELEMENT_BODY_PARTS.get(row.get("element", "").lower()) else ""),
            "metal": plant.get("metal", ""),
            "plant": plant.get("plant") or _NAKSHATRA_PLANTS.get(row.get("name_key", ""), ""),
            "mantra": _NAKSHATRA_MANTRAS.get(row.get("name", ""), ""),
            "adjacent_nakshatras": _adjacent_nakshatras(row["name"]),
            "same_deity_group": _same_deity_group(row["name"]),
            "pada_navamsa": _pada_navamsa_details(row["name"]),
            "symbol_meaning": _SYMBOL_MEANINGS.get(symbol, symbol.replace("_", " ") if symbol else ""),
        })
        return {
            "id": f"nakshatra:{_slugify(row.get('name_key') or row['name'])}",
            "type": "nakshatra",
            "name": row["name"],
            "name_key": row.get("name_key", ""),
            "data": enriched,
            "relations": relation_rows,
            "mantra": enriched["mantra"] or " · ".join(_NAKSHATRA_SYLLABLES.get(row.get("name_key", ""), [])),
            "plants": [plant] if plant else [p for p in [_NAKSHATRA_PLANTS.get(row.get("name_key", ""))] if p] or _element_matched_plants(row.get("element", "")),
            "body_parts": [enriched["body_part"]] if enriched["body_part"] else _ELEMENT_BODY_PARTS.get(row.get("element", "").lower(), []),
            "coherence": _field_resonance({"type": "nakshatra", "name": row["name"], **enriched}, fs),
            "today": {
                "is_active": row["name"] == anchor["nakshatra"],
                "field_relation": "active nakshatra" if row["name"] == anchor["nakshatra"] else f"ruled by {row.get('graha', '')}",
            },
        }
    if entity_type == "graha":
        bija = _GRAHA_BIJA.get(row.get("name_key", ""), "")
        profile = _GRAHA_PROFILE.get(row["name"], {})
        enriched = dict(row)
        enriched.update({
            "body_part": profile.get("body_part", ""),
            "metal": profile.get("metal", ""),
            "gem": profile.get("gem", ""),
            "color": profile.get("color", ""),
            "weekday": profile.get("weekday", ""),
            "nakshatra_rulerships": _graha_rulerships(row["name"]),
            "friends": profile.get("friends", []),
            "enemies": profile.get("enemies", []),
            "exaltation": profile.get("exaltation", ""),
            "debilitation": profile.get("debilitation", ""),
            "yantra": profile.get("yantra", ""),
            "mantra_text": profile.get("mantra", ""),
        })
        relation_rows = [
            {"type": "domain", "value": row.get("domain", "")},
            {"type": "vehicle", "value": row.get("vehicle", "")},
            {"type": "weapon", "value": row.get("weapon", "")},
        ]
        return {
            "id": f"graha:{_slugify(row.get('name_key') or row['name'])}",
            "type": "graha",
            "name": row["name"],
            "name_key": row.get("name_key", ""),
            "data": enriched,
            "relations": relation_rows,
            "mantra": profile.get("mantra", "") or (f"oṁ {bija} {row['name']}ya namaḥ" if bija else ""),
            "plants": _element_matched_plants(row.get("element", "")),
            "body_parts": [profile.get("body_part")] if profile.get("body_part") else _GRAHA_BODY_PARTS.get(row["name"], _ELEMENT_BODY_PARTS.get(row.get("element", "").lower(), [])),
            "coherence": _field_resonance({"type": "graha", "name": row["name"], **enriched}, fs),
            "today": {
                "is_active": row["name"] in {anchor["nak_lord"], (fs.get("vara_graha") or {}).get("name", "")},
                "field_relation": "nakshatra lord" if row["name"] == anchor["nak_lord"] else "vara graha" if row["name"] == (fs.get("vara_graha") or {}).get("name", "") else row.get("domain", ""),
            },
        }
    if entity_type == "plant":
        ecology = _today_plants(fs["panchanga"]["now"])
        active_names = {p.get("plant", "") for p in ecology.get("plants", [])}
        return {
            "id": row["id"],
            "type": "plant",
            "name": row["plant"],
            "name_key": row.get("common_name", ""),
            "data": row,
            "relations": [
                {"type": "nakshatra", "value": row.get("nakshatra", "")},
                {"type": "deity", "value": row.get("deity", "")},
                {"type": "dosha", "value": row.get("dosha", "")},
                {"type": "metal", "value": row.get("metal", "")},
            ],
            "mantra": row.get("mantra", ""),
            "plants": [row],
            "body_parts": [row.get("body_part", "")] if row.get("body_part") else [],
            "coherence": _field_resonance({"type": "plant", "name": row["plant"], **row}, fs),
            "today": {
                "is_active": row["plant"] in active_names,
                "field_relation": "today's ecology plant" if row["plant"] in active_names else row.get("use", ""),
            },
        }
    related = _same_tattva_guna_nakshatras(row.get("element", ""), row.get("guna", ""))
    governed_graha = GRAHA_DATA[(row["tithi_number"] - 1) % len(GRAHA_DATA)]["name"] if GRAHA_DATA else ""
    enriched = dict(row)
    enriched.update({
        "full_process": row["process"],
        "yantra_geometry_name": _DEVI_YANTRAS.get(row["name"], "sri-yantra derivative"),
        "tithi_relationship": f"{row['paksha']} tithi {row['tithi_number']} · {row['tithi_name']}",
        "governing_graha": governed_graha,
        "practice_for_day": f"Build toward {row['process'].split('·')[0].strip().lower()} with mantra and rāga alignment.",
    })
    return {
        "id": row["id"],
        "type": "devi",
        "name": row["name"],
        "data": enriched,
        "relations": [
            {"type": "tithi", "value": f"{row['tithi_number']} · {row['tithi_name']}"},
            {"type": "field_raga", "value": row.get("raga", "")},
            {"type": "same_tattva_guna_nakshatras", "value": ", ".join(related[:4])},
        ],
        "mantra": row["mantra"],
        "plants": _element_matched_plants(row.get("element", "")),
        "body_parts": row.get("body_parts", []),
        "coherence": _field_resonance({"type": "devi", "name": row["name"], **row}, fs),
        "today": {
            "is_active": row["name"] == anchor["devi"],
            "field_relation": "today's nitya devi" if row["name"] == anchor["devi"] else row["process"],
        },
    }


def get_entity_data(entity_id, now=None):
    """Resolve a graha/nakshatra/devi card to structured Atlas data."""
    fs = field_state(now)
    key = _slugify(entity_id)
    match = ENTITY_INDEX.get(key)
    if not match and ":" not in str(entity_id):
        for prefix in ("nakshatra", "graha", "devi", "plant"):
            match = ENTITY_INDEX.get(_slugify(f"{prefix}:{entity_id}"))
            if match:
                break
    if not match:
        return None
    entity_type, row = match
    payload = _build_entity_payload(entity_type, row, fs)
    payload["field"] = {
        "tithi": fs["panchanga"]["tithi"],
        "paksha": fs["panchanga"]["paksha"],
        "nakshatra": fs["panchanga"]["nakshatra"],
        "devi": _devi_field(fs["panchanga"]["devi"], 0),
        "muhurta": fs["muhurta"]["name"],
        "raga": fs.get("devi_raga", ""),
    }
    return payload


def companion_state(fs):
    """Companion states emerge from the current field instead of fixed presets."""
    p5 = fs["panchanga"]
    nak = p5.get("nak_data") or {}
    raga = fs.get("devi_raga", "")
    coherence = _field_resonance({"type": "devi", "name": _devi_field(p5["devi"], 0), "element": nak.get("element", ""), "guna": nak.get("guna", ""), "raga": raga}, fs)
    bandhu_focus = "observe" if coherence["score"] < 0.45 else "advise" if coherence["score"] < 0.7 else "confirm"
    shilpi_phase = "refine" if fs["muhurta"]["name"] == "Rātri" else "build" if coherence["score"] >= 0.55 else "sketch"
    return {
        "bandhu_bhai": {
            **COMPANIONS["bandhu_bhai"],
            "focus": f"{p5['nakshatra']} · {p5['nak_lord']} · {fs['muhurta']['name']}",
            "signal": bandhu_focus,
            "guidance": f"Read the field through {nak.get('element', 'field')} element and {nak.get('guna', 'mixed')} guna.",
            "coherence": coherence["score"],
        },
        "shilpi_bhai": {
            **COMPANIONS["shilpi_bhai"],
            "focus": f"{_devi_field(p5['devi'], 0)} · ♫ {raga} · {fs['muhurta']['bpm']} bpm",
            "signal": shilpi_phase,
            "guidance": f"Build toward {_devi_field(p5['devi'], 2)} with {fs['muhurta']['name'].lower()} pacing.",
            "coherence": coherence["score"],
        },
    }

# ── Varas (no dataset file — calendar constant) ─────────────
VARAS = ["Ravivāra ☀", "Somavāra ☽", "Maṅgalavāra ♂", "Budhavāra ☿",
         "Guruvāra ♃", "Śukravāra ♀", "Śanivāra ♄"]


# ══════════════════════════════════════════════════════════════
# PAÑCĀṄGA
# ══════════════════════════════════════════════════════════════

_REF_DATE = datetime(2025, 1, 13)

# ── Vaiṣṇava calendar ────────────────────────────────────
# The Vaiṣṇava calendar is not a material auspicious timing system.
# Material observances: "this moment is powerful — use it."
# Vaiṣṇava observances: "the Lord appeared here — we remember and serve."
# The astronomical moment is the window. The S0 entity is what's seen through it.

_vaishnava_cal = None    # list of all rows
_vaishnava_idx = None    # {(masa, paksha, tithi_num): [row, ...]}
_parampara_meta = None   # {parampara_id: {name_iast, role, source, ...}}

def _load_vaishnava_calendar():
    global _vaishnava_cal, _vaishnava_idx
    if _vaishnava_cal is not None:
        return _vaishnava_cal
    _vaishnava_cal = []
    _vaishnava_idx = {}
    cal_path = os.path.join(str(_HERE), "datasets", "ritual", "vaishnava_calendar.csv")
    try:
        import csv
        with open(cal_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                entry = {
                    "masa_num":     int(row.get("masa_num", -1)),
                    "paksha":       row.get("paksha", "").strip(),
                    "tithi_num":    int(row.get("tithi_num", -1)),
                    "name":         row.get("observance_name", ""),
                    "name_iast":    row.get("observance_name_iast", ""),
                    "type":         row.get("observance_type", ""),
                    "deity":        row.get("deity", ""),
                    "parampara_ref": row.get("parampara_ref", ""),
                    "source":       row.get("source", ""),
                    "notes":        row.get("notes", ""),
                }
                _vaishnava_cal.append(entry)
                key = (entry["masa_num"], entry["paksha"], entry["tithi_num"])
                _vaishnava_idx.setdefault(key, []).append(entry)
    except Exception as e:
        print(f"  ⚠ vaishnava_calendar.csv: {e}")
    return _vaishnava_cal


def _load_parampara_meta():
    global _parampara_meta
    if _parampara_meta is not None:
        return _parampara_meta
    _parampara_meta = {}
    path = os.path.join(str(_HERE), "datasets", "ontology", "parampara.csv")
    try:
        import csv
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                pid = row.get("id", "").strip()
                if pid:
                    _parampara_meta[pid] = {
                        "id":        pid,
                        "name_iast": row.get("name_iast", ""),
                        "name_sk":   row.get("name_sk", ""),
                        "position":  row.get("position", ""),
                        "role":      row.get("role", ""),
                        "era":       row.get("era", ""),
                        "source":    row.get("source", ""),
                        "layer":     "S0",
                    }
    except Exception:
        pass
    return _parampara_meta


def vaishnava_observance(panchanga=None):
    """Look up Vaiṣṇava observance(s) for a pañcāṅga moment.

    The astronomical moment is the window.
    The S0 entity (parampara_, tattva_) is what's seen through it.

    Args:
        panchanga: dict from calc_panchanga(), or None for current moment

    Returns:
        list of observance dicts, each with resolved parampara metadata.
        Empty list if no observance today.
    """
    if panchanga is None:
        panchanga = calc_panchanga()

    _load_vaishnava_calendar()
    if not _vaishnava_idx:
        return []

    masa_num = panchanga.get("masa", 0)
    paksha = panchanga.get("paksha", "Śukla")
    tidx = panchanga.get("tidx", 0)

    p = "sukla" if "ukla" in paksha else "krsna"
    didx = tidx % 15

    matches = _vaishnava_idx.get((masa_num, p, didx), [])

    # Resolve parampara S0 entity metadata for each match
    para_meta = _load_parampara_meta()
    results = []
    for obs in matches:
        entry = dict(obs)  # copy
        pref = obs.get("parampara_ref", "")
        if pref and pref in para_meta:
            entry["parampara_entity"] = para_meta[pref]
        results.append(entry)

    return results


def calc_panchanga(now=None):
    """Compute pañcāṅga using drik-panchanga (Swiss Ephemeris, Lahiri ayanāṃśa).

    Location: Gainesville FL — 29.65°N, 82.32°W, UTC−4 (EDT) / UTC−5 (EST).
    Tithi and nakṣatra computed at sunrise per Vedic convention.
    Returns dict with: tithi, tidx, didx, paksha, devi,
    nakshatra, nak_lord, nak_data, tithi_deity, vara, masa, now.
    """
    if now is None:
        now = datetime.now()

    # Gainesville FL — timezone offset (EDT = -4, EST = -5)
    # Simple DST: second Sunday Mar → first Sunday Nov
    _dst_start = datetime(now.year, 3, 8 + (6 - datetime(now.year, 3, 1).weekday()) % 7)
    _dst_end   = datetime(now.year, 11, 1 + (6 - datetime(now.year, 11, 1).weekday()) % 7)
    tz_offset  = -4.0 if _dst_start <= now.replace(hour=2) < _dst_end else -5.0

    _MASA_NAMES = [
        "Caitra", "Vaiśākha", "Jyeṣṭha", "Āṣāḍha",
        "Śrāvaṇa", "Bhādrapada", "Āśvina", "Kārtika",
        "Mārgaśīrṣa", "Pauṣa", "Māgha", "Phālguna",
    ]

    try:
        import drik_panchanga as dp
        dp.set_chosen_ayanamsa('lahiri')
        place = dp.Place(29.65, -82.32, tz_offset)
        jd = dp.local_time_to_jdut1(now.year, now.month, now.day,
                                     now.hour, now.minute, now.second, tz_offset)

        # Tithi at sunrise (1-based, 1-30)
        ti = dp.tithi(jd, place)
        tidx = ti[0] - 1  # convert to 0-based

        # Nakshatra at sunrise (1-based, 1-27)
        nak = dp.nakshatra(jd, place)
        nak_idx = (nak[0] - 1) % 27  # convert to 0-based

        # Masa (1-based, 1-12)
        masa_result = dp.masa(jd, place)
        masa_num = (masa_result[0] - 1) % 12  # convert to 0-based

    except Exception as _e:
        print(f"⚠ drik-panchanga failed ({_e}), falling back to swisseph")
        try:
            import swisseph as swe
            swe.set_sid_mode(swe.SIDM_LAHIRI)
            jd = swe.julday(now.year, now.month, now.day,
                            now.hour + now.minute / 60.0 + now.second / 3600.0)
            moon_long = swe.calc_ut(jd, swe.MOON)[0][0]
            sun_long  = swe.calc_ut(jd, swe.SUN)[0][0]
            ayanamsha = swe.get_ayanamsa_ut(jd)
            moon_sid  = (moon_long - ayanamsha) % 360
            sun_sid   = (sun_long  - ayanamsha) % 360
            nak_idx   = int(moon_sid / (360 / 27)) % 27
            phase     = (moon_long - sun_long) % 360
            tidx      = min(int(phase / 12), 29)
            rashi_idx = int(sun_sid / 30) % 12
            masa_num  = rashi_idx
        except Exception:
            days  = (now - _REF_DATE).total_seconds() / 86400
            cycle = ((days % 29.5306) + 29.5306) % 29.5306
            tidx  = min(int(cycle / 29.5306 * 30), 29)
            nak_idx = int((days * 13.176) % 360 / (360 / 27)) % 27
            masa_num = (now.month + 8) % 12

    paksha     = "Śukla" if tidx < 15 else "Kṛṣṇa"
    didx       = tidx % 15
    nak_record = NAKSHATRA_DATA[nak_idx] if nak_idx < len(NAKSHATRA_DATA) else {}
    tithi_deity = TITHI_DEITIES[tidx] if tidx < len(TITHI_DEITIES) else ""
    masa_name = _MASA_NAMES[masa_num]

    result = {
        "tithi":       TITHIS[tidx],
        "tidx":        tidx,
        "didx":        didx,
        "paksha":      paksha,
        "tithi_deity": tithi_deity,
        "devi":        _devi_dict(didx),
        "nakshatra":   NAKSHATRAS[nak_idx],
        "nak_lord":    NAK_LORDS[nak_idx],
        "nak_data":    nak_record,
        "element":     (nak_record.get("element") or "").lower(),
        "guna":        (nak_record.get("guna") or "").lower(),
        "body_region": nak_record.get("body_region", ""),
        "vara":        VARAS[(now.weekday() + 1) % 7],
        "masa":        masa_num,
        "masa_name":   masa_name,
        "now":         now,
    }

    # Vaiṣṇava observance lookup (pass the result so it can read masa/paksha/tidx)
    result["observances"] = vaishnava_observance(result)

    return result

def get_muhurta(now=None):
    """Current muhūrta window → {emoji, name, raga, bpm}."""
    if now is None:
        now = datetime.now()
    m = now.hour * 60 + now.minute
    SR, SS = 360, 1140   # sunrise 6 AM, sunset 7 PM (approx Gainesville FL)
    brahma = SR - 96
    noon = (SR + SS) // 2
    if brahma <= m < SR:
        return {"em": "🌙", "name": "Brahma Muhūrta", "raga": "Bhairava",    "bpm": 54}
    if SR <= m < SR + 48:
        return {"em": "🌅", "name": "Prātaḥ",         "raga": "Bhairava",    "bpm": 60}
    if noon - 24 <= m < noon + 24:
        return {"em": "✦",  "name": "Abhijit",         "raga": "Bhimpalasī",  "bpm": 96}
    if SS - 60 <= m < SS + 48:
        return {"em": "🌆", "name": "Sāyaṃ Sandhyā",  "raga": "Mārvā",       "bpm": 72}
    if m < SR or m > SS + 120:
        return {"em": "🌟", "name": "Rātri",           "raga": "Bāgeshṛī",   "bpm": 56}
    return {"em": "☀",  "name": "Divasam",         "raga": "Yaman",       "bpm": 84}


# ══════════════════════════════════════════════════════════════
# EXTENDED PANCHANGA COMPUTATIONS
# ══════════════════════════════════════════════════════════════

# Yoga names (27 yogas from sun+moon longitude)
_YOGA_NAMES = [
    "Viṣkambha", "Prīti", "Āyuṣmān", "Saubhāgya", "Śobhana",
    "Atigaṇḍa", "Sukarmā", "Dhṛti", "Śūla", "Gaṇḍa",
    "Vṛddhi", "Dhruvā", "Vyāghāta", "Harṣaṇa", "Vajra",
    "Siddhi", "Vyatīpāta", "Variyan", "Parigha", "Śiva",
    "Siddha", "Sādhya", "Śubha", "Śukla", "Brahma",
    "Indra", "Vaidhṛti",
]
_YOGA_QUALITY = {
    "Prīti": "auspicious", "Āyuṣmān": "auspicious", "Saubhāgya": "auspicious",
    "Śobhana": "auspicious", "Sukarmā": "auspicious", "Dhṛti": "auspicious",
    "Vṛddhi": "auspicious", "Harṣaṇa": "auspicious", "Siddhi": "auspicious",
    "Śiva": "auspicious", "Siddha": "auspicious", "Sādhya": "auspicious",
    "Śubha": "auspicious", "Śukla": "auspicious", "Brahma": "auspicious",
    "Indra": "auspicious", "Variyan": "auspicious",
    "Viṣkambha": "mixed", "Dhruvā": "mixed", "Vajra": "mixed",
    "Atigaṇḍa": "inauspicious", "Śūla": "inauspicious", "Gaṇḍa": "inauspicious",
    "Vyāghāta": "inauspicious", "Vyatīpāta": "inauspicious",
    "Parigha": "inauspicious", "Vaidhṛti": "inauspicious",
}

# Karana names (11 karanas, rotating through 60 half-tithis)
_KARANA_CYCLE = [
    "Bava", "Bālava", "Kaulava", "Taitila", "Gara", "Vaṇija", "Viṣṭi",
]
_KARANA_FIXED = {0: "Kiṃstughna", 57: "Śakuni", 58: "Catuṣpāda", 59: "Nāga"}
_KARANA_QUALITY = {
    "Bava": "auspicious", "Bālava": "auspicious", "Kaulava": "auspicious",
    "Taitila": "auspicious", "Gara": "auspicious",
    "Vaṇija": "mixed", "Viṣṭi": "inauspicious",
    "Kiṃstughna": "auspicious", "Śakuni": "inauspicious",
    "Catuṣpāda": "inauspicious", "Nāga": "inauspicious",
}

# Hora sequence: each day starts with its own lord, then follows the chaldean order
_HORA_SEQUENCE = {
    0: ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"],
    1: ["Moon", "Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury"],
    2: ["Mars", "Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter"],
    3: ["Mercury", "Moon", "Saturn", "Jupiter", "Mars", "Sun", "Venus"],
    4: ["Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon", "Saturn"],
    5: ["Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars", "Sun"],
    6: ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"],
}

# Rahu Kala periods (hour offsets from sunrise=6am, 1.5h each)
_RAHU_KALA_SLOT = {
    0: 8,   # Sunday: 4:30-6pm → slot 8 (1.5h from 6am → hour 18-19:30 mapped to slot)
    1: 2,   # Monday: slot 2 (7:30-9am)
    2: 7,   # Tuesday
    3: 5,   # Wednesday
    4: 6,   # Thursday
    5: 4,   # Friday
    6: 3,   # Saturday
}

# Load extended datasets
_swara_vara_rules = _load_csv("svarodaya/vara_rules.csv")
_vastu_perimeter = _load_csv("vastu/perimeter_deities.csv")
_raga_therapeutic = _load_csv("gandharva/raga_therapeutic.csv")
_graha_gems = _load_csv("ratna/graha_gems.csv")
_body_marma = _load_csv("marma/body_region_marma.csv")
_herb_exemplars = _load_csv("ayurveda/herb_exemplars.csv")
_dosha_nakshatra = _load_csv("ayurveda/dosha_nakshatra_matrix.csv")


def _approx_sun_lon(days_from_ref):
    """Approximate sidereal Sun longitude. Mean motion ~0.9856 deg/day."""
    # Reference: 2025-01-13 Sun near ~269° sidereal (Uttara Ashadha region)
    return (269.0 + days_from_ref * 0.9856) % 360


def compute_yoga(days):
    """Yoga = (sun_lon + moon_lon) / (360/27)."""
    moon_lon = _calc_approx_moon_lon(days)
    sun_lon = _approx_sun_lon(days)
    yoga_deg = (sun_lon + moon_lon) % 360
    yoga_idx = int(yoga_deg / (360 / 27)) % 27
    name = _YOGA_NAMES[yoga_idx]
    return {
        "yoga_name": name,
        "yoga_quality": _YOGA_QUALITY.get(name, "mixed"),
        "yoga_index": yoga_idx,
    }


def compute_karana(tidx):
    """Karana = half-tithi. 60 half-tithis per lunar month."""
    half = tidx * 2  # first half of this tithi
    # We return the current half-tithi karana
    if half in _KARANA_FIXED:
        name = _KARANA_FIXED[half]
    else:
        cycle_pos = (half - 1) % 7 if half > 0 else 0
        name = _KARANA_CYCLE[cycle_pos]
    return {
        "karana_name": name,
        "karana_quality": _KARANA_QUALITY.get(name, "mixed"),
    }


def compute_hora(now, weekday):
    """Planetary hour based on sunrise at ~6am."""
    hour = now.hour
    hora_idx = (hour - 6) % 24
    if hora_idx < 0:
        hora_idx += 24
    seq = _HORA_SEQUENCE.get(weekday, _HORA_SEQUENCE[0])
    lord = seq[hora_idx % 7]
    # Quality based on lord
    quality_map = {
        "Jupiter": "very auspicious", "Venus": "auspicious", "Mercury": "auspicious",
        "Moon": "auspicious", "Sun": "neutral", "Mars": "challenging", "Saturn": "challenging",
    }
    return {
        "hora_lord": lord,
        "hora_quality": quality_map.get(lord, "neutral"),
        "hora_index": hora_idx % 7,
    }


def compute_rahu_kala(now, weekday):
    """Is current time within Rahu Kala?"""
    slot = _RAHU_KALA_SLOT.get(weekday, 8)
    sunrise_hour = 6  # approximate
    start_hour = sunrise_hour + int(slot * 1.5)
    start_min = 30 if slot % 2 else 0
    end_hour = start_hour + 1
    end_min = start_min + 30
    if end_min >= 60:
        end_hour += 1
        end_min -= 60
    start_total = start_hour * 60 + start_min
    end_total = end_hour * 60 + end_min
    cur = now.hour * 60 + now.minute
    active = start_total <= cur < end_total
    return {
        "rahu_kala_active": active,
        "rahu_kala_start": f"{start_hour}:{start_min:02d}",
        "rahu_kala_end": f"{end_hour}:{end_min:02d}",
    }


def compute_swara(weekday):
    """Recommended nadi for this vara."""
    vara_names = ["Ravivara", "Somavara", "Mangalavara", "Budhavara",
                  "Guruvara", "Shukravara", "Shanivara"]
    vara_name = vara_names[weekday] if weekday < 7 else "Ravivara"
    for row in _swara_vara_rules:
        if row.get("vara", "") == vara_name:
            return {
                "swara_nadi": row.get("optimal_nadi", "sushumna"),
                "swara_element": row.get("reasoning", ""),
            }
    # Fallback
    nadi = "pingala" if weekday in (0, 2, 4) else "ida"
    return {"swara_nadi": nadi, "swara_element": ""}


def compute_vastu_zone(vara_lord, nakshatra):
    """Active vastu zone from vara_lord + nakshatra."""
    # Match by element or deity proximity
    vara_lord_lower = str(vara_lord).lower()
    nak_lower = str(nakshatra).lower()
    for row in _vastu_perimeter:
        deity = str(row.get("deity", "")).lower()
        if vara_lord_lower in deity or nak_lower[:4] in deity:
            return {
                "zone_name": row.get("position", ""),
                "zone_deity": row.get("deity", ""),
                "zone_direction": row.get("direction", ""),
            }
    # Fallback: match by element
    element_dir = {"fire": "south", "water": "west", "air": "east", "earth": "north", "ether": "center"}
    for row in _vastu_perimeter:
        if row.get("direction", "") == element_dir.get(vara_lord_lower, "east"):
            return {
                "zone_name": row.get("position", ""),
                "zone_deity": row.get("deity", ""),
                "zone_direction": row.get("direction", ""),
            }
    return {"zone_name": "center", "zone_deity": "Brahma", "zone_direction": "center"}


def compute_therapeutic_raga(now, element):
    """Best raga for current time of day + element/dosha."""
    hour = now.hour
    time_label = "morning" if hour < 12 else "afternoon" if hour < 18 else "night"
    # Map element to dosha
    dosha_map = {"fire": "pitta", "water": "kapha", "air": "vata", "earth": "kapha", "ether": "vata"}
    dosha = dosha_map.get(str(element).lower(), "vata")
    for row in _raga_therapeutic:
        if dosha in str(row.get("dosha_target", "")).lower():
            return {
                "therapeutic_raga": row.get("raga", "Yaman"),
                "dosha_target": dosha,
                "attestation": row.get("attestation", "TRADITIONAL"),
            }
    return {"therapeutic_raga": "Yaman", "dosha_target": dosha, "attestation": "TRADITIONAL"}


def compute_gem_today(weekday):
    """Gem for today's vara lord."""
    vara_lords = ["Surya", "Chandra", "Mangala", "Budha", "Guru", "Shukra", "Shani"]
    lord = vara_lords[weekday] if weekday < 7 else "Surya"
    for row in _graha_gems:
        if str(row.get("graha", "")).lower() == lord.lower():
            return {
                "primary_gem": row.get("primary_gem", ""),
                "substitute_gem": row.get("substitute_gem", ""),
                "vara_lord": lord,
            }
    return {"primary_gem": "", "substitute_gem": "", "vara_lord": lord}


def compute_marma(body_region):
    """Marma point for current nakshatra body region."""
    region = str(body_region).lower().strip()
    for row in _body_marma:
        if str(row.get("body_region", "")).lower().strip() == region:
            return {
                "marma_name": row.get("marma_name", ""),
                "marma_location": row.get("marma_location", ""),
                "therapeutic_action": row.get("therapeutic_action", ""),
            }
    return {"marma_name": "", "marma_location": "", "therapeutic_action": ""}


# ══════════════════════════════════════════════════════════════
# NAKSHATRA → TĀLA MAP (module-level, used by field_state_v1 + generate_composition)
# ══════════════════════════════════════════════════════════════

_NAKSHATRA_TALA = {
    "Ashwini": {"tala": "Rupak", "beats": 7},
    "Bharani": {"tala": "Dadra", "beats": 6},
    "Krittika": {"tala": "Adi", "beats": 8},
    "Rohini": {"tala": "Adi", "beats": 8},
    "Mrigashira": {"tala": "Rupak", "beats": 7},
    "Ardra": {"tala": "Jhaptal", "beats": 10},
    "Punarvasu": {"tala": "Adi", "beats": 8},
    "Pushya": {"tala": "Rupak", "beats": 7},
    "Ashlesha": {"tala": "Chautal", "beats": 12},
    "Magha": {"tala": "Adi", "beats": 8},
    "Purva Phalguni": {"tala": "Dadra", "beats": 6},
    "Uttara Phalguni": {"tala": "Adi", "beats": 8},
    "Hasta": {"tala": "Rupak", "beats": 7},
    "Chitra": {"tala": "Adi", "beats": 8},
    "Swati": {"tala": "Rupak", "beats": 7},
    "Vishakha": {"tala": "Jhaptal", "beats": 10},
    "Anuradha": {"tala": "Rupak", "beats": 7},
    "Jyeshtha": {"tala": "Chautal", "beats": 12},
    "Mula": {"tala": "Adi", "beats": 8},
    "Purva Ashadha": {"tala": "Dadra", "beats": 6},
    "Uttara Ashadha": {"tala": "Adi", "beats": 8},
    "Shravana": {"tala": "Rupak", "beats": 7},
    "Dhanishta": {"tala": "Adi", "beats": 8},
    "Shatabhisha": {"tala": "Jhaptal", "beats": 10},
    "Purva Bhadrapada": {"tala": "Adi", "beats": 8},
    "Uttara Bhadrapada": {"tala": "Chautal", "beats": 12},
    "Revati": {"tala": "Rupak", "beats": 7},
}

_GUNA_GATI = {"sattva": "tisra", "rajas": "chatusra", "tamas": "khanda"}

# Directional bias from element (N/E/S/W weights, 0–1)
# Used by field_state_v1; Vāstu will later read this instead of computing locally
_ELEMENT_DIR_BIAS = {
    "fire":  {"N": 0.3, "E": 0.5, "S": 0.9, "W": 0.3},
    "water": {"N": 0.5, "E": 0.3, "S": 0.3, "W": 0.9},
    "earth": {"N": 0.9, "E": 0.5, "S": 0.5, "W": 0.5},
    "air":   {"N": 0.5, "E": 0.9, "S": 0.3, "W": 0.5},
    "ether": {"N": 0.6, "E": 0.6, "S": 0.6, "W": 0.6},
}


def _phi_to_label(phi_rad):
    """Convert φ radians to human-readable position label."""
    if phi_rad is None:
        return "center"
    import math as _m
    phi = phi_rad % (2 * _m.pi)
    if phi < _m.pi / 8:
        return "far-left"
    elif phi < 3 * _m.pi / 8:
        return "left"
    elif phi < 5 * _m.pi / 8:
        return "center-left"
    elif phi < 9 * _m.pi / 8:
        return "center"
    elif phi < 11 * _m.pi / 8:
        return "center-right"
    elif phi < 13 * _m.pi / 8:
        return "right"
    elif phi < 15 * _m.pi / 8:
        return "far-right"
    else:
        return "far-left"


def _phi_to_companion(phi_rad):
    """Derive active companion from φ position."""
    if phi_rad is None:
        return None
    import math as _m
    phi = phi_rad % (2 * _m.pi)
    margin = _m.pi / 6  # ~30° zone around center
    if abs(phi - _m.pi) < margin:
        return "Bheruṇḍā"
    elif phi < _m.pi:
        return "Shilpi"
    else:
        return "Bandhu"


def _derive_sound_state(fs):
    """Derive complete sound state from field_state dict.

    Returns a dict with everything a sound surface needs to visualize
    or generate sound — raga notes, tala bols, tempo, etc.
    All derived from kernel data, not duplicating NPU logic.
    """
    p5 = fs.get("panchanga", {})
    mu = fs.get("muhurta", {})
    devi_raga_name = fs.get("devi_raga", "Yaman")
    devi_raga_def = fs.get("devi_raga_def") or {}

    # Raga scale → swara names
    scale_semis = devi_raga_def.get("scale", [])
    aroha_semis = devi_raga_def.get("aroha", [])
    avaroha_semis = devi_raga_def.get("avaroha", [])
    vadi_semi = devi_raga_def.get("vadi")
    samvadi_semi = devi_raga_def.get("samvadi")

    raga_notes = [_SEMI_TO_SWARA.get(s, "?") for s in scale_semis]
    raga_aroha = [_SEMI_TO_SWARA.get(s, "?") for s in aroha_semis]
    raga_avaroha = [_SEMI_TO_SWARA.get(s, "?") for s in avaroha_semis]
    raga_vadi = _SEMI_TO_SWARA.get(vadi_semi, "") if vadi_semi is not None else ""
    raga_samvadi = _SEMI_TO_SWARA.get(samvadi_semi, "") if samvadi_semi is not None else ""

    # Tala
    nak_itrans = nak_to_itrans(p5.get("nakshatra", ""))
    tala_info = _NAKSHATRA_TALA.get(nak_itrans, {"tala": "Ādi", "beats": 8})
    tala_name = tala_info["tala"]
    tala_beats = tala_info["beats"]
    tala_bols = _TALA_BOLS.get(tala_name, _TALA_BOLS.get("Adi", []))

    # Gati
    guna = p5.get("guna", "").lower()
    gati = _GUNA_GATI.get(guna, "chatusra")

    # Tempo
    bpm = mu.get("bpm", 72)

    # Arc phase (lunar position)
    arc_phase = round(p5.get("tidx", 0) / 30.0, 3)

    # Element frequency
    element = p5.get("element", "ether").lower()
    element_freq = _ELEMENT_FREQ.get(element, 329.63)

    # Rasa — extract primary keyword
    raga_rasa_raw = devi_raga_def.get("rasa", "")
    _RASA_ALIASES = {
        "shringara": "shringara", "srngara": "shringara", "sringara": "shringara",
        "hasya": "hasya", "karuna": "karuna", "raudra": "raudra", "vira": "vira",
        "bhayanaka": "bhayanaka", "bibhatsa": "bibhatsa",
        "adbhuta": "adbhuta", "shanta": "shanta", "santa": "shanta",
    }
    _rn = raga_rasa_raw.lower()
    for _o, _n in [("ā","a"),("ṛ","r"),("ṅ","n"),("ṇ","n"),("ś","s"),("ṣ","s"),("ī","i"),("ū","u"),("ṭ","t"),("ḍ","d"),("ṃ","m"),("ñ","n")]:
        _rn = _rn.replace(_o, _n)
    rasa_primary = "shanta"
    for _tok in _rn.split():
        _cl = _tok.strip("·,; ")
        if _cl in _RASA_ALIASES:
            rasa_primary = _RASA_ALIASES[_cl]
            break

    # Shruti ratios for the scale
    _SEMI_SHRUTI = {0:1.0,1:256/243,2:9/8,3:32/27,4:5/4,5:4/3,6:45/32,7:3/2,8:128/81,9:5/3,10:16/9,11:15/8}
    shruti_scale = [round(_SEMI_SHRUTI.get(s % 12, 1.0), 6) for s in scale_semis]

    result = {
        "raga": devi_raga_name,
        "raga_notes": raga_notes,
        "raga_aroha": raga_aroha,
        "raga_avaroha": raga_avaroha,
        "raga_vadi": raga_vadi,
        "raga_samvadi": raga_samvadi,
        "raga_rasa": raga_rasa_raw,
        "rasa_primary": rasa_primary,
        "raga_time": devi_raga_def.get("time", ""),
        "tala": tala_name,
        "tala_beats": tala_beats,
        "tala_bols": tala_bols,
        "gati": gati,
        "bpm": bpm,
        "arc_phase": arc_phase,
        "element": element,
        "element_frequency": element_freq,
        "shruti_ratios": shruti_scale,
        "tuning": "shruti_just_intonation",
        "beat_position": 0,
        "derived_from_field": True,
    }

    # ── NPU graph enrichment: sa_hz + bija from the descent chain ──
    try:
        from npu_engine.field_to_sound import field_to_sound
        npu_spec = field_to_sound(fs)
        result["sa_hz"] = npu_spec.get("sa_hz", element_freq)
        result["bija"] = npu_spec.get("bija", "om")
        result["bija_path"] = npu_spec.get("bija_path", [])
        result["npu_element"] = npu_spec.get("element", element)
        result["npu_guna"] = npu_spec.get("guna", guna)
        result["npu_graha"] = npu_spec.get("graha", "")
        result["npu_devi"] = npu_spec.get("devi", "")
        result["npu_chakra"] = npu_spec.get("chakra", "")
        # Override element_frequency with NPU sa_hz if available
        result["element_frequency"] = npu_spec.get("sa_hz", element_freq)
    except Exception:
        result["sa_hz"] = element_freq
        result["bija"] = "om"
        result["bija_path"] = []

    result["attestation"] = {
            "raga": "OBSERVED",
            "raga_notes": "OBSERVED",
            "tala": "TRADITIONAL",
            "tala_bols": "TRADITIONAL",
            "gati": "SYNTHESIS",
            "bpm": "OBSERVED",
            "element_frequency": "TRADITIONAL",
            "shruti_ratios": "TRADITIONAL",
            "tuning": "TRADITIONAL",
            "rasa_primary": "TRADITIONAL",
    }

    return result


# Wire RelationalEngine with derive_sound after it's defined
if _relational is not None:
    _relational._derive_sound = _derive_sound_state

# ══════════════════════════════════════════════════════════════
# FIELD STATE — what is active right now
# ══════════════════════════════════════════════════════════════

def field_state(now=None):
    """Snapshot of the complete field: pañcāṅga + muhūrta + rāga + layer context.

    Single call for any front-end that needs "what is happening today".
    Includes full nakshatra/graha/plant data from datasets.

    Canonical FieldState structure (TWO_AXIS_FIELD_SPEC.md):
        Two axes encode the toroidal field:
          θ (vertical / time / S0→S6): tithi × nakshatra × vara
          φ (horizontal / witness↔participant): element/guna blend
        Every entity has BOTH coordinates.  Every query uses BOTH axes.
        Companion presence:
          Shilpi Bhai → LEFT  (φ < π, witness side)
          Bandhu Bhai → RIGHT (φ > π, participant side)
          Bheruṇḍā    → CENTER (φ = π, both held)
        FieldState keys: panchanga, muhurta, devi_raga, muhurta_raga,
          nak_graha, vara_graha, yoga, karana, hora, rahu_kala, swara,
          vastu_zone, therapeutic_raga, gem_today, marma_today,
          plants, vedic_schools, yuga, alpha, dasha, natal, companions.
    """
    p5 = calc_panchanga(now)
    mu = get_muhurta(p5["now"])
    devi = p5["devi"]                       # (name, emoji, process, rāga)
    devi_raga_name = _devi_field(devi, 3)
    devi_raga = RAGAS.get(devi_raga_name)
    muhurta_raga = RAGAS.get(mu["raga"])

    # find the graha record for the current nakshatra lord
    nak_lord = p5.get("nak_lord", "")
    graha_record = None
    for g in GRAHA_DATA:
        if g["name"] == nak_lord:
            graha_record = g
            break

    # vara → graha of the day
    vara_graha_order = ["Sūrya", "Candra", "Maṅgala", "Budha", "Guru", "Śukra", "Śani"]
    weekday = p5["now"].weekday()
    vara_graha_name = vara_graha_order[weekday] if weekday < 7 else None
    vara_graha = None
    if vara_graha_name:
        for g in GRAHA_DATA:
            if g["name"] == vara_graha_name:
                vara_graha = g
                break

    current_dasha = get_current_dasha(p5["now"])

    # Extended panchanga computations
    _now = p5["now"]
    _days = (_now - _REF_DATE).total_seconds() / 86400
    _weekday = _now.weekday()
    _element = p5.get("element", "")
    _body = p5.get("body_region", "")

    yoga = compute_yoga(_days)
    karana = compute_karana(p5.get("tidx", 0))
    hora = compute_hora(_now, _weekday)
    rahu_kala = compute_rahu_kala(_now, _weekday)
    swara = compute_swara(_weekday)
    vastu_zone = compute_vastu_zone(
        vara_graha_name or "", p5.get("nakshatra", ""))
    therapeutic_raga = compute_therapeutic_raga(_now, _element)
    gem_today = compute_gem_today(_weekday)
    marma_today = compute_marma(_body)

    fs = {
        "panchanga":        p5,
        "muhurta":          mu,
        "devi_raga":        devi_raga_name,
        "devi_raga_def":    devi_raga,
        "muhurta_raga":     mu["raga"],
        "muhurta_raga_def": muhurta_raga,
        "nak_graha":        graha_record,
        "vara_graha":       vara_graha,
        "yoga":             yoga,
        "karana":           karana,
        "hora":             hora,
        "rahu_kala":        rahu_kala,
        "swara":            swara,
        "vastu_zone":       vastu_zone,
        "therapeutic_raga": therapeutic_raga,
        "gem_today":        gem_today,
        "marma_today":      marma_today,
        "plants":           PLANT_DATA,
        "vedic_schools":    VEDIC_SCHOOLS,
        "yuga":             "Kali",
        "alpha":            1.0,
        "dasha":            current_dasha,
        "natal":            NATAL,
    }
    fs["companions"] = companion_state(fs)

    # ── FieldState v1 contract (additive — does not replace existing keys) ──
    _v1_theta_rad = None
    _v1_phi_rad = None
    try:
        _v1_toroid = get_toroid()
        _v1_theta_rad, _v1_phi_rad = _v1_toroid.moment_to_coords(
            _toroid_panchanga(fs))
    except Exception:
        pass

    _v1_nak_itrans = nak_to_itrans(p5.get("nakshatra", ""))
    _v1_tala_info = _NAKSHATRA_TALA.get(
        _v1_nak_itrans, {"tala": "Ādi", "beats": 8})
    _v1_gati = _GUNA_GATI.get(
        p5.get("guna", "").lower(), "chatusra")
    _v1_elem = p5.get("element", "ether").lower()

    _v1_center = 0.0
    _v1_peaks = []
    try:
        _v1_coh = get_coherence_score(now)
        _v1_center = _v1_coh.get("coherence_top", 0.0)
    except Exception:
        pass
    try:
        _v1_t = get_toroid()
        _v1_results = _v1_t.field_query(
            _toroid_panchanga(fs), top_n=5)
        _v1_peaks = [
            {"entity_id": r["entity_id"],
             "score": round(r["score"], 3),
             "element": r.get("element", "")}
            for r in _v1_results
        ]
    except Exception:
        pass

    fs["field_state_v1"] = {
        "version": 1,
        "theta": {
            "panchanga": {
                "tithi": p5["tithi"],
                "tithi_num": p5["tidx"] + 1,
                "paksha": p5["paksha"],
                "nakshatra": p5["nakshatra"],
                "nak_lord": p5["nak_lord"],
                "vara": p5["vara"],
                "yoga": yoga,
                "karana": karana,
            },
            "s_layer": None,
            "theta_rad": (round(_v1_theta_rad, 4)
                          if _v1_theta_rad is not None else None),
            "attestation": "OBSERVED",
        },
        "phi": {
            "position": (round(_v1_phi_rad, 4)
                         if _v1_phi_rad is not None else None),
            "label": _phi_to_label(_v1_phi_rad),
            "companion": _phi_to_companion(_v1_phi_rad),
            "element": _v1_elem,
            "guna": p5.get("guna", ""),
            "attestation": "OBSERVED",
        },
        "psi": "jijnasu",
        "field_signals": {
            "center_strength": round(_v1_center, 3),
            "directional_bias": _ELEMENT_DIR_BIAS.get(
                _v1_elem, _ELEMENT_DIR_BIAS["ether"]),
            "coherence_peaks": _v1_peaks,
            "attestation": "SYNTHESIS",
        },
        "sound": {
            "raga": devi_raga_name,
            "tala": _v1_tala_info["tala"],
            "tala_beats": _v1_tala_info["beats"],
            "gati": _v1_gati,
            "bpm": mu.get("bpm", 72),
            "arc_phase": round(p5["tidx"] / 30.0, 3),
            "attestation": {
                "raga": "OBSERVED",
                "tala": "TRADITIONAL",
                "gati": "SYNTHESIS",
                "bpm": "OBSERVED",
            },
        },
        "muhurta": {
            "name": mu.get("name", ""),
            "quality": hora.get("hora_quality", "neutral"),
            "rahu_kala_active": rahu_kala.get("rahu_kala_active", False),
        },
    }

    # sound_state: full derived sound structure for UI surfaces
    fs["sound_state"] = _derive_sound_state(fs)

    # visual: rendering data for canvas surfaces
    import math as _math
    _v_elem = p5.get("element", "ether").lower()
    _v_nak_idx = NAKSHATRAS.index(p5["nakshatra"]) if p5.get("nakshatra") in NAKSHATRAS else 0
    fs["visual"] = {
        "nak_theta": round(_v_nak_idx / 27 * 2 * _math.pi, 4),
        "element_rgb": _ELEMENT_RGB.get(_v_elem, _ELEMENT_RGB["ether"]),
        "guna_alpha": _GUNA_ALPHA.get(p5.get("guna", "").lower(), 0.5),
        "phi_default": round(_math.pi, 5),
        "arc_phase": round(p5.get("tidx", 0) / 30.0, 3),
    }

    return fs


def _ascii_key(text):
    raw = unicodedata.normalize("NFKD", str(text or ""))
    return "".join(ch for ch in raw if not unicodedata.combining(ch)).strip()


def generate_composition(panchanga):
    nak_iast = panchanga.get("nakshatra", "")
    nak = nak_to_itrans(nak_iast)
    element = str(panchanga.get("element", "air") or "air").lower()
    guna = str(panchanga.get("guna", "tamas") or "tamas").lower()
    vara = str(panchanga.get("vara", "") or "")
    tithi = str(panchanga.get("tithi", "") or "")
    devi = (panchanga.get("devi") or ["", ""])[0]
    muhurta = panchanga.get("muhurta") or {}
    bpm = int(muhurta.get("bpm", 72) or 72)

    # Tala/beats from module-level _NAKSHATRA_TALA; reasons are local
    _tala_reasons = {
        "Ashwini": "Ashwini Kumaras = swift pairs", "Bharani": "Yama = 6 seasons",
        "Krittika": "Agni = 8 Vasus fire", "Rohini": "Brahma = full creation",
        "Mrigashira": "Soma = 7 notes of scale", "Ardra": "Rudra = 10 forms",
        "Punarvasu": "Aditi = boundless return", "Pushya": "Brihaspati = 7 planets",
        "Ashlesha": "Nagas = 12 serpent kings", "Magha": "Pitrs = 8 ancestors",
        "Purva Phalguni": "Bhaga = 6 seasons", "Uttara Phalguni": "Aryaman = solar 8",
        "Hasta": "Savitar = 7 sunrays", "Chitra": "Tvashtr = 8 directions",
        "Swati": "Vayu = 7 winds", "Vishakha": "Indra/Agni = 10 forms",
        "Anuradha": "Mitra = 7 Adityas", "Jyeshtha": "Indra = 12 months",
        "Mula": "Nirrti = 8 directions", "Purva Ashadha": "Apas = 6 waters",
        "Uttara Ashadha": "Vishvadevas = 8", "Shravana": "Vishnu = 7 steps",
        "Dhanishta": "Vasus = 8 attendants", "Shatabhisha": "Varuna = 100 physicians",
        "Purva Bhadrapada": "Aja Ekapada = 8", "Uttara Bhadrapada": "Ahirbudhnya = 12",
        "Revati": "Pushan = 7 directions",
    }
    nakshatra_tala = {
        k: {**v, "reason": _tala_reasons.get(k, "")} for k, v in _NAKSHATRA_TALA.items()
    }
    nakshatra_instrument = {
        "Dhanishta": "mridanga",
        "Shravana": "tabla",
        "Hasta": "kartal",
        "Ashwini": "ghungru",
        "Mrigashira": "tabla",
        "Ardra": "damaru",
        "Purva Phalguni": "mridanga",
        "Uttara Phalguni": "mridanga",
        "Magha": "mridanga",
        "Vishakha": "kartal",
    }
    tala_bols = _TALA_BOLS
    guna_laya = {
        "sattva": {"ratio": 1, "name": "Saral", "reason": "sattva = pure · no division needed"},
        "rajas": {"ratio": 2, "name": "Dugun", "reason": "rajas = active · double time activates"},
        "tamas": {"ratio": 1.5, "name": "Dedh", "reason": "tamas = heavy · 3:2 lifts without forcing"},
    }
    vara_raga = {
        "ravivara": "Bhairava",
        "somavara": "Bageshri",
        "mangalavara": "Puriya",
        "budhavara": "Bhimpalasi",
        "guruvara": "Yaman",
        "shukravara": "Marwa",
        "shanivara": "Darbari",
    }
    prahar_raga = {
        "brahma": "Lalit",
        "dawn": "Bhairava",
        "morning": "Bhairavi",
        "afternoon": "Sarang",
        "lateAfternoon": "Bhimpalasi",
        "dusk": "Marwa",
        "night": "Bageshri",
        "deepNight": "Darbari",
    }
    raga_desc = {
        "Bhairava": "Dawn · Śiva · śānta · sacred stillness",
        "Bhairavi": "Morning · Devī · karuṇā · tender farewell",
        "Sarang": "Midday · longing · water · searching",
        "Bhimpalasi": "Afternoon · śṛṅgāra · yearning love",
        "Marwa": "Dusk · vīra · unresolved · the held note",
        "Bageshri": "Night · śṛṅgāra · devotion · Bāgeshvarī",
        "Darbari": "Midnight · karuṇā · Akbar's rāga · depth",
        "Yaman": "Evening · śṛṅgāra · beauty · Kalyāṇī",
        "Puriya": "Dusk · raudra · intensity · searching",
        "Lalit": "Pre-dawn · adbhuta · wonder · the arriving",
    }
    raga_gamaka = {
        "Bhairava": "slow mīḍ on Re · andolan on Ga",
        "Bhairavi": "gentle kan on komal notes",
        "Marwa": "sharp mīḍ on Ga · held komal Re",
        "Bageshri": "soft andolan on Ga and Ni",
        "Darbari": "deep andolan on Ga · heavy mīḍ",
        "Yaman": "ascending mīḍ on tīvra Ma",
        "Bhimpalasi": "gentle mīḍ on Ga · soft Ni",
    }
    guna_bpm_modifier = {"sattva": 0.9, "rajas": 1.1, "tamas": 0.85}

    now_dt = panchanga.get("now")
    if isinstance(now_dt, str):
        try:
            now_dt = datetime.fromisoformat(now_dt)
        except ValueError:
            now_dt = None
    hour = now_dt.hour if isinstance(now_dt, datetime) else datetime.now().hour

    def get_prahar(h):
        if h < 4:
            return "deepNight"
        if h < 6:
            return "brahma"
        if h < 9:
            return "dawn"
        if h < 12:
            return "morning"
        if h < 15:
            return "afternoon"
        if h < 18:
            return "lateAfternoon"
        if h < 21:
            return "dusk"
        return "night"

    prahar = get_prahar(hour)
    vara_key = _ascii_key(vara.split()[0]).lower()
    raga = prahar_raga.get(prahar, vara_raga.get(vara_key, "Yaman"))
    tala_info = nakshatra_tala.get(nak, {"tala": "Adi", "beats": 8, "reason": "default"})
    lead_instrument = nakshatra_instrument.get(nak, "tabla")
    laya_info = guna_laya.get(guna, guna_laya["sattva"])
    bols = tala_bols.get(tala_info["tala"], tala_bols["Adi"])
    final_bpm = max(40, min(120, int(bpm * guna_bpm_modifier.get(guna, 1.0))))

    return {
        "tala": tala_info["tala"],
        "beats": tala_info["beats"],
        "bols": bols,
        "lead_instrument": lead_instrument,
        "laya": laya_info["ratio"],
        "laya_name": laya_info["name"],
        "raga": raga,
        "raga_desc": raga_desc.get(raga, ""),
        "gamaka": raga_gamaka.get(raga, ""),
        "bpm": final_bpm,
        "prahar": prahar,
        "reasoning": {
            "tala": tala_info["reason"],
            "instrument": f"{nak_iast or nak} symbol → {lead_instrument}",
            "laya": laya_info["reason"],
            "raga": f"{prahar} prahar → {raga}",
            "bpm": f"{guna} guna → {final_bpm}bpm",
        },
        "field": {
            "nakshatra": nak_iast,
            "nakshatra_itrans": nak,
            "element": element,
            "guna": guna,
            "vara": vara,
            "tithi": tithi,
            "devi": devi,
        },
    }


# ══════════════════════════════════════════════════════════════
# INTERPRET FIELD — jyotish reading for today
# ══════════════════════════════════════════════════════════════

# Rāśi names (sidereal zodiac, 30° each)
RASHIS = [
    "Meṣa", "Vṛṣabha", "Mithuna", "Karka",
    "Siṃha", "Kanyā", "Tulā", "Vṛścika",
    "Dhanu", "Makara", "Kumbha", "Mīna",
]

# Pada → navāṃśa rāśi (each nakshatra pada maps to one of 12 signs)
# The cycle repeats: Aries for pada 1 of Ashwini, Taurus for pada 2, etc.
# navamsa_index = (nak_index * 4 + pada - 1) % 12

# Guna-specific guidance
_GUNA_STUDY = {
    "sattva": "scripture · meditation · sacred music · japa",
    "rajas":  "skill-building · creative work · strategy · service",
    "tamas":  "shadow work · rest · root clearing · silence",
}
_GUNA_AVOID = {
    "sattva": "overwork · harsh speech · intoxicants",
    "rajas":  "laziness · procrastination · excessive sleep",
    "tamas":  "new ventures · public declarations · travel",
}
_GUNA_PRACTICE = {
    "sattva": "prāṇāyāma · sūrya namaskāra · satsaṅga",
    "rajas":  "vigorous āsana · karma yoga · focused building",
    "tamas":  "yoga nidrā · mauna (silence) · grounding walks",
}

# Element-specific guidance
_ELEMENT_PRACTICE = {
    "fire":  "agnihotra · sun gazing · intensity work",
    "earth": "gardening · body work · grounding · cooking",
    "water": "bath ritual · emotional clearing · flow",
    "air":   "prāṇāyāma · study · communication · travel",
    "ether": "meditation · space · listening · silence",
}

# Dosha-specific guidance
_DOSHA_FOOD = {
    "vata":  "warm · moist · grounding — ghee · root vegetables · warm milk",
    "pitta": "cooling · sweet · bitter — coconut · cucumber · coriander",
    "kapha": "light · dry · stimulating — ginger · greens · honey",
}


def _calc_approx_moon_lon(days_from_ref):
    """Approximate sidereal Moon longitude from lunation days.

    Not ephemeris-accurate — uses mean lunar motion (13.176°/day).
    Good enough for nakshatra/pada/rashi estimation.
    """
    # Mean lunar motion: ~13.176°/day
    # Reference: 2025-01-13 new moon ≈ Moon near 0° sidereal (Ashwini)
    return (days_from_ref * 13.176) % 360


def _pada_from_moon(moon_lon):
    """Nakshatra pada (1-4) from Moon longitude."""
    nak_size = 360.0 / 27.0
    pada_size = nak_size / 4.0
    return int(moon_lon % nak_size / pada_size) + 1


def _navamsa_rashi(nak_idx, pada):
    """Navāṃśa rāśi from nakshatra index and pada."""
    return RASHIS[(nak_idx * 4 + pada - 1) % 12]


def _moon_rashi(moon_lon):
    """Rāśi from Moon longitude."""
    return RASHIS[int(moon_lon / 30) % 12]


def _current_dasha(days_from_ref):
    """Approximate current Vimśottarī mahādaśā lord.

    Uses the nakshatra-lord cycle: each nakshatra maps to a
    daśā lord in the 9-lord sequence. The elapsed fraction
    within the nakshatra determines how far into that lord's
    period we are.
    """
    nak_size = 360.0 / 27.0
    moon_lon = _calc_approx_moon_lon(days_from_ref)
    nak_idx = int(moon_lon / nak_size) % 27
    lord_name, lord_years = DASHA_SEQUENCE[nak_idx % 9]
    fraction_elapsed = (moon_lon % nak_size) / nak_size
    balance = lord_years * (1.0 - fraction_elapsed)
    return {
        "lord":    lord_name,
        "years":   lord_years,
        "balance": round(balance, 2),
    }


def interpret_field(now=None):
    """Jyotish interpretation layer for today.

    Returns a reading based on the current pañcāṅga state,
    combining nakshatra, graha, tithi, and guna data from
    the loaded datasets.

    Keys returned:
        graha_quality  — today's dominant graha and its qualities
        nakshatra_pada — current pada with navāṃśa rāśi
        moon_rashi     — approximate sidereal Moon sign
        dasha          — approximate current mahādaśā lord
        tithi_quality  — what this tithi is for
        practice       — recommended practice for today
        study          — what to study
        avoid          — what to avoid
        dosha_food     — Ayurvedic food guidance
        gana           — temperament of the nakshatra (deva/manushya/rakshasa)
        themes         — nakshatra themes from dataset
    """
    if now is None:
        now = datetime.now()
    days = (now - _REF_DATE).total_seconds() / 86400

    # panchanga (reuse existing calc)
    p5 = calc_panchanga(now)
    nak = p5["nak_data"]
    nak_idx = NAKSHATRAS.index(p5["nakshatra"]) if p5["nakshatra"] in NAKSHATRAS else 0

    # Moon longitude + pada
    moon_lon = _calc_approx_moon_lon(days)
    pada = _pada_from_moon(moon_lon)
    navamsa = _navamsa_rashi(nak_idx, pada)
    m_rashi = _moon_rashi(moon_lon)

    # graha of the day (vara lord)
    vara_graha_order = ["Sūrya", "Candra", "Maṅgala", "Budha", "Guru", "Śukra", "Śani"]
    vara_lord = vara_graha_order[now.weekday()]
    vara_qualities = _GRAHA_QUALITIES.get(vara_lord, [])

    # nakshatra lord qualities
    nak_lord = p5["nak_lord"]
    nak_lord_qualities = _GRAHA_QUALITIES.get(nak_lord, [])

    # combined graha quality: vara lord + nakshatra lord
    combined_qualities = list(dict.fromkeys(vara_qualities + nak_lord_qualities))

    # guna → guidance
    guna = nak.get("guna", "sattva").lower()
    if guna not in _GUNA_STUDY:
        guna = "sattva"

    # dosha
    dosha = nak.get("dosha", "vata").lower()
    if dosha not in _DOSHA_FOOD:
        dosha = "vata"

    # tithi quality
    tithi_name = p5["tithi"]
    tithi_qual = _TITHI_QUALITY.get(tithi_name, "")

    # dasha
    dasha = get_current_dasha(now)

    # themes
    themes = nak.get("themes", "").split() if nak.get("themes") else []
    qualities = nak.get("qualities", [])

    # element
    element = nak.get("element", "fire").lower()
    if element not in _ELEMENT_PRACTICE:
        element = "fire"

    return {
        "graha_quality": {
            "vara_lord":       vara_lord,
            "vara_qualities":  vara_qualities,
            "nak_lord":        nak_lord,
            "nak_qualities":   nak_lord_qualities,
            "combined":        combined_qualities,
        },
        "nakshatra_pada": {
            "nakshatra":  p5["nakshatra"],
            "pada":       pada,
            "navamsa":    navamsa,
            "deity":      nak.get("deity", ""),
            "shakti":     nak.get("shakti", ""),
            "symbol":     nak.get("symbol", ""),
        },
        "moon_rashi":    m_rashi,
        "dasha":         dasha,
        "tithi_quality":  tithi_qual,
        "gana":          nak.get("gana", ""),
        "themes":        qualities or themes,
        "practice":      _GUNA_PRACTICE[guna] + " · " + _ELEMENT_PRACTICE[element],
        "study":         _GUNA_STUDY[guna],
        "avoid":         _GUNA_AVOID[guna],
                "dosha_food":    _DOSHA_FOOD[dosha],
    }


# ══════════════════════════════════════════════════════════════
# COHERENCE SCORING — validate today against constraints
# ══════════════════════════════════════════════════════════════

def get_coherence_score(now=None):
    """Score today's panchanga against coherence constraints.

    Returns coherence data for tithi + element + guna.
    Uses hybrid vector+rule scoring when vector store is present,
    falls back to pure rule scoring via score_batch().
    """
    if not _coherence:
        return {"error": "CoherenceEngine not available", "score": 0, "tithi": "unknown"}

    if now is None:
        now = datetime.now()

    p5 = calc_panchanga(now)
    tithi_num = p5.get("tidx", 1)
    tithi_for_scoring = ((tithi_num % 15) or 15)

    try:
        # Avoid recursion: field_state() calls get_coherence_score() for field_signals.
        # Hybrid scoring only needs a minimal snapshot for context (nakshatra, etc.).
        fs = {"panchanga": p5}
        # prefer hybrid scoring (vector+rule); falls back internally
        scores = _coherence.score_hybrid(tithi_for_scoring, limit=5, fs=fs)

        if scores:
            top = scores[0]
            top_score = top.score
            top_match = top.candidate
            top_class = top.node_class
        else:
            top_score = 0
            top_match = "none"
            top_class = "rift"

        return {
            "tithi": p5["tithi"],
            "tithi_num": tithi_for_scoring,
            "coherence_top": top_score,
            "top_match": top_match,
            "node_class": top_class,
            "all_scores": [
                {
                    "candidate": s.candidate,
                    "score": s.score,
                    "reasons": s.reasons,
                    "node_class": s.node_class,
                }
                for s in scores
            ],
        }
    except Exception as e:
        return {
            "error": str(e),
            "tithi": p5.get("tithi", "unknown"),
            "tithi_num": tithi_for_scoring,
            "score": 0,
            "node_class": "rift",
        }


def _normalize_vara_for_toroid(vara_name):
    text = unicodedata.normalize("NFKD", str(vara_name or ""))
    text = text.encode("ascii", "ignore").decode("ascii").lower()
    text = text.split()[0]
    return text


def _toroid_panchanga(fs):
    p5 = fs["panchanga"]
    nak_data = p5.get("nak_data", {}) or {}
    return {
        "tithi_num": int(p5.get("tidx", 0)) + 1,
        "nakshatra": nak_to_itrans(p5.get("nakshatra", "")),
        "vara": _normalize_vara_for_toroid(p5.get("vara", "")),
        "element": (nak_data.get("element") or "").lower(),
        "guna": (nak_data.get("guna") or "").lower(),
    }


def get_toroid():
    global _toroid
    if _toroid is None:
        if ToroidalField is None or load_all_entities is None:
            raise RuntimeError("ToroidalField not available")
        entities = load_all_entities()
        _toroid = ToroidalField()
        if not getattr(_toroid, "entities", None):
            for eid, coords in entities.items():
                _toroid.register_entity(eid, coords[0], coords[1])
    return _toroid


# ══════════════════════════════════════════════════════════════
# HTTP API  —  python kernel.py [port]
# ══════════════════════════════════════════════════════════════

def _json_serial(obj):
    """Handle datetime and tuple serialization for JSON."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, tuple):
        return list(obj)
    raise TypeError(f"Type {type(obj)} not serializable")


def _hour_chandas(hour=None):
    hour = datetime.now().hour if hour is None else int(hour)
    hour_map = (
        (range(4, 6), {"chandas": "Gayatri", "syllables": 8, "padas": 4}),
        (range(6, 9), {"chandas": "Anushtubh", "syllables": 8, "padas": 4}),
        (range(9, 12), {"chandas": "Trishtubh", "syllables": 11, "padas": 4}),
        (range(12, 15), {"chandas": "Jagati", "syllables": 12, "padas": 4}),
        (range(15, 18), {"chandas": "Trishtubh", "syllables": 11, "padas": 4}),
        (range(18, 21), {"chandas": "Anushtubh", "syllables": 8, "padas": 4}),
        (range(21, 24), {"chandas": "Gayatri", "syllables": 8, "padas": 4}),
        (range(0, 4), {"chandas": "Gayatri", "syllables": 8, "padas": 4}),
    )
    for hour_range, payload in hour_map:
        if hour in hour_range:
            return payload
    return {"chandas": "Anushtubh", "syllables": 8, "padas": 4}


def _codex_coherence(fs, limit=5):
    try:
        toroid = get_toroid()
        return toroid.field_query(_toroid_panchanga(fs), top_n=limit, category=None)
    except Exception:
        return []


# ══════════════════════════════════════════════════════════════
# /observe — domain-separated reading for a single entity
# ══════════════════════════════════════════════════════════════

def _observe_astrology(entity_id, fs):
    """Astrology domain: entity data from toroidal_field."""
    p5 = fs["panchanga"]
    nak = p5.get("nak_data") or {}
    entity_data = get_entity_data(entity_id)
    if entity_data:
        content = entity_data
    else:
        content = {
            "entity": entity_id,
            "nakshatra": p5.get("nakshatra", ""),
            "nak_lord": p5.get("nak_lord", ""),
            "tithi": p5.get("tithi", ""),
            "paksha": p5.get("paksha", ""),
            "vara": p5.get("vara", ""),
            "element": p5.get("element", ""),
            "guna": p5.get("guna", ""),
        }
    return {
        "content": content,
        "source": "toroidal_field entity registry + panchanga",
        "attestation": nak.get("attestation_status", "OBSERVED"),
    }


def _observe_ayurveda(fs):
    """Ayurveda domain: herb_exemplars + dosha_nakshatra_matrix."""
    p5 = fs["panchanga"]
    nak_itrans = nak_to_itrans(p5.get("nakshatra", ""))

    # dosha for current nakshatra
    dosha_row = None
    for row in _dosha_nakshatra:
        if str(row.get("nakshatra", "")).lower() == nak_itrans.lower():
            dosha_row = row
            break
    if not dosha_row:
        # fuzzy: try first 4 chars
        for row in _dosha_nakshatra:
            if str(row.get("nakshatra", ""))[:4].lower() == nak_itrans[:4].lower():
                dosha_row = row
                break

    # herb recommendation from dosha row or herb_exemplars
    herb_rec = (dosha_row or {}).get("herb_recommendation", "")
    herb_row = None
    for row in _herb_exemplars:
        if herb_rec and herb_rec.lower() in str(row.get("name_common", "")).lower():
            herb_row = row
            break
    # Don't fall back to wrong herb — use dosha recommendation directly

    content = {
        "dosha_profile": dosha_row or {"note": "no dosha row for " + nak_itrans},
        "herb": {
            "name": (herb_row or {}).get("name_iast", herb_rec),
            "common": (herb_row or {}).get("name_common", herb_rec),
            "rasa": (herb_row or {}).get("rasa", ""),
            "virya": (herb_row or {}).get("virya", ""),
            "dosha_effect": (herb_row or {}).get("dosha_effect", ""),
            "preparation": (herb_row or {}).get("preparation", ""),
        } if (herb_row or herb_rec) else {},
    }
    attestation = (dosha_row or {}).get("attestation_status",
                   (herb_row or {}).get("attestation_status", "TRADITIONAL"))
    return {
        "content": content,
        "source": "datasets/ayurveda/herb_exemplars.csv + datasets/ayurveda/dosha_nakshatra_matrix.csv",
        "attestation": attestation,
    }


def _observe_marma(fs):
    """Marma domain: body_region_marma.csv."""
    body = fs["panchanga"].get("body_region", "")
    marma = compute_marma(body)
    # get full row for attestation
    region = str(body).lower().strip()
    att = "TRADITIONAL"
    for row in _body_marma:
        if str(row.get("body_region", "")).lower().strip() == region:
            att = row.get("attestation_status", "TRADITIONAL")
            marma["therapeutic_action"] = row.get("therapeutic_action", "")
            marma["contraindication"] = row.get("contraindication", "")
            break
    return {
        "content": marma,
        "source": "datasets/marma/body_region_marma.csv",
        "attestation": att,
    }


def _observe_ratna(fs):
    """Ratna domain: graha_gems.csv."""
    weekday = fs["panchanga"]["now"].weekday()
    gem = compute_gem_today(weekday)
    # full row
    vara_lords = ["Surya", "Chandra", "Mangala", "Budha", "Guru", "Shukra", "Shani"]
    lord = vara_lords[weekday] if weekday < 7 else "Surya"
    att = "TRADITIONAL"
    for row in _graha_gems:
        if str(row.get("graha", "")).lower() == lord.lower():
            gem["metal"] = row.get("metal", "")
            gem["finger"] = row.get("finger", "")
            gem["mantra"] = row.get("mantra_for_consecration", "")
            att = row.get("attestation_status", "TRADITIONAL")
            break
    return {
        "content": gem,
        "source": "datasets/ratna/graha_gems.csv",
        "attestation": att,
    }


def _observe_gandharva(fs):
    """Gandharva domain: raga_therapeutic.csv."""
    element = fs["panchanga"].get("element", "")
    now = fs["panchanga"]["now"]
    therapeutic = compute_therapeutic_raga(now, element)
    # find full row
    att = therapeutic.get("attestation", "TRADITIONAL")
    raga_name = therapeutic.get("therapeutic_raga", "")
    source_text = ""
    for row in _raga_therapeutic:
        if str(row.get("raga", "")).lower() == raga_name.lower():
            therapeutic["conditions"] = row.get("conditions", "")
            therapeutic["duration_min"] = row.get("duration", "")
            att = row.get("attestation", att)
            source_text = row.get("source", "")
            break
    return {
        "content": therapeutic,
        "source": "datasets/gandharva/raga_therapeutic.csv" + (f" ({source_text})" if source_text else ""),
        "attestation": att,
    }


def _observe_vastu(fs):
    """Vastu domain: perimeter_deities.csv."""
    vara_graha = fs.get("vara_graha") or {}
    vara_lord = vara_graha.get("name", "")
    nak = fs["panchanga"].get("nakshatra", "")
    zone = compute_vastu_zone(vara_lord, nak)
    # full row for attestation
    att = "OBSERVED"
    for row in _vastu_perimeter:
        if row.get("position", "") == zone.get("zone_name", ""):
            zone["element"] = row.get("element", "")
            zone["function"] = row.get("function", "")
            att = row.get("attestation_status", "OBSERVED")
            break
    return {
        "content": zone,
        "source": "datasets/vastu/perimeter_deities.csv",
        "attestation": att,
    }


def _observe_synthesis(fs, entity_id, domains):
    """Synthesis: brief integration from domain readings. 3 sentences max."""
    p5 = fs["panchanga"]
    nak = p5.get("nakshatra", "")
    dosha_info = domains.get("ayurveda", {}).get("content", {}).get("dosha_profile", {})
    primary_dosha = dosha_info.get("primary_dosha", "") if isinstance(dosha_info, dict) else ""
    raga = domains.get("gandharva", {}).get("content", {}).get("therapeutic_raga", "")
    gem = domains.get("ratna", {}).get("content", {}).get("primary_gem", "")
    marma = domains.get("marma", {}).get("content", {}).get("marma_name", "")
    zone = domains.get("vastu", {}).get("content", {}).get("zone_deity", "")

    parts = []
    parts.append(f"Entity {entity_id} observed under {nak}")
    if primary_dosha:
        parts[0] += f" with {primary_dosha} dosha active"
    parts[0] += "."
    mid = []
    if raga:
        mid.append(f"rāga {raga}")
    if gem:
        mid.append(f"{gem}")
    if marma:
        mid.append(f"marma {marma}")
    if mid:
        parts.append("Coherent supports: " + ", ".join(mid) + ".")
    if zone:
        parts.append(f"Vāstu alignment through {zone}.")
    synthesis = " ".join(parts[:3])
    return {
        "content": synthesis,
        "source": "Coherence Atlas synthesis",
        "attestation": "SYNTHESIS",
    }


def _load_canonical_plant(entity_id):
    """Load a canonical plant entity from datasets/plants/<entity_id>.json.

    Returns the full domain-separated entity, or None if not found.
    """
    plant_file = _DATA / "plants" / f"{entity_id}.json"
    if not plant_file.exists():
        return None
    try:
        with open(plant_file, encoding="utf-8") as f:
            plant = json.load(f)
        # Reshape domains into observe format: {content, source, attestation}
        raw_domains = plant.get("domains", {})
        domains = {}
        for dkey, dval in raw_domains.items():
            domains[dkey] = {
                "content": {k: v for k, v in dval.items()
                            if k not in ("source", "attestation")},
                "source": dval.get("source", ""),
                "attestation": dval.get("attestation", ""),
            }
        result = {
            "entity": entity_id,
            "identity": plant.get("identity", {}),
            "field_coordinates": plant.get("field_coordinates", {}),
            "nakshatra_correspondence": plant.get("nakshatra_correspondence", {}),
            "domains": domains,
        }
        # Include use_ratings if present
        ur = plant.get("use_ratings")
        if ur:
            result["use_ratings"] = ur
        return result
    except Exception:
        return None


def _score_use_ratings(use_ratings, phi):
    """Given use_ratings and a request phi, compute current_phi_score
    and recommended_use by finding the closest rating."""
    if not use_ratings or phi is None:
        return None
    ratings = use_ratings.get("ratings", {})
    if not ratings:
        return None
    # Interpolate score at request phi by finding nearest rating
    best_name = None
    best_dist = float("inf")
    for name, r in ratings.items():
        d = abs(r.get("phi", 0) - phi)
        if d < best_dist:
            best_dist = d
            best_name = name
    # Linear interpolation between two nearest
    sorted_r = sorted(ratings.items(), key=lambda x: x[1].get("phi", 0))
    score = 0.5  # default
    for i in range(len(sorted_r) - 1):
        lo_name, lo = sorted_r[i]
        hi_name, hi = sorted_r[i + 1]
        lo_phi, hi_phi = lo.get("phi", 0), hi.get("phi", 0)
        if lo_phi <= phi <= hi_phi and hi_phi > lo_phi:
            t = (phi - lo_phi) / (hi_phi - lo_phi)
            score = lo.get("score", 0) * (1 - t) + hi.get("score", 0) * t
            break
    else:
        if phi <= sorted_r[0][1].get("phi", 0):
            score = sorted_r[0][1].get("score", 1.0)
        elif phi >= sorted_r[-1][1].get("phi", 0):
            score = sorted_r[-1][1].get("score", 0.1)
    return {
        "current_phi": round(phi, 3),
        "current_phi_score": round(score, 3),
        "recommended_use": best_name,
        "recommended_label": ratings.get(best_name, {}).get("label", ""),
        "attestation": "SYNTHESIS",
        "note": "descriptive not prescriptive",
    }


def observe_entity(entity_id, phi=None, psi=None):
    """Full domain-separated observation for a single entity.

    Args:
        entity_id: entity key (e.g. 'nakshatra_dhanishtha')
        phi: optional φ axis position (float, radians)
        psi: optional ψ/engagement mode label (str)

    Returns dict with entity, phi, psi, and 7+ domain readings.
    """
    def _semantic_query(_entity_id: str, _fs: Optional[Dict[str, Any]] = None) -> str:
        parts = [str(_entity_id or "").replace("_", " ").strip()]
        if _fs:
            p5 = (_fs.get("panchanga") or {}) if isinstance(_fs, dict) else {}
            for key in ("nakshatra", "tithi", "vara", "element", "guna"):
                value = p5.get(key)
                if value:
                    parts.append(str(value).strip())
        return " · ".join(p for p in parts if p)

    def _maybe_add_semantic(_payload: Dict[str, Any], _entity_id: str, _fs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        query = _semantic_query(_entity_id, _fs=_fs)
        semantic: Dict[str, Any] = {"query": query, "hits": [], "entity_chunks": []}
        try:
            from npu_engine.vector_store import get_vector_store
            store = get_vector_store()
            semantic["hits"] = store.search(query, n=6)
            semantic["entity_chunks"] = store.entity_chunks(_entity_id)
        except Exception as exc:
            semantic["error"] = str(exc)

        if isinstance(_payload.get("domains"), dict):
            _payload["domains"]["semantic"] = semantic
        else:
            _payload["semantic"] = semantic
        return _payload

    # Check for canonical plant entity first
    canonical = _load_canonical_plant(entity_id)
    if canonical:
        canonical["phi"] = phi
        canonical["psi"] = psi
        # Compute phi-relative use score if use_ratings present
        ur = canonical.get("use_ratings")
        if ur and phi is not None:
            canonical["phi_score"] = _score_use_ratings(ur, phi)
        return _maybe_add_semantic(canonical, entity_id, _fs=None)

    fs = field_state()

    domains = {}
    domains["astrology"] = _observe_astrology(entity_id, fs)
    domains["ayurveda"] = _observe_ayurveda(fs)
    domains["marma"] = _observe_marma(fs)
    domains["ratna"] = _observe_ratna(fs)
    domains["gandharva"] = _observe_gandharva(fs)
    domains["vastu"] = _observe_vastu(fs)
    domains["synthesis"] = _observe_synthesis(fs, entity_id, domains)

    payload = {
        "entity": entity_id,
        "phi": phi,
        "psi": psi,
        "domains": domains,
    }
    return _maybe_add_semantic(payload, entity_id, _fs=None)


def install_download_handoff(repo_root=None, out=print):
    """Disabled — the repo is the source of truth now."""
    out("  ● Downloads handoff disabled — repo is truth")


def _claude_generate(system: str, prompt: str, max_tokens: int = 800) -> Optional[str]:
    """Call Claude API via anthropic SDK or urllib fallback.

    Returns generated text, or None if API key missing or call fails.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return None
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text if msg.content else None
    except ImportError:
        pass
    # Fallback: raw urllib
    try:
        import urllib.request
        body = json.dumps({
            "model": "claude-sonnet-4-20250514",
            "max_tokens": max_tokens,
            "system": system,
            "messages": [{"role": "user", "content": prompt}],
        }).encode()
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=body,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        content = data.get("content", [])
        return content[0]["text"] if content else None
    except Exception as e:
        print(f"  ⚠ Claude API error: {e}")
        return None


def create_app():
    from flask import Flask, Response, jsonify, redirect, request, send_file, send_from_directory

    app = Flask(__name__, static_folder=None)

    # OSC client and sound state — shared with sound_bp
    from npu_engine.routes._sound_state import send_osc as _send_osc
    import npu_engine.routes._sound_state as _ss

    # Supabase config (anon key — used by /observe plant enrichment)
    from npu_engine.routes.render_bp import _SUPA_URL, _SUPA_KEY

    @app.after_request
    def _cors(resp):
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        resp.headers["Pragma"] = "no-cache"
        resp.headers["Expires"] = "0"
        return resp

    @app.errorhandler(404)
    def _not_found(e):
        return jsonify({"error": "not found", "hint": "try /field or /spine"}), 404

    # ── Health/system/snapshot/dashboard routes → system_bp ────────
    from npu_engine.routes.system_bp import system_bp
    app.register_blueprint(system_bp)

    # ── Jyotisha chart engine → jyotish_bp ────────
    from npu_engine.routes.jyotish_bp import jyotish_bp
    app.register_blueprint(jyotish_bp)
    print(f"  [jyotish] /jyotish/natal /jyotish/transits /jyotish/compute /jyotish/tara/<nak> /jyotish/compatibility")

    # ── Nitya Devi → nitya_bp ────────
    from npu_engine.routes.nitya_bp import nitya_bp
    app.register_blueprint(nitya_bp)
    print(f"  [nitya] /nitya/devi/today /nitya/devi/<tithi> /nitya/field/<tithi> /nitya/srichakra")

    @app.route("/osc", methods=["POST", "OPTIONS"])
    def _osc_proxy():
        if request.method == "OPTIONS":
            return "", 204
        try:
            data = request.get_json(force=True)
            osc_path = data.get("path", "")
            args = data.get("args", [])
            if osc_path and osc_path.startswith("/atlas"):
                _send_osc(osc_path, args)
                return jsonify({"ok": True})
            return jsonify({"error": "invalid path"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    _field_override = {}
    _field_override_ts = [0]

    @app.route("/field/override", methods=["POST", "DELETE"])
    def _field_override_route():
        if request.method == "DELETE":
            _field_override.clear()
            return jsonify({"cleared": True})
        data = request.json or {}
        _field_override.update(data)
        _field_override_ts[0] = __import__("time").time()
        return jsonify({"override": _field_override})

    def _merge_override(fs):
        """Deep merge override into field state."""
        if not _field_override:
            return fs
        # Auto-expire after 120s
        if __import__("time").time() - _field_override_ts[0] > 120:
            _field_override.clear()
            return fs
        for k, v in _field_override.items():
            if isinstance(v, dict) and isinstance(fs.get(k), dict):
                fs[k].update(v)
            else:
                fs[k] = v
        return fs

    @app.route("/field")
    def _field():
        fs = field_state()
        fs = _merge_override(fs)
        return app.response_class(
            json.dumps(fs, default=_json_serial, ensure_ascii=False),
            mimetype="application/json",
        )

    @app.route("/entity/<path:entity_id>")
    def _entity(entity_id):
        payload = get_entity_data(entity_id)
        if payload is None:
            return app.response_class(
                json.dumps({"error": f"Entity not found: {entity_id}"}, ensure_ascii=False),
                mimetype="application/json",
                status=404,
            )
        return app.response_class(
            json.dumps(payload, default=_json_serial, ensure_ascii=False),
            mimetype="application/json",
        )

    @app.route("/interpret")
    def _interpret():
        reading = interpret_field()
        return app.response_class(
            json.dumps(reading, default=_json_serial, ensure_ascii=False),
            mimetype="application/json",
        )

    @app.route("/observe", methods=["POST"])
    def _observe():
        body = request.get_json(silent=True) or {}
        entity_id = body.get("entity", "")
        phi = body.get("phi")
        psi = body.get("psi")
        if not entity_id:
            return app.response_class(
                json.dumps({"error": "entity is required"}, ensure_ascii=False),
                mimetype="application/json",
                status=400,
            )
        try:
            result = observe_entity(entity_id, phi=phi, psi=psi)
        except Exception as e:
            import traceback
            return app.response_class(
                json.dumps({"error": str(e), "trace": traceback.format_exc()}, ensure_ascii=False),
                mimetype="application/json",
                status=500,
            )
        # Enrich with torus context if entity is a nakshatra
        try:
            from npu_engine.torus_queries import torus_context_for_entity
            from npu_engine.graph_engine import GraphEngine as _GE
            _g = _GE()
            # Extract nakshatra name from entity_id
            _nak_name = entity_id.replace("nakshatra_", "").replace("_", " ").title()
            _torus = torus_context_for_entity(_nak_name, _g._metadata, _g)
            if _torus:
                result.update(_torus)
        except Exception:
            pass

        # Enrich with deity_attributes if this is a nakshatra
        try:
            if not hasattr(_g, '_metadata'):
                from npu_engine.graph_engine import GraphEngine as _GE
                _g = _GE()
            # Find deity_attr entity matching this nakshatra
            for _eid, _m in _g._metadata.items():
                if _m.get("category") != "deity_attr":
                    continue
                _da = _m.get("attributes", {})
                if _nak_name in _da.get("nakshatra", []):
                    result["deity_attributes"] = {
                        "deity": (_da.get("deity", [""]))[0],
                        "items": [(_da.get(f"item_{i}", [""]))[0] for i in range(1, 5) if (_da.get(f"item_{i}", [""]))[0]],
                        "vahana": (_da.get("vahana", [""]))[0],
                        "mudra": (_da.get("mudra", [""]))[0],
                        "color_body": (_da.get("color_body", [""]))[0],
                        "color_garment": (_da.get("color_garment", [""]))[0],
                        "direction": (_da.get("direction", [""]))[0],
                        "gemstone": (_da.get("gemstone", [""]))[0],
                        "metal": (_da.get("metal", [""]))[0],
                        "time_of_day": (_da.get("time_of_day", [""]))[0],
                        "day": (_da.get("day", [""]))[0],
                        "mantra_bija": (_da.get("mantra_bija", [""]))[0],
                        "shakti_name": (_da.get("shakti_name", [""]))[0],
                        "tattva": (_da.get("tattva", [""]))[0],
                        "rasa": (_da.get("rasa", [""]))[0],
                    }
                    break
        except Exception:
            pass

        # Enrich devi entities with NITYA_DEVIS data + nitya_devi_mapping
        if entity_id.startswith("devi_") or entity_id.startswith("nitya_devi_"):
            try:
                import unicodedata, re as _re
                _devi_slug = entity_id.replace("devi_", "").replace("nitya_devi_", "")
                # Find matching NITYA_DEVIS entry
                for _di, (_dn, _ds, _dd, _dr) in enumerate(NITYA_DEVIS):
                    _dns = unicodedata.normalize("NFKD", _dn).encode("ascii","ignore").decode("ascii").lower()
                    _dns = _re.sub(r"[^a-z]+", "", _dns)
                    _ds2 = _re.sub(r"[^a-z]+", "", _devi_slug)
                    if _dns == _ds2 or _dns.startswith(_ds2) or _ds2.startswith(_dns):
                        # Build character sheet
                        result["devi_sheet"] = {
                            "name": _dn,
                            "symbol": _ds,
                            "description": _dd,
                            "raga": _dr,
                            "tithi_position": _di + 1,
                            "entity_id": entity_id,
                        }
                        # Look up color from nitya_devi_mapping.csv
                        _ndm_path = os.path.join(os.path.dirname(__file__), "datasets", "nitya_devi_mapping.csv")
                        if os.path.exists(_ndm_path):
                            import csv as _csv
                            with open(_ndm_path, encoding="utf-8") as _nf:
                                for _nr in _csv.DictReader(_nf):
                                    _nn = _nr.get("nitya_devi", "")
                                    _nn_clean = _re.sub(r"[^a-z]+", "", _nn.lower()).replace("sh","s")
                                    _ds3 = _ds2.replace("sh","s")
                                    if _nn_clean == _ds3 or _nn_clean.startswith(_ds3) or _ds3.startswith(_nn_clean):
                                        result["devi_sheet"]["color"] = _nr.get("color_hex", "")
                                        result["devi_sheet"]["color_meaning"] = _nr.get("color_meaning", "")
                                        break
                        # Add graph relations to devi_sheet
                        if not hasattr(_g, '_metadata'):
                            from npu_engine.graph_engine import GraphEngine as _GE
                            _g = _GE()
                        _devi_neighbors = _g.get_neighbors(entity_id)
                        if _devi_neighbors:
                            result["devi_sheet"]["relations"] = [
                                {"type": e.get("relation",""), "target": e.get("to_id","")}
                                for e in _devi_neighbors
                            ]
                        break
            except Exception:
                pass

        # Enrich with plant data from Supabase plant_identity
        try:
            import urllib.request as _ur
            _plant_url = (
                f"{_SUPA_URL}/rest/v1/plant_identity"
                f"?select=entity_id,name_common,name_sanskrit,latin_name,family,"
                f"rasa,dosha_effect,key_constituents,element,"
                f"ayurveda_thermal,ayurveda_category,ayurveda_uses,ayurveda_affinity,"
                f"tcm_name,tcm_thermal,tcm_uses,tcm_meridians,"
                f"western_category,western_thermal,western_uses,western_body_systems,"
                f"thermal_agreement,use_agreement"
                f"&nakshatra_id=eq.{entity_id}"
            )
            _preq = _ur.Request(_plant_url, headers={
                "apikey": _SUPA_KEY,
                "Authorization": f"Bearer {_SUPA_KEY}",
            })
            with _ur.urlopen(_preq, timeout=3) as _presp:
                _plants = json.loads(_presp.read())
                if _plants:
                    _pl = _plants[0]
                    # Look up yantra_triangle from graph for this nakshatra
                    _tri = ""
                    if hasattr(_g, '_metadata'):
                        from npu_engine.torus_queries import find_pada_for_nakshatra
                        _pada = find_pada_for_nakshatra(_nak_name, _g._metadata)
                        if _pada:
                            _tri = (_g._metadata.get(_pada, {})
                                    .get("attributes", {})
                                    .get("yantra_triangle_id", [""]))[0]
                    result["plant"] = {
                        "name_sanskrit": _pl.get("name_sanskrit", ""),
                        "name_common": _pl.get("name_common", ""),
                        "latin_name": _pl.get("latin_name", ""),
                        "family": _pl.get("family", ""),
                        "ayurvedic_taste": _pl.get("rasa", ""),
                        "dosha_effect": _pl.get("dosha_effect", ""),
                        "key_constituents": _pl.get("key_constituents", []),
                        "element": _pl.get("element", ""),
                        "ayurveda": {
                            "thermal": _pl.get("ayurveda_thermal", ""),
                            "category": _pl.get("ayurveda_category", ""),
                            "uses": _pl.get("ayurveda_uses") or [],
                            "affinity": _pl.get("ayurveda_affinity") or [],
                        },
                        "tcm": {
                            "name": _pl.get("tcm_name", ""),
                            "thermal": _pl.get("tcm_thermal", ""),
                            "uses": _pl.get("tcm_uses") or [],
                            "meridians": _pl.get("tcm_meridians") or [],
                        },
                        "western": {
                            "category": _pl.get("western_category", ""),
                            "thermal": _pl.get("western_thermal", ""),
                            "uses": _pl.get("western_uses") or [],
                            "body_systems": _pl.get("western_body_systems") or [],
                        },
                        "thermal_agreement": _pl.get("thermal_agreement"),
                        "use_agreement": _pl.get("use_agreement"),
                        "yantra_triangle": _tri,
                    }
        except Exception:
            pass

        # Surface text passages mentioning this entity
        try:
            _idx_path = Path(_here) / "datasets" / "sources" / "entity_index.json"
            if _idx_path.exists():
                _idx = json.loads(_idx_path.read_text())
                _chunk_ids = _idx.get(entity_id, [])[:5]
                if _chunk_ids:
                    _passages = []
                    for _cid in _chunk_ids:
                        _src, _num = _cid.split(":", 1)
                        # Find the chunk file
                        for _jf in Path(_here, "datasets", "sources").rglob(
                                f"{_src}_chunks.jsonl"):
                            with open(_jf) as _cf:
                                for _line in _cf:
                                    _ch = json.loads(_line)
                                    if str(_ch.get("id")) == _num:
                                        _passages.append({
                                            "text": _ch["text"][:300],
                                            "source": _src,
                                            "domain": _ch.get("domain", _jf.parent.name),
                                            "chunk_id": _cid,
                                        })
                                        break
                            break
                    if _passages:
                        result["passages"] = _passages
        except Exception:
            pass

        # Trigger bija playback for observed entity (async, non-blocking)
        try:
            from npu_engine.datasets import load_entity_metadata
            meta = load_entity_metadata().get(entity_id, {})
            bija_attr = meta.get("attributes", {}).get("bija", [])
            bija = bija_attr[0] if isinstance(bija_attr, list) and bija_attr else None
            if not bija:
                # Check if entity itself is a bija
                if entity_id.startswith("bija_"):
                    bija = entity_id.replace("bija_", "")
            if bija:
                _play_bija_async(bija.lower(), 2.0)
                result["bija_played"] = bija
        except Exception:
            pass

        return app.response_class(
            json.dumps(result, default=_json_serial, ensure_ascii=False),
            mimetype="application/json",
        )

    @app.route("/attend", methods=["POST"])
    def _attend():
        """Attention signal — user is looking at this entity.

        Nudges MixKernel toward the entity's element for ~60 seconds.
        Subtle — 15% nudge, fades back after 32 beats.
        """
        data = request.get_json(silent=True) or {}
        entity_id = data.get("entity_id", "")
        if not entity_id:
            return jsonify({"ok": False, "reason": "no entity_id"})

        element = "ether"
        guna = "sattva"
        try:
            from npu_engine.datasets import load_entity_metadata
            meta = load_entity_metadata()
            ent = meta.get(entity_id, {})
            attrs = ent.get("attributes", {})
            e = attrs.get("element", ["ether"])
            element = (e[0] if isinstance(e, list) and e else str(e)).lower()
            g = attrs.get("guna", ["sattva"])
            guna = (g[0] if isinstance(g, list) and g else str(g)).lower()
        except Exception:
            pass

        _ELEM_NUDGE = {
            "fire":  {"tabla": 0.05, "electronic": 0.04, "melody": 0.03},
            "water": {"pad": 0.05, "mantra_drone": 0.04, "vocal_pad": 0.03},
            "earth": {"tanpura": 0.04, "tabla": 0.03},
            "air":   {"melody": 0.05, "konnakol": 0.03},
            "ether": {"mantra_drone": 0.05, "bija": 0.04},
        }
        nudges = _ELEM_NUDGE.get(element, {})

        # Write attention signal to /tmp/om_attend.json
        import time as _t
        attend_data = {
            "entity_id": entity_id,
            "element": element,
            "guna": guna,
            "nudges": nudges,
            "timestamp": _t.time(),
            "expires": _t.time() + 60,
        }
        try:
            Path(_here, "..", "tmp").mkdir(exist_ok=True)
            Path("/tmp/om_attend.json").write_text(
                json.dumps(attend_data, ensure_ascii=False))
        except Exception:
            pass

        return jsonify({
            "ok": True,
            "entity": entity_id,
            "element": element,
            "guna": guna,
            "nudges": list(nudges.keys()),
        })

    @app.route("/natal")
    def _natal():
        payload = dict(NATAL)
        # Add orientation from natal chart
        try:
            from npu_engine.orientation import compute_orientation
            payload["orientation"] = compute_orientation(NATAL)
        except Exception as e:
            payload["orientation"] = {"error": str(e)}
        return app.response_class(
            json.dumps(payload, default=_json_serial, ensure_ascii=False),
            mimetype="application/json",
        )

    @app.route("/orientation")
    def _orientation():
        """Philosophical orientation for a user."""
        try:
            from npu_engine.orientation import compute_orientation
            orient = compute_orientation(NATAL)
            orient["chart_basis"] = {
                "lagna": NATAL.get("lagna", ""),
                "lagna_nak": NATAL.get("lagna_nak", ""),
                "moon_nak": NATAL.get("moon", {}).get("nak", ""),
                "dasha_lord": NATAL.get("dasha", {}).get("lord", ""),
            }
            return app.response_class(
                json.dumps(orient, default=_json_serial, ensure_ascii=False),
                mimetype="application/json",
            )
        except Exception as e:
            return app.response_class(
                json.dumps({"error": str(e)}), mimetype="application/json",
            )

    @app.route("/interact", methods=["POST"])
    def _interact():
        """Log a user interaction for orientation tracking."""
        try:
            from npu_engine.orientation import compute_entity_signal
            data = request.get_json(force=True)
            eid = data.get("entity_id", "")
            # Look up entity metadata for element/guna/category
            meta = {}
            try:
                from npu_engine.datasets import load_entity_metadata
                m = load_entity_metadata().get(eid, {})
                attrs = m.get("attributes", {})
                meta["element"] = (attrs.get("element", [""])[0] if isinstance(attrs.get("element"), list) else attrs.get("element", ""))
                meta["guna"] = (attrs.get("guna", [""])[0] if isinstance(attrs.get("guna"), list) else attrs.get("guna", ""))
                meta["category"] = m.get("category", eid.split("_")[0] if "_" in eid else "")
            except Exception:
                pass
            signal = compute_entity_signal(eid, meta.get("element", ""),
                                            meta.get("guna", ""), meta.get("category", ""))
            signal["entity_id"] = eid
            signal["layer_n"] = data.get("layer_n", 0)
            signal["layer_position"] = data.get("layer_position", 0)
            return app.response_class(
                json.dumps({"logged": True, "signal": signal}, ensure_ascii=False),
                mimetype="application/json",
            )
        except Exception as e:
            return app.response_class(
                json.dumps({"error": str(e)}), mimetype="application/json",
            )

    @app.route("/claims")
    def _claims():
        """Claims about an entity grouped by convergence."""
        entity = request.args.get("entity", "")
        if not entity:
            return app.response_class(json.dumps({"error": "entity param required"}),
                                       mimetype="application/json")
        # For now return from entity metadata + graph
        try:
            from npu_engine.datasets import load_entity_metadata
            from npu_engine.graph_engine import GraphEngine
            meta = load_entity_metadata().get(entity, {})
            g = GraphEngine()
            neighbors = g.get_neighbors(entity, exclude_inverse=False)
            # Group claims by relation type
            universal = []
            tradition_specific = {}
            for n in neighbors:
                rel = n.get("relation", "")
                auth = n.get("authority", "")
                claim = {"predicate": rel, "object": n["to_id"], "source": auth}
                # Simple heuristic: if multiple sources agree → universal
                universal.append(claim)
            return app.response_class(
                json.dumps({"entity": entity, "universal": universal[:10],
                            "majority": [], "tradition_specific": tradition_specific,
                            "note": f"{len(neighbors)} relations from graph"},
                           default=_json_serial, ensure_ascii=False),
                mimetype="application/json",
            )
        except Exception as e:
            return app.response_class(json.dumps({"error": str(e)}), mimetype="application/json")

    # ── Arts recommendation engine ──────────────────────
    _arts_data = None
    _arts_s0_map = None  # {art_id: [s0_root_id, ...]}

    def _load_arts():
        nonlocal _arts_data, _arts_s0_map
        if _arts_data is not None:
            return
        _arts_data = []
        _arts_s0_map = {}
        # Load arts CSV
        arts_path = os.path.join(_here, "datasets", "cosmology", "vedic_arts_64.csv")
        try:
            import csv
            with open(arts_path, newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    art_id = "art_" + row.get("art", "").strip().lower()
                    gp = row.get("gaudiya_priority", "").strip()
                    _arts_data.append({
                        "art": row.get("art", ""),
                        "art_id": art_id,
                        "category": row.get("category", ""),
                        "from_layer": row.get("from_layer", ""),
                        "to_layer": row.get("to_layer", ""),
                        "gaudiya_priority": int(gp) if gp else 0,
                    })
        except Exception:
            pass
        # Load s0_roots for arts
        _load_s0_roots()
        if _s0_roots_up:
            for art in _arts_data:
                roots = _s0_roots_up.get(art["art_id"], [])
                _arts_s0_map[art["art_id"]] = [r["to_id"] for r in roots]

    def _recommend_arts(observances):
        """Recommend arts for current observance, sorted by Gauḍīya priority.

        Priority: 1=Nāma (mantra/chanting), 2=Nṛtya (dance),
                  3=Gīta (singing), 4=Vādya (instruments).
        Then: arts sharing S0 root with the observance deity/parampara.
        Then: S0-rooted arts generally.
        """
        _load_arts()
        if not _arts_data:
            return []

        # Collect S0 roots relevant to current observances
        obs_s0_roots = set()
        for obs in observances:
            pref = obs.get("parampara_ref", "")
            if pref:
                obs_s0_roots.add(pref)
            # Also check the observance deity's S0 root
            deity = obs.get("deity", "")
            if deity:
                deity_id = "deity_" + deity.lower().replace(" ", "_").replace("ā", "a").replace("ī", "i").replace("ṇ", "n").replace("ṣ", "s")
                for root in (_s0_roots_up or {}).get(deity_id, []):
                    obs_s0_roots.add(root["to_id"])

        recommended = []
        for art in _arts_data:
            art_roots = set(_arts_s0_map.get(art["art_id"], []))
            shared = art_roots & obs_s0_roots
            has_gp = art["gaudiya_priority"] > 0
            has_s0 = art["from_layer"] == "S0"

            # Include: has gaudiya priority, or shares S0 root, or is S0-rooted
            if has_gp or shared or has_s0:
                recommended.append({
                    "art": art["art"],
                    "category": art["category"],
                    "gaudiya_priority": art["gaudiya_priority"],
                    "s0_rooted": has_s0,
                    "shared_roots": list(shared),
                    "from_layer": art["from_layer"],
                })

        # Sort: gaudiya_priority first (1-4), then shared roots, then S0, then alpha
        def sort_key(a):
            gp = a["gaudiya_priority"] if a["gaudiya_priority"] > 0 else 99
            shared = -len(a["shared_roots"])
            s0 = 0 if a["s0_rooted"] else 1
            return (gp, shared, s0, a["art"])

        recommended.sort(key=sort_key)
        return recommended

    @app.route("/playlist")
    def _playlist():
        """Field-state driven composition playlist + mantra of the moment."""
        try:
            fs = json.loads(_spine().get_data(as_text=True))
            from npu_engine.composition_db import get_playlist, get_mantra_for_now
            playlist = get_playlist(fs, limit=5)
            mantra = get_mantra_for_now(fs)
            return app.response_class(
                json.dumps({"playlist": playlist, "mantra": mantra},
                           default=_json_serial, ensure_ascii=False),
                mimetype="application/json",
            )
        except Exception as exc:
            return app.response_class(
                json.dumps({"error": str(exc)}, ensure_ascii=False),
                mimetype="application/json",
            )

    @app.route("/observance")
    def _observance():
        """Current Vaiṣṇava observance(s) with S0 entity connections
        and recommended arts in Gauḍīya priority order.

        The astronomical moment is the window.
        The S0 entity is what's seen through it.
        The arts are how the jīva responds.
        """
        p5 = calc_panchanga()
        observances = p5.get("observances", [])
        arts = _recommend_arts(observances)
        payload = {
            "masa_num":     p5.get("masa"),
            "masa":         p5.get("masa_name"),
            "paksha":       p5.get("paksha"),
            "tithi":        p5.get("tithi"),
            "tidx":         p5.get("tidx"),
            "nakshatra":    p5.get("nakshatra"),
            "vara":         p5.get("vara"),
            "observances":  observances,
            "count":        len(observances),
            "recommended_arts": arts,
        }
        return app.response_class(
            json.dumps(payload, default=_json_serial, ensure_ascii=False),
            mimetype="application/json",
        )

    # ── S0 root traversal ────────────────────────────────
    _s0_roots_up = None    # {entity_id: [{to_id, attestation, notes}]}
    _s0_roots_down = None  # {s0_id: [{from_id, attestation, notes}]}

    def _load_s0_roots():
        nonlocal _s0_roots_up, _s0_roots_down
        if _s0_roots_up is not None:
            return
        _s0_roots_up = {}
        _s0_roots_down = {}
        path = os.path.join(_here, "datasets", "relations", "s0_roots.csv")
        try:
            import csv
            with open(path, newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    from_id = row.get("from_id", "").strip()
                    to_id = row.get("to_id", "").strip()
                    att = row.get("attestation", "")
                    notes = row.get("notes", "")
                    if from_id and to_id:
                        _s0_roots_up.setdefault(from_id, []).append({
                            "to_id": to_id, "attestation": att, "notes": notes,
                        })
                        _s0_roots_down.setdefault(to_id, []).append({
                            "from_id": from_id, "attestation": att, "notes": notes,
                        })
        except Exception as e:
            print(f"  ⚠ s0_roots.csv: {e}")

    @app.route("/navigate", methods=["POST"])
    def _navigate():
        """Traverse the S0 root system.

        POST {"entity_id": "nakshatra_rohini", "direction": "up"}
          → returns the S0 root(s) of that entity

        POST {"entity_id": "tattva_lila", "direction": "down"}
          → returns all S1-S6 entities rooted in that S0 entity

        The S0 layer doesn't sit above or below.
        It spreads through all layers as a root system.
        """
        _load_s0_roots()
        data = request.get_json(force=True) or {}
        entity_id = data.get("entity_id", "")
        direction = data.get("direction", "up")

        if direction == "up":
            # Find S0 roots of this entity
            roots = _s0_roots_up.get(entity_id, [])
            # Resolve S0 entity metadata
            para_meta = _load_parampara_meta()
            resolved = []
            for r in roots:
                entry = dict(r)
                tid = r["to_id"]
                # Check parampara
                if tid in para_meta:
                    entry["entity"] = para_meta[tid]
                # Check tattva
                elif tid.startswith("tattva_"):
                    for trow in (_load_vaishnava_calendar() or []):
                        pass  # tattva metadata is in a different CSV
                    # Load tattva inline
                    entry["entity"] = _resolve_s0_entity(tid)
                else:
                    entry["entity"] = _resolve_s0_entity(tid)
                resolved.append(entry)
            return app.response_class(
                json.dumps({"entity_id": entity_id, "direction": "up",
                            "roots": resolved, "count": len(resolved)},
                           default=_json_serial, ensure_ascii=False),
                mimetype="application/json",
            )

        elif direction == "down":
            # Find all entities rooted in this S0 entity
            branches = _s0_roots_down.get(entity_id, [])
            return app.response_class(
                json.dumps({"entity_id": entity_id, "direction": "down",
                            "branches": branches, "count": len(branches)},
                           default=_json_serial, ensure_ascii=False),
                mimetype="application/json",
            )

        return app.response_class(
            json.dumps({"error": "direction must be 'up' or 'down'"},
                       ensure_ascii=False),
            mimetype="application/json", status=400,
        )

    def _resolve_s0_entity(entity_id):
        """Resolve an S0 entity (tattva_, rasa_, parampara_) to its metadata."""
        # Parampara
        para = _load_parampara_meta()
        if entity_id in para:
            return para[entity_id]
        # Tattva — load from CSV
        tattva_path = os.path.join(_here, "datasets", "ontology", "vaishnava_tattva.csv")
        try:
            import csv
            with open(tattva_path, newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    if row.get("id", "").strip() == entity_id:
                        return {"id": entity_id, "name_iast": row.get("name_iast", ""),
                                "category": row.get("category", ""),
                                "description": row.get("description", ""),
                                "source": row.get("source", ""), "layer": "S0"}
        except Exception:
            pass
        # Rasa
        rasa_path = os.path.join(_here, "datasets", "ontology", "rasa_siddhanta.csv")
        try:
            import csv
            with open(rasa_path, newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    if row.get("id", "").strip() == entity_id:
                        return {"id": entity_id, "name_iast": row.get("name_iast", ""),
                                "type": row.get("type", ""),
                                "sthayi_bhava": row.get("sthayi_bhava", ""),
                                "source": row.get("source", ""), "layer": "S0"}
        except Exception:
            pass
        return {"id": entity_id, "layer": "S0"}

    @app.route("/transits")
    def _transits():
        payload = get_transit_data()
        return app.response_class(
            json.dumps(payload, default=_json_serial, ensure_ascii=False),
            mimetype="application/json",
        )

    @app.route("/dasha")
    def _dasha():
        payload = get_current_dasha()
        return app.response_class(
            json.dumps(payload, default=_json_serial, ensure_ascii=False),
            mimetype="application/json",
        )

    # ── MODE CONTRACT ─────────────────────────────────────────
    _MODE_CONTRACT = {
        "OBSERVE":    {"surfaces": ["brahmanda","vastu_heatmap","cosmos_idle"], "allows": ["read_field","read_coherence","read_sound"], "denies": ["write_entity","mutate_field","generate"]},
        "UNDERSTAND": {"surfaces": ["wiki","vyasasana","codex_read"], "allows": ["read_field","read_coherence","search","entity_detail"], "denies": ["mutate_field","generate"], "attestation_visible": True},
        "PRACTICE":   {"surfaces": ["agriculture","body_map","marma","ecology"], "allows": ["read_field","read_coherence","log_practice"], "denies": ["generate","mutate_field"]},
        "CREATE":     {"surfaces": ["cosmos_perform","codex_write","yantra_draw"], "allows": ["read_field","generate","mutate_field"], "denies": []},
    }

    @app.route("/mode/contract")
    def _mode_contract():
        return app.response_class(json.dumps({"modes": _MODE_CONTRACT, "rule": "one dominant mode per surface, no silent mixing", "axes": {"mode": "OBSERVE|UNDERSTAND|PRACTICE|CREATE", "layer": "S0-S6", "yuga": "Kali|Satya", "dynamics": "winding,twist,spiral"}}, ensure_ascii=False), mimetype="application/json")

    @app.route("/mode/surface/<surface>")
    def _mode_for_surface(surface):
        smap = {}
        for mn, md in _MODE_CONTRACT.items():
            for s in md["surfaces"]:
                smap[s] = mn
        mode = smap.get(surface)
        if not mode:
            return app.response_class(json.dumps({"error": f"unknown surface: {surface}"}, ensure_ascii=False), mimetype="application/json", status=404)
        return app.response_class(json.dumps({"surface": surface, "mode": mode, "contract": _MODE_CONTRACT[mode]}, ensure_ascii=False), mimetype="application/json")

    # ── SPINE ROUTE — single FieldState for all downstream ────
    @app.route("/spine")
    def _spine():
        """Unified FieldState from the NPU spine.

        This is the ONE endpoint that atlas.html (and any surface)
        should use when it wants the complete field picture:
          panchanga + toroidal coords + ranked entities + geometry + modulation

        Replaces the need to call /field + /coherence + /sound/state separately.
        """
        fs = field_state()
        try:
            from npu_engine.build_field_state import build_field_state as _bfs
            from npu_engine.graph_engine import GraphEngine
            toroid = get_toroid()
            _graph = GraphEngine()
            _vs = None
            try:
                from npu_engine.vector_store import get_vector_store
                _vs = get_vector_store()
            except Exception:
                pass
            spine = _bfs(_toroid_panchanga(fs), toroid,
                         _temple or __import__('npu_engine.temple_geometry', fromlist=['TempleGeometry']).TempleGeometry(),
                         graph=_graph, vector_store=_vs)

            # Enrich entities with element rgb for rendering
            for ent in spine.entities:
                elem = ent.get("element", "ether")
                ent["rgb"] = _ELEMENT_RGB.get(elem, _ELEMENT_RGB.get("ether", [200,169,110]))

            # Nitya Devi from tithi + Vastu from field
            from npu_engine.field_to_sound import get_devi_from_tithi, get_vastu_from_field
            _p = fs.get("panchanga", {})
            _tithi_n = (_p.get("didx", 0) + 1)  # didx is 0-based within paksha
            _devi = get_devi_from_tithi(_tithi_n)
            _vastu = get_vastu_from_field(fs)

            payload = {
                "panchanga": _p,
                "theta": round(spine.theta, 4),
                "phi": round(spine.phi, 4),
                "entities": spine.entities[:64],
                "active_relations": spine.active_relations[:80],
                "formations": spine.formations,
                "lifecycle": spine.lifecycle,
                "vastu_grid_count": len(spine.vastu_grid),
                "arc_phase": spine.arc_phase,
                "modulation": spine.modulation,
                "psi": spine.psi,
                "devi": _devi,
                "vastu": _vastu,
                "sound_state": fs.get("sound_state", _derive_sound_state(fs)),
                "summary": spine.summary(),
                "mode_contract": _MODE_CONTRACT,
            }

            # S-layer mapping from field state
            from npu_engine.field_layers import generate_layer_mapping
            payload["layers"] = generate_layer_mapping(payload)

            # Sound spec — derive from spine field state
            try:
                from npu_engine.sound.sound_engine import derive_sound_spec
                _sound_fs = {
                    "panchanga": _p,
                    "sound_state": payload.get("sound_state", {}),
                    "entities": spine.entities[:32],
                    "observances": [],
                    "psi": spine.psi,
                }
                payload["sound_spec"] = derive_sound_spec(_sound_fs, mode=_ss.sound_mode)
            except Exception:
                payload["sound_spec"] = {}

            # System state — lightweight, no subprocess calls in hot path
            try:
                from npu_engine.field.system_engine import derive_audio_route
                payload["system_audio"] = derive_audio_route()
            except Exception:
                payload["system_audio"] = {}

            # Temporal trajectory
            try:
                from npu_engine.field.trajectory_engine import derive_trajectory
                payload["trajectory"] = derive_trajectory(fs)
            except Exception:
                payload["trajectory"] = {}
        except Exception as exc:
            # Fallback: serve the legacy field_state if spine fails
            payload = {
                "error": f"spine unavailable: {exc}",
                "panchanga": fs.get("panchanga", {}),
                "sound_state": fs.get("sound_state", _derive_sound_state(fs)),
                "sound_spec": {},
                "fallback": True,
            }
        return app.response_class(
            json.dumps(payload, default=_json_serial, ensure_ascii=False),
            mimetype="application/json",
        )

    # ── Render/yantra routes → render_bp ─────────────────────────────
    from npu_engine.routes.render_bp import render_bp
    app.register_blueprint(render_bp)

    @app.route("/render")
    def _render():
        """iGPU render state — spatial layout for any canvas/UI."""
        proj = request.args.get("projection", "plane")
        try:
            spine_data = json.loads(_spine().get_data())
            if spine_data.get("error"):
                raise Exception(spine_data["error"])
            from npu_engine.igpu import render_field_state, render_state_to_dict
            rs = render_field_state(spine_data, projection=proj)
            payload = render_state_to_dict(rs)
        except Exception as exc:
            payload = {"error": str(exc)}
        return app.response_class(
            json.dumps(payload, default=_json_serial, ensure_ascii=False),
            mimetype="application/json",
        )

    # ── render/eternal → render_bp (registered above) ────────

    @app.route("/render/4d")
    def _render_4d():
        """4D torus projection — theta rotates with time parameter t."""
        t_param = float(request.args.get("t", 0.0))
        try:
            spine_data = json.loads(_spine().get_data())
            if spine_data.get("error"):
                raise Exception(spine_data["error"])
            from npu_engine.igpu import render_field_state, render_state_to_dict
            rs = render_field_state(spine_data, projection="4d", t=t_param)
            payload = render_state_to_dict(rs)
        except Exception as exc:
            payload = {"error": str(exc)}
        return app.response_class(
            json.dumps(payload, default=_json_serial, ensure_ascii=False),
            mimetype="application/json",
        )

    @app.route("/visual/state")
    def _visual_state():
        """Return canonical cosmological colors for the current field moment."""
        import csv as _csv
        try:
            spine_data = json.loads(_spine().get_data())
            p = spine_data.get("panchanga", {})

            # Load graha colors
            graha_colors = {}
            graha_csv = ROOT / "datasets" / "cosmology" / "graha_master.csv"
            if graha_csv.exists():
                with open(graha_csv) as f:
                    for row in _csv.DictReader(f):
                        graha_colors[row["graha"]] = {
                            "color": row.get("color_primary", ""),
                            "luminosity": row.get("color_luminosity", ""),
                            "meaning": row.get("color_meaning", ""),
                        }

            # Load nakshatra colors
            nak_colors = {}
            nak_csv = ROOT / "datasets" / "cosmology" / "nakshatra_master.csv"
            if nak_csv.exists():
                with open(nak_csv) as f:
                    for row in _csv.DictReader(f):
                        nak_colors[row["nakshatra"]] = row.get("color_hex", "")

            # Load devi colors
            devi_colors = {}
            devi_csv = ROOT / "datasets" / "cosmology" / "nitya_devi_master.csv"
            if devi_csv.exists():
                with open(devi_csv) as f:
                    for row in _csv.DictReader(f):
                        devi_colors[row.get("name_iast", "")] = row.get("color_hex", "")

            # Current field colors
            cur_nak = p.get("nakshatra", "")
            cur_nak_lord = p.get("nak_lord", "")
            cur_devi = p.get("devi", "")
            if isinstance(cur_devi, (list, tuple)):
                cur_devi = cur_devi[0] if cur_devi else ""
            elif isinstance(cur_devi, dict):
                cur_devi = cur_devi.get("name", "")

            payload = {
                "field": {
                    "nakshatra": cur_nak,
                    "nakshatra_color": nak_colors.get(cur_nak, ""),
                    "graha": cur_nak_lord,
                    "graha_color": graha_colors.get(cur_nak_lord, {}).get("color", ""),
                    "devi": cur_devi,
                    "devi_color": devi_colors.get(cur_devi, ""),
                },
                "grahas": graha_colors,
                "nakshatras": nak_colors,
                "devis": devi_colors,
                "ground": "#0a0d1a",
                "surface": "#0d1020",
            }
        except Exception as exc:
            payload = {"error": str(exc)}
        return app.response_class(
            json.dumps(payload, default=_json_serial, ensure_ascii=False),
            mimetype="application/json",
        )

    @app.route("/render/stream")
    def _render_stream():
        """SSE stream of render state — pushes when field changes."""
        import time as _time
        import hashlib

        # Capture request args before entering generator (request context
        # is gone once the generator yields its first value)
        proj = request.args.get("projection", "plane")

        def _sse_gen():
            last_hash = ""
            while True:
                try:
                    with app.app_context():
                        spine_data = json.loads(_spine().get_data(as_text=True))
                    from npu_engine.igpu import render_field_state, render_state_to_dict
                    rs = render_field_state(spine_data, projection=proj)
                    payload = render_state_to_dict(rs)
                except Exception as exc:
                    payload = {"error": str(exc)}

                raw = json.dumps(payload, default=_json_serial,
                                 ensure_ascii=False, sort_keys=True)
                cur_hash = hashlib.md5(raw.encode()).hexdigest()

                if cur_hash != last_hash:
                    last_hash = cur_hash
                    yield f"data: {raw}\n\n"

                _time.sleep(10)

        return Response(
            _sse_gen(),
            mimetype="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    # ── Sound/bija routes → sound_bp ─────────────────────────────
    from npu_engine.routes.sound_bp import sound_bp
    app.register_blueprint(sound_bp)

    @app.route("/musician")
    def _musician():
        """Natal-aware musician reading — raga coloring, gamak, rest, phrasing."""
        try:
            from npu_engine.natal_musician import derive_musician_reading
            spine_data = json.loads(_spine().get_data(as_text=True))
            reading = derive_musician_reading(NATAL, spine_data)
        except Exception as exc:
            reading = {"error": str(exc)}
        return app.response_class(
            json.dumps(reading, default=_json_serial, ensure_ascii=False),
            mimetype="application/json",
        )

    @app.route("/yantra")
    def _yantra():
        """Yantra geometry from current field state."""
        try:
            from npu_engine.yantra_engine import generate_yantra
            spine_data = json.loads(_spine().get_data(as_text=True))
            payload = generate_yantra(spine_data)
        except Exception as exc:
            payload = {"error": str(exc)}
        return app.response_class(
            json.dumps(payload, default=_json_serial, ensure_ascii=False),
            mimetype="application/json",
        )

    @app.route("/compose", methods=["GET", "POST"])
    def _compose():
        """Generate a musical phrase from current field + natal.

        Returns melody notes, bol sequence, mantra, and trigger reason.
        POST body can include: {"reason": "nakshatra_resonance", "intensity": 0.8}
        """
        import random

        try:
            spine_data = json.loads(_spine().get_data(as_text=True))
        except Exception:
            spine_data = field_state()

        ss = spine_data.get("sound_state", {})
        p5 = spine_data.get("panchanga", {})
        nd = p5.get("nak_data") or {}

        # Read request body if POST
        req_data = {}
        if request.method == "POST":
            try:
                req_data = request.get_json(force=True) or {}
            except Exception:
                pass

        reason = req_data.get("reason", "field_pulse")
        intensity = float(req_data.get("intensity", 0.7))

        # ── Current raga scale ──
        raga_name = ss.get("raga", "Yaman")
        raga_def = RAGAS.get(raga_name, RAGAS.get("Yaman"))
        aroha = raga_def.get("aroha", [0, 2, 4, 5, 7, 9, 11])
        avaroha = raga_def.get("avaroha", [11, 9, 7, 5, 4, 2, 0])
        vadi = raga_def.get("vadi", 4)
        samvadi = raga_def.get("samvadi", 11)
        sa = ss.get("sa", 261.63) if "sa" in ss else 261.63

        # ── Melody: 6-10 note phrase in current raga ──
        phrase_len = random.randint(6, 10)
        beat_dur = 60.0 / max(ss.get("bpm", 72), 30)
        melody = []
        ascending = random.choice([True, False])
        path = aroha if ascending else avaroha

        for i in range(phrase_len):
            # Weighted note selection: vadi 35%, samvadi 20%, other 45%
            r = random.random()
            if r < 0.35:
                semi = vadi
            elif r < 0.55:
                semi = samvadi
            else:
                semi = random.choice(path)

            # Last note: resolve to Sa
            if i == phrase_len - 1:
                semi = 0

            swara = _SEMI_TO_SWARA.get(semi % 12, "Sa")
            # Duration: vadi/samvadi held longer
            if semi == vadi:
                dur = beat_dur * random.choice([0.9, 1.2, 1.5])
            elif semi == samvadi:
                dur = beat_dur * random.choice([0.7, 0.9, 1.0])
            else:
                dur = beat_dur * random.choice([0.4, 0.5, 0.6])

            vel = min(1.0, intensity * (0.7 + random.random() * 0.3))
            if i == 0:
                vel = min(1.0, vel * 1.1)  # first note slightly louder

            melody.append({
                "swara": swara,
                "semi": semi,
                "freq": round(sa * (2 ** (semi / 12)), 2),
                "duration": round(dur, 3),
                "velocity": round(vel, 2),
                "time_offset": round(sum(n["duration"] for n in melody), 3),
            })

        # ── Bols: one tala cycle ──
        tala_beats = ss.get("tala_beats", 8)
        nak_itrans = nak_to_itrans(p5.get("nakshatra", ""))
        tala_info = _NAKSHATRA_TALA.get(nak_itrans, {"tala": "Ādi", "beats": 8})
        tala_sym = tala_info["tala"]
        # Get bol pattern
        theka = _TALA_BOLS.get(tala_sym, _TALA_BOLS.get("Adi", []))
        bols = []
        for bi, bol in enumerate(theka[:tala_beats]):
            bols.append({
                "bol": bol,
                "beat": bi,
                "time_offset": round(bi * beat_dur, 3),
                "velocity": round(0.8 * intensity if bi == 0 else 0.6 * intensity, 2),
            })

        # ── Nakshatra mantra ──
        _NAK_MANTRA = {
            "Ashwini":    "Om Aśvinau namaḥ",
            "Bharani":    "Om Yamāya namaḥ",
            "Krittika":   "Om Agnaye namaḥ",
            "Rohini":     "Om Brahmāya namaḥ",
            "Mrigashira": "Om Somāya namaḥ",
            "Ardra":      "Om Rudrāya namaḥ",
            "Punarvasu":  "Om Bṛhaspataye namaḥ",
            "Pushya":     "Om Bṛhaspataye namaḥ",
            "Ashlesha":   "Om Sarpebhyo namaḥ",
            "Magha":      "Om Pitṛbhyo namaḥ",
            "Purva Phalguni":  "Om Bhagāya namaḥ",
            "Uttara Phalguni": "Om Aryamṇe namaḥ",
            "Hasta":      "Om Savitre namaḥ",
            "Chitra":     "Om Tvaṣṭre namaḥ",
            "Swati":      "Om Vāyave namaḥ",
            "Vishakha":   "Om Indrāgnibhyāṃ namaḥ",
            "Anuradha":   "Om Mitrāya namaḥ",
            "Jyeshtha":   "Om Indrāya namaḥ",
            "Mula":       "Om Nirṛtaye namaḥ",
            "Purva Ashadha":   "Om Apāṃ namaḥ",
            "Uttara Ashadha":  "Om Viśvedevebhyo namaḥ",
            "Shravana":   "Om Viṣṇave namaḥ",
            "Dhanishta":  "Om Vasubhyo namaḥ",
            "Shatabhisha": "Om Varuṇāya namaḥ",
            "Purva Bhadrapada":  "Om Ajaikapāde namaḥ",
            "Uttara Bhadrapada": "Om Ahirbudhnyāya namaḥ",
            "Revati":     "Om Pūṣṇe namaḥ",
        }
        mantra_full = _NAK_MANTRA.get(nak_itrans, "Om namaḥ")
        # Split into syllables for bija synthesis
        mantra_syls = [s.lower().strip(".,") for s in mantra_full.split() if s]

        # ── Coherence score ──
        coherence = intensity
        # Natal alignment boosts coherence
        natal_moon_nak = NATAL.get("moon", {}).get("nak", "Punarvasu").split(" pada")[0].strip()
        cur_nak = p5.get("nakshatra", "")
        if natal_moon_nak.lower() in cur_nak.lower():
            coherence = min(1.0, coherence + 0.25)
            if reason == "field_pulse":
                reason = "natal_alignment"

        # ── Bhajan form selection ──
        try:
            from npu_engine.natal_musician import select_bhajan_form
            bhajan = select_bhajan_form(p5, NATAL)
        except Exception:
            bhajan = {"form": "khayal", "tala": tala_sym, "meter": "chaupai",
                      "language": "hindi", "deity_invocation": mantra_full,
                      "antara_length": 3, "sthayi_refrain": mantra_full}

        payload = {
            "melody": melody,
            "bols": bols,
            "mantra": mantra_full,
            "mantra_syllables": mantra_syls,
            "raga": raga_name,
            "tala": tala_sym,
            "nakshatra": cur_nak,
            "trigger_reason": reason,
            "coherence_score": round(coherence, 3),
            "intensity": round(intensity, 2),
            "bhajan_form": bhajan,
        }
        return app.response_class(
            json.dumps(payload, default=_json_serial, ensure_ascii=False),
            mimetype="application/json",
        )

    @app.route("/compose/variation", methods=["POST"])
    def _compose_variation():
        """Generate a composition variation using SwaraEngine's three axes.

        POST body: {
            "classical_experimental": 0.0-1.0,
            "acoustic_electronic": 0.0-1.0,
            "composed_improvised": 0.0-1.0
        }
        """
        data = request.get_json(force=True) if request.data else {}
        classical_exp = float(data.get("classical_experimental", 0.2))
        acoustic_elec = float(data.get("acoustic_electronic", 0.3))
        composed_imp = float(data.get("composed_improvised", 0.5))

        try:
            from npu_engine.swara_engine import SwaraEngine
            from npu_engine.graph_engine import GraphEngine

            fs = field_state()
            g = GraphEngine()
            se = SwaraEngine(g, fs)

            variation = se.get_compose_variation(
                classical_exp, acoustic_elec, composed_imp)
            gazes = se.get_active_gazes()
            vakra = list(se.get_vakra_notes())

            # Summarize gazes for response
            gaze_summary = {}
            for swara_id, gaze_list in gazes.items():
                primary = max(gaze_list, key=lambda g: g["force"])
                gaze_summary[swara_id] = {
                    "planet": primary["planet"],
                    "force": round(primary["force"], 3),
                    "quality": primary["quality"],
                    "gamaka": se._gamaka_for_planet(primary["planet"]),
                }

            p5 = fs.get("panchanga", {})
            return app.response_class(
                json.dumps({
                    "variation": variation,
                    "gazes": gaze_summary,
                    "vakra_notes": vakra,
                    "raga": se.current_raga.get("name", ""),
                    "nakshatra": p5.get("nakshatra", ""),
                    "nak_lord": p5.get("nak_lord", ""),
                }, default=_json_serial, ensure_ascii=False),
                mimetype="application/json",
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # ── sound/relational through sound/freesound-key → sound_bp (registered above) ────────

    @app.route("/mandala/layout")
    def _mandala_layout():
        """Relational mandala — 5 rings of graph-derived data for center canvas."""
        fs = field_state()
        p5 = fs.get("panchanga", {})
        ss = fs.get("sound_state") or _derive_sound_state(fs)
        nd = p5.get("nak_data", {}) or {}

        # Center — nakshatra deity
        center = {
            "nakshatra": p5.get("nakshatra", ""),
            "deity": nd.get("deity", ""),
            "element": p5.get("element", "ether"),
            "devi": p5.get("devi", ["", ""])[0] if isinstance(p5.get("devi"), list) else "",
        }

        # Ring 1 — 12 chromatic positions, active notes from raga
        raga_name = fs.get("devi_raga", "Yaman")
        raga_def = fs.get("devi_raga_def", {}) or {}
        scale_semis = set(raga_def.get("scale", [0, 2, 4, 5, 7, 9, 11]))
        vadi = raga_def.get("vadi")
        samvadi = raga_def.get("samvadi")
        ring1 = []
        for s in range(12):
            ring1.append({
                "id": f"note:{s}",
                "angle": s * 30.0,
                "size": 1.8 if s == vadi else (1.4 if s == samvadi else 1.0),
                "label": _SEMI_TO_SWARA.get(s, ""),
                "active": s in scale_semis,
                "vadi": s == vadi,
                "samvadi": s == samvadi,
            })

        # Ring 2 — tala beats
        tala_name = ss.get("tala", "Ādi")
        tala_bols = ss.get("tala_bols", _TALA_BOLS.get(tala_name, _TALA_BOLS.get("Adi", [])))
        ring2 = [{
            "id": f"beat:{i}",
            "angle": (i / max(len(tala_bols), 1)) * 360.0,
            "size": 1.6 if i == 0 else 1.0,
            "bol": b,
            "sam": i == 0,
        } for i, b in enumerate(tala_bols)]

        # Ring 3 — coherence entities (top 8)
        coh_entities = []
        try:
            toroid = get_toroid()
            results = toroid.field_query(_toroid_panchanga(fs), top_n=8)
            for e in results:
                elem = _phi_to_element(e.get("phi", 0))
                coh_entities.append({
                    "id": e.get("entity_id", ""),
                    "angle": (len(coh_entities) / 8.0) * 360.0,
                    "size": round(e.get("score", 0.5), 2),
                    "label": (e.get("entity_id") or "").split("_")[-1],
                    "element": elem,
                })
        except Exception:
            pass

        # Ring 4 — sympathetic strings (27 just-intonation ratios)
        _JUST = [1, 256/243, 9/8, 32/27, 81/64, 4/3, 729/512,
                 3/2, 128/81, 27/16, 16/9, 243/128,
                 2, 2*256/243, 2*9/8, 2*32/27, 2*81/64, 2*4/3,
                 2*729/512, 3, 2*128/81, 2*27/16, 2*16/9,
                 2*243/128, 4, 4*256/243, 4*9/8]
        sa_freq = _ELEMENT_FREQ.get(p5.get("element", "ether"), 261.63)
        ring4 = [{
            "id": f"string:{i}",
            "angle": (i / 27.0) * 360.0,
            "freq": round(sa_freq * _JUST[i % len(_JUST)], 2),
            "active": False,
        } for i in range(27)]

        # Ring 5 — nakshatra wheel
        nak_iast = p5.get("nakshatra", "")
        ring5 = []
        for i, nd_row in enumerate(NAKSHATRA_DATA):
            ring5.append({
                "id": f"nakshatra:{nd_row.get('name_key', '')}",
                "angle": (i / 27.0) * 360.0,
                "active": nd_row.get("name", "") == nak_iast,
                "element": nd_row.get("element", "ether").lower(),
                "name": nd_row.get("name", ""),
            })

        payload = {
            "center": center,
            "rings": [ring1, ring2, coh_entities, ring4, ring5],
            "field": {
                "nakshatra": nak_iast,
                "raga": raga_name,
                "tala": tala_name,
                "bpm": ss.get("bpm", 72),
                "vadi": _SEMI_TO_SWARA.get(vadi, ""),
                "samvadi": _SEMI_TO_SWARA.get(samvadi, ""),
            },
        }
        return app.response_class(
            json.dumps(payload, default=_json_serial, ensure_ascii=False),
            mimetype="application/json",
        )

    @app.route("/knowledge/relational")
    def _knowledge_relational():
        """Relational knowledge law. Delegated to RelationalEngine."""
        fs = field_state()
        if _relational:
            payload = _relational.knowledge_state(fs)
        else:
            payload = {"error": "RelationalEngine not available"}
        return app.response_class(
            json.dumps(payload, default=_json_serial, ensure_ascii=False),
            mimetype="application/json",
        )

    @app.route("/s5/data")
    def _s5_data():
        """S5 plant wheel — 3 rings from field state."""
        p = Path("/tmp/s5_state.json")
        if p.exists():
            return app.response_class(p.read_text(), mimetype="application/json")
        try:
            from npu_engine.s5_kernel import write_s5_state
            return jsonify(write_s5_state(field_state()))
        except Exception as exc:
            return jsonify({"error": str(exc)})

    # ── Card/reading routes → reading_bp ─────────────────────────────
    from npu_engine.routes.reading_bp import reading_bp
    app.register_blueprint(reading_bp)

    # /codex app route removed — codex functionality handled by
    # reading_engine, composition_engine, and observe panel.
    # Codex API routes (/codex/render, /codex/entity, etc.) kept
    # as they're used by devi_tarot, wiki, and mala apps.

    @app.route("/altar")
    def _altar_get():
        """Read the personal altar."""
        p = Path(_here) / "instance" / "personal" / "altar.json"
        if not p.exists():
            return jsonify({"deities": [], "plants": [], "mantras": [], "texts": []})
        altar = json.loads(p.read_text())
        try:
            fs = field_state()
            altar["field_now"] = {
                "nakshatra": fs.get("panchanga", {}).get("nakshatra"),
                "element": fs.get("panchanga", {}).get("element"),
                "tithi": fs.get("panchanga", {}).get("tithi"),
            }
        except Exception:
            pass
        return jsonify(altar)

    @app.route("/altar", methods=["POST"])
    def _altar_update():
        """Add or remove items from the altar."""
        p = Path(_here) / "instance" / "personal" / "altar.json"
        data = request.get_json(silent=True) or {}
        altar = json.loads(p.read_text()) if p.exists() else {}
        action    = data.get("action", "add")
        item_type = data.get("type")
        item_id   = data.get("id")
        if item_type and item_id:
            if item_type not in altar:
                altar[item_type] = []
            if action == "add" and item_id not in altar[item_type]:
                altar[item_type].append(item_id)
            elif action == "remove":
                altar[item_type] = [x for x in altar[item_type] if x != item_id]
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(altar, indent=2, ensure_ascii=False))
        return jsonify({"ok": True, "altar": altar})

    @app.route("/library")
    def _library():
        """Library inventory — what we have, what's missing, what's next."""
        p = Path("/tmp/library_state.json")
        if p.exists():
            return app.response_class(p.read_text(), mimetype="application/json")
        try:
            from npu_engine.library_kernel import build_library_state
            return jsonify(build_library_state())
        except Exception as exc:
            return jsonify({"error": str(exc)})


    # ── Plants + land routes → plants_bp (RTE-005) ────────
    from npu_engine.routes.plants_bp import plants_bp
    app.register_blueprint(plants_bp)

    @app.route("/muhurta-quality")
    def _muhurta_quality():
        payload = get_muhurta_quality()
        return app.response_class(
            json.dumps(payload, default=_json_serial, ensure_ascii=False),
            mimetype="application/json",
        )

    @app.route("/coherence-score")
    def _coherence_score():
        """Legacy scalar coherence score for today's panchanga."""
        coh = get_coherence_score()
        return app.response_class(
            json.dumps(coh, default=_json_serial, ensure_ascii=False),
            mimetype="application/json",
        )

    @app.route("/coherence")
    def _coherence_route():
        fs = field_state()
        panchanga = fs["panchanga"]
        try:
            top_n = int(request.args.get("n", 10))
        except (TypeError, ValueError):
            top_n = 10
        category = request.args.get("cat", None)
        top_n = max(1, min(top_n, 100))

        try:
            toroid = get_toroid()
            # Over-fetch so category weighting can promote cosmological entities
            fetch_n = max(top_n, min(top_n * 5, 200)) if not category else top_n
            results = toroid.field_query(_toroid_panchanga(fs), top_n=fetch_n, category=category)
        except Exception as e:
            return app.response_class(
                json.dumps({"error": str(e), "moment": panchanga, "entities": [], "count": 0}, default=_json_serial, ensure_ascii=False),
                mimetype="application/json",
                status=503,
            )

        # Apply category weights so cosmological entities dominate
        from npu_engine.coherence_engine_v2 import _cat_w
        for ent in results:
            eid = ent.get("entity_id", "")
            w = _cat_w(eid)
            ent["score"] = ent.get("score", 0.0) * w
        # Normalize to 0..1 after weighting
        max_sc = max((e.get("score", 0.0) for e in results), default=1.0) or 1.0
        for ent in results:
            ent["score"] = round(ent["score"] / max_sc, 6)
        results.sort(key=lambda e: e.get("score", 0.0), reverse=True)
        # Diversity cap: max 3 entities per category prefix
        _seen_cat = {}
        _diverse = []
        for ent in results:
            eid = ent.get("entity_id", "")
            cat = eid.split("_")[0] if "_" in eid else eid
            _seen_cat[cat] = _seen_cat.get(cat, 0) + 1
            if _seen_cat[cat] <= 3:
                _diverse.append(ent)
        results = _diverse[:top_n]

        # Enrich entities with element + rgb for rendering
        for ent in results:
            elem = _phi_to_element(ent.get("phi", 0))
            ent["element"] = elem
            ent["rgb"] = _ELEMENT_RGB.get(elem, _ELEMENT_RGB["ether"])

        legacy = get_coherence_score()

        # Temple geometry
        _formations = []
        _vastu_active = False
        _pralaya = False
        if _temple:
            _formations = _temple.detect_formations(results)
            _vastu_active = len(results) >= 64
            arc = fs.get("visual", {}).get("arc_phase", 0.5)
            for fm in _formations:
                fm["lifecycle"] = _temple.formation_lifecycle(fm, arc)

        # Optional semantic retrieval layer (additive; never breaks /coherence contract)
        semantic = {"query": "", "hits": []}
        try:
            from npu_engine.vector_store import get_vector_store
            store = get_vector_store()
            p5 = fs.get("panchanga") or {}
            nak = p5.get("nakshatra", "")
            tithi = p5.get("tithi", "")
            vara = p5.get("vara", "")
            element = (p5.get("element") or (p5.get("nak_data") or {}).get("element") or "")
            guna = (p5.get("guna") or (p5.get("nak_data") or {}).get("guna") or "")
            semantic["query"] = " · ".join(str(x).strip() for x in (nak, tithi, vara, element, guna) if x)
            semantic["hits"] = store.search(semantic["query"], n=8) if semantic["query"] else []
            by_entity = {}
            for hit in semantic["hits"]:
                eid = str(hit.get("entity_id", "") or "")
                try:
                    score = float(hit.get("score", 0.0) or 0.0)
                except Exception:
                    score = 0.0
                if eid:
                    by_entity[eid] = max(by_entity.get(eid, 0.0), score)
            for ent in results:
                eid = ent.get("entity_id")
                if eid and eid in by_entity:
                    ent["semantic_score"] = round(by_entity[eid], 6)
        except Exception as exc:
            semantic["error"] = str(exc)

        payload = {
            "moment": panchanga,
            "entities": results,
            "count": len(results),
            "all_scores": legacy.get("all_scores", []),
            "coherence_top": legacy.get("coherence_top", 0),
            "top_match": legacy.get("top_match"),
            "node_class": legacy.get("node_class"),
            "semantic": semantic,
            "formations": _formations,
            "vastu_active": _vastu_active,
            "pralaya": _pralaya,
        }
        return app.response_class(
            json.dumps(payload, default=_json_serial, ensure_ascii=False),
            mimetype="application/json",
        )

    @app.route("/generate-composition")
    def _generate_composition():
        fs = field_state()
        panchanga = dict(fs["panchanga"])
        panchanga["muhurta"] = fs.get("muhurta") or {}
        payload = generate_composition(panchanga)
        return app.response_class(
            json.dumps(payload, default=_json_serial, ensure_ascii=False),
            mimetype="application/json",
        )

    @app.route("/codex/render", methods=["POST"])
    def _codex_render():
        """Typographic field renderer — segments text according to field state.

        Takes: {text, mode, layer}
        Returns: {segments, palette, rhythm_ms}
        All typography derived from current panchanga + sound state.
        """
        data = request.get_json(force=True)
        text = data.get("text", "")
        req_layer = data.get("layer", currentLayer if 'currentLayer' in dir() else 0)

        fs = field_state()
        p = fs.get("panchanga", {})
        ss = fs.get("sound_state", {})
        nak = p.get("nak_data", {})
        devi = p.get("devi", ["", "", "", ""])

        element = (nak.get("element") or p.get("element") or "ether").lower()
        guna = (nak.get("guna") or p.get("guna") or "sattva").lower()
        bpm = ss.get("bpm", 72)
        tala_bols = ss.get("tala_bols", [])
        arc = p.get("tidx", 0) / 30.0
        paksha = p.get("paksha", "Śukla")

        # Element → color
        elem_colors = {"fire": "#c86420", "water": "#2868a8", "earth": "#5a7040",
                       "air": "#6098b0", "ether": "#c8a96e"}
        # Guna → density (line-height)
        guna_density = {"sattva": 2.2, "rajas": 1.6, "tamas": 1.3}
        # Guna → color
        guna_colors = {"sattva": "#dcdace", "rajas": "#c8a96e", "tamas": "#8060a0"}
        # S-layer symbols
        layer_syms = ["✦", "🔱", "♫", "☽", "◈", "✿", "◎"]
        # Nakshatra → weight
        nak_weights = {"fire": 500, "water": 300, "earth": 400, "air": 300, "ether": 300}
        # Nakshatra → tracking
        nak_tracking = {"fire": "0.1em", "water": "0.2em", "earth": "0.08em",
                        "air": "0.25em", "ether": "0.3em"}

        rhythm_ms = int(60000 / max(bpm, 30))
        n_bols = max(len(tala_bols), 1)

        # Split text into words, assign to tala beats
        words = text.split() if text else []
        segments = []
        li = int(req_layer) if isinstance(req_layer, (int, float, str)) and str(req_layer).isdigit() else 0
        li = max(0, min(6, li))
        sym = layer_syms[li]
        base_color = elem_colors.get(element, "#c8a96e")
        weight = nak_weights.get(element, 400)
        tracking = nak_tracking.get(element, "0.12em")

        # Devi bija prepend
        bija = _devi_field(devi, 1) or None

        for i, word in enumerate(words):
            bol_idx = i % n_bols
            is_sam = bol_idx == 0
            delay = bol_idx * rhythm_ms

            # Size hierarchy: first word large, sam positions medium, rest small
            if i == 0:
                size = "1.8rem"
                w = 500
            elif is_sam:
                size = "1.1rem"
                w = 400
            else:
                size = "0.85rem"
                w = weight

            seg = {
                "text": word,
                "layer": f"S{li}",
                "size": size,
                "weight": w,
                "tracking": tracking if i == 0 else "normal",
                "color": base_color if not is_sam else "#dcdace",
                "delay_ms": delay + (i // n_bols) * rhythm_ms * n_bols,
                "emphasis": is_sam,
                "symbol": sym if i == 0 else (bija if i == 1 and bija else None),
            }
            segments.append(seg)

        # Waning arc → reverse reveal order
        if paksha == "Kṛṣṇa":
            max_delay = max((s["delay_ms"] for s in segments), default=0)
            for s in segments:
                s["delay_ms"] = max_delay - s["delay_ms"]

        palette = {
            "primary": base_color,
            "muted": guna_colors.get(guna, "#c8a96e"),
            "accent": elem_colors.get(element, "#c8a96e"),
            "bg": "#010503",
            "density": guna_density.get(guna, 1.6),
        }

        return app.response_class(
            json.dumps({"segments": segments, "palette": palette, "rhythm_ms": rhythm_ms},
                       ensure_ascii=False),
            mimetype="application/json",
        )

    @app.route("/codex-context")
    def _codex_context():
        """Everything Codex needs for field-aware generation in one payload."""
        fs = field_state()
        natal = load_natal() or {}
        p = fs.get("panchanga") or {}
        nak = p.get("nak_data") or {}
        devi = p.get("devi") or ["", "", "", ""]
        mu = fs.get("muhurta") or {}
        coherence = _codex_coherence(fs, limit=5)
        payload = {
            "field": p,
            "natal": natal,
            "chandas": _hour_chandas(),
            "coherence_top": coherence[:5],
            "context": {
                "nakshatra": p.get("nakshatra", ""),
                "nakshatra_deity": nak.get("deity", ""),
                "nakshatra_shakti": nak.get("shakti", ""),
                "nakshatra_themes": nak.get("themes", ""),
                "element": p.get("element") or nak.get("element", ""),
                "guna": p.get("guna") or nak.get("guna", ""),
                "body_region": p.get("body_region") or nak.get("body_region", ""),
                "tithi": p.get("tithi", ""),
                "tithi_deity": p.get("tithi_deity", ""),
                "devi": _devi_field(devi, 0),
                "devi_description": _devi_field(devi, 2),
                "vara": p.get("vara", ""),
                "raga": fs.get("devi_raga") or (_devi_field(devi, 3)),
                "paksha": p.get("paksha", ""),
                "lagna": natal.get("lagna", "Vrishabha"),
                "lagna_nak": natal.get("lagna_nak", natal.get("lagna_nakshatra", "Rohini pada 1")),
                "dasha_lord": (natal.get("dasha") or {}).get("lord", "Budha"),
                "dasha_sub": (natal.get("dasha") or {}).get("sub_lord", "Budha"),
                "bpm": mu.get("bpm", 72),
                "muhurta": mu.get("name", ""),
            },
        }
        return app.response_class(
            json.dumps(payload, default=_json_serial, ensure_ascii=False),
            mimetype="application/json",
        )

    @app.route("/journal/save", methods=["POST"])
    def _journal_save_legacy():
        payload = request.get_json(silent=True) or {}
        now = datetime.now()
        journal_dir = Path(_here, "instance", "journal")
        journal_dir.mkdir(parents=True, exist_ok=True)
        journal_file = journal_dir / f"{now.strftime('%Y-%m-%d')}.json"
        entries = []
        if journal_file.exists():
            try:
                entries = json.loads(journal_file.read_text(encoding="utf-8"))
                if not isinstance(entries, list):
                    entries = []
            except Exception:
                entries = []
        entry_id = now.strftime("%Y%m%d%H%M%S%f")
        entry = {
            "entry_id": entry_id,
            "timestamp": payload.get("timestamp") or now.isoformat(),
            "mode": payload.get("mode", ""),
            "approach": payload.get("approach", ""),
            "intention": payload.get("intention", ""),
            "output": payload.get("output", ""),
            "field": payload.get("field", {}),
        }
        entries.append(entry)
        journal_file.write_text(
            json.dumps(entries, default=_json_serial, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return jsonify({"saved": True, "entry_id": entry_id})

    @app.route("/codex/generate", methods=["POST"])
    def _codex_generate():
        """Proxy generation to Claude API with field context."""
        body = request.get_json(silent=True) or {}
        system = body.get("system", "You are the Atlas codex.")
        prompt = body.get("prompt", "")
        max_tokens = int(body.get("max_tokens", 800))
        result = _claude_generate(system, prompt, max_tokens)
        if result:
            return jsonify({"text": result})
        return jsonify({"error": "generation failed — no API key or API unreachable"}), 500

    # ── NPU ENGINE ENDPOINTS ─────────────────────────

    @app.route("/codex/entity/<path:entity_id>")
    def _codex_entity(entity_id):
        mode = request.args.get("mode", "brief")
        fs = field_state()
        try:
            from npu_engine.codex_interaction import codex_from_entity
            canonical = entity_id.replace(":", "_").replace("-", "_").lower()
            text = codex_from_entity(fs, canonical, mode=mode)
            return app.response_class(
                json.dumps({"text": text, "entity": canonical, "mode": mode}, ensure_ascii=False),
                mimetype="application/json",
            )
        except Exception as e:
            return app.response_class(
                json.dumps({"error": str(e), "entity": entity_id}, ensure_ascii=False),
                mimetype="application/json", status=500,
            )

    @app.route("/codex/paths/<path:entity_id>")
    def _codex_paths(entity_id):
        depth = min(int(request.args.get("depth", 2)), 3)
        fs = field_state()
        try:
            from npu_engine.codex_interaction import paths_from_entity
            from npu_engine.path_engine import format_path
            canonical = entity_id.replace(":", "_").replace("-", "_").lower()
            paths = paths_from_entity(fs, canonical, depth=depth)
            formatted = [format_path(p) for p in paths[:8]]
            return app.response_class(
                json.dumps({"paths": formatted, "entity": canonical, "count": len(formatted)}, ensure_ascii=False),
                mimetype="application/json",
            )
        except Exception as e:
            return app.response_class(
                json.dumps({"error": str(e), "entity": entity_id, "paths": []}, ensure_ascii=False),
                mimetype="application/json", status=500,
            )

    @app.route("/query/entity")
    def _query_entity():
        focus = request.args.get("focus", "").replace(":", "_").replace("-", "_").lower()
        domain = request.args.get("domain", "")
        depth = min(int(request.args.get("depth", 1)), 3)
        top_n = min(int(request.args.get("top_n", 20)), 50)
        fs = field_state()
        try:
            from npu_engine.query_engine import query
            result = query(fs, focus=focus or None, domain=domain or None,
                           depth=depth, top_n=top_n)
            return app.response_class(
                json.dumps(result, default=_json_serial, ensure_ascii=False),
                mimetype="application/json",
            )
        except Exception as e:
            return app.response_class(
                json.dumps({"error": str(e), "entities": [], "count": 0}, ensure_ascii=False),
                mimetype="application/json", status=500,
            )

    @app.route("/layers/summary")
    def _layers_summary():
        try:
            from npu_engine.layer_engine import all_layer_summaries
            return app.response_class(
                json.dumps(all_layer_summaries(), default=_json_serial, ensure_ascii=False),
                mimetype="application/json",
            )
        except Exception as e:
            return app.response_class(
                json.dumps({"error": str(e)}, ensure_ascii=False),
                mimetype="application/json", status=500,
            )

    @app.route("/codex/cluster", methods=["POST"])
    def _codex_cluster():
        data = request.get_json(force=True)
        entity_ids = [eid.replace(":", "_").replace("-", "_").lower()
                      for eid in data.get("entities", [])]
        mode = data.get("mode", "cluster")
        fs = field_state()
        try:
            from npu_engine.codex_interaction import codex_from_cluster
            text = codex_from_cluster(fs, entity_ids, mode=mode)
            return app.response_class(
                json.dumps({"text": text, "entities": entity_ids}, ensure_ascii=False),
                mimetype="application/json",
            )
        except Exception as e:
            return app.response_class(
                json.dumps({"error": str(e), "entities": entity_ids}, ensure_ascii=False),
                mimetype="application/json", status=500,
            )

    @app.route("/hexfield-data")
    def _hexfield_data():
        """Plant/agriculture/biodynamic data indexed by nakshatra for hex field."""
        plants = _load_csv("plants/nakshatra_plants.csv")
        agri = _load_csv("plants/nakshatra_agriculture.csv")
        bio = _load_csv("astrobotany/biodynamic_vedic_mapping.csv")

        # Build biodynamic lookup: nakshatra → day type
        bio_map = {}
        for row in bio:
            naks_str = row.get("nakshatra_equivalents_sidereal_major", "")
            day_type = row.get("biodynamic_day_type", "")
            for chunk in naks_str.split(";"):
                name = chunk.strip().split("(")[0].strip().lower().replace(" ", "_")
                if name:
                    bio_map[name] = day_type

        result = {}
        for p in plants:
            key = (p.get("nakshatra") or "").strip()
            nid = key.lower().replace(" ", "_")
            entry = {
                "plant": p.get("plant", ""),
                "common_name": p.get("common_name", ""),
                "sanskrit_name": p.get("sanskrit_name", ""),
                "deity": p.get("deity", ""),
                "element": p.get("element", ""),
                "dosha": p.get("dosha", ""),
                "use": p.get("use", ""),
                "mantra": p.get("mantra", ""),
                "body_part": p.get("body_part", ""),
                "season": p.get("season", ""),
                "growing_notes": p.get("growing_notes", ""),
                "ritual_use": p.get("ritual_use", ""),
                "ayurvedic_use": p.get("ayurvedic_use", ""),
            }
            # Merge agriculture
            for a in agri:
                if (a.get("nakshatra") or "").strip().lower().replace(" ", "_") == nid:
                    entry["activity"] = a.get("activity", "")
                    entry["avoid"] = a.get("avoid", "")
                    entry["crops"] = a.get("crops", "")
                    entry["quality"] = a.get("quality", "")
                    break
            entry["biodynamic_type"] = bio_map.get(nid, "")
            result[nid] = entry
        return jsonify(result)

    @app.route("/coherence-field")
    def _coherence_field():
        """Return all node scores with node_class for shell ring brightness."""
        if not _coherence:
            return app.response_class(
                json.dumps({"error": "CoherenceEngine not available"}, ensure_ascii=False),
                mimetype="application/json",
                status=503,
            )
        fs = field_state()
        p5 = fs["panchanga"]
        tithi_for_scoring = ((p5.get("tidx", 1) % 15) or 15)
        scores = _coherence.score_hybrid(tithi_for_scoring, limit=500, fs=fs)
        nodes = []
        for i, s in enumerate(scores):
            layer_idx = min(i // max(1, len(scores) // 7), 6)
            nodes.append({
                "node_id": s.candidate,
                "node_class": s.node_class,
                "score": s.score,
                "s_layer": f"S{layer_idx}",
                "reasons": s.reasons,
            })
        return app.response_class(
            json.dumps(nodes, default=_json_serial, ensure_ascii=False),
            mimetype="application/json",
        )

    @app.route("/vastu")
    def _vastu_field():
        """Vastu zone data from CSVs enriched with live field state."""
        _datasets_dir = Path(__file__).resolve().parent / "datasets"
        # Load the two vastu CSVs
        zones_csv = _datasets_dir / "cosmology" / "vastu_zones.csv"
        dirs_csv = _datasets_dir / "cosmology" / "vastu_directions.csv"
        zones_rows = []
        dirs_rows = []
        if zones_csv.exists():
            with open(zones_csv) as f:
                zones_rows = list(csv.DictReader(f))
        if dirs_csv.exists():
            with open(dirs_csv) as f:
                dirs_rows = list(csv.DictReader(f))

        # Build zone_meta and direction_to_zone from CSV data
        zone_meta = {}
        direction_to_zone = {}
        for row in zones_rows:
            name = row.get("zone", "")
            direction = row.get("direction", "")
            zone_meta[name] = {
                "direction": direction if direction != "Center" else "C",
                "deity": row.get("deity", ""),
                "element": row.get("element", ""),
                "planet": row.get("planet", ""),
            }
            d_key = direction if direction != "Center" else "C"
            direction_to_zone[d_key] = name

        # Enrich with direction CSV data (guna, zone_activity, body)
        body_map = {
            "NE": "head \u00b7 wisdom \u00b7 third eye",
            "E": "right side \u00b7 liver \u00b7 vision",
            "SE": "digestive fire \u00b7 metabolism",
            "S": "legs \u00b7 grounding \u00b7 ancestors",
            "SW": "reproductive \u00b7 stability",
            "W": "kidneys \u00b7 emotions \u00b7 creativity",
            "NW": "lungs \u00b7 breath \u00b7 movement",
            "N": "heart \u00b7 wealth \u00b7 open",
            "C": "spine \u00b7 central channel \u00b7 sushumna",
        }
        synthesis_meta = {
            "NE": "inward / clarifying / receptive",
            "E": "awakening / opening / emergent",
            "SE": "outward / transforming / catalytic",
            "S": "settling / ancestral / grounding",
            "SW": "dense / containing / stabilizing",
            "W": "absorbing / reflective / fluid",
            "NW": "mobile / circulatory / distributive",
            "N": "gathering / nourishing / magnetic",
            "C": "still / pressurized / integrating",
        }
        for row in dirs_rows:
            raw_dir = row.get("direction", "")
            # Normalize direction names to match zone CSV
            dir_norm = {
                "East": "E", "West": "W", "North": "N", "South": "S",
                "NorthEast": "NE", "NorthWest": "NW",
                "SouthEast": "SE", "SouthWest": "SW",
                "Center": "C",
            }.get(raw_dir, raw_dir)
            zone_name = direction_to_zone.get(dir_norm, "")
            if zone_name and zone_name in zone_meta:
                zone_meta[zone_name]["guna"] = row.get("guna", "")
                zone_meta[zone_name]["zone_activity"] = row.get("zone_activity", "")

        for name, meta in zone_meta.items():
            d = meta.get("direction", "")
            meta["body"] = body_map.get(d, "")
            meta["synthesis"] = synthesis_meta.get(d, "balanced")

        # Live field state for active zone
        fs = field_state()
        p5 = fs["panchanga"]
        element = p5.get("element", "ether")
        vara = p5.get("vara", "")
        nakshatra = p5.get("nakshatra", "")
        vara_graha_name = ""
        if fs.get("vara_graha"):
            vara_graha_name = fs["vara_graha"].get("name", "")

        active_zone_data = compute_vastu_zone(vara_graha_name or element, nakshatra)
        active_direction = active_zone_data.get("zone_direction", "center")
        # Normalize active_direction
        active_dir_norm = {
            "north": "N", "south": "S", "east": "E", "west": "W",
            "northeast": "NE", "northwest": "NW",
            "southeast": "SE", "southwest": "SW",
            "center": "C",
        }.get(active_direction.lower(), "C")

        devi = p5.get("devi", ["", "\u2726", "", ""])

        result = {
            "zones": zone_meta,
            "direction_to_zone": direction_to_zone,
            "active_zone": direction_to_zone.get(active_dir_norm, "Brahma"),
            "active_direction": active_dir_norm,
            "field": {
                "element": element,
                "guna": p5.get("guna", ""),
                "vara": vara,
                "nakshatra": nakshatra,
                "raga": fs.get("devi_raga", ""),
                "devi_name": _devi_field(devi, 0),
                "devi_emoji": _devi_field(devi, 1) or "\u2726",
            },
        }
        return app.response_class(
            json.dumps(result, default=_json_serial, ensure_ascii=False),
            mimetype="application/json",
        )

    @app.route("/s3/practice")
    def _s3_practice():
        """Unified practice data for S3 ecology app — replaces 8+ CSV fetches."""
        fs = field_state()
        p5 = fs["panchanga"]
        nak = p5.get("nakshatra", "")
        element = p5.get("element", "ether").lower()
        guna = p5.get("guna", "").lower()
        vara = p5.get("vara", "")
        body_region = p5.get("body_region", "")

        # Load all practice datasets (kernel already has some cached)
        body_map = _load_csv("yoga/nakshatra_body_map.csv")
        marma_data = _body_marma  # already loaded at module level
        dosha_data = _dosha_nakshatra  # already loaded
        herb_data = _herb_exemplars  # already loaded
        raga_data = _raga_therapeutic  # already loaded
        vara_rules = _swara_vara_rules  # already loaded
        activity_matrix = _load_csv("svarodaya/activity_matrix.csv")
        elements_data = _load_csv("svarodaya/elements.csv")
        dinacharya = _load_csv("ayurveda/dinacharya_panchanga.csv")
        tulsi_data = _load_json("plants/plant_tulsi.json")
        astrobotany = _load_csv("astrobotany/astrobotanical_classes.csv")

        result = {
            "field": {
                "nakshatra": nak,
                "element": element,
                "guna": guna,
                "vara": vara,
                "body_region": body_region,
                "raga": fs.get("devi_raga", ""),
                "panchanga": p5,
            },
            "datasets": {
                "body_map": body_map,
                "marma": marma_data,
                "dosha": dosha_data,
                "herbs": herb_data,
                "ragas": raga_data,
                "vara_rules": vara_rules,
                "activity_matrix": activity_matrix,
                "elements": elements_data,
                "dinacharya": dinacharya,
                "tulsi": tulsi_data,
                "astrobotany": astrobotany,
            },
        }
        return app.response_class(
            json.dumps(result, default=_json_serial, ensure_ascii=False),
            mimetype="application/json",
        )

    @app.route("/bandhu/chat", methods=["POST"])
    def _bandhu_chat():
        """Bandhu companion — field-revealed tradition composition.

        Qwen3:8b provides optional connector sentence between pada and passage.
        Tradition speaks through pada + passage + metre; LLM is only grammar.
        """
        data = request.get_json(force=True) or {}
        message = data.get("message", "").strip()
        speak = bool(data.get("speak", False))
        if not message:
            return app.response_class(
                json.dumps({"error": "no message"}),
                mimetype="application/json", status=400,
            )

        fs = field_state()
        p5 = fs.get("panchanga", {})
        devi = p5.get("devi", {})
        devi_name = _devi_field(devi, 0) if isinstance(devi, (list, tuple)) else (devi.get("name", "") if isinstance(devi, dict) else "")

        use_llm = bool(data.get("use_llm", False))  # Qwen3:8b too slow for interactive; send use_llm=true explicitly

        from npu_engine.field.composition_engine import compose_response
        comp = compose_response(message, fs, speak=speak, use_llm=use_llm)

        return app.response_class(
            json.dumps({
                "response": comp.get("response_text", ""),
                "response_text": comp.get("response_text", ""),
                "pada": comp.get("pada", {}),
                "passage": comp.get("passage", {}).get("text", ""),
                "connector": comp.get("connector"),
                "interpretation": "",
                "metre": comp.get("metre", {}),
                "musical_response": comp.get("musical_response", {}),
                "rasa": comp.get("rasa", ""),
                "field": {
                    "nakshatra": p5.get("nakshatra", ""),
                    "devi": devi_name,
                    "raga": fs.get("devi_raga", ""),
                    "element": p5.get("element", ""),
                },
                "attestation": comp.get("attestation", "SYNTHESIS"),
                "source": "llm+graph" if use_llm and comp.get("connector") else "graph",
            }, ensure_ascii=False),
            mimetype="application/json",
        )

    @app.route("/bandhu/chat/full", methods=["POST"])
    def _bandhu_chat_full():
        """Bandhu with LLM connector — always use_llm=True."""
        data = request.get_json(force=True) or {}
        message = data.get("message", "").strip()
        if not message:
            return app.response_class(
                json.dumps({"error": "no message"}),
                mimetype="application/json", status=400,
            )
        fs = field_state()
        p5 = fs.get("panchanga", {})
        devi = p5.get("devi", {})
        devi_name = _devi_field(devi, 0) if isinstance(devi, (list, tuple)) else (devi.get("name", "") if isinstance(devi, dict) else "")

        from npu_engine.field.composition_engine import compose_response
        comp = compose_response(message, fs, use_llm=True)

        return app.response_class(
            json.dumps({
                "response": comp.get("response_text", ""),
                "response_text": comp.get("response_text", ""),
                "pada": comp.get("pada", {}),
                "passage": comp.get("passage", {}).get("text", ""),
                "connector": comp.get("connector"),
                "metre": comp.get("metre", {}),
                "musical_response": comp.get("musical_response", {}),
                "rasa": comp.get("rasa", ""),
                "field": {
                    "nakshatra": p5.get("nakshatra", ""),
                    "devi": devi_name,
                    "raga": fs.get("devi_raga", ""),
                    "element": p5.get("element", ""),
                },
                "attestation": comp.get("attestation", "SYNTHESIS"),
                "source": "llm+graph" if comp.get("connector") else "graph",
            }, ensure_ascii=False),
            mimetype="application/json",
        )

    @app.route("/graph/entities")
    def _graph_entities():
        """All NPU entities with theta/phi/category for graph apps."""
        try:
            from npu_engine.datasets import load_all_entities, load_entity_metadata, load_relations
            ents = load_all_entities()
            meta = load_entity_metadata()
            rels_raw = load_relations()
        except Exception as exc:
            return app.response_class(
                json.dumps({"error": str(exc)}),
                mimetype="application/json", status=503,
            )
        limit = int(request.args.get("limit", 2000))
        nodes = []
        for eid, (theta, phi) in list(ents.items())[:limit]:
            m = meta.get(eid, {})
            cat = m.get("category", eid.split("_")[0] if "_" in eid else "entity")
            attrs = m.get("attributes", {})
            elem = attrs.get("element", "")
            if isinstance(elem, list):
                elem = elem[0] if elem else ""
            name_iast = m.get("name", eid.replace("_", " "))
            nodes.append({
                "id": eid,
                "name_iast": name_iast,
                "category": cat,
                "element": elem,
                "theta": round(theta, 4),
                "phi": round(phi, 4),
                "coherence": 0.5,
            })

        edges = []
        seen = set()
        for src, rel_list in rels_raw.items():
            for rel in rel_list[:5]:  # limit edges per node
                edge_key = (src, rel.get("to_id", ""))
                if edge_key in seen:
                    continue
                seen.add(edge_key)
                edges.append({
                    "from_id": src,
                    "to_id": rel.get("to_id", ""),
                    "relation": rel.get("relation", ""),
                    "strength": float(rel.get("confidence", rel.get("strength", 0.5))),
                })
                if len(edges) >= 5000:
                    break
            if len(edges) >= 5000:
                break

        return app.response_class(
            json.dumps({"entities": nodes, "relations": edges}, ensure_ascii=False),
            mimetype="application/json",
        )

    @app.route("/tarot/deck/<deck>")
    def _tarot_deck(deck):
        """Return full card list for a tarot deck from datasets/tarot/."""
        deck_files = {
            "devi": "tarot/devi_cards.json",
            "graha": "tarot/graha_cards.json",
            "nakshatra": "tarot/nakshatra_cards.json",
        }
        if deck not in deck_files:
            return app.response_class(
                json.dumps({"error": f"unknown deck: {deck}", "available": list(deck_files.keys())}),
                mimetype="application/json", status=404,
            )
        cards = _load_json(deck_files[deck])
        if isinstance(cards, dict) and not cards:
            cards = []
        # Enrich with live field relevance
        fs = field_state()
        p5 = fs["panchanga"]
        current_element = p5.get("element", "").lower()
        current_nak = p5.get("nakshatra", "").lower()
        tidx = p5.get("tidx", 0)
        for card in cards:
            card["field_active"] = False
            card_elem = (card.get("element") or "").lower()
            if card_elem == current_element:
                card["field_active"] = True
            if deck == "devi" and card.get("tithi") == ((tidx % 15) or 15):
                card["field_active"] = True
            if deck == "nakshatra" and card.get("name", "").lower() in current_nak:
                card["field_active"] = True
        return app.response_class(
            json.dumps({"deck": deck, "cards": cards, "count": len(cards)},
                       default=_json_serial, ensure_ascii=False),
            mimetype="application/json",
        )

    @app.route("/tarot/draw", methods=["POST"])
    def _tarot_draw():
        """Weighted card draw from a deck based on field state."""
        import random
        data = request.get_json(force=True) or {}
        deck_name = data.get("deck", "devi")
        n = min(int(data.get("n", 3)), 15)

        deck_files = {
            "devi": "tarot/devi_cards.json",
            "graha": "tarot/graha_cards.json",
            "nakshatra": "tarot/nakshatra_cards.json",
        }
        cards = _load_json(deck_files.get(deck_name, "tarot/devi_cards.json"))
        if isinstance(cards, dict) and not cards:
            cards = []
        if not cards:
            return app.response_class(
                json.dumps({"error": "deck empty"}),
                mimetype="application/json", status=404,
            )

        fs = field_state()
        p5 = fs["panchanga"]
        current_element = p5.get("element", "").lower()

        # Weight by field resonance
        weights = []
        for card in cards:
            w = 1.0
            if (card.get("element") or "").lower() == current_element:
                w += 0.5
            if card.get("guna", "").lower() == p5.get("guna", "").lower():
                w += 0.3
            weights.append(w)

        drawn = []
        available = list(range(len(cards)))
        for _ in range(min(n, len(available))):
            avail_weights = [weights[i] for i in available]
            total = sum(avail_weights)
            r = random.random() * total
            cumulative = 0
            chosen = available[0]
            for idx in available:
                cumulative += weights[idx]
                if cumulative >= r:
                    chosen = idx
                    break
            drawn.append(cards[chosen])
            available.remove(chosen)

        return app.response_class(
            json.dumps({
                "deck": deck_name,
                "drawn": drawn,
                "field": {
                    "nakshatra": p5.get("nakshatra", ""),
                    "element": current_element,
                    "tithi": p5.get("tithi", ""),
                },
            }, default=_json_serial, ensure_ascii=False),
            mimetype="application/json",
        )

    @app.route("/archana/cards")
    def _archana_cards():
        """Return nakshatra, devi, and graha card data from NPU entity metadata."""
        # Nakshatras — match archana app's {n, e, g, d} shape
        naks = []
        for nd in NAKSHATRA_DATA:
            naks.append({
                "n": nd["name_key"],
                "e": nd.get("element", "ether").lower(),
                "g": nd.get("guna", "rajas").lower(),
                "d": nd.get("deity", ""),
            })

        # Nitya Devis — match archana app's {t, n, dv, b, e} shape
        devis = []
        for dd in DEVI_DATA:
            # Extract bija from mantra (last word before 'yai namah')
            bija = dd.get("mantra", "").split()
            bija_short = bija[3] if len(bija) > 3 else "hrīṁ"
            devis.append({
                "t": dd["tithi_number"],
                "n": dd["name"],
                "dv": dd.get("emoji", "✦") + " " + dd["name"],
                "b": bija_short,
                "e": dd.get("element", "fire").lower(),
            })

        # Varas — match archana app's {v, l, b, c, dv} shape
        vara_bijas = ["hram", "shram", "kram", "bram", "gram", "dram", "pram"]
        vara_colors = ["#F97316", "#CBD5E1", "#DC2626", "#16A34A", "#CA8A04", "#EC4899", "#6366F1"]
        vara_dv = ["सूर्य", "चन्द्र", "मंगल", "बुध", "गुरु", "शुक्र", "शनि"]
        vara_names = ["Ravivara", "Somavara", "Mangalavara", "Budhavara", "Guruvara", "Shukravara", "Shanivara"]
        varas = []
        for i, gd in enumerate(GRAHA_DATA[:7]):
            varas.append({
                "v": vara_names[i] if i < len(vara_names) else "",
                "l": gd["name_key"],
                "b": vara_bijas[i] if i < len(vara_bijas) else "",
                "c": vara_colors[i] if i < len(vara_colors) else "#888",
                "dv": vara_dv[i] if i < len(vara_dv) else "",
            })

        return app.response_class(
            json.dumps({"naks": naks, "devis": devis, "varas": varas},
                       default=_json_serial, ensure_ascii=False),
            mimetype="application/json",
        )

    @app.route("/layer-data")
    def _layer_data():
        """All data needed by S0-S6 layer panels in one call."""
        fs = field_state()
        interp = interpret_field()
        transit_data = get_transit_data()
        dasha = get_current_dasha()
        ecology = _today_plants()
        p5 = fs["panchanga"]
        devi = p5["devi"]
        nak = p5["nak_data"]
        raga_name = fs["devi_raga"]
        raga_def = fs.get("devi_raga_def") or {}
        mu = fs["muhurta"]
        # note names for display
        _nn = ["S","r","R","g","G","m","M","P","d","D","n","N"]
        scale_str = " ".join(_nn[s] for s in raga_def.get("scale",[])) if raga_def else ""
        vadi_str = _nn[raga_def["vadi"]] if raga_def and "vadi" in raga_def else ""
        samvadi_str = _nn[raga_def["samvadi"]] if raga_def and "samvadi" in raga_def else ""

        # plant for today's nakshatra element
        nak_element = nak.get("element","").lower()
        today_plant = None
        for pl in PLANT_DATA:
            if pl.get("element","").lower() == nak_element:
                today_plant = pl; break
        if not today_plant and PLANT_DATA:
            today_plant = PLANT_DATA[0]

        data = {
            "panchanga": {
                "tithi": p5["tithi"], "paksha": p5["paksha"],
                "tidx": p5["tidx"], "didx": p5["didx"],
                "tithi_deity": p5["tithi_deity"],
                "nakshatra": p5["nakshatra"], "nak_lord": p5["nak_lord"],
                "nak_data": nak, "vara": p5["vara"],
            },
            "devi": {"name":_devi_field(devi,0),"emoji":_devi_field(devi,1),"process":_devi_field(devi,2),"raga":_devi_field(devi,3)},
            "muhurta": mu,
            "raga": {
                "name": raga_name, "scale": scale_str,
                "vadi": vadi_str, "samvadi": samvadi_str,
                "rasa": raga_def.get("rasa",""), "time": raga_def.get("time",""),
            },
            "interpret": {
                "pada": interp["nakshatra_pada"],
                "moon_rashi": interp["moon_rashi"],
                "dasha": dasha,
                "tithi_quality": interp["tithi_quality"],
                "gana": interp["gana"],
                "themes": interp["themes"],
                "practice": interp["practice"],
                "study": interp["study"],
                "avoid": interp["avoid"],
                "dosha_food": interp["dosha_food"],
            },
            "plant": today_plant,
            "plants_today": ecology,
            "graha": fs.get("nak_graha"),
            "vara_graha": fs.get("vara_graha"),
            "natal": NATAL,
            "transit_hits": transit_data["hits"][:6],
            "dasha": dasha,
            "yuga": "Kali", "alpha": 1.0,
        }
        return app.response_class(
            json.dumps(data, default=_json_serial, ensure_ascii=False),
            mimetype="application/json",
        )

    @app.route("/layers")
    def _layers():
        """S0-S6 layer summaries with dataset content."""
        try:
            from npu_engine.layer_engine import all_layer_summaries, load_layer_data
            summaries = all_layer_summaries()
            # Add sample rows for each layer (top 20)
            for s in summaries:
                rows = load_layer_data(s["layer"])
                s["sample_rows"] = rows[:20]
                s["row_count"] = len(rows)
        except Exception as exc:
            summaries = [{"error": str(exc)}]
        return app.response_class(
            json.dumps(summaries, default=_json_serial, ensure_ascii=False),
            mimetype="application/json",
        )

    @app.route("/layers/<layer>")
    def _layer_detail(layer):
        """Full dataset content for a single S-layer."""
        layer = layer.upper()
        if layer not in [f"S{i}" for i in range(7)]:
            return app.response_class(json.dumps({"error": f"unknown layer: {layer}"}), mimetype="application/json", status=404)
        try:
            from npu_engine.layer_engine import layer_summary, load_layer_data
            summary = layer_summary(layer)
            summary["rows"] = load_layer_data(layer)
        except Exception as exc:
            summary = {"error": str(exc)}
        return app.response_class(
            json.dumps(summary, default=_json_serial, ensure_ascii=False),
            mimetype="application/json",
        )

    @app.route("/ollama", methods=["POST"])
    def _ollama_proxy():
        """Proxy to local Ollama API — avoids CORS issues."""
        import urllib.request as _ur
        body = request.get_data()
        try:
            req = _ur.Request("http://localhost:11434/api/generate",
                              data=body,
                              headers={"Content-Type": "application/json"})
            with _ur.urlopen(req, timeout=30) as r:
                result = r.read()
            return app.response_class(result, mimetype="application/json")
        except Exception as exc:
            return app.response_class(
                json.dumps({"error": str(exc)}, ensure_ascii=False),
                mimetype="application/json", status=502)

    # ── Base path ─────────────────────────────────────────────
    _here = os.path.dirname(os.path.abspath(__file__))

    @app.route("/helix")
    def _helix():
        from npu_engine.field.helix_engine import derive_helix_field
        days = int(request.args.get("days", 90))
        return jsonify(derive_helix_field(field_state(), days))

    # ── _enrich_fs_yantra, yantra/svg, yantra/data → render_bp (registered above) ────────

    @app.route("/passages")
    def _passages():
        """GET /passages?entity=devi_kamesvari&limit=5

        Returns text passages mentioning an entity, ranked by tradition weight.
        """
        from npu_engine.passage_resolver import find_passages
        entity_id = request.args.get("entity", "")
        limit = int(request.args.get("limit", "5"))
        if not entity_id:
            return app.response_class(
                json.dumps({"error": "entity param required"}, ensure_ascii=False),
                mimetype="application/json", status=400)
        try:
            passages = find_passages(entity_id, limit=limit)
        except Exception as exc:
            passages = []
        return app.response_class(
            json.dumps({"entity": entity_id, "passages": passages},
                       default=_json_serial, ensure_ascii=False),
            mimetype="application/json")

    @app.route("/shell/state")
    def _shell_state():
        """Resolved mandala state — all 9 zones with content.

        Query params:
          ?layer=S5            — return sub-mandala for that layer
          ?layer=S5&zone=SW    — return sub-zone (third level) for that zone
          (omit)               — return main mandala
        """
        from npu_engine.mandala_schema import (
            resolve_mandala, resolve_sub_mandala, resolve_sub_zone
        )
        try:
            fs = field_state()

            # Build graph for entity resolution
            try:
                from npu_engine.graph_engine import GraphEngine
                graph = GraphEngine()
            except Exception:
                graph = None

            # Build spine-like payload with layers
            try:
                from npu_engine.field_layers import generate_layer_mapping
                spine_payload = {
                    "panchanga": fs.get("panchanga", {}),
                    "entities": (fs.get("entities") or [])[:64],
                    "formations": fs.get("formations", []),
                    "sound_state": fs.get("sound_state", _derive_sound_state(fs)),
                    "theta": fs.get("theta", 0.0),
                    "phi": fs.get("phi", 1.57),
                    "vastu_state": fs.get("vastu_state", {}),
                }
                spine_payload["layers"] = generate_layer_mapping(spine_payload)
            except Exception:
                spine_payload = {
                    "panchanga": fs.get("panchanga", {}),
                    "layers": {},
                }

            layer = request.args.get("layer", "")
            zone = request.args.get("zone", "")

            # Prepare S5 data if needed
            s5_data = {}
            if layer in ("S5",) or (not layer and not zone):
                try:
                    from npu_engine.s5_kernel import derive_s5_state
                    s5_data = derive_s5_state(fs)._asdict()
                except Exception:
                    s5_data = {}

            if layer and layer in ("S0", "S1", "S2", "S3", "S4", "S5", "S6"):
                if zone and zone in ("NW","N","NE","W","C","E","SW","S","SE"):
                    result = resolve_sub_zone(
                        layer, zone, spine_payload,
                        graph=graph, s5_data=s5_data
                    )
                    if result is None:
                        result = resolve_sub_mandala(
                            layer, spine_payload,
                            graph=graph, s5_data=s5_data
                        )
                else:
                    result = resolve_sub_mandala(
                        layer, spine_payload,
                        graph=graph, s5_data=s5_data
                    )
            else:
                result = resolve_mandala(spine_payload, graph=graph)

            # Inject center icons from zone engines
            try:
                from npu_engine.engines import CENTER
                center_icons = CENTER.render_zone(spine_payload).get("icons", [])
                if result.get("zones", {}).get("c"):
                    result["zones"]["c"]["icons"] = center_icons
            except Exception:
                pass

            # Inject trajectory session arc
            try:
                from npu_engine.field.trajectory_engine import derive_trajectory
                traj = derive_trajectory(fs)
                sa = traj.get("session_arc", {})
                result["session_arc"] = {
                    "suggested_arc": sa.get("suggested_arc", ""),
                    "suggested_duration_min": sa.get("suggested_duration_min", 0),
                    "opening_mood": sa.get("opening_mood", ""),
                    "closing_mood": sa.get("closing_mood", ""),
                }
            except Exception:
                pass

        except Exception as exc:
            import traceback
            result = {"error": str(exc), "trace": traceback.format_exc()}

        return app.response_class(
            json.dumps(result, default=_json_serial, ensure_ascii=False),
            mimetype="application/json",
        )

    @app.route("/field-stream")
    def _field_stream():
        import time as _time

        def _sse_gen():
            while True:
                fs = field_state()
                interp = interpret_field()
                data = json.dumps({"field": fs, "interpret": interp}, default=_json_serial, ensure_ascii=False)
                yield f"data: {data}\n\n"
                _time.sleep(10)
        return Response(
            _sse_gen(),
            mimetype="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    # ── Beat SSE — bridge POSTs beat index, shell listens ──
    _beat_listeners = []

    @app.route("/beat", methods=["POST"])
    def _beat_post():
        try:
            data = request.get_json(force=True) or {}
        except Exception:
            data = {}
        beat = data.get("beat", 0)
        msg = f"data: {json.dumps({'beat': beat})}\n\n"
        dead = []
        for q in _beat_listeners:
            try:
                q.put_nowait(msg)
            except Exception:
                dead.append(q)
        for q in dead:
            _beat_listeners.remove(q)
        return jsonify({"ok": True})

    @app.route("/beat")
    def _beat_stream():
        import queue
        q = queue.Queue(maxsize=64)
        _beat_listeners.append(q)

        def _gen():
            try:
                while True:
                    msg = q.get()
                    yield msg
            except GeneratorExit:
                pass
            finally:
                if q in _beat_listeners:
                    _beat_listeners.remove(q)
        return Response(
            _gen(),
            mimetype="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    @app.route("/npu-commentary")
    def _npu_commentary():
        fs = field_state()
        interp = interpret_field()
        try:
            from scripts.ollama_client import generate as ollama_gen, ping
            if ping():
                prompt = json.dumps(interp, default=_json_serial, ensure_ascii=False) + "\nGive a 1-sentence field reading."
                text = ollama_gen(prompt)
            else:
                text = f"Tithi {fs['panchanga']['tithi']} · {fs['panchanga']['nakshatra']} · {_devi_field(fs['panchanga']['devi'], 0)}"
        except Exception:
            text = f"Tithi {fs['panchanga']['tithi']} · {fs['panchanga']['nakshatra']}"
        return jsonify({
            "commentary": text,
            "field": {
                "tithi": fs["panchanga"]["tithi"],
                "devi": _devi_field(fs["panchanga"]["devi"], 0),
                "nakshatra": fs["panchanga"]["nakshatra"],
            },
        })

    # Serve atlas portal and static assets from the same directory

    @app.route("/brahmanda/state")
    def _brahmanda_state():
        """Unified state for brahmanda — one poll drives both visual and sound.

        Returns: entities (visual), svara weights (melody), yantra geometry (tāla),
        s0 thread activation (mantra volume), breath rate (tempo).
        """
        try:
            spine_data = json.loads(_spine().get_data(as_text=True))
        except Exception:
            spine_data = field_state()

        ss = spine_data.get("sound_state", {})
        p5 = spine_data.get("panchanga", {})

        # Entity positions with layer classification
        entities = []
        for e in (spine_data.get("entities") or [])[:64]:
            eid = e.get("entity_id", e.get("id", ""))
            prefix = eid.split("_")[0] if "_" in eid else ""
            layer_map = {
                "tattva":"S0","parampara":"S0","rasa":"S0",
                "deity":"S1","devi":"S1","graha":"S1","bija":"S1",
                "raga":"S2","svara":"S2","tala":"S2",
                "nakshatra":"S3","tithi":"S3","vara":"S3",
                "yantra":"S4","vastu":"S4","element":"S4",
                "plant":"S5","marma":"S5","dosha":"S5","herb":"S5",
                "art":"S6","activity":"S6",
            }
            entities.append({
                "id": eid,
                "layer": layer_map.get(prefix, "S5"),
                "theta": e.get("theta", 0),
                "phi": e.get("phi", 0),
                "score": e.get("score", 0),
                "element": e.get("element", "ether"),
            })

        # Svara weights from raga scale — S3 ring entity density
        raga_notes = ss.get("raga_notes", [])
        svara_all = ["Sa","re","Re","ga","Ga","ma","Ma","Pa","dha","Dha","ni","Ni"]
        active_set = set(raga_notes)
        vadi = ss.get("raga_vadi", "")
        samvadi = ss.get("raga_samvadi", "")
        svara_weights = {}
        for s in svara_all:
            w = 0.0
            if s in active_set:
                w = 0.5
                if s == vadi: w = 1.0
                elif s == samvadi: w = 0.75
            svara_weights[s] = w

        # Yantra geometry
        try:
            from npu_engine.yantra_engine import generate_yantra
            yantra = generate_yantra(spine_data)
            yantra_out = {
                "beat_points": yantra.get("beat_points", []),
                "shape_type": yantra.get("shape_type", "circle"),
                "tala_beats": yantra.get("tala_beats", 8),
                "connections": len(yantra.get("connections", [])),
            }
        except Exception:
            yantra_out = {"beat_points": [], "shape_type": "circle", "tala_beats": 8, "connections": 0}

        # S0 thread activation — how many top entities have S0 roots
        _load_s0_roots()
        s0_count = sum(1 for e in entities[:16] if e["id"] in (_s0_roots_up or {}))
        s0_activation = min(1.0, s0_count / max(len(entities[:16]), 1))

        # Breath rate from observance
        obs_list = p5.get("observances") or vaishnava_observance(p5)
        obs_type = obs_list[0].get("type", "") if obs_list else ""
        breath_map = {"ekadashi":0.5, "disappearance":0.6, "purnima":0.8, "appearance":1.0, "lila":1.0}
        breath_rate = breath_map.get(obs_type, 1.0)

        _panchanga_dict = {
            "masa": p5.get("masa_name", ""),
            "tithi": p5.get("tithi", ""),
            "tidx": p5.get("tidx", 0),
            "paksha": p5.get("paksha", ""),
            "nakshatra": p5.get("nakshatra", ""),
            "vara": p5.get("vara", ""),
            "element": p5.get("element", ""),
            "guna": p5.get("guna", ""),
            "masa_num": p5.get("masa", 0),
        }

        # Vāstu S4 state + UI layout (derived, not cached)
        try:
            from npu_engine.vastu_engine import derive_vastu_state
            from npu_engine.ui_vastu_engine import derive_ui_layout
            # Normalize entity keys: brahmanda uses "id", engines expect "entity_id"
            _ents_norm = [{**e, "entity_id": e.get("id", e.get("entity_id", ""))} for e in entities]
            _vastu = derive_vastu_state(_panchanga_dict, _ents_norm, [], [], 0, 0)
            _ui_fs = {
                "panchanga": _panchanga_dict,
                "entities": _ents_norm,
                "formations": [],
                "vastu_state": _vastu,
                "lifecycle": {"phase": "formation", "intensity": breath_rate},
                "psi": {"intensity": s0_activation, "focus": 0.5, "stability": 0.7},
                "arc_phase": _panchanga_dict.get("tidx", 0) / 30.0,
            }
            _ui_layout = derive_ui_layout(_ui_fs)
        except Exception:
            _vastu = {}
            _ui_layout = {}

        # Sound spec (derived, same place as UI layout)
        _sound_spec = {}
        try:
            from npu_engine.sound.sound_engine import derive_sound_spec
            from npu_engine.sound.osc_bridge import send_sound_spec
            _sound_fs = {
                "panchanga": _panchanga_dict,
                "sound_state": ss,
                "entities": entities,
                "observances": obs_list,
                "psi": {"intensity": s0_activation, "stability": 0.7},
            }
            _sound_spec = derive_sound_spec(_sound_fs, mode=_ss.sound_mode)
            send_sound_spec(_sound_spec)
        except Exception:
            pass

        payload = {
            "entities": entities,
            "svara_weights": svara_weights,
            "raga": ss.get("raga", "Yaman"),
            "tala": ss.get("tala", "Adi"),
            "bpm": ss.get("bpm", 72),
            "yantra": yantra_out,
            "s0_activation": round(s0_activation, 3),
            "breath_rate": breath_rate,
            "observance": obs_list[0] if obs_list else None,
            "panchanga": _panchanga_dict,
            "vastu_state": _vastu,
            "ui_layout": _ui_layout,
            "sound_spec": _sound_spec,
        }
        return app.response_class(
            json.dumps(payload, default=_json_serial, ensure_ascii=False),
            mimetype="application/json",
        )

    # ── FLAT ROUTES — domain apps (April 2026 reorg) ──────────

    # ── KALA (time) ──
    @app.route("/kala/day/data")
    def _kala_day_data():
        """Today's full kala data — panchanga + agriculture + intention."""
        try:
            day = _day_agri()
            fs = field_state()
            p5 = fs.get("panchanga", {})
            hora = fs.get("hora", "")
            rk = fs.get("rahu_kala", "")
            yoga = fs.get("yoga", "")
            devi = p5.get("devi", {})
            devi_name = devi.get("name", "") if isinstance(devi, dict) else str(devi)
            day["hora"] = hora
            day["rahu_kala"] = rk
            day["yoga"] = yoga
            day["devi"] = devi_name
            day["element"] = p5.get("element", "")
            day["paksha"] = p5.get("paksha", "")
            day["guna"] = p5.get("guna", "")
            return jsonify(day)
        except Exception as exc:
            return jsonify({"error": str(exc)})

    @app.route("/kala/week/data")
    def _kala_week_data():
        """7-day kala forecast."""
        try:
            now = datetime.now()
            days = [_day_agri(now + timedelta(days=i)) for i in range(7)]
            return jsonify({"days": days, "ts": int(now.timestamp())})
        except Exception as exc:
            return jsonify({"error": str(exc)})

    @app.route("/kala/month/data")
    def _kala_month_data():
        """Full month kala data with per-day panchanga."""
        import calendar as _cal
        try:
            now = datetime.now()
            y, m = now.year, now.month
            num = _cal.monthrange(y, m)[1]
            days = [_day_agri(datetime(y, m, d, 12, 0)) for d in range(1, num + 1)]
            return jsonify({
                "month": m, "month_name": _cal.month_name[m],
                "year": y, "days": days,
                "ts": int(now.timestamp()),
            })
        except Exception as exc:
            return jsonify({"error": str(exc)})

    @app.route("/guild/generate", methods=["POST"])
    def _guild_generate():
        """Generate a permaculture guild from a base plant + region."""
        data = request.get_json(force=True)
        base_plant = data.get("plant", "")
        region = data.get("region", "florida_9b")
        intention = data.get("intention", "medicine")

        HARDINESS = {
            "florida_9b": ["9", "10", "11", "12"],
            "temperate": ["6", "7", "8"],
            "tropical": ["10", "11", "12"],
            "global": [],
        }
        zones = HARDINESS.get(region, [])

        def search_role(keyword, limit=6):
            if zones:
                zone_filter = " OR ".join(
                    f"hardiness LIKE '%{z}%'" for z in zones)
                sql = f"""SELECT latin_name, common_name, habit, height,
                                 hardiness, edibility_rating, medicinal_rating,
                                 summary, other_uses
                          FROM plants
                          WHERE ({zone_filter})
                          AND (other_uses LIKE ? OR cultivation_details LIKE ?)
                          AND medicinal_rating + edibility_rating > 0
                          ORDER BY medicinal_rating + edibility_rating DESC
                          LIMIT {limit}"""
                return _pfaf_query(sql, [f"%{keyword}%", f"%{keyword}%"])
            else:
                sql = f"""SELECT latin_name, common_name, habit, height,
                                 hardiness, edibility_rating, medicinal_rating,
                                 summary, other_uses
                          FROM plants
                          WHERE other_uses LIKE ?
                          LIMIT {limit}"""
                return _pfaf_query(sql, [f"%{keyword}%"])

        # Build guild rings
        guild = {
            "center": base_plant,
            "region": region,
            "intention": intention,
            "rings": {
                "nitrogen_fixers": search_role("nitrogen", 5),
                "dynamic_accumulators": search_role("accumulator", 5),
                "pest_repellents": search_role("repel", 5),
                "pollinators": search_role("pollinator", 5),
                "ground_covers": search_role("ground cover", 4),
                "medicinal": search_role("medicinal herb", 5)
                    if intention == "medicine" else [],
                "food": search_role("edible", 5)
                    if intention == "food" else [],
            },
        }

        # Add nakshatra timing from field
        fs = field_state()
        p = fs.get("panchanga", {})
        nak = p.get("nakshatra", "")
        agri = {}
        agri_path = os.path.join(_here, "datasets", "plants", "nakshatra_agriculture.csv")
        if os.path.isfile(agri_path):
            import csv as _csv
            import unicodedata as _ud
            import re as _re
            # Build lookup: strip all diacritics + normalize v/w for IAST→English
            _NAK_MAP = {
                "asvini": "Ashwini", "ashvini": "Ashwini",
                "bharani": "Bharani", "krittika": "Krittika",
                "rohini": "Rohini", "mrigashira": "Mrigashira", "mrigashirsha": "Mrigashira",
                "ardra": "Ardra", "punarvasu": "Punarvasu", "pushya": "Pushya",
                "ashlesha": "Ashlesha", "magha": "Magha",
                "purva phalguni": "Purva Phalguni", "purvaphalguni": "Purva Phalguni",
                "uttara phalguni": "Uttara Phalguni", "uttaraphalguni": "Uttara Phalguni",
                "hasta": "Hasta", "chitra": "Chitra", "swati": "Swati", "svati": "Swati",
                "vishakha": "Vishakha", "visakha": "Vishakha",
                "anuradha": "Anuradha", "jyeshtha": "Jyeshtha", "jyestha": "Jyeshtha",
                "mula": "Mula", "moola": "Mula",
                "purva ashadha": "Purva Ashadha", "purvashadha": "Purva Ashadha",
                "uttara ashadha": "Uttara Ashadha", "uttarashadha": "Uttara Ashadha",
                "shravana": "Shravana", "shravana": "Shravana",
                "dhanishta": "Dhanishta", "dhanistha": "Dhanishta",
                "shatabhisha": "Shatabhisha", "shatabhishak": "Shatabhisha",
                "purva bhadrapada": "Purva Bhadrapada", "purvabhadrapada": "Purva Bhadrapada",
                "uttara bhadrapada": "Uttara Bhadrapada", "uttarabhadrapada": "Uttara Bhadrapada",
                "revati": "Revati",
            }
            def _nak_ascii(s):
                n = s.lower().strip()
                n = n.replace("ś", "sh").replace("ṣ", "sh").replace("ṛ", "ri")
                n = _ud.normalize("NFD", n)
                n = "".join(c for c in n if _ud.category(c) != "Mn")
                return _re.sub(r"[^a-z ]", "", n).strip()
            nak_ascii = _nak_ascii(nak)
            nak_csv = _NAK_MAP.get(nak_ascii, _NAK_MAP.get(nak_ascii.replace(" ", ""), ""))
            agri_rows = {}
            with open(agri_path) as _f:
                for row in _csv.DictReader(_f):
                    agri_rows[row.get("nakshatra", "").strip()] = row
            if nak_csv and nak_csv in agri_rows:
                agri = agri_rows[nak_csv]
            else:
                # Fallback: substring match
                for csv_name, row in agri_rows.items():
                    if _nak_ascii(csv_name)[:4] == nak_ascii[:4]:
                        agri = row
                        break

        guild["timing"] = {
            "nakshatra": nak,
            "activity": agri.get("activity", ""),
            "avoid": agri.get("avoid", ""),
            "quality": agri.get("quality", ""),
            "moon_phase": p.get("paksha", ""),
        }

        return app.response_class(
            json.dumps(guild, default=_json_serial, ensure_ascii=False),
            mimetype="application/json",
        )

    @app.route("/guild/search")
    def _guild_search():
        """Search PFAF by name, use, or property."""
        q = request.args.get("q", "")
        zone = request.args.get("zone", "")
        limit = min(int(request.args.get("limit", 12)), 50)

        if zone:
            sql = """SELECT latin_name, common_name, habit, height,
                            hardiness, edibility_rating, medicinal_rating, summary
                     FROM plants
                     WHERE (latin_name LIKE ? OR common_name LIKE ?
                            OR summary LIKE ? OR other_uses LIKE ?)
                     AND hardiness LIKE ?
                     ORDER BY edibility_rating + medicinal_rating DESC
                     LIMIT ?"""
            results = _pfaf_query(sql, [f"%{q}%"] * 4 + [f"%{zone}%", limit])
        else:
            sql = """SELECT latin_name, common_name, habit, height,
                            hardiness, edibility_rating, medicinal_rating, summary
                     FROM plants
                     WHERE latin_name LIKE ? OR common_name LIKE ?
                            OR summary LIKE ? OR other_uses LIKE ?
                     ORDER BY edibility_rating + medicinal_rating DESC
                     LIMIT ?"""
            results = _pfaf_query(sql, [f"%{q}%"] * 4 + [limit])

        return app.response_class(
            json.dumps(results, default=_json_serial, ensure_ascii=False),
            mimetype="application/json",
        )

        return {'tithi': tithi, 'devi': fs['panchanga']['tithi_deity'], 'geometry': 'mandala'}

    # ── yantra-data → render_bp (registered above) ────────

    @app.route("/music/<int:tithi>")
    def _music(tithi):
        """Field-derived music spec for a tithi — raga, tala, gamaka, bhava."""
        fs = field_state()
        ss = _derive_sound_state(fs)
        p5 = fs.get("panchanga", {})
        raga_def = fs.get("devi_raga_def") or {}

        # Natal musician reading if natal chart available
        musician = {}
        try:
            from npu_engine.natal_musician import derive_musician_reading
            natal = NATAL
            if natal:
                spine = {"panchanga": p5, "sound_state": ss, "entities": fs.get("entities", [])}
                musician = derive_musician_reading(natal, spine)
        except Exception:
            pass

        # Bhava from guna
        guna = p5.get("guna", "sattva").lower()
        bhava_map = {
            "sattva": "shanta", "rajas": "vira", "tamas": "karuna",
        }

        # Gamaka style from element
        element = p5.get("element", "ether").lower()
        gamaka_map = {
            "fire": "kampita", "water": "andolan", "earth": "meend",
            "air": "murki", "ether": "sparsha",
        }

        result = {
            "tithi": tithi,
            "raga": fs.get("devi_raga", "Yaman"),
            "raga_notes": ss.get("raga_notes", []),
            "vadi": ss.get("raga_vadi", ""),
            "samvadi": ss.get("raga_samvadi", ""),
            "tala": ss.get("tala", "Adi"),
            "tala_beats": ss.get("tala_beats", 8),
            "bpm": ss.get("bpm", 72),
            "gamaka": gamaka_map.get(element, "sparsha"),
            "bhava": bhava_map.get(guna, "shanta"),
            "rasa": ss.get("rasa", "shanta"),
            "element": element,
            "guna": guna,
            "sa_hz": ss.get("element_freq", 261.63),
            "arc_phase": ss.get("arc_phase", 0.5),
            "gati": ss.get("gati", "chatusra"),
        }
        if musician:
            result["musician"] = {
                "primary_raga": musician.get("primary_raga", ""),
                "secondary_raga": musician.get("secondary_raga", ""),
                "raga_blend": musician.get("raga_blend", 0.0),
                "gamak_emphasis": musician.get("gamak_emphasis", []),
                "tempo_feel": musician.get("tempo_feel", ""),
                "phrase_arc": musician.get("phrase_arc", ""),
                "field_tensions": musician.get("field_tensions", [])[:3],
                "musician_note": musician.get("musician_note", ""),
            }
        return jsonify(result)

    @app.route("/practice/<int:tithi>")
    def _practice(tithi):
        """Field-derived practice spec — asana, pranayama, marma, dinacharya."""
        import csv as _pcsv
        fs = field_state()
        p5 = fs.get("panchanga", {})
        element = p5.get("element", "ether").lower()
        guna = p5.get("guna", "sattva").lower()
        nakshatra = p5.get("nakshatra", "")

        # ── Dinacharya from time of day ──
        dinacharya = {}
        try:
            now_h = __import__("datetime").datetime.now().hour
            dina_path = Path(_here) / "datasets" / "ayurveda" / "dinacharya_panchanga.csv"
            if dina_path.exists():
                with open(dina_path, newline="", encoding="utf-8") as f:
                    rows = list(_pcsv.DictReader(f))
                # Map hour ranges to muhurta windows
                muhurta_hours = [
                    (0, 5, 0),    # Brahma Muhurta
                    (5, 7, 1),    # Sunrise Sandhya
                    (7, 10, 2),   # Morning Kapha
                    (10, 14, 3),  # Midday Pitta
                    (14, 17, 4),  # Afternoon Vata
                    (17, 19, 5),  # Evening Sandhya
                    (19, 22, 6),  # Night Kapha
                    (22, 24, 7),  # Late Night
                ]
                row_idx = 0
                for start, end, idx in muhurta_hours:
                    if start <= now_h < end and idx < len(rows):
                        row_idx = idx
                        break
                if row_idx < len(rows):
                    r = rows[row_idx]
                    dinacharya = {
                        "muhurta": r.get("muhurta_name", ""),
                        "quality": r.get("quality", ""),
                        "practices": r.get("recommended_practices", ""),
                        "herbs": r.get("recommended_herbs", ""),
                        "diet": r.get("dietary_guidance", ""),
                        "dosha_active": r.get("dosha_active", ""),
                        "tithi_note": r.get("tithi_influence", ""),
                        "attestation": r.get("attestation_status", ""),
                    }
        except Exception:
            pass

        # ── Marma from body region ──
        marma = {}
        body_region = ""
        try:
            # Get body region from S5 layer
            ss = fs.get("sound_state", {})
            # Nakshatra -> body region from existing data
            nak_body_path = Path(_here) / "datasets" / "marma" / "body_region_marma.csv"
            if nak_body_path.exists():
                with open(nak_body_path, newline="", encoding="utf-8") as f:
                    for row in _pcsv.DictReader(f):
                        # Match by element affinity
                        if not body_region:
                            body_region = row.get("body_region", "")
                        # Look for element match
                        region_el = row.get("body_region", "").lower()

            # Load marma details from marma_field.csv
            marma_path = Path(_here) / "datasets" / "marma" / "marma_field.csv"
            if marma_path.exists():
                with open(marma_path, newline="", encoding="utf-8") as f:
                    matches = []
                    for row in _pcsv.DictReader(f):
                        # Match by element
                        if row.get("element", "").lower() == element:
                            matches.append(row)
                        elif row.get("dosha", "").lower().startswith(
                                {"fire": "pitta", "water": "kapha", "earth": "kapha",
                                 "air": "vata", "ether": "vata"}.get(element, "")):
                            matches.append(row)
                    if matches:
                        m = matches[0]
                        marma = {
                            "name": m.get("name_iast", ""),
                            "body_region": m.get("body_region", ""),
                            "element": m.get("element", ""),
                            "dosha": m.get("dosha", ""),
                            "chakra": m.get("chakra_nearest", ""),
                            "raga_therapeutic": m.get("raga_therapeutic", ""),
                            "herb_primary": m.get("herb_primary", ""),
                            "herb_secondary": m.get("herb_secondary", ""),
                            "treatment": m.get("treatment_approach", ""),
                        }
                        body_region = m.get("body_region", body_region)
        except Exception:
            pass

        # ── Asana from element + guna ──
        asana_map = {
            ("fire", "rajas"):   "Sūrya Namaskāra",
            ("fire", "sattva"):  "Vīrabhadrāsana I",
            ("fire", "tamas"):   "Śalabhāsana",
            ("water", "rajas"):  "Nāvāsana",
            ("water", "sattva"): "Matsyāsana",
            ("water", "tamas"):  "Bālāsana",
            ("earth", "rajas"):  "Vīrabhadrāsana II",
            ("earth", "sattva"): "Vṛkṣāsana",
            ("earth", "tamas"):  "Supta Baddha Koṇāsana",
            ("air", "rajas"):    "Pārśvakoṇāsana",
            ("air", "sattva"):   "Ardha Candrāsana",
            ("air", "tamas"):    "Paścimottānāsana",
            ("ether", "rajas"):  "Śīrṣāsana",
            ("ether", "sattva"): "Padmāsana",
            ("ether", "tamas"):  "Śavāsana",
        }
        pranayama_map = {
            "fire": "Śītalī", "water": "Ujjāyī", "earth": "Bhastrikā",
            "air": "Nāḍī Śodhana", "ether": "Bhrāmarī",
        }
        mudra_map = {
            "fire": "Agni Mudrā", "water": "Varuṇa Mudrā", "earth": "Pṛthivī Mudrā",
            "air": "Vāyu Mudrā", "ether": "Ākāśa Mudrā",
        }
        dosha_map = {
            "fire": "Pitta", "water": "Kapha", "earth": "Kapha",
            "air": "Vāta", "ether": "Vāta",
        }

        result = {
            "tithi": tithi,
            "nakshatra": nakshatra,
            "element": element,
            "guna": guna,
            "asana": asana_map.get((element, guna), "Tāḍāsana"),
            "pranayama": pranayama_map.get(element, "Ujjāyī"),
            "mudra": mudra_map.get(element, "Jñāna Mudrā"),
            "dosha_balance": dosha_map.get(element, "Tridosha"),
            "body_region": body_region,
        }
        if marma:
            result["marma"] = marma
        if dinacharya:
            result["dinacharya"] = dinacharya
        return jsonify(result)

    # ── AGRICULTURE ENDPOINTS ────────────────────────────────
    _NAK_AGRI = {}
    try:
        import csv as _csv
        _ag_path = Path(_here, "datasets", "plants", "nakshatra_agriculture.csv")
        with open(_ag_path, newline="", encoding="utf-8") as _af:
            for _row in _csv.DictReader(_af):
                _NAK_AGRI[_row.get("nakshatra", "").strip()] = {
                    "quality": _row.get("quality", ""),
                    "activity": _row.get("activity", ""),
                    "avoid": _row.get("avoid", ""),
                    "crops": _row.get("crops", ""),
                    "notes": _row.get("notes", ""),
                }
    except Exception:
        pass

    def _tithi_quality(tidx):
        if tidx == 29: return "rest"
        if tidx == 14: return "harvest"
        didx = tidx % 15
        if didx in (0,1,2,4,6,9,10,12): return "favorable"
        if didx in (3,8,13): return "rikta"
        if didx in (5,7,11): return "mixed"
        return "favorable"

    def _moon_guidance(paksha, tidx):
        if tidx == 14: return "full moon · harvest · maximum potency in plants"
        if tidx == 29: return "new moon · rest · compost · soil preparation"
        if paksha == "Śukla": return "waxing · above-ground crops · sap rising · leafy vegetables, fruits, flowers"
        return "waning · below-ground crops · root activity · root vegetables, garlic, onions, tubers"

    def _seasonal_crops_fl(month):
        if month in (12,1,2): return ["lettuce","kale","broccoli","carrots","beets","celery","spinach"]
        if month in (3,4,5): return ["tomatoes","peppers","basil","herbs","beans","eggplant","squash"]
        if month in (6,7,8): return ["sweet potato","okra","rosemary","Thai basil","southern peas","yard-long beans"]
        return ["cucumbers","squash","root crops","lettuces","kale","broccoli"]

    def _day_agri(now=None):
        if now is None: now = datetime.now()
        p5 = calc_panchanga(now)
        nak_name = p5["nakshatra"]
        tidx = p5["tidx"]
        paksha = p5["paksha"]
        # CSV uses ITRANS names, kernel returns IAST — use module-level map
        nak_key = nak_to_itrans(nak_name)
        nak_info = _NAK_AGRI.get(nak_key, {})
        tq = _tithi_quality(tidx)
        moon = _moon_guidance(paksha, tidx)
        seasonal = _seasonal_crops_fl(now.month)
        activity = nak_info.get("activity", "general maintenance")
        avoid = nak_info.get("avoid", "")
        crops = nak_info.get("crops", "")
        return {
            "date": now.strftime("%Y-%m-%d"),
            "weekday": now.strftime("%A"),
            "vara": p5["vara"],
            "nakshatra": nak_name,
            "nak_quality": nak_info.get("quality", "unknown"),
            "activity": activity,
            "avoid": avoid,
            "crops": crops,
            "tithi": p5["tithi"],
            "tidx": tidx,
            "tithi_quality": tq,
            "paksha": paksha,
            "moon_phase": moon,
            "seasonal_crops": seasonal,
            "notes": nak_info.get("notes", ""),
            "full_guidance": f"{nak_name} · {p5['tithi']} · {paksha} · {activity}",
        }

    @app.route("/agriculture/today")
    def _agri_today():
        now = datetime.now()
        today = _day_agri(now)
        tomorrow = _day_agri(now + timedelta(days=1))
        week = []
        for i in range(7):
            d = _day_agri(now + timedelta(days=i))
            has_plant = "plant" in d["activity"].lower() or "all" in d["activity"].lower()
            d["_s"] = (2 if d["tithi_quality"]=="favorable" else 1 if d["tithi_quality"] in ("harvest","mixed") else 0) + (2 if has_plant and not d["avoid"] else 0)
            week.append(d)
        best = sorted(week, key=lambda x: x["_s"], reverse=True)[:3]
        for d in week+best: d.pop("_s", None)
        return app.response_class(
            json.dumps({"today": today, "tomorrow_preview": tomorrow, "week_best_days": best, "ts": int(datetime.now().timestamp())},
                       default=_json_serial, ensure_ascii=False),
            mimetype="application/json")

    @app.route("/agriculture/week")
    def _agri_week():
        now = datetime.now()
        days = [_day_agri(now + timedelta(days=i)) for i in range(7)]
        return app.response_class(
            json.dumps({"days": days, "ts": int(datetime.now().timestamp())}, default=_json_serial, ensure_ascii=False),
            mimetype="application/json")

    @app.route("/agriculture/month")
    def _agri_month():
        import calendar as _cal
        now = datetime.now()
        y, m = now.year, now.month
        num = _cal.monthrange(y, m)[1]
        days = [_day_agri(datetime(y, m, d, 12, 0)) for d in range(1, num+1)]
        return app.response_class(
            json.dumps({"month": m, "month_name": _cal.month_name[m], "year": y, "days": days, "ts": int(datetime.now().timestamp())},
                       default=_json_serial, ensure_ascii=False),
            mimetype="application/json")

    @app.route("/generated/card_spread")
    def _card_spread():
        gen = _ensure_generated()
        spread = gen.get("card_spread")
        if not spread:
            fs = field_state()
            p = fs.get("panchanga", {})
            nd = p.get("nak_data", {}) or {}
            itrans = nd.get("name_key", "ashwini")
            spread = gen._gen_card_spread(f"nakshatra_{itrans.lower()}", fs)
        return app.response_class(json.dumps(spread, default=_json_serial, ensure_ascii=False), mimetype="application/json")

    @app.route("/generated/mandala")
    def _gen_mandala():
        gen = _ensure_generated()
        mandala = gen.get("mandala_layout")
        if not mandala:
            fs = field_state()
            nd = fs.get("panchanga", {}).get("nak_data", {}) or {}
            itrans = nd.get("name_key", "ashwini")
            mandala = gen._gen_mandala(f"nakshatra_{itrans.lower()}", fs)
        return app.response_class(json.dumps(mandala, default=_json_serial, ensure_ascii=False), mimetype="application/json")

    @app.route("/generated/tala")
    def _gen_tala():
        gen = _ensure_generated()
        tala = gen.get("tala_pattern")
        if not tala:
            tala = gen._gen_tala(field_state())
        return app.response_class(json.dumps(tala, default=_json_serial, ensure_ascii=False), mimetype="application/json")

    @app.route("/generated/<key>")
    def _get_generated(key):
        gen = _ensure_generated()
        content = gen.get(key)
        if content:
            if isinstance(content, (dict, list)):
                return app.response_class(json.dumps(content, default=_json_serial, ensure_ascii=False), mimetype="application/json")
            return app.response_class(str(content), mimetype="text/plain")
        # Fallback to disk
        for ext in (".md", ".json"):
            gpath = Path(_here, "generated", f"{key}{ext}")
            if gpath.exists():
                text = gpath.read_text(encoding="utf-8")
                if ext == ".json":
                    return app.response_class(text, mimetype="application/json")
                return app.response_class(text, mimetype="text/plain")
        return "not generated yet", 404

    @app.route("/generated/save", methods=["POST"])
    def _save_generated():
        data = request.get_json(force=True)
        key = data.get("key", "")
        content = data.get("content", "")
        if key and content:
            gdir = Path(_here, "generated")
            gdir.mkdir(exist_ok=True)
            (gdir / f"{key}.md").write_text(content, encoding="utf-8")
        return app.response_class(json.dumps({"saved": True}), mimetype="application/json")

    @app.route("/generated/list")
    def _list_generated():
        gen = _ensure_generated()
        keys = gen.all_keys()
        gdir = Path(_here, "generated")
        disk = sorted(p.stem for p in gdir.glob("*.*")) if gdir.exists() else []
        return app.response_class(json.dumps({"keys": keys, "files": disk}), mimetype="application/json")

    @app.route("/docs-list")
    def _docs_list():
        wiki_dir = Path(_here, "wiki")
        if not wiki_dir.exists():
            wiki_dir = Path(_here, "docs", "docs", "wiki")  # fallback
        files = sorted(p.name for p in wiki_dir.glob("*.md"))
        return jsonify({"files": files})

    @app.route("/docs/<path:filename>")
    def _docs(filename):
        wiki_dir = Path(_here, "wiki")
        if not wiki_dir.exists():
            wiki_dir = Path(_here, "docs", "docs", "wiki")  # fallback
        docs_file = wiki_dir / filename
        if docs_file.exists() and docs_file.suffix == ".md":
            return app.response_class(docs_file.read_text(encoding="utf-8"), mimetype="text/markdown")
        return "Not found", 404

    # ── yantra/deposit, yantra/field → render_bp (registered above) ────────

    # ── Shared attribute query endpoints ──────────────────────────────
    def _deity_attr_search(filter_fn):
        """Search deity_attributes for rows matching a filter."""
        from npu_engine.datasets import load_entity_metadata
        meta = load_entity_metadata()
        matches = []
        for eid, m in meta.items():
            if m.get("category") != "deity_attr":
                continue
            a = m.get("attributes", {})
            if filter_fn(a):
                matches.append({
                    "deity_id": eid,
                    "nakshatra": (a.get("nakshatra", [""]))[0],
                    "deity": (a.get("deity", [""]))[0],
                })
        return matches

    @app.route("/item/<item_name>")
    def _item_query(item_name):
        matches = _deity_attr_search(lambda a: any(
            item_name in (a.get(f"item_{i}", [""]))[0]
            for i in range(1, 5)
        ))
        return jsonify({"item": item_name, "matches": matches, "count": len(matches)})

    @app.route("/vahana/<vahana>")
    def _vahana_query(vahana):
        matches = _deity_attr_search(lambda a: vahana == (a.get("vahana", [""]))[0])
        return jsonify({"vahana": vahana, "matches": matches, "count": len(matches)})

    @app.route("/gemstone/<gem>")
    def _gemstone_query(gem):
        matches = _deity_attr_search(lambda a: gem == (a.get("gemstone", [""]))[0])
        return jsonify({"gemstone": gem, "matches": matches, "count": len(matches)})

    # ── Standalone HTML apps (session 3) ──────────────────────────────
    @app.route("/treasury")
    def _treasury():
        """GET /treasury?prahar=sayahna&limit=5

        Field-matched content from the living canon.
        """
        from npu_engine.treasury import resolve_treasury
        prahar = request.args.get("prahar", "")
        limit = int(request.args.get("limit", "5"))
        try:
            fs = field_state()
            result = resolve_treasury(fs, prahar=prahar or None, limit=limit)
        except Exception as exc:
            result = {"error": str(exc)}
        return app.response_class(
            json.dumps(result, default=_json_serial, ensure_ascii=False),
            mimetype="application/json")

    @app.route("/wheel/options")
    def _wheel_options():
        """Entity wheel — radial options for any entity."""
        entity_id = request.args.get("entity", "")
        if not entity_id:
            return app.response_class(json.dumps({"options": []}), mimetype="application/json")
        try:
            from npu_engine.graph_engine import GraphEngine
            g = GraphEngine()
            neighbors = g.get_neighbors(entity_id, exclude_inverse=False)
            etype = entity_id.split("_")[0] if "_" in entity_id else "entity"

            # Build relation type set
            rel_types = set(e.get("relation", "") for e in neighbors)

            options = [
                {"symbol": "\u25C9", "label": "Observe", "action": "observe",
                 "angle": 90, "target": entity_id, "color": "#ffffff"},
                {"symbol": "\U0001F4DC", "label": "Literary", "action": "literary",
                 "angle": 0, "target": entity_id, "color": "#c8d8f0"},
            ]

            if any("yantra" in r or "triangle" in r for r in rel_types) or etype in ("nakshatra", "devi", "deity"):
                tri_id = ""
                for e in neighbors:
                    if "yantra" in e.get("relation", "") or "triangle" in e.get("to_id", ""):
                        tri_id = e["to_id"]
                        break
                options.append({"symbol": "\u25B3", "label": "Yantra", "action": "yantra",
                                "angle": 315, "target": tri_id or entity_id, "color": "#aa77dd"})

            if any("raga" in r for r in rel_types) or etype in ("nakshatra", "devi", "dosha"):
                raga_id = ""
                for e in neighbors:
                    if "raga" in e.get("relation", ""):
                        raga_id = e["to_id"]
                        break
                options.append({"symbol": "\u266A", "label": "Sound", "action": "sound",
                                "angle": 45, "target": raga_id or entity_id, "color": "#5cb87a"})

            if any("plant" in r for r in rel_types) or etype == "nakshatra":
                plant_id = ""
                for e in neighbors:
                    if "plant" in e.get("relation", ""):
                        plant_id = e["to_id"]
                        break
                options.append({"symbol": "\u274B", "label": "Plant", "action": "plant",
                                "angle": 225, "target": plant_id or entity_id, "color": "#5cb87a"})

            if any("weapon" in r for r in rel_types):
                options.append({"symbol": "\u2694", "label": "Weapons", "action": "weapons",
                                "angle": 180, "target": entity_id, "color": "#d44040"})

            layer_map = {"nakshatra": "S3", "devi": "S1", "deity": "S1", "raga": "S2",
                         "tala": "S3", "plant": "S5", "body": "S5", "graha": "S3", "dosha": "S5"}
            layer = layer_map.get(etype, "S0")
            options.append({"symbol": "\u2726", "label": f"Enter {layer}", "action": f"layer_{layer}",
                            "angle": 270, "target": layer, "color": "#f0c040"})

            return app.response_class(
                json.dumps({"entity_id": entity_id, "entity_type": etype, "options": options},
                           ensure_ascii=False),
                mimetype="application/json")
        except Exception as exc:
            return app.response_class(
                json.dumps({"error": str(exc), "options": []}, ensure_ascii=False),
                mimetype="application/json")

    @app.route("/wheel")
    def _wheel():
        return send_file(os.path.join(_here, "nakshatra_wheel.html"))

    # /yantra route is defined at line ~4711 (yantra geometry JSON).
    # Yantra HTML is served via /apps/yantra/ route.

    # calendar/ moved to ~/arc-atlas/ — absorbed into kala

    @app.route("/intention/classify", methods=["POST"])
    def _intention_classify():
        from npu_engine.field.intention_engine import classify_intention
        data = request.get_json(force=True, silent=True) or {}
        text = data.get("text", "")
        result = classify_intention(text)
        return jsonify(result)

    @app.route("/intention/windows", methods=["POST"])
    def _intention_windows():
        from npu_engine.field.intention_engine import derive_windows
        data = request.get_json(force=True, silent=True) or {}
        intention_id = data.get("intention_id", "")
        days = min(int(data.get("days", 7)), 30)
        fs = field_state()
        result = derive_windows(intention_id, fs, days=days)
        return jsonify(result)

    @app.route("/intention/now")
    def _intention_now():
        from npu_engine.field.intention_engine import score_moment
        intention_id = request.args.get("intention_id", "")
        fs = field_state()
        score = score_moment(intention_id, fs)
        return jsonify({"intention_id": intention_id, "score": score})

    @app.route("/calendar/day")
    def _calendar_day():
        fs = field_state()
        p5 = fs.get("panchanga", {})
        mu = fs.get("muhurta", {})
        hora = fs.get("hora", {})
        rahu = fs.get("rahu_kala", {})
        yoga = fs.get("yoga", {})
        karana = fs.get("karana", {})

        now = p5.get("now", datetime.now())
        sunrise_min = 360  # 6:00 AM
        _MUHURTA_NAMES = [
            "Rudra", "Ahi", "Mitra", "Pitri", "Vasu",
            "Vara", "Vishvedeva", "Vidhi", "Satamukhi", "Puruhuta",
            "Vahini", "Naktanakara", "Varuna", "Aryaman", "Bhaga",
            "Girisha", "Ajapada", "Ahir Budhnya", "Pushan", "Ashvini",
            "Yama", "Agni", "Vidhata", "Chanda", "Aditi",
            "Jiva", "Vishnu", "Yumigadyuti", "Brahma", "Samudram",
        ]

        rahu_start = rahu.get("rahu_kala_start", "")
        rahu_end = rahu.get("rahu_kala_end", "")
        def _parse_hm(s):
            try:
                parts = s.split(":")
                return int(parts[0]) * 60 + int(parts[1])
            except Exception:
                return -1
        rahu_s = _parse_hm(rahu_start)
        rahu_e = _parse_hm(rahu_end)

        windows = []
        # Brahma Muhurta
        windows.append({
            "muhurta_name": "Brahma Muhurta",
            "start_min": 264, "end_min": 312,
            "quality": "excellent",
        })

        for i in range(30):
            m_start = sunrise_min + i * 48
            m_end = m_start + 48
            name = _MUHURTA_NAMES[i] if i < 30 else f"Muhurta_{i+1}"
            if 726 <= m_start < 774:
                name = "Abhijit"
                quality = "excellent"
            elif rahu_s > 0 and rahu_s <= m_start + 24 < rahu_e:
                quality = "avoid"
            else:
                quality = "neutral"
            windows.append({
                "muhurta_name": name,
                "start_min": m_start,
                "end_min": m_end,
                "quality": quality,
            })

        return jsonify({
            "panchanga": {
                "tithi": p5.get("tithi", ""),
                "tidx": p5.get("tidx", 0),
                "paksha": p5.get("paksha", ""),
                "nakshatra": p5.get("nakshatra", ""),
                "vara": p5.get("vara", ""),
            },
            "tithi_deity": p5.get("tithi_deity", ""),
            "muhurta": mu,
            "hora": hora,
            "rahu_kala": rahu,
            "yoga": yoga,
            "karana": karana,
            "windows": windows,
        })

    @app.route("/journal", methods=["GET"])
    def _journal_list():
        journal_dir = os.path.join(_here, "instance", "journal")
        os.makedirs(journal_dir, exist_ok=True)
        search = request.args.get("search", "").lower()
        entries = []
        for fname in sorted(os.listdir(journal_dir), reverse=True):
            if not fname.endswith(".json"):
                continue
            try:
                with open(os.path.join(journal_dir, fname), "r") as f:
                    day_entries = json.load(f)
                if isinstance(day_entries, list):
                    for e in day_entries:
                        if search:
                            blob = json.dumps(e).lower()
                            if search not in blob:
                                continue
                        entries.append(e)
            except Exception:
                continue
        return jsonify({"entries": entries[:100]})

    @app.route("/journal", methods=["POST"])
    def _journal_save():
        journal_dir = os.path.join(_here, "instance", "journal")
        os.makedirs(journal_dir, exist_ok=True)

        data = request.get_json(force=True, silent=True) or {}
        text = data.get("text", "").strip()
        if not text:
            return jsonify({"error": "empty text"}), 400

        now = datetime.now()
        fs = field_state()
        # Sanitize field_state for JSON (remove datetime objects)
        fs_clean = {}
        for k, v in fs.items():
            if k == "panchanga":
                p5c = {pk: pv for pk, pv in v.items() if pk != "now"}
                fs_clean[k] = p5c
            elif k in ("muhurta", "hora", "rahu_kala", "yoga", "karana", "dasha"):
                fs_clean[k] = v

        entry = {
            "text": text,
            "datetime": now.isoformat(),
            "field_state": fs_clean,
        }

        day_file = os.path.join(journal_dir, now.strftime("%Y-%m-%d") + ".json")
        existing = []
        if os.path.exists(day_file):
            try:
                with open(day_file, "r") as f:
                    existing = json.load(f)
            except Exception:
                existing = []

        existing.append(entry)
        with open(day_file, "w") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)

        return jsonify({"ok": True, "entry": entry})

    # ── System self-model routes ──────────────────────────

    # ── system/state, system/audio → system_bp (registered above) ────────

    @app.route("/svarodaya")
    def _svarodaya():
        from npu_engine.field.svarodaya_engine import derive_svarodaya
        fs = field_state()
        return jsonify(derive_svarodaya(fs))

    @app.route("/dinacharya")
    def _dinacharya():
        from npu_engine.field.dinacharya_engine import derive_dinacharya
        fs = field_state()
        return jsonify(derive_dinacharya(fs))

    @app.route("/chandas")
    def _chandas():
        from npu_engine.field.chandas_engine import derive_chandas
        fs = field_state()
        return jsonify(derive_chandas(fs))

    @app.route("/astrobotany")
    def _astrobotany():
        from npu_engine.field.astrobotany_engine import derive_astrobotany
        fs = field_state()
        return jsonify(derive_astrobotany(fs))

    @app.route("/trajectory")
    def _trajectory():
        from npu_engine.field.trajectory_engine import derive_trajectory
        fs = field_state()
        return jsonify(derive_trajectory(fs))

    # ── Reading engine routes ─────────────────────────────

    # ── reading/* → reading_bp (registered above) ─────────────────────────────

    # ── Goloka engine route ───────────────────────────────

    @app.route("/goloka")
    def _goloka():
        from npu_engine.field.goloka_engine import derive_goloka_state
        return jsonify(derive_goloka_state(field_state()))

    # ── render/bandhu, render/species, render/shrine → render_bp (registered above) ────────

    # ── Symbol/glyph/ring routes → symbols_bp ─────────────────────────────
    from npu_engine.routes.symbols_bp import symbols_bp
    app.register_blueprint(symbols_bp)

    # ── Game character routes ─────────────────────────────

    @app.route("/character")
    def _character():
        from npu_engine.game.character_engine import derive_character_state
        return jsonify(derive_character_state(field_state=field_state()))

    @app.route("/character/lineages")
    def _character_lineages():
        from npu_engine.game.lineage_engine import calculate_accessible_lineages
        natal_path = Path(_here) / "instance" / "personal" / "natal.json"
        natal = json.loads(natal_path.read_text()) if natal_path.exists() else {}
        return jsonify(calculate_accessible_lineages(natal))

    @app.route("/character/orientation")
    def _character_orientation():
        from npu_engine.game.orientation_engine import derive_sura_asura
        return jsonify(derive_sura_asura(field_state()))

    @app.route("/guild/state")
    def _guild_state():
        from npu_engine.engines.guild_engine import derive_guild
        return jsonify(derive_guild(field_state()))

    @app.route("/guild/timing")
    def _guild_timing():
        from npu_engine.engines.guild_engine import derive_guild_timing
        return jsonify(derive_guild_timing(field_state()))

    @app.route("/guild/plan")
    def _guild_plan():
        from npu_engine.field.guild_planner import plan_guild
        anchor = request.args.get("anchor", "")
        size = request.args.get("size", "medium")
        dosha = request.args.get("dosha", None)
        return jsonify(plan_guild(anchor, field_state(), plot_size=size, dosha_target=dosha))

    @app.route("/guild/plan/current")
    def _guild_plan_current():
        from npu_engine.field.guild_planner import plan_guild
        fs = field_state()
        size = request.args.get("size", "medium")
        return jsonify(plan_guild("", fs, plot_size=size))


    # ── Land routes → plants_bp (RTE-005) ────────────────
    # (land, land/plot, land/layout, land/mandala, land/mandala/recommend
    #  and all mandala/PFAF helpers moved to plants_bp)

    # ── HEXD helpers (imported from plants_bp) ──────────
    from npu_engine.routes.plants_bp import (
        _mandala_slug, _pfaf_row_to_plant_input, _hexd_site_context,
        _lookup_pfaf_row, _serialize_weighted_candidate,
        _build_hexd_plant_payload, _build_hexd_patch_payload,
        _build_land_mandala_recommendation, _mandala_patch_class_from_type,
    )

    @app.route("/hexd/object")
    def _hexd_object_payload():
        object_type = request.args.get("object_type", "").strip()
        object_id = request.args.get("object_id", "").strip()
        label = request.args.get("label", "").strip()
        session_controls = {
            "situation": request.args.get("situation", "").strip() or "generate_medicinal_patch",
            "resolution_profile": request.args.get("resolution_profile", "").strip() or "medicinal_weighted",
            "policy_mode": request.args.get("policy_mode", "").strip() or "default",
        }
        if not object_type or not object_id:
            return jsonify({"error": "object_type and object_id are required"}), 400
        if object_type == "plant_recommendation":
            return jsonify(_build_hexd_plant_payload(object_id, label, session_controls))
        if object_type == "patch":
            return jsonify(_build_hexd_patch_payload(object_id, label, session_controls))
        return jsonify({
            "payload_kind": "unsupported",
            "object_ref": {"object_type": object_type, "object_id": object_id, "label": label},
            "summary": {"primary_reason": "No object-specific analytical payload is available yet."},
            "claims": [],
        })

    # ── Corpus/research routes → corpus_bp ─────────────────────────────
    from npu_engine.routes.corpus_bp import corpus_bp
    app.register_blueprint(corpus_bp)

    # ── corpus/read, corpus/search → corpus_bp (registered above) ────────

    # ── Site terrain intelligence ──────────────────────────

    @app.route("/site/state")
    def _site_state():
        try:
            lat = float(request.args.get("lat", 0))
            lon = float(request.args.get("lon", 0))
            radius_m = float(request.args.get("radius_m", 100))
            house_lat = request.args.get("house_lat")
            house_lon = request.args.get("house_lon")
            if house_lat:
                house_lat = float(house_lat)
            if house_lon:
                house_lon = float(house_lon)
            from npu_engine.field.site_engine import derive_site_state
            fs = field_state()
            return jsonify(derive_site_state(lat, lon, radius_m,
                                             house_lat=house_lat, house_lon=house_lon,
                                             field_state=fs))
        except Exception as e:
            return jsonify({"error": str(e), "terrain": {}, "suitability": {}})

    @app.route("/site/swales")
    def _site_swales():
        try:
            lat = float(request.args.get("lat", 0))
            lon = float(request.args.get("lon", 0))
            radius_m = float(request.args.get("radius_m", 100))
            from npu_engine.field.site_engine import derive_site_state
            r = derive_site_state(lat, lon, radius_m)
            return jsonify({
                "swale_candidates": r["hydrology"]["swale_candidates"],
                "pond_candidates": r["hydrology"]["pond_candidates"],
            })
        except Exception as e:
            return jsonify({"error": str(e)})

    @app.route("/site/suitability")
    def _site_suitability():
        try:
            lat = float(request.args.get("lat", 0))
            lon = float(request.args.get("lon", 0))
            radius_m = float(request.args.get("radius_m", 100))
            from npu_engine.field.site_engine import derive_site_state
            r = derive_site_state(lat, lon, radius_m)
            return jsonify({
                "suitability": r["suitability"],
                "recommendations": r["design_recommendations"],
                "site_brief": r["site_brief"],
                "solar": r["solar"],
            })
        except Exception as e:
            return jsonify({"error": str(e)})

    # ── system/services → system_bp (registered above) ────────

    # ── research/* → corpus_bp (registered above) ────────

    # ── Core index ────────────────────────────────────────
    @app.route("/")
    def _index():
        return send_from_directory('static', 'index.html')

    @app.route("/home")
    def _home():
        return send_from_directory('static', 'home.html')

    @app.route("/api")
    def _api_index():
        return jsonify({
            'system': 'Atlas Core',
            'status': 'running',
            'endpoints': {
                'field': '/field',
                'spine': '/spine',
                'observe': '/observe',
                'plants': '/plants/region',
                'site': '/site/state',
                'corpus': '/corpus/search',
                'guild': '/guild/state',
                'land': '/land/mandala',
            }
        })

    # ── Static file serving (for future app layer) ────────
    @app.route('/apps/<path:name>')
    def serve_app(name):
        return send_from_directory('apps', name)

    @app.route('/static/<path:name>')
    def serve_static(name):
        return send_from_directory('static', name)

    # ── S-layer field state pages ────────
    @app.route('/s0')
    def s0(): return send_from_directory('static', 's0.html')

    @app.route('/s1')
    def s1(): return send_from_directory('static', 's1.html')

    @app.route('/s2')
    def s2(): return send_from_directory('static', 's2.html')

    @app.route('/s3')
    def s3(): return send_from_directory('static', 's3.html')

    @app.route('/s4')
    def s4(): return send_from_directory('static', 's4.html')

    @app.route('/s5')
    def s5(): return send_from_directory('static', 's5.html')

    @app.route('/s6')
    def s6(): return send_from_directory('static', 's6.html')

    @app.route('/glyphs')
    def _glyphs_page(): return send_from_directory('static', 'glyphs.html')

    @app.route('/assets/wesnoth/<path:filename>')
    def _wesnoth_assets(filename):
        return send_from_directory('static/assets/wesnoth', filename)

    @app.route('/hexd-portal')
    def _hexd_portal():
        return send_from_directory('static', 'hexd-portal.html')

    # ── Snapshots → system_bp (registered above) ────────

    # ── Rings → symbols_bp (registered above) ────────

    # ── Dashboard + widgets ────────
    @app.route('/dashboard')
    def dashboard(): return send_from_directory('static', 'dashboard.html')

    # ── dashboard/health, dashboard/status → system_bp (registered above) ────────

    @app.route('/widgets/<path:name>')
    def widgets(name): return send_from_directory('static/widgets', name)

    # ── Oracle page ────────
    @app.route('/oracle')
    def _oracle_page(): return send_from_directory('static', 'oracle.html')

    # ── Lila: I Ching augury engine ──��─────
    from npu_engine.field.iching_augury_engine import (
        score_hexagram, score_omen, trigram_field_map, cast_hexagram,
    )

    @app.route('/lila/augury/hexagram/<int:hex_int>')
    def _augury_hexagram(hex_int):
        if not 0 <= hex_int <= 63:
            return jsonify({"error": "hexagram must be 0-63"}), 400
        return jsonify(score_hexagram(hex_int, field_state()))

    @app.route('/lila/augury/omen/<phenomenon>')
    @app.route('/lila/augury/omen/<phenomenon>/<direction>')
    def _augury_omen(phenomenon, direction=None):
        return jsonify(score_omen(phenomenon, direction or '', field_state()))

    @app.route('/lila/augury/cast')
    def _augury_cast():
        return jsonify(cast_hexagram(field_state()))

    @app.route('/lila/augury/field')
    def _augury_field():
        return jsonify(trigram_field_map(field_state()))

    # ── Lila: Pāśaka dice oracle ─────────
    @app.route('/lila/augury/pasaka')
    def _augury_pasaka():
        from npu_engine.pasaka_engine import cast
        return jsonify(cast(field_state()))

    @app.route('/lila/augury/pasaka/<int:d1>/<int:d2>/<int:d3>')
    def _augury_pasaka_fixed(d1, d2, d3):
        from npu_engine.pasaka_engine import get
        return jsonify(get(d1, d2, d3))

    print(f"  [pasaka] /lila/augury/pasaka")
    print(f"  [pasaka] /lila/augury/pasaka/<d1>/<d2>/<d3>")

    # ── Lila: Time Pointer oracle ─��──────
    @app.route('/lila/oracle/timepointer')
    def _oracle_timepointer():
        """Find next occurrence of a tithi+nakshatra pair within 90 days."""
        import csv as _tp_csv
        from datetime import timedelta

        target_tithi = request.args.get('tithi', '')
        target_nak = request.args.get('nakshatra', '')
        if not target_tithi and not target_nak:
            return jsonify({"error": "provide tithi and/or nakshatra"}), 400

        now = datetime.now()
        tithi_match = None
        nak_match = None
        conjunction = None

        # Scan daily for 90 days
        for day_offset in range(1, 91):
            dt = now + timedelta(days=day_offset)
            try:
                p5 = calc_panchanga(dt)
            except Exception:
                continue

            p_tithi = p5.get("tithi", "")
            p_nak = p5.get("nakshatra", "")

            # Check tithi match
            if target_tithi and not tithi_match:
                if target_tithi.lower() in p_tithi.lower():
                    tithi_match = {"date": dt.strftime("%Y-%m-%d"),
                                   "weekday": dt.strftime("%A"),
                                   "days_from_now": day_offset,
                                   "panchanga": p5}

            # Check nakshatra match
            if target_nak and not nak_match:
                if target_nak.lower() in p_nak.lower():
                    nak_match = {"date": dt.strftime("%Y-%m-%d"),
                                 "weekday": dt.strftime("%A"),
                                 "days_from_now": day_offset,
                                 "panchanga": p5}

            # Check conjunction
            if target_tithi and target_nak and not conjunction:
                if (target_tithi.lower() in p_tithi.lower() and
                        target_nak.lower() in p_nak.lower()):
                    conjunction = {"date": dt.strftime("%Y-%m-%d"),
                                   "weekday": dt.strftime("%A"),
                                   "days_from_now": day_offset,
                                   "panchanga": p5}

            if tithi_match and nak_match and conjunction:
                break

        # Get hora from matching panchanga
        best = conjunction or tithi_match or nak_match
        hora_lord = ""
        if best:
            p = best.get("panchanga", {})
            vara = p.get("vara", "")
            hora_lord = _vara_to_hora(vara)

        # Load chakra for nakshatra
        chakra = ""
        try:
            _ck_path = os.path.join(_here, "datasets", "tantra",
                                    "chakra_cross_domain.csv")
            if os.path.exists(_ck_path):
                with open(_ck_path) as _ckf:
                    for row in _tp_csv.DictReader(_ckf):
                        naks = row.get("nakshatras", "")
                        if target_nak and target_nak.lower() in naks.lower():
                            chakra = row.get("name_iast", "")
                            break
        except Exception:
            pass

        # Load tithi good_for
        preparation = ""
        try:
            _td_path = os.path.join(_here, "datasets", "astro",
                                    "tithi_data.csv")
            if os.path.exists(_td_path):
                with open(_td_path) as _tdf:
                    for row in _tp_csv.DictReader(
                            (l for l in _tdf if l.strip())):
                        if (target_tithi and
                                target_tithi.lower() in
                                row.get("name_iast", "").lower()):
                            preparation = row.get("good_for", "")
                            break
        except Exception:
            pass

        # Cast hexagram for that field
        hex_result = None
        if best:
            dt_best = datetime.strptime(best["date"], "%Y-%m-%d")
            try:
                p5_best = calc_panchanga(dt_best)
                fs_best = {"panchanga": p5_best,
                           "hora": {"hora_lord": hora_lord}}
                hex_result = cast_hexagram(fs_best, seed=hash(
                    best["date"]) % (2**31))
            except Exception:
                pass

        return jsonify({
            "target_tithi": target_tithi,
            "target_nakshatra": target_nak,
            "tithi_match": tithi_match,
            "nakshatra_match": nak_match,
            "conjunction": conjunction,
            "hora_lord": hora_lord,
            "chakra": chakra,
            "preparation": preparation,
            "hexagram": hex_result,
        })

    def _vara_to_hora(vara):
        """Extract hora lord from vara string."""
        vara_map = {
            "ravi": "surya", "soma": "chandra", "mangala": "mangala",
            "budha": "budha", "guru": "guru", "brihas": "guru",
            "shukra": "shukra", "shani": "shani",
        }
        vl = vara.lower()
        for k, v in vara_map.items():
            if k in vl:
                return v
        return "surya"

    print(f"  [oracle] /oracle")
    print(f"  [oracle] /lila/augury/hexagram|omen|cast|field")
    print(f"  [oracle] /lila/oracle/timepointer")

    # ── Geosolar field monitor ─────────────────────────────
    from npu_engine.field.geosolar_engine import (
        get_geosolar_state, read_log, correlate_with_panchanga,
        _start_geosolar_logger,
    )

    @app.route('/geosolar')
    def _geosolar():
        return jsonify(get_geosolar_state())

    @app.route('/geosolar/log')
    def _geosolar_log():
        return jsonify(read_log(50))

    @app.route('/geosolar/correlate')
    def _geosolar_correlate():
        return jsonify(correlate_with_panchanga())

    # Start background logger — inject panchanga function
    _start_geosolar_logger(lambda: calc_panchanga(), interval_s=600)
    print(f"  [geosolar] /geosolar /geosolar/log /geosolar/correlate")

    # ── Briefing engine ────────────────────────────────────
    from npu_engine.field.briefing_engine import get_briefing

    @app.route('/briefing')
    def _briefing():
        return jsonify(get_briefing(calc_panchanga, field_state))

    print(f"  [briefing] /briefing (qwen2.5:1.5b via ollama)")

    # ── Transit analysis (Tarabala) ───────────────────────
    from npu_engine.field.transit_engine import get_transit_analysis

    @app.route('/transit/analysis')
    def _transit_analysis():
        td = get_transit_data()
        return jsonify(get_transit_analysis(td.get('natal', {}), td.get('positions', {})))

    print(f"  [transit] /transit/analysis (Tarabala)")

    # ── Shalaka page ──────────────────────────────────────
    @app.route('/shalaka')
    def _shalaka_page():
        return send_from_directory('static', 'shalaka.html')

    print(f"  [shalaka] /shalaka")

    # ── Sound field loop ─────────────────────────────────
    # Re-derive sound spec from live field state every 60s and push to SC.
    # Makes tanpura/bija/tabla/reverb follow nakshatra, hora, coherence, Ekadashi.
    def _sound_field_loop():
        import time, sys
        from npu_engine.sound.sound_engine import derive_sound_spec
        from npu_engine.sound.osc_bridge import send_sound_spec
        import npu_engine.routes._sound_state as _ss_local

        def _log(msg):
            print(msg, file=sys.stderr, flush=True)

        # Wait for SC to finish booting and loading SynthDefs
        time.sleep(8)
        _log("  ✦ sound field loop started (60s tick)")

        last_sig = None
        while True:
            try:
                fs = field_state()
                spec = derive_sound_spec(fs, _ss_local.sound_mode)
                send_sound_spec(spec)

                # Log only when something meaningful changed
                sig = (
                    spec.get("sa_hz"),
                    spec.get("mode"),
                    spec.get("ekadashi"),
                    tuple(sorted(spec.get("layers", {}).items())),
                )
                if sig != last_sig:
                    _log(f"  ♪ sound: mode={spec['mode']} sa={spec['sa_hz']} "
                         f"eka={spec['ekadashi']} layers={spec['layers']}")
                    last_sig = sig
            except Exception as e:
                _log(f"  ⚠ sound loop: {e}")

            time.sleep(60)

    import threading as _t
    _sound_loop_thread = _t.Thread(
        target=_sound_field_loop, daemon=True, name="atlas-sound-loop")
    _sound_loop_thread.start()

    return app


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    install_download_handoff()
    app = create_app()
    print(f"✦ atlas_core serving on http://localhost:{port}")
    print(f"  /field  → field_state() JSON")
    print(f"  /       → core index JSON")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


# --- COHERENCE SERVER ---
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

LIVE_STATE = {
    "coherence": 0.5,
    "phase": "intro",
    "tala_step": 0,
    "energy": 0.5,
}

class _CoherenceHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/coherence":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(LIVE_STATE).encode())
        else:
            self.send_response(404)
            self.end_headers()

def run_coherence_server():
    server = HTTPServer(("localhost", 8000), _CoherenceHandler)
    print("→ http://localhost:8000/coherence")
    server.serve_forever()

# ── INSTANCE / NATAL ────────────────────────────────
import json as _json
_NATAL_PATH = os.path.join(os.path.dirname(__file__), 
              'instance', 'personal', 'natal.json')

def load_natal():
    try:
        with open(_NATAL_PATH) as f:
            return _json.load(f)
    except:
        return {}
