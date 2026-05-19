from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.services.analysis import analyze_recording
from app.services.storage import save_upload

app = FastAPI(title="Presentation Coach API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze")
async def analyze_audio(file: UploadFile = File(...)):
    audio_path = await save_upload(file)
    return analyze_recording(audio_path, original_filename=file.filename or "recording")
