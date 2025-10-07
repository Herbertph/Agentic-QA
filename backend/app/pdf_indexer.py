import fitz  # PyMuPDF
import os
import json
from sqlalchemy.orm import Session
from app import database, models, utils
from tqdm import tqdm

CHUNK_SIZE = 500  # número de palavras por bloco

def split_text(text, chunk_size=CHUNK_SIZE):
    words = text.split()
    return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

def process_pdf(file_path: str, db: Session):
    """Extrai texto do PDF e salva os embeddings no banco."""
    doc = fitz.open(file_path)
    all_text = ""

    for page in doc:
        all_text += page.get_text("text") + "\n"

    chunks = split_text(all_text)
    source_name = os.path.basename(file_path)

    print(f"📘 Indexando '{source_name}' com {len(chunks)} blocos...")

    for chunk in tqdm(chunks, desc="Gerando embeddings"):
        embedding = utils.get_embedding(chunk)
        if not embedding:
            print(f"⚠️ Falha ao gerar embedding para um bloco em {source_name}")
            continue

        db_chunk = models.DocumentChunk(
            source_name=source_name,
            content=chunk,
            embedding=json.dumps(embedding)
        )
        db.add(db_chunk)

    db.commit()
    print(f"✅ Indexação completa para {source_name}!")


if __name__ == "__main__":
    db = database.SessionLocal()
    folder = "pdfs"  # pasta onde estão os PDFs (crie ela no diretório raiz do backend)
    os.makedirs(folder, exist_ok=True)

    for filename in os.listdir(folder):
        if filename.endswith(".pdf"):
            file_path = os.path.join(folder, filename)
            process_pdf(file_path, db)

    db.close()
