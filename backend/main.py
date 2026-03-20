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
