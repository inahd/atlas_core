#!/usr/bin/env python3
"""
fetch_texts.py — Download canonical source texts into datasets/sources/.

Downloads from GRETIL, SARIT, and Archive.org.
Saves raw text + chunked JSONL for each source.
Writes manifest.json tracking what's been fetched.

Usage:
  python3 scripts/fetch_texts.py              # fetch all
  python3 scripts/fetch_texts.py --domain jyotish  # fetch one domain
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("pip install requests")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "datasets" / "sources"

# ── Source catalog ────────────────────────────────────────────
# GRETIL GitHub mirror base:
_G = "https://raw.githubusercontent.com/INDOLOGY/GRETIL-mirror/master/gretil.sub.uni-goettingen.de/gretil/1_sanskr"

TEXTS = [
    # ── Jyotish ──────────────────────────────────────────────
    {
        "id": "brihat_jataka",
        "name": "Brihat Jataka (Varahamihira)",
        "domain": "jyotish",
        "url": f"{_G}/6_sastra/8_jyot/brhajj_u.htm",
        "format": "html",
    },
    {
        "id": "brihat_samhita",
        "name": "Brihat Samhita (Varahamihira)",
        "domain": "jyotish",
        "url": f"{_G}/6_sastra/8_jyot/brhats_u.htm",
        "format": "html",
    },
    {
        "id": "surya_siddhanta",
        "name": "Surya Siddhanta",
        "domain": "jyotish",
        "url": f"{_G}/6_sastra/8_jyot/surysidu.htm",
        "format": "html",
    },
    # ── Ayurveda ─────────────────────────────────────────────
    {
        "id": "charaka_samhita",
        "name": "Charaka Samhita",
        "domain": "ayurveda",
        "url": f"{_G}/6_sastra/7_ayur/caraka_u.htm",
        "format": "html",
    },
    {
        "id": "yogasataka",
        "name": "Yogasataka (100 Ayurvedic formulas)",
        "domain": "ayurveda",
        "url": f"{_G}/6_sastra/7_ayur/yogasatu.htm",
        "format": "html",
    },
    {
        "id": "bhavaprakasha",
        "name": "Bhavaprakasha (herbal pharmacopoeia)",
        "domain": "ayurveda",
        "url": f"{_G}/6_sastra/7_ayur/bhavpr_u.htm",
        "format": "html",
    },
    # ── Cosmology / Vedic ────────────────────────────────────
    {
        "id": "bhagavata_purana_01",
        "name": "Bhagavata Purana (Canto 1)",
        "domain": "cosmology",
        "url": f"{_G}/3_purana/bhagp/bhp_01u.htm",
        "format": "html",
    },
    {
        "id": "bhagavata_purana_05",
        "name": "Bhagavata Purana (Canto 5 — cosmography)",
        "domain": "cosmology",
        "url": f"{_G}/3_purana/bhagp/bhp_05u.htm",
        "format": "html",
    },
    {
        "id": "bhagavata_purana_10",
        "name": "Bhagavata Purana (Canto 10 — Krishna lila)",
        "domain": "cosmology",
        "url": f"{_G}/3_purana/bhagp/bhp_10u.htm",
        "format": "html",
    },
    # ── Yoga ─────────────────────────────────────────────────
    {
        "id": "yoga_sutras",
        "name": "Yoga Sutras (Patanjali)",
        "domain": "yoga",
        "url": f"{_G}/6_sastra/3_phil/yoga/yogasutu.htm",
        "format": "html",
    },
    {
        "id": "hatha_yoga_pradipika",
        "name": "Hatha Yoga Pradipika",
        "domain": "yoga",
        "url": f"{_G}/6_sastra/3_phil/yoga/hathyopu.htm",
        "format": "html",
    },
    {
        "id": "gheranda_samhita",
        "name": "Gheranda Samhita",
        "domain": "yoga",
        "url": f"{_G}/6_sastra/3_phil/yoga/ghers__u.htm",
        "format": "html",
    },
    # Gaudiya — from Vedabase/public sources
    {
        "id": "brahma_samhita",
        "name": "Brahma Samhita (Chapter 5, key verses)",
        "domain": "gaudiya",
        "url": None,
        "format": "text",
        "inline": True,
        "text": """Brahma Samhita Chapter 5 — Key Verses

5.1
ishvarah paramah krishnah sac-cid-ananda-vigrahah
anadir adir govindah sarva-karana-karanam

The Supreme Controller is Krishna, whose form is eternal, full of knowledge and bliss. He is the origin of all, the cause of all causes, known as Govinda.

5.29
cintamani-prakara-sadmasu kalpa-vriksha-
lakshavriteshu surabhir abhipalayantam
lakshmi-sahasra-shata-sambhrama-sevyamanam
govindam adi-purusham tam aham bhajami

In spiritual abodes made of touchstone, surrounded by millions of wish-fulfilling trees, tending the surabhi cows, served with great reverence by hundreds of thousands of Lakshmis — I worship that original person, Govinda.

5.30
venum kvanantam aravinda-dalayataksham
barhavatamsam asitambuda-sundarangam
kandarpa-koti-kamaniya-vishesha-shobham
govindam adi-purusham tam aham bhajami

Playing on His flute, with eyes like lotus petals, His head adorned with a peacock feather, His beautiful form tinged with the hue of blue clouds, His unique loveliness captivating millions of Cupids — I worship that original person, Govinda.

5.37
ananda-cinmaya-rasa-pratibhavitabhis
tabhir ya eva nija-rupataya kalabhih
goloka eva nivasaty akhilatma-bhuto
govindam adi-purusham tam aham bhajami

He resides in His own realm, Goloka, with Radha, who resembles His own spiritual blissful self, and who is the counterpart of His own spiritual form. He is the soul of all souls — I worship that original person, Govinda.

5.38
premanjana-cchurita-bhakti-vilocanena
santah sadaiva hridayeshu vilokayanti
yam shyamasundaram acintya-guna-svarupam
govindam adi-purusham tam aham bhajami

Those who have anointed their eyes with the salve of pure love always see within their hearts that beautiful dark-complexioned Lord, whose inconceivable qualities are His very form — I worship that original person, Govinda.
""",
    },
    {
        "id": "sikshashtakam",
        "name": "Sikshashtakam (8 verses of Mahaprabhu)",
        "domain": "gaudiya",
        "url": None,  # No public URL — we'll create from known text
        "format": "text",
        "inline": True,
        "text": """verse 1
ceto-darpana-marjanam bhava-maha-davagni-nirvapanam
shreyah-kairava-chandrika-vitaranam vidya-vadhu-jivanam
anandambudhi-vardhanam prati-padam purnamritasvadanam
sarvatma-snapanam param vijayate sri-krishna-sankirtanam

verse 2
namnam akari bahudha nija-sarva-shaktis
tatrarpita niyamitah smarane na kalah
etadrishi tava kripa bhagavan mamapi
durdaivam idrisham ihajani nanuragah

verse 3
trinad api sunichena taror api sahishnuna
amanina manadena kirtaniyah sada harih

verse 4
na dhanam na janam na sundarim kavitam va jagad-isha kamaye
mama janmani janmanishvare bhavatad bhaktir ahaituki tvayi

verse 5
ayi nanda-tanuja kinkaram patitam mam vishame bhavambudhau
kripaya tava pada-pankaja-sthita-dhuli-sadrisham vichintaya

verse 6
nayanam galad-ashru-dharaya vadanam gadgada-ruddhaya gira
pulakair nichitam vapuh kada tava nama-grahane bhavishyati

verse 7
yugayitam nimeshena chakshusha pravrishayitam
shunyayitam jagat sarvam govinda-virahena me

verse 8
ashlishya va pada-ratam pinashtu mam
adarshanan marma-hatam karotu va
yatha tatha va vidadhatu lampato
mat-prana-nathas tu sa eva naparah
""",
    },
]


# ── HTML stripping ────────────────────────────────────────────

def strip_html(html: str) -> str:
    """Remove HTML tags, decode entities, clean whitespace."""
    # Remove script/style blocks
    text = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', html,
                  flags=re.DOTALL | re.IGNORECASE)
    # Remove tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Decode common entities
    for ent, ch in [('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>'),
                    ('&quot;', '"'), ('&nbsp;', ' '), ('&#39;', "'")]:
        text = text.replace(ent, ch)
    # Collapse whitespace
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def strip_xml(xml: str) -> str:
    """Extract text content from XML."""
    text = re.sub(r'<[^>]+>', ' ', xml)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


# ── Chunker ───────────────────────────────────────────────────

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    """Split text into overlapping chunks."""
    chunks = []
    pos = 0
    idx = 0
    while pos < len(text):
        end = min(pos + chunk_size, len(text))
        # Try to break at sentence/paragraph boundary
        if end < len(text):
            for sep in ['\n\n', '\n', '. ', '। ', '॥']:
                bp = text.rfind(sep, pos + chunk_size // 2, end + 100)
                if bp > pos:
                    end = bp + len(sep)
                    break
        chunk = text[pos:end].strip()
        if chunk:
            chunks.append({
                "id": idx,
                "char_start": pos,
                "char_end": end,
                "text": chunk,
            })
            idx += 1
        pos = max(pos + 1, end - overlap)
    return chunks


# ── Fetch ─────────────────────────────────────────────────────

def fetch_one(entry: dict, force: bool = False) -> dict:
    """Fetch a single text source. Returns manifest entry."""
    domain = entry["domain"]
    text_id = entry["id"]
    domain_dir = SOURCES / domain
    domain_dir.mkdir(parents=True, exist_ok=True)

    raw_path = domain_dir / f"{text_id}.txt"
    chunks_path = domain_dir / f"{text_id}_chunks.jsonl"

    result = {
        "id": text_id,
        "name": entry["name"],
        "domain": domain,
        "url": entry.get("url", ""),
        "format": entry.get("format", "text"),
        "raw_path": str(raw_path.relative_to(ROOT)),
        "chunks_path": str(chunks_path.relative_to(ROOT)),
    }

    # Skip if already fetched (unless forced)
    if raw_path.exists() and raw_path.stat().st_size > 100 and not force:
        result["status"] = "cached"
        result["size_bytes"] = raw_path.stat().st_size
        result["fetched_at"] = datetime.fromtimestamp(
            raw_path.stat().st_mtime).isoformat()
        print(f"  SKIP  {text_id} ({result['size_bytes']:,} bytes)")
        # Ensure chunks exist
        if not chunks_path.exists():
            _chunk_file(raw_path, chunks_path, entry)
        return result

    # Inline text (no URL needed)
    if entry.get("inline"):
        text = entry.get("text", "")
        raw_path.write_text(text, encoding="utf-8")
        result["status"] = "inline"
        result["size_bytes"] = len(text.encode("utf-8"))
        result["fetched_at"] = datetime.now().isoformat()
        print(f"  WRITE {text_id} ({result['size_bytes']:,} bytes, inline)")
        _chunk_file(raw_path, chunks_path, entry)
        return result

    # Fetch from URL
    url = entry.get("url")
    if not url:
        result["status"] = "no_url"
        result["size_bytes"] = 0
        print(f"  SKIP  {text_id} (no URL)")
        return result

    for attempt in range(3):
        try:
            print(f"  FETCH {text_id} (attempt {attempt + 1})...")
            r = requests.get(url, timeout=30, headers={
                "User-Agent": "AtlasResearch/1.0 (academic)"
            })
            r.raise_for_status()

            # Process based on format
            fmt = entry.get("format", "text")
            if fmt == "html":
                text = strip_html(r.text)
            elif fmt == "xml":
                text = strip_xml(r.text)
            else:
                text = r.text

            raw_path.write_text(text, encoding="utf-8")
            result["status"] = "fetched"
            result["size_bytes"] = len(text.encode("utf-8"))
            result["fetched_at"] = datetime.now().isoformat()
            print(f"  OK    {text_id} ({result['size_bytes']:,} bytes)")

            _chunk_file(raw_path, chunks_path, entry)
            return result

        except Exception as exc:
            last_err = str(exc)
            print(f"  ERR   {text_id}: {last_err}")
            if attempt < 2:
                time.sleep(2 ** attempt)

    result["status"] = "failed"
    result["size_bytes"] = 0
    result["error"] = last_err
    return result


def _chunk_file(raw_path: Path, chunks_path: Path, entry: dict):
    """Chunk a raw text file into JSONL."""
    text = raw_path.read_text(encoding="utf-8")
    chunks = chunk_text(text)
    with open(chunks_path, "w", encoding="utf-8") as f:
        for chunk in chunks:
            chunk["source"] = entry["id"]
            chunk["domain"] = entry["domain"]
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    print(f"  CHUNK {entry['id']}: {len(chunks)} chunks → {chunks_path.name}")


# ── Prabhupadabooks crawler ────────────────────────────────────

# SB canto → chapter count (Prabhupada original ends at 10.13)
SB_STRUCTURE = {
    1: 19, 2: 10, 3: 33, 4: 31, 5: 26, 6: 19,
    7: 15, 8: 24, 9: 24, 10: 13,
}
BG_CHAPTERS = {
    1: 46, 2: 72, 3: 43, 4: 42, 5: 29, 6: 47, 7: 30,
    8: 28, 9: 34, 10: 42, 11: 55, 12: 20, 13: 35, 14: 27,
    15: 20, 16: 24, 17: 28, 18: 78,
}
CC_STRUCTURE = {
    "adi": 17, "madhya": 25, "antya": 20,
}


def _extract_pb_verse(html: str) -> dict:
    """Extract verse components from a prabhupadabooks.com page."""
    result = {"sanskrit": "", "iast": "", "synonyms": "",
              "translation": "", "purport": ""}

    # Strip to text first
    text = strip_html(html)

    # Split into sections by uppercase headers
    sections = {}
    current = None
    lines = text.split('\n')
    for line in lines:
        stripped = line.strip()
        up = stripped.upper()
        if up in ("SYNONYMS", "TRANSLATION", "PURPORT",
                  "TRANSLATIONS", "PURPORTS"):
            current = up.rstrip("S")  # normalize plurals
            sections[current] = []
            continue
        if current and stripped and len(stripped) > 5:
            sections.setdefault(current, []).append(stripped)

    result["synonyms"]   = ' '.join(sections.get("SYNONYM", []))[:1000]
    result["translation"] = ' '.join(sections.get("TRANSLATION", []))[:2000]
    result["purport"]     = ' '.join(sections.get("PURPORT", []))[:5000]

    # Sanskrit — look for devanagari in the raw HTML
    m = re.search(r'class="(?:r|verse_text)"[^>]*>(.*?)</(?:td|div)',
                  html, re.DOTALL | re.IGNORECASE)
    if m:
        result["iast"] = strip_html(m.group(1)).strip()[:500]

    return result


def crawl_prabhupadabooks(book: str = "sb", force: bool = False,
                          chapter_filter: int = None):
    """Crawl prabhupadabooks.com for Bhagavatam, Gita, or CC."""
    base_url = "https://prabhupadabooks.com"
    out_dir = SOURCES / "gaudiya"
    out_dir.mkdir(parents=True, exist_ok=True)

    if book == "sb":
        structure = SB_STRUCTURE
        chunks_path = out_dir / "bhagavatam_chunks.jsonl"
        prefix = "sb"
        name = "Srimad Bhagavatam"
    elif book == "bg":
        chunks_path = out_dir / "bg_chunks.jsonl"
        prefix = "bg"
        name = "Bhagavad Gita As It Is"
    elif book == "cc":
        chunks_path = out_dir / "cc_chunks.jsonl"
        prefix = "cc"
        name = "Caitanya Caritamrta"
    else:
        print(f"Unknown book: {book}")
        return

    print(f"\n✦ Crawling {name} from prabhupadabooks.com")
    print(f"  Output: {chunks_path}")

    verse_dir = out_dir / f"{prefix}_verses"
    verse_dir.mkdir(exist_ok=True)

    chunk_id = 0
    total_fetched = 0
    total_cached = 0

    # Open chunks file in append mode if not forcing
    mode = "w" if force else "a"
    existing_ids = set()
    if not force and chunks_path.exists():
        with open(chunks_path) as f:
            for line in f:
                try:
                    existing_ids.add(json.loads(line).get("verse_ref", ""))
                except Exception:
                    pass
        chunk_id = len(existing_ids)

    chunks_f = open(chunks_path, mode, encoding="utf-8")

    try:
        if book == "cc":
            _crawl_cc(base_url, verse_dir, chunks_f, existing_ids,
                      chunk_id, force)
        elif book == "bg":
            _crawl_bg(base_url, verse_dir, chunks_f, existing_ids,
                      chunk_id, force, chapter_filter=chapter_filter)
        else:
            for canto, max_ch in sorted(structure.items()):
                for ch in range(1, max_ch + 1):
                    for verse in range(1, 100):
                        ref = f"{prefix.upper()} {canto}.{ch}.{verse}"
                        if ref in existing_ids:
                            total_cached += 1
                            continue

                        url = f"{base_url}/{prefix}/{canto}/{ch}/{verse}"
                        vfile = verse_dir / f"{canto}_{ch}_{verse}.json"

                        if vfile.exists() and not force:
                            total_cached += 1
                            continue

                        try:
                            r = requests.get(url, timeout=20, headers={
                                "User-Agent": "AtlasResearch/1.0 (academic)"})
                            if r.status_code == 404:
                                break  # no more verses in this chapter
                            r.raise_for_status()
                        except Exception as exc:
                            if "404" in str(exc):
                                break
                            print(f"  ERR {ref}: {exc}")
                            continue

                        data = _extract_pb_verse(r.text)
                        data["verse_ref"] = ref
                        data["url"] = url

                        vfile.write_text(json.dumps(data, ensure_ascii=False),
                                         encoding="utf-8")

                        # Write chunk
                        text = data["translation"]
                        if data["purport"]:
                            text += "\n\n" + data["purport"]
                        if text.strip():
                            chunk = {
                                "id": chunk_id,
                                "verse_ref": ref,
                                "domain": "gaudiya",
                                "authority": "shastra",
                                "translator": "AC Bhaktivedanta Swami Prabhupada",
                                "text": text[:2000],
                                "sanskrit": data.get("iast", ""),
                                "source": prefix,
                            }
                            chunks_f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
                            chunk_id += 1

                        total_fetched += 1
                        if total_fetched % 10 == 0:
                            print(f"  {ref} ({total_fetched} fetched)")
                        time.sleep(0.5)

                    # Chapter done
                print(f"  Canto {canto} done ({total_fetched} fetched, "
                      f"{total_cached} cached)")

    finally:
        chunks_f.close()

    print(f"\n✦ {name}: {total_fetched} fetched, {total_cached} cached, "
          f"{chunk_id} total chunks")


def _crawl_bg(base_url, verse_dir, chunks_f, existing_ids, chunk_id, force,
              chapter_filter=None):
    """Crawl Bhagavad Gita — URL pattern: /bg/chapter/verse (2-level).
    Some verses are combined (e.g. 42-43). On 404, probe combined slugs."""
    total = 0
    chapters = sorted(BG_CHAPTERS.keys())
    if chapter_filter:
        chapters = [ch for ch in chapters if ch == chapter_filter]

    for ch in chapters:
        max_verse = BG_CHAPTERS[ch]
        ch_fetched = 0
        skip_to = 0  # skip verses consumed by a combined slug

        for verse in range(1, max_verse + 1):
            if verse <= skip_to:
                continue

            ref = f"BG {ch}.{verse}"
            slug = str(verse)
            url = f"{base_url}/bg/{ch}/{slug}"
            vfile = verse_dir / f"{ch}_{slug}.json"

            if ref in existing_ids:
                continue
            if vfile.exists() and not force:
                continue

            try:
                r = requests.get(url, timeout=20, headers={
                    "User-Agent": "AtlasResearch/1.0 (academic)"})
                if r.status_code == 404:
                    # Try combined verse: verse-(verse+1), verse-(verse+2), etc.
                    found = False
                    for span in range(2, 6):
                        combo = f"{verse}-{verse + span - 1}"
                        combo_url = f"{base_url}/bg/{ch}/{combo}"
                        try:
                            rc = requests.get(combo_url, timeout=20, headers={
                                "User-Agent": "AtlasResearch/1.0 (academic)"})
                            if rc.status_code == 200:
                                r = rc
                                slug = combo
                                ref = f"BG {ch}.{combo}"
                                url = combo_url
                                vfile = verse_dir / f"{ch}_{combo}.json"
                                skip_to = verse + span - 1
                                found = True
                                break
                        except Exception:
                            pass
                    if not found:
                        continue
                else:
                    r.raise_for_status()
            except Exception as exc:
                if "404" in str(exc):
                    continue
                print(f"  ERR {ref}: {exc}")
                continue

            data = _extract_pb_verse(r.text)
            data["verse_ref"] = ref
            data["url"] = url

            vfile.write_text(json.dumps(data, ensure_ascii=False),
                             encoding="utf-8")

            text = data["translation"]
            if data["purport"]:
                text += "\n\n" + data["purport"]
            if text.strip():
                chunk = {
                    "id": chunk_id,
                    "verse_ref": ref,
                    "domain": "gaudiya",
                    "authority": "shastra",
                    "translator": "AC Bhaktivedanta Swami Prabhupada",
                    "text": text[:2000],
                    "sanskrit": data.get("iast", ""),
                    "source": "bg",
                }
                chunks_f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
                chunk_id += 1

            total += 1
            ch_fetched += 1
            if total % 10 == 0:
                print(f"  {ref} ({total})")
            time.sleep(0.5)

        print(f"  BG ch.{ch}: {ch_fetched} verse pages fetched")

    print(f"\n✦ Bhagavad Gita: {total} verse pages fetched")


def _crawl_cc(base_url, verse_dir, chunks_f, existing_ids, chunk_id, force):
    """Crawl Caitanya Caritamrta (adi/madhya/antya)."""
    total = 0
    for lila, max_ch in CC_STRUCTURE.items():
        for ch in range(1, max_ch + 1):
            for verse in range(1, 400):
                ref = f"CC {lila.title()} {ch}.{verse}"
                if ref in existing_ids:
                    continue
                url = f"{base_url}/cc/{lila}/{ch}/{verse}"
                try:
                    r = requests.get(url, timeout=20, headers={
                        "User-Agent": "AtlasResearch/1.0 (academic)"})
                    if r.status_code == 404:
                        break
                    r.raise_for_status()
                except Exception:
                    break

                data = _extract_pb_verse(r.text)
                data["verse_ref"] = ref
                text = data["translation"]
                if data["purport"]:
                    text += "\n\n" + data["purport"]
                if text.strip():
                    chunk = {
                        "id": chunk_id,
                        "verse_ref": ref,
                        "domain": "gaudiya",
                        "authority": "shastra",
                        "translator": "AC Bhaktivedanta Swami Prabhupada",
                        "text": text[:2000],
                        "sanskrit": data.get("iast", ""),
                        "source": "cc",
                    }
                    chunks_f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
                    chunk_id += 1
                total += 1
                if total % 10 == 0:
                    print(f"  {ref} ({total})")
                time.sleep(0.5)
        print(f"  CC {lila.title()} done ({total})")


# ── Main ──────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Fetch canonical texts")
    parser.add_argument("--domain", help="Fetch only this domain")
    parser.add_argument("--force", action="store_true",
                        help="Re-fetch even if cached")
    parser.add_argument("--source", help="Specific source (e.g. prabhupadabooks)")
    parser.add_argument("--book", default="sb",
                        help="For prabhupadabooks: sb, bg, or cc")
    parser.add_argument("--chapter", type=int, default=None,
                        help="Crawl only this chapter (for testing)")
    args = parser.parse_args()

    # Special source: prabhupadabooks crawler
    if args.source == "prabhupadabooks":
        crawl_prabhupadabooks(book=args.book, force=args.force,
                              chapter_filter=args.chapter)
        return

    texts = TEXTS
    if args.domain:
        texts = [t for t in texts if t["domain"] == args.domain]
        if not texts:
            print(f"No texts for domain: {args.domain}")
            print(f"Available: {sorted(set(t['domain'] for t in TEXTS))}")
            return

    print(f"✦ Atlas text harvester — {len(texts)} sources")
    print(f"  Target: {SOURCES}")
    print()

    manifest = []
    for entry in texts:
        result = fetch_one(entry, force=args.force)
        manifest.append(result)

    # Write manifest
    manifest_path = SOURCES / "manifest.json"
    # Merge with existing manifest
    existing = {}
    if manifest_path.exists():
        try:
            for item in json.loads(manifest_path.read_text()):
                existing[item["id"]] = item
        except Exception:
            pass
    for item in manifest:
        existing[item["id"]] = item

    manifest_path.write_text(
        json.dumps(list(existing.values()), indent=2, ensure_ascii=False),
        encoding="utf-8")

    # Summary
    print()
    fetched = sum(1 for m in manifest if m["status"] == "fetched")
    cached = sum(1 for m in manifest if m["status"] == "cached")
    inline = sum(1 for m in manifest if m["status"] == "inline")
    failed = sum(1 for m in manifest if m["status"] == "failed")
    total_bytes = sum(m.get("size_bytes", 0) for m in manifest)
    print(f"✦ Done: {fetched} fetched, {cached} cached, "
          f"{inline} inline, {failed} failed")
    print(f"  Total: {total_bytes:,} bytes across {len(manifest)} sources")
    print(f"  Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
