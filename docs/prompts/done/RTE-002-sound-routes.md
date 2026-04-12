# RTE-002: Wire sound routes to engines

**Phase**: 2 — First audio  
**Priority**: HIGH  
**Estimated time**: 2–3 hrs  
**Depends on**: SND-001 (PipeWire/JACK — human task, but routes can be wired regardless)

## Context

16 sound routes exist in kernel.py but only `/sound/spec` is FULL. The others
(`/sound/raga`, `/sound/mantra`, `/sound/voice`, `/sound/bols`, `/sound/mode`, etc.)
have inline stubs or no implementation. The engines are all written — they just need
wiring.

## Instructions

### Step 1: Read the existing sound routes

```bash
grep -n "def _sound" ~/atlas_core/kernel.py | head -30
```

For each function, read its body in kernel.py.

### Step 2: Read the target engines

```bash
cat ~/atlas_core/npu_engine/sound/sound_engine.py
cat ~/atlas_core/npu_engine/sound/osc_bridge.py
cat ~/atlas_core/npu_engine/field_to_sound.py | head -60
cat ~/atlas_core/npu_engine/tabla_sampler.py | head -40
cat ~/atlas_core/npu_engine/phrase_engine.py | head -40
```

### Step 3: Wire each route

**`/sound/raga` (POST)** — accepts `{raga_id, duration}`, sends OSC raga spec:
```python
from npu_engine.field_to_sound import get_treatment_vector
from npu_engine.sound.sound_engine import SoundEngine
from npu_engine.sound.osc_bridge import send_sound_spec
fs = build_field_state()
spec = SoundEngine().compute(fs)
return jsonify(send_sound_spec(spec) or spec)
```

**`/sound/bols` (POST)** — tabla bols for current tala:
```python
from npu_engine.tabla_sampler import render_tala_beat
fs = build_field_state()
result = render_tala_beat(fs.get('panchanga', {}).get('tithi_num', 1))
return jsonify(result)
```

**`/sound/mantra` (POST)** — bija mantra synthesis:
```python
from npu_engine.bija_synth import _synth_varna
```

**`/sound/state` (GET)** — current sound engine state:
```python
from npu_engine.sound.sound_engine import SoundEngine
fs = build_field_state()
return jsonify(SoundEngine().state(fs))
```

**`/sound/mode` (GET/POST)** — get or set perform mode:
Read current implementation; if it's a stub, implement as a simple
in-memory mode store (global dict) with get/set.

**`/sound/recommend` (GET)** — raga recommendation for field state:
```python
from npu_engine.field_to_sound import get_treatment_vector
fs = build_field_state()
return jsonify(get_treatment_vector(fs))
```

For each route: read the existing stub, understand what it should return,
wire it to the correct engine, test it.

### Step 4: Test each

```bash
curl -s localhost:5000/sound/state | python3 -m json.tool | head -20
curl -s localhost:5000/sound/recommend | python3 -m json.tool | head -20
curl -s -X POST localhost:5000/sound/raga | python3 -m json.tool | head -20
```

## Success check

```bash
for route in /sound/state /sound/recommend /sound/spec; do
  code=$(curl -s -o /dev/null -w '%{http_code}' localhost:5000$route)
  echo "$route: $code"
done
# All should be 200, not 500
```

At least 3 sound routes returning 200 (not necessarily producing audio yet —
that requires SND-001).

## Output

- Modify sound route functions in `kernel.py`
- No new files required
