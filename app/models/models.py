from sqlalchemy import Column,Integer,String,Float,Date
from app.db.database import Base


class Transaction(Base):

    __tablename__="transactions"

    id=Column(
       Integer,
       primary_key=True,
       index=True
    )

    amount=Column(Float)
    date=Column(Date)
    category=Column(String)
    type=Column(String)


class Budget(Base):
    __tablename__ = "budgets"
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )
    category = Column(
        String,
        unique=True
    )
    limit_amount = Column(
        Float
    )