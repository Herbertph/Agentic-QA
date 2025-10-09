FROM python:3.11

# Definir diretório principal do app dentro do container
WORKDIR /app

# Tornar o diretório /app visível como raiz de importação do Python
ENV PYTHONPATH=/app

# Copiar dependências e instalar
COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o conteúdo do backend (inclusive a pasta app/)
COPY . .

# Expor a porta usada pelo backend
EXPOSE 8000

# Iniciar o servidor apontando para app.main:app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]