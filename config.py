from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_connection_string: str

    # Admin
    fastapi_admin_secret_key: str
    admin_user: str
    admin_password: str

    # Application
    app_env: str = "development"
    debug: bool = False

    # Analytics
    ga_tracking_id: str | None = None

    # ipapi
    ipapi_secret_key: str | None = None


settings = Settings()
