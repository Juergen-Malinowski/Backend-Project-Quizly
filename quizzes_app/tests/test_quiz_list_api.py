"""Tests for the quiz list API endpoint."""

from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APITestCase

from quizzes_app.tests.mixins import QuizTestMixin


class QuizListApiTests(QuizTestMixin, APITestCase):
    """Tests quiz list endpoint behavior."""

    def test_quiz_list_returns_authenticated_users_quizzes(self):
        """Ensures users receive only their own quizzes with nested questions."""

        user = self.authenticate_with_access_token_cookie()
        own_quiz = self.create_quiz_with_questions(user)
        other_user = self.create_other_test_user()
        self.create_quiz_with_questions(other_user, title='Other Quiz')

        response = self.client.get(self.get_quiz_list_create_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], own_quiz.id)

        self.assert_quiz_list_item_data(response.data[0])


    def assert_quiz_list_item_data(self, quiz_data):
        """Asserts that one listed quiz item matches the documented structure."""

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

        self.assert_quiz_list_questions_data(quiz_data['questions'])


    def assert_quiz_list_questions_data(self, questions):
        """Asserts that listed quiz questions match the documented structure."""

        for question in questions:
            self.assertIn('id', question)
            self.assertIn('question_title', question)
            self.assertIn('question_options', question)
            self.assertIn('answer', question)
            self.assertEqual(len(question['question_options']), 4)
            self.assertIn(question['answer'], question['question_options'])


    def test_quiz_list_fails_without_authentication(self):
        """Ensures unauthenticated users cannot list quizzes."""

        response = self.client.get(self.get_quiz_list_create_url())

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    @patch('quizzes_app.api.views.Quiz.objects.filter')
    def test_quiz_list_returns_500_on_unexpected_error(self, mocked_filter):
        """Ensures unexpected quiz list errors return status 500."""

        self.authenticate_with_access_token_cookie()
        mocked_filter.side_effect = Exception('Unexpected error')

        response = self.client.get(self.get_quiz_list_create_url())

        self.assertEqual(
            response.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )