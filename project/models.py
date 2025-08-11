"""
Data classes for autocomplete matches and results.
"""

from dataclasses import dataclass

@dataclass
class Match:
    """
    Represents a candidate match with score and source metadata.
    """
    score: int
    file_path: str
    line_num: int
    original: str

@dataclass
class AutoCompleteData:
    """
    Represents an autocomplete result returned to the user.
    """
    completed_sentence: str
    source_text: str
    offset: int
    score: int
