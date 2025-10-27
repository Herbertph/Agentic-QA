from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Caminho do banco de dados SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./data/agent.db"

# Criando o engine (responsável pela conexão com o banco)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# SessionLocal será usada para abrir conexões (sessions) com o banco
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base que todos os modelos (tabelas) vão herdar
Base = declarative_base()