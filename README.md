# FitFusion

Production-style fitness tracking app with a SvelteKit frontend, FastAPI backend, MongoDB persistence, Groq-powered LLaMA coaching, and gRPC communication between AI/calendar services.

## Stack

- Frontend: SvelteKit, TailwindCSS
- Backend: FastAPI, gRPC, PyMongo
- AI: Groq Chat Completions API with LLaMA
- Database: Local MongoDB

## Project Structure

```text
frontend/
backend/
```

## Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Set:

```bash
PUBLIC_API_BASE_URL=http://localhost:8000
```

## Backend Setup

```bash
cd backend
python -m venv .venv
iled pip install -r requirements.txt
cp .env.example .env
python -m uvicorn api.main:app --reload --port 8000
```

Set:

```bash
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=fitfusion
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama-3.1-8b-instant
GRPC_HOST=127.0.0.1
GRPC_PORT=50051
```

## Implemented Features

- Local profile selection with create, update, delete, and select flows
- Dashboard with BMI, workout summary, diet summary, and AI chat panel
- Monthly calendar with highlighted AI-generated tasks
- FastAPI routes for profiles, tasks, chat, and AI plan generation
- gRPC services for AI plan generation/chat and calendar task access
- MongoDB persistence for profiles and tasks

## API Routes

- `GET /profiles`
- `POST /profiles`
- `PUT /profiles/{id}`
- `DELETE /profiles/{id}`
- `GET /tasks/{profile_id}`
- `POST /tasks`
- `POST /generate-plan`
- `POST /chat`
