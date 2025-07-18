import uuid

from fastapi import Request
from sqladmin.authentication import AuthenticationBackend

from config import settings


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        if username == settings.admin_user and password == settings.admin_password:
            request.session.update({"token": str(uuid.uuid4())})
            return True

        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return False

        return True


authentication_backend = AdminAuth(secret_key=settings.fastapi_admin_secret_key)
