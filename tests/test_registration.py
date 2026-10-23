import sqlite3

from tests.helpers import csrf_from, make_client, register


def test_register_creates_hashed_account_and_confirms(tmp_path):
    client = make_client(tmp_path)
    response = register(client)
    assert response.status_code == 303
    assert response.headers["location"] == "/?registered=1"
    home_page = client.get("/?registered=1")
    assert "Account created" in home_page.text

    connection = sqlite3.connect(tmp_path / "test.db")
    row = connection.execute("SELECT email, password_hash, role FROM users").fetchone()
    assert row[0] == "ada@example.com"
    assert row[2] == "client"
    assert "correct-horse" not in row[1]


def test_duplicate_email_is_rejected(tmp_path):
    client = make_client(tmp_path)
    assert register(client).status_code == 303
    again = register(client)
    assert again.status_code == 200
    assert "already registered" in again.text


def test_short_password_is_rejected(tmp_path):
    client = make_client(tmp_path)
    page = client.get("/register")
    response = client.post(
        "/register",
        data={
            "csrf": csrf_from(page),
            "name": "Ada",
            "email": "ada@example.com",
            "password": "short",
            "role": "freelancer",
        },
    )
    assert response.status_code == 200
    assert "8 and 128" in response.text
    connection = sqlite3.connect(tmp_path / "test.db")
    assert connection.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0
