#!/usr/bin/env python3
"""
session_open.py — Run at START of every Atlas session.
Prints a clear oriented summary. Nothing else.

Usage: python3 scripts/session_open.py
"""
import json, subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def sh(cmd):
    try:
        return subprocess.check_output(cmd, shell=True,
            stderr=subprocess.DEVNULL, text=True).strip()
    except:
        return "?"

def svc(name):
    s = sh(f"systemctl is-active {name}.service")
    return "●" if s == "active" else "○"

def fetch_field():
    try:
        import urllib.request
        with urllib.request.urlopen(
                "http://localhost:5000/field", timeout=2) as r:
            return json.loads(r.read())
    except:
        return {}

print("\n✦ ATLAS SESSION OPEN", datetime.now().strftime("%Y-%m-%d %H:%M"))
print("━" * 52)

# Services
print(f"\nSERVICES")
print(f"  {svc('om_audio')} om_audio    {svc('om_engines')} om_engines")
ks = "●" if sh("curl -s http://localhost:5000/field") != "?" else "○"
sc = "●" if sh("pgrep -x sclang") else "○"
print(f"  {ks} kernel      {sc} sclang")

# Field
fs = fetch_field()
p5 = fs.get("panchanga", {})
print(f"\nFIELD")
print(f"  {p5.get('nakshatra','?')} · {p5.get('element','?')} · {p5.get('guna','?')}")
print(f"  {p5.get('tithi','?')} · {fs.get('devi_raga','?')} · {fs.get('muhurta',{}).get('bpm','?')}bpm")

# Top TODOs
todo = (ROOT / "docs" / "TODO.md")
if todo.exists():
    lines = todo.read_text().splitlines()
    open_items = [l for l in lines if l.strip().startswith("- [ ]")][:5]
    print(f"\nNEXT TASKS")
    for item in open_items:
        print(f"  {item.strip()[6:]}")

# Library
print(f"\nLIBRARY")
try:
    sys.path.insert(0, str(ROOT))
    from npu_engine.library_kernel import build_library_state
    lib = build_library_state()
    s = lib["summary"]
    print(f"  {s['dataset_files']} datasets · {s['dataset_rows']:,} rows · {s['graph_nodes']:,} nodes")
    print(f"  {s['open_gaps']} gaps open")
    if lib["next"]:
        print(f"  next: {lib['next'][0]['description']}")
except Exception as e:
    print(f"  library: {e}")

# Last commit
print(f"\nLAST COMMIT")
print(f"  {sh('git -C ' + str(ROOT) + ' log --oneline -1')}")

print("\n" + "━" * 52)
print("Ready. What do you want to work on?\n")
