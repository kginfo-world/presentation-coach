# Presentation Coach

AI-assisted presentation practice app. Upload an audio recording, get a transcript-oriented analysis, and receive actionable speaking feedback.

## Project Layout

```text
backend/   FastAPI API for audio upload and analysis
frontend/  React + Vite UI for uploading recordings and viewing feedback
docs/      Technical architecture and project documentation
```

Technical documentation:

- [Technical Architecture](docs/technical-architecture.md)

## Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Edit .env and set OPENAI_API_KEY
uvicorn app.main:app --reload --port 8000
```

API endpoint:

```text
POST /analyze
```

Upload an audio file using multipart form field `file`.

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

The frontend expects the backend at `http://localhost:8000`.

## MVP Scope

- Upload a recorded speech audio file.
- Estimate WAV duration, pause count, silence ratio, and volume from the real audio waveform.
- Return a structured feedback report.
- Use OpenAI speech-to-text when `OPENAI_API_KEY` is configured.
- Fall back to waveform-only analysis when the API key is missing or transcription fails.
