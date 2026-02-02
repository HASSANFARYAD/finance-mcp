def test_api_key_allows_access(client):
    # register user
    r = client.post("/api/v1/auth/register", json={"email": "keyuser@example.com", "password": "secret123"})
    assert r.status_code == 200
    token = r.json()["access_token"]

    # create api key
    r = client.post(
        "/api/v1/auth/api-keys",
        json={"name": "ci-key"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    api_key = r.json()["plain_key"]

    # access protected endpoint with api key
    r = client.get("/api/v1/expenses", headers={"X-API-KEY": api_key})
    assert r.status_code == 200
    assert r.json() == []
