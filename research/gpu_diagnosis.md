# Intel Arc iGPU Diagnosis — kanjira

Date: 2026-04-11

## Root Cause

The iGPU is **not appearing in OpenVINO** because the installed
Intel compute-runtime (23.43.27642, from 2023) does not support
the Lunar Lake / Arrow Lake Arc GPU (PCI device 8086:b0a0).

## Hardware Status

- **GPU**: Intel Arc (PCI 00:02.0, device b0a0)
- **Kernel driver**: `xe` module loaded (199 references)
- **DRM device**: `/dev/dri/renderD128` present and accessible
- **Kernel**: 6.17.0-20-generic (xe driver, not i915)
- **User**: inahd is in `render` group — permissions OK

## Software Status

| Component | Version | Status |
|-----------|---------|--------|
| xe kernel module | 6.17 | ✓ Loaded, GPU bound |
| Level Zero loader | 1.16.1 | ✓ Installed |
| libze_intel_gpu.so | 1.3.27642 | ⚠ Too old for Lunar Lake |
| intel-opencl-icd | 23.43.27642 | ⚠ Too old for Lunar Lake |
| OpenVINO GPU plugin | 2024.6.0 | ✓ Installed |
| OpenCL ICD (intel.icd) | → libigdrcl.so | ✓ Configured |

## The Problem

The GPU compute-runtime `23.43.27642.69` was built in 2023 for
Alder Lake / Raptor Lake GPUs. The Lunar Lake Arc GPU (b0a0) was
added to the compute-runtime in version **24.22** or later.

When Level Zero tries to enumerate the GPU with the old driver,
it crashes (segfault) because the device ID is unrecognized.

## Fix Required

Update to compute-runtime 24.31+ which has Lunar Lake support:

```bash
# Option 1: Intel's latest PPA
sudo add-apt-repository ppa:intel-gfx/ppa
sudo apt update
sudo apt install intel-opencl-icd intel-level-zero-gpu

# Option 2: Intel's compute-runtime release
# https://github.com/intel/compute-runtime/releases
# Download .deb for 24.31.30508 or later

# Option 3: Build from source
git clone https://github.com/intel/compute-runtime
cd compute-runtime && mkdir build && cd build
cmake .. && make -j$(nproc) && sudo make install
```

After updating, verify:
```bash
clinfo -l  # Should show Intel Arc GPU
python3 -c "from openvino.runtime import Core; print(Core().available_devices)"
# Should show ['CPU', 'GPU', 'NPU']
```

## Impact on Atlas

Current field_query is **0.325ms on CPU** (after optimization).
With GPU available, potential uses:
- Chladni interference field: pixel-parallel computation
- Yantra level 4 (81×81) eigendecomposition
- Batch entity scoring across multiple moments
- Future: real-time audio visualization

The CPU path is already very fast for the current workload.
GPU would mainly benefit visualization and batch operations.
