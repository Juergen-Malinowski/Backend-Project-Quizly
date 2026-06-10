from django.conf import settings

from django.db import models


class Quiz(models.Model):
    """Stores a generated quiz for one authenticated user."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quizzes',
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    video_url = models.URLField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Defines default ordering for quizzes."""

        ordering = ['-created_at']
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quizze'

    def __str__(self):
        """Returns the quiz title for admin and shell output."""

        return self.title


class QuizQuestion(models.Model):
    """Stores one question and its answer options for a quiz."""

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions',
    )

    question_title = models.TextField()
    question_options = models.JSONField()
    answer = models.TextField()
    position = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Defines question ordering and unique positions per quiz."""

        ordering = ['position']
        verbose_name = 'Quizfrage'
        verbose_name_plural = 'Quizfragen'

        constraints = [
            models.UniqueConstraint(
                fields=['quiz', 'position'],
                name='unique_question_position_per_quiz',
            ),
        ]

    def __str__(self):
        """Returns a readable question label for admin and shell output."""

        return f'{self.position}. {self.question_title}'