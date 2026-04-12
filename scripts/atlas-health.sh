#!/bin/bash
# atlas-health.sh — check Atlas 330 system health and restart if needed

ATLAS_ROOT="$HOME/atlas_core"
LOG="$ATLAS_ROOT/logs/health.log"
TIMESTAMP="$(date '+%Y-%m-%d %H:%M:%S')"

log() { echo "[$TIMESTAMP] $1" | tee -a "$LOG"; }

# Check kernel
if curl -s --max-time 3 localhost:5000/health > /dev/null 2>&1; then
    log "kernel: OK"
else
    log "kernel: DOWN — attempting restart"
    systemctl --user restart atlas-kernel 2>/dev/null || \
      (cd "$ATLAS_ROOT" && python kernel.py >> "$LOG" 2>&1 &)
    sleep 5
    curl -s --max-time 3 localhost:5000/health > /dev/null 2>&1 && \
      log "kernel: restarted OK" || log "kernel: restart FAILED"
fi

# Check SC (if service installed)
if systemctl --user is-active atlas-sound > /dev/null 2>&1; then
    SC_STATE=$(curl -s --max-time 2 localhost:5000/sound/sc_ready | \
               python3 -c "import sys,json; print(json.load(sys.stdin).get('status','unknown'))" 2>/dev/null)
    log "sound: $SC_STATE"
fi

# Quick route probe
for route in /field /goloka /helix; do
    CODE=$(curl -s -o /dev/null -w '%{http_code}' --max-time 2 "localhost:5000$route")
    [ "$CODE" = "200" ] || log "WARN: $route returned $CODE"
done

log "health check complete"
