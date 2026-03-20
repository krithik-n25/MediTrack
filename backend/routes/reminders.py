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
