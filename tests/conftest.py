import os
from collections.abc import Iterator
from unittest.mock import AsyncMock, patch

import pytest
from pydantic_ai import models


os.environ.setdefault(
    "DB_CONNECTION_STRING",
    "postgresql+asyncpg://chat_user:password@localhost:5432/chat_agent_db",
)
os.environ.setdefault("FASTAPI_ADMIN_SECRET_KEY", "test-secret-key-32-chars-minimum")
os.environ.setdefault("ADMIN_USER", "admin")
os.environ.setdefault("ADMIN_PASSWORD", "admin")

models.ALLOW_MODEL_REQUESTS = False

SYSTEM_PROMPT = "You are Andres. Answer questions about your career and hobbies."


@pytest.fixture
def system_prompt() -> Iterator[str]:
    with patch(
        "modules.agent.agent.get_agent_context",
        new_callable=AsyncMock,
        return_value=SYSTEM_PROMPT,
    ):
        yield SYSTEM_PROMPT


@pytest.fixture
def kb_search() -> Iterator[AsyncMock]:
    with (
        patch("modules.agent.agent.embed_query", new_callable=AsyncMock, return_value=[0.1] * 8),
        patch(
            "modules.agent.agent.get_knowledge_base_embedding_list",
            new_callable=AsyncMock,
        ) as search,
    ):
        search.return_value = []
        yield search
