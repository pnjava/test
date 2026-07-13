#!/usr/bin/env python3
"""
Embed + Store (T3.2)

Loads knowledge/chunks.jsonl into a persistent ChromaDB collection at
knowledge/chroma/. Embeddings use Chroma's default model
(all-MiniLM-L6-v2 via ONNX, downloaded on first run).

Chunk metadata stored per record (Chroma metadata must be scalar):
  source_file, kb_file, heading, sequence, date, state, owner, category,
  confidence, review_status, tags (comma-joined), systems (comma-joined,
  wrapped in commas for exact-token matching via $contains).

Rebuild is idempotent: the collection is recreated from chunks.jsonl each run.

Usage:
    python3 embed_store.py            # (re)build collection from chunks.jsonl
    python3 embed_store.py --verify   # count + sample metadata queries only
"""

import json
import sys
from pathlib import Path

import chromadb

ROOT = Path(__file__).parent.parent
CHUNKS = ROOT / "knowledge" / "chunks.jsonl"
CHROMA_DIR = ROOT / "knowledge" / "chroma"
COLLECTION = "eaip_knowledge"


def load_chunks():
    with open(CHUNKS) as f:
        return [json.loads(line) for line in f if line.strip()]


def to_metadata(chunk):
    sp, md = chunk["source_pointer"], chunk["metadata"]
    return {
        "source_file": sp["source_file"],
        "kb_file": sp["kb_file"],
        "heading": sp["heading"],
        "sequence": sp["sequence"],
        "words": chunk["words"],
        "date": md.get("date", ""),
        "state": md.get("state", "unknown"),
        "owner": md.get("owner", "TBD"),
        "category": md.get("category", ""),
        "confidence": md.get("confidence", "assumed"),
        "review_status": md.get("review_status", "") or "",
        "tags": "," + ",".join(md.get("tags", [])) + ",",
        # comma-wrapped so `$contains: ",DG,"` matches the exact token
        "systems": "," + ",".join(chunk.get("systems", [])) + ",",
    }


def get_client():
    return chromadb.PersistentClient(path=str(CHROMA_DIR))


def build():
    chunks = load_chunks()
    client = get_client()
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass
    coll = client.create_collection(COLLECTION, metadata={"hnsw:space": "cosine"})

    BATCH = 64
    for i in range(0, len(chunks), BATCH):
        batch = chunks[i : i + BATCH]
        coll.add(
            ids=[c["chunk_id"] for c in batch],
            documents=[c["text"] for c in batch],
            metadatas=[to_metadata(c) for c in batch],
        )
        print(f"  embedded {min(i + BATCH, len(chunks))}/{len(chunks)}")

    print(f"✓ Collection '{COLLECTION}' built: {coll.count()} chunks (source: {CHUNKS.name})")
    return coll.count(), len(chunks)


def verify():
    chunks = load_chunks()
    client = get_client()
    coll = client.get_collection(COLLECTION)
    ok = True

    n_coll, n_chunks = coll.count(), len(chunks)
    print(f"Collection count = {n_coll}, chunks.jsonl = {n_chunks}", "✓" if n_coll == n_chunks else "✗")
    ok &= n_coll == n_chunks

    # Metadata queryability checks
    verified = coll.get(where={"confidence": "verified"}, limit=1000)
    print(f"✓ where confidence=verified → {len(verified['ids'])} chunks")

    dg = coll.get(where_document=None, where={"systems": {"$ne": ",,"}}, limit=1000)
    print(f"✓ chunks tagged with ≥1 confirmed system → {len(dg['ids'])}")

    pending = coll.get(where={"review_status": "pending_human_review (T1.4)"}, limit=1000)
    print(f"✓ where review_status=pending_human_review → {len(pending['ids'])} chunks")

    # Semantic sanity probe
    res = coll.query(query_texts=["core claims adjudication database"], n_results=3)
    top = [(i, m["source_file"]) for i, m in zip(res["ids"][0], res["metadatas"][0])]
    print("✓ semantic probe 'core claims adjudication database' top-3:")
    for cid, src in top:
        print(f"    {cid}  ({src})")

    return ok


if __name__ == "__main__":
    if "--verify" in sys.argv:
        sys.exit(0 if verify() else 1)
    n_coll, n_chunks = build()
    sys.exit(0 if n_coll == n_chunks else 1)
