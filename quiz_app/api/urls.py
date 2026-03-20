from django.urls import path
from .views import QuizzesView, SingleQuizView

urlpatterns = [
    path('quizzes/', QuizzesView.as_view(), name='quizzes'), # New registration endpoint
    path('quizzes/<int:pk>/', SingleQuizView.as_view(), name='quizzes_detail'), # Updated login endpoint to use the custom view that sets cookies
]