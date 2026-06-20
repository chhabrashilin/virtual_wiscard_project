# Security

This document describes the security model of Virtual WisCard, the safety checks
that are in place, known limitations, and the steps required before any real
("production") deployment.

> Status: **prototype / educational**. Do not deploy to handle real student data,
> real money, or real building access without completing the production checklist
> in section 6 and a professional security review.

---

## 1. Security model

### Authentication
- Login exchanges NetID + password for a **JWT** (HS256), signed with `SECRET_KEY`.
- Tokens expire after `JWT_EXPIRATION_MINUTES` (default 30).
- Passwords are hashed with **bcrypt** (`passlib`). Plaintext passwords are never
  stored or logged.

### Authorization
- `get_current_user` rejects requests for inactive or expired cards.
- `get_current_admin_user` gates all `/api/admin/*` routes to admins.
- Students can only read/affect their own card, balances, tickets, and history.

### Access codes (QR tokens)
- Generated as **32-byte URL-safe random tokens** (`secrets.token_urlsafe(32)`),
  stored server-side, expiring after 5 minutes, and individually revocable.
- Validated **only** on the server. A frozen, inactive, or expired account's
  token is rejected at the gate.

### Event tickets
- Each ticket has a unique random `code` and is **single-use**: once validated at
  a gate it is marked `used` and cannot be reused.

### Lost-card freeze
- A student can freeze their card instantly. While frozen, new access codes
  cannot be generated and any outstanding token is rejected.

### Input validation
- Pydantic models validate all request bodies. Monetary amounts are bounded and
  must be positive; balances and swipe counts cannot be set negative.
- All database access goes through SQLAlchemy ORM (parameterized) — no raw,
  string-built SQL with user input.

### Secrets
- `SECRET_KEY` and all credentials come from environment variables.
- In `ENVIRONMENT=production`, the app **refuses to start** with the default key.
- `.env` files are git-ignored and excluded from Docker images (`.dockerignore`).

---

## 2. Safety checks in place
- ✅ No hardcoded secrets in source; production rejects the default `SECRET_KEY`.
- ✅ `.env` excluded from git and Docker build context.
- ✅ Passwords hashed (bcrypt), never returned by the API.
- ✅ Short-lived, high-entropy, revocable access tokens.
- ✅ Single-use event tickets.
- ✅ Authorization checks on every protected route; admin routes gated.
- ✅ Pydantic validation; positive/bounded amounts; no negative balances.
- ✅ Transactional balance updates with rollback on error.
- ✅ CORS restricted to configured origins.
- ✅ Automated test suite (pytest) covering auth guards, the verify loop,
  freeze enforcement, single-use tickets, and permission denial — run in CI.

---

## 3. Known limitations (by design, for a prototype)
- **Authentication is simulated** (dummy NetID accounts), not real UW-Madison SSO.
- **Scanner endpoints are public** (`/api/services/access`, `/api/tickets/validate`)
  so a reader device need not authenticate. They are safe against guessing
  (high-entropy tokens) but are **not rate-limited** — see hardening below.
- **No rate limiting / brute-force lockout** on login or scanner endpoints.
- **Blockchain & Apple Wallet are simulations** — no real on-chain calls and no
  signed `.pkpass` (requires a paid Apple Developer certificate).
- **SQLite by default** — fine for dev, not for concurrent production load.
- **No HTTPS in the dev stack** — terminate TLS at a reverse proxy in production.
- **No audit log of admin actions** beyond access logs.

---

## 4. Reporting a vulnerability
This is an educational project without a formal disclosure process. If you find
an issue, open a private issue or contact the maintainer directly. Please do not
post exploit details publicly while the project is in use.

---

## 5. Dependency hygiene
- Backend versions are pinned in `requirements.txt` / `requirements-dev.txt`.
- Frontend versions are locked via `package-lock.json` (`npm ci` in CI).
- Known cosmetic warning: `passlib 1.7.4` + `bcrypt 4.x` logs
  `(trapped) error reading bcrypt version`. It is harmless (hashing still works);
  pin `bcrypt==4.0.1` or upgrade `passlib` to silence it.
- Recommend running `pip-audit` and `npm audit` in CI before any real launch.

---

## 6. Production hardening checklist (do these before going live)
- [ ] Set `ENVIRONMENT=production` and a strong, unique `SECRET_KEY`.
- [ ] Replace simulated login with real UW-Madison SSO/Shibboleth.
- [ ] Move to PostgreSQL; add Alembic migrations (drop the dev `ensure_schema`).
- [ ] Put the API behind HTTPS (reverse proxy / load balancer) and set HSTS.
- [ ] Restrict `CORS_ORIGINS` to the real frontend domain only.
- [ ] Add rate limiting / lockout on `/api/auth/login` and scanner endpoints
      (e.g. `slowapi` or gateway-level throttling).
- [ ] Require authenticated, registered reader devices for scanner endpoints.
- [ ] Lower JWT lifetime and add refresh-token rotation.
- [ ] Add security headers (CSP, X-Frame-Options, etc.).
- [ ] Add structured audit logging for admin actions.
- [ ] Run `pip-audit` and `npm audit`; resolve high/critical findings.
- [ ] Remove `--reload`, source volume mounts, and seeded demo accounts.
- [ ] Independent security review / penetration test.
