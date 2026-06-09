"""
embed_and_retrieve.py
Stage 3 of the RAG pipeline: Embedding + Vector Store + Retrieval.

Dependencies:
    pip install sentence-transformers chromadb

Usage:
    python embed_and_retrieve.py          # embeds all chunks then runs sample query
    python embed_and_retrieve.py --reset  # wipes the collection and re-embeds from scratch
"""

import sys
import argparse
from chunk_texts import load_and_chunk_all       # Stage 2 — returns list[dict]

from sentence_transformers import SentenceTransformer
import chromadb

# ── Config ────────────────────────────────────────────────────────────────────
CHROMA_PATH     = "./chroma_db"          # folder where ChromaDB persists data on disk
COLLECTION_NAME = "housing_chunks"       # logical name for this dataset's collection
EMBED_MODEL     = "all-MiniLM-L6-v2"    # sentence-transformers model
TOP_K           = 5                      # number of chunks to retrieve per query
BATCH_SIZE      = 64                     # how many chunks to embed at once


# ── ChromaDB client & collection ─────────────────────────────────────────────
def get_collection(reset: bool = False) -> chromadb.Collection:
    """
    Open (or create) the persistent ChromaDB collection.

    chromadb.PersistentClient(path=...)
        Stores the vector index and metadata as files under `path` so
        embeddings survive between Python sessions — no re-embedding needed
        on the second run unless you pass --reset.

    client.get_or_create_collection(name, metadata={"hnsw:space": "cosine"})
        `get_or_create` is idempotent: it returns the existing collection if
        it already exists, or creates a new one if it doesn't.
        The `metadata` argument configures the underlying HNSW index.
        Setting "hnsw:space" to "cosine" makes ChromaDB use cosine similarity
        (distance = 1 − cosine_similarity) instead of the default L2 / Euclidean
        distance.  For sentence embeddings, cosine distance is the standard choice
        because it measures directional alignment rather than vector magnitude.
    """
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    if reset:
        # delete_collection raises if the collection doesn't exist, so guard it
        existing = [c.name for c in client.list_collections()]
        if COLLECTION_NAME in existing:
            client.delete_collection(COLLECTION_NAME)
            print(f"  Deleted existing collection '{COLLECTION_NAME}'.")

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},   # cosine distance for semantic search
    )
    return collection


# ── Embedding ─────────────────────────────────────────────────────────────────
def embed_chunks(chunks: list[dict], collection: chromadb.Collection) -> None:
    """
    Embed every chunk and upsert it into the collection.

    collection.upsert(ids, embeddings, documents, metadatas)
        Inserts a record if the id is new, or overwrites it if it already exists.
        This makes re-runs safe: calling embed_chunks twice won't duplicate data.

        ids         — must be unique strings; we use "<source>__<chunk_index>"
                      so the id encodes provenance and position.
        embeddings  — list of float vectors (one per chunk), produced by the
                      SentenceTransformer model.
        documents   — the raw text stored alongside the vector so we can return
                      it at query time without a separate lookup.
        metadatas   — list of dicts; ChromaDB stores these as filterable fields.
                      We keep `source` and `chunk_index` so the caller can
                      attribute retrieved passages back to the original file.
    """
    # Skip files already in the collection (avoids re-embedding on every run)
    existing_count = collection.count()
    if existing_count > 0:
        print(f"  Collection already has {existing_count} vectors — skipping embedding.")
        print("  Run with --reset to force a full re-embed.\n")
        return

    print(f"  Loading embedding model '{EMBED_MODEL}' …")
    model = SentenceTransformer(EMBED_MODEL)

    total = len(chunks)
    print(f"  Embedding {total} chunks in batches of {BATCH_SIZE} …")

    for batch_start in range(0, total, BATCH_SIZE):
        batch = chunks[batch_start : batch_start + BATCH_SIZE]

        texts      = [c["text"]        for c in batch]
        ids        = [f"{c['source']}_{c['chunk_index']}" for c in batch]
        metadatas  = [{"source": c["source"], "chunk_index": c["chunk_index"]}
                      for c in batch]

        # encode() returns a numpy array of shape (batch_size, 384);
        # tolist() converts it to plain Python lists that ChromaDB accepts.
        embeddings = model.encode(texts, show_progress_bar=False).tolist()

        # upsert is preferred over add: safe to call even if some ids exist
        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )

        end = min(batch_start + BATCH_SIZE, total)
        print(f"    Upserted chunks {batch_start + 1}–{end} / {total}")

    print(f"\n  Done. Collection now contains {collection.count()} vectors.\n")


# ── Retrieval ─────────────────────────────────────────────────────────────────
def retrieve(query: str, collection: chromadb.Collection,
             top_k: int = TOP_K) -> list[dict]:
    """
    Embed `query` with the same model and return the top-k closest chunks.

    collection.query(query_embeddings, n_results, include)
        query_embeddings  — a list of one or more query vectors (we send one).
        n_results         — how many neighbours to return (top_k = 5).
        include           — which fields to return alongside the ids.
                            "documents" = the stored chunk text,
                            "metadatas" = source + chunk_index dicts,
                            "distances" = cosine distances (lower = more similar,
                            range 0–2 for cosine; near 0 means near-identical).

    The response is a dict of parallel lists, all indexed by result rank.
    We zip them together into clean result dicts for easy consumption downstream.
    """
    model = SentenceTransformer(EMBED_MODEL)
    query_embedding = model.encode([query]).tolist()  # shape: (1, 384)

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    # results["documents"][0] is the list of matched texts for query index 0
    hits = []
    for text, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        hits.append({
            "text":        text,
            "source":      meta["source"],
            "chunk_index": meta["chunk_index"],
            "distance":    round(dist, 4),   # cosine distance; lower = more relevant
        })

    return hits


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true",
                        help="Delete and rebuild the collection from scratch.")
    args = parser.parse_args()

    print("=" * 60)
    print("RAG Pipeline — Stage 3: Embedding + Retrieval")
    print("=" * 60)

    # ── Step 1: Load chunks from Stage 2 ──────────────────────────────────────
    print("\nIngesting and chunking source files …\n")
    chunks = load_and_chunk_all()
    print(f"\n  {len(chunks)} total chunks loaded.\n")

    # ── Step 2: Set up ChromaDB and embed ─────────────────────────────────────
    print("Setting up ChromaDB collection …")
    collection = get_collection(reset=args.reset)
    embed_chunks(chunks, collection)

    # ── Step 3: Sample retrieval test ─────────────────────────────────────────
    test_queries = [
        "According to the Rambler article. what factors contribute to the cost of living near Georgia Tech?",
        "What neighborhoods are recommended for college students and why?",
        "What characteristics do students value when choosing off-campus housing in Atlanta?"
    ]

    for query in test_queries:
        print("\n" + "=" * 60)
        print("QUERY:", query)
        print("=" * 60)

        hits = retrieve(query, collection, top_k=TOP_K)

        for rank, hit in enumerate(hits, 1):
            print(
                f"\nRank {rank} | {hit['source']} | "
                f"chunk #{hit['chunk_index']} | distance: {hit['distance']}"
            )
            print("." * 40)
            print(hit["text"][:300])

if __name__ == "__main__":
    main()