from sqlalchemy.orm import Session
from datetime import date
import random

from app.db.database import SessionLocal
from app.models import models

db: Session = SessionLocal()

categories = [
    "food", "travel", "shopping", "subscription",
    "health", "gifts", "accommodation"
]

income_categories = [
    "salary", "pocket money", "refunds"
]

def random_date():
    year = random.choice([2025, 2026])
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return date(year, month, day)

# clear old data (optional)
db.query(models.Transaction).delete()
db.commit()

transactions = []

for i in range(120):

    if random.random() < 0.3:
        # income
        tx = models.Transaction(
            amount=random.randint(5000, 60000),
            category=random.choice(income_categories),
            type="income",
            date=random_date()
        )
    else:
        # expense
        tx = models.Transaction(
            amount=random.randint(100, 15000),
            category=random.choice(categories),
            type="expense",
            date=random_date()
        )

    transactions.append(tx)

db.add_all(transactions)
db.commit()

db.close()

print("✅ 120 transactions inserted successfully")