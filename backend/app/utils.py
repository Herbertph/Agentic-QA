from sentence_transformers import SentenceTransformer
import numpy as np
import json

# carregar modelo uma vez
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
