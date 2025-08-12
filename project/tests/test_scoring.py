import pytest
from project.scoring import (
    _penalty_replace, _penalty_add_del,
    _match_one_replace, _match_one_add, _match_one_del,
    _find_candidate_windows, _best_substring_score
)


# ---------- Penalties ----------
@pytest.mark.parametrize("pos,expected", [
    (1, 5), (2, 4), (3, 3), (4, 2), (5, 1), (10, 1), (0, 5), (-3, 5)
])
def test_penalty_replace(pos, expected):
    assert _penalty_replace(pos) == expected

@pytest.mark.parametrize("pos,expected", [
    (1, 10), (2, 8), (3, 6), (4, 4), (5, 2), (10, 2), (0, 10), (-2, 10)
])
def test_penalty_add_del(pos, expected):
    assert _penalty_add_del(pos) == expected

# ---------- One replace (same length) ----------
def test_match_one_replace_no_diff():
    ok, score = _match_one_replace("test", "test")
    assert ok is False and score == 0

@pytest.mark.parametrize("q,cand,pos_pen",
    [
        ("test", "text", 3),
        ("abcd", "abXd", 3),
        ("abcd", "Xbcd", 1),
        ("abcd", "abcX", 4),
    ]
)
def test_match_one_replace_single(q, cand, pos_pen):
    ok, score = _match_one_replace(q, cand)
    assert ok is True
    assert score == 2*len(q) - _penalty_replace(pos_pen)

def test_match_one_replace_multiple_diffs():
    ok, score = _match_one_replace("abcd", "abXY")
    assert ok is False and score == 0

# ---------- One add (query longer by 1) ----------
@pytest.mark.parametrize("q,cand,miss_pos", [
    ("abcd", "abd", 3),
    ("abcd", "acd", 2),
    ("abcd", "abc", 4),
    ("ab",   "a",   2),
])
def test_match_one_add(q, cand, miss_pos):
    ok, score = _match_one_add(q, cand)
    assert ok is True
    assert score == 2*len(cand) - _penalty_add_del(miss_pos)

def test_match_one_add_not_one_extra():
    ok, score = _match_one_add("abc", "a")
    assert ok is False and score == 0


# ---------- One delete (query shorter by 1) ----------
@pytest.mark.parametrize("q,cand,miss_pos", [
    ("abd",  "abcd", 3),
    ("acd",  "abcd", 2),
    ("abc",  "abcd", 4),
    ("a",    "ab",   2),
])
def test_match_one_del(q, cand, miss_pos):
    ok, score = _match_one_del(q, cand)
    assert ok is True
    assert score == 2*len(q) - _penalty_add_del(miss_pos)

def test_match_one_del_not_one_missing():
    ok, score = _match_one_del("a", "abcd")
    assert ok is False and score == 0


# ---------- Candidate windows ----------
def test_find_candidate_windows_basic():
    s = "hello world"
    starts = _find_candidate_windows(s, 5, "world")
    assert starts == [6]

def test_find_candidate_windows_fallback_on_no_hint_match():
    s = "abcde"
    starts = _find_candidate_windows(s, 3, "z")
    assert starts == [0,1,2]

def test_find_candidate_windows_all_when_no_hint():
    s = "abcdef"
    starts = _find_candidate_windows(s, 2, "")
    assert starts == [0,1,2,3,4]

def test_find_candidate_windows_bounds():
    assert _find_candidate_windows("abc", 0, "a") == []
    assert _find_candidate_windows("abc", 4, "a") == []

# ---------- Best substring score ----------
def test_best_substring_exact_substring():
    assert _best_substring_score("ello", "hello world") == 2*4

def test_best_substring_one_replace_best():
    score = _best_substring_score("helo", "hello")
    assert 0 < score < 2*4

def test_best_substring_one_add_best():
    score = _best_substring_score("abxd", "zzabydzz")
    assert score > 0

def test_best_substring_one_del_best():
    score = _best_substring_score("acd", "xxabcdyy")
    expected = max(0, 2*len("acd") - _penalty_add_del(2))  
    assert score == expected


def test_best_substring_no_match():
    assert _best_substring_score("xyz", "aaaaa") == 0

def test_best_substring_empty_q():
    assert _best_substring_score("", "anything") == 0