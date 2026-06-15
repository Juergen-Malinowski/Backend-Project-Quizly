"""Service functions for YouTube audio handling."""

from django.conf import settings

import yt_dlp


def create_audio_file_from_youtube_url(url):
    """Creates a temporary audio file from a YouTube URL."""

    settings.QUIZ_AUDIO_TEMP_DIR.mkdir(parents=True, exist_ok=True)

    ydl_options = {
        'format': 'bestaudio/best',
        'outtmpl': str(settings.QUIZ_AUDIO_TEMP_DIR / '%(id)s.%(ext)s'),
        'quiet': True,
        'noplaylist': True,
    }

    with yt_dlp.YoutubeDL(ydl_options) as ydl:
        video_info = ydl.extract_info(url, download=True)

        return ydl.prepare_filename(video_info)