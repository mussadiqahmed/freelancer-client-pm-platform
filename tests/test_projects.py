from tests.helpers import csrf_from, login, make_client, register


def _post_project(client, status="published", title="Logo refresh", budget="1500.50"):
    page = client.get("/projects/new")
    return client.post(
        "/projects",
        data={
            "csrf": csrf_from(page),
            "title": title,
            "description": "Redraw the logo and deliver source files.",
            "budget": budget,
            "deadline": "2026-12-01",
            "status": status,
        },
        follow_redirects=False,
    )


def test_client_can_publish_and_freelancer_can_see_it(tmp_path):
    client = make_client(tmp_path)
    register(client, role="client", email="client@example.com")
    login(client, email="client@example.com")
    created = _post_project(client, status="published")
    assert created.status_code == 303
    assert created.headers["location"] == "/dashboard"
    board = client.get("/dashboard")
    assert "Logo refresh" in board.text
    assert "1500.50" in board.text

    freelancer = make_client(tmp_path)
    register(freelancer, role="freelancer", email="free@example.com")
    login(freelancer, email="free@example.com")
    freelancer_board = freelancer.get("/dashboard")
    assert "Logo refresh" in freelancer_board.text


def test_draft_is_hidden_from_freelancers(tmp_path):
    client = make_client(tmp_path)
    register(client, role="client", email="client@example.com")
    login(client, email="client@example.com")
    assert _post_project(client, status="draft").status_code == 303

    freelancer = make_client(tmp_path)
    register(freelancer, role="freelancer", email="free@example.com")
    login(freelancer, email="free@example.com")
    assert "Logo refresh" not in freelancer.get("/dashboard").text


def test_freelancer_cannot_post_and_missing_budget_is_rejected(tmp_path):
    client = make_client(tmp_path)
    register(client, role="freelancer", email="free@example.com")
    login(client, email="free@example.com")
    denied = client.get("/projects/new")
    assert denied.status_code == 403

    owner = make_client(tmp_path)
    register(owner, role="client", email="client@example.com")
    login(owner, email="client@example.com")
    rejected = _post_project(owner, budget="0")
    assert rejected.status_code == 200
    assert "greater than 0" in rejected.text
