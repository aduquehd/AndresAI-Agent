"""Rate limiting backed by pyrate-limiter over the shared Redis connection."""

from collections.abc import Awaitable, Callable
from time import time_ns

from fastapi import HTTPException, Request, status
from pyrate_limiter import AbstractBucket, BucketFactory, Limiter, Rate, RateItem, RedisBucket
from pyrate_limiter.buckets.redis_bucket import LuaScript
from redis.asyncio import Redis

from modules.utils.redis import get_redis
from modules.utils.request import get_client_ip


KEY_PREFIX = "rate-limit"

# Entries older than the window are dead weight in the sorted set, and a key
# nobody touches again should not outlive its window either. Both are trimmed
# on every request, so an idle client leaves nothing behind.
_TTL_GRACE_SECONDS = 60


async def get_client_ip_identifier(request: Request) -> str:
    """
    Get client IP address as identifier for rate limiting.

    This uses the same IP extraction logic as the geo data implementation,
    handling CloudFlare, proxies, and load balancers.
    """
    return get_client_ip(request)


class _PerIdentityBucketFactory(BucketFactory):
    """Give every client identity its own Redis bucket.

    pyrate-limiter evaluates rates per *bucket*, not per item name: routing
    every caller through a single bucket would apply the limit globally, so one
    busy IP would lock out everybody else. Deriving the bucket key from the
    identity is what preserves the per-client behaviour.
    """

    def __init__(self, redis: Redis, rates: list[Rate], prefix: str, script_hash: str):
        self.redis = redis
        self.rates = rates
        self.prefix = prefix
        self.script_hash = script_hash

    def bucket_key(self, name: str) -> str:
        return f"{self.prefix}:{name}"

    def wrap_item(self, name: str, weight: int = 1) -> RateItem:
        return RateItem(name, time_ns() // 1_000_000, weight=weight)

    def get(self, item: RateItem) -> AbstractBucket:
        # A RedisBucket is just a handle - the state lives in Redis - so these
        # are built per request rather than cached in a dict that would grow one
        # entry per client IP and never shrink.
        return RedisBucket(self.rates, self.redis, self.bucket_key(item.name), self.script_hash)


class RateLimiter:
    """Allow `times` requests per `seconds` for each client identity.

    Used as a route dependency, mirroring the fastapi-limiter API it replaces:

        dependencies=[Depends(RateLimiter(times=100, seconds=60))]
    """

    def __init__(
        self,
        times: int,
        seconds: int,
        identifier: Callable[[Request], Awaitable[str]] = get_client_ip_identifier,
    ):
        self.times = times
        self.seconds = seconds
        self.identifier = identifier
        self.rate = Rate(times, seconds * 1000)
        self.prefix = f"{KEY_PREFIX}:{times}per{seconds}s"
        self._factory: _PerIdentityBucketFactory | None = None
        self._limiter: Limiter | None = None

    async def _get_limiter(self) -> Limiter:
        """Build the limiter on first use, once Redis is available.

        Route dependencies are constructed at import time, before the lifespan
        handler has connected to Redis, so this cannot happen in __init__.
        """
        if self._limiter is None:
            redis = get_redis()
            if redis is None:
                raise RuntimeError("Redis is not initialized; cannot enforce rate limits")
            script_hash = await redis.script_load(LuaScript.PUT_ITEM)
            self._factory = _PerIdentityBucketFactory(redis, [self.rate], self.prefix, script_hash)
            self._limiter = Limiter(self._factory)
        return self._limiter

    async def __call__(self, request: Request) -> None:
        limiter = await self._get_limiter()
        identity = await self.identifier(request)

        allowed = await limiter.try_acquire_async(identity, blocking=False)
        await self._trim(identity)

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too Many Requests",
            )

    async def _trim(self, identity: str) -> None:
        """Drop out-of-window entries and expire keys for idle clients.

        pyrate-limiter's Lua script only ever adds to the sorted set - it sets
        no TTL and removes nothing - so without this both the set and the key
        would grow for as long as a client keeps calling.
        """
        assert self._factory is not None
        key = self._factory.bucket_key(identity)
        cutoff = (time_ns() // 1_000_000) - (self.seconds * 1000)

        pipe = self._factory.redis.pipeline()
        pipe.zremrangebyscore(key, 0, cutoff)
        pipe.expire(key, self.seconds + _TTL_GRACE_SECONDS)
        await pipe.execute()
