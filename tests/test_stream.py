import json
from unittest.mock import AsyncMock

from pydantic_ai.messages import (
    ModelRequest,
    PartDeltaEvent,
    PartStartEvent,
    TextPart,
    TextPartDelta,
    ToolReturnPart,
)
from pydantic_ai.models.function import DeltaToolCall, FunctionModel
from pydantic_ai.models.test import TestModel

from modules.agent.agent import agent
from modules.chats.stream import append_stream_delta, event_text_delta, iter_streamed_text
from modules.utils.agent import Deps


def test_append_stream_delta_skips_empty():
    assert append_stream_delta("Hello", None, False) is None
    assert append_stream_delta("Hello", "", False) is None


def test_append_stream_delta_accumulates():
    assert append_stream_delta("Hello", " world", False) == "Hello world"


def test_append_stream_delta_separates_text_parts():
    assert append_stream_delta("Hello", "Next", True) == "Hello\n\nNext"
    assert append_stream_delta("Hello\n\n", "Next", True) == "Hello\n\nNext"


def test_event_text_delta_reads_part_start_and_delta():
    start = PartStartEvent(index=0, part=TextPart(content="Hi"))
    assert event_text_delta(start) == (True, "Hi")

    delta = PartDeltaEvent(index=0, delta=TextPartDelta(content_delta=" there"))
    assert event_text_delta(delta) == (False, " there")
    assert event_text_delta(object()) == (False, None)


async def test_iter_streamed_text_text_only(system_prompt: str, kb_search: AsyncMock):
    with agent.override(
        model=TestModel(call_tools=[], custom_output_text="Hello world from Andres")
    ):
        async with agent.iter("Hi", deps=Deps()) as agent_run:
            chunks = [chunk async for chunk in iter_streamed_text(agent_run)]

    assert chunks
    assert chunks[-1] == "Hello world from Andres"
    for previous, current in zip(chunks, chunks[1:]):
        assert current.startswith(previous) or previous in current


async def test_iter_streamed_text_includes_text_after_tool_call(
    system_prompt: str, kb_search: AsyncMock
):
    kb_search.return_value = []

    async def stream_fn(messages, _info):
        has_tool_return = any(
            isinstance(part, ToolReturnPart)
            for message in messages
            if isinstance(message, ModelRequest)
            for part in message.parts
        )
        if not has_tool_return:
            yield "Let me look that up."
            yield {
                0: DeltaToolCall(
                    name="search_knowledge_base",
                    json_args=json.dumps({"category": "hobbies", "search_query": "hobbies"}),
                    tool_call_id="call_stream_1",
                )
            }
        else:
            yield "I enjoy playing guitar."

    with agent.override(model=FunctionModel(stream_function=stream_fn)):
        async with agent.iter("What are your hobbies?", deps=Deps()) as agent_run:
            chunks = [chunk async for chunk in iter_streamed_text(agent_run)]

    assert any("Let me look that up." in chunk for chunk in chunks)
    assert chunks[-1].endswith("I enjoy playing guitar.")
    assert "Let me look that up." in chunks[-1]
