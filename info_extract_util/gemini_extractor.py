import os
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List, Optional
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# PYDANTIC MODELS - Defines the JSON structure you want
# ============================================================================

class ICDCode(BaseModel):
    """Single ICD-10 code"""
    code: str = Field(description="ICD-10 code like E11.10")
    description: str = Field(description="What the code means")


class Disease(BaseModel):
    """Disease with its ICD codes"""
    disease_name: str = Field(description="Disease or diagnosis name")
    icd_codes: List[ICDCode] = Field(description="ICD-10 codes for this disease")


class PatientMedicalExtraction(BaseModel):
    """
    SIMPLIFIED OUTPUT - Only what you need!
    This is your final JSON structure.
    """
    patient_name: Optional[str] = Field(
        default=None,
        description="Patient's full name"
    )
    diseases: List[Disease] = Field(
        default_factory=list,
        description="List of diseases with their ICD codes"
    )
    confidence_score: float = Field(
        default=0.85,
        description="How confident we are (0-1)"
    )


# ============================================================================
# MAIN EXTRACTION CLASS
# ============================================================================

class GeminiMedicalExtractor:
    """
    Simple Gemini extractor for: Patient Name, Disease, ICD Code
    
    Usage:
        extractor = GeminiMedicalExtractor(api_key="YOUR_API_KEY")
        result = extractor.extract_from_file("document.pdf")
        print(result)
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize Gemini.
        
        Args:
            api_key: Your Gemini API key
                    Get it from: https://aistudio.google.com/
                    
        Example:
            # Option 1: Pass directly (for testing)
            extractor = GeminiMedicalExtractor(api_key="AIzaSy...")
            
            # Option 2: Use environment variable (RECOMMENDED)
            # Before running: export GEMINI_API_KEY="AIzaSy..."
            extractor = GeminiMedicalExtractor()
        """
        if api_key is None:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError(
                    "API key not found!\n"
                    "Either:\n"
                    "  1. Pass it: GeminiMedicalExtractor(api_key='YOUR_KEY')\n"
                    "  2. Set env: export GEMINI_API_KEY='YOUR_KEY'"
                )
        
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.0-flash"
        logger.info(f"✅ Gemini initialized with model: {self.model}")
    
    def extract_from_pdf(self, pdf_path: str) -> dict:
        """Extract from PDF file"""
        try:
            logger.info(f"📄 Processing PDF: {pdf_path}")
            
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"File not found: {pdf_path}")
            
            with open(pdf_path, 'rb') as f:
                pdf_data = f.read()
            
            prompt = """
            Extract from this medical document:
            1. Patient's name
            2. All diseases/diagnoses listed
            3. ICD-10 codes for each disease
            
            Return ONLY JSON. Example format:
            {
              "patient_name": "John Doe",
              "diseases": [
                {
                  "disease_name": "Type 2 Diabetes Mellitus",
                  "icd_codes": [
                    {"code": "E11.10", "description": "Type 2 diabetes mellitus with ketoacidosis without coma"}
                  ]
                }
              ]
            }
            """
            
            logger.info("🔄 Calling Gemini...")
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    types.Part.from_bytes(
                        data=pdf_data,
                        mime_type='application/pdf'
                    ),
                    prompt
                ],
                config={
                    "response_mime_type": "application/json",
                    "response_schema": PatientMedicalExtraction
                }
            )
            
            extracted_data = response.parsed
            result = extracted_data.model_dump()
            result['status'] = 'success'
            
            logger.info(f"✅ Extraction successful!")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e),
                'patient_name': None,
                'diseases': []
            }
    
    def extract_from_image(self, image_path: str) -> dict:
        """Extract from JPG or PNG"""
        try:
            logger.info(f"🖼️  Processing image: {image_path}")
            
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"File not found: {image_path}")
            
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            if image_path.lower().endswith('.png'):
                mime_type = 'image/png'
            elif image_path.lower().endswith(('.jpg', '.jpeg')):
                mime_type = 'image/jpeg'
            else:
                raise ValueError(f"Unsupported format: {image_path}")
            
            prompt = """
            Extract from this medical document image:
            1. Patient's name
            2. All diseases/diagnoses
            3. ICD-10 codes for each disease
            
            Return ONLY JSON.
            """
            
            logger.info("🔄 Calling Gemini...")
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    types.Part.from_bytes(
                        data=image_data,
                        mime_type=mime_type
                    ),
                    prompt
                ],
                config={
                    "response_mime_type": "application/json",
                    "response_schema": PatientMedicalExtraction
                }
            )
            
            extracted_data = response.parsed
            result = extracted_data.model_dump()
            result['status'] = 'success'
            
            logger.info(f"✅ Extraction successful!")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e),
                'patient_name': None,
                'diseases': []
            }
    
    def extract_from_file(self, file_path: str) -> dict:
        """Smart handler - detects file type automatically"""
        if file_path.lower().endswith('.pdf'):
            return self.extract_from_pdf(file_path)
        elif file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
            return self.extract_from_image(file_path)
        else:
            return {
                'status': 'failed',
                'error': f'Unsupported file type. Use PDF, JPG, or PNG',
                'patient_name': None,
                'diseases': []
            }


# ============================================================================
# TEST YOUR MODULE
# ============================================================================

if __name__ == "__main__":
    """
    Test your extraction.
    
    BEFORE RUNNING:
    1. pip install google-genai pydantic
    2. Get API key from https://aistudio.google.com/
    3. export GEMINI_API_KEY="your_key_here"
    4. Place a test PDF: test_document.pdf
    5. python gemini_extractor.py
    """
    
    try:
        # Initialize
        extractor = GeminiMedicalExtractor()
        
        # Test with sample
        test_file = "test_document.pdf"  # Replace with your test file
        
        print("\n" + "="*60)
        print("MEDICAL DOCUMENT EXTRACTION")
        print("="*60 + "\n")
        
        result = extractor.extract_from_file(test_file)
        
        # Pretty print
        print(json.dumps(result, indent=2))
        
        # Print summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Status: {result.get('status')}")
        print(f"Patient: {result.get('patient_name')}")
        print(f"Diseases: {len(result.get('diseases', []))}")
        
        for disease in result.get('diseases', []):
            print(f"\n✓ {disease.get('disease_name')}")
            for icd in disease.get('icd_codes', []):
                print(f"  - {icd.get('code')}: {icd.get('description')}")
        
        print("\n")
        
    except Exception as e:
        print(f"Error: {e}")
