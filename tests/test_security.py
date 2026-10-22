from app.security import hash_password, verify_password


def test_password_hash_is_salted_and_verifies():
    stored = hash_password("correct-horse")
    assert "correct-horse" not in stored
    assert verify_password("correct-horse", stored)
    assert not verify_password("wrong-password", stored)
    assert stored != hash_password("correct-horse")


def test_health(tmp_path):
    from tests.helpers import make_client

    response = make_client(tmp_path).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
