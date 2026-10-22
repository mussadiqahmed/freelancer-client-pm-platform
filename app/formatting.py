def money(cents: int) -> str:
    return f"{cents / 100:.2f}"


def user_view(row) -> dict:
    return {"id": row["id"], "name": row["name"], "email": row["email"], "role": row["role"]}


def project_view(row) -> dict:
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "budget": money(row["budget_cents"]),
        "deadline": row["deadline"],
        "status": row["status"],
        "owner_id": row["owner_id"],
    }


def milestone_view(row) -> dict:
    return {
        "id": row["id"],
        "title": row["title"],
        "amount": money(row["amount_cents"]),
        "due_date": row["due_date"],
    }
