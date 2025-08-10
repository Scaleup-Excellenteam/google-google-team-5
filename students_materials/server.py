from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Flask Server is running!"

@app.route('/api/data', methods=['GET'])
def get_data():
    data = {
        "message": "This is sample data",
        "status": "success"
    }
    return jsonify(data)

@app.route('/api/echo', methods=['POST'])
def echo():
    json_data = request.json
    return jsonify({
        "you_sent": json_data
    })

if __name__ == '__main__':
    app.run(debug=True)
