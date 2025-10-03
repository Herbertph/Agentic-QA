from sqlalchemy import Column, Integer, String
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
