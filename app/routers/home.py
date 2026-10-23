from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.deps import current_user, ensure_csrf, get_connection
from app.factory import TEMPLATE_DIR

router = APIRouter()
templates = Jinja2Templates(directory=TEMPLATE_DIR)


def render(request: Request, name: str, connection, status_code: int = 200, **context):
    user = current_user(request, connection)
    context.update(
        request=request,
        csrf=ensure_csrf(request),
        user=None if user is None else {"name": user["name"], "role": user["role"]},
    )
    return templates.TemplateResponse(request, name, context, status_code=status_code)


@router.get("/", response_class=HTMLResponse)
def home(request: Request, connection=Depends(get_connection)):
    notice = "Account created. You can log in now." if request.query_params.get("registered") else ""
    return render(request, "home.html", connection, title="Home", notice=notice)


@router.get("/health")
def health():
    return {"status": "ok"}
