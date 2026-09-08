import json
import uuid
from redis.asyncio import Redis

from app.core.config import settings
from app.schemas.user import UserRead

USER_CACHE_PREFIX = "user"


def _user_key(user_id: uuid.UUID | str) -> str:
    return f"{USER_CACHE_PREFIX}:{user_id}"


async def get_cached_user(redis: Redis, user_id: uuid.UUID | str) -> UserRead | None:
    raw = await redis.get(_user_key(user_id))
    if raw is None:
        return None
    return UserRead.model_validate(json.loads(raw))


async def set_cached_user(redis: Redis, user: UserRead) -> None:
    await redis.set(
        _user_key(user.id),
        user.model_dump_json(),
        ex=settings.REDIS_CACHE_TTL_SECONDS,
    )


async def invalidate_cached_user(redis: Redis, user_id: uuid.UUID | str) -> None:
    await redis.delete(_user_key(user_id))