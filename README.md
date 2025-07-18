# Chat agent

## Development

- `docker compose -f docker-compose.yml build`

- Create a `.env` file: 
```dotenv
OPENAI_API_KEY=YOUR-TOKEN
LOGFIRE_TOKEN=LOGFIRE-TOKEN
DB_CONNECTION_STRING=postgresql+asyncpg://postgres:postgres@db/postgres

ADMIN_USER='admin'
ADMIN_PASSWORD='your-password'
FASTAPI_ADMIN_SECRET_KEY='your-secret-key'
```

- `docker compose -f docker-compose.yml up`

- Set up the pgvector extension:
  - Run `docker exec -it ai_agent_db psql -U postgres -d postgres`
  - Run `CREATE EXTENSION IF NOT EXISTS vector;`
  - Close the session typing `\q`.
  - Stop Docker compose and run it again
    - `docker compose -f docker-compose.yml stop`
    - `docker compose -f docker-compose.yml up`


- Go to `http://localhost:8000/chat-ui/{user-id}`


## Local DB connect.

To connect to the database locally, connect using `jdbc:postgresql://localhost:5432/postgres`.

## Running the project properly.

The agent can be used through the web UI at `http://localhost:8000/chat-ui/{user-id}`.

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
OPENAI_API_KEY=YOUR-TOKEN
LOGFIRE_TOKEN=LOGFIRE-TOKEN
DB_CONNECTION_STRING=postgresql+asyncpg://postgres:postgres@db/postgres

ADMIN_USER='admin'
ADMIN_PASSWORD='your-password'
FASTAPI_ADMIN_SECRET_KEY='your-secret-key'
```

- `docker compose -f docker-compose.prod.yml build`
- `docker compose -f docker-compose.prod.yml up`
- Set up the pgvector extension:
  - Run `docker exec -it ai_agent_db psql -U postgres -d postgres`
  - Run `CREATE EXTENSION IF NOT EXISTS vector;`
  - Close the session typing `\q`.
- Let's try opening the URL `{domain}/chat-ui/{user-id}`.

## Re-deployment
To deploy any changes, just run the script `source deploy-server.sh`

## Optionally setup Supervisor to run the project.

- `sudo apt install supervisor -y`
- Create a conf file: `sudo nano /etc/supervisor/conf.d/chat_agent.conf`
```
[program:chat_agent]
directory=/home/ubuntu/chat-agent
command=sudo /usr/bin/docker compose -f docker-compose.prod.yml up
autostart=true
autorestart=true
stderr_logfile=/var/log/chat_agent.err.log
stdout_logfile=/var/log/chat_agent.out.log
```
- `sudo supervisorctl reread`
- `sudo supervisorctl update`
- `sudo supervisorctl start chat_agent`
- PD: The logs can be shown at `sudo tail -f /var/log/chat_agent.out.log`.

If you would like to see better logs for debugging, stop supervisor
and run docker compose manually.
- `sudo supervisorctl stop chat_agent`
- `docker compose -f docker-compose.prod.yml up`
