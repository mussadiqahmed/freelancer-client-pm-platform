import re
import sqlite3

from fastapi.testclient import TestClient

from app.factory import create_app


def make_client(tmp_path):
    app = create_app(str(tmp_path / "test.db"), "test-secret-value")
    return TestClient(app)


def csrf_from(response) -> str:
    match = re.search(r'name="csrf" value="([^"]+)"', response.text)
    assert match, response.text
    return match.group(1)


def register(client, role="client", email="ada@example.com", password="correct-horse"):
    page = client.get("/register")
    return client.post(
        "/register",
        data={
            "csrf": csrf_from(page),
            "name": "Ada Client",
            "email": email,
            "password": password,
            "role": role,
        },
        follow_redirects=False,
    )


def login(client, email="ada@example.com", password="correct-horse"):
    page = client.get("/login")
    return client.post(
        "/login",
        data={"csrf": csrf_from(page), "email": email, "password": password},
        follow_redirects=False,
    )
