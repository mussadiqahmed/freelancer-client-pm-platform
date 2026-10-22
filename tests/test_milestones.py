from tests.helpers import csrf_from, login, make_client, register


def _client_with_project(tmp_path):
    client = make_client(tmp_path)
    register(client, role="client", email="client@example.com")
    login(client, email="client@example.com")
    page = client.get("/projects/new")
    created = client.post(
        "/projects",
        data={
            "csrf": csrf_from(page),
            "title": "Site copy",
            "description": "Write the home page.",
            "budget": "800",
            "deadline": "2026-11-15",
            "status": "published",
        },
        follow_redirects=False,
    )
    assert created.status_code == 303
    return client


def test_owner_adds_milestones_in_order(tmp_path):
    client = _client_with_project(tmp_path)
    first = client.get("/projects/1")
    client.post(
        "/projects/1/milestones",
        data={"csrf": csrf_from(first), "title": "Outline", "amount": "200", "due_date": "2026-11-01"},
        follow_redirects=False,
    )
    second_page = client.get("/projects/1")
    client.post(
        "/projects/1/milestones",
        data={"csrf": csrf_from(second_page), "title": "Final copy", "amount": "600.50", "due_date": "2026-11-15"},
        follow_redirects=False,
    )
    page = client.get("/projects/1")
    assert page.text.index("Outline") < page.text.index("Final copy")
    assert "600.50" in page.text


def test_invalid_milestone_and_other_client_are_rejected(tmp_path):
    owner = _client_with_project(tmp_path)
    page = owner.get("/projects/1")
    rejected = owner.post(
        "/projects/1/milestones",
        data={"csrf": csrf_from(page), "title": "", "amount": "-5", "due_date": "tomorrow"},
    )
    assert rejected.status_code == 200
    assert "milestone title" in rejected.text
    assert "greater than 0" in rejected.text
    assert "YYYY-MM-DD" in rejected.text

    other = make_client(tmp_path)
    register(other, role="client", email="other@example.com")
    login(other, email="other@example.com")
    other_page = other.get("/projects/1")
    assert other_page.status_code == 404

    freelancer = make_client(tmp_path)
    register(freelancer, role="freelancer", email="free@example.com")
    login(freelancer, email="free@example.com")
    seen = freelancer.get("/projects/1")
    assert seen.status_code == 200
    blocked = freelancer.post(
        "/projects/1/milestones",
        data={"csrf": csrf_from(seen), "title": "Sneaky", "amount": "10", "due_date": "2026-11-01"},
    )
    assert blocked.status_code == 403
