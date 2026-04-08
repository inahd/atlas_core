#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════
# Atlas — system boot and control
#
# Usage:
#   ./start.sh            full boot (kill stale → SC → kernel → ngrok)
#   ./start.sh sound      restart SC engine
#   ./start.sh sc         restart SC engine (alias)
#   ./start.sh kernel     restart kernel only
#   ./start.sh ngrok      restart ngrok, print new URL
#   ./start.sh status     show status of all components
#   ./start.sh stop       stop everything gracefully
#   ./start.sh url        print current ngrok URL
#   ./start.sh reset      full reset — kill all, clean, reboot
# ═══════════════════════════════════════════════════════════
set -u

ATLAS=~/atlas_330
KERNEL_LOG=/tmp/atlas_kernel.log
NGROK_LOG=/tmp/ngrok.log
PORT=5000

cd "$ATLAS"

# ── helpers ───────────────────────────────────────────────

_kernel_pid() { pgrep -f "python3.*kernel\.py" 2>/dev/null | head -1; }
_ngrok_pid()  { pgrep -f "ngrok.*http.*$PORT" 2>/dev/null | head -1; }

_scsynth_pid() { pgrep -x scsynth 2>/dev/null | head -1; }
_sclang_pid()  { pgrep -x sclang 2>/dev/null | head -1; }
_sc_running()  { [ -n "$(_sclang_pid)" ]; }

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

_field_data() {
  curl -s --max-time 3 "localhost:$PORT/field" 2>/dev/null
}

_wait_kernel() {
  local max=${1:-30}
  for i in $(seq 1 "$max"); do
    if curl -s --max-time 2 "localhost:$PORT/field" >/dev/null 2>&1; then
      return 0
    fi
    sleep 1
  done
  return 1
}

# ── subcommands ───────────────────────────────────────────

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

do_om() {
  echo "  stopping old om.py…"
  pkill -f 'python3.*om\.py' 2>/dev/null || true
  pkill -f pw-cat 2>/dev/null || true
  sleep 1

  echo "  starting om.py (pw-cat → MOTU)…"
  cd "$ATLAS"
  nohup python3 -u om.py >> om.log 2>&1 &
  OM_PID=$!
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

do_kernel() {
  echo "  stopping old kernel…"
  local pid; pid=$(_kernel_pid)
  [ -n "$pid" ] && kill "$pid" 2>/dev/null
  fuser -k "$PORT/tcp" 2>/dev/null || true
  sleep 1

  echo "  starting kernel.py…"
  python3 kernel.py > "$KERNEL_LOG" 2>&1 &
  local kpid=$!
  echo "  kernel pid $kpid — waiting…"

  if _wait_kernel 30; then
    echo "  ✦ kernel ready on :$PORT"
  else
    echo "  ✗ kernel failed to start"
    echo "  check: tail -20 $KERNEL_LOG"
    return 1
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
  echo "  stopping atlas…"

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

  # Retired Python audio processes
  pkill -f om_audio.py 2>/dev/null
  pkill -f om_engines.py 2>/dev/null
  pkill -f om.py 2>/dev/null

  # om.service — stop if still active
  if systemctl --user is-active om.service --quiet 2>/dev/null; then
    systemctl --user stop om.service
    echo "  om.service stopped"
  fi

  echo "  ✦ stopped"
}

do_status() {
  echo ""
  echo "── Atlas Status ──────────────────────────────"

  # om.py audio
  local ompid; ompid=$(pgrep -f 'python3.*om\.py' | head -1)
  if [ -n "$ompid" ]; then
    echo "om.py          ● running (pid $ompid) · pw-cat → MOTU"
  else
    echo "om.py          ○ not running"
  fi

  # sclang mix relay (OSC: MixKernel 57121 → om.py 57122)
  if _sc_running; then
    echo "sclang (mix)   ● running (pid $(_sclang_pid)) · 57121→57122"
  else
    echo "sclang (mix)   ○ not running"
  fi

  # kernel
  local kpid; kpid=$(_kernel_pid)
  if [ -n "$kpid" ]; then
    echo "kernel.py      ● running (pid $kpid)  localhost:$PORT"
  else
    echo "kernel.py      ○ not running"
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
    nak = p.get('nakshatra', '—')
    tithi = p.get('tithi', '—')
    elem = p.get('element', '—')
    mu = d.get('muhurta', {})
    raga = mu.get('raga', '—')
    hora = d.get('hora', {}).get('hora_lord', '—')
    yoga = d.get('yoga', {}).get('yoga_name', '—')
    print(f'panchanga      {nak} · {tithi} · {elem}')
    print(f'muhurta        {mu.get(\"name\", \"—\")} · raga {raga}')
    print(f'hora           {hora} · yoga {yoga}')
except Exception:
    print('panchanga      (parse error)')
" 2>/dev/null; then
    true
  else
    echo "panchanga      (kernel not responding)"
  fi

  # NPU graph + instruments
  python3 -c "
from npu_engine.graph_engine import GraphEngine
g = GraphEngine()
instruments = [k for k in g._metadata if k.startswith('instrument_')]
ragas = [k for k in g._metadata if k.startswith('raga_')]
print(f'npu graph      ● {g.node_count} nodes · {g.edge_count} edges')
print(f'               {len(ragas)} ragas · {len(instruments)} instruments')
" 2>/dev/null || echo "npu graph      ○ not loaded"

  # System capabilities (from system_engine)
  python3 -c "
from npu_engine.field.system_engine import derive_system_state
s = derive_system_state()
caps = s.get('capabilities', {})
ready = caps.get('ready', [])
if ready:
    names = [c['name'] + ' (' + c.get('install_time','?') + ')' for c in ready[:3]]
    print('ready          ' + ' · '.join(names))
" 2>/dev/null

  echo "──────────────────────────────────────────────"
  echo ""
}

do_audio() {
  echo ""
  echo "── Audio Route ───────────────────────────────"
  python3 -c "
from npu_engine.field.system_engine import derive_audio_route, check_audio_connections, restore_audio_connections
import json

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
for b in conns.get('broken', []):
    print(f'  ⚠ {b}')

if conns.get('missing'):
    print()
    print('restoring connections…')
    ok = restore_audio_connections()
    print(f'result: {\"ok\" if ok else \"failed\"} ')
else:
    print()
    print('all connections live')
" 2>&1
  echo "──────────────────────────────────────────────"
  echo ""
}

do_bija() {
  local bija="${1:-om}"
  echo "  synthesizing $bija…"
  python3 -c "
import sounddevice as sd
from npu_engine.bija_synth import synthesize_bija
import json, urllib.request
try:
    with urllib.request.urlopen('http://localhost:5000/field', timeout=2) as r:
        fs = json.loads(r.read())
except:
    fs = {'panchanga':{'nakshatra':'Rohini','tidx':0,'element':'water','guna':'sattva','nak_lord':'Candra'}}
audio = synthesize_bija('$bija', fs, duration_s=4.0)
sd.play(audio, 44100, blocking=True)
print('  ✦ done')
"
}

do_boot() {
  echo ""
  echo "  ✦ Atlas starting…"
  echo ""

  # Kill stale
  echo "  cleaning stale processes…"
  local pid
  pid=$(_ngrok_pid); [ -n "$pid" ] && kill "$pid" 2>/dev/null
  pid=$(_kernel_pid); [ -n "$pid" ] && kill "$pid" 2>/dev/null
  pkill -9 sclang 2>/dev/null || true
  pkill -9 scsynth 2>/dev/null || true
  pkill -f om_audio.py 2>/dev/null || true
  pkill -f om_engines.py 2>/dev/null || true
  pkill -f om.py 2>/dev/null || true
  fuser -k "$PORT/tcp" 2>/dev/null || true
  sleep 1

  pkill -f pw-cat 2>/dev/null || true

  # Start om.py — tanpura + tabla via pw-cat → MOTU
  echo "  starting om.py (pw-cat → MOTU)…"
  nohup python3 -u om.py >> om.log 2>&1 &
  sleep 4

  if pgrep -f 'python3.*om\.py' >/dev/null; then
    echo "  ✦ om.py active (pw-cat → PipeWire → MOTU)"
    python3 -c "
from npu_engine.field.system_engine import restore_audio_connections
ok = restore_audio_connections()
print('  audio: ' + ('ok' if ok else 'connections need attention'))
" 2>/dev/null || true
  else
    echo "  ⚠ om.py failed — check om.log"
    tail -5 om.log 2>/dev/null
  fi

  # Start sclang mix relay (OSC: MixKernel → om.py)
  echo "  starting sclang (mix relay)…"
  nohup sclang sc/atlas_mix.scd > /tmp/sclang_mix.log 2>&1 &
  sleep 3
  if _sc_running; then
    echo "  ✦ sclang mix relay active (57121→57122)"
  else
    echo "  ⚠ sclang mix relay failed"
  fi

  # Kernel
  do_kernel || exit 1

  # ngrok
  do_ngrok

  # Status
  do_status

  echo "  logs:"
  echo "    kernel: tail -f $KERNEL_LOG"
  echo "    om:     tail -f $ATLAS/om.log"
  echo "    ngrok:  tail -f $NGROK_LOG"
  echo ""
  echo "  stop:  ./start.sh stop"
  echo ""

  wait "$(_kernel_pid)" 2>/dev/null
}

do_reset() {
  echo ""
  echo "  ✦ Atlas full reset…"
  echo ""

  # Kill everything
  echo "  killing all processes…"
  pkill -f "python3.*kernel\.py" 2>/dev/null
  pkill -f om_audio.py 2>/dev/null
  pkill -f om_engines.py 2>/dev/null
  pkill -f om.py 2>/dev/null
  pkill -9 scsynth 2>/dev/null
  pkill -9 sclang 2>/dev/null
  pkill -f "ngrok.*http" 2>/dev/null
  fuser -k "$PORT/tcp" 2>/dev/null || true
  systemctl --user stop om.service 2>/dev/null || true
  systemctl --user disable om.service 2>/dev/null || true
  sleep 2
  echo "  ✓ all processes stopped"

  # Clean temp files
  echo "  cleaning temp files…"
  rm -f /tmp/field.json /tmp/voice_input.json /tmp/oracle_response.json
  rm -f /tmp/sc.log /tmp/scsynth.log /tmp/sclang.log
  truncate -s 0 "$ATLAS/om.log" 2>/dev/null
  echo "  ✓ temp files cleaned"

  # Start om.py — tanpura + tabla via pw-cat → MOTU
  echo "  starting om.py (pw-cat → MOTU)…"
  pkill -f pw-cat 2>/dev/null || true
  nohup python3 -u om.py >> om.log 2>&1 &
  sleep 4

  if pgrep -f 'python3.*om\.py' >/dev/null; then
    echo "  ✦ om.py active (pw-cat → PipeWire → MOTU)"
  else
    echo "  ⚠ om.py failed — check om.log"
    tail -5 om.log 2>/dev/null
  fi

  # Start kernel
  do_kernel || exit 1

  # Start ngrok
  do_ngrok

  # Get URL
  local url; url=$(_ngrok_url)

  echo ""
  echo "  ══════════════════════════════════════"
  echo "    Atlas Field Computer"
  echo "  ══════════════════════════════════════"
  echo "    local   → http://localhost:$PORT/atlas"
  [ -n "$url" ] && \
  echo "    public  → $url/atlas"
  echo "    sound   → om.py (pw-cat → MOTU)"
  echo "  ══════════════════════════════════════"
  echo ""

  wait "$(_kernel_pid)" 2>/dev/null
}

# ── dispatch ──────────────────────────────────────────────

do_install() {
  bash "$ATLAS/scripts/install_services.sh"
}

do_services() {
  echo ""
  echo "── Atlas Services ────────────────────────────"
  local unit state mark
  for unit in atlas-sc atlas-sclang atlas-porter atlas-om atlas-kernel atlas-ngrok; do
    state=$(systemctl --user is-active "$unit.service" 2>/dev/null) || state="inactive"
    mark="○"
    [ "$state" = "active" ] && mark="●"
    [ "$state" = "failed" ] && mark="✗"
    printf "  %s %-20s %s\n" "$mark" "$unit" "$state"
  done
  echo ""
  state=$(systemctl --user is-active atlas.target 2>/dev/null) || state="inactive"
  echo "  atlas.target: $state"
  echo "──────────────────────────────────────────────"
  echo ""
}

do_logs() {
  journalctl --user -u "atlas-*" -f --no-hostname
}

case "${1:-boot}" in
  sound|om) do_om ;;
  audio) do_audio ;;
  sc) do_sc ;;
  kernel)   do_kernel ;;
  ngrok)    do_ngrok ;;
  status)   do_status ;;
  services) do_services ;;
  stop)     do_stop ;;
  url)      do_url ;;
  reset)    do_reset ;;
  install)  do_install ;;
  logs)     do_logs ;;
  bija)     do_bija "${2:-om}" ;;
  boot|*)   do_boot ;;
esac
