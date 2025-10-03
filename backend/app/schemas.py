from pydantic import BaseModel

# -------------------------
# Respondidas
# -------------------------
class QuestionBase(BaseModel):
    text: str
    answer: str

class QuestionCreate(QuestionBase):
    pass

class Question(QuestionBase):
    id: int
    class Config:
        orm_mode = True

# -------------------------
# Pendentes
# -------------------------
class UnansweredBase(BaseModel):
    text: str

class UnansweredCreate(UnansweredBase):
    pass

class Unanswered(UnansweredBase):
    id: int
    class Config:
        orm_mode = True
