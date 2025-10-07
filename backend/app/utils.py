import requests
import json
import numpy as np
import re
from sqlalchemy.orm import Session
import app.models as models


# 🔧 Normaliza o texto antes de gerar o embedding
def normalize_text(text: str):
    """
    Deixa o texto em minúsculo, remove pontuação e espaços extras.
    Isso ajuda o modelo a comparar frases parecidas de forma mais robusta.
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9áéíóúàãõç\s]", "", text)
    return text.strip()


# ✅ Gera embedding REAL com Ollama local (modelo nomic-embed-text)
def get_embedding(text: str):
    try:
        text = normalize_text(text)
        response = requests.post(
            "http://localhost:11434/api/embeddings",
            json={"model": "nomic-embed-text", "prompt": text},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        return data.get("embedding", [])
    except Exception as e:
        print("⚠️ Falha ao gerar embedding:", e)
        return None


# ✅ Calcula similaridade de cosseno
def cosine_similarity(vec1, vec2):
    v1 = np.array(vec1, dtype=float)
    v2 = np.array(vec2, dtype=float)

    if v1.size == 0 or v2.size == 0:
        return -1.0

    min_len = min(len(v1), len(v2))
    v1 = v1[:min_len]
    v2 = v2[:min_len]

    denom = np.linalg.norm(v1) * np.linalg.norm(v2)
    if denom == 0:
        return -1.0

    return float(np.dot(v1, v2) / denom)


# ✅ Busca a pergunta mais similar no banco
def find_most_similar(user_embedding, db: Session):
    questions = db.query(models.Question).all()
    if not questions:
        return None, 0.0

    best_question = None
    best_score = -1.0

    for q in questions:
        embedding_record = db.query(models.QuestionEmbedding).filter_by(question_id=q.id).first()
        if not embedding_record or not embedding_record.embedding:
            continue

        try:
            emb = json.loads(embedding_record.embedding)
            score = cosine_similarity(user_embedding, emb)
            if score > best_score:
                best_question = q
                best_score = score
        except Exception as e:
            print(f"⚠️ Erro comparando embeddings (ID {q.id}): {e}")
            continue

    return best_question, best_score


# ✅ Consulta ao modelo local (Llama3 via Ollama)
def query_local_ai(prompt: str, context: list[str] = []):
    try:
        context_text = "\n".join(context)
        full_prompt = f"Context:\n{context_text}\n\nQuestion:\n{prompt}\nAnswer concisely."

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3", "prompt": full_prompt, "stream": False},
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "").strip()
    except Exception as e:
        print("⚠️ Erro ao consultar modelo local:", e)
        return "⚠️ Erro interno ao consultar o modelo local."
