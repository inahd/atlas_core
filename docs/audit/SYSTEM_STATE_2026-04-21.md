# Atlas System State — April 21, 2026

## What Atlas Is

Atlas is a coherence computer. It reads the Vedic cosmological moment (panchanga)
and expresses it simultaneously through sound, visual topology, text, relational
graph, and now wave interference mathematics. It runs continuously on a van-mounted
Intel NUC (kanjira), outputting through a MOTU M2 audio interface.

## Scale

| Metric | Count |
|--------|-------|
| Python engine files | 218 |
| CSV datasets | 240 |
| JSON datasets | 677 |
| Total routes (kernel + blueprints) | 259 |
| kernel.py lines | 8,404 |
| S-layer HTML pages | 7 (S0-S6) |
| Static HTML pages | 17 |
| Blueprints registered | 8 |
| Dataset domains | 42 |
| Research papers (md) | 14 |
| Research artifacts (json) | 9 |

## Architecture

Two repos: `atlas_core` (active, computation) and `atlas_330` (archive, presentation).

**atlas_core** returns JSON. 259 routes serve panchanga, field state, charts,
wave fields, sound specs, corpus search, codex, readings, compose, render, plants,
guild, agriculture, geography, vastu, yantra, tarot, hexfield, geosolar, briefing,
transit analysis, pasaka oracle, shalaka, and the jyotisha chart engine.

**atlas_330** holds the app layer: 27 HTML apps across 6 domains (kala, devi,
bhumi, lila, vidya, bandhu), 219 wiki pages, and the audio output pipeline
(om.py, SuperCollider).

The boundary: atlas_core returns JSON, atlas_330 presents HTML/SVG/audio.
Some HTML has crept into atlas_core/static/ (17 pages including S-layer views,
oracle, mandala, dashboard).

## Live Systems

| System | Status | Notes |
|--------|--------|-------|
| Kernel (Flask, port 5000) | Running | 259 routes |
| Swiss Ephemeris | Active | Real positions for panchanga + jyotisha |
| Sound field loop | Running | 60s tick, 15 OSC messages to SC |
| SuperCollider (scsynth) | Available | 17 SynthDefs loaded, PipeWire audio |
| Geosolar logger | Running | 600s tick, solar/wind/barometric |
| Vector store | Active | 26k JSONL passage chunks |
| Graph engine | Active | 7,208 entities, 8,466 edges |
| Toroidal field | Active | OpenVINO NPU for coherence scoring |
| iGPU render | Active | 4 projections (plane/toroid/hex/4D) |

## Recent Work (April 2026)

| Date | What was built |
|------|---------------|
| Apr 2 | S4 Chladni nodal interference + tithi slider |
| Apr 6 | 15 Nitya Devi yantra images |
| Apr 8 | Yantra extension engine (Kronecker 3→81) |
| Apr 10 | Layer composer — self-assembling S-layer pages |
| Apr 11 | S1 page — Devi yantra + mantra + corpus passage |
| Apr 12 | Yantra eigenvalue exploration — 7 findings |
| Apr 16 | Jyotisha engine (Swiss Ephemeris, dignity, aspects, wave field) |
| Apr 16 | Nakshatra mandala visualization |
| Apr 16 | Sound engine wired to wave field (raga, gamak, tempo, partials) |
| Apr 16 | Kala calendar wired to real ephemeris |
| Apr 16 | Pasaka oracle engine + oracle.html integration |
| Apr 16-17 | Two-source interference paper (Findings 7-14) |
| Apr 17 | Planetary primes paper (retrograde symmetries + vertebral) |
| Apr 18 | SC SynthDef upgrade (breathing tanpura, rhythm task, dynamic partials) |
| Apr 21 | Devi layer framework analysis |

## What Works End-to-End

1. **Panchanga → Sound**: calc_panchanga() → field_state() → derive_sound_spec() →
   OSC → SuperCollider. Raga, tempo, drone partials all derived from astronomical
   moment. Updates every 60 seconds.

2. **Jyotish Chart**: Swiss Ephemeris → compute_chart() → /jyotish/natal → mandala
   visualization with wave field overlay, dignity assessment, tara bala.

3. **Oracle**: /oracle page with I Ching (Lo Shu weighted hexagram) + pasaka
   (3d4 dice) side by side, both reading the same field moment.

4. **Corpus Search**: 26k passage chunks across 80+ texts → vector_store.search() →
   /corpus/search endpoint.

5. **S-Layer Pages**: S0-S6 HTML pages self-assembling from dataset manifests via
   layer_composer, drawing from 240+ CSVs.
