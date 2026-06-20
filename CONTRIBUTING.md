# Contributing

Thanks for working on Virtual WisCard. This guide covers local setup, how to run
and test, and project conventions.

> Read **[PROJECT_PLAN.md](./PROJECT_PLAN.md)** for the vision/architecture and
> **[SECURITY.md](./SECURITY.md)** for the security model before making changes.

---

## Prerequisites
- Python 3.11+
- Node.js 20+
- (Optional) Docker + Docker Compose

---

## Local setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env            # then set SECRET_KEY
python init_db.py               # create tables + seed demo data
uvicorn app.main:app --reload   # http://localhost:8000  (docs at /docs)
```

### Frontend
```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev                     # http://localhost:3000
```

### Docker (everything at once)
```bash
docker-compose up --build
```

---

## Running tests & checks

### Backend (pytest)
```bash
cd backend
pytest
```

### Frontend (lint + type-checked build)
```bash
cd frontend
npm run lint
npm run build
```

CI (`.github/workflows/ci.yml`) runs all of the above on every push and PR.

---

## Test accounts (seeded)
| Role | NetID | Password |
|---|---|---|
| Student | `jdoe` / `jsmith` / `bwilliams` | `password123` |
| Admin | `admin` | `admin123` |

These are **demo only** and must be removed before any real deployment.

---

## Project structure
```
backend/
  app/
    main.py            # FastAPI app, startup, health
    auth.py            # JWT, hashing, current-user dependencies
    database.py        # engine/session + ensure_schema (dev migration)
    models.py          # SQLAlchemy models
    utils.py           # token + QR helpers
    routers/           # auth, cards, services, admin, blockchain, wallet, tickets
  tests/               # pytest suite (+ conftest fixtures)
  init_db.py           # table creation + demo seed
frontend/
  app/                 # Next.js routes: /, /login, /dashboard, /admin, /verify
  components/          # React components
  lib/api.ts           # API client
  types/               # TS declarations (window, jsbarcode)
contracts/             # Solidity soulbound NFT + deployment guide
```

---

## Conventions
- **Database changes**: add new tables via models (created by `create_all`). New
  *columns* on existing tables need an entry in `database.py::_ADDED_COLUMNS`
  (dev shim) — production should use Alembic instead.
- **Datetimes**: store naive UTC; when returning a timestamp the browser will
  render as a time, append `"Z"` so it is interpreted as UTC.
- **Money/counts**: validate with Pydantic; keep amounts positive and bounded;
  never allow negative balances.
- **New endpoints**: add server-side validation, log to `AccessLog` where
  relevant, handle error states in the UI, add a test, and update the docs
  (README + PROJECT_PLAN API table).
- **Secrets**: only via environment variables; never commit `.env`.

---

## Definition of done
A change is done when it works end-to-end through the UI, is validated
server-side, handles errors gracefully, has a test, passes lint/build, and is
reflected in the documentation.
