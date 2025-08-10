# autocomplete.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple
import os

from text_data import TextDatabase

# נשתמש באותה פונקציית נירמול של ה-DB
normalize = TextDatabase.normalize

@dataclass(order=True)
class AutoCompleteData:
    completed_sentence: str  # המשפט המלא (כפי שמופיע בקובץ)
    source_text: str         # נתיב הקובץ
    offset: int              # מספר שורה (1-מבוסס)
    score: int               # הציון לפי החוקים

class AutoCompleter:
    """מנוע התאמה וניקוד לפי כללי החלק הראשון (תת־מחרוזת/טעות אחת)."""
    def __init__(self, db: TextDatabase):
        self.db = db

    # --- קנסות לפי מיקום (1..)
    @staticmethod
    def _penalty_replace(pos1: int) -> int:
        # החלפה: 1→5, 2→4, 3→3, 4→2, >=5→1
        return {1: 5, 2: 4, 3: 3, 4: 2}.get(pos1, 1)

    @staticmethod
    def _penalty_insdel(pos1: int) -> int:
        # הוספה/מחיקה: 1→10, 2→8, 3→6, 4→4, >=5→2
        return {1: 10, 2: 8, 3: 6, 4: 4}.get(pos1, 2)

    def _best_match_score(self, q: str, s: str) -> Tuple[bool, int]:
        """
        בדיקת התאמה בין q (שאילתה מנורמלת) ל-s (משפט מנורמל).
        התאמה חוקית אם:
          - q הוא תת־מחרוזת של s, או
          - ניתן להגיע לתת־מחרוזת של s באמצעות טעות אחת בדיוק ב-q:
              החלפה/הוספה/מחיקה.
        ציון: base = 2 * len(q); אם יש טעות – מפחיתים קנס לפי מיקום.
        מחזיר (התאמה?, הציון הטוב ביותר).
        """
        if not q:
            return False, 0

        base = 2 * len(q)
        best = -1  # נשמור את הציון המקסימלי שמצאנו

        # --- 1) תת־מחרוזת מדויקת ---
        if s.find(q) != -1:
            best = max(best, base)

        L, n = len(q), len(s)

        # --- 2) החלפה אחת (Hamming distance == 1) על חלון באורך L ---
        for start in range(0, n - L + 1):
            seg = s[start:start + L]
            diffs = 0
            pos = -1
            for i in range(L):
                if seg[i] != q[i]:
                    diffs += 1
                    pos = i
                    if diffs > 1:
                        break
            if diffs == 1:
                score = base - self._penalty_replace(pos + 1)
                if score > best:
                    best = score

        # --- 3) הוספת תו ב-q (כלומר תו מיותר ב-q) => נסיר תו אחד מ-q ---
        if L >= 1:
            for i in range(L):  # מיקום התו המיותר
                q_removed = q[:i] + q[i+1:]
                if s.find(q_removed) != -1:
                    score = base - self._penalty_insdel(i + 1)
                    if score > best:
                        best = score

        # --- 4) מחיקת תו ב-q (כלומר חסר תו ב-q) => חלון ב-s באורך L+1 ---
        for start in range(0, n - (L + 1) + 1):
            seg = s[start:start + L + 1]
            # בדיקת כל מיקום אפשרי שבו הוסף התו ב-q
            for i in range(L + 1):
                if seg[:i] == q[:i] and seg[i+1:] == q[i:]:
                    score = base - self._penalty_insdel(i + 1)
                    if score > best:
                        best = score

        return (best >= 0, best if best >= 0 else 0)

    def completion_function(self, query: str, limit: int = 5) -> List[AutoCompleteData]:
        q_norm = normalize(query)
        results: List[AutoCompleteData] = []

        for rec in self.db.records():
            matched, score = self._best_match_score(q_norm, rec.normalized)
            if matched:
                results.append(
                    AutoCompleteData(
                        completed_sentence=rec.original,
                        source_text=rec.file_path,
                        offset=rec.line_number,
                        score=score,
                    )
                )

        # מיון: ציון יורד ואז אלפביתית (לפי הדרישות)
        results.sort(key=lambda x: (-x.score, x.completed_sentence.lower()))
        return results[:limit]

# ---- דמו CLI ----
if __name__ == "__main__":
    db = TextDatabase()
    total = db.load("Archive")
    print(f"✅ Loaded {total} sentences.")

    ac = AutoCompleter(db)

    while True:
        q = input("\nType query (or 'exit'): ").strip()
        if q.lower() == "exit":
            break
        top = ac.completion_function(q, limit=5)
        if not top:
            print("No matches found.")
            continue
        print("\nTop completions:")
        for i, t in enumerate(top, 1):
            print(f"{i}. {t.completed_sentence}  "
                  f"[File: {os.path.basename(t.source_text)}, Line: {t.offset}]  "
                  f"(score={t.score})")
