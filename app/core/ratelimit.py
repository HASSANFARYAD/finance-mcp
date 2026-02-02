import time
from fastapi import HTTPException
import redis


class SimpleRateLimiter:
    """Very lightweight in-memory sliding window rate limiter."""

    def __init__(self, max_requests: int, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window = window_seconds
        self.store = {}  # key -> (count, window_start)

    def check(self, key: str):
        now = time.time()
        count, start = self.store.get(key, (0, now))
        if now - start > self.window:
            self.store[key] = (1, now)
            return
        if count + 1 > self.max_requests:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        self.store[key] = (count + 1, start)

    def reset(self):
        self.store = {}


class RedisRateLimiter:
    """Redis sliding window (per minute) using INCR + EXPIRE."""

    def __init__(self, redis_url: str, max_requests: int, window_seconds: int = 60):
        self.r = redis.Redis.from_url(redis_url)
        self.max_requests = max_requests
        self.window = window_seconds

    def check(self, key: str):
        bucket = f"rl:{key}"
        pipe = self.r.pipeline()
        pipe.incr(bucket, 1)
        pipe.expire(bucket, self.window)
        count, _ = pipe.execute()
        if int(count) > self.max_requests:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

    def reset(self):
        # Not efficient to scan; provided for tests only.
        for key in self.r.scan_iter("rl:*"):
            self.r.delete(key)


def build_limiter(redis_url: str | None, max_requests: int, window_seconds: int = 60):
    if redis_url:
        return RedisRateLimiter(redis_url, max_requests, window_seconds)
    return SimpleRateLimiter(max_requests, window_seconds)
