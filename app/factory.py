import os
import secrets
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.db import connect, init_db

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"


def create_app(database_path: str, session_secret: str) -> FastAPI:
    """Build the app. Sessions are signed cookies, not JWTs.

    One SQLite process does not need stateless tokens. The cookie holds only
    the user id and a CSRF token, and Starlette signs it.
    """
    database = Path(database_path)
    database.parent.mkdir(parents=True, exist_ok=True)
    connection = connect(database)
    init_db(connection)
    connection.close()

    app = FastAPI(title="Freelancer-Client PM Platform")
    app.add_middleware(
        SessionMiddleware,
        secret_key=session_secret,
        same_site="lax",
        https_only=False,
        max_age=60 * 60 * 8,
    )
    app.state.database_path = str(database)
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    _register_routers(app)
    return app


def _register_routers(app: FastAPI) -> None:
    import importlib

    # Each story adds its own module. A missing module means that branch is not merged yet.
    for module_name in ("home", "registration", "login", "projects", "milestones"):
        try:
            module = importlib.import_module(f"app.routers.{module_name}")
        except ModuleNotFoundError:
            continue
        app.include_router(module.router)


def default_app() -> FastAPI:
    secret = os.environ.get("SESSION_SECRET") or secrets.token_hex(32)
    database = os.environ.get("APP_DATABASE", "data/fcpp.db")
    return create_app(database, secret)
