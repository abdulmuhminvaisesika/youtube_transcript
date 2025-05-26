from flask import Flask, request, jsonify
from deepgram import Deepgram
import yt_dlp
import asyncio
import time

app = Flask(__name__)

AUDIO_FILE = "temp_audio.mp3"

def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': AUDIO_FILE,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }]
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

async def transcribe_audio(dg_client):
    with open(AUDIO_FILE, 'rb') as audio:
        source = {'buffer': audio, 'mimetype': 'audio/mp3'}
        response = await dg_client.transcription.prerecorded(source, {
            'punctuate': True,
            'paragraphs': True,
            'utterances': True,
        })
    return response

def format_transcript(response):
    formatted = ""
    for u in response["results"]["utterances"]:
        start = time.strftime('%M:%S', time.gmtime(u["start"]))
        text = u["transcript"]
        formatted += f"{start}\n{text}\n\n"
    return formatted

@app.route('/transcribe', methods=['POST'])
def transcribe():
    data = request.json
    if not data or 'url' not in data:
        return jsonify({"error": "Missing 'url' in request body"}), 400
    
    url = data['url']

    # Read the Authorization header
    auth_header = request.headers.get('Authorization', None)
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Missing or invalid Authorization header"}), 401

    api_key = auth_header.split(' ')[1]  # Extract the token after 'Bearer '

    try:
        download_audio(url)

        dg_client = Deepgram(api_key)  # Create client dynamically using provided key

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(transcribe_audio(dg_client))

        transcript = format_transcript(response)
        return jsonify({"transcript": transcript})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
