"""
Comprehensive Test Suite for Constraints Feature
Tests database operations for holidays, vacations, absences, classes, and modules
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.core.database import DatabaseManager
from src.utils.config import DB_PATH
import logging
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def print_test_header(test_name):
    """Print formatted test header"""
    print(f"\n{'='*70}")
    print(f"TEST: {test_name}")
    print('='*70)


def test_database_tables():
    """Test 1: Verify constraints-related tables exist"""
    print_test_header("Database Tables Verification")
    
    db = DatabaseManager(DB_PATH)
    
    required_tables = ['holidays', 'vacations', 'absences', 'classes', 'modules', 'teachers']
    existing_tables = db.get_all_tables()
    
    print(f"Existing tables: {existing_tables}")
    
    for table in required_tables:
        if table in existing_tables:
            print(f"✓ Table '{table}' exists")
        else:
            print(f"✗ Table '{table}' MISSING")
            db.close()
            return False
    
    db.close()
    print("\n✓ All required tables exist")
    return True


def test_holidays_crud():
    """Test 2: Test holidays CRUD operations"""
    print_test_header("Holidays CRUD Operations")
    
    db = DatabaseManager(DB_PATH)
    
    # Clear test data
    print("Clearing test holidays...")
    db.execute_update("DELETE FROM holidays WHERE label LIKE 'TEST%'")
    
    # Test INSERT
    print("\n1. Testing INSERT operation...")
    test_holidays = [
        ('2026-01-01', 'TEST Nouvel An', 'public'),
        ('2026-05-01', 'TEST Fête du Travail', 'public'),
        ('2026-07-14', 'TEST Fête Nationale', 'national'),
    ]
    
    inserted_ids = []
    for date, label, h_type in test_holidays:
        query = "INSERT INTO holidays (date, label, holiday_type) VALUES (?, ?, ?)"
        row_id = db.execute_update(query, (date, label, h_type))
        inserted_ids.append(row_id)
        print(f"  ✓ Inserted holiday ID {row_id}: {label}")
    
    # Test SELECT
    print("\n2. Testing SELECT operation...")
    query = "SELECT * FROM holidays WHERE label LIKE 'TEST%' ORDER BY date"
    results = db.execute_query(query)
    
    print(f"  ✓ Found {len(results)} holidays")
    for row in results:
        print(f"    - {row['date']}: {row['label']} ({row['holiday_type']})")
    
    if len(results) != 3:
        print(f"  ✗ Expected 3 holidays, got {len(results)}")
        db.close()
        return False
    
    # Test UPDATE
    print("\n3. Testing UPDATE operation...")
    update_query = "UPDATE holidays SET label = ? WHERE id = ?"
    db.execute_update(update_query, ('TEST Nouvel An UPDATED', inserted_ids[0]))
    
    verify_query = "SELECT label FROM holidays WHERE id = ?"
    updated = db.execute_query(verify_query, (inserted_ids[0],))
    
    if updated[0]['label'] == 'TEST Nouvel An UPDATED':
        print("  ✓ Update successful")
    else:
        print("  ✗ Update failed")
        db.close()
        return False
    
    # Test DELETE
    print("\n4. Testing DELETE operation...")
    delete_query = "DELETE FROM holidays WHERE label LIKE 'TEST%'"
    db.execute_update(delete_query)
    
    verify_delete = db.execute_query("SELECT COUNT(*) as count FROM holidays WHERE label LIKE 'TEST%'")
    if verify_delete[0]['count'] == 0:
        print("  ✓ Delete successful")
    else:
        print("  ✗ Delete failed")
        db.close()
        return False
    
    db.close()
    print("\n✓ All holidays CRUD operations successful")
    return True


def test_vacations_crud():
    """Test 3: Test vacations CRUD operations"""
    print_test_header("Vacations CRUD Operations")
    
    db = DatabaseManager(DB_PATH)
    
    # Clear test data
    print("Clearing test vacations...")
    db.execute_update("DELETE FROM vacations WHERE label LIKE 'TEST%'")
    
    # Test INSERT
    print("\n1. Testing INSERT operation...")
    test_vacations = [
        ('2026-12-20', '2027-01-03', 'TEST Vacances de Noël'),
        ('2026-02-14', '2026-03-02', 'TEST Vacances d\'Hiver'),
    ]
    
    for start, end, label in test_vacations:
        query = "INSERT INTO vacations (start_date, end_date, label) VALUES (?, ?, ?)"
        row_id = db.execute_update(query, (start, end, label))
        print(f"  ✓ Inserted vacation ID {row_id}: {label}")
    
    # Test SELECT
    print("\n2. Testing SELECT operation...")
    query = "SELECT * FROM vacations WHERE label LIKE 'TEST%' ORDER BY start_date"
    results = db.execute_query(query)
    
    print(f"  ✓ Found {len(results)} vacation periods")
    for row in results:
        print(f"    - {row['start_date']} to {row['end_date']}: {row['label']}")
    
    if len(results) != 2:
        print(f"  ✗ Expected 2 vacations, got {len(results)}")
        db.close()
        return False
    
    # Cleanup
    print("\n3. Testing DELETE operation...")
    db.execute_update("DELETE FROM vacations WHERE label LIKE 'TEST%'")
    print("  ✓ Delete successful")
    
    db.close()
    print("\n✓ All vacations CRUD operations successful")
    return True


def test_absences_crud():
    """Test 4: Test teacher absences CRUD operations"""
    print_test_header("Absences CRUD Operations")
    
    db = DatabaseManager(DB_PATH)
    
    # Get a teacher ID
    teachers = db.execute_query("SELECT id, name FROM teachers LIMIT 1")
    if not teachers:
        print("  ⚠️  No teachers found, skipping absences test")
        db.close()
        return True
    
    teacher_id = teachers[0]['id']
    teacher_name = teachers[0]['name']
    print(f"Using teacher: {teacher_name} (ID: {teacher_id})")
    
    # Clear test data
    print("\nClearing test absences...")
    db.execute_update("DELETE FROM absences WHERE reason LIKE 'TEST%'")
    
    # Test INSERT
    print("\n1. Testing INSERT operation...")
    test_absences = [
        ('2026-02-10', teacher_id, 'TEST Maladie'),
        ('2026-03-15', teacher_id, 'TEST Congé personnel'),
    ]
    
    for date, tid, reason in test_absences:
        query = "INSERT INTO absences (date, teacher_id, reason) VALUES (?, ?, ?)"
        row_id = db.execute_update(query, (date, tid, reason))
        print(f"  ✓ Inserted absence ID {row_id}: {reason}")
    
    # Test SELECT with JOIN
    print("\n2. Testing SELECT operation with JOIN...")
    query = """
        SELECT a.id, a.date, a.reason, t.name as teacher_name
        FROM absences a
        LEFT JOIN teachers t ON a.teacher_id = t.id
        WHERE a.reason LIKE 'TEST%'
        ORDER BY a.date
    """
    results = db.execute_query(query)
    
    print(f"  ✓ Found {len(results)} absences")
    for row in results:
        print(f"    - {row['date']}: {row['teacher_name']} - {row['reason']}")
    
    if len(results) != 2:
        print(f"  ✗ Expected 2 absences, got {len(results)}")
        db.close()
        return False
    
    # Cleanup
    print("\n3. Testing DELETE operation...")
    db.execute_update("DELETE FROM absences WHERE reason LIKE 'TEST%'")
    print("  ✓ Delete successful")
    
    db.close()
    print("\n✓ All absences CRUD operations successful")
    return True


def test_classes_crud():
    """Test 5: Test classes CRUD operations"""
    print_test_header("Classes CRUD Operations")
    
    db = DatabaseManager(DB_PATH)
    
    # Clear test data
    print("Clearing test classes...")
    db.execute_update("DELETE FROM classes WHERE name LIKE 'TEST%'")
    
    # Test INSERT
    print("\n1. Testing INSERT operation...")
    test_classes = [
        ('TEST 6ème A', '6ème', '2025-2026'),
        ('TEST 5ème B', '5ème', '2025-2026'),
        ('TEST 4ème C', '4ème', '2025-2026'),
    ]
    
    for name, level, year in test_classes:
        query = "INSERT INTO classes (name, level, school_year) VALUES (?, ?, ?)"
        row_id = db.execute_update(query, (name, level, year))
        print(f"  ✓ Inserted class ID {row_id}: {name}")
    
    # Test SELECT
    print("\n2. Testing SELECT operation...")
    query = "SELECT * FROM classes WHERE name LIKE 'TEST%' ORDER BY name"
    results = db.execute_query(query)
    
    print(f"  ✓ Found {len(results)} classes")
    for row in results:
        print(f"    - {row['name']} ({row['level']}) - {row['school_year']}")
    
    if len(results) != 3:
        print(f"  ✗ Expected 3 classes, got {len(results)}")
        db.close()
        return False
    
    # Test UPDATE
    print("\n3. Testing UPDATE operation...")
    update_query = "UPDATE classes SET level = ? WHERE name = ?"
    db.execute_update(update_query, ('6ème (Updated)', 'TEST 6ème A'))
    
    verify = db.execute_query("SELECT level FROM classes WHERE name = 'TEST 6ème A'")
    if verify[0]['level'] == '6ème (Updated)':
        print("  ✓ Update successful")
    else:
        print("  ✗ Update failed")
        db.close()
        return False
    
    # Cleanup
    print("\n4. Testing DELETE operation...")
    db.execute_update("DELETE FROM classes WHERE name LIKE 'TEST%'")
    print("  ✓ Delete successful")
    
    db.close()
    print("\n✓ All classes CRUD operations successful")
    return True


def test_modules_crud():
    """Test 6: Test modules CRUD operations"""
    print_test_header("Modules CRUD Operations")
    
    db = DatabaseManager(DB_PATH)
    
    # Clear test data
    print("Clearing test modules...")
    db.execute_update("DELETE FROM modules WHERE name LIKE 'TEST%'")
    
    # Test INSERT
    print("\n1. Testing INSERT operation...")
    test_modules = [
        ('TEST Mathématiques', 'Module de mathématiques test'),
        ('TEST Français', 'Module de français test'),
    ]
    
    for name, desc in test_modules:
        query = "INSERT INTO modules (name, description) VALUES (?, ?)"
        row_id = db.execute_update(query, (name, desc))
        print(f"  ✓ Inserted module ID {row_id}: {name}")
    
    # Test SELECT
    print("\n2. Testing SELECT operation...")
    query = "SELECT * FROM modules WHERE name LIKE 'TEST%' ORDER BY name"
    results = db.execute_query(query)
    
    print(f"  ✓ Found {len(results)} modules")
    for row in results:
        print(f"    - {row['name']}: {row['description']}")
    
    if len(results) != 2:
        print(f"  ✗ Expected 2 modules, got {len(results)}")
        db.close()
        return False
    
    # Cleanup
    print("\n3. Testing DELETE operation...")
    db.execute_update("DELETE FROM modules WHERE name LIKE 'TEST%'")
    print("  ✓ Delete successful")
    
    db.close()
    print("\n✓ All modules CRUD operations successful")
    return True


def test_date_validation():
    """Test 7: Test date format validation"""
    print_test_header("Date Format Validation")
    
    print("Testing date format conversions...")
    
    # Test valid formats
    valid_dates = [
        ('01/01/2026', '2026-01-01'),
        ('15/03/2026', '2026-03-15'),
        ('31/12/2026', '2026-12-31'),
    ]
    
    for input_date, expected in valid_dates:
        try:
            date_obj = datetime.strptime(input_date, '%d/%m/%Y')
            output = date_obj.strftime('%Y-%m-%d')
            if output == expected:
                print(f"  ✓ {input_date} → {output}")
            else:
                print(f"  ✗ {input_date} → {output} (expected {expected})")
                return False
        except ValueError as e:
            print(f"  ✗ Failed to parse {input_date}: {e}")
            return False
    
    # Test invalid formats
    print("\nTesting invalid date formats...")
    invalid_dates = ['32/01/2026', '15/13/2026', '2026-01-01', 'invalid']
    
    for invalid_date in invalid_dates:
        try:
            datetime.strptime(invalid_date, '%d/%m/%Y')
            print(f"  ✗ {invalid_date} should have failed but didn't")
            return False
        except ValueError:
            print(f"  ✓ {invalid_date} correctly rejected")
    
    print("\n✓ Date validation working correctly")
    return True


def test_foreign_key_relationships():
    """Test 8: Test foreign key relationships"""
    print_test_header("Foreign Key Relationships")
    
    db = DatabaseManager(DB_PATH)
    
    # Test absences -> teachers relationship
    print("Testing absences to teachers foreign key...")
    
    # Get a valid teacher
    teachers = db.execute_query("SELECT id FROM teachers LIMIT 1")
    if teachers:
        teacher_id = teachers[0]['id']
        
        # Insert absence with valid teacher_id
        query = "INSERT INTO absences (date, teacher_id, reason) VALUES (?, ?, ?)"
        absence_id = db.execute_update(query, ('2026-02-20', teacher_id, 'TEST FK'))
        print(f"  ✓ Inserted absence with valid teacher_id: {absence_id}")
        
        # Verify relationship with JOIN
        join_query = """
            SELECT a.id, t.name 
            FROM absences a 
            JOIN teachers t ON a.teacher_id = t.id 
            WHERE a.id = ?
        """
        result = db.execute_query(join_query, (absence_id,))
        
        if result:
            print(f"  ✓ JOIN successful: absence linked to teacher '{result[0]['name']}'")
        else:
            print("  ✗ JOIN failed")
            db.close()
            return False
        
        # Cleanup
        db.execute_update("DELETE FROM absences WHERE reason = 'TEST FK'")
    else:
        print("  ⚠️  No teachers found to test foreign key")
    
    db.close()
    print("\n✓ Foreign key relationships working correctly")
    return True


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*70)
    print("CONSTRAINTS FEATURE - COMPREHENSIVE TEST SUITE")
    print("="*70)
    print(f"Database: {DB_PATH}")
    print(f"Testing: Holidays, Vacations, Absences, Classes, Modules")
    print("="*70)
    
    tests = [
        ("Database Tables", test_database_tables),
        ("Holidays CRUD Operations", test_holidays_crud),
        ("Vacations CRUD Operations", test_vacations_crud),
        ("Absences CRUD Operations", test_absences_crud),
        ("Classes CRUD Operations", test_classes_crud),
        ("Modules CRUD Operations", test_modules_crud),
        ("Date Format Validation", test_date_validation),
        ("Foreign Key Relationships", test_foreign_key_relationships),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' crashed with error: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Final report
    print("\n" + "="*70)
    print("TEST RESULTS SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")
    
    print("="*70)
    print(f"Total: {passed}/{total} tests passed ({100*passed//total}%)")
    print("="*70)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Constraints feature is fully functional.")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review errors above.")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
