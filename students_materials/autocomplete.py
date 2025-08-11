# autocomplete.py
from __future__ import annotations
from typing import List, Tuple
from dataclasses import dataclass
from text_data import TextDatabase, AutoCompleteData, _normalize

# ----- Penalties per spec (1-based positions) -----
def _penalty_replace(pos1: int) -> int:
    # -5, -4, -3, -2, -1 for 1st,2nd,3rd,4th,5th+
    if pos1 <= 0:
        pos1 = 1
    if pos1 == 1: return 5
    if pos1 == 2: return 4
    if pos1 == 3: return 3
    if pos1 == 4: return 2
    return 1

def _penalty_add_del(pos1: int) -> int:
    # -10, -8, -6, -4, -2 for 1st,2nd,3rd,4th,5th+
    if pos1 <= 0:
        pos1 = 1
    if pos1 == 1: return 10
    if pos1 == 2: return 8
    if pos1 == 3: return 6
    if pos1 == 4: return 4
    return 2

# ---------- Single-edit matching against a candidate substring ----------

def _match_equal(q: str, cand: str) -> Tuple[bool, int]:
    # exact substring
    if q == cand:
        return True, 2 * len(q)
    return False, 0

def _match_one_replace(q: str, cand: str) -> Tuple[bool, int]:
    # same length; allow exactly one replacement
    if len(q) != len(cand):
        return (False, 0)
    diffs = []
    for i, (a, b) in enumerate(zip(q, cand), start=1):
        if a != b:
            diffs.append(i)
            if len(diffs) > 1:
                return (False, 0)
    if len(diffs) == 1:
        pos = diffs[0]
        return True, 2 * len(q) - _penalty_replace(pos)
    return (False, 0)

def _match_one_add(q: str, cand: str) -> Tuple[bool, int]:
    """
    Query has one EXTRA char vs cand: len(q) = len(cand) + 1
    (i.e., an added letter in the query; need to delete one from q)
    Position penalty is the position (1-based) of the extra letter in the query.
    """
    n, m = len(q), len(cand)
    if n != m + 1:
        return (False, 0)
    i = j = 0
    skipped = 0
    skip_pos = 0
    while i < n and j < m:
        if q[i] == cand[j]:
            i += 1; j += 1
        else:
            if skipped:
                return (False, 0)
            skipped = 1
            skip_pos = i + 1  # 1-based in query
            i += 1
    if not skipped:
        # extra at the end
        skip_pos = n
    # base = 2 * matches = 2 * m
    return True, 2 * m - _penalty_add_del(skip_pos)

def _match_one_del(q: str, cand: str) -> Tuple[bool, int]:
    """
    Query is MISSING one char vs cand: len(q) = len(cand) - 1
    (i.e., need to insert one char into q)
    Position penalty is the position (1-based) in the query where the missing char occurs.
    If the missing char is before q[0], position is 1; if after the last, position is len(q)+1.
    """
    n, m = len(q), len(cand)
    if n + 1 != m:
        return (False, 0)
    i = j = 0
    skipped = 0
    miss_pos = 0
    while i < n and j < m:
        if q[i] == cand[j]:
            i += 1; j += 1
        else:
            if skipped:
                return (False, 0)
            skipped = 1
            miss_pos = i + 1  # insertion position in query (1-based)
            j += 1
    if not skipped:
        # missing at the end (i == n, j == m-1)
        miss_pos = n + 1
    # base = 2 * matches = 2 * n
    return True, 2 * n - _penalty_add_del(miss_pos)

def _best_substring_score(q: str, s: str) -> int:
    """
    Given normalized query q and normalized sentence s, compute the best score over all substrings of s
    that can match q with: exact, or exactly one replace/add/delete.
    Return 0 if no match under these rules.
    """
    n = len(q)
    if n == 0:
        return 0

    # Fast path: exact substring exists → base score with no penalty.
    if q in s:
        return 2 * n

    best = 0

    # Case: one replacement → check all substrings of length n
    if len(s) >= n:
        for start in _find_candidate_windows(s, n, q):
            cand = s[start:start+n]
            ok, score = _match_one_replace(q, cand)
            if ok and score > best:
                best = score
                if best == 2 * n - 1:  # max possible under replace is base - min penalty (1)
                    break

    # Case: one extra in query (add) → substrings of length n-1
    if n >= 2 and len(s) >= n - 1:
        L = n - 1
        for start in _find_candidate_windows(s, L, q[:-1] if n > 1 else q):
            cand = s[start:start+L]
            ok, score = _match_one_add(q, cand)
            if ok and score > best:
                best = score

    # Case: one missing in query (delete) → substrings of length n+1
    if len(s) >= n + 1:
        L = n + 1
        for start in _find_candidate_windows(s, L, q):
            cand = s[start:start+L]
            ok, score = _match_one_del(q, cand)
            if ok and score > best:
                best = score

    return best

def _find_candidate_windows(s: str, L: int, q_hint: str) -> List[int]:
    """
    Cheap prefilter for window starts:
    - If L <= 0 → none.
    - Prefer windows that share the first character of q_hint to reduce checks.
    """
    if L <= 0 or L > len(s):
        return []
    starts: List[int] = []
    if not q_hint:
        return list(range(0, len(s) - L + 1))
    ch = q_hint[0]
    i = s.find(ch, 0)
    while i != -1 and i <= len(s) - L:
        starts.append(i)
        i = s.find(ch, i + 1)
    # Fallback if too sparse:
    if not starts:
        return list(range(0, len(s) - L + 1))
    return starts

@dataclass
class Match:
    score: int
    file_path: str
    line_num: int
    original: str

class AutoCompleter:
    def __init__(self, db: TextDatabase, cap_per_query: int = 500) -> None:
        self.db = db
        self.cap = cap_per_query
        self._qnorm_cache = {}  # raw_query -> normalized

    def _norm(self, q: str) -> str:
        if q in self._qnorm_cache:
            return self._qnorm_cache[q]
        v = _normalize(q)
        self._qnorm_cache[q] = v
        return v

    def get_best_k_completions(self, query: str, k: int = 5) -> List[AutoCompleteData]:
        qn = self._norm(query)
        if not qn:
            return []
        cand_indices = self.db.candidates_by_query(qn, cap=self.cap)

        matches: List[Match] = []
        qn_len = len(qn)

        # Evaluate candidates
        for idx in cand_indices:
            original, fpath, line, s_norm = self.db.items[idx]
            score = _best_substring_score(qn, s_norm)
            if score > 0:
                matches.append(Match(score=score, file_path=fpath, line_num=line, original=original))

        if not matches:
            return []

        # Sort: higher score first; tie-breaker alphabetical by completed_sentence (case-insensitive)
        matches.sort(key=lambda m: (-m.score, m.original.lower()))

        # Build final outputs
        out: List[AutoCompleteData] = []
        for m in matches[:k]:
            out.append(AutoCompleteData(
                completed_sentence=m.original,
                source_text=m.file_path,
                offset=m.line_num,
                score=m.score
            ))
        return out