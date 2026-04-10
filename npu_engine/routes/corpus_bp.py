"""corpus_bp.py — Corpus and research portal routes.

Extracted from kernel.py (RTE-005).
"""
import os
from datetime import datetime
from pathlib import Path

from flask import Blueprint, Response, jsonify, request

corpus_bp = Blueprint('corpus', __name__)

# Project root — resolved once at import time
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)
_RESEARCH_ROOT = os.path.join(_PROJECT_ROOT, "research")
_DS_ROOT = os.path.join(_PROJECT_ROOT, "datasets")
_ALLOWED_ROOTS = {
    "wiki": os.path.join(_PROJECT_ROOT, "docs", "wiki"),
}


# ── Corpus routes ─────────────────────────────

@corpus_bp.route("/corpus/registry")
def _corpus_registry():
    from kernel import _load_full_corpus_registry
    registry = _load_full_corpus_registry()
    tradition_breakdown = {}
    total_chunks = 0
    for entry in registry:
        t = entry.get("tradition", "unknown")
        tradition_breakdown[t] = tradition_breakdown.get(t, 0) + 1
        total_chunks += entry.get("chunks", 0)
    return jsonify({
        "count": len(registry),
        "total_chunks": total_chunks,
        "traditions": tradition_breakdown,
        "corpora": registry,
    })


@corpus_bp.route("/corpus/read")
def _corpus_read():
    from kernel import (LOCAL_TEXT_CORPORA, _HERE, _iter_jsonl_records,
                        _load_full_corpus_registry, _read_local_corpus_passage)
    corpus_id = request.args.get("corpus", "").strip()
    ref = request.args.get("ref", "").strip()
    chunk_id = request.args.get("chunk_id", "").strip()

    # Support chunk_id format: corpus_name:chunk_num
    if chunk_id and not corpus_id:
        parts = chunk_id.split(":", 1)
        if len(parts) == 2:
            corpus_id, ref = parts[0], parts[1]

    if not corpus_id:
        return jsonify({"error": "missing corpus or chunk_id"}), 400

    # Try LOCAL_TEXT_CORPORA first (bg/bhagavatam/sikshashtakam with special handling)
    if corpus_id in LOCAL_TEXT_CORPORA and ref:
        try:
            return jsonify(_read_local_corpus_passage(corpus_id, ref))
        except FileNotFoundError:
            pass
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    # Fall back to full registry
    registry = _load_full_corpus_registry()
    reg_entry = next((e for e in registry if e.get("id") == corpus_id), None)
    if not reg_entry:
        return jsonify({"error": f"unknown corpus: {corpus_id}"}), 404
    cp = reg_entry.get("chunks_path", "")
    chunk_path = _HERE / cp if cp else None
    if not chunk_path or not chunk_path.exists():
        return jsonify({"error": "corpus file not found"}), 404

    target = str(ref or "").strip()
    for record in _iter_jsonl_records(chunk_path):
        rid = str(record.get("id", ""))
        vref = str(record.get("verse_ref", ""))
        if (target and rid == target) or (target and vref and vref.upper() == target.upper()):
            text = " ".join(
                str(record.get(k, "")).strip()
                for k in ("text", "translation", "purport", "sanskrit", "iast", "synonyms")
                if str(record.get(k, "")).strip()
            )
            return jsonify({
                "corpus_id": corpus_id,
                "title": reg_entry.get("title", ""),
                "reference": vref or rid,
                "text": text,
                "domain": record.get("domain", reg_entry.get("domain", "")),
                "tradition": reg_entry.get("tradition", ""),
            })
    return jsonify({"error": "chunk not found"}), 404


@corpus_bp.route("/corpus/search")
def _corpus_search():
    from kernel import (LOCAL_TEXT_CORPORA, _entity_corpus_search,
                        _search_full_corpus, _search_local_corpus)
    query = request.args.get("q", "").strip()
    corpus_id = request.args.get("corpus", "").strip()
    tradition = request.args.get("tradition", "").strip()
    entity = request.args.get("entity", "").strip()
    limit_raw = request.args.get("limit", "10").strip()
    try:
        limit = max(1, min(int(limit_raw or "10"), 50))
    except Exception:
        limit = 10

    # Entity-linked search
    if entity:
        results = _entity_corpus_search(entity, limit=limit)
        return jsonify({
            "query": entity,
            "mode": "entity",
            "count": len(results),
            "results": results,
        })

    if not query:
        return jsonify({"error": "missing q parameter"}), 400

    # Single-corpus search (backward compat)
    if corpus_id and corpus_id in LOCAL_TEXT_CORPORA:
        results = _search_local_corpus(corpus_id, query, limit=limit)
        return jsonify({
            "corpus_id": corpus_id,
            "query": query,
            "count": len(results),
            "results": results,
        })

    # Full cross-corpus search
    results = _search_full_corpus(query, tradition=tradition, limit=limit)
    return jsonify({
        "query": query,
        "tradition": tradition or None,
        "count": len(results),
        "results": results,
    })


# ── Research portal routes ─────────────────────────────

@corpus_bp.route("/research/files")
def research_files():
    dirname = request.args.get("dir", "")
    if not dirname:
        return jsonify({"error": "invalid dir"}), 400
    # allow named roots, datasets/<subdir>, or research/ subdirs
    if dirname in _ALLOWED_ROOTS:
        target = _ALLOWED_ROOTS[dirname]
    elif dirname.startswith("datasets/") and ".." not in dirname:
        target = os.path.join(_DS_ROOT, dirname[len("datasets/"):])
    elif ".." in dirname:
        return jsonify({"error": "invalid dir"}), 400
    else:
        target = os.path.join(_RESEARCH_ROOT, dirname)
    if not os.path.isdir(target):
        return jsonify([])
    files = []
    for f in sorted(os.listdir(target)):
        fp = os.path.join(target, f)
        if os.path.isfile(fp):
            stat = os.stat(fp)
            first_line = ""
            try:
                with open(fp, "r", encoding="utf-8", errors="replace") as fh:
                    first_line = fh.readline().strip()[:120]
            except Exception:
                pass
            files.append({
                "name": f,
                "path": f"{dirname}/{f}",
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "size": stat.st_size,
                "first_line": first_line
            })
    return jsonify(files)


@corpus_bp.route("/research/file")
def research_file():
    filepath = request.args.get("path", "")
    if not filepath or ".." in filepath:
        return jsonify({"error": "invalid path"}), 400
    # resolve path: datasets/X, wiki/X, or research/X
    if filepath.startswith("datasets/"):
        target = os.path.join(_DS_ROOT, filepath[len("datasets/"):])
    elif filepath.startswith("wiki/"):
        target = os.path.join(_PROJECT_ROOT, "docs", filepath)
    else:
        target = os.path.join(_RESEARCH_ROOT, filepath)
    if not os.path.isfile(target):
        return jsonify({"error": "not found"}), 404
    try:
        content = Path(target).read_text(encoding="utf-8", errors="replace")
        return Response(content, mimetype="text/plain")
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@corpus_bp.route("/research/save", methods=["POST"])
def research_save():
    data = request.get_json(force=True)
    filename = data.get("filename", "")
    content = data.get("content", "")
    subdir = data.get("dir", "artifacts")
    if not filename or ".." in filename or ".." in subdir:
        return jsonify({"error": "invalid params"}), 400
    dest_dir = os.path.join(_RESEARCH_ROOT, subdir)
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, filename)
    Path(dest).write_text(content, encoding="utf-8")
    return jsonify({"saved": True, "path": f"{subdir}/{filename}"})


@corpus_bp.route("/research/gaps")
def research_gaps():
    wiki_dir = os.path.join(_PROJECT_ROOT, "docs", "wiki")
    gaps = []
    if os.path.isdir(wiki_dir):
        for f in sorted(os.listdir(wiki_dir)):
            fp = os.path.join(wiki_dir, f)
            if os.path.isfile(fp):
                size = os.path.getsize(fp)
                try:
                    content = Path(fp).read_text(encoding="utf-8", errors="replace").strip()
                except Exception:
                    content = ""
                lines = len(content.splitlines()) if content else 0
                if lines < 5 or size < 200:
                    gaps.append({
                        "entity": f.replace(".md", "").replace("_", " ").title(),
                        "file": f"wiki/{f}",
                        "missing": "empty shell" if lines < 2 else "sparse content",
                        "lines": lines,
                        "confidence": round(1.0 - min(lines / 10, 1.0), 2)
                    })
    # Also check datasets for entity coverage gaps
    gaps.sort(key=lambda x: -x["confidence"])
    return jsonify(gaps[:10])


@corpus_bp.route("/research/datasets")
def research_datasets():
    ds_root = os.path.join(_PROJECT_ROOT, "datasets")
    dirs = []
    if os.path.isdir(ds_root):
        for d in sorted(os.listdir(ds_root)):
            dp = os.path.join(ds_root, d)
            if os.path.isdir(dp):
                files = [f for f in os.listdir(dp) if os.path.isfile(os.path.join(dp, f))]
                mtime = max((os.path.getmtime(os.path.join(dp, f)) for f in files), default=0)
                dirs.append({
                    "name": d,
                    "file_count": len(files),
                    "last_modified": datetime.fromtimestamp(mtime).isoformat() if mtime else None
                })
    return jsonify(dirs)
