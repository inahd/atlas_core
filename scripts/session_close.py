#!/usr/bin/env python3
"""
session_close.py — Run at end of every Atlas development session.

Writes:
  docs/SESSION_STATE.md   — current system state snapshot
  docs/TODO.md            — living priority-ordered task list
  docs/SESSION_LOG.md     — appends this session's summary

Usage: python3 scripts/session_close.py
"""

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOW  = datetime.now()

# ── Helpers ───────────────────────────────────────────────────

def sh(cmd, default="unknown"):
    try:
        return subprocess.check_output(cmd, shell=True,
            stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return default

def service_status(name):
    s = sh(f"systemctl is-active {name}.service")
    return "active" if s == "active" else s

def fetch_field():
    try:
        import urllib.request
        with urllib.request.urlopen(
                "http://localhost:5000/field", timeout=2) as r:
            return json.loads(r.read())
    except Exception:
        return {}

def git_log_since(n=10):
    return sh(f"git -C {ROOT} log --oneline -{n}")

def read_queue():
    p = Path("/tmp/om_note_queue.json")
    if p.exists():
        try:
            d = json.loads(p.read_text())
            notes = d.get("notes", [])
            return len(notes), round(sum(x.get("duration_sec",0) for x in notes),1)
        except Exception:
            pass
    return 0, 0

# ── Gather state ──────────────────────────────────────────────

fs      = fetch_field()
p5      = fs.get("panchanga", {})
q_n, q_d = read_queue()
commits = git_log_since(8)

state = {
    "timestamp":   NOW.isoformat(),
    "nakshatra":   p5.get("nakshatra", "unknown"),
    "element":     p5.get("element", "unknown"),
    "guna":        p5.get("guna", "unknown"),
    "tithi":       p5.get("tithi", "unknown"),
    "tidx":        p5.get("tidx", 0),
    "devi_raga":   fs.get("devi_raga", "unknown"),
    "bpm":         fs.get("muhurta", {}).get("bpm", 72),
    "services": {
        "om_audio":   service_status("om_audio"),
        "om_engines": service_status("om_engines"),
        "kernel":     service_status("kernel"),
        "sclang":     "active" if sh("pgrep -x sclang", "") else "inactive",
    },
    "note_queue":  {"notes": q_n, "duration_sec": q_d},
    "last_commit": sh(f"git -C {ROOT} log --oneline -1"),
}

# ── Write SESSION_STATE.md ────────────────────────────────────

state_md = f"""# Atlas Session State
*{NOW.strftime("%Y-%m-%d %H:%M")}*

## Field
| | |
|--|--|
| nakshatra | {state['nakshatra']} |
| element | {state['element']} |
| guna | {state['guna']} |
| tithi | {state['tithi']} (tidx={state['tidx']}) |
| devi_raga | {state['devi_raga']} |
| bpm | {state['bpm']} |

## Services
| Service | Status |
|---------|--------|
| om_audio | {state['services']['om_audio']} |
| om_engines | {state['services']['om_engines']} |
| kernel | {state['services']['kernel']} |
| sclang | {state['services']['sclang']} |

## Note Queue
{q_n} notes / {q_d}s

## Recent Commits
```
{commits}
```

## Sound Architecture
- om_audio.py: thin audio kernel (tanpura + tabla + melody)
- om_engines.py: MixKernel + RhythmKernel + SympatheticKernel + PhraseEngine
- Tanpura: tanpura_simple() pre-rendered 12s buffer, crossfaded loop
- Tabla: 26 WAV samples, pre-rendered full tala cycle
- Melody: PhraseEngine walks raga_graph, writes /tmp/om_note_queue.json
- Audio: sounddevice 48kHz stereo, BLOCKSIZE 16384

## Visual Architecture
- /shell -> static/shell.html — SVG cosmos with igpu nodes
- /render -> igpu.RenderState — 64 entity nodes with positions
- /spine -> full field state for shell.js
- Command layer: backtick to open, :help for commands
"""

(ROOT / "docs" / "SESSION_STATE.md").write_text(state_md)
print("wrote docs/SESSION_STATE.md")

# ── Write TODO.md ─────────────────────────────────────────────

todo_md = f"""# Atlas TODO
*Updated: {NOW.strftime("%Y-%m-%d %H:%M")}*

## Priority 1 — Audio stability
- [ ] Verify MOTU M2 selected (not HDMI) after restart
- [ ] Note queue drain/refill gap — occasional silence between phrases
- [ ] Tabla volume too quiet (0.35 gain) — try 0.5
- [ ] Test 10-minute continuous playback — report any skips

## Priority 2 — Visual shell
- [ ] /coherence-field returns 500 — core/coherence_engine.py runtime bug
- [ ] Shell.js node click -> igpu orbit animation — verify working
- [ ] Wire brahmanda4 iframe into shell mode switcher
- [ ] Test command layer backtick toggle in browser

## Priority 3 — Vocal engine
- [ ] Wire VocalKernel into om_engines.py
- [ ] Write SC synthdef for /atlas/vocal/phoneme formant synthesis
- [ ] Build NAKSHATRA_MAP in vocal/graph_seed_data.py if missing

## Priority 4 — SC synthdefs
- [ ] atlas_mix.scd: rhythm synthdef (tabla percussion from /atlas/rhythm/bol)
- [ ] atlas_mix.scd: sympathetic synthdef (Karplus-Strong 13-string)
- [ ] atlas_mix.scd: vocal synthdef (formant)

## Priority 5 — State broadcast
- [ ] Engines write /tmp/rhythm_state.json, /tmp/mix_state.json
- [ ] Talachakra reads state files instead of recomputing
- [ ] Shell.js reads mix amps from state files

## Priority 6 — Relational navigation
- [ ] /attend endpoint live after kernel restart
- [ ] Test: click deity node -> music nudges toward element
- [ ] Entity detail panel in shell — relations, not just JSON

## Priority 7 — kernel.service
- [ ] kernel.service crash-loops (stale process at PID works)
- [ ] Restart kernel to pick up /attend, deity_attributes, plant_identity

## Done
- [x] Microkernel: om_audio + om_engines separated
- [x] PhraseEngine: live raga graph traversal, natal-aware
- [x] tanpura_field: relational tuning from raga/nakshatra/tithi
- [x] relational_params: field -> instrument physics
- [x] atlas_mix.scd: SC OSC receiver
- [x] talachakra: audio command center with layer toggles
- [x] shell command layer: backtick, tabbed editor, :observe/:seed/:field
- [x] Audio: pre-rendered buffers, zero allocation in callback
- [x] Purnima raga fallback: maps to raga by hour
- [x] /attend endpoint: node click -> mix nudge (needs kernel restart)
- [x] deity_attributes: 27 nakshatra deities + items + vahanas
- [x] plant_identity: tradition data in portrait panel
- [x] 108 pada topology in NPU graph
- [x] Yantra: 9 triangles, vastu compass
- [x] Bija synth: pure formant, no TTS
"""

(ROOT / "docs" / "TODO.md").write_text(todo_md)
print("wrote docs/TODO.md")

# ── Append to SESSION_LOG.md ──────────────────────────────────

log_path = ROOT / "docs" / "SESSION_LOG.md"
log_entry = f"""
---
## Session {NOW.strftime("%Y-%m-%d %H:%M")}

**Field:** {state['nakshatra']} / {state['element']} / {state['guna']} / {state['devi_raga']}

**Services:** {' '.join(f"{k}={v}" for k,v in state['services'].items())}

**Commits this session:**
```
{commits}
```

**Key changes:** see git log above
"""

with open(log_path, "a") as f:
    f.write(log_entry)
print("appended docs/SESSION_LOG.md")

# ── Auto-update skill files in docs/skills/ ───────────────────

skills_dir = ROOT / "docs" / "skills"
if skills_dir.exists():
    # Update atlas-state skill with current sound/visual architecture
    atlas_state_path = skills_dir / "atlas-state.md"
    if atlas_state_path.exists():
        content = atlas_state_path.read_text()
        # Append session state reference if not present
        if "SESSION_STATE.md" not in content:
            content += f"\n\n## Session State\nSee `docs/SESSION_STATE.md` for live system snapshot.\nSee `docs/TODO.md` for prioritized task list.\n"
            atlas_state_path.write_text(content)
            print("updated docs/skills/atlas-state.md")

    # Update npu-integrator skill
    npu_int_path = skills_dir / "npu-integrator.md"
    if npu_int_path.exists():
        content = npu_int_path.read_text()
        if "SESSION_STATE.md" not in content:
            content += f"\n\n## Session State\nSee `docs/SESSION_STATE.md` for live system snapshot.\nSee `docs/TODO.md` for prioritized task list.\n"
            npu_int_path.write_text(content)
            print("updated docs/skills/npu-integrator.md")
else:
    print("docs/skills/ not found — skills not updated")

# ── Commit ────────────────────────────────────────────────────

sh(f"git -C {ROOT} add docs/SESSION_STATE.md docs/TODO.md docs/SESSION_LOG.md docs/skills/")
result = sh(f'git -C {ROOT} commit -m "session: state snapshot {NOW.strftime("%Y-%m-%d %H:%M")}"')
print(f"git: {result}")

print()
print("session_close complete")
