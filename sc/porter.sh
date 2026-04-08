#!/bin/bash
# porter.sh — JACK connection watchdog
#
# Keeps SuperCollider → MOTU M2 connections alive.
# SC stays running for future Talachakra work;
# om.py handles tanpura/tabla/melody via pw-cat.
#
# Usage: ./sc/porter.sh &

INTERVAL=10

while true; do
    if pgrep -x scsynth >/dev/null 2>&1; then
        pw-jack jack_connect "SuperCollider:out_1" \
            "M Series Analog Stereo:playback_FL" 2>/dev/null
        pw-jack jack_connect "SuperCollider:out_2" \
            "M Series Analog Stereo:playback_FR" 2>/dev/null
    fi
    sleep "$INTERVAL"
done
