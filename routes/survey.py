import json
import os
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from utils.sheets import append_row

BASE_DIR = Path(__file__).resolve().parents[1]
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter()

LIKERT_ITEMS = [
    "Estoy satisfecho(a) con la plataforma interactiva de rehabilitación propuesta.",
    "La experiencia general de uso de la plataforma fue positiva.",
    "Estoy satisfecho con la metodología propuesta para la rehabilitación de extremidad superior.",
    "Estoy satisfecho(a) con la metodología de rehabilitación propuesta a través de la plataforma.",
    "Los ejercicios presentados son adecuados para los objetivos terapéuticos.",
    "La plataforma permite adaptar la terapia a distintos niveles de desempeño del usuario.",
    "La plataforma es fácil de usar y comprender.",
    "La interacción con la plataforma es intuitiva.",
    "El tiempo requerido para aprender a usar la plataforma es adecuado.",
    "La interfaz gráfica es clara y comprensible.",
    "El uso de la plataforma resulta motivante para el usuario.",
    "El feedback entregado por la plataforma es claro y útil durante la rehabilitación.",
    "Utilizaría esta plataforma de forma regular.",
    "Considero viable su implementación en un entorno clínico real.",
    "Recomendaría esta plataforma a otros profesionales o usuarios.",
]


@router.get("/encuesta", response_class=HTMLResponse)
def survey_get(request: Request):
    return templates.TemplateResponse(
        "survey.html",
        {"request": request, "items": LIKERT_ITEMS},
    )


@router.post("/encuesta")
async def survey_post(request: Request):
    form = await request.form()

    # Campos obligatorios
    nombre = (form.get("nombre") or "").strip()
    correo = (form.get("correo") or "").strip()
    edad_raw = (form.get("edad") or "").strip()

    if not nombre or not correo or not edad_raw:
        return RedirectResponse(url="/encuesta", status_code=303)

    # Validación básica de edad
    try:
        edad = int(edad_raw)
        if edad < 10 or edad > 110:
            return RedirectResponse(url="/encuesta", status_code=303)
    except ValueError:
        return RedirectResponse(url="/encuesta", status_code=303)

    # Armamos payload final
    payload = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "datos_generales": {
            "nombre": nombre,
            "correo": correo,
            "edad": edad,
        },
        "likert": {},
        "abiertas": {
            "problemas": (form.get("problemas") or "").strip(),
            "ventajas": (form.get("ventajas") or "").strip(),
            "otros_juegos": (form.get("otros_juegos") or "").strip(),
        },
    }

    # Guardar Likert (item_1 ... item_N)
    for idx in range(1, len(LIKERT_ITEMS) + 1):
        payload["likert"][f"item_{idx}"] = (form.get(f"item_{idx}") or "").strip()

    # ===== Google Sheets (si están las variables) =====
    sheet_id = os.getenv("GSHEET_ID", "").strip()
    tab = os.getenv("GSHEET_TAB", "Respuestas").strip()

    if sheet_id:
        row = [
            payload["timestamp"],
            payload["datos_generales"]["nombre"],
            payload["datos_generales"]["correo"],
            str(payload["datos_generales"]["edad"]),
        ]

        # Likert
        for idx in range(1, len(LIKERT_ITEMS) + 1):
            row.append(str(payload["likert"].get(f"item_{idx}", "")))

        # Abiertas
        row.extend(
            [
                payload["abiertas"]["problemas"],
                payload["abiertas"]["ventajas"],
                payload["abiertas"]["otros_juegos"],
            ]
        )

        try:
            append_row(sheet_id, row, sheet_name=tab)
        except Exception as e:
            # Importante: no caer la app si falla Sheets
            print("Sheets append failed:", repr(e))

    # ===== Guardar respuestas (modo prototipo / respaldo) =====
    data_dir = BASE_DIR / "data"
    data_dir.mkdir(exist_ok=True)
    out_file = data_dir / "respuestas.jsonl"

    with open(out_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")

    return RedirectResponse(url="/gracias", status_code=303)


@router.get("/gracias", response_class=HTMLResponse)
def thanks(request: Request):
    return templates.TemplateResponse("thanks.html", {"request": request})


# Endpoint de debug para probar escritura en Sheets (úsalo y luego lo borras si quieres)
@router.get("/debug/sheets")
def debug_sheets():
    sheet_id = os.getenv("GSHEET_ID", "").strip()
    tab = os.getenv("GSHEET_TAB", "Respuestas").strip()
    if not sheet_id:
        return {"ok": False, "error": "Missing GSHEET_ID"}

    try:
        append_row(sheet_id, ["TEST", "ok"], sheet_name=tab)
        return {"ok": True, "sheet_id": sheet_id, "tab": tab}
    except Exception as e:
        return {"ok": False, "error": repr(e), "sheet_id": sheet_id, "tab": tab}