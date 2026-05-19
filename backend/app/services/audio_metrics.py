from pathlib import Path
import wave

FILLER_WORDS = ["음", "어", "그", "약간", "뭔가", "이제", "그러니까", "사실", "막"]


def get_audio_metrics(audio_path: Path, transcript: str) -> dict:
    duration_seconds = _get_wav_duration(audio_path)
    words = [word for word in transcript.split() if word.strip()]
    word_count = len(words)
    minutes = max(duration_seconds / 60, 0.01)
    words_per_minute = round(word_count / minutes)

    filler_counts = {
        filler: transcript.count(filler)
        for filler in FILLER_WORDS
        if transcript.count(filler) > 0
    }

    return {
        "durationSeconds": round(duration_seconds, 1),
        "wordCount": word_count,
        "wordsPerMinute": words_per_minute,
        "fillerCounts": filler_counts,
        "estimatedPauseCount": _estimate_pause_count(duration_seconds, word_count),
    }


def _get_wav_duration(audio_path: Path) -> float:
    if audio_path.suffix.lower() != ".wav":
        return 0.0

    with wave.open(str(audio_path), "rb") as wav_file:
        frames = wav_file.getnframes()
        rate = wav_file.getframerate()
        return frames / float(rate)


def _estimate_pause_count(duration_seconds: float, word_count: int) -> int:
    if duration_seconds <= 0 or word_count <= 0:
        return 0

    expected_words = duration_seconds / 60 * 130
    missing_words = max(expected_words - word_count, 0)
    return round(missing_words / 8)
