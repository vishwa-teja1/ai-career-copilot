#!/usr/bin/env bash
# Runs the whole app locally with ONE command - no Docker required.
#
#   ./start.sh
#
# First run does one-time setup automatically:
#   - creates a Python venv and installs backend dependencies
#   - creates backend/.env with freshly generated secrets (if missing)
#   - creates a local SQLite database (if missing)
#   - installs frontend dependencies
# Every run after that just starts the backend + frontend.
#
# Stop with Ctrl+C - both servers shut down together.

set -e
cd "$(dirname "$0")"

BACKEND_DIR="backend"
FRONTEND_DIR="frontend"
VENV_DIR="$BACKEND_DIR/venv"

# Pick python3/python and the right venv bin folder (Linux/Mac vs Windows)
PYTHON_BIN=$(command -v python3 || command -v python)
if [ -z "$PYTHON_BIN" ]; then
  echo "Python 3 is required but wasn't found. Install it from https://python.org and try again."
  exit 1
fi
if [ -d "$VENV_DIR/Scripts" ]; then
  VENV_BIN="$VENV_DIR/Scripts"   # Windows venv layout
else
  VENV_BIN="$VENV_DIR/bin"       # Linux/Mac venv layout
fi

echo "=== Backend setup ==="
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating Python virtual environment..."
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

echo "Installing backend dependencies (only installs what's missing/changed)..."
"$VENV_BIN/pip" install -q --upgrade pip
"$VENV_BIN/pip" install -q -r "$BACKEND_DIR/requirements.txt"

if [ ! -f "$BACKEND_DIR/.env" ]; then
  echo "First run: generating backend/.env with fresh secrets and a local SQLite database..."
  SECRET_KEY=$("$VENV_BIN/python" -c "import secrets; print(secrets.token_urlsafe(32))")
  FIELD_KEY=$("$VENV_BIN/python" -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
  cat > "$BACKEND_DIR/.env" << EOF
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=$SECRET_KEY
FIELD_ENCRYPTION_KEY=$FIELD_KEY
CORS_ORIGINS=http://localhost:3000
DATABASE_URL=sqlite:///./dev.db
REDIS_URL=redis://localhost:6379/0
STORAGE_BACKEND=local
UPLOAD_DIR=./storage/resumes
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
EOF
  echo "backend/.env created. To enable AI resume parsing, open backend/.env and set OPENAI_API_KEY=sk-..."
fi

if [ ! -f "$BACKEND_DIR/dev.db" ]; then
  echo "Creating local SQLite database..."
  (cd "$BACKEND_DIR" && "../$VENV_BIN/python" scripts/create_dev_db.py)
fi

echo ""
echo "=== Frontend setup ==="
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
  echo "Installing frontend dependencies (first run only, this takes a minute)..."
  (cd "$FRONTEND_DIR" && npm install)
fi
if [ ! -f "$FRONTEND_DIR/.env.local" ]; then
  echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > "$FRONTEND_DIR/.env.local"
fi

echo ""
echo "=== Starting servers ==="
echo "Backend:  http://localhost:8000  (API docs: http://localhost:8000/api/docs)"
echo "Frontend: http://localhost:3000"
echo "OTP codes will print in this terminal (no email server configured)."
echo "Press Ctrl+C to stop both."
echo ""

cleanup() {
  echo ""
  echo "Stopping servers..."
  kill "$BACKEND_PID" 2>/dev/null
  wait "$BACKEND_PID" 2>/dev/null
  exit 0
}
trap cleanup INT TERM

(cd "$BACKEND_DIR" && "../$VENV_BIN/uvicorn" app.main:app --reload --port 8000) &
BACKEND_PID=$!

# Give the backend a moment before starting the frontend, and confirm it's alive
sleep 2
if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
  echo "Backend failed to start - check the output above for the error."
  exit 1
fi

(cd "$FRONTEND_DIR" && npm run dev)

cleanup
