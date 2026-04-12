# Atlas iGPU Integration Test Results

Date: 2026-04-11

## Device Status

| Device | Status | Name |
|--------|--------|------|
| CPU | ✓ Working | Intel Core Ultra 7 356H |
| GPU | ⚠ Detected, cannot compile | Intel Graphics (iGPU) |
| NPU | ✓ Working | Intel AI Boost |

GPU compiles fail at `program_builder.cpp:186` — OpenCL kernel compilation
not supported for Lunar Lake with compute-runtime 23.43.27642.

## Benchmark Results (CPU vs NPU)

### Matrix Multiply
| Size | CPU | NPU | CPU advantage |
|------|-----|-----|---------------|
| 3×3 | 0.033ms | 0.164ms | 5.0× |
| 9×9 | 0.034ms | 0.199ms | 5.8× |
| 27×27 | 0.034ms | 0.114ms | 3.3× |
| 81×81 | 0.049ms | 0.187ms | 3.8× |
| 243×243 | 0.182ms | 0.390ms | 2.1× |

### Entity Coherence
| Entities | CPU | NPU | CPU advantage |
|----------|-----|-----|---------------|
| 1,000 | 0.189ms | 0.388ms | 2.1× |
| 5,000 | 0.127ms | 0.535ms | 4.2× |
| 16,693 | 0.173ms | 0.898ms | 5.2× |
| 50,000 | 0.152ms | 0.889ms | 5.8× |
| 100,000 | 0.203ms | 1.025ms | 5.1× |

### Chladni Wave Field (CPU only — GPU fails)
| Grid | CPU |
|------|-----|
| 128×128 | 0.239ms |
| 256×256 | 0.200ms |
| 512×512 | 0.440ms |
| 1024×1024 | 1.960ms |

## Key Findings

1. **CPU is faster than NPU for ALL tested operations** (2-6×)
2. **GPU cannot compile** — needs compute-runtime 24.22+
3. **NPU overhead** exceeds compute savings at these batch sizes
4. **AUTO device routing** correctly selects CPU every time
5. **243×243 matmul** shows NPU getting closer (2.1×) — NPU may win at ~1000×1000+

## Optimal Routing for Atlas

| Operation | Device | Time | Notes |
|-----------|--------|------|-------|
| Entity coherence (16K) | **CPU** | 0.17ms | Vectorized numpy even faster at 0.04ms |
| Yantra 3×3 | **CPU** | 0.03ms | NPU overhead too high |
| Yantra 81×81 | **CPU** | 0.05ms | Still CPU-dominated |
| Chladni 512×512 | **CPU** | 0.44ms | GPU would help when available |
| field_query() | **CPU** | 0.33ms | After optimization (was 36.9ms) |

## Recommendation

Keep `_OV_DEVICE = "AUTO"` which correctly routes to CPU.
When compute-runtime is updated for Lunar Lake, GPU will unlock
for large grid operations (Chladni 1024×1024+, visualization).
