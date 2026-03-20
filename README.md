#                                                MediTrack

Track health vitals and medication reminders with a FastAPI + React + Supabase stack.

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-38BDF8?style=for-the-badge&logo=tailwindcss&logoColor=white)

* [Features](#features)
* [Architecture](#architecture)
* [Data Model](#data-model)
* [API Reference](#api-reference)
* [Quick Start](#quick-start)
* [Roadmap](#roadmap)
* [Project Structure](#project-structure)

---

## The Challenge

Healthcare tracking often suffers from:

* Manual entry and inconsistent logs
* Missing medication schedules
* No single view of "today's health" vs "historical trends"
* Hard-to-maintain integrations between UI and backend services

---

## Our Solution

MediTrack gives you a clean workflow:

* Capture vitals (heart rate, blood pressure, blood sugar, mood) and store them in Supabase
* Maintain medication reminders per user in Supabase
* Show a simple health dashboard plus analytics/history charts
* Provide lightweight health tips with a dedicated `/tips` endpoint

---

## Features

### Core Features

* Vitals logging
  * POST `/vitals/` to save a new entry
  * GET `GET /vitals/{user_id}/latest` to load the most recent vitals
  * GET `GET /vitals/{user_id}` to fetch full history
* Medication reminders
  * POST `/reminders/` to create reminders
  * GET `GET /reminders/{user_id}` to list reminders
  * DELETE `DELETE /reminders/{reminder_id}` to remove reminders
* Health tips
  * GET `GET /tips` for all tips
  * GET `GET /tips/{category}` for category-specific tips

### Frontend Experience

* React SPA (React Router) with a dedicated `/login` flow
* Dashboard + charts (Recharts) for vitals history
* Token + identity bootstrap:
  * Frontend uses Supabase Auth to sign up / log in
  * Stores `token` and `user_id` in `localStorage` for subsequent usage

---

## Innovation Highlights

* Supabase Auth integration for signup/login
  * `/auth/signup` and `/auth/login` delegate user management to Supabase
* Supabase-py direct persistence (no ORM layer)
  * Vitals and reminders are stored via `supabase.table(...).insert(...).execute()`
* REST-first, JSON-first backend
  * Every endpoint returns plain JSON that the React UI can render immediately
* Separation of concerns in the backend
  * `routes/auth.py`, `routes/vitals.py`, `routes/reminders.py`, `routes/tips.py` keep each feature focused
* Lightweight wellness content
  * `/tips` is static data to avoid unnecessary database complexity

---

## Architecture

```mermaid
flowchart LR
  U[User] --> FE[React UI]
  FE -->|REST (signup/login, vitals, reminders, tips)| API[FastAPI REST API]
  API -->|Auth + Postgres CRUD| SB[Supabase]
  SB -->|Data (vitals/reminders)| API
  API --> FE
```

Key points:

* FastAPI exposes a small, REST-first API surface
* Supabase handles data persistence (and Supabase Auth for login/sign up)
* The frontend calls the API using `VITE_API_URL` (defaults to `http://localhost:8000`)

---

## Data Model

MediTrack expects these Supabase tables:

### `vitals`

| Column | Type | Notes |
|---|---|---|
| id | uuid | Primary key |
| user_id | uuid | References `auth.users` |
| heart_rate | int4 | Nullable |
| systolic | int4 | Nullable |
| diastolic | int4 | Nullable |
| blood_sugar | float4 | Nullable |
| mood | text | Expected: `great`, `good`, `okay`, `bad` |
| notes | text | Nullable |
| created_at | timestamptz | Defaults to `now()` |

### `reminders`

| Column | Type | Notes |
|---|---|---|
| id | uuid | Primary key |
| user_id | uuid | References `auth.users` |
| medicine_name | text | Required |
| dosage | text | Nullable |
| time | text | Nullable |
| frequency | text | Expected values like `daily`, `twice daily` |
| created_at | timestamptz | Defaults to `now()` |

### `tips`

* Not stored in a database
* Implemented as static data returned from the backend `/tips` routes

---

## API Reference

Base URL: `http://localhost:8000`

API docs (Swagger UI): `http://localhost:8000/docs`

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/signup` | Register a new user |
| POST | `/auth/login` | Login and receive a Supabase-issued JWT `access_token` |

### Vitals

| Method | Endpoint | Description |
|---|---|---|
| POST | `/vitals/` | Log a new vitals entry |
| GET | `/vitals/{user_id}` | Get all vitals for a user |
| GET | `/vitals/{user_id}/latest` | Get the most recent vitals entry |

### Reminders

| Method | Endpoint | Description |
|---|---|---|
| POST | `/reminders/` | Add a new reminder |
| GET | `/reminders/{user_id}` | Get reminders for a user |
| DELETE | `/reminders/{reminder_id}` | Delete a reminder by its id |

### Tips

| Method | Endpoint | Description |
|---|---|---|
| GET | `/tips` | Get all health tips |
| GET | `/tips/{category}` | Get tips filtered by category |

---

## Auth & Security Notes

* The backend returns a JWT on `/auth/login`.
* Current route handlers operate on `user_id` passed in requests (the API surface is not wired to enforce JWT validation in the route code).
* If you plan to deploy, consider adding token verification + RBAC so users can only read/write their own records.

---

## Quick Start

## Prerequisites

* Python 3.11+
* Node.js (for the React frontend)
* A Supabase project
* Supabase tables: `vitals` and `reminders`

---

## Step 1: Configure Supabase

1. Create the Supabase tables:
   * `vitals` with the columns listed in [Data Model](#data-model)
   * `reminders` with the columns listed in [Data Model](#data-model)
2. From Supabase Dashboard:
   * `Project Settings` -> `API`
   * Copy `Project URL` and `anon public key`

---

## Step 2: Backend (FastAPI)

```powershell
cd backend
pip install -r requirements.txt
```

Create `backend/.env`:

```bash
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
```

Run the server:

```powershell
uvicorn main:app --reload
```

Health check:

* `GET /` -> `{"message":"MediTrack API is running"}`

Docs:

* `http://localhost:8000/docs`

---

## Step 3: Frontend (React + Vite)

```powershell
cd frontend
npm install
npm run dev
```

Create `frontend/.env`:

```bash
VITE_API_URL=http://localhost:8000
```

Open the UI:

* Vite default: `http://localhost:5173`

---

## Quick Test (cURL)

```powershell
# Note (PowerShell): use curl.exe (real curl), not the curl alias.

# Root
curl.exe http://localhost:8000/

# Sign up
curl.exe -X POST "http://localhost:8000/auth/signup" -H "Content-Type: application/json" -d '{"email":"you@example.com","password":"your_password"}'

# Login
curl.exe -X POST "http://localhost:8000/auth/login" -H "Content-Type: application/json" -d '{"email":"you@example.com","password":"your_password"}'

# Log vitals (user_id should be your Supabase auth user id)
curl.exe -X POST "http://localhost:8000/vitals/" -H "Content-Type: application/json" -d '{"user_id":"USER_UUID","heart_rate":72,"systolic":120,"diastolic":80,"blood_sugar":95,"mood":"good","notes":"Felt good"}'

# Latest vitals
curl.exe "http://localhost:8000/vitals/USER_UUID/latest"
```

---

## Testing & Validation

### Manual Test Flow (Realistic)

1. Sign up and log in
   * Call `POST /auth/signup`, then `POST /auth/login`
2. Log daily vitals
   * Open the frontend `Log Vitals` page
   * This calls `POST /vitals/` with `user_id` and vitals fields
3. View today's overview + latest entry
   * Dashboard calls:
     * `GET /vitals/{user_id}/latest`
     * `GET /reminders/{user_id}`
4. Review vitals history
   * History page calls `GET /vitals/{user_id}`
5. Manage medication reminders
   * Reminders page calls:
     * `POST /reminders/` to add
     * `DELETE /reminders/{reminder_id}` to remove
6. Read health tips
   * Tips page calls:
     * `GET /tips` (all) and filters by category in the UI

### Troubleshooting

* CORS errors
  * Backend currently allows `http://localhost:5173` in `backend/main.py`
  * If you change frontend port, update the allowed origin

---

## Roadmap

### Phase 1 (Current)

* Supabase-backed vitals logging
* Medication reminders CRUD
* Health tips API
* History visualization on the frontend

### Phase 2 (Next)

* JWT-protected API routes (enforce access per user)
* More vitals types + flexible charting
* Reminder scheduling improvements (e.g., next due time)

### Phase 3 (Future Vision)

* Predictive insights from vitals trends
* Notifications / email reminders
* Export to CSV/PDF for doctor-friendly reports

---

## Project Structure

```text
MediTrack/
  README.md
  backend/
    main.py
    supabase_client.py
    requirements.txt
    routes/
      auth.py
      vitals.py
      reminders.py
      tips.py
  frontend/
    src/
      pages/
        Login.jsx
        Dashboard.jsx
        LogVitals.jsx
        History.jsx
        Reminders.jsx
        Tips.jsx
  assets/
```

---

## Made for Hackathons. Ready for Iteration.

MediTrack - a focused health tracking dashboard that keeps your day organized, your history visible, and your reminders actionable.

