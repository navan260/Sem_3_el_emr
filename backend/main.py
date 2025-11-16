from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import datetime
from db.supabase import patient_operations
from fastapi.staticfiles import StaticFiles  # <-- 1. IMPORT THIS
from pathlib import Path
from info_extract_util import main
from typing import Optional
import mimetypes

app = FastAPI()

templates = Jinja2Templates(directory="backend/templates")
BASE_DIR = Path(__file__).resolve().parent

app.mount(
    "/static",
    StaticFiles(directory=str(Path(BASE_DIR, "static"))),
    name="static"
)


#API Endpoint for root webpage
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    context = {
        "request": request
    }
    return templates.TemplateResponse(name="index.html", context=context)


#API Endpoint for New Patient (Manually)
@app.post("/patient/form", response_class=HTMLResponse)
async def read_patient_form(
    request: Request,
    patientName: str = Form(...),
    patientPhone : str = Form(...),
    patientEmail: str = Form(...),
    patientAddress: str = Form(...),
    diseaseName: str = Form(...),
    diseaseID: int = Form(...)
):
    patient_operations.insert_patient(
        name=patientName,
        phone=patientPhone,
        email=patientEmail,
        address=patientAddress,
        disease_name=diseaseName,
        disease_id=diseaseID
    )
    return RedirectResponse(url="/display", status_code=303)


#API Endpoint for Upload File
@app.get("/upload",response_class=HTMLResponse)
async def file_upload(request: Request):
    context = {
        "request": request
    }
    return templates.TemplateResponse(name="upload.html", context=context)


#API Endpoint for New Patient (upload file)
@app.post("/patient/upload", response_class=HTMLResponse)
async def upload_file_info(
    request: Request,
    file: UploadFile = File(...)
):
    file_bytes = await file.read()
    mime_type, _ = mimetypes.guess_type(file.filename)
    res = main.gemini_extract(file_bytes, mime_type)

    context = {
        "request": request,
        "data": res
    }
    # Pass extracted info to HTML page
    return templates.TemplateResponse(name="edit_patient.html", context=context)


#API Endpoint to Edit Details given by Gemini
@app.post("/patient/save")
async def save_patient(
    name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    address: str = Form(...),
    disease_name: str = Form(...),
    disease_id: int = Form(...)
):
    patient_operations.insert_patient(
        name=name,
        phone=phone,
        email=email,
        address=address,
        disease_name=disease_name,
        disease_id=disease_id
    )

    return RedirectResponse(url="/display", status_code=303)


#API Endpoint to display all the patients
@app.get("/display", response_class=HTMLResponse)
async def get_all_patients(request: Request):
    patients = patient_operations.get_all_patients()
    context = {
        "request": request,
        "patients": patients 
    }
    return templates.TemplateResponse(name="display.html", context=context)


#API Endpoint to get patient detail by ID
@app.get("/edit/{patient_id}")
async def edit_patient_form(request: Request, patient_id: int):
    patient = patient_operations.get_patient_by_id(patient_id)
    context = {
        "request": request,
        "patient": patient
    }
    return templates.TemplateResponse(name="edit.html", context=context)


#API Endpoint to edit patient details
@app.post("/edit/{patient_id}")
async def update_patient(
    request: Request,
    patient_id: int,
    name: Optional[str] = Form(None),
    phone: Optional[int] = Form(None),
    email: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    disease_id: Optional[int] = Form(None),
    disease_name: Optional[str] = Form(None)
):
    
    patient_operations.update_patient(patient_id, name, phone, email, address, disease_id, disease_name)
    return RedirectResponse(url="/display", status_code=303)
