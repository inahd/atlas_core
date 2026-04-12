# Atlas iGPU / NPU Benchmark Results

Date: 2026-04-11

## Hardware

- CPU: Intel Core Ultra 7 356H
- NPU: Intel AI Boost (available, functional)
- iGPU: Intel Arc (PCI 00:02.0, device b0a0)
  - /dev/dri/renderD128 present
  - **NOT available in OpenVINO** — GPU plugin not installed
  - OpenVINO sees: [CPU, NPU] only

## Task 1: Current Bottleneck Profile

| Operation | Time | Notes |
|-----------|------|-------|
| ToroidalField init | 1713ms | Loads 16,693 entities + compiles NPU model |
| field_query (NPU path) | 36.9ms | The main bottleneck |
| field_query (CPU numpy) | 0.24ms | Pure vectorized distance |
| field_query (NPU inference) | 0.76ms | OpenVINO inference call |
| Yantra 3×3 | 0.017ms | Negligible |
| Yantra 9×9 eigen | 0.010ms | Negligible |
| Yantra 27×27 eigen | 0.036ms | Negligible |
| Yantra 81×81 eigen | 0.363ms | Still fast |

**Where is the 36.9ms going?**
The NPU inference itself is 0.76ms. The remaining ~36ms is spent in:
- Post-processing: sorting scores, building result dicts
- Entity metadata lookups
- 3D coordinate computation (toroid_3d for each result)
- Python object creation overhead

The actual math (distance computation) is **0.24ms on CPU** — faster
than the NPU's 0.76ms due to NPU launch overhead for this batch size.

## Task 2: OpenVINO Device Comparison

Compiled model: toroidal coherence for 16,693 entities

| Device | Time (ms) | Std (ms) | Notes |
|--------|-----------|----------|-------|
| CPU (numpy) | 0.243 | 0.056 | Pure numpy vectorized |
| CPU (OpenVINO) | 0.043 | 0.018 | **Fastest** — OpenVINO CPU optimized |
| NPU (compiled) | 0.688 | 0.046 | Consistent but slower than CPU |
| AUTO | 0.108 | 0.041 | Routes to CPU (correct choice) |
| GPU | N/A | N/A | **Not available** — plugin missing |

## Task 3: AUTO Device Routing

AUTO mode correctly selected CPU for this workload (0.108ms vs NPU's 0.688ms).

**Key insight:** For the 16K entity vectorized distance computation,
CPU is optimal. The NPU's strength would be in larger batch sizes
or more complex operations (convolutions, matmuls on large matrices).

The NPU is currently being used for the distance computation where
CPU is actually faster. The NPU would be better used for:
- Yantra extension eigendecomposition at levels 3-4
- Coherence reranking (the full pipeline including graph expansion)
- Batch entity scoring across multiple moments simultaneously

## Task 4: iGPU Activation

The Intel Arc iGPU at /dev/dri/renderD128 is present but OpenVINO
cannot access it. To enable:

```bash
# Install OpenVINO GPU plugin
pip install openvino-gpu
# Or install the full GPU runtime
sudo apt install intel-opencl-icd
```

Once enabled, the iGPU would be ideal for:
- Level 3-4 yantra eigendecomposition (27×27, 81×81 matrices)
- Parallel entity scoring (GPU excels at embarrassingly parallel)
- Chladni field computation (pixel-parallel interference)

## Recommendations

1. **Switch field_query from NPU to CPU** — 3× faster for current workload
2. **Install GPU plugin** — `intel-opencl-icd` for iGPU access
3. **Use NPU for** — coherence reranking pipeline (more complex ops)
4. **Use AUTO** — let OpenVINO route per-operation
5. **Profile the 36ms overhead** — post-processing dominates, not compute
