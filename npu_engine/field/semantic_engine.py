"""
semantic_engine.py — NPU semantic search over Atlas corpus.

Uses sentence-transformers/all-MiniLM-L6-v2 on Intel NPU
for 2.43ms/embedding semantic similarity search.
"""

import json
import logging
import os
import threading

import numpy as np

log = logging.getLogger(__name__)

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
MODELS_PATH = os.path.join(_ROOT, "models")
SOURCES_PATH = os.path.join(_ROOT, "datasets", "sources")
CACHE_DIR = os.path.join(_ROOT, "cache")

# Lazy init — don't load until first call
_compiled_model = None
_tokenizer = None
_corpus_embeddings = None  # np.ndarray (N, 384)
_corpus_metadata = None    # list of dicts
_embedding_lock = threading.Lock()


def _init_model():
    """Load OpenVINO model and tokenizer. NPU first, CPU fallback."""
    global _compiled_model, _tokenizer

    import openvino as ov
    from transformers import AutoTokenizer

    model_dir = os.path.join(MODELS_PATH, "minilm-ov")
    core = ov.Core()
    model = core.read_model(os.path.join(model_dir, "openvino_model.xml"))
    model.reshape({
        "input_ids": [1, 128],
        "attention_mask": [1, 128],
        "token_type_ids": [1, 128],
    })

    try:
        _compiled_model = core.compile_model(model, "NPU")
        log.info("Semantic engine: model compiled on NPU")
    except Exception:
        _compiled_model = core.compile_model(model, "CPU")
        log.info("Semantic engine: NPU unavailable, using CPU fallback")

    _tokenizer = AutoTokenizer.from_pretrained(model_dir)


def embed(text: str) -> np.ndarray:
    """Embed a single text string. Returns L2-normalized 384-d vector."""
    global _compiled_model, _tokenizer

    with _embedding_lock:
        if _compiled_model is None:
            _init_model()

    tokens = _tokenizer(
        text, padding="max_length", max_length=128,
        truncation=True, return_tensors="np",
    )
    result = _compiled_model({
        "input_ids": tokens["input_ids"],
        "attention_mask": tokens["attention_mask"],
        "token_type_ids": tokens["token_type_ids"],
    })

    # Mean pool last hidden state
    hidden = result[_compiled_model.output(0)]
    mask = tokens["attention_mask"].astype(np.float32)
    pooled = (hidden * mask[:, :, None]).sum(axis=1) / mask.sum(axis=1, keepdims=True)

    # L2 normalize
    norm = np.linalg.norm(pooled, axis=1, keepdims=True)
    return (pooled / norm).squeeze()


# ── Corpus index ─────────────────────────────────────────────────

def _build_corpus_index():
    """Scan all JSONL chunk files, embed each, cache to disk."""
    global _corpus_embeddings, _corpus_metadata

    cache_emb = os.path.join(CACHE_DIR, "corpus_embeddings.npy")
    cache_meta = os.path.join(CACHE_DIR, "corpus_metadata.json")

    # Check cache
    if os.path.exists(cache_emb) and os.path.exists(cache_meta):
        _corpus_embeddings = np.load(cache_emb)
        with open(cache_meta) as f:
            _corpus_metadata = json.load(f)
        log.info(f"Loaded cached corpus index: {len(_corpus_metadata)} chunks")
        return

    # Scan all JSONL files
    import glob as glob_mod
    jsonl_files = sorted(glob_mod.glob(
        os.path.join(SOURCES_PATH, "**", "*.jsonl"), recursive=True))

    metadata = []
    texts = []
    for jf in jsonl_files:
        with open(jf, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    chunk = json.loads(line)
                except json.JSONDecodeError:
                    continue
                text = chunk.get("text", chunk.get("passage", ""))
                if not text or len(text) < 20:
                    continue
                texts.append(text[:512])  # truncate for embedding
                metadata.append({
                    "source": chunk.get("source", chunk.get("text_id",
                                                            os.path.basename(jf))),
                    "tradition": chunk.get("tradition", chunk.get("family", "")),
                    "chapter": chunk.get("chapter", ""),
                    "verse": chunk.get("verse", chunk.get("verse_ref", "")),
                    "text": text[:300],  # store truncated for display
                })

    if not texts:
        log.warning("No corpus texts found for indexing")
        return

    # Embed with progress
    log.info(f"Embedding corpus: 0/{len(texts)} chunks")
    embeddings = []
    for i, text in enumerate(texts):
        try:
            vec = embed(text)
            embeddings.append(vec)
        except Exception:
            embeddings.append(np.zeros(384, dtype=np.float32))
        if (i + 1) % 5000 == 0:
            log.info(f"Embedding corpus: {i+1}/{len(texts)} chunks")

    _corpus_embeddings = np.array(embeddings, dtype=np.float32)
    _corpus_metadata = metadata

    # Cache to disk
    os.makedirs(CACHE_DIR, exist_ok=True)
    np.save(cache_emb, _corpus_embeddings)
    with open(cache_meta, "w") as f:
        json.dump(metadata, f)
    log.info(f"Corpus index built: {len(metadata)} chunks cached")


def start_indexing():
    """Start background corpus indexing thread."""
    t = threading.Thread(target=_build_corpus_index, daemon=True)
    t.start()
    return t


# ── Search ───────────────────────────────────────────────────────

def semantic_search(query: str, limit: int = 10,
                    tradition: str = None) -> list:
    """Return top-k corpus chunks by cosine similarity to query."""
    if _corpus_embeddings is None or _corpus_metadata is None:
        return []

    query_vec = embed(query)
    # Cosine similarity (vectors are already normalized)
    scores = _corpus_embeddings @ query_vec

    # Filter by tradition if specified
    if tradition:
        tradition_lower = tradition.lower()
        mask = np.array([
            tradition_lower in (m.get("tradition", "") or "").lower()
            for m in _corpus_metadata
        ])
        scores = np.where(mask, scores, -1.0)

    # Top-k
    top_k = min(limit, len(scores))
    top_indices = np.argpartition(scores, -top_k)[-top_k:]
    top_indices = top_indices[np.argsort(scores[top_indices])[::-1]]

    results = []
    for idx in top_indices:
        if scores[idx] < 0:
            continue
        meta = _corpus_metadata[idx]
        results.append({
            "text": meta["text"],
            "source": meta["source"],
            "tradition": meta["tradition"],
            "chapter": meta.get("chapter", ""),
            "verse": meta.get("verse", ""),
            "score": round(float(scores[idx]), 4),
        })
    return results


def corpus_status() -> dict:
    """Return current indexing state."""
    return {
        "indexed": _corpus_embeddings is not None,
        "chunks": len(_corpus_metadata) if _corpus_metadata else 0,
        "embedding_dim": 384,
        "device": "NPU",
    }
