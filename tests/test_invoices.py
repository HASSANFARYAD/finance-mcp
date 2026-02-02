from decimal import Decimal


def test_create_invoice_with_items(client):
    # auth
    r = client.post("/api/v1/auth/register", json={"email": "inv@example.com", "password": "secret123"})
    token = r.json()["access_token"]

    payload = {
        "invoice_number": "INV-1",
        "due_date": "2026-12-31T00:00:00Z",
        "client_name": "Test Client",
        "currency": "USD",
        "tax_rate": "10",
        "items": [
            {"description": "Item A", "quantity": "2", "unit_price": "100"},
            {"description": "Item B", "quantity": "1", "unit_price": "50"},
        ],
    }
    r = client.post("/api/v1/invoices", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["subtotal"] == "250.00"
    assert data["tax_amount"] == "25.00"
    assert data["total"] == "275.00"
    assert len(data["items"]) == 2
