from rest_framework.views import APIView
from rest_framework.response import Response
from ..services import process_video, generate_quiz_from_transcript
from .serializers import QuizSerializer, QuestionSerializer
from rest_framework import status

class TranscribeView(APIView):
    def post(self, request):
        url = request.data.get("url")

        if not url:
            return Response({"error": "No URL provided"}, status=400)

        text = process_video(url)

        # Pseudo-Code:
        ki_result = generate_quiz_from_transcript(text) # Deine KI-Funktion
        
        serializer_data = {
            "video_url": url,
            "title": ki_result["title"],
            "description": ki_result["description"],
            "questions": ki_result["questions"] # Eine Liste von Dictionaries
        }
        serializer = QuizSerializer(data=serializer_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)