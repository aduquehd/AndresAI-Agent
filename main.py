from contextlib import asynccontextmanager
from pathlib import Path

import logfire
from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqladmin import Admin
from sqlmodel import SQLModel

from config import settings
from modules.admin.agent import AgentContextAdmin
from modules.admin.auth import authentication_backend
from modules.admin.knowledge_base import KnowledgeBaseAdmin
from modules.admin.messages import AgentMessagesAdmin, MessagesAdmin
from modules.admin.user import UserAdmin
from modules.chats.routers import router as chats_router
from utils.database import engine


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


THIS_DIR = Path(__file__).parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    # await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


admin = Admin(app, engine, authentication_backend=authentication_backend, title="Chat Agent Admin")

admin.add_view(UserAdmin)
admin.add_view(AgentMessagesAdmin)
admin.add_view(MessagesAdmin)
admin.add_view(KnowledgeBaseAdmin)
admin.add_view(AgentContextAdmin)


app.include_router(chats_router, prefix="/api/chats")


app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

logfire.configure(send_to_logfire="if-token-present")
logfire.instrument_fastapi(app)


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        request=request, name="404.html", status_code=404, context={"settings": settings}
    )


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request, name="chat_app.html", context={"settings": settings}
    )
