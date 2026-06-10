from django.contrib import admin

from quizzes_app.models import Quiz, QuizQuestion


class QuizQuestionInline(admin.TabularInline):
    """Allows editing quiz questions inside the related quiz admin page."""

    model = QuizQuestion
    extra = 0
    fields = (
        'position',
        'question_title',
        'question_options',
        'answer',
    )


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    """Admin configuration for generated quizzes."""

    list_display = (
        'title',
        'owner',
        'video_url',
        'created_at',
        'updated_at',
    )

    search_fields = (
        'title',
        'description',
        'video_url',
        'owner__username',
        'owner__email',
    )

    list_filter = (
        'created_at',
        'updated_at',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    inlines = [
        QuizQuestionInline,
    ]


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    """Admin configuration for generated quiz questions."""

    list_display = (
        'quiz',
        'position',
        'question_title',
        'answer',
        'created_at',
    )

    search_fields = (
        'quiz__title',
        'question_title',
        'answer',
    )

    list_filter = (
        'quiz',
        'created_at',
        'updated_at',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )