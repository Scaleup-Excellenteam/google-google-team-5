from typing import List, Tuple

def _penalty_replace(pos1: int) -> int:
    """
    Calculate penalty for replacing a character at given 1-based position.

    Args:
        pos1 (int): Position (1-based) of the replaced character.

    Returns:
        int: Penalty score.
    """
    if pos1 <= 0:
        pos1 = 1
    if pos1 == 1: return 5
    if pos1 == 2: return 4
    if pos1 == 3: return 3
    if pos1 == 4: return 2
    return 1

def _penalty_add_del(pos1: int) -> int:
    """
    Calculate penalty for adding or deleting a character at given 1-based position.

    Args:
        pos1 (int): Position (1-based) of the added/deleted character.

    Returns:
        int: Penalty score.
    """
    if pos1 <= 0:
        pos1 = 1
    if pos1 == 1: return 10
    if pos1 == 2: return 8
    if pos1 == 3: return 6
    if pos1 == 4: return 4
    return 2

def _match_equal(q: str, cand: str) -> Tuple[bool, int]:
    """
    Check if query exactly matches candidate substring.

    Args:
        q (str): Query string.
        cand (str): Candidate substring.

    Returns:
        Tuple[bool, int]: (match success, score)
    """
    if q == cand:
        return True, 2 * len(q)
    return False, 0

def _match_one_replace(q: str, cand: str) -> Tuple[bool, int]:
    """
    Check if query matches candidate with exactly one character replaced.

    Args:
        q (str): Query string.
        cand (str): Candidate substring.

    Returns:
        Tuple[bool, int]: (match success, score)
    """
    if len(q) != len(cand):
        return False, 0
    diffs = [i for i, (a, b) in enumerate(zip(q, cand), start=1) if a != b]
    if len(diffs) == 1:
        return True, 2 * len(q) - _penalty_replace(diffs[0])
    return False, 0

def _match_one_add(q: str, cand: str) -> Tuple[bool, int]:
    """
    Check if query has one extra character compared to candidate (one deletion in candidate).

    Args:
        q (str): Query string (longer).
        cand (str): Candidate substring (shorter).

    Returns:
        Tuple[bool, int]: (match success, score)
    """
    n, m = len(q), len(cand)
    if n != m + 1:
        return False, 0
    i = j = 0
    skipped = False
    skip_pos = 0
    while i < n and j < m:
        if q[i] == cand[j]:
            i += 1
            j += 1
        else:
            if skipped:
                return False, 0
            skipped = True
            skip_pos = i + 1
            i += 1
    if not skipped:
        skip_pos = n
    return True, 2 * m - _penalty_add_del(skip_pos)

def _match_one_del(q: str, cand: str) -> Tuple[bool, int]:
    """
    Check if query has one missing character compared to candidate (one insertion in candidate).

    Args:
        q (str): Query string (shorter).
        cand (str): Candidate substring (longer).

    Returns:
        Tuple[bool, int]: (match success, score)
    """
    n, m = len(q), len(cand)
    if n + 1 != m:
        return False, 0
    i = j = 0
    skipped = False
    miss_pos = 0
    while i < n and j < m:
        if q[i] == cand[j]:
            i += 1
            j += 1
        else:
            if skipped:
                return False, 0
            skipped = True
            miss_pos = i + 1
            j += 1
    if not skipped:
        miss_pos = n + 1
    return True, 2 * n - _penalty_add_del(miss_pos)

def _find_candidate_windows(s: str, L: int, q_hint: str) -> List[int]:
    """
    Find candidate substring start indices in s of length L that start with the first character of q_hint.

    Args:
        s (str): Candidate string.
        L (int): Window length.
        q_hint (str): Query hint string.

    Returns:
        List[int]: List of valid start indices.
    """
    if L <= 0 or L > len(s):
        return []
    if not q_hint:
        return list(range(len(s) - L + 1))
    ch = q_hint[0]
    starts = []
    i = s.find(ch)
    while i != -1 and i <= len(s) - L:
        starts.append(i)
        i = s.find(ch, i + 1)
    if not starts:
        return list(range(len(s) - L + 1))
    return starts

def _best_substring_score(q: str, s: str) -> int:
    """
    Compute the best match score of normalized query q against all substrings of normalized sentence s,
    allowing exact match or one edit (replace, add, delete).

    Args:
        q (str): Normalized query.
        s (str): Normalized candidate string.

    Returns:
        int: Best matching score or 0 if no valid match.
    """
    n = len(q)
    if n == 0:
        return 0
    # Fast exact substring check
    if q in s:
        return 2 * n

    best = 0

    # One replace
    if len(s) >= n:
        for start in _find_candidate_windows(s, n, q):
            cand = s[start:start+n]
            ok, score = _match_one_replace(q, cand)
            if ok and score > best:
                best = score
                if best == 2 * n - 1:
                    break

    # One add (query longer by one)
    if n >= 2 and len(s) >= n - 1:
        for start in _find_candidate_windows(s, n-1, q[:-1] if n > 1 else q):
            cand = s[start:start + n - 1]
            ok, score = _match_one_add(q, cand)
            if ok and score > best:
                best = score

    # One delete (query shorter by one)
    if len(s) >= n + 1:
        for start in _find_candidate_windows(s, n+1, q):
            cand = s[start:start + n + 1]
            ok, score = _match_one_del(q, cand)
            if ok and score > best:
                best = score

    return best
