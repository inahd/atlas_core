#!/bin/bash
# start_sc.sh — Boot SC audio engine for Atlas
#
# Starts scsynth via PipeWire JACK bridge,
# connects to MOTU M2, then loads atlas_synth.scd
#
# Usage: ./sc/start_sc.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Kill any existing SC processes
pkill -9 scsynth 2>/dev/null || true
pkill -9 sclang 2>/dev/null || true
sleep 1

echo "Starting scsynth via PipeWire JACK bridge..."
# JACK_NO_AUDIO_RESERVATION=1 prevents JACK shim from trying to reserve ALSA device
# JACK_START_SERVER=0 prevents fallback JACK server launch
JACK_NO_AUDIO_RESERVATION=1 \
JACK_START_SERVER=0 \
PIPEWIRE_LATENCY=1024/48000 \
pw-jack scsynth -u 57110 -o 2 -i 0 -R 0 -l 1 \
    &>/tmp/scsynth.log &
SCSYNTH_PID=$!
echo "scsynth PID: $SCSYNTH_PID"

# Wait for scsynth to be ready
sleep 3
if ! kill -0 $SCSYNTH_PID 2>/dev/null; then
    echo "ERROR: scsynth failed to start"
    cat /tmp/scsynth.log
    exit 1
fi
echo "scsynth running."

# Connect SC outputs to MOTU M2 via pw-link (native PipeWire, not JACK shim)
# NOTE: pw-jack jack_connect creates connections that appear but don't pass audio
# on PipeWire 1.2.6 with SC 3.13.0. pw-link is preferred.
echo "Connecting to MOTU M2 via pw-link..."
pw-link "SuperCollider:out_1" \
    "alsa_output.usb-MOTU_M2_M20000063536-00.analog-stereo:playback_FL" 2>/dev/null || true
pw-link "SuperCollider:out_2" \
    "alsa_output.usb-MOTU_M2_M20000063536-00.analog-stereo:playback_FR" 2>/dev/null || true
echo "Audio connected (pw-link)."
echo "WARNING: SC→MOTU audio may be silent due to PW 1.2.6 JACK shim bug."
echo "om.py (pw-cat) is the working audio output path."

# Start sclang with atlas_synth.scd
echo "Loading atlas_synth.scd..."
exec sclang "$SCRIPT_DIR/atlas_synth.scd"
