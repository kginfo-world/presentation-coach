const form = document.querySelector("#uploadForm");
const fileInput = document.querySelector("#audioFile");
const fileName = document.querySelector("#fileName");
const submitButton = document.querySelector("#submitButton");
const errorMessage = document.querySelector("#errorMessage");
const report = document.querySelector("#report");

fileInput.addEventListener("change", () => {
  fileName.textContent = fileInput.files[0]?.name ?? "음성 파일 선택";
  errorMessage.textContent = "";
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const file = fileInput.files[0];
  if (!file) {
    errorMessage.textContent = "분석할 음성 파일을 선택해 주세요.";
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  submitButton.disabled = true;
  submitButton.textContent = "분석 중...";
  errorMessage.textContent = "";

  try {
    const response = await fetch("http://localhost:8000/analyze", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error("분석 요청에 실패했습니다.");
    }

    renderReport(await response.json());
  } catch (error) {
    errorMessage.textContent = error instanceof Error ? error.message : "알 수 없는 오류가 발생했습니다.";
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = "분석 시작";
  }
});

function renderReport(result) {
  const fillerEntries = Object.entries(result.metrics.fillerCounts);

  report.classList.remove("hidden");
  report.innerHTML = `
    <div class="metric-grid">
      ${metric("말 속도", `${result.metrics.wordsPerMinute} WPM`)}
      ${metric("단어 수", result.metrics.wordCount)}
      ${metric("길이", `${result.metrics.durationSeconds}s`)}
      ${metric("예상 멈춤", result.metrics.estimatedPauseCount)}
    </div>

    <div class="report-section">
      <h2>Transcript</h2>
      <p>${escapeHtml(result.transcript)}</p>
    </div>

    <div class="report-section">
      <h2>Filler Words</h2>
      ${
        fillerEntries.length
          ? `<div class="chips">${fillerEntries.map(([word, count]) => `<span>${escapeHtml(word)}: ${count}</span>`).join("")}</div>`
          : "<p>반복 감지된 습관어가 없습니다.</p>"
      }
    </div>

    ${feedbackList("좋은 점", result.feedback.strengths)}
    ${feedbackList("개선할 점", result.feedback.improvements)}
    ${feedbackList("다음 연습", result.feedback.practiceTasks)}
  `;
}

function metric(label, value) {
  return `
    <div class="metric">
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(String(value))}</strong>
    </div>
  `;
}

function feedbackList(title, items) {
  return `
    <div class="report-section">
      <h2>${escapeHtml(title)}</h2>
      <ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
    </div>
  `;
}

function escapeHtml(value) {
  return value.replace(/[&<>"']/g, (char) => {
    const entities = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#039;",
    };
    return entities[char];
  });
}
