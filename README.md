# Quizly Backend

Quizly Backend is a Django REST Framework backend for the provided Quizly frontend.

The backend will provide JWT authentication with HttpOnly cookies and quiz generation from YouTube URLs.

## Setup

### Clone repository

```bash
git clone <your-backend-repository-url>
```

### Open backend folder

```bash
cd backend
```

### Create virtual environment

```bash
python -m venv .venv
```

### Activate virtual environment (Windows)

```bash
.venv\Scripts\activate
```

### Activate virtual environment (Linux / Mac)

```bash
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Create local environment file (Windows)

```bash
copy .env.template .env
```

### Create local environment file (Linux / Mac)

```bash
cp .env.template .env
```

### Generate a Django SECRET_KEY

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Insert SECRET_KEY into .env

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
CORS_ALLOWED_ORIGINS=http://127.0.0.1:5500,http://localhost:5500
GEMINI_API_KEY=your-gemini-api-key
```

### Start development server

```bash
python manage.py runserver
```

## External Requirements

FFmpeg must be installed globally because Whisper requires it for audio processing.

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
└── frontend/
```

The frontend and backend are separated projects. The provided frontend communicates with this backend through a REST API.
