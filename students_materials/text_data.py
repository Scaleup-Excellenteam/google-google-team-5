import os
import re

class TextSearcher:
    def __init__(self):
        # אחסון גלובלי של משפטים
        self.records = []  # list of dicts: {original, normalized, file_path, line_number}

    # ---------- Normalize ----------
    @staticmethod
    def normalize(text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^\w\s]", " ", text)   # הסרת פיסוק
        text = re.sub(r"\s+", " ", text)       # איחוד רווחים
        return text.strip()

    # ---------- Load all text files ----------
    def load_texts(self, folder_path: str):
        """Load all .txt files from folder_path recursively into records."""
        self.records.clear()
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(".txt"):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line_number, line in enumerate(f, start=1):
                            line = line.strip()
                            if not line:
                                continue
                            self.records.append({
                                "original": line,
                                "normalized": self.normalize(line),
                                "file_path": file_path,
                                "line_number": line_number
                            })
        print(f"✅ Loaded {len(self.records)} sentences from {folder_path}")

    # ---------- Search ----------
    def search(self, query: str, limit: int = 5):
        """Search for query in the loaded records and return top matches."""
        q_norm = self.normalize(query)
        matches = [r for r in self.records if q_norm in r["normalized"]]
        return matches[:limit]

# ----------- Demo -----------
if __name__ == "__main__":
    ts = TextSearcher()
    
    folder = os.path.join('Archive')
    if not os.path.exists(folder):
        print(f"❌ Folder not found: {folder}")
        exit(1)

    ts.load_texts(folder)

    while True:
        q = input("\nSearch (or 'exit'): ").strip()
        if q.lower() == "exit":
            break
        results = ts.search(q)
        if not results:
            print("No matches found.")
        else:
            print("\nSearch results:")
            for idx, r in enumerate(results, start=1):
                file_name = os.path.basename(r["file_path"])
                print(f"{idx}. {r['original']}  [File: {file_name}, Line: {r['line_number']}]")
