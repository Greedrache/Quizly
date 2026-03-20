from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..services import process_video, generate_quiz_from_transcript
from .serializers import QuizSerializer, QuestionSerializer
from ..models import Quiz
from rest_framework import status
from django.http import Http404

class QuizzesView(APIView):
    """
    API view for handling quiz-related operations.
    This view allows authenticated users to retrieve a list of their quizzes (GET) and create new quizzes (POST) by providing a video URL.
    The view processes the video to generate quiz questions using AI and saves the quiz to the database with the current user as the author.
    The GET method retrieves only the quizzes that belong to the currently authenticated user, ensuring that users can only access their own quizzes.
    The POST method expects a video URL in the request data, processes the video to extract text, generates quiz questions using an AI function, and saves the quiz along with its questions to the database.
    It also handles various error cases such as missing URL, AI response parsing errors, and validation errors when saving the quiz.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Handle GET requests to retrieve a list of quizzes for the authenticated user.
        This method queries the database for quizzes that are associated with the currently authenticated user (using the 'author' field) and returns them in the response.
        It uses the QuizSerializer to convert the quiz instances into JSON format for the API response."""
        quizzes = Quiz.objects.filter(author=request.user)
        # many=True da es sich um eine Liste handelt
        serializer = QuizSerializer(quizzes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Handle POST requests to create a new quiz from a provided video URL.
        This method expects a 'url' field in the request data, which should contain the URL of the video to process. 
        It uses the process_video function to extract text from the video and the generate_quiz_from_transcript function to create quiz questions based on the extracted text.
        The generated quiz data is then validated and saved to the database with the current user set as the author.
        The method also includes error handling for cases such as missing URL, AI response parsing errors, and validation errors when saving the quiz.
        """
        url = request.data.get("url")

        if not url:
            return Response({"error": "No URL provided"}, status=400)

        text = process_video(url)

        ki_result_str = generate_quiz_from_transcript(text) 
        
        import json
        import re
        
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
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SingleQuizView(APIView):
    """
    API view for handling operations on a single quiz instance.
    This view allows authenticated users to retrieve (GET), update (PATCH), or delete (DELETE) a specific quiz by its ID (pk).
    The view ensures that users can only access and modify their own quizzes by filtering the quiz based on the authenticated user.
    The GET method retrieves the quiz details, the PATCH method allows for partial updates to the quiz (such as updating the title), and the DELETE method removes the quiz from the database.
    Each method includes error handling to ensure that users cannot access or modify quizzes that do not belong to them, and that appropriate responses are returned for invalid requests.
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        """
        Helper method to retrieve a quiz instance by its ID (pk) and the authenticated user.
        This method attempts to retrieve a quiz from the database that matches the provided ID and is associated
        with the authenticated user (using the 'author' field). If such a quiz exists, it is returned; otherwise, a 404 error is raised to indicate that the quiz was not found or does not belong to the user.
        """
        try:
            # Stellt sicher, dass das Quiz existiert UND dem eingeloggten User gehört
            return Quiz.objects.get(pk=pk, author=user)
        except Quiz.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        """
        Handle GET requests to retrieve details of a specific quiz instance.
        This method retrieves the quiz instance based on the provided ID (pk) and the authenticated user to ensure that users can only access their own quizzes. It then uses the QuizSerializer to convert the quiz instance into JSON format for the API response. If the quiz does not exist or does not belong to the user, it raises a 404 error.
        """
        quiz = self.get_object(pk, request.user)
        serializer = QuizSerializer(quiz)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        """
        Handle PATCH requests to update a specific quiz instance.
        This method retrieves the quiz instance based on the provided ID (pk) and the authenticated user to ensure that users can only update their own quizzes. It then uses the QuizSerializer to validate and apply the partial updates to the quiz instance.
        If the quiz is successfully updated, it returns the updated quiz data in the response. If the quiz does not exist or does not belong to the user, it raises a 404 error. If the provided data is invalid, it returns a 400 error with details about the validation errors.
        """
        quiz = self.get_object(pk, request.user)
        serializer = QuizSerializer(quiz, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Handle DELETE requests to remove a specific quiz instance.
        This method retrieves the quiz instance based on the provided ID (pk) and the authenticated user to ensure that users can only delete their own quizzes. If the quiz exists and belongs to the user, it is deleted from the database. If the quiz does not exist or does not belong to the user, it raises a 404 error.
        """
        quiz = self.get_object(pk, request.user)
        quiz.delete()
        return Response({"detail": "Quiz deleted deleted successfully."}, status=status.HTTP_204_NO_CONTENT)