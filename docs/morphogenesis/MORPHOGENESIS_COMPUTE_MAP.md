# Morphogenesis Compute Map

Where each computation **lives** today vs. where it **should live**.

## Legend

- **CPU-JS** — Float32Array + plain JS
- **GPU** — WebGL/WebGPU fragment shader (none currently)
- **NPU** — local AI inference (none currently)
- **REL** — relational graph / Atlas Python derive functions
- **DOM** — Canvas2D, ImageData, document events

## Per-Frame Pipeline (current)

| Stage | Where | Should be |
|---|---|---|
| Mouse / key event | DOM | DOM (correct) |
| Gesture intent classification | CPU-JS (gesture.js) | CPU-JS (correct, heuristic ≥ ML for this) |
| Phrase analysis (rolling-window features) | CPU-JS (interactionPhrase.js) | CPU-JS (with throttle) |
| Phrase reward / transition selection | CPU-JS (phraseRewardDirector.js) | CPU-JS |
| `sim.regionMap.applyTransition` (target stamp) | CPU-JS | CPU-JS (16×16 grid is tiny) |
| `sim.regionMap.step` (lerp + decay + echo) | CPU-JS | CPU-JS |
| Replenish pass (4 fields × N) | CPU-JS | **GPU** |
| Sacred pass (3 mask multiplies × N) | CPU-JS | **GPU** |
| Bhasma calcination (multi-op × N) | CPU-JS | **GPU** |
| Dhātu material bias (1–2 × N) | CPU-JS | **GPU** |
| Tensegrity (local disk) | CPU-JS | CPU-JS (bounded, cheap) |
| Grammar events apply (variable, splats) | CPU-JS | CPU-JS (event-driven, low N) |
| Pulse marma (single splat) | CPU-JS | CPU-JS |
| Movement phrase (3 × N typical) | CPU-JS | **GPU** |
| Diffusion (5 × N Laplacian) | CPU-JS | **GPU** (texture ping-pong) |
| Reaction-diffusion (Gray-Scott × N) | CPU-JS | **GPU** (texture ping-pong) |
| Quasicrystal (11-cos × N) | CPU-JS | **GPU** (huge win) |
| Curl flow (1 × N) | CPU-JS | **GPU** |
| Helical shear (local) | CPU-JS | CPU-JS |
| Advection (bilinear × N) | CPU-JS | **GPU** (sample is native) |
| Branch memory (gradient + accum + decay × N) | CPU-JS | **GPU** |
| Discharge (walk per high-charge pixel) | CPU-JS | CPU-JS (branch-heavy, awkward in shaders) |
| Interference (6 sources × N) | CPU-JS | **GPU** (per-pixel transcendentals) |
| Voronoi (10 seeds × N) | CPU-JS | **GPU** (one of the textbook GPU wins) |
| Life update (1 × N) | CPU-JS | **GPU** |
| Relations sum (1 × N) | CPU-JS | CPU-JS (single sum, cheap) |
| Edge-density clamp (3 × N) | CPU-JS | **GPU** + CPU readback |
| Prime beat add (1 × N when prime tick) | CPU-JS | **GPU** (cheap shader pass) |
| `_stepSymbolEvents` apply (per-event splats) | CPU-JS | CPU-JS (event count is bounded) |
| **Intergenesis renderer** (per-pixel × 2 extractors) | CPU-JS | **GPU** (single fragment shader) |
| Compositor history max-blend | CPU-JS | **GPU** |
| Compositor composite + stats | CPU-JS | **GPU** for blend; CPU readback for stats |
| Float32 → Uint8 → ImageData → drawImage | CPU-JS + DOM | **GPU** (texture render to canvas, no CPU readback) |

**Total full-grid sweeps**: ~25 per frame on CPU. With GPU migration: 0 full-grid sweeps on CPU; per-frame becomes a sequence of fragment shader calls + final composite, with CPU only running the orchestrator + event handlers.

## Where Atlas Cosmological State Lives

| Concept | Source | Compute | Latency |
|---|---|---|---|
| field_state() bundle | Python (`kernel.py`) | REL (Python) | one-shot fetch via `/field/morphogenesis` |
| derive_embodiment / derive_bhasma_stage / derive_intent | Python (`morphogenesis.py`) | REL (Python) | one-shot fetch |
| applyAesthetic per-pixel tint | JS (atlas/aesthetics.js) | CPU-JS | per frame |
| Lo Shu cell / prime beat | JS (atlas/aesthetics.js) | CPU-JS | per tick |
| Visual state extractors (per pixel) | JS (render/visualStates.js) | CPU-JS | per frame × per pixel |
| Region state weights (16×16) | JS (render/intergenesis.js) | CPU-JS | per tick (cheap) |

**Recommendation**: keep Atlas REL state computation in Python (correct location). The bundle is fetched once or a few times per session — not a per-frame cost. JS consumes it as static input until the user re-fetches.

## Suggested Migration Phases

### Phase 0 — Stabilize CPU (this PR)
- Profiler HUD
- Symbol event cap (200, LRU)
- Phrase recordMove throttle (16 ms)
- Quasicrystal early-exit
- Fixed-timestep sim loop

### Phase 1 — GPU compositor
- Move `renderIntergenesis` per-pixel work to a single fragment shader.
- Region weights → uniform buffer (16² × 16 floats = 4 KB, trivial).
- 16 visual state extractors → one big switch in shader, indexed by `topStateIdx`.
- Field stack stays CPU; uploaded as 6–10 R32F textures per frame (one upload per field at sim resolution).
- History/composite → second shader pass.
- **Expected gain**: ~10× render budget (~5 ms → 0.5 ms).

### Phase 2 — GPU sim (diffusion + reaction)
- Ping-pong textures for `density`, `coherence`, `moisture`, `life`.
- Diffusion pass = single 5-stencil shader.
- Reaction pass = Gray-Scott shader.
- Other passes still CPU; field readback only when the renderer needs CPU access.
- **Expected gain**: another 30–40 % off frame time.

### Phase 3 — GPU sim (advection + curl + voronoi + interference + quasicrystal)
- Replace per-pixel transcendentals with shader natives.
- Voronoi via standard Worley shader (not the current 10-seed CPU loop).
- Quasicrystal sum becomes a `sum(cos(...))` over a static angle uniform.
- **Expected gain**: large at sim resolution > 192².

### Phase 4 — Optional NPU layer
- Inspiration folder image classifier (curator).
- Hidden-form detector (CLIP-text similarity → composition lock label).
- **Never** image generation.

## What NOT to Migrate

- Gesture recognizer — heuristic is fine, latency-critical, must stay on main thread
- Phrase analyzer — small data, latency-critical, stays CPU
- RegionMap step — 256-cell grid, basically free
- Atlas symbolic derives — Python is correct, latency is fine
- HUD updates — DOM is correct
