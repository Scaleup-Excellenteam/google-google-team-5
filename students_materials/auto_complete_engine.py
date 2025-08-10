from typing import List

class AutoCompleteEngine:
    def __init__(self):
        self.data = []  # List of AutoCompleteData objects

    def initialize(self, sources: List[List[str]]):
        # Build the list of AutoCompleteData from the sources
        # Simple example: each sentence gets basic info assigned
        self.data = []
        for source_idx, source in enumerate(sources):
            for offset, sentence in enumerate(source):
                item = AutoCompleteData(
                    complete_sentence=sentence,
                    source_text="\n".join(source),  # Or another relevant source text
                    offset=offset,
                    source=source_idx
                )
                self.data.append(item)

    def get_best_k_completions(self, prefix: str, k=5) -> List[AutoCompleteData]:
        prefix = prefix.lower()
        # Find all sentences that start with the prefix (case insensitive)
        matches = [item for item in self.data if item.complete_sentence.lower().startswith(prefix)]
        # Return up to k matches
        return matches[:k]
