import json
from sqlalchemy.orm import Session
from app import database, models, utils

# Cria as tabelas se não existirem
models.Base.metadata.create_all(bind=database.engine)

# Abre conexão com o banco
db: Session = database.SessionLocal()

print("🔄 Atualizando embeddings das perguntas existentes...\n")

questions = db.query(models.Question).all()
updated = 0

for q in questions:
    print(f"➡️ Gerando embedding para: '{q.text}'")
    emb = utils.get_embedding(q.text)

    if not emb:
        print(f"⚠️ Falha ao gerar embedding para '{q.text}'")
        continue

    # Verifica se já existe registro de embedding
    existing = db.query(models.QuestionEmbedding).filter_by(question_id=q.id).first()
    if existing:
        existing.embedding = json.dumps(emb)
    else:
        new_emb = models.QuestionEmbedding(question_id=q.id, embedding=json.dumps(emb))
        db.add(new_emb)

    updated += 1
    db.commit()

print(f"\n✅ {updated} embeddings atualizados com sucesso.")
db.close()
