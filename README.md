# AI Agent Chatbot

A production-ready AI chatbot system built with FastAPI that supports web interfaces. The system uses OpenAI for AI capabilities and PostgreSQL with pgvector for semantic search in the knowledge base.

## Features

- 🤖 AI-powered conversational interface
- 🌐 Modern web chat UI with real-time streaming
- 🔍 Semantic search with vector embeddings
- 📊 Admin panel for knowledge base management
- 🔒 Secure authentication and session management
- 🐳 Full Docker containerization

## Prerequisites

- Docker and Docker Compose
- Node.js and npm (for TypeScript compilation)
- OpenAI API key

## Quick Start

1. **Clone the repository**
```bash
git clone <repository-url>
cd AI_agent
```

2. **Install dependencies**
```bash
npm install
npm run build
```

3. **Create environment file**
Copy `.env.example` to `.env` and fill in your values:
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```dotenv
# OpenAI API Configuration
OPENAI_API_KEY=sk-proj-your-openai-api-key-here

# Logfire Configuration (optional - for observability)
LOGFIRE_TOKEN=pylf_v1_us_your-logfire-token-here

# Database Configuration
DB_CONNECTION_STRING=postgresql+asyncpg://chat_user:your_secure_password@db/ai_agent_db
POSTGRES_USER=chat_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=ai_agent_db

# FastAPI Admin
ADMIN_USER=admin
ADMIN_PASSWORD='your_secure_admin_password'
FASTAPI_ADMIN_SECRET_KEY='your_secret_key_here_32_chars_min'

# Application Configuration
APP_ENV=development
DEBUG=false
```

4. **Build and start the services**
```bash
docker compose build
docker compose up
```

5. **Set up the pgvector extension**
In another terminal, run:
```bash
docker exec -it ai_agent_db psql -U chat_user -d ai_agent_db
```
Then execute:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
\q
```

6. **Access the application**
- Chat UI: http://localhost:8000/chat
- Admin panel: http://localhost:8000/admin

## Development


## Local DB connect.

To connect to the database locally, connect using `jdbc:postgresql://localhost:5432/ai_agent_db` with username `chat_user`.

## Running the project properly.

The agent can be used through the web UI at `http://localhost:8000/chat`. Each visitor is automatically assigned a unique UUID stored in localStorage, keeping conversations separate and persistent across sessions.

## Configuring the Agent

The knowledge base is what the Agent uses to get the context of what to do.

### Example of Knowledge base:

```json
{
    "kbs": [
        {
            "type": "hobbies",
            "title": "Racing bikes",
            "content": "I've been racing bikes for 3 years, and I love the adrenaline rush."
        },
        {
            "type": "hobbies",
            "title": "Playing guitar",
            "content": "Started playing guitar last year, it helps me relax after work."
        }
    ]
}
```


# Deployment

Since the project is using Docker and Docker compose, the deployment is very simple.

PD: You may need to use `sudo` in all docker commands, like `sudo docker compose ...`.

- Install Docker in the machine.
- Create a `.env` file:
- Make sure the domain at `compose/prod/Caddyfile` is correct.
```dotenv
# OpenAI API Configuration
OPENAI_API_KEY=sk-proj-your-openai-api-key-here

# Logfire Configuration (optional - for observability)
LOGFIRE_TOKEN=pylf_v1_us_your-logfire-token-here

# Database Configuration
DB_CONNECTION_STRING=postgresql+asyncpg://chat_user:your_secure_password@db/ai_agent_db
POSTGRES_USER=chat_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=ai_agent_db

# FastAPI Admin
ADMIN_USER=admin
ADMIN_PASSWORD='your_secure_admin_password'
FASTAPI_ADMIN_SECRET_KEY='your_secret_key_here_32_chars_min'

# Application Configuration
APP_ENV=development
DEBUG=false
```

- `docker compose -f docker-compose.prod.yml build`
- `docker compose -f docker-compose.prod.yml up`
- Set up the pgvector extension:
  - Run `docker exec -it ai_agent_db psql -U chat_user -d ai_agent_db`
  - Run `CREATE EXTENSION IF NOT EXISTS vector;`
  - Close the session typing `\q`.
- Let's try opening the URL `{domain}/chat`.

## Re-deployment
To deploy any changes, just run the script `source deploy-server.sh`

## Optionally setup Supervisor to run the project.

- `sudo apt install supervisor -y`
- Create a conf file: `sudo nano /etc/supervisor/conf.d/ai_agent.conf`
```
[program:ai_agent]
directory=/home/ubuntu/AI_agent
command=sudo /usr/bin/docker compose -f docker-compose.prod.yml up
autostart=true
autorestart=true
stderr_logfile=/var/log/ai_agent.err.log
stdout_logfile=/var/log/ai_agent.out.log
```
- `sudo supervisorctl reread`
- `sudo supervisorctl update`
- `sudo supervisorctl start ai_agent`
- PD: The logs can be shown at `sudo tail -f /var/log/ai_agent.out.log`.

If you would like to see better logs for debugging, stop ai_agent
and run docker compose manually.
- `sudo supervisorctl stop ai_agent`
- `docker compose -f docker-compose.prod.yml up`
