# Atlas iGPU Benchmark — GPU Online

Date: 2026-04-11

## All 3 Devices Working

| Device | Name | Status |
|--------|------|--------|
| CPU | Intel Core Ultra 7 356H | ✓ |
| GPU | Intel Graphics (iGPU) | ✓ **NOW WORKING** |
| NPU | Intel AI Boost | ✓ |

## Crossover Points — Where GPU Beats CPU

| Operation | GPU wins at | Speedup | Below that, CPU wins by |
|-----------|------------|---------|------------------------|
| Matrix multiply | **729×729** | **1.7×** | CPU 0.5-0.9× at smaller |
| Entity coherence | **100,000** | **1.2×** | CPU wins at 16K (0.3×) |
| Chladni wave | **1024×1024** | **2.1×** | CPU wins at 512 (0.7×) |
| Gamak DSP | **16 notes** | **1.5×** | CPU wins at 4 notes |

## Full Results

### Matmul
| Size | CPU | GPU | NPU | GPU/CPU |
|------|-----|-----|-----|---------|
| 3×3 | 0.033ms | 0.071ms | 0.208ms | 0.5× |
| 9×9 | 0.034ms | 0.067ms | 0.203ms | 0.5× |
| 27×27 | 0.034ms | 0.072ms | 0.156ms | 0.5× |
| 81×81 | 0.086ms | 0.092ms | 0.181ms | 0.9× |
| 243×243 | 0.213ms | 0.287ms | 0.367ms | 0.7× |
| **729×729** | **1.944ms** | **1.138ms** | 1.718ms | **1.7×** |

### Entity Coherence
| Entities | CPU | GPU | GPU/CPU |
|----------|-----|-----|---------|
| 1,000 | 0.148ms | 0.187ms | 0.8× |
| 16,693 | 0.165ms | 0.585ms | 0.3× |
| 50,000 | 0.199ms | 0.368ms | 0.5× |
| **100,000** | **0.487ms** | **0.393ms** | **1.2×** |

### Chladni Wave Field
| Grid | CPU | GPU | GPU/CPU |
|------|-----|-----|---------|
| 128×128 | 0.160ms | 0.199ms | 0.8× |
| 512×512 | 0.402ms | 0.618ms | 0.7× |
| **1024×1024** | **2.464ms** | **1.180ms** | **2.1×** |

### Gamak DSP
| Notes | CPU | GPU | GPU/CPU |
|-------|-----|-----|---------|
| 4 | 0.081ms | 0.115ms | 0.7× |
| **16** | **0.204ms** | **0.134ms** | **1.5×** |
| 64 | 0.192ms | 0.194ms | 1.0× |
| 256 | 0.485ms | 0.442ms | 1.1× |

## Optimal Device Routing for Atlas

| Operation | Optimal Device | Reason |
|-----------|---------------|--------|
| field_query (16K entities) | **CPU** | 0.165ms vs GPU 0.585ms |
| Yantra 3×3 to 81×81 | **CPU** | GPU overhead exceeds compute |
| Yantra 729×729+ | **GPU** | 1.7× faster |
| Chladni 1024×1024 | **GPU** | 2.1× faster — use for S4 bloom |
| Gamak 16+ simultaneous | **GPU** | 1.5× for batch DSP |
| NPU | **Not recommended** | Slowest for all tested operations |
| AUTO | **Correct choice** | Routes to CPU for small, GPU for large |
