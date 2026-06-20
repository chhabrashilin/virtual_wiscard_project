# Virtual WisCard — Master Plan, Scope & Engineering Document

> The single source of truth for what Virtual WisCard *is*, where it is today, and
> how we take it from "hackathon prototype" to a real, dependable product.
>
> Last updated: 2026-06-19 · Status: **Active development (Phase 1)**

---

## 1. Vision

Replace the physical UW-Madison Wiscard with a secure, verifiable, phone-native
digital student ID that works everywhere the plastic card does — dining halls,
libraries, residence-hall doors, printing, events — and is **impossible to share
or counterfeit**.

One student → one identity → one card that lives on their phone, backed by an
optional blockchain-anchored credential and exportable to Apple/Google Wallet.

### Why it matters
- **Security**: Plastic IDs are trivially shared and faked. A short-lived,
  server-validated QR/credential makes "lending your ID to a friend" useless.
- **Cost & sustainability**: No plastic, no reprints for lost cards.
- **Experience**: Instant issuance, real-time balances, full activity history.
- **Foundation**: A platform for verifiable campus credentials (library cards,
  event tickets, lab access) — not just one card.

---

## 2. Personas & Core Use Cases

| Persona | Needs |
|---|---|
| **Student** | View their ID, generate a scannable access code, check/spend balances, see history, add card to wallet |
| **Service operator** (dining cashier, library desk, door reader) | Scan a student's code and instantly get a verified yes/no + identity |
| **Administrator** | Issue/revoke cards, manage balances, deactivate accounts, view usage analytics |

### Primary end-to-end loop (the product's heartbeat)
1. Student logs in → sees their virtual card.
2. Student taps **Generate Access Code** → a 5-minute QR token appears.
3. Operator opens the **Verifier** → scans/enters the token → backend validates →
   shows ✅ identity + logs the access.
4. The event appears in the student's **Activity History** and admin analytics.

This loop must be flawless, fast, and demoable on two devices. Everything else
(blockchain, wallet passes) is an enhancement on top of it.

---

## 3. Current State Assessment (as of this document)

### What exists and works conceptually
- FastAPI backend with JWT auth, SQLAlchemy models, routers for auth/cards/
  services/admin/blockchain/wallet.
- Next.js 14 + Tailwind frontend: login, dashboard, admin, virtual card, QR
  display with countdown, service cards, transaction history, blockchain card.
- Solidity soulbound NFT contract (`WisCardNFT.sol`) + deployment guide.
- Apple Wallet `pass.json` generation endpoint.
- Docker Compose for one-command local startup.

### 🔴 Critical bugs found (must fix to be functional)
1. **Auth is fully broken**: `auth.py::get_current_user` compares a `datetime`
   (`expiration_date`) to a `date` (`datetime.utcnow().date()`), which raises
   `TypeError` and returns **HTTP 500 on every authenticated request**. The app
   does not actually work end-to-end today.
2. **Health check broken**: `main.py` calls `db.execute("SELECT 1")`; under
   SQLAlchemy 2.x raw SQL must be wrapped in `text()`.
3. **Empty demo**: `init_db.py` seeds only dining balances — no access logs, so
   "Recent Activity" is always empty and analytics show zeros.

### 🟡 Gaps / rough edges
- No **verifier/scanner** surface — the QR can be generated but never validated
  through the UI, so the core loop is incomplete.
- No actual **barcode** rendered (a dependency is listed but unused; note
  `jsbarcode` does **not** support PDF417 — we use CODE128 for the scannable
  barcode and keep the binary encoding as a conceptual/wallet field).
- `BlockchainCard` surfaces results via `alert()`/`console.log` instead of UI.
- `verify-nft` and NFT minting are placeholders (no real on-chain calls).
- No automated tests, no CI.
- Secrets default to an insecure hardcoded value.
- No photo upload; photos are placeholders.

---

## 4. Architecture

```
                         ┌─────────────────────────────┐
                         │        Browser (Student)     │
                         │  Next.js App Router + Tailwind│
                         └───────────────┬─────────────┘
                                         │ HTTPS / JWT
                         ┌───────────────▼─────────────┐
   ┌──────────────┐      │          FastAPI API         │
   │  Verifier UI │─────▶│  auth · cards · services ·   │
   │ (operator)   │ token│  admin · blockchain · wallet │
   └──────────────┘      └───────────────┬─────────────┘
                                         │ SQLAlchemy
                                  ┌──────▼──────┐
                                  │  SQLite/PG  │
                                  └─────────────┘
        Optional anchors:  Polygon (Soulbound NFT)  ·  Apple/Google Wallet
```

### Tech stack
- **Frontend**: Next.js 14 (App Router), React 18, TypeScript, Tailwind,
  `qrcode.react`, `jsbarcode`, `react-hot-toast`, `ethers` v6.
- **Backend**: FastAPI, SQLAlchemy 2.x, `python-jose` (JWT), `passlib[bcrypt]`,
  `qrcode`, Pydantic v2.
- **DB**: SQLite (dev) → PostgreSQL (prod) via `DATABASE_URL`.
- **Blockchain (optional)**: Solidity 0.8 + OpenZeppelin, Polygon testnet.
- **Infra**: Docker Compose; production target = managed Postgres + container host.

### Data model
- `User` — identity, role, `is_active`, `is_frozen` (lost-card freeze), expiration.
- `Balance` — per-account stored value (`dining`, `print`, `wiscard_cash`).
- `MealPlan` — meal-plan swipes (count) + plan name.
- `AccessPermission` — door/building grants (`resource_key`, `resource_name`).
- `TransitPass` — Madison Metro bus-pass eligibility (status, semester, validity).
- `Ticket` — athletic/event ticket with a unique single-use `code`.
- `AccessToken` — short-lived QR/NFC token, revocable, expiring.
- `AccessLog` — every access/transaction, with `service_type`, `action`,
  `success`, `location`, `created_at`. This powers history + analytics.

---

## 5. Scope

### In scope (the product we're building)
- Secure auth (simulated NetID now; SSO-ready later).
- Virtual card with identity, status, expiry, balances, and a scannable barcode.
- Short-lived, revocable, server-validated access codes (QR).
- A real **verifier** surface for operators (dining, Wiscard Cash, transit,
  permission-based door access, and event-ticket validation).
- Stored value: **Dining Dollars**, unified **Wiscard Cash** (vending, laundry,
  bookstore, off-campus), and **Wisc Print**.
- **Meal-plan swipes** (count-based, distinct from dollars).
- **Permission-based door/building access** (RecWell, residence halls, labs).
- **Madison Metro transit** bus-pass eligibility + tap.
- **Athletic & event ticketing** (single-use ticket codes validated at the gate).
- **Lost-card freeze** initiated by the student.
- Activity history for students.
- Admin: user CRUD, activate/deactivate, balance management, revoke tokens,
  analytics dashboard, plus management of tickets, access grants, meal plans,
  and transit passes.
- Optional enhancements: Apple Wallet pass data, Soulbound NFT credential.

### Out of scope (for now)
- Real UW-Madison SSO/Shibboleth integration (requires institutional access).
- Real payment rails / money movement (balances are simulated stored-value).
- Native iOS/Android apps (PWA-first instead).
- Production-signed `.pkpass` (requires a paid Apple Developer cert).

### Non-functional requirements
- **Security**: no hardcoded secrets, short token TTL, server-side validation,
  least-privilege admin routes, input validation everywhere.
- **Reliability**: transactional balance updates with rollback.
- **Performance**: verifier round-trip < 300ms on localhost.
- **Portability**: one-command Docker startup; SQLite→Postgres with one env var.

---

## 6. Roadmap (phased)

### Phase 0 — Make it actually run ✅ (this change)
- Fix the auth `datetime`/`date` crash.
- Fix the health-check `text()` issue.
- Seed realistic demo data (balances + history) so every screen has content.

### Phase 1 — Complete the core loop ✅ (this change)
- Build the **Verifier/Scanner** page (`/verify`) + API client wiring.
- Render a real **CODE128 barcode** on the virtual card.
- Replace `BlockchainCard` `alert()`/`console.log` with a proper result modal.

### Phase 2 — Hardening & trust (next)
- Automated tests (pytest for API, Playwright/RTL for UI) + GitHub Actions CI.
- Enforce a real `SECRET_KEY` (fail fast if default in production).
- Photo upload + storage; richer card front/back.
- Rate-limit token generation and verification.

### Phase 3 — Real wallet & on-chain (next)
- Camera-based QR scanning in the verifier (mobile-friendly).
- Real `.pkpass` packaging path (documented, cert-gated) + Google Wallet JWT.
- Wire `ethers` to a deployed testnet contract for genuine mint/verify.

### Phase 4 — Platform & scale
- PostgreSQL deployment, migrations (Alembic).
- Multi-credential support (events, lab access).
- Observability (structured logs, metrics), audit trails.

---

## 7. API Surface (current)

| Area | Method & Path | Purpose |
|---|---|---|
| Auth | `POST /api/auth/login` | NetID/password → JWT |
| Auth | `GET /api/auth/me` | Current user |
| Cards | `GET /api/cards/my-card` | Card + balances |
| Cards | `POST /api/cards/generate-qr` | 5-min access token + QR image |
| Cards | `GET /api/cards/balances` | All balances |
| Cards | `GET /api/cards/transaction-history` | Activity log |
| Cards | `POST /api/cards/freeze` · `/unfreeze` | Lost-card freeze toggle |
| Services | `POST /api/services/access` | **Validate a scanned token** (verifier; supports `resource` for door access and `transit`) |
| Services | `POST /api/services/dining/check-balance` · `/use` | Dining dollars |
| Services | `GET /api/services/dining/swipes` · `POST /dining/swipe` | Meal-plan swipes |
| Services | `POST /api/services/wiscard-cash/check-balance` · `/use` | Unified Wiscard Cash |
| Services | `POST /api/services/print/check-balance` · `/use` | Wisc Print |
| Services | `GET /api/services/transit/pass` | Transit bus-pass status |
| Services | `GET /api/services/access-permissions` | My door/building access |
| Services | `POST /api/services/library/checkout` | Library checkout |
| Services | `POST /api/services/residence/access` | Residence door access |
| Tickets | `GET /api/tickets` | My event tickets |
| Tickets | `POST /api/tickets/validate` | Validate a ticket at the gate (single-use) |
| Admin | `POST /api/admin/permissions` · `/permissions/revoke` | Grant/revoke door access |
| Admin | `POST /api/admin/meal-swipes` | Set a meal plan |
| Admin | `POST /api/admin/transit` | Set transit eligibility |
| Admin | `POST /api/admin/tickets` | Issue an event ticket |
| Admin | `GET/POST /api/admin/users` | List/create users |
| Admin | `PATCH /api/admin/users/{id}/toggle-active` | Activate/deactivate |
| Admin | `POST /api/admin/balances` | Set balance |
| Admin | `GET /api/admin/stats` | Analytics |
| Admin | `POST /api/admin/revoke-token` | Revoke a token |
| Blockchain | `POST /api/blockchain/student-id-to-binary` | Binary encoding |
| Blockchain | `POST /api/blockchain/mint-nft` | NFT metadata prep |
| Blockchain | `GET /api/blockchain/verify-nft/{wallet}` | Ownership (placeholder) |
| Wallet | `POST /api/wallet/generate-pkpass-data` | Apple pass JSON |
| Wallet | `GET /api/wallet/barcode-data` | Barcode payload |

---

## 8. Security Model
- **Authentication**: JWT (HS256), 30-min expiry, `sub = netid`.
- **Authorization**: `get_current_user` (active + non-expired) and
  `get_current_admin_user` (admin-only) dependencies.
- **Access codes**: random 32-byte URL-safe tokens, 5-min TTL, single source of
  truth in DB, revocable, validated server-side only.
- **Secrets**: from environment; production must reject the default key.
- **Input validation**: Pydantic validators (e.g., dining amount bounds).
- **Anti-sharing**: short TTL + server validation + optional soulbound NFT.

---

## 9. Testing Strategy (target)
- **Backend unit/integration**: pytest + httpx `TestClient` covering auth,
  token lifecycle (generate → validate → expire/revoke), balance transactions
  (including insufficient-funds and rollback), admin guards.
- **Frontend**: React Testing Library for components; Playwright for the
  login → generate code → verify happy path across two contexts.
- **CI**: GitHub Actions running both suites on PR.

---

## 10. Deployment
- **Local**: `docker-compose up --build` → frontend :3000, backend :8000.
- **Env**: copy `backend/.env.example` → `.env`; generate `SECRET_KEY` with
  `python -c "import secrets; print(secrets.token_hex(32))"`.
- **Production**: Postgres via `DATABASE_URL`, restricted `CORS_ORIGINS`,
  `ENVIRONMENT=production`, no `--reload`, real `SECRET_KEY`.

---

## 11. Definition of Done (per feature)
A feature is done when it: works end-to-end through the UI, has server-side
validation, handles error states gracefully in the UI, logs to `AccessLog`
where relevant, and is reflected in this document.

---

## 12. Changelog
- **2026-06-19** — Created master plan. Fixed critical auth/date crash and
  health-check; enriched seed data; added Verifier page + barcode on card;
  reworked BlockchainCard result UX. (Phase 0 + Phase 1)
- **2026-06-19** — Completed services (dining/print pay), camera QR scanning,
  Apple Wallet pass download, production SECRET_KEY enforcement, pytest suite +
  CI. (Phase 2 partial)
- **2026-06-19** — Full audit pass. Fixed: jsbarcode missing TS types
  (build break), naive-UTC timestamps breaking the browser countdown/history
  (now UTC-marked), SQLite-only `check_same_thread` blocking Postgres, missing
  table creation on startup, negative-balance admin validation, wallet/admin
  500s on bad input (now 400). Added regression tests.
- **2026-06-19** — Full Wiscard parity bundle: unified **Wiscard Cash**,
  **meal-plan swipes**, **permission-based door/building access**, **Madison
  Metro transit pass**, **athletic/event ticketing**, and **lost-card freeze**.
  New models (MealPlan, AccessPermission, TransitPass, Ticket) + lightweight
  schema migration, tickets router, expanded services/admin APIs, student
  dashboard cards, verifier modes (door/transit/ticket), admin management UI,
  and tests for every new capability.
