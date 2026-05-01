from fastapi import APIRouter, HTTPException
from app.db.database import SessionLocal
from app.models import models
from app.services.finance_service import (
   calculate_summary,
   category_breakdown
)

router = APIRouter()


@router.get("/summary")
def get_summary(
    month:int=None,
    breakdown:bool=False
):
    if month is not None:
        if month < 1 or month > 12:
            raise HTTPException(
                status_code=400,
                detail="Month must be between 1 and 12"
            )
    db = SessionLocal()
    transactions = db.query(
        models.Transaction
    ).all()
    if month is not None:
        transactions = [
            t for t in transactions
            if t.date.month == month
        ]
    if breakdown:
        result = category_breakdown(
            transactions
        )
    else:
        result = calculate_summary(
            transactions
        )
    db.close()
    return result