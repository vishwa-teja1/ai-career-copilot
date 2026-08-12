# AI Career Copilot — Module 1: Auth & Resume Parsing

This is the first module of AI Career Copilot: account creation/login and the AI-powered
resume parser that turns one uploaded resume into a structured **Master Candidate Profile**.
Every later module (job matching, ATS scoring, tailoring, cover letters, auto-apply) will read
from this profile — the original PDF/DOCX is stored once as an audit artifact and never
re-parsed on the fly.

## What's included

**Backend (FastAPI + PostgreSQL)**
- Email/password auth with OTP email verification, JWT access + refresh tokens, RBAC (user/admin)
- Google/GitHub OAuth endpoint scaffolded — see "Known gap" below
- Resume upload (PDF/DOCX) → text extraction → AI parsing (OpenAI structured outputs) → structured profile
- Clean architecture: API routes → services → repositories → SQLAlchemy models, all DI-wired via FastAPI `Depends`
- Field-level encryption (Fernet) for stored raw resume text
- Rate limiting, security headers, uniform error envelope, audit logging
- Alembic migration for the full schema
- 19 passing pytest tests (auth flows + resume upload/parsing flows, OpenAI mocked)

**Frontend (Next.js 14 + TypeScript + Tailwind)**
- Register → OTP verification → Login flow
- Dashboard shell with sidebar nav
- Resume upload page (drag-and-drop, parsing status, error states)
- Profile page rendering the full structured profile (skills, experience, education, projects,
  certifications, achievements) with inline-editable headline
- Zustand for auth state (persisted), React Query for server state, automatic token refresh via axios interceptor

**Infra**
- Multi-stage Dockerfiles for both services
- `docker-compose.yml` wiring Postgres + Redis + backend + frontend, running migrations on boot

## Known gap (intentional)

The `/api/v1/auth/oauth` endpoint is scaffolded but raises `NotImplementedError` rather than being
faked. Wiring real Google/GitHub login requires *your* OAuth client ID/secret from each provider's
console — plug in `google-auth`'s `id_token.verify_oauth2_token` (Google) or GitHub's OAuth App
token exchange, then call `auth_service.login_oauth(...)`, which is already implemented and tested
end-to-end for the account-creation/token-issuing side.

## Running locally

### Easiest — one command, no Docker

```bash
./start.sh
```

That's it. First run automatically: creates a Python virtual environment, installs backend
dependencies, generates `backend/.env` with fresh secrets, creates a local SQLite database,
and installs frontend dependencies. Every run after that just starts both servers.

- Frontend: http://localhost:3000
- Backend: http://localhost:8000 (Swagger docs at `/api/docs`)
- OTP codes print directly in this terminal (no email server is configured by default)
- Press `Ctrl+C` to stop both servers together

To enable AI resume parsing, open `backend/.env` after the first run and set
`OPENAI_API_KEY=sk-...`, then restart `./start.sh`.

Uses SQLite instead of Postgres, so there's nothing else to install. If you later want to run
against a real Postgres database, use the Docker path below instead.

### Quickest path — Docker

```bash
cp backend/.env.example backend/.env
# edit backend/.env: set SECRET_KEY, FIELD_ENCRYPTION_KEY, and OPENAI_API_KEY

docker compose up --build
```

- Backend: http://localhost:8000 (Swagger docs at `/api/docs`)
- Frontend: http://localhost:3000

Note on `BACKEND_INTERNAL_URL`: the frontend's Next.js server proxies `/api/*` requests to the
backend server-side (see `frontend/next.config.js`). Inside `docker-compose`, that proxy runs
*inside the frontend container*, where `localhost` means itself, not the backend container — so
`docker-compose.yml` sets `BACKEND_INTERNAL_URL=http://backend:8000` (the Docker service name) for
that container specifically. `NEXT_PUBLIC_API_URL` is separate and unrelated to this — it's baked
into the browser bundle and is what the docs/examples above refer to.

Generate the two required secrets:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"          # SECRET_KEY
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"  # FIELD_ENCRYPTION_KEY
```

### Manual (without Docker)

**Backend**
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in SECRET_KEY, FIELD_ENCRYPTION_KEY, OPENAI_API_KEY
# point DATABASE_URL at a local Postgres, then:
alembic upgrade head
uvicorn app.main:app --reload
```

**Zero-dependency smoke test (no Postgres install needed):**
```bash
# in .env: DATABASE_URL=sqlite:///./dev.db
python scripts/create_dev_db.py   # Alembic's migration is Postgres-only (native UUID/ARRAY
                                   # types) - this bypasses it for a quick local SQLite spin-up
uvicorn app.main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

### Running tests

```bash
cd backend
pip install -r requirements.txt
pytest -v
```

Tests run against an in-memory SQLite DB with the OpenAI call mocked — no API key or live
database needed to run the suite.

## Without an OpenAI key

`OPENAI_API_KEY` can be left blank to boot the app, but resume upload will return a clear
502 error ("AI parsing failed... you can retry, or fill in your profile manually") instead of
silently failing — and the `/profile/me` PATCH endpoint lets you fill in the profile by hand.

## Architecture notes

- **Repository pattern**: `app/repositories/` is the only layer that touches SQLAlchemy sessions
  directly. Services never write raw queries.
- **Portable types**: `app/core/db_types.py` defines `GUID`/`StringArray` types that compile to
  native Postgres `UUID`/`ARRAY` in production but degrade to SQLite-compatible types for tests —
  same model file, no test-only schema fork.
- **AI parsing contract**: `app/ai/schema.py` defines a strict JSON schema OpenAI's structured
  outputs must conform to, with an explicit "never invent experience" system prompt — matches the
  product requirement that tailoring/cover letters never fabricate a candidate's background.

## Next module

Per the original spec, the next module (once you confirm) is **Job Search + AI Semantic Matching +
ATS Scoring** — built against Greenhouse/Lever's public job APIs plus user-pasted job
descriptions/URLs for LinkedIn/Indeed/Naukri (see the note on automated scraping/auto-apply from
earlier in this conversation).
