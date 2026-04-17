# FitFusion

## Project Title and Overview

FitFusion is a full-stack AI-powered fitness planner web application designed to help users create smarter workout and diet plans. It combines a modern SvelteKit frontend with a FastAPI backend, leverages MongoDB for persistent storage, and integrates a Groq LLaMA 3 8B Instant model for generative fitness planning. FitFusion is built as a generative AI-based fitness planning system that turns user goals, health metrics, and preferences into structured fitness guidance.

FitFusion is intended for users who want a guided fitness workflow with profile management, personalized planning, calendar organization, and conversational AI support.

## Features

- **User Profiles**: Create, update, and manage multiple personal profiles with fitness metadata like age, height, weight, and goals.
- **Dashboard Insights**: View BMI, workout recommendations, diet highlights, and plan summaries in one consolidated dashboard.
- **AI Chat Assistant**: Ask fitness planning questions through a chatbot interface powered by Groq LLaMA. The assistant provides guidance, explanations, and training recommendations.
- **Generative Plan Creation**: Generate tailored workout and diet plans from natural language prompts and stored profile information.
- **Calendar Planning**: Turn generated plans into scheduled tasks and visualize them in a monthly calendar view.
- **REST + gRPC Communication**: Use REST APIs for frontend/backend interactions and gRPC services for modular AI/chat and calendar operations.
- **Persistent Storage**: Store profiles and tasks in MongoDB for consistency across sessions.

## System Architecture

FitFusion uses a modular architecture to separate UI, API, AI, and persistence layers. This design keeps the application maintainable, scalable, and easier to extend.

- **Frontend**: SvelteKit application with TailwindCSS for styling and TypeScript for UI logic.
- **Backend**: FastAPI server handles business logic, REST endpoints, and data access.
- **AI Layer**: Groq LLaMA model is invoked through the Groq Chat Completions API for plan generation and chatbot responses.
- **Database**: MongoDB stores user profiles and generated task data.
- **gRPC Services**: Dedicated services manage AI operations and calendar task workflows separately from the REST API.

### Architecture Diagram

```text
User Browser
    │
    ├─ SvelteKit Frontend
    │    ├─ Dashboard UI
    │    ├─ Calendar UI
    │    ├─ Chatbot UI
    │    └─ Profile Management UI
    │
    ├─ REST API --> FastAPI Backend
    │                 ├─ Profile routes
    │                 ├─ Task routes
    │                 ├─ AI plan endpoint
    │                 └─ Chat endpoint
    │
    ├─ gRPC Services
    │    ├─ AI Service (Groq / LLaMA)
    │    └─ Calendar Service
    │
    └─ MongoDB
         ├─ Profiles collection
         └─ Tasks collection
```

## Methodology / Working Process

1. **User Input**: The user enters fitness profile details and selects goals within the UI.
2. **BMI Calculation**: The frontend or backend computes BMI from weight and height, then displays it on the dashboard.
3. **Prompt Engineering**: The backend constructs a prompt that includes user profile data, fitness goals, and preferred schedule details.
4. **AI Model Processing**: The prompt is sent to the Groq Chat Completions API using the LLaMA 3 8B Instant model.
5. **Plan Generation**: The LLM returns structured workout and diet recommendations, which are parsed and stored as plan data.
6. **Calendar Creation**: The app converts plan items into calendar tasks and schedules them in a month view.
7. **Chatbot Interaction**: Users can ask follow-up questions via the chatbot, which provides responses based on the same AI layer.

This process ensures that plan generation and scheduling are linked, while the chatbot remains available for guidance.

## Generative AI Pipeline

- **Prompt Construction**: Prompts combine profile context, fitness goals, current activity level, and user preferences.
- **LLM Inference**: The prompt is sent to Groq with the LLaMA 3 8B Instant model, which generates workout and diet suggestions.
- **Output Structure**: The model response is parsed into plan elements such as exercise routines, nutrition recommendations, and scheduling hints.
- **Task Mapping**: Generated plan elements are mapped into the task calendar system and persisted in MongoDB.

The pipeline is designed to deliver coherent plans with structured outputs suitable for UI rendering and task scheduling.

## Agentic AI Note

FitFusion currently uses a partially agentic design: the chatbot provides intelligent responses and generates plans, but it does not autonomously revise or update plans without explicit user input. Future versions may introduce more dynamic agentic behavior.

## Tech Stack

| Layer         | Technology                                | Purpose                                               |
| ------------- | ----------------------------------------- | ----------------------------------------------------- |
| Frontend      | SvelteKit, TailwindCSS, TypeScript, Vite  | UI rendering and client interaction                   |
| Backend       | Python, FastAPI, Pydantic                 | REST API, business logic, service orchestration       |
| AI            | Groq Chat Completions, LLaMA 3 8B Instant | Generative plan creation and conversational assistant |
| Database      | MongoDB, PyMongo                          | Persistent storage for profiles and tasks             |
| Communication | REST, gRPC                                | API and service integration                           |

## Folder Structure

- `frontend/` — SvelteKit application, UI components, Svelte stores, and frontend services.
- `backend/` — FastAPI server logic, routing, database integration, and service implementations.
  - `api/` — API entrypoints and request handling.
  - `grpc/` — gRPC service definitions and bootstrap logic.
  - `models/` — Domain models for users and tasks.
  - `rpc/` — RPC client and server coordination.
  - `services/` — AI, calendar, and serializer helpers.

## Installation & Setup

### Prerequisites

- Node.js and npm
- Python 3.11+ (or compatible Python 3.x)
- MongoDB instance
- Groq API key

### Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file and configure the required environment variables:

```bash
cp .env.example .env
```

Example `backend/.env` values:

```bash
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=fitfusion
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.1-8b-instant
GRPC_HOST=127.0.0.1
GRPC_PORT=50051
```

Start the backend server:

```bash
python -m uvicorn api.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
```

If an environment file is used, create it from the example:

```bash
cp .env.example .env
```

Configure the API base URL:

```bash
PUBLIC_API_BASE_URL=http://localhost:8000
```

Launch the frontend:

```bash
npm run dev
```

## API Endpoints

### Profile Management

- `GET /profiles` — retrieve all profiles
- `POST /profiles` — create a new profile
- `PUT /profiles/{id}` — update an existing profile
- `DELETE /profiles/{id}` — delete a profile

### Task Management

- `GET /tasks/{profile_id}` — fetch generated tasks for a profile
- `POST /tasks` — create or update workout/diet tasks

### AI and Chat

- `POST /generate-plan` — generate or refresh a workout and diet plan
- `POST /chat` — send a query to the AI chatbot

## How the Application Works (User Flow)

1. The user opens the FitFusion app and selects or creates a profile.
2. Profile data and goals are captured and stored in MongoDB.
3. The dashboard calculates BMI and displays fitness metrics.
4. When the user requests a plan, the backend builds a prompt and sends it to Groq.
5. The AI returns structured workout and diet recommendations.
6. The app converts recommendations into calendar tasks.
7. The user views scheduled activities on the calendar and asks follow-up questions through the chatbot.

## Screens / UI Description

- **Dashboard**: Displays profile summary, BMI, current plan highlights, and progress overview.
- **Calendar**: Shows scheduled workouts and diet tasks for the month with a clean timeline view.
- **Chatbot**: Offers conversational AI support for fitness questions, plan details, and motivation.
- **Profile**: Allows users to manage personal information, fitness goals, and active profile selection.

## Future Enhancements

- **Agentic AI**: Enable the assistant to actively revise plans and schedule changes in response to user feedback.
- **Real-time Adaptation**: Add dynamic plan adjustments based on user progress, workout completion, and wellness metrics.
- **Wearable Integration**: Connect with fitness devices and wearables for automatic activity tracking and recommendations.
- **More AI Planning Modes**: Support advanced plan personalization such as nutrition macros, recovery cycles, and phased training plans.

## Conclusion

FitFusion demonstrates a polished full-stack fitness planner that bridges modern UI, scalable backend services, a generative AI planning pipeline, and persistent data storage. It is built for users who want actionable, AI-guided fitness planning with an intuitive workflow.

## License

This project is provided as-is for demonstration and education purposes.
