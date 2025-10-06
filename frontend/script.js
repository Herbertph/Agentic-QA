const sendBtn = document.getElementById("sendBtn");
const resetBtn = document.getElementById("resetBtn");
const questionInput = document.getElementById("question");
const responseDiv = document.getElementById("response");

const API_URL = "http://127.0.0.1:8000/ask"; // seu backend local

sendBtn.addEventListener("click", async (event) => {
  event.preventDefault(); // evita qualquer reload
  const userQuestion = questionInput.value.trim();
  if (!userQuestion) {
    alert("Digite uma pergunta primeiro!");
    return;
  }

  // mostra status de carregamento
  responseDiv.innerHTML = "<em>Consultando agente...</em>";

  try {
    const res = await fetch(`${API_URL}?user_question=${encodeURIComponent(userQuestion)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });

    if (!res.ok) {
      throw new Error(`Erro ${res.status}: falha ao consultar a API`);
    }

    const data = await res.json();

    // impede que o texto seja apagado
    questionInput.value = userQuestion;

    // exibe resposta

    const answer = data.ai_answer || "❓ Nenhuma resposta encontrada. O agente local foi notificado.";
const context = data.context_used || "Sem contexto correspondente.";
const score = data.context_match_score ? `${(data.context_match_score * 100).toFixed(2)}%` : "N/A";

    responseDiv.innerHTML = `
  <strong>💬 Resposta:</strong><br>${answer}<br><br>
  <small><strong>📘 Contexto usado:</strong> ${context}</small><br>
  <small><strong>📊 Similaridade:</strong> ${score}</small>
`;
  } catch (err) {
    console.error(err);
    responseDiv.innerHTML = `<span style="color:red;">Erro: ${err.message}</span>`;
  }
});

// reset só limpa quando clicado
resetBtn.addEventListener("click", (event) => {
  event.preventDefault();
  questionInput.value = "";
  responseDiv.innerHTML = "";
});
