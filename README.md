# Quizly Backend

Quizly Backend is a Django REST Framework backend for the provided Quizly frontend.

The backend will provide JWT authentication with HttpOnly cookies and quiz generation from YouTube URLs.

## Setup

Run the following commands to set up the project locally.

```bash
# Clone repository
git clone <your-backend-repository-url>

# Open backend folder
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Activate virtual environment (Linux / Mac)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create local environment file (Windows)
copy .env.template .env

# Create local environment file (Linux / Mac)
cp .env.template .env

# Generate a Django SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Insert SECRET_KEY into .env

# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

## Table of Contents

- [External Requirements](#external-requirements)
  - [Python AI and video dependencies](#python-ai-and-video-dependencies)
  - [Install FFmpeg on Windows](#install-ffmpeg-on-windows)
  - [Install FFmpeg on macOS](#install-ffmpeg-on-macos)
- [Project Structure](#project-structure)
- [Database Models](#database-models)
  - [Django User Model](#django-user-model)
  - [Quiz Model](#quiz-model)
  - [QuizQuestion Model](#quizquestion-model)
- [Django Admin](#django-admin)
  - [Quiz Admin](#quiz-admin)
  - [QuizQuestion Admin](#quizquestion-admin)
- [Testing](#testing)
  - [Test Structure](#test-structure)
  - [Tested Apps](#tested-apps)
  - [Test File Locations](#test-file-locations)
    - [auth_app](#auth_app)
    - [quizzes_app](#quizzes_app)
  - [Running Tests](#running-tests)
  - [Current Test Counts - 43 Tests](#current-test-counts---43-tests)
- [Current Implementation Status](#current-implementation-status)

## External Requirements

FFmpeg must be installed globally because Whisper requires it for audio processing.

### Python AI and video dependencies

The backend uses the following Python packages for quiz generation:

- `yt-dlp` for reading YouTube metadata and downloading audio
- `openai-whisper` for local audio transcription
- `google-genai` for Gemini Flash quiz generation

### Install FFmpeg on Windows

```bash
winget install --id Gyan.FFmpeg -e --source winget
```

### Install FFmpeg on macOS

```bash
brew install ffmpeg
```

## Project Structure

```txt
project_quizly/
├── backend/
│   ├── auth_app/
│   │   ├── api/
│   │   └── tests/
│   ├── core/
│   ├── quizzes_app/
│   │   ├── api/
│   │   ├── migrations/
│   │   ├── services/
│   │   └── tests/
│   ├── manage.py
│   ├── pytest.ini
│   ├── requirements.txt
│   ├── .env.template
│   └── README.md
└── frontend/
```

The frontend and backend are separated projects. The provided frontend communicates with this backend through a REST API.

## Database Models

### Django User Model

Purpose:

- provides the default authentication user model
- stores login-relevant user data
- is used as the owner relation for generated quizzes
- is used for JWT authentication with HttpOnly cookies

Fields used by Quizly:

- id
- username
- email
- password

Additional notes:

- Quizly uses Django's default user model
- no custom user model is currently required
- email uniqueness is handled during registration validation
- users can only access their own quizzes

### Quiz Model

Purpose:

- stores generated quizzes created by authenticated users
- stores the normalized YouTube URL used for quiz generation
- stores editable quiz metadata such as title and description
- groups all related quiz questions

Fields:

- owner (ForeignKey → User)
- title
- description
- video_url
- created_at
- updated_at

Important behavior:

- each quiz belongs to exactly one user
- users can only retrieve, update and delete their own quizzes
- deleting a user deletes all quizzes owned by that user
- newest quizzes are ordered first by default

Admin integration:

- Quiz objects must be editable through the Django admin
- related QuizQuestion objects should be manageable inside the related Quiz admin page through Django admin inlines

### QuizQuestion Model

Purpose:

- stores generated questions for a quiz
- stores the answer options for each question
- stores the correct answer
- preserves the question order inside a quiz

Fields:

- quiz (ForeignKey → Quiz)
- question_title
- question_options
- answer
- position
- created_at
- updated_at

Important behavior:

- each question belongs to exactly one quiz
- deleting a quiz deletes all related questions
- question_options stores the answer options as JSON data
- each question must provide exactly four answer options
- the correct answer must be present in question_options
- questions are ordered by position

Constraints:

- each quiz can contain only one question per position

Admin integration:

- QuizQuestion objects must be editable through the Django admin
- QuizQuestion objects should be manageable directly inside the related Quiz admin page through Django admin inlines

## Django Admin

The Django admin is configured for managing Quizly's database content during development and review.

Admin areas currently available:

- Django users
- Django groups
- quiz management
- JWT token blacklist data

### Quiz Admin

Purpose:

- allows staff users to view and manage generated quizzes
- displays quiz ownership, title, video URL and timestamps
- supports searching by title, description, video URL, username and email
- supports filtering by creation and update timestamps

Related objects:

- QuizQuestion objects are editable directly inside the related Quiz admin page through Django admin inlines

### QuizQuestion Admin

Purpose:

- allows staff users to view and manage generated quiz questions
- displays the related quiz, question position, question title, answer and creation timestamp
- supports searching by quiz title, question title and answer
- supports filtering by quiz, creation timestamp and update timestamp

Admin naming:

- the quiz app is displayed as `Quizverwaltung`
- the quiz model is displayed as `Quiz` / `Quizze`
- the quiz question model is displayed as `Quizfrage` / `Quizfragen`

## Testing

This project follows a strong test-driven development (TDD) approach.

Quizly uses `pytest` and `pytest-django` for endpoint-based backend tests.

The pytest configuration is stored in `pytest.ini`.

The goal of the testing architecture is to validate backend behavior before endpoint implementation is completed. Each endpoint receives dedicated API tests to verify authentication, permissions, validation behavior, ownership rules, JWT cookie behavior, token blacklist behavior, nested response structures and expected HTTP responses.

### Test Structure

The test suite is organized by app and endpoint responsibility.

Each endpoint has its own dedicated test file to keep tests isolated, maintainable and easier to debug.

Reusable setup logic is extracted into `mixins.py` files where appropriate.

Example structure:

```txt
app_name/tests/
├── mixins.py
├── test_endpoint_create_api.py
├── test_endpoint_list_api.py
├── test_endpoint_detail_retrieve_api.py
├── test_endpoint_detail_update_api.py
└── test_endpoint_detail_delete_api.py
```

### Tested Apps

The following apps currently contain dedicated API test coverage:

- `auth_app`
- `quizzes_app`

### Test File Locations

#### auth_app

```txt
auth_app/tests/
├── mixins.py
├── test_login_api.py
├── test_logout_api.py
├── test_registration_api.py
└── test_token_refresh_api.py
```

#### quizzes_app

```txt
quizzes_app/tests/
├── mixins.py
├── test_quiz_create_api.py
├── test_quiz_detail_delete_api.py
├── test_quiz_detail_retrieve_api.py
├── test_quiz_detail_update_api.py
└── test_quiz_list_api.py
```

### Running Tests

Run all tests:

```bash
pytest
```

Run tests for a specific app:

```bash
pytest auth_app/tests/
```

```bash
pytest quizzes_app/tests/
```

Run a single endpoint test file:

```bash
pytest quizzes_app/tests/test_quiz_create_api.py
```

Run a single test method:

```bash
pytest quizzes_app/tests/test_quiz_create_api.py::QuizCreateApiTests::test_quiz_create_returns_created_quiz_with_questions
```

This allows every endpoint test suite to be executed independently during development and debugging.

### Current Test Counts - 43 Tests

| App           | Test Count |
| ------------- | ---------: |
| `auth_app`    |         19 |
| `quizzes_app` |         24 |
| **Total**     |     **43** |

## Current Implementation Status

The backend project currently includes the basic Django and Django REST Framework structure.

Implemented so far:

- Django project `core`
- authentication app `auth_app`
- quiz management app `quizzes_app`
- API folder structure for both apps
- service folder structure for YouTube, Whisper, Gemini and quiz generation logic
- test folder structure for endpoint-based TDD
- environment-based settings for `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` and CORS origins
- basic API routing skeleton
- `Quiz` model for generated user quizzes
- `QuizQuestion` model for generated quiz questions
- initial database migrations for quiz models
- Django admin configuration for `Quiz`
- Django admin configuration for `QuizQuestion`
- inline editing of quiz questions inside the related quiz admin page
- German admin labels for quiz-related admin sections
- installed Python dependencies for YouTube metadata handling, audio transcription and Gemini integration
- updated `requirements.txt` after installing AI and video processing dependencies
- pytest configuration with `pytest.ini`
- pytest-based authentication endpoint tests
- registration endpoint tests for success, validation errors and internal errors
- login endpoint tests for success, invalid credentials, HttpOnly cookies and internal errors
- logout endpoint tests for cookie deletion, refresh token blacklisting, unauthorized access and internal errors
- token refresh endpoint tests for new access cookies, missing refresh tokens, invalid refresh tokens and internal errors
- quiz create endpoint tests for success, authentication, validation errors and internal errors
- quiz list endpoint tests for authenticated user-specific quiz retrieval, unauthorized access and internal errors
- quiz detail retrieve endpoint tests for success, ownership checks, missing quizzes, unauthorized access and internal errors
- quiz detail update endpoint tests for partial updates, validation errors, ownership checks, missing quizzes, unauthorized access and internal errors
- quiz detail delete endpoint tests for permanent deletion, ownership checks, missing quizzes, unauthorized access and internal errors
- quiz endpoint tests verifying nested question response structures
- quiz endpoint tests verifying user-specific quiz access rules
- quiz endpoint tests verifying related question deletion when a quiz is deleted
- expanded README testing documentation with TDD structure, test file locations, test commands and current test counts
