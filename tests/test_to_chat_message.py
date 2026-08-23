from datetime import datetime, timezone

import pytest
from pydantic_ai.messages import (
    ModelRequest,
    ModelResponse,
    SystemPromptPart,
    TextPart,
    ToolCallPart,
    UserPromptPart,
)
from pydantic_ai.run import AgentRunResult

from modules.utils.agent import to_chat_message


TS = datetime(2026, 1, 15, 12, 0, 0, tzinfo=timezone.utc)


def test_user_prompt_becomes_user_chat_message():
    message = ModelRequest(parts=[UserPromptPart(content="Hello", timestamp=TS)])

    assert to_chat_message(message) == {
        "role": "user",
        "timestamp": "2026-01-15T12:00:00+00:00",
        "content": "Hello",
    }


def test_model_text_becomes_model_chat_message():
    message = ModelResponse(parts=[TextPart(content="Hi there.")], timestamp=TS)

    assert to_chat_message(message) == {
        "role": "model",
        "timestamp": "2026-01-15T12:00:00+00:00",
        "content": "Hi there.",
    }


def test_system_prompt_only_is_hidden():
    message = ModelRequest(parts=[SystemPromptPart(content="You are Andres.", timestamp=TS)])

    assert to_chat_message(message) is None


def test_tool_call_only_response_is_hidden():
    message = ModelResponse(
        parts=[
            ToolCallPart(
                tool_name="search_knowledge_base",
                args={"category": "hobbies", "search_query": "music"},
            )
        ],
        timestamp=TS,
    )

    assert to_chat_message(message) is None


def test_non_string_user_content_raises_type_error():
    message = ModelRequest(parts=[UserPromptPart(content=["Hello"])])

    with pytest.raises(TypeError, match="Expected string content"):
        to_chat_message(message)


def test_agent_run_result_becomes_model_chat_message():
    result = AgentRunResult(output="Done.")
    chat_msg = to_chat_message(result)

    assert chat_msg is not None
    assert chat_msg["role"] == "model"
    assert chat_msg["content"] == "Done."
    assert "timestamp" in chat_msg
