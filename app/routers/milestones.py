from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse

from app.deps import csrf_is_valid, get_connection
from app.formatting import milestone_view, project_view
from app.repository import create_milestone, find_project, list_milestones, project_visible_to
from app.routers.home import render
from app.routers.login import require_user
from app.validation import clean, milestone_errors

router = APIRouter()


@router.get("/projects/{project_id}")
def project_detail(project_id: int, request: Request, connection=Depends(get_connection)):
    user = require_user(request, connection)
    if user is None:
        return RedirectResponse("/login", status_code=303)
    project = find_project(connection, project_id)
    if not project_visible_to(project, user):
        return render(request, "not_found.html", connection, status_code=404, title="Project not found")
    milestones = [milestone_view(row) for row in list_milestones(connection, project_id)]
    return render(
        request,
        "project_detail.html",
        connection,
        title=project["title"],
        project=project_view(project),
        milestones=milestones,
        can_add=project["owner_id"] == user["id"],
        errors={},
        form={"title": "", "amount": "", "due_date": ""},
    )


@router.post("/projects/{project_id}/milestones")
def add_milestone(
    project_id: int,
    request: Request,
    connection=Depends(get_connection),
    title: str = Form(""),
    amount: str = Form(""),
    due_date: str = Form(""),
    csrf: str = Form(""),
):
    user = require_user(request, connection)
    if user is None:
        return RedirectResponse("/login", status_code=303)
    project = find_project(connection, project_id)
    if not project_visible_to(project, user):
        return render(request, "not_found.html", connection, status_code=404, title="Project not found")
    if project["owner_id"] != user["id"] or user["role"] != "client":
        return render(request, "forbidden.html", connection, status_code=403, title="Not allowed")

    form = {"title": clean(title), "amount": clean(amount), "due_date": clean(due_date)}
    milestones = [milestone_view(row) for row in list_milestones(connection, project_id)]
    page = {
        "title": project["title"],
        "project": project_view(project),
        "milestones": milestones,
        "can_add": True,
        "form": form,
    }
    if not csrf_is_valid(request, csrf):
        page["errors"] = {"form": "The form expired. Submit it again."}
        return render(request, "project_detail.html", connection, **page)

    errors, values = milestone_errors(form["title"], form["amount"], form["due_date"])
    if errors:
        page["errors"] = errors
        return render(request, "project_detail.html", connection, **page)

    create_milestone(connection, project_id, values["title"], values["amount_cents"], values["due_date"])
    return RedirectResponse(f"/projects/{project_id}", status_code=303)
