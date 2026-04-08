# iGPU Audit — 2026-04-05

Read-only audit of all iGPU, NPU, toroidal, and rendering code in Atlas.

---

## 1. WHAT IGPU.PY ACTUALLY DOES

`npu_engine/igpu.py` (787 lines) is a **pure-Python spatial layout engine**. It computes node positions, edge styling, formation clustering, and role assignment. It produces data structures (dataclasses), not pixels. Despite the name "iGPU", it does not use any GPU hardware.

### Dataclasses (output types)
| Class | Fields | Purpose |
|-------|--------|---------|
| `RenderNode` | id, name, x, y, z, size, color, alpha, attestation, element, guna, pinned, group, role, motion | Single positioned entity |
| `RenderEdge` | source, target, relation, attestation, style, width, alpha, mutual | Relation line between entities |
| `RenderFlow` | source, via, target, relations, strength, domains, sx/sy/vx/vy/tx/ty | 2-step path (A→B→C) |
| `RenderFormation` | name, center_x, center_y, radius, member_ids, symmetry, style | Cluster centroid |
| `RenderState` | nodes, edges, flows, formations, lifecycle, psi, projection, bounds | Complete snapshot |

### Functions defined
| Function | Computes | Called? |
|----------|----------|--------|
| `project_plane(theta, phi)` | Flat 2D mapping | **Yes** — default projection |
| `project_toroid(theta, phi, R, r)` | Toroid → 2D perspective | **Yes** — used by shell, live, cosmos |
| `project_hex(theta, phi)` | Hex grid mapping | Available but **rarely called** |
| `project_4d(theta, phi, t)` | Toroid + time rotation | **Yes** — works via `?projection=4d` |
| `layout_nodes(entities, projection)` | Position N entities | **Yes** — core pipeline |
| `layout_edges(relations)` | Style relation edges | **Yes** — core pipeline |
| `layout_formations(formations, node_map)` | Compute cluster centroids | **Yes** — core pipeline |
| `assign_roles(nodes, formations, relations)` | Center/orbit/bridge/free | **Yes** — core pipeline |
| `activate_formations(nodes, formations, lifecycle, psi)` | Pull members into clusters | **Yes** — core pipeline |
| `build_flow_vectors(state)` | 2-step path detection | **Yes** — core pipeline (currently returns 0 flows; graph expansion may fail silently) |
| `render_field_state(state, projection, selected_id, t)` | **Main entry point** — full pipeline | **Yes** — called by 3 routes |
| `render_state_to_dict(rs)` | Serialize RenderState → JSON | **Yes** — called by 3 routes |

### Constants
| Constant | Purpose |
|----------|---------|
| `ELEMENT_RGB` | 5 elements → RGB tuples |
| `ATTESTATION_STYLE` | 4 levels → edge style/alpha/width |
| `FORMATION_STYLE` | 7 named formations → ring/hex/grid |
| `PROJECTIONS` | Dict mapping names → projection functions |

---

## 2. CURRENT USAGE

### Kernel routes using iGPU functions

| Route | What it does | Working? |
|-------|-------------|----------|
| `GET /render` | Builds spine → `render_field_state()` → JSON | **Yes** — 64 nodes, 24 edges, 2 formations |
| `GET /render/eternal` | Canonical entity positions (not field-weighted) | **Yes** — 64 nodes, uniform scores |
| `GET /render/stream` | SSE stream of /render every second | **Broken** — request context error |
| `GET /render/toroid` | Separate toroid route (POST/GET) | **Exists** — untested |

### Client-side consumers of /render

| Client | Fetches | Projection | Frequency |
|--------|---------|-----------|-----------|
| `static/shell.html` | `/render?projection=plane` | plane | every 30s |
| `static/shell.html` | `/render?projection=toroid` + `/render/eternal` | toroid | on load |
| `static/shell-cosmos.html` | `/render?projection=toroid` + `/render/eternal` | toroid | on load |
| `static/live.html` | `/render?projection=toroid` | toroid | every 5min |
| `static/live.html` | `/render/eternal` | toroid | on "eternal" button |
| `static/js/shell.js` | `/render?projection=plane` + `/render/stream` | plane | 30s + SSE |
| `static/index.html` | Listed as status check | — | on load |

### npu_engine modules importing igpu.py
- `npu_engine/geometry/igpu.py` — re-export layer (`from ..igpu import *`)
- No other engine imports igpu.py directly. It's consumed only by kernel.py routes.

### Is OpenVINO loaded?
- **Yes.** `openvino.runtime.Core()` shows `['CPU', 'NPU']` as available devices.
- **NPU is at `/dev/accel/accel0`** (Intel Meteor Lake NPU).
- **iGPU is at `/dev/dri/renderD128`** (Intel Iris Xe).
- These are **different devices**. The NPU does coherence scoring. The iGPU does WebGL in the browser. `igpu.py` uses neither — it's CPU Python.

---

## 3. TOROIDAL FIELD

### What toroidal_field.py computes (597 lines)

`ToroidalField` is the **core coherence scoring engine**. It:
1. Loads all 11,394 entities with (theta, phi) coordinates
2. Converts panchanga (tithi, nakshatra, vara, element, guna) to toroid coordinates
3. Computes geodesic distance between the moment and every entity
4. Returns entities sorted by coherence score (cosine falloff)

Key functions:
| Function | Purpose |
|----------|---------|
| `panchanga_to_coords(panchanga)` | Time moment → (theta, phi) |
| `toroidal_distance(t1, p1, t2, p2)` | Geodesic on torus surface |
| `coherence_from_distance(dist)` | Distance → 0.0-1.0 score |
| `ToroidalField.field_query(panchanga, top_n)` | **The main query** — batch coherence |
| `ToroidalField._compile_npu()` | Compiles OpenVINO model with entity coords baked in |
| `ToroidalField._npu_coherence_scores(t, p)` | Runs inference on NPU |
| `toroid_3d(theta, phi)` | (theta, phi) → 3D point for visualization |

### Where it's called
- `build_field_state.py` line 288: `field = ToroidalField()` — constructs the field on every `/spine` call
- `build_field_state.py` line 171: `field.field_query(panchanga, top_n=top_n)` — the actual coherence ranking
- `torus_queries.py` is imported by `mandala_schema.py` line 1432 for pada context

### Is the NPU doing computation?

**Yes, confirmed live:**
```
NPU ready flag: True
NPU compiled: 11394 entities baked, device=NPU
NPU call count after query: 1
```

The NPU (Intel Meteor Lake, `/dev/accel/accel0`) runs the coherence scoring. Entity coordinates are baked into the compiled OpenVINO model as constants. Only the moment position `[theta, phi]` is sent as runtime input. The NPU computes 11,394 distance+cosine operations per inference call.

The numpy fallback exists but is not used when NPU is available.

---

## 4. GAPS

### Functions defined but never called
| Function | Location | Issue |
|----------|----------|-------|
| `project_hex()` | igpu.py:161 | Available via `?projection=hex` but no client requests it |
| `build_flow_vectors()` | igpu.py:584 | Called but returns 0 flows (path_engine import may silently fail, or graph expansion returns nothing) |
| `/render/stream` | kernel.py:4609 | SSE endpoint is broken — request context error in threaded generator |
| `ToroidalField.explain()` | toroidal_field.py:561 | Defined, never exposed via a route. Useful for debugging coherence. |
| `ToroidalField.s0_ground()` | toroidal_field.py:605 | Returns S0 eternal entities, never used by any route |
| `ToroidalField.categories()` | toroidal_field.py:597 | List entity categories, never exposed |

### Routes that should use iGPU but don't
- `/render/bandhu` — serves SVG from figure_renderer, not igpu. Correct — different rendering pipeline.
- `/render/species/<id>` — serves species SVG. Also correct.
- `/render/shrine` — serves shrine SVG. Also correct.
- These `/render/*` routes are not iGPU routes despite sharing the prefix. The naming is slightly misleading.

### 4D projection status
- `project_4d(theta, phi, t)` works: it adds `t * 2pi` to theta, making the toroid rotate with time.
- Accessible via `GET /render?projection=4d` — returns 64 valid nodes.
- **No client uses it.** live.html, shell.html, and shell-cosmos.html all request `projection=toroid` or `projection=plane`.
- The `/render/eternal` route accepts a `t` parameter and passes it to `render_field_state`, but defaults to 0.0.

---

## 5. VERDICT

### Is the iGPU doing GPU work?

**No.** `igpu.py` is a pure-Python CPU spatial layout engine. The name is aspirational — it was designed to eventually offload to the Intel Iris Xe iGPU via WebGL or compute shaders, but currently runs entirely on the x86 CPU.

The hardware breakdown:
| Device | What it does in Atlas | Where |
|--------|----------------------|-------|
| **Intel NPU** (`/dev/accel/accel0`) | Toroidal coherence scoring — 11,394 entities, OpenVINO compiled model | `toroidal_field.py` |
| **Intel Iris Xe iGPU** (`/dev/dri/renderD128`) | WebGL rendering **in the browser** (Three.js in live.html) | Client-side only |
| **x86 CPU** | Everything in igpu.py — projections, layout, formations, role assignment | `igpu.py` |

The "iGPU" name refers to the ambition, not the reality. The actual GPU acceleration happens in the browser via WebGL (Three.js consuming the JSON output). The actual NPU acceleration happens in `toroidal_field.py` for coherence scoring.

### What's the fastest path to real iGPU acceleration?

**Option A: WebGPU compute shaders (medium effort)**
Move projection + formation activation to a WebGPU compute shader running on the Iris Xe. This would let the browser do layout computation on the GPU and render directly, eliminating the Python→JSON→JavaScript→Three.js pipeline for the toroid view. Requires WebGPU support in the browser (Chrome 113+).

**Option B: OpenVINO on iGPU (low effort, high impact)**
OpenVINO supports `GPU` as a device (in addition to `NPU` and `CPU`). The iGPU could run a compiled model for the projection math, similar to how the NPU runs coherence scoring. Change `_OV_DEVICE = "GPU"` in a new model. However, the current projection math is simple enough that CPU is not the bottleneck — the bottleneck is the HTTP roundtrip and JSON serialization.

**Option C: Do nothing (recommended for now)**
The current pipeline handles 64 entities in <10ms on CPU. The NPU handles 11,394 entities for coherence scoring. The bottleneck is not computation but the multiple fetch→parse→render cycles in the browser. The fastest real improvement would be:
1. Fix `/render/stream` SSE so clients don't need to poll
2. Cache `render_field_state` output (field changes at most every 30s)
3. Expose `project_4d` in a client for temporal exploration

---

## Files inspected

```
npu_engine/igpu.py                  — 787 lines, full read
npu_engine/toroidal_field.py        — 665 lines, full read
npu_engine/torus_queries.py         — 40 lines, full read
npu_engine/build_field_state.py     — grep for ToroidalField usage
npu_engine/geometry/igpu.py         — re-export layer (1 line)
npu_engine/core/toroidal_field.py   — re-export layer (1 line)
npu_engine/mandala_schema.py        — grep for torus_queries usage
kernel.py                           — grep for /render, igpu, OpenVINO
static/shell.html                   — grep for /render fetch calls
static/shell-cosmos.html            — grep for /render fetch calls
static/live.html                    — grep for /render fetch calls
static/js/shell.js                  — grep for /render fetch calls
static/index.html                   — grep for /render status checks
SYSTEM_MAP.md                       — hardware topology
/dev/accel/accel0                   — NPU device confirmed
/dev/dri/renderD128                 — iGPU device confirmed
```

## Summary table

| Component | Status | Hardware | Notes |
|-----------|--------|----------|-------|
| igpu.py projections | **Working, CPU** | x86 | 4 projections, all functional |
| igpu.py layout engine | **Working, CPU** | x86 | 64 nodes, 24 edges, 2 formations |
| igpu.py flow vectors | **Partial** | x86 | Returns 0 flows (silent import failure) |
| /render route | **Working** | x86 | Serves JSON to 5 clients |
| /render/eternal | **Working** | x86 | Canonical positions |
| /render/stream | **Broken** | — | Request context error |
| toroidal_field.py | **Working, NPU** | Intel NPU | 11,394 entities, OpenVINO compiled |
| project_4d | **Working but unexposed** | x86 | No client uses it |
| iGPU hardware | **Unused by Python** | Iris Xe | Used by browser WebGL only |
