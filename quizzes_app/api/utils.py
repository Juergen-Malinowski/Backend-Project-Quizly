"""Utility functions for quiz API endpoints."""

from django.db import transaction

from quizzes_app.models import Quiz, QuizQuestion


@transaction.atomic
def create_quiz_with_questions(owner, generated_quiz_data):
    """Creates a quiz with all generated questions."""

    quiz = create_quiz(owner, generated_quiz_data)
    create_question_records(quiz, generated_quiz_data['questions'])

    return quiz


def create_quiz(owner, generated_quiz_data):
    """Creates the quiz base record."""

    return Quiz.objects.create(
        owner=owner,
        title=generated_quiz_data['title'],
        description=generated_quiz_data['description'],
        video_url=generated_quiz_data['video_url'],
    )


def create_question_records(quiz, questions_data):
    """Creates generated question records for a quiz."""

    for position, question_data in enumerate(questions_data, start=1):
        QuizQuestion.objects.create(
            quiz=quiz,
            position=position,
            **question_data,
        )