#!/bin/bash
# start_atlas.sh — Atlas SuperCollider startup
# Boots scsynth via PipeWire JACK, loads SynthDefs, signals readiness to Flask.
#
# Usage: ./sc/start_atlas.sh
#
# SynthDefs loaded:
#   \tanpura_engine  \tanpura_string  \raga_note
#   \tabla_bol       \bija_drone      \master

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG="$PROJECT_DIR/logs/sound.log"
SC_PORT=57110
OSC_READY_URL="http://localhost:5000/sound/sc_ready"

mkdir -p "$PROJECT_DIR/logs"

echo "[$(date)] Starting Atlas sound engine..." | tee -a "$LOG"

# Kill any existing SC processes
pkill -9 scsynth 2>/dev/null || true
pkill -9 sclang 2>/dev/null || true
sleep 1

# Boot scsynth via PipeWire JACK bridge
JACK_NO_AUDIO_RESERVATION=1 \
JACK_START_SERVER=0 \
PIPEWIRE_LATENCY=1024/48000 \
pw-jack scsynth -u $SC_PORT -o 2 -i 0 -R 0 -l 1 >> "$LOG" 2>&1 &
SCSYNTH_PID=$!
echo "$SCSYNTH_PID" > /tmp/atlas_scsynth.pid
echo "[$(date)] scsynth PID: $SCSYNTH_PID" | tee -a "$LOG"

# Wait for scsynth to be ready
sleep 3
if ! kill -0 "$SCSYNTH_PID" 2>/dev/null; then
    echo "[$(date)] ERROR: scsynth failed to start" | tee -a "$LOG"
    curl -s -X POST "$OSC_READY_URL" \
      -H "Content-Type: application/json" \
      -d '{"status":"error","error":"scsynth failed to start"}' >> "$LOG" 2>&1 || true
    exit 1
fi
echo "[$(date)] scsynth running on UDP $SC_PORT" | tee -a "$LOG"

# Connect SC outputs to MOTU M2 via pw-link
echo "[$(date)] Connecting to MOTU M2 via pw-link..." | tee -a "$LOG"
pw-link "SuperCollider:out_1" \
    "alsa_output.usb-MOTU_M2_M20000063536-00.analog-stereo:playback_FL" 2>/dev/null || true
pw-link "SuperCollider:out_2" \
    "alsa_output.usb-MOTU_M2_M20000063536-00.analog-stereo:playback_FR" 2>/dev/null || true
echo "[$(date)] Audio routing connected (pw-link)" | tee -a "$LOG"

# Load Atlas SynthDefs via sclang
echo "[$(date)] Loading Atlas SynthDefs..." | tee -a "$LOG"
sclang -e "
Server.default = Server(\\atlas, NetAddr(\"127.0.0.1\", $SC_PORT));
Server.default.doWhenBooted({
    [\"$SCRIPT_DIR/atlas_synth.scd\", \"$SCRIPT_DIR/atlas_mix.scd\"].do({ |f|
        f.load;
        (\"Loaded: \" ++ f).postln;
    });
    \"Atlas SynthDefs loaded.\".postln;
});
" >> "$LOG" 2>&1 &
SCLANG_PID=$!
echo "$SCLANG_PID" > /tmp/atlas_sclang.pid
sleep 5

echo "[$(date)] SynthDefs loaded" | tee -a "$LOG"

# Signal to Flask that SC is ready
curl -s -X POST "$OSC_READY_URL" \
  -H "Content-Type: application/json" \
  -d "{\"status\":\"ready\",\"port\":$SC_PORT,\"pid\":$SCSYNTH_PID,\"synthdefs\":[\"tanpura_engine\",\"tanpura_string\",\"raga_note\",\"tabla_bol\",\"bija_drone\",\"master\"]}" \
  >> "$LOG" 2>&1 || true

echo "[$(date)] Atlas sound engine ready" | tee -a "$LOG"
echo "  scsynth PID: $SCSYNTH_PID"
echo "  sclang PID: $SCLANG_PID"
echo "  UDP port:   $SC_PORT"

# Keep alive for systemd
wait "$SCSYNTH_PID"
