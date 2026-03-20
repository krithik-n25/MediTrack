# MediTrack — Backend PRD
## For AI IDE (Cursor / Windsurf / Copilot)
> Copy and paste this entire file into your AI IDE and say: "Build this backend exactly as described."

---

## Project Overview

Build a **FastAPI** backend for a healthcare dashboard app called **MediTrack**.
The frontend is React. The database is **Supabase** (PostgreSQL).
This backend only needs to serve a REST API — no frontend rendering.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Framework | FastAPI |
| Database | Supabase (via `supabase-py`) |
| Auth | Supabase built-in Auth (JWT tokens) |
| Server | Uvicorn |
| Env config | python-dotenv |

---

## Folder Structure to Create

```
backend/
├── main.py
├── .env
├── requirements.txt
├── supabase_client.py
└── routes/
    ├── auth.py
    ├── vitals.py
    ├── reminders.py
    └── tips.py
```

---

## Step 1 — requirements.txt

Create this file exactly:

```
fastapi
uvicorn
supabase
python-dotenv
pydantic
```

---

## Step 2 — .env file

Create this file. The AI IDE should leave the values blank for the user to fill in:

```
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
```

> User will get these values from: Supabase Dashboard → Project Settings → API

---

## Step 3 — supabase_client.py

Create a single shared Supabase client used across all routes:

```python
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
```

---

## Step 4 — main.py

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, vitals, reminders, tips

app = FastAPI(title="MediTrack API")

# Allow React frontend (localhost:5173) to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all route files
app.include_router(auth.router,      prefix="/auth",      tags=["Auth"])
app.include_router(vitals.router,    prefix="/vitals",    tags=["Vitals"])
app.include_router(reminders.router, prefix="/reminders", tags=["Reminders"])
app.include_router(tips.router,      prefix="/tips",      tags=["Tips"])

@app.get("/")
def root():
    return {"message": "MediTrack API is running"}
```

---

## Step 5 — routes/auth.py

Handles user signup and login using Supabase Auth.

### Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/auth/signup` | Register a new user |
| POST | `/auth/login` | Login and get JWT token |

### Code

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from supabase_client import supabase

router = APIRouter()

class AuthRequest(BaseModel):
    email: str
    password: str

@router.post("/signup")
def signup(data: AuthRequest):
    try:
        response = supabase.auth.sign_up({
            "email": data.email,
            "password": data.password
        })
        return {"message": "Signup successful", "user": response.user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
def login(data: AuthRequest):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })
        return {
            "access_token": response.session.access_token,
            "user": response.user
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid email or password")
```

---

## Step 6 — routes/vitals.py

Handles logging and fetching health vitals (heart rate, blood pressure, sugar, mood).

### Supabase Table Required

Create this table in Supabase Dashboard → Table Editor:

**Table name:** `vitals`

| Column | Type | Notes |
|---|---|---|
| id | uuid | Primary key, default: gen_random_uuid() |
| user_id | uuid | Foreign key to auth.users |
| heart_rate | int4 | nullable |
| systolic | int4 | nullable (BP top number) |
| diastolic | int4 | nullable (BP bottom number) |
| blood_sugar | float4 | nullable |
| mood | text | nullable — values: great / good / okay / bad |
| notes | text | nullable |
| created_at | timestamptz | default: now() |

### Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/vitals` | Log new vitals entry |
| GET | `/vitals/{user_id}` | Get all vitals for a user |
| GET | `/vitals/{user_id}/latest` | Get only the most recent entry |

### Code

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from supabase_client import supabase

router = APIRouter()

class VitalsEntry(BaseModel):
    user_id: str
    heart_rate: Optional[int] = None
    systolic: Optional[int] = None
    diastolic: Optional[int] = None
    blood_sugar: Optional[float] = None
    mood: Optional[str] = None
    notes: Optional[str] = None

@router.post("/")
def log_vitals(data: VitalsEntry):
    try:
        response = supabase.table("vitals").insert(data.dict()).execute()
        return {"message": "Vitals logged", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}")
def get_vitals(user_id: str):
    try:
        response = (
            supabase.table("vitals")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}/latest")
def get_latest_vitals(user_id: str):
    try:
        response = (
            supabase.table("vitals")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        if response.data:
            return response.data[0]
        return {}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

---

## Step 7 — routes/reminders.py

Handles medication reminders.

### Supabase Table Required

**Table name:** `reminders`

| Column | Type | Notes |
|---|---|---|
| id | uuid | Primary key, default: gen_random_uuid() |
| user_id | uuid | Foreign key to auth.users |
| medicine_name | text | required |
| dosage | text | e.g. "500mg" |
| time | text | e.g. "08:00 AM" |
| frequency | text | e.g. "daily" / "twice daily" |
| created_at | timestamptz | default: now() |

### Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/reminders` | Add a new reminder |
| GET | `/reminders/{user_id}` | Get all reminders for a user |
| DELETE | `/reminders/{reminder_id}` | Delete a reminder |

### Code

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from supabase_client import supabase

router = APIRouter()

class Reminder(BaseModel):
    user_id: str
    medicine_name: str
    dosage: Optional[str] = None
    time: Optional[str] = None
    frequency: Optional[str] = "daily"

@router.post("/")
def add_reminder(data: Reminder):
    try:
        response = supabase.table("reminders").insert(data.dict()).execute()
        return {"message": "Reminder added", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}")
def get_reminders(user_id: str):
    try:
        response = (
            supabase.table("reminders")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{reminder_id}")
def delete_reminder(reminder_id: str):
    try:
        supabase.table("reminders").delete().eq("id", reminder_id).execute()
        return {"message": "Reminder deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

---

## Step 8 — routes/tips.py

Returns static health tips. No database needed — just a hardcoded list.
This is intentionally simple so the frontend can display tips without complex logic.

### Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/tips` | Get all health tips |
| GET | `/tips/{category}` | Get tips by category |

### Code

```python
from fastapi import APIRouter, HTTPException

router = APIRouter()

TIPS = [
    {"id": 1, "category": "heart", "title": "Stay Active", "body": "Aim for 30 minutes of moderate exercise daily to keep your heart healthy."},
    {"id": 2, "category": "heart", "title": "Monitor Your BP", "body": "Check your blood pressure regularly. Normal is below 120/80 mmHg."},
    {"id": 3, "category": "sugar", "title": "Limit Sugar Intake", "body": "Avoid sugary drinks and processed foods to keep blood sugar stable."},
    {"id": 4, "category": "sugar", "title": "Eat Fiber Rich Foods", "body": "Whole grains, vegetables, and legumes help regulate blood sugar levels."},
    {"id": 5, "category": "mood", "title": "Sleep Well", "body": "7-9 hours of quality sleep significantly improves mood and mental health."},
    {"id": 6, "category": "mood", "title": "Stay Hydrated", "body": "Dehydration can cause fatigue and worsen mood. Drink 8 glasses of water daily."},
    {"id": 7, "category": "general", "title": "Regular Checkups", "body": "Visit your doctor at least once a year for preventive health screenings."},
    {"id": 8, "category": "general", "title": "Reduce Stress", "body": "Practice deep breathing or meditation for 10 minutes a day to reduce stress hormones."},
]

@router.get("/")
def get_all_tips():
    return TIPS

@router.get("/{category}")
def get_tips_by_category(category: str):
    filtered = [t for t in TIPS if t["category"] == category]
    if not filtered:
        raise HTTPException(status_code=404, detail=f"No tips found for category: {category}")
    return filtered
```

---

## Step 9 — Supabase Setup Instructions

Tell the user to do these steps manually in their Supabase dashboard:

1. Go to https://supabase.com and open your project
2. Go to **Table Editor** → create the `vitals` table (columns listed in Step 6)
3. Go to **Table Editor** → create the `reminders` table (columns listed in Step 7)
4. Go to **Project Settings → API** → copy `Project URL` and `anon public key`
5. Paste those into the `.env` file

---

## Step 10 — How to Run the Backend

After all files are created, run these commands in the `backend/` folder:

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

The API will be available at: `http://localhost:8000`

Auto-generated API docs at: `http://localhost:8000/docs`

---

## API Summary

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/signup` | Register user |
| POST | `/auth/login` | Login, returns JWT |
| POST | `/vitals` | Log vitals |
| GET | `/vitals/{user_id}` | Get all vitals |
| GET | `/vitals/{user_id}/latest` | Get latest vitals |
| POST | `/reminders` | Add reminder |
| GET | `/reminders/{user_id}` | Get all reminders |
| DELETE | `/reminders/{reminder_id}` | Delete reminder |
| GET | `/tips` | Get all tips |
| GET | `/tips/{category}` | Get tips by category |

---

## Notes for AI IDE

- Do NOT add authentication middleware/guards on routes for now — keep it simple
- Do NOT use SQLAlchemy or any ORM — use supabase-py directly
- Do NOT create Docker files
- All responses should be plain JSON
- Use Pydantic models for all request bodies
- Keep each route file focused — no mixing of concerns