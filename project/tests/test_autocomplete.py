import pytest
from unittest.mock import MagicMock, patch
from project.autocomplete import AutoCompleter
from project.models import AutoCompleteData, Match

@pytest.fixture
def mock_db():
    db = MagicMock()
    db.candidates_by_query.return_value = [0, 1]
    db.items = [
        ("Hello World", "file1.txt", 10, "hello world"),
        ("Hi There", "file2.txt", 20, "hi there"),
    ]
    return db

def test_norm_caching(mock_db):
    ac = AutoCompleter(mock_db)
    with patch("project.autocomplete._normalize", return_value="normalized") as mock_norm:
        result1 = ac._norm("Query")
        result2 = ac._norm("Query")  # אמור להגיע מה־cache, לא לקרוא שוב
        assert result1 == "normalized"
        assert result2 == "normalized"
        mock_norm.assert_called_once_with("Query")

def test_get_best_k_completions_empty_query(mock_db):
    ac = AutoCompleter(mock_db)
    with patch("project.autocomplete._normalize", return_value="") as mock_norm:
        results = ac.get_best_k_completions("  ")
        assert results == []
        mock_db.candidates_by_query.assert_not_called()

def test_get_best_k_completions_with_matches(mock_db):
    ac = AutoCompleter(mock_db)

    # מדמים ניקוד: פריט ראשון יקבל ניקוד 10, השני 5
    with patch("project.autocomplete._normalize", return_value="hello") as mock_norm, \
         patch("project.autocomplete._best_substring_score", side_effect=[10, 5]) as mock_score:
        
        results = ac.get_best_k_completions("hello", k=2)

        assert len(results) == 2
        assert isinstance(results[0], AutoCompleteData)
        assert results[0].completed_sentence == "Hello World"
        assert results[1].completed_sentence == "Hi There"
        assert results[0].score == 10
        assert results[1].score == 5
        # בדיקת סדר: הכי גבוה ראשון
        assert results[0].score >= results[1].score

def test_get_best_k_completions_no_positive_score(mock_db):
    ac = AutoCompleter(mock_db)
    with patch("project.autocomplete._normalize", return_value="hello"), \
         patch("project.autocomplete._best_substring_score", return_value=0):
        results = ac.get_best_k_completions("hello")
        assert results == []
