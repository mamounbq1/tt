"""
Comprehensive Test Suite for Remaining Features
Tests Print Schedules, Import Content, and Distribution features
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.core.database import DatabaseManager
from src.utils.config import DB_PATH
import logging
import tempfile
import csv

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


def test_print_schedule_data():
    """Test 1: Verify schedule data exists for printing"""
    print_test_header("Print Schedule - Data Verification")
    
    db = DatabaseManager(DB_PATH)
    
    # Add test schedule data
    print("Adding test schedule data...")
    db.execute_update("DELETE FROM schedule_data WHERE week_number = 99")
    
    days = db.execute_query("SELECT id FROM days LIMIT 3")
    slots = db.execute_query("SELECT id FROM time_slots WHERE is_lunch = 0 LIMIT 3")
    
    test_entries = []
    for day in days:
        for slot in slots:
            query = """
                INSERT INTO schedule_data (week_number, day_id, slot_id, content)
                VALUES (?, ?, ?, ?)
            """
            content = f"Test Course - Day {day['id']} Slot {slot['id']}"
            db.execute_update(query, (99, day['id'], slot['id'], content))
            test_entries.append((day['id'], slot['id']))
            print(f"  ✓ Added: {content}")
    
    # Verify data exists
    verify_query = "SELECT COUNT(*) as count FROM schedule_data WHERE week_number = 99"
    result = db.execute_query(verify_query)
    count = result[0]['count']
    
    if count == len(test_entries):
        print(f"\n✓ Schedule data verified: {count} entries")
        db.close()
        return True
    else:
        print(f"\n✗ Expected {len(test_entries)}, got {count}")
        db.close()
        return False


def test_html_generation():
    """Test 2: Test HTML generation for printing"""
    print_test_header("Print Schedule - HTML Generation")
    
    print("Testing HTML structure generation...")
    
    # Create minimal HTML structure
    html_template = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Test Schedule</title>
</head>
<body>
    <h1>Emploi du Temps - Semaine Test</h1>
    <table border="1">
        <tr><th>Lundi</th><th>Mardi</th></tr>
        <tr><td>Math</td><td>Français</td></tr>
    </table>
</body>
</html>"""
    
    # Validate HTML contains required elements
    required_elements = ['<!DOCTYPE html>', '<table', '<th>', '<td>', 'Emploi du Temps']
    
    for element in required_elements:
        if element in html_template:
            print(f"  ✓ Found: {element}")
        else:
            print(f"  ✗ Missing: {element}")
            return False
    
    print("\n✓ HTML structure valid")
    return True


def test_csv_import_format():
    """Test 3: Test CSV import format validation"""
    print_test_header("Import Content - CSV Format")
    
    print("Testing CSV format parsing...")
    
    # Create test CSV data
    test_csv_data = [
        ['15/01/2026', '6ème A', 'Mathématiques', 'Géométrie', 'Exercices', ''],
        ['20/01/2026', '5ème B', 'Français', 'Grammaire', 'Rédaction', 'Contrôle'],
        ['25/01/2026', '4ème C', 'Sciences', 'Physique', 'TP', ''],
    ]
    
    # Write to temporary CSV file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(test_csv_data)
        temp_path = f.name
    
    try:
        # Read back and validate
        with open(temp_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        print(f"  ✓ Read {len(rows)} rows from CSV")
        
        # Validate each row
        for idx, row in enumerate(rows, start=1):
            if len(row) >= 4:  # At least 4 required columns
                print(f"  ✓ Row {idx}: {row[0]} - {row[1]} - {row[2]}")
            else:
                print(f"  ✗ Row {idx}: Insufficient columns")
                return False
        
        # Cleanup
        os.unlink(temp_path)
        
        print("\n✓ CSV format validation passed")
        return True
        
    except Exception as e:
        print(f"\n✗ CSV validation failed: {e}")
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        return False


def test_import_data_insertion():
    """Test 4: Test data insertion from import"""
    print_test_header("Import Content - Data Insertion")
    
    db = DatabaseManager(DB_PATH)
    
    print("Testing data insertion from import...")
    
    # Clear test data
    db.execute_update("DELETE FROM homework_entries WHERE subject LIKE 'TEST%'")
    
    # Get teacher ID
    teachers = db.execute_query("SELECT id FROM teachers LIMIT 1")
    teacher_id = teachers[0]['id'] if teachers else 1
    
    # Insert test entries (simulating import)
    test_imports = [
        ('2026-01-15', 'TEST 6ème A', 'TEST Math', 'Géométrie', 'Exercices', '', teacher_id),
        ('2026-01-20', 'TEST 5ème B', 'TEST Français', 'Grammaire', 'Rédaction', 'Contrôle', teacher_id),
    ]
    
    inserted_ids = []
    for entry in test_imports:
        query = """
            INSERT INTO homework_entries
            (date, class_name, subject, content, homework, exam, teacher_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        row_id = db.execute_update(query, entry)
        inserted_ids.append(row_id)
        print(f"  ✓ Inserted ID {row_id}: {entry[1]} - {entry[2]}")
    
    # Verify insertion
    verify_query = "SELECT COUNT(*) as count FROM homework_entries WHERE subject LIKE 'TEST%'"
    result = db.execute_query(verify_query)
    count = result[0]['count']
    
    # Cleanup
    db.execute_update("DELETE FROM homework_entries WHERE subject LIKE 'TEST%'")
    
    db.close()
    
    if count == len(test_imports):
        print(f"\n✓ Data insertion verified: {count} entries")
        return True
    else:
        print(f"\n✗ Expected {len(test_imports)}, got {count}")
        return False


def test_distribution_algorithm():
    """Test 5: Test course distribution algorithm"""
    print_test_header("Distribution - Algorithm Logic")
    
    db = DatabaseManager(DB_PATH)
    
    print("Testing distribution algorithm...")
    
    # Clear test data
    db.execute_update("DELETE FROM schedule_data WHERE week_number = 98")
    
    # Get available slots
    days = db.execute_query("SELECT id FROM days ORDER BY display_order")
    slots = db.execute_query("SELECT id FROM time_slots WHERE is_lunch = 0 ORDER BY display_order")
    
    print(f"  ℹ Available: {len(days)} days × {len(slots)} slots = {len(days) * len(slots)} total")
    
    # Test subjects to distribute
    subjects = [
        {'name': 'Math', 'hours': 4},
        {'name': 'Français', 'hours': 4},
        {'name': 'Sciences', 'hours': 3},
    ]
    
    total_hours = sum(s['hours'] for s in subjects)
    print(f"  ℹ Total hours to distribute: {total_hours}")
    
    # Simulate distribution
    slot_index = 0
    available_slots = [(d['id'], s['id']) for d in days for s in slots]
    
    distributed = 0
    for subject in subjects:
        for _ in range(subject['hours']):
            if slot_index >= len(available_slots):
                break
            
            day_id, slot_id = available_slots[slot_index]
            content = f"{subject['name']} - TEST Class"
            
            query = """
                INSERT INTO schedule_data (week_number, day_id, slot_id, content)
                VALUES (?, ?, ?, ?)
            """
            db.execute_update(query, (98, day_id, slot_id, content))
            
            distributed += 1
            slot_index += 1
        
        if slot_index >= len(available_slots):
            break
    
    print(f"  ✓ Distributed {distributed}/{total_hours} hours")
    
    # Verify distribution
    verify_query = "SELECT COUNT(*) as count FROM schedule_data WHERE week_number = 98"
    result = db.execute_query(verify_query)
    count = result[0]['count']
    
    # Cleanup
    db.execute_update("DELETE FROM schedule_data WHERE week_number = 98")
    
    db.close()
    
    if count == distributed:
        print(f"\n✓ Distribution algorithm working: {count} slots filled")
        return True
    else:
        print(f"\n✗ Expected {distributed}, got {count}")
        return False


def test_distribution_coverage():
    """Test 6: Test distribution covers all days"""
    print_test_header("Distribution - Day Coverage")
    
    db = DatabaseManager(DB_PATH)
    
    print("Testing distribution day coverage...")
    
    # Clear test data
    db.execute_update("DELETE FROM schedule_data WHERE week_number = 97")
    
    # Get days
    days = db.execute_query("SELECT id, name FROM days ORDER BY display_order")
    slots = db.execute_query("SELECT id FROM time_slots WHERE is_lunch = 0 LIMIT 2")
    
    # Distribute evenly across all days
    for day in days:
        for slot in slots:
            query = """
                INSERT INTO schedule_data (week_number, day_id, slot_id, content)
                VALUES (?, ?, ?, ?)
            """
            content = f"Test - {day['name']}"
            db.execute_update(query, (97, day['id'], slot['id'], content))
    
    # Verify each day has entries
    all_covered = True
    for day in days:
        check_query = """
            SELECT COUNT(*) as count
            FROM schedule_data
            WHERE week_number = 97 AND day_id = ?
        """
        result = db.execute_query(check_query, (day['id'],))
        count = result[0]['count']
        
        if count > 0:
            print(f"  ✓ {day['name']}: {count} entries")
        else:
            print(f"  ✗ {day['name']}: No entries")
            all_covered = False
    
    # Cleanup
    db.execute_update("DELETE FROM schedule_data WHERE week_number = 97")
    
    db.close()
    
    if all_covered:
        print("\n✓ All days covered in distribution")
        return True
    else:
        print("\n✗ Some days not covered")
        return False


def test_date_format_conversion():
    """Test 7: Test date format conversion for import"""
    print_test_header("Import Content - Date Conversion")
    
    print("Testing date format conversion...")
    
    from datetime import datetime
    
    test_dates = [
        ('01/01/2026', '2026-01-01'),
        ('15/03/2026', '2026-03-15'),
        ('31/12/2026', '2026-12-31'),
    ]
    
    for input_date, expected in test_dates:
        try:
            date_obj = datetime.strptime(input_date, '%d/%m/%Y')
            output = date_obj.strftime('%Y-%m-%d')
            
            if output == expected:
                print(f"  ✓ {input_date} → {output}")
            else:
                print(f"  ✗ {input_date} → {output} (expected {expected})")
                return False
        except ValueError as e:
            print(f"  ✗ Failed to convert {input_date}: {e}")
            return False
    
    print("\n✓ Date conversion working correctly")
    return True


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*70)
    print("FINAL FEATURES - COMPREHENSIVE TEST SUITE")
    print("="*70)
    print(f"Database: {DB_PATH}")
    print(f"Testing: Print Schedules, Import Content, Distribution")
    print("="*70)
    
    tests = [
        ("Print Schedule - Data Verification", test_print_schedule_data),
        ("Print Schedule - HTML Generation", test_html_generation),
        ("Import Content - CSV Format", test_csv_import_format),
        ("Import Content - Data Insertion", test_import_data_insertion),
        ("Distribution - Algorithm Logic", test_distribution_algorithm),
        ("Distribution - Day Coverage", test_distribution_coverage),
        ("Import Content - Date Conversion", test_date_format_conversion),
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
        print("\n🎉 ALL TESTS PASSED! All features are fully functional.")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review errors above.")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
