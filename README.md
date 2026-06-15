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
  - [Install Deno on Windows](#install-deno-on-windows)
  - [Install Deno on macOS](#install-deno-on-macos)
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
  - [Manual Smoke Test](#manual-smoke-test)
  - [Current Test Counts - 60 Tests](#current-test-counts---60-tests)
- [Current Implementation Status](#current-implementation-status)

## External Requirements

FFmpeg must be installed globally because Whisper requires it for audio loading and transcription.

Deno must be installed globally because newer YouTube extraction with `yt-dlp` may require a supported JavaScript runtime.

The Python packages for YouTube metadata handling, audio transcription and Gemini quiz generation are installed through `requirements.txt`.

### Python AI and video dependencies

The backend uses the following Python packages for quiz generation:

- `yt-dlp` for reading YouTube metadata and downloading audio
- `openai-whisper` for local audio transcription
- `google-genai` for Gemini Flash quiz generation

These packages are installed with the regular project dependencies:

```bash
pip install -r requirements.txt
```

### Install FFmpeg on Windows

```bash
winget install --id Gyan.FFmpeg -e --source winget
```

### Install FFmpeg on macOS

```bash
brew install ffmpeg
```

### Install Deno on Windows

```bash
winget install DenoLand.Deno
```

### Install Deno on macOS

```bash
brew install deno
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

The project uses `pytest` and `pytest-django` for automated backend testing.

Automated tests are endpoint-based and service-based. External services such as YouTube extraction, local Whisper transcription and Gemini quiz generation are mocked during automated tests to keep the test suite stable, fast and independent from external providers.

### Test Structure

The test structure follows the app-based project architecture.

Each tested app contains its own `tests` folder with endpoint-specific test files and shared test helpers.

```txt
app_name/
└── tests/
    ├── mixins.py
    └── test_*_api.py
```

Service tests are placed in the related app test folder and validate isolated service behavior.

### Tested Apps

The current test suite covers the following apps:

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

The authentication tests cover:

- user registration
- password confirmation validation
- duplicate username validation
- duplicate email validation
- user login
- JWT cookie creation
- logout handling
- refresh token blacklisting
- access token refresh through HttpOnly cookies
- invalid credentials
- authentication error cases

#### quizzes_app

```txt
quizzes_app/tests/
├── mixins.py
├── test_gemini_service.py
├── test_quiz_create_api.py
├── test_quiz_detail_delete_api.py
├── test_quiz_detail_retrieve_api.py
├── test_quiz_detail_update_api.py
├── test_quiz_generation_service.py
├── test_quiz_list_api.py
├── test_whisper_service.py
└── test_youtube_service.py
```

The quiz tests cover:

- authenticated quiz creation
- unauthenticated quiz creation rejection
- YouTube URL validation
- YouTube URL normalization
- rejection of non-YouTube URLs
- rejection of YouTube URLs without video IDs
- generated quiz persistence
- generated quiz question persistence
- quiz generation service orchestration
- temporary audio file cleanup after successful quiz generation
- temporary audio file cleanup after failed quiz generation
- YouTube audio extraction service behavior
- `yt_dlp` option handling
- single-video download handling
- Whisper model loading
- Whisper transcript extraction
- Gemini prompt handling
- Gemini markdown fence cleanup
- Gemini JSON parsing
- generated quiz data validation
- generated question data validation
- quiz list endpoint behavior
- quiz detail retrieval behavior
- quiz detail update behavior
- quiz detail deletion behavior

### Running Tests

Run the complete test suite from the backend root folder:

```bash
python -m pytest
```

Run only authentication tests:

```bash
python -m pytest auth_app/tests/
```

Run only quiz tests:

```bash
python -m pytest quizzes_app/tests/
```

Run one specific test file:

```bash
python -m pytest quizzes_app/tests/test_quiz_create_api.py
```

### Manual Smoke Test

The real quiz generation pipeline depends on external runtime behavior and external services.

The following parts are mocked during automated tests:

- YouTube extraction through `yt_dlp`
- local Whisper transcription
- Gemini quiz generation

For this reason, one manual Postman smoke test was used to verify the real end-to-end quiz creation flow.

Verified flow:

- authenticated request with JWT HttpOnly cookies
- YouTube audio extraction through `yt_dlp`
- FFmpeg availability for Whisper audio loading
- local Whisper transcription
- Gemini quiz generation
- database persistence of quiz and related questions
- successful API response from the quiz creation endpoint

Smoke-tested endpoint:

```txt
POST /api/quizzes/
```

The manual smoke test returned `201 Created` with one generated quiz and exactly 10 generated questions.

### Current Test Counts - 60 Tests

| App           | Test Count |
| ------------- | ---------: |
| `auth_app`    |         19 |
| `quizzes_app` |         41 |
| **Total**     |     **60** |

## Current Implementation Status

The backend project currently includes the Django and Django REST Framework structure, completed authentication endpoints and the first implemented quiz generation endpoint.

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
- registration API endpoint with user creation, password confirmation validation and duplicate username/email validation
- login API endpoint with credential validation, user response data and HttpOnly JWT cookies
- cookie-based JWT authentication for protected API requests
- logout API endpoint with refresh token blacklisting and auth cookie deletion
- token refresh API endpoint with refresh-token-cookie validation and refreshed access-token cookie handling
- reusable authentication utility helpers for login responses, token cookies and cookie deletion
- DRF authentication configuration for access tokens stored in HttpOnly cookies
- quiz creation API endpoint for authenticated users
- YouTube URL validation for quiz creation
- YouTube URL normalization before quiz generation
- rejection of non-YouTube URLs and YouTube URLs without video IDs
- generated quiz persistence with related quiz questions
- transactional quiz and question creation
- YouTube audio extraction service with `yt-dlp`
- temporary audio file handling for quiz generation
- automatic cleanup of temporary audio files after successful or failed quiz generation
- Whisper transcription service for local audio transcription
- configurable Whisper model setting
- Gemini quiz generation service
- configurable Gemini API key and Gemini model settings
- Gemini prompt structure for generating valid quiz JSON
- markdown fence cleanup for Gemini responses
- JSON parsing and validation for generated quiz data
- validation that generated quizzes contain exactly 10 questions
- validation that each generated question contains exactly four answer options
- validation that each generated answer exists in the related answer options
- error logging for unexpected quiz creation failures
- quiz creation API tests for YouTube URL validation and normalization
- quiz generation service tests for service orchestration and temporary audio cleanup
- YouTube service tests for `yt_dlp` options and audio path handling
- Whisper service tests for model loading and transcript extraction
- Gemini service tests for prompt handling, JSON parsing and generated quiz validation
- successful manual smoke test for `POST /api/quizzes/` with real YouTube extraction, Whisper transcription and Gemini quiz generation
