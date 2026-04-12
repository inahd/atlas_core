# SND-006: Verify tanpura audio end-to-end

**Phase**: 2 — First audio  
**Priority**: HIGH  
**Status**: HUMAN_REQUIRED (audio verification needed)  
**Depends on**: SND-001 (PipeWire/JACK — human task), SND-002, SND-005

## Context

Once PipeWire/JACK is configured and SuperCollider is running (SND-001, human task),
this task verifies the complete tanpura audio path and fixes any remaining issues.

## Automated preparation (Claude Code can do this)

### Step 1: Verify SC is running

```bash
curl -s localhost:5000/sound/sc_ready | python3 -m json.tool
# status should be "ready"

# Check scsynth process
pgrep scsynth && echo "scsynth running" || echo "scsynth NOT running"

# Check OSC port is listening
ss -ulnp | grep 57110 || echo "port 57110 not listening"
```

### Step 2: Send a test tone via OSC

```bash
cd ~/atlas_core
python3 -c "
from npu_engine.sound.osc_bridge import send_sound_spec
result = send_sound_spec({
    'type': 'tanpura',
    'sa_hz': 261.63,
    'pa_hz': 392.00,
    'volume': 0.6,
    'reverb': 0.3
})
print('OSC send result:', result)
"
```

### Step 3: Test full pipeline

```bash
curl -s -X POST localhost:5000/sound/tanpura | python3 -m json.tool
# osc_sent should be true if SC is running
```

### Step 4: Check SC post window for errors

```bash
tail -50 ~/atlas_core/logs/sound.log
# Look for: SynthDef loaded, any errors
```

### Step 5: Verify SynthDef names match

```bash
# Get SynthDef names from atlas_synth.scd
grep "SynthDef(" ~/atlas_core/sc/atlas_synth.scd | grep -oP '"[^"]+"'

# Get SynthDef names the OSC bridge uses
grep "SynthDef\|synthDef\|synth_name" ~/atlas_core/npu_engine/sound/sound_engine.py | head -10
```

Names must match exactly — case sensitive.

## Human action required

After automated prep completes:
1. Run `bash ~/atlas_core/sc/start_atlas.sh`
2. Listen — tanpura drone should be audible from MOTU M2
3. Run `curl -X POST localhost:5000/sound/tanpura`
4. Adjust volume if needed via `/sound/volume`
5. Confirm by running: `curl localhost:5000/sound/state`

## Success check (automated part)

```bash
python3 -c "
from npu_engine.sound.osc_bridge import send_sound_spec
try:
    result = send_sound_spec({'type': 'tanpura', 'sa_hz': 261.63})
    print('OSC bridge: functional (SC may or may not be running)')
except Exception as e:
    print('OSC bridge ERROR:', e)
"
# Should not crash even if SC is not running
```

## Output

- Fix any SynthDef name mismatches between sound_engine.py and atlas_synth.scd
- Fix any OSC bridge errors
- Document: what works, what volume level, any latency issues
