from pathlib import Path
from unittest.mock import AsyncMock

from pydantic_ai.messages import ModelMessagesTypeAdapter
from pydantic_ai.models.test import TestModel

from modules.agent.agent import agent
from modules.utils.agent import Deps, chat_messages_from_history, load_model_messages


FIXTURES = Path(__file__).parent / "fixtures"
V1_HISTORY = (FIXTURES / "v1_agent_messages.json").read_text()
V1_FOLLOWUP = (FIXTURES / "v1_followup_messages.json").read_text()


def test_v1_stored_messages_validate():
    messages = load_model_messages([V1_HISTORY])
    assert len(messages) == 4


def test_v1_history_maps_to_chat_ui_payloads():
    chat_messages = chat_messages_from_history([V1_HISTORY])

    assert [m["role"] for m in chat_messages] == ["user", "model", "model"]
    assert chat_messages[0]["content"] == "What are your hobbies?"
    assert chat_messages[1]["content"] == "Let me look that up."
    assert chat_messages[2]["content"] == "I enjoy playing guitar."


def test_concatenated_stored_rows_rebuild_full_history():
    messages = load_model_messages([V1_HISTORY, V1_FOLLOWUP])
    chat_messages = chat_messages_from_history([V1_HISTORY, V1_FOLLOWUP])

    assert len(messages) == 6
    assert chat_messages[-1]["content"] == "I like Colombian food."
    assert chat_messages[-2]["content"] == "What about food?"


async def test_new_messages_json_round_trips(system_prompt: str, kb_search: AsyncMock):
    with agent.override(model=TestModel(call_tools=[], custom_output_text="Hello.")):
        result = await agent.run("Hi", deps=Deps())

    raw = result.new_messages_json()
    restored = ModelMessagesTypeAdapter.validate_json(raw)
    assert restored
    chat_messages = chat_messages_from_history([raw.decode("utf-8")])
    assert chat_messages[-1]["content"] == "Hello."
