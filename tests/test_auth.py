from app.crud.user import get_user_by_email


def test_register_and_login(client):
    resp = client.post("/api/v1/auth/register", json={"email": "test@example.com", "password": "secret123"})
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    assert token

    resp2 = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "secret123"},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert resp2.status_code == 200
    assert resp2.json()["access_token"]
