# ENV-004: Health monitoring script

**Phase**: 3  
**Priority**: MEDIUM  
**Estimated time**: 1 hr  
**Depends on**: ENV-003 (systemd services installed)

## Context

No automated health monitoring exists. If the kernel crashes or SC dies,
nothing alerts and nothing restarts. This task adds a lightweight health
check script and cron job.

## Instructions

### Step 1: Write scripts/atlas-health.sh

```bash
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
    systemctl restart atlas-kernel 2>/dev/null || \
      (cd "$ATLAS_ROOT" && python kernel.py > "$LOG" 2>&1 &)
    sleep 5
    curl -s --max-time 3 localhost:5000/health > /dev/null 2>&1 && \
      log "kernel: restarted OK" || log "kernel: restart FAILED"
fi

# Check SC (if service installed)
if systemctl is-active atlas-sound > /dev/null 2>&1; then
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
```

### Step 2: Make executable and test

```bash
chmod +x ~/atlas_core/scripts/atlas-health.sh
bash ~/atlas_core/scripts/atlas-health.sh
cat ~/atlas_core/logs/health.log
```

### Step 3: Install cron job

```bash
# Add to crontab — check every 5 minutes
(crontab -l 2>/dev/null; echo "*/5 * * * * bash $HOME/atlas_core/scripts/atlas-health.sh") | crontab -
crontab -l | grep atlas
```

### Step 4: Add /health route detail

The existing `/health` route likely returns minimal data. Enrich it:

```python
@app.route("/health")
def _health():
    import time
    from npu_engine.build_field_state import build_field_state
    health = {"status": "ok", "timestamp": time.time(), "uptime": time.time() - START_TIME}
    try:
        fs = build_field_state()
        health["field"] = "ok"
        health["nakshatra"] = fs.get("panchanga", {}).get("nakshatra")
    except Exception as e:
        health["field"] = f"error: {e}"
        health["status"] = "degraded"
    return jsonify(health)
```

(Add `START_TIME = time.time()` near the top of kernel.py)

## Success check

```bash
bash ~/atlas_core/scripts/atlas-health.sh
tail -5 ~/atlas_core/logs/health.log
# Should show "health check complete" with no WARN lines

crontab -l | grep atlas
# Should show the cron entry

curl -s localhost:5000/health | python3 -c "
import sys,json; d=json.load(sys.stdin)
assert d.get('status') in ('ok','degraded')
print('Health endpoint OK:', d.get('status'), '| field:', d.get('field'))
"
```

## Output

- Write `scripts/atlas-health.sh`
- Install cron job
- Enrich `/health` route in kernel.py
- Create `logs/` directory if not present
