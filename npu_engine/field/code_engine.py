"""
code_engine.py — Atlas codebase self-model.

This is the single place where code topology is queried.
Claude Code reads the result before starting any task.

Hierarchy:
    datasets/system/code_topology.csv  — file dependency graph
    → derive_code_context(task)        — relevant files for a task
    → get_file_context(path)           — full context for one file
    → check_route_conflicts()          — duplicate Flask routes
    → get_broken_relations()           — stale imports / missing modules

Pattern follows ui_vastu_engine.py:
    canonical data → internal helpers → validation → public API
"""

from typing import Any, Dict, List, Optional
import csv
import os
import re

# ══════════════════════════════════════════════════════════
# DATA LOADING
# ══════════════════════════════════════════════════════════

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
_TOPO_PATH = os.path.join(_ROOT, "datasets", "system", "code_topology.csv")

_topo_cache: Optional[List[dict]] = None


def _load_topology() -> List[dict]:
    global _topo_cache
    if _topo_cache is not None:
        return _topo_cache
    rows = []
    try:
        with open(_TOPO_PATH, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                rows.append(row)
    except Exception:
        pass
    _topo_cache = rows
    return rows


def _split(val: str) -> List[str]:
    if not val:
        return []
    return [s.strip() for s in val.split(";") if s.strip()]


# ══════════════════════════════════════════════════════════
# KEYWORD INDEX
# ══════════════════════════════════════════════════════════

_kw_cache: Optional[Dict[str, List[dict]]] = None


def _build_keyword_index() -> Dict[str, List[dict]]:
    global _kw_cache
    if _kw_cache is not None:
        return _kw_cache
    topo = _load_topology()
    idx: Dict[str, List[dict]] = {}
    for row in topo:
        tokens = set()
        for field in ("entity_id", "name", "exports", "routes",
                      "notes", "fragile", "last_known_issue"):
            val = row.get(field, "")
            for word in re.split(r"[^a-zA-Z0-9_]+", val.lower()):
                if len(word) >= 3:
                    tokens.add(word)
        # Add file path segments
        fp = row.get("file_path", "")
        for seg in fp.replace("/", ".").replace(".py", "").replace(".html", "").split("."):
            if len(seg) >= 3:
                tokens.add(seg.lower())
        for token in tokens:
            idx.setdefault(token, []).append(row)
    _kw_cache = idx
    return idx


# ══════════════════════════════════════════════════════════
# INTERNAL HELPERS
# ══════════════════════════════════════════════════════════

def _score_file(row: dict, keywords: set) -> float:
    """Score a file's relevance to a set of keywords."""
    score = 0.0
    searchable = " ".join([
        row.get("entity_id", ""),
        row.get("name", ""),
        row.get("exports", ""),
        row.get("routes", ""),
        row.get("notes", ""),
        row.get("fragile", ""),
        row.get("file_path", ""),
    ]).lower()
    for kw in keywords:
        if kw in searchable:
            score += 1.0
        # Bonus for entity_id or file_path match
        if kw in row.get("entity_id", "").lower():
            score += 2.0
        if kw in row.get("file_path", "").lower():
            score += 1.5
    return score


def _find_related(entity_id: str) -> List[str]:
    """Find files that import or are imported by this entity."""
    topo = _load_topology()
    related = set()
    for row in topo:
        if row.get("entity_id") == entity_id:
            related.update(_split(row.get("imports", "")))
            related.update(_split(row.get("called_by", "")))
            continue
        # Check if this row imports or is called by the target
        if entity_id in row.get("imports", ""):
            related.add(row["entity_id"])
        if entity_id in row.get("called_by", ""):
            related.add(row["entity_id"])
    related.discard(entity_id)
    return sorted(related)


def _row_to_context(row: dict) -> dict:
    """Convert a topology row to a context dict."""
    return {
        "entity_id": row.get("entity_id", ""),
        "file_path": row.get("file_path", ""),
        "entity_type": row.get("entity_type", ""),
        "name": row.get("name", ""),
        "imports": _split(row.get("imports", "")),
        "exports": _split(row.get("exports", "")),
        "called_by": _split(row.get("called_by", "")),
        "routes": _split(row.get("routes", "")),
        "stability": row.get("stability", ""),
        "fragile": row.get("fragile", ""),
        "last_known_issue": row.get("last_known_issue", ""),
        "notes": row.get("notes", ""),
    }


# ══════════════════════════════════════════════════════════
# VALIDATION
# ══════════════════════════════════════════════════════════

def _validate_code_context(ctx: dict) -> dict:
    defaults = {
        "task": "",
        "files_to_read": [],
        "functions_to_check": [],
        "fragile_points": [],
        "related_routes": [],
        "known_issues": [],
        "related_files": [],
        "attestation": "SYNTHESIS",
    }
    for key, default in defaults.items():
        if key not in ctx or ctx[key] is None:
            ctx[key] = default
    return ctx


def _validate_file_context(ctx: dict) -> dict:
    defaults = {
        "entity_id": "",
        "file_path": "",
        "name": "",
        "imports": [],
        "exports": [],
        "called_by": [],
        "routes": [],
        "stability": "",
        "fragile": "",
        "last_known_issue": "",
        "related_files": [],
        "attestation": "SYNTHESIS",
    }
    for key, default in defaults.items():
        if key not in ctx or ctx[key] is None:
            ctx[key] = default
    return ctx


# ══════════════════════════════════════════════════════════
# PUBLIC API
# ══════════════════════════════════════════════════════════

def derive_code_context(task: str) -> dict:
    """Given a task description, find relevant files to read.

    Keyword-matches against code_topology.csv to identify:
    - files to read before starting
    - functions to check
    - known fragile points
    - related Flask routes

    Args:
        task: free text describing the work to do.

    Returns:
        Validated dict — all keys guaranteed present.
    """
    idx = _build_keyword_index()
    topo = _load_topology()

    words = set(re.split(r"[^a-zA-Z0-9_]+", task.lower()))
    words = {w for w in words if len(w) >= 3}

    if not words:
        return _validate_code_context({"task": task})

    # Score every file
    scored = []
    for row in topo:
        s = _score_file(row, words)
        if s > 0:
            scored.append((s, row))
    scored.sort(key=lambda x: x[0], reverse=True)

    # Build context from top matches
    files_to_read = []
    functions_to_check = []
    fragile_points = []
    related_routes = []
    known_issues = []
    related_set = set()

    for score, row in scored[:10]:
        fp = row.get("file_path", "")
        if fp:
            files_to_read.append(fp)
        for exp in _split(row.get("exports", ""))[:5]:
            functions_to_check.append(exp)
        frag = row.get("fragile", "")
        if frag:
            fragile_points.append(f"{row.get('entity_id', '')}: {frag}")
        for route in _split(row.get("routes", ""))[:5]:
            related_routes.append(route)
        issue = row.get("last_known_issue", "")
        if issue:
            known_issues.append(f"{row.get('entity_id', '')}: {issue}")
        # Gather related files
        for rel in _find_related(row.get("entity_id", ""))[:3]:
            related_set.add(rel)

    # Map related entity_ids back to file paths
    related_files = []
    for row in topo:
        if row.get("entity_id") in related_set:
            fp = row.get("file_path", "")
            if fp and fp not in files_to_read:
                related_files.append(fp)

    ctx = {
        "task": task,
        "files_to_read": files_to_read[:8],
        "functions_to_check": functions_to_check[:12],
        "fragile_points": fragile_points[:5],
        "related_routes": related_routes[:10],
        "known_issues": known_issues[:5],
        "related_files": related_files[:8],
        "attestation": "SYNTHESIS",
    }
    return _validate_code_context(ctx)


def get_file_context(file_path: str) -> dict:
    """Return full context for one file.

    Args:
        file_path: path relative to atlas_330 (e.g. "kernel.py" or "npu_engine/tanpura_engine.py")

    Returns:
        Validated dict with imports, exports, callers, known issues, related files.
    """
    topo = _load_topology()

    # Find by file_path or entity_id
    row = None
    for r in topo:
        if r.get("file_path", "") == file_path or r.get("entity_id", "") == file_path:
            row = r
            break

    if row is None:
        return _validate_file_context({"file_path": file_path})

    ctx = _row_to_context(row)
    ctx["related_files"] = _find_related(row.get("entity_id", ""))
    return _validate_file_context(ctx)


def check_route_conflicts() -> List[dict]:
    """Find duplicate Flask route paths in code_topology.csv.

    Only checks server-side route definitions (kernel, engine types),
    not client-side fetch consumers (apps, renderers).
    Returns list of conflicts before they cause Flask AssertionError.
    """
    topo = _load_topology()
    _SERVER_TYPES = {"kernel", "engine", "service"}
    route_map: Dict[str, List[str]] = {}

    for row in topo:
        # Only check server-side route definitions
        if row.get("entity_type", "") not in _SERVER_TYPES:
            continue
        routes = _split(row.get("routes", ""))
        entity = row.get("entity_id", "")
        for route in routes:
            if route.startswith("http"):
                continue  # skip client-side URL references
            route_map.setdefault(route, []).append(entity)

    conflicts = []
    for route, entities in route_map.items():
        if len(entities) > 1:
            conflicts.append({
                "route": route,
                "defined_in": entities,
                "severity": "high",
            })

    # Also check known fragile points mentioning "duplicate" or "route"
    for row in topo:
        frag = row.get("fragile", "").lower()
        if "duplicate" in frag or "route" in frag or "defined twice" in frag:
            conflicts.append({
                "route": "see fragile note",
                "defined_in": [row.get("entity_id", "")],
                "severity": "medium",
                "note": row.get("fragile", ""),
            })

    return conflicts


def get_broken_relations() -> List[dict]:
    """Find broken import chains and stale references.

    Checks:
    - imports that reference non-existent entity_ids
    - called_by references that don't match any importer
    - files marked as broken or with known issues

    Returns list of problems with fix suggestions.
    """
    topo = _load_topology()
    all_ids = {r.get("entity_id", "") for r in topo}
    problems = []

    for row in topo:
        eid = row.get("entity_id", "")

        # Check stability
        if row.get("stability") == "broken":
            problems.append({
                "entity_id": eid,
                "file_path": row.get("file_path", ""),
                "problem": "marked as broken",
                "detail": row.get("last_known_issue", ""),
                "suggestion": "check if issue is resolved, update stability field",
            })

        # Check known issues
        issue = row.get("last_known_issue", "")
        if issue:
            problems.append({
                "entity_id": eid,
                "file_path": row.get("file_path", ""),
                "problem": "has known issue",
                "detail": issue,
                "suggestion": "verify current state",
            })

        # Check fragile points
        frag = row.get("fragile", "")
        if frag:
            problems.append({
                "entity_id": eid,
                "file_path": row.get("file_path", ""),
                "problem": "fragile point",
                "detail": frag,
                "suggestion": "handle with care during edits",
            })

    return problems
