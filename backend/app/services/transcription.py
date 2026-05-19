from dataclasses import dataclass
from pathlib import Path


@dataclass
class Transcript:
    text: str


def transcribe_audio(audio_path: Path) -> Transcript:
    # Replace this with Whisper, OpenAI STT, or another provider.
    return Transcript(
        text=(
            "음 안녕하세요. 오늘은 AI 음성 인식을 활용해서 발표 연습을 개선하는 방법을 "
            "소개하겠습니다. 핵심은 녹음 파일을 분석하고 말 속도와 습관어를 확인하는 것입니다."
        )
    )
