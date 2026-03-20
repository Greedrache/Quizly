from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..services import process_video, generate_quiz_from_transcript
from .serializers import QuizSerializer, QuestionSerializer
from ..models import Quiz
from rest_framework import status
from django.http import Http404

class QuizzesView(APIView):
    # Nur eingeloggte User dürfen auf diese View zugreifen
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Alle Quizzes aus der DB abrufen
        quizzes = Quiz.objects.all()
        # many=True da es sich um eine Liste handelt
        serializer = QuizSerializer(quizzes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        url = request.data.get("url")

        if not url:
            return Response({"error": "No URL provided"}, status=400)

        text = process_video(url)

        # KI-Ergebnis generieren
        ki_result_str = generate_quiz_from_transcript(text) # Deine KI-Funktion
        
        # Das Ergebnis ist ein JSON-String, dieses müssen wir noch in Python-Daten umwandeln
        import json
        import re
        
        # Manchmal hängt die KI trotzdem Blockquotes an ("```json ... ```"), die müssen wir filtern
        clean_json_str = ki_result_str.strip()
        if clean_json_str.startswith("```"):
            clean_json_str = re.sub(r"^```(json)?|```$", "", clean_json_str).strip()

        try:
            ki_result = json.loads(clean_json_str)
        except json.JSONDecodeError as e:
            return Response({"error": f"Failed to parse AI response: {str(e)}", "ai_raw_response": ki_result_str}, status=500)
            
        serializer_data = {
            "video_url": url,
            "title": ki_result.get("title", ""),
            "description": ki_result.get("description", ""),
            "questions": ki_result.get("questions", [])
        }
        serializer = QuizSerializer(data=serializer_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SingleQuizView(APIView):
    # Nur eingeloggte User dürfen auch einzelne Quizzes sehen/ändern/löschen
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Quiz.objects.get(pk=pk)
        except Quiz.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        quiz = self.get_object(pk)
        serializer = QuizSerializer(quiz)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        quiz = self.get_object(pk)
        # partial=True erlaubt es, nur bestimmte Felder (wie nur den "title") zu updaten
        serializer = QuizSerializer(quiz, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        quiz = self.get_object(pk)
        quiz.delete()
        return Response({"detail": "Quiz deleted deleted successfully."}, status=status.HTTP_204_NO_CONTENT)