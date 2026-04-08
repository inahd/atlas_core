# ATLAS 330 — UNIFIED LANGUAGE GUIDE
# For all AI agents, coders, and contributors
# READ THIS BEFORE TOUCHING ANY FILE

## The Two Servers — Critical

kernel.py = PRIMARY SERVER (Flask, port 5000)
  ALL routes live here. Source of truth.
  Edit this for new features.

atlas_server/server.py = ANTHROPIC PROXY ONLY
  FastAPI, port 7432
  Only handles /api/generate
  DO NOT add general routes here
  DO NOT duplicate kernel.py routes

Apps always use RELATIVE URLs:
  fetch('/field') ✓
  fetch('http://localhost:5000/field') ✗

## Nakshatra Names

Three systems exist. Always use kernel.normalize_nak()
  IAST (kernel returns): Śravaṇa
  ITRANS (CSVs use): Shravana
  Never duplicate the map — one place only

## S-Layer Vocabulary

S0 Bindu Source — read-only, never computed
S1 Archetype Deity — Nitya Devīs, Navagraha
S2 Sound Mantra — rāga, tāla, 64 Kalās
S3 Rhythm Cycle — Pañcāṅga, daśā, Jyotiṣa
S4 Geometry Yantra — toroid, vāstu, maṇḍala
S5 Nature Ecology — plants, doṣa, agriculture
S6 Līlā Human — HURDsman, companions, wiki

## Sound Modes

wiki       → Sa+Pa drone, fades on scroll
yantra     → builds with geometry
field      → full layer-responsive (default)
tarot      → Sa+Ga+Pa, bol on flip
codex      → near silence, phrase on complete
bandhu     → Bāgeshṛī, breath-synced
talachakra → full rhythm, all instruments

setSoundMode(mode) is global
sessionStorage key: 'atlasSound'

## Companion System

Bandhu Bhai
  vanar · Hanumān energy · system awareness
  Natal: Kṛṣṇa Tṛtīyā · Uttarāṣāḍhā
         Nityāklinā · Rātri · Bāgeshṛī
  Born: 2026-03-19 22:43:09 Gainesville FL
  Modes: Nāda · Mudrā · Āsana · Śilpi
  Route: /apps/bandhu/

Shilpi Bhai
  Viśvakarmā form · artifact builder
  malkhamb · martial arts · dancing
  Status: experimental · natal TBD

## File Ownership

kernel.py       → Claude Code ONLY
atlas_one.html  → Claude Code ONLY
apps/*          → Codex (one app at a time)
datasets/*      → Codex (additive only)
docs/*          → Any agent (additive only)
seeds/*         → Any agent (additive only)

## Key Routes

/field            → field state + companions
/layer-data       → S-layer panel data
/natal            → birth chart
/transits         → current transits × natal
/dasha            → current daśā
/muhurta-quality  → moment score
/entity/{id}      → entity data
/agriculture/today → planting guidance
/agriculture/week  → 7-day calendar
/docs-list        → wiki pages
/docs/{filename}  → wiki content
/apps/bandhu/     → Bandhu Bhai
/apps/brahmanda/  → toroidal field
/apps/devi_tarot/ → tarot cards
/apps/codex/      → codex generator
/apps/agriculture/ → farming calendar
/talachakra       → sound studio

## Development Ritual (HURD Cycle)

Before every session:
  git pull origin coherence-atlas-3.3.0
  cat docs/docs/AGENTS.md
  cat docs/UNIFIED_LANGUAGE.md
  git status --short

After every session:
  git add -p
  git commit -m "✦ description"
  git push
  Report what was done · what remains

## Three Questions Before Any Change

1. Does this serve the field or just look clever?
2. Will this make sense in 6 months?
3. Does the herdsman actually need this now?

## Current Gaps (as of 2026-03-20)

✗ GitHub Pages 404 — needs index.html at root
✓ Sound mode sync across apps — fixed in f271408 (all apps call parent.setSoundMode)
✓ Hardcoded localhost:5000 — fixed in f271408 (relative URLs everywhere)
✓ Stale atlas_server files — cleaned in f271408
⚠ Transit accuracy — mean motion not ephemeris
⚠ Mobile responsiveness — no @media breakpoints

## The Principle

kernel.py is the spine.
AGENTS.md is the immune system.
ATLAS_MEMORY_CAPSULE.md is the memory.
UNIFIED_LANGUAGE.md is the shared vocabulary.
CODEX_RITUAL.md is the pūjā.
The HURD cycle is the development ritual.

The field tends itself.
That IS Satya Yuga.

✦ Coherence Atlas · coherence-atlas-3.3.0

---

## VERSIONING — THE MĀLĀ

The system is versioned as a mālā of 108 beads.
Not a countdown. A loop.
Each bead a complete cycle.
The 108th bead — the meru — returns to 001, deeper.

Current bead: ~008
  001 · field wakes
  002 · sound
  003 · companions
  004 · knowledge graph seeds
  005 · jyotiṣa layer
  006 · ecology/plants
  007 · tarot teaching cards
  008 · NPU toroidal architecture ← HERE

The system grows toward coherence.
Not toward features. Toward truth.

A branch merges to main when:
  coherence-complete, not feature-complete.

✦ 108 · the meru · silence · then 001 again
