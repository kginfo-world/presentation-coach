from dataclasses import dataclass
import os
from pathlib import Path

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

DEFAULT_TRANSCRIPTION_MODEL = os.getenv("OPENAI_TRANSCRIPTION_MODEL", "gpt-4o-mini-transcribe")


@dataclass
class Transcript:
    text: str
    status: str
    message: str
    model: str | None = None


def transcribe_audio(audio_path: Path) -> Transcript:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return Transcript(
            text="",
            status="missing_api_key",
            message="OPENAI_API_KEY가 설정되어 있지 않아 STT를 건너뛰었습니다. 현재는 음성 파형 지표만 분석했습니다.",
        )

    try:
        client = OpenAI(api_key=api_key)
        with audio_path.open("rb") as audio_file:
            result = client.audio.transcriptions.create(
                model=DEFAULT_TRANSCRIPTION_MODEL,
                file=audio_file,
                language="ko",
                response_format="json",
            )

        text = (result.text or "").strip()
        return Transcript(
            text=text,
            status="completed" if text else "empty",
            message="STT가 완료되었습니다." if text else "STT 결과가 비어 있습니다.",
            model=DEFAULT_TRANSCRIPTION_MODEL,
        )
    except Exception as error:
        return Transcript(
            text="",
            status="failed",
            message=f"STT 처리 중 오류가 발생했습니다: {error}",
            model=DEFAULT_TRANSCRIPTION_MODEL,
        )
