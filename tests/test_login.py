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
