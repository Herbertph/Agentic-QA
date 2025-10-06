from sentence_transformers import SentenceTransformer
import numpy as np
import json
import requests

# carregar modelo de embeddings
model = SentenceTransformer("all-MiniLM-L6-v2")

def get_embedding(text: str) -> list:
    """Gera embedding para um texto"""
    embedding = model.encode(text)
    return embedding.tolist()

def serialize_embedding(embedding: list) -> str:
    """Transforma lista em string JSON para salvar no banco"""
    return json.dumps(embedding)

def deserialize_embedding(embedding_str: str) -> np.ndarray:
    """Transforma string JSON em vetor numpy"""
    return np.array(json.loads(embedding_str))

def cosine_similarity(vec1, vec2):
    """Calcula similaridade de cosseno entre dois vetores"""
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def query_ollama(prompt: str, model_name: str = "llama3") -> str:
    """Consulta o modelo local via API do Ollama"""
    url = "http://localhost:11434/api/generate"
    payload = {"model": model_name, "prompt": prompt}
    try:
        response = requests.post(url, json=payload, stream=True)
        response.raise_for_status()
        full_response = ""
        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode("utf-8"))
                full_response += data.get("response", "")
        return full_response.strip()
    except Exception as e:
        print(f"❌ Erro ao consultar Ollama: {e}")
        return "Erro interno ao consultar o modelo local."
