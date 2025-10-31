from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from server.db.database import init_db
from server.api.routers.auth import router as auth_router
from server.api.routers.listings import router as listings_router
from server.api.routers.comments import router as comments_router

MEDIA_ROOT = Path(__file__).parent / "media"
LISTINGS_MEDIA_DIR = MEDIA_ROOT / "listings"

app = FastAPI(title="Avitolog API", version="0.1.0")

# Ensure media directories exist at startup
@app.on_event("startup")
def on_startup() -> None:
    init_db()
    LISTINGS_MEDIA_DIR.mkdir(parents=True, exist_ok=True)

# Static files serving for media
app.mount("/media", StaticFiles(directory=str(MEDIA_ROOT)), name="media")

# Routers
app.include_router(auth_router)
app.include_router(listings_router)
app.include_router(comments_router)


@app.get("/health", tags=["system"])
def healthcheck():
    return {"status": "ok"}
