"""Views for quiz API endpoints."""

import logging

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from quizzes_app.api.serializers import QuizCreateUrlSerializer, QuizSerializer
from quizzes_app.api.utils import create_quiz_with_questions
from quizzes_app.services.quiz_generation_service import generate_quiz_from_youtube_url


logger = logging.getLogger(__name__)


class QuizListCreateView(GenericAPIView):
    """Handles quiz creation and quiz list retrieval."""

    permission_classes = [IsAuthenticated]
    serializer_class = QuizCreateUrlSerializer

    def post(self, request):
        """Creates a generated quiz from a YouTube URL."""

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            generated_data = generate_quiz_from_youtube_url(
                serializer.validated_data['url'],
            )
            quiz = create_quiz_with_questions(request.user, generated_data)
        except Exception:
            logger.exception('Unexpected error during quiz creation.')

            return Response(
                {'detail': 'Internal server error.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        response_serializer = QuizSerializer(quiz)

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class QuizDetailView(GenericAPIView):
    """Handles quiz retrieval, update and deletion."""
    pass