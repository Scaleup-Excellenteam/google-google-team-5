from flask import Flask, jsonify, request, render_template
import threading
import time
from text_data import load_texts, search

app = Flask(__name__)

data_loaded = False

def load_data_thread():
    global data_loaded
    load_texts('Archive')
    data_loaded = True

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search')
def search_api():
    global data_loaded
    if not data_loaded:
        return jsonify({"error": "Data is still loading"}), 503

    query = request.args.get('q', '')
    if not query:
        return jsonify([])

    results = search(query)
    output = []
    for r in results:
        output.append({
            "original": r["original"],
            "file": r["file_path"].split("/")[-1],
            "line": r["line_number"]
        })
    return jsonify(output)

@app.route('/status')
def status():
    return jsonify({"loaded": data_loaded})

if __name__ == '__main__':
    thread = threading.Thread(target=load_data_thread)
    thread.start()

    app.run(debug=True)