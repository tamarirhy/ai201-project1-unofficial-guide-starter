"""
chunk_texts.py
Stage 2 of the RAG pipeline: load .txt files from data/, clean, and chunk.

Chunk size:  500–800 characters (target ~600)
Overlap:     100–150 characters (target ~100)
Output:      list of dicts with keys: source, chunk_index, text
"""

import os
import re
import glob
from pathlib import Path


# ── Config ────────────────────────────────────────────────────────────────────
DATA_DIR    = "data"          # folder containing .txt files
CHUNK_SIZE  = 600             # target chunk length (chars)
CHUNK_MIN   = 500             # hard minimum
CHUNK_MAX   = 800             # hard maximum
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
    # Strip leading/trailing whitespace from each line
    lines = [line.strip() for line in text.splitlines()]
    text = "\n".join(lines)
    return text.strip()


# ── Chunking ──────────────────────────────────────────────────────────────────
def split_into_chunks(text: str, chunk_size: int = CHUNK_SIZE,
                      overlap: int = OVERLAP) -> list[str]:
    """
    Split text into overlapping character-level chunks.
    Tries to break at sentence boundaries (. ! ?) or spaces so words aren't cut.
    """
    chunks = []
    start = 0
    length = len(text)

    while start < length:
        end = min(start + chunk_size, length)

        # If we're not at the end, try to break at a sentence boundary
        if end < length:
            # Look for the last sentence-ending punctuation in the window
            window = text[start:end]
            # Search backwards for ". ", "! ", "? "
            match = None
            for m in re.finditer(r"[.!?]\s", window):
                match = m
            if match:
                end = start + match.end()
            else:
                # Fall back to last space to avoid cutting mid-word
                last_space = text.rfind(" ", start, end)
                if last_space > start:
                    end = last_space + 1

        chunk = text[start:end].strip()

        # Only keep chunks within the allowed size range
        if len(chunk) >= CHUNK_MIN or start == 0:  # always keep first chunk
            chunks.append(chunk)

        # Advance start by (chunk_size - overlap), land after a word boundary
        next_start = end - overlap
        # Snap forward to next space so overlap doesn't start mid-word
        snap = text.find(" ", next_start)
        if snap != -1 and snap < end:
            next_start = snap + 1

        # Safety: always move forward
        if next_start <= start:
            next_start = start + 1

        start = next_start

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