from sqlalchemy import Column, Integer, String, ForeignKey
from .database import Base

# -------------------------
# Perguntas respondidas
# -------------------------
class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    answer = Column(String)

# -------------------------
# Perguntas pendentes
# -------------------------
class UnansweredQuestion(Base):
    __tablename__ = "unanswered_questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)

# -------------------------
# Embeddings (para busca semântica)
# -------------------------
class QuestionEmbedding(Base):
    __tablename__ = "question_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), unique=True)
    embedding = Column(String)  # será uma string JSON com os números do vetor