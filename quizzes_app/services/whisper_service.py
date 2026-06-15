"""Service functions for Whisper audio transcription."""

import whisper

from django.conf import settings


def transcribe_audio_file(audio_file_path):
    """Transcribes an audio file and returns the transcript."""

    model = whisper.load_model(settings.WHISPER_MODEL_NAME)
    result = model.transcribe(audio_file_path)

    return result['text']