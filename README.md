# Virtual Wiscard

A full-stack digital student ID system for UW-Madison students that replaces the physical Wiscard with a virtual card accessible through a web application.

### Documentation
- 📘 **[PROJECT_PLAN.md](./PROJECT_PLAN.md)** — vision, scope, architecture, data model, API surface, roadmap
- 🔐 **[SECURITY.md](./SECURITY.md)** — security model, safety checks, known limits, production hardening checklist
- 🤝 **[CONTRIBUTING.md](./CONTRIBUTING.md)** — local setup, running, testing, conventions
- 📝 **[CHANGELOG.md](./CHANGELOG.md)** — what changed and when

## Features

- 🪪 **Student Authentication**: Login using UW NetID (simulated with dummy accounts)
- 💳 **Virtual ID Display**: Shows name, photo, student ID, expiration, active status, and a scannable CODE128 barcode
- 🔐 **Secure QR Code**: Generate temporary (5-minute) access codes for identity verification
- 🛂 **Verifier station** (`/verify`): An operator-facing page that scans (camera) or accepts a pasted token and validates it in real time — for dining, Wiscard Cash, transit, **permission-based door access**, and **event-ticket** check-in
- 🏫 **Service Integration**:
  - **Dining Dollars** (check + pay) and **meal-plan swipes** (count-based)
  - Unified **Wiscard Cash** (vending, laundry, bookstore, off-campus)
  - **Wisc Print** (check + pay)
  - **Permission-based door/building access** (RecWell, residence halls, labs)
  - **Madison Metro transit** bus-pass eligibility + tap
  - Library entry and checkout validation
- 🎟️ **Athletic & Event Ticketing**: tickets with single-use QR codes validated at the gate
- 🧊 **Lost-card Freeze**: students can instantly freeze/unfreeze their card
- 📊 **Activity History**: Every access/transaction is logged and shown to the student
- ⚙️ **Admin Dashboard**: Manage users, balances, **access grants, meal plans, transit passes, and tickets**, revoke cards, and see usage analytics
- 🔗 **Blockchain & Wallet (optional)**: Soulbound NFT metadata prep + Apple Wallet `pass.json` download
- ✅ **Tested**: pytest API suite + GitHub Actions CI (backend tests, frontend lint/build)

## Tech Stack

- **Frontend**: Next.js 14, React, TypeScript, Tailwind CSS
- **Backend**: FastAPI (Python), SQLAlchemy, JWT authentication
- **Database**: SQLite
- **QR Code**: qrcode library
- **Deployment**: Docker Compose

## Project Structure

```
virtual_wiscard_project/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI application
│   │   ├── database.py       # Database configuration
│   │   ├── models.py         # SQLAlchemy models
│   │   ├── auth.py           # Authentication utilities
│   │   ├── utils.py          # QR code and token utilities
│   │   └── routers/          # API route handlers
│   ├── requirements.txt
│   ├── Dockerfile
│   └── init_db.py            # Database initialization
├── frontend/
│   ├── app/                  # Next.js app directory
│   ├── components/           # React components
│   ├── lib/                  # API client
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Getting Started

### Prerequisites

- Docker and Docker Compose installed
- Git (optional, for cloning)

### Running with Docker Compose

1. **Clone or navigate to the project directory**:
   ```bash
   cd virtual_wiscard_project
   ```

2. **Start the services**:
   ```bash
   docker-compose up --build
   ```

   This will:
   - Build and start the backend API on `http://localhost:8000`
   - Build and start the frontend on `http://localhost:3000`
   - Initialize the database with dummy student accounts

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Running Locally (Without Docker)

#### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```bash
   python init_db.py
   ```

5. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

#### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

## Test Accounts

The database is pre-populated with the following test accounts:

### Students
- **NetID**: `jdoe` | **Password**: `password123`
- **NetID**: `jsmith` | **Password**: `password123`
- **NetID**: `bwilliams` | **Password**: `password123`

### Admin
- **NetID**: `admin` | **Password**: `admin123`

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login with NetID and password
- `GET /api/auth/me` - Get current user information

### Cards
- `GET /api/cards/my-card` - Get current user's virtual card (balances, meal plan, transit, permissions, frozen state)
- `POST /api/cards/generate-qr` - Generate temporary QR code
- `GET /api/cards/balances` - Get all service balances
- `POST /api/cards/freeze` / `POST /api/cards/unfreeze` - Lost-card freeze toggle
- `GET /api/cards/transaction-history` - Activity log

### Services
- `POST /api/services/access` - Validate access token (for scanning)
- `POST /api/services/dining/check-balance` - Check dining balance
- `POST /api/services/dining/use` - Pay with dining balance
- `POST /api/services/print/check-balance` - Check Wisc Print balance
- `POST /api/services/print/use` - Pay for a print job
- `POST /api/services/wiscard-cash/check-balance` - Check Wiscard Cash balance
- `POST /api/services/wiscard-cash/use` - Spend Wiscard Cash at a vendor
- `GET /api/services/dining/swipes` / `POST /api/services/dining/swipe` - Meal-plan swipes
- `GET /api/services/transit/pass` - Transit bus-pass status
- `GET /api/services/access-permissions` - My door/building access
- `POST /api/services/library/checkout` - Library checkout validation
- `POST /api/services/residence/access` - Residence hall access

### Tickets
- `GET /api/tickets` - My event tickets
- `POST /api/tickets/validate` - Validate a ticket at the gate (single-use)

### Admin (Admin only)
- `GET /api/admin/users` - Get all users
- `POST /api/admin/users` - Create new user
- `PATCH /api/admin/users/{id}/toggle-active` - Toggle user active status
- `POST /api/admin/balances` - Update user balance
- `GET /api/admin/stats` - Get system statistics
- `POST /api/admin/revoke-token` - Revoke access token
- `POST /api/admin/permissions` / `POST /api/admin/permissions/revoke` - Grant/revoke door access
- `POST /api/admin/meal-swipes` - Set a meal plan
- `POST /api/admin/transit` - Set transit eligibility
- `POST /api/admin/tickets` - Issue an event ticket

## Usage

1. **Login**: Use one of the test accounts to log in
2. **View Card**: See your virtual Wiscard with all student information and barcode
3. **Generate QR**: Create a temporary 5-minute access code
4. **Verify (the core loop)**: On a second device/tab open **`/verify`** (the "Verifier" button in the header), pick a service, then scan the QR with the camera or paste the token. The server validates it and shows the student's verified identity — and the event appears in the student's Activity History.
5. **Access Services**: Use the service cards to check balances, pay for dining/printing, or access facilities
6. **Admin Panel**: Admin users can manage users and balances from the admin dashboard

## Testing

Backend API tests (pytest):

```bash
cd backend
pip install -r requirements-dev.txt
pytest
```

These cover the full loop: login → generate code → verify, balance spend (incl.
insufficient/negative guards), transaction history, and admin authorization.
CI runs them automatically on every push/PR (see `.github/workflows/ci.yml`).

## Security

Highlights (full details in **[SECURITY.md](./SECURITY.md)**):

- JWT auth, bcrypt password hashing, admin-gated routes.
- Short-lived (5-min), high-entropy, revocable QR access tokens; single-use tickets.
- `SECRET_KEY` is required in production — the app refuses to start with the default.
- `.env` is git-ignored and excluded from Docker images.
- Pydantic validation everywhere; balances can't go negative; transactional spends.

> ⚠️ This is a prototype. Before any real deployment, complete the production
> hardening checklist in [SECURITY.md](./SECURITY.md) (real SSO, HTTPS, rate
> limiting, PostgreSQL + migrations, removing demo accounts, security review).

## Design

The application features:
- UW-Madison branding with red (#C5050C) and white color scheme
- Mobile-first responsive design
- Clean, modern interface
- Intuitive navigation

## Development

### Backend Development

The backend uses FastAPI with automatic API documentation available at `/docs`. The database is SQLite for simplicity, but can be easily switched to PostgreSQL.

### Frontend Development

The frontend uses Next.js 14 with the App Router. Components are modular and reusable. The API client in `lib/api.ts` handles all backend communication.

## Future Enhancements

See **[PROJECT_PLAN.md](./PROJECT_PLAN.md)** for the full phased roadmap. Highlights still ahead:

- Real UW-Madison SSO/Shibboleth integration
- Production-signed `.pkpass` + Google Wallet JWT
- On-chain mint/verify against a deployed testnet contract
- PostgreSQL + Alembic migrations for production
- NFC simulation with Web NFC API
- Photo upload (currently uses generated avatar placeholders)
- Multi-factor authentication

## License

This is a prototype project for educational purposes.

## Notes

- The authentication system simulates UW NetID login. In production, this would integrate with UW-Madison's actual authentication system.
- QR codes expire after 5 minutes for security.
- All service integrations are currently simulated/mocked.
- The database is initialized with dummy data on first run.

