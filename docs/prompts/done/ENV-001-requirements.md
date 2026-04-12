# ENV-001: Audit and complete requirements.txt

**Phase**: 1 — Stop the bleeding  
**Priority**: HIGH  
**Estimated time**: 1 hr

## Context

`requirements.txt` has only 4 entries. The npu_engine package imports numpy, scipy,
flask, and likely a dozen other packages. The file is dangerously incomplete — a fresh
venv install would fail immediately.

## Instructions

1. Run import collection:
```bash
cd ~/atlas_core
grep -rh "^import \|^from " npu_engine/ kernel.py \
  | grep -v "^from \." \
  | sed 's/import .*//' \
  | sed 's/from //' \
  | sort -u > /tmp/all_imports.txt
cat /tmp/all_imports.txt
```

2. Read the current `requirements.txt`

3. Cross-reference stdlib modules (do not add these):
   `os, sys, json, re, math, time, datetime, pathlib, typing, collections,
   functools, itertools, threading, subprocess, hashlib, uuid, copy, random,
   concurrent, io, struct, base64, urllib, http, logging, traceback, __future__`

4. For each non-stdlib import, find the pip package name and current stable version:
   - `flask` → Flask
   - `numpy` → numpy
   - `scipy` → scipy
   - `ephem` or `skyfield` → check which one is actually imported
   - `osc` or `pythonosc` → python-osc
   - `requests` → requests
   - `PIL` → Pillow
   - `playwright` → playwright
   - `cv2` → opencv-python
   - `yaml` → PyYAML
   - `dotenv` → python-dotenv

5. Write the complete `requirements.txt` with pinned versions.
   Use `==` for exact pins on core packages; `>=` acceptable for minor utilities.

6. Verify the install would work:
```bash
pip install -r requirements.txt --dry-run 2>&1 | tail -20
```

## Success check

```bash
pip install -r ~/atlas_core/requirements.txt --dry-run 2>&1 | grep -c "Would install"
```

Should report > 5 packages. No errors.

## Output

- Rewrite `requirements.txt` — complete, pinned
- No other files modified
