import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from server.db.database import Base, engine
from server.api.routers.auth import router as auth_router
from server.api.routers.listings import router as listings_router
from server.api.routers.comments import router as comments_router

MEDIA_DIR = os.path.join(os.path.dirname(__file__), "media")
MEDIA_LISTINGS_DIR = os.path.join(MEDIA_DIR, "listings")

app = FastAPI(title="Avitolog API", version="0.1.0")

# CORS for development convenience
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables and media dirs on startup
@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    os.makedirs(MEDIA_LISTINGS_DIR, exist_ok=True)

# Routers
app.include_router(auth_router, tags=["auth"])
app.include_router(listings_router, tags=["listings"])
app.include_router(comments_router, tags=["comments"])

# Static media
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")


@app.get("/healthz")
def healthz():
    return {"status": "ok"}
