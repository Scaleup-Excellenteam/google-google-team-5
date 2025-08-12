from typing import List, Tuple, Dict
from collections import defaultdict
import os
import pickle
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


    def _load_pickle(self, pickle_path: str) -> bool:
        """
        Try to load the database from a pickle file.
        Returns True if successful, False otherwise.
        """
        if not os.path.exists(pickle_path):
            return False
        try:
            with open(pickle_path, "rb") as f:
                data = pickle.load(f)
            self.items = data["items"]
            self._gram_index = data["gram_index"]
            self._loaded = True
            print(f"Loaded database from pickle cache: {pickle_path}")
            return True
        except (pickle.UnpicklingError, EOFError, KeyError, Exception) as e:
            print(f"[WARN] Failed to load pickle cache '{pickle_path}': {e}")
            return False

    def _save_pickle(self, pickle_path: str) -> None:
        """
        Save the database to a pickle file.
        """
        try:
            with open(pickle_path, "wb") as f:
                pickle.dump({
                    "items": self.items,
                    "gram_index": self._gram_index
                }, f)
            print(f"Saved database pickle cache: {pickle_path}")
        except Exception as e:
            print(f"[WARN] Failed to save pickle cache '{pickle_path}': {e}")

    def load(self, root_folder: str) -> None:
        """
        Load database from pickle cache if available,
        otherwise load recursively from text files and save pickle.

        Args:
            root_folder (str): Path to the root folder containing .txt files.

        Process:
            - Clears existing data and index.
            - Opens each .txt file found.
            - Reads each line, normalizes it.
            - Stores tuple of (original line, file path, line number, normalized line).
            - Indexes each unique character trigram of the normalized line.
        """

        pickle_path = os.path.join(os.path.dirname(__file__), "cache.pkl")
        if self._load_pickle(pickle_path):
            self._loaded = True
            return  # loaded successfully


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
                        original = line.strip()
                        if not original:
                            continue
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

        self._save_pickle(pickle_path)
        self._loaded = True
        

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
