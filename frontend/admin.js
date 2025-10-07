const API_URL = "http://127.0.0.1:8000";
const adminKeyInput = document.getElementById("adminKey");
const loadBtn = document.getElementById("loadBtn");
const unansweredList = document.getElementById("unansweredList");

// 🔄 Carrega perguntas não respondidas
loadBtn.addEventListener("click", async () => {
  const adminKey = adminKeyInput.value.trim();
  if (!adminKey) {
    alert("Digite sua Admin Key!");
    return;
  }

  unansweredList.innerHTML = "<em>Carregando perguntas...</em>";

  try {
    const res = await fetch(`${API_URL}/admin/unanswered/`, {
      headers: { "admin_key": adminKey },
    });

    if (!res.ok) throw new Error("Falha ao buscar perguntas.");

    const data = await res.json();

    if (data.length === 0) {
      unansweredList.innerHTML = "<p>✅ Nenhuma pergunta pendente!</p>";
      return;
    }

    unansweredList.innerHTML = data
  .map(
    (q) => `
      <div class="question-item" id="question-${q.id}">
        <p><strong>❓ ${q.text}</strong></p>
        <textarea id="answer-${q.id}" placeholder="Digite a resposta aqui..."></textarea>
        <div class="btn-row">
          <button onclick="sendAnswer(${q.id})" class="save-btn">💾 Salvar</button>
          <button onclick="deleteQuestion(${q.id})" class="delete-btn">🗑️ Apagar</button>
        </div>
      </div>
    `
  )
  .join("");
  } catch (err) {
    unansweredList.innerHTML = `<p style="color:red;">Erro: ${err.message}</p>`;
  }
});

// 💾 Envia resposta
async function sendAnswer(id) {
  const adminKey = adminKeyInput.value.trim();
  const textarea = document.getElementById(`answer-${id}`);
  const answer = textarea.value.trim();

  if (!answer) {
    alert("Digite uma resposta antes de salvar!");
    return;
  }

  try {
    const res = await fetch(`${API_URL}/admin/questions/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "admin_key": adminKey,
      },
      body: JSON.stringify({
        text: document.querySelector(`p strong`).innerText.replace("❓ ", ""),
        answer: answer,
      }),
    });

    if (!res.ok) throw new Error("Falha ao salvar resposta.");

    await fetch(`${API_URL}/admin/unanswered/${id}`, {
      method: "DELETE",
      headers: { "admin_key": adminKey },
    });

    alert("✅ Resposta salva com sucesso!");
    textarea.parentElement.remove();
  } catch (err) {
    alert("❌ Erro ao salvar: " + err.message);
  }
}

// 🗑️ Deleta pergunta
async function deleteQuestion(id) {
  const adminKey = adminKeyInput.value.trim();
  if (!confirm("Tem certeza que deseja excluir esta pergunta?")) return;

  try {
    const res = await fetch(`${API_URL}/admin/unanswered/${id}`, {
      method: "DELETE",
      headers: { "Admin-Key": adminKey },
    });

    if (!res.ok) throw new Error("Falha ao apagar pergunta.");

    document.getElementById(`question-${id}`).remove();
    alert("🗑️ Pergunta removida com sucesso!");
  } catch (err) {
    alert("❌ Erro ao apagar: " + err.message);
  }
}
