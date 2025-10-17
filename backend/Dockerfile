# Etapa 1: Builder — instala dependências com cache
FROM python:3.11-slim AS builder

WORKDIR /install
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --user -r requirements.txt

# Etapa 2: Runtime — imagem leve e limpa
FROM python:3.11-slim
WORKDIR /app
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Copia apenas dependências da etapa anterior
COPY --from=builder /root/.local /root/.local

# Copia o restante do código
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
