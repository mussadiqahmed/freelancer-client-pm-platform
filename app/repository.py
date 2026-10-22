import sqlite3

from app.db import utc_now


def create_user(connection, name, email, password_hash, role):
    try:
        cursor = connection.execute(
            """
            INSERT INTO users (name, email, password_hash, role, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, email, password_hash, role, utc_now()),
        )
    except sqlite3.IntegrityError:
        return None
    return cursor.lastrowid


def find_user_by_email(connection, email):
    return connection.execute(
        "SELECT * FROM users WHERE email = ? COLLATE NOCASE",
        (email,),
    ).fetchone()


def find_user_by_id(connection, user_id):
    return connection.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def create_project(connection, owner_id, title, description, budget_cents, deadline, status):
    cursor = connection.execute(
        """
        INSERT INTO projects
            (owner_id, title, description, budget_cents, deadline, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (owner_id, title, description, budget_cents, deadline, status, utc_now()),
    )
    return cursor.lastrowid


def list_projects_for_user(connection, user):
    if user["role"] == "client":
        query = "SELECT * FROM projects WHERE owner_id = ? ORDER BY id DESC"
        return connection.execute(query, (user["id"],)).fetchall()
    query = """
        SELECT * FROM projects
        WHERE status = 'published'
        ORDER BY id DESC
    """
    return connection.execute(query).fetchall()


def find_project(connection, project_id):
    return connection.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()


def project_visible_to(project, user) -> bool:
    if project is None or user is None:
        return False
    if project["owner_id"] == user["id"]:
        return True
    return user["role"] == "freelancer" and project["status"] == "published"


def create_milestone(connection, project_id, title, amount_cents, due_date):
    cursor = connection.execute(
        """
        INSERT INTO milestones (project_id, title, amount_cents, due_date, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (project_id, title, amount_cents, due_date, utc_now()),
    )
    return cursor.lastrowid


def list_milestones(connection, project_id):
    return connection.execute(
        "SELECT * FROM milestones WHERE project_id = ? ORDER BY id ASC",
        (project_id,),
    ).fetchall()
