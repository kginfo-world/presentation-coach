from dataclasses import dataclass
from pathlib import Path


@dataclass
class Transcript:
    text: str
    status: str
    message: str


def transcribe_audio(audio_path: Path) -> Transcript:
    # A real STT provider should be connected here later.
    return Transcript(
        text="",
        status="not_configured",
        message="아직 STT가 연결되지 않아 실제 발화 텍스트는 분석하지 않았습니다. 현재 리포트는 음성 파형 지표를 기준으로 생성됩니다.",
    )
