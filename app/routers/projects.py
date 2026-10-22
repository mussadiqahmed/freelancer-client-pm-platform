from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse

from app.deps import csrf_is_valid, get_connection
from app.repository import create_project
from app.routers.home import render
from app.routers.login import require_user
from app.validation import clean, project_errors

router = APIRouter()


@router.get("/projects/new")
def new_project_form(request: Request, connection=Depends(get_connection)):
    user = require_user(request, connection)
    if user is None:
        return RedirectResponse("/login", status_code=303)
    if user["role"] != "client":
        return render(request, "forbidden.html", connection, title="Not allowed", status_code=403)
    return render(
        request,
        "project_form.html",
        connection,
        title="Post a project",
        errors={},
        form={"title": "", "description": "", "budget": "", "deadline": "", "status": "draft"},
    )


@router.post("/projects")
def post_project(
    request: Request,
    connection=Depends(get_connection),
    title: str = Form(""),
    description: str = Form(""),
    budget: str = Form(""),
    deadline: str = Form(""),
    status: str = Form("draft"),
    csrf: str = Form(""),
):
    user = require_user(request, connection)
    if user is None:
        return RedirectResponse("/login", status_code=303)
    if user["role"] != "client":
        return render(request, "forbidden.html", connection, title="Not allowed", status_code=403)

    form = {
        "title": clean(title),
        "description": clean(description),
        "budget": clean(budget),
        "deadline": clean(deadline),
        "status": clean(status),
    }
    if not csrf_is_valid(request, csrf):
        errors = {"form": "The form expired. Submit it again."}
        return render(request, "project_form.html", connection, title="Post a project", errors=errors, form=form)

    errors, values = project_errors(
        form["title"], form["description"], form["budget"], form["deadline"], form["status"]
    )
    if errors:
        return render(request, "project_form.html", connection, title="Post a project", errors=errors, form=form)

    create_project(
        connection,
        user["id"],
        values["title"],
        values["description"],
        values["budget_cents"],
        values["deadline"],
        values["status"],
    )
    return RedirectResponse("/dashboard", status_code=303)
