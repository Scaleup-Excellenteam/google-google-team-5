from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple
import re
import string

from text_data import TextDatabase, Sentence

# ---------------- Normalization helpers ----------------

_PUNC_SET = set(string.punctuation)

def _normalize(s: str) -> str:
    """
    Lowercase, remove punctuation (replace with space),
    collapse spaces, strip ends.
    """
    s = ''.join(ch.lower() if ch not in _PUNC_SET else ' ' for ch in s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def _penalty_replace(pos_1based: int) -> int:
    # Replacement penalties
    if pos_1based == 1: return 5
    if pos_1based == 2: return 4
    if pos_1based == 3: return 3
    if pos_1based == 4: return 2
    return 1

def _penalty_add_or_miss(pos_1based: int) -> int:
    # Insertion/Deletion penalties
    if pos_1based == 1: return 10
    if pos_1based == 2: return 8
    if pos_1based == 3: return 6
    if pos_1based == 4: return 4
    return 2

def _score_pair(q_norm: str, cand_norm: str) -> Tuple[bool, int]:
    """
    Return (is_match, score) between normalized query and candidate substring.
    Allow at most ONE correction: replace / insert / delete.
    """
    n, m = len(q_norm), len(cand_norm)
    if n == 0 or m == 0:
        return (False, 0)

    base_equal = 2 * n
    base_unequal = 2 * min(n, m)

    # Case 1: Same length => possible match or 1 replacement
    if n == m:
        diffs = [i for i, (a, b) in enumerate(zip(q_norm, cand_norm), start=1) if a != b]
        if not diffs:
            return True, base_equal
        if len(diffs) == 1:
            return True, base_equal - _penalty_replace(diffs[0])
        return False, 0

    # Case 2: Query longer by 1 => insertion in query (remove one letter)
    if n == m + 1:
        i = j = 0
        skip_pos = None
        while i < n and j < m:
            if q_norm[i] == cand_norm[j]:
                i += 1; j += 1
            else:
                if skip_pos is not None:
                    return (False, 0)
                skip_pos = i + 1
                i += 1
        if skip_pos is None:
            skip_pos = n
        return True, base_unequal - _penalty_add_or_miss(skip_pos)

    # Case 3: Query shorter by 1 => missing letter in query (add one letter)
    if m == n + 1:
        i = j = 0
        miss_pos = None
        while i < n and j < m:
            if q_norm[i] == cand_norm[j]:
                i += 1; j += 1
            else:
                if miss_pos is not None:
                    return (False, 0)
                miss_pos = j + 1
                j += 1
        if miss_pos is None:
            miss_pos = m
        return True, base_unequal - _penalty_add_or_miss(miss_pos)

    # Anything else => needs >1 edit
    return (False, 0)

def score_query_against_sentence(query: str, sentence_original: str) -> int:
    """
    Calculate max score of query vs sentence.
    Only consider matches starting/ending on word boundaries,
    and only alphabetic substrings (letters + spaces).
    """
    q = _normalize(query)
    s = _normalize(sentence_original)
    if not q or not s:
        return 0

    best = 0
    lengths = {len(q) - 1, len(q), len(q) + 1}
    for L in lengths:
        if L <= 0 or L > len(s):
            continue
        for start in range(0, len(s) - L + 1):
            if start > 0 and s[start - 1] != ' ':
                continue
            end = start + L
            if end < len(s) and s[end] != ' ':
                continue

            cand = s[start:end]

            # NEW: only letters+spaces, to avoid matches like "27 be"
            # (התקן מדבר על "letters including space but not punctuation")
            if not re.fullmatch(r"[a-z ]+", cand):
                continue

            ok, sc = _score_pair(q, cand)
            if ok and sc > best:
                best = sc
    return best

# ---------------- Public API ----------------

@dataclass
class AutoCompleteData:
    completed_sentence: str
    source_text: str
    offset: int
    score: int

class AutoCompleter:
    def __init__(self, db: TextDatabase) -> None:
        self.db = db

    def get_best_k_completions(self, query: str, k: int = 5) -> List[AutoCompleteData]:
        if not query or not query.strip():
            return []

        results: List[AutoCompleteData] = []
        for s in self.db.iter_sentences():
            sc = score_query_against_sentence(query, s.text)
            if sc > 0:
                results.append(AutoCompleteData(
                    completed_sentence=s.text,
                    source_text=s.file_path,
                    offset=s.line_number,
                    score=sc
                ))

        results.sort(key=lambda r: (-r.score, r.completed_sentence.casefold()))
        return results[:k]
