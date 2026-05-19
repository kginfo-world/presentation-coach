from pathlib import Path
import math
import struct
import wave

FILLER_WORDS = ["음", "어", "그", "약간", "뭔가", "이제", "그러니까", "사실", "막"]


def get_audio_metrics(audio_path: Path, transcript: str) -> dict:
    audio = _analyze_wav(audio_path)
    words = [word for word in transcript.split() if word.strip()]
    minutes = max(audio["durationSeconds"] / 60, 0.01)

    return {
        "durationSeconds": audio["durationSeconds"],
        "wordCount": len(words),
        "wordsPerMinute": round(len(words) / minutes) if words else 0,
        "fillerCounts": _count_fillers(transcript),
        "estimatedPauseCount": audio["pauseCount"],
        "silenceRatio": audio["silenceRatio"],
        "averageVolumePercent": audio["averageVolumePercent"],
        "peakVolumePercent": audio["peakVolumePercent"],
        "supportedAudioMetrics": audio["supported"],
    }


def _count_fillers(transcript: str) -> dict[str, int]:
    return {
        filler: transcript.count(filler)
        for filler in FILLER_WORDS
        if transcript.count(filler) > 0
    }


def _analyze_wav(audio_path: Path) -> dict:
    empty = {
        "durationSeconds": 0.0,
        "pauseCount": 0,
        "silenceRatio": 0,
        "averageVolumePercent": 0,
        "peakVolumePercent": 0,
        "supported": False,
    }

    if audio_path.suffix.lower() != ".wav":
        return empty

    with wave.open(str(audio_path), "rb") as wav_file:
        channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        frame_rate = wav_file.getframerate()
        frame_count = wav_file.getnframes()
        raw = wav_file.readframes(frame_count)

    duration = frame_count / float(frame_rate) if frame_rate else 0
    samples = _decode_samples(raw, sample_width, channels)

    if not samples:
        return {**empty, "durationSeconds": round(duration, 1), "supported": True}

    max_amplitude = float(2 ** (sample_width * 8 - 1))
    peak = max(abs(sample) for sample in samples)
    average_rms = math.sqrt(sum(sample * sample for sample in samples) / len(samples))

    window_size = max(int(frame_rate * 0.1), 1)
    rms_windows = []
    for start in range(0, len(samples), window_size):
        window = samples[start : start + window_size]
        rms = math.sqrt(sum(sample * sample for sample in window) / len(window))
        rms_windows.append(rms)

    active_peak = max(rms_windows) if rms_windows else 0
    silence_threshold = max(active_peak * 0.12, max_amplitude * 0.01)
    silent_windows = [rms <= silence_threshold for rms in rms_windows]

    return {
        "durationSeconds": round(duration, 1),
        "pauseCount": _count_long_pauses(silent_windows, 0.1),
        "silenceRatio": round(sum(silent_windows) / len(silent_windows), 2) if silent_windows else 0,
        "averageVolumePercent": round(min(average_rms / max_amplitude * 100, 100)),
        "peakVolumePercent": round(min(peak / max_amplitude * 100, 100)),
        "supported": True,
    }


def _decode_samples(raw: bytes, sample_width: int, channels: int) -> list[int]:
    if sample_width == 1:
        samples = [byte - 128 for byte in raw]
    elif sample_width == 2:
        samples = list(struct.unpack(f"<{len(raw) // 2}h", raw))
    elif sample_width == 4:
        samples = list(struct.unpack(f"<{len(raw) // 4}i", raw))
    else:
        return []

    if channels <= 1:
        return samples

    return [
        round(sum(samples[index : index + channels]) / channels)
        for index in range(0, len(samples), channels)
    ]


def _count_long_pauses(silent_windows: list[bool], window_seconds: float) -> int:
    pauses = 0
    run = 0
    min_windows = math.ceil(0.7 / window_seconds)

    for is_silent in silent_windows:
        if is_silent:
            run += 1
            continue

        if run >= min_windows:
            pauses += 1
        run = 0

    if run >= min_windows:
        pauses += 1

    return pauses
