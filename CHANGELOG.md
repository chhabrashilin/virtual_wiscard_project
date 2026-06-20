# Changelog

All notable changes to Virtual WisCard. This project uses date-based entries
(it is a prototype and not yet semantically versioned).

## [Unreleased]

### Added
- **Documentation & safety pass**: `SECURITY.md` (security model, safety checks,
  known limitations, production hardening checklist), `CONTRIBUTING.md`,
  this `CHANGELOG.md`, completed `backend/.env.example` (incl. `ENVIRONMENT`),
  and `frontend/.env.local.example`.
- **Full Wiscard parity bundle**:
  - Unified **Wiscard Cash** account (vending, laundry, bookstore, off-campus).
  - **Meal-plan swipes** (count-based, distinct from dining dollars).
  - **Permission-based door/building access** (RecWell, residence halls, labs).
  - **Madison Metro transit** bus-pass eligibility + tap.
  - **Athletic & event ticketing** with single-use ticket codes.
  - **Lost-card freeze** initiated by the student.
  - New models (`MealPlan`, `AccessPermission`, `TransitPass`, `Ticket`),
    tickets router, expanded services/admin/cards APIs, student dashboard cards,
    verifier modes (door/transit/ticket), admin management UI, and tests.
- **Operator Verifier** page (`/verify`) with camera QR scanning (native
  `BarcodeDetector`) + manual entry.
- Dining and Wisc Print **pay** flows; scannable CODE128 barcode on the card.
- pytest API suite and GitHub Actions CI (backend tests + frontend lint/build).
- `PROJECT_PLAN.md` master plan (vision, scope, architecture, roadmap).

### Fixed
- **Critical**: `get_current_user` compared a `datetime` to a `date`, causing a
  500 on every authenticated request.
- **Critical**: health check used raw `db.execute("SELECT 1")` (invalid under
  SQLAlchemy 2.x) — now wrapped in `text()`.
- **Build**: added a TypeScript declaration for `jsbarcode` (no shipped types),
  which would otherwise break `next build`.
- **UX**: naive UTC timestamps were rendered as local time, breaking the QR
  countdown and history times — timestamps are now UTC-marked (`Z`).
- **Portability**: SQLite-only `check_same_thread` is no longer passed to other
  database drivers (PostgreSQL works now).
- **Robustness**: tables are created on startup; admin/wallet endpoints return
  400 (not 500) on bad input; admin balance updates reject negatives.

### Security
- `SECRET_KEY` is required in production (app refuses to start with the default).
- `.env` excluded from git and Docker images.

### Enhanced
- Richer seeded demo data so every screen has content.

---

## Historical
Earlier hackathon-era notes live in `IMPLEMENTATION_GUIDE.md` and
`HACKATHON_READY.md` and are retained for context. `PROJECT_PLAN.md`,
`README.md`, and `SECURITY.md` are the current source of truth.
