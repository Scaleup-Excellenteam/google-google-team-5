from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple
import re
import string

from text_data import TextDatabase, Sentence

# ---------------- Normalization helpers ----------------

_PUNC_SET = set(string.punctuation) # signs in strings.

def _normalize(s: str) -> str:
    """
    Lowercases the string, replaces punctuation with spaces,
    collapses multiple spaces into one, and strips leading/trailing spaces.

    Args:
        s (str): The input string to normalize.

    Returns:
        str: The normalized string.
    """
    s = ''.join(ch.lower() if ch not in _PUNC_SET else ' ' for ch in s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def _penalty_replace(pos_1based: int) -> int:
    """
    Calculates the penalty score for replacing a character,
    based on its 1-based position in the string.

    Higher penalties are given for earlier positions.

    Args:
        pos_1based (int): The position in 1-based indexing (1 is the first position).

    Returns:
        int: The penalty score associated with the given position.
    """
    if pos_1based == 1: return 5
    if pos_1based == 2: return 4
    if pos_1based == 3: return 3
    if pos_1based == 4: return 2
    return 1

def _penalty_add_or_miss(pos_1based: int) -> int:
    """
    Calculates the penalty score for adding or missing a character,
    based on its 1-based position in the string.

    Higher penalties are given for earlier positions.

    Args:
        pos_1based (int): The position in 1-based indexing (1 is the first position).

    Returns:
        int: The penalty score associated with the given position.
    """
    if pos_1based == 1: return 10
    if pos_1based == 2: return 8
    if pos_1based == 3: return 6
    if pos_1based == 4: return 4
    return 2

def _score_pair(q_norm: str, cand_norm: str) -> Tuple[bool, int]:
    """
    Compare a normalized query (q_norm) with a normalized candidate substring (cand_norm)
    and return a tuple: (is_match, score).

    The function allows at most ONE correction:
    - Replace one character
    - Insert one character
    - Delete one character
    """

    # Lengths of query and candidate
    n, m = len(q_norm), len(cand_norm)

    # If either string is empty → no match
    if n == 0 or m == 0:
        return (False, 0)

    # Base scores: higher for exact length match
    base_equal = 2 * n               # Score for perfect equal-length match
    base_unequal = 2 * min(n, m)     # Score for slightly unequal length matches

    # ---------------- Case 1: Equal length → possible replacement ----------------
    if n == m:
        # Find all positions where characters differ
        diffs = [i for i, (a, b) in enumerate(zip(q_norm, cand_norm), start=1) if a != b]

        if not diffs:
            # Exact match → return full score
            return True, base_equal

        if len(diffs) == 1:
            # One letter difference → allowed replacement
            return True, base_equal - _penalty_replace(diffs[0])

        # More than one difference → not allowed
        return False, 0

    # ---------------- Case 2: Query is longer by 1 → possible deletion ----------------
    if n == m + 1:
        i = j = 0
        skip_pos = None  # Position where the extra letter is skipped

        while i < n and j < m:
            if q_norm[i] == cand_norm[j]:
                # Characters match → move both pointers
                i += 1
                j += 1
            else:
                if skip_pos is not None:
                    # More than one mismatch → not allowed
                    return (False, 0)
                skip_pos = i + 1  # Record where we skipped
                i += 1            # Move only query pointer

        # If no skip happened, extra char is at the end
        if skip_pos is None:
            skip_pos = n

        # Return score after applying deletion penalty
        return True, base_unequal - _penalty_add_or_miss(skip_pos)

    # ---------------- Case 3: Query is shorter by 1 → possible insertion ----------------
    if m == n + 1:
        i = j = 0
        miss_pos = None  # Position where an extra char exists in candidate

        while i < n and j < m:
            if q_norm[i] == cand_norm[j]:
                i += 1
                j += 1
            else:
                if miss_pos is not None:
                    # More than one mismatch → not allowed
                    return (False, 0)
                miss_pos = j + 1  # Record where we inserted
                j += 1            # Move only candidate pointer

        # If no mismatch found, the extra char is at the end
        if miss_pos is None:
            miss_pos = m

        # Return score after applying insertion penalty
        return True, base_unequal - _penalty_add_or_miss(miss_pos)

    # ---------------- Case 4: More than 1 edit needed ----------------
    return (False, 0)


def score_query_against_sentence(query: str, sentence_original: str) -> int:
    """
    Calculate the maximum possible score of a query against a sentence.

    Rules:
    - Matches must start/end on word boundaries (spaces)
    - Only alphabetic substrings (letters + spaces) are considered
    - Allows at most ONE edit (replace/insert/delete)
    """

    # Normalize query and sentence (remove punctuation, lowercase, etc.)
    q = _normalize(query)
    s = _normalize(sentence_original)

    # If either is empty → no match
    if not q or not s:
        return 0

    best = 0  # Track best score found

    # Possible candidate lengths to check:
    # - same length as query
    # - 1 less
    # - 1 more
    lengths = {len(q) - 1, len(q), len(q) + 1}

    for L in lengths:
        # Skip invalid lengths
        if L <= 0 or L > len(s):
            continue

        # Slide a window of length L over the sentence
        for start in range(0, len(s) - L + 1):
            # Ensure match starts at word boundary
            if start > 0 and s[start - 1] != ' ':
                continue

            end = start + L

            # Ensure match ends at word boundary
            if end < len(s) and s[end] != ' ':
                continue

            # Extract candidate substring
            cand = s[start:end]

            # Ensure only letters + spaces are considered
            if not re.fullmatch(r"[a-z ]+", cand):
                continue

            # Compare query vs candidate
            ok, sc = _score_pair(q, cand)

            # Update best score if match found
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
