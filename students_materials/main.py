import os
from text_data import TextDatabase
from autocomplete import AutoCompleter

def main():
    db = TextDatabase()
    # טען את מאגר הטקסטים (התיקייה Archive צריכה להיות ליד הקוד)
    db.load("Archive")

    ac = AutoCompleter(db)

    print("Type your query and press Enter (type 'exit' to quit")
    while True:
        q = input("query: ").strip()
        if q.lower() == "exit":
            break
        if not q:
            continue

        results = ac.get_best_k_completions(q)  
        if not results:
            print("(no matches)\n")
            continue

        for i, m in enumerate(results, 1):
            fname = os.path.basename(m.source_text)
            print(f"{i}. {m.score:>3}  {m.completed_sentence}  [File: {fname}, Line: {m.offset}]")
        print()

if __name__ == "__main__":
    main()
