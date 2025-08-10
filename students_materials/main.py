# main.py (או בתוך autocomplete.py בבלוק __main__)
from text_data import TextDatabase
from autocomplete import AutoCompleter

db = TextDatabase()
db.load("Archive")
ac = AutoCompleter(db)

while True:
    q = input("query: ").strip()
    if q == "exit": break
    for i, m in enumerate(ac.completion_function(q), 1):
        print(i, m.score, m.completed_sentence)
