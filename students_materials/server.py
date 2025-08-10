from flask import Flask, jsonify, request, render_template
from text_data import load_texts, search

app = Flask(__name__)

# load files before server runnig
load_texts('Archive')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search')
def search_api():
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

if __name__ == '__main__':
    app.run(debug=True)
