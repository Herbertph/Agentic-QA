## Agentic-QA — Backend Documentation

AI Agent backend for a QA team, built with `FastAPI`, `SQLAlchemy` and local embeddings via an Ollama server.

### Stack
- FastAPI (ASGI)
- Uvicorn
- SQLAlchemy + SQLite (`backend/agent.db`)
- Pydantic
- Ollama for embeddings (`nomic-embed-text`) and optional generation (`llama3`)

### Directory layout
- `backend/app/main.py`: FastAPI application and routes
- `backend/app/models.py`: SQLAlchemy models
- `backend/app/schemas.py`: Pydantic schemas
- `backend/app/crud.py`: Data access and embedding maintenance
- `backend/app/utils.py`: Embeddings, similarity, local model utilities
- `backend/app/pdf_indexer.py`: Index PDFs into `DocumentChunk` with embeddings
- `backend/app/refresh_embeddings.py`: Rebuild question embeddings
- `backend/agent.db`: SQLite database
- `backend/requirements.txt`: Python dependencies
- `backend/Dockerfile`: Container image definition

## Prerequisites
- Python 3.11+
- [Ollama](https://ollama.com) running locally (or reachable over HTTP)
  - Ensure the `nomic-embed-text` model is available for embeddings
  - Optional: `llama3` for generation in `utils.query_local_ai`

## Environment variables
Create a `.env` file in `backend/` with:

```env
ADMIN_KEY=change-me
LLAMA_URL=http://localhost:11434
```

- `ADMIN_KEY`: required for all `/admin/*` endpoints via header (`Admin-Key`, `admin_key`, or `adminkey`).
- `LLAMA_URL`: base URL of your Ollama server.

## Install (local)
From the repository root:

```bash
cd backend
python -m venv venv
./venv/Scripts/Activate.ps1   # PowerShell on Windows
pip install -r requirements.txt
```

Initialize the database tables automatically on first run (no manual migration needed).

## Run (local)
With the virtual environment activated and from `backend/`:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive API docs:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Run with Docker
From `backend/`:

```bash
docker build -t agentic-qa-backend .
docker run --rm -p 8000:8000 --env-file .env -v %cd%/agent.db:/app/agent.db agentic-qa-backend
```

Notes:
- Bind-mounting `agent.db` is optional; omit the `-v` flag to keep DB inside the container.
- Ensure the container can reach `LLAMA_URL` (default assumes Ollama on the host).

## PDF indexing
Place PDFs in `backend/pdfs/` and run the indexer to extract text, chunk it, and store embeddings in `DocumentChunk`:

```bash
cd backend
python -m app.pdf_indexer
```

The script uses chunk size of 500 words and will retry commits to handle SQLite locks.

## Refresh question embeddings
If you edited existing answered questions manually, rebuild their embeddings:

```bash
cd backend
python -m app.refresh_embeddings
```

## Database
- SQLite file lives at `backend/agent.db`.
- Connection URL: `sqlite:///./agent.db` (relative to the `backend/` working directory).

## API Reference

Base URL: `http://localhost:8000`

### Health
- Method: GET
- Path: `/`
- Response:

```json
{ "message": "Agent API is running with embeddings ready!" }
```

### Ask a question
- Method: POST
- Path: `/ask`
- Query parameters:
  - `user_question` (string, required)
- Responses:
  - 200 JSON — one of:

```json
{ "context_match_score": 0.91, "context_used": "the matched question text", "ai_answer": "the stored answer" }
```

```json
{ "context_match_score": 0.62, "context_used": "Excerpt of the PDF: file.pdf", "ai_answer": "truncated chunk..." }
```

```json
{ "context_match_score": 0, "context_used": null, "ai_answer": "❓ I don’t have this answer now. Please check with one of the leads." }
```

On internal error:

```json
{ "context_match_score": 0, "context_used": null, "ai_answer": "⚠️ Internal Error: <details>" }
```

### List answered questions
- Method: GET
- Path: `/questions/`
- Query parameters: `skip` (int, default 0), `limit` (int, default 10)
- Response (200):

```json
[ { "id": 1, "text": "...", "answer": "..." } ]
```

### Get one answered question
- Method: GET
- Path: `/questions/{question_id}`
- Response (200):

```json
{ "id": 1, "text": "...", "answer": "..." }
```

404 if not found.

### Admin — headers
All admin endpoints require a header with the configured `ADMIN_KEY` (any of these names are accepted):

```http
Admin-Key: <your-admin-key>
```

or `admin_key` or `adminkey`.

### Admin — create answered question
- Method: POST
- Path: `/admin/questions/`
- Headers: `Admin-Key: <ADMIN_KEY>`
- Body:

```json
{ "text": "question text", "answer": "answer text" }
```

- Response (200): created question object. Also creates/updates its embedding.

### Admin — update answered question
- Method: PUT
- Path: `/admin/questions/{question_id}`
- Headers: `Admin-Key: <ADMIN_KEY>`
- Body:

```json
{ "text": "new question text", "answer": "new answer" }
```

- Response (200): updated question object, with embedding refreshed.

### Admin — delete answered question
- Method: DELETE
- Path: `/admin/questions/{question_id}`
- Headers: `Admin-Key: <ADMIN_KEY>`
- Response (200):

```json
{ "message": "Question <id> deleted successfully" }
```

### Admin — list unanswered questions
- Method: GET
- Path: `/admin/unanswered/`
- Headers: `Admin-Key: <ADMIN_KEY>`
- Query parameters: `skip`, `limit`
- Response (200):

```json
[ { "id": 10, "text": "user question that had no match" } ]
```

### Admin — delete unanswered question
- Method: DELETE
- Path: `/admin/unanswered/{unanswered_id}`
- Headers: `Admin-Key: <ADMIN_KEY>`
- Response (200):

```json
{ "message": "Unanswered question <id> deleted successfully" }
```

## CORS
The API is configured to allow all origins, methods, and headers. Adjust in `app.main` if you need stricter policies.

## Notes and tips
- `/ask` expects the `user_question` as a query parameter even though it’s a POST; this matches the current FastAPI signature.
- Embedding thresholds: 0.85 for existing answered questions; 0.45 for PDF chunks. Tune as needed in `app.main`.
