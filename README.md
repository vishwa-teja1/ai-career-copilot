# AI Career Copilot 🎯

An AI-powered career assistant I'm building that takes one resume upload and turns it into a
structured profile — which will later power job matching, ATS scoring, resume tailoring, and
auto-generated cover letters.

This is **Module 1** of a bigger project: **Auth + AI Resume Parsing**. More modules (job search,
matching, tailoring, interview prep) are on the way.

---

## Why I built this

Applying to jobs is repetitive — rewriting the same resume details, re-explaining the same
skills, tailoring things manually for every application. I wanted to build something that does
the boring parts automatically, while learning how a real production-style full-stack + AI app
is actually put together (auth, databases, clean architecture, AI integration, deployment) —
not just another CRUD tutorial project.

---

## What it does (so far)

- Create an account (email + OTP verification) and log in securely
- Upload your resume once (PDF/DOCX)
- AI reads it and builds a structured profile: skills, experience, education, projects,
  certifications, achievements
- Edit anything the AI got wrong, right from the dashboard
- Everything downstream (future modules) will reuse this profile instead of re-reading the resume
  every time

---

## Tech stack

**Frontend:** Next.js 14, TypeScript, Tailwind CSS, Zustand, React Query
**Backend:** FastAPI, PostgreSQL, SQLAlchemy, Alembic
**AI:** OpenAI (structured outputs for resume parsing)
**Auth:** JWT (access + refresh tokens), OTP email verification
**Deployment:** Docker, Render, Vercel

---

## Screenshots

*(adding these soon)*

---

## Running it yourself

### Easiest way (no Docker needed)

```bash
git clone https://github.com/vishwa-teja1/ai-career-copilot.git
cd ai-career-copilot
./start.sh
```

First run sets everything up automatically (Python environment, dependencies, a local database).
Then just open **http://localhost:3000**.

> Since there's no email service hooked up locally, your OTP code will just print in the
> terminal — check there after registering.

### With Docker

```bash
cp backend/.env.example backend/.env
# fill in SECRET_KEY, FIELD_ENCRYPTION_KEY, and (optionally) OPENAI_API_KEY

docker compose up --build
```

Generate the two required keys with:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Running tests

```bash
cd backend
pip install -r requirements.txt
pytest -v
```

---

## What's next

- Job search + AI semantic matching against real listings
- ATS compatibility scoring
- AI resume tailoring per job description
- Auto-generated cover letters
- Interview prep AI

---

## About me

I'm Teja, a final-year Information Technology student. Building this as part of my portfolio
while prepping for SWE/AI engineering roles. Always open to feedback — feel free to open an issue
or reach out.

**GitHub:** [@vishwa-teja1](https://github.com/vishwa-teja1)
