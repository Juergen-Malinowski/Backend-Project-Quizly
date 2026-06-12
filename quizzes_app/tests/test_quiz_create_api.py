"""Tests for the quiz creation API endpoint."""

from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APITestCase

from quizzes_app.models import Quiz, QuizQuestion
from quizzes_app.tests.mixins import QuizTestMixin


class QuizCreateApiTests(QuizTestMixin, APITestCase):
    """Tests quiz creation endpoint behavior."""

    @patch('quizzes_app.api.views.generate_quiz_from_youtube_url')
    def test_quiz_create_returns_created_quiz_with_questions(self, mocked_generation):
        """Ensures authenticated users can create a quiz with questions."""

        user = self.authenticate_with_access_token_cookie()
        mocked_generation.return_value = self.get_generated_quiz_data()

        response = self.client.post(
            self.get_quiz_list_create_url(),
            self.get_valid_quiz_create_data(),
            format='json',
        )

        self.assert_quiz_response_data(response)
        self.assert_quiz_questions_response_data(response.data['questions'])
        self.assert_quiz_database_state(user)


    def assert_quiz_response_data(self, response):
        """Ensures the created quiz response contains expected data."""

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIn('created_at', response.data)
        self.assertIn('updated_at', response.data)
        self.assertIn('questions', response.data)
        self.assertEqual(response.data['title'], 'Quiz Title')
        self.assertEqual(response.data['description'], 'Quiz Description')
        self.assertEqual(
            response.data['video_url'],
            'https://www.youtube.com/watch?v=example',
        )


    def assert_quiz_questions_response_data(self, questions):
        """Ensures the created quiz response contains valid questions."""

        self.assertEqual(len(questions), 10)

        for question in questions:
            self.assertIn('id', question)
            self.assertIn('question_title', question)
            self.assertIn('question_options', question)
            self.assertIn('answer', question)
            self.assertIn('created_at', question)
            self.assertIn('updated_at', question)
            self.assertEqual(len(question['question_options']), 4)
            self.assertIn(question['answer'], question['question_options'])


    def assert_quiz_database_state(self, user):
        """Ensures quiz and question records were stored correctly."""

        self.assertEqual(Quiz.objects.count(), 1)
        self.assertEqual(QuizQuestion.objects.count(), 10)
        self.assertEqual(Quiz.objects.first().owner, user)


    def test_quiz_create_fails_without_authentication(self):
        """Ensures unauthenticated users cannot create quizzes."""

        response = self.client.post(
            self.get_quiz_list_create_url(),
            self.get_valid_quiz_create_data(),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Quiz.objects.count(), 0)
        self.assertEqual(QuizQuestion.objects.count(), 0)


    def test_quiz_create_fails_with_missing_url(self):
        """Ensures missing URL data is rejected."""

        self.authenticate_with_access_token_cookie()

        response = self.client.post(
            self.get_quiz_list_create_url(),
            {},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Quiz.objects.count(), 0)
        self.assertEqual(QuizQuestion.objects.count(), 0)


    def test_quiz_create_fails_with_invalid_url(self):
        """Ensures invalid URL data is rejected."""

        self.authenticate_with_access_token_cookie()

        response = self.client.post(
            self.get_quiz_list_create_url(),
            {'url': 'not-a-valid-url'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Quiz.objects.count(), 0)
        self.assertEqual(QuizQuestion.objects.count(), 0)


    @patch('quizzes_app.api.views.generate_quiz_from_youtube_url')
    def test_quiz_create_returns_500_on_unexpected_error(self, mocked_generation):
        """Ensures unexpected quiz creation errors return status 500."""

        self.authenticate_with_access_token_cookie()
        mocked_generation.side_effect = Exception('Unexpected error')

        response = self.client.post(
            self.get_quiz_list_create_url(),
            self.get_valid_quiz_create_data(),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(Quiz.objects.count(), 0)
        self.assertEqual(QuizQuestion.objects.count(), 0)