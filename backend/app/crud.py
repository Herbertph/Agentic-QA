from sqlalchemy.orm import Session
from . import models, schemas

# Criar pergunta
def create_question(db: Session, question: schemas.QuestionCreate):
    db_question = models.Question(text=question.text, answer=question.answer)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question

# Buscar todas perguntas
def get_questions(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Question).offset(skip).limit(limit).all()

# Buscar uma pergunta por ID
def get_question(db: Session, question_id: int):
    return db.query(models.Question).filter(models.Question.id == question_id).first()
