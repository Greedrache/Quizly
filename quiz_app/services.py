import yt_dlp
import whisper
import os
from dotenv import load_dotenv
from google import genai

load_dotenv('.env.template')
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
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
    Erstelle basierend auf dem folgenden Text ein Quiz. 
    Gib NUR pures JSON in diesem Format zurück (ohne Markdown ```json formatierung), 
    mit title, description und questions array. Jede Frage soll question_title, question_options (array mit 4 Optionen) und answer (die korrekte Option) haben.

    Text: {text}
    """

    response = client.models.generate_content(
        model="gemini-3-flash-preview", # Use a reliable and fast gemini model
        contents=prompt,
    )
    
    return response.text