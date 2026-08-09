import json
import csv
from pathlib import Path
from typing import List, Dict

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class IndexBuilder:
    """Build and persist a FAISS vector index from dataset CSVs."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self.model = SentenceTransformer(model_name)
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.dataset_dir = self.base_dir / "datasets"
        self.output_dir = self.base_dir / "backend" / "rag"
        self.index_path = self.output_dir / "faiss_index.bin"
        self.metadata_path = self.output_dir / "metadata.json"

    def load_dataset_rows(self) -> List[Dict[str, str]]:
        """Load question/answer rows from all CSVs in the datasets folder."""
        rows: List[Dict[str, str]] = []
        for file_path in self.dataset_dir.glob("*.csv"):
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    question = (row.get("question") or "").strip()
                    answer = (row.get("answer") or "").strip()
                    if question and answer:
                        rows.append({"question": question, "answer": answer, "source": file_path.name})
        return rows

    def build(self) -> None:
        """Generate embeddings, build FAISS index, and persist artifacts."""
        rows = self.load_dataset_rows()
        if not rows:
            raise RuntimeError("No dataset rows found to build the index.")

        texts = [f"Q: {r['question']} | A: {r['answer']}" for r in rows]
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        embedding_matrix = np.array(embeddings, dtype=np.float32)

        index = faiss.IndexFlatIP(embedding_matrix.shape[1])
        index.add(embedding_matrix)

        self.output_dir.mkdir(parents=True, exist_ok=True)
        faiss.write_index(index, str(self.index_path))

        metadata = {
            "model": "all-MiniLM-L6-v2",
            "rows": [
                {
                    "question": r["question"],
                    "answer": r["answer"],
                    "source": r["source"],
                }
                for r in rows
            ],
        }
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        print(f"Index built: {index.ntotal} vectors saved to {self.index_path}")
        print(f"Metadata saved to {self.metadata_path}")


if __name__ == "__main__":
    IndexBuilder().build()
