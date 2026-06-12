"""Tests for the quiz detail retrieve API endpoint."""

from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APITestCase

from quizzes_app.tests.mixins import QuizTestMixin


class QuizDetailRetrieveApiTests(QuizTestMixin, APITestCase):
    """Tests quiz detail retrieve endpoint behavior."""

    def test_quiz_detail_returns_authenticated_users_quiz(self):
        """Ensures users can retrieve their own quiz with nested questions."""

        user = self.authenticate_with_access_token_cookie()
        quiz = self.create_quiz_with_questions(user)

        response = self.client.get(self.get_quiz_detail_url(quiz.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], quiz.id)

        self.assert_quiz_detail_data(response.data)


    def assert_quiz_detail_data(self, quiz_data):
        """Asserts that quiz detail data matches the documented structure."""

        self.assertIn('id', quiz_data)
        self.assertIn('title', quiz_data)
        self.assertIn('description', quiz_data)
        self.assertIn('created_at', quiz_data)
        self.assertIn('updated_at', quiz_data)
        self.assertIn('video_url', quiz_data)
        self.assertIn('questions', quiz_data)
        self.assertEqual(quiz_data['title'], 'Quiz Title')
        self.assertEqual(quiz_data['description'], 'Quiz Description')
        self.assertEqual(
            quiz_data['video_url'],
            'https://www.youtube.com/watch?v=example',
        )
        self.assertEqual(len(quiz_data['questions']), 10)

        self.assert_quiz_detail_questions_data(quiz_data['questions'])


    def assert_quiz_detail_questions_data(self, questions):
        """Asserts that quiz detail questions match the documented structure."""

        for question in questions:
            self.assertIn('id', question)
            self.assertIn('question_title', question)
            self.assertIn('question_options', question)
            self.assertIn('answer', question)
            self.assertEqual(len(question['question_options']), 4)
            self.assertIn(question['answer'], question['question_options'])


    def test_quiz_detail_fails_without_authentication(self):
        """Ensures unauthenticated users cannot retrieve quiz details."""

        user = self.create_test_user()
        quiz = self.create_quiz_with_questions(user)

        response = self.client.get(self.get_quiz_detail_url(quiz.id))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_quiz_detail_fails_for_other_users_quiz(self):
        """Ensures users cannot retrieve quizzes owned by another user."""

        self.authenticate_with_access_token_cookie()
        other_user = self.create_other_test_user()
        other_quiz = self.create_quiz_with_questions(other_user)

        response = self.client.get(self.get_quiz_detail_url(other_quiz.id))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_quiz_detail_fails_for_missing_quiz(self):
        """Ensures missing quizzes return status 404."""

        self.authenticate_with_access_token_cookie()

        response = self.client.get(self.get_quiz_detail_url(9999))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    @patch('quizzes_app.api.views.Quiz.objects.get')
    def test_quiz_detail_returns_500_on_unexpected_error(self, mocked_get):
        """Ensures unexpected quiz detail errors return status 500."""

        self.authenticate_with_access_token_cookie()
        mocked_get.side_effect = Exception('Unexpected error')

        response = self.client.get(self.get_quiz_detail_url(1))

        self.assertEqual(
            response.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )