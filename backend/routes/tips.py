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
