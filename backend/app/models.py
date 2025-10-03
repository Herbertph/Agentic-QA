from sqlalchemy import Column, Integer, String
from .database import Base

# Exemplo inicial: tabela de "Questions"
# (no futuro teremos outras tabelas)
class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    answer = Column(String)
