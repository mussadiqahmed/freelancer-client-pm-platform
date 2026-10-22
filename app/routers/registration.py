from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse

from app.deps import csrf_is_valid, get_connection
from app.repository import create_user, find_user_by_email
from app.routers.home import render
from app.security import hash_password
from app.validation import clean, registration_errors

router = APIRouter()


@router.get("/register")
def registration_form(request: Request, connection=Depends(get_connection)):
    return render(
        request,
        "register.html",
        connection,
        title="Register",
        errors={},
        form={"name": "", "email": "", "role": "freelancer"},
    )


@router.post("/register")
def register_account(
    request: Request,
    connection=Depends(get_connection),
    name: str = Form(""),
    email: str = Form(""),
    password: str = Form(""),
    role: str = Form(""),
    csrf: str = Form(""),
):
    form = {"name": clean(name), "email": clean(email).lower(), "role": clean(role)}
    if not csrf_is_valid(request, csrf):
        errors = {"form": "The form expired. Submit it again."}
        return render(request, "register.html", connection, title="Register", errors=errors, form=form)

    errors = registration_errors(form["name"], form["email"], password, form["role"])
    if find_user_by_email(connection, form["email"]) and "email" not in errors:
        errors["email"] = "That email is already registered."
    if errors:
        return render(request, "register.html", connection, title="Register", errors=errors, form=form)

    created = create_user(connection, form["name"], form["email"], hash_password(password), form["role"])
    if created is None:
        errors = {"email": "That email is already registered."}
        return render(request, "register.html", connection, title="Register", errors=errors, form=form)
    return RedirectResponse("/login?registered=1", status_code=303)
