Personal Finance Tracker

A modular backend system for tracking personal finances, managing budgets, and generating spending insights.
Built using FastAPI and SQLAlchemy, this project goes beyond basic CRUD by incorporating analytics such as budget alerts, savings rate, and category-wise trends.

Features
🔹 Transaction Management
Create, update, delete transactions
Filter by category, type, and date
Duplicate transaction detection with override option
🔹 Budget Management
Create, update, delete budgets
Category-based budgeting
Prevent invalid categories
🔹 Analytics & Insights
Monthly & overall summary
Savings rate calculation
Budget alerts (within / near / exceeded)
Spending insights:
highest spend category
largest expense
average monthly expense
Category-wise trends


Tech Stack
Backend: FastAPI
ORM: SQLAlchemy
Database: SQLite
Language: Python

Project Structure
finance-tracker/
│
├── app/
│   ├── db/              # Database connection
│   ├── models/          # SQLAlchemy models
│   ├── routes/          # API routes
│   ├── services/        # Business logic
│   └── main.py          # App entry point
│
├── seed_data.py         # Script to populate test data
├── requirements.txt
└── README.md


Setup & Run
1. Clone the repo
git clone <your-repo-url>
cd finance-tracker
2. Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
3. Install dependencies
pip install -r requirements.txt
4. Run the server
uvicorn app.main:app --reload

App will run at:

http://127.0.0.1:8000
Seed Data (Optional)

Populate database with 100+ sample transactions:

python seed_data.py
API Endpoints
Transactions
POST   /transactions
PUT    /transactions/{id}
DELETE /transactions/{id}
GET    /transactions
GET    /transactions/filter
Budgets
POST   /budgets
GET    /budgets
PUT    /budgets/{category}
DELETE /budgets/{category}
Analytics
GET /summary
GET /budget/alerts
GET /insights
GET /trends?category=food


Example Request
Create Transaction
{
  "amount": 2500,
  "category": "food",
  "type": "expense",
  "date": "2026-04-20"
}
Duplicate Handling
POST /transactions → 409 if duplicate
POST /transactions?force=true → allows duplicate

Example Response
Insights
{
  "highest_spend_category": "travel",
  "largest_expense": 11000,
  "avg_monthly_expense": 12000
}
Trends
{
  "Jan": 1200,
  "Feb": 1800,
  "Mar": 900
}

Key Design Decisions
Separation of concerns
Routes → request handling
Services → business logic
Models → database
Validation layers
Pydantic → input validation
Service layer → DB/business validation
Reusable logic
Centralized validation functions
Shared filtering & aggregation logic

Future Improvements
Authentication & user-specific data
Recurring transactions
Frontend dashboard
Export reports (CSV/PDF)

Learning Highlights
API design with FastAPI
ORM usage with SQLAlchemy
Data aggregation & analytics
Handling duplicates and validation
Structuring scalable backend systems


Author
Nishtha Gulati