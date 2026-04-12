from __future__ import annotations

import csv
import json
import math
import os
import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STORE_DIR = ROOT / "instance" / "vector_store"


# ── Cached SentenceTransformer model (loaded once, stays in memory) ──
import threading
_ST_MODEL = None
_ST_MODEL_NAME = None
_ST_LOCK = threading.Lock()

def _get_st_model(model_name: str = ""):
    """Return a cached SentenceTransformer instance. Loads once, thread-safe."""
    global _ST_MODEL, _ST_MODEL_NAME
    if not model_name:
        model_name = os.environ.get("ATLAS_EMBED_MODEL", "all-MiniLM-L6-v2")
    if _ST_MODEL is not None and _ST_MODEL_NAME == model_name:
        return _ST_MODEL
    with _ST_LOCK:
        # Double-check after acquiring lock
        if _ST_MODEL is not None and _ST_MODEL_NAME == model_name:
            return _ST_MODEL
        from sentence_transformers import SentenceTransformer  # type: ignore
        _ST_MODEL = SentenceTransformer(model_name)
        _ST_MODEL_NAME = model_name
        return _ST_MODEL


_TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)
_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by",
    "for", "from", "has", "have", "he", "her", "his", "i",
    "if", "in", "into", "is", "it", "its", "me", "my",
    "not", "of", "on", "or", "our", "she", "so", "that",
    "the", "their", "them", "then", "there", "they", "this",
    "to", "was", "we", "were", "what", "when", "which", "who",
    "will", "with", "you", "your",
}


def _slug(value: str) -> str:
    value = (value or "").strip().lower()
    value = value.replace("ṛ", "r").replace("ś", "s").replace("ṣ", "s").replace("ṅ", "n")
    value = value.replace("ñ", "n").replace("ṭ", "t").replace("ḍ", "d").replace("ṃ", "m")
    value = re.sub(r"[^a-z0-9]+", "_", value).strip("_")
    replacements = {
        "dhanistha": "dhanishtha",
        "margasirsha": "mrigashira",
        "mrigasirsha": "mrigashira",
        "shravan": "shravana",
    }
    return replacements.get(value, value)


def _tokenize(text: str) -> List[str]:
    tokens = [t.lower() for t in _TOKEN_RE.findall(text or "")]
    return [t for t in tokens if t not in _STOPWORDS and len(t) > 1]


def _chunk_words(text: str, max_words: int = 200) -> List[str]:
    words = (text or "").split()
    if not words:
        return []
    chunks = []
    for start in range(0, len(words), max_words):
        chunk = " ".join(words[start : start + max_words]).strip()
        if chunk:
            chunks.append(chunk)
    return chunks


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        try:
            return path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return ""


def _attestation_from_text(text: str) -> str:
    # Heuristic: first explicit "Attestation:" line wins.
    for line in (text or "").splitlines()[:80]:
        if "attestation" in line.lower():
            m = re.search(r"attestation\s*:\s*(.+)$", line, flags=re.IGNORECASE)
            if m:
                return m.group(1).strip()
    return ""


def _derive_entity_id_from_wiki(path: Path) -> Optional[str]:
    parts = path.parts
    try:
        wiki_idx = parts.index("wiki")
    except ValueError:
        return None
    rel = parts[wiki_idx + 1 :]
    if not rel:
        return None
    if len(rel) == 1:
        return None
    folder = rel[0]
    stem = path.stem
    if stem.lower() in {"readme", "home", "today"}:
        return None
    category_map = {
        "nakshatras": "nakshatra",
        "grahas": "graha",
        "devis": "devi",
        "tithis": "tithi",
        "kalas": "kala",
        "plants": "plant",
    }
    category = category_map.get(folder, _slug(folder))
    return f"{category}_{_slug(stem)}"


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    text: str
    source: str
    entity_id: str
    attestation: str
    domain: str


class VectorStore:
    """
    Semantic retrieval layer.
    Indexes wiki + datasets + PDFs.
    """

    SOURCES = [
        "wiki/",
        "datasets/astro/",
        "datasets/gandharva/",
        "datasets/plants/",
        "docs/sources/gaudiya/",
    ]

    def __init__(self, store_dir: Optional[Path] = None):
        self.store_dir = Path(store_dir) if store_dir else DEFAULT_STORE_DIR
        self.meta_path = self.store_dir / "meta.json"
        self.chunks_path = self.store_dir / "chunks.jsonl"
        self.embeddings_path = self.store_dir / "embeddings.npy"
        self.embedding_meta_path = self.store_dir / "embeddings_meta.json"

        self._loaded = False
        self._chunks: List[Chunk] = []
        self._chunks_by_entity: Dict[str, List[int]] = {}

        # BM25 index
        self._postings: Dict[str, List[Tuple[int, int]]] = {}
        self._doc_len: List[int] = []
        self._avg_len: float = 0.0
        self._num_docs: int = 0

        # Optional embedding backends (built once, loaded from disk)
        self._embeddings = None
        self._embed_backend = ""
        self._embed_model = ""
        self._tfidf_vectorizer = None
        self._tfidf_matrix = None

    # ── public API ──────────────────────────────────────────

    def build(self) -> None:
        self.store_dir.mkdir(parents=True, exist_ok=True)

        chunks: List[Chunk] = []
        chunks.extend(self._index_wiki())
        chunks.extend(self._index_nakshatra_csv())
        chunks.extend(self._index_gandharva())
        chunks.extend(self._index_plants())
        chunks.extend(self._index_gaudiya_pdfs())

        # Persist chunks (append-only source set; rebuild is overwrite of store_dir)
        tmp = self.chunks_path.with_suffix(".jsonl.tmp")
        with tmp.open("w", encoding="utf-8") as fh:
            for ch in chunks:
                fh.write(json.dumps(ch.__dict__, ensure_ascii=False) + "\n")
        os.replace(tmp, self.chunks_path)

        embed_meta = self._build_embeddings_if_available(chunks)
        meta = {
            "version": 1,
            "built_at": time.time(),
            "chunk_count": len(chunks),
            "backend": embed_meta.get("backend") or "bm25",
            "sources": list(self.SOURCES),
            "embedding": embed_meta,
        }
        tmpm = self.meta_path.with_suffix(".json.tmp")
        tmpm.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
        os.replace(tmpm, self.meta_path)

        self._loaded = False
        self.load()

    def search(self, query: str, n: int = 5) -> List[Dict[str, Any]]:
        self.ensure_built()
        if not query:
            return []

        n = max(1, min(int(n or 5), 50))

        # Try A, then B, then C. Never crash.
        try:
            return self._search_sentence_transformers(query, n=n)
        except (ImportError, ModuleNotFoundError):
            pass
        except Exception:
            pass
        try:
            return self._search_sklearn_tfidf(query, n=n)
        except (ImportError, ModuleNotFoundError):
            pass
        except Exception:
            pass
        return self._search_bm25(query, n=n)

    def entity_chunks(self, entity_id: str) -> List[Dict[str, Any]]:
        self.ensure_built()
        if not entity_id:
            return []
        idxs = self._chunks_by_entity.get(entity_id, [])
        out = []
        for i in idxs:
            ch = self._chunks[i]
            out.append({
                "text": ch.text,
                "source": ch.source,
                "entity_id": ch.entity_id,
                "attestation": ch.attestation,
            })
        return out

    # ── lifecycle ───────────────────────────────────────────

    def ensure_built(self) -> None:
        if self.meta_path.exists() and self.chunks_path.exists():
            self.load()
            return
        # Never silently "work" without a store: build the first time we need it.
        self.build()

    def load(self) -> None:
        if self._loaded:
            return
        if not self.chunks_path.exists():
            return

        chunks: List[Chunk] = []
        with self.chunks_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    chunks.append(Chunk(
                        chunk_id=str(obj.get("chunk_id", "")),
                        text=str(obj.get("text", "")),
                        source=str(obj.get("source", "")),
                        entity_id=str(obj.get("entity_id", "")),
                        attestation=str(obj.get("attestation", "")),
                        domain=str(obj.get("domain", "")),
                    ))
                except Exception:
                    continue

        self._chunks = chunks
        self._chunks_by_entity = {}
        for idx, ch in enumerate(self._chunks):
            if ch.entity_id:
                self._chunks_by_entity.setdefault(ch.entity_id, []).append(idx)

        # Build BM25 structures (always available).
        self._build_bm25()

        # Load embeddings if present.
        self._embeddings = None
        self._embed_backend = ""
        self._embed_model = ""
        self._tfidf_vectorizer = None
        self._tfidf_matrix = None
        if self.embeddings_path.exists() and self.embedding_meta_path.exists():
            try:
                import numpy as np
                meta = json.loads(self.embedding_meta_path.read_text(encoding="utf-8"))
                vecs = np.load(str(self.embeddings_path))
                if getattr(vecs, "shape", (0, 0))[0] == len(self._chunks):
                    self._embeddings = vecs
                    self._embed_backend = str(meta.get("backend", ""))
                    self._embed_model = str(meta.get("model", ""))
            except Exception:
                self._embeddings = None

        self._loaded = True

    # ── indexing ────────────────────────────────────────────

    def _index_wiki(self) -> List[Chunk]:
        root = ROOT / "wiki"
        out: List[Chunk] = []
        if not root.exists():
            return out
        for path in sorted(root.rglob("*.md")):
            text = _read_text(path)
            if not text.strip():
                continue
            entity_id = _derive_entity_id_from_wiki(path) or ""
            domain = path.parent.name
            attest = _attestation_from_text(text) or ""
            for i, chunk_text in enumerate(_chunk_words(text, max_words=200)):
                chunk_id = f"wiki:{path.as_posix()}#{i}"
                out.append(Chunk(
                    chunk_id=chunk_id,
                    text=chunk_text,
                    source=path.as_posix(),
                    entity_id=entity_id,
                    attestation=attest,
                    domain=domain,
                ))
        return out

    def _index_nakshatra_csv(self) -> List[Chunk]:
        path = ROOT / "datasets" / "astro" / "nakshatra_canonical.csv"
        if not path.exists():
            path = ROOT / "datasets" / "astro" / "nakshatra_full.csv"
        if not path.exists():
            return []
        out: List[Chunk] = []
        with path.open(encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row_idx, row in enumerate(reader):
                name = (row.get("nakshatra") or row.get("name") or "").strip()
                if not name:
                    continue
                entity_id = f"nakshatra_{_slug(name)}"
                parts = []
                for key in ("nakshatra", "graha", "deity", "symbol", "element", "guna", "dosha", "themes", "shakti"):
                    val = (row.get(key) or "").strip()
                    if val:
                        parts.append(f"{key}: {val}")
                text = " · ".join(parts) if parts else json.dumps(row, ensure_ascii=False)
                out.append(Chunk(
                    chunk_id=f"datasets:astro/nakshatra_full.csv#{row_idx}",
                    text=text,
                    source=path.as_posix(),
                    entity_id=entity_id,
                    attestation="OBSERVED",
                    domain="astro",
                ))
        return out

    def _index_gandharva(self) -> List[Chunk]:
        root = ROOT / "datasets" / "gandharva"
        if not root.exists():
            return []
        out: List[Chunk] = []
        for path in sorted(root.glob("*.csv")):
            with path.open(encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                for row_idx, row in enumerate(reader):
                    name = (row.get("raga") or row.get("name") or "").strip()
                    entity_id = f"raga_{_slug(name)}" if name else ""
                    parts = []
                    for k, v in row.items():
                        v = (v or "").strip()
                        if v:
                            parts.append(f"{k}: {v}")
                    out.append(Chunk(
                        chunk_id=f"datasets:gandharva/{path.name}#{row_idx}",
                        text=" · ".join(parts),
                        source=path.as_posix(),
                        entity_id=entity_id,
                        attestation=(row.get("attestation") or "").strip(),
                        domain="gandharva",
                    ))
        return out

    def _index_plants(self) -> List[Chunk]:
        root = ROOT / "datasets" / "plants"
        out: List[Chunk] = []
        if not root.exists():
            return out

        for path in sorted(root.glob("*.json")):
            try:
                data = json.loads(_read_text(path))
            except Exception:
                continue
            name = str(data.get("name") or data.get("plant") or path.stem).strip()
            entity_id = f"plant_{_slug(name)}"
            text = json.dumps(data, ensure_ascii=False)
            out.append(Chunk(
                chunk_id=f"datasets:plants/{path.name}#0",
                text=text,
                source=path.as_posix(),
                entity_id=entity_id,
                attestation=str(data.get("attestation") or "OBSERVED"),
                domain="plants",
            ))

        for path in sorted(root.glob("*.csv")):
            with path.open(encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                for row_idx, row in enumerate(reader):
                    parts = []
                    for k, v in row.items():
                        v = (v or "").strip()
                        if v:
                            parts.append(f"{k}: {v}")
                    text = " · ".join(parts)

                    # Prefer stable entity ids where possible; duplicate chunks when a row
                    # clearly references multiple canonical entities (e.g., nakshatra+plant).
                    entity_ids: List[str] = []
                    plant_name = (row.get("plant") or row.get("name") or row.get("common_name") or "").strip()
                    if plant_name:
                        entity_ids.append(f"plant_{_slug(plant_name)}")
                    nak_name = (row.get("nakshatra") or "").strip()
                    if nak_name:
                        entity_ids.append(f"nakshatra_{_slug(nak_name)}")
                    graha_name = (row.get("graha") or row.get("ruler") or "").strip()
                    if graha_name:
                        entity_ids.append(f"graha_{_slug(graha_name)}")
                    devi_name = (row.get("devi") or row.get("deity") or "").strip()
                    if devi_name:
                        entity_ids.append(f"devi_{_slug(devi_name)}")

                    entity_ids = [eid for eid in dict.fromkeys(entity_ids) if eid]
                    if not entity_ids:
                        entity_ids = [""]

                    for eid in entity_ids:
                        out.append(Chunk(
                            chunk_id=f"datasets:plants/{path.name}#{row_idx}:{eid or 'none'}",
                            text=text,
                            source=path.as_posix(),
                            entity_id=eid,
                            attestation=(row.get("attestation") or "OBSERVED").strip(),
                            domain="plants",
                        ))
        return out

    def _index_gaudiya_pdfs(self) -> List[Chunk]:
        root = ROOT / "docs" / "sources" / "gaudiya"
        if not root.exists():
            return []
        out: List[Chunk] = []
        for path in sorted(root.glob("*.pdf")):
            txt = self._pdf_to_text(path)
            if not txt.strip():
                continue
            entity_id = f"gaudiya_{_slug(path.stem)}"
            for i, chunk_text in enumerate(_chunk_words(txt, max_words=200)):
                out.append(Chunk(
                    chunk_id=f"pdf:{path.as_posix()}#{i}",
                    text=chunk_text,
                    source=path.as_posix(),
                    entity_id=entity_id,
                    attestation="TRADITIONAL",
                    domain="gaudiya",
                ))
        return out

    def _pdf_to_text(self, path: Path) -> str:
        try:
            proc = subprocess.run(
                ["pdftotext", "-layout", str(path), "-"],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=60,
            )
            if proc.returncode != 0:
                return ""
            return proc.stdout.decode("utf-8", errors="ignore")
        except Exception:
            return ""

    # ── BM25 backend (always available) ─────────────────────

    def _build_bm25(self) -> None:
        postings: Dict[str, List[Tuple[int, int]]] = {}
        doc_len: List[int] = []
        for doc_id, chunk in enumerate(self._chunks):
            tokens = _tokenize(chunk.text)
            doc_len.append(len(tokens))
            if not tokens:
                continue
            tf: Dict[str, int] = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1
            for t, c in tf.items():
                postings.setdefault(t, []).append((doc_id, c))
        self._postings = postings
        self._doc_len = doc_len
        self._num_docs = len(self._chunks)
        self._avg_len = (sum(doc_len) / max(1, len(doc_len))) if doc_len else 0.0

    def _bm25_idf(self, df: int) -> float:
        # Standard BM25 idf with +1 to avoid negative for very common terms.
        return math.log(1.0 + (self._num_docs - df + 0.5) / (df + 0.5))

    def _search_bm25(self, query: str, n: int) -> List[Dict[str, Any]]:
        q_tokens = _tokenize(query)
        if not q_tokens or not self._chunks:
            return []

        k1 = 1.5
        b = 0.75
        scores: Dict[int, float] = {}

        for term in q_tokens:
            plist = self._postings.get(term)
            if not plist:
                continue
            idf = self._bm25_idf(len(plist))
            for doc_id, tf in plist:
                dl = self._doc_len[doc_id] if doc_id < len(self._doc_len) else 0
                denom = tf + k1 * (1.0 - b + b * (dl / (self._avg_len + 1e-9)))
                scores[doc_id] = scores.get(doc_id, 0.0) + idf * (tf * (k1 + 1.0)) / (denom + 1e-9)

        if not scores:
            # Fallback: simple overlap on entity id and source strings.
            qlow = query.lower()
            for doc_id, ch in enumerate(self._chunks):
                if qlow in ch.text.lower():
                    scores[doc_id] = scores.get(doc_id, 0.0) + 0.1

        best = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:n]
        top_score = best[0][1] if best else 1.0
        out = []
        for doc_id, score in best:
            ch = self._chunks[doc_id]
            out.append({
                "text": ch.text,
                "source": ch.source,
                "entity_id": ch.entity_id,
                "score": round(float(score) / max(1e-9, float(top_score)), 6),
                "attestation": ch.attestation,
            })
        return out

    # ── Optional backends (best-effort) ─────────────────────

    def _backend_name(self) -> str:
        if self._embeddings is not None:
            return self._embed_backend or "sentence-transformers"
        if self._tfidf_vectorizer is not None:
            return "sklearn-tfidf"
        return "bm25"

    def _search_sentence_transformers(self, query: str, n: int) -> List[Dict[str, Any]]:
        self._ensure_sentence_transformers_embeddings()
        if self._embeddings is None:
            raise ImportError("sentence-transformers embeddings not available")
        import numpy as np

        model = _get_st_model(self._embed_model or "")
        qv = model.encode([query], normalize_embeddings=True)[0]
        sims = np.dot(self._embeddings, qv)
        best_idx = np.argsort(sims)[::-1][:n]
        out = []
        top = float(sims[best_idx[0]]) if len(best_idx) else 1.0
        for idx in best_idx:
            ch = self._chunks[int(idx)]
            out.append({
                "text": ch.text,
                "source": ch.source,
                "entity_id": ch.entity_id,
                "score": round(float(sims[int(idx)]) / max(1e-9, top), 6),
                "attestation": ch.attestation,
            })
        return out

    def _search_sklearn_tfidf(self, query: str, n: int) -> List[Dict[str, Any]]:
        from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
        from sklearn.metrics.pairwise import cosine_similarity  # type: ignore

        if not self._chunks:
            return []
        if self._tfidf_vectorizer is None or self._tfidf_matrix is None:
            docs = [ch.text for ch in self._chunks]
            vectorizer = TfidfVectorizer(stop_words="english", max_features=50000)
            X = vectorizer.fit_transform(docs)
            self._tfidf_vectorizer = vectorizer
            self._tfidf_matrix = X
        qv = self._tfidf_vectorizer.transform([query])  # type: ignore[union-attr]
        sims = cosine_similarity(self._tfidf_matrix, qv).reshape(-1)  # type: ignore[arg-type]
        best_idx = sims.argsort()[::-1][:n]
        out = []
        top = float(sims[best_idx[0]]) if len(best_idx) else 1.0
        for idx in best_idx:
            ch = self._chunks[int(idx)]
            out.append({
                "text": ch.text,
                "source": ch.source,
                "entity_id": ch.entity_id,
                "score": round(float(sims[int(idx)]) / max(1e-9, top), 6),
                "attestation": ch.attestation,
            })
        return out

    def _ensure_sentence_transformers_embeddings(self) -> None:
        if self._embeddings is not None:
            return
        if not self._chunks:
            return
        # If sentence-transformers is installed but this store was built without embeddings,
        # build embeddings lazily and persist them under instance/vector_store/.
        try:
            import numpy as np
        except Exception as exc:
            raise ImportError(str(exc))
        try:
            model_name = os.environ.get("ATLAS_EMBED_MODEL", "all-MiniLM-L6-v2")
            model = _get_st_model(model_name)
            texts = [ch.text for ch in self._chunks]
            vecs = model.encode(texts, normalize_embeddings=True)
            vecs = np.asarray(vecs, dtype=np.float32)
            np.save(str(self.embeddings_path), vecs)
            meta = {"backend": "sentence-transformers", "model": model_name, "dim": int(vecs.shape[1])}
            self.embedding_meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
            self._embeddings = vecs
            self._embed_backend = "sentence-transformers"
            self._embed_model = model_name
        except Exception as exc:
            raise ImportError(str(exc))

    def _build_embeddings_if_available(self, chunks: Sequence[Chunk]) -> Dict[str, Any]:
        """Try A (sentence-transformers) then B (sklearn) then C (bm25).

        Returns metadata dict (possibly empty). Never raises.
        """
        # Clear existing embedding artifacts.
        try:
            if self.embeddings_path.exists():
                self.embeddings_path.unlink()
            if self.embedding_meta_path.exists():
                self.embedding_meta_path.unlink()
        except Exception:
            pass

        texts = [ch.text for ch in chunks]
        if not texts:
            return {}

        # Option A: sentence-transformers
        try:
            import numpy as np

            model_name = os.environ.get("ATLAS_EMBED_MODEL", "all-MiniLM-L6-v2")
            model = _get_st_model(model_name)
            vecs = model.encode(texts, normalize_embeddings=True)
            vecs = np.asarray(vecs, dtype=np.float32)
            np.save(str(self.embeddings_path), vecs)
            meta = {"backend": "sentence-transformers", "model": model_name, "dim": int(vecs.shape[1])}
            self.embedding_meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
            return meta
        except Exception:
            pass

        # Option B: sklearn tf-idf (no persistence; build-time marker only)
        try:
            import sklearn  # noqa: F401
            return {"backend": "sklearn-tfidf"}
        except Exception:
            pass

        # Option C: BM25/overlap
        return {"backend": "bm25"}


_DEFAULT_STORE: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    global _DEFAULT_STORE
    if _DEFAULT_STORE is None:
        _DEFAULT_STORE = VectorStore()
    return _DEFAULT_STORE
