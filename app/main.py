from fastapi import FastAPI
from app.db.database import engine
from app.models import models

from app.routes.transactions import router as transaction_router
from app.routes.summary import router as summary_router

models.Base.metadata.create_all(
    bind=engine
)

app = FastAPI()

app.include_router(transaction_router)
app.include_router(summary_router)