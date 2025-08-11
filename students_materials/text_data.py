# text_data.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Dict, Iterable
import os
import re
import string
from collections import defaultdict

_PUNC_SET = set(string.punctuation)  # punctuation is ignored for scoring (replaced by spaces)

def _normalize(s: str) -> str:
    """
    Lowercase, replace punctuation with spaces, collapse spaces.
    Spaces count; punctuation doesn't.
    """
    s = ''.join((ch.lower() if ch not in _PUNC_SET else ' ') for ch in s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def _trigrams(s: str) -> Iterable[str]:
    """Yield overlapping character trigrams (3-grams). For strings < 3, yield the whole string."""
    if len(s) < 3:
        if s:
            yield s
        return
    for i in range(len(s) - 2):
        yield s[i:i+3]

@dataclass
class AutoCompleteData:
    completed_sentence: str    # original sentence (with punctuation/casing)
    source_text: str           # file path
    offset: int                # 1-based line number
    score: int

class TextDatabase:
    """
    Loads a folder of .txt files, keeps both original and normalized sentences,
    and builds a character trigram inverted index for fast candidate pruning.
    """
    def __init__(self) -> None:
        self.items: List[Tuple[str, str, int, str]] = []
        # List of tuples: (original_sentence, file_path, line_number, normalized_sentence)
        self._gram_index: Dict[str, List[int]] = defaultdict(list)
        self._loaded = False

    def load(self, root_folder: str) -> None:
        """
        Walks the folder tree and loads all .txt files.
        Each line is treated as a sentence.
        """
        self.items.clear()
        self._gram_index.clear()

        for dirpath, _, filenames in os.walk(root_folder):
            for fn in filenames:
                if not fn.lower().endswith('.txt'):
                    continue
                fpath = os.path.join(dirpath, fn)
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    for i, line in enumerate(f, start=1):
                        original = line.rstrip('\n')
                        norm = _normalize(original)
                        if not norm:
                            continue
                        idx = len(self.items)
                        self.items.append((original, fpath, i, norm))
                        # index by character trigrams
                        seen = set()
                        for g in _trigrams(norm):
                            if g not in seen:
                                self._gram_index[g].append(idx)
                                seen.add(g)
        self._loaded = True

    def __len__(self) -> int:
        return len(self.items)

    def candidates_by_query(self, q_norm: str, cap: int = 500) -> List[int]:
        """
        Use trigram postings to collect likely candidates.
        Fall back to scanning if query is tiny or unseen.
        """
        if not self._loaded or not q_norm:
            return []
        grams = list(_trigrams(q_norm))
        if not grams:
            return []
        counts: Dict[int, int] = defaultdict(int)
        # collect posting hits
        for g in grams:
            for idx in self._gram_index.get(g, ()):
                counts[idx] += 1
        if not counts:
            # tiny/rare query: return a small random-like slice (but deterministic) to keep latency bounded
            # Prefer sentences that contain the first character at least
            first = q_norm[0]
            rough = [i for i, (_, _, _, s) in enumerate(self.items) if first in s]
            return rough[:cap]
        # rank by number of shared grams (desc), then by shorter normalized sentence
        ranked = sorted(counts.items(), key=lambda kv: (-kv[1], len(self.items[kv[0]][3])))
        return [idx for idx, _ in ranked[:cap]]