from typing import List, Tuple, Dict
from collections import defaultdict
import os
from trigram import _normalize, _trigrams

class TextDatabase:
    """
    Manages loading and indexing of text data from .txt files in a folder tree.
    Each line in the files is treated as a sentence, stored with metadata,
    and indexed by character trigrams for efficient candidate retrieval.
    """

    def __init__(self) -> None:
        self.items: List[Tuple[str, str, int, str]] = []
        self._gram_index: Dict[str, List[int]] = defaultdict(list)
        self._loaded = False

    def load(self, root_folder: str) -> None:
        """
        Recursively walks through the given folder, loads all .txt files,
        and indexes their lines as sentences.

        Args:
            root_folder (str): Path to the root folder containing .txt files.

        Process:
            - Clears existing data and index.
            - Opens each .txt file found.
            - Reads each line, normalizes it.
            - Stores tuple of (original line, file path, line number, normalized line).
            - Indexes each unique character trigram of the normalized line.
        """
        self.items.clear()
        self._gram_index.clear()
        files_num = 0
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
                        seen = set()
                        for g in _trigrams(norm):
                            if g not in seen:
                                self._gram_index[g].append(idx)
                                seen.add(g)
                files_num += 1
                print(f'loading {files_num}')
        self._loaded = True
        print(f'{files_num} txt files loaded')

    def __len__(self) -> int:
        return len(self.items)

    def candidates_by_query(self, q_norm: str, cap: int = 500) -> List[int]:
        """
        Given a normalized query string, retrieve a list of candidate sentence indices
        that share character trigrams with the query, ranked by number of shared trigrams
        and normalized sentence length.

        Args:
            q_norm (str): The normalized query string.
            cap (int, optional): Maximum number of candidates to return. Defaults to 500.

        Returns:
            List[int]: List of indices into `self.items` representing candidate sentences.
        """
        if not self._loaded or not q_norm:
            return []
        grams = list(_trigrams(q_norm))
        if not grams:
            return []
        counts: Dict[int, int] = defaultdict(int)
        for g in grams:
            for idx in self._gram_index.get(g, ()):
                counts[idx] += 1
        if not counts:
            first = q_norm[0]
            rough = [i for i, (_, _, _, s) in enumerate(self.items) if first in s]
            return rough[:cap]
        ranked = sorted(counts.items(), key=lambda kv: (-kv[1], len(self.items[kv[0]][3])))
        return [idx for idx, _ in ranked[:cap]]
