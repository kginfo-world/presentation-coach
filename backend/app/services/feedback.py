def build_feedback(transcript: str, metrics: dict) -> dict:
    strengths: list[str] = []
    improvements: list[str] = []
    practice_tasks: list[str] = []
    detailed_analysis: list[dict] = []
    revision_targets: list[dict] = []

    def add_analysis(title: str, finding: str, evidence: str, recommendation: str, priority: str = "medium") -> None:
        detailed_analysis.append(
            {
                "title": title,
                "finding": finding,
                "evidence": evidence,
                "recommendation": recommendation,
                "priority": priority,
            }
        )

    def add_revision(target: str, reason: str, how_to_fix: str, example: str) -> None:
        revision_targets.append(
            {
                "target": target,
                "reason": reason,
                "howToFix": how_to_fix,
                "example": example,
            }
        )

    if not metrics["supportedAudioMetrics"]:
        return {
            "summary": "파일 업로드는 되었지만, 현재 상세 파형 분석은 WAV 파일을 가장 안정적으로 지원합니다.",
            "overallReview": "STT는 시도할 수 있지만, 길이와 멈춤, 볼륨 같은 음성 근거는 WAV 파일에서 가장 정확하게 계산됩니다.",
            "strengths": ["업로드 흐름은 정상 동작합니다."],
            "improvements": ["길이, 볼륨, 멈춤 분석을 위해 WAV 형식의 녹음 파일을 사용해 주세요."],
            "practiceTasks": ["같은 녹음을 WAV로 변환한 뒤 결과를 다시 비교해 보세요."],
            "detailedAnalysis": [
                {
                    "title": "파일 형식",
                    "finding": "현재 파일은 파형 분석 지원 범위가 제한됩니다.",
                    "evidence": "supportedAudioMetrics=false",
                    "recommendation": "WAV로 변환한 파일을 업로드하면 침묵 비율, 긴 멈춤, 볼륨을 더 정확히 볼 수 있습니다.",
                    "priority": "high",
                }
            ],
            "revisionTargets": [],
        }

    duration = metrics["durationSeconds"]
    silence_ratio = metrics["silenceRatio"]
    pause_count = metrics["estimatedPauseCount"]
    average_volume = metrics["averageVolumePercent"]
    peak_volume = metrics["peakVolumePercent"]

    _analyze_duration(duration, strengths, improvements, practice_tasks, add_analysis)
    _analyze_silence(silence_ratio, strengths, improvements, practice_tasks, add_analysis, add_revision)
    _analyze_pauses(pause_count, strengths, improvements, practice_tasks, add_analysis, add_revision)
    _analyze_volume(average_volume, peak_volume, strengths, improvements, add_analysis, add_revision)

    if transcript.strip():
        _analyze_text(transcript, metrics, strengths, improvements, practice_tasks, add_analysis, add_revision)
    else:
        improvements.append("STT가 완료되지 않아 습관어와 정확한 말하기 속도는 측정하지 않았습니다.")
        practice_tasks.append("OPENAI_API_KEY를 설정하면 실제 발화 텍스트, 습관어, 문장 구조까지 분석할 수 있습니다.")
        add_analysis(
            "텍스트 분석",
            "발화 텍스트가 없어 내용 기반 피드백은 제한됩니다.",
            "transcript가 비어 있어 단어 수, 습관어, 문장 흐름을 계산하지 않았습니다.",
            "STT 설정을 확인한 뒤 같은 파일을 다시 분석해 주세요.",
            "high",
        )

    return {
        "summary": "발표 음성의 파형 지표와 STT transcript를 함께 사용해 만든 상세 코칭 리포트입니다.",
        "overallReview": _build_overall_review(metrics, bool(transcript.strip())),
        "strengths": strengths or ["녹음 파일이 정상적으로 업로드되고 분석되었습니다."],
        "improvements": improvements or ["현재 측정 지표에서는 큰 문제 신호가 보이지 않습니다."],
        "practiceTasks": practice_tasks or ["같은 발표를 다시 녹음한 뒤 긴 멈춤 수와 침묵 비율을 비교해 보세요."],
        "detailedAnalysis": detailed_analysis,
        "revisionTargets": revision_targets,
    }


def _analyze_duration(duration: float, strengths: list, improvements: list, practice_tasks: list, add_analysis) -> None:
    if duration >= 45:
        strengths.append("말하기 흐름과 멈춤 습관을 살펴볼 만큼 충분한 길이의 녹음입니다.")
        add_analysis(
            "발표 길이",
            "분석에 충분한 길이입니다.",
            f"전체 녹음 길이는 {duration:.1f}초입니다. 45초 이상이면 흐름, 멈춤, 반복 표현을 관찰하기에 충분합니다.",
            "현재 길이는 유지하고, 같은 주제로 반복 녹음하며 지표 변화를 비교해 보세요.",
            "low",
        )
    else:
        improvements.append("녹음 길이가 짧아 코칭 신뢰도가 제한적입니다.")
        practice_tasks.append("최소 1분 분량으로 다시 녹음해 발표 흐름을 확인해 보세요.")
        add_analysis(
            "발표 길이",
            "녹음이 짧아 종합 판단이 제한됩니다.",
            f"전체 녹음 길이는 {duration:.1f}초입니다. 짧은 녹음은 일시적인 말투나 멈춤에 결과가 크게 흔들립니다.",
            "최소 60초 이상 녹음하고, 도입-핵심 주장-마무리가 모두 들어가게 구성해 주세요.",
            "medium",
        )


def _analyze_silence(
    silence_ratio: float,
    strengths: list,
    improvements: list,
    practice_tasks: list,
    add_analysis,
    add_revision,
) -> None:
    percent = round(silence_ratio * 100)

    if 0.12 <= silence_ratio <= 0.35:
        strengths.append("문장 사이에 청중이 따라올 수 있는 여백이 어느 정도 있습니다.")
        add_analysis(
            "침묵 비율",
            "전체 침묵 비율이 적정 범위에 있습니다.",
            f"침묵 비율은 약 {percent}%입니다. 12%~35% 범위는 문장 사이 호흡과 정보 소화 시간을 만들 가능성이 높습니다.",
            "핵심 문장 직후의 멈춤은 유지하고, 불필요하게 길어진 공백만 줄이면 좋습니다.",
            "low",
        )
    elif silence_ratio > 0.35:
        improvements.append("침묵 비율이 높은 편입니다. 의도적인 멈춤인지, 망설임 때문에 생긴 공백인지 확인해 보세요.")
        practice_tasks.append("멈춘 뒤 한 호흡 안에 다음 문장을 다시 시작하는 연습을 해 보세요.")
        add_analysis(
            "침묵 비율",
            "침묵이 많아 발표 흐름이 끊겨 들릴 수 있습니다.",
            f"침묵 비율은 약 {percent}%입니다. 35%를 넘으면 청중에게 망설임이나 준비 부족처럼 느껴질 수 있습니다.",
            "문장 사이 pause는 1초 안팎으로 줄이고, 다음 문장의 첫 단어를 미리 정해 둔 뒤 말해 보세요.",
            "high",
        )
        add_revision(
            "긴 공백 줄이기",
            "침묵 비율이 높으면 발표의 자신감과 연결성이 약해 보일 수 있습니다.",
            "문장 끝에서 멈춘 뒤 바로 다음 문장의 첫 세 단어를 떠올리고 말하세요.",
            "예: '다음으로 중요한 점은...'처럼 연결 문장을 미리 준비합니다.",
        )
    else:
        improvements.append("침묵이 거의 없습니다. 핵심 주장 뒤에 짧은 멈춤을 넣으면 청중이 따라오기 쉽습니다.")
        practice_tasks.append("발표문에서 1초 쉬어갈 위치를 세 곳 표시해 보세요.")
        add_analysis(
            "침묵 비율",
            "침묵이 너무 적어 정보가 몰아서 전달될 수 있습니다.",
            f"침묵 비율은 약 {percent}%입니다. 12%보다 낮으면 청중이 핵심 내용을 처리할 시간이 부족할 수 있습니다.",
            "핵심 주장, 숫자, 결론 직후에 1초 pause를 넣어 메시지의 무게를 살려 주세요.",
            "high",
        )
        add_revision(
            "핵심 문장 뒤 pause 추가",
            "쉼이 없으면 중요한 문장도 평범한 문장처럼 지나갑니다.",
            "주장-근거-예시 단락마다 주장 문장 뒤에 1초 pause를 넣으세요.",
            "예: '이 기능의 핵심은 반복 연습을 데이터로 바꾸는 것입니다. [1초 pause]'",
        )


def _analyze_pauses(
    pause_count: int,
    strengths: list,
    improvements: list,
    practice_tasks: list,
    add_analysis,
    add_revision,
) -> None:
    if pause_count >= 5:
        improvements.append(f"긴 멈춤이 {pause_count}회 감지되었습니다. 일부는 망설임처럼 들릴 수 있습니다.")
        add_analysis(
            "긴 멈춤",
            "긴 멈춤이 많은 편입니다.",
            f"0.7초 이상 이어지는 긴 멈춤이 {pause_count}회 감지되었습니다.",
            "강조를 위한 pause와 생각이 끊긴 pause를 구분하세요. 원고에 의도한 pause만 표시하고 나머지는 연결 문장으로 줄이는 것이 좋습니다.",
            "high",
        )
        add_revision(
            "망설임처럼 들리는 멈춤 줄이기",
            "긴 멈춤이 반복되면 발표 준비도가 낮아 보일 수 있습니다.",
            "단락 전환 문장 3개를 미리 정해 두세요.",
            "예: '이제 실제 사용 흐름을 보겠습니다.', '여기서 중요한 지표는 세 가지입니다.'",
        )
    elif pause_count > 0:
        strengths.append(f"긴 멈춤이 {pause_count}회 감지되었습니다. 의도한 멈춤이라면 강조 효과로 활용할 수 있습니다.")
        add_analysis(
            "긴 멈춤",
            "긴 멈춤 수는 과도하지 않습니다.",
            f"0.7초 이상 긴 멈춤이 {pause_count}회 감지되었습니다.",
            "핵심 메시지 앞뒤의 멈춤은 살리고, 생각을 고르느라 생긴 멈춤만 줄여 보세요.",
            "low",
        )
    else:
        add_analysis(
            "긴 멈춤",
            "긴 멈춤은 거의 감지되지 않았습니다.",
            "0.7초 이상 이어지는 긴 멈춤이 감지되지 않았습니다.",
            "중요한 문장 뒤에는 오히려 짧은 pause를 추가하면 전달력이 좋아질 수 있습니다.",
            "medium",
        )


def _analyze_volume(
    average_volume: int,
    peak_volume: int,
    strengths: list,
    improvements: list,
    add_analysis,
    add_revision,
) -> None:
    evidence = f"평균 볼륨은 {average_volume}%, 최대 볼륨은 {peak_volume}%입니다."

    if average_volume < 8:
        improvements.append("평균 볼륨이 낮습니다. 마이크에 조금 더 가까이 말하거나 입력 볼륨을 높여 보세요.")
        add_analysis(
            "녹음 볼륨",
            "평균 볼륨이 낮아 STT와 청취 품질이 떨어질 수 있습니다.",
            evidence,
            "마이크와 입 사이 거리를 줄이고, 녹음 전 5초 테스트로 파형이 너무 작지 않은지 확인하세요.",
            "medium",
        )
        add_revision(
            "마이크 입력 개선",
            "볼륨이 낮으면 발음이 좋아도 인식과 청취 품질이 흔들립니다.",
            "마이크를 입에서 15~25cm 거리로 두고, 문장 끝을 흐리지 않게 말하세요.",
            "예: 마지막 단어를 작게 줄이지 말고 끝까지 같은 크기로 발음합니다.",
        )
    elif peak_volume > 95:
        improvements.append("최대 볼륨이 매우 높습니다. 강하게 말할 때 음성이 찢어질 수 있습니다.")
        add_analysis(
            "녹음 볼륨",
            "최대 볼륨이 높아 clipping 위험이 있습니다.",
            evidence,
            "입력 gain을 낮추거나 마이크와의 거리를 조금 늘려 강한 발성에서도 여유를 확보하세요.",
            "medium",
        )
    else:
        strengths.append("분석에 사용할 수 있는 수준의 녹음 볼륨입니다.")
        add_analysis(
            "녹음 볼륨",
            "볼륨이 분석에 무리가 없는 범위입니다.",
            evidence,
            "현재 녹음 환경을 유지하되, 실제 발표처럼 강하게 말하는 구간에서도 clipping이 없는지 확인하세요.",
            "low",
        )


def _analyze_text(
    transcript: str,
    metrics: dict,
    strengths: list,
    improvements: list,
    practice_tasks: list,
    add_analysis,
    add_revision,
) -> None:
    wpm = metrics["wordsPerMinute"]
    word_count = metrics["wordCount"]
    filler_counts = metrics["fillerCounts"]
    filler_total = sum(filler_counts.values())

    if 100 <= wpm <= 150:
        strengths.append("말하기 속도가 청중이 따라가기 좋은 범위입니다.")
        add_analysis(
            "말하기 속도",
            "전체 속도는 안정적인 범위입니다.",
            f"STT 기준 단어 수는 {word_count}개, 말하기 속도는 약 {wpm} WPM입니다.",
            "현재 속도는 유지하되, 중요한 문장에는 의도적인 pause를 넣어 강조를 만드세요.",
            "low",
        )
    elif wpm > 150:
        improvements.append("말하기 속도가 빠른 편입니다. 핵심 문장 뒤에 짧게 쉬어 주세요.")
        practice_tasks.append("첫 30초를 다시 녹음하며 문장 끝마다 1초 pause를 넣어 보세요.")
        add_analysis(
            "말하기 속도",
            "전체 속도가 빠르게 측정되었습니다.",
            f"STT 기준 단어 수는 {word_count}개, 말하기 속도는 약 {wpm} WPM입니다. 150 WPM을 넘으면 정보가 압축되어 들릴 수 있습니다.",
            "핵심 주장 뒤에는 1초 멈추고, 예시는 한 문장씩 끊어 말하세요.",
            "high",
        )
        add_revision(
            "빠른 문장 끊어 말하기",
            "빠른 속도는 청중의 이해보다 발표자의 전달 욕심이 앞서 보이게 만들 수 있습니다.",
            "한 문장에 하나의 정보만 넣고, 쉼표 위치에서 호흡하세요.",
            "예: '첫째, 녹음 파일을 분석합니다. 둘째, 습관어를 찾습니다. 셋째, 다음 연습 과제를 제안합니다.'",
        )
    elif wpm > 0:
        improvements.append("말하기 속도가 느린 편입니다. 예시보다 핵심 주장을 먼저 말해 보세요.")
        add_analysis(
            "말하기 속도",
            "전체 속도가 느리게 측정되었습니다.",
            f"STT 기준 단어 수는 {word_count}개, 말하기 속도는 약 {wpm} WPM입니다. 100 WPM 미만이면 발표가 늘어지는 느낌을 줄 수 있습니다.",
            "도입 설명을 줄이고 결론 문장을 먼저 말한 뒤 근거를 붙여 보세요.",
            "medium",
        )
        add_revision(
            "핵심 주장 선명하게 말하기",
            "느린 속도에서는 핵심이 늦게 나오면 집중이 떨어질 수 있습니다.",
            "각 단락 첫 문장을 결론형으로 바꾸세요.",
            "예: '이 앱은 발표 연습을 데이터로 바꿔 줍니다.'",
        )

    if filler_total == 0:
        strengths.append("반복적인 습관어가 감지되지 않았습니다.")
        add_analysis(
            "습관어",
            "반복 습관어가 거의 없습니다.",
            "현재 transcript에서 설정된 습관어 목록이 감지되지 않았습니다.",
            "문장 시작 전 호흡을 유지하면 이 장점을 계속 살릴 수 있습니다.",
            "low",
        )
    else:
        filler_text = ", ".join(f"{word} {count}회" for word, count in filler_counts.items())
        improvements.append(f"습관어가 {filler_total}회 감지되었습니다.")
        practice_tasks.append("첫 1분을 다시 들으며 습관어가 나온 위치를 표시해 보세요.")
        add_analysis(
            "습관어",
            "반복되는 연결 표현이 발표의 선명도를 낮출 수 있습니다.",
            f"감지된 습관어는 총 {filler_total}회입니다. 세부 빈도: {filler_text}.",
            "문장을 시작하기 전에 숨을 한 번 고르고, '음/어/그' 대신 바로 핵심 명사로 시작해 보세요.",
            "high" if filler_total >= 8 else "medium",
        )
        add_revision(
            "습관어 대체",
            "습관어가 반복되면 자신감이 낮아 보이고 핵심 문장이 흐려집니다.",
            "습관어가 나오는 위치를 pause로 바꾸거나 전환 문장으로 대체하세요.",
            "예: '음, 이 기능은...' 대신 '[0.5초 pause] 이 기능은...'으로 말합니다.",
        )

    if len(transcript) > 0:
        add_analysis(
            "내용 기반 분석 가능성",
            "STT transcript가 확보되어 내용 분석 확장이 가능합니다.",
            f"transcript 길이는 약 {len(transcript)}자입니다.",
            "다음 단계에서는 도입-본론-결론 구조, 주장과 근거의 연결성을 LLM으로 평가할 수 있습니다.",
            "medium",
        )


def _build_overall_review(metrics: dict, has_transcript: bool) -> str:
    pieces = [
        f"이번 발표는 총 {metrics['durationSeconds']:.1f}초이며",
        f"침묵 비율은 약 {round(metrics['silenceRatio'] * 100)}%",
        f"긴 멈춤은 {metrics['estimatedPauseCount']}회 감지되었습니다.",
    ]

    if has_transcript:
        pieces.append(
            f"STT 기준 {metrics['wordCount']}개 단어, 약 {metrics['wordsPerMinute']} WPM으로 말했습니다."
        )
        filler_total = sum(metrics["fillerCounts"].values())
        pieces.append(f"습관어는 총 {filler_total}회 감지되었습니다.")
    else:
        pieces.append("STT transcript가 없어 텍스트 기반 분석은 제한되었습니다.")

    return " ".join(pieces)
