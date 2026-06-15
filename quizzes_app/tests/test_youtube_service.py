"""Tests for the YouTube audio service."""

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from quizzes_app.services.youtube_service import create_audio_file_from_youtube_url


class YouTubeServiceTests(SimpleTestCase):
    """Tests YouTube audio handling without external downloads."""

    @patch('quizzes_app.services.youtube_service.yt_dlp.YoutubeDL')
    def test_create_audio_file_from_youtube_url_returns_audio_file_path(
        self,
        mocked_youtube_dl,
    ):
        """Ensures YouTube audio creation returns the prepared file path."""

        url = 'https://www.youtube.com/watch?v=example'

        with TemporaryDirectory() as temp_directory:
            audio_temp_dir = Path(temp_directory)
            expected_file_path = str(audio_temp_dir / 'example.webm')

            self.configure_youtube_dl_mock(
                mocked_youtube_dl,
                expected_file_path,
            )

            with override_settings(QUIZ_AUDIO_TEMP_DIR=audio_temp_dir):
                result = create_audio_file_from_youtube_url(url)

        self.assertEqual(result, expected_file_path)


    @patch('quizzes_app.services.youtube_service.yt_dlp.YoutubeDL')
    def test_create_audio_file_from_youtube_url_uses_expected_ydl_options(
        self,
        mocked_youtube_dl,
    ):
        """Ensures yt_dlp is configured with expected audio options."""

        url = 'https://www.youtube.com/watch?v=example'

        with TemporaryDirectory() as temp_directory:
            audio_temp_dir = Path(temp_directory)
            expected_template = str(audio_temp_dir / '%(id)s.%(ext)s')

            self.configure_youtube_dl_mock(
                mocked_youtube_dl,
                str(audio_temp_dir / 'example.webm'),
            )

            with override_settings(QUIZ_AUDIO_TEMP_DIR=audio_temp_dir):
                create_audio_file_from_youtube_url(url)

        ydl_options = mocked_youtube_dl.call_args[0][0]

        self.assertEqual(ydl_options['format'], 'bestaudio/best')
        self.assertEqual(ydl_options['outtmpl'], expected_template)
        self.assertTrue(ydl_options['quiet'])
        self.assertTrue(ydl_options['noplaylist'])


    @patch('quizzes_app.services.youtube_service.yt_dlp.YoutubeDL')
    def test_create_audio_file_from_youtube_url_downloads_single_video(
        self,
        mocked_youtube_dl,
    ):
        """Ensures yt_dlp downloads metadata and audio for one URL."""

        url = 'https://www.youtube.com/watch?v=example'

        with TemporaryDirectory() as temp_directory:
            self.configure_youtube_dl_mock(
                mocked_youtube_dl,
                str(Path(temp_directory) / 'example.webm'),
            )

            with override_settings(QUIZ_AUDIO_TEMP_DIR=Path(temp_directory)):
                create_audio_file_from_youtube_url(url)

        youtube_dl_instance = mocked_youtube_dl.return_value.__enter__.return_value
        youtube_dl_instance.extract_info.assert_called_once_with(
            url,
            download=True,
        )


    def configure_youtube_dl_mock(self, mocked_youtube_dl, expected_file_path):
        """Configures the mocked yt_dlp downloader."""

        youtube_dl_instance = mocked_youtube_dl.return_value.__enter__.return_value
        youtube_dl_instance.extract_info.return_value = {
            'id': 'example',
            'ext': 'webm',
        }
        youtube_dl_instance.prepare_filename.return_value = expected_file_path