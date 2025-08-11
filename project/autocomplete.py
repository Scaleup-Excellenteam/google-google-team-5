# autocomplete.py
from typing import List
from text_data import TextDatabase
from scoring import _best_substring_score
from models import Match, AutoCompleteData
from trigram import _normalize

class AutoCompleter:
    def __init__(self, db: TextDatabase, cap_per_query: int = 500) -> None:
        self.db = db
        self.cap = cap_per_query
        self._qnorm_cache = {}  # raw_query -> normalized

    def _norm(self, q: str) -> str:
        """
        Normalize the input query string using a cache to avoid repeated normalization.

        Args:
            q (str): Raw query string input by the user.

        Returns:
            str: Normalized query string.
        """
        if q in self._qnorm_cache:
            return self._qnorm_cache[q]
        v = _normalize(q)
        self._qnorm_cache[q] = v
        return v

    def get_best_k_completions(self, query: str, k: int = 5) -> List[AutoCompleteData]:
        """
        Get the best k autocomplete suggestions matching the given query.

        The method normalizes the query, retrieves candidate sentence indices from
        the database using character trigram indexing, scores each candidate against
        the query allowing at most one edit, and returns the top k scored matches.

        Args:
            query (str): The raw input query string.
            k (int, optional): Number of top completions to return. Defaults to 5.

        Returns:
            List[AutoCompleteData]: List of autocomplete results sorted by descending score
                and then alphabetically by completed sentence.
        """
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