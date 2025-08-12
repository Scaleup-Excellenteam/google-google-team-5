from dataclasses import dataclass
from typing import Iterable
import re
import string

_PUNC_SET = set(string.punctuation)

def _normalize(s: str) -> str:
    """
    Normalize the input string by lowercasing all characters,
    replacing punctuation characters with spaces,
    collapsing multiple spaces into a single space,
    and stripping leading and trailing whitespace.

    Args:
        s (str): The input string to normalize.

    Returns:
        str: The normalized string.
    """
    s = ''.join((ch.lower() if ch not in _PUNC_SET else ' ') for ch in s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def _trigrams(s: str) -> Iterable[str]:
    """
    Generate overlapping character trigrams (3-character sequences) from the input string.
    If the string length is less than 3, yields the entire string as a single trigram.

    Args:
        s (str): The input string from which to generate trigrams.

    Yields:
        str: Each trigram substring from the input string.
    """
    if len(s) < 3:
        if s:
            yield s
        return
    for i in range(len(s) - 2):
        yield s[i:i+3]

@dataclass
class AutoCompleteData:
    completed_sentence: str
    source_text: str
    offset: int
    score: int
