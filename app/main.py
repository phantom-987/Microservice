from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import configure_logging
from app.api.users import router as users_router

from app.api.auth import router as auth_router

configure_logging()

app = FastAPI(title=settings.APP_NAME)

app.include_router(users_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}

