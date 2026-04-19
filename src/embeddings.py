"""
embeddings.py - FAISS Vector Store Handler
Uses FAISS (no C++ compiler needed) instead of ChromaDB
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

VECTOR_DB_DIR = os.getenv("CHROMA_DB_DIR", "./vector_db")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")


def get_embeddings():
    if LLM_PROVIDER == "openai" and os.getenv("OPENAI_API_KEY"):
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(model="text-embedding-3-small")
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
    except ImportError:
        from langchain_community.embeddings import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def _store_path(video_id: str) -> Path:
    path = Path(VECTOR_DB_DIR) / video_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def create_vector_store(chunks: list, video_id: str, metadata: dict):
    from langchain_community.vectorstores import FAISS
    texts = [c["text"] for c in chunks]
    metadatas = [
        {
            "video_id": video_id,
            "chunk_index": str(c["chunk_index"]),
            "timestamp": c["timestamp"],
            "video_title": metadata.get("title", "Unknown"),
            "author": metadata.get("author", "Unknown"),
            "word_start": str(c["word_start"]),
            "word_end": str(c["word_end"]),
        }
        for c in chunks
    ]
    embeddings = get_embeddings()
    vector_store = FAISS.from_texts(texts=texts, embedding=embeddings, metadatas=metadatas)
    vector_store.save_local(str(_store_path(video_id)))
    return vector_store


def load_vector_store(video_id: str):
    from langchain_community.vectorstores import FAISS
    store_path = _store_path(video_id)
    if not (store_path / "index.faiss").exists():
        return None
    try:
        embeddings = get_embeddings()
        return FAISS.load_local(str(store_path), embeddings, allow_dangerous_deserialization=True)
    except Exception:
        return None


def delete_vector_store(video_id: str) -> bool:
    import shutil
    try:
        shutil.rmtree(_store_path(video_id))
        return True
    except Exception:
        return False


def list_stored_videos() -> list:
    base = Path(VECTOR_DB_DIR)
    if not base.exists():
        return []
    return [
        {"video_id": f.name, "chunk_count": "cached"}
        for f in base.iterdir()
        if f.is_dir() and (f / "index.faiss").exists()
    ]


def get_retriever(vector_store, k: int = 5):
    return vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={"k": k, "fetch_k": k * 3},
    )