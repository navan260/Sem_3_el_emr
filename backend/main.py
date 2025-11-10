from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import datetime

from db import crud_operations

app = FastAPI()

templates = Jinja2Templates(directory="backend/templates")


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
    patientAddress: str = Form(...)
):
    print(patientName)
    context = {
        "request": request,
        "success": patientName
    }
    crud_operations.insert_patient(
        name=patientName,
        phone=patientPhone,
        email=patientEmail,
        address=patientAddress,
        date_added=datetime.datetime.now()
    )
    return templates.TemplateResponse(name="success.html", context=context)