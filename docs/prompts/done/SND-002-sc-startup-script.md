# SND-002: Write SuperCollider startup script and config

**Phase**: 2 — First audio  
**Priority**: HIGH  
**Depends on**: SND-001 (PipeWire/JACK — human task, but this can be prepared regardless)

## Context

SuperCollider needs a reliable startup sequence: boot scsynth, load atlas_synth.scd,
load atlas_mix.scd, confirm SynthDefs are registered, signal readiness to the Flask kernel.
This task writes that script and the OSC readiness endpoint.

## Instructions

### Step 1: Read existing SC files

```bash
cat ~/atlas_core/sc/atlas_synth.scd
cat ~/atlas_core/sc/atlas_mix.scd
```

Identify all SynthDef names defined in these files — you'll use them for verification.

### Step 2: Write `sc/start_atlas.sh`

```bash
#!/bin/bash
# sc/start_atlas.sh — Atlas SuperCollider startup
# Starts scsynth via PipeWire JACK, loads SynthDefs, signals readiness.

set -e
ATLAS_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG="$ATLAS_ROOT/logs/sound.log"
SC_PORT=57110
OSC_READY_URL="http://localhost:5000/sound/sc_ready"

echo "[$(date)] Starting Atlas sound engine..." | tee -a "$LOG"

# Start scsynth via PipeWire JACK
pw-jack scsynth -u $SC_PORT -D 0 -l 1 >> "$LOG" 2>&1 &
SCSYNTH_PID=$!
echo $SCSYNTH_PID > /tmp/atlas_scsynth.pid
echo "[$(date)] scsynth PID: $SCSYNTH_PID" | tee -a "$LOG"

# Wait for scsynth to be ready
sleep 3

# Load SynthDefs via sclang
pw-jack sclang << 'EOF' >> "$LOG" 2>&1
s = Server(\atlas, NetAddr("127.0.0.1", 57110));
s.boot;
s.waitForBoot({
    "Loading atlas_synth.scd...".postln;
    thisProcess.nowExecutingPath.dirname +/+ "../sc/atlas_synth.scd".load;
    "Loading atlas_mix.scd...".postln;
    thisProcess.nowExecutingPath.dirname +/+ "../sc/atlas_mix.scd".load;
    s.sync;
    "Atlas SynthDefs loaded. Ready.".postln;
    // Signal Flask kernel that SC is ready
    0.exit;
});
EOF

echo "[$(date)] SynthDefs loaded" | tee -a "$LOG"

# Signal to Flask that SC is ready
curl -s -X POST "http://localhost:5000/sound/sc_ready" \
  -H "Content-Type: application/json" \
  -d '{"status":"ready","port":57110}' >> "$LOG" 2>&1 || true

echo "[$(date)] Atlas sound engine ready" | tee -a "$LOG"
```

Make executable: `chmod +x sc/start_atlas.sh`

### Step 3: Write `sc/stop_atlas.sh`

```bash
#!/bin/bash
if [ -f /tmp/atlas_scsynth.pid ]; then
    kill $(cat /tmp/atlas_scsynth.pid) 2>/dev/null || true
    rm /tmp/atlas_scsynth.pid
    echo "scsynth stopped"
fi
curl -s -X POST http://localhost:5000/sound/sc_ready \
  -d '{"status":"stopped"}' > /dev/null 2>&1 || true
```

### Step 4: Add `/sound/sc_ready` route to kernel.py

This lets the shell script signal SC state to the Flask kernel:

```python
_SC_STATE = {"status": "unknown", "port": 57110}

@app.route("/sound/sc_ready", methods=["POST", "GET"])
def _sound_sc_ready():
    global _SC_STATE
    if request.method == "POST":
        _SC_STATE.update(request.get_json(force=True) or {})
        return jsonify({"ok": True, "state": _SC_STATE})
    return jsonify(_SC_STATE)
```

Update `/sound/state` to include SC state:
```python
@app.route("/sound/state")
def _sound_state():
    return jsonify({**_SC_STATE, "engine": "ready"})
```

### Step 5: Verify scripts are valid bash

```bash
bash -n ~/atlas_core/sc/start_atlas.sh && echo "start_atlas.sh: syntax OK"
bash -n ~/atlas_core/sc/stop_atlas.sh && echo "stop_atlas.sh: syntax OK"
```

## Success check

```bash
# Scripts exist and are executable
test -x ~/atlas_core/sc/start_atlas.sh && echo "start_atlas.sh: OK"
test -x ~/atlas_core/sc/stop_atlas.sh && echo "stop_atlas.sh: OK"

# SC ready route exists
curl -s localhost:5000/sound/sc_ready | python3 -c \
  "import sys,json; d=json.load(sys.stdin); print('sc_ready route OK:', d.get('status'))"
```

## Output

- Write `sc/start_atlas.sh` (executable)
- Write `sc/stop_atlas.sh` (executable)
- Add `/sound/sc_ready` GET/POST route to kernel.py
- Update `/sound/state` to include SC state
