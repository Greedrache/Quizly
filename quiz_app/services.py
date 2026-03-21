import yt_dlp
import whisper
import os
from google import genai
from django.conf import settings

GEMINI_API_KEY = settings.GEMINI_API_KEY

def get_video_info(url):
    ydl_opts = {
        "quiet": True,
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return ydl.sanitize_info(info)

def process_video(url):
    """
    1. Downloads audio from YouTube
    2. Transcribes it with Whisper
    3. Returns the transcribed text
    """
    tmp_filename = "downloaded_audio.%(ext)s"
    
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": tmp_filename,
        "quiet": True,
        "noplaylist": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }

    # 1. Download audio
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    audio_file = "downloaded_audio.mp3"

    # 2. Transcribe
    model = whisper.load_model("base")
    result = model.transcribe(audio_file)
    text = result["text"]

    # Optional: Aufräumen (Audio-Datei löschen)
    if os.path.exists(audio_file):
        os.remove(audio_file)

    return text

def generate_quiz_from_transcript(text):
    """
    Uses Google GenAI to generate the quiz JSON from transcript
    """
    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = f"""
           Create a quiz based on the following text with EXACTLY 10 questions.
           Return ONLY pure JSON in this format (without Markdown ```json formatting),
           including a title, description, and a questions array. Each question should have
           a question_title, question_options (an array with 4 options), and answer (the correct option).

           Text: {text}
           """


    response = client.models.generate_content(
        model="gemini-3-flash-preview", # Use a reliable and fast gemini model
        contents=prompt,
    )
    
    return response.text