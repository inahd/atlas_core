#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════
# Atlas Core — system boot and control
#
# Usage:
#   ./start.sh            full boot: kernel + SC + ngrok
#   ./start.sh kernel     restart kernel only
#   ./start.sh sc         restart SuperCollider (scsynth + sclang + sc_boot)
#   ./start.sh sound      same as sc
#   ./start.sh boot-sc    scsynth only via start_sc.sh + sc_boot POST
#   ./start.sh tanpura    POST /sound/sc_boot — send field params to SC
#   ./start.sh ngrok      restart ngrok tunnel
#   ./start.sh status     show status of all components
#   ./start.sh stop       stop everything gracefully
#   ./start.sh reset      full reset — kill all, clean, reboot
#   ./start.sh url        print current ngrok URL
#   ./start.sh logs       follow kernel + scsynth logs
#   ./start.sh services   show systemd service status
#   ./start.sh audio      check audio route + connections
# ═══════════════════════════════════════════════════════════
set -u

ATLAS=~/atlas_core
KERNEL_LOG=/tmp/atlas_kernel.log
SC_LOG=/tmp/scsynth.log
NGROK_LOG=/tmp/ngrok.log
PORT=5000

cd "$ATLAS"

# ── helpers ───────────────────────────────────────────────

_kernel_pid() { pgrep -f "python3.*kernel\.py" 2>/dev/null | head -1; }
_ngrok_pid()  { pgrep -f "ngrok.*http.*$PORT" 2>/dev/null | head -1; }
_scsynth_pid(){ pgrep -x scsynth 2>/dev/null | head -1; }
_sclang_pid() { pgrep -x sclang 2>/dev/null | head -1; }
_sc_running() { [ -n "$(_scsynth_pid)" ] || [ -n "$(_sclang_pid)" ]; }

_ngrok_url() {
  curl -s --max-time 2 localhost:4040/api/tunnels 2>/dev/null \
    | python3 -c "
import sys, json
try:
    t = json.load(sys.stdin).get('tunnels', [])
    print(t[0]['public_url'] if t else '')
except Exception:
    print('')
" 2>/dev/null
}

_wait_kernel() {
  local max=${1:-30}
  for i in $(seq 1 "$max"); do
    if curl -s --max-time 2 "localhost:$PORT/health" >/dev/null 2>&1; then
      return 0
    fi
    sleep 1
  done
  return 1
}

# ── subcommands ───────────────────────────────────────────

do_kernel() {
  echo "  stopping old kernel…"
  local pid; pid=$(_kernel_pid)
  [ -n "$pid" ] && kill "$pid" 2>/dev/null
  fuser -k "$PORT/tcp" 2>/dev/null || true
  sleep 1

  echo "  starting kernel.py…"
  cd "$ATLAS"
  python3 kernel.py > "$KERNEL_LOG" 2>&1 &
  local kpid=$!
  echo "  kernel pid $kpid — waiting…"

  if _wait_kernel 30; then
    echo "  ✦ kernel ready on :$PORT"
    echo "    home:  http://localhost:$PORT/home"
    echo "    field: http://localhost:$PORT/field"
  else
    echo "  ✗ kernel failed to start"
    echo "  check: tail -20 $KERNEL_LOG"
    return 1
  fi
}

do_sc() {
  echo "  stopping old SC…"
  pkill -9 scsynth 2>/dev/null || true
  pkill -9 sclang 2>/dev/null || true
  sleep 1

  echo "  starting SC via start_sc.sh…"
  cd "$ATLAS"
  bash sc/start_sc.sh &
  local SC_PID=$!

  # Wait for scsynth + sclang to boot
  echo "  waiting for SC engine…"
  sleep 10

  if _sc_running; then
    echo "  ✦ SC running (scsynth=$(_scsynth_pid) sclang=$(_sclang_pid))"
    echo "    SynthDefs: tanpura_engine, raga_note, tabla_bol, bija_drone"
    echo "    OSC recv:  sclang on :57120"

    # Send field params to instantiate tanpura
    do_tanpura
  else
    echo "  ✗ SC failed — check $SC_LOG"
    tail -5 "$SC_LOG" 2>/dev/null
  fi
}

do_sound() { do_sc; }
do_boot_sc() { do_sc; }

do_tanpura() {
  echo "  sending field params to SC…"
  local result
  result=$(curl -s -X POST "localhost:$PORT/sound/sc_boot" \
    -H 'Content-Type: application/json' 2>/dev/null)
  if echo "$result" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    if d.get('booted'):
        print('  ✦ tanpura booted · Sa=%sHz' % d.get('sa_hz', '?'))
    else:
        print('  ⚠ sc_boot: %s' % d.get('error', 'unknown'))
except:
    print('  ⚠ kernel not responding')
" 2>/dev/null; then
    true
  else
    echo "  ⚠ kernel not responding — tanpura not sent"
  fi
}

do_ngrok() {
  echo "  stopping old ngrok…"
  local pid; pid=$(_ngrok_pid)
  [ -n "$pid" ] && kill "$pid" 2>/dev/null
  sleep 1

  echo "  starting ngrok…"
  ngrok http "$PORT" --log=stdout > "$NGROK_LOG" 2>&1 &
  sleep 3

  local url; url=$(_ngrok_url)
  if [ -n "$url" ]; then
    echo "  ✦ ngrok active"
    echo ""
    echo "  ╔═══════════════════════════════════════╗"
    echo "  ║  $url  ║"
    echo "  ╚═══════════════════════════════════════╝"
    echo ""
  else
    echo "  ✗ ngrok failed — check $NGROK_LOG"
  fi
}

do_url() {
  local url; url=$(_ngrok_url)
  if [ -n "$url" ]; then
    echo "$url"
  else
    echo "no tunnel"
  fi
}

do_stop() {
  echo "  stopping Atlas Core…"

  local pid

  # ngrok
  pid=$(_ngrok_pid)
  [ -n "$pid" ] && { kill "$pid" 2>/dev/null; echo "  ngrok stopped"; }

  # kernel
  pid=$(_kernel_pid)
  [ -n "$pid" ] && { kill "$pid" 2>/dev/null; echo "  kernel stopped"; }
  fuser -k "$PORT/tcp" 2>/dev/null || true

  # SC
  pkill -9 sclang 2>/dev/null && echo "  sclang stopped"
  pkill -9 scsynth 2>/dev/null && echo "  scsynth stopped"

  echo "  ✦ stopped"
}

do_status() {
  echo ""
  echo "── Atlas Core Status ─────────────────────────"

  # kernel
  local kpid; kpid=$(_kernel_pid)
  if [ -n "$kpid" ]; then
    echo "kernel         ● running (pid $kpid)  :$PORT"
  else
    echo "kernel         ○ not running"
  fi

  # scsynth
  local scpid; scpid=$(_scsynth_pid)
  if [ -n "$scpid" ]; then
    echo "scsynth        ● running (pid $scpid)  :57110"
  else
    echo "scsynth        ○ not running"
  fi

  # sclang
  local slpid; slpid=$(_sclang_pid)
  if [ -n "$slpid" ]; then
    echo "sclang         ● running (pid $slpid)  OSC :57120"
  else
    echo "sclang         ○ not running"
  fi

  # SC sound state from kernel
  if [ -n "$kpid" ]; then
    curl -s --max-time 2 "localhost:$PORT/sound/state" 2>/dev/null | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    raga = d.get('raga', d.get('raga_name', '—'))
    bpm = d.get('bpm', '—')
    sa = d.get('sa_hz', '—')
    print(f'sound          {raga} · {bpm}bpm · Sa={sa}Hz')
except:
    print('sound          (no spec)')
" 2>/dev/null || true
  fi

  # ngrok
  local npid; npid=$(_ngrok_pid)
  local url; url=$(_ngrok_url)
  if [ -n "$npid" ] && [ -n "$url" ]; then
    echo "ngrok          ● active → $url"
  elif [ -n "$npid" ]; then
    echo "ngrok          ● running (no tunnel yet)"
  else
    echo "ngrok          ○ not running"
  fi

  # field data
  if [ -n "$kpid" ]; then
    curl -s --max-time 3 "localhost:$PORT/field" 2>/dev/null | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    p = d.get('panchanga', {})
    nak = p.get('nakshatra', '—')
    tithi = p.get('tithi', '—')
    devi = p.get('devi', {})
    if isinstance(devi, dict): devi = devi.get('name', '—')
    ss = d.get('sound_state', {})
    raga = ss.get('raga', '—')
    print(f'field          {nak} · {tithi} · {devi} · {raga}')
except Exception as e:
    print(f'field          (parse error)')
" 2>/dev/null || echo "field          (kernel not responding)"
  fi

  # PipeWire audio connections
  if command -v pw-link >/dev/null 2>&1; then
    local sc_links
    sc_links=$(pw-link -l 2>/dev/null | grep -c "SuperCollider" || echo 0)
    if [ "$sc_links" -gt 0 ]; then
      echo "audio          ● SC connected ($sc_links links)"
    else
      echo "audio          ○ SC not connected"
    fi
  fi

  echo "──────────────────────────────────────────────"
  echo "  home:  http://localhost:$PORT/home"
  echo "  s4:    http://localhost:$PORT/s4"
  echo ""
}

do_audio() {
  echo ""
  echo "── Audio Route ───────────────────────────────"
  python3 -c "
from npu_engine.field.system_engine import derive_audio_route, check_audio_connections, restore_audio_connections

route = derive_audio_route()
conns = check_audio_connections()

print(f'primary:  {route[\"primary\"] or \"none\"}')
print(f'synth:    {route[\"synthesis\"]}')
if route['fallback']:
    print(f'fallback: {route[\"fallback\"]}')
for b in route.get('broken', []):
    print(f'broken:   {b}')
print()

if conns['connected']:
    for src, sink in conns['connected']:
        print(f'  ✓ {src} → {sink}')
for m in conns.get('missing', []):
    print(f'  ✗ {m}')

if conns.get('missing'):
    print()
    print('restoring connections…')
    ok = restore_audio_connections()
    print(f'result: {\"ok\" if ok else \"failed\"}')
else:
    print()
    print('all connections live')
" 2>&1
  echo "──────────────────────────────────────────────"
  echo ""
}

do_boot() {
  echo ""
  echo "  ✦ Atlas Core starting…"
  echo ""

  # Kill stale
  echo "  cleaning stale processes…"
  local pid
  pid=$(_kernel_pid);  [ -n "$pid" ] && kill "$pid" 2>/dev/null
  pid=$(_ngrok_pid);   [ -n "$pid" ] && kill "$pid" 2>/dev/null
  pkill -9 sclang 2>/dev/null || true
  pkill -9 scsynth 2>/dev/null || true
  fuser -k "$PORT/tcp" 2>/dev/null || true
  sleep 1

  # Kernel first
  do_kernel || exit 1

  # SuperCollider
  echo ""
  do_sc

  # ngrok (optional)
  # do_ngrok

  # Final status
  echo ""
  echo "  ══════════════════════════════════════"
  echo "    Atlas Core Field Computer"
  echo "  ══════════════════════════════════════"
  echo "    home:     http://localhost:$PORT/home"
  echo "    field:    http://localhost:$PORT/field"
  echo "    s-layers: /s0 through /s6"
  echo "    s4 bloom: http://localhost:$PORT/s4"
  echo "  ══════════════════════════════════════"
  echo ""
  echo "  logs:"
  echo "    kernel:  tail -f $KERNEL_LOG"
  echo "    scsynth: tail -f $SC_LOG"
  echo ""
  echo "  stop:  ./start.sh stop"
  echo ""

  do_status

  wait "$(_kernel_pid)" 2>/dev/null
}

do_reset() {
  echo ""
  echo "  ✦ Atlas Core full reset…"
  echo ""

  echo "  killing all processes…"
  pkill -f "python3.*kernel\.py" 2>/dev/null || true
  pkill -9 scsynth 2>/dev/null || true
  pkill -9 sclang 2>/dev/null || true
  pkill -f "ngrok.*http" 2>/dev/null || true
  fuser -k "$PORT/tcp" 2>/dev/null || true
  sleep 2
  echo "  ✓ all processes stopped"

  echo "  cleaning temp files…"
  rm -f "$KERNEL_LOG" "$SC_LOG" "$NGROK_LOG"
  echo "  ✓ cleaned"

  do_boot
}

do_logs() {
  echo "Tailing kernel + scsynth logs (Ctrl+C to stop):"
  tail -f "$KERNEL_LOG" "$SC_LOG" 2>/dev/null
}

do_services() {
  echo ""
  echo "── Systemd Services ──────────────────────────"
  for unit in atlas-kernel atlas-sound; do
    local state
    state=$(systemctl --user is-active "$unit.service" 2>/dev/null) || state="inactive"
    local mark="○"
    [ "$state" = "active" ] && mark="●"
    [ "$state" = "failed" ] && mark="✗"
    printf "  %s %-20s %s\n" "$mark" "$unit" "$state"
  done
  echo "──────────────────────────────────────────────"
  echo ""
}

# ── dispatch ──────────────────────────────────────────────

case "${1:-boot}" in
  sound|sc)   do_sc ;;
  boot-sc)    do_sc ;;
  tanpura)    do_tanpura ;;
  audio)      do_audio ;;
  kernel)     do_kernel ;;
  ngrok)      do_ngrok ;;
  status)     do_status ;;
  services)   do_services ;;
  stop)       do_stop ;;
  url)        do_url ;;
  reset)      do_reset ;;
  logs)       do_logs ;;
  boot|*)     do_boot ;;
esac
