# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a production-ready AI chatbot system built with FastAPI that supports web interfaces. The system uses OpenAI for AI capabilities and PostgreSQL with pgvector for semantic search in the knowledge base. Users are automatically identified by client-generated UUIDs stored in localStorage for persistent chat sessions.

## Key Technologies

- **Backend**: FastAPI, SQLModel, Pydantic AI
- **Frontend**: TypeScript (compiled to JavaScript)
- **Database**: PostgreSQL with pgvector extension
- **Containerization**: Docker Compose
- **Package Manager**: uv (Python), npm (JavaScript/TypeScript)
- **Code Quality**: Ruff for linting/formatting
- **Migrations**: Alembic

## Essential Commands

### Development

```bash
# Build TypeScript
npm install
npm run build  # or npm run watch for development

# Build and start services
docker compose -f docker-compose.yml build
docker compose -f docker-compose.yml up

# Run database migrations
docker compose -f docker-compose.yml run --rm backend uv run alembic upgrade head

# Create new migration
docker compose -f docker-compose.yml run --rm backend uv run alembic revision --autogenerate -m "description"

# Lint and format code
uv run ruff check .
uv run ruff format .

# Access services
# Chat UI: http://localhost:8000/chat
# Admin panel: http://localhost:8000/admin
```

### Production Deployment

```bash
# Quick deploy (uses deploy-server.sh)
source deploy-server.sh

# Manual deploy
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up
```

## Architecture

The application follows a modular architecture:

- **modules/**: Core business logic organized by domain
  - **admin/**: SQLAdmin views for managing entities
  - **agent/**: AI agent logic and models
  - **chats/**: Chat functionality and WebSocket handling
  - **knowledge_base/**: RAG system for agent context
  - **users/**: User management

- **utils/**: Shared utilities
  - **agent.py**: Pydantic AI agent configuration
  - **auth.py**: Authentication logic
  - **database.py**: Database session management

- **templates/** and **static/**: Frontend assets for web chat UI

## Critical Setup Requirements

1. **Environment Variables**: Create `.env` file with:
   - `OPENAI_API_KEY`
   - `LOGFIRE_TOKEN`
   - `DB_CONNECTION_STRING`
   - `ADMIN_USER`, `ADMIN_PASSWORD`
   - `FASTAPI_ADMIN_SECRET_KEY`

2. **pgvector Extension**: Must be manually enabled after first container start:
   ```bash
   docker exec -it ai_agent_db psql -U chat_user -d chat_agent_db
   CREATE EXTENSION IF NOT EXISTS vector;
   \q
   ```


## Knowledge Base API

The agent's behavior is controlled through the knowledge base API:

- `GET /api/kb` - List all knowledge base entries
- `POST /api/kb` - Add entries (types: "initial_questions", "faq", "hobbies")
- `DELETE /api/kb/{id}` - Delete specific entry
- `DELETE /api/kb/delete-all` - Clear all entries

## Database Schema

Key models in `modules/*/models.py`:
- **User**: User accounts
- **Agent**: AI agent configurations
- **Chat**: Conversation sessions
- **Message**: Individual messages
- **KnowledgeBase**: Context for AI responses

All models extend SQLModel for both ORM and Pydantic validation.

## Development Notes

- Users are created automatically when interacting with the system
- Frontend TypeScript source is in `src/` and compiles to `static/js/`
- For local development with HTTPS issues, update protocol replacements in `chat_app.html`
- No test suite currently exists - consider adding pytest for new features
- TypeScript compilation is handled automatically in Docker builds