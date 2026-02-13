import os
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    # Link configurable desde Railway (Variables)
    survey_url = os.getenv("SURVEY_URL", "").strip()
    if not survey_url:
        survey_url = "https://TU-LINK-DE-ENCUESTA-AQUI"  # fallback

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "survey_url": survey_url,
        },
    )