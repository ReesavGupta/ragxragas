import os
import redis.asyncio as aioredis
import json
from typing import Optional

class AsyncRedisCache:
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.data_version = os.getenv("DATA_VERSION", "v1")
        self._pool = None

    async def get_pool(self):
        if self._pool is None:
            self._pool = aioredis.from_url(self.redis_url, decode_responses=True)
        return self._pool

    def _make_key(self, key: str) -> str:
        return f"{self.data_version}:cache:{key}"

    async def get(self, key: str) -> Optional[dict]:
        pool = await self.get_pool()
        value = await pool.get(self._make_key(key))
        if isinstance(value, str):
            return json.loads(value)
        return None

    async def set(self, key: str, value: dict, ttl: int):
        pool = await self.get_pool()
        await pool.set(self._make_key(key), json.dumps(value), ex=ttl) 