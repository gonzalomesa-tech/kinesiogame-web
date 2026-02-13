import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()
FAVICON_PNG_PATH = os.path.join("assets", "kinesiogame-favicon.png")

def _file_or_404(path: str):
    if not os.path.isfile(path):
        raise HTTPException(
            status_code=404,
            detail=f"Favicon not found at: {path}"
        )
    return FileResponse(path, media_type="image/png")

@router.get("/favicon.png", include_in_schema=False)
def favicon_png():
    return _file_or_404(FAVICON_PNG_PATH)

@router.get("/favicon.ico", include_in_schema=False)
def favicon_ico():
    return _file_or_404(FAVICON_PNG_PATH)