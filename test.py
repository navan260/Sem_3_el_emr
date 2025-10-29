"""
Test Module - Demonstrates All Database Operations
"""

from datetime import date
from crud_operations import *
from db_connection import test_connection, run_diagnostics


def test_all_operations():
    """Test all database operations"""
    print("\n" + "=" * 70)
    print("CLINIC DATABASE - TEST SUITE")
    print("=" * 70)

    # Test connection
    print("\n📡 Testing database connection...")
    if not test_connection():
        print("\n❌ Connection failed!")
        print("\nSteps to fix:")
        print("1. Edit config.py with correct database credentials")
        print("2. Ensure MySQL/Railway is running")
        print("3. Ensure database 'clinic' exists")
        return

    print("\n✅ Connection successful!\n")

    # Run diagnostics
    run_diagnostics()

    # Test doctor operations
    print("\n" + "=" * 70)
    print("TESTING DOCTOR OPERATIONS")
    print("=" * 70)

    doctors = get_all_doctors()
    print(f"\n✅ Found {len(doctors)} doctors")
    for doc in doctors:
        print(f"   - Dr. {doc['doctor_name']} (ID: {doc['doctor_id']})")

    # Test patient operations
    print("\n" + "=" * 70)
    print("TESTING PATIENT OPERATIONS")
    print("=" * 70)

    patients = get_all_patients()
    print(f"\n✅ Found {len(patients)} patients")
    for patient in patients[:5]:
        print(f"   - {patient['patient_name']} (ID: {patient['patient_id']})")

    # Test appointment operations
    print("\n" + "=" * 70)
    print("TESTING APPOINTMENT OPERATIONS")
    print("=" * 70)

    appointments = get_appointments_by_date(date.today())
    print(f"\n✅ Found {len(appointments)} appointments for today")

    # Test medicine operations
    print("\n" + "=" * 70)
    print("TESTING MEDICINE OPERATIONS")
    print("=" * 70)

    medicines = get_all_medicines()
    print(f"\n✅ Found {len(medicines)} medicines")

    print("\n" + "=" * 70)
    print("✅ ALL TESTS COMPLETED!")
    print("=" * 70)
    print("\nYour database is ready to use!")
    print("Share this code with your teammates via GitHub.\n")


if __name__ == "__main__":
    test_all_operations()
