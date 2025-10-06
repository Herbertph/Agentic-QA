from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from . import models, schemas, crud, database
from dotenv import load_dotenv
from . import utils
import os

# 🔹 Carregar variáveis do .env
load_dotenv()

# Criar as tabelas no banco
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# 🔹 Dependência para abrir/fechar sessão
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 🔹 Verificação do ADMIN_KEY
def verify_admin(admin_key: str = Header(...)):
    if admin_key != os.getenv("ADMIN_KEY"):
        raise HTTPException(status_code=403, detail="Invalid ADMIN_KEY")

# -------------------------
# 👥 Usuário comum
# -------------------------
@app.get("/")
def read_root():
    return {"message": "Agent API is running with embeddings ready!"}

@app.post("/ask")
def ask_question(user_question: str, db: Session = Depends(get_db)):
    # 1️⃣ Gerar embedding da pergunta do usuário
    user_embedding = utils.get_embedding(user_question)

    # 2️⃣ Buscar todas embeddings salvas
    db_embeddings = db.query(models.QuestionEmbedding).all()
    if not db_embeddings:
        crud.create_unanswered(db, user_question)
        return {"answer": "Ainda não tenho uma resposta para isso. Procure um lead."}

    # 3️⃣ Calcular similaridade e encontrar a mais próxima
    similarities = []
    for e in db_embeddings:
        stored_vec = utils.deserialize_embedding(e.embedding)
        sim = utils.cosine_similarity(user_embedding, stored_vec)
        similarities.append((e.question_id, sim))

    # 4️⃣ Ordenar por similaridade
    similarities.sort(key=lambda x: x[1], reverse=True)
    best_match_id, best_score = similarities[0]

    # 5️⃣ Se a similaridade for baixa, salvar como pendente
    if best_score < 0.75:
        crud.create_unanswered(db, user_question)
        return {"answer": "Ainda não tenho uma resposta para isso. Procure um lead."}

    # 6️⃣ Buscar a pergunta/resposta correspondente
    best_question = crud.get_question(db, best_match_id)

    # 7️⃣ Criar o prompt com contexto e perguntar à IA local
    context = f"Base de conhecimento:\nPergunta: {best_question.text}\nResposta: {best_question.answer}"
    prompt = f"{context}\n\nPergunta do usuário: {user_question}\n\nBaseando-se APENAS no contexto acima, responda de forma clara e objetiva."

    ai_answer = utils.query_ollama(prompt)

    return {
        "context_match_score": round(float(best_score), 3),
        "context_used": best_question.text,
        "ai_answer": ai_answer
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
