from app.core.ratelimit import SimpleRateLimiter


def test_rate_limit_blocks_after_threshold(client):
    # override limiter to small window/limit for test
    limiter = SimpleRateLimiter(max_requests=2, window_seconds=60)
    client.app.state.limiter = limiter
    headers = {"X-API-KEY": "ratetest"}

    r1 = client.get("/api/v1/tools", headers=headers)
    r2 = client.get("/api/v1/tools", headers=headers)
    r3 = client.get("/api/v1/tools", headers=headers)

    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r3.status_code == 429
