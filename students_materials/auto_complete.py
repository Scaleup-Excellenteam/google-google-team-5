from dataclasses import dataclass

@dataclass
class AutoCompleteData:
    complete_sentence: str
    source_text: str
    offset: int
    source: int