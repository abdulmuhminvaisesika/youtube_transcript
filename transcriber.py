import yt_dlp
import asyncio
import time
import os
import uuid
from deepgram import Deepgram

def download_audio(url, filename_base):
    print(f"Downloading audio to {filename_base} ...")
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': filename_base,  # yt-dlp will add the .mp3 extension automatically
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }],
        'verbose': True,
        'quiet': False,  # Show logs for debugging
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'cookiefile': 'cookies.txt',  # Use browser cookies only
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    print("Download completed.")

async def transcribe_audio(dg_client, filename):
    with open(filename, 'rb') as audio:
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
    # Generate unique filename base (no extension)
    temp_audio_file_base = str(uuid.uuid4())

    # Download audio (yt-dlp will add .mp3)
    download_audio(url, temp_audio_file_base)

    # Construct full filename with .mp3 extension
    temp_audio_file = temp_audio_file_base + ".mp3"

    # Verify the audio file exists
    if not os.path.exists(temp_audio_file):
        raise FileNotFoundError(f"Audio file '{temp_audio_file}' was not created. Download may have failed.")

    dg_client = Deepgram(api_key)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    response = loop.run_until_complete(transcribe_audio(dg_client, temp_audio_file))

    transcript = format_transcript(response)

    # Clean up temporary file
    try:
        os.remove(temp_audio_file)
        print(f"Deleted temporary audio file: {temp_audio_file}")
    except Exception as e:
        print(f"Warning: Could not delete temporary file {temp_audio_file}: {e}")

    return transcript
