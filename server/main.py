from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from server.db.database import init_db
from server.api.routers import auth as auth_router
from server.api.routers import listings as listings_router
from server.api.routers import comments as comments_router

MEDIA_ROOT = os.path.join("server", "media")
LISTINGS_MEDIA_DIR = os.path.join(MEDIA_ROOT, "listings")

def ensure_media_dirs() -> None:
    os.makedirs(LISTINGS_MEDIA_DIR, exist_ok=True)


def create_app() -> FastAPI:
    app = FastAPI(title="Avitolog API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    ensure_media_dirs()
    init_db()

    app.include_router(auth_router.router)
    app.include_router(listings_router.router)
    app.include_router(comments_router.router)

    app.mount("/media", StaticFiles(directory=MEDIA_ROOT), name="media")

    return app


app = create_app()
