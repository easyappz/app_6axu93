import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from server.db.database import init_db
from server.api.routers.auth import router as auth_router
from server.api.routers.listings import router as listings_router
from server.api.routers.comments import router as comments_router

MEDIA_ROOT = os.path.join(os.path.dirname(__file__), "media")
MEDIA_LISTINGS_DIR = os.path.join(MEDIA_ROOT, "listings")


def ensure_media_dirs() -> None:
    os.makedirs(MEDIA_LISTINGS_DIR, exist_ok=True)


def create_app() -> FastAPI:
    app = FastAPI(title="Avitolog API", version="0.1.0")

    # CORS for development (can be restricted later)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(auth_router)
    app.include_router(listings_router)
    app.include_router(comments_router)

    # Static /media serving
    app.mount("/media", StaticFiles(directory=MEDIA_ROOT), name="media")

    @app.on_event("startup")
    def on_startup() -> None:
        ensure_media_dirs()
        init_db()

    return app


app = create_app()
