"""Tests for the Whisper transcription service."""

from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from quizzes_app.services.whisper_service import transcribe_audio_file


class WhisperServiceTests(SimpleTestCase):
    """Tests Whisper transcription without loading a real model."""

    @override_settings(WHISPER_MODEL_NAME='base')
    @patch('quizzes_app.services.whisper_service.whisper.load_model')
    def test_transcribe_audio_file_returns_transcript_text(
        self,
        mocked_load_model,
    ):
        """Ensures Whisper transcription returns the transcript text."""

        audio_file_path = 'tmp/quiz_audio/example.webm'
        whisper_model = mocked_load_model.return_value
        whisper_model.transcribe.return_value = {
            'text': 'Generated transcript text.',
        }

        result = transcribe_audio_file(audio_file_path)

        self.assertEqual(result, 'Generated transcript text.')
        mocked_load_model.assert_called_once_with('base')
        whisper_model.transcribe.assert_called_once_with(audio_file_path)