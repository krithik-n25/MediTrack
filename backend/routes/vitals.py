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
