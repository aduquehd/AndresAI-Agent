from types import SimpleNamespace
from unittest.mock import AsyncMock

from pydantic_ai import capture_run_messages
from pydantic_ai.messages import (
    ModelRequest,
    SystemPromptPart,
    ToolCallPart,
    ToolReturnPart,
)
from pydantic_ai.models.function import FunctionModel
from pydantic_ai.models.test import TestModel

from modules.agent.agent import agent
from modules.knowledge_base.models import KnowledgeBaseTypeEnum
from modules.utils.agent import Deps


async def test_dynamic_system_prompt_is_injected(system_prompt: str, kb_search: AsyncMock):
    with (
        agent.override(model=TestModel(call_tools=[])),
        capture_run_messages() as messages,
    ):
        result = await agent.run("Hello", deps=Deps())

    assert result.output
    system_parts = [
        part
        for message in messages
        if isinstance(message, ModelRequest)
        for part in message.parts
        if isinstance(part, SystemPromptPart)
    ]
    assert any(part.content == system_prompt for part in system_parts)


async def test_search_knowledge_base_returns_json_hits(system_prompt: str, kb_search: AsyncMock):
    kb_search.return_value = [
        SimpleNamespace(title="Guitar", content="I play guitar on weekends."),
    ]

    def call_tool(messages, _info):
        if any(
            isinstance(part, ToolReturnPart)
            for message in messages
            if isinstance(message, ModelRequest)
            for part in message.parts
        ):
            from pydantic_ai.messages import ModelResponse, TextPart

            return ModelResponse(parts=[TextPart(content="You play guitar.")])

        from pydantic_ai.messages import ModelResponse

        return ModelResponse(
            parts=[
                ToolCallPart(
                    tool_name="search_knowledge_base",
                    args={"category": "hobbies", "search_query": "music"},
                )
            ]
        )

    with (
        agent.override(model=FunctionModel(call_tool)),
        capture_run_messages() as messages,
    ):
        result = await agent.run("What are your hobbies?", deps=Deps())

    kb_search.assert_awaited()
    _session, category, _embedding = kb_search.await_args.args
    assert category == KnowledgeBaseTypeEnum.hobbies
    assert kb_search.await_args.kwargs.get("limit", 30) == 30
    assert result.output == "You play guitar."

    tool_returns = [
        part
        for message in messages
        if isinstance(message, ModelRequest)
        for part in message.parts
        if isinstance(part, ToolReturnPart)
    ]
    assert tool_returns
    assert b"Guitar" in tool_returns[0].content.encode() or "Guitar" in str(tool_returns[0].content)


async def test_search_knowledge_base_returns_no_data(system_prompt: str, kb_search: AsyncMock):
    kb_search.return_value = []

    def call_tool(messages, _info):
        from pydantic_ai.messages import ModelResponse, TextPart

        if any(
            isinstance(part, ToolReturnPart)
            for message in messages
            if isinstance(message, ModelRequest)
            for part in message.parts
        ):
            return ModelResponse(parts=[TextPart(content="I don't have that.")])

        return ModelResponse(
            parts=[
                ToolCallPart(
                    tool_name="search_knowledge_base",
                    args={
                        "category": "favorite_foods",
                        "search_query": "arepas",
                    },
                )
            ]
        )

    with capture_run_messages() as messages, agent.override(model=FunctionModel(call_tool)):
        await agent.run("What food do you like?", deps=Deps())

    tool_returns = [
        part
        for message in messages
        if isinstance(message, ModelRequest)
        for part in message.parts
        if isinstance(part, ToolReturnPart)
    ]
    assert tool_returns
    assert tool_returns[0].content == "NO_DATA"
    _session, category, _embedding = kb_search.await_args.args
    assert category == KnowledgeBaseTypeEnum.favorite_foods
