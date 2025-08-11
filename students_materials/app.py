from flask import Flask, jsonify, request, render_template
import threading
from text_data import TextDatabase
from autocomplete import AutoCompleter

app = Flask(__name__)

db = None
ac = None
data_loaded = False


def load_data_thread():
    global db, ac, data_loaded
    db = TextDatabase()
    db.load("Archive")
    ac = AutoCompleter(db)
    data_loaded = True


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/search')
def search_api():
    global ac, data_loaded
    if not data_loaded:
        return jsonify({"error": "Data is still loading"}), 503

    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])

    results = ac.get_best_k_completions(query)
    output = []
    for r in results:
        output.append({
            "completed_sentence": r.completed_sentence,
            "file": r.source_text.split("/")[-1],
            "line": r.offset,
            "score": r.score
        })
    return jsonify(output)


@app.route('/status')
def status():
    return jsonify({"loaded": data_loaded})


if __name__ == '__main__':
    thread = threading.Thread(target=load_data_thread)
    thread.start()
    app.run(debug=True)
