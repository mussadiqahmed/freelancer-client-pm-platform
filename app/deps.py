import secrets
from collections.abc import Iterator

from fastapi import Request

from app.db import connect
from app.repository import find_user_by_id
from app.security import new_csrf_token


def get_connection(request: Request) -> Iterator:
    connection = connect(request.app.state.database_path)
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def current_user(request: Request, connection):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return find_user_by_id(connection, user_id)


def ensure_csrf(request: Request) -> str:
    token = request.session.get("csrf")
    if not token:
        token = new_csrf_token()
        request.session["csrf"] = token
    return token


def csrf_is_valid(request: Request, submitted: str | None) -> bool:
    expected = request.session.get("csrf")
    if not expected or not submitted:
        return False
    return secrets.compare_digest(expected, submitted)
