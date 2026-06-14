"""Serializers for quiz API endpoints."""

from urllib.parse import urlparse

from rest_framework import serializers

from quizzes_app.models import Quiz, QuizQuestion


class QuizCreateUrlSerializer(serializers.Serializer):
    """Validates the YouTube URL for quiz creation."""

    url = serializers.URLField()

    def validate_url(self, value):
        """Validates that the submitted URL is a YouTube URL."""

        if not self.is_youtube_url(value):
            raise serializers.ValidationError('Enter a valid YouTube URL.')

        return value


    def is_youtube_url(self, url):
        """Checks whether the URL belongs to YouTube."""

        hostname = urlparse(url).hostname or ''
        valid_hostnames = (
            'youtube.com',
            'www.youtube.com',
            'm.youtube.com',
            'youtu.be',
        )

        return hostname in valid_hostnames


class QuizQuestionSerializer(serializers.ModelSerializer):
    """Serializes generated quiz questions."""

    class Meta:
        """Defines serialized quiz question fields."""

        model = QuizQuestion
        fields = (
            'id',
            'question_title',
            'question_options',
            'answer',
            'created_at',
            'updated_at',
        )


class QuizSerializer(serializers.ModelSerializer):
    """Serializes generated quizzes with related questions."""

    questions = QuizQuestionSerializer(many=True, read_only=True)

    class Meta:
        """Defines serialized quiz fields."""

        model = Quiz
        fields = (
            'id',
            'title',
            'description',
            'created_at',
            'updated_at',
            'video_url',
            'questions',
        )