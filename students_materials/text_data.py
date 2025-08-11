from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import List, Iterable
import os

@dataclass
class Sentence:
    text: str           # השורה המקורית (כולל פיסוק)
    file_path: str      # נתיב קובץ מקור
    line_number: int    # מספר שורה (1-based)

class TextDatabase:
    """
    טוען את כל קבצי הטקסט (‎.txt) מתיקיית שורש נתונה (רקורסיבי),
    ושומר כל קובץ כרשימת שורות (משפטים).
    """
    def __init__(self) -> None:
        self.sentences: List[Sentence] = []

    def load(self, root_folder: str | os.PathLike) -> None:
        root = Path(root_folder)
        if not root.exists():
            raise FileNotFoundError(f"Folder not found: {root_folder}")

        self.sentences.clear()
        for path in root.rglob("*.txt"):
            try:
                with path.open("r", encoding="utf-8", errors="ignore") as f:
                    for i, line in enumerate(f, start=1):
                        line = line.rstrip("\n\r")
                        if line.strip() == "":
                            continue
                        self.sentences.append(Sentence(text=line, file_path=str(path), line_number=i))
            except Exception as e:
                # מדלגים על קובץ בעייתי, אבל ממשיכים
                print(f"[WARN] Could not read {path}: {e}")

    def __len__(self) -> int:
        return len(self.sentences)

    def iter_sentences(self) -> Iterable[Sentence]:
        return iter(self.sentences)
