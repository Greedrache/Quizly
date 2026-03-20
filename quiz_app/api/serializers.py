from rest_framework import serializers
from ..models import Quiz, Question


class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Question model.
    This serializer converts Question model instances to and from JSON format for API responses and requests.
    It includes fields for the question title, options, answer, and timestamps.
    The question_options field is expected to be a list of options for the quiz question.
    """
    class Meta:
        model = Question
        fields = ['id', 'question_title', 'question_options', 'answer', 'created_at', 'updated_at']


class QuizSerializer(serializers.ModelSerializer):
    """
    Serializer for the Quiz model.
    This serializer converts Quiz model instances to and from JSON format for API responses and requests.
    It includes fields for the quiz title, description, video URL, and associated questions.
    The questions field is a nested serializer that allows for the inclusion of related Question instances when creating or retrieving a Quiz.
    The create method is overridden to handle the creation of related Question instances when a new Quiz is created through the API."""
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'created_at', 'updated_at', 'video_url', 'questions']

    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        quiz = Quiz.objects.create(**validated_data)
        for question_data in questions_data:
            Question.objects.create(quiz=quiz, **question_data)
        return quiz