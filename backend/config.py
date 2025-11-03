"""
Backend Configuration
======================
Configuration settings for FastAPI backend server
"""

import os
from typing import Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# SERVER CONFIGURATION
# ============================================================================

SERVER_CONFIG: Dict[str, any] = {
    'host': os.getenv('SERVER_HOST', '0.0.0.0'),
    'port': int(os.getenv('SERVER_PORT', 8000)),
    'reload': os.getenv('SERVER_RELOAD', 'true').lower() == 'true',
    'debug': os.getenv('DEBUG', 'false').lower() == 'true',
}

# ============================================================================
# FILE UPLOAD SETTINGS
# ============================================================================

UPLOAD_CONFIG: Dict[str, any] = {
    'upload_dir': os.getenv('UPLOAD_DIR', 'uploads'),
    'max_file_size': int(os.getenv('MAX_FILE_SIZE', 10 * 1024 * 1024)),  # 10MB default
    'allowed_extensions': ['.pdf', '.jpg', '.jpeg', '.png'],
    'allowed_mime_types': [
        'application/pdf',
        'image/jpeg',
        'image/jpg',
        'image/png'
    ]
}

# ============================================================================
# CORS SETTINGS
# ============================================================================

CORS_CONFIG: Dict[str, any] = {
    'allow_origins': os.getenv('CORS_ORIGINS', '*').split(','),
    'allow_credentials': True,
    'allow_methods': ['*'],
    'allow_headers': ['*'],
}

# ============================================================================
# API KEYS
# ============================================================================

API_KEYS: Dict[str, str] = {
    'gemini': os.getenv('GEMINI_API_KEY', ''),
}

# ============================================================================
# DATABASE SETTINGS (Import from db/config.py)
# ============================================================================

# Database config is handled by db/config.py
# This file only handles backend-specific settings

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOGGING_CONFIG: Dict[str, any] = {
    'level': os.getenv('LOG_LEVEL', 'INFO'),
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'datefmt': '%Y-%m-%d %H:%M:%S',
}

# ============================================================================
# APPLICATION METADATA
# ============================================================================

APP_METADATA: Dict[str, str] = {
    'title': 'EMR Digitization API',
    'description': 'Backend API for Electronic Medical Records digitization and extraction',
    'version': '1.0.0',
    'contact': {
        'name': 'EMR Team',
        'email': 'team@emr.local',
    }
}

# ============================================================================
# VALIDATION
# ============================================================================

def validate_config():
    """Validate critical configuration settings"""
    issues = []
    
    # Check Gemini API key
    if not API_KEYS['gemini']:
        issues.append("⚠️  GEMINI_API_KEY not set - extraction will not work")
    
    # Check upload directory
    upload_dir = UPLOAD_CONFIG['upload_dir']
    if not os.path.exists(upload_dir):
        try:
            os.makedirs(upload_dir)
            print(f"✅ Created upload directory: {upload_dir}")
        except Exception as e:
            issues.append(f"❌ Cannot create upload directory: {e}")
    
    return issues

def print_config():
    """Print current configuration (without sensitive data)"""
    print("\n" + "="*60)
    print("BACKEND CONFIGURATION")
    print("="*60)
    
    print("\n📡 Server Settings:")
    for key, value in SERVER_CONFIG.items():
        print(f"   {key:15}: {value}")
    
    print("\n📤 Upload Settings:")
    print(f"   upload_dir     : {UPLOAD_CONFIG['upload_dir']}")
    print(f"   max_file_size  : {UPLOAD_CONFIG['max_file_size'] / (1024*1024):.1f}MB")
    print(f"   allowed_types  : {', '.join(UPLOAD_CONFIG['allowed_extensions'])}")
    
    print("\n🔑 API Keys:")
    gemini_key = API_KEYS['gemini']
    if gemini_key:
        masked_key = gemini_key[:8] + "..." + gemini_key[-4:]
        print(f"   gemini         : {masked_key}")
    else:
        print(f"   gemini         : ❌ NOT SET")
    
    print("\n🌐 CORS:")
    print(f"   origins        : {CORS_CONFIG['allow_origins']}")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    print_config()
    
    issues = validate_config()
    if issues:
        print("\n⚠️  Configuration Issues:")
        for issue in issues:
            print(f"   {issue}")
        print()