import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.redis import get_redis
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services import user_service, cache
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await user_service.create_user(db, data)
    except user_service.UserAlreadyExistsError:
        raise HTTPException(status_code=400, detail="Email already registered")


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    cached = await cache.get_cached_user(redis, user_id)
    if cached is not None:
        return cached

    user = await user_service.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user_read = UserRead.model_validate(user)
    await cache.set_cached_user(redis, user_read)
    return user_read


@router.get("/", response_model=list[UserRead])
async def list_users(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    users, _ = await user_service.list_users(db, skip, limit)
    return users


@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: uuid.UUID,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user),
):
    try:
        user = await user_service.update_user(db, user_id, data)
    except user_service.UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    await cache.invalidate_cached_user(redis, user_id)
    return user



@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user),
):
    try:
        await user_service.delete_user(db, user_id)
    except user_service.UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    await cache.invalidate_cached_user(redis, user_id)