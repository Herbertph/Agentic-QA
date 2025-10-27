const sendBtn = document.getElementById("sendBtn");
const resetBtn = document.getElementById("resetBtn");
const questionInput = document.getElementById("question");
const responseDiv = document.getElementById("response");

const API_URL = `http://${window.location.hostname}:8000/ask`;

let isProcessing = false;

sendBtn.addEventListener("click", async (event) => {
  event.preventDefault();
  if (isProcessing) return;

  const userQuestion = questionInput.value.trim();
  if (!userQuestion) {
    alert("Type a question!");
    return;
  }

  responseDiv.innerHTML = "<em>⌛ Consulting...</em>";
  isProcessing = true;
  sendBtn.disabled = true;

  try {
    const res = await fetch(
      `${API_URL}?user_question=${encodeURIComponent(userQuestion)}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        cache: "no-cache",
      }
    );

    const data = await res.json();
    console.log("🧩 Backend response:", data); // mantém debug

    // ✅ Proteção contra campos ausentes
    const answer =
      data?.ai_answer && data.ai_answer.trim() !== ""
        ? data.ai_answer
        : "❓ I don’t have this answer now. Please check with one of the leads.";

    const score =
      typeof data?.context_match_score === "number"
        ? `${(data.context_match_score * 100).toFixed(2)}%`
        : "N/A";

    const context =
      data?.context_used && data.context_used !== "null"
        ? data.context_used
        : "No context available.";

    responseDiv.innerHTML = `
  <div class="response">
    <p><strong>💬 Answer:</strong></p>
    <div class="answer-line">${answer}</div>

    <p><strong>📊 Similarity:</strong> ${score}</p>
    <p><strong>🧩 Context:</strong> ${context}</p>
  </div>
    `;
  } catch (err) {
    console.error("⚠️ Error:", err);
    responseDiv.innerHTML = `<span style="color:red;">Error: ${err.message}</span>`;
  } finally {
    isProcessing = false;
    sendBtn.disabled = false;
  }
});

resetBtn.addEventListener("click", (e) => {
  e.preventDefault();
  questionInput.value = "";
  responseDiv.innerHTML = "";
});

questionInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendBtn.click();
  }
});
