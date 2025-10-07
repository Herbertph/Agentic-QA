from fastapi import FastAPI, Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session
from . import models, schemas, crud, database, utils
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import json
import os

# 🔹 Carregar variáveis do .env
load_dotenv()

# Criar as tabelas no banco
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# 🔹 Permitir acesso do frontend local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # você pode restringir depois, ex: ["http://127.0.0.1:5500"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 Dependência para abrir/fechar sessão
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 🔹 Verificação do ADMIN_KEY
async def verify_admin(request: Request, admin_key: str = Header(None)):
    # aceita Admin-Key, admin_key, ou adminkey
    key = (
        request.headers.get("Admin-Key")
        or request.headers.get("admin_key")
        or request.headers.get("adminkey")
    )
    if key != os.getenv("ADMIN_KEY"):
        raise HTTPException(status_code=403, detail="Invalid ADMIN_KEY")

# -------------------------
# 👥 Usuário comum
# -------------------------
@app.get("/")
def read_root():
    return {"message": "Agent API is running with embeddings ready!"}

@app.post("/ask")
def ask_question(user_question: str, db: Session = Depends(get_db)):
    try:
        # 1️⃣ Gera embedding da pergunta do usuário
        user_embedding = utils.get_embedding(user_question)
        if not user_embedding:
            raise Exception("Falha ao gerar embedding")

        # --------------------------
        # 2️⃣ Busca nas perguntas do banco
        # --------------------------
        all_embeddings = db.query(models.QuestionEmbedding).all()
        question_match = None
        question_score = -1.0

        if all_embeddings:
            similarities = []
            for emb in all_embeddings:
                score = utils.cosine_similarity(user_embedding, json.loads(emb.embedding))
                similarities.append((emb, score))

            best_match, best_score = max(similarities, key=lambda x: x[1])
            if best_score >= 0.85:  # limiar de confiança
                question_match = db.query(models.Question).filter(models.Question.id == best_match.question_id).first()
                question_score = best_score

        # --------------------------
        # 3️⃣ Busca nos documentos (PDFs)
        # --------------------------
        pdf_match = None
        pdf_score = -1.0

        all_chunks = db.query(models.DocumentChunk).all()
        if all_chunks:
            similarities = []
            for chunk in all_chunks:
                score = utils.cosine_similarity(user_embedding, json.loads(chunk.embedding))
                similarities.append((chunk, score))

            best_chunk, best_chunk_score = max(similarities, key=lambda x: x[1])
            if best_chunk_score >= 0.83:
                pdf_match = best_chunk
                pdf_score = best_chunk_score

        # --------------------------
        # 4️⃣ Define qual resposta usar
        # --------------------------
        # Caso 1: encontrou pergunta no banco
        if question_match and question_score >= 0.85:
            return {
                "context_match_score": round(question_score, 3),
                "context_used": question_match.text,
                "ai_answer": question_match.answer,
            }

        # Caso 2: encontrou resposta em PDF
        elif pdf_match and pdf_score >= 0.83:
            return {
                "context_match_score": round(pdf_score, 3),
                "context_used": f"Trecho do documento: {pdf_match.source_name}",
                "ai_answer": pdf_match.content[:600] + "..."  # limita o tamanho da resposta
            }

        # Caso 3: nada encontrado
        unanswered = models.UnansweredQuestion(text=user_question)
        db.add(unanswered)
        db.commit()

        return {
            "context_match_score": 0,
            "context_used": None,
            "ai_answer": "❓ I don’t have this answer now. Please check with one of the leads.",
        }

    except Exception as e:
        print("Erro interno:", e)
        return {
            "context_match_score": 0,
            "context_used": None,
            "ai_answer": f"⚠️ Erro interno: {str(e)}",
        }



@app.get("/questions/", response_model=list[schemas.Question])
def read_questions(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_questions(db, skip=skip, limit=limit)

@app.get("/questions/{question_id}", response_model=schemas.Question)
def read_question(question_id: int, db: Session = Depends(get_db)):
    db_question = crud.get_question(db, question_id=question_id)
    if db_question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return db_question

# -------------------------
# 🔑 Admin - Respondidas
# -------------------------
@app.post("/admin/questions/", response_model=schemas.Question, dependencies=[Depends(verify_admin)])
def create_question_admin(question: schemas.QuestionCreate, db: Session = Depends(get_db)):
    return crud.create_question(db=db, question=question)

@app.put("/admin/questions/{question_id}", response_model=schemas.Question, dependencies=[Depends(verify_admin)])
def update_question_admin(question_id: int, updated: schemas.QuestionCreate, db: Session = Depends(get_db)):
    db_question = crud.update_question(db, question_id, updated)
    if not db_question:
        raise HTTPException(status_code=404, detail="Question not found")
    return db_question

@app.delete("/admin/questions/{question_id}", dependencies=[Depends(verify_admin)])
def delete_question_admin(question_id: int, db: Session = Depends(get_db)):
    db_question = crud.delete_question(db, question_id)
    if not db_question:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"message": f"Question {question_id} deleted successfully"}

# -------------------------
# 🔑 Admin - Pendentes
# -------------------------
@app.get("/admin/unanswered/", response_model=list[schemas.Unanswered], dependencies=[Depends(verify_admin)])
def read_unanswered(db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    return crud.get_unanswered(db, skip=skip, limit=limit)

@app.delete("/admin/unanswered/{unanswered_id}", dependencies=[Depends(verify_admin)])
def delete_unanswered(unanswered_id: int, db: Session = Depends(get_db)):
    db_question = crud.delete_unanswered(db, unanswered_id)
    if not db_question:
        raise HTTPException(status_code=404, detail="Unanswered question not found")
    return {"message": f"Unanswered question {unanswered_id} deleted successfully"}
