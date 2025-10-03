from pydantic import BaseModel

# Schema de leitura (saída)
class QuestionBase(BaseModel):
    text: str
    answer: str

# Schema de criação (entrada)
class QuestionCreate(QuestionBase):
    pass

# Schema completo (inclui ID do banco)
class Question(QuestionBase):
    id: int

    class Config:
        orm_mode = True
