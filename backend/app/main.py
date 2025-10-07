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

        # 2️⃣ Busca todos os embeddings do banco
        all_embeddings = db.query(models.QuestionEmbedding).all()
        if not all_embeddings:
            unanswered = models.UnansweredQuestion(text=user_question)
            db.add(unanswered)
            db.commit()
            return {
                "context_match_score": 0,
                "context_used": None,
                "ai_answer": "❓ I don’t have this answer now. Please check with one of the leads.",
            }

        # 3️⃣ Calcula similaridades
        similarities = []
        for emb in all_embeddings:
            score = utils.cosine_similarity(user_embedding, json.loads(emb.embedding))
            similarities.append((emb, score))

        # 4️⃣ Encontra o melhor match
        best_match, best_score = max(similarities, key=lambda x: x[1])

        # 5️⃣ Define limiar dinâmico
        limiar = 0.9
        if len(user_question.split()) <= 10:
            limiar = 0.85

        # 6️⃣ Se houver correspondência suficiente → usa resposta do banco
        if best_score >= limiar:
            question = db.query(models.Question).filter(models.Question.id == best_match.question_id).first()
            return {
                "context_match_score": round(best_score, 3),
                "context_used": question.text,
                "ai_answer": question.answer,
            }

        # 7️⃣ Caso contrário → salva no banco como sem resposta
        unanswered = models.UnansweredQuestion(text=user_question)
        db.add(unanswered)
        db.commit()

        # 🔒 Retorna resposta padrão — sem IA, sem sumiço
        return {
            "context_match_score": round(best_score, 3),
            "context_used": None,
            "ai_answer": "❓ I don’t have this answer now. Please check with one of the leads.",
        }

    except Exception as e:
        print("Erro interno:", e)
        # 🔒 Garante que o frontend sempre receba algo
        return {
            "context_match_score": 0,
            "context_used": None,
            "ai_answer": f"⚠️ Internal error: {str(e)}" if str(e) else "⚠️ Unknown internal error.",
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
