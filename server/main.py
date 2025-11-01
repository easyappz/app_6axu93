from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

from server.db.database import init_db
from server.api.routers import auth as auth_router
from server.api.routers import listings as listings_router
from server.api.routers import comments as comments_router

# Toggle CORS if needed (frontend/backend on same host by default)
ENABLE_CORS = False
try:
    from fastapi.middleware.cors import CORSMiddleware  # type: ignore
except Exception:  # pragma: no cover
    CORSMiddleware = None  # type: ignore

MEDIA_ROOT = os.path.join("server", "media")
LISTINGS_MEDIA_DIR = os.path.join(MEDIA_ROOT, "listings")


def ensure_media_dirs() -> None:
    os.makedirs(LISTINGS_MEDIA_DIR, exist_ok=True)


def create_app() -> FastAPI:
    app = FastAPI(title="Avitolog API", version="0.1.0")

    if ENABLE_CORS and CORSMiddleware is not None:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=False,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    ensure_media_dirs()
    init_db()

    # Serve all API under /api prefix
    app.include_router(auth_router.router, prefix="/api")
    app.include_router(listings_router.router, prefix="/api")
    app.include_router(comments_router.router, prefix="/api")

    # Keep media as is
    app.mount("/media", StaticFiles(directory=MEDIA_ROOT), name="media")

    return app


app = create_app()
