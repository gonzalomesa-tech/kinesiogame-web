from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes.survey import router as survey_router

from routes.landing import router as landing_router
from routes.favicon import router as favicon_router

app = FastAPI(title="KinesioGame - Encuesta")

# Static (CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Routers
app.include_router(landing_router)
app.include_router(favicon_router)
app.include_router(survey_router)