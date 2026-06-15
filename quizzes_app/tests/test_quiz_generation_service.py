"""Tests for the quiz generation service."""

from unittest.mock import patch

from django.test import SimpleTestCase

from quizzes_app.services.quiz_generation_service import generate_quiz_from_youtube_url


class QuizGenerationServiceTests(SimpleTestCase):
    """Tests the internal quiz generation service pipeline."""

    @patch('quizzes_app.services.quiz_generation_service.generate_quiz_from_transcript')
    @patch('quizzes_app.services.quiz_generation_service.transcribe_audio_file')
    @patch('quizzes_app.services.quiz_generation_service.create_audio_file_from_youtube_url')
    def test_generate_quiz_from_youtube_url_returns_complete_quiz_data(
        self,
        mocked_audio_creation,
        mocked_transcription,
        mocked_quiz_generation,
    ):
        """Ensures quiz generation returns complete quiz data."""

        url = 'https://www.youtube.com/watch?v=example'
        audio_file_path = 'tmp/audio-file.mp3'
        transcript = 'Generated transcript text.'

        self.configure_generation_mocks(
            mocked_audio_creation,
            mocked_transcription,
            mocked_quiz_generation,
            audio_file_path,
            transcript,
        )

        result = generate_quiz_from_youtube_url(url)

        self.assert_generated_quiz_data(result, url)
        self.assert_generation_pipeline_calls(
            mocked_audio_creation,
            mocked_transcription,
            mocked_quiz_generation,
            url,
            audio_file_path,
            transcript,
        )


    def configure_generation_mocks(
        self,
        mocked_audio_creation,
        mocked_transcription,
        mocked_quiz_generation,
        audio_file_path,
        transcript,
    ):
        """Configures mocked service return values."""

        mocked_audio_creation.return_value = audio_file_path
        mocked_transcription.return_value = transcript
        mocked_quiz_generation.return_value = self.get_generated_ai_quiz_data()


    def assert_generated_quiz_data(self, result, url):
        """Ensures the generated service result is complete."""

        self.assertEqual(result['title'], 'Quiz Title')
        self.assertEqual(result['description'], 'Quiz Description')
        self.assertEqual(result['video_url'], url)
        self.assertEqual(len(result['questions']), 10)


    def assert_generation_pipeline_calls(
        self,
        mocked_audio_creation,
        mocked_transcription,
        mocked_quiz_generation,
        url,
        audio_file_path,
        transcript,
    ):
        """Ensures all generation services were called correctly."""

        mocked_audio_creation.assert_called_once_with(url)
        mocked_transcription.assert_called_once_with(audio_file_path)
        mocked_quiz_generation.assert_called_once_with(transcript)


    def get_generated_ai_quiz_data(self):
        """Returns valid AI quiz data without a video URL."""

        return {
            'title': 'Quiz Title',
            'description': 'Quiz Description',
            'questions': self.get_generated_questions_data(),
        }


    def get_generated_questions_data(self):
        """Returns ten generated quiz questions."""

        questions = []

        for question_number in range(1, 11):
            questions.append(self.get_generated_question_data(question_number))

        return questions


    def get_generated_question_data(self, question_number):
        """Returns one generated quiz question."""

        question_options = [
            f'Question {question_number} Option A',
            f'Question {question_number} Option B',
            f'Question {question_number} Option C',
            f'Question {question_number} Option D',
        ]

        return {
            'question_title': f'Question {question_number}',
            'question_options': question_options,
            'answer': question_options[0],
        }


    @patch('quizzes_app.services.quiz_generation_service.Path')
    @patch('quizzes_app.services.quiz_generation_service.generate_quiz_from_transcript')
    @patch('quizzes_app.services.quiz_generation_service.transcribe_audio_file')
    @patch('quizzes_app.services.quiz_generation_service.create_audio_file_from_youtube_url')
    def test_generate_quiz_from_youtube_url_removes_temporary_audio_file(
        self,
        mocked_audio_creation,
        mocked_transcription,
        mocked_quiz_generation,
        mocked_path,
    ):
        """Ensures temporary audio files are removed after generation."""

        url = 'https://www.youtube.com/watch?v=example'
        audio_file_path = 'tmp/audio-file.webm'
        transcript = 'Generated transcript text.'

        self.configure_generation_mocks(
            mocked_audio_creation,
            mocked_transcription,
            mocked_quiz_generation,
            audio_file_path,
            transcript,
        )

        generate_quiz_from_youtube_url(url)

        mocked_path.assert_called_once_with(audio_file_path)
        mocked_path.return_value.unlink.assert_called_once_with(missing_ok=True)


    @patch('quizzes_app.services.quiz_generation_service.Path')
    @patch('quizzes_app.services.quiz_generation_service.generate_quiz_from_transcript')
    @patch('quizzes_app.services.quiz_generation_service.transcribe_audio_file')
    @patch('quizzes_app.services.quiz_generation_service.create_audio_file_from_youtube_url')
    def test_generate_quiz_from_youtube_url_removes_audio_file_on_error(
        self,
        mocked_audio_creation,
        mocked_transcription,
        mocked_quiz_generation,
        mocked_path,
    ):
        """Ensures temporary audio files are removed when generation fails."""

        url = 'https://www.youtube.com/watch?v=example'
        audio_file_path = 'tmp/audio-file.webm'
        mocked_audio_creation.return_value = audio_file_path
        mocked_transcription.return_value = 'Generated transcript text.'
        mocked_quiz_generation.side_effect = ValueError('Invalid quiz data.')

        with self.assertRaises(ValueError):
            generate_quiz_from_youtube_url(url)

        mocked_path.assert_called_once_with(audio_file_path)
        mocked_path.return_value.unlink.assert_called_once_with(missing_ok=True)