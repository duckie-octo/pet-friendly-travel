# Pet-Friendly Travel API

FastAPI backend for the CMPE 131 travel planner (flights, hotels, bookings, JWT auth).

## Setup

```bash
cd server
cp .env.example .env
uv sync
```

Initialize the sample database (only needed on first run or to reset demo data):

```bash
sqlite3 travel_booking.db < app/schemas/init_db.sql
```

The API also auto-loads `app/schemas/init_db.sql` on startup if `Flight_Reservations` is missing.

## Run

```bash
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000/docs for interactive API docs.

## Demo user

```bash
curl http://127.0.0.1:8000/api/v1/setup-seed-data/
```

Then sign in with `test@example.com` / `testpass123`.

## Sample search

- Flights: **JFK → LAX** on **2024-08-15** (pet weight ≤ 8 kg)
- Hotels: city **Los Angeles**
