from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse

from app.deps import csrf_is_valid, current_user, get_connection
from app.formatting import project_view
from app.repository import find_user_by_email, list_projects_for_user
from app.routers.home import render
from app.security import verify_password
from app.validation import clean, login_errors

router = APIRouter()


@router.get("/login")
def login_form(request: Request, connection=Depends(get_connection)):
    notice = "Account created. You can log in now." if request.query_params.get("registered") else ""
    return render(
        request,
        "login.html",
        connection,
        title="Log in",
        errors={},
        form={"email": ""},
        notice=notice,
    )


@router.post("/login")
def login(
    request: Request,
    connection=Depends(get_connection),
    email: str = Form(""),
    password: str = Form(""),
    csrf: str = Form(""),
):
    form = {"email": clean(email).lower()}
    if not csrf_is_valid(request, csrf):
        errors = {"form": "The form expired. Submit it again."}
        return render(request, "login.html", connection, title="Log in", errors=errors, form=form, notice="")

    errors = login_errors(form["email"], password)
    user = find_user_by_email(connection, form["email"]) if not errors else None
    if errors or user is None or not verify_password(password, user["password_hash"]):
        if not errors:
            errors = {"form": "The email or password is incorrect."}
        return render(request, "login.html", connection, title="Log in", errors=errors, form=form, notice="")

    request.session["user_id"] = user["id"]
    return RedirectResponse("/dashboard", status_code=303)


@router.post("/logout")
def logout(request: Request, csrf: str = Form(""), connection=Depends(get_connection)):
    if csrf_is_valid(request, csrf):
        request.session.clear()
    return RedirectResponse("/", status_code=303)


@router.get("/dashboard")
def dashboard(request: Request, connection=Depends(get_connection)):
    user = require_user(request, connection)
    if user is None:
        return RedirectResponse("/login", status_code=303)
    projects = [project_view(row) for row in list_projects_for_user(connection, user)]
    return render(request, "dashboard.html", connection, title="Dashboard", projects=projects)


def require_user(request: Request, connection):
    user = current_user(request, connection)
    if user is None:
        return None
    return user
