# Atlas Session Handoff — 2026-04-05

## Verified system state

Routes: 46 verified 200, 0 x 404 (217 total definitions in kernel.py)
Engines: 27 verified OK, 0 FAIL
Wiki: 219 pages, 3 empty stubs (Today.md, index_tithi.md, index_ritual.md)
Research: 4 briefs, 1 anomaly, 0 seeds
Datasets: 37 directories, 150+ CSVs
Ollama: qwen3:8b CPU ~130s/prompt
NPU: available for OpenVINO coherence scoring
Wesnoth: assets/wesnoth/ + assets/wesnoth-full/

Live field: Anurādha nakshatra, Pañcamī tithi, Ravivāra (as of last check)
Spine: 20 keys, 64 entities, all 7 layers (S0-S6) populated

## What was built (recent sessions)

- static/index.html — dashboard at /, live route status
- static/home.html — landing page, field-aware app cards by domain
- static/live.html — dual helix toroidal field, Three.js
- static/portal.html — 404 portal, no dead ends
- npu_engine/field/helix_engine.py — 338 lines, JDN ephemeris
- apps/kala/ — time oracle + wheel (2 HTML files)
- apps/devi/ — archana, tarot, mala, yantra (4 apps)
- apps/bhumi/ — agriculture, ecology, guild, vastu, streams (5 apps)
- apps/vidya/wiki/ — entity browser
- apps/lila/hexed/ — hex map level 1, Wesnoth tiles, Vayu↔Agni portals
- apps/lila/lila/ — coherence game
- apps/bandhu/ — ambient presence (2 HTML files)
- Flat route structure — all domains at clean URLs
- Domain reorganization — apps/ by domain
- 163 Python files in npu_engine/ across 15 subdirectories with re-export layer

## What does NOT exist (avoid assuming these are built)

- kala_engine.py — no such engine, /kala serves static HTML
- bot_engine.py — no such engine, journal routes inline in kernel.py
- apps/vidya/journal/ — directory does not exist, journal routes are in kernel.py
- /journal/tasks, /journal/ollama — not real routes, caught by /<path:name> wildcard
- Vishvakarma kernel route — app exists at apps/vishvakarma/index.html, no route

## Immediate next tasks (prioritized)

1. WIRE vishvakarma — one line in kernel.py
   @app.route('/vishvakarma')
   def vishvakarma(): return send_from_directory('apps/vishvakarma', 'index.html')

2. FILL wiki stubs — 3 remaining
   wiki/Today.md, wiki/index_tithi.md, wiki/index_ritual.md

3. SEEDS PIPELINE — 4 briefs waiting in research/briefs/
   Convert to seed files in research/seeds/
   Pipeline: briefs → seeds → wiki

4. JOURNAL UI — backend routes exist (GET/POST /journal, POST /journal/save)
   No standalone app HTML yet. Needs apps/vidya/journal/index.html or similar.

5. SC→MOTU AUDIO — blocked on PipeWire 1.2.6 JACK shim
   No fix without PW upgrade or alternative bridge

## Design decisions (carried forward)

Domain map:
  /kala   S3  Time
  /devi   S1  Devi
  /deha   S6  Body (Bandhu)
  /bhumi  S5  Nature
  /vidya  S2  Knowledge
  /lila   S6  Game
  Bandhu = ambient S6 presence across all domains

Shell zone → domain wiring:
  NW Vayu → /kala      N Kubera → /vidya    NE Ishana → /devi
  W Varuna → /bhumi     C Brahma → /live     E Indra → /lila
  SW Nirriti → /bhumi   S Yama → /deha       SE Agni → /lila/hexed

Game mechanic:
  Dead routes = sealed gates = dark terrain in hex map
  Fix route = gate opens = terrain transforms
  First level: NW Vayu ↔ SE Agni portal pair
  No dead ends — portal.html redirects from any 404

## Known blockers

- SC→MOTU audio: PipeWire 1.2.6 JACK shim broken (pw-cat works, pw-jack does not)
- Vocal SynthDef: 1154 lines waiting, no SC audio path
- 4D projection: project_4d() exists, not in any shell
- Systemd services: scripts ready, not installed
- Qwen3:8b: CPU-only (~130s/prompt), needs NPU or lighter model
