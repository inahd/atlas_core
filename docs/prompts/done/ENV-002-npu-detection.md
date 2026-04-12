# ENV-002: Enable NPU detection

**Phase**: 2 — First audio  
**Priority**: HIGH  
**Estimated time**: 2–4 hrs

## Context

The Intel Meteor Lake NUC (kanjira) has a built-in NPU. `lspci` showed it undetected
during the audit. `npu_engine/toroidal_field.py` has `_init_npu()` already written
and waiting. This task investigates the hardware state and enables OpenVINO inference.

## Instructions

### Step 1: Hardware investigation

```bash
# Check all Intel devices
lspci | grep -i intel
lspci | grep -i "neural\|npu\|vpu\|accel\|gna"

# Check kernel modules
lsmod | grep -i "intel\|npu\|vpu"

# Check accelerator devices
ls /dev/accel* 2>/dev/null || echo "no /dev/accel devices"
ls /dev/dri/ 2>/dev/null

# Check dmesg for NPU mentions
dmesg | grep -i "npu\|vpu\|accel\|meteor" 2>/dev/null | tail -20

# Check kernel version (Meteor Lake NPU needs 6.7+)
uname -r
```

### Step 2: Check OpenVINO state

```bash
python3 -c "import openvino; print(openvino.__version__)" 2>/dev/null || echo "openvino not installed"
python3 -c "
from openvino.runtime import Core
c = Core()
print('Available devices:', c.available_devices)
" 2>/dev/null || echo "openvino runtime error"

# Check for intel NPU driver
dpkg -l | grep -i "intel\|npu\|openvino" 2>/dev/null
```

### Step 3: Install/fix based on findings

**If openvino not installed:**
```bash
pip install openvino --break-system-packages
pip install openvino-dev --break-system-packages
```

**If kernel < 6.7 (Meteor Lake NPU needs 6.7+):**
```bash
uname -r
# If < 6.7, note this as HUMAN_REQUIRED — kernel upgrade needed
```

**If openvino installed but NPU not in available_devices:**
```bash
# Try installing Intel NPU driver
# Check: https://github.com/intel/linux-npu-driver
sudo apt-get install -y intel-npu-driver 2>/dev/null || \
  echo "intel-npu-driver package not in apt — may need manual install"
```

### Step 4: Test toroidal_field NPU init

```bash
cd ~/atlas_core
python3 -c "
from npu_engine.toroidal_field import ToroidalField
tf = ToroidalField()
print('ToroidalField initialized')
print('NPU available:', getattr(tf, '_npu_available', 'unknown'))
"
```

### Step 5: Write NPU status to system topology

Update `datasets/system/system_topology.csv` with NPU detection result.
Read the file first to find the NPU row, update its status field.

### Step 6: Document findings

Append to `docs/ATLAS_CYCLE_LOG.md` what was found:
- Kernel version
- OpenVINO version (if installed)
- Available devices list
- Whether NPU is now active or still requires intervention

## HUMAN_REQUIRED condition

If kernel version < 6.7 → mark HUMAN_REQUIRED with note "kernel upgrade needed for Meteor Lake NPU"
If intel-npu-driver requires DKMS build that fails → mark HUMAN_REQUIRED

## Success check

```bash
python3 -c "
from openvino.runtime import Core
c = Core()
devices = c.available_devices
print('Devices:', devices)
if 'NPU' in devices:
    print('NPU: DETECTED')
else:
    print('NPU: not detected — CPU/GPU available:', [d for d in devices if d != 'NPU'])
"
```

## Output

- Update `datasets/system/system_topology.csv` with detection result
- Update `datasets/system/capability_map.csv` NPU row
- No engine changes (toroidal_field.py already handles NPU gracefully)
