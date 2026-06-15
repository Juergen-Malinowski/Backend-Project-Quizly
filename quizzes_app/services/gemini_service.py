"""Service functions for Gemini quiz generation."""

import json

from django.conf import settings
from google import genai


QUIZ_GENERATION_PROMPT = """
Based on the following transcript, generate a quiz in valid JSON format.

The quiz must follow this exact structure:

{{
  "title": "Create a concise quiz title based on the topic of the transcript.",
  "description": "Summarize the transcript in no more than 150 characters.",
  "questions": [
    {{
      "question_title": "The question goes here.",
      "question_options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "The correct answer from the above options"
    }}
  ]
}}

Requirements:
- Each question must have exactly 4 distinct answer options.
- Only one correct answer is allowed per question.
- The correct answer must be present in question_options.
- Generate exactly 10 questions.
- Do not include explanations, comments, or text outside the JSON.

Transcript:
{transcript}
""".strip()


def generate_quiz_from_transcript(transcript):
    """Generates quiz data from a transcript using Gemini."""

    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    response = client.models.generate_content(
        model=settings.GEMINI_MODEL_NAME,
        contents=QUIZ_GENERATION_PROMPT.format(transcript=transcript),
    )

    return parse_gemini_response(response.text)


def parse_gemini_response(response_text):
    """Parses and validates Gemini response text into quiz data."""

    cleaned_response = remove_markdown_fences(response_text)
    quiz_data = json.loads(cleaned_response)

    validate_generated_quiz_data(quiz_data)

    return quiz_data


def validate_generated_quiz_data(quiz_data):
    """Validates the generated quiz data structure."""

    questions = quiz_data.get('questions', [])

    if not quiz_data.get('title'):
        raise ValueError('Generated quiz title is missing.')

    if not quiz_data.get('description'):
        raise ValueError('Generated quiz description is missing.')

    if not isinstance(questions, list) or len(questions) != 10:
        raise ValueError('Generated quiz must contain exactly 10 questions.')

    for question_data in questions:
        validate_generated_question_data(question_data)


def validate_generated_question_data(question_data):
    """Validates one generated question data structure."""

    question_options = question_data.get('question_options', [])

    if not isinstance(question_options, list) or len(question_options) != 4:
        raise ValueError('Generated question must contain exactly 4 options.')

    if question_data.get('answer') not in question_options:
        raise ValueError('Generated answer must exist in question options.')


def remove_markdown_fences(response_text):
    """Removes optional markdown fences from Gemini response text."""

    cleaned_response = response_text.strip()

    if cleaned_response.startswith('```json'):
        cleaned_response = cleaned_response.removeprefix('```json').strip()

    if cleaned_response.startswith('```'):
        cleaned_response = cleaned_response.removeprefix('```').strip()

    if cleaned_response.endswith('```'):
        cleaned_response = cleaned_response.removesuffix('```').strip()

    return cleaned_response