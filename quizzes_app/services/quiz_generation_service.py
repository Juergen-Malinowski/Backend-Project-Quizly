"""Service entry point for generated quizzes from YouTube URLs."""

from quizzes_app.services.gemini_service import generate_quiz_from_transcript
from quizzes_app.services.whisper_service import transcribe_audio_file
from quizzes_app.services.youtube_service import create_audio_file_from_youtube_url


def generate_quiz_from_youtube_url(url):
    """Generates complete quiz data from a YouTube URL."""

    audio_file_path = create_audio_file_from_youtube_url(url)
    transcript = transcribe_audio_file(audio_file_path)
    generated_quiz_data = generate_quiz_from_transcript(transcript)

    return add_video_url_to_quiz_data(generated_quiz_data, url)


def add_video_url_to_quiz_data(generated_quiz_data, url):
    """Adds the original video URL to generated quiz data."""

    quiz_data = generated_quiz_data.copy()
    quiz_data['video_url'] = url

    return quiz_data