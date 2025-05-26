from transcriber import get_transcript

# Put your actual Deepgram API key here for testing
API_KEY = "7159bfaba2c41c0fa5ea666060336e19f9fe8705"

# YouTube video URL to test
url = "https://www.youtube.com/watch?v=e3MX7HoGXug"

transcript = get_transcript(url, API_KEY)
print(transcript)
