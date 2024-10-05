import os
import sys

import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from components.redis_client import AsyncRedisClient, RedisConnectionError, RedisSetError, RedisGetError # type: ignore

async def main():
  redis_client: AsyncRedisClient = AsyncRedisClient()
  await redis_client.connect()
  await redis_client.set("123", "test")

if __name__ == '__main__':
  asyncio.run(main())
