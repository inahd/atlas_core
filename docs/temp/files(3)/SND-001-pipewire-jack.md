# SND-001: Configure PipeWire JACK bridge

**Phase**: 2 — First audio  
**Priority**: CRITICAL  
**Status**: HUMAN_REQUIRED  
**Reason**: Requires physical audio hardware verification (MOTU M2)

## Context

The sound computation layer is complete. The only gap is audio plumbing.
SuperCollider needs to see the MOTU M2 audio interface via a JACK-compatible
audio server. On this system (Ubuntu 24, Meteor Lake NUC), PipeWire provides
JACK compatibility via `pipewire-jack`.

## Why this is HUMAN_REQUIRED

This task requires:
1. Physical verification that the MOTU M2 is connected and powered
2. Listening to verify audio output actually works
3. Possible firmware/driver iteration that can't be verified programmatically

## What Claude Code can prepare (run this part automatically)

### Check current audio state

```bash
# What audio devices are visible:
pactl list cards short
aplay -l
# Is pipewire-jack installed:
dpkg -l | grep pipewire
pw-jack --version 2>/dev/null || echo "pw-jack not found"
# Is SuperCollider installed:
which scsynth sclang
scsynth -v 2>/dev/null | head -2
```

### Install missing packages if needed

```bash
sudo apt-get install -y pipewire-jack jackd2 supercollider
```

### Write the SC startup script (preparatory)

Write `sc/start_atlas.sh`:
```bash
#!/bin/bash
# Atlas SuperCollider startup
set -e

echo "Starting SuperCollider server..."
pw-jack scsynth -u 57110 -D 0 &
SCSYNTH_PID=$!
sleep 3

echo "Loading Atlas SynthDefs..."
pw-jack sclang -e "
Server.default = Server(\atlas, NetAddr(\\"127.0.0.1\\", 57110));
Server.default.boot;
Server.default.doWhenBooted({
    [\\"sc/atlas_synth.scd\\", \\"sc/atlas_mix.scd\\"].do({ |f| f.load });
    \\"Atlas SynthDefs loaded\\".postln;
});
"

echo "SC server PID: $SCSYNTH_PID"
echo $SCSYNTH_PID > /tmp/atlas_sc.pid
```

### Write the systemd service files (preparatory)

Write `config/atlas-kernel.service`:
```ini
[Unit]
Description=Atlas 330 Flask Kernel
After=network.target

[Service]
Type=simple
User=%i
WorkingDirectory=/root/atlas_core
ExecStart=/usr/bin/python3 /root/atlas_core/kernel.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Write `config/atlas-sound.service`:
```ini
[Unit]
Description=Atlas 330 SuperCollider Sound Engine
After=atlas-kernel.service pipewire.service

[Service]
Type=simple
User=%i
WorkingDirectory=/root/atlas_core
ExecStart=/bin/bash /root/atlas_core/sc/start_atlas.sh
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## What needs human action

1. Connect MOTU M2, power on
2. Run `pactl list cards short` — verify M2 appears
3. Run `sc/start_atlas.sh`
4. Run `curl localhost:5000/sound/spec` — verify JSON output
5. Check SC post window for SynthDef load confirmation
6. Play a test tone: `curl -X POST localhost:5000/sound/bols`

## Output (automated part)

- Write `sc/start_atlas.sh` (executable)
- Write `config/atlas-kernel.service`
- Write `config/atlas-sound.service`
- Print checklist for human to follow
