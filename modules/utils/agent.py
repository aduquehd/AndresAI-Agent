from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal

from pydantic_ai.messages import (
    ModelMessage,
    ModelMessagesTypeAdapter,
    ModelRequest,
    ModelResponse,
    TextPart,
    UserPromptPart,
)
from pydantic_ai.run import AgentRunResult
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import TypedDict


@dataclass
class Deps:
    session: AsyncSession | None = None


class ChatMessage(TypedDict):
    """Format of messages sent to the browser."""

    role: Literal["user", "model"]
    timestamp: str
    content: str


def to_chat_message(m: ModelMessage | AgentRunResult) -> ChatMessage | None:
    if isinstance(m, ModelRequest):
        for part in m.parts:
            if isinstance(part, UserPromptPart):
                if not isinstance(part.content, str):
                    raise TypeError(f"Expected string content, got {type(part.content)}")
                return {
                    "role": "user",
                    "timestamp": part.timestamp.isoformat(),
                    "content": part.content,
                }
    elif isinstance(m, ModelResponse):
        for part in m.parts:
            if isinstance(part, TextPart):
                return {
                    "role": "model",
                    "timestamp": m.timestamp.isoformat(),
                    "content": part.content,
                }
    elif isinstance(m, AgentRunResult):
        return {
            "role": "model",
            "timestamp": datetime.now(UTC).isoformat(),
            "content": m.output,
        }
    else:
        return None


def load_model_messages(stored_json_lists: list[str]) -> list[ModelMessage]:
    """Rehydrate stored AgentMessage.message_list rows into a single history."""
    messages: list[ModelMessage] = []
    for raw in stored_json_lists:
        messages.extend(ModelMessagesTypeAdapter.validate_json(raw))
    return messages


def chat_messages_from_history(stored_json_lists: list[str]) -> list[ChatMessage]:
    """Convert stored Pydantic AI message JSON into chat-UI payloads."""
    chat_messages: list[ChatMessage] = []
    for message in load_model_messages(stored_json_lists):
        chat_msg = to_chat_message(message)
        if chat_msg:
            chat_messages.append(chat_msg)
    return chat_messages
