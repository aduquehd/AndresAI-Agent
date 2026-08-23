from collections.abc import AsyncIterator
from typing import Any

from pydantic_ai import Agent
from pydantic_ai.messages import PartDeltaEvent, PartStartEvent, TextPart, TextPartDelta


def append_stream_delta(accumulated: str, delta: str | None, is_new_text_part: bool) -> str | None:
    """Apply a streamed text delta. Return the new accumulated text, or None to skip."""
    if not delta:
        return None
    if is_new_text_part and accumulated and not accumulated.endswith("\n\n"):
        accumulated += "\n\n"
    return accumulated + delta


def event_text_delta(event: Any) -> tuple[bool, str | None]:
    """Extract (is_new_text_part, delta) from a model stream event."""
    if isinstance(event, PartStartEvent) and isinstance(event.part, TextPart):
        return True, event.part.content
    if isinstance(event, PartDeltaEvent) and isinstance(event.delta, TextPartDelta):
        return False, event.delta.content_delta
    return False, None


async def iter_streamed_text(agent_run: Any) -> AsyncIterator[str]:
    """Yield accumulated model text as tokens arrive across all request nodes.

    Text emitted after tool calls is included. A blank line is inserted between
    separate TextParts. Empty deltas are skipped.
    """
    accumulated = ""
    async for node in agent_run:
        if not Agent.is_model_request_node(node):
            continue
        async with node.stream(agent_run.ctx) as request_stream:
            async for event in request_stream:
                is_new_text_part, delta = event_text_delta(event)
                updated = append_stream_delta(accumulated, delta, is_new_text_part)
                if updated is None:
                    continue
                accumulated = updated
                yield accumulated
