"""
resonance_engine.py

Domain: S0-S2 — Pratibimba (reflection of the eternal in the material)
Purpose: Given the current field state, find what is resonant in the
         living world right now — streaming temples, deity images,
         raga recordings appropriate to this moment.

The pratibimba principle: the material field reflects the eternal.
The resonance engine surfaces where the field IS already manifesting.
"""

import csv
import io
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))

_TEMPLES_CSV = os.path.join(_ROOT, "datasets", "temples", "temple_streams.csv")
_IMAGES_CSV = os.path.join(_ROOT, "datasets", "temples", "deity_images.csv")
_RECORDINGS_CSV = os.path.join(_ROOT, "datasets", "sound", "raga_recordings.csv")

_temples: Optional[List[dict]] = None
_images: Optional[List[dict]] = None
_recordings: Optional[List[dict]] = None


def _load_csv(path):
    try:
        with open(path, encoding="utf-8") as f:
            return list(csv.DictReader(io.StringIO(f.read().lstrip())))
    except Exception:
        return []


def _get_temples():
    global _temples
    if _temples is None:
        _temples = _load_csv(_TEMPLES_CSV)
    return _temples


def _get_images():
    global _images
    if _images is None:
        _images = _load_csv(_IMAGES_CSV)
    return _images


def _get_recordings():
    global _recordings
    if _recordings is None:
        _recordings = _load_csv(_RECORDINGS_CSV)
    return _recordings


def _current_ist_hour():
    """Get current IST hour (0-23)."""
    try:
        from zoneinfo import ZoneInfo
        now = datetime.now(ZoneInfo("Asia/Kolkata"))
        return now.hour, now.minute
    except Exception:
        # Fallback: UTC+5:30
        from datetime import timezone, timedelta
        ist = timezone(timedelta(hours=5, minutes=30))
        now = datetime.now(ist)
        return now.hour, now.minute


def _prahar_for_hour(hour):
    """Map hour to prahar name."""
    if 4 <= hour < 7:
        return "dawn"
    elif 7 <= hour < 10:
        return "morning"
    elif 10 <= hour < 14:
        return "afternoon"
    elif 14 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "night"


def _near_arati(arati_times_str, current_hour, current_min, window=30):
    """Check if current IST time is within window minutes of any arati."""
    if not arati_times_str:
        return False, ""
    times = [t.strip() for t in arati_times_str.split(",")]
    current_total = current_hour * 60 + current_min
    for t in times:
        try:
            parts = t.split(":")
            arati_total = int(parts[0]) * 60 + int(parts[1])
            if abs(current_total - arati_total) <= window:
                return True, t
        except (ValueError, IndexError):
            continue
    return False, ""


def _normalize(s):
    """Normalize for comparison — lowercase, strip diacritics."""
    if not s:
        return ""
    return s.lower().replace("ā", "a").replace("ī", "i").replace("ū", "u").replace("ṣ", "sh").replace("ś", "sh").replace("ṭ", "t").replace("ḍ", "d").replace("ṇ", "n")


def _match_field(value, target):
    """Check if field value matches target (fuzzy)."""
    if not value or not target:
        return False
    return _normalize(target) in _normalize(value) or _normalize(value) in _normalize(target)


def derive_resonance(field_state: dict) -> dict:
    """Find what is resonant in the living world right now."""
    pa = field_state.get("panchanga", {})
    nak = pa.get("nakshatra", "")
    tithi = pa.get("tithi", "")
    vara = pa.get("vara", "")
    devi = pa.get("devi", {})
    devi_name = devi.get("name", "") if isinstance(devi, dict) else str(devi)
    ss = field_state.get("sound_state", {})
    raga = ss.get("raga", "")
    element = pa.get("element", "")

    hour, minute = _current_ist_hour()
    prahar = _prahar_for_hour(hour)

    # ── Temple matching ──
    temple_results = []
    for t in _get_temples():
        score = 0
        reasons = []
        if _match_field(nak, t.get("nakshatra_primary", "")):
            score += 1
            reasons.append(f"nakshatra {nak}")
        if _match_field(vara, t.get("vara_primary", "")) or t.get("vara_primary") == "all":
            score += 1
            if t.get("vara_primary") != "all":
                reasons.append(f"vara {vara}")
        if _match_field(tithi, t.get("tithi_primary", "")) or t.get("tithi_primary") == "all":
            score += 1
            if t.get("tithi_primary") != "all":
                reasons.append(f"tithi {tithi}")

        is_live, arati_time = _near_arati(t.get("arati_times_ist", ""), hour, minute)
        schedule = t.get("stream_schedule", "")

        temple_results.append({
            "temple_id": t.get("temple_id", ""),
            "name": t.get("name", ""),
            "deity": t.get("deity_primary", ""),
            "tradition": t.get("tradition", ""),
            "stream_url": t.get("stream_url", ""),
            "stream_type": t.get("stream_type", ""),
            "match_score": score,
            "match_reason": " + ".join(reasons) if reasons else "general",
            "live_now": is_live or schedule == "always",
            "current_arati": arati_time if is_live else "",
            "location": f"{t.get('location_city', '')}, {t.get('location_country', '')}",
        })

    temple_results.sort(key=lambda x: (-x["match_score"], -x["live_now"]))

    # ── Deity image matching ──
    image_results = []
    for img in _get_images():
        score = 0
        reasons = []
        if _match_field(nak, img.get("nakshatra_primary", "")):
            score += 2
            reasons.append(f"nakshatra {nak}")
        if _match_field(tithi, img.get("tithi_primary", "")):
            score += 1
            reasons.append(f"tithi {tithi}")
        if _match_field(vara, img.get("vara_primary", "")):
            score += 1
            reasons.append(f"vara")
        if _match_field(element, img.get("element_association", "")):
            score += 1
            reasons.append(f"element {element}")
        # Always include current Nitya Devi
        if devi_name and _match_field(devi_name, img.get("deity_name", "")):
            score += 3
            reasons.append(f"Nitya Devi {devi_name}")

        if score > 0:
            image_results.append({
                "deity_name": img.get("deity_name", ""),
                "deity_form": img.get("deity_form", ""),
                "image_url": img.get("image_url", ""),
                "image_description": img.get("image_description", ""),
                "match_score": score,
                "match_reason": " + ".join(reasons),
                "attribution": img.get("attribution", ""),
                "license": img.get("license", ""),
            })

    image_results.sort(key=lambda x: -x["match_score"])

    # ── Raga recording matching ──
    recording_results = []
    for rec in _get_recordings():
        score = 0
        reasons = []
        rec_prahar = rec.get("prahar", "")
        if rec_prahar == prahar:
            score += 2
            reasons.append(f"prahar {prahar}")
        if _match_field(raga, rec.get("raga_name", "")):
            score += 3
            reasons.append(f"raga {raga}")
        if _match_field(nak, rec.get("nakshatra_resonance", "")):
            score += 1
            reasons.append(f"nakshatra")
        if _match_field(vara, rec.get("vara_resonance", "")):
            score += 1
            reasons.append(f"vara")

        if score > 0:
            recording_results.append({
                "raga_name": rec.get("raga_name", ""),
                "artist": rec.get("artist", ""),
                "instrument": rec.get("instrument", ""),
                "archive_url": rec.get("archive_url", ""),
                "duration_minutes": rec.get("duration_minutes", ""),
                "match_score": score,
                "match_reason": " + ".join(reasons),
                "tradition": rec.get("tradition", ""),
            })

    recording_results.sort(key=lambda x: -x["match_score"])

    # ── Live now summary ──
    live_temples = [t for t in temple_results if t["live_now"]]
    live_now = len(live_temples) > 0
    live_summary = ""
    if live_temples:
        t = live_temples[0]
        if t["current_arati"]:
            live_summary = f"Arati at {t['name']} near {t['current_arati']} IST"
        else:
            live_summary = f"{t['name']} streaming now"

    return {
        "temples": temple_results[:5],
        "deity_images": image_results[:5],
        "raga_recordings": recording_results[:5],
        "live_now": live_now,
        "live_summary": live_summary,
        "field_summary": f"{nak} · {tithi} · {vara} · {devi_name}",
        "prahar": prahar,
        "attestation": "SYNTHESIS",
    }
