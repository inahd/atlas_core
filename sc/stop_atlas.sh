#!/bin/bash
# stop_atlas.sh — Stop Atlas SuperCollider processes
# Kills scsynth + sclang and signals Flask.

OSC_READY_URL="http://localhost:5000/sound/sc_ready"

if [ -f /tmp/atlas_sclang.pid ]; then
    kill "$(cat /tmp/atlas_sclang.pid)" 2>/dev/null || true
    rm -f /tmp/atlas_sclang.pid
    echo "sclang stopped"
fi

if [ -f /tmp/atlas_scsynth.pid ]; then
    kill "$(cat /tmp/atlas_scsynth.pid)" 2>/dev/null || true
    rm -f /tmp/atlas_scsynth.pid
    echo "scsynth stopped"
fi

# Signal Flask that SC is stopped
curl -s -X POST "$OSC_READY_URL" \
  -H "Content-Type: application/json" \
  -d '{"status":"stopped"}' > /dev/null 2>&1 || true

echo "Atlas sound engine stopped"
