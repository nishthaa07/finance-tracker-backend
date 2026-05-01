from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, field_validator
from sqlalchemy import func
from datetime import date
from enum import Enum

from app.db.database import SessionLocal
from app.models import models
from app.services import finance_service as service 


router = APIRouter()

class TransactionRequest(BaseModel):
    amount: float
    category: str
    type: str
    date: date

    @field_validator("amount")
    @classmethod
    def validate_amount(cls,v):
        if v <=0:
            raise ValueError(
            "Amount must be positive"
            )
        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls,v):
        if not v.strip():
            raise ValueError(
            "Category required"
            )

        return v.strip().lower()

    @field_validator("type")
    @classmethod
    def validate_type(cls,v):
        v = v.lower().strip()
        if v not in ["income","expense"]:
            raise ValueError(
            "Type must be income or expense"
            )
        return v

    @field_validator("date")
    @classmethod
    def validate_date(cls,v):
        if v > date.today():
            raise ValueError(
            "Future date not allowed"
            )
        return v


class TransactionUpdateRequest(BaseModel):
    amount: float
    category: str
    type: str
    date: date


class BudgetRequest(BaseModel):
    category:str
    limit_amount:float
    
    @field_validator("limit_amount")
    @classmethod
    def validate_limit(cls,v):

        if v<=0:
            raise ValueError(
                "Budget must be positive"
            )
        return v

class BudgetUpdateRequest(BaseModel):
    limit_amount: float
    @field_validator("limit_amount")
    @classmethod
    def validate_limit(cls,v):
        if v <=0:
            raise ValueError(
              "Budget must be positive"
            )
        return v


@router.post("/transactions")
def create_transaction(
    transaction: TransactionRequest,
    force: bool = Query(False)
):
    db = SessionLocal()
    category, txn_type = service.validate_and_normalize_transaction(
        db, transaction, force=force
    )
    new_tx = models.Transaction(
        amount=transaction.amount,
        date=transaction.date,
        category=category,
        type=txn_type
    )
    db.add(new_tx)
    db.commit()
    db.refresh(new_tx)
    db.close()
    return {"message": "saved", "id": new_tx.id}


@router.get("/transactions")
def get_transactions():
    db = SessionLocal()
    transactions = db.query(
       models.Transaction
    ).all()
    db.close()
    return transactions


@router.put("/transactions/{transaction_id}")
def update_transaction(
    transaction_id: int,
    transaction: TransactionRequest,
    force: bool = Query(False)
):
    db = SessionLocal()
    tx = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id
    ).first()
    if not tx:
        db.close()
        raise HTTPException(404, "Transaction not found")
    category, txn_type = service.validate_and_normalize_transaction(
        db,
        transaction,
        force=force,
        ignore_id=transaction_id   
    )
    tx.amount = transaction.amount
    tx.category = category
    tx.type = txn_type
    tx.date = transaction.date
    db.commit()
    db.close()
    return {"message": "updated"}


@router.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id:int):
    db = SessionLocal()
    tx = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id
    ).first()
    if not tx:
        db.close()
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )
    db.delete(tx)
    db.commit()
    db.close()
    return {"message":"Deleted"}


@router.get("/transactions/filter")
def filter_transactions(
    category: str = None,
    type: str = None,
    month: int = None
):
    db = SessionLocal()
    query = db.query(models.Transaction)
    if category:
        category = category.strip().lower()
        query = query.filter(
            func.lower(models.Transaction.category) == category
        )
    if type:
        type = type.strip().lower()
        query = query.filter(
            func.lower(models.Transaction.type) == type
        )
    if month:
        if month < 1 or month > 12:
            db.close()
            raise HTTPException(
                status_code=400,
                detail="Month must be between 1 and 12"
            )
        query = query.filter(
            func.strftime("%m", models.Transaction.date) == f"{month:02d}"
        )
    results = query.all()
    db.close()
    return results


@router.post("/budgets")
def create_budget(
    budget: BudgetRequest
):
    db=SessionLocal()
    category = (
       budget.category
       .strip()
       .lower()
    )
    existing=db.query(
       models.Budget
    ).filter(
       models.Budget.category==category
    ).first()
    if existing:
        db.close()

        raise HTTPException(
           status_code=409,
           detail="Budget already exists. Please Update"
        )
    new_budget=models.Budget(
       category=category,
       limit_amount=budget.limit_amount
    )
    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)
    db.close()
    return {
      "message":"Budget saved"
    }


@router.get("/budgets")
def get_budgets():
    db=SessionLocal()
    budgets=db.query(
      models.Budget
    ).all()
    db.close()
    return budgets


@router.put("/budgets/{category}")
def update_budget(
   category:str,
   budget:BudgetUpdateRequest
):
    db=SessionLocal()
    existing=db.query(
      models.Budget
    ).filter(
      models.Budget.category==
      category.strip().lower()
    ).first()
    if not existing:
       db.close()
       raise HTTPException(
         status_code=404,
         detail="Budget not found"
       )
    existing.limit_amount=(
       budget.limit_amount
    )
    db.commit()
    db.close()
    return {
      "message":"Budget updated"
    }


@router.delete("/budgets/{category}")
def delete_budget(category:str):
    db = SessionLocal()
    category = (
       category.strip().lower()
    )
    budget = db.query(
       models.Budget
    ).filter(
       models.Budget.category
       == category
    ).first()
    if not budget:
        db.close()
        raise HTTPException(
           status_code=404,
           detail="Budget not found"
        )
    db.delete(budget)
    db.commit()
    db.close()
    return {
      "message":"Budget deleted"
    }


@router.get("/budget/alerts")
def budget_alerts(
    month:int=None
):
    if (
      month is not None
      and (month<1 or month>12)
    ):
       raise HTTPException(
          status_code=400,
          detail="Invalid month"
       )
    db=SessionLocal()
    transactions=db.query(
       models.Transaction
    ).all()
    budgets=db.query(
       models.Budget
    ).all()
    if month is not None:
        transactions = [
          t for t in transactions
          if t.date.month==month
        ]
    result = service.get_budget_alerts(
       transactions,
       budgets
    )
    db.close()
    return result


@router.get("/insights")
def spending_insights(
    month:int=None
):
    if (
       month is not None
       and (month <1 or month >12)
    ):
        raise HTTPException(
           status_code=400,
           detail="Month must be 1-12"
        )
    db=SessionLocal()
    transactions=db.query(
       models.Transaction
    ).all()
    if month is not None:
        transactions = [
            t for t in transactions
            if t.date.month == month
        ]
    result=service.get_spending_insights(
       transactions
    )
    db.close()
    return result


@router.get("/trends")
def get_trends(
   category:str
):
    category = (
      category.strip().lower()
    )
    db = SessionLocal()
    if not service.category_exists(
        db,
        category
    ):
        db.close()
        raise HTTPException(
           status_code=400,
           detail="Invalid category"
        )
    transactions=db.query(
      models.Transaction
    ).all()
    result = service.category_trends(
       transactions,
       category
    )
    db.close()
    return result