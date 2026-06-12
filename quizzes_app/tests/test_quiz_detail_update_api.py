"""Tests for the quiz detail update API endpoint."""

from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APITestCase

from quizzes_app.tests.mixins import QuizTestMixin


class QuizDetailUpdateApiTests(QuizTestMixin, APITestCase):
    """Tests quiz detail update endpoint behavior."""

    def test_quiz_detail_patch_updates_authenticated_users_quiz(self):
        """Ensures users can partially update their own quiz."""

        user = self.authenticate_with_access_token_cookie()
        quiz = self.create_quiz_with_questions(user)

        response = self.client.patch(
            self.get_quiz_detail_url(quiz.id),
            {'title': 'Partially Updated Title'},
            format='json',
        )

        quiz.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], quiz.id)
        self.assertEqual(response.data['title'], 'Partially Updated Title')
        self.assertEqual(response.data['description'], 'Quiz Description')
        self.assertEqual(quiz.title, 'Partially Updated Title')
        self.assertEqual(quiz.description, 'Quiz Description')

        self.assert_quiz_update_response_data(response.data)


    def assert_quiz_update_response_data(self, quiz_data):
        """Asserts that updated quiz data matches the documented structure."""

        self.assertIn('id', quiz_data)
        self.assertIn('title', quiz_data)
        self.assertIn('description', quiz_data)
        self.assertIn('created_at', quiz_data)
        self.assertIn('updated_at', quiz_data)
        self.assertIn('video_url', quiz_data)
        self.assertIn('questions', quiz_data)
        self.assertEqual(
            quiz_data['video_url'],
            'https://www.youtube.com/watch?v=example',
        )
        self.assertEqual(len(quiz_data['questions']), 10)

        self.assert_quiz_update_questions_data(quiz_data['questions'])


    def assert_quiz_update_questions_data(self, questions):
        """Asserts that updated quiz questions match the documented structure."""

        for question in questions:
            self.assertIn('id', question)
            self.assertIn('question_title', question)
            self.assertIn('question_options', question)
            self.assertIn('answer', question)
            self.assertEqual(len(question['question_options']), 4)
            self.assertIn(question['answer'], question['question_options'])


    def test_quiz_detail_patch_fails_with_invalid_data(self):
        """Ensures invalid update data is rejected."""

        user = self.authenticate_with_access_token_cookie()
        quiz = self.create_quiz_with_questions(user)

        response = self.client.patch(
            self.get_quiz_detail_url(quiz.id),
            {'title': ''},
            format='json',
        )

        quiz.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(quiz.title, 'Quiz Title')


    def test_quiz_detail_patch_fails_without_authentication(self):
        """Ensures unauthenticated users cannot update quiz details."""

        user = self.create_test_user()
        quiz = self.create_quiz_with_questions(user)

        response = self.client.patch(
            self.get_quiz_detail_url(quiz.id),
            {'title': 'Partially Updated Title'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_quiz_detail_patch_fails_for_other_users_quiz(self):
        """Ensures users cannot update quizzes owned by another user."""

        self.authenticate_with_access_token_cookie()
        other_user = self.create_other_test_user()
        other_quiz = self.create_quiz_with_questions(other_user)

        response = self.client.patch(
            self.get_quiz_detail_url(other_quiz.id),
            {'title': 'Partially Updated Title'},
            format='json',
        )

        other_quiz.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(other_quiz.title, 'Quiz Title')


    def test_quiz_detail_patch_fails_for_missing_quiz(self):
        """Ensures missing quizzes return status 404 on update."""

        self.authenticate_with_access_token_cookie()

        response = self.client.patch(
            self.get_quiz_detail_url(9999),
            {'title': 'Partially Updated Title'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    @patch('quizzes_app.api.views.Quiz.objects.get')
    def test_quiz_detail_patch_returns_500_on_unexpected_error(self, mocked_get):
        """Ensures unexpected quiz update errors return status 500."""

        self.authenticate_with_access_token_cookie()
        mocked_get.side_effect = Exception('Unexpected error')

        response = self.client.patch(
            self.get_quiz_detail_url(1),
            {'title': 'Partially Updated Title'},
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )