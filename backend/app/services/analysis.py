from pathlib import Path

from app.services.audio_metrics import get_audio_metrics
from app.services.feedback import build_feedback
from app.services.transcription import transcribe_audio


def analyze_recording(audio_path: Path, original_filename: str) -> dict:
    transcript = transcribe_audio(audio_path)
    metrics = get_audio_metrics(audio_path, transcript.text)
    feedback = build_feedback(transcript.text, metrics)

    return {
        "filename": original_filename,
        "transcript": transcript.text,
        "metrics": metrics,
        "feedback": feedback,
    }
