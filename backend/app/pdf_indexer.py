import fitz  # PyMuPDF
import os
import json
import time
import sqlite3
from sqlalchemy.orm import Session
from sqlalchemy import text
from app import database, models, utils
from tqdm import tqdm

CHUNK_SIZE = 500  # número de palavras por bloco


def safe_commit(db, retries=5, delay=1):
    """Evita o erro 'database is locked' com tentativas automáticas."""
    for attempt in range(retries):
        try:
            db.commit()
            return
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e).lower():
                print(f"⚠️ Banco bloqueado, aguardando {delay}s (tentativa {attempt + 1}/{retries})...")
                time.sleep(delay)
            else:
                raise
    raise RuntimeError("❌ Falha ao gravar no banco após múltiplas tentativas.")


def split_text(text, chunk_size=CHUNK_SIZE):
    """Divide o texto em blocos de tamanho fixo."""
    words = text.split()
    return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]


def process_pdf(file_path: str):
    """Extrai texto do PDF e salva os embeddings no banco, isoladamente por arquivo."""
    db = database.SessionLocal()

    # 🔧 Ativa o modo WAL com retry (evita travamentos do SQLite)
    for attempt in range(5):
        try:
            db.connection().connection.execute("PRAGMA journal_mode=WAL;")
            break
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower():
                print(f"⚠️ Banco bloqueado, tentando novamente em 2s... (tentativa {attempt + 1}/5)")
                time.sleep(2)
            else:
                raise

    try:
        doc = fitz.open(file_path)
        all_text = ""

        for page in doc:
            all_text += page.get_text("text") + "\n"

        chunks = split_text(all_text)
        source_name = os.path.basename(file_path)

        print(f"📘 Indexando '{source_name}' com {len(chunks)} blocos...")

        for chunk in tqdm(chunks, desc=f"Gerando embeddings → {source_name}"):
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

        safe_commit(db)
        print(f"✅ Indexação completa para {source_name}!")

    except Exception as e:
        print(f"❌ Erro ao processar {file_path}: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    folder = "pdfs"  # pasta onde estão os PDFs
    os.makedirs(folder, exist_ok=True)

    pdf_files = [f for f in os.listdir(folder) if f.endswith(".pdf")]
    print(f"📁 Encontrados {len(pdf_files)} PDFs na pasta '{folder}'.")

    for filename in pdf_files:
        file_path = os.path.join(folder, filename)
        process_pdf(file_path)

    print("🎯 Indexação finalizada para todos os PDFs!")
