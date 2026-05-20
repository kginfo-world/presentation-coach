def build_feedback(transcript: str, metrics: dict) -> dict:
    strengths = []
    improvements = []
    practice_tasks = []

    if not metrics["supportedAudioMetrics"]:
        return {
            "summary": "파일 업로드는 되었지만, 현재 상세 파형 분석은 WAV 파일을 가장 안정적으로 지원합니다.",
            "strengths": ["업로드 흐름은 정상 동작합니다."],
            "improvements": ["길이, 볼륨, 멈춤 분석을 위해 WAV 형식의 녹음 파일을 사용해 주세요."],
            "practiceTasks": ["같은 녹음을 WAV로 변환한 뒤 결과를 다시 비교해 보세요."],
        }

    duration = metrics["durationSeconds"]
    silence_ratio = metrics["silenceRatio"]
    pause_count = metrics["estimatedPauseCount"]
    average_volume = metrics["averageVolumePercent"]
    peak_volume = metrics["peakVolumePercent"]

    if duration >= 45:
        strengths.append("말하기 흐름과 멈춤 습관을 살펴볼 만큼 충분한 길이의 녹음입니다.")
    else:
        improvements.append("녹음 길이가 짧아 코칭 신뢰도가 제한적입니다.")

    if 0.12 <= silence_ratio <= 0.35:
        strengths.append("문장 사이에 청중이 따라올 수 있는 여백이 어느 정도 있습니다.")
    elif silence_ratio > 0.35:
        improvements.append("침묵 비율이 높은 편입니다. 의도적인 멈춤인지, 망설임 때문에 생긴 공백인지 확인해 보세요.")
        practice_tasks.append("멈춘 뒤 한 호흡 안에 다음 문장을 다시 시작하는 연습을 해 보세요.")
    else:
        improvements.append("침묵이 거의 없습니다. 핵심 주장 뒤에 짧은 멈춤을 넣으면 청중이 따라오기 쉽습니다.")
        practice_tasks.append("발표문에서 1초 쉬어갈 위치를 세 곳 표시해 보세요.")

    if average_volume < 8:
        improvements.append("평균 볼륨이 낮습니다. 마이크에 조금 더 가까이 말하거나 입력 볼륨을 높여 보세요.")
    elif peak_volume > 95:
        improvements.append("최대 볼륨이 매우 높습니다. 강하게 말할 때 음성이 찢어질 수 있습니다.")
    else:
        strengths.append("분석에 사용할 수 있는 수준의 녹음 볼륨입니다.")

    if pause_count >= 5:
        improvements.append(f"긴 멈춤이 {pause_count}회 감지되었습니다. 일부는 망설임처럼 들릴 수 있습니다.")
    elif pause_count > 0:
        strengths.append(f"긴 멈춤이 {pause_count}회 감지되었습니다. 의도한 멈춤이라면 강조 효과로 활용할 수 있습니다.")

    if transcript.strip():
        _add_text_feedback(transcript, metrics, strengths, improvements, practice_tasks)
    else:
        improvements.append("STT가 완료되지 않아 습관어와 정확한 말하기 속도는 측정하지 않았습니다.")
        practice_tasks.append("OPENAI_API_KEY를 설정하면 실제 발화 텍스트, 습관어, 문장 구조까지 분석할 수 있습니다.")

    return {
        "summary": "이 리포트는 실제 음성 파형의 길이, 침묵, 긴 멈춤, 볼륨을 기준으로 생성되었습니다.",
        "strengths": strengths or ["녹음 파일이 정상적으로 업로드되고 분석되었습니다."],
        "improvements": improvements or ["음성 레벨 기준으로는 큰 문제 신호가 보이지 않습니다."],
        "practiceTasks": practice_tasks or ["같은 발표를 다시 녹음한 뒤 긴 멈춤 수와 침묵 비율을 비교해 보세요."],
    }


def _add_text_feedback(transcript: str, metrics: dict, strengths: list, improvements: list, practice_tasks: list) -> None:
    wpm = metrics["wordsPerMinute"]
    filler_total = sum(metrics["fillerCounts"].values())

    if 110 <= wpm <= 150:
        strengths.append("말하기 속도가 청중이 따라가기 좋은 범위입니다.")
    elif wpm > 150:
        improvements.append("말하기 속도가 빠른 편입니다. 핵심 문장 뒤에 짧게 쉬어 주세요.")
    elif wpm > 0:
        improvements.append("말하기 속도가 느린 편입니다. 예시보다 핵심 주장을 먼저 말해 보세요.")

    if filler_total == 0:
        strengths.append("반복적인 습관어가 감지되지 않았습니다.")
    else:
        improvements.append(f"습관어가 {filler_total}회 감지되었습니다.")
        practice_tasks.append("첫 1분을 다시 들으며 습관어가 나온 위치를 표시해 보세요.")
