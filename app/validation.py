import re
from datetime import date
from decimal import Decimal, InvalidOperation

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
ROLES = {"client", "freelancer"}
PROJECT_STATUSES = {"draft", "published"}
MAX_BUDGET_CENTS = 100_000_000_00


def clean(value: str | None) -> str:
    return (value or "").strip()


def registration_errors(name: str, email: str, password: str, role: str) -> dict[str, str]:
    errors: dict[str, str] = {}
    if not name or len(name) > 80:
        errors["name"] = "Enter a name up to 80 characters."
    if not EMAIL_PATTERN.fullmatch(email):
        errors["email"] = "Enter a valid email address."
    if len(password) < 8 or len(password) > 128:
        errors["password"] = "Use a password between 8 and 128 characters."
    if role not in ROLES:
        errors["role"] = "Choose freelancer or client."
    return errors


def login_errors(email: str, password: str) -> dict[str, str]:
    errors: dict[str, str] = {}
    if not email:
        errors["email"] = "Email is required."
    if not password:
        errors["password"] = "Password is required."
    return errors


def parse_money(raw: str) -> int | None:
    try:
        amount = Decimal(raw.strip())
    except (InvalidOperation, AttributeError):
        return None
    if amount <= 0 or amount != amount.quantize(Decimal("0.01")):
        return None
    cents = int(amount * 100)
    if cents > MAX_BUDGET_CENTS:
        return None
    return cents


def parse_date(raw: str) -> str | None:
    try:
        return date.fromisoformat(raw.strip()).isoformat()
    except (ValueError, AttributeError):
        return None


def project_errors(title, description, budget_raw, deadline_raw, status):
    errors: dict[str, str] = {}
    if not title or len(title) > 120:
        errors["title"] = "Enter a title up to 120 characters."
    if not description or len(description) > 4000:
        errors["description"] = "Enter a description up to 4000 characters."
    budget = parse_money(budget_raw)
    if budget is None:
        errors["budget"] = "Enter a budget greater than 0, with up to 2 decimal places."
    deadline = parse_date(deadline_raw)
    if deadline is None:
        errors["deadline"] = "Enter a deadline as YYYY-MM-DD."
    if status not in PROJECT_STATUSES:
        errors["status"] = "Save the project as a draft or publish it."
    values = {
        "title": title,
        "description": description,
        "budget_cents": budget,
        "deadline": deadline,
        "status": status,
    }
    return errors, values


def milestone_errors(title: str, amount_raw: str, due_raw: str):
    errors: dict[str, str] = {}
    if not title or len(title) > 120:
        errors["title"] = "Enter a milestone title up to 120 characters."
    amount = parse_money(amount_raw)
    if amount is None:
        errors["amount"] = "Enter an amount greater than 0, with up to 2 decimal places."
    due_date = parse_date(due_raw)
    if due_date is None:
        errors["due_date"] = "Enter a due date as YYYY-MM-DD."
    values = {"title": title, "amount_cents": amount, "due_date": due_date}
    return errors, values
