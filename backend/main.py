from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import datetime
from db.supabase import patient_operations
from fastapi.staticfiles import StaticFiles  # <-- 1. IMPORT THIS
from pathlib import Path

app = FastAPI()

templates = Jinja2Templates(directory="backend/templates")
BASE_DIR = Path(__file__).resolve().parent

app.mount(
    "/static",
    StaticFiles(directory=str(Path(BASE_DIR, "static"))),
    name="static"
)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    context = {
        "request": request
    }
    return templates.TemplateResponse(name="index.html", context=context)


@app.post("/patient/form", response_class=HTMLResponse)
async def read_patient_form(
    request: Request,
    patientId: str = Form(...),
    patientName: str = Form(...),
    patientPhone : str = Form(...),
    patientEmail: str = Form(...),
    patientAddress: str = Form(...),
    diseaseName: str = Form(...)
):
    print(patientName)
    context = {
        "request": request,
        "success": patientName,
        "name": patientName,
    }
    patient_operations.insert_patient(
        name=patientName,
        phone=patientPhone,
        email=patientEmail,
        address=patientAddress,
        disease_name=diseaseName,
        disease_id="3293279327"
    )
    return templates.TemplateResponse(name="success.html", context=context)

@app.get("/upload",response_class=HTMLResponse)
async def file_upload(request: Request):
    context = {
        "request": request
    }
    return templates.TemplateResponse(name="upload.html", context=context)

@app.post("/patient/upload", response_class=HTMLResponse)
async def upload_file_info(request: Request):
    context = {
        "request": request
    }
    
    return templates.TemplateResponse(name="success.html", context=context)