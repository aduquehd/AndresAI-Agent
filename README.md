<div align="center">

# 🤖 AI Agent Chatbot

<a href="https://andres-ai.aduquehd.com/">
  <img src="https://img.shields.io/badge/🔗%20Live%20Demo-Visit%20Site-blue?style=for-the-badge" alt="Live Demo">
</a>

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com/)

**A production-ready AI chatbot system built with modern web technologies**

[Features](#features) • [Quick Start](#quick-start) • [Development](#development) • [Deployment](#deployment)

</div>

---

## ✨ Features

<table>
<tr>
<td>

### 🚀 Core Features
- 🤖 **AI-Powered Chat** - Intelligent conversational interface
- 🌐 **Modern Web UI** - Real-time streaming responses
- 🔍 **Semantic Search** - Vector embeddings with pgvector
- 📊 **Admin Panel** - Easy knowledge base management

</td>
<td>

### 🛡️ Production Ready
- 🔒 **Secure Auth** - Session management & authentication
- 🐳 **Dockerized** - Full container orchestration
- 📈 **Scalable** - Async architecture with FastAPI
- 🔧 **Configurable** - Environment-based configuration

</td>
</tr>
</table>

## 📋 Prerequisites

<table>
<tr>
<td align="center">
<img src="https://raw.githubusercontent.com/docker/compose/main/logo.png" width="60" height="60" alt="Docker">
<br>
<b>Docker & Compose</b>
</td>
<td align="center">
<img src="https://nodejs.org/static/images/logo.svg" width="60" height="60" alt="Node.js">
<br>
<b>Node.js & npm</b>
</td>
<td align="center">
<img src="https://upload.wikimedia.org/wikipedia/commons/4/4d/OpenAI_Logo.svg" width="60" height="60" alt="OpenAI">
<br>
<b>OpenAI API Key</b>
</td>
</tr>
</table>

## 🚀 Quick Start

### 1️⃣ **Clone the repository**

```bash
git clone <repository-url>
cd AI_agent
```

### 2️⃣ **Install dependencies**

```bash
npm install
npm run build
```

### 3️⃣ **Create environment file**

```bash
cp .env.example .env
```

<details>
<summary>📝 <b>Environment Configuration</b> (click to expand)</summary>

```dotenv
# 🔑 OpenAI API Configuration
OPENAI_API_KEY=sk-proj-your-openai-api-key-here

# 📊 Logfire Configuration (optional - for observability)
LOGFIRE_TOKEN=pylf_v1_us_your-logfire-token-here

# 🗄️ Database Configuration
DB_CONNECTION_STRING=postgresql+asyncpg://chat_user:your_secure_password@db/chat_agent_db
POSTGRES_USER=chat_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=chat_agent_db

# 👤 FastAPI Admin
ADMIN_USER=admin
ADMIN_PASSWORD='your_secure_admin_password'
FASTAPI_ADMIN_SECRET_KEY='your_secret_key_here_32_chars_min'

# ⚙️ Application Configuration
APP_ENV=development
DEBUG=false

# 📈 Analytics Configuration (optional)
GA_TRACKING_ID=G-YOUR-TRACKING-ID-HERE
```

</details>

### 4️⃣ **Build and start the services**

```bash
docker compose build
docker compose up
```

### 5️⃣ **Set up the pgvector extension**

```bash
# In another terminal
docker exec -it ai_agent_db psql -U chat_user -d chat_agent_db
```

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 6️⃣ **Access the application**

<table>
<tr>
<td align="center">
<h4>💬 Chat Interface</h4>
<a href="http://localhost:8000/">http://localhost:8000/</a>
</td>
<td align="center">
<h4>⚙️ Admin Panel</h4>
<a href="http://localhost:8000/admin">http://localhost:8000/admin</a>
</td>
</tr>
</table>

## 💻 Development

### 🎨 Code Formatting

<table>
<tr>
<td>

#### 🐍 Python Code (Ruff)

```bash
# Format all Python files
docker compose run --rm backend uv run ruff format .

# Check for linting issues
docker compose run --rm backend uv run ruff check .

# Fix auto-fixable issues
docker compose run --rm backend uv run ruff check . --fix
```

</td>
<td>

#### 🌐 Frontend Code (Prettier)

```bash
# Format all files
npm run format

# Check formatting
npm run format:check

# Format specific types
npm run format:html
npm run format:css
npm run format:js
```

</td>
</tr>
</table>

> ⚠️ **Important**: Always run both formatters after making changes:
> ```bash
> docker compose run --rm backend uv run ruff format . && npm run format
> ```

### 🗄️ Database Connection

```yaml
Connection String: jdbc:postgresql://localhost:5432/chat_agent_db
Username: chat_user
Password: (from your .env file)
```

### 📊 Data Management

#### Populate Geographic Data

To populate geographic data for existing users:

```bash
docker compose run --rm backend uv run python -m scripts.populate_user_geo_data
```

## 🎯 Configuring the Agent

The knowledge base powers your AI agent's contextual understanding. Manage it through the admin panel at `/admin`.

<details>
<summary>📚 <b>Knowledge Base Example</b> (click to expand)</summary>

```json
[
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
```

</details>

# 🚢 Deployment

> 💡 **Note**: You may need to use `sudo` for all docker commands.

### Prerequisites

- ✅ Install Docker on your server
- ✅ Configure your domain in `compose/prod/Caddyfile`
- ✅ Create production `.env` file

<details>
<summary>🔐 <b>Production Environment Variables</b> (click to expand)</summary>

```dotenv
# 🔑 OpenAI API Configuration
OPENAI_API_KEY=sk-proj-your-openai-api-key-here

# 📊 Logfire Configuration (optional)
LOGFIRE_TOKEN=pylf_v1_us_your-logfire-token-here

# 🗄️ Database Configuration
DB_CONNECTION_STRING=postgresql+asyncpg://chat_user:your_secure_password@db/chat_agent_db
POSTGRES_USER=chat_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=chat_agent_db

# 👤 FastAPI Admin
ADMIN_USER=admin
ADMIN_PASSWORD='your_secure_admin_password'
FASTAPI_ADMIN_SECRET_KEY='your_secret_key_here_32_chars_min'

# ⚙️ Application Configuration
APP_ENV=production
DEBUG=false

# 📈 Analytics Configuration (optional)
GA_TRACKING_ID=G-YOUR-TRACKING-ID-HERE
```

</details>

### 🚀 Deploy Steps

```bash
# 1. Build the production images
docker compose -f docker-compose.prod.yml build

# 2. Start the services
docker compose -f docker-compose.prod.yml up -d

# 3. Setup pgvector extension
docker exec -it ai_agent_db psql -U chat_user -d chat_agent_db -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 4. Visit your application
# https://your-domain.com
```

### 🔄 Re-deployment

```bash
# Quick redeploy with existing script
source deploy-server.sh
```

## 🛠️ Production Setup with Supervisor

<details>
<summary>⚡ <b>Auto-restart Configuration</b> (click to expand)</summary>

### 1. Install Supervisor
```bash
sudo apt install supervisor -y
```

### 2. Create Configuration
```bash
sudo nano /etc/supervisor/conf.d/ai_agent.conf
```

```ini
[program:ai_agent]
directory=/home/ubuntu/AI_agent
command=sudo /usr/bin/docker compose -f docker-compose.prod.yml up
autostart=true
autorestart=true
stderr_logfile=/var/log/ai_agent.err.log
stdout_logfile=/var/log/ai_agent.out.log
```

### 3. Apply Configuration
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start ai_agent
```

### 📋 Useful Commands
```bash
# View logs
sudo tail -f /var/log/ai_agent.out.log

# Stop for debugging
sudo supervisorctl stop ai_agent
docker compose -f docker-compose.prod.yml up
```

</details>

---

<div align="center">

**Built with ❤️ using modern web technologies**

[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

</div>
