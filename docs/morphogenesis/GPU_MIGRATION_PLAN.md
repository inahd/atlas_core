# GPU Migration Plan

**Status**: not implemented. This document is the staged plan, not a record of work.

## Why

CPU per-frame budget is at the edge (see ENGINE_AUDIT.md §2). Roughly 25 full-grid sweeps × N=36,864 pixels × ~5 op-equivalents = ~5M ops per frame minimum. At 60 fps that's ~300M ops/s — within reach of one core but no headroom for upgrades (larger sim grid, more passes, multiple windows).

GPU migration unblocks: higher sim resolution (256² → 384² → 512²), lower per-frame variance, and frees CPU for richer interaction analysis.

## Constraints

- **WebGL2 baseline** — ubiquitous. No WebGPU dependency until 95 %+ browser support.
- **Float texture support** — required for sim fields. WebGL2 has `EXT_color_buffer_float` widely; gracefully fall back to half-float (or disable GPU mode) if absent.
- **No raw-buffer rendering** — even GPU output must go through the feature extractors. Don't expose density-as-grayscale as the default visual.
- **CPU readback for stats** — anti-collapse monitor needs `avgLuminance`/`fieldVariance`. Use 1×1 mip readback or skip on GPU and accept estimated values.

## Phase 1 — Render only (intergenesis fragment shader)

**Effort**: ~1 day. **Gain**: ~10× render budget.

### What

Replace `render/intergenesis.js:renderIntergenesis` with a fragment shader. CPU still runs all simulation passes; field stack is uploaded as R32F textures once per frame; the shader does per-pixel state extraction + blending + tone-map + shyama floor.

### Files

- new `render/glRenderer.js` — WebGL2 context, FBO, shader compile + link
- new `render/shaders/intergenesis.frag` — feature extractors + blend + ACES tone-map
- new `render/shaders/intergenesis.vert` — full-screen quad
- modify `render/compositor.js` — when GPU available, route `_paintCurrent` through `glRenderer.render()`; fall back to CPU path otherwise
- modify `main.js` — initialize glRenderer; flag `state.useGpu`

### Texture Layout

10 R32F textures, one per scalar field: density, moisture, heat, pressure, rigidity, coherence, branch_memory, charge, life. Plus 2 RG32F for vx/vy (or one RG32F).

Region weights upload: 16×16 RGBA32F texture where each pixel encodes 4 of the 16 state weights → 4 textures total, or one 16×16×16 texture array. (Keep as 4 RGBA32F for WebGL2 compatibility.)

### Shader Outline

```glsl
#version 300 es
precision highp float;

uniform sampler2D u_density, u_moisture, u_heat, u_pressure, u_rigidity,
                  u_coherence, u_branch_memory, u_charge, u_life;
uniform sampler2D u_vx, u_vy;
uniform sampler2D u_regionA, u_regionB, u_regionC, u_regionD; // 16×16 weights
uniform float u_contrast, u_exposure;
uniform vec3  u_aestheticBhasmaTint;
uniform float u_aestheticHueShift;
in vec2 v_uv;
out vec4 fragColor;

vec3 stateMembrane(/*sample fields at v_uv*/);
vec3 stateFilament(/*sample + gradient*/);
// ... 14 more
vec3 dispatchState(int idx, /*field samples*/) {
  if (idx == 0) return stateFilament(...);
  // etc — switch flattened into branchless mix
}
vec3 acesToneMap(vec3 c);
vec3 applyAesthetic(vec3 c);

void main() {
  // 1. Compute density gradient magnitude (4-tap)
  // 2. Sample region weights at v_uv (bilinear native)
  // 3. Extract top-2 indices + weights from 16-state vector
  // 4. Run two state extractors, blend by weight
  // 5. ACES tone-map → contrast pivot → exposure → shyama floor
  // 6. Aesthetic tint
  fragColor = vec4(rgb, 1.0);
}
```

### Switch Logic

The 16-way state dispatch is the only hard part. Three options:

1. **Branched switch** — naive, slow on some GPUs, fine for 16 cases on most modern
2. **Pre-baked LUT** — build a 16-state RGB output texture per frame, sample twice per pixel — but extractors need full field access, not just one sample
3. **Compute extractors for top-2 only** — match top indices on host (or in shader via reduction) and compute only those — cleanest

Recommend option 3.

### CPU Readback

Skip per-frame CPU readback in Phase 1. Keep CPU compositor's `blackRatio`/`avgLuminance` running on the *small* 192² CPU-side field for stats. Eventually move to a 1×1 mip reduce on GPU.

### Fallback

If WebGL2 init fails or floats unsupported → keep CPU renderer. State `state.useGpu = false`.

## Phase 2 — Sim diffusion + reaction

**Effort**: ~2 days. **Gain**: ~30 % off frame time.

### What

Move the 4 most expensive sim passes to GPU:
- `diffusionPass` — 5-stencil shader on density, moisture, life, coherence
- `reactionPass` — Gray-Scott shader (single fragment shader)
- `replenishPass` — fields toward target with multiplicative add
- Movement phrase per-pixel writes — `charge`, `coherence`, `life`

### Files

- new `passes_gpu/diffusion.frag`
- new `passes_gpu/reaction.frag`
- new `passes_gpu/replenish.frag`
- new `passes_gpu/movement.frag`
- modify `engine/sim.js` step() — branch on `state.useGpu`

### Texture Lifecycle

Each field gets a ping-pong pair (read texture + write texture). Sim step swaps them at end of each pass. Phase 1's renderer still reads from the same set so it now sees GPU-resident fields directly — **no CPU readback needed for rendering**.

CPU passes that still need fields (events, branch memory, discharge) read from a CPU mirror that's only updated when those passes run.

## Phase 3 — All field passes GPU

**Effort**: 3–5 days. **Gain**: enables sim res > 256², minor frame-time gain at 192².

Port advection, curl flow, branch memory, voronoi, interference, quasicrystal. Each is a single fragment shader of comparable size to the existing CPU code.

Discharge (which walks high-charge pixels) is awkward in shaders — keep on CPU with a small readback of the charge texture.

After Phase 3, CPU per-frame work is:
- gesture / phrase analysis (negligible)
- region map step (256 cells, negligible)
- event envelope dispatch + paint (bounded, ~100 ops)
- discharge walks (small)
- HUD / DOM
- texture upload of any CPU-emitted SymbolEvent splats

Frame budget at 60 fps becomes mostly idle.

## Phase 4 — Optional WebGPU port

**Effort**: 1–2 weeks. **Gain**: compute shaders, multi-pass dispatch, lower CPU dispatch cost.

Only worth doing if Phase 3 is hitting a WebGL bottleneck. WebGL2 is sufficient for a 192–384² grid.

## Risks

- **Float precision**: WebGL2 highp is 32-bit on desktop, 16-bit on some mobile. The reaction-diffusion equations are float-sensitive; test on mobile early.
- **Render target switching**: every pass that writes to a field texture means an FBO swap. Modern drivers handle this efficiently, but old GLES paths may stall.
- **Driver bugs**: float textures + multiple render targets are still sometimes flaky. Wrap each pass in a try/catch with a CPU fallback.
- **Lost context**: WebGL contexts can be lost (GPU reset, tab switch). Add a `webglcontextlost` listener that disables GPU mode and falls back to CPU.

## Decision Gate

Before starting Phase 1, run the profiler HUD (Phase 0) for one session and confirm:
- frame ms > 14 ms sustained (otherwise CPU is fine)
- sim ms + render ms breakdown shows render ms > 5 ms
- a non-trivial fraction of frames drops below 60 fps

If those conditions don't hold, Phase 1 is premature. Stay on CPU and address P1–P4 from ENGINE_AUDIT instead.
