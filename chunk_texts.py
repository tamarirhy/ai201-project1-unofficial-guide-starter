"""
chunk_texts.py
Stage 1 & 2 of the RAG pipeline: load .txt files from data/, clean, and chunk.

Chunk size:  600–900 characters (target ~700)
Overlap:     100–150 characters (target ~100)
Output:      list of dicts with keys: source, chunk_index, text
"""

import os
import re
import glob
from pathlib import Path


# ── Config ────────────────────────────────────────────────────────────────────
DATA_DIR    = "data"          # folder containing .txt files
CHUNK_SIZE  = 700             # target chunk length (chars)
CHUNK_MIN   = 600             # hard minimum
CHUNK_MAX   = 900             # hard maximum
OVERLAP     = 100             # overlap between consecutive chunks
SAMPLE_N    = 5               # number of sample chunks to print


# ── Cleaning ──────────────────────────────────────────────────────────────────
def clean_text(text: str) -> str:
    """Remove HTML tags, entities, and normalise whitespace."""
    # Strip HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Decode common HTML entities
    entities = {
        "&amp;": "&", "&lt;": "<", "&gt;": ">",
        "&quot;": '"', "&#39;": "'", "&nbsp;": " ",
        "&ndash;": "–", "&mdash;": "—", "&hellip;": "…",
    }
    for entity, char in entities.items():
        text = text.replace(entity, char)
    # Remove residual HTML entities (&something; or &#123;)
    text = re.sub(r"&[a-zA-Z]{2,6};", " ", text)
    text = re.sub(r"&#\d+;", " ", text)
    # Collapse multiple spaces / tabs into one space
    text = re.sub(r"[ \t]+", " ", text)
    # Collapse 3+ newlines into 2 (preserve paragraph breaks)
    text = re.sub(r"\n{3,}", "\n\n", text)
    #Remove common source / URL boilerplate
    text = re.sub(r"Source:.*", "", text)
    text = re.sub(r"URL:.*", "", text)
    text = re.sub(r"https?://\S+", "", text)
    #Remove review metadata lines
    text = re.sub(r"Review by.*", "", text)
    text = re.sub(r"\d+\.\d+\s*rating.*", "", text, flags=re.IGNORECASE)
    # Strip leading/trailing whitespace from each line
    lines = [line.strip() for line in text.splitlines()]
    text = "\n".join(lines)
    return text.strip()


# ── Chunking ──────────────────────────────────────────────────────────────────
def split_into_chunks(text: str, chunk_size: int = CHUNK_SIZE,
                      overlap: int = OVERLAP) -> list[str]:
    """
    Paragraph-aware chunker: splits on blank lines first, then groups whole
    paragraphs into chunks that stay within CHUNK_MIN–CHUNK_MAX characters.

    Overlap is implemented by re-including the tail paragraph(s) from the
    previous chunk whose combined length is closest to `overlap` chars.
    Because overlap is always a whole paragraph, every chunk starts and ends
    at a clean paragraph (and therefore sentence) boundary.

    Edge cases:
    - A single paragraph longer than CHUNK_MAX is emitted as its own chunk
      so no content is ever dropped.
    - A paragraph shorter than CHUNK_MIN is grouped with its neighbours until
      the minimum is met.
    """
    # ── 1. Split into paragraphs ──────────────────────────────────────────────
    paragraphs = [p.strip() for p in re.split(r"\n\n+", text) if p.strip()]
    if not paragraphs:
        return []

    chunks: list[str] = []
    i = 0  # index into paragraphs[]

    while i < len(paragraphs):
        chunk_paras: list[str] = []
        length = 0
        j = i

        # ── 2. Greedily accumulate paragraphs ─────────────────────────────────
        while j < len(paragraphs):
            para = paragraphs[j]
            # "\n\n" separator adds 2 chars between paragraphs
            sep = 2 if chunk_paras else 0
            new_length = length + sep + len(para)

            # Stop only when we've met the minimum AND adding this paragraph
            # would push us past the maximum.  If we haven't met the minimum
            # yet, keep going even past CHUNK_MAX (avoids losing tiny files).
            if chunk_paras and new_length > CHUNK_MAX and length >= CHUNK_MIN:
                break

            chunk_paras.append(para)
            length = new_length
            j += 1

            # Once we've hit the target size (and cleared the minimum) we can
            # stop — no need to pack the chunk tighter.
            if length >= chunk_size and length >= CHUNK_MIN:
                break

        chunks.append("\n\n".join(chunk_paras))

        # ── 3. Determine overlap for next chunk ───────────────────────────────
        # Walk backwards through chunk_paras, accumulating paragraphs until
        # their combined length meets or exceeds `overlap`.  Those paragraphs
        # become the opening context of the next chunk.
        overlap_count = 0
        overlap_len = 0
        for para in reversed(chunk_paras):
            overlap_len += len(para)
            overlap_count += 1
            if overlap_len >= overlap:
                break

        # Next chunk starts `overlap_count` paragraphs before j, but must
        # always advance at least one paragraph past i to prevent infinite loops.
        i = max(i + 1, j - overlap_count)

    return chunks


# ── Ingestion ─────────────────────────────────────────────────────────────────
def load_and_chunk_all(data_dir: str = DATA_DIR) -> list[dict]:
    """
    Walk data_dir, load every .txt file, clean it, chunk it,
    and return a flat list of chunk dicts.
    """
    txt_files = sorted(glob.glob(os.path.join(data_dir, "*.txt")))

    if not txt_files:
        raise FileNotFoundError(
            f"No .txt files found in '{data_dir}/'. "
            "Make sure your scraped text files are saved there."
        )

    all_chunks = []
    for filepath in txt_files:
        source = Path(filepath).name
        raw = Path(filepath).read_text(encoding="utf-8", errors="replace")
        cleaned = clean_text(raw)
        chunks = split_into_chunks(cleaned)

        for i, chunk_text in enumerate(chunks):
            all_chunks.append({
                "source":      source,
                "chunk_index": i,
                "text":        chunk_text,
            })

        print(f"  Loaded '{source}': {len(raw):,} chars → "
              f"{len(cleaned):,} cleaned → {len(chunks)} chunks")

    return all_chunks


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("RAG Pipeline — Stage 2: Chunking")
    print("=" * 60)

    print(f"\nScanning '{DATA_DIR}/' for .txt files …\n")
    chunks = load_and_chunk_all(DATA_DIR)

    print(f"\n{'─' * 60}")
    print(f"Total chunks produced: {len(chunks)}")
    print(f"{'─' * 60}\n")

    # ── Print sample chunks ───────────────────────────────────────────────────
    import random
    random.seed(42)
    samples = random.sample(chunks, min(SAMPLE_N, len(chunks)))

    print(f"Sample {SAMPLE_N} chunks (randomly selected):\n")
    for n, chunk in enumerate(samples, 1):
        bar = "─" * 60
        print(f"{bar}")
        print(f"Sample {n}  |  source: {chunk['source']}  |  "
              f"chunk #{chunk['chunk_index']}  |  {len(chunk['text'])} chars")
        print(f"{bar}")
        print(chunk["text"])
        print()

    return chunks   # expose for import use


if __name__ == "__main__":
    main()