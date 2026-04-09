#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════
# Atlas Core — system boot and control
#
# Usage:
#   ./start.sh            full boot
#   ./start.sh kernel     restart kernel only
#   ./start.sh sound      restart om.py audio
#   ./start.sh sc         restart SuperCollider
#   ./start.sh dashy      restart Dashy portal
#   ./start.sh ngrok      restart ngrok tunnel
#   ./start.sh status     show status of all components
#   ./start.sh stop       stop everything gracefully
#   ./start.sh reset      full reset — kill all, clean, reboot
#   ./start.sh url        print current ngrok URL
#   ./start.sh logs       follow all service logs
# ═══════════════════════════════════════════════════════════
set -u

ATLAS=~/atlas_core
DASHY=~/dashy
KERNEL_LOG=/tmp/atlas_kernel.log
NGROK_LOG=/tmp/ngrok.log
PORT=5000
DASHY_PORT=4000

cd "$ATLAS"

# ── helpers ───────────────────────────────────────────────

_kernel_pid() { pgrep -f "python3.*kernel\.py" 2>/dev/null | head -1; }
_ngrok_pid()  { pgrep -f "ngrok.*http.*$PORT" 2>/dev/null | head -1; }
_om_pid()     { pgrep -f 'python3.*om\.py' 2>/dev/null | head -1; }
_dashy_pid()  { pgrep -f "node.*$DASHY" 2>/dev/null | head -1; }
_sclang_pid() { pgrep -x sclang 2>/dev/null | head -1; }
_sc_running() { [ -n "$(_sclang_pid)" ]; }

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

_wait_dashy() {
  local max=${1:-15}
  for i in $(seq 1 "$max"); do
    if curl -s --max-time 2 "localhost:$DASHY_PORT" >/dev/null 2>&1; then
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

do_om() {
  echo "  stopping old om.py…"
  pkill -f 'python3.*om\.py' 2>/dev/null || true
  pkill -f pw-cat 2>/dev/null || true
  sleep 1

  echo "  starting om.py (pw-cat → MOTU)…"
  cd "$ATLAS"
  nohup python3 -u om.py >> om.log 2>&1 &
  local OM_PID=$!
  sleep 4

  if kill -0 "$OM_PID" 2>/dev/null; then
    echo "  ✦ om.py running (pid $OM_PID)"
    echo "    output: pw-cat → PipeWire → MOTU M2"
    tail -3 om.log 2>/dev/null | sed 's/^/    /'
  else
    echo "  ✗ om.py failed — check om.log"
    tail -5 om.log 2>/dev/null
  fi
}

do_sound() { do_om; }

do_sc() {
  echo "  stopping old sclang…"
  pkill -9 sclang 2>/dev/null || true
  sleep 1

  echo "  starting sclang (mix relay)…"
  cd "$ATLAS"
  nohup sclang sc/atlas_mix.scd > /tmp/sclang_mix.log 2>&1 &
  sleep 4

  if _sc_running; then
    echo "  ✦ sclang mix relay running (pid $(_sclang_pid))"
    echo "    recv: 57121 (MixKernel) → echo: 57122 (om.py)"
  else
    echo "  ✗ sclang failed — check /tmp/sclang_mix.log"
    tail -5 /tmp/sclang_mix.log 2>/dev/null
  fi
}

do_dashy() {
  echo "  stopping old Dashy…"
  local pid; pid=$(_dashy_pid)
  [ -n "$pid" ] && kill "$pid" 2>/dev/null
  sleep 1

  echo "  starting Dashy portal…"
  cd "$DASHY"
  nohup npm start > /tmp/dashy.log 2>&1 &
  sleep 3

  if _wait_dashy 15; then
    echo "  ✦ Dashy ready on :$DASHY_PORT"
    echo "    http://localhost:$DASHY_PORT"
  else
    echo "  ✗ Dashy failed — check /tmp/dashy.log"
    tail -5 /tmp/dashy.log 2>/dev/null
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

  # Dashy
  pid=$(_dashy_pid)
  [ -n "$pid" ] && { kill "$pid" 2>/dev/null; echo "  Dashy stopped"; }

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

  # om.py + audio
  pkill -f om.py 2>/dev/null && echo "  om.py stopped"
  pkill -f pw-cat 2>/dev/null || true

  echo "  ✦ stopped"
}

do_status() {
  echo ""
  echo "── Atlas Core Status ─────────────────────────"

  # kernel
  local kpid; kpid=$(_kernel_pid)
  if [ -n "$kpid" ]; then
    echo "kernel.py      ● running (pid $kpid)  :$PORT"
  else
    echo "kernel.py      ○ not running"
  fi

  # om.py
  local ompid; ompid=$(_om_pid)
  if [ -n "$ompid" ]; then
    echo "om.py          ● running (pid $ompid) · pw-cat → MOTU"
  else
    echo "om.py          ○ not running"
  fi

  # sclang
  if _sc_running; then
    echo "sclang         ● running (pid $(_sclang_pid)) · 57121→57122"
  else
    echo "sclang         ○ not running"
  fi

  # Dashy
  local dpid; dpid=$(_dashy_pid)
  if [ -n "$dpid" ]; then
    echo "dashy          ● running (pid $dpid)  :$DASHY_PORT"
  else
    echo "dashy          ○ not running"
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
  if curl -s --max-time 3 "localhost:$PORT/field" 2>/dev/null | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    p = d.get('panchanga', {})
    nak = p.get('nakshatra', {})
    if isinstance(nak, dict): nak = nak.get('name', '—')
    tithi = p.get('tithi', {})
    if isinstance(tithi, dict): tithi = tithi.get('name', '—')
    devi = p.get('devi', {})
    if isinstance(devi, dict): devi = devi.get('name', '—')
    raga = d.get('sound_spec', {}).get('raga', '—')
    print(f'field          {nak} · {tithi} · {devi} · {raga}')
except Exception as e:
    print(f'field          (parse error: {e})')
" 2>/dev/null; then
    true
  else
    echo "field          (kernel not responding)"
  fi

  # graph
  python3 -c "
import sys
sys.path.insert(0, '$ATLAS')
from npu_engine.datasets import load_all_entities
ents = load_all_entities()
print(f'graph          {len(ents)} entities loaded')
" 2>/dev/null || echo "graph          ○ not loaded"

  echo "──────────────────────────────────────────────"
  echo "  home:   http://localhost:$PORT/home"
  echo "  portal: http://localhost:$DASHY_PORT"
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
  pid=$(_om_pid);      [ -n "$pid" ] && kill "$pid" 2>/dev/null
  pid=$(_ngrok_pid);   [ -n "$pid" ] && kill "$pid" 2>/dev/null
  pid=$(_dashy_pid);   [ -n "$pid" ] && kill "$pid" 2>/dev/null
  pkill -9 sclang 2>/dev/null || true
  pkill -9 scsynth 2>/dev/null || true
  pkill -f pw-cat 2>/dev/null || true
  fuser -k "$PORT/tcp" 2>/dev/null || true
  sleep 1

  # om.py — tanpura via pw-cat → MOTU
  echo "  starting om.py…"
  cd "$ATLAS"
  nohup python3 -u om.py >> om.log 2>&1 &
  sleep 4
  if _om_pid >/dev/null 2>&1; then
    echo "  ✦ om.py active (pw-cat → PipeWire → MOTU)"
  else
    echo "  ⚠ om.py failed — check om.log"
  fi

  # sclang mix relay
  echo "  starting sclang…"
  nohup sclang sc/atlas_mix.scd > /tmp/sclang_mix.log 2>&1 &
  sleep 3
  if _sc_running; then
    echo "  ✦ sclang active (57121→57122)"
  else
    echo "  ⚠ sclang failed"
  fi

  # kernel
  do_kernel || exit 1

  # Dashy
  do_dashy

  # ngrok (optional — comment out if not using)
  # do_ngrok

  # Final status
  echo ""
  echo "  ══════════════════════════════════════"
  echo "    Atlas Core Field Computer"
  echo "  ══════════════════════════════════════"
  echo "    home:    http://localhost:$PORT/home"
  echo "    portal:  http://localhost:$DASHY_PORT"
  echo "    field:   http://localhost:$PORT/field"
  echo "    s-layers: /s0 through /s6"
  echo "  ══════════════════════════════════════"
  echo ""
  echo "  logs:"
  echo "    kernel: tail -f $KERNEL_LOG"
  echo "    om:     tail -f $ATLAS/om.log"
  echo "    dashy:  tail -f /tmp/dashy.log"
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

  # Kill everything
  echo "  killing all processes…"
  pkill -f "python3.*kernel\.py" 2>/dev/null || true
  pkill -f om.py 2>/dev/null || true
  pkill -9 scsynth 2>/dev/null || true
  pkill -9 sclang 2>/dev/null || true
  pkill -f "ngrok.*http" 2>/dev/null || true
  pkill -f "node.*dashy" 2>/dev/null || true
  pkill -f pw-cat 2>/dev/null || true
  fuser -k "$PORT/tcp" 2>/dev/null || true
  sleep 2
  echo "  ✓ all processes stopped"

  # Clean temp files
  echo "  cleaning temp files…"
  rm -f /tmp/atlas_kernel.log /tmp/dashy.log
  rm -f /tmp/sclang_mix.log /tmp/ngrok.log
  truncate -s 0 "$ATLAS/om.log" 2>/dev/null || true
  echo "  ✓ cleaned"

  # Full boot
  do_boot
}

do_logs() {
  echo "Tailing kernel log (Ctrl+C to stop):"
  tail -f "$KERNEL_LOG" 2>/dev/null &
  tail -f "$ATLAS/om.log" 2>/dev/null &
  tail -f /tmp/dashy.log 2>/dev/null &
  wait
}

do_services() {
  echo ""
  echo "── Systemd Services ──────────────────────────"
  for unit in atlas-kernel atlas-om atlas-sc; do
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
  sound|om)  do_om ;;
  audio)     do_audio ;;
  sc)        do_sc ;;
  kernel)    do_kernel ;;
  dashy)     do_dashy ;;
  ngrok)     do_ngrok ;;
  status)    do_status ;;
  services)  do_services ;;
  stop)      do_stop ;;
  url)       do_url ;;
  reset)     do_reset ;;
  logs)      do_logs ;;
  boot|*)    do_boot ;;
esac
