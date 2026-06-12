"""Tests for the quiz detail delete API endpoint."""

from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APITestCase

from quizzes_app.models import Quiz, QuizQuestion
from quizzes_app.tests.mixins import QuizTestMixin


class QuizDetailDeleteApiTests(QuizTestMixin, APITestCase):
    """Tests quiz detail delete endpoint behavior."""

    def test_quiz_detail_delete_removes_authenticated_users_quiz(self):
        """Ensures users can permanently delete their own quiz."""

        user = self.authenticate_with_access_token_cookie()
        quiz = self.create_quiz_with_questions(user)

        response = self.client.delete(self.get_quiz_detail_url(quiz.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b'')
        self.assertFalse(Quiz.objects.filter(id=quiz.id).exists())
        self.assertEqual(QuizQuestion.objects.count(), 0)


    def test_quiz_detail_delete_fails_without_authentication(self):
        """Ensures unauthenticated users cannot delete quiz details."""

        user = self.create_test_user()
        quiz = self.create_quiz_with_questions(user)

        response = self.client.delete(self.get_quiz_detail_url(quiz.id))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Quiz.objects.filter(id=quiz.id).exists())
        self.assertEqual(QuizQuestion.objects.count(), 10)


    def test_quiz_detail_delete_fails_for_other_users_quiz(self):
        """Ensures users cannot delete quizzes owned by another user."""

        self.authenticate_with_access_token_cookie()
        other_user = self.create_other_test_user()
        other_quiz = self.create_quiz_with_questions(other_user)

        response = self.client.delete(self.get_quiz_detail_url(other_quiz.id))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Quiz.objects.filter(id=other_quiz.id).exists())
        self.assertEqual(QuizQuestion.objects.count(), 10)


    def test_quiz_detail_delete_fails_for_missing_quiz(self):
        """Ensures missing quizzes return status 404 on delete."""

        self.authenticate_with_access_token_cookie()

        response = self.client.delete(self.get_quiz_detail_url(9999))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    @patch('quizzes_app.api.views.Quiz.objects.get')
    def test_quiz_detail_delete_returns_500_on_unexpected_error(self, mocked_get):
        """Ensures unexpected quiz delete errors return status 500."""

        self.authenticate_with_access_token_cookie()
        mocked_get.side_effect = Exception('Unexpected error')

        response = self.client.delete(self.get_quiz_detail_url(1))

        self.assertEqual(
            response.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )