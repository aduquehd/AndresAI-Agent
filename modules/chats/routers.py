import json
from datetime import datetime, timezone
from typing import Annotated

import logfire
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import Response, StreamingResponse
from openai import AsyncOpenAI
from pydantic_ai.messages import (
    ModelMessage,
    ModelMessagesTypeAdapter,
    ModelResponse,
    TextPart,
)
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from modules.agent.agent import agent
from modules.chats.models import AgentMessage, Message, MessageDirectionEnum
from modules.chats.services import add_agent_message, add_message
from modules.users.models import User
from modules.users.services import create_user, get_user_by_username
from utils.agent import Deps, to_chat_message
from utils.auth import get_user_id_from_auth_header
from utils.database import get_session


router = APIRouter()


def get_client_ip(request: Request) -> str:
    """Extract client IP address, handling proxies and load balancers."""
    # Check X-Forwarded-For header (common with proxies/load balancers)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # X-Forwarded-For can contain multiple IPs, take the first one (original client)
        return forwarded_for.split(",")[0].strip()
    
    # Check X-Real-IP header (nginx proxy)
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    # Fall back to client.host (direct connection)
    if request.client:
        return request.client.host
    
    return "unknown"


@router.get("/history")
async def get_chat(
    user_id: Annotated[str, Depends(get_user_id_from_auth_header)],
    session: AsyncSession = Depends(get_session),
) -> Response:
    user = await get_user_by_username(session, user_id)

    if not user:
        return Response(b"", media_type="text/plain")

    query = (
        select(AgentMessage).where(AgentMessage.user_id == user.id).order_by(AgentMessage.id.asc())
    )
    result = await session.exec(query)
    messages = result.all()

    list_messages: list[ModelMessage] = []
    for message in messages:
        list_messages.extend(ModelMessagesTypeAdapter.validate_json(message.message_list))

    lines = []
    for message in list_messages:
        chat_msg = to_chat_message(message)
        if chat_msg:
            json_str = json.dumps(chat_msg)
            lines.append(json_str.encode("utf-8"))

    return Response(b"\n".join(lines), media_type="text/plain")


@router.post("/send")
async def post_chat(
    request: Request,
    user_id: Annotated[str, Depends(get_user_id_from_auth_header)],
    prompt: Annotated[str, Form()],
    session: AsyncSession = Depends(get_session),
) -> StreamingResponse:
    user = await get_user_by_username(session, user_id)
    now = datetime.now(timezone.utc)
    client_ip = get_client_ip(request)

    if not user:
        user = User(username=user_id)
        user = await create_user(session, user)

    async def stream_messages():
        """Streams new line delimited JSON Messages to the client."""
        # stream the user prompt so that can be displayed straight away
        yield (
            json.dumps(
                {
                    "role": "user",
                    "timestamp": datetime.now(tz=timezone.utc).isoformat(),
                    "content": prompt,
                }
            ).encode("utf-8")
            + b"\n"
        )

        openai = AsyncOpenAI()
        logfire.instrument_openai(openai)

        logfire.info('Asking "{question}" from user {user_id}', question=prompt, user_id=user_id)

        query = select(AgentMessage).where(AgentMessage.user_id == user.id)
        result = await session.exec(query)
        messages = result.all()

        list_messages: list[ModelMessage] = []
        for message in messages:
            list_messages.extend(ModelMessagesTypeAdapter.validate_json(message.message_list))

        deps = Deps(openai=openai, session=session)

        async with agent.run_stream(prompt, message_history=list_messages, deps=deps) as result:
            async for text in result.stream(debounce_by=0.01):
                # text here is a str and the frontend wants
                # JSON encoded ModelResponse, so we create one
                m = ModelResponse(parts=[TextPart(text)], timestamp=result.timestamp())
                agent_response = to_chat_message(m)

                yield json.dumps(agent_response).encode("utf-8") + b"\n"

        new_message_json = result.new_messages_json()
        agent_message = AgentMessage(
            user_id=user.id, message_list=new_message_json.decode("utf-8"), created_at=now
        )
        await add_agent_message(session, agent_message)

        new_message = Message(
            message=prompt,
            user_id=user.id,
            created_at=now,
            direction=MessageDirectionEnum.outgoing,
            ip_address=client_ip,
        )
        await add_message(session, new_message)

        new_message = Message(
            message=agent_response["content"],
            user_id=user.id,
            created_at=now,
            direction=MessageDirectionEnum.incoming,
            ip_address=client_ip,
        )
        await add_message(session, new_message)

    return StreamingResponse(stream_messages(), media_type="text/plain")