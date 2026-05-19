# Travel Agency Frontend

React + Vite app for the CMPE 131 pet-friendly travel planner API (`../server`).

## Setup

```bash
cd client
npm install
cp .env.example .env
```

Start the API from `../server` (port 8000), then:

```bash
npm run dev
```

Open http://localhost:5173

## Demo login

1. Seed a test user: `GET http://localhost:8000/api/v1/setup-seed-data/`
2. Sign in with `test@example.com` / `testpass123`

## Search tip

Sample flights use **JFK → LAX** on **2024-08-15**. Pet-friendly hotels in Los Angeles are in the seeded database.

## Features

- Register / login (JWT)
- Search pet-friendly flights and hotels
- Create and view bookings
- Cancel bookings
