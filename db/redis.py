import redis.asyncio as red_db
from config import settings



token_blocklist = red_db.from_url(settings.REDIS_URL)


async def add_jti_to_blocklist(jti: str):
    await token_blocklist.set(name=jti, value="", ex=3600)


async def token_in_blocklist(jti: str):
    jti_value = await token_blocklist.get(jti)
    return jti_value is not None
