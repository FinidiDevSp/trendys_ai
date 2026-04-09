# News Radar

News monitoring and classification system with a React admin frontend and Python backend.

## Project Structure

```
├── frontend/          # React admin UI (TailAdmin + Tailwind CSS)
├── backend/           # Python FastAPI backend service
├── CLAUDE.md          # AI development operating guide
└── README.md
```

## Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+
- Git

## Quick Start

### Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (macOS/Linux)
source .venv/bin/activate

# Install dependencies (editable + dev extras)
pip install -e ".[dev]"

# Copy environment config
cp .env.example .env

# Run the server
uvicorn news_radar.main:app --reload
```

The backend starts at http://localhost:8000. Verify with:

```bash
curl http://localhost:8000/health
```

API docs available at http://localhost:8000/docs.

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

The frontend starts at http://localhost:5173.

### Running Tests

```bash
cd backend
pytest
```

## Environment Variables

See `backend/.env.example` for available configuration.

| Variable | Default | Description |
|---|---|---|
| `NR_DEBUG` | `false` | Enable debug mode |
| `NR_DATABASE_URL` | `sqlite+aiosqlite:///./news_radar.db` | Database connection URL |

## Database

The backend uses SQLAlchemy with async support. By default it creates a local SQLite database file.
On startup, tables are created automatically (development mode). For production, use Alembic migrations:

```bash
cd backend
alembic upgrade head
```

## Future Work

- Docker Compose for local development
- CI/CD with GitHub Actions
- PostgreSQL for production persistence
- Authentication for admin UI

See `CLAUDE.md` for full architectural guidance.
