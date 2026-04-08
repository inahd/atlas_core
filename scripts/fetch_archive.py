#!/usr/bin/env python3
"""
fetch_archive.py — Comprehensive literature harvester for Atlas archive.

Fetches Sanskrit originals from GRETIL and English translations from Archive.org.
Covers: vastu, jyotish, ayurveda, yoga, music, cosmology, epics, gaudiya, vedic, dharma.

Usage:
  python3 scripts/fetch_archive.py --all              # fetch everything
  python3 scripts/fetch_archive.py --domain vastu      # one domain
  python3 scripts/fetch_archive.py --domain jyotish --domain vedic  # multiple
  python3 scripts/fetch_archive.py --list              # list all texts
  python3 scripts/fetch_archive.py --archive-only      # only Archive.org
  python3 scripts/fetch_archive.py --gretil-only       # only GRETIL
  python3 scripts/fetch_archive.py --force             # re-fetch cached

Designed to run overnight. Respects rate limits (1s between Archive.org requests).
"""

import argparse
import json
import os
import re
import sys
import time
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from threading import Lock

try:
    import requests
except ImportError:
    print("pip install requests")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "datasets" / "sources"

# ── GRETIL mirror base ──────────────────────────────────────────
_G = "https://raw.githubusercontent.com/INDOLOGY/GRETIL-mirror/master/gretil.sub.uni-goettingen.de/gretil"
_G1 = f"{_G}/1_sanskr"
_G2 = f"{_G}/2_pali"

# Rate limiting
_archive_lock = Lock()
_last_archive_req = [0.0]

CHUNK_SIZE = 600
CHUNK_OVERLAP = 60

# ── Source catalog ──────────────────────────────────────────────
# Each entry: id, name, domain, authority, sources[]
#   source type: "gretil" (url) or "archive" (search query)

TEXTS = [
    # �══════════════════════════════════════════════════════════════
    #  VASTU & ARCHITECTURE
    # ╚════════════════════════════════════════════════════════════
    {
        "id": "brihat_samhita",
        "name": "Brihat Samhita (Varahamihira)",
        "domain": "vastu",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/6_sastra/8_jyot/brhats_u.htm", "format": "html", "lang": "sa"},
            {"type": "archive", "query": "brihat samhita varahamihira english", "lang": "en"},
        ],
    },
    {
        "id": "vishvakarma_prakash",
        "name": "Vishvakarma Prakash",
        "domain": "vastu",
        "authority": "shastra",
        "sources": [
            {"type": "archive", "query": "vishvakarma prakash", "lang": "en"},
        ],
    },
    {
        "id": "manasara",
        "name": "Manasara (architecture treatise)",
        "domain": "vastu",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/6_sastra/6_kala/manasaru.htm", "format": "html", "lang": "sa"},
            {"type": "archive", "query": "manasara vastu architecture", "lang": "en"},
        ],
    },
    {
        "id": "mayamata",
        "name": "Mayamata (temple architecture)",
        "domain": "vastu",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/6_sastra/6_kala/mayamatu.htm", "format": "html", "lang": "sa"},
            {"type": "archive", "query": "mayamata temple architecture", "lang": "en"},
        ],
    },
    # ╚════════════════════════════════════════════════════════════
    #  JYOTISH
    # ╚════════════════════════════════════════════════════════════
    {
        "id": "brihat_parashara_hora",
        "name": "Brihat Parashara Hora Shastra",
        "domain": "jyotish",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/6_sastra/8_jyot/brhphs_u.htm", "format": "html", "lang": "sa"},
            {"type": "archive", "query": "brihat parashara hora shastra english", "lang": "en"},
        ],
    },
    {
        "id": "brihat_jataka",
        "name": "Brihat Jataka (Varahamihira)",
        "domain": "jyotish",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/6_sastra/8_jyot/brhajj_u.htm", "format": "html", "lang": "sa"},
            {"type": "archive", "query": "brihat jataka varahamihira english", "lang": "en"},
        ],
    },
    {
        "id": "saravali",
        "name": "Saravali (Kalyanvarma)",
        "domain": "jyotish",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/6_sastra/8_jyot/saravu_u.htm", "format": "html", "lang": "sa"},
            {"type": "archive", "query": "saravali kalyanvarma jyotish", "lang": "en"},
        ],
    },
    {
        "id": "phala_deepika",
        "name": "Phala Deepika (Mantreswara)",
        "domain": "jyotish",
        "authority": "shastra",
        "sources": [
            {"type": "archive", "query": "phala deepika translation mantreswara", "lang": "en"},
        ],
    },
    {
        "id": "jataka_parijata",
        "name": "Jataka Parijata",
        "domain": "jyotish",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/6_sastra/8_jyot/jatparu.htm", "format": "html", "lang": "sa"},
            {"type": "archive", "query": "jataka parijata english", "lang": "en"},
        ],
    },
    {
        "id": "uttara_kalamrita",
        "name": "Uttara Kalamrita",
        "domain": "jyotish",
        "authority": "shastra",
        "sources": [
            {"type": "archive", "query": "uttara kalamrita jyotish", "lang": "en"},
        ],
    },
    {
        "id": "surya_siddhanta",
        "name": "Surya Siddhanta",
        "domain": "jyotish",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/6_sastra/8_jyot/surysidu.htm", "format": "html", "lang": "sa"},
            {"type": "archive", "query": "surya siddhanta english translation", "lang": "en"},
        ],
    },
    # ╚════════════════════════════════════════════════════════════
    #  AYURVEDA
    # ╚════════════════════════════════════════════════════════════
    {
        "id": "charaka_samhita",
        "name": "Charaka Samhita",
        "domain": "ayurveda",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/6_sastra/7_ayur/caraka_u.htm", "format": "html", "lang": "sa"},
            {"type": "archive", "query": "charaka samhita english translation", "lang": "en"},
        ],
    },
    {
        "id": "sushruta_samhita",
        "name": "Sushruta Samhita",
        "domain": "ayurveda",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/6_sastra/7_ayur/susrutu.htm", "format": "html", "lang": "sa"},
            {"type": "archive", "query": "sushruta samhita english translation", "lang": "en"},
        ],
    },
    {
        "id": "ashtanga_hridayam",
        "name": "Ashtanga Hridayam (Vagbhata)",
        "domain": "ayurveda",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/6_sastra/7_ayur/asthd_u.htm", "format": "html", "lang": "sa"},
            {"type": "archive", "query": "ashtanga hridayam vagbhata english", "lang": "en"},
        ],
    },
    {
        "id": "ashtanga_sangraha",
        "name": "Ashtanga Sangraha",
        "domain": "ayurveda",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/6_sastra/7_ayur/astsan_u.htm", "format": "html", "lang": "sa"},
            {"type": "archive", "query": "ashtanga sangraha ayurveda english", "lang": "en"},
        ],
    },
    {
        "id": "bhavaprakasha",
        "name": "Bhavaprakasha (herbal pharmacopoeia)",
        "domain": "ayurveda",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/6_sastra/7_ayur/bhavpr_u.htm", "format": "html", "lang": "sa"},
        ],
    },
    # ╚════════════════════════════════════════════════════════════
    #  YOGA & TANTRA
    # ╚════════════════════════════════════════════════════════════
    {
        "id": "yoga_sutras",
        "name": "Yoga Sutras (Patanjali)",
        "domain": "yoga",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/6_sastra/3_phil/yoga/yogasutu.htm", "format": "html", "lang": "sa"},
            {"type": "archive", "query": "yoga sutras patanjali english", "lang": "en"},
        ],
    },
    {
        "id": "hatha_yoga_pradipika",
        "name": "Hatha Yoga Pradipika",
        "domain": "yoga",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/6_sastra/3_phil/yoga/hathyopu.htm", "format": "html", "lang": "sa"},
            {"type": "archive", "query": "hatha yoga pradipika english", "lang": "en"},
        ],
    },
    {
        "id": "gheranda_samhita",
        "name": "Gheranda Samhita",
        "domain": "yoga",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/6_sastra/3_phil/yoga/ghers__u.htm", "format": "html", "lang": "sa"},
            {"type": "archive", "query": "gheranda samhita english", "lang": "en"},
        ],
    },
    {
        "id": "shiva_samhita",
        "name": "Shiva Samhita",
        "domain": "yoga",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/6_sastra/3_phil/yoga/sivsam_u.htm", "format": "html", "lang": "sa"},
            {"type": "archive", "query": "shiva samhita english translation", "lang": "en"},
        ],
    },
    {
        "id": "vijnana_bhairava",
        "name": "Vijnana Bhairava Tantra",
        "domain": "yoga",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/6_sastra/3_phil/saiva/vijbht_u.htm", "format": "html", "lang": "sa"},
            {"type": "archive", "query": "vijnana bhairava tantra english", "lang": "en"},
        ],
    },
    {
        "id": "tantraloka",
        "name": "Tantraloka (Abhinavagupta)",
        "domain": "yoga",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/6_sastra/3_phil/saiva/tantralu.htm", "format": "html", "lang": "sa"},
            {"type": "archive", "query": "tantraloka abhinavagupta", "lang": "en"},
        ],
    },
    {
        "id": "kularnava_tantra",
        "name": "Kularnava Tantra",
        "domain": "yoga",
        "authority": "shastra",
        "sources": [
            {"type": "archive", "query": "kularnava tantra english", "lang": "en"},
        ],
    },
    {
        "id": "mahanirvana_tantra",
        "name": "Mahanirvana Tantra",
        "domain": "yoga",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/6_sastra/3_phil/tantra/mahntanu.htm", "format": "html", "lang": "sa"},
            {"type": "archive", "query": "mahanirvana tantra english", "lang": "en"},
        ],
    },
    # ╚════════════════════════════════════════════════════════════
    #  GANDHARVA VEDA / MUSIC
    # ╚════════════════════════════════════════════════════════════
    {
        "id": "natyashastra",
        "name": "Natyashastra (Bharata)",
        "domain": "music",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/6_sastra/6_kala/natyasu.htm", "format": "html", "lang": "sa"},
            {"type": "archive", "query": "natyashastra bharata music chapters english", "lang": "en"},
        ],
    },
    {
        "id": "sangita_ratnakara",
        "name": "Sangita Ratnakara (Sarangadeva)",
        "domain": "music",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/6_sastra/6_kala/sangratu.htm", "format": "html", "lang": "sa"},
            {"type": "archive", "query": "sangita ratnakara sarangadeva english", "lang": "en"},
        ],
    },
    {
        "id": "brihaddeshi",
        "name": "Brihaddeshi (Matanga)",
        "domain": "music",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/6_sastra/6_kala/brhdsh_u.htm", "format": "html", "lang": "sa"},
            {"type": "archive", "query": "brihaddeshi matanga raga english", "lang": "en"},
        ],
    },
    # ╚════════════════════════════════════════════════════════════
    #  COSMOLOGY & PURANAS
    # ╚════════════════════════════════════════════════════════════
    {
        "id": "vishnu_purana",
        "name": "Vishnu Purana",
        "domain": "cosmology",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/3_purana/visnp__u.htm", "format": "html", "lang": "sa"},
            {"type": "archive", "query": "vishnu purana english wilson translation", "lang": "en"},
        ],
    },
    {
        "id": "devi_bhagavata",
        "name": "Devi Bhagavata Purana",
        "domain": "cosmology",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/3_purana/devibhpu.htm", "format": "html", "lang": "sa"},
            {"type": "archive", "query": "devi bhagavata purana english", "lang": "en"},
        ],
    },
    {
        "id": "markandeya_purana",
        "name": "Markandeya Purana (Devi Mahatmya)",
        "domain": "cosmology",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/3_purana/markp__u.htm", "format": "html", "lang": "sa"},
            {"type": "archive", "query": "markandeya purana devi mahatmya english", "lang": "en"},
        ],
    },
    {
        "id": "shiva_purana",
        "name": "Shiva Purana",
        "domain": "cosmology",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/3_purana/sivap__u.htm", "format": "html", "lang": "sa"},
            {"type": "archive", "query": "shiva purana english translation", "lang": "en"},
        ],
    },
    {
        "id": "brahma_vaivarta_purana",
        "name": "Brahma Vaivarta Purana",
        "domain": "cosmology",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/3_purana/brahmvpu.htm", "format": "html", "lang": "sa"},
            {"type": "archive", "query": "brahma vaivarta purana english", "lang": "en"},
        ],
    },
    # ╚════════════════════════════════════════════════════════════
    #  EPICS
    # ╚════════════════════════════════════════════════════════════
    {
        "id": "mahabharata",
        "name": "Mahabharata (Vyasa)",
        "domain": "epics",
        "authority": "shastra",
        "sources": [
            # GRETIL has it split into parvans — fetch the main index
            {"type": "gretil", "url": f"{_G1}/2_epic/mbh/mbh_01_u.htm", "format": "html", "lang": "sa", "note": "Adi Parva"},
            {"type": "gretil", "url": f"{_G1}/2_epic/mbh/mbh_02_u.htm", "format": "html", "lang": "sa", "note": "Sabha Parva"},
            {"type": "gretil", "url": f"{_G1}/2_epic/mbh/mbh_03_u.htm", "format": "html", "lang": "sa", "note": "Vana Parva"},
            {"type": "gretil", "url": f"{_G1}/2_epic/mbh/mbh_04_u.htm", "format": "html", "lang": "sa", "note": "Virata Parva"},
            {"type": "gretil", "url": f"{_G1}/2_epic/mbh/mbh_05_u.htm", "format": "html", "lang": "sa", "note": "Udyoga Parva"},
            {"type": "gretil", "url": f"{_G1}/2_epic/mbh/mbh_06_u.htm", "format": "html", "lang": "sa", "note": "Bhishma Parva"},
            {"type": "gretil", "url": f"{_G1}/2_epic/mbh/mbh_07_u.htm", "format": "html", "lang": "sa", "note": "Drona Parva"},
            {"type": "gretil", "url": f"{_G1}/2_epic/mbh/mbh_08_u.htm", "format": "html", "lang": "sa", "note": "Karna Parva"},
            {"type": "gretil", "url": f"{_G1}/2_epic/mbh/mbh_09_u.htm", "format": "html", "lang": "sa", "note": "Shalya Parva"},
            {"type": "gretil", "url": f"{_G1}/2_epic/mbh/mbh_10_u.htm", "format": "html", "lang": "sa", "note": "Sauptika Parva"},
            {"type": "gretil", "url": f"{_G1}/2_epic/mbh/mbh_11_u.htm", "format": "html", "lang": "sa", "note": "Stri Parva"},
            {"type": "gretil", "url": f"{_G1}/2_epic/mbh/mbh_12_u.htm", "format": "html", "lang": "sa", "note": "Shanti Parva"},
            {"type": "gretil", "url": f"{_G1}/2_epic/mbh/mbh_13_u.htm", "format": "html", "lang": "sa", "note": "Anushasana Parva"},
            {"type": "gretil", "url": f"{_G1}/2_epic/mbh/mbh_14_u.htm", "format": "html", "lang": "sa", "note": "Ashvamedhika Parva"},
            {"type": "gretil", "url": f"{_G1}/2_epic/mbh/mbh_15_u.htm", "format": "html", "lang": "sa", "note": "Ashramvasika Parva"},
            {"type": "gretil", "url": f"{_G1}/2_epic/mbh/mbh_16_u.htm", "format": "html", "lang": "sa", "note": "Mausala Parva"},
            {"type": "gretil", "url": f"{_G1}/2_epic/mbh/mbh_17_u.htm", "format": "html", "lang": "sa", "note": "Mahaprasthanika Parva"},
            {"type": "gretil", "url": f"{_G1}/2_epic/mbh/mbh_18_u.htm", "format": "html", "lang": "sa", "note": "Svargarohanika Parva"},
            {"type": "archive", "query": "mahabharata ganguli translation complete", "lang": "en"},
        ],
    },
    {
        "id": "ramayana",
        "name": "Ramayana (Valmiki)",
        "domain": "epics",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/2_epic/ram/ram_1_u.htm", "format": "html", "lang": "sa", "note": "Bala Kanda"},
            {"type": "gretil", "url": f"{_G1}/2_epic/ram/ram_2_u.htm", "format": "html", "lang": "sa", "note": "Ayodhya Kanda"},
            {"type": "gretil", "url": f"{_G1}/2_epic/ram/ram_3_u.htm", "format": "html", "lang": "sa", "note": "Aranya Kanda"},
            {"type": "gretil", "url": f"{_G1}/2_epic/ram/ram_4_u.htm", "format": "html", "lang": "sa", "note": "Kishkindha Kanda"},
            {"type": "gretil", "url": f"{_G1}/2_epic/ram/ram_5_u.htm", "format": "html", "lang": "sa", "note": "Sundara Kanda"},
            {"type": "gretil", "url": f"{_G1}/2_epic/ram/ram_6_u.htm", "format": "html", "lang": "sa", "note": "Yuddha Kanda"},
            {"type": "gretil", "url": f"{_G1}/2_epic/ram/ram_7_u.htm", "format": "html", "lang": "sa", "note": "Uttara Kanda"},
            {"type": "archive", "query": "ramayana valmiki english translation", "lang": "en"},
        ],
    },
    {
        "id": "harivamsa",
        "name": "Harivamsa",
        "domain": "epics",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/2_epic/harivamu.htm", "format": "html", "lang": "sa"},
            {"type": "archive", "query": "harivamsa english translation", "lang": "en"},
        ],
    },
    # ╚════════════════════════════════════════════════════════════
    #  GAUDIYA (additions to existing)
    # ╚════════════════════════════════════════════════════════════
    {
        "id": "bhakti_rasamrita_sindhu",
        "name": "Bhakti Rasamrita Sindhu (Rupa Gosvami)",
        "domain": "gaudiya",
        "authority": "shastra",
        "sources": [
            {"type": "archive", "query": "bhakti rasamrita sindhu rupa gosvami", "lang": "en"},
            {"type": "archive", "query": "nectar of devotion prabhupada", "lang": "en"},
        ],
    },
    {
        "id": "ujjvala_nilamani",
        "name": "Ujjvala Nilamani (Rupa Gosvami)",
        "domain": "gaudiya",
        "authority": "shastra",
        "sources": [
            {"type": "archive", "query": "ujjvala nilamani rupa gosvami", "lang": "en"},
        ],
    },
    {
        "id": "brihad_bhagavatamrita",
        "name": "Brihad Bhagavatamrita (Sanatana Gosvami)",
        "domain": "gaudiya",
        "authority": "shastra",
        "sources": [
            {"type": "archive", "query": "brihad bhagavatamrita sanatana gosvami", "lang": "en"},
        ],
    },
    {
        "id": "hari_bhakti_vilasa",
        "name": "Hari Bhakti Vilasa (Sanatana Gosvami)",
        "domain": "gaudiya",
        "authority": "shastra",
        "sources": [
            {"type": "archive", "query": "hari bhakti vilasa sanatana gosvami", "lang": "en"},
        ],
    },
    {
        "id": "vedanta_sutra",
        "name": "Vedanta Sutra (Brahma Sutra)",
        "domain": "gaudiya",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/6_sastra/3_phil/vedanta/brahmsbu.htm", "format": "html", "lang": "sa"},
            {"type": "archive", "query": "vedanta sutra brahma sutra english commentary", "lang": "en"},
        ],
    },
    # ╚════════════════════════════════════════════════════════════
    #  VEDIC (Samhitas + Upanishads)
    # ╚════════════════════════════════════════════════════════════
    {
        "id": "rigveda",
        "name": "Rigveda",
        "domain": "vedic",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/1_veda/1_sam/rv_asa_u.htm", "format": "html", "lang": "sa"},
            {"type": "archive", "query": "rigveda english translation griffith", "lang": "en"},
        ],
    },
    {
        "id": "atharvaveda",
        "name": "Atharvaveda",
        "domain": "vedic",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/1_veda/1_sam/av_pipp_u.htm", "format": "html", "lang": "sa"},
            {"type": "archive", "query": "atharvaveda english translation", "lang": "en"},
        ],
    },
    {
        "id": "isha_upanishad",
        "name": "Isha Upanishad",
        "domain": "vedic",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/1_veda/4_upa/isup___u.htm", "format": "html", "lang": "sa"},
        ],
    },
    {
        "id": "kena_upanishad",
        "name": "Kena Upanishad",
        "domain": "vedic",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/1_veda/4_upa/kenup__u.htm", "format": "html", "lang": "sa"},
        ],
    },
    {
        "id": "katha_upanishad",
        "name": "Katha Upanishad",
        "domain": "vedic",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/1_veda/4_upa/katup__u.htm", "format": "html", "lang": "sa"},
        ],
    },
    {
        "id": "mundaka_upanishad",
        "name": "Mundaka Upanishad",
        "domain": "vedic",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/1_veda/4_upa/munup__u.htm", "format": "html", "lang": "sa"},
        ],
    },
    {
        "id": "mandukya_upanishad",
        "name": "Mandukya Upanishad",
        "domain": "vedic",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/1_veda/4_upa/mauup__u.htm", "format": "html", "lang": "sa"},
        ],
    },
    {
        "id": "taittiriya_upanishad",
        "name": "Taittiriya Upanishad",
        "domain": "vedic",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/1_veda/4_upa/taiup__u.htm", "format": "html", "lang": "sa"},
        ],
    },
    {
        "id": "chandogya_upanishad",
        "name": "Chandogya Upanishad",
        "domain": "vedic",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/1_veda/4_upa/chaup__u.htm", "format": "html", "lang": "sa"},
        ],
    },
    {
        "id": "brihadaranyaka_upanishad",
        "name": "Brihadaranyaka Upanishad",
        "domain": "vedic",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/1_veda/4_upa/brhup__u.htm", "format": "html", "lang": "sa"},
        ],
    },
    {
        "id": "prashna_upanishad",
        "name": "Prashna Upanishad",
        "domain": "vedic",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/1_veda/4_upa/praup__u.htm", "format": "html", "lang": "sa"},
        ],
    },
    {
        "id": "aitareya_upanishad",
        "name": "Aitareya Upanishad",
        "domain": "vedic",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/1_veda/4_upa/aitup__u.htm", "format": "html", "lang": "sa"},
        ],
    },
    {
        "id": "shvetashvatara_upanishad",
        "name": "Shvetashvatara Upanishad",
        "domain": "vedic",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/1_veda/4_upa/sveup__u.htm", "format": "html", "lang": "sa"},
        ],
    },
    {
        "id": "upanishads_english",
        "name": "Principal Upanishads (English translations)",
        "domain": "vedic",
        "authority": "sadhu",
        "sources": [
            {"type": "archive", "query": "principal upanishads english radhakrishnan", "lang": "en"},
            {"type": "archive", "query": "upanishads max muller sacred books east", "lang": "en"},
        ],
    },
    # ╚════════════════════════════════════════════════════════════
    #  DHARMASHASTRA
    # ╚════════════════════════════════════════════════════════════
    {
        "id": "manusmriti",
        "name": "Manusmriti (Laws of Manu)",
        "domain": "dharma",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/6_sastra/4_dharma/manu2__u.htm", "format": "html", "lang": "sa"},
            {"type": "archive", "query": "manusmriti laws of manu english buhler", "lang": "en"},
        ],
    },
    {
        "id": "arthashastra",
        "name": "Arthashastra (Kautilya)",
        "domain": "dharma",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/6_sastra/4_dharma/kautlyu.htm", "format": "html", "lang": "sa"},
            {"type": "archive", "query": "arthashastra kautilya english translation", "lang": "en"},
        ],
    },
    {
        "id": "nitisara",
        "name": "Nitisara (Kamandaki)",
        "domain": "dharma",
        "authority": "shastra",
        "sources": [
            {"type": "gretil", "url": f"{_G1}/6_sastra/4_dharma/kanitisu.htm", "format": "html", "lang": "sa"},
            {"type": "archive", "query": "nitisara kamandaki english", "lang": "en"},
        ],
    },
]


# ── HTML / XML stripping ────────────────────────────────────────

def strip_html(html: str) -> str:
    """Remove HTML tags, decode entities, clean whitespace."""
    text = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', html,
                  flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', text)
    for ent, ch in [('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>'),
                    ('&quot;', '"'), ('&nbsp;', ' '), ('&#39;', "'"),
                    ('&apos;', "'")]:
        text = text.replace(ent, ch)
    # Decode numeric entities
    text = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), text)
    text = re.sub(r'&#x([0-9a-fA-F]+);', lambda m: chr(int(m.group(1), 16)), text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


# ── Chunker ─────────────────────────────────────────────────────

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE,
               overlap: int = CHUNK_OVERLAP) -> list:
    """Split text into overlapping chunks, respecting verse boundaries."""
    chunks = []
    pos = 0
    idx = 0
    while pos < len(text):
        end = min(pos + chunk_size, len(text))
        if end < len(text):
            # Try to break at verse/paragraph boundary
            for sep in ['\n\n', '॥', '||', '\n', '. ']:
                bp = text.rfind(sep, pos + chunk_size // 2, end + 100)
                if bp > pos:
                    end = bp + len(sep)
                    break
        chunk = text[pos:end].strip()
        if chunk:
            # Try to extract verse reference from chunk
            verse_ref = ""
            ref_m = re.search(r'(\d+[\.\-]\d+[\.\-]?\d*)', chunk[:80])
            if ref_m:
                verse_ref = ref_m.group(1)
            chunks.append({
                "id": idx,
                "char_start": pos,
                "char_end": end,
                "verse_ref": verse_ref,
                "text": chunk,
            })
            idx += 1
        pos = max(pos + 1, end - overlap)
    return chunks


# ── Archive.org fetcher ─────────────────────────────────────────

def _archive_rate_limit():
    """Enforce 1s between Archive.org requests."""
    with _archive_lock:
        elapsed = time.time() - _last_archive_req[0]
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)
        _last_archive_req[0] = time.time()


def search_archive(query: str, max_results: int = 5) -> list:
    """Search Archive.org, return list of {identifier, title}."""
    _archive_rate_limit()
    url = "https://archive.org/advancedsearch.php"
    params = {
        "q": query,
        "fl[]": ["identifier", "title", "mediatype"],
        "rows": max_results,
        "output": "json",
    }
    try:
        r = requests.get(url, params=params, timeout=30,
                         headers={"User-Agent": "AtlasResearch/1.0 (academic)"})
        r.raise_for_status()
        data = r.json()
        docs = data.get("response", {}).get("docs", [])
        # Prefer texts over other media types
        texts = [d for d in docs if d.get("mediatype") == "texts"]
        return texts if texts else docs[:max_results]
    except Exception as exc:
        print(f"    SEARCH ERR: {exc}")
        return []


def fetch_archive_text(identifier: str) -> str | None:
    """Download text version of an Archive.org item.

    Tries multiple text format patterns:
      1. {id}_djvu.txt (OCR text)
      2. {id}.txt
      3. First .txt file in the item's file listing
    """
    base = f"https://archive.org/download/{identifier}"

    # Try common text file patterns
    for suffix in [f"/{identifier}_djvu.txt",
                   f"/{identifier}.txt"]:
        _archive_rate_limit()
        try:
            r = requests.get(base + suffix, timeout=60,
                             headers={"User-Agent": "AtlasResearch/1.0 (academic)"},
                             stream=True)
            if r.status_code == 200:
                # Stream to avoid loading huge files entirely in memory
                content = []
                total = 0
                for chunk in r.iter_content(chunk_size=65536, decode_unicode=True):
                    if chunk:
                        content.append(chunk)
                        total += len(chunk)
                        if total > 50_000_000:  # 50MB cap
                            break
                return ''.join(content)
        except Exception:
            continue

    # Fallback: check item metadata for .txt files
    _archive_rate_limit()
    try:
        meta_url = f"https://archive.org/metadata/{identifier}/files"
        r = requests.get(meta_url, timeout=30,
                         headers={"User-Agent": "AtlasResearch/1.0 (academic)"})
        if r.status_code == 200:
            files = r.json().get("result", [])
            txt_files = [f for f in files
                         if f.get("name", "").endswith(".txt")
                         and int(f.get("size", 0)) > 100]
            # Sort by size descending — largest txt is usually the full text
            txt_files.sort(key=lambda f: int(f.get("size", 0)), reverse=True)
            for tf in txt_files[:3]:
                _archive_rate_limit()
                try:
                    r2 = requests.get(f"{base}/{tf['name']}", timeout=60,
                                      headers={"User-Agent": "AtlasResearch/1.0 (academic)"})
                    if r2.status_code == 200 and len(r2.text) > 200:
                        return r2.text[:50_000_000]
                except Exception:
                    continue
    except Exception:
        pass

    return None


# ── GRETIL fetcher ──────────────────────────────────────────────

def fetch_gretil(url: str, fmt: str = "html") -> str | None:
    """Fetch a text from GRETIL mirror. Returns cleaned text or None."""
    for attempt in range(3):
        try:
            r = requests.get(url, timeout=30,
                             headers={"User-Agent": "AtlasResearch/1.0 (academic)"})
            if r.status_code == 404:
                # Try alternate URL patterns
                alt = url.replace("_u.htm", ".htm")
                if alt != url:
                    r = requests.get(alt, timeout=30,
                                     headers={"User-Agent": "AtlasResearch/1.0 (academic)"})
                if r.status_code == 404:
                    return None
            r.raise_for_status()
            if fmt == "html":
                return strip_html(r.text)
            return r.text
        except requests.exceptions.HTTPError:
            return None
        except Exception as exc:
            if attempt < 2:
                time.sleep(2 ** attempt)
            else:
                print(f"    GRETIL ERR: {exc}")
    return None


# ── Core fetch logic ────────────────────────────────────────────

def fetch_text_entry(entry: dict, force: bool = False,
                     gretil_only: bool = False,
                     archive_only: bool = False) -> dict:
    """Fetch all sources for a single text entry. Returns manifest record."""
    text_id = entry["id"]
    domain = entry["domain"]
    domain_dir = SOURCES / domain
    domain_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "id": text_id,
        "name": entry["name"],
        "domain": domain,
        "authority": entry["authority"],
        "files": [],
        "status": "pending",
        "fetched_at": datetime.now().isoformat(),
    }

    sources = entry.get("sources", [])
    any_success = False

    for i, src in enumerate(sources):
        src_type = src["type"]
        lang = src.get("lang", "en")

        if gretil_only and src_type != "gretil":
            continue
        if archive_only and src_type != "archive":
            continue

        # File naming: {id}_{lang}[_{i}].txt
        suffix = f"_{lang}" if len([s for s in sources if s.get("lang") == lang]) > 1 else f"_{lang}"
        if i > 0 and any(s.get("lang") == lang for s in sources[:i]):
            suffix += f"_{i}"
        raw_path = domain_dir / f"{text_id}{suffix}.txt"
        chunks_path = domain_dir / f"{text_id}{suffix}_chunks.jsonl"

        # Check cache
        if raw_path.exists() and raw_path.stat().st_size > 100 and not force:
            print(f"  CACHED {text_id}{suffix} ({raw_path.stat().st_size:,} bytes)")
            result["files"].append({
                "path": str(raw_path.relative_to(ROOT)),
                "lang": lang,
                "source": src_type,
                "size": raw_path.stat().st_size,
                "status": "cached",
            })
            any_success = True
            # Ensure chunks exist
            if not chunks_path.exists():
                _write_chunks(raw_path, chunks_path, entry)
            continue

        text = None

        if src_type == "gretil":
            url = src["url"]
            note = src.get("note", "")
            label = f"{text_id}{suffix}"
            if note:
                label += f" ({note})"
            print(f"  GRETIL {label}...")
            text = fetch_gretil(url, src.get("format", "html"))
            if text:
                print(f"    OK {len(text):,} chars")
            else:
                print(f"    NOT FOUND at {url.split('/')[-1]}")

        elif src_type == "archive":
            query = src["query"]
            print(f"  ARCHIVE search: \"{query}\"...")
            results = search_archive(query, max_results=5)
            if not results:
                print(f"    NO RESULTS")
            else:
                for item in results:
                    ident = item.get("identifier", "")
                    title = item.get("title", "")
                    print(f"    trying: {ident} — {title[:60]}")
                    text = fetch_archive_text(ident)
                    if text and len(text) > 500:
                        print(f"    OK {len(text):,} chars from {ident}")
                        break
                    else:
                        text = None
                if not text:
                    print(f"    NO TEXT FOUND in any result")

        if text:
            raw_path.write_text(text, encoding="utf-8")
            _write_chunks(raw_path, chunks_path, entry)
            result["files"].append({
                "path": str(raw_path.relative_to(ROOT)),
                "lang": lang,
                "source": src_type,
                "size": len(text.encode("utf-8")),
                "status": "fetched",
                "archive_id": ident if src_type == "archive" else None,
            })
            any_success = True
        else:
            result["files"].append({
                "path": str(raw_path.relative_to(ROOT)),
                "lang": lang,
                "source": src_type,
                "size": 0,
                "status": "failed",
            })

    result["status"] = "ok" if any_success else "failed"
    return result


def _write_chunks(raw_path: Path, chunks_path: Path, entry: dict):
    """Chunk a raw text file into JSONL with metadata."""
    text = raw_path.read_text(encoding="utf-8")
    chunks = chunk_text(text)
    with open(chunks_path, "w", encoding="utf-8") as f:
        for chunk in chunks:
            chunk["source"] = entry["id"]
            chunk["domain"] = entry["domain"]
            chunk["authority"] = entry.get("authority", "shastra")
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    print(f"    CHUNK {len(chunks)} → {chunks_path.name}")


# ── Domain-parallel executor ────────────────────────────────────

def fetch_domain(domain: str, texts: list, force: bool = False,
                 gretil_only: bool = False, archive_only: bool = False) -> list:
    """Fetch all texts for a domain. Returns manifest entries."""
    domain_texts = [t for t in texts if t["domain"] == domain]
    if not domain_texts:
        return []

    print(f"\n{'═' * 60}")
    print(f"  {domain.upper()} — {len(domain_texts)} texts")
    print(f"{'═' * 60}")

    results = []
    for entry in domain_texts:
        try:
            result = fetch_text_entry(entry, force=force,
                                      gretil_only=gretil_only,
                                      archive_only=archive_only)
            results.append(result)
        except Exception as exc:
            print(f"  FATAL {entry['id']}: {exc}")
            results.append({
                "id": entry["id"],
                "name": entry["name"],
                "domain": domain,
                "authority": entry.get("authority", "shastra"),
                "status": "error",
                "error": str(exc),
                "files": [],
            })

    ok = sum(1 for r in results if r["status"] == "ok")
    fail = sum(1 for r in results if r["status"] != "ok")
    print(f"\n  {domain.upper()} summary: {ok} ok, {fail} failed")
    return results


# ── Main ────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Comprehensive literature harvester for Atlas archive")
    parser.add_argument("--all", action="store_true",
                        help="Fetch all domains")
    parser.add_argument("--domain", action="append", default=[],
                        help="Fetch specific domain(s)")
    parser.add_argument("--list", action="store_true",
                        help="List all texts and exit")
    parser.add_argument("--force", action="store_true",
                        help="Re-fetch even if cached")
    parser.add_argument("--gretil-only", action="store_true",
                        help="Only fetch from GRETIL")
    parser.add_argument("--archive-only", action="store_true",
                        help="Only fetch from Archive.org")
    parser.add_argument("--parallel", type=int, default=3,
                        help="Number of domains to fetch in parallel (default: 3)")
    args = parser.parse_args()

    all_domains = sorted(set(t["domain"] for t in TEXTS))

    if args.list:
        print(f"✦ Atlas archive catalog — {len(TEXTS)} texts across {len(all_domains)} domains\n")
        for domain in all_domains:
            dt = [t for t in TEXTS if t["domain"] == domain]
            print(f"  {domain.upper()} ({len(dt)} texts)")
            for t in dt:
                gretil = sum(1 for s in t["sources"] if s["type"] == "gretil")
                archive = sum(1 for s in t["sources"] if s["type"] == "archive")
                print(f"    {t['id']:40s} G:{gretil} A:{archive}  {t['name']}")
            print()
        return

    if not args.all and not args.domain:
        parser.print_help()
        print(f"\nAvailable domains: {', '.join(all_domains)}")
        return

    domains = all_domains if args.all else args.domain
    invalid = [d for d in domains if d not in all_domains]
    if invalid:
        print(f"Unknown domains: {invalid}")
        print(f"Available: {all_domains}")
        return

    total_texts = sum(1 for t in TEXTS if t["domain"] in domains)
    print(f"✦ Atlas archive harvester")
    print(f"  Domains: {', '.join(domains)}")
    print(f"  Texts:   {total_texts}")
    print(f"  Target:  {SOURCES}")
    if args.gretil_only:
        print(f"  Mode:    GRETIL only")
    elif args.archive_only:
        print(f"  Mode:    Archive.org only")
    print(f"  Started: {datetime.now().isoformat()}")
    print()

    all_results = []

    if len(domains) > 1 and args.parallel > 1:
        # Run domains in parallel
        with ThreadPoolExecutor(max_workers=min(args.parallel, len(domains))) as ex:
            futures = {}
            for domain in domains:
                f = ex.submit(fetch_domain, domain, TEXTS,
                              force=args.force,
                              gretil_only=args.gretil_only,
                              archive_only=args.archive_only)
                futures[f] = domain
            for f in as_completed(futures):
                domain = futures[f]
                try:
                    results = f.result()
                    all_results.extend(results)
                except Exception as exc:
                    print(f"DOMAIN {domain} FAILED: {exc}")
    else:
        for domain in domains:
            results = fetch_domain(domain, TEXTS,
                                   force=args.force,
                                   gretil_only=args.gretil_only,
                                   archive_only=args.archive_only)
            all_results.extend(results)

    # ── Update manifest ──────────────────────────────────────────
    manifest_path = SOURCES / "archive_manifest.json"
    existing = {}
    if manifest_path.exists():
        try:
            for item in json.loads(manifest_path.read_text()):
                existing[item["id"]] = item
        except Exception:
            pass
    for item in all_results:
        existing[item["id"]] = item

    manifest_path.write_text(
        json.dumps(list(existing.values()), indent=2, ensure_ascii=False),
        encoding="utf-8")

    # ── Summary ──────────────────────────────────────────────────
    ok = sum(1 for r in all_results if r["status"] == "ok")
    failed = sum(1 for r in all_results if r["status"] != "ok")
    total_files = sum(len(r.get("files", [])) for r in all_results)
    total_bytes = sum(
        f.get("size", 0)
        for r in all_results
        for f in r.get("files", [])
    )

    print(f"\n{'═' * 60}")
    print(f"  HARVEST COMPLETE")
    print(f"{'═' * 60}")
    print(f"  Texts:  {ok} ok / {failed} failed / {len(all_results)} total")
    print(f"  Files:  {total_files}")
    print(f"  Bytes:  {total_bytes:,}")
    print(f"  Manifest: {manifest_path}")
    print(f"  Finished: {datetime.now().isoformat()}")

    if failed:
        print(f"\n  Failed texts:")
        for r in all_results:
            if r["status"] != "ok":
                print(f"    {r['id']:40s} {r.get('error', 'no sources found')}")


if __name__ == "__main__":
    main()
