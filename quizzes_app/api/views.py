"""Views for quiz API endpoints."""

import logging

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from quizzes_app.api.serializers import (
     QuizCreateUrlSerializer, 
     QuizSerializer, 
     QuizUpdateSerializer,
)
from quizzes_app.api.utils import create_quiz_with_questions
from quizzes_app.models import Quiz
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


    def get(self, request):
        """Returns all quizzes owned by the authenticated user."""

        try:
            quizzes = Quiz.objects.filter(
                owner=request.user,
            ).prefetch_related('questions')
        except Exception:
            logger.exception('Unexpected error during quiz list retrieval.')

            return Response(
                {'detail': 'Internal server error.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        response_serializer = QuizSerializer(quizzes, many=True)

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )


class QuizDetailView(GenericAPIView):
    """Handles quiz retrieval, update and deletion."""

    permission_classes = [IsAuthenticated]
    serializer_class = QuizSerializer

    def get(self, request, pk):
        """Returns one quiz owned by the authenticated user."""

        try:
            quiz = Quiz.objects.get(pk=pk)
        except Quiz.DoesNotExist:
            return Response(
                {'detail': 'Not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception:
            logger.exception('Unexpected error during quiz detail retrieval.')

            return Response(
                {'detail': 'Internal server error.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if quiz.owner_id != request.user.id:
            return Response(
                {'detail': 'You do not have permission to access this quiz.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        response_serializer = QuizSerializer(quiz)

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )


    def patch(self, request, pk):
        """Partially updates one quiz owned by the authenticated user."""

        try:
            quiz = Quiz.objects.get(pk=pk)
        except Quiz.DoesNotExist:
            return Response(
                {'detail': 'Not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception:
            logger.exception('Unexpected error during quiz detail update.')

            return Response(
                {'detail': 'Internal server error.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if quiz.owner_id != request.user.id:
            return Response(
                {'detail': 'You do not have permission to update this quiz.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = QuizUpdateSerializer(quiz, data=request.data, partial=True,)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response_serializer = QuizSerializer(quiz)

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )


    def delete(self, request, pk):
        """Permanently deletes one quiz owned by the authenticated user."""

        try:
            quiz = Quiz.objects.get(pk=pk)
        except Quiz.DoesNotExist:
            return Response(
                {'detail': 'Not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception:
            logger.exception('Unexpected error during quiz detail deletion.')

            return Response(
                {'detail': 'Internal server error.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if quiz.owner_id != request.user.id:
            return Response(
                {'detail': 'You do not have permission to delete this quiz.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        quiz.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)