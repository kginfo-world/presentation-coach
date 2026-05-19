def build_feedback(transcript: str, metrics: dict) -> dict:
    strengths = []
    improvements = []
    practice_tasks = []

    wpm = metrics["wordsPerMinute"]
    filler_total = sum(metrics["fillerCounts"].values())

    if 110 <= wpm <= 150:
        strengths.append("말의 속도가 청중이 따라가기 좋은 범위에 있습니다.")
    elif wpm > 150:
        improvements.append("말의 속도가 빠른 편입니다. 핵심 문장 뒤에 1초 정도 쉬어 주세요.")
        practice_tasks.append("다음 녹음에서는 문단마다 의도적인 멈춤을 1번씩 넣어 보세요.")
    elif wpm > 0:
        improvements.append("말의 속도가 느린 편입니다. 예시보다 핵심 주장 문장을 먼저 말해 보세요.")
        practice_tasks.append("30초 안에 발표 주제를 요약하는 연습을 해 보세요.")

    if filler_total == 0:
        strengths.append("반복적으로 감지된 습관어가 적습니다.")
    else:
        improvements.append(f"습관어가 총 {filler_total}회 감지되었습니다. 문장을 시작하기 전 짧게 숨을 고르면 줄일 수 있습니다.")
        practice_tasks.append("녹음 후 첫 1분만 다시 들으면서 습관어가 나온 위치를 표시해 보세요.")

    if len(transcript.strip()) < 30:
        improvements.append("분석할 수 있는 발화 텍스트가 부족합니다. STT 연결 후 더 정확한 피드백을 받을 수 있습니다.")

    return {
        "summary": "발표 속도, 습관어, 멈춤 패턴을 기준으로 만든 1차 코칭 리포트입니다.",
        "strengths": strengths or ["좋은 점을 더 정확히 찾으려면 실제 음성 인식 결과가 필요합니다."],
        "improvements": improvements or ["현재 지표에서는 큰 위험 신호가 보이지 않습니다."],
        "practiceTasks": practice_tasks or ["같은 주제로 한 번 더 녹음하고, 첫 문장과 마지막 문장을 더 선명하게 다듬어 보세요."],
    }
