from unittest.mock import patch

from tests.helpers import csrf_from, login, make_client, register


def test_login_starts_session_and_opens_dashboard(tmp_path):
    client = make_client(tmp_path)
    register(client)
    response = login(client)
    assert response.status_code == 303
    assert response.headers["location"] == "/dashboard"
    dashboard = client.get("/dashboard")
    assert dashboard.status_code == 200
    assert "Ada Client" in dashboard.text


def test_wrong_password_does_not_start_session(tmp_path):
    client = make_client(tmp_path)
    register(client)
    response = login(client, password="not-the-password")
    assert response.status_code == 200
    assert "incorrect" in response.text
    assert client.get("/dashboard", follow_redirects=False).status_code == 303


def test_empty_login_is_rejected(tmp_path):
    client = make_client(tmp_path)
    page = client.get("/login")
    response = client.post("/login", data={"csrf": csrf_from(page), "email": "", "password": ""})
    assert response.status_code == 200
    assert "Email is required" in response.text
    assert "Password is required" in response.text


def test_login_replaces_the_pre_login_session(tmp_path):
    client = make_client(tmp_path)
    register(client)
    page = client.get("/login")
    old_csrf = csrf_from(page)
    old_cookie = client.cookies.get("session")

    response = login(client)
    assert response.status_code == 303
    assert client.cookies.get("session") != old_cookie

    refreshed = client.get("/login")
    assert csrf_from(refreshed) != old_csrf
    rejected = client.post("/logout", data={"csrf": old_csrf}, follow_redirects=False)
    assert rejected.status_code == 303
    assert client.get("/dashboard", follow_redirects=False).status_code == 200


def test_unknown_email_still_verifies_a_password_hash(tmp_path):
    client = make_client(tmp_path)
    page = client.get("/login")
    with patch("app.routers.login.verify_password", return_value=False) as verify:
        response = client.post(
            "/login",
            data={"csrf": csrf_from(page), "email": "missing@example.com", "password": "correct-horse"},
        )
    assert response.status_code == 200
    assert "incorrect" in response.text
    assert verify.call_count == 1
    assert "$" in verify.call_args.args[1]
    assert client.get("/dashboard", follow_redirects=False).status_code == 303
