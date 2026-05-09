# Morphogenesis Engine Audit

**Date**: 2026-05-03
**Scope**: `static/morphogenesis/` (~8,540 LOC across 38 modules)
**Issue**: coherence-atlas#6

## 0. Summary

The current engine is **CPU-only Canvas2D** at 192×192 sim resolution × 720×720 display. Every frame runs 13 sim passes + an intergenesis state renderer + envelope-shaped SymbolEvents + a Float32Array → ImageData blit. There is no GPU, no NPU, no fixed timestep, and no event cap. The bottleneck is **per-pixel work** (≈37k pixels × multiple loops) accumulating across passes; secondary bottlenecks are unbounded SymbolEvent and echo arrays.

**Top finding**: the system is over-renderered, not over-simulated. Roughly 70 % of CPU per frame goes to per-pixel passes and the per-pixel renderer; less than 20 % goes to gestures/phrase analysis. A staged GPU migration of just the *renderer* (visualStates extraction) would unblock most of the visual budget.

## 1. Current Architecture

```
main.js                    bootstrap, frame loop, slider wiring
└── visionMode.js          fullscreen orchestrator + HUD
    ├── tools/
    │   ├── gesture.js          mouse → intent classifier (8 intents)
    │   ├── interactionPhrase.js  rolling-window dosha/guṇa/rhythm analyzer
    │   ├── phraseRewardDirector  phrase → transition + reward multipliers
    │   ├── visualEvent.js       8 event types with envelopes
    │   ├── symbolEvent.js       paint operators for 26 event kinds
    │   ├── beginner.js          gesture+style+phrase orchestrator
    │   └── inputController.js   advanced/tool-based mouse + key
    │
    ├── engine/
    │   ├── sim.js               Sim class, step() pipeline (~13 passes)
    │   ├── fields.js            Float32Array stack (10 scalar + 2 vector)
    │   ├── grid.js              Laplacian, gradient, sample helpers
    │   └── prng.js              mulberry32
    │
    ├── passes/  (13 modules)    diffusion, advection, reaction, branch,
    │                            discharge, interference, voronoi, sacred,
    │                            bhasmaCalcination, dhatuMaterial, pulseMarma,
    │                            helicalShear, tensegrity, movementPhrase,
    │                            quasicrystal, events
    │
    ├── render/
    │   ├── compositor.js        Float32 RGB → ImageData → Canvas2D
    │   ├── colormap.js          9 palettes + ACES tone-map + shyama floor
    │   ├── visualStates.js      16 feature extractors (per-pixel)
    │   ├── intergenesis.js      RegionMap (16×16) + 12 transitions + render
    │   ├── overlays.js          streamlines/branch/coherence-rings overlays
    │   └── timeline.js          per-pass activity ring buffer (debug HUD)
    │
    └── atlas/                   data: modes, presets, styles, vision presets,
                                 grammar, vastu, yantra, mandala, phyllotaxy,
                                 aesthetics (DHATU/BHASMA/VERB tints),
                                 elements, relations
```

Sim grid: **W=192, H=192, N=36 864**.
Render canvas: **720×720** (CSS-scaled from 192×192 buffer).
Frame loop: `requestAnimationFrame(frame)` — uncapped, no fixed timestep.

## 2. Per-Frame Cost Inventory

Numbers below are *static loop counts*, not measured ms. Profiler HUD added in this PR will produce real numbers.

| Stage | File:line | Loops × N | Notes |
|---|---|---|---|
| `replenishPass` | passes/events.js:273 | 4 × N (one per field) | fast adds |
| `applySacred` | passes/sacred.js:9 | 3 × N (vastu+yantra+mandala) | mask multiplies |
| `bhasmaCalcinationPass` | passes/bhasmaCalcination.js | up to 11 × N (one per active op) | most ops mul or add |
| `dhatuMaterialPass` | passes/dhatuMaterial.js:24 | 2 × N (typical) | per-dhātu bias add |
| `tensegrityPass` | passes/tensegrity.js | local disk × 7 nodes | bounded, cheap |
| `applyEvents` (grammar) | passes/events.js:197 | per-event splats | unbounded if grammar dense |
| `pulseMarmaPass` | passes/pulseMarma.js | 1 local splat | bounded |
| `movementPhrasePass` | passes/movementPhrase.js | 3 × N (charge/coh/life) | one of these is alternating × 2N |
| `diffusionPass` | passes/diffusion.js:4 | 5 × N (Laplacian per field) | wraparound idx, 5-stencil |
| `reactionPass` | passes/reaction.js | 2 × N (Gray-Scott) | per-pixel branch |
| `quasicrystalPass` | passes/quasicrystal.js | 1 × N when active, **+ 11 cos() per pixel** | **expensive when active** |
| `curlFlowPass` | passes/advection.js | 1 × N | curl + injection |
| `helicalShearPass` | passes/helicalShear.js | local disk | bounded |
| `advectionPass` | passes/advection.js | 1 × N (bilinear sample) | sample = 4 reads |
| `branchMemoryPass` | passes/branchMemory.js:10 | 2 × N (accum + decay) + Laplacian | gradient inside |
| `dischargePass` | passes/discharge.js | 1 × N + walks | branching walk per high-charge pixel |
| `InterferenceField.apply` | passes/interference.js | 1 × N + 6 sources × N | **6N + N work** |
| `VoronoiField.apply` | passes/voronoi.js | every 3 ticks: 1 × N × 10 seeds | **10N when active** |
| **Life update** | sim.js:383 | 1 × N | |
| `computeRelations` | atlas/relations.js | 1 × N | per-pixel sum |
| `_stepSymbolEvents` | sim.js | per-event apply, each is a local splat | **scales with event count** |
| **Edge-density clamp** | sim.js:406 | 1 × N (sum) + 2 × N (clamp) | new in v0.13 |
| `prime beat add` | sim.js:307 | 1 × N (when prime tick) | every 3rd/5th/7th/11th tick |
| **`renderIntergenesis`** | render/intergenesis.js:178 | 1 × N for gradient + 1 × N for radial + **1 × N × 2 extractors** | **largest single cost**; per-pixel topStatesAt does bilinear blend across 4 region cells × 16 states |
| `_updateHistory` | compositor.js:100 | 1 × N | max-blend |
| `_composite` | compositor.js:128 | 1 × N | combine + black-ratio + lum-mean |
| `_present` | compositor.js:156 | 1 × N (Float32→Uint8) + ImageData+drawImage | |
| `aesthetic.applyAesthetic` | atlas/aesthetics.js | 1 × N (when active) | rotateHue + tint |

**Conservative estimate**: ~25–30 full-grid passes per frame at N=36,864. That is ~1M pixel-ops per frame at 60 fps = **60M ops/s** before any per-op work cost. Realistic per-op cost (multiple math ops, array indirection): ~5–10×, so ~300–600M ops/s. That puts us near or over a single CPU core's headroom — explains the bog.

## 3. Hot Paths (what to fix first)

| Rank | Hot path | Why | Impact if fixed |
|---|---|---|---|
| H1 | `renderIntergenesis` per-pixel `topStatesAt` (intergenesis.js:138) | runs every pixel, blends 4 cells × 16 states with bilinear weights | huge — 30–40% of render frame |
| H2 | `quasicrystalPass` 11-cos-per-pixel sum | 11 trig fn calls × 36k pixels = 400k ops just here | only when active, but ×0.4 of a frame |
| H3 | Compositor's three full-grid passes (paint, history, composite) | three back-to-back N loops + Float32→Uint8 | ~20% |
| H4 | Per-pass full-grid sweeps in 13 passes | even cheap passes add up; ~10 of them are full N | spread cost |
| H5 | `interference.apply` 6 sources × N | mostly memory bandwidth, loops are cheap | ~10% |

## 4. Event / Echo Growth Audit

- `sim.symbolEvents`: appended unboundedly by every gesture stream + every recognized intent + every visual signature key. **No cap.** Each tick `_stepSymbolEvents` walks the full list applying envelope + paint.
- Per-frame stream emit cadence in `BeginnerController._fireStream`: every drag mousemove event triggers a SymbolEvent + a regionMap transition. On a fast drag this can fire 50+ events/second.
- `regionMap.echoes`: capped only by natural expiration (echo schedules push, decay deletes after `tMs` lapses). A rapid sequence of sattvic-rewarded clicks adds up to **3 echoes each**, so a 10-click flurry creates ~30 pending echoes.
- `phraseAnalyzer.moves`: bounded by 4.5-s rolling window via `_trim`, but `recordMove` still gets called on every mousemove (no throttle).

**Risk**: a long uninterrupted drag in beginner mode can grow `symbolEvents` to several hundred concurrent events. Each tick walks all of them. Fixed by adding a hard cap (e.g., 200) and an LRU drop policy.

## 5. mousemove Handler Activity

Three independent listeners attach to `document`:
1. `gesture.move` — only when mouse button held (gesture.button >= 0)
2. `phraseAnalyzer.recordMove` — **every** mousemove, no throttle
3. `inputController` (advanced mode only): drag stream emit + cursor tracking

`phraseAnalyzer.recordMove` runs on every native pointermove (60–1000 Hz depending on hardware). It pushes to `samples[]` then calls `_trim` which iterates the array. At ~500 Hz cursor reports this is non-negligible.

**Fix**: throttle `recordMove` to 16 ms (60 Hz max). Throttle `_fireStream` is already implicit via `EMIT_INTERVAL_MS = 32` in inputController; beginner mode has no equivalent and may emit on every frame's mousemove.

## 6. Compositor

`compositor.paint` runs **three full-grid loops back-to-back**:
1. `_paintCurrent` — palette OR intergenesis renderer
2. `_updateHistory` — max-blend phosphor history + decay
3. `_composite` — combine current + history with shyama floor + black-ratio + lum-mean stats
4. `_present` — Float32 → Uint8 ImageData → `drawImage` upscale

This is **5 buffer sweeps per frame** including the present blit. The Canvas2D `drawImage` upscale from 192² to 720² is GPU-accelerated by the browser, but the four prior sweeps are not.

## 7. Top 5 Immediate Performance Fixes

In **priority order** (most impact, least risk):

| # | Fix | Where | Expected gain | Risk |
|---|---|---|---|---|
| **P1** | **Cap `sim.symbolEvents` at 200** with LRU drop of oldest in `addSymbolEvent` | engine/sim.js | prevents drift bog under long drags | none |
| **P2** | **Throttle `phraseAnalyzer.recordMove`** to ≥16 ms gap between recordings | tools/interactionPhrase.js + tools/beginner.js | up to 30× fewer recordMove ops on fast cursors | none |
| **P3** | **Lazy-skip quasicrystal pass** when `params.active=false` (already does), but also skip the per-frame 11-cos sum when `strength*gain < 0.05` | passes/quasicrystal.js | ~10% peak frames recovered | none |
| **P4** | **Merge intergenesis sub-passes** — `renderIntergenesis`'s per-pixel `topStatesAt` recomputes the bilinear blend even though region weights changed only at 16² resolution. Precompute a 16² × 16-state weights buffer once per frame, sample bilinearly during pixel pass | render/intergenesis.js | ~20% render time | low |
| **P5** | **Add fixed timestep + frame skipping** when budget exceeds 16 ms — run sim every other frame at high cursor velocity, render every frame | main.js | smooth sustained interactivity | medium |

Quick wins without architecture changes. P1 + P2 alone solve the drift bog the issue describes ("becoming too heavy and noisy").

## 8. Top 5 Visual Leverage Fixes

What actually controls visual feel, in **leverage order**:

| # | Lever | Source | What it should drive | Status |
|---|---|---|---|---|
| **L1** | **Region state weight curve** | intergenesis.js | Currently linear lerp toward target. Sharper visuals come from steeper curves: cubic or smoothstep instead of linear. | underused |
| **L2** | **Composition lock duration** | sim.js / visualEvent.js | Currently lock active during attack+peak only. Extending to attack+peak+decay gives "the gesture has consequences" feel. | underused |
| **L3** | **Bhasma stage tint warmth** | atlas/aesthetics.js | Each of 9 stages has [-0.30, +0.45] warmth range; pacha agni (1.20 saturation) is very visible, marana (0.78 sat) is muted. The currently-static dropdown means most users never see this rotate. | overused as static, underused as dynamic |
| **L4** | **Tithi hue shift** | atlas/aesthetics.js | 0–360° rotation by `tithi_pos`. Currently not bound to anything that changes — hue stays fixed across a session unless preset changes. **Should drift slowly with real time** to provide a long-arc visual breath. | dormant |
| **L5** | **Phrase reward intensity multiplier** | tools/phraseRewardDirector.js | sattvic phrases get ×1.40 intensity + 2 echoes (visible). pitta strikes get ×1.45 (visible). vata erratic gets ×0.85–0.95 (barely distinguishable from default). The vata-fragmenting feel needs a *visual* operator, not just intensity reduction. | partially applied |

## 9. NPU / Local-AI Candidates

Tasks that should be local-AI biased rather than shader-simulated:

| Candidate | What | Why | Suggested model |
|---|---|---|---|
| Inspiration folder feature extraction | Read user-supplied images, extract style/morphology vectors | one-time offline batch; no per-frame cost | CLIP image encoder (ONNX) |
| Hidden-form detection | Identify whether the field currently resembles a body / flower / lightning / yantra | curatorial — used to decide composition lock duration and HUD label | small CNN or CLIP image-text similarity |
| Phrase classifier (alternative to heuristic) | Replace `interactionPhrase.classify` if ML is more accurate | last priority — heuristic works fine for v0.15 | gradient-boosted tree, not neural |

**Anti-recommendation**: do NOT use NPU for image generation, latent diffusion, or any per-frame neural pass. Keep it as a curator/critic, not a renderer.

## 10. Relational Engine Audit

Where Atlas symbolic state becomes field parameters:

| Atlas concept | Code path | Field side |
|---|---|---|
| tithi phase | `morphogenesis.derive_bhasma_stage` (Python) → bundle.bhasma_stage.tithi_pos | aesthetics tithiHueShift, bhasma stage selection |
| nakshatra body region | `derive_embodiment` → embodiment.body_region | pulseMarma anatomical position table |
| graha | embodiment.graha | currently HUD-only; not bound to a field operator |
| nitya / yantra | sacredCtx.yantraMask | applied multiplicatively per-pixel via passes/sacred.js |
| pranayama | embodiment.pranayama_that_loads | movementPhrase pass cycle timing (smooth/sharp/alternating) |
| bhasma stage | bhasmaStage.visual_operators | bhasmaCalcination pass — applies up to 11 op multipliers |
| quasicrystal fold | quasicrystalParams.fold | 11-cos sum in quasicrystal pass |
| dosha phrase | InteractionPhrase | phraseRewardDirector → transition selection + reward multipliers |

**Underused relations**:
- **graha** — should bias palette/dhātu selection (Mars→raudra, Jupiter→shringara, Mercury→adbhuta…); currently does nothing visual
- **paksha** (waxing/waning) — used to select bhasma stage (krishna inverts), but the *direction* could also drive transition preference (waxing → bloom_to_eye, waning → density_to_void)
- **wave amplitude** — exists in derive_morphogenesis_elements but not wired to event intensity scaling
- **dominant_k** — not currently piped to morphogenesis at all

**Overused relations**: bhasma stage drives **two** layers (aesthetics tint + bhasma pass). Either consolidate or split — currently one moves slowly with tithi, the other is whatever the bundle says, so they can disagree.

## 11. Cosmological Leverage Ranking

Ranked by visual impact when you change the value (1 = highest):

| Rank | Parameter | Visual control | Compute location | Status |
|---|---|---|---|---|
| 1 | **bhasma_stage** | Color warmth + saturation + pass multipliers | Python derive + JS aesthetics + JS pass | live, both active |
| 2 | **palette / style** | Entire visual register | JS (style + palette + per-pixel postProcess) | live, user-driven |
| 3 | **interaction phrase** | Which transition fires + reward multipliers | JS (analyzer + director) | live (v0.15) |
| 4 | **active embodiment** | Region of canvas where pulse/marma fires | Python derive + JS pulseMarma/helical/tensegrity | live |
| 5 | **wave_amplitude** | Event intensity scaling | should multiply VisualEvent intensityMul | **dormant** (not wired) |
| 6 | **dominant_k** | Echo subdivision count, mandala fold | should drive shockwave petal count + qc fold | **dormant** (not piped) |
| 7 | **tithi_pos** | Hue rotation | live (slow drift recommended) | static |
| 8 | **paksha** | Direction bias (bloom vs void) | should bias transition selection | partial (bhasma only) |
| 9 | **graha** | Palette/dhātu bias | should pick palette family at preset time | **dormant** |
| 10 | **nitya yantra** | Spatial mask | live (sacred pass) | live |
| 11 | **pranayama** | Breath cycle timing | live (movementPhrase pass) | live |

## 12. Anti-Goals Reminder

This audit identifies **what to rebuild before adding anything new**.

- ✅ No new visual concepts proposed
- ✅ No full GPU port proposed
- ✅ No NPU image generation proposed
- ✅ No new sliders proposed
- ✅ No defense of noisy raw-buffer rendering — render path goes through feature extractors (intergenesis); old palette is fallback only

## 13. Suggested Next Task

Implement P1 + P2 + P5 from §7 + the **profiler HUD** (this PR adds it):

1. Cap `sim.symbolEvents` at 200 with LRU drop
2. Throttle `phraseAnalyzer.recordMove` to 16 ms
3. Fixed-timestep sim loop (60 Hz) decoupled from render loop
4. Quasicrystal early-exit when `strength*gain < 0.05`
5. Profiler HUD (added in this PR) with: fps, frame ms, sim ms, render ms, event count, echo count, region map step ms, dropped frames, auto-quality flag

Once those land, measure. Then decide if GPU migration is needed (it likely is, for any sim grid > 256²).
