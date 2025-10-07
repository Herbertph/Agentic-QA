from sqlalchemy import Column, Integer, String, ForeignKey, Text
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

# -------------------------
# Trechos de documentos (PDFs)
# -------------------------
class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String, nullable=False)       # nome do PDF
    content = Column(Text, nullable=False)             # texto do trecho
    embedding = Column(Text, nullable=False)           # embedding JSON