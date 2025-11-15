# Virtual Wiscard

A full-stack digital student ID system for UW-Madison students that replaces the physical Wiscard with a virtual card accessible through a web application.

## Features

- 🪪 **Student Authentication**: Login using UW NetID (simulated with dummy accounts)
- 💳 **Virtual ID Display**: Shows name, photo, student ID, expiration, and active status
- 🔐 **Secure QR Code**: Generate temporary QR codes for identity verification and access
- 🏫 **Service Integration**: 
  - Dining balance check and management
  - Residence hall door access (simulated)
  - Library entry and checkout validation
- ⚙️ **Admin Dashboard**: View active users, manage balances, and revoke cards

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
- `GET /api/cards/my-card` - Get current user's virtual card
- `POST /api/cards/generate-qr` - Generate temporary QR code
- `GET /api/cards/balances` - Get all service balances

### Services
- `POST /api/services/access` - Validate access token (for scanning)
- `POST /api/services/dining/check-balance` - Check dining balance
- `POST /api/services/dining/use` - Use dining balance
- `POST /api/services/library/checkout` - Library checkout validation
- `POST /api/services/residence/access` - Residence hall access

### Admin (Admin only)
- `GET /api/admin/users` - Get all users
- `POST /api/admin/users` - Create new user
- `PATCH /api/admin/users/{id}/toggle-active` - Toggle user active status
- `POST /api/admin/balances` - Update user balance
- `GET /api/admin/stats` - Get system statistics
- `POST /api/admin/revoke-token` - Revoke access token

## Usage

1. **Login**: Use one of the test accounts to log in
2. **View Card**: See your virtual Wiscard with all student information
3. **Generate QR**: Create a temporary QR code for scanning at campus services
4. **Access Services**: Use the service cards to check balances or access facilities
5. **Admin Panel**: Admin users can manage users and balances from the admin dashboard

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

- Apple Wallet / Google Wallet integration
- NFC simulation with Web NFC API
- Analytics dashboard for card usage
- Real-time notifications
- Multi-factor authentication
- Photo upload functionality

## License

This is a prototype project for educational purposes.

## Notes

- The authentication system simulates UW NetID login. In production, this would integrate with UW-Madison's actual authentication system.
- QR codes expire after 5 minutes for security.
- All service integrations are currently simulated/mocked.
- The database is initialized with dummy data on first run.

