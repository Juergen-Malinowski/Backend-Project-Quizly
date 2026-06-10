"""Quiz API routes for the Quizly backend."""


from django.urls import path

from quizzes_app.api.views import QuizDetailView, QuizListCreateView


urlpatterns = [
    path('quizzes/', QuizListCreateView.as_view(), name='quiz-list-create'),
    path('quizzes/<int:pk>/', QuizDetailView.as_view(), name='quiz-detail'),
]