"""
CRUD Operations Module
======================
Create, Read, Update, Delete operations for clinic database tables
"""

from typing import Optional, List, Dict
from datetime import date
from db_connection import (
    create_connection, close_connection,
    execute_insert_query, execute_select_query, execute_query
)
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# DOCTOR OPERATIONS
# =============================================================================

def insert_doctor(doctor_id: int, name: str, phone: str, email: str) -> bool:
    """Insert a new doctor"""
    connection = create_connection()
    if not connection:
        return False

    query = """
            INSERT INTO doctor (doctor_id, doctor_name, doctor_phone, doctor_email)
            VALUES (%s, %s, %s, %s) \
            """
    result = execute_query(connection, query, (doctor_id, name, phone, email))
    close_connection(connection)
    return result


def get_doctor_by_id(doctor_id: int) -> Optional[Dict]:
    """Get doctor details by ID"""
    connection = create_connection()
    if not connection:
        return None

    query = "SELECT * FROM doctor WHERE doctor_id = %s"
    results = execute_select_query(connection, query, (doctor_id,))
    close_connection(connection)
    return results[0] if results else None


def get_all_doctors() -> List[Dict]:
    """Get all doctors"""
    connection = create_connection()
    if not connection:
        return []

    query = "SELECT * FROM doctor ORDER BY doctor_name"
    results = execute_select_query(connection, query)
    close_connection(connection)
    return results


def update_doctor(doctor_id: int, name: str = None, phone: str = None, email: str = None) -> bool:
    """Update doctor details"""
    connection = create_connection()
    if not connection:
        return False

    updates = []
    params = []

    if name:
        updates.append("doctor_name = %s")
        params.append(name)
    if phone:
        updates.append("doctor_phone = %s")
        params.append(phone)
    if email:
        updates.append("doctor_email = %s")
        params.append(email)

    if not updates:
        close_connection(connection)
        return False

    params.append(doctor_id)
    query = f"UPDATE doctor SET {', '.join(updates)} WHERE doctor_id = %s"
    result = execute_query(connection, query, tuple(params))
    close_connection(connection)
    return result


def delete_doctor(doctor_id: int) -> bool:
    """Delete a doctor"""
    connection = create_connection()
    if not connection:
        return False

    query = "DELETE FROM doctor WHERE doctor_id = %s"
    result = execute_query(connection, query, (doctor_id,))
    close_connection(connection)
    return result


# =============================================================================
# PATIENT OPERATIONS
# =============================================================================

def insert_patient(name: str, phone: str, email: str, address: str, date_added: date = None) -> Optional[int]:
    """Insert a new patient"""
    connection = create_connection()
    if not connection:
        return None

    if date_added is None:
        date_added = date.today()

    query = """
            INSERT INTO patient
            (patient_name, patient_phone, patient_email, patient_address, date_added)
            VALUES (%s, %s, %s, %s, %s) \
            """
    patient_id = execute_insert_query(connection, query, (name, phone, email, address, date_added))
    close_connection(connection)
    return patient_id


def get_patient_by_id(patient_id: int) -> Optional[Dict]:
    """Get patient details by ID"""
    connection = create_connection()
    if not connection:
        return None

    query = "SELECT * FROM patient WHERE patient_id = %s"
    results = execute_select_query(connection, query, (patient_id,))
    close_connection(connection)
    return results[0] if results else None


def get_all_patients() -> List[Dict]:
    """Get all patients"""
    connection = create_connection()
    if not connection:
        return []

    query = "SELECT * FROM patient ORDER BY date_added DESC"
    results = execute_select_query(connection, query)
    close_connection(connection)
    return results


def search_patients(search_term: str) -> List[Dict]:
    """Search patients by name, phone, or email"""
    connection = create_connection()
    if not connection:
        return []

    query = """
            SELECT * \
            FROM patient
            WHERE patient_name LIKE %s \
               OR patient_phone LIKE %s \
               OR patient_email LIKE %s
            ORDER BY patient_name \
            """
    search_pattern = f"%{search_term}%"
    results = execute_select_query(connection, query, (search_pattern, search_pattern, search_pattern))
    close_connection(connection)
    return results


def update_patient(patient_id: int, name: str = None, phone: str = None,
                   email: str = None, address: str = None) -> bool:
    """Update patient details"""
    connection = create_connection()
    if not connection:
        return False

    updates = []
    params = []

    if name:
        updates.append("patient_name = %s")
        params.append(name)
    if phone:
        updates.append("patient_phone = %s")
        params.append(phone)
    if email:
        updates.append("patient_email = %s")
        params.append(email)
    if address:
        updates.append("patient_address = %s")
        params.append(address)

    if not updates:
        close_connection(connection)
        return False

    params.append(patient_id)
    query = f"UPDATE patient SET {', '.join(updates)} WHERE patient_id = %s"
    result = execute_query(connection, query, tuple(params))
    close_connection(connection)
    return result


def delete_patient(patient_id: int) -> bool:
    """Delete a patient"""
    connection = create_connection()
    if not connection:
        return False

    query = "DELETE FROM patient WHERE patient_id = %s"
    result = execute_query(connection, query, (patient_id,))
    close_connection(connection)
    return result


# =============================================================================
# APPOINTMENT OPERATIONS
# =============================================================================

def create_appointment(appointment_date: date, patient_id: int, doctor_id: int) -> Optional[int]:
    """Create a new appointment"""
    connection = create_connection()
    if not connection:
        return None

    query = """
            INSERT INTO appointment (appointment_date, patient_id, doctor_id)
            VALUES (%s, %s, %s) \
            """
    appointment_id = execute_insert_query(connection, query, (appointment_date, patient_id, doctor_id))
    close_connection(connection)
    return appointment_id


def get_appointment_by_id(appointment_id: int) -> Optional[Dict]:
    """Get appointment details with patient and doctor info"""
    connection = create_connection()
    if not connection:
        return None

    query = """
            SELECT a.*,
                   p.patient_name, \
                   p.patient_phone,
                   d.doctor_name, \
                   d.doctor_phone
            FROM appointment a
                     JOIN patient p ON a.patient_id = p.patient_id
                     JOIN doctor d ON a.doctor_id = d.doctor_id
            WHERE a.appointment_id = %s \
            """
    results = execute_select_query(connection, query, (appointment_id,))
    close_connection(connection)
    return results[0] if results else None


def get_appointments_by_patient(patient_id: int) -> List[Dict]:
    """Get all appointments for a patient"""
    connection = create_connection()
    if not connection:
        return []

    query = """
            SELECT a.*, d.doctor_name, d.doctor_phone
            FROM appointment a
                     JOIN doctor d ON a.doctor_id = d.doctor_id
            WHERE a.patient_id = %s
            ORDER BY a.appointment_date DESC \
            """
    results = execute_select_query(connection, query, (patient_id,))
    close_connection(connection)
    return results


def get_appointments_by_doctor(doctor_id: int) -> List[Dict]:
    """Get all appointments for a doctor"""
    connection = create_connection()
    if not connection:
        return []

    query = """
            SELECT a.*, p.patient_name, p.patient_phone, p.patient_email
            FROM appointment a
                     JOIN patient p ON a.patient_id = p.patient_id
            WHERE a.doctor_id = %s
            ORDER BY a.appointment_date DESC \
            """
    results = execute_select_query(connection, query, (doctor_id,))
    close_connection(connection)
    return results


def get_appointments_by_date(appointment_date: date) -> List[Dict]:
    """Get all appointments for a specific date"""
    connection = create_connection()
    if not connection:
        return []

    query = """
            SELECT a.*,
                   p.patient_name, \
                   p.patient_phone,
                   d.doctor_name
            FROM appointment a
                     JOIN patient p ON a.patient_id = p.patient_id
                     JOIN doctor d ON a.doctor_id = d.doctor_id
            WHERE a.appointment_date = %s
            ORDER BY a.appointment_id \
            """
    results = execute_select_query(connection, query, (appointment_date,))
    close_connection(connection)
    return results


def delete_appointment(appointment_id: int) -> bool:
    """Delete an appointment"""
    connection = create_connection()
    if not connection:
        return False

    query = "DELETE FROM appointment WHERE appointment_id = %s"
    result = execute_query(connection, query, (appointment_id,))
    close_connection(connection)
    return result


# =============================================================================
# MEDICINE OPERATIONS
# =============================================================================

def insert_medicine(medicine_id: int, medicine_name: str) -> bool:
    """Insert a new medicine"""
    connection = create_connection()
    if not connection:
        return False

    query = "INSERT INTO medicine (medicine_id, medicine_name) VALUES (%s, %s)"
    result = execute_query(connection, query, (medicine_id, medicine_name))
    close_connection(connection)
    return result


def get_medicine_by_id(medicine_id: int) -> Optional[Dict]:
    """Get medicine details by ID"""
    connection = create_connection()
    if not connection:
        return None

    query = "SELECT * FROM medicine WHERE medicine_id = %s"
    results = execute_select_query(connection, query, (medicine_id,))
    close_connection(connection)
    return results[0] if results else None


def get_all_medicines() -> List[Dict]:
    """Get all medicines"""
    connection = create_connection()
    if not connection:
        return []

    query = "SELECT * FROM medicine ORDER BY medicine_name"
    results = execute_select_query(connection, query)
    close_connection(connection)
    return results


def delete_medicine(medicine_id: int) -> bool:
    """Delete a medicine"""
    connection = create_connection()
    if not connection:
        return False

    query = "DELETE FROM medicine WHERE medicine_id = %s"
    result = execute_query(connection, query, (medicine_id,))
    close_connection(connection)
    return result


# =============================================================================
# APPOINTMENT-MEDICINE OPERATIONS
# =============================================================================

def add_medicine_to_appointment(appointment_id: int, medicine_id: int) -> bool:
    """Add medicine to an appointment"""
    connection = create_connection()
    if not connection:
        return False

    query = """
            INSERT INTO appointment_medicine (appointment_id, medicine_id)
            VALUES (%s, %s) \
            """
    result = execute_query(connection, query, (appointment_id, medicine_id))
    close_connection(connection)
    return result


def get_medicines_for_appointment(appointment_id: int) -> List[Dict]:
    """Get all medicines prescribed in an appointment"""
    connection = create_connection()
    if not connection:
        return []

    query = """
            SELECT m.*
            FROM medicine m
                     JOIN appointment_medicine am ON m.medicine_id = am.medicine_id
            WHERE am.appointment_id = %s \
            """
    results = execute_select_query(connection, query, (appointment_id,))
    close_connection(connection)
    return results


def remove_medicine_from_appointment(appointment_id: int, medicine_id: int) -> bool:
    """Remove medicine from an appointment"""
    connection = create_connection()
    if not connection:
        return False

    query = """
            DELETE \
            FROM appointment_medicine
            WHERE appointment_id = %s \
              AND medicine_id = %s \
            """
    result = execute_query(connection, query, (appointment_id, medicine_id))
    close_connection(connection)
    return result


if __name__ == "__main__":
    print("\nTesting CRUD Operations...\n")

    # Test operations
    doctors = get_all_doctors()
    print(f"Total doctors: {len(doctors)}")

    patients = get_all_patients()
    print(f"Total patients: {len(patients)}")

    print("\n✅ CRUD operations working!")
