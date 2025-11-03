"""
FastAPI Backend Server - EMR Digitization System
=================================================
Central hub for patient data, file uploads, and medical information extraction
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
import os
import shutil
import logging
from datetime import date

# Import database operations
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'db'))
from crud_operations import insert_patient, get_patient_by_id, get_all_patients

# Import Gemini extractor
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'info_extract_util'))
from gemini_extractor import GeminiMedicalExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="EMR Digitization API",
    description="Backend API for Electronic Medical Records digitization and extraction",
    version="1.0.0"
)

# CORS Configuration - Allow frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create uploads directory if not exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize Gemini extractor
try:
    extractor = GeminiMedicalExtractor()
    logger.info("✅ Gemini extractor initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize Gemini extractor: {e}")
    extractor = None

# ============================================================================
# PYDANTIC MODELS - Request/Response Validation
# ============================================================================

class PatientModel(BaseModel):
    """Patient demographic data model"""
    patient_name: str = Field(..., min_length=2, max_length=100)
    patient_phone: str = Field(..., pattern=r'^\d{10,15}$')
    patient_email: EmailStr
    patient_address: str = Field(..., min_length=5, max_length=500)

class PatientResponse(BaseModel):
    """Response after patient creation"""
    status: str
    message: str
    patient_id: Optional[int] = None
    data: Optional[dict] = None

class DocumentModel(BaseModel):
    """Document metadata"""
    document_id: int
    patient_id: int
    filename: str
    upload_date: str
    status: str

class ExtractionResult(BaseModel):
    """Extracted medical information"""
    status: str
    patient_name: Optional[str] = None
    diseases: List[dict] = []
    confidence_score: Optional[float] = None
    error: Optional[str] = None

# ============================================================================
# ROUTE HANDLERS
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve patient information form"""
    try:
        with open("templates/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse("<h1>EMR Digitization API</h1><p>Use /docs for API documentation</p>")

@app.get("/upload", response_class=HTMLResponse)
async def upload_page():
    """Serve file upload page"""
    try:
        with open("templates/upload.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Upload page not found")

@app.get("/health")
async def health_check():
    """API health check endpoint"""
    return {
        "status": "healthy",
        "message": "EMR Digitization API is running",
        "gemini_available": extractor is not None
    }

# ============================================================================
# PATIENT OPERATIONS
# ============================================================================

@app.post("/api/patient", response_model=PatientResponse)
async def create_patient(patient: PatientModel):
    """
    Create a new patient record
    
    Args:
        patient: Patient demographic data
        
    Returns:
        PatientResponse with patient_id
    """
    try:
        logger.info(f"📝 Creating patient: {patient.patient_name}")
        
        # Insert patient into database
        patient_id = insert_patient(
            name=patient.patient_name,
            phone=patient.patient_phone,
            email=patient.patient_email,
            address=patient.patient_address,
            date_added=date.today()
        )
        
        if patient_id:
            logger.info(f"✅ Patient created with ID: {patient_id}")
            return PatientResponse(
                status="success",
                message="Patient registered successfully",
                patient_id=patient_id,
                data=patient.dict()
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to create patient record")
            
    except Exception as e:
        logger.error(f"❌ Error creating patient: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/patient/{patient_id}")
async def get_patient(patient_id: int):
    """
    Retrieve patient information by ID
    
    Args:
        patient_id: Patient ID
        
    Returns:
        Patient data
    """
    try:
        logger.info(f"🔍 Fetching patient ID: {patient_id}")
        patient = get_patient_by_id(patient_id)
        
        if patient:
            return {
                "status": "success",
                "data": patient
            }
        else:
            raise HTTPException(status_code=404, detail="Patient not found")
            
    except Exception as e:
        logger.error(f"❌ Error fetching patient: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/patients")
async def list_patients():
    """
    Get all patients
    
    Returns:
        List of all patients
    """
    try:
        logger.info("📋 Fetching all patients")
        patients = get_all_patients()
        
        return {
            "status": "success",
            "count": len(patients),
            "data": patients
        }
    except Exception as e:
        logger.error(f"❌ Error fetching patients: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# FILE UPLOAD & PROCESSING
# ============================================================================

@app.post("/api/upload")
async def upload_document(
    file: UploadFile = File(...),
    patient_id: Optional[int] = Form(None)
):
    """
    Upload medical document (PDF, JPG, PNG)
    
    Args:
        file: Uploaded file
        patient_id: Optional patient ID to associate with document
        
    Returns:
        Upload confirmation with file details
    """
    try:
        logger.info(f"📤 Uploading file: {file.filename}")
        
        # Validate file type
        allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Validate file size (max 10MB)
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()  # Get position (file size)
        file.file.seek(0)  # Reset to beginning
        
        max_size = 10 * 1024 * 1024  # 10MB
        if file_size > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {max_size / (1024*1024)}MB"
            )
        
        # Save file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"✅ File saved: {file_path}")
        
        return {
            "status": "success",
            "message": "File uploaded successfully",
            "filename": file.filename,
            "file_path": file_path,
            "file_size": file_size,
            "patient_id": patient_id
        }
        
    except Exception as e:
        logger.error(f"❌ Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process/{filename}", response_model=ExtractionResult)
async def process_document(filename: str):
    """
    Process uploaded document with Gemini extraction
    
    Args:
        filename: Name of uploaded file
        
    Returns:
        Extracted medical information
    """
    try:
        if not extractor:
            raise HTTPException(
                status_code=503,
                detail="Gemini extractor not available. Check GEMINI_API_KEY environment variable."
            )
        
        logger.info(f"🔄 Processing document: {filename}")
        
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Extract information using Gemini
        result = extractor.extract_from_file(file_path)
        
        logger.info(f"✅ Extraction complete: {result.get('status')}")
        
        return ExtractionResult(**result)
        
    except Exception as e:
        logger.error(f"❌ Processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-and-process")
async def upload_and_process(
    file: UploadFile = File(...),
    patient_id: Optional[int] = Form(None)
):
    """
    Upload and immediately process document (combined endpoint)
    
    Args:
        file: Uploaded file
        patient_id: Optional patient ID
        
    Returns:
        Upload confirmation + extracted data
    """
    try:
        # First, upload the file
        upload_result = await upload_document(file, patient_id)
        
        # Then, process it
        extraction_result = await process_document(upload_result['filename'])
        
        return {
            "upload": upload_result,
            "extraction": extraction_result
        }
        
    except Exception as e:
        logger.error(f"❌ Upload and process error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# RESULTS & ANALYTICS
# ============================================================================

@app.get("/api/results/{patient_id}")
async def get_patient_results(patient_id: int):
    """
    Get all results for a patient
    
    Args:
        patient_id: Patient ID
        
    Returns:
        Patient data with associated medical records
    """
    try:
        logger.info(f"📊 Fetching results for patient: {patient_id}")
        
        patient = get_patient_by_id(patient_id)
        
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # TODO: Add logic to fetch associated documents and extractions
        
        return {
            "status": "success",
            "patient": patient,
            "documents": [],  # Will be populated when document tracking is added
            "extractions": []  # Will be populated when extraction storage is added
        }
        
    except Exception as e:
        logger.error(f"❌ Error fetching results: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🚀 Starting EMR Digitization API Server")
    print("="*60)
    print("\n📍 API Documentation: http://localhost:8000/docs")
    print("📍 Patient Form: http://localhost:8000/")
    print("📍 Upload Page: http://localhost:8000/upload")
    print("\n" + "="*60 + "\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload on code changes
    )