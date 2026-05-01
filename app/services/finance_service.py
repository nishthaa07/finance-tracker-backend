from collections import defaultdict
from app.models import models
from fastapi import HTTPException


def calculate_summary(transactions, month=None):
    income = 0
    expense = 0
    for t in transactions:
        if month and t.date.month != month:
            continue
        if t.type.lower() == "income":
            income += t.amount
        elif t.type.lower() == "expense":
            expense += t.amount

    if income > 0:
        savings_rate = (
        (income-expense)/income
        ) * 100
    else:
        savings_rate = 0

    return {
      "income": income,
      "expense": expense,
      "balance": income-expense,
      "savings_rate": round(
            savings_rate,2
        )
    }



def category_breakdown(transactions):
    summary = {}
    for t in transactions:
        if t.type.lower() != "expense":
            continue
        if t.category not in summary:
            summary[t.category]=0
        summary[t.category]+=t.amount

    return summary


def get_budget_alerts(
    transactions,
    budgets
):
    spent = {}
    for t in transactions:
        if t.type.lower() != "expense":
            continue
        if t.category not in spent:
            spent[t.category] = 0
        spent[t.category] += t.amount
    alerts = {}
    for b in budgets:
        used = spent.get(b.category, 0)
        limit = b.limit_amount
        if used > limit:
            alerts[b.category] = {
                "status":"Exceeded",
                "spent":used,
                "budget":limit,
                "over_by":used-limit
            }
        elif used >= limit*0.8:
            alerts[b.category] = {
                "status":"Near Limit",
                "spent":used,
                "budget":limit,
                "remaining":limit-used
            }
        else:
            alerts[b.category] = {
                "status":"Within Budget",
                "spent":used,
                "budget":limit,
                "remaining":limit-used
            }
    return alerts


def get_spending_insights(transactions
    ):
    category_totals = {}
    monthly_expenses = defaultdict(float)
    largest_expense = 0
    for t in transactions:
        if t.type.lower() != "expense":
            continue
        # category totals
        if t.category not in category_totals:
            category_totals[t.category] = 0
        category_totals[t.category] += t.amount
        # largest expense
        if t.amount > largest_expense:
            largest_expense = t.amount
        # month totals
        month_key = (
           f"{t.date.year}-"
           f"{t.date.month}"
        )
        monthly_expenses[
           month_key
        ] += t.amount
    if category_totals:
        highest_spend_category = max(
            category_totals,
            key=category_totals.get
        )
    else:
        highest_spend_category = None
    if monthly_expenses:
        avg_monthly_expense = (
            sum(monthly_expenses.values())/
            len(monthly_expenses)
        )
    else:
        avg_monthly_expense = 0
    return {
        "highest_spend_category":
           highest_spend_category,

        "largest_expense":
           largest_expense,

        "avg_monthly_expense":
           round(avg_monthly_expense, 2)
    }


from collections import defaultdict


def category_trends(
    transactions,
    category
):
    trend = defaultdict(float)
    for t in transactions:
        if t.type.lower() != "expense":
            continue
        if (
          t.category.lower()
          != category.lower()
        ):
            continue
        month_name = t.date.strftime(
            "%b"
        )
        trend[month_name] += t.amount
    
    month_order = [
      "Jan","Feb","Mar",
      "Apr","May","Jun",
      "Jul","Aug","Sep",
      "Oct","Nov","Dec"
    ]
    ordered_trend = {}
    for m in month_order:
        if m in trend:
            ordered_trend[m]=trend[m]
    return ordered_trend


DEFAULT_CATEGORIES = {
 "food",
 "salary",
 "pocket money",
 "travel",
 "accommodation",
 "subscription",
 "shopping",
 "health",
 "gifts",
 "refunds",
 "other"
}


def category_exists(
    db,
    category
):
    if category in DEFAULT_CATEGORIES:
        return True
    custom = db.query(
       models.Budget
    ).filter(
       models.Budget.category
       == category
    ).first()
    return custom is not None


def validate_and_normalize_transaction(db, transaction, *, force: bool=False, ignore_id: int | None = None):
    category = transaction.category.strip().lower()
    txn_type = transaction.type.strip().lower()
    if not category_exists(db, category):
        raise HTTPException(
            status_code=400,
            detail="Invalid category. Use default category or add budget first."
        )
    q = db.query(models.Transaction).filter(
        models.Transaction.amount == transaction.amount,
        models.Transaction.category == category,
        models.Transaction.type == txn_type,
        models.Transaction.date == transaction.date
    )
    if ignore_id is not None:
        q = q.filter(models.Transaction.id != ignore_id)
    existing = q.first()
    if existing and not force:
        raise HTTPException(
            status_code=409,
            detail=f"Duplicate transaction detected (id={existing.id})"
        )
    return category, txn_type