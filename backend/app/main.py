from fastapi import FastAPI
from . import models, database

# Cria todas as tabelas no banco (caso não existam)
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, Agent is running with DB!"}
