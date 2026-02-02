def test_create_and_update_expense(client):
    r = client.post("/api/v1/auth/register", json={"email": "exp@example.com", "password": "secret123"})
    token = r.json()["access_token"]

    payload = {
        "amount": "42.50",
        "currency": "USD",
        "category": "Travel",
        "description": "Taxi",
    }
    r = client.post("/api/v1/expenses", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    exp_id = r.json()["id"]

    r = client.patch(
        f"/api/v1/expenses/{exp_id}",
        json={"status": "approved", "amount": "45.00"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "approved"
    assert data["amount"] == "45.00"
