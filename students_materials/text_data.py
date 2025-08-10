# text_data.py
from __future__ import annotations
from dataclasses import dataclass
import os
import re
import string
from typing import Iterable, List

# translate punctuation → space (so words don't stick together after removal)
_PUNCT_TABLE = str.maketrans({c: " " for c in string.punctuation})

def normalize(text: str) -> str:
    """
    Normalize text for matching:
    - lowercase
    - remove punctuation (as spaces)
    - collapse multiple spaces
    """
    text = text.lower().translate(_PUNCT_TABLE)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

@dataclass
class SentenceRecord:
    original: str       # original (with punctuation)
    normalized: str     # normalized for matching
    file_path: str
    line_number: int

class TextDatabase:
    """Loads .txt files (recursively) and stores sentence records."""
    def __init__(self) -> None:
        self._records: List[SentenceRecord] = []

    @staticmethod
    def normalize(text: str) -> str:
        return normalize(text)

    def load(self, folder_path: str) -> int:
        self._records.clear()
        for root, _, files in os.walk(folder_path):
            for file in files:
                if not file.lower().endswith(".txt"):
                    continue
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    for ln, line in enumerate(f, start=1):
                        line = line.strip()
                        if not line:
                            continue
                        self._records.append(
                            SentenceRecord(
                                original=line,
                                normalized=normalize(line),
                                file_path=file_path,
                                line_number=ln,
                            )
                        )
        return len(self._records)

    def __len__(self) -> int:
        return len(self._records)

    def records(self) -> Iterable[SentenceRecord]:
        return self._records
