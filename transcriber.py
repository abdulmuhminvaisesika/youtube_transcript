
import yt_dlp
import asyncio
import time
import os
from deepgram import Deepgram

AUDIO_FILE = "temp_audio.mp3"

def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': AUDIO_FILE,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }],
        'quiet': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
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

def get_transcript(url, api_key):
    download_audio(url)
    dg_client = Deepgram(api_key)  # Create Deepgram client dynamically
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    response = loop.run_until_complete(transcribe_audio(dg_client))
    transcript = format_transcript(response)
    
    # Remove temp audio file to clean up
    if os.path.exists(AUDIO_FILE):
        os.remove(AUDIO_FILE)
        
    return transcript
