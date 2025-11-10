"""
Patient CRUD Operations for Supabase
=====================================
"""

from supabase_config import get_supabase_client
from datetime import date
from typing import List, Dict, Optional

# Get Supabase client
supabase = get_supabase_client()


# =============================================================================
# PATIENT OPERATIONS
# =============================================================================

def insert_patient(name: str, phone: str, email: str, address: str,
                  disease_id: str, disease_name: str, 
                  date_added: date = None) -> Optional[Dict]:
    """
    Insert a new patient
    
    Args:
        name: Patient name
        phone: Phone number
        email: Email address
        address: Address
        disease_id: Disease ID
        disease_name: Disease name
        date_added: Date added (default: today)
    
    Returns:
        Inserted patient data or None if error
    """
    if date_added is None:
        date_added = date.today()
    
    try:
        data = {
            'patient_name': name,
            'patient_phone': phone,
            'patient_email': email,
            'patient_address': address,
            'disease_id': disease_id,
            'disease_name': disease_name,
            'date_added': str(date_added)
        }
        
        response = supabase.table('patient').insert(data).execute()
        print(f"✅ Patient inserted: {name}")
        return response.data[0] if response.data else None
        
    except Exception as e:
        print(f"❌ Error inserting patient: {e}")
        return None


def get_patient_by_id(patient_id: int) -> Optional[Dict]:
    """
    Get patient by ID
    
    Args:
        patient_id: Patient ID
    
    Returns:
        Patient data or None
    """
    try:
        response = supabase.table('patient').select('*').eq('patient_id', patient_id).execute()
        return response.data[0] if response.data else None
        
    except Exception as e:
        print(f"❌ Error getting patient: {e}")
        return None


def get_all_patients() -> List[Dict]:
    """
    Get all patients
    
    Returns:
        List of all patients
    """
    try:
        response = supabase.table('patient').select('*').order('date_added', desc=True).execute()
        return response.data
        
    except Exception as e:
        print(f"❌ Error getting patients: {e}")
        return []


def search_patients(search_term: str) -> List[Dict]:
    """
    Search patients by name, phone, or email
    
    Args:
        search_term: Search term
    
    Returns:
        List of matching patients
    """
    try:
        response = supabase.table('patient').select('*').or_(
            f'patient_name.ilike.%{search_term}%,'
            f'patient_phone.ilike.%{search_term}%,'
            f'patient_email.ilike.%{search_term}%'
        ).execute()
        return response.data
        
    except Exception as e:
        print(f"❌ Error searching patients: {e}")
        return []


def search_patients_by_disease(disease_name: str) -> List[Dict]:
    """
    Search patients by disease name
    
    Args:
        disease_name: Disease name to search
    
    Returns:
        List of patients with that disease
    """
    try:
        response = supabase.table('patient').select('*').ilike(
            'disease_name', f'%{disease_name}%'
        ).execute()
        return response.data
        
    except Exception as e:
        print(f"❌ Error searching by disease: {e}")
        return []


def update_patient(patient_id: int, name: str = None, phone: str = None,
                  email: str = None, address: str = None,
                  disease_id: str = None, disease_name: str = None) -> bool:
    """
    Update patient details
    
    Args:
        patient_id: Patient ID
        name: New name (optional)
        phone: New phone (optional)
        email: New email (optional)
        address: New address (optional)
        disease_id: New disease ID (optional)
        disease_name: New disease name (optional)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        updates = {}
        
        if name:
            updates['patient_name'] = name
        if phone:
            updates['patient_phone'] = phone
        if email:
            updates['patient_email'] = email
        if address:
            updates['patient_address'] = address
        if disease_id:
            updates['disease_id'] = disease_id
        if disease_name:
            updates['disease_name'] = disease_name
        
        if not updates:
            print("⚠️  No fields to update")
            return False
        
        response = supabase.table('patient').update(updates).eq('patient_id', patient_id).execute()
        print(f"✅ Patient updated: ID {patient_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating patient: {e}")
        return False


def delete_patient(patient_id: int) -> bool:
    """
    Delete a patient
    
    Args:
        patient_id: Patient ID
    
    Returns:
        True if successful, False otherwise
    """
    try:
        response = supabase.table('patient').delete().eq('patient_id', patient_id).execute()
        print(f"✅ Patient deleted: ID {patient_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error deleting patient: {e}")
        return False


def get_patient_count() -> int:
    """Get total number of patients"""
    try:
        response = supabase.table('patient').select('patient_id', count='exact').execute()
        return response.count if hasattr(response, 'count') else len(response.data)
        
    except Exception as e:
        print(f"❌ Error getting count: {e}")
        return 0


