import json
from pathlib import Path
from typing import List, Dict, Tuple

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class Retriever:
    """Retriever that loads a saved FAISS index and returns top-k context chunks."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", top_k: int = 3) -> None:
        self.model = SentenceTransformer(model_name)
        self.top_k = top_k
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.index_dir = self.base_dir / "backend" / "rag"
        self.index_path = self.index_dir / "faiss_index.bin"
        self.metadata_path = self.index_dir / "metadata.json"

        self.index = faiss.read_index(str(self.index_path))
        with open(self.metadata_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)
        self.rows = self.metadata.get("rows", [])

    def retrieve(self, question: str) -> List[str]:
        """Return the top-k relevant context chunks as formatted strings."""
        if not question.strip() or self.index.ntotal == 0:
            return ["No relevant context available."]

        query_embedding = self.model.encode([question], normalize_embeddings=True)
        query_matrix = np.array(query_embedding, dtype=np.float32)
        scores, indices = self.index.search(query_matrix, min(self.top_k, self.index.ntotal))

        results: List[str] = []
        for rank, idx in enumerate(indices[0]):
            if idx < 0 or idx >= len(self.rows):
                continue
            row = self.rows[idx]
            similarity = float(scores[0][rank])
            results.append(
                f"Q: {row['question']} | A: {row['answer']} | similarity: {similarity:.4f}"
            )
        return results if results else ["No relevant context found."]

    def retrieve_with_scores(self, question: str) -> List[Dict[str, str]]:
        """Return structured top-k results including question, answer, and similarity."""
        if not question.strip() or self.index.ntotal == 0:
            return []

        query_embedding = self.model.encode([question], normalize_embeddings=True)
        query_matrix = np.array(query_embedding, dtype=np.float32)
        scores, indices = self.index.search(query_matrix, min(self.top_k, self.index.ntotal))

        results: List[Dict[str, str]] = []
        for rank, idx in enumerate(indices[0]):
            if idx < 0 or idx >= len(self.rows):
                continue
            row = self.rows[idx]
            similarity = float(scores[0][rank])
            results.append(
                {
                    "question": row["question"],
                    "answer": row["answer"],
                    "similarity": f"{similarity:.4f}",
                }
            )
        return results
