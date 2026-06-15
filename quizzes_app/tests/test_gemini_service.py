"""Tests for the Gemini quiz generation service."""

import json
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from quizzes_app.services.gemini_service import generate_quiz_from_transcript


class GeminiServiceTests(SimpleTestCase):
    """Tests Gemini quiz generation without external API calls."""

    @override_settings(
        GEMINI_API_KEY='test-api-key',
        GEMINI_MODEL_NAME='gemini-2.5-flash',
    )
    @patch('quizzes_app.services.gemini_service.genai.Client')
    def test_generate_quiz_from_transcript_returns_quiz_data(
        self,
        mocked_client,
    ):
        """Ensures Gemini response text is parsed into quiz data."""

        transcript = 'Transcript text about artificial intelligence.'
        response = mocked_client.return_value.models.generate_content.return_value
        response.text = self.get_gemini_response_text()

        result = generate_quiz_from_transcript(transcript)

        mocked_client.assert_called_once_with(api_key='test-api-key')
        self.assert_generated_quiz_data(result)
        self.assert_gemini_generation_call(mocked_client, transcript)


    def assert_generated_quiz_data(self, result):
        """Ensures parsed Gemini quiz data has the expected structure."""

        self.assertEqual(result['title'], 'Quiz Title')
        self.assertEqual(result['description'], 'Quiz Description')
        self.assertEqual(len(result['questions']), 10)
        self.assertEqual(result['questions'][0]['answer'], 'Option A')


    def assert_gemini_generation_call(self, mocked_client, transcript):
        """Ensures Gemini is called with model and transcript prompt."""

        generate_content = mocked_client.return_value.models.generate_content
        call_kwargs = generate_content.call_args.kwargs

        self.assertEqual(call_kwargs['model'], 'gemini-2.5-flash')
        self.assertIn(transcript, call_kwargs['contents'])
        self.assertIn('exactly 10 questions', call_kwargs['contents'])


    def get_gemini_response_text(self, quiz_data=None):
        """Returns a mocked Gemini response with markdown fences."""

        if quiz_data is None:
            quiz_data = self.get_valid_quiz_data()

        return f'```json\n{json.dumps(quiz_data)}\n```'


    def get_valid_quiz_data(self):
        """Returns valid Gemini quiz data."""

        return {
            'title': 'Quiz Title',
            'description': 'Quiz Description',
            'questions': self.get_questions_data(),
        }


    def get_questions_data(self):
        """Returns ten generated question dictionaries."""

        questions = []

        for question_number in range(1, 11):
            questions.append(self.get_question_data(question_number))

        return questions


    def get_question_data(self, question_number):
        """Returns one generated question dictionary."""

        return {
            'question_title': f'Question {question_number}',
            'question_options': [
                'Option A',
                'Option B',
                'Option C',
                'Option D',
            ],
            'answer': 'Option A',
        }


    @override_settings(
        GEMINI_API_KEY='test-api-key',
        GEMINI_MODEL_NAME='gemini-2.5-flash',
    )
    @patch('quizzes_app.services.gemini_service.genai.Client')
    def test_generate_quiz_from_transcript_rejects_invalid_question_count(
        self,
        mocked_client,
    ):
        """Ensures Gemini quiz data must contain exactly ten questions."""

        transcript = 'Transcript text.'
        quiz_data = self.get_valid_quiz_data()
        quiz_data['questions'] = []

        response = mocked_client.return_value.models.generate_content.return_value
        response.text = self.get_gemini_response_text(quiz_data)

        with self.assertRaises(ValueError):
            generate_quiz_from_transcript(transcript)


    @override_settings(
        GEMINI_API_KEY='test-api-key',
        GEMINI_MODEL_NAME='gemini-2.5-flash',
    )
    @patch('quizzes_app.services.gemini_service.genai.Client')
    def test_generate_quiz_from_transcript_rejects_invalid_option_count(
        self,
        mocked_client,
    ):
        """Ensures each Gemini question must contain four options."""

        transcript = 'Transcript text.'
        quiz_data = self.get_valid_quiz_data()
        quiz_data['questions'][0]['question_options'] = ['Option A']

        response = mocked_client.return_value.models.generate_content.return_value
        response.text = self.get_gemini_response_text(quiz_data)

        with self.assertRaises(ValueError):
            generate_quiz_from_transcript(transcript)


    @override_settings(
        GEMINI_API_KEY='test-api-key',
        GEMINI_MODEL_NAME='gemini-2.5-flash',
    )
    @patch('quizzes_app.services.gemini_service.genai.Client')
    def test_generate_quiz_from_transcript_rejects_answer_outside_options(
        self,
        mocked_client,
    ):
        """Ensures the correct answer must exist in question options."""

        transcript = 'Transcript text.'
        quiz_data = self.get_valid_quiz_data()
        quiz_data['questions'][0]['answer'] = 'Invalid Answer'

        response = mocked_client.return_value.models.generate_content.return_value
        response.text = self.get_gemini_response_text(quiz_data)

        with self.assertRaises(ValueError):
            generate_quiz_from_transcript(transcript)


    @override_settings(
        GEMINI_API_KEY='test-api-key',
        GEMINI_MODEL_NAME='gemini-2.5-flash',
    )
    @patch('quizzes_app.services.gemini_service.genai.Client')
    def test_generate_quiz_from_transcript_rejects_missing_title(
        self,
        mocked_client,
    ):
        """Ensures generated quiz data must contain a title."""

        transcript = 'Transcript text.'
        quiz_data = self.get_valid_quiz_data()
        quiz_data['title'] = ''

        response = mocked_client.return_value.models.generate_content.return_value
        response.text = self.get_gemini_response_text(quiz_data)

        with self.assertRaises(ValueError):
            generate_quiz_from_transcript(transcript)


    @override_settings(
    GEMINI_API_KEY='test-api-key',
    GEMINI_MODEL_NAME='gemini-2.5-flash',
    )
    @patch('quizzes_app.services.gemini_service.genai.Client')
    def test_generate_quiz_from_transcript_rejects_missing_description(
        self,
        mocked_client,
    ):
        """Ensures generated quiz data must contain a description."""

        transcript = 'Transcript text.'
        quiz_data = self.get_valid_quiz_data()
        quiz_data['description'] = ''

        response = mocked_client.return_value.models.generate_content.return_value
        response.text = self.get_gemini_response_text(quiz_data)

        with self.assertRaises(ValueError):
            generate_quiz_from_transcript(transcript)


    @override_settings(
        GEMINI_API_KEY='test-api-key',
        GEMINI_MODEL_NAME='gemini-2.5-flash',
    )
    @patch('quizzes_app.services.gemini_service.genai.Client')
    def test_generate_quiz_from_transcript_rejects_non_list_options(
        self,
        mocked_client,
    ):
        """Ensures generated question options must be a list."""

        transcript = 'Transcript text.'
        quiz_data = self.get_valid_quiz_data()
        quiz_data['questions'][0]['question_options'] = 'abcd'

        response = mocked_client.return_value.models.generate_content.return_value
        response.text = self.get_gemini_response_text(quiz_data)

        with self.assertRaises(ValueError):
            generate_quiz_from_transcript(transcript)