from fastmcp import FastMCP
from models import Expenses
from database import get_session_local, Base, init_db
from sqlalchemy import func
import json

# we can easily convert fastapi to fastmcp
'''mcp =  FastMCP.from_fastapi(
    app=app,
    name="Expense Tracker Server"
)

if __name__ == '__main__':
    mcp.run()
'''   

mcp = FastMCP("Expense Tracker")

def _ensure_db():
    if not getattr(_ensure_db, "_done", False):
        init_db()
        _ensure_db._done = True

@mcp.tool
def add_expense(date: str, amount: float, category: str, subcategory: str = "", note: str = ""):
    """ Add a new expense record"""

    _ensure_db()
    db = get_session_local()()

    try:
        expense = Expenses(
            date=date,
            amount=amount,
            category=category,
            subcategory=subcategory,
            note=note,
        )
        db.add(expense)
        db.commit()
        db.refresh(expense)

        return {
             "status": 'ok',
             "id": expense.id
            }
    
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": f"Database error: {str(e)}"}
    
    finally:
        db.close()

@mcp.tool
def list_expenses(start_date: str, end_date: str):
    """List expense entries within an inclusive date range."""
    
    _ensure_db()
    db = get_session_local()()

    try:
        expenses =  db.query(Expenses).filter(Expenses.date.between(start_date, end_date)).order_by(Expenses.date.asc()).all()
        return [ {
                "id": e.id,
                "date": e.date,
                "amount": e.amount,
                "category": e.category,
                "subcategory": e.subcategory,
                "note": e.note
        } for e in expenses]
    
    except Exception as e:
        return { 
            "status": "error", 
            "message": f"Error listing expenses: {str(e)}"
            }
    
    finally:
        db.close()

@mcp.tool
def get_expense(expense_id: int):
    """Get an expense by ID."""
    
    _ensure_db()
    db = get_session_local()()

    try:
        expense = (
            db.query(Expenses)
            .filter(Expenses.id == expense_id)
            .first()
        )

        if not expense:
            return {
                "status": "error",
                "message": "Expense not found",
            }

        return {
            "id": expense.id,
            "date": expense.date,
            "amount": expense.amount,
            "category": expense.category,
            "subcategory": expense.subcategory,
            "note": expense.note,
        }

    finally:
        db.close()

@mcp.tool
def update_expense( expense_id: int,  date: str | None = None, amount: float | None = None, category: str | None = None, subcategory: str | None = None,
                    note: str | None = None):
    """Update an existing expense."""

    _ensure_db()
    db = get_session_local()()

    try:
        expense = (
            db.query(Expenses)
            .filter(Expenses.id == expense_id)
            .first()
        )

        if not expense:
            return {
                "status": "error",
                "message": "Expense not found",
            }

        if date is not None:
            expense.date = date
        if amount is not None:
            expense.amount = amount
        if category is not None:
            expense.category = category
        if subcategory is not None:
            expense.subcategory = subcategory
        if note is not None:
            expense.note = note

        db.commit()

        return {
            "status": "ok",
            "id": expense.id,
        }

    except Exception as e:
        db.rollback()
        return {
            "status": "error",
            "message": str(e),
        }

    finally:
        db.close()

@mcp.tool
def delete_expense(expense_id: int):
    """Delete an expense by ID."""

    _ensure_db()
    db = get_session_local()()

    try:
        expense = (
            db.query(Expenses)
            .filter(Expenses.id == expense_id)
            .first()
        )

        if not expense:
            return {
                "status": "error",
                "message": "Expense not found",
            }

        db.delete(expense)
        db.commit()

        return {
            "status": "ok",
            "message": f"Expense {expense_id} deleted",
        }

    except Exception as e:
        db.rollback()
        return {
            "status": "error",
            "message": str(e),
        }

    finally:
        db.close()

@mcp.tool
def summarise(start_date: str, end_date: str, category: str | None = None):
    """Summarize expenses by category within an inclusive date range."""

    _ensure_db()
    db = get_session_local()()

    try:
        query = (
                db.query(
                        Expenses.category,
                        func.sum(Expenses.amount).label("total_amount")
                    )
                    .filter(Expenses.date.between(start_date, end_date))
                )
        
        if category:
            query = query.filter(Expenses.category == category)

        return [{
                "category": cat, 
                "total_amount": total
                }
            for cat, total in query.group_by(Expenses.category).all()
        ]
    
    except Exception as e:
        return {
                "status": "error",
                "message": f"Error summarizing expenses: {str(e)}"
            }
    
    finally:
        db.close()

# consistent schema/entries in database ex: category 
@mcp.resource("categories://all")
def categories():
    """Read fresh each time so you can edit file without restarting"""

    default_categories = {
            "categories": [
                "Food & Dining",
                "Transportation",
                "Shopping",
                "Entertainment",
                "Bills & Utilities",
                "Healthcare",
                "Travel",
                "Education",
                "Business",
                "Other"
            ]
        }
    
    try:
        with open('categories.json', 'r') as f:
            return f.read()
        
    except FileNotFoundError:
            return json.dumps(default_categories, indent=2)

#start the server
#if __name__ == '__main__':
    #mcp.run()
    


