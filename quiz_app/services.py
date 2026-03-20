import yt_dlp

def get_video_info(url):
    ydl_opts = {
        "quiet": True,
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return ydl.sanitize_info(info)
    
tmp_filename = "audio.%(ext)s" # Temporary filename template for downloaded audio


ydl_opts = {
    "format": "bestaudio/best",
    "outtmpl": tmp_filename,
    "quiet": True,
    "noplaylist": True,
}



import whisper

model = whisper.load_model("base")  # tiny, base, small, medium, large

result = model.transcribe("audio.mp3")

print(result["text"])

# Example usage of the Google Gemini API
from google import genai

GEMINI_API_KEY = "AIzaSyA3Oss_txV7pfpwAPY0TVFJcOM1lXXdzkY"

client = genai.Client(api_key=GEMINI_API_KEY)

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="Explain how AI works in a few words",
)

print(response.text)