from pathlib import Path
from typing import List


class DatasetLoader:
    """Load dataset text files for the RAG module."""

    def __init__(self) -> None:
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.dataset_dir = self.base_dir / "datasets"

    def load_texts(self) -> List[str]:
        """Load available text files from the datasets folder."""
        texts: List[str] = []
        for file_path in self.dataset_dir.glob("*.csv"):
            texts.append(file_path.read_text(encoding="utf-8", errors="ignore"))

        if not texts:
            raise RuntimeError(
                "No dataset files found in the datasets directory. "
                "Place TruthfulQA and SQuAD CSV files in the datasets folder."
            )

        return texts
