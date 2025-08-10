import os 
import re 

# ----------- Global storage for sentences -----------
records = []  # list of dicts: {original, normalized, file_path, line_number}

# ----------- Helper: normalize a sentence -----------
def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)   # remove punctuation
    text = re.sub(r"\s+", " ", text)       # collapse spaces
    return text.strip()

# ----------- Load all text files -----------
def load_texts(folder_path: str):
    """Load all .txt files from folder_path recursively into records."""
    records.clear()
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".txt"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line_number, line in enumerate(f, start=1):
                        line = line.strip()
                        if not line:
                            continue
                        records.append({
                            "original": line,
                            "normalized": normalize(line),
                            "file_path": file_path,
                            "line_number": line_number
                        })
    print(f"✅ Loaded {len(records)} sentences from {folder_path}")

# ----------- Search for a query -----------
def search(query: str, limit: int = 5):
    """Search for query in the loaded records and return top matches."""
    q_norm = normalize(query)
    matches = [r for r in records if q_norm in r["normalized"]]
    return matches[:limit]

# ----------- Demo -----------
if __name__ == "__main__":
    folder = input("Enter folder path with .txt files: ").strip()
    load_texts(folder)

    while True:
        q = input("\nSearch (or 'exit'): ").strip()
        if q.lower() == "exit":
            break
        results = search(q)
        if not results:
            print("No matches found.")
        else:
            print("\nSearch results:")
            for idx, r in enumerate(results, start=1):
                file_name = os.path.basename(r["file_path"])
                print(f"{idx}. {r['original']}  [File: {file_name}, Line: {r['line_number']}]")
