# SND-005: Wire sound routes end-to-end (tanpura first)

**Phase**: 2 — First audio  
**Priority**: HIGH  
**Depends on**: RTE-002 (sound routes wired), SND-002 (SC startup script)

## Context

This task wires the complete sound path from field state to OSC to SuperCollider
for the tanpura instrument — the simplest and most fundamental sound in Atlas.
If tanpura plays from field state, the sound architecture is proven end-to-end.

## Instructions

### Step 1: Read the tanpura pipeline

```bash
cat ~/atlas_core/npu_engine/tanpura_engine.py | head -80
cat ~/atlas_core/npu_engine/tanpura_field.py | head -60
cat ~/atlas_core/npu_engine/sound/osc_bridge.py
head -5 ~/atlas_core/datasets/sound/tanpura_strings.csv
```

### Step 2: Trace the full path

Map: `field_state → tanpura_field.py → tanpura_engine.py → osc_bridge.py → SC`

```bash
cd ~/atlas_core
python3 -c "
from npu_engine.build_field_state import build_field_state
from npu_engine.tanpura_field import derive_tanpura_params

fs = build_field_state()
params = derive_tanpura_params(fs)
print('Tanpura params:', params)
"
```

```bash
python3 -c "
from npu_engine.build_field_state import build_field_state
from npu_engine.tanpura_field import derive_tanpura_params
from npu_engine.tanpura_engine import TanpuraEngine

fs = build_field_state()
params = derive_tanpura_params(fs)
engine = TanpuraEngine()
spec = engine.render(params)
print('Tanpura spec:', spec)
"
```

```bash
python3 -c "
from npu_engine.sound.osc_bridge import send_sound_spec
result = send_sound_spec({'type': 'tanpura', 'sa_hz': 261.63, 'volume': 0.7})
print('OSC send result:', result)
"
```

### Step 3: Fix any errors in the chain

Work through each step. Common issues:
- `tanpura_strings.csv` path not found → check `_load_string_defs()` path
- `derive_tanpura_params` missing field keys → check what keys it expects
- OSC send fails → SC not running (expected if SND-001 not done yet), but the function should not crash

### Step 4: Add `/sound/tanpura` route

```python
@app.route("/sound/tanpura")
def _sound_tanpura():
    """Compute and send tanpura parameters for current field state."""
    from npu_engine.tanpura_field import derive_tanpura_params
    from npu_engine.tanpura_engine import TanpuraEngine
    from npu_engine.sound.osc_bridge import send_sound_spec
    
    fs = build_field_state()
    params = derive_tanpura_params(fs)
    engine = TanpuraEngine()
    spec = engine.render(params)
    
    # Send to SC (will silently fail if SC not running)
    try:
        send_sound_spec(spec)
        spec["osc_sent"] = True
    except Exception as e:
        spec["osc_sent"] = False
        spec["osc_error"] = str(e)
    
    return jsonify(spec)
```

### Step 5: Test the route

```bash
curl -s localhost:5000/sound/tanpura | python3 -m json.tool
```

Should return a JSON spec with string frequencies, jivari values, etc.
`osc_sent` will be `false` until SND-001 is done — that's expected.

### Step 6: Wire `/sound/spec` to include tanpura

Read the current `/sound/spec` implementation. If it doesn't include tanpura params,
add them:

```python
# In _sound_spec():
tanpura_params = derive_tanpura_params(fs)
spec["tanpura"] = tanpura_params
```

## Success check

```bash
curl -s localhost:5000/sound/tanpura | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert 'sa_hz' in d or 'strings' in d or 'params' in d, f'Missing tanpura data: {list(d.keys())}'
print('Tanpura route OK')
print('Keys:', list(d.keys()))
print('SC sent:', d.get('osc_sent'))
"
```

## Output

- Fix any errors in tanpura pipeline
- Add GET /sound/tanpura route to kernel.py
- Update /sound/spec to include tanpura params
