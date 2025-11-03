"""
Pydantic Models
===============
Data validation models for API requests and responses
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict
from datetime import date, datetime
from enum import Enum

# ============================================================================
# ENUMS
# ============================================================================

class DocumentStatus(str, Enum):
    """Document processing status"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ProcessingStatus(str, Enum):
    """Overall processing status"""
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"

# ============================================================================
# PATIENT MODELS
# ============================================================================

class PatientModel(BaseModel):
    """Patient demographic data for registration"""
    patient_name: str = Field(
        ..., 
        min_length=2, 
        max_length=100,
        description="Patient's full name"
    )
    patient_phone: str = Field(
        ..., 
        pattern=r'^\d{10,15}$',
        description="Phone number (10-15 digits)"
    )
    patient_email: EmailStr = Field(
        ...,
        description="Valid email address"
    )
    patient_address: str = Field(
        ..., 
        min_length=5, 
        max_length=500,
        description="Full address"
    )
    
    @validator('patient_name')
    def name_must_contain_letters(cls, v):
        if not any(c.isalpha() for c in v):
            raise ValueError('Name must contain letters')
        return v.strip()
    
    @validator('patient_phone')
    def phone_must_be_valid(cls, v):
        if not v.isdigit():
            raise ValueError('Phone must contain only digits')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "patient_name": "John Doe",
                "patient_phone": "9876543210",
                "patient_email": "john.doe@email.com",
                "patient_address": "123 Main St, City, State 12345"
            }
        }

class PatientResponse(BaseModel):
    """Response after patient creation"""
    status: str = Field(..., description="Operation status")
    message: str = Field(..., description="Status message")
    patient_id: Optional[int] = Field(None, description="Created patient ID")
    data: Optional[Dict] = Field(None, description="Patient data")

class PatientDetails(BaseModel):
    """Complete patient information"""
    patient_id: int
    patient_name: str
    patient_phone: str
    patient_email: str
    patient_address: str
    date_added: date
    
    class Config:
        from_attributes = True

# ============================================================================
# DOCUMENT MODELS
# ============================================================================

class DocumentUploadModel(BaseModel):
    """Document upload metadata"""
    patient_id: Optional[int] = Field(None, description="Associated patient ID")
    
class DocumentModel(BaseModel):
    """Document information"""
    document_id: int = Field(..., description="Unique document identifier")
    patient_id: Optional[int] = Field(None, description="Associated patient ID")
    filename: str = Field(..., description="Original filename")
    file_path: str = Field(..., description="Server file path")
    file_size: int = Field(..., description="File size in bytes")
    upload_date: datetime = Field(default_factory=datetime.now, description="Upload timestamp")
    status: DocumentStatus = Field(default=DocumentStatus.UPLOADED, description="Processing status")

class DocumentResponse(BaseModel):
    """Response after document upload"""
    status: str
    message: str
    filename: str
    file_path: str
    file_size: int
    patient_id: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "File uploaded successfully",
                "filename": "medical_report.pdf",
                "file_path": "uploads/medical_report.pdf",
                "file_size": 524288,
                "patient_id": 1
            }
        }

# ============================================================================
# EXTRACTION MODELS
# ============================================================================

class ICDCodeModel(BaseModel):
    """ICD-10 code"""
    code: str = Field(..., description="ICD-10 code")
    description: str = Field(..., description="Code description")
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "E11.10",
                "description": "Type 2 diabetes mellitus with ketoacidosis without coma"
            }
        }

class DiseaseModel(BaseModel):
    """Disease with ICD codes"""
    disease_name: str = Field(..., description="Disease or diagnosis name")
    icd_codes: List[ICDCodeModel] = Field(default_factory=list, description="Associated ICD-10 codes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "disease_name": "Type 2 Diabetes Mellitus",
                "icd_codes": [
                    {
                        "code": "E11.10",
                        "description": "Type 2 diabetes mellitus with ketoacidosis without coma"
                    }
                ]
            }
        }

class ExtractionResult(BaseModel):
    """Extracted medical information from document"""
    status: str = Field(..., description="Extraction status")
    patient_name: Optional[str] = Field(None, description="Extracted patient name")
    diseases: List[DiseaseModel] = Field(default_factory=list, description="Extracted diseases")
    confidence_score: Optional[float] = Field(None, ge=0, le=1, description="Confidence score (0-1)")
    error: Optional[str] = Field(None, description="Error message if failed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "patient_name": "John Doe",
                "diseases": [
                    {
                        "disease_name": "Type 2 Diabetes Mellitus",
                        "icd_codes": [
                            {
                                "code": "E11.10",
                                "description": "Type 2 diabetes mellitus with ketoacidosis"
                            }
                        ]
                    }
                ],
                "confidence_score": 0.92
            }
        }

# ============================================================================
# COMBINED RESPONSE MODELS
# ============================================================================

class UploadAndProcessResponse(BaseModel):
    """Combined response for upload + extraction"""
    upload: DocumentResponse = Field(..., description="Upload details")
    extraction: ExtractionResult = Field(..., description="Extraction results")

class PatientResultsResponse(BaseModel):
    """Complete patient results with documents and extractions"""
    status: str
    patient: PatientDetails
    documents: List[DocumentModel] = Field(default_factory=list)
    extractions: List[ExtractionResult] = Field(default_factory=list)

# ============================================================================
# ERROR MODELS
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response"""
    status: str = "error"
    message: str
    detail: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "message": "File not found",
                "detail": "The requested file does not exist on the server"
            }
        }

class ValidationErrorResponse(BaseModel):
    """Validation error response"""
    status: str = "error"
    message: str = "Validation failed"
    errors: List[Dict] = Field(default_factory=list)

# ============================================================================
# HEALTH CHECK MODEL
# ============================================================================

class HealthCheckResponse(BaseModel):
    """API health check response"""
    status: str = "healthy"
    message: str
    gemini_available: bool
    database_connected: bool = True
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "message": "EMR Digitization API is running",
                "gemini_available": True,
                "database_connected": True,
                "timestamp": "2024-01-01T12:00:00"
            }
        }