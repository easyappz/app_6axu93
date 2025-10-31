# Avitolog API (FastAPI)

Lightweight backend to ingest Avito listings, authenticate users via JWT and manage comments.

Requirements
- Python 3.10+

Install
1. Create a virtual environment and install deps:
   pip install -r server/requirements.txt

2. Run the server (auto creates SQLite DB at ./app.db and media directories):
   uvicorn server.main:app --reload

Auth
- After registration/login you receive a JWT token.
- Send it in headers: Authorization: Bearer <token>

Media
- Images are stored locally under server/media/listings and served from /media path.

Endpoints (short)
- POST /auth/register { email, password, name? } -> { user, token }
- POST /auth/login { email, password } -> { user, token }
- GET /auth/me -> user
- POST /listings/ingest { url } -> { listing }
- GET /listings?sort=views&limit=10 -> { items, total }
- GET /listings/{id} -> { listing } (increments view_count)
- GET /listings/{id}/comments -> { items }
- POST /listings/{id}/comments { content } (auth) -> { comment }
- PATCH /comments/{id} { content } (author only) -> { comment }
- DELETE /comments/{id} (author only) -> { success: true }

Notes
- Passwords are hashed with bcrypt (passlib).
- JWT expires in 7 days.
- Only images are saved locally when ingesting listings; if image detection fails, listing is created without an image.
