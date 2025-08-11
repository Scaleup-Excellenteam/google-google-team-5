# main.py
import os
from text_data import TextDatabase
from autocomplete import AutoCompleter

def main():
    db = TextDatabase()
    root = os.environ.get("AC_ARCHIVE", "Archive")
    db.load(root)
    ac = AutoCompleter(db)
    print("Type your query and press Enter.")
    print("Type 'exit' to quit.")
    while True:
        q = input("query: ").strip()

        if not q:
            continue
        if q.lower() == "exit":
            break
        results = ac.get_best_k_completions(q, k=5)
        if not results:
            print("No matches.")
            continue

        for i, m in enumerate(results, 1):
            fname = os.path.basename(m.source_text)
            print(f"{i:>2}. {m.score:>3}  {m.completed_sentence}  [File: {fname}, Line: {m.offset}]")

if __name__ == "__main__":
    main()