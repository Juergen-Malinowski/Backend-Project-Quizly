"""Reusable test helpers for quiz API tests."""

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework_simplejwt.tokens import RefreshToken

from quizzes_app.models import Quiz, QuizQuestion


class QuizTestMixin:
    """Provides shared helpers for quiz endpoint tests."""

    def get_quiz_list_create_url(self):
        """Returns the quiz list and create endpoint URL."""

        return reverse('quiz-list-create')


    def get_quiz_detail_url(self, quiz_id):
        """Returns the quiz detail endpoint URL."""

        return reverse('quiz-detail', kwargs={'pk': quiz_id})


    def create_test_user(self):
        """Creates a reusable test user."""

        return get_user_model().objects.create_user(
            username='test_user',
            email='test_user@example.com',
            password='SecurePass123!',
        )


    def create_other_test_user(self):
        """Creates another reusable test user."""

        return get_user_model().objects.create_user(
            username='other_user',
            email='other_user@example.com',
            password='SecurePass123!',
        )


    def authenticate_with_access_token_cookie(self):
        """Adds a valid access token cookie to the test client."""

        user = self.create_test_user()
        refresh = RefreshToken.for_user(user)
        self.client.cookies['access_token'] = str(refresh.access_token)

        return user


    def get_valid_quiz_create_data(self):
        """Returns valid quiz creation payload data."""

        return {
            'url': 'https://www.youtube.com/watch?v=example',
        }


    def get_generated_quiz_data(self):
        """Returns generated quiz data without external API calls."""

        return {
            'title': 'Quiz Title',
            'description': 'Quiz Description',
            'video_url': 'https://www.youtube.com/watch?v=example',
            'questions': self.get_generated_questions_data(),
        }


    def get_generated_questions_data(self):
        """Returns ten generated quiz questions with valid answer data."""

        questions = []

        for question_number in range(1, 11):
            question_options = [
                f'Question {question_number} Option A',
                f'Question {question_number} Option B',
                f'Question {question_number} Option C',
                f'Question {question_number} Option D',
            ]

            questions.append(
                {
                    'question_title': f'Question {question_number}',
                    'question_options': question_options,
                    'answer': question_options[0],
                },
            )

        return questions


    def create_quiz_with_questions(self, owner, title='Quiz Title'):
        """Creates a quiz with ten related questions."""

        quiz = Quiz.objects.create(
            owner=owner,
            title=title,
            description='Quiz Description',
            video_url='https://www.youtube.com/watch?v=example',
        )

        for position, question_data in enumerate(
            self.get_generated_questions_data(),
            start=1,
        ):
            QuizQuestion.objects.create(
                quiz=quiz,
                position=position,
                **question_data,
            )

        return quiz