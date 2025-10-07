const sendBtn = document.getElementById("sendBtn");
const resetBtn = document.getElementById("resetBtn");
const questionInput = document.getElementById("question");
const responseDiv = document.getElementById("response");

const API_URL = "http://127.0.0.1:8000/ask";

let isProcessing = false;

sendBtn.addEventListener("click", async (event) => {
  event.preventDefault(); // evita qualquer reload ou repaint
  event.stopPropagation(); // impede eventos do container

  if (isProcessing) return;

  const userQuestion = questionInput.value.trim();
  if (!userQuestion) {
    alert("Digite uma pergunta primeiro!");
    return;
  }

  // Mostra status de carregamento
  responseDiv.innerHTML = "<em>⌛ Consultando agente...</em>";
  isProcessing = true;
  sendBtn.disabled = true;

  try {
    const res = await fetch(`${API_URL}?user_question=${encodeURIComponent(userQuestion)}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    cache: "no-cache"
  });

  const data = await res.json();

  // Garante que a resposta sempre persista
  const safe = data || {};
  const answer = safe.ai_answer || "❓ I don’t have this answer now. Please check with one of the leads.";
  const context = safe.context_used || "Sem contexto correspondente.";
  const score = (typeof safe.context_match_score === "number")
    ? `${(safe.context_match_score * 100).toFixed(2)}%`
    : "N/A";

  responseDiv.innerHTML = `
    <div style="white-space: pre-wrap;">
      <strong>💬 Resposta:</strong><br>${answer}<br><br>
      <small><strong>📘 Contexto usado:</strong> ${context}</small><br>
      <small><strong>📊 Similaridade:</strong> ${score}</small>
    </div>
  `;
} catch (err) {
  console.error("⚠️ Erro:", err);
  responseDiv.innerHTML = `<span style="color:red;">Erro: ${err.message}</span>`;
} finally {
    isProcessing = false;
    sendBtn.disabled = false;
  }
});

resetBtn.addEventListener("click", (event) => {
  event.preventDefault();
  event.stopPropagation();
  questionInput.value = "";
  responseDiv.innerHTML = "";
});

// Impede que Enter recarregue a página dentro do textarea
questionInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && e.ctrlKey) {
    sendBtn.click(); // Ctrl+Enter envia a pergunta
  } else if (e.key === "Enter") {
    e.preventDefault();
  }
});
