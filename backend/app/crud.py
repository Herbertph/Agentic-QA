from sqlalchemy.orm import Session
from . import models, schemas, utils
import json

# -------------------------
# Respondidas
# -------------------------
def create_question(db: Session, question: schemas.QuestionCreate):
    # Criar pergunta
    db_question = models.Question(text=question.text, answer=question.answer)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)

    # Criar embedding
    embedding = utils.get_embedding(question.text)
    db_embedding = models.QuestionEmbedding(
        question_id=db_question.id,
        embedding=utils.serialize_embedding(embedding)
    )
    db.add(db_embedding)
    db.commit()

    return db_question


def get_questions(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Question).offset(skip).limit(limit).all()


def get_question(db: Session, question_id: int):
    return db.query(models.Question).filter(models.Question.id == question_id).first()


def get_question_by_text(db: Session, text: str):
    return db.query(models.Question).filter(models.Question.text == text).first()


def update_question(db: Session, question_id: int, updated: schemas.QuestionCreate):
    db_question = get_question(db, question_id)
    if not db_question:
        return None
    db_question.text = updated.text
    db_question.answer = updated.answer
    db.commit()
    db.refresh(db_question)

    # Atualizar embedding
    embedding = utils.get_embedding(updated.text)
    db_embedding = db.query(models.QuestionEmbedding).filter(
        models.QuestionEmbedding.question_id == question_id
    ).first()
    if db_embedding:
        db_embedding.embedding = utils.serialize_embedding(embedding)
    else:
        db_embedding = models.QuestionEmbedding(
            question_id=question_id,
            embedding=utils.serialize_embedding(embedding)
        )
        db.add(db_embedding)
    db.commit()

    return db_question


def delete_question(db: Session, question_id: int):
    db_question = get_question(db, question_id)
    if not db_question:
        return None

    # Deletar embedding associado
    db_embedding = db.query(models.QuestionEmbedding).filter(
        models.QuestionEmbedding.question_id == question_id
    ).first()
    if db_embedding:
        db.delete(db_embedding)

    db.delete(db_question)
    db.commit()
    return db_question

# -------------------------
# Pendentes
# -------------------------
def create_unanswered(db: Session, text: str):
    db_unanswered = models.UnansweredQuestion(text=text)
    db.add(db_unanswered)
    db.commit()
    db.refresh(db_unanswered)
    return db_unanswered


def get_unanswered(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.UnansweredQuestion).offset(skip).limit(limit).all()


def delete_unanswered(db: Session, unanswered_id: int):
    db_question = db.query(models.UnansweredQuestion).filter(
        models.UnansweredQuestion.id == unanswered_id
    ).first()
    if not db_question:
        return None
    db.delete(db_question)
    db.commit()
    return db_question
