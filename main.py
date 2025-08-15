from contextlib import asynccontextmanager
from pathlib import Path

import logfire
from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_limiter import FastAPILimiter
from sqladmin import Admin
from sqlmodel import SQLModel

from config import settings
from modules.admin.agent import AgentContextAdmin
from modules.admin.auth import authentication_backend
from modules.admin.knowledge_base import KnowledgeBaseAdmin
from modules.admin.messages import AgentMessagesAdmin, MessagesAdmin
from modules.admin.user import UserAdmin
from modules.chats.routers import router as chats_router
from modules.utils.database import engine
from modules.utils.redis import init_redis
from modules.utils.sentry import init_sentry


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


THIS_DIR = Path(__file__).parent

# Initialize Sentry before creating the FastAPI app
init_sentry()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # await create_db_and_tables()

    # Initialize Redis and FastAPI Limiter
    redis_client = await init_redis()
    await FastAPILimiter.init(redis_client)

    yield
    # Cleanup on shutdown
    await FastAPILimiter.close()


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


@app.get("/robots.txt")
async def robots():
    return FileResponse("robots.txt", media_type="text/plain")


@app.get("/sitemap.xml")
async def sitemap():
    return FileResponse("sitemap.xml", media_type="application/xml")
