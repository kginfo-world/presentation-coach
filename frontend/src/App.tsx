import { ChangeEvent, FormEvent, useState } from "react";
import { Mic, UploadCloud } from "lucide-react";

type DetailItem = {
  title: string;
  finding: string;
  evidence: string;
  recommendation: string;
  priority: "low" | "medium" | "high" | string;
};

type RevisionTarget = {
  target: string;
  reason: string;
  howToFix: string;
  example: string;
};

type AnalysisResult = {
  filename: string;
  transcript: string;
  transcription: {
    status: string;
    message: string;
    model?: string | null;
  };
  metrics: {
    durationSeconds: number;
    wordCount: number;
    wordsPerMinute: number;
    estimatedPauseCount: number;
    fillerCounts: Record<string, number>;
    silenceRatio: number;
    averageVolumePercent: number;
    peakVolumePercent: number;
    supportedAudioMetrics: boolean;
  };
  feedback: {
    summary: string;
    overallReview?: string;
    strengths: string[];
    improvements: string[];
    practiceTasks: string[];
    detailedAnalysis?: DetailItem[];
    revisionTargets?: RevisionTarget[];
  };
};

export function App() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    setFile(event.target.files?.[0] ?? null);
    setError("");
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();

    if (!file) {
      setError("분석할 음성 파일을 선택해 주세요.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setIsLoading(true);
    setError("");

    try {
      const response = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("분석 요청에 실패했습니다.");
      }

      setResult(await response.json());
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "알 수 없는 오류가 발생했습니다.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="app-shell">
      <section className="workspace">
        <div className="intro">
          <div className="brand-mark">
            <Mic size={28} />
          </div>
          <div>
            <h1>Presentation Coach</h1>
            <p>녹음 파일을 업로드하면 발표 속도, 습관어, 근거 기반 개선점을 분석합니다.</p>
          </div>
        </div>

        <form className="upload-panel" onSubmit={handleSubmit}>
          <label className="dropzone">
            <UploadCloud size={34} />
            <span>{file ? file.name : "음성 파일 선택"}</span>
            <input type="file" accept="audio/*,.wav,.mp3,.m4a" onChange={handleFileChange} />
          </label>
          <button type="submit" disabled={isLoading}>
            {isLoading ? "분석 중..." : "분석 시작"}
          </button>
          {error && <p className="error">{error}</p>}
        </form>

        {result && <AnalysisReport result={result} />}
      </section>
    </main>
  );
}

function AnalysisReport({ result }: { result: AnalysisResult }) {
  const fillerEntries = Object.entries(result.metrics.fillerCounts);

  return (
    <section className="report">
      <div className="metric-grid">
        <Metric label="음성 길이" value={`${result.metrics.durationSeconds}s`} />
        <Metric label="침묵 비율" value={`${Math.round(result.metrics.silenceRatio * 100)}%`} />
        <Metric label="말 속도" value={`${result.metrics.wordsPerMinute} WPM`} />
        <Metric label="긴 멈춤" value={`${result.metrics.estimatedPauseCount}`} />
      </div>

      <div className="report-section">
        <h2>종합 분석</h2>
        <p>{result.feedback.overallReview ?? result.feedback.summary}</p>
      </div>

      <div className="report-section">
        <h2>Transcript</h2>
        <p>{result.transcript}</p>
      </div>

      <div className="report-section">
        <h2>습관어</h2>
        {fillerEntries.length > 0 ? (
          <div className="chips">
            {fillerEntries.map(([word, count]) => (
              <span key={word}>{word}: {count}</span>
            ))}
          </div>
        ) : (
          <p>반복 감지된 습관어가 없습니다.</p>
        )}
      </div>

      <FeedbackList title="좋은 점" items={result.feedback.strengths} />
      <FeedbackList title="개선할 점" items={result.feedback.improvements} />
      <DetailedAnalysis items={result.feedback.detailedAnalysis ?? []} />
      <RevisionTargets items={result.feedback.revisionTargets ?? []} />
      <FeedbackList title="다음 연습" items={result.feedback.practiceTasks} />
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function FeedbackList({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="report-section">
      <h2>{title}</h2>
      <ul>
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

function DetailedAnalysis({ items }: { items: DetailItem[] }) {
  if (items.length === 0) {
    return null;
  }

  return (
    <div className="report-section">
      <h2>근거 기반 상세 분석</h2>
      <ul>
        {items.map((item) => (
          <li key={`${item.title}-${item.evidence}`}>
            <strong>{item.title}</strong>: {item.finding}
            <br />
            근거: {item.evidence}
            <br />
            수정 방향: {item.recommendation}
          </li>
        ))}
      </ul>
    </div>
  );
}

function RevisionTargets({ items }: { items: RevisionTarget[] }) {
  if (items.length === 0) {
    return null;
  }

  return (
    <div className="report-section">
      <h2>수정해야 할 부분</h2>
      <ul>
        {items.map((item) => (
          <li key={item.target}>
            <strong>{item.target}</strong>: {item.reason}
            <br />
            방법: {item.howToFix}
            <br />
            예시: {item.example}
          </li>
        ))}
      </ul>
    </div>
  );
}
