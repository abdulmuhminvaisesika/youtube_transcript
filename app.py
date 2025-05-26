from flask import Flask, request, jsonify
from transcriber import get_transcript
app = Flask(__name__)

@app.route('/')
def home():
    return "YouTube Transcript API is running!"

@app.route('/transcribe', methods=['POST'])
def transcribe():
    data = request.json
    if not data or 'url' not in data:
        return jsonify({"error": "Missing 'url' in request body"}), 400
    
    url = data['url']

    auth_header = request.headers.get('Authorization', None)
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Missing or invalid Authorization header"}), 401

    api_key = auth_header.split(' ')[1]  # Extract the API key

    try:
        transcript = get_transcript(url, api_key)
        return jsonify({"transcript": transcript})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
